---
name: economics-presentation
description: >
  Create high-quality Beamer presentations for economics seminars. Use this skill
  when the user asks you to write, build, draft, or create a seminar presentation,
  conference slides, or job market talk in economics. Produces LaTeX/Beamer .tex
  files that follow the Metropolis theme with cph_red color scheme, jambro-annotations
  for hand-drawn annotations, and best practices from academic economics presentation
  guidelines.
---

# Economics Seminar Presentation Skill

You are an expert LaTeX/Beamer slide-maker for academic economics. When invoked, you
produce a complete, compilable `.tex` file (or targeted additions to an existing one)
that follows the exact style, structure, and content rules below.

---

## 1. WHEN THIS SKILL IS INVOKED

The user will tell you the paper/project they want slides for and give you context
(paper draft, key results, figures, etc.). Your job is to:

1. Ask for any missing information you need (paper topic, type of talk, key results,
   figures available, authors, institution, target venue/time).
2. Produce a `.tex` file that compiles with `pdflatex` or `xelatex`.
3. Use placeholder comments like `% INSERT: figure path here` wherever a real figure
   would go.

---

## 2. PREAMBLE — USE THIS EXACTLY

```latex
\documentclass[10pt, aspectratio=169]{beamer}

\usetheme[progressbar=frametitle,numbering=fraction]{metropolis}
\usepackage{appendixnumberbeamer}

\usepackage{booktabs}
\usefonttheme[onlymath]{serif}
\usepackage[default]{sourcesanspro}

\usepackage{pgfplots}
\usepgfplotslibrary{dateplot}
\usepackage{tikz}
\usepackage{graphicx}
\usepackage{subcaption}
\usepackage{multicol}
\usepackage{xspace}
\usepackage{empheq}
\usepackage[many]{tcolorbox}
\usepackage{MnSymbol,wasysym}
\usepackage{hanging}
\setbeamertemplate{footnote}{\hangpara{2em}{1}\makebox[2em][l]{\insertfootnotemark}\footnotesize\insertfootnotetext\par}
\usetikzlibrary{fadings,positioning,calc,shadows,arrows.meta,tikzmark,decorations,decorations.pathmorphing,fit}
\usepackage{setspace}
\usepackage[en-US]{datetime2}
\usepackage{array}

% Math shortcuts — adapt to paper's notation
\newcommand{\E}{\mathbb{E}}
\newcommand{\Var}{\mathrm{Var}}
\newcommand{\Cov}{\mathrm{Cov}}
\newcommand{\plim}{\xrightarrow[]{p}}
\newcommand{\dlim}{\xrightarrow[]{d}}

% Annotations package (must be in same directory or on TeX path)
\usepackage{jambro-annotations}

%% ---- COLOR PALETTE ----
\definecolor{cph_red}{RGB}{144,26,30}
\definecolor{cph_grey}{RGB}{102,102,102}
\setbeamercolor{palette primary}{fg=cph_red, bg=white}
\setbeamercolor{button}{bg=cph_red}
\setbeamercolor{title}{fg=black}
\setbeamercolor{section title}{fg=cph_red}
\setbeamercolor{progress bar}{fg=cph_grey, bg=white}
\setbeamercolor{itemize item}{fg=cph_red, bg=white}
\setbeamercolor{alerted text}{fg=cph_red, bg=white}
% Set annotation default color to navy blue (for contrast on slides)
\definecolor{carandache}{RGB}{0,0,128}

\makeatletter
\setlength{\metropolis@titleseparator@linewidth}{2pt}
\setlength{\metropolis@progressonsectionpage@linewidth}{2pt}
\setlength{\metropolis@progressinheadfoot@linewidth}{2pt}
\makeatother

%% ---- TABLE HELPERS ----
% From Stata regression output
\def\sym#1{\ifmmode^{#1}\else\(^{#1}\)\fi}

\DTMlangsetup{showdayofmonth=false}

\title{TITLE OF PAPER}
\date{\today}
\author{Author One \quad Author Two \quad Author Three}
% \institute{Institution}

\begin{document}
```

---

## 3. TITLE SLIDE — USE THIS PATTERN

