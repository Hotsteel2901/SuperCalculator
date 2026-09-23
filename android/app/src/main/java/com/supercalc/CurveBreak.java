package com.supercalc;

import com.github.mikephil.charting.data.Entry;

import java.util.ArrayList;
import java.util.List;
import java.util.TreeSet;

/**
 * Discontinuity handling shared by every 2D plot.
 *
 * <p>Sampled functions such as {@code tan(x)} or {@code 1/x} have poles where
 * the value jumps from +infinity to -infinity between two adjacent samples.
 * MPAndroidChart's {@link com.github.mikephil.charting.data.LineDataSet} cannot
 * break a polyline at a NaN, so feeding it the raw samples draws a bogus
 * near-vertical line across the asymptote (and every {@code tan} branch ends up
 * with a slightly different height).</p>
 *
 * <p>This helper detects those break points against the <em>visible</em> y-band
 * (so the result does not depend on the sampling density) and splits the curve
 * into independent segments. Callers draw one {@code LineDataSet} per segment,
 * which produces a clean gap at every pole.</p>
 */
public final class CurveBreak {

    /** A jump must clear this fraction of the visible band to count as a break. */
    private static final double BAND_FRAC = 0.5;
    /** ... and dwarf the curve's typical step by this factor. */
    private static final double JUMP_FACTOR = 6.0;
    private static final double MIN_ABS = 1e-9;

    /**
     * Edge in a {@link Mesh} is drawn only when the two samples do not differ by
     * more than this fraction of the visible z-band. A pole in {@code 1/(x*y)}
     * makes neighbours leap across the whole band; those edges are exactly the
     * bogus spikes we must not draw.
     */
    private static final float MESH_EDGE_FRAC = 0.5f;

    /**
     * A 3D sample is blanked when it differs from the mean of its four immediate
     * neighbours by more than this multiple of the typical adjacent-sample
     * difference. Catches {@code 1/(x*y)}-style samples that land almost on a
     * pole.
     */
    private static final double CONTRAST_FACTOR = 6.0;

    private CurveBreak() { }

    /**
     * A 3D surface grid after pole handling: missing samples are {@code NaN} and
     * low/high masks mark which grid line each sample may connect to.
     *
     * <p>Unlike 2D there is no "split into segments" notion here — the grid keeps
     * its {@code rows x cols} shape and we only decide, per edge, whether it may
     * be drawn. That still tears the wireframe apart at every pole.</p>
     */
    public static final class Mesh {
        public final float[][] z;
        public final boolean[][] lowOk;
        public final boolean[][] highOk;

        Mesh(int rows, int cols) {
            z = new float[rows][cols];
            lowOk = new boolean[rows][cols];
            highOk = new boolean[rows][cols];
        }

        public boolean isEmpty() { return z.length == 0 || z[0].length == 0; }
        public int rows() { return z.length; }
        public int cols() { return z.length == 0 ? 0 : z[0].length; }
    }

    /** A polyline segment: parallel arrays of x and y in sample order. */
    public static final class Segment {
        public final ArrayList<Float> xs = new ArrayList<>();
        public final ArrayList<Float> ys = new ArrayList<>();

        public boolean isEmpty() { return xs.size() < 1; }

        public int size() { return xs.size(); }

        public ArrayList<Entry> toEntries() {
            ArrayList<Entry> out = new ArrayList<>(xs.size());
            for (int i = 0; i < xs.size(); i++) {
                out.add(new Entry(xs.get(i), ys.get(i)));
            }
            return out;
        }
    }

