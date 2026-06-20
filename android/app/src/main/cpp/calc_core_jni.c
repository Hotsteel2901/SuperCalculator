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
int ode_solve_euler(const char* expr, double x0, double y0, double x_end,
                    int n_steps, double* out_x, double* out_y, int max_out);
int ode_solve_improved_euler(const char* expr, double x0, double y0, double x_end,
                             int n_steps, double* out_x, double* out_y, int max_out);
int ode_solve_midpoint(const char* expr, double x0, double y0, double x_end,
                        int n_steps, double* out_x, double* out_y, int max_out);
int ode_solve_rkf45(const char* expr, double x0, double y0, double x_end,
                     double tol, double* out_x, double* out_y, int max_points);
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

double volume_disk(const char* expr_f, double a, double b, double tol);
double volume_washer(const char* expr_f, const char* expr_g, double a, double b, double tol);
double volume_shell(const char* expr_f, double a, double b, double tol);

int solve_system_2d(const char* f_expr, const char* g_expr,
                    double x0, double y0, double tol, int max_iter,
                    double* out_x, double* out_y);

/* Custom function registry */
int custom_func_define(const char* name, const char* body);
void custom_func_clear(void);
int custom_func_delete(const char* name);
int custom_func_list(char* output, int max_out);

/* Laplace Transform */
double laplace_transform(const char* expr, double s);
double inverse_laplace(const char* expr, double t);

/* Akima Interpolation */
double interp_akima(const double* xs, const double* ys, int n, double x);

/* Natural Spline Interpolation */
double interp_natural_spline(const double* xs, const double* ys, int n, double x);

/* Calculation History */
void history_add(const char* expr, double result);
int history_count(void);
int history_get(int index, char* expr_out, int expr_max, double* result_out);
void history_clear(void);
int history_get_all(char* output, int max_out);

/* Contour Grid Evaluation */
int contour_grid_eval(const char* expr, double x_min, double x_max,
                      double y_min, double y_max, int n_cols, int n_rows,
                      double* out);

/* Vector Field Grid Evaluation */
int vector_field_grid_eval(const char* expr_p, const char* expr_q,
                           double x_min, double x_max,
                           double y_min, double y_max,
                           int n_cols, int n_rows,
                           double* out_p, double* out_q);

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
    const char* err = get_last_error();
    if (!err) err = "";
    return (*env)->NewStringUTF(env, err);
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
        if (!xs_array || !ys_array) {
            if (xs_array) (*env)->DeleteLocalRef(env, xs_array);
            if (ys_array) (*env)->DeleteLocalRef(env, ys_array);
            free(out_x);
            free(out_y);
            (*env)->ReleaseStringUTFChars(env, expr, str);
            return NULL;
        }
        
        (*env)->SetDoubleArrayRegion(env, xs_array, 0, count, out_x);
        (*env)->SetDoubleArrayRegion(env, ys_array, 0, count, out_y);

        /* Create HashMap result: {"xs": [...], "ys": [...], "count": n} */
        jclass hashMapClass = (*env)->FindClass(env, "java/util/HashMap");
        if (!hashMapClass) {
            (*env)->DeleteLocalRef(env, xs_array);
            (*env)->DeleteLocalRef(env, ys_array);
            free(out_x);
            free(out_y);
            (*env)->ReleaseStringUTFChars(env, expr, str);
            return NULL;
        }
        
        jmethodID hashMapInit = (*env)->GetMethodID(env, hashMapClass, "<init>", "(I)V");
        jmethodID putMethod = (*env)->GetMethodID(env, hashMapClass, "put",
            "(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;");
        if (!hashMapInit || !putMethod) {
            (*env)->DeleteLocalRef(env, hashMapClass);
            (*env)->DeleteLocalRef(env, xs_array);
            (*env)->DeleteLocalRef(env, ys_array);
            free(out_x);
            free(out_y);
            (*env)->ReleaseStringUTFChars(env, expr, str);
            return NULL;
        }

        result = (*env)->NewObject(env, hashMapClass, hashMapInit, (jint)3);
        if (!result) {
            (*env)->DeleteLocalRef(env, hashMapClass);
            (*env)->DeleteLocalRef(env, xs_array);
            (*env)->DeleteLocalRef(env, ys_array);
            free(out_x);
            free(out_y);
            (*env)->ReleaseStringUTFChars(env, expr, str);
            return NULL;
        }

        jstring xsKey = (*env)->NewStringUTF(env, "xs");
        jstring ysKey = (*env)->NewStringUTF(env, "ys");
        jstring countKey = (*env)->NewStringUTF(env, "count");
        if (!xsKey || !ysKey || !countKey) {
            if (xsKey) (*env)->DeleteLocalRef(env, xsKey);
            if (ysKey) (*env)->DeleteLocalRef(env, ysKey);
            if (countKey) (*env)->DeleteLocalRef(env, countKey);
            (*env)->DeleteLocalRef(env, result);
            (*env)->DeleteLocalRef(env, xs_array);
            (*env)->DeleteLocalRef(env, ys_array);
            free(out_x); free(out_y);
            (*env)->ReleaseStringUTFChars(env, expr, str);
            return NULL;
        }

        jobject old1 = (*env)->CallObjectMethod(env, result, putMethod, xsKey, xs_array);
        if ((*env)->ExceptionCheck(env)) {
            (*env)->DeleteLocalRef(env, result);
            (*env)->DeleteLocalRef(env, xsKey);
            (*env)->DeleteLocalRef(env, ysKey);
            (*env)->DeleteLocalRef(env, countKey);
            (*env)->DeleteLocalRef(env, xs_array);
            (*env)->DeleteLocalRef(env, ys_array);
            free(out_x); free(out_y);
            (*env)->ReleaseStringUTFChars(env, expr, str);
            return NULL;
        }
        if (old1) (*env)->DeleteLocalRef(env, old1);
        jobject old2 = (*env)->CallObjectMethod(env, result, putMethod, ysKey, ys_array);
        if ((*env)->ExceptionCheck(env)) {
            (*env)->DeleteLocalRef(env, result);
            (*env)->DeleteLocalRef(env, xsKey);
            (*env)->DeleteLocalRef(env, ysKey);
            (*env)->DeleteLocalRef(env, countKey);
            (*env)->DeleteLocalRef(env, xs_array);
            (*env)->DeleteLocalRef(env, ys_array);
            free(out_x); free(out_y);
            (*env)->ReleaseStringUTFChars(env, expr, str);
            return NULL;
        }
        if (old2) (*env)->DeleteLocalRef(env, old2);

        /* Put count as Integer */
        jclass integerClass = (*env)->FindClass(env, "java/lang/Integer");
        if (!integerClass || (*env)->ExceptionCheck(env)) {
            (*env)->DeleteLocalRef(env, xsKey);
            (*env)->DeleteLocalRef(env, ysKey);
            (*env)->DeleteLocalRef(env, countKey);
            (*env)->DeleteLocalRef(env, result);
            (*env)->DeleteLocalRef(env, xs_array);
            (*env)->DeleteLocalRef(env, ys_array);
            free(out_x); free(out_y);
            (*env)->ReleaseStringUTFChars(env, expr, str);
            return NULL;
        }
        jmethodID valueOfMethod = (*env)->GetStaticMethodID(env, integerClass, "valueOf", "(I)Ljava/lang/Integer;");
        if (!valueOfMethod || (*env)->ExceptionCheck(env)) {
            (*env)->DeleteLocalRef(env, integerClass);
            (*env)->DeleteLocalRef(env, xsKey);
            (*env)->DeleteLocalRef(env, ysKey);
            (*env)->DeleteLocalRef(env, countKey);
            (*env)->DeleteLocalRef(env, result);
            (*env)->DeleteLocalRef(env, xs_array);
            (*env)->DeleteLocalRef(env, ys_array);
            free(out_x); free(out_y);
            (*env)->ReleaseStringUTFChars(env, expr, str);
            return NULL;
        }
        jobject countObj = (*env)->CallStaticObjectMethod(env, integerClass, valueOfMethod, (jint)count);
        if ((*env)->ExceptionCheck(env)) {
            (*env)->DeleteLocalRef(env, integerClass);
            (*env)->DeleteLocalRef(env, result);
            (*env)->DeleteLocalRef(env, xsKey);
            (*env)->DeleteLocalRef(env, ysKey);
            (*env)->DeleteLocalRef(env, countKey);
            (*env)->DeleteLocalRef(env, xs_array);
            (*env)->DeleteLocalRef(env, ys_array);
            free(out_x); free(out_y);
            (*env)->ReleaseStringUTFChars(env, expr, str);
            return NULL;
        }
        (*env)->CallObjectMethod(env, result, putMethod, countKey, countObj);
        if ((*env)->ExceptionCheck(env)) {
            (*env)->DeleteLocalRef(env, countObj);
            (*env)->DeleteLocalRef(env, integerClass);
            (*env)->DeleteLocalRef(env, result);
            (*env)->DeleteLocalRef(env, xsKey);
            (*env)->DeleteLocalRef(env, ysKey);
            (*env)->DeleteLocalRef(env, countKey);
            (*env)->DeleteLocalRef(env, xs_array);
            (*env)->DeleteLocalRef(env, ys_array);
            free(out_x); free(out_y);
            (*env)->ReleaseStringUTFChars(env, expr, str);
            return NULL;
        }

        (*env)->DeleteLocalRef(env, xsKey);
        (*env)->DeleteLocalRef(env, ysKey);
        (*env)->DeleteLocalRef(env, countKey);
        (*env)->DeleteLocalRef(env, xs_array);
        (*env)->DeleteLocalRef(env, ys_array);
        (*env)->DeleteLocalRef(env, countObj);
        (*env)->DeleteLocalRef(env, hashMapClass);
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