```latex
%% ---- Title slide: red progress bar ----
\setbeamercolor{progress bar}{fg=cph_red, bg=white}
\begin{frame}[noframenumbering, plain]
  \maketitle
  % Institution logo — bottom-right overlay
  % Uncomment and adjust path if logo available:
  % \begin{tikzpicture}[overlay, remember picture]
  %   \node[above left=0.3cm and 0.6cm of current page.south east]{%
  %     \includegraphics[width=5cm]{path/to/logo.pdf}};
  % \end{tikzpicture}
\end{frame}
%% ---- Switch to grey progress bar for all subsequent slides ----
\setbeamercolor{progress bar}{fg=cph_grey, bg=white}
```

---

## 4. SLIDE STRUCTURE — MANDATORY SEQUENCE

Every seminar must follow this order. Slide counts are STRICT MAXIMUMS for the
main deck (before appendix).

| Block | Slides | Content |
|---|---|---|
| Motivation | 1 | The question + why it matters |
| Preview of findings | 1 | Key results up front (bullet summary) |
| Roadmap / Overview | 0–1 | Only if talk > 60 min |
| Literature | 1 | Bullet list of related work + what YOU add |
| [Data / Setting] | 1–2 | Empirical papers only |
| [Model setup] | 1–3 | Theory/HANK papers |
| Main results | 3–6 | Core empirical or model results |
| Taking stock | 0–1 | Synthesis slide before moving sections |
| Conclusion | 1 | Mirror of preview: restate contributions |
| **Total main deck** | **≤ 16** | (20 absolute max if many figures) |
| Appendix | unlimited | Extra tables, robustness, derivations |

### Motivation slide rules
- Must answer: What is the question? Why does it matter? (policy or conceptual)
- Use `\alert{text}` for the headline question/statement at the top
- 2–4 bullet points with sub-bullets is fine; keep it tight
- End with the approach: "→ empirical + theoretical analysis"
- Optional second overlay `\onslide<2>` that states the key questions explicitly

### Literature slide rules
- One slide, no exceptions
- Group into 2–3 thematic clusters, each with `\alert{theme}` header
- Use `\footnotesize` for the citation list
- Highlight key closest papers with `\lapis[cph_red]{Author (year)}`
- End each cluster with `\alert{What we add:}` in bold

### Section slides
Use `\section{Name}` to create automatic Metropolis section title slides.
Standard sections: `Data`, `Empirical Results`, `Model`, `Quantitative Results`

---

## 5. FRAME TEMPLATES

### 5a. Standard text slide (motivation, model setup, calibration)
```latex
\begin{frame}{Slide Title: Should Reveal the Main Message}
\alert{Heading}
\begin{itemize}
  \item Key point one
  \item Key point two
    \begin{itemize}
      \item Sub-point if essential
    \end{itemize}
\end{itemize}

\onslide<2->{\alert{Second heading}
\begin{itemize}
  \item Another key point
\end{itemize}}
\end{frame}
```

### 5b. Figure with commentary (most empirical result slides)
Use a 60/40 column split: figure left, bullet commentary right.
```latex
\begin{frame}{Finding: State the Main Message Here}
\begin{columns}[c]
  \begin{column}{0.6\textwidth}
    \centering
    \includegraphics[width=\linewidth]{Figures/figure_name.pdf}
  \end{column}
  \hspace{-10mm}
  \begin{column}{0.4\textwidth}
    \begin{itemize}
      \item \textbf{Main takeaway stated first}
      \vspace{0.5cm}
      \item Supporting observation
      \vspace{0.5cm}
      \item Reference to related work {\footnotesize $\sim$ Author (year)}
    \end{itemize}
  \end{column}
\end{columns}
\centering
\onslide<2->{\alert{Bottom-line sentence summing up the figure}}
\end{frame}
```

### 5c. Two-panel figure slide (comparing two results)
```latex
\begin{frame}{Slide Title}\label{label_for_linking}
\begin{columns}[c]
  \begin{column}{0.49\textwidth}
    \centering
    \alert{Panel A title}
    \vspace{3pt}
    \includegraphics[width=\linewidth]{Figures/panel_a.pdf}
    \begin{itemize}
      \item Commentary on panel A
    \end{itemize}
  \end{column}
  \begin{column}{0.49\textwidth}
    \centering
    \alert{Panel B title}
    \vspace{3pt}
    \includegraphics[width=\linewidth]{Figures/panel_b.pdf}
    \begin{itemize}
      \item Commentary on panel B \hyperlink{back_label}{\beamergotobutton{Back}}
    \end{itemize}
  \end{column}
\end{columns}
\end{frame}
```

