package com.supercalc;

import android.content.Context;

/**
 * Statistical Distribution Calculator for Android.
 * Implements common probability distributions:
 * - Normal (Gaussian)
 * - Student's t
 * - Chi-squared
 * - F-distribution
 * - Binomial
 * - Poisson
 */
public class StatDistCalc {

    public enum DistType {
        NORMAL, T, CHI2, F, BINOMIAL, POISSON
    }

    public static String[] getDistributionNames(Context context) {
        return new String[]{
            context.getString(R.string.dist_normal),
            context.getString(R.string.dist_t),
            context.getString(R.string.dist_chi2),
            context.getString(R.string.dist_f),
            context.getString(R.string.dist_binomial),
            context.getString(R.string.dist_poisson)
        };
    }

    public static DistType fromName(Context context, String name) {
        if (name.equals(context.getString(R.string.dist_normal))) return DistType.NORMAL;
        if (name.equals(context.getString(R.string.dist_t))) return DistType.T;
        if (name.equals(context.getString(R.string.dist_chi2))) return DistType.CHI2;
        if (name.equals(context.getString(R.string.dist_f))) return DistType.F;
        if (name.equals(context.getString(R.string.dist_binomial))) return DistType.BINOMIAL;
        if (name.equals(context.getString(R.string.dist_poisson))) return DistType.POISSON;
        return DistType.NORMAL;
    }

    // PDF / PMF
    public static double pdf(DistType type, double x, double... params) {
        switch (type) {
            case NORMAL:
                if (params.length < 2) return Double.NaN;
                return normalPdf(x, params[0], params[1]);
            case T:
                if (params.length < 1) return Double.NaN;
                return tPdf(x, (int) params[0]);
            case CHI2:
                if (params.length < 1) return Double.NaN;
                return chi2Pdf(x, (int) params[0]);
            case F:
                if (params.length < 2) return Double.NaN;
                return fPdf(x, params[0], params[1]);
            case BINOMIAL:
                if (params.length < 2) return Double.NaN;
                return binomialPmf((int) x, (int) params[0], params[1]);
            case POISSON:
                if (params.length < 1) return Double.NaN;
                return poissonPmf((int) x, params[0]);
            default: return Double.NaN;
        }
    }

    // CDF
    public static double cdf(DistType type, double x, double... params) {
        switch (type) {
            case NORMAL:
                if (params.length < 2) return Double.NaN;
                return normalCdf(x, params[0], params[1]);
            case T:
                if (params.length < 1) return Double.NaN;
                return tCdf(x, (int) params[0]);
            case CHI2:
                if (params.length < 1) return Double.NaN;
                return chi2Cdf(x, (int) params[0]);
            case F:
                if (params.length < 2) return Double.NaN;
                return fCdf(x, params[0], params[1]);
            case BINOMIAL:
                if (params.length < 2) return Double.NaN;
                return binomialCdf((int) x, (int) params[0], params[1]);
            case POISSON:
                if (params.length < 1) return Double.NaN;
                return poissonCdf((int) x, params[0]);
            default: return Double.NaN;
        }
    }

    // --- Normal Distribution ---
    private static double normalPdf(double x, double mu, double sigma) {
        if (sigma <= 0) return Double.NaN;
        double z = (x - mu) / sigma;
        return Math.exp(-0.5 * z * z) / (sigma * Math.sqrt(2 * Math.PI));
    }

    private static double normalCdf(double x, double mu, double sigma) {
        if (sigma <= 0) return Double.NaN;
        return 0.5 * (1.0 + erf((x - mu) / (sigma * Math.sqrt(2))));
    }

    // --- Student's t-distribution ---
    private static double tPdf(double x, int nu) {
        if (nu < 1) return Double.NaN;
        double coeff = Math.exp(logGamma((nu + 1.0) / 2.0) - logGamma(nu / 2.0))
                / (Math.sqrt(nu * Math.PI));
        return coeff * Math.pow(1.0 + x * x / nu, -(nu + 1.0) / 2.0);
    }

