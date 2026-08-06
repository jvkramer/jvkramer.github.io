# CPH → CUN fare tracker

Answers one question: **is the Copenhagen–Cancún fare high right now, relative to
what this route normally costs?** A fare level on its own says nothing — 8,000 DKK
is cheap in December and dear in November. What matters is the percentile.

`fetch_prices.py` collects the data, `../cancun.html` plots it.

## Quick start

```bash
pip install fast-flights          # only needed for the keyless source

# no credentials — today's cheapest fare only
python fetch_prices.py --source google --departure 2027-02-15 --return 2027-03-01

# with a free Amadeus key — today's fare *and* the historical distribution
export AMADEUS_CLIENT_ID=...
export AMADEUS_CLIENT_SECRET=...
python fetch_prices.py --source amadeus --scan-year --environment production
```

Then open `cancun.html` (any static server, e.g. `python -m http.server` from the
repo root).

## The two sources

| | `--source amadeus` | `--source google` |
|---|---|---|
| Credentials | free key, no card | none |
| Today's fare | yes | yes |
| Historical distribution | **yes** — min/Q1/median/Q3/max | no |
| Percentile verdict | **yes** | no |
| Backed by | Amadeus booking history | Google Flights scrape |

`amadeus` is the one that answers the question. `/v1/analytics/itinerary-price-metrics`
returns the historical fare distribution for a route and departure period as
quartiles; the script places today's cheapest offer on that ladder by linear
interpolation and stores the resulting percentile. Free tier allows 10,000
calls/month — sign up at <https://developers.amadeus.com/register>.

Use `--environment production` for real fares. The default `test` environment
returns cached sample data, which is fine for wiring things up but is **not**
current pricing.

`google` needs nothing but gives no history, so percentiles stay blank. It is
useful for accumulating your own series: run it on a schedule and every run
appends an observation.

## Output

Rows are appended to `../cph_cancun_prices.csv`. Re-running for the same
`(run_date, departure_date, source)` replaces that row rather than duplicating
it, so re-running on the same day is safe.

| column | meaning |
|---|---|
| `run_date` | date the price was observed |
| `departure_date`, `return_date` | the itinerary priced |
| `current_price` | cheapest fare found on `run_date` |
| `hist_min` … `hist_max` | historical distribution (Amadeus only) |
| `percentile` | where `current_price` sits on that distribution, 0–100 |

## Keeping it up to date

The chart gets more useful the longer it runs. A daily cron:

```cron
0 7 * * * cd /path/to/repo/flightprices && \
  AMADEUS_CLIENT_ID=... AMADEUS_CLIENT_SECRET=... \
  python fetch_prices.py --source amadeus --scan-year --environment production
```

## Tests

```bash
python fetch_prices.py --self-test     # percentile maths, no network
```

## Caveats

- Quartiles describe fares **previously seen** on the route. They are not a
  forecast, and a route that has structurally got more expensive will keep
  reading "high".
- "Cheapest fare" is the lowest offer returned, ignoring cabin, bags, and
  routing quality. A 34-hour two-stop itinerary counts the same as a clean one.
- Amadeus coverage of the historical endpoint is not uniform across routes and
  dates; when it returns nothing, the distribution columns are left empty rather
  than filled with a guess.