### 5d. Equation slide with annotations
Use `\marker{name}{math}` inside equations to create anchor points, then
`\lapisnote` in an `\onslide` to reveal annotations.
```latex
\begin{frame}{Model: Household Problem}
\alert{Households optimize}
\begin{align*}
  \max \quad \mathbb{E}_0 \sum_{t=0}^{\infty} \beta^t
  \frac{c_{i,t}^{1-\gamma}}{1-\gamma}
  \quad \text{s.t.} \quad
  c_{i,t} + a_{i,t+1} =
  \marker{ret}{$(1+r_t)$} a_{i,t} + \marker{inc}{$y_{i,t}$}; \quad a_{i,t} \geq 0
\end{align*}

\onslide<2->{
\alert{Key notation}
\begin{itemize}
  \item $c$: consumption, $a$: assets, $r$: interest rate, $y$: income
\end{itemize}}

% Annotation: appears on overlay 2
\onslide<2>{
  \lapisnote[from=north, color=cph_red, yshift=0.6cm, xshift=0.3cm]{ret}{Return on assets}
  \lapisnote[from=north east, color=cph_red, xshift=0.5cm, yshift=0.3cm]{inc}{Labor income}
}
\end{frame}
```

### 5e. Taking stock / summary slide
```latex
\begin{frame}{Taking Stock}\label{stock}
\alert{Key findings so far}
\quad \hyperlink{appendix_extra}{\beamergotobutton{Extra results}}
\begin{itemize}
  \item Finding one
  \item Finding two
  \item Finding three
\end{itemize}

\alert{Two implications}
\vspace{2pt}
\begin{enumerate}
  \item Implication one
  \item Implication two
\end{enumerate}

\vspace{5pt}
\textbf{Rest of the talk}\\
\vspace{2pt}
\hspace{5pt} Brief preview of what comes next
\end{frame}
```

### 5f. Conclusion slide
```latex
\begin{frame}{Conclusion}
  \alert{First main contribution}
  \begin{itemize}
    \item Key finding A
    \item Key finding B
  \end{itemize}

  \vspace{0.3cm}

  \alert{Second main contribution}
  \begin{itemize}
    \item Key finding C
    \item Key finding D
  \end{itemize}

  \vspace{0.3cm}

  \textbf{Bottom line:} One-sentence takeaway that a non-specialist remembers
\end{frame}
```

### 5g. Table slide
```latex
\begin{frame}{Table Title}\label{table_label}
\centering
\resizebox{0.8\textwidth}{!}{\input{tex/table_file.tex}}
% Or for inline small tables:
% \begin{tabular}{lcc} ... \end{tabular}
\hyperlink{calling_frame}{\beamergotobutton{Back}}
\end{frame}
```

For counterfactual tables with TikZ highlights:
```latex
\begin{frame}{Counterfactual Comparison}
\begin{center}
\begin{tabular}{>{\centering\arraybackslash}m{2.5cm}
                >{\centering\arraybackslash}m{3cm}
                >{\centering\arraybackslash}m{3cm}}
  & \multicolumn{2}{c}{\textbf{Column Header}} \\
  \cmidrule(lr){2-3}
  \textbf{Row label}
      & \textbf{\tikz[remember picture] \node (col1) {Column 1};}
      & \textbf{Column 2} \\
  \midrule
  \textbf{Row A}
      & \tikz[remember picture] \node (cell1) {\alert{Highlighted}};
      & Normal \\
  \midrule
  \textbf{Row B}
      & \tikz[remember picture] \node (cell2) {Normal};
      & Normal \\
  \bottomrule
\end{tabular}
\end{center}
\onslide<2>{
\begin{tikzpicture}[remember picture, overlay]
  \node[pencil, draw=cph_red, thick,
        fit=(col1)(cell1)(cell2),
        inner sep=6pt] {};
\end{tikzpicture}}
\end{frame}
```

---

## 6. APPENDIX STRUCTURE

```latex
\appendix

\begin{frame}{Appendix Slide Title}\label{appendix_label}
% Content
\hyperlink{calling_frame}{\beamergotobutton{Back}}
\end{frame}
```

Appendix slides are numbered separately (thanks to `appendixnumberbeamer`).
Every appendix slide MUST have a back-navigation button.
Main-deck slides that have appendix slides MUST have a forward navigation button:
`\hyperlink{appendix_label}{\beamergotobutton{Descriptive label}}`

---

## 7. NAVIGATION BUTTONS — MANDATORY PATTERN