JNIEXPORT jdouble JNICALL
Java_com_supercalc_CalcEngine_volumeDisk(JNIEnv* env, jclass clazz,
                                          jstring exprF, jdouble a, jdouble b) {
    const char* strF = (*env)->GetStringUTFChars(env, exprF, NULL);
    if (!strF) return NAN;
    double result = volume_disk(strF, a, b, 1e-8);
    (*env)->ReleaseStringUTFChars(env, exprF, strF);
    return result;
}

JNIEXPORT jdouble JNICALL
Java_com_supercalc_CalcEngine_volumeWasher(JNIEnv* env, jclass clazz,
                                            jstring exprF, jstring exprG,
                                            jdouble a, jdouble b) {
    const char* strF = (*env)->GetStringUTFChars(env, exprF, NULL);
    const char* strG = (*env)->GetStringUTFChars(env, exprG, NULL);
    if (!strF || !strG) {
        if (strF) (*env)->ReleaseStringUTFChars(env, exprF, strF);
        if (strG) (*env)->ReleaseStringUTFChars(env, exprG, strG);
        return NAN;
    }
    double result = volume_washer(strF, strG, a, b, 1e-8);
    (*env)->ReleaseStringUTFChars(env, exprF, strF);
    (*env)->ReleaseStringUTFChars(env, exprG, strG);
    return result;
}

JNIEXPORT jdouble JNICALL
Java_com_supercalc_CalcEngine_volumeShell(JNIEnv* env, jclass clazz,
                                           jstring exprF, jdouble a, jdouble b) {
    const char* strF = (*env)->GetStringUTFChars(env, exprF, NULL);
    if (!strF) return NAN;
    double result = volume_shell(strF, a, b, 1e-8);
    (*env)->ReleaseStringUTFChars(env, exprF, strF);
    return result;
}

JNIEXPORT jobject JNICALL
Java_com_supercalc_CalcEngine_solveSystem2d(JNIEnv* env, jclass clazz,
                                             jstring fExpr, jstring gExpr,
                                             jdouble x0, jdouble y0) {
    const char* strF = (*env)->GetStringUTFChars(env, fExpr, NULL);
    const char* strG = (*env)->GetStringUTFChars(env, gExpr, NULL);
    if (!strF || !strG) {
        if (strF) (*env)->ReleaseStringUTFChars(env, fExpr, strF);
        if (strG) (*env)->ReleaseStringUTFChars(env, gExpr, strG);
        return NULL;
    }

    double out_x = 0.0, out_y = 0.0;
    int success = solve_system_2d(strF, strG, x0, y0, 1e-10, 100, &out_x, &out_y);

    (*env)->ReleaseStringUTFChars(env, fExpr, strF);
    (*env)->ReleaseStringUTFChars(env, gExpr, strG);

    if (!success) return NULL;

    /* Create HashMap result: {"x": ..., "y": ...} */
    jclass hashMapClass = (*env)->FindClass(env, "java/util/HashMap");
    if (!hashMapClass) return NULL;

    jmethodID hashMapInit = (*env)->GetMethodID(env, hashMapClass, "<init>", "(I)V");
    jmethodID putMethod = (*env)->GetMethodID(env, hashMapClass, "put",
        "(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;");
    if (!hashMapInit || !putMethod) {
        (*env)->DeleteLocalRef(env, hashMapClass);
        return NULL;
    }

    jobject result = (*env)->NewObject(env, hashMapClass, hashMapInit, (jint)2);
    if (!result) {
        (*env)->DeleteLocalRef(env, hashMapClass);
        return NULL;
    }

    jstring xKey = (*env)->NewStringUTF(env, "x");
    jstring yKey = (*env)->NewStringUTF(env, "y");
    if (!xKey || !yKey) {
        if (xKey) (*env)->DeleteLocalRef(env, xKey);
        if (yKey) (*env)->DeleteLocalRef(env, yKey);
        (*env)->DeleteLocalRef(env, result);
        (*env)->DeleteLocalRef(env, hashMapClass);
        return NULL;
    }

    jclass doubleClass = (*env)->FindClass(env, "java/lang/Double");
    if (!doubleClass || (*env)->ExceptionCheck(env)) {
        (*env)->DeleteLocalRef(env, xKey);
        (*env)->DeleteLocalRef(env, yKey);
        (*env)->DeleteLocalRef(env, result);
        (*env)->DeleteLocalRef(env, hashMapClass);
        return NULL;
    }
    jmethodID valueOfDouble = (*env)->GetStaticMethodID(env, doubleClass, "valueOf", "(D)Ljava/lang/Double;");
    if (!valueOfDouble || (*env)->ExceptionCheck(env)) {
        (*env)->DeleteLocalRef(env, doubleClass);
        (*env)->DeleteLocalRef(env, xKey);
        (*env)->DeleteLocalRef(env, yKey);
        (*env)->DeleteLocalRef(env, result);
        (*env)->DeleteLocalRef(env, hashMapClass);
        return NULL;
    }
    jobject xObj = (*env)->CallStaticObjectMethod(env, doubleClass, valueOfDouble, out_x);
    if ((*env)->ExceptionCheck(env)) {
        (*env)->DeleteLocalRef(env, doubleClass);
        (*env)->DeleteLocalRef(env, xKey);
        (*env)->DeleteLocalRef(env, yKey);
        (*env)->DeleteLocalRef(env, result);
        (*env)->DeleteLocalRef(env, hashMapClass);
        return NULL;
    }
    jobject yObj = (*env)->CallStaticObjectMethod(env, doubleClass, valueOfDouble, out_y);
    if ((*env)->ExceptionCheck(env)) {
        (*env)->DeleteLocalRef(env, xObj);
        (*env)->DeleteLocalRef(env, doubleClass);
        (*env)->DeleteLocalRef(env, xKey);
        (*env)->DeleteLocalRef(env, yKey);
        (*env)->DeleteLocalRef(env, result);
        (*env)->DeleteLocalRef(env, hashMapClass);
        return NULL;
    }

    (*env)->CallObjectMethod(env, result, putMethod, xKey, xObj);
    if ((*env)->ExceptionCheck(env)) {
        (*env)->DeleteLocalRef(env, xObj);
        (*env)->DeleteLocalRef(env, yObj);
        (*env)->DeleteLocalRef(env, doubleClass);
        (*env)->DeleteLocalRef(env, xKey);
        (*env)->DeleteLocalRef(env, yKey);
        (*env)->DeleteLocalRef(env, result);
        (*env)->DeleteLocalRef(env, hashMapClass);
        return NULL;
    }
    (*env)->CallObjectMethod(env, result, putMethod, yKey, yObj);
    if ((*env)->ExceptionCheck(env)) {
        (*env)->DeleteLocalRef(env, xObj);
        (*env)->DeleteLocalRef(env, yObj);
        (*env)->DeleteLocalRef(env, doubleClass);
        (*env)->DeleteLocalRef(env, xKey);
        (*env)->DeleteLocalRef(env, yKey);
        (*env)->DeleteLocalRef(env, result);
        (*env)->DeleteLocalRef(env, hashMapClass);
        return NULL;
    }

    (*env)->DeleteLocalRef(env, xKey);
    (*env)->DeleteLocalRef(env, yKey);
    (*env)->DeleteLocalRef(env, xObj);
    (*env)->DeleteLocalRef(env, yObj);
    (*env)->DeleteLocalRef(env, doubleClass);
    (*env)->DeleteLocalRef(env, hashMapClass);

    return result;
}