    /**
     * Split sampled (xs, ys) into continuous {@link Segment}s.
     *
     * @param xs     sample abscissae (aligned with ys)
     * @param ys     sample values (NaN / infinite allowed, treated as a gap)
     * @param yLo    visible lower y bound (pass NaN to auto-detect)
     * @param yHi    visible upper y bound (pass NaN to auto-detect)
     * @return list of segments; never null, may be empty
     */
    public static List<Segment> split(double[] xs, double[] ys, double yLo, double yHi) {
        List<Segment> out = new ArrayList<>();
        if (xs == null || ys == null || xs.length == 0 || xs.length != ys.length) {
            return out;
        }
        int n = ys.length;

        // Collect finite adjacent pairs for a robust scale estimate.
        boolean haveBand = isFinite(yLo) && isFinite(yHi) && yHi > yLo;
        double lo = yLo, hi = yHi;
        if (!haveBand) {
            double mn = Double.POSITIVE_INFINITY, mx = Double.NEGATIVE_INFINITY;
            for (double y : ys) {
                if (isFinite(y)) { if (y < mn) mn = y; if (y > mx) mx = y; }
            }
            if (!isFinite(mn) || !isFinite(mx)) { return out; }
            lo = mn; hi = mx;
        }
        double span = hi - lo;
        if (!isFinite(span) || span <= 0) span = 1.0;
        double blo = lo - 0.10 * span, bhi = hi + 0.10 * span;

        // Median of |dy| across finite adjacent pairs.
        ArrayList<Double> jumps = new ArrayList<>();
        for (int i = 1; i < n; i++) {
            if (isFinite(ys[i - 1]) && isFinite(ys[i])) {
                jumps.add(Math.abs(ys[i] - ys[i - 1]));
            }
        }
        double median = MIN_ABS;
        if (!jumps.isEmpty()) {
            java.util.Collections.sort(jumps);
            median = jumps.get(jumps.size() / 2);
        }
        double bandThresh = BAND_FRAC * span;
        double jumpThresh = Math.max(JUMP_FACTOR * median, MIN_ABS);

        TreeSet<Integer> breaks = new TreeSet<>();
        for (int i = 1; i < n; i++) {
            if (!isFinite(ys[i - 1]) || !isFinite(ys[i])) continue;
            double a = ys[i - 1], b = ys[i];
            boolean ao = a < blo || a > bhi;
            boolean bo = b < blo || b > bhi;
            boolean d = Math.abs(b - a) > bandThresh;
            if (ao && bo) {
                if ((a < 0) != (b < 0) || (a > bhi && b < blo) || (a < blo && b > bhi)) {
                    breaks.add(i);
                }
            } else if ((ao || bo) && d) {
                breaks.add(i);
            } else if (d && Math.abs(b - a) > jumpThresh && (a < 0) != (b < 0)) {
                breaks.add(i);
            }
        }
        // Collapse runs of adjacent breaks into a single gap.
        TreeSet<Integer> collapsed = new TreeSet<>();
        Integer prev = null;
        for (Integer idx : breaks) {
            if (prev == null || idx - prev > 1) collapsed.add(idx);
            prev = idx;
        }

        Segment cur = new Segment();
        for (int i = 0; i < n; i++) {
            if (i > 0 && collapsed.contains(i) && !cur.isEmpty()) {
                out.add(cur);
                cur = new Segment();
            }
            double xv = xs[i], yv = ys[i];
            if (!isFinite(xv) || !isFinite(yv)) {
                if (!cur.isEmpty()) { out.add(cur); cur = new Segment(); }
                continue;
            }
            cur.xs.add((float) xv);
            cur.ys.add((float) yv);
        }
        if (!cur.isEmpty()) out.add(cur);

        return out;
    }

    /**
     * Split a polyline into segments where <em>either</em> coordinate jumps.
     * Used for parametric / polar curves.
     */
    public static List<Segment> splitXY(double[] xs, double[] ys) {
        List<Segment> out = new ArrayList<>();
        if (xs == null || ys == null || xs.length == 0 || xs.length != ys.length) {
            return out;
        }
        // Union of breaks detected on x (band = x range) and on y (band = y range).
        TreeSet<Integer> breaks = new TreeSet<>();
        breaks.addAll(breakIndices(xs, ys));
        breaks.addAll(breakIndices(ys, xs));

        TreeSet<Integer> collapsed = new TreeSet<>();
        Integer prev = null;
        for (Integer idx : breaks) {
            if (prev == null || idx - prev > 1) collapsed.add(idx);
            prev = idx;
        }

        Segment cur = new Segment();
        for (int i = 0; i < xs.length; i++) {
            if (i > 0 && collapsed.contains(i)) {
                if (!cur.isEmpty()) { out.add(cur); cur = new Segment(); }
            }
            if (!isFinite(xs[i]) || !isFinite(ys[i])) {
                if (!cur.isEmpty()) { out.add(cur); cur = new Segment(); }
                continue;
            }
            cur.xs.add((float) xs[i]);
            cur.ys.add((float) ys[i]);
        }
        if (!cur.isEmpty()) out.add(cur);
        return out;
    }