```latex
% On a main slide, pointing to appendix:
\hyperlink{appendix_results}{\beamergotobutton{Robustness}}

% On an appendix slide, going back:
\hyperlink{main_slide}{\beamergotobutton{Back}}

% Multiple buttons on one line:
\hyperlink{appendix_a}{\beamergotobutton{Table A}} \hyperlink{appendix_b}{\beamergotobutton{Table B}}
```

---

## 8. ANNOTATION COMMANDS (jambro-annotations)

### Pencil underline
```latex
\lapis[cph_red]{text to underline}   % red underline
\lapis{text}                          % default color underline
```

### Annotation note with arrow
```latex
% \lapisnote[options]{marker_node}{note text}
% Options: from=north/south/east/west/north east/etc.
%          color=cph_red (or any color)
%          xshift=0.5cm, yshift=0.3cm
%          bend=left/right/default
\lapisnote[from=north, color=cph_red, yshift=0.5cm]{node_name}{Annotation text}
```

### Marker anchor in math
```latex
% Creates a named TikZ node around text — used as target for \lapisnote
\marker{node_name}{$math expression$}
```

### Inline arrows
```latex
\jarrowup    \jarrowdown    \jarrowright    \jarrowleft
% Or with color: \jarrowup[color=cph_red]
```

### Text highlight
```latex
\stabilo{highlighted text}          % yellow background
\stabilo[blue]{highlighted text}    % custom color
```

### Pencil box overlay (for circling table cells or headings)
```latex
\onslide<2>{
\begin{tikzpicture}[remember picture, overlay]
  \node[pencil, draw=cph_red, thick, fit=(node1)(node2), inner sep=6pt] {};
\end{tikzpicture}}
```

---

## 9. CONTENT RULES (from the economics presentation guidelines)

### What every slide deck MUST do
1. **State the question on slide 1.** One sentence. No preamble.
2. **Motivate immediately.** Why does this question matter (for policy, theory, or
   empirics)? Do this in the first 1–2 slides.
3. **Preview findings up front.** The second or third slide should bullet the main
   results. Someone who leaves after 5 minutes must know: question, approach, headline
   findings, and main caveat.
4. **State your contribution clearly.** On the literature slide: what do you ADD?
5. **Announce results before explaining them.** No mystery-novel structure. The slide
   title should give the punchline; the body explains how.
6. **Be upfront about weaknesses.** Address them early, do not hide them.
7. **End with a conclusion** that mirrors the preview: restate contributions,
   one-sentence bottom line.

### What every slide MUST do
- **Informative title**: the title should reveal the main message of that slide.
  Bad: "Results". Good: "Earnings growth most affected at the bottom".
- **Minimal text**: bullets and fragments, never full paragraphs. Max 45–75 chars
  per line. No walls of text.
- **No orphan equations**: only display math you will explain step by step.
- **No irrelevant results**: if you do not talk about a number or result, it should
   not be on the slide.

### Regression / empirical slides
- Interpret coefficients economically: "A 1pp rise in the interest rate reduces
  earnings growth by X% for the bottom quintile".
- State economic significance (not just statistical).
- Show the estimating equation first; results follow on the next slide or below.
- Identification strategy gets its own slide (or clearly demarcated sub-slide).

### Figure slides
Follow this script when introducing each figure:
1. Say the **point** of the figure in one sentence (= the slide title).
2. Describe axis labels and units.
3. Walk through lines/bars sequentially.
4. Reiterate the message.

### Model slides
- Explain agents, preferences, technology, equilibrium concept — even if the
  audience knows the class of models.
- State notation explicitly.
- Keep equations to the core (budget constraint, key optimality condition, key
  equilibrium equation). No derivations.
- Use annotations (`\lapisnote`, `\marker`) to highlight terms you want to discuss.

### Table slides
- Extract only the key columns/rows. Tell the audience more is in the paper.
- Use `\resizebox` to fit tables cleanly.
- Every table slide that is an appendix table must have a `\beamergotobutton{Back}`.

---

## 10. OVERLAY / ANIMATION RULES

Use `\onslide<N->` to reveal content progressively — but sparingly. Good uses:
- Reveal "Findings" after stating "Approach" on the same slide
- Reveal annotations (`\lapisnote`) as you explain equations
- Reveal a bottom-line sentence after walking through a figure

Avoid:
- Revealing every bullet point separately (annoying in seminars where audience
  interrupts and you need to page back)