/* ---- Base Conversion ---- */

long long base_to_long(const char* str, int base);
int long_to_base(long long n, int base, char* output, int max_out);

JNIEXPORT jlong JNICALL
Java_com_supercalc_CalcEngine_baseToLong(JNIEnv* env, jclass clazz,
                                          jstring input, jint base) {
    const char* str = (*env)->GetStringUTFChars(env, input, NULL);
    if (!str) return 0;
    long long result = base_to_long(str, base);
    (*env)->ReleaseStringUTFChars(env, input, str);
    return (jlong)result;
}

JNIEXPORT jstring JNICALL
Java_com_supercalc_CalcEngine_longToBase(JNIEnv* env, jclass clazz,
                                          jlong value, jint base) {
    char buf[128];
    int len = long_to_base((long long)value, base, buf, sizeof(buf));
    if (len <= 0) return (*env)->NewStringUTF(env, "");
    return (*env)->NewStringUTF(env, buf);
}

JNIEXPORT jstring JNICALL
Java_com_supercalc_CalcEngine_convertBase(JNIEnv* env, jclass clazz,
                                           jstring input, jint fromBase, jint toBase) {
    const char* str = (*env)->GetStringUTFChars(env, input, NULL);
    if (!str) return (*env)->NewStringUTF(env, "");

    long long value = base_to_long(str, fromBase);
    (*env)->ReleaseStringUTFChars(env, input, str);

    char buf[128];
    int len = long_to_base(value, toBase, buf, sizeof(buf));
    if (len <= 0) return (*env)->NewStringUTF(env, "");
    return (*env)->NewStringUTF(env, buf);
}

JNIEXPORT jobject JNICALL
Java_com_supercalc_CalcEngine_convertBaseAll(JNIEnv* env, jclass clazz,
                                              jstring input, jint fromBase) {
    const char* str = (*env)->GetStringUTFChars(env, input, NULL);
    if (!str) return NULL;

    long long value = base_to_long(str, fromBase);
    (*env)->ReleaseStringUTFChars(env, input, str);

    char bufBin[128], bufOct[128], bufDec[128], bufHex[128];
    long_to_base(value, 2, bufBin, sizeof(bufBin));
    long_to_base(value, 8, bufOct, sizeof(bufOct));
    long_to_base(value, 10, bufDec, sizeof(bufDec));
    long_to_base(value, 16, bufHex, sizeof(bufHex));

    jclass hashMapClass = (*env)->FindClass(env, "java/util/HashMap");
    if (!hashMapClass) return NULL;
    jmethodID initMethod = (*env)->GetMethodID(env, hashMapClass, "<init>", "(I)V");
    if (!initMethod) { (*env)->DeleteLocalRef(env, hashMapClass); return NULL; }
    jmethodID putMethod = (*env)->GetMethodID(env, hashMapClass, "put",
        "(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;");
    if (!putMethod) { (*env)->DeleteLocalRef(env, hashMapClass); return NULL; }

    jobject result = (*env)->NewObject(env, hashMapClass, initMethod, 4);
    if (!result) { (*env)->DeleteLocalRef(env, hashMapClass); return NULL; }

    jstring keyBin = (*env)->NewStringUTF(env, "bin");
    jstring keyOct = (*env)->NewStringUTF(env, "oct");
    jstring keyDec = (*env)->NewStringUTF(env, "dec");
    jstring keyHex = (*env)->NewStringUTF(env, "hex");
    jstring valBin = (*env)->NewStringUTF(env, bufBin);
    jstring valOct = (*env)->NewStringUTF(env, bufOct);
    jstring valDec = (*env)->NewStringUTF(env, bufDec);
    jstring valHex = (*env)->NewStringUTF(env, bufHex);

    if (!keyBin || !keyOct || !keyDec || !keyHex || !valBin || !valOct || !valDec || !valHex) {
        if (keyBin) (*env)->DeleteLocalRef(env, keyBin);
        if (keyOct) (*env)->DeleteLocalRef(env, keyOct);
        if (keyDec) (*env)->DeleteLocalRef(env, keyDec);
        if (keyHex) (*env)->DeleteLocalRef(env, keyHex);
        if (valBin) (*env)->DeleteLocalRef(env, valBin);
        if (valOct) (*env)->DeleteLocalRef(env, valOct);
        if (valDec) (*env)->DeleteLocalRef(env, valDec);
        if (valHex) (*env)->DeleteLocalRef(env, valHex);
        (*env)->DeleteLocalRef(env, result);
        (*env)->DeleteLocalRef(env, hashMapClass);
        return NULL;
    }

    (*env)->CallObjectMethod(env, result, putMethod, keyBin, valBin);
    if ((*env)->ExceptionCheck(env)) {
        (*env)->DeleteLocalRef(env, keyBin); (*env)->DeleteLocalRef(env, keyOct);
        (*env)->DeleteLocalRef(env, keyDec); (*env)->DeleteLocalRef(env, keyHex);
        (*env)->DeleteLocalRef(env, valBin); (*env)->DeleteLocalRef(env, valOct);
        (*env)->DeleteLocalRef(env, valDec); (*env)->DeleteLocalRef(env, valHex);
        (*env)->DeleteLocalRef(env, result); (*env)->DeleteLocalRef(env, hashMapClass);
        return NULL;
    }
    (*env)->CallObjectMethod(env, result, putMethod, keyOct, valOct);
    if ((*env)->ExceptionCheck(env)) {
        (*env)->DeleteLocalRef(env, keyBin); (*env)->DeleteLocalRef(env, keyOct);
        (*env)->DeleteLocalRef(env, keyDec); (*env)->DeleteLocalRef(env, keyHex);
        (*env)->DeleteLocalRef(env, valBin); (*env)->DeleteLocalRef(env, valOct);
        (*env)->DeleteLocalRef(env, valDec); (*env)->DeleteLocalRef(env, valHex);
        (*env)->DeleteLocalRef(env, result); (*env)->DeleteLocalRef(env, hashMapClass);
        return NULL;
    }
    (*env)->CallObjectMethod(env, result, putMethod, keyDec, valDec);
    if ((*env)->ExceptionCheck(env)) {
        (*env)->DeleteLocalRef(env, keyBin); (*env)->DeleteLocalRef(env, keyOct);
        (*env)->DeleteLocalRef(env, keyDec); (*env)->DeleteLocalRef(env, keyHex);
        (*env)->DeleteLocalRef(env, valBin); (*env)->DeleteLocalRef(env, valOct);
        (*env)->DeleteLocalRef(env, valDec); (*env)->DeleteLocalRef(env, valHex);
        (*env)->DeleteLocalRef(env, result); (*env)->DeleteLocalRef(env, hashMapClass);
        return NULL;
    }
    (*env)->CallObjectMethod(env, result, putMethod, keyHex, valHex);
    if ((*env)->ExceptionCheck(env)) {
        (*env)->DeleteLocalRef(env, keyBin); (*env)->DeleteLocalRef(env, keyOct);
        (*env)->DeleteLocalRef(env, keyDec); (*env)->DeleteLocalRef(env, keyHex);
        (*env)->DeleteLocalRef(env, valBin); (*env)->DeleteLocalRef(env, valOct);
        (*env)->DeleteLocalRef(env, valDec); (*env)->DeleteLocalRef(env, valHex);
        (*env)->DeleteLocalRef(env, result); (*env)->DeleteLocalRef(env, hashMapClass);
        return NULL;
    }

    (*env)->DeleteLocalRef(env, keyBin); (*env)->DeleteLocalRef(env, keyOct);
    (*env)->DeleteLocalRef(env, keyDec); (*env)->DeleteLocalRef(env, keyHex);
    (*env)->DeleteLocalRef(env, valBin); (*env)->DeleteLocalRef(env, valOct);
    (*env)->DeleteLocalRef(env, valDec); (*env)->DeleteLocalRef(env, valHex);
    (*env)->DeleteLocalRef(env, hashMapClass);

    return result;
}

