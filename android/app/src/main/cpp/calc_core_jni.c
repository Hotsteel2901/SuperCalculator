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
double limit_left(const char* expr, double a, int max_level);
double limit_right(const char* expr, double a, int max_level);
double limit(const char* expr, double a, double tol, int max_level);
void evaluate_array(const char* expr, const double* xs, double* out, int n);
void evaluate_xy_array(const char* expr, const double* xs, const double* ys, double* out, int n);
double nth_derivative(const char* expr, double x, int n, double h);
int taylor_coefficients(const char* expr, double a, int order, double* out_coeffs, int max_out);
int ode_solve_rk4(const char* expr, double x0, double y0, double x_end,
                   int n_steps, double* out_x, double* out_y, int max_out);
const char* get_last_error(void);

/* Complex number functions */
void complex_add_values(double re1, double im1, double re2, double im2,
                        double* out_re, double* out_im);
void complex_sub_values(double re1, double im1, double re2, double im2,
                        double* out_re, double* out_im);
void complex_mul_values(double re1, double im1, double re2, double im2,
                        double* out_re, double* out_im);
void complex_div_values(double re1, double im1, double re2, double im2,
                        double* out_re, double* out_im);
void complex_pow_values(double re1, double im1, double re2, double im2,
                        double* out_re, double* out_im);
void complex_sin_value(double re, double im, double* out_re, double* out_im);
void complex_cos_value(double re, double im, double* out_re, double* out_im);
void complex_tan_value(double re, double im, double* out_re, double* out_im);
void complex_exp_value(double re, double im, double* out_re, double* out_im);
void complex_ln_value(double re, double im, double* out_re, double* out_im);
void complex_sqrt_value(double re, double im, double* out_re, double* out_im);
double complex_abs_value(double re, double im);
void complex_conj_value(double re, double im, double* out_re, double* out_im);

double area_between_curves(const char* expr_f, const char* expr_g,
                           double a, double b, double tol);

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

JNIEXPORT jdouble JNICALL
Java_com_supercalc_CalcEngine_limitLeft(JNIEnv* env, jclass clazz,
                                         jstring expr, jdouble a) {
    const char* str = (*env)->GetStringUTFChars(env, expr, NULL);
    if (!str) return NAN;
    double result = limit_left(str, a, 10);
    (*env)->ReleaseStringUTFChars(env, expr, str);
    return result;
}

JNIEXPORT jdouble JNICALL
Java_com_supercalc_CalcEngine_limitRight(JNIEnv* env, jclass clazz,
                                          jstring expr, jdouble a) {
    const char* str = (*env)->GetStringUTFChars(env, expr, NULL);
    if (!str) return NAN;
    double result = limit_right(str, a, 10);
    (*env)->ReleaseStringUTFChars(env, expr, str);
    return result;
}

JNIEXPORT jdouble JNICALL
Java_com_supercalc_CalcEngine_limit(JNIEnv* env, jclass clazz,
                                     jstring expr, jdouble a) {
    const char* str = (*env)->GetStringUTFChars(env, expr, NULL);
    if (!str) return NAN;
    double result = limit(str, a, 1e-8, 10);
    (*env)->ReleaseStringUTFChars(env, expr, str);
    return result;
}

JNIEXPORT jdouble JNICALL
Java_com_supercalc_CalcEngine_nthDerivative(JNIEnv* env, jclass clazz,
                                             jstring expr, jdouble x,
                                             jint n, jdouble h) {
    const char* str = (*env)->GetStringUTFChars(env, expr, NULL);
    if (!str) return NAN;
    double result = nth_derivative(str, x, n, h);
    (*env)->ReleaseStringUTFChars(env, expr, str);
    return result;
}

