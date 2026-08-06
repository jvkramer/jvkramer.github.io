#!/usr/bin/env python3
"""Collect Copenhagen -> Cancun airfares and the historical distribution they sit in.

Two independent sources, either of which can fill the CSV that ``cancun.html`` plots:

``amadeus``  (recommended -- this is the one that answers "historically high?")
    Amadeus for Developers, Self-Service tier. Two endpoints:
      * GET /v1/analytics/itinerary-price-metrics  -> the historical fare
        distribution for the route as quartiles (MINIMUM/FIRST/MEDIUM/THIRD/
        MAXIMUM), built from Amadeus' own booking history.
      * GET /v2/shopping/flight-offers             -> the cheapest fare on sale
        today.
    Put the current fare on the historical ladder and you get a percentile,
    which is exactly the question being asked. Free tier covers 10k calls/month.
    Needs AMADEUS_CLIENT_ID / AMADEUS_CLIENT_SECRET (free signup, no card).

``google``  (no credentials at all)
    Scrapes Google Flights via the ``fast-flights`` package (``pip install
    fast-flights``). Gives today's cheapest fare but no history, so percentiles
    stay empty. Useful to start accumulating your own series immediately: run it
    on a schedule and each run appends a row.

Rows are appended, never rewritten, so repeated runs build a real longitudinal
series. Re-running for a (run_date, departure_date) pair that is already present
replaces that row rather than duplicating it.

Examples
--------
    # one departure, full historical context
    python fetch_prices.py --source amadeus --departure 2027-02-15 --return 2027-03-01

    # sample the next 12 months, one mid-month departure each (the site chart)
    python fetch_prices.py --source amadeus --scan-year

    # no API key, just today's fare
    python fetch_prices.py --source google --departure 2027-02-15

    # check the maths without touching the network
    python fetch_prices.py --self-test
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_ORIGIN = "CPH"
DEFAULT_DESTINATION = "CUN"
DEFAULT_CURRENCY = "DKK"
DEFAULT_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "cph_cancun_prices.csv")

FIELDS = [
    "run_date",
    "origin",
    "destination",
    "departure_date",
    "return_date",
    "currency",
    "source",
    "current_price",
    "hist_min",
    "hist_q1",
    "hist_median",
    "hist_q3",
    "hist_max",
    "percentile",
]

# Amadeus returns the distribution as labelled quartiles; these are the
# percentile positions each label sits at.
QUARTILE_POSITIONS = {
    "MINIMUM": 0.0,
    "FIRST": 25.0,
    "MEDIUM": 50.0,
    "THIRD": 75.0,
    "MAXIMUM": 100.0,
}


# --------------------------------------------------------------------------
# the actual question: where on the historical ladder does today's fare sit?
# --------------------------------------------------------------------------

def percentile_of(price, ladder):
    """Linearly interpolate ``price`` onto a [(percentile, value), ...] ladder.

    The ladder is the historical fare distribution. Returns 0..100, clamped at
    the ends: a fare below every historical observation is 0, above every one
    is 100. Returns None if there is nothing to compare against.
    """
    if price is None or not ladder:
        return None

    pts = sorted((v, p) for p, v in ladder if v is not None)
    if not pts:
        return None
    if len(pts) == 1:
        return 50.0

    if price <= pts[0][0]:
        return 0.0
    if price >= pts[-1][0]:
        return 100.0

    for (v_lo, p_lo), (v_hi, p_hi) in zip(pts, pts[1:]):
        if v_lo <= price <= v_hi:
            if v_hi == v_lo:
                return round((p_lo + p_hi) / 2, 1)
            frac = (price - v_lo) / (v_hi - v_lo)
            return round(p_lo + frac * (p_hi - p_lo), 1)
    return None


# --------------------------------------------------------------------------
# Amadeus
# --------------------------------------------------------------------------

class Amadeus:
    """Minimal Amadeus Self-Service client (stdlib only, no SDK dependency)."""

    def __init__(self, client_id, client_secret, environment="test"):
        self.host = "test.api.amadeus.com" if environment == "test" else "api.amadeus.com"
        self.client_id = client_id
        self.client_secret = client_secret
        self._token = None

    def _authenticate(self):
        body = urllib.parse.urlencode(
            {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            }
        ).encode()
        req = urllib.request.Request(
            "https://%s/v1/security/oauth2/token" % self.host,
            data=body,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            self._token = json.load(resp)["access_token"]

    def get(self, path, **params):
        if self._token is None:
            self._authenticate()
        url = "https://%s%s?%s" % (self.host, path, urllib.parse.urlencode(params))
        req = urllib.request.Request(url, headers={"Authorization": "Bearer " + self._token})
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:400]
            raise SystemExit("Amadeus %s on %s\n%s" % (exc.code, path, detail))

    def price_metrics(self, origin, destination, departure_date, currency, one_way):
        """Historical fare distribution for the route, as labelled quartiles."""
        payload = self.get(
            "/v1/analytics/itinerary-price-metrics",
            originIataCode=origin,
            destinationIataCode=destination,
            departureDate=departure_date,
            currencyCode=currency,
            oneWay=str(bool(one_way)).lower(),
        )
        data = payload.get("data") or []
        if not data:
            return {}
        out = {}
        for metric in data[0].get("priceMetrics", []):
            label = metric.get("quartileRanking")
            if label in QUARTILE_POSITIONS:
                out[label] = float(metric["amount"])
        return out

    def cheapest_offer(self, origin, destination, departure_date, return_date, currency, adults=1):
        """Cheapest fare currently on sale."""
        params = dict(
            originLocationCode=origin,
            destinationLocationCode=destination,
            departureDate=departure_date,
            adults=str(adults),
            currencyCode=currency,
            max="50",
        )
        if return_date:
            params["returnDate"] = return_date
        payload = self.get("/v2/shopping/flight-offers", **params)
        offers = payload.get("data") or []
        prices = [float(o["price"]["grandTotal"]) for o in offers if o.get("price", {}).get("grandTotal")]
        return min(prices) if prices else None


def collect_amadeus(args, departure_date, return_date):
    client_id = os.environ.get("AMADEUS_CLIENT_ID")
    client_secret = os.environ.get("AMADEUS_CLIENT_SECRET")
    if not (client_id and client_secret):
        raise SystemExit(
            "Set AMADEUS_CLIENT_ID and AMADEUS_CLIENT_SECRET.\n"
            "Free key: https://developers.amadeus.com/register (no card required)."
        )

    api = Amadeus(client_id, client_secret, environment=args.environment)
    one_way = return_date is None

    metrics = api.price_metrics(
        args.origin, args.destination, departure_date, args.currency, one_way
    )
    current = api.cheapest_offer(
        args.origin, args.destination, departure_date, return_date, args.currency
    )

    ladder = [(QUARTILE_POSITIONS[k], v) for k, v in metrics.items()]

    return {
        "source": "amadeus",
        "current_price": current,
        "hist_min": metrics.get("MINIMUM"),
        "hist_q1": metrics.get("FIRST"),
        "hist_median": metrics.get("MEDIUM"),
        "hist_q3": metrics.get("THIRD"),
        "hist_max": metrics.get("MAXIMUM"),
        "percentile": percentile_of(current, ladder),
    }


# --------------------------------------------------------------------------
# Google Flights (keyless)
# --------------------------------------------------------------------------

def collect_google(args, departure_date, return_date):
    try:
        from fast_flights import FlightQuery, Passengers, create_query, get_flights
    except ImportError:
        raise SystemExit("pip install fast-flights")

    legs = [FlightQuery(date=departure_date, from_airport=args.origin, to_airport=args.destination)]
    if return_date:
        legs.append(
            FlightQuery(date=return_date, from_airport=args.destination, to_airport=args.origin)
        )

    query = create_query(
        flights=legs,
        trip="round-trip" if return_date else "one-way",
        seat="economy",
        passengers=Passengers(adults=1),
        currency=args.currency,
    )
    results = get_flights(query)
    prices = [f.price for f in results if getattr(f, "price", None)]

    return {
        "source": "google-flights",
        "current_price": min(prices) if prices else None,
        "hist_min": None,
        "hist_q1": None,
        "hist_median": None,
        "hist_q3": None,
        "hist_max": None,
        # Google Flights exposes no numeric history, so the percentile is only
        # filled once enough of our own runs have accumulated. Left blank here
        # rather than guessed.
        "percentile": None,
    }


# --------------------------------------------------------------------------
# CSV
# --------------------------------------------------------------------------

def read_rows(path):
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def write_rows(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in FIELDS})


def upsert(path, new_rows):
    """Append rows, replacing any with the same (run_date, departure_date)."""
    existing = read_rows(path)
    key = lambda r: (r.get("run_date"), r.get("departure_date"), r.get("source"))
    incoming = {key(r): r for r in new_rows}
    merged = [r for r in existing if key(r) not in incoming]
    merged.extend(new_rows)
    merged.sort(key=lambda r: (r.get("departure_date") or "", r.get("run_date") or ""))
    write_rows(path, merged)
    return len(merged)


# --------------------------------------------------------------------------

def month_samples(count, day=15):
    """One departure per month for the next ``count`` months."""
    today = dt.date.today()
    out = []
    year, month = today.year, today.month
    for _ in range(count):
        month += 1
        if month > 12:
            month = 1
            year += 1
        out.append(dt.date(year, month, day).isoformat())
    return out


def self_test():
    ladder = [(0.0, 4000.0), (25.0, 5200.0), (50.0, 6100.0), (75.0, 7300.0), (100.0, 11000.0)]
    cases = [
        (3000.0, 0.0),      # below every historical fare
        (4000.0, 0.0),      # exactly the minimum
        (6100.0, 50.0),     # exactly the median
        (5650.0, 37.5),     # midway between Q1 and median
        (11000.0, 100.0),   # exactly the maximum
        (14000.0, 100.0),   # above every historical fare
    ]
    failures = 0
    for price, expected in cases:
        got = percentile_of(price, ladder)
        ok = got == expected
        failures += not ok
        print("  %-9s -> %-6s expected %-6s %s" % (price, got, expected, "ok" if ok else "FAIL"))

    edge = [
        ("no price", percentile_of(None, ladder), None),
        ("no ladder", percentile_of(5000.0, []), None),
        ("single point", percentile_of(5000.0, [(50.0, 6000.0)]), 50.0),
    ]
    for label, got, expected in edge:
        ok = got == expected
        failures += not ok
        print("  %-13s -> %-6s expected %-6s %s" % (label, got, expected, "ok" if ok else "FAIL"))

    print("\n%s" % ("all passed" if not failures else "%d FAILED" % failures))
    return 1 if failures else 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--source", choices=["amadeus", "google"], default="amadeus")
    parser.add_argument("--origin", default=DEFAULT_ORIGIN)
    parser.add_argument("--destination", default=DEFAULT_DESTINATION)
    parser.add_argument("--departure", help="YYYY-MM-DD")
    parser.add_argument("--return", dest="return_date", help="YYYY-MM-DD; omit for one-way")
    parser.add_argument("--trip-length", type=int, default=14,
                        help="nights, used to derive a return date in --scan-year (default 14)")
    parser.add_argument("--scan-year", action="store_true",
                        help="sample one departure per month for the next 12 months")
    parser.add_argument("--months", type=int, default=12, help="months to sample with --scan-year")
    parser.add_argument("--currency", default=DEFAULT_CURRENCY)
    parser.add_argument("--environment", choices=["test", "production"], default="test",
                        help="Amadeus environment; 'test' uses cached sample data")
    parser.add_argument("--csv", default=DEFAULT_CSV)
    parser.add_argument("--self-test", action="store_true", help="check percentile maths, no network")
    args = parser.parse_args(argv)

    if args.self_test:
        return self_test()

    if args.scan_year:
        departures = month_samples(args.months)
    elif args.departure:
        departures = [args.departure]
    else:
        parser.error("give --departure YYYY-MM-DD or --scan-year")

    collector = collect_amadeus if args.source == "amadeus" else collect_google
    run_date = dt.date.today().isoformat()
    rows = []

    for departure in departures:
        if args.scan_year:
            return_date = (
                dt.date.fromisoformat(departure) + dt.timedelta(days=args.trip_length)
            ).isoformat()
        else:
            return_date = args.return_date

        print("fetching %s %s->%s dep %s" % (args.source, args.origin, args.destination, departure))
        try:
            result = collector(args, departure, return_date)
        except SystemExit:
            raise
        except Exception as exc:  # one bad departure date shouldn't lose the rest
            print("  skipped: %s" % exc, file=sys.stderr)
            continue

        row = {
            "run_date": run_date,
            "origin": args.origin,
            "destination": args.destination,
            "departure_date": departure,
            "return_date": return_date or "",
            "currency": args.currency,
        }
        row.update({k: ("" if v is None else v) for k, v in result.items()})
        rows.append(row)

        pct = result.get("percentile")
        print("  price %s %s%s" % (
            result.get("current_price") or "n/a",
            args.currency,
            "" if pct is None else "  (%.0fth percentile of history)" % pct,
        ))

    if not rows:
        print("nothing collected", file=sys.stderr)
        return 1

    total = upsert(args.csv, rows)
    print("\nwrote %d row(s) to %s (%d total)" % (len(rows), args.csv, total))
    return 0


if __name__ == "__main__":
    sys.exit(main())