/* Helper function for ODE methods */
static jobject ode_solve_helper(JNIEnv* env, jclass clazz, jstring expr,
                                jdouble x0, jdouble y0, jdouble x_end,
                                jint n_steps,
                                int (*solver)(const char*, double, double, double, int, double*, double*, int)) {
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

    int count = solver(str, x0, y0, x_end, n_steps, out_x, out_y, max_out);

    jobject result = NULL;
    if (count > 0) {
        jdoubleArray xs_array = (*env)->NewDoubleArray(env, count);
        jdoubleArray ys_array = (*env)->NewDoubleArray(env, count);
        if (!xs_array || !ys_array) {
            if (xs_array) (*env)->DeleteLocalRef(env, xs_array);
            if (ys_array) (*env)->DeleteLocalRef(env, ys_array);
            free(out_x);
            free(out_y);
            (*env)->ReleaseStringUTFChars(env, expr, str);
            return NULL;
        }
        
        (*env)->SetDoubleArrayRegion(env, xs_array, 0, count, out_x);
        (*env)->SetDoubleArrayRegion(env, ys_array, 0, count, out_y);

        jclass hashMapClass = (*env)->FindClass(env, "java/util/HashMap");
        if (!hashMapClass) {
            (*env)->DeleteLocalRef(env, xs_array);
            (*env)->DeleteLocalRef(env, ys_array);
            free(out_x);
            free(out_y);
            (*env)->ReleaseStringUTFChars(env, expr, str);
            return NULL;
        }
        
        jmethodID hashMapInit = (*env)->GetMethodID(env, hashMapClass, "<init>", "(I)V");
        jmethodID putMethod = (*env)->GetMethodID(env, hashMapClass, "put",
            "(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;");
        if (!hashMapInit || !putMethod) {
            (*env)->DeleteLocalRef(env, hashMapClass);
            (*env)->DeleteLocalRef(env, xs_array);
            (*env)->DeleteLocalRef(env, ys_array);
            free(out_x);
            free(out_y);
            (*env)->ReleaseStringUTFChars(env, expr, str);
            return NULL;
        }

        result = (*env)->NewObject(env, hashMapClass, hashMapInit, 3);
        if (result) {
            jstring keyXs = (*env)->NewStringUTF(env, "xs");
            jstring keyYs = (*env)->NewStringUTF(env, "ys");
            jstring keyCount = (*env)->NewStringUTF(env, "count");
            
            jclass integerClass = (*env)->FindClass(env, "java/lang/Integer");
            if (!integerClass || (*env)->ExceptionCheck(env)) {
                (*env)->DeleteLocalRef(env, keyXs);
                (*env)->DeleteLocalRef(env, keyYs);
                (*env)->DeleteLocalRef(env, keyCount);
                (*env)->DeleteLocalRef(env, result);
                (*env)->DeleteLocalRef(env, xs_array);
                (*env)->DeleteLocalRef(env, ys_array);
                (*env)->DeleteLocalRef(env, hashMapClass);
                free(out_x); free(out_y);
                (*env)->ReleaseStringUTFChars(env, expr, str);
                return NULL;
            }
            jmethodID integerInit = (*env)->GetMethodID(env, integerClass, "<init>", "(I)V");
            if ((*env)->ExceptionCheck(env)) {
                (*env)->DeleteLocalRef(env, integerClass);
                (*env)->DeleteLocalRef(env, keyXs);
                (*env)->DeleteLocalRef(env, keyYs);
                (*env)->DeleteLocalRef(env, keyCount);
                (*env)->DeleteLocalRef(env, result);
                (*env)->DeleteLocalRef(env, xs_array);
                (*env)->DeleteLocalRef(env, ys_array);
                (*env)->DeleteLocalRef(env, hashMapClass);
                free(out_x); free(out_y);
                (*env)->ReleaseStringUTFChars(env, expr, str);
                return NULL;
            }
            jobject countObj = (*env)->NewObject(env, integerClass, integerInit, count);
            if ((*env)->ExceptionCheck(env)) {
                (*env)->DeleteLocalRef(env, integerClass);
                (*env)->DeleteLocalRef(env, keyXs);
                (*env)->DeleteLocalRef(env, keyYs);
                (*env)->DeleteLocalRef(env, keyCount);
                (*env)->DeleteLocalRef(env, result);
                (*env)->DeleteLocalRef(env, xs_array);
                (*env)->DeleteLocalRef(env, ys_array);
                (*env)->DeleteLocalRef(env, hashMapClass);
                free(out_x); free(out_y);
                (*env)->ReleaseStringUTFChars(env, expr, str);
                return NULL;
            }

            (*env)->CallObjectMethod(env, result, putMethod, keyXs, xs_array);
            if ((*env)->ExceptionCheck(env)) {
                (*env)->DeleteLocalRef(env, countObj);
                (*env)->DeleteLocalRef(env, integerClass);
                (*env)->DeleteLocalRef(env, result);
                (*env)->DeleteLocalRef(env, keyXs);
                (*env)->DeleteLocalRef(env, keyYs);
                (*env)->DeleteLocalRef(env, keyCount);
                (*env)->DeleteLocalRef(env, xs_array);
                (*env)->DeleteLocalRef(env, ys_array);
                (*env)->DeleteLocalRef(env, hashMapClass);
                free(out_x); free(out_y);
                (*env)->ReleaseStringUTFChars(env, expr, str);
                return NULL;
            }
            (*env)->CallObjectMethod(env, result, putMethod, keyYs, ys_array);
            if ((*env)->ExceptionCheck(env)) {
                (*env)->DeleteLocalRef(env, countObj);
                (*env)->DeleteLocalRef(env, integerClass);
                (*env)->DeleteLocalRef(env, result);
                (*env)->DeleteLocalRef(env, keyXs);
                (*env)->DeleteLocalRef(env, keyYs);
                (*env)->DeleteLocalRef(env, keyCount);
                (*env)->DeleteLocalRef(env, xs_array);
                (*env)->DeleteLocalRef(env, ys_array);
                (*env)->DeleteLocalRef(env, hashMapClass);
                free(out_x); free(out_y);
                (*env)->ReleaseStringUTFChars(env, expr, str);
                return NULL;
            }
            (*env)->CallObjectMethod(env, result, putMethod, keyCount, countObj);
            if ((*env)->ExceptionCheck(env)) {
                (*env)->DeleteLocalRef(env, countObj);
                (*env)->DeleteLocalRef(env, integerClass);
                (*env)->DeleteLocalRef(env, result);
                (*env)->DeleteLocalRef(env, keyXs);
                (*env)->DeleteLocalRef(env, keyYs);
                (*env)->DeleteLocalRef(env, keyCount);
                (*env)->DeleteLocalRef(env, xs_array);
                (*env)->DeleteLocalRef(env, ys_array);
                (*env)->DeleteLocalRef(env, hashMapClass);
                free(out_x); free(out_y);
                (*env)->ReleaseStringUTFChars(env, expr, str);
                return NULL;
            }

            (*env)->DeleteLocalRef(env, keyXs);
            (*env)->DeleteLocalRef(env, keyYs);
            (*env)->DeleteLocalRef(env, keyCount);
            (*env)->DeleteLocalRef(env, countObj);
            (*env)->DeleteLocalRef(env, integerClass);
        }
        
        (*env)->DeleteLocalRef(env, xs_array);
        (*env)->DeleteLocalRef(env, ys_array);
        (*env)->DeleteLocalRef(env, hashMapClass);
    }

    free(out_x);
    free(out_y);
    (*env)->ReleaseStringUTFChars(env, expr, str);
    return result;
}

