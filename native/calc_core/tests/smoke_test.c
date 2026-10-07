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
    assert(sc_evaluate(context, "x + y", 2.0, 3.0, &result) == SC_OK);
    assert(fabs(result - 5.0) < 1e-12);

    double xs[] = {0.0, 1.0, 2.0};
    double values[] = {0.0, 0.0, 0.0};
    assert(sc_evaluate_array(context, "x^2", xs, 3, values) == SC_OK);
    assert(fabs(values[2] - 4.0) < 1e-12);

    double discontinuity_xs[] = {-1.0, 0.0, 1.0};
    double discontinuity_values[] = {0.0, 0.0, 0.0};
    assert(sc_evaluate_array(context, "1/x", discontinuity_xs, 3, discontinuity_values) == SC_OK);
    assert(isfinite(discontinuity_values[0]));
    assert(!isfinite(discontinuity_values[1]));
    assert(isfinite(discontinuity_values[2]));

    assert(sc_evaluate(context, "1/0", 0.0, 0.0, &result) != SC_OK);
    assert(sc_last_error(context) != NULL);

    sc_context_destroy(context);
    puts("supercalc_core smoke test passed");
    return 0;
}
