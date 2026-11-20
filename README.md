# Catholic Novenas

A small library of nine-day Catholic novenas, each with a phone prayer app and a 4-page print layout.
Live at https://catholic-novenas.netlify.app

- `novenas/<slug>/novena.json`: all of a novena's words (saints, prayers, nine days)
- `novenas/<slug>/img/`: portraits (480×600) and round faces (112×112), all public domain
- `templates/`: the novena page and the library page
- `tools/build.py`: builds `site/` (what Netlify serves), or one self-contained HTML file with `--artifact <slug>`
- `tools/print_fill.py`, `tools/check_print.py`: fill and check the Google Docs print layout
- `tools/shots.py`, `tools/og.py`: phone screenshots and link-preview images
- `skill/SKILL.md`: the step-by-step guide for making a new novena

Scripture quotations are from the Revised Standard Version, Catholic Edition (RSV-CE), copyright © 1965, 1966
National Council of the Churches of Christ in the United States of America. Used by permission. All rights reserved worldwide.