JNIEXPORT jobject JNICALL
Java_com_supercalc_CalcEngine_odeSolveEuler(JNIEnv* env, jclass clazz,
                                             jstring expr, jdouble x0, jdouble y0,
                                             jdouble x_end, jint n_steps) {
    return ode_solve_helper(env, clazz, expr, x0, y0, x_end, n_steps, ode_solve_euler);
}

JNIEXPORT jobject JNICALL
Java_com_supercalc_CalcEngine_odeSolveImprovedEuler(JNIEnv* env, jclass clazz,
                                                     jstring expr, jdouble x0, jdouble y0,
                                                     jdouble x_end, jint n_steps) {
    return ode_solve_helper(env, clazz, expr, x0, y0, x_end, n_steps, ode_solve_improved_euler);
}

JNIEXPORT jobject JNICALL
Java_com_supercalc_CalcEngine_odeSolveMidpoint(JNIEnv* env, jclass clazz,
                                                jstring expr, jdouble x0, jdouble y0,
                                                jdouble x_end, jint n_steps) {
    return ode_solve_helper(env, clazz, expr, x0, y0, x_end, n_steps, ode_solve_midpoint);
}

/* ---- ODE RKF45 (adaptive step size) ---- */

JNIEXPORT jobject JNICALL
Java_com_supercalc_CalcEngine_odeSolveRkf45(JNIEnv* env, jclass clazz,
                                              jstring expr, jdouble x0, jdouble y0,
                                              jdouble x_end, jdouble tol) {
    const char* str = (*env)->GetStringUTFChars(env, expr, NULL);
    if (!str) return NULL;

    int max_points = 100000;
    double* out_x = malloc(max_points * sizeof(double));
    double* out_y = malloc(max_points * sizeof(double));
    if (!out_x || !out_y) {
        free(out_x);
        free(out_y);
        (*env)->ReleaseStringUTFChars(env, expr, str);
        return NULL;
    }

    int count = ode_solve_rkf45(str, x0, y0, x_end, tol, out_x, out_y, max_points);

    jobject result = NULL;
    if (count > 0) {
        jdoubleArray xs_array = (*env)->NewDoubleArray(env, count);
        jdoubleArray ys_array = (*env)->NewDoubleArray(env, count);
        if (!xs_array || !ys_array) {
            if (xs_array) (*env)->DeleteLocalRef(env, xs_array);
            if (ys_array) (*env)->DeleteLocalRef(env, ys_array);
            free(out_x);
            free(out_y);
            (*env)->ReleaseStringUTFChars(env, expr, str);
            return NULL;
        }

        (*env)->SetDoubleArrayRegion(env, xs_array, 0, count, out_x);
        (*env)->SetDoubleArrayRegion(env, ys_array, 0, count, out_y);

        jclass hashMapClass = (*env)->FindClass(env, "java/util/HashMap");
        if (!hashMapClass) {
            (*env)->DeleteLocalRef(env, xs_array);
            (*env)->DeleteLocalRef(env, ys_array);
            free(out_x);
            free(out_y);
            (*env)->ReleaseStringUTFChars(env, expr, str);
            return NULL;
        }

        jmethodID hashMapInit = (*env)->GetMethodID(env, hashMapClass, "<init>", "(I)V");
        jmethodID putMethod = (*env)->GetMethodID(env, hashMapClass, "put",
            "(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;");
        if (!hashMapInit || !putMethod) {
            (*env)->DeleteLocalRef(env, hashMapClass);
            (*env)->DeleteLocalRef(env, xs_array);
            (*env)->DeleteLocalRef(env, ys_array);
            free(out_x);
            free(out_y);
            (*env)->ReleaseStringUTFChars(env, expr, str);
            return NULL;
        }

        result = (*env)->NewObject(env, hashMapClass, hashMapInit, 3);
        if (result) {
            jstring keyXs = (*env)->NewStringUTF(env, "xs");
            jstring keyYs = (*env)->NewStringUTF(env, "ys");
            jstring keyCount = (*env)->NewStringUTF(env, "count");

            jclass integerClass = (*env)->FindClass(env, "java/lang/Integer");
            if (!integerClass || (*env)->ExceptionCheck(env)) {
                (*env)->DeleteLocalRef(env, keyXs);
                (*env)->DeleteLocalRef(env, keyYs);
                (*env)->DeleteLocalRef(env, keyCount);
                (*env)->DeleteLocalRef(env, result);
                (*env)->DeleteLocalRef(env, xs_array);
                (*env)->DeleteLocalRef(env, ys_array);
                (*env)->DeleteLocalRef(env, hashMapClass);
                free(out_x); free(out_y);
                (*env)->ReleaseStringUTFChars(env, expr, str);
                return NULL;
            }
            jmethodID integerInit = (*env)->GetMethodID(env, integerClass, "<init>", "(I)V");
            if ((*env)->ExceptionCheck(env)) {
                (*env)->DeleteLocalRef(env, integerClass);
                (*env)->DeleteLocalRef(env, keyXs);
                (*env)->DeleteLocalRef(env, keyYs);
                (*env)->DeleteLocalRef(env, keyCount);
                (*env)->DeleteLocalRef(env, result);
                (*env)->DeleteLocalRef(env, xs_array);
                (*env)->DeleteLocalRef(env, ys_array);
                (*env)->DeleteLocalRef(env, hashMapClass);
                free(out_x); free(out_y);
                (*env)->ReleaseStringUTFChars(env, expr, str);
                return NULL;
            }
            jobject countObj = (*env)->NewObject(env, integerClass, integerInit, count);
            if ((*env)->ExceptionCheck(env)) {
                (*env)->DeleteLocalRef(env, integerClass);
                (*env)->DeleteLocalRef(env, keyXs);
                (*env)->DeleteLocalRef(env, keyYs);
                (*env)->DeleteLocalRef(env, keyCount);
                (*env)->DeleteLocalRef(env, result);
                (*env)->DeleteLocalRef(env, xs_array);
                (*env)->DeleteLocalRef(env, ys_array);
                (*env)->DeleteLocalRef(env, hashMapClass);
                free(out_x); free(out_y);
                (*env)->ReleaseStringUTFChars(env, expr, str);
                return NULL;
            }

            (*env)->CallObjectMethod(env, result, putMethod, keyXs, xs_array);
            if ((*env)->ExceptionCheck(env)) {
                (*env)->DeleteLocalRef(env, countObj);
                (*env)->DeleteLocalRef(env, integerClass);
                (*env)->DeleteLocalRef(env, result);
                (*env)->DeleteLocalRef(env, keyXs);
                (*env)->DeleteLocalRef(env, keyYs);
                (*env)->DeleteLocalRef(env, keyCount);
                (*env)->DeleteLocalRef(env, xs_array);
                (*env)->DeleteLocalRef(env, ys_array);
                (*env)->DeleteLocalRef(env, hashMapClass);
                free(out_x); free(out_y);
                (*env)->ReleaseStringUTFChars(env, expr, str);
                return NULL;
            }
            (*env)->CallObjectMethod(env, result, putMethod, keyYs, ys_array);
            if ((*env)->ExceptionCheck(env)) {
                (*env)->DeleteLocalRef(env, countObj);
                (*env)->DeleteLocalRef(env, integerClass);
                (*env)->DeleteLocalRef(env, result);
                (*env)->DeleteLocalRef(env, keyXs);
                (*env)->DeleteLocalRef(env, keyYs);
                (*env)->DeleteLocalRef(env, keyCount);
                (*env)->DeleteLocalRef(env, xs_array);
                (*env)->DeleteLocalRef(env, ys_array);
                (*env)->DeleteLocalRef(env, hashMapClass);
                free(out_x); free(out_y);
                (*env)->ReleaseStringUTFChars(env, expr, str);
                return NULL;
            }
            (*env)->CallObjectMethod(env, result, putMethod, keyCount, countObj);
            if ((*env)->ExceptionCheck(env)) {
                (*env)->DeleteLocalRef(env, countObj);
                (*env)->DeleteLocalRef(env, integerClass);
                (*env)->DeleteLocalRef(env, result);
                (*env)->DeleteLocalRef(env, keyXs);
                (*env)->DeleteLocalRef(env, keyYs);
                (*env)->DeleteLocalRef(env, keyCount);
                (*env)->DeleteLocalRef(env, xs_array);
                (*env)->DeleteLocalRef(env, ys_array);
                (*env)->DeleteLocalRef(env, hashMapClass);
                free(out_x); free(out_y);
                (*env)->ReleaseStringUTFChars(env, expr, str);
                return NULL;
            }

            (*env)->DeleteLocalRef(env, keyXs);
            (*env)->DeleteLocalRef(env, keyYs);
            (*env)->DeleteLocalRef(env, keyCount);
            (*env)->DeleteLocalRef(env, countObj);
            (*env)->DeleteLocalRef(env, integerClass);
        }

        (*env)->DeleteLocalRef(env, xs_array);
        (*env)->DeleteLocalRef(env, ys_array);
        (*env)->DeleteLocalRef(env, hashMapClass);
    }

    free(out_x);
    free(out_y);
    (*env)->ReleaseStringUTFChars(env, expr, str);
    return result;
}