JNIEXPORT jdoubleArray JNICALL
Java_com_supercalc_CalcEngine_taylorCoefficients(JNIEnv* env, jclass clazz,
                                                  jstring expr, jdouble a,
                                                  jint order) {
    const char* str = (*env)->GetStringUTFChars(env, expr, NULL);
    if (!str) return NULL;

    int max_coeffs = order + 1;
    double* coeffs = malloc(max_coeffs * sizeof(double));
    if (!coeffs) {
        (*env)->ReleaseStringUTFChars(env, expr, str);
        return NULL;
    }

    int count = taylor_coefficients(str, a, order, coeffs, max_coeffs);

    jdoubleArray result_array = NULL;
    if (count > 0) {
        result_array = (*env)->NewDoubleArray(env, count);
        if (result_array) {
            (*env)->SetDoubleArrayRegion(env, result_array, 0, count, coeffs);
        }
    }

    free(coeffs);
    (*env)->ReleaseStringUTFChars(env, expr, str);
    return result_array;
}

JNIEXPORT jobject JNICALL
Java_com_supercalc_CalcEngine_odeSolveRk4(JNIEnv* env, jclass clazz,
                                           jstring expr, jdouble x0,
                                           jdouble y0, jdouble x_end,
                                           jint n_steps) {
    const char* str = (*env)->GetStringUTFChars(env, expr, NULL);
    if (!str) return NULL;

    int max_out = n_steps + 1;
    double* out_x = malloc(max_out * sizeof(double));
    double* out_y = malloc(max_out * sizeof(double));
    if (!out_x || !out_y) {
        free(out_x);
        free(out_y);
        (*env)->ReleaseStringUTFChars(env, expr, str);
        return NULL;
    }

    int count = ode_solve_rk4(str, x0, y0, x_end, n_steps, out_x, out_y, max_out);

    jobject result = NULL;
    if (count > 0) {
        /* Create double arrays for xs and ys */
        jdoubleArray xs_array = (*env)->NewDoubleArray(env, count);
        jdoubleArray ys_array = (*env)->NewDoubleArray(env, count);
        if (xs_array && ys_array) {
            (*env)->SetDoubleArrayRegion(env, xs_array, 0, count, out_x);
            (*env)->SetDoubleArrayRegion(env, ys_array, 0, count, out_y);

            /* Create HashMap result: {"xs": [...], "ys": [...], "count": n} */
            jclass hashMapClass = (*env)->FindClass(env, "java/util/HashMap");
            jmethodID hashMapInit = (*env)->GetMethodID(env, hashMapClass, "<init>", "(I)V");
            jmethodID putMethod = (*env)->GetMethodID(env, hashMapClass, "put",
                "(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;");

            result = (*env)->NewObject(env, hashMapClass, hashMapInit, (jint)3);

            jstring xsKey = (*env)->NewStringUTF(env, "xs");
            jstring ysKey = (*env)->NewStringUTF(env, "ys");
            jstring countKey = (*env)->NewStringUTF(env, "count");

            (*env)->CallObjectMethod(env, result, putMethod, xsKey, xs_array);
            (*env)->CallObjectMethod(env, result, putMethod, ysKey, ys_array);

            /* Put count as Integer */
            jclass integerClass = (*env)->FindClass(env, "java/lang/Integer");
            jmethodID valueOfMethod = (*env)->GetStaticMethodID(env, integerClass, "valueOf", "(I)Ljava/lang/Integer;");
            jobject countObj = (*env)->CallStaticObjectMethod(env, integerClass, valueOfMethod, (jint)count);
            (*env)->CallObjectMethod(env, result, putMethod, countKey, countObj);

            (*env)->DeleteLocalRef(env, xsKey);
            (*env)->DeleteLocalRef(env, ysKey);
            (*env)->DeleteLocalRef(env, countKey);
            (*env)->DeleteLocalRef(env, xs_array);
            (*env)->DeleteLocalRef(env, ys_array);
            (*env)->DeleteLocalRef(env, countObj);
            (*env)->DeleteLocalRef(env, hashMapClass);
        }
    }

    free(out_x);
    free(out_y);
    (*env)->ReleaseStringUTFChars(env, expr, str);
    return result;
}

