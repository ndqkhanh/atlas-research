# Atlas-Research Block 08 — Memory & Citation Store

## Responsibility

Persist across reports: (a) user preferences, (b) high-quality source records with per-user trust ratings, (c) prior briefs and reports for re-use, (d) aggregated citation provenance. Memory is per-user (or per-tenant) and opt-in.

## What is stored

### User memory

```
user_preferences:
  - prefers_bullet_summaries: true
  - citation_style: "arxiv_id"
  - typical_audience: "technical"
  - prior topics of interest: [...]

user_source_ratings:
  - per-domain trust: {"arxiv.org": 0.95, "medium.com": 0.45, ...}
  - per-author trust (in user's field)
  - blacklist of domains user has flagged as unreliable
```

### Report memory

```
prior_reports[]:
  - id, question, brief, date, cost
  - sections, top claims, sources
  - user feedback (if any)
```

Used for:
- Cold-start boost when a new question matches a prior ("similar question at step 0, offer to reuse or expand").
- Source re-use (prior high-quality sources prioritized in new retrievals).

### Citation store

Global-ish (not per-user): a deduplicated store of seen sources with:

- Canonical SourceRef (URL / DOI / arXiv ID + hash).
- Retrieval history (how often cited, in how many reports).
- Abstract/title/metadata cache.
- Observed trust (aggregate across users).

Report retrievals can reference the citation store before fetching, saving cost.

## Storage

- Per-user: pgvector or similar with tenant-scoped rows.
- Global citation store: a document DB with full-text and embedding indexes.

## Memory hygiene

- **TTL on ratings.** Source trust decays if not refreshed — reduces staleness.
- **User-visible.** User can list / edit / delete their memory at any time.
- **Explicit opt-in.** Users must enable memory; off by default for privacy.

## Integration with other blocks

- **Intake Clarify** reads user preferences to produce a brief consistent with prior accepted style.
- **Query Planner** reads source ratings: `source.trust.prior = 0.9` adjusts the expected utility of a retrieval.
- **Synthesis Writer** honors citation style.
- **Citation Verifier** uses the citation store's cached metadata to avoid redundant fetches.

## Privacy

- Data boundary: per-user memory never mixes across users.
- Citation store is aggregated; individual user histories never exposed.
- GDPR-style right-to-erasure: purge by user ID cascades to all linked memories.
- Audit log of memory read/write per user.

## Failure modes

| Mode | Defense |
|---|---|
| Memory rot (stale preferences) | Surface assumptions applied in brief so user notices |
| Cross-user leakage | Strict per-tenant scoping |
| Memory overfit (agent too opinionated) | Cap influence weight; fallback defaults |
| Citation-store poisoning | Trust based on verification pass rate, not frequency |
| Stale cached metadata | Hash compare on re-fetch; invalidate on drift |

## Metrics

- `memory.applied_prefs` per report
- `memory.source_reuse_rate`
- `citation_store.cache_hit_rate`
- `memory.user_edit_events`
- `memory.size_per_user`
