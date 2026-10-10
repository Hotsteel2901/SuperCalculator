#include "supercalc_core.h"

#include <assert.h>
#include <math.h>
#include <stdio.h>

int main(void) {
    assert(sc_abi_version() == SC_ABI_VERSION);
    sc_context_t* context = sc_context_create();
    assert(context != NULL);

    double result = 0.0;
    assert(sc_evaluate(context, "x^2 + 1", 3.0, 0.0, &result) == SC_OK);
    assert(fabs(result - 10.0) < 1e-12);
    assert(sc_evaluate(context, "2x + 2(x + 1)", 3.0, 0.0, &result) == SC_OK);
    assert(fabs(result - 14.0) < 1e-12);
    assert(sc_evaluate(context, "x + y", 2.0, 3.0, &result) == SC_OK);
    assert(fabs(result - 5.0) < 1e-12);
    assert(sc_evaluate(context, "Sin(PI / 2)", 0.0, 0.0, &result) == SC_OK);
    assert(fabs(result - 1.0) < 1e-12);
    assert(sc_evaluate(context, "cbrt(-8)", 0.0, 0.0, &result) == SC_OK);
    assert(fabs(result + 2.0) < 1e-12);
    assert(sc_evaluate(context, "1 / 1e-20", 0.0, 0.0, &result) == SC_OK);
    assert(fabs(result - 1e20) / 1e20 < 1e-12);

    double xs[] = {0.0, 1.0, 2.0};
    double values[] = {0.0, 0.0, 0.0};
    assert(sc_evaluate_array(context, "x^2", xs, 3, values) == SC_OK);
    assert(fabs(values[2] - 4.0) < 1e-12);
    assert(sc_evaluate_array(context, "unknown(x)", xs, 3, values) == SC_CALCULATION_ERROR);

    double discontinuity_xs[] = {-1.0, 0.0, 1.0};
    double discontinuity_values[] = {0.0, 0.0, 0.0};
    assert(sc_evaluate_array(context, "1/x", discontinuity_xs, 3, discontinuity_values) == SC_OK);
    assert(isfinite(discontinuity_values[0]));
    assert(!isfinite(discontinuity_values[1]));
    assert(isfinite(discontinuity_values[2]));

    assert(sc_evaluate(context, "1/0", 0.0, 0.0, &result) != SC_OK);
    assert(sc_last_error(context) != NULL);
    assert(sc_evaluate(context, "x", NAN, 0.0, &result) == SC_INVALID_ARGUMENT);
    assert(sc_derivative(context, "x^2", 3.0, NAN, &result) == SC_INVALID_ARGUMENT);

    assert(sc_derivative(context, "x^2", 3.0, 1e-6, &result) == SC_OK);
    assert(fabs(result - 6.0) < 1e-5);
    assert(sc_integrate(context, "x^2", 0.0, 1.0, 1e-8, &result) == SC_OK);
    assert(fabs(result - (1.0 / 3.0)) < 1e-7);
    assert(sc_solve(context, "x^2 - 2", 1.0, -2.0, 2.0, 1e-10, 100, &result) == SC_OK);
    assert(fabs(result - sqrt(2.0)) < 1e-8);

    double ode_x[101] = {0.0};
    double ode_y[101] = {0.0};
    int32_t ode_count = 0;
    assert(sc_ode_rk4(context, "y", 0.0, 1.0, 1.0, 100,
                      ode_x, ode_y, 101, &ode_count) == SC_OK);
    assert(ode_count == 101);
    assert(fabs(ode_y[100] - exp(1.0)) < 1e-5);

    sc_context_destroy(context);
    puts("supercalc_core smoke test passed");
    return 0;
}
