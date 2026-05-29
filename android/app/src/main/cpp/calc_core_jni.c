/*
 * JNI bridge for Super Calculator C core on Android.
 * Links against calc_core.c and exposes functions to Java via JNI.
 */
#include <jni.h>
#include <stdlib.h>

#include <math.h>
/* Forward declarations — implemented in calc_core.c (linked in same .so) */
double evaluate(const char* expr, double x);
double evaluate_xy(const char* expr, double x, double y);
double derivative(const char* expr, double x, double h);
double derivative2(const char* expr, double x, double h);
double integrate_adaptive(const char* expr, double a, double b, double tol);
double solve_equation(const char* expr, double guess, double xmin, double xmax,
                      double tol, int max_iter);
double solve_bisection(const char* expr, double a, double b,
                       double tol, int max_iter);
double find_minimum(const char* expr, double a, double b, double tol, int max_iter);
double find_maximum(const char* expr, double a, double b, double tol, int max_iter);
void evaluate_array(const char* expr, const double* xs, double* out, int n);
void evaluate_xy_array(const char* expr, const double* xs, const double* ys, double* out, int n);
const char* get_last_error(void);

/* Helper: extract UTF-8 string from jstring, call fn, release, return */
static jdouble call_with_expr(JNIEnv* env, jstring expr, double x,
                              double (*fn)(const char*, double)) {
    const char* str = (*env)->GetStringUTFChars(env, expr, NULL);
    if (!str) return NAN;
    double result = fn(str, x);
    (*env)->ReleaseStringUTFChars(env, expr, str);
    return result;
}

JNIEXPORT jdouble JNICALL
Java_com_supercalc_CalcEngine_evaluate(JNIEnv* env, jclass clazz,
                                        jstring expr, jdouble x) {
    return call_with_expr(env, expr, x, evaluate);
}

JNIEXPORT jdouble JNICALL
Java_com_supercalc_CalcEngine_evaluateXY(JNIEnv* env, jclass clazz,
                                          jstring expr, jdouble x, jdouble y) {
    const char* str = (*env)->GetStringUTFChars(env, expr, NULL);
    if (!str) return NAN;
    double result = evaluate_xy(str, x, y);
    (*env)->ReleaseStringUTFChars(env, expr, str);
    return result;
}

JNIEXPORT jdouble JNICALL
Java_com_supercalc_CalcEngine_derivative(JNIEnv* env, jclass clazz,
                                          jstring expr, jdouble x, jdouble h) {
    const char* str = (*env)->GetStringUTFChars(env, expr, NULL);
    if (!str) return NAN;
    double result = derivative(str, x, h);
    (*env)->ReleaseStringUTFChars(env, expr, str);
    return result;
}

JNIEXPORT jdouble JNICALL
Java_com_supercalc_CalcEngine_derivative2(JNIEnv* env, jclass clazz,
                                           jstring expr, jdouble x, jdouble h) {
    const char* str = (*env)->GetStringUTFChars(env, expr, NULL);
    if (!str) return NAN;
    double result = derivative2(str, x, h);
    (*env)->ReleaseStringUTFChars(env, expr, str);
    return result;
}

JNIEXPORT jdouble JNICALL
Java_com_supercalc_CalcEngine_integrate(JNIEnv* env, jclass clazz,
                                         jstring expr, jdouble a, jdouble b) {
    const char* str = (*env)->GetStringUTFChars(env, expr, NULL);
    if (!str) return NAN;
    double result = integrate_adaptive(str, a, b, 1e-8);
    (*env)->ReleaseStringUTFChars(env, expr, str);
    return result;
}

JNIEXPORT jdouble JNICALL
Java_com_supercalc_CalcEngine_solve(JNIEnv* env, jclass clazz,
                                     jstring expr, jdouble guess,
                                     jdouble xmin, jdouble xmax) {
    const char* str = (*env)->GetStringUTFChars(env, expr, NULL);
    if (!str) return NAN;
    double result = solve_equation(str, guess, xmin, xmax, 1e-8, 100);
    (*env)->ReleaseStringUTFChars(env, expr, str);
    return result;
}

JNIEXPORT jstring JNICALL
Java_com_supercalc_CalcEngine_getLastError(JNIEnv* env, jclass clazz) {
    return (*env)->NewStringUTF(env, get_last_error());
}

