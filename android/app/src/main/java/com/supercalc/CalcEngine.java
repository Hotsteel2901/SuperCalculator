package com.supercalc;

import java.util.HashMap;

/**
 * JNI bridge to the C core (libcalc_core.so).
 * All methods are static — no instance needed.
 */
public class CalcEngine {
    static {
        try {
            System.loadLibrary("calc_core");
        } catch (UnsatisfiedLinkError e) {
            throw new RuntimeException("Failed to load calc_core native library", e);
        }
    }

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

    /** Evaluate f(x,y) for multiple (x,y) pairs. xs and ys must have the same length. */
    public static native double[] evaluateXYArray(String expr, double[] xs, double[] ys);

    /** Find a local minimum of f(x) on [a, b]. */
    public static native double findMinimum(String expr, double a, double b);

    /** Find a local maximum of f(x) on [a, b]. */
    public static native double findMaximum(String expr, double a, double b);

    /** Find root using bisection method (requires sign change on [a,b]). */
    public static native double solveBisection(String expr, double a, double b);

    /** Left-hand limit: lim(x→a⁻) f(x). */
    public static native double limitLeft(String expr, double a);

    /** Right-hand limit: lim(x→a⁺) f(x). */
    public static native double limitRight(String expr, double a);

    /** Two-sided limit: lim(x→a) f(x). Returns NaN if limit does not exist. */
    public static native double limit(String expr, double a);

    /** nth-order derivative f^(n)(x) at x with step h. */
    public static native double nthDerivative(String expr, double x, int n, double h);

    /** Compute Taylor series coefficients c_k = f^(k)(a)/k! for k=0..order. Returns double[order+1] or null on error. */
    public static native double[] taylorCoefficients(String expr, double a, int order);

    /** Solve ODE dy/dx = f(x,y) with y(x0)=y0 using RK4. Returns HashMap with "xs", "ys", "count" keys, or null on error. */
    public static native HashMap<String, Object> odeSolveRk4(String expr, double x0, double y0, double xEnd, int nSteps);

    /** Solve ODE using Euler's method (1st order). Returns HashMap with "xs", "ys", "count" keys, or null on error. */
    public static native HashMap<String, Object> odeSolveEuler(String expr, double x0, double y0, double xEnd, int nSteps);

    /** Solve ODE using Improved Euler's method (Heun's method, 2nd order). Returns HashMap with "xs", "ys", "count" keys, or null on error. */
    public static native HashMap<String, Object> odeSolveImprovedEuler(String expr, double x0, double y0, double xEnd, int nSteps);

    /** Solve ODE using Midpoint method (2nd order). Returns HashMap with "xs", "ys", "count" keys, or null on error. */
    public static native HashMap<String, Object> odeSolveMidpoint(String expr, double x0, double y0, double xEnd, int nSteps);

    /** Last error message from the C core. */
    public static native String getLastError();

    // Complex number methods
    /** Add two complex numbers: z1 + z2. Returns double[2] = {real, imag}. */
    public static native double[] complexAdd(double re1, double im1, double re2, double im2);

    /** Subtract two complex numbers: z1 - z2. Returns double[2] = {real, imag}. */
    public static native double[] complexSub(double re1, double im1, double re2, double im2);

    /** Multiply two complex numbers: z1 * z2. Returns double[2] = {real, imag}. */
    public static native double[] complexMul(double re1, double im1, double re2, double im2);

    /** Divide two complex numbers: z1 / z2. Returns double[2] = {real, imag}. */
    public static native double[] complexDiv(double re1, double im1, double re2, double im2);

    /** Raise complex number to power: z1 ^ z2. Returns double[2] = {real, imag}. */
    public static native double[] complexPow(double re1, double im1, double re2, double im2);

    /** Compute sin of complex number. Returns double[2] = {real, imag}. */
    public static native double[] complexSin(double re, double im);

    /** Compute cos of complex number. Returns double[2] = {real, imag}. */
    public static native double[] complexCos(double re, double im);

    /** Compute tan of complex number. Returns double[2] = {real, imag}. */
    public static native double[] complexTan(double re, double im);

    /** Compute exp of complex number. Returns double[2] = {real, imag}. */
    public static native double[] complexExp(double re, double im);

    /** Compute ln of complex number. Returns double[2] = {real, imag}. */
    public static native double[] complexLn(double re, double im);

    /** Compute sqrt of complex number. Returns double[2] = {real, imag}. */
    public static native double[] complexSqrt(double re, double im);

    /** Compute absolute value (modulus) of complex number. */
    public static native double complexAbs(double re, double im);

    /** Compute complex conjugate. Returns double[2] = {real, imag}. */
    public static native double[] complexConj(double re, double im);

    /** Compute area between two curves f(x) and g(x) over [a,b]. Returns integral_a^b |f(x)-g(x)| dx. */
    public static native double areaBetweenCurves(String exprF, String exprG, double a, double b);

    /** Volume of revolution using disk method: V = π∫[a,b] [f(x)]² dx. */
    public static native double volumeDisk(String exprF, double a, double b);

    /** Volume of revolution using washer method: V = π∫[a,b] ([f(x)]²-[g(x)]²) dx. */
    public static native double volumeWasher(String exprF, String exprG, double a, double b);

    /** Volume of revolution using shell method: V = 2π∫[a,b] x·f(x) dx. */
    public static native double volumeShell(String exprF, double a, double b);

    /** Solve a system of two nonlinear equations f(x,y)=0, g(x,y)=0 using Newton's method for systems.
     *  Returns HashMap with "x" and "y" keys on success, or null on failure. */
    public static native HashMap<String, Object> solveSystem2d(String fExpr, String gExpr, double x0, double y0);

    // Base conversion methods
    /** Parse a number string in the given base and return its integer value. */
    public static native long baseToLong(String input, int base);

    /** Convert an integer to a string in the given base (2-36). */
    public static native String longToBase(long value, int base);

    /** Convert a number string from one base to another. Returns the converted string. */
    public static native String convertBase(String input, int fromBase, int toBase);

    /** Convert a number string to binary, octal, decimal, and hexadecimal.
     *  Returns HashMap with "bin", "oct", "dec", "hex" keys. */
    public static native HashMap<String, String> convertBaseAll(String input, int fromBase);

    // Custom function registry
    /** Define a custom function: f(x) = body. Returns true on success. */
    public static native boolean customFuncDefine(String name, String body);

    /** Clear all custom function definitions. */
    public static native void customFuncClear();

    /** Delete a custom function by name. Returns true if found and deleted. */
    public static native boolean customFuncDelete(String name);

    /** List all custom functions as "name(x)=body;..." string. */
    public static native String customFuncList();
}
