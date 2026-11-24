# Request for professional peer review — FAIZA LAB V10

**Context.** We are developing an offline-capable design pipeline for beadwork charts (including loom, peyote/brick variants and hanging fringes). Our requirement is *a beautiful, recognizable, actually craftable final pattern*, not pixel-perfect reproduction of a bad photograph. We want to derive image-admission criteria backward from final pattern quality, rather than hard-code arbitrary Laplacian blur cutoffs.

### What we measured

We rendered three known bead grids into synthetic bead images (10 px/bead), applied 23 degradation conditions (blur, downsampling, JPEG, noise, exposure), then evaluated two recovery treatments (138 tests). We ran 21 SVG round-trips and further structure-aware SVG checks. Our complete report, scripts and CSVs are in this repository. Five real beadwork photos were examined qualitatively, but have no verified bead-by-bead ground truth; their images are not redistributed.

Surprising finding: on a controlled poppy motif blurred at sigma 1.2 px, cell-color recovery was still 100% before contour-SVG tracing, but dropped to 62.7% after. Bead-structure-first SVG avoids this *additional* tracing error in the controlled experiment. This suggests a source photograph should not be rejected because of a failure introduced downstream by the tracer.

### Specific questions for experts

1. **Beadwork practitioners:** What objective *manufacturing* constraints must an acceptance test include (minimum connected paths, row offsets, tension, fringe anchors, peyote/brick/loom differences)? What failures would cause you to reject a pattern even if it looks attractive?
2. **Computer vision:** What metrics (edge spread, estimated smallest recoverable element, segmentation uncertainty, color ambiguity) would support a *task-dependent* photo quality gate? Which failure modes or synthetic-to-real biases are missing here?
3. **Vectorization/SVG developers:** For image→shape→grid, when is contour-based SVG appropriate, and when should the pipeline detect and reconstruct the discrete bead lattice first? Suggested methods to preserve thin parts without creating excessive paths?
4. **Design/art specialists:** How should we score recognizability, silhouette, contrast, balanced symmetry and pleasing color hierarchy without training a large model? What should be human-reviewed?
5. **Mobile/offline engineering:** What subset of this pipeline is feasible on-device for Android (memory/performance), and how to benchmark fairly?

### We particularly appreciate

- Concrete failure cases, sample photos **with usage rights**, or benchmark datasets with known charts;
- Review of the measurement method and any code mistakes;
- Suggestions for falsifiable experiments, not generic thresholds;
- Beadwork-specific critique from experienced makers.

**Important limitations:** These results do **not** establish production-ready acceptance thresholds, do **not** validate real-world photos, and do **not** claim to benchmark VTracer or ImageTracerJS.

Thank you for reviewing. Please reply to the GitHub issue/discussion with your specialty and specific recommendations.
