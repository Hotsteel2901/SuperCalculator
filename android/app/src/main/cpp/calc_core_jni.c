/*
 * JNI bridge for Super Calculator C core on Android.
 * Links against calc_core.c and exposes functions to Java via JNI.
 */
#include <jni.h>

/* Forward declarations — implemented in calc_core.c (linked in same .so) */
double evaluate(const char* expr, double x);
double derivative(const char* expr, double x, double h);
double derivative2(const char* expr, double x, double h);
double integrate_adaptive(const char* expr, double a, double b, double tol);
double solve_equation(const char* expr, double guess, double xmin, double xmax,
                      double tol, int max_iter);
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