    /** Break indices when {@code ys} is tested against its own range. */
    private static TreeSet<Integer> breakIndices(double[] xs, double[] ys) {
        TreeSet<Integer> res = new TreeSet<>();
        int n = ys.length;
        if (n < 2) return res;
        double mn = Double.POSITIVE_INFINITY, mx = Double.NEGATIVE_INFINITY;
        for (double y : ys) {
            if (isFinite(y)) { if (y < mn) mn = y; if (y > mx) mx = y; }
        }
        if (!isFinite(mn) || !isFinite(mx)) return res;
        double span = mx - mn;
        if (span <= 0) span = 1.0;
        double blo = mn - 0.10 * span, bhi = mx + 0.10 * span;
        List<Double> jumps = new ArrayList<>();
        for (int i = 1; i < n; i++) {
            if (isFinite(ys[i - 1]) && isFinite(ys[i])) {
                jumps.add(Math.abs(ys[i] - ys[i - 1]));
            }
        }
        double median = MIN_ABS;
        if (!jumps.isEmpty()) {
            java.util.Collections.sort(jumps);
            median = jumps.get(jumps.size() / 2);
        }
        double bandThresh = BAND_FRAC * span;
        double jumpThresh = Math.max(JUMP_FACTOR * median, MIN_ABS);
        for (int i = 1; i < n; i++) {
            if (!isFinite(ys[i - 1]) || !isFinite(ys[i])) continue;
            double a = ys[i - 1], b = ys[i];
            boolean ao = a < blo || a > bhi, bo = b < blo || b > bhi;
            boolean d = Math.abs(b - a) > bandThresh;
            if (ao && bo && (a < 0) != (b < 0)) {
                res.add(i);
            } else if ((ao || bo) && d) {
                res.add(i);
            } else if (d && Math.abs(b - a) > jumpThresh && (a < 0) != (b < 0)) {
                res.add(i);
            }
        }
        return res;
    }

    private static boolean isFinite(double v) {
        return !Double.isNaN(v) && !Double.isInfinite(v);
    }

    /**
     * Insert extra sample abscissae right next to every detected pole.
     *
     * <p>Uniform sampling of {@code tan(x)} truncates each branch at whichever
     * sample lands closest to the pole, so the branches end up at different
     * heights.  Adding a few geometrically-closer samples on both sides of each
     * pole lets every branch reach the same clipped extremum.</p>
     *
     * @param xs   uniform sample abscissae
     * @param ys   matching values (NaN allowed)
     * @param yLo  visible lower bound (NaN to auto-detect)
     * @param yHi  visible upper bound (NaN to auto-detect)
     * @param extra how many extra samples per side (e.g. 8)
     * @return a new sorted abscissa array, or the original if nothing to add
     */
    public static double[] refineNearPoles(double[] xs, double[] ys,
                                           double yLo, double yHi, int extra) {
        if (xs == null || ys == null || xs.length < 3 || xs.length != ys.length) {
            return xs;
        }
        // Reuse the break detection to find pole locations.
        boolean haveBand = isFinite(yLo) && isFinite(yHi) && yHi > yLo;
        TreeSet<Integer> breaks = haveBand
                ? breakIndicesBand(xs, ys, yLo, yHi)
                : breakIndices(xs, ys);
        if (breaks.isEmpty()) return xs;

        java.util.TreeSet<Double> merged = new java.util.TreeSet<>();
        for (double v : xs) merged.add(v);

        int n = xs.length;
        for (Integer idx : breaks) {
            if (idx <= 0 || idx >= n) continue;
            double xLeft = xs[idx - 1], xRight = xs[idx];
            double gap = xRight - xLeft;
            if (gap <= 0) continue;
            for (int k = 1; k <= extra; k++) {
                double frac = Math.pow(0.5, k);
                merged.add(xLeft + gap * frac);
                merged.add(xRight - gap * frac);
            }
        }

        if (merged.size() == n) return xs;
        double[] out = new double[merged.size()];
        int i = 0;
        for (double v : merged) out[i++] = v;
        return out;
    }

