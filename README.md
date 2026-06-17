# Insan Biryani

Code for my girlfriend's night-market food stall at Gapan City Plaza, Nueva
Ecija.

This is the umbrella repo for Insan Biryani code projects. Related projects
should live here as sibling subfolders when they become real work.

## Current subprojects

- **`pos/`** - the offline single-file point-of-sale app she uses every night.
  See `pos/README.md`.
- **`contracts/`** - generates the helpers' one-page payment agreement PDFs and
  stores the related agreement files. Run:
  `uv run --with reportlab --with pillow python contracts/generate_contracts.py`

The subprojects do not share code or dependencies. Work in whichever folder
matches the task.

Vault notes, decisions, roadmap, and progress logs live in the second-brain
vault under `01_Projects/Insan Biryani/`, not in this repo.
