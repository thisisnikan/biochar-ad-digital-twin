# Presentation

This folder contains `index.html`, an animated, single-file HTML slide deck explaining
the whole idea of the Biochar–AD Digital Twin: the confounding problem it addresses, the
falsifiable research question, what the software pipeline actually does, and an honest
current-status readout, the repository structure and quality controls, and the next
validation gate. It has no build step and no required JavaScript packages; Google Fonts
is the only external visual dependency.

Two slides are real data, not illustrations: the bar charts are computed directly from
`results/experimental/kinetic_baseline_comparison.csv` and
`results/external-dose/dose_response_comparison.csv`, the same reproducible outputs
`biochar-ad benchmark-experimental` and `biochar-ad benchmark-external-dose` regenerate.
Only the confounding-problem schematic on slide 3 is illustrative, and it is labelled as
such in the deck.

If you have never touched this project, [`docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md)
is the more detailed, plain-language companion to this deck.

## Open locally

Download `index.html` and open it in a modern web browser.

- `Left` / `Right`, `Page Up` / `Page Down`, or click: navigate
- `Home` / `End`: first or last slide
- `F`: enter or exit fullscreen
- Swipe horizontally on a touch device

## Edit and publish

Edit `index.html`, commit the change, and verify the deck locally before publishing. If a
committed result CSV changes, re-check the two data slides' bar heights and value labels
by hand against the new CSV — they are static SVG, not generated from the file at load
time — and update `data/README.md`/`results/README.md` cross-references if needed.

The deck intentionally avoids unverified paper titles, invented results and claims beyond
the evidence documented in [`../docs/PROJECT_STATUS.md`](../docs/PROJECT_STATUS.md).