    /** Break indices detected against an explicit visible band. */
    private static TreeSet<Integer> breakIndicesBand(double[] xs, double[] ys,
                                                     double yLo, double yHi) {
        TreeSet<Integer> res = new TreeSet<>();
        int n = ys.length;
        double span = yHi - yLo;
        if (span <= 0) span = 1.0;
        double blo = yLo - 0.10 * span, bhi = yHi + 0.10 * span;

        ArrayList<Double> jumps = new ArrayList<>();
        for (int i = 1; i < n; i++) {
            if (isFinite(ys[i - 1]) && isFinite(ys[i])) {
                jumps.add(Math.abs(ys[i] - ys[i - 1]));
            }
        }
        double median = MIN_ABS;
        if (!jumps.isEmpty()) {
            java.util.Collections.sort(jumps);
            median = jumps.get(jumps.size() / 2);
        }
        double bandThresh = BAND_FRAC * span;
        double jumpThresh = Math.max(JUMP_FACTOR * median, MIN_ABS);

        for (int i = 1; i < n; i++) {
            if (!isFinite(ys[i - 1]) || !isFinite(ys[i])) continue;
            double a = ys[i - 1], b = ys[i];
            boolean ao = a < blo || a > bhi, bo = b < blo || b > bhi;
            double d = Math.abs(b - a);
            if (ao && bo) {
                if ((a < 0) != (b < 0) || (a > bhi && b < blo) || (a < blo && b > bhi)) {
                    res.add(i);
                }
            } else if ((ao || bo) && d > bandThresh) {
                res.add(i);
            } else if (d > bandThresh && d > jumpThresh && (a < 0) != (b < 0)) {
                res.add(i);
            }
        }
        TreeSet<Integer> collapsed = new TreeSet<>();
        Integer prev = null;
        for (Integer idx : res) {
            if (prev == null || idx - prev > 1) collapsed.add(idx);
            prev = idx;
        }
        return collapsed;
    }

    // ------------------------------------------------------------------
    // 3D surface culling
    // ------------------------------------------------------------------