/* ---- Custom Function Registry ---- */

JNIEXPORT jboolean JNICALL
Java_com_supercalc_CalcEngine_customFuncDefine(JNIEnv* env, jclass clazz,
                                                jstring name, jstring body) {
    const char* nameStr = (*env)->GetStringUTFChars(env, name, NULL);
    const char* bodyStr = (*env)->GetStringUTFChars(env, body, NULL);
    if (!nameStr || !bodyStr) {
        if (nameStr) (*env)->ReleaseStringUTFChars(env, name, nameStr);
        if (bodyStr) (*env)->ReleaseStringUTFChars(env, body, bodyStr);
        return JNI_FALSE;
    }
    int result = custom_func_define(nameStr, bodyStr);
    (*env)->ReleaseStringUTFChars(env, name, nameStr);
    (*env)->ReleaseStringUTFChars(env, body, bodyStr);
    return result ? JNI_TRUE : JNI_FALSE;
}

JNIEXPORT void JNICALL
Java_com_supercalc_CalcEngine_customFuncClear(JNIEnv* env, jclass clazz) {
    custom_func_clear();
}

JNIEXPORT jboolean JNICALL
Java_com_supercalc_CalcEngine_customFuncDelete(JNIEnv* env, jclass clazz,
                                                jstring name) {
    const char* nameStr = (*env)->GetStringUTFChars(env, name, NULL);
    if (!nameStr) return JNI_FALSE;
    int result = custom_func_delete(nameStr);
    (*env)->ReleaseStringUTFChars(env, name, nameStr);
    return result ? JNI_TRUE : JNI_FALSE;
}

JNIEXPORT jstring JNICALL
Java_com_supercalc_CalcEngine_customFuncList(JNIEnv* env, jclass clazz) {
    char buf[4096];
    int len = custom_func_list(buf, sizeof(buf));
    if (len <= 0) return (*env)->NewStringUTF(env, "");
    return (*env)->NewStringUTF(env, buf);
}

/* ---- Laplace Transform ---- */

JNIEXPORT jdouble JNICALL
Java_com_supercalc_CalcEngine_laplaceTransform(JNIEnv* env, jclass clazz,
                                               jstring expr, jdouble s) {
    const char* str = (*env)->GetStringUTFChars(env, expr, NULL);
    if (!str) return NAN;
    double result = laplace_transform(str, s);
    (*env)->ReleaseStringUTFChars(env, expr, str);
    return result;
}

JNIEXPORT jdouble JNICALL
Java_com_supercalc_CalcEngine_inverseLaplace(JNIEnv* env, jclass clazz,
                                             jstring expr, jdouble t) {
    const char* str = (*env)->GetStringUTFChars(env, expr, NULL);
    if (!str) return NAN;
    double result = inverse_laplace(str, t);
    (*env)->ReleaseStringUTFChars(env, expr, str);
    return result;
}

/* ---- Calculation History ---- */

JNIEXPORT void JNICALL
Java_com_supercalc_CalcEngine_historyAdd(JNIEnv* env, jclass clazz,
                                          jstring expr, jdouble result) {
    const char* str = (*env)->GetStringUTFChars(env, expr, NULL);
    if (!str) return;
    history_add(str, result);
    (*env)->ReleaseStringUTFChars(env, expr, str);
}

JNIEXPORT jint JNICALL
Java_com_supercalc_CalcEngine_historyCount(JNIEnv* env, jclass clazz) {
    return (jint)history_count();
}

JNIEXPORT jboolean JNICALL
Java_com_supercalc_CalcEngine_historyGet(JNIEnv* env, jclass clazz,
                                          jint index, jobject resultObj) {
    char exprBuf[256];
    double resultVal = 0.0;
    int ok = history_get((int)index, exprBuf, sizeof(exprBuf), &resultVal);
    if (!ok) return JNI_FALSE;

    /* Put expression and result into the HashMap */
    jclass hashMapClass = (*env)->FindClass(env, "java/util/HashMap");
    if (!hashMapClass) return JNI_FALSE;
    jmethodID putMethod = (*env)->GetMethodID(env, hashMapClass, "put",
        "(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;");
    if (!putMethod) { (*env)->DeleteLocalRef(env, hashMapClass); return JNI_FALSE; }

    jstring keyExpr = (*env)->NewStringUTF(env, "expr");
    jstring valExpr = (*env)->NewStringUTF(env, exprBuf);
    (*env)->CallObjectMethod(env, resultObj, putMethod, keyExpr, valExpr);
    if ((*env)->ExceptionCheck(env)) {
        (*env)->DeleteLocalRef(env, keyExpr);
        if (valExpr) (*env)->DeleteLocalRef(env, valExpr);
        (*env)->DeleteLocalRef(env, hashMapClass);
        return JNI_FALSE;
    }
    (*env)->DeleteLocalRef(env, keyExpr);
    (*env)->DeleteLocalRef(env, valExpr);

    jclass doubleClass = (*env)->FindClass(env, "java/lang/Double");
    if (!doubleClass || (*env)->ExceptionCheck(env)) {
        (*env)->DeleteLocalRef(env, hashMapClass);
        return JNI_FALSE;
    }
    jmethodID valueOfDouble = (*env)->GetStaticMethodID(env, doubleClass, "valueOf", "(D)Ljava/lang/Double;");
    if (!valueOfDouble || (*env)->ExceptionCheck(env)) {
        (*env)->DeleteLocalRef(env, doubleClass);
        (*env)->DeleteLocalRef(env, hashMapClass);
        return JNI_FALSE;
    }
    jobject resultDouble = (*env)->CallStaticObjectMethod(env, doubleClass, valueOfDouble, resultVal);
    if ((*env)->ExceptionCheck(env)) {
        (*env)->DeleteLocalRef(env, doubleClass);
        (*env)->DeleteLocalRef(env, hashMapClass);
        return JNI_FALSE;
    }
    jstring keyResult = (*env)->NewStringUTF(env, "result");
    (*env)->CallObjectMethod(env, resultObj, putMethod, keyResult, resultDouble);
    if ((*env)->ExceptionCheck(env)) {
        (*env)->DeleteLocalRef(env, keyResult);
        (*env)->DeleteLocalRef(env, resultDouble);
        (*env)->DeleteLocalRef(env, doubleClass);
        (*env)->DeleteLocalRef(env, hashMapClass);
        return JNI_FALSE;
    }
    (*env)->DeleteLocalRef(env, keyResult);
    (*env)->DeleteLocalRef(env, resultDouble);
    (*env)->DeleteLocalRef(env, doubleClass);
    (*env)->DeleteLocalRef(env, hashMapClass);

    return JNI_TRUE;
}

