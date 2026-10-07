#ifndef SUPERCALC_CORE_H
#define SUPERCALC_CORE_H

#include <stdint.h>

#if defined(_WIN32) || defined(__CYGWIN__)
  #if defined(SUPERCALC_CORE_BUILD)
    #define SC_API __declspec(dllexport)
  #else
    #define SC_API __declspec(dllimport)
  #endif
#else
  #define SC_API __attribute__((visibility("default")))
#endif

#ifdef __cplusplus
extern "C" {
#endif

typedef struct sc_context sc_context_t;

enum {
    SC_ABI_VERSION = 1,
    SC_OK = 0,
    SC_INVALID_ARGUMENT = 1,
    SC_CALCULATION_ERROR = 2,
    SC_BUFFER_TOO_SMALL = 3,
};

SC_API int32_t sc_abi_version(void);
SC_API sc_context_t* sc_context_create(void);
SC_API void sc_context_destroy(sc_context_t* context);
SC_API const char* sc_last_error(const sc_context_t* context);

SC_API int32_t sc_evaluate(
    sc_context_t* context,
    const char* expression,
    double x,
    double y,
    double* result);

SC_API int32_t sc_evaluate_array(
    sc_context_t* context,
    const char* expression,
    const double* xs,
    int32_t count,
    double* results);

SC_API int32_t sc_derivative(
    sc_context_t* context,
    const char* expression,
    double x,
    double step,
    double* result);

SC_API int32_t sc_integrate(
    sc_context_t* context,
    const char* expression,
    double a,
    double b,
    double tolerance,
    double* result);

SC_API int32_t sc_solve(
    sc_context_t* context,
    const char* expression,
    double guess,
    double xmin,
    double xmax,
    double tolerance,
    int32_t max_iterations,
    double* result);

#ifdef __cplusplus
}
#endif

#endif  // SUPERCALC_CORE_H
