# Performance plan

M0 establishes correctness and architecture; performance numbers are recorded once
Flutter is available in CI. Heavy computation is scheduled away from the UI isolate.
Plot rendering uses adaptive sampling, discontinuity segmentation, level-of-detail
and incremental repainting.

The release gate measures:

- frame build and raster timing at 60 Hz and, when available, 120 Hz;
- time to first frame and first interactive input;
- expression/plot latency for representative sample counts;
- peak memory for large plots, grids and CSV files;
- native library and application package size.

The target is a stable 60 fps core experience, best-effort 120 fps on high-refresh
hardware, and no blocking native calculation on the UI isolate.
