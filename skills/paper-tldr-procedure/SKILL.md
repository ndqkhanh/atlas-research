---
name: 'paper-tldr-procedure'
description: 'Extract a canonical TLDR (≤ 280 chars) from a paper following a fixed structure.'
version: '0.1.0'
triggers: ['tldr', 'summary']
tags: ['document-derived', 'extraction']
---

# Goal
Produce a stable, comparable TLDR for any paper.

# Constraints & Style
- ≤ 280 characters.
- Three-clause structure: *what was done* + *what was found* + *why it matters*.
- No quoting; paraphrase faithfully.
- No author names, no venue.

# Workflow
1. Read the abstract.
2. Identify the contribution clause (`we propose / we show / we present`).
3. Identify the result clause (numerical headline if available).
4. Identify the implication clause (the "matters" claim).
5. Compose into the three-clause TLDR; trim to 280.