/* Complex number JNI functions */
JNIEXPORT jdoubleArray JNICALL
Java_com_supercalc_CalcEngine_complexAdd(JNIEnv* env, jclass clazz,
                                          jdouble re1, jdouble im1,
                                          jdouble re2, jdouble im2) {
    double out_re, out_im;
    complex_add_values(re1, im1, re2, im2, &out_re, &out_im);
    
    jdoubleArray result = (*env)->NewDoubleArray(env, 2);
    if (result) {
        jdouble values[2] = {out_re, out_im};
        (*env)->SetDoubleArrayRegion(env, result, 0, 2, values);
    }
    return result;
}

JNIEXPORT jdoubleArray JNICALL
Java_com_supercalc_CalcEngine_complexSub(JNIEnv* env, jclass clazz,
                                          jdouble re1, jdouble im1,
                                          jdouble re2, jdouble im2) {
    double out_re, out_im;
    complex_sub_values(re1, im1, re2, im2, &out_re, &out_im);
    
    jdoubleArray result = (*env)->NewDoubleArray(env, 2);
    if (result) {
        jdouble values[2] = {out_re, out_im};
        (*env)->SetDoubleArrayRegion(env, result, 0, 2, values);
    }
    return result;
}

JNIEXPORT jdoubleArray JNICALL
Java_com_supercalc_CalcEngine_complexMul(JNIEnv* env, jclass clazz,
                                          jdouble re1, jdouble im1,
                                          jdouble re2, jdouble im2) {
    double out_re, out_im;
    complex_mul_values(re1, im1, re2, im2, &out_re, &out_im);
    
    jdoubleArray result = (*env)->NewDoubleArray(env, 2);
    if (result) {
        jdouble values[2] = {out_re, out_im};
        (*env)->SetDoubleArrayRegion(env, result, 0, 2, values);
    }
    return result;
}

JNIEXPORT jdoubleArray JNICALL
Java_com_supercalc_CalcEngine_complexDiv(JNIEnv* env, jclass clazz,
                                          jdouble re1, jdouble im1,
                                          jdouble re2, jdouble im2) {
    double out_re, out_im;
    complex_div_values(re1, im1, re2, im2, &out_re, &out_im);
    
    jdoubleArray result = (*env)->NewDoubleArray(env, 2);
    if (result) {
        jdouble values[2] = {out_re, out_im};
        (*env)->SetDoubleArrayRegion(env, result, 0, 2, values);
    }
    return result;
}

JNIEXPORT jdoubleArray JNICALL
Java_com_supercalc_CalcEngine_complexPow(JNIEnv* env, jclass clazz,
                                          jdouble re1, jdouble im1,
                                          jdouble re2, jdouble im2) {
    double out_re, out_im;
    complex_pow_values(re1, im1, re2, im2, &out_re, &out_im);
    
    jdoubleArray result = (*env)->NewDoubleArray(env, 2);
    if (result) {
        jdouble values[2] = {out_re, out_im};
        (*env)->SetDoubleArrayRegion(env, result, 0, 2, values);
    }
    return result;
}

JNIEXPORT jdoubleArray JNICALL
Java_com_supercalc_CalcEngine_complexSin(JNIEnv* env, jclass clazz,
                                          jdouble re, jdouble im) {
    double out_re, out_im;
    complex_sin_value(re, im, &out_re, &out_im);
    
    jdoubleArray result = (*env)->NewDoubleArray(env, 2);
    if (result) {
        jdouble values[2] = {out_re, out_im};
        (*env)->SetDoubleArrayRegion(env, result, 0, 2, values);
    }
    return result;
}

JNIEXPORT jdoubleArray JNICALL
Java_com_supercalc_CalcEngine_complexCos(JNIEnv* env, jclass clazz,
                                          jdouble re, jdouble im) {
    double out_re, out_im;
    complex_cos_value(re, im, &out_re, &out_im);
    
    jdoubleArray result = (*env)->NewDoubleArray(env, 2);
    if (result) {
        jdouble values[2] = {out_re, out_im};
        (*env)->SetDoubleArrayRegion(env, result, 0, 2, values);
    }
    return result;
}