JNIEXPORT void JNICALL
Java_com_supercalc_CalcEngine_historyClear(JNIEnv* env, jclass clazz) {
    history_clear();
}

JNIEXPORT jstring JNICALL
Java_com_supercalc_CalcEngine_historyGetAll(JNIEnv* env, jclass clazz) {
    char buf[8192];
    int len = history_get_all(buf, sizeof(buf));
    if (len <= 0) return (*env)->NewStringUTF(env, "");
    return (*env)->NewStringUTF(env, buf);
}

/* ---- Akima Interpolation ---- */

JNIEXPORT jdouble JNICALL
Java_com_supercalc_CalcEngine_interpAkima(JNIEnv* env, jclass clazz,
                                           jdoubleArray xs, jdoubleArray ys,
                                           jdouble x) {
    jsize n = (*env)->GetArrayLength(env, xs);
    jsize ny = (*env)->GetArrayLength(env, ys);
    if (n != ny || n < 2) return NAN;

    jdouble* x_vals = (*env)->GetDoubleArrayElements(env, xs, NULL);
    jdouble* y_vals = (*env)->GetDoubleArrayElements(env, ys, NULL);
    if (!x_vals || !y_vals) {
        if (x_vals) (*env)->ReleaseDoubleArrayElements(env, xs, x_vals, JNI_ABORT);
        if (y_vals) (*env)->ReleaseDoubleArrayElements(env, ys, y_vals, JNI_ABORT);
        return NAN;
    }

    double result = interp_akima(x_vals, y_vals, (int)n, x);

    (*env)->ReleaseDoubleArrayElements(env, xs, x_vals, JNI_ABORT);
    (*env)->ReleaseDoubleArrayElements(env, ys, y_vals, JNI_ABORT);
    return result;
}

/* ---- Natural Spline Interpolation ---- */

JNIEXPORT jdouble JNICALL
Java_com_supercalc_CalcEngine_interpNaturalSpline(JNIEnv* env, jclass clazz,
                                                   jdoubleArray xs, jdoubleArray ys,
                                                   jdouble x) {
    jsize n = (*env)->GetArrayLength(env, xs);
    jsize ny = (*env)->GetArrayLength(env, ys);
    if (n != ny || n < 2) return NAN;

    jdouble* x_vals = (*env)->GetDoubleArrayElements(env, xs, NULL);
    jdouble* y_vals = (*env)->GetDoubleArrayElements(env, ys, NULL);
    if (!x_vals || !y_vals) {
        if (x_vals) (*env)->ReleaseDoubleArrayElements(env, xs, x_vals, JNI_ABORT);
        if (y_vals) (*env)->ReleaseDoubleArrayElements(env, ys, y_vals, JNI_ABORT);
        return NAN;
    }

    double result = interp_natural_spline(x_vals, y_vals, (int)n, x);

    (*env)->ReleaseDoubleArrayElements(env, xs, x_vals, JNI_ABORT);
    (*env)->ReleaseDoubleArrayElements(env, ys, y_vals, JNI_ABORT);
    return result;
}

/* ---- Contour Grid Evaluation ---- */

JNIEXPORT jdoubleArray JNICALL
Java_com_supercalc_CalcEngine_contourGridEval(JNIEnv* env, jclass clazz,
                                               jstring expr, jdouble xMin, jdouble xMax,
                                               jdouble yMin, jdouble yMax,
                                               jint nCols, jint nRows) {
    const char* str = (*env)->GetStringUTFChars(env, expr, NULL);
    if (!str) return NULL;

    int total = nCols * nRows;
    double* buf = (double*)malloc(total * sizeof(double));
    if (!buf) {
        (*env)->ReleaseStringUTFChars(env, expr, str);
        return NULL;
    }

    int rc = contour_grid_eval(str, xMin, xMax, yMin, yMax, nCols, nRows, buf);
    (*env)->ReleaseStringUTFChars(env, expr, str);

    if (rc != 0) {
        free(buf);
        return NULL;
    }

    jdoubleArray result = (*env)->NewDoubleArray(env, total);
    if (result) {
        (*env)->SetDoubleArrayRegion(env, result, 0, total, buf);
    }
    free(buf);
    return result;
}

/* ---- Vector Field Grid Evaluation ---- */

JNIEXPORT jdoubleArray JNICALL
Java_com_supercalc_CalcEngine_vectorFieldGridEval(JNIEnv* env, jclass clazz,
                                                   jstring exprP, jstring exprQ,
                                                   jdouble xMin, jdouble xMax,
                                                   jdouble yMin, jdouble yMax,
                                                   jint nCols, jint nRows) {
    const char* strP = (*env)->GetStringUTFChars(env, exprP, NULL);
    const char* strQ = (*env)->GetStringUTFChars(env, exprQ, NULL);
    if (!strP || !strQ) {
        if (strP) (*env)->ReleaseStringUTFChars(env, exprP, strP);
        if (strQ) (*env)->ReleaseStringUTFChars(env, exprQ, strQ);
        return NULL;
    }

    int total = nCols * nRows;
    double* out_p = (double*)malloc(total * sizeof(double));
    double* out_q = (double*)malloc(total * sizeof(double));
    if (!out_p || !out_q) {
        free(out_p);
        free(out_q);
        (*env)->ReleaseStringUTFChars(env, exprP, strP);
        (*env)->ReleaseStringUTFChars(env, exprQ, strQ);
        return NULL;
    }

    int rc = vector_field_grid_eval(strP, strQ, xMin, xMax, yMin, yMax,
                                     nCols, nRows, out_p, out_q);

    (*env)->ReleaseStringUTFChars(env, exprP, strP);
    (*env)->ReleaseStringUTFChars(env, exprQ, strQ);

    jdoubleArray jresult = NULL;
    if (rc == 0) {
        jresult = (*env)->NewDoubleArray(env, 2 * total);
        if (jresult) {
            double* flat = (double*)malloc(2 * total * sizeof(double));
            if (flat) {
                for (int i = 0; i < total; i++) {
                    flat[i] = out_p[i];
                    flat[total + i] = out_q[i];
                }
                (*env)->SetDoubleArrayRegion(env, jresult, 0, 2 * total, flat);
                free(flat);
            }
        }
    }

    free(out_p);
    free(out_q);
    return jresult;
}

/* ---- Sparse Matrix Solver ---- */

