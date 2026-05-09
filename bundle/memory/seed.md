# Atlas-Research seed memory

## Default citation styles

- **Academic** — author-year inline + numbered footnote.
- **Web** — title-link inline; full URL in references section.
- **Mixed** — both, with a per-paragraph default chosen by source
  type majority.

## Default rubric thresholds

- `direct` support: confidence 0.9–1.0.
- `partial` support: confidence 0.5–0.7 (with `LBL-ATLAS-DUAL-SOURCE`
  flag).
- `tangential`: rejected.
- `unsupported`: rejected.

## Default search depth

- 5–10 sub-queries per question.
- 3–5 candidates per sub-query (15–50 candidates total).
- Top-3 per sub-query survive to synthesis after verification.
- Final report cites 10–25 sources for a typical question.

## Default report length

- Short — 200–400 words, 5–10 cited claims.
- Standard — 600–1000 words, 12–25 cited claims.
- Long — 1500–2500 words, 30–60 cited claims.