JNIEXPORT jdoubleArray JNICALL
Java_com_supercalc_CalcEngine_complexTan(JNIEnv* env, jclass clazz,
                                          jdouble re, jdouble im) {
    double out_re, out_im;
    complex_tan_value(re, im, &out_re, &out_im);
    
    jdoubleArray result = (*env)->NewDoubleArray(env, 2);
    if (result) {
        jdouble values[2] = {out_re, out_im};
        (*env)->SetDoubleArrayRegion(env, result, 0, 2, values);
    }
    return result;
}

JNIEXPORT jdoubleArray JNICALL
Java_com_supercalc_CalcEngine_complexExp(JNIEnv* env, jclass clazz,
                                          jdouble re, jdouble im) {
    double out_re, out_im;
    complex_exp_value(re, im, &out_re, &out_im);
    
    jdoubleArray result = (*env)->NewDoubleArray(env, 2);
    if (result) {
        jdouble values[2] = {out_re, out_im};
        (*env)->SetDoubleArrayRegion(env, result, 0, 2, values);
    }
    return result;
}

JNIEXPORT jdoubleArray JNICALL
Java_com_supercalc_CalcEngine_complexLn(JNIEnv* env, jclass clazz,
                                         jdouble re, jdouble im) {
    double out_re, out_im;
    complex_ln_value(re, im, &out_re, &out_im);
    
    jdoubleArray result = (*env)->NewDoubleArray(env, 2);
    if (result) {
        jdouble values[2] = {out_re, out_im};
        (*env)->SetDoubleArrayRegion(env, result, 0, 2, values);
    }
    return result;
}

JNIEXPORT jdoubleArray JNICALL
Java_com_supercalc_CalcEngine_complexSqrt(JNIEnv* env, jclass clazz,
                                           jdouble re, jdouble im) {
    double out_re, out_im;
    complex_sqrt_value(re, im, &out_re, &out_im);
    
    jdoubleArray result = (*env)->NewDoubleArray(env, 2);
    if (result) {
        jdouble values[2] = {out_re, out_im};
        (*env)->SetDoubleArrayRegion(env, result, 0, 2, values);
    }
    return result;
}

JNIEXPORT jdouble JNICALL
Java_com_supercalc_CalcEngine_complexAbs(JNIEnv* env, jclass clazz,
                                          jdouble re, jdouble im) {
    return complex_abs_value(re, im);
}

JNIEXPORT jdoubleArray JNICALL
Java_com_supercalc_CalcEngine_complexConj(JNIEnv* env, jclass clazz,
                                           jdouble re, jdouble im) {
    double out_re, out_im;
    complex_conj_value(re, im, &out_re, &out_im);
    
    jdoubleArray result = (*env)->NewDoubleArray(env, 2);
    if (result) {
        jdouble values[2] = {out_re, out_im};
        (*env)->SetDoubleArrayRegion(env, result, 0, 2, values);
    }
    return result;
}

JNIEXPORT jdouble JNICALL
Java_com_supercalc_CalcEngine_areaBetweenCurves(JNIEnv* env, jclass clazz,
                                                 jstring exprF, jstring exprG,
                                                 jdouble a, jdouble b) {
    const char* strF = (*env)->GetStringUTFChars(env, exprF, NULL);
    const char* strG = (*env)->GetStringUTFChars(env, exprG, NULL);
    if (!strF || !strG) {
        if (strF) (*env)->ReleaseStringUTFChars(env, exprF, strF);
        if (strG) (*env)->ReleaseStringUTFChars(env, exprG, strG);
        return NAN;
    }
    double result = area_between_curves(strF, strG, a, b, 1e-8);
    (*env)->ReleaseStringUTFChars(env, exprF, strF);
    (*env)->ReleaseStringUTFChars(env, exprG, strG);
    return result;
}