    /**
     * Clean up a 3D surface grid for wireframe drawing.
     *
     * <p>Two things tear the wireframe cleanly at a pole:</p>
     * <ol>
     *   <li>blank samples that explode relative to their four neighbours, and</li>
     *   <li>refuse the <em>edges</em> that span more than half the visible z-band.</li>
     * </ol>
     *
     * <p>Step 2 matters because a pole rarely lands exactly on a sample: for
     * {@code tan(x)} the nearest column only reaches ~30-60, which is not a spike
     * on its own, yet the edge joining it to the opposite branch jumps by far
     * more than half the band. Leaving such edges in is the "bogus line"
     * artefact.</p>
     *
     * <p>Judging a jump against half the <em>visible band</em> (rather than
     * against the local neighbour scale) is what keeps a steep-but-smooth
     * surface such as {@code 50*sin(3x)cos(3y)} or {@code x+2y} intact while
     * still tearing {@code tan(x)} and {@code 1/(x*y)}.</p>
     *
     * @param z         surface samples, {@code rows x cols}
     * @param zLo       low end of the visible z-band
     * @param zHi       high end of the visible z-band
     * @param magnitude unused legacy flag, kept for call-site compatibility
     */
    public static Mesh cull3D(float[][] z, float zLo, float zHi, boolean magnitude) {
        if (z == null || z.length == 0 || z[0].length == 0) {
            return new Mesh(0, 0);
        }
        int rows = z.length;
        int cols = z[0].length;
        Mesh mesh = new Mesh(rows, cols);

        boolean haveBand = !Float.isNaN(zLo) && !Float.isNaN(zHi) && zHi > zLo;
        double band = haveBand ? (double) (zHi - zLo) : 0.0;

        // Typical local variation: the 98th percentile of adjacent-sample
        // differences.  The median collapses to ~0 on a mostly-flat surface and
        // would make a smooth Gaussian peak look spiky, so it is the wrong
        // statistic for judging "does this sample explode".
        double nbScale = neighbourScale(z, rows, cols);

        // Blank samples that tower over the median of their four immediate
        // neighbours.  The median (not the mean) is essential: a mean is dragged
        // around by the very pole we are hunting, which mis-flags the pole's
        // innocent neighbours and tears a smooth surface.
        double contrastLimit = nbScale > 0 ? CONTRAST_FACTOR * nbScale : Double.POSITIVE_INFINITY;
        double[] nb = new double[4];
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                float v = z[i][j];
                if (Float.isNaN(v) || Float.isInfinite(v)) {
                    mesh.z[i][j] = Float.NaN;
                    continue;
                }
                int cnt = 0;
                if (i > 0 && isFinite(z[i - 1][j])) nb[cnt++] = z[i - 1][j];
                if (i + 1 < rows && isFinite(z[i + 1][j])) nb[cnt++] = z[i + 1][j];
                if (j > 0 && isFinite(z[i][j - 1])) nb[cnt++] = z[i][j - 1];
                if (j + 1 < cols && isFinite(z[i][j + 1])) nb[cnt++] = z[i][j + 1];
                if (cnt > 0) {
                    double nbMed = medianOf(nb, cnt);
                    if (Math.abs(v - nbMed) > contrastLimit) {
                        mesh.z[i][j] = Float.NaN;
                        continue;
                    }
                }
                mesh.z[i][j] = v;
            }
        }

        // Refuse edges that span more than half the visible band.
        float edgeLimit = haveBand ? (float) (MESH_EDGE_FRAC * band) : Float.POSITIVE_INFINITY;
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                mesh.highOk[i][j] = mayConnect(mesh.z, i, j, i, j + 1, edgeLimit);
                mesh.lowOk[i][j] = mayConnect(mesh.z, i, j, i + 1, j, edgeLimit);
            }
        }
        return mesh;
    }

    /** Median of the first {@code n} entries of {@code a}. */
    private static double medianOf(double[] a, int n) {
        double[] c = new double[n];
        System.arraycopy(a, 0, c, 0, n);
        java.util.Arrays.sort(c);
        if ((n & 1) == 1) return c[n / 2];
        return 0.5 * (c[n / 2 - 1] + c[n / 2]);
    }

    /** 98th-percentile absolute difference between adjacent samples. */
    private static double neighbourScale(float[][] z, int rows, int cols) {
        ArrayList<Double> diffs = new ArrayList<>();
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j + 1 < cols; j++) {
                if (isFinite(z[i][j]) && isFinite(z[i][j + 1])) {
                    diffs.add(Math.abs((double) z[i][j + 1] - z[i][j]));
                }
            }
        }
        for (int i = 0; i + 1 < rows; i++) {
            for (int j = 0; j < cols; j++) {
                if (isFinite(z[i][j]) && isFinite(z[i + 1][j])) {
                    diffs.add(Math.abs((double) z[i + 1][j] - z[i][j]));
                }
            }
        }
        if (diffs.isEmpty()) return 0.0;
        java.util.Collections.sort(diffs);
        double s = percentile(diffs, 98.0);
        if (!isFinite(s) || s <= 0) s = diffs.get(diffs.size() - 1);
        return s;
    }

    /**
     * {@code true} when the edge to the given neighbour should be drawn: both
     * endpoints are finite and their values stay within {@code edgeLimit} of each
     * other. Neighbours are given in row/col coordinates; out-of-range indices
     * simply yield {@code false}.
     */
    public static boolean mayConnect(float[][] z, int r1, int c1, int r2, int c2, float edgeLimit) {
        if (r1 < 0 || c1 < 0 || r2 < 0 || c2 < 0) return false;
        if (r1 >= z.length || r2 >= z.length) return false;
        if (c1 >= z[0].length || c2 >= z[0].length) return false;
        float a = z[r1][c1];
        float b = z[r2][c2];
        if (Float.isNaN(a) || Float.isNaN(b)) return false;
        return Math.abs(b - a) <= edgeLimit;
    }

    /** Linear-interpolated percentile of a pre-sorted list. */
    private static double percentile(java.util.List<Double> sorted, double pct) {
        int n = sorted.size();
        if (n == 0) return 0.0;
        if (n == 1) return sorted.get(0);
        double rank = (pct / 100.0) * (n - 1);
        int lo = (int) Math.floor(rank);
        int hi = (int) Math.ceil(rank);
        if (lo == hi) return sorted.get(lo);
        double frac = rank - lo;
        return sorted.get(lo) * (1 - frac) + sorted.get(hi) * frac;
    }
}