typedef struct SparseMatrix SparseMatrix;

SparseMatrix* sparse_from_triplets(int n_rows, int n_cols,
                                    const int* rows, const int* cols,
                                    const double* vals, int nnz);
int sparse_to_dense(const SparseMatrix* m, double* out, int max_out);
int sparse_spmv(const SparseMatrix* m, const double* x, double* y, int n);
int sparse_solve_cg(const SparseMatrix* m, const double* b, double* x,
                     int max_iter, double tol, double* out_x, int n);
int sparse_matrix_nnz(const SparseMatrix* m);
void sparse_matrix_free(SparseMatrix* m);

JNIEXPORT jdoubleArray JNICALL
Java_com_supercalc_CalcEngine_sparseFromTriplets(JNIEnv* env, jclass clazz,
                                                  jint nRows, jint nCols,
                                                  jintArray rows, jintArray cols,
                                                  jdoubleArray vals) {
    jsize nnz = (*env)->GetArrayLength(env, vals);
    if ((*env)->GetArrayLength(env, rows) != nnz || (*env)->GetArrayLength(env, cols) != nnz) {
        return NULL;
    }

    jint* row_data = (*env)->GetIntArrayElements(env, rows, NULL);
    jint* col_data = (*env)->GetIntArrayElements(env, cols, NULL);
    jdouble* val_data = (*env)->GetDoubleArrayElements(env, vals, NULL);
    if (!row_data || !col_data || !val_data) {
        if (row_data) (*env)->ReleaseIntArrayElements(env, rows, row_data, JNI_ABORT);
        if (col_data) (*env)->ReleaseIntArrayElements(env, cols, col_data, JNI_ABORT);
        if (val_data) (*env)->ReleaseDoubleArrayElements(env, vals, val_data, JNI_ABORT);
        return NULL;
    }

    SparseMatrix* m = sparse_from_triplets(nRows, nCols, row_data, col_data, val_data, (int)nnz);

    (*env)->ReleaseIntArrayElements(env, rows, row_data, JNI_ABORT);
    (*env)->ReleaseIntArrayElements(env, cols, col_data, JNI_ABORT);
    (*env)->ReleaseDoubleArrayElements(env, vals, val_data, JNI_ABORT);

    if (!m) return NULL;

    /* Return dense matrix as flat double array */
    int total = m->n_rows * m->n_cols;
    double* dense = (double*)malloc(total * sizeof(double));
    if (!dense) {
        sparse_matrix_free(m);
        return NULL;
    }
    sparse_to_dense(m, dense, total);
    sparse_matrix_free(m);

    jdoubleArray result = (*env)->NewDoubleArray(env, total);
    if (result) {
        (*env)->SetDoubleArrayRegion(env, result, 0, total, dense);
    }
    free(dense);
    return result;
}

JNIEXPORT jdoubleArray JNICALL
Java_com_supercalc_CalcEngine_sparseSpmv(JNIEnv* env, jclass clazz,
                                          jint nRows, jint nCols,
                                          jintArray rows, jintArray cols,
                                          jdoubleArray vals, jdoubleArray x) {
    jsize nnz = (*env)->GetArrayLength(env, vals);
    jsize n = (*env)->GetArrayLength(env, x);
    if ((*env)->GetArrayLength(env, rows) != nnz || (*env)->GetArrayLength(env, cols) != nnz) {
        return NULL;
    }

    jint* row_data = (*env)->GetIntArrayElements(env, rows, NULL);
    jint* col_data = (*env)->GetIntArrayElements(env, cols, NULL);
    jdouble* val_data = (*env)->GetDoubleArrayElements(env, vals, NULL);
    jdouble* x_data = (*env)->GetDoubleArrayElements(env, x, NULL);
    if (!row_data || !col_data || !val_data || !x_data) {
        if (row_data) (*env)->ReleaseIntArrayElements(env, rows, row_data, JNI_ABORT);
        if (col_data) (*env)->ReleaseIntArrayElements(env, cols, col_data, JNI_ABORT);
        if (val_data) (*env)->ReleaseDoubleArrayElements(env, vals, val_data, JNI_ABORT);
        if (x_data) (*env)->ReleaseDoubleArrayElements(env, x, x_data, JNI_ABORT);
        return NULL;
    }

    SparseMatrix* m = sparse_from_triplets(nRows, nCols, row_data, col_data, val_data, (int)nnz);

    (*env)->ReleaseIntArrayElements(env, rows, row_data, JNI_ABORT);
    (*env)->ReleaseIntArrayElements(env, cols, col_data, JNI_ABORT);
    (*env)->ReleaseDoubleArrayElements(env, vals, val_data, JNI_ABORT);

    if (!m) return NULL;

    double* y_out = (double*)malloc(m->n_rows * sizeof(double));
    if (!y_out) {
        sparse_matrix_free(m);
        return NULL;
    }

    sparse_spmv(m, x_data, y_out, (int)n);
    (*env)->ReleaseDoubleArrayElements(env, x, x_data, JNI_ABORT);

    jdoubleArray result = (*env)->NewDoubleArray(env, m->n_rows);
    if (result) {
        (*env)->SetDoubleArrayRegion(env, result, 0, m->n_rows, y_out);
    }

    sparse_matrix_free(m);
    free(y_out);
    return result;
}

JNIEXPORT jdoubleArray JNICALL
Java_com_supercalc_CalcEngine_sparseSolveCg(JNIEnv* env, jclass clazz,
                                             jint nRows, jint nCols,
                                             jintArray rows, jintArray cols,
                                             jdoubleArray vals, jdoubleArray b,
                                             jint maxIter, jdouble tol) {
    jsize nnz = (*env)->GetArrayLength(env, vals);
    jsize n = (*env)->GetArrayLength(env, b);
    if ((*env)->GetArrayLength(env, rows) != nnz || (*env)->GetArrayLength(env, cols) != nnz) {
        return NULL;
    }

    jint* row_data = (*env)->GetIntArrayElements(env, rows, NULL);
    jint* col_data = (*env)->GetIntArrayElements(env, cols, NULL);
    jdouble* val_data = (*env)->GetDoubleArrayElements(env, vals, NULL);
    jdouble* b_data = (*env)->GetDoubleArrayElements(env, b, NULL);
    if (!row_data || !col_data || !val_data || !b_data) {
        if (row_data) (*env)->ReleaseIntArrayElements(env, rows, row_data, JNI_ABORT);
        if (col_data) (*env)->ReleaseIntArrayElements(env, cols, col_data, JNI_ABORT);
        if (val_data) (*env)->ReleaseDoubleArrayElements(env, vals, val_data, JNI_ABORT);
        if (b_data) (*env)->ReleaseDoubleArrayElements(env, b, b_data, JNI_ABORT);
        return NULL;
    }

    SparseMatrix* m = sparse_from_triplets(nRows, nCols, row_data, col_data, val_data, (int)nnz);

    (*env)->ReleaseIntArrayElements(env, rows, row_data, JNI_ABORT);
    (*env)->ReleaseIntArrayElements(env, cols, col_data, JNI_ABORT);
    (*env)->ReleaseDoubleArrayElements(env, vals, val_data, JNI_ABORT);

    if (!m) return NULL;

    double* x_out = (double*)malloc(n * sizeof(double));
    if (!x_out) {
        sparse_matrix_free(m);
        return NULL;
    }

    int iters = sparse_solve_cg(m, b_data, NULL, (int)maxIter, (double)tol, x_out, (int)n);
    (*env)->ReleaseDoubleArrayElements(env, b, b_data, JNI_ABORT);

    jdoubleArray result = NULL;
    if (iters >= 0) {
        result = (*env)->NewDoubleArray(env, n);
        if (result) {
            (*env)->SetDoubleArrayRegion(env, result, 0, n, x_out);
        }
    }

    sparse_matrix_free(m);
    free(x_out);
    return result;
}
