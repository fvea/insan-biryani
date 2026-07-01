# CLAUDE.md

This is the umbrella repo for Insan Biryani code projects. Related projects
should live here as sibling subfolders when they become real work.

## Current subprojects

- **`pos/`** - the offline single-file POS app the stall runs every night. See
  `pos/CLAUDE.md` for its architecture and editing rules.
- **`contracts/`** - a small ReportLab script (`generate_contracts.py`) that
  generates the helpers' one-page payment agreement PDFs. Run it from the repo
  root with:
  `uv run --with reportlab --with pillow python contracts/generate_contracts.py`

The subprojects do not share code, dependencies, or a build step. Treat each
subfolder as its own project surface while keeping the whole Insan Biryani code
base under this git repo.
