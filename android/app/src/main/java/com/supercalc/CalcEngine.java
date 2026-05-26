package com.supercalc;

/**
 * JNI bridge to the C core (libcalc_core.so).
 * All methods are static — no instance needed.
 */
public class CalcEngine {
    static { System.loadLibrary("calc_core"); }

    /** Evaluate f(x) at a point. Returns NaN on error. */
    public static native double evaluate(String expr, double x);

    /** Evaluate f(x,y) at given x and y. Returns NaN on error. */
    public static native double evaluateXY(String expr, double x, double y);

    /** First derivative f'(x) at x with step h. */
    public static native double derivative(String expr, double x, double h);

    /** Second derivative f''(x) at x with step h. */
    public static native double derivative2(String expr, double x, double h);

    /** Definite integral over [a,b] (adaptive). */
    public static native double integrate(String expr, double a, double b);

    /** Find root f(x)=0 using Newton-Raphson + bisection. */
    public static native double solve(String expr, double guess,
                                      double xmin, double xmax);

    /** Evaluate f(x) for multiple x values. */
    public static native double[] evaluateArray(String expr, double[] xs);

    /** Find a local minimum of f(x) on [a, b]. */
    public static native double findMinimum(String expr, double a, double b);

    /** Find a local maximum of f(x) on [a, b]. */
    public static native double findMaximum(String expr, double a, double b);

    /** Find root using bisection method (requires sign change on [a,b]). */
    public static native double solveBisection(String expr, double a, double b);

    /** Last error message from the C core. */
    public static native String getLastError();
}