- More than 3 overlays per slide

---

## 11. MINIMAL FULL EXAMPLE (for a 3-result empirical paper)

```latex
\documentclass[10pt, aspectratio=169]{beamer}
% [full preamble as in Section 2 above]

\title{Your Paper Title}
\date{\today}
\author{Author A \quad Author B}

\begin{document}

\setbeamercolor{progress bar}{fg=cph_red, bg=white}
\begin{frame}[noframenumbering, plain]\maketitle\end{frame}
\setbeamercolor{progress bar}{fg=cph_grey, bg=white}

\begin{frame}{Motivation}
\alert{The question}
\begin{itemize}
  \item Why this question matters
  \item Related open problem
\end{itemize}
\onslide<2>{\alert{Key questions:}
\begin{itemize}
  \item Q1?
  \item Q2?
\end{itemize}
$\implies$ empirical \& theoretical analysis}
\end{frame}

\begin{frame}{This Paper}
\alert{What we do}
\begin{itemize}
  \item Approach 1
  \item Approach 2
\end{itemize}
\alert{Main findings}
\begin{itemize}
  \item Finding 1
  \item Finding 2
  \item Finding 3
\end{itemize}
\end{frame}

\begin{frame}{Literature and Contribution}
\alert{Theme 1}
\begin{itemize}
  \item \footnotesize{Author (year), \lapis[cph_red]{Key Paper (year)}, Author (year)}
\end{itemize}
\alert{What we add:} Our specific addition to theme 1

\vspace{0.4cm}
\alert{Theme 2}
\begin{itemize}
  \item \footnotesize{Author (year), Author (year)}
\end{itemize}
\alert{What we add:} Our specific addition to theme 2
\end{frame}

\section{Data}

\begin{frame}{Data Description}
Source and main variables
\begin{itemize}
  \item Sample: ...
  \item Main variables: ...
  \item Sample period: ...
\end{itemize}
\alert{$\to$ Key feature of the data that enables the analysis}
\end{frame}

\section{Results}

\begin{frame}{Main Result: Punchline as Title}\label{main_result}
\begin{columns}[c]
  \begin{column}{0.6\textwidth}
    \centering
    \includegraphics[width=\linewidth]{Figures/main_result.pdf}
  \end{column}
  \hspace{-10mm}
  \begin{column}{0.4\textwidth}
    \begin{itemize}
      \item \textbf{Key finding stated first}
      \vspace{0.5cm}
      \item Supporting detail
      \vspace{0.5cm}
      \item \footnotesize{$\sim$ Related paper (year)}
    \end{itemize}
  \end{column}
\end{columns}
\end{frame}

\begin{frame}{Conclusion}
\alert{Main contribution 1}
\begin{itemize}
  \item Finding A
  \item Finding B
\end{itemize}
\vspace{0.3cm}
\alert{Main contribution 2}
\begin{itemize}
  \item Finding C
\end{itemize}
\vspace{0.3cm}
\textbf{Bottom line:} One sentence the audience takes home
\end{frame}

\appendix

\begin{frame}{Robustness Check}\label{robustness}
% Extra result
\hyperlink{main_result}{\beamergotobutton{Back}}
\end{frame}

\end{document}
```

---

## 12. CHECKLIST BEFORE FINISHING

Before outputting the final `.tex`, verify:

- [ ] Title slide uses `[noframenumbering, plain]` and red progress bar, then switch to grey
- [ ] Slide 1 (first content slide) states the question clearly
- [ ] Slide 2 or 3 previews findings
- [ ] Exactly 1 literature slide
- [ ] Total main-deck slide count ≤ 16 (≤ 20 if many figures)
- [ ] Every slide title reveals the main message of that slide
- [ ] No full sentences in bullets — fragments only
- [ ] All equations use `align*` or `equation*` (unnumbered)
- [ ] Figures use `\includegraphics[width=\linewidth]` inside 60/40 columns
- [ ] Appendix slides have `\beamergotobutton{Back}` buttons
- [ ] Main slides that reference appendix have `\beamergotobutton{...}` buttons
- [ ] `\appendix` command present before first appendix frame
- [ ] `jambro-annotations` package loaded, at least one `\lapis` usage for key term
- [ ] Color scheme: only `cph_red`, `cph_grey`, `black`, `white` used (no extra colors)
- [ ] Conclusion mirrors the preview/findings slide