    private static double tCdf(double x, int nu) {
        if (nu < 1) return Double.NaN;
        // Use numerical integration (trapezoidal) from 0 to x, plus 0.5 offset
        // to get integral from -infinity to x
        if (x > 10) return 1.0;
        if (x < -10) return 0.0;
        int n = 2000;
        double h = x / n;
        double sum = tPdf(0, nu) / 2.0;
        for (int i = 1; i < n; i++) {
            sum += tPdf(i * h, nu);
        }
        sum += tPdf(x, nu) / 2.0;
        return sum * h + 0.5;
    }

    // --- Chi-squared distribution ---
    private static double chi2Pdf(double x, int k) {
        if (k < 1) return Double.NaN;
        if (x <= 0) return 0.0;
        double logPdf = (k / 2.0 - 1) * Math.log(x) - x / 2.0
                - (k / 2.0) * Math.log(2.0) - logGamma(k / 2.0);
        return Math.exp(logPdf);
    }

    private static double chi2Cdf(double x, int k) {
        if (k < 1) return Double.NaN;
        if (x <= 0) return 0.0;
        return lowerIncompleteGamma(k / 2.0, x / 2.0);
    }

    // --- F-distribution ---
    private static double fPdf(double x, double d1, double d2) {
        if (Double.isNaN(d1) || Double.isNaN(d2) || Double.isNaN(x)) return Double.NaN;
        if (d1 < 1 || d2 < 1) return Double.NaN;
        if (x <= 0) return 0.0;
        double logPdf = (d1 / 2.0) * Math.log(d1) + (d2 / 2.0) * Math.log(d2)
                + ((d1 / 2.0) - 1) * Math.log(x)
                - ((d1 + d2) / 2.0) * Math.log(d1 * x + d2)
                + logGamma((d1 + d2) / 2.0)
                - logGamma(d1 / 2.0) - logGamma(d2 / 2.0);
        return Math.exp(logPdf);
    }

    private static double fCdf(double x, double d1, double d2) {
        if (Double.isNaN(d1) || Double.isNaN(d2) || Double.isNaN(x)) return Double.NaN;
        if (d1 < 1 || d2 < 1) return Double.NaN;
        if (x <= 0) return 0.0;
        double z = d1 * x / (d1 * x + d2);
        return incompleteBeta(d1 / 2.0, d2 / 2.0, z);
    }

    // --- Binomial distribution ---
    private static double binomialPmf(int k, int n, double p) {
        if (n < 0 || p < 0 || p > 1) return Double.NaN;
        if (k < 0 || k > n) return 0.0;
        if (p == 0.0) return (k == 0) ? 1.0 : 0.0;
        if (p == 1.0) return (k == n) ? 1.0 : 0.0;
        double logPmf = logGamma(n + 1) - logGamma(k + 1) - logGamma(n - k + 1)
                + k * Math.log(p) + (n - k) * Math.log(1 - p);
        return Math.exp(logPmf);
    }

    private static double binomialCdf(int k, int n, double p) {
        if (k < 0) return 0.0;
        if (k >= n) return 1.0;
        double sum = 0.0;
        for (int i = 0; i <= k; i++) {
            sum += binomialPmf(i, n, p);
        }
        return Math.min(sum, 1.0);
    }

    // --- Poisson distribution ---
    private static double poissonPmf(int k, double lambda) {
        if (lambda < 0) return Double.NaN;
        if (k < 0) return 0.0;
        if (lambda == 0.0) return (k == 0) ? 1.0 : 0.0;
        double logPmf = k * Math.log(lambda) - lambda - logGamma(k + 1);
        return Math.exp(logPmf);
    }

    private static double poissonCdf(int k, double lambda) {
        if (k < 0) return 0.0;
        double sum = 0.0;
        for (int i = 0; i <= k; i++) {
            sum += poissonPmf(i, lambda);
        }
        return Math.min(sum, 1.0);
    }

    // --- Helper functions ---

