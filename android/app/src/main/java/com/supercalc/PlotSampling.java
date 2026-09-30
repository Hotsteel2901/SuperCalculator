package com.supercalc;

/**
 * Sampling policy shared by every plotting surface (2D line plots and 3D
 * parametric grids, on both the inline and full-screen activities).
 *
 * <p>Why this exists: sample counts used to be hard-coded -- a fixed step size
 * with a hard ceiling of 1500 (2D) and a fixed 120x120 grid (3D). That works
 * at small ranges and falls apart at large ones, because a <em>constant</em>
 * number of samples spread over a wider interval means less detail per unit of
 * x. Concretely, {@code tan(x)} over {@code [-10,10]} got ~157 samples per
 * branch; over {@code [-100,100]} only ~47; over {@code [-1000,1000]} barely
 * 2.4 -- so the branches aliased into a comb of vertical strokes and the plot
 * looked broken even though the discontinuity detection was correct.
 *
 * <p>The fix is to hold density constant in <em>data</em> units. Enlarging the
 * range then adds samples proportionally.
 */
public final class PlotSampling {

    private PlotSampling() {}

    /** Samples per unit of x. 200 over a span of 20 gives 4000 samples. */
    public static final double SAMPLES_PER_UNIT_2D = 200.0;

    /** Never sample a 2D curve more coarsely than this, however narrow the window. */
    public static final int MIN_SAMPLES_2D = 2000;

    /**
     * Upper bound for 2D. Generous because a single curve is cheap to evaluate
     * (the engine batches the whole array in one JNI call), and because
     * {@code tan(x)} over a range like [-1000,1000] genuinely needs six figures
     * of samples to resolve individual branches.
     */
    public static final int MAX_SAMPLES_2D = 200000;

    /** Grid edge length per unit of x/y for 3D surfaces. */
    public static final double SAMPLES_PER_UNIT_3D = 24.0;

    /** 3D grid floor: 3D cost is quadratic, so it cannot scale down freely. */
    public static final int MIN_SAMPLES_3D = 60;

    /**
     * 3D grid ceiling. Above this the surface has far more vertices than the
     * screen has pixels and the extra samples only cost time.
     */
    public static final int MAX_SAMPLES_3D = 240;

    /**
     * Number of 2D abscissae covering {@code [xMin, xMax]}.
     *
     * <p>Density is held constant in data units, so the result grows linearly
     * with the span until it hits {@link #MAX_SAMPLES_2D}.
     */
    public static int sampleCount2D(double xMin, double xMax) {
        return target((xMax - xMin), SAMPLES_PER_UNIT_2D,
                      MIN_SAMPLES_2D, MAX_SAMPLES_2D);
    }

    /**
     * Number of 3D grid columns/rows covering {@code [xMin, xMax]}.
     *
     * @param xMin    visible x lower bound
     * @param xMax    visible x upper bound
     * @param userPts resolution the user explicitly requested; the automatic
     *                density may only ever <em>raise</em> this, never lower it,
     *                so an explicit request is always honoured
     */
    public static int sampleCount3D(double xMin, double xMax, int userPts) {
        int auto = target((xMax - xMin), SAMPLES_PER_UNIT_3D,
                          MIN_SAMPLES_3D, MAX_SAMPLES_3D);
        return Math.max(MIN_SAMPLES_3D,
                        Math.min(MAX_SAMPLES_3D, Math.max(userPts, auto)));
    }

    /** Convenience overload using the default 3D density with no user request. */
    public static int sampleCount3D(double xMin, double xMax) {
        return target((xMax - xMin), SAMPLES_PER_UNIT_3D,
                      MIN_SAMPLES_3D, MAX_SAMPLES_3D);
    }

    private static int target(double span, double perUnit, int floor, int ceiling) {
        if (Double.isNaN(span) || Double.isInfinite(span) || span <= 0) {
            return ceiling;
        }
        // Guard against overflow before the cast: span * perUnit can exceed
        // Integer.MAX_VALUE for absurd ranges (e.g. [-1e9, 1e9]).
        double wanted = span * perUnit + 1.0;
        if (wanted >= ceiling) {
            return ceiling;
        }
        int n = (int) Math.round(wanted);
        return Math.max(floor, Math.min(ceiling, n));
    }
}