JNIEXPORT jdoubleArray JNICALL
Java_com_supercalc_CalcEngine_evaluateArray(JNIEnv* env, jclass clazz,
                                             jstring expr, jdoubleArray xs) {
    const char* str = (*env)->GetStringUTFChars(env, expr, NULL);
    if (!str) return NULL;
    
    jsize n = (*env)->GetArrayLength(env, xs);
    jdouble* x_vals = (*env)->GetDoubleArrayElements(env, xs, NULL);
    if (!x_vals) {
        (*env)->ReleaseStringUTFChars(env, expr, str);
        return NULL;
    }
    
    double* results = malloc(n * sizeof(double));
    if (!results) {
        (*env)->ReleaseDoubleArrayElements(env, xs, x_vals, JNI_ABORT);
        (*env)->ReleaseStringUTFChars(env, expr, str);
        return NULL;
    }
    
    evaluate_array(str, x_vals, results, n);
    
    jdoubleArray result_array = (*env)->NewDoubleArray(env, n);
    if (result_array) {
        (*env)->SetDoubleArrayRegion(env, result_array, 0, n, results);
    }
    
    (*env)->ReleaseDoubleArrayElements(env, xs, x_vals, JNI_ABORT);
    (*env)->ReleaseStringUTFChars(env, expr, str);
    free(results);
    
    return result_array;
}

JNIEXPORT jdoubleArray JNICALL
Java_com_supercalc_CalcEngine_evaluateXYArray(JNIEnv* env, jclass clazz,
                                                jstring expr, jdoubleArray xs, jdoubleArray ys) {
    const char* str = (*env)->GetStringUTFChars(env, expr, NULL);
    if (!str) return NULL;

    jsize n = (*env)->GetArrayLength(env, xs);
    jsize ny = (*env)->GetArrayLength(env, ys);
    if (n != ny) {
        (*env)->ReleaseStringUTFChars(env, expr, str);
        return NULL;
    }
    jdouble* x_vals = (*env)->GetDoubleArrayElements(env, xs, NULL);
    jdouble* y_vals = (*env)->GetDoubleArrayElements(env, ys, NULL);
    if (!x_vals || !y_vals) {
        if (x_vals) (*env)->ReleaseDoubleArrayElements(env, xs, x_vals, JNI_ABORT);
        if (y_vals) (*env)->ReleaseDoubleArrayElements(env, ys, y_vals, JNI_ABORT);
        (*env)->ReleaseStringUTFChars(env, expr, str);
        return NULL;
    }

    double* results = malloc(n * sizeof(double));
    if (!results) {
        (*env)->ReleaseDoubleArrayElements(env, xs, x_vals, JNI_ABORT);
        (*env)->ReleaseDoubleArrayElements(env, ys, y_vals, JNI_ABORT);
        (*env)->ReleaseStringUTFChars(env, expr, str);
        return NULL;
    }

    evaluate_xy_array(str, x_vals, y_vals, results, n);

    jdoubleArray result_array = (*env)->NewDoubleArray(env, n);
    if (result_array) {
        (*env)->SetDoubleArrayRegion(env, result_array, 0, n, results);
    }

    (*env)->ReleaseDoubleArrayElements(env, xs, x_vals, JNI_ABORT);
    (*env)->ReleaseDoubleArrayElements(env, ys, y_vals, JNI_ABORT);
    (*env)->ReleaseStringUTFChars(env, expr, str);
    free(results);

    return result_array;
}

JNIEXPORT jdouble JNICALL
Java_com_supercalc_CalcEngine_findMinimum(JNIEnv* env, jclass clazz,
                                           jstring expr, jdouble a, jdouble b) {
    const char* str = (*env)->GetStringUTFChars(env, expr, NULL);
    if (!str) return NAN;
    double result = find_minimum(str, a, b, 1e-8, 200);
    (*env)->ReleaseStringUTFChars(env, expr, str);
    return result;
}

JNIEXPORT jdouble JNICALL
Java_com_supercalc_CalcEngine_findMaximum(JNIEnv* env, jclass clazz,
                                           jstring expr, jdouble a, jdouble b) {
    const char* str = (*env)->GetStringUTFChars(env, expr, NULL);
    if (!str) return NAN;
    double result = find_maximum(str, a, b, 1e-8, 200);
    (*env)->ReleaseStringUTFChars(env, expr, str);
    return result;
}

JNIEXPORT jdouble JNICALL
Java_com_supercalc_CalcEngine_solveBisection(JNIEnv* env, jclass clazz,
                                               jstring expr, jdouble a, jdouble b) {
    const char* str = (*env)->GetStringUTFChars(env, expr, NULL);
    if (!str) return NAN;
    double result = solve_bisection(str, a, b, 1e-8, 200);
    (*env)->ReleaseStringUTFChars(env, expr, str);
    return result;
}