    // Lanczos approximation for log(Gamma)
    private static double logGamma(double z) {
        if (Double.isNaN(z)) return Double.NaN;
        if (z <= 0.0 && z == Math.floor(z)) {
            return Double.POSITIVE_INFINITY;
        }
        if (z < 0.5) {
            return Math.log(Math.PI / Math.sin(Math.PI * z)) - logGamma(1.0 - z);
        }
        z -= 1.0;
        double[] c = {0.99999999999980993, 676.5203681218851, -1259.1392167224028,
                771.32342877765313, -176.61502916214059, 12.507343278686905,
                -0.13857109526572012, 9.9843695780195716e-6, 1.5056327351493116e-7};
        double x = c[0];
        for (int k = 1; k < c.length; k++) {
            x += c[k] / (z + k);
        }
        double t = z + 7 + 0.5;
        return 0.5 * Math.log(2 * Math.PI) + (z + 0.5) * Math.log(t) - t + Math.log(x);
    }

    // Error function approximation (Abramowitz & Stegun 7.1.26)
    private static double erf(double x) {
        double sign = (x >= 0) ? 1.0 : -1.0;
        x = Math.abs(x);
        double t = 1.0 / (1.0 + 0.3275911 * x);
        double y = 1.0 - (((((1.061405429 * t - 1.453152027) * t + 1.421413741) * t
                - 0.284496736) * t + 0.254829592) * t) * Math.exp(-x * x);
        return sign * y;
    }

    // Lower regularized incomplete gamma P(a, x)
    private static double lowerIncompleteGamma(double a, double x) {
        if (a <= 0) return Double.NaN;
        if (x <= 0) return 0.0;
        if (x < a + 1) {
            // Series
            double ap = a;
            double sum = 1.0 / a;
            double delta = sum;
            for (int n = 1; n < 200; n++) {
                ap += 1.0;
                delta *= x / ap;
                sum += delta;
                if (Math.abs(delta) < Math.abs(sum) * 1e-15) break;
            }
            return sum * Math.exp(-x + a * Math.log(x) - logGamma(a));
        } else {
            // Continued fraction
            double b = x + 1.0 - a;
            double c = 1e30;
            double d = 1.0 / b;
            double h = d;
            for (int i = 1; i < 200; i++) {
                double an = -i * (i - a);
                b += 2.0;
                d = an * d + b;
                if (Math.abs(d) < 1e-30) d = 1e-30;
                c = b + an / c;
                if (Math.abs(c) < 1e-30) c = 1e-30;
                d = 1.0 / d;
                double delta = d * c;
                h *= delta;
                if (Math.abs(delta - 1.0) < 1e-10) break;
            }
            return 1.0 - h * Math.exp(-x + a * Math.log(x) - logGamma(a));
        }
    }

    // Regularized incomplete beta I_x(a, b)
    private static double incompleteBeta(double a, double b, double x) {
        if (a <= 0 || b <= 0) return Double.NaN;
        if (x <= 0) return 0.0;
        if (x >= 1) return 1.0;
        if (x > (a + 1) / (a + b + 2)) {
            return 1.0 - incompleteBeta(b, a, 1.0 - x);
        }
        double lbeta = logGamma(a) + logGamma(b) - logGamma(a + b);
        double front = Math.exp(Math.log(x) * a + Math.log(1.0 - x) * b + lbeta) / a;
        // Lentz's continued fraction
        double f = 1.0, c = 1.0, d = 1.0 - (a + b) * x / (a + 1);
        if (Math.abs(d) < 1e-30) d = 1e-30;
        d = 1.0 / d;
        f = d;
        for (int m = 1; m < 200; m++) {
            double num1 = m * (b - m) * x / ((a + 2 * m - 1) * (a + 2 * m));
            d = 1.0 + num1 * d;
            if (Math.abs(d) < 1e-30) d = 1e-30;
            c = 1.0 + num1 / c;
            if (Math.abs(c) < 1e-30) c = 1e-30;
            d = 1.0 / d;
            f *= c * d;
            double num2 = -(a + m) * (a + b + m) * x / ((a + 2 * m) * (a + 2 * m + 1));
            d = 1.0 + num2 * d;
            if (Math.abs(d) < 1e-30) d = 1e-30;
            c = 1.0 + num2 / c;
            if (Math.abs(c) < 1e-30) c = 1e-30;
            d = 1.0 / d;
            double delta = c * d;
            f *= delta;
            if (Math.abs(delta - 1.0) < 1e-10) break;
        }
        return front * f;
    }
}
