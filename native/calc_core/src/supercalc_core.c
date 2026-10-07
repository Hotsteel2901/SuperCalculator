#include "supercalc_core.h"

#include <math.h>
#include <stdlib.h>
#include <string.h>

/* Transitional declarations from the legacy implementation. The wrapper is
 * intentionally additive: existing Python and Android entry points remain
 * available until their parity tests pass against this ABI. */
extern const char* get_last_error(void);
extern double evaluate(const char* expression, double x);
extern double evaluate_xy(const char* expression, double x, double y);
extern void evaluate_array(const char* expression, const double* xs, double* out, int n);
extern double derivative(const char* expression, double x, double h);
extern double integrate_adaptive(const char* expression, double a, double b, double tol);
extern double solve_equation(const char* expression, double guess, double xmin, double xmax,
                             double tol, int max_iter);

struct sc_context {
    uint32_t magic;
};

static int valid_context(const sc_context_t* context) {
    return context != NULL && context->magic == 0x53434F52u;
}

static int valid_text(const char* expression) {
    return expression != NULL && expression[0] != '\0';
}

static int status_from_result(double value) {
    return isfinite(value) ? SC_OK : SC_CALCULATION_ERROR;
}

SC_API int32_t sc_abi_version(void) {
    return SC_ABI_VERSION;
}

SC_API sc_context_t* sc_context_create(void) {
    sc_context_t* context = (sc_context_t*)calloc(1, sizeof(sc_context_t));
    if (context != NULL) context->magic = 0x53434F52u;
    return context;
}

SC_API void sc_context_destroy(sc_context_t* context) {
    if (valid_context(context)) {
        context->magic = 0;
        free(context);
    }
}

SC_API const char* sc_last_error(const sc_context_t* context) {
    (void)context;
    const char* message = get_last_error();
    return message == NULL ? "Native calculation failed." : message;
}

SC_API int32_t sc_evaluate(
    sc_context_t* context,
    const char* expression,
    double x,
    double y,
    double* result) {
    if (!valid_context(context) || !valid_text(expression) || result == NULL) {
        return SC_INVALID_ARGUMENT;
    }
    const double value = evaluate_xy(expression, x, y);
    *result = value;
    return status_from_result(value);
}

SC_API int32_t sc_evaluate_array(
    sc_context_t* context,
    const char* expression,
    const double* xs,
    int32_t count,
    double* results) {
    if (!valid_context(context) || !valid_text(expression) || xs == NULL || results == NULL || count < 0) {
        return SC_INVALID_ARGUMENT;
    }
    if (count == 0) return SC_OK;
    /* Non-finite samples are valid plot discontinuities. The caller maps them
     * to gaps instead of failing the complete array operation. */
    evaluate_array(expression, xs, results, count);
    return SC_OK;
}

SC_API int32_t sc_derivative(
    sc_context_t* context,
    const char* expression,
    double x,
    double step,
    double* result) {
    if (!valid_context(context) || !valid_text(expression) || result == NULL || step == 0.0) {
        return SC_INVALID_ARGUMENT;
    }
    const double value = derivative(expression, x, step);
    *result = value;
    return status_from_result(value);
}

SC_API int32_t sc_integrate(
    sc_context_t* context,
    const char* expression,
    double a,
    double b,
    double tolerance,
    double* result) {
    if (!valid_context(context) || !valid_text(expression) || result == NULL || tolerance <= 0.0) {
        return SC_INVALID_ARGUMENT;
    }
    const double value = integrate_adaptive(expression, a, b, tolerance);
    *result = value;
    return status_from_result(value);
}

SC_API int32_t sc_solve(
    sc_context_t* context,
    const char* expression,
    double guess,
    double xmin,
    double xmax,
    double tolerance,
    int32_t max_iterations,
    double* result) {
    if (!valid_context(context) || !valid_text(expression) || result == NULL ||
        tolerance <= 0.0 || max_iterations <= 0 || xmin > xmax) {
        return SC_INVALID_ARGUMENT;
    }
    const double value = solve_equation(
        expression, guess, xmin, xmax, tolerance, max_iterations);
    *result = value;
    return status_from_result(value);
}
