# FAIZA LAB V10 — Reverse-calibrated image quality for beadwork (experimental)

**Research preview for peer review — not a production-ready photo rejection model.**

Faiza is an offline-oriented, Arabic-first beadwork design project. The V10 laboratory tests a **reverse-calibration principle**: start from a final bead chart with known cell colors, degrade the rendered image, reconstruct the chart, and work backward to learn which source-image characteristics actually matter. We specifically want to avoid picking a Laplacian-variance blur threshold arbitrarily.

## What has been tested

- Three controlled bead grids: poppy-inspired decorative pattern, floral-green band, geometric motif.
- Gaussian blur, downsampling, JPEG compression, sensor-like noise, and exposure changes.
- 138 grid recovery results (`mesures_completes.csv`): 3 motifs × 23 degradation conditions × 2 processing modes.
- 21 full contour-SVG round-trip cases (`test_chaine_complete.csv`).
- 84 structure-aware SVG trials (`test_vectorisation_structurelle.csv`), including cases with lossless SVG round-trip relative to the reconstructed grid.
- Five photos were also reviewed qualitatively, with manual crops, but no validated physical bead-grid targets. Their source images are **not redistributed**.

## Key controlled observations

| Test, naive direct palette recovery | Poppy | Floral band | Geometric |
|---|---:|---:|---:|
| Gaussian blur σ=1.8 px (initial pitch 10 px/bead) | 100.0% | 100.0% | 100.0% |
| Blur σ=2.5 px | 62.3% | 99.9% | 100.0% |
| Downsample to 3 effective px/bead | 100.0% | 100.0% | 100.0% |
| Downsample to 2 effective px/bead | 9.9% | 74.8% | 19.6% |

These figures are **not general acceptance thresholds**: the palette, bead positions and synthetic renderer are known in advance. Exact recovery can be much harder for real handheld photographs.

**Critical failure case:** for the poppy with σ=1.2 px blur, foreground-color recovery was 100% **before** contour-to-SVG conversion but only **62.7% afterward**. A structure-aware bead-grid-to-SVG conversion can avoid introducing that additional loss. This shows why rejecting a source photo based on a downstream algorithm's failure can be misleading.

## Replication

Use Python 3.12 and a fresh virtual environment. On Windows, make Cairo available to CairoSVG before running the SVG tests. See the [CairoSVG installation guide](https://cairosvg.org/documentation/).

Run these commands from a disposable copy of the repository. The runner writes CSV and SVG outputs in place and generates previews in `exemples/`. Leave `sources/` absent for the synthetic run.

```bash
python -m venv .venv
# Activate .venv for your platform, then run:
python -m pip install -r requirements.txt
python RUN_ALL.py
```

The run was checked on Linux with Python 3.12.14. All 138 recovery rows, 21 contour round-trip rows, and 84 structure-aware rows matched the archived CSVs field for field. The runner produces synthetic previews and leaves the supplied comparison plots as archived figures. If Cairo is unavailable, use `python faiza_lab_v10.py` to run the primary recovery experiment.

| File | Contents |
| --- | --- |
| [mesures_completes.csv](mesures_completes.csv) | Synthetic grid recovery across degradation conditions |
| [test_chaine_complete.csv](test_chaine_complete.csv) | Contour-SVG round-trip measurements |
| [test_vectorisation_structurelle.csv](test_vectorisation_structurelle.csv) | Structure-aware SVG measurements |
| [validation_svg.csv](validation_svg.csv) | Historical SVG checks. Some rows refer to excluded photo-derived SVGs and lack a corresponding real-photo ground truth. The historical table is outside the current runner. |
| [protocole.json](protocole.json) | Experiment settings and seed |
| [PARAMETRES_OBSERVES.json](PARAMETRES_OBSERVES.json) | Provisional observations |
| [masters/](masters/) · [figures/](figures/) · [svg/](svg/) | Synthetic references, archived plots, and SVG outputs |

## Reproducibility and study boundaries

- The poppy master was built in an earlier Faiza experiment; it is not a validated manufacturing chart. The other two masters are constructed tests, not actual photos.
- Metrics include exact foreground color accuracy, accent recovery, foreground mask IoU, and boundary F1. **Exact color agreement is NOT beauty, plausibility, or weaving feasibility.**
- The known target palette and fixed bead pitch are advantageous test assumptions and must not be presented as real-world performance.
- Real photo segmentation was not automated or validated.
- **VTracer and ImageTracerJS were not executed** in this benchmark: the contour vectorization is an OpenCV baseline.
- No loom/peyote/brick stitch validation or artisan evaluation yet.
- We intentionally have **not** defined a universal photo-acceptance blur threshold.

## Research questions

We are requesting expert feedback in [REVIEW_REQUEST.md](REVIEW_REQUEST.md), especially from beadwork makers, computer-vision practitioners, SVG specialists, and people familiar with offline Android processing.

Detailed original report in French: [RAPPORT_FAIZA_V10_FR.md](RAPPORT_FAIZA_V10_FR.md).

### Publication scope and image rights

The reproducible synthetic test grids and our original experimental Python code are included. Private/unverified-rights reference photos (and derivatives directly depicting them) are omitted. To replicate qualitative photo tests, provide your own licensed photos under `sources/` with the expected filenames (see `faiza_lab_v10.py`). The repository contains no full Faiza application or unreleased business code. No open-source license is automatically granted by this preview: [RIGHTS_AND_SCOPE.md](RIGHTS_AND_SCOPE.md).
