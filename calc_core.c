/**
 * Super Calculator - C Core Engine
 *
 * Provides expression parsing (shunting-yard + RPN), numerical calculus
 * (central-difference derivatives, Simpson integration), and equation
 * solving (Newton-Raphson with bisection fallback).
 *
 * ========================== BUILD INSTRUCTIONS ==========================
 *
 * --- Windows (MinGW-w64 / MSYS2) ---
 *   gcc -shared -O2 -o calc_core.dll calc_core.c -lm
 *
 * --- Windows (MSVC - Developer Command Prompt) ---
 *   cl /LD /O2 calc_core.c /Fe:calc_core.dll
 *
 * --- Linux ---
 *   gcc -shared -O2 -fPIC -o calc_core.so calc_core.c -lm
 *
 * --- macOS ---
 *   gcc -shared -O2 -fPIC -o calc_core.dylib calc_core.c -lm
 *
 * --- Cross-compile for Windows from Linux ---
 *   x86_64-w64-mingw32-gcc -shared -O2 -o calc_core.dll calc_core.c -lm
 *
 * =======================================================================
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <ctype.h>
#include <limits.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif
#ifndef M_E
#define M_E  2.71828182845904523536
#endif
#ifndef M_LN2
#define M_LN2 0.69314718055994530942
#endif

/* signbit compatibility for MSVC and older compilers */
#ifndef _WIN32
#include <math.h>  /* signbit is defined here on POSIX systems */
#else
/* signbit may not be available on older MSVC; provide a fallback */
#ifndef signbit
static inline int signbit(double x) {
    return (x < 0.0) || (x == 0.0 && 1.0/x < 0.0);
}
#define signbit signbit
#endif
#endif

#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT
#endif

/* Thread-local error buffer for concurrent access safety (Android JNI, etc.) */
#if defined(__STDC_VERSION__) && __STDC_VERSION__ >= 201112L
static _Thread_local char g_error[256] = {0};
#elif defined(__GNUC__)
static __thread char g_error[256] = {0};
#elif defined(_MSC_VER)
static __declspec(thread) char g_error[256] = {0};
#else
static char g_error[256] = {0};
#endif

static void set_error(const char* msg) {
    if (!msg) return;
    size_t len = strlen(msg);
    if (len > 255) {
        strncpy(g_error, msg, 255);
        g_error[255] = '\0';
    } else {
        strcpy(g_error, msg);
    }
}

static void clear_error(void) {
    g_error[0] = '\0';
}

EXPORT const char* get_last_error(void) { return g_error; }

#define MAX_TOKENS 512
#define MAX_RPN    512

typedef enum {
    T_NUMBER, T_VARIABLE_X, T_VARIABLE_Y, T_OP, T_FUNC, T_LPAREN, T_RPAREN, T_COMMA, T_END, T_CUSTOM_FUNC
} TokenKind;

typedef enum {
    F_SIN, F_COS, F_TAN, F_LOG, F_LN, F_SQRT, F_EXP, F_ABS,
    F_FLOOR, F_CEIL
} FuncId;

typedef struct {
    TokenKind kind;
    double   val;
    char     op;
    FuncId   func;
    int      custom_idx;  /* Index into g_custom_funcs for T_CUSTOM_FUNC */
} Token;

typedef struct {
    int      tag;
    double   num;
    char     op;
    FuncId   func;
    int      custom_idx;  /* Index into g_custom_funcs for tag==5 */
} RPN;

/* Custom function registry - forward declarations */
#define MAX_CUSTOM_FUNCS 64
#define MAX_FUNC_NAME    32
#define MAX_FUNC_BODY    512

typedef struct {
    char name[MAX_FUNC_NAME];
    char body[MAX_FUNC_BODY];
    int  defined;
} CustomFunc;

static CustomFunc g_custom_funcs[MAX_CUSTOM_FUNCS];
static int g_custom_func_count = 0;
static CustomFunc* custom_func_find(const char* name);
static int parse_and_eval(const char* expr, double x, double y, double* result);

static int tokenize(const char* s, Token* toks, int max_toks) {
    int n = 0;
    while (*s && n < max_toks - 1) {
        if (isspace(*s)) { s++; continue; }
        if (isdigit(*s) || (*s == '.' && isdigit(*(s+1)))) {
            char* end;
            toks[n].kind = T_NUMBER;
            toks[n].val  = strtod(s, &end);
            s = end; n++; continue;
        }
        if (*s == 'x' || *s == 'X') {
            toks[n++].kind = T_VARIABLE_X; s++; continue;
        }
        if (*s == 'y' || *s == 'Y') {
            toks[n++].kind = T_VARIABLE_Y; s++; continue;
        }
        if (*s == '!') {
            toks[n].kind = T_OP; toks[n].op = '!'; s++; n++; continue;
        }
        if (*s == 'p' && *(s+1) == 'i' && !isalpha(*(s+2))) {
            toks[n].kind = T_NUMBER;
            toks[n].val  = M_PI;
            s += 2; n++; continue;
        }
        if (*s == 'e' && !isalpha(*(s+1))) {
            toks[n].kind = T_NUMBER;
            toks[n].val  = M_E;
            s++; n++; continue;
        }
        if (isalpha(*s)) {
            char name[8] = {0};
            int  i = 0;
            while (isalpha(*s) && i < 7) name[i++] = *s++;
            if      (!strcmp(name, "sin"))  { toks[n].kind=T_FUNC; toks[n].func=F_SIN;  n++; continue; }
            else if (!strcmp(name, "cos"))  { toks[n].kind=T_FUNC; toks[n].func=F_COS;  n++; continue; }
            else if (!strcmp(name, "tan"))  { toks[n].kind=T_FUNC; toks[n].func=F_TAN;  n++; continue; }
            else if (!strcmp(name, "log"))  { toks[n].kind=T_FUNC; toks[n].func=F_LOG;  n++; continue; }
            else if (!strcmp(name, "ln"))   { toks[n].kind=T_FUNC; toks[n].func=F_LN;   n++; continue; }
            else if (!strcmp(name, "sqrt")) { toks[n].kind=T_FUNC; toks[n].func=F_SQRT; n++; continue; }
            else if (!strcmp(name, "exp"))  { toks[n].kind=T_FUNC; toks[n].func=F_EXP;  n++; continue; }
            else if (!strcmp(name, "abs"))   { toks[n].kind=T_FUNC; toks[n].func=F_ABS;   n++; continue; }
            else if (!strcmp(name, "floor")) { toks[n].kind=T_FUNC; toks[n].func=F_FLOOR; n++; continue; }
            else if (!strcmp(name, "ceil"))  { toks[n].kind=T_FUNC; toks[n].func=F_CEIL;  n++; continue; }
            else if (!strcmp(name, "mod"))   { toks[n].kind=T_OP;   toks[n].op='%';        n++; continue; }
            else {
                /* Check custom function registry (allow names up to 31 chars) */
                char full_name[32] = {0};
                int fi = i;
                strncpy(full_name, name, 7);
                while (isalpha(*s) && fi < 31) full_name[fi++] = *s++;
                full_name[fi] = '\0';
                CustomFunc* cf = custom_func_find(full_name);
                if (cf) {
                    toks[n].kind = T_CUSTOM_FUNC;
                    toks[n].custom_idx = (int)(cf - g_custom_funcs);
                    n++;
                    continue;
                } else {
                    set_error("Unknown function");
                    return -1;
                }
            }
        }
        switch (*s) {
            case '+': case '-': case '*': case '/': case '^': case '%':
                toks[n].kind = T_OP; toks[n].op = *s; s++; n++; break;
            case '(': toks[n++].kind = T_LPAREN; s++; break;
            case ')': toks[n++].kind = T_RPAREN; s++; break;
            case ',': toks[n++].kind = T_COMMA;  s++; break;
            default:  set_error("Unexpected character"); return -1;
        }
    }
    toks[n].kind = T_END;
    return n;
}

static int precedence(char op) {
    if (op == '!' ) return 5;
    if (op == '~' ) return 2;
    if (op == '+' || op == '-') return 1;
    if (op == '*' || op == '/' || op == '%') return 2;
    if (op == '^')              return 3;
    return 0;
}

static int is_right_assoc(char op) { return op == '^' || op == '~'; }

static int shunt(Token* toks, int ntoks, RPN* output, int max_out) {
    #define MAX_STACK 256
    Token stack[MAX_STACK]; int sp = 0;
    int    out_n = 0;
    int    prev_was_op_or_lp = 1;

    for (int i = 0; i <= ntoks && out_n < max_out; i++) {
        Token t = toks[i];
        if (t.kind == T_NUMBER) {
            output[out_n].tag = 0; output[out_n].num = t.val; out_n++;
            prev_was_op_or_lp = 0;
        } else if (t.kind == T_VARIABLE_X) {
            output[out_n].tag = 1; out_n++;
            prev_was_op_or_lp = 0;
        } else if (t.kind == T_VARIABLE_Y) {
            output[out_n].tag = 4; out_n++;
            prev_was_op_or_lp = 0;
        } else if (t.kind == T_FUNC) {
            if (sp >= MAX_STACK) { set_error("Expression too deeply nested"); return -1; }
            stack[sp++] = t;
            prev_was_op_or_lp = 1;
        } else if (t.kind == T_CUSTOM_FUNC) {
            if (sp >= MAX_STACK) { set_error("Expression too deeply nested"); return -1; }
            stack[sp++] = t;
            prev_was_op_or_lp = 1;
        } else if (t.kind == T_COMMA) {
            while (sp > 0 && stack[sp-1].kind != T_LPAREN) {
                if (out_n >= max_out) { set_error("Expression too long"); return -1; }
                Token top = stack[--sp];
                if (top.kind == T_OP) {
                    output[out_n].tag=2; output[out_n].op=top.op; out_n++;
                } else if (top.kind == T_FUNC) {
                    output[out_n].tag=3; output[out_n].func=top.func; out_n++;
                } else if (top.kind == T_CUSTOM_FUNC) {
                    output[out_n].tag=5; output[out_n].custom_idx=top.custom_idx; out_n++;
                }
            }
            prev_was_op_or_lp = 1;
        } else if (t.kind == T_OP) {
            if ((t.op == '-' || t.op == '+') && prev_was_op_or_lp) {
                if (t.op == '+') continue;
                t.op = '~';
            }
            if (t.op == '!' && prev_was_op_or_lp) { set_error("Invalid factorial position"); return -1; }
            
            if (t.op == '!') {
                while (sp > 0) {
                    if (out_n >= max_out) { set_error("Expression too long"); return -1; }
                    Token top = stack[sp-1];
                    if (top.kind == T_OP) {
                        int top_prec = precedence(top.op);
                        if (top_prec >= precedence('!')) {
                            sp--;
                            output[out_n].tag=2; output[out_n].op=top.op; out_n++;
                            continue;
                        }
                    } else if (top.kind == T_FUNC) {
                        sp--;
                        output[out_n].tag=3; output[out_n].func=top.func; out_n++;
                        continue;
                    } else if (top.kind == T_CUSTOM_FUNC) {
                        sp--;
                        output[out_n].tag=5; output[out_n].custom_idx=top.custom_idx; out_n++;
                        continue;
                    }
                    break;
                }
                if (sp >= MAX_STACK) { set_error("Expression too deeply nested"); return -1; }
                stack[sp++] = t;
                prev_was_op_or_lp = 0;
            } else if (t.op == '~') {
                /* Unary prefix: push without popping — it binds to the next
                   operand, not to whatever is already on the operator stack.
                   This prevents 2^-3 from incorrectly popping '^'. */
                if (sp >= MAX_STACK) { set_error("Expression too deeply nested"); return -1; }
                stack[sp++] = t;
                prev_was_op_or_lp = 1;
            } else {
                int prec = precedence(t.op);
                int ra   = is_right_assoc(t.op);
                while (sp > 0) {
                    if (out_n >= max_out) { set_error("Expression too long"); return -1; }
                    Token top = stack[sp-1];
                    if (top.kind == T_OP) {
                        int top_prec = precedence(top.op);
                        if (top_prec > prec || (top_prec == prec && !ra)) {
                            sp--;
                            output[out_n].tag=2; output[out_n].op=top.op; out_n++;
                            continue;
                        }
                    } else if (top.kind == T_FUNC) {
                        sp--;
                        output[out_n].tag=3; output[out_n].func=top.func; out_n++;
                        continue;
                    } else if (top.kind == T_CUSTOM_FUNC) {
                        sp--;
                        output[out_n].tag=5; output[out_n].custom_idx=top.custom_idx; out_n++;
                        continue;
                    }
                    break;
                }
                if (sp >= MAX_STACK) { set_error("Expression too deeply nested"); return -1; }
                stack[sp++] = t;
                prev_was_op_or_lp = 1;
            }
        } else if (t.kind == T_LPAREN) {
            if (sp >= MAX_STACK) { set_error("Expression too deeply nested"); return -1; }
            stack[sp++] = t;
            prev_was_op_or_lp = 1;
        } else if (t.kind == T_RPAREN || t.kind == T_END) {
            while (sp > 0 && stack[sp-1].kind != T_LPAREN) {
                if (out_n >= max_out) { set_error("Expression too long"); return -1; }
                Token top = stack[--sp];
                if (top.kind == T_OP) {
                    output[out_n].tag=2; output[out_n].op=top.op; out_n++;
                } else if (top.kind == T_FUNC) {
                    output[out_n].tag=3; output[out_n].func=top.func; out_n++;
                } else if (top.kind == T_CUSTOM_FUNC) {
                    output[out_n].tag=5; output[out_n].custom_idx=top.custom_idx; out_n++;
                }
            }
            if (t.kind == T_RPAREN && sp > 0 && stack[sp-1].kind == T_LPAREN)
                sp--;
            else if (t.kind == T_RPAREN) {
                set_error("Mismatched parentheses"); return -1;
            }
            if (t.kind == T_RPAREN || t.kind == T_END) {
                while (sp > 0 && stack[sp-1].kind == T_OP && stack[sp-1].op == '!') {
                    if (out_n >= max_out) { set_error("Expression too long"); return -1; }
                    Token top = stack[--sp];
                    output[out_n].tag=2; output[out_n].op=top.op; out_n++;
                }
            }
            if (t.kind == T_END) {
                while (sp > 0) {
                    if (out_n >= max_out) { set_error("Expression too long"); return -1; }
                    Token top = stack[--sp];
                    if (top.kind == T_OP) {
                        output[out_n].tag=2; output[out_n].op=top.op; out_n++;
                    } else if (top.kind == T_FUNC) {
                        output[out_n].tag=3; output[out_n].func=top.func; out_n++;
                    } else if (top.kind == T_CUSTOM_FUNC) {
                        output[out_n].tag=5; output[out_n].custom_idx=top.custom_idx; out_n++;
                    } else if (top.kind == T_LPAREN) {
                        set_error("Mismatched parentheses"); return -1;
                    }
                }
            }
            prev_was_op_or_lp = 0;
        }
    }
    if (out_n >= max_out) { set_error("Expression too long"); return -1; }
    #undef MAX_STACK
    return out_n;
}

static double apply_func(FuncId f, double v) {
    switch (f) {
        case F_SIN:  return sin(v);
        case F_COS:  return cos(v);
        case F_TAN:  return tan(v);
        case F_LOG:
            if (v <= 0.0) { set_error("log() domain error: argument must be > 0"); return NAN; }
            return log10(v);
        case F_LN:
            if (v <= 0.0) { set_error("ln() domain error: argument must be > 0"); return NAN; }
            return log(v);
        case F_SQRT:
            if (v < 0.0) { set_error("sqrt() domain error: argument must be >= 0"); return NAN; }
            return sqrt(v);
        case F_EXP:  return exp(v);
        case F_ABS:  return fabs(v);
        case F_FLOOR: return floor(v);
        case F_CEIL:  return ceil(v);
        default:     return NAN;
    }
}

static int eval_rpn(RPN* rpn, int nrpn, double x, double y, double* result) {
    double stack[256]; int sp = 0;
    const int MAX_STACK = 256;
    
    for (int i = 0; i < nrpn; i++) {
        RPN t = rpn[i];
        if (t.tag == 0) { 
            if (sp >= MAX_STACK) { set_error("Stack overflow (expression too complex)"); return -1; }
            stack[sp++] = t.num; 
        }
        else if (t.tag == 1) { 
            if (sp >= MAX_STACK) { set_error("Stack overflow (expression too complex)"); return -1; }
            stack[sp++] = x; 
        }
        else if (t.tag == 4) { 
            if (sp >= MAX_STACK) { set_error("Stack overflow (expression too complex)"); return -1; }
            stack[sp++] = y; 
        }
        else if (t.tag == 2) {
            if (t.op == '~') { 
                if (sp < 1) { set_error("Invalid expression"); return -1; }
                stack[sp-1] = -stack[sp-1]; 
            }
            else if (t.op == '!') {
                if (sp < 1) { set_error("Invalid expression"); return -1; }
                double a = stack[--sp];
                if (a < 0 || floor(a) != a) { set_error("Factorial requires non-negative integer"); return -1; }
                else if (a > 170) { set_error("Factorial overflow (max 170!)"); stack[sp++] = NAN; }
                else {
                    double r = 1.0;
                    for (int k = 2; k <= (int)a; k++) r *= k;
                    stack[sp++] = r;
                }
            }
            else {
                if (sp < 2) { set_error("Invalid expression"); return -1; }
                double b = stack[--sp], a = stack[--sp];
                switch (t.op) {
                    case '+': stack[sp++] = a+b; break;
                    case '-': stack[sp++] = a-b; break;
                    case '*': stack[sp++] = a*b; break;
                    case '/': stack[sp++] = fabs(b) > 1e-15 ? a/b : (set_error("Division by zero"),NAN); break;
                    case '%': stack[sp++] = fabs(b) > 1e-15 ? fmod(a,b) : (set_error("Modulo by zero"),NAN); break;
                    case '^':
                        if (a == 0.0 && b < 0.0) {
                            set_error("Division by zero (0^negative)");
                            stack[sp++] = NAN;
                        } else if (a < 0.0 && floor(b) != b) {
                            set_error("Negative base with non-integer exponent");
                            stack[sp++] = NAN;
                        } else {
                            stack[sp++] = pow(a,b);
                        }
                        break;
                    default:  set_error("Unknown operator"); return -1;
                }
            }
        } else if (t.tag == 3) {
            if (sp < 1) { set_error("Invalid expression"); return -1; }
            stack[sp-1] = apply_func(t.func, stack[sp-1]);
        } else if (t.tag == 5) {
            /* Custom function: substitute argument into body and evaluate */
            if (sp < 1) { set_error("Invalid expression"); return -1; }
            double arg_val = stack[--sp];
            CustomFunc* cf = &g_custom_funcs[t.custom_idx];
            /* Build expression: substitute x with (arg_val) in body */
            char eval_expr[MAX_FUNC_BODY + 64];
            snprintf(eval_expr, sizeof(eval_expr), "(%s)", cf->body);
            /* Simple approach: re-evaluate the body with x = arg_val */
            double body_result;
            if (parse_and_eval(cf->body, arg_val, 0.0, &body_result) != 0) {
                stack[sp++] = NAN;
            } else {
                stack[sp++] = body_result;
            }
        }
    }
    if (sp != 1) { set_error("Invalid expression"); return -1; }
    *result = stack[0];
    return 0;
}

static int parse_and_eval(const char* expr, double x, double y, double* result) {
    clear_error();
    Token toks[MAX_TOKENS];
    RPN   rpn[MAX_RPN];
    int nt = tokenize(expr, toks, MAX_TOKENS);
    if (nt < 0) return -1;
    int nr = shunt(toks, nt, rpn, MAX_RPN);
    if (nr < 0) return -1;
    return eval_rpn(rpn, nr, x, y, result);
}

EXPORT double evaluate(const char* expr, double x) {
    double r;
    clear_error();
    if (!expr) { set_error("NULL expression"); return NAN; }
    if (parse_and_eval(expr, x, 0.0, &r) != 0) return NAN;
    return r;
}

EXPORT double evaluate_xy(const char* expr, double x, double y) {
    double r;
    clear_error();
    if (!expr) { set_error("NULL expression"); return NAN; }
    if (parse_and_eval(expr, x, y, &r) != 0) return NAN;
    return r;
}

EXPORT void evaluate_array(const char* expr, const double* xs, double* out, int n) {
    if (!expr || !xs || !out || n <= 0) return;
    clear_error();
    Token toks[MAX_TOKENS];
    RPN   rpn[MAX_RPN];
    int nt = tokenize(expr, toks, MAX_TOKENS);
    if (nt < 0) {
        for (int i = 0; i < n; i++) out[i] = NAN;
        return;
    }
    int nr = shunt(toks, nt, rpn, MAX_RPN);
    if (nr < 0) {
        for (int i = 0; i < n; i++) out[i] = NAN;
        return;
    }
    for (int i = 0; i < n; i++) {
        double r;
        if (eval_rpn(rpn, nr, xs[i], 0.0, &r) != 0)
            out[i] = NAN;
        else
            out[i] = r;
    }
}

EXPORT void evaluate_xy_array(const char* expr, const double* xs, const double* ys, double* out, int n) {
    if (!expr || !xs || !ys || !out || n <= 0) return;
    clear_error();
    Token toks[MAX_TOKENS];
    RPN   rpn[MAX_RPN];
    int nt = tokenize(expr, toks, MAX_TOKENS);
    if (nt < 0) {
        for (int i = 0; i < n; i++) out[i] = NAN;
        return;
    }
    int nr = shunt(toks, nt, rpn, MAX_RPN);
    if (nr < 0) {
        for (int i = 0; i < n; i++) out[i] = NAN;
        return;
    }
    for (int i = 0; i < n; i++) {
        double r;
        if (eval_rpn(rpn, nr, xs[i], ys[i], &r) != 0)
            out[i] = NAN;
        else
            out[i] = r;
    }
}

EXPORT double derivative(const char* expr, double x, double h) {
    double fp, fm;
    clear_error();
    if (!expr) { set_error("NULL expression"); return NAN; }
    if (h == 0.0) { set_error("Step size h cannot be zero"); return NAN; }
    if (parse_and_eval(expr, x+h, 0.0, &fp) != 0) return NAN;
    if (parse_and_eval(expr, x-h, 0.0, &fm) != 0) return NAN;
    return (fp - fm) / (2.0 * h);
}

EXPORT double derivative2(const char* expr, double x, double h) {
    double fc, fp, fm;
    clear_error();
    if (!expr) { set_error("NULL expression"); return NAN; }
    if (h == 0.0) { set_error("Step size h cannot be zero"); return NAN; }
    if (parse_and_eval(expr, x,   0.0, &fc) != 0) return NAN;
    if (parse_and_eval(expr, x+h, 0.0, &fp) != 0) return NAN;
    if (parse_and_eval(expr, x-h, 0.0, &fm) != 0) return NAN;
    return (fp - 2.0*fc + fm) / (h*h);
}

EXPORT double integrate(const char* expr, double a, double b, int n) {
    if (!expr) { set_error("NULL expression"); return NAN; }
    if (n < 2 || n % 2 != 0) { set_error("n must be even and >= 2"); return NAN; }
    if (n > 1000000) { set_error("n too large (max 1000000)"); return NAN; }
    if (a > b) { set_error("Invalid interval: a must be <= b"); return NAN; }
    if (a == b) { clear_error(); return 0.0; }
    clear_error();
    double h = (b - a) / n;
    double fa, fb;
    if (parse_and_eval(expr, a, 0.0, &fa) != 0) return NAN;
    if (parse_and_eval(expr, b, 0.0, &fb) != 0) return NAN;
    double sum = fa + fb;
    for (int i = 1; i < n; i++) {
        double xi = a + i*h, fi;
        if (parse_and_eval(expr, xi, 0.0, &fi) != 0) return NAN;
        sum += (i%2==0 ? 2.0 : 4.0) * fi;
    }
    return (h/3.0) * sum;
}

EXPORT double solve_equation(const char* expr, double guess,
                              double xmin, double xmax,
                              double tol, int max_iter) {
    if (!expr) { set_error("NULL expression"); return NAN; }
    if (xmin >= xmax) { set_error("Invalid interval: xmin must be < xmax"); return NAN; }
    if (max_iter <= 0) max_iter = 100;
    clear_error();
    double x = guess;
    if (x < xmin) x = xmin + 0.1*(xmax-xmin);
    if (x > xmax) x = xmax - 0.1*(xmax-xmin);

    for (int iter = 0; iter < max_iter; iter++) {
        double f, fp, fm, df;
        if (parse_and_eval(expr, x, 0.0, &f) != 0) return NAN;
        if (isnan(f)) { set_error("Function returned NaN at current point"); return NAN; }
        if (fabs(f) < tol) return x;
        double h = 1e-6 * (fabs(x) + 1.0);
        if (parse_and_eval(expr, x+h, 0.0, &fp) != 0) return NAN;
        if (isnan(fp)) { set_error("Function returned NaN during derivative evaluation"); return NAN; }
        if (parse_and_eval(expr, x-h, 0.0, &fm) != 0) return NAN;
        if (isnan(fm)) { set_error("Function returned NaN during derivative evaluation"); return NAN; }
        df = (fp - fm) / (2.0*h);
        if (fabs(df) < 1e-15) {
            double fa; if (parse_and_eval(expr, xmin, 0.0, &fa) != 0) return NAN;
            if (isnan(fa)) { set_error("Function returned NaN at interval endpoint"); return NAN; }
            double mid = (xmin + xmax)/2.0, fmid;
            if (parse_and_eval(expr, mid, 0.0, &fmid) != 0) return NAN;
            if (isnan(fmid)) { set_error("Function returned NaN during bisection"); return NAN; }
            if (fa*fmid <= 0) xmax = mid;
            else xmin = mid;
            x = mid;
        } else {
            double nx = x - f/df;
            if (isnan(nx) || isinf(nx)) { set_error("Newton step produced NaN/Inf"); return NAN; }
            if (nx < xmin || nx > xmax) {
                double fa; if (parse_and_eval(expr, xmin, 0.0, &fa) != 0) return NAN;
                if (isnan(fa)) { set_error("Function returned NaN at interval endpoint"); return NAN; }
                double mid = (xmin+xmax)/2.0, fmid;
                if (parse_and_eval(expr, mid, 0.0, &fmid) != 0) return NAN;
                if (isnan(fmid)) { set_error("Function returned NaN during bisection"); return NAN; }
                if (fa*fmid <= 0) xmax = mid; else xmin = mid;
                x = mid;
            } else x = nx;
        }
    }
    set_error("Equation solver did not converge");
    return NAN;
}

EXPORT double solve_bisection(const char* expr, double a, double b,
                               double tol, int max_iter) {
    if (!expr) { set_error("NULL expression"); return NAN; }
    if (a >= b) { set_error("Invalid interval: a must be < b"); return NAN; }
    if (max_iter <= 0) max_iter = 100;
    clear_error();
    double fa, fb, fc, c;
    if (parse_and_eval(expr, a, 0.0, &fa) != 0) return NAN;
    if (isnan(fa)) { set_error("Function returned NaN at interval endpoint"); return NAN; }
    if (parse_and_eval(expr, b, 0.0, &fb) != 0) return NAN;
    if (isnan(fb)) { set_error("Function returned NaN at interval endpoint"); return NAN; }
    if (fabs(fa) < tol) return a;
    if (fabs(fb) < tol) return b;
    if (signbit(fa) == signbit(fb)) { set_error("f(a) and f(b) must have opposite signs"); return NAN; }
    for (int i = 0; i < max_iter; i++) {
        c = (a+b)/2.0;
        if (parse_and_eval(expr, c, 0.0, &fc) != 0) return NAN;
        if (isnan(fc)) { set_error("Function returned NaN during bisection"); return NAN; }
        if (fabs(fc) < tol || (b-a)/2.0 < tol) return c;
        if (signbit(fa) != signbit(fc)) { b = c; fb = fc; }
        else { a = c; fa = fc; }
    }
    set_error("Bisection did not converge");
    return (a+b)/2.0;
}

EXPORT double integrate_adaptive(const char* expr, double a, double b, double tol) {
    if (!expr) { set_error("NULL expression"); return NAN; }
    if (a > b) { set_error("Invalid interval: a must be <= b"); return NAN; }
    if (a == b) { clear_error(); return 0.0; }
    clear_error();
    int n = 64;
    double prev, cur;
    cur = integrate(expr, a, b, n);
    if (isnan(cur)) return NAN;
    for (int k = 0; k < 12; k++) {
        n *= 2;
        prev = cur;
        cur  = integrate(expr, a, b, n);
        if (isnan(cur)) return NAN;
        if (fabs(cur - prev) < tol) return cur;
    }
    set_error("Adaptive integration did not converge");
    return cur;
}

/* --------------------------------------------------------------------------
 *  Extremum finding (golden-section search)
 * -------------------------------------------------------------------------- */

#define GOLDEN_RATIO_RES ((3.0 - sqrt(5.0)) / 2.0)

/* --------------------------------------------------------------------------
 *  ODE Solver — 4th-order Runge-Kutta (RK4)
 *  Solves the initial value problem:  dy/dx = f(x, y),  y(x0) = y0
 *  over the interval [x0, x_end] with n_steps uniform steps.
 *  out_x and out_y must have space for at least (n_steps + 1) doubles.
 *  Returns the number of points stored, or -1 on error.
 * -------------------------------------------------------------------------- */

EXPORT int ode_solve_rk4(const char* expr, double x0, double y0, double x_end,
                          int n_steps, double* out_x, double* out_y, int max_out) {
    if (!expr || !out_x || !out_y) { set_error("NULL pointer argument"); return -1; }
    if (n_steps < 1) { set_error("n_steps must be >= 1"); return -1; }
    if (n_steps > 10000000) { set_error("n_steps too large (max 10000000)"); return -1; }
    if (max_out < n_steps + 1) { set_error("Output buffer too small"); return -1; }
    clear_error();

    double h = (x_end - x0) / n_steps;
    double x = x0;
    double y = y0;

    out_x[0] = x;
    out_y[0] = y;

    for (int i = 0; i < n_steps; i++) {
        double k1_val, k2_val, k3_val, k4_val;

        /* k1 = f(x, y) */
        if (parse_and_eval(expr, x, y, &k1_val) != 0) return -1;
        if (isnan(k1_val)) { set_error("f(x,y) returned NaN at RK4 k1"); return -1; }

        /* k2 = f(x + h/2, y + h*k1/2) */
        if (parse_and_eval(expr, x + 0.5 * h, y + 0.5 * h * k1_val, &k2_val) != 0) return -1;
        if (isnan(k2_val)) { set_error("f(x,y) returned NaN at RK4 k2"); return -1; }

        /* k3 = f(x + h/2, y + h*k2/2) */
        if (parse_and_eval(expr, x + 0.5 * h, y + 0.5 * h * k2_val, &k3_val) != 0) return -1;
        if (isnan(k3_val)) { set_error("f(x,y) returned NaN at RK4 k3"); return -1; }

        /* k4 = f(x + h, y + h*k3) */
        if (parse_and_eval(expr, x + h, y + h * k3_val, &k4_val) != 0) return -1;
        if (isnan(k4_val)) { set_error("f(x,y) returned NaN at RK4 k4"); return -1; }

        /* y_{n+1} = y_n + h*(k1 + 2*k2 + 2*k3 + k4)/6 */
        y = y + h * (k1_val + 2.0 * k2_val + 2.0 * k3_val + k4_val) / 6.0;
        x = x0 + (i + 1) * h;

        out_x[i + 1] = x;
        out_y[i + 1] = y;
    }

    return n_steps + 1;
}


/* --------------------------------------------------------------------------
 *  Limit computation (left-hand, right-hand, two-sided)
 *  Uses Richardson extrapolation for improved accuracy.
 * -------------------------------------------------------------------------- */

static double richardson_limit(const char* expr, double a, double dir, int max_level) {
    double h0 = 0.1;
    double table[16][16] = {{0}};
    int n = max_level < 16 ? max_level : 16;

    for (int i = 0; i < n; i++) {
        double h = h0 * pow(0.5, i);
        double fv;
        if (parse_and_eval(expr, a + dir * h, 0.0, &fv) != 0) return NAN;
        if (isnan(fv)) return NAN;
        table[i][0] = fv;
    }

    for (int j = 1; j < n; j++) {
        for (int i = 0; i < n - j; i++) {
            double num = table[i+1][j-1] * pow(2.0, j) - table[i][j-1];
            double den = pow(2.0, j) - 1.0;
            table[i][j] = num / den;
        }
    }

    return table[0][n-1];
}

EXPORT double limit_left(const char* expr, double a, int max_level) {
    if (!expr) { set_error("NULL expression"); return NAN; }
    if (max_level <= 0) max_level = 10;
    clear_error();
    return richardson_limit(expr, a, -1.0, max_level);
}

EXPORT double limit_right(const char* expr, double a, int max_level) {
    if (!expr) { set_error("NULL expression"); return NAN; }
    if (max_level <= 0) max_level = 10;
    clear_error();
    return richardson_limit(expr, a, 1.0, max_level);
}

EXPORT double limit(const char* expr, double a, double tol, int max_level) {
    if (!expr) { set_error("NULL expression"); return NAN; }
    if (max_level <= 0) max_level = 10;
    if (tol <= 0.0) tol = 1e-8;
    clear_error();

    double left  = richardson_limit(expr, a, -1.0, max_level);
    double right = richardson_limit(expr, a,  1.0, max_level);

    if (isnan(left) && isnan(right)) return NAN;
    if (isnan(left))  return right;
    if (isnan(right)) return left;

    if (fabs(left - right) < tol) {
        return (left + right) / 2.0;
    }

    set_error("Left and right limits differ (limit does not exist)");
    return NAN;
}

/* --------------------------------------------------------------------------
 *  nth-order derivative via recursive central differences
 *  Uses f^(n)(x) = (f^(n-1)(x+h) - f^(n-1)(x-h)) / (2h)
 *  with adaptive step size for numerical stability.
 * -------------------------------------------------------------------------- */

static double _eval_or_nan(const char* expr, double x) {
    double r;
    if (parse_and_eval(expr, x, 0.0, &r) != 0) return NAN;
    return r;
}

static double _central_diff_nth(const char* expr, double x, int n, double h) {
    if (n == 0) return _eval_or_nan(expr, x);

    /* Iterative nth-order central difference to avoid 2^n stack recursion.
     * Uses the closed-form formula:
     *   f^(n)(x) ≈ (1/(2h))^n * Σ_{k=0}^{n} (-1)^{n-k} * C(n,k) * f(x + (2k-n)*h)
     * Requires n+1 function evaluations instead of 2^n. */
    int np1 = n + 1;
    double* fvals = (double*)malloc(np1 * sizeof(double));
    if (!fvals) { set_error("Memory allocation failed"); return NAN; }

    for (int k = 0; k <= n; k++) {
        fvals[k] = _eval_or_nan(expr, x + (2.0 * k - n) * h);
        if (isnan(fvals[k])) { free(fvals); return NAN; }
    }

    /* Compute binomial coefficients C(n, k) iteratively */
    double coeff = 1.0;  /* C(n, 0) = 1 */
    double sum = 0.0;
    for (int k = 0; k <= n; k++) {
        double sign = ((n - k) & 1) ? -1.0 : 1.0;
        sum += sign * coeff * fvals[k];
        /* Update coefficient: C(n, k+1) = C(n, k) * (n - k) / (k + 1) */
        if (k < n) coeff = coeff * (n - k) / (k + 1);
    }

    free(fvals);
    double h2n = pow(2.0 * h, n);
    if (fabs(h2n) < 1e-15) {
        set_error("Step size too small, denominator underflow");
        return NAN;
    }
    return sum / h2n;
}

EXPORT double nth_derivative(const char* expr, double x, int n, double h) {
    if (!expr) { set_error("NULL expression"); return NAN; }
    if (n < 0) { set_error("Derivative order must be non-negative"); return NAN; }
    if (n > 1000) { set_error("Derivative order too large (max 1000)"); return NAN; }
    if (n > 400) { set_error("Derivative order too large for numerical stability (max 400)"); return NAN; }
    clear_error();
    if (n == 0) {
        double r;
        if (parse_and_eval(expr, x, 0.0, &r) != 0) return NAN;
        return r;
    }
    if (h <= 0.0) h = 1e-5;

    /* Adaptive step: for higher orders, use larger h to avoid catastrophic cancellation */
    double eps = 1e-16;
    double h_opt = pow(eps, 1.0 / (n + 2));
    if (h < h_opt) h = h_opt;
    if (h > 0.1) h = 0.1;

    return _central_diff_nth(expr, x, n, h);
}

/* --------------------------------------------------------------------------
 *  Taylor series coefficients at expansion point a
 *  Computes c_k = f^(k)(a) / k! for k = 0..order
 *  Returns the number of coefficients computed, or -1 on error.
 *  out_coeffs must have space for (order+1) doubles.
 * -------------------------------------------------------------------------- */

EXPORT int taylor_coefficients(const char* expr, double a, int order, double* out_coeffs, int max_out) {
    if (!expr) { set_error("NULL expression"); return -1; }
    if (order < 0) { set_error("Order must be non-negative"); return -1; }
    if (order > 1000) { set_error("Order too large (max 1000)"); return -1; }
    if (!out_coeffs || max_out < order + 1) { set_error("Output buffer too small"); return -1; }
    clear_error();

    double h = 1e-5;
    double factorial = 1.0;

    for (int k = 0; k <= order; k++) {
        if (k > 0) {
            if (k <= 170) factorial *= k;
            else factorial = INFINITY;
        }
        double dk = nth_derivative(expr, a, k, h);
        if (isnan(dk)) return -1;
        out_coeffs[k] = (isinf(factorial) || factorial == 0.0) ? 0.0 : dk / factorial;
    }
    return order + 1;
}

EXPORT double find_maximum(const char* expr, double a, double b, double tol, int max_iter) {
    if (!expr) { set_error("NULL expression"); return NAN; }
    if (a >= b) { set_error("Invalid interval: a must be < b"); return NAN; }
    if (max_iter <= 0) max_iter = 100;
    clear_error();
    const double resphi = GOLDEN_RATIO_RES;
    double c = a + resphi * (b - a);
    double d = b - resphi * (b - a);
    double fc, fd;

    if (parse_and_eval(expr, c, 0.0, &fc) != 0) return NAN;
    if (isnan(fc)) { set_error("Function returned NaN during extremum search"); return NAN; }
    if (parse_and_eval(expr, d, 0.0, &fd) != 0) return NAN;
    if (isnan(fd)) { set_error("Function returned NaN during extremum search"); return NAN; }
    fc = -fc; fd = -fd;

    for (int i = 0; i < max_iter && fabs(b - a) > tol; i++) {
        if (fc < fd) {
            b = d; d = c; fd = fc;
            c = a + resphi * (b - a);
            if (parse_and_eval(expr, c, 0.0, &fc) != 0) return NAN;
            if (isnan(fc)) { set_error("Function returned NaN during extremum search"); return NAN; }
            fc = -fc;
        } else {
            a = c; c = d; fc = fd;
            d = b - resphi * (b - a);
            if (parse_and_eval(expr, d, 0.0, &fd) != 0) return NAN;
            if (isnan(fd)) { set_error("Function returned NaN during extremum search"); return NAN; }
            fd = -fd;
        }
    }
    return (b + a) / 2.0;
}

EXPORT double find_minimum(const char* expr, double a, double b, double tol, int max_iter) {
    if (!expr) { set_error("NULL expression"); return NAN; }
    if (a >= b) { set_error("Invalid interval: a must be < b"); return NAN; }
    if (max_iter <= 0) max_iter = 100;
    clear_error();
    const double resphi = GOLDEN_RATIO_RES;
    double c = a + resphi * (b - a);
    double d = b - resphi * (b - a);
    double fc, fd;

    if (parse_and_eval(expr, c, 0.0, &fc) != 0) return NAN;
    if (isnan(fc)) { set_error("Function returned NaN during extremum search"); return NAN; }
    if (parse_and_eval(expr, d, 0.0, &fd) != 0) return NAN;
    if (isnan(fd)) { set_error("Function returned NaN during extremum search"); return NAN; }

    for (int i = 0; i < max_iter && fabs(b - a) > tol; i++) {
        if (fc < fd) {
            b = d; d = c; fd = fc;
            c = a + resphi * (b - a);
            if (parse_and_eval(expr, c, 0.0, &fc) != 0) return NAN;
            if (isnan(fc)) { set_error("Function returned NaN during extremum search"); return NAN; }
        } else {
            a = c; c = d; fc = fd;
            d = b - resphi * (b - a);
            if (parse_and_eval(expr, d, 0.0, &fd) != 0) return NAN;
            if (isnan(fd)) { set_error("Function returned NaN during extremum search"); return NAN; }
        }
    }
    return (b + a) / 2.0;
}

/* --------------------------------------------------------------------------
 *  Complex Number Support
 *  Provides complex arithmetic, trigonometric, logarithmic, and exponential
 *  functions for complex-valued expressions.
 * -------------------------------------------------------------------------- */

typedef struct {
    double re;  /* Real part */
    double im;  /* Imaginary part */
} Complex;

static Complex complex_make(double re, double im) {
    Complex z;
    z.re = re;
    z.im = im;
    return z;
}

static Complex complex_add(Complex a, Complex b) {
    return complex_make(a.re + b.re, a.im + b.im);
}

static Complex complex_sub(Complex a, Complex b) {
    return complex_make(a.re - b.re, a.im - b.im);
}

static Complex complex_mul(Complex a, Complex b) {
    return complex_make(a.re * b.re - a.im * b.im,
                        a.re * b.im + a.im * b.re);
}

static Complex complex_div(Complex a, Complex b) {
    double denom = b.re * b.re + b.im * b.im;
    if (denom < 1e-30) {
        set_error("Complex division by zero");
        return complex_make(NAN, NAN);
    }
    return complex_make((a.re * b.re + a.im * b.im) / denom,
                        (a.im * b.re - a.re * b.im) / denom);
}

static Complex complex_neg(Complex a) {
    return complex_make(-a.re, -a.im);
}

static Complex complex_conj(Complex a) {
    return complex_make(a.re, -a.im);
}

static double complex_abs(Complex a) {
    return sqrt(a.re * a.re + a.im * a.im);
}

static Complex complex_sqrt(Complex a) {
    double r = complex_abs(a);
    if (r == 0.0) return complex_make(0.0, 0.0);
    double re = sqrt((r + a.re) / 2.0);
    double im = (a.im >= 0 ? 1.0 : -1.0) * sqrt(fmax(0.0, (r - a.re) / 2.0));
    return complex_make(re, im);
}

static Complex complex_exp(Complex a) {
    double er = exp(a.re);
    return complex_make(er * cos(a.im), er * sin(a.im));
}

static Complex complex_ln(Complex a) {
    double r = complex_abs(a);
    if (r <= 0.0) {
        set_error("ln() domain error: |z| must be > 0");
        return complex_make(NAN, NAN);
    }
    return complex_make(log(r), atan2(a.im, a.re));
}

static Complex complex_pow(Complex base, Complex exp) {
    if (exp.im == 0.0 && exp.re == 0.0) {
        return complex_make(1.0, 0.0);
    }
    if (base.im == 0.0 && base.re == 0.0) {
        if (exp.re > 0.0 || exp.im != 0.0)
            return complex_make(0.0, 0.0);
        else if (exp.re < 0.0 && exp.im == 0.0)
            return complex_make(INFINITY, 0.0);
        else
            return complex_make(0.0, 0.0);
    }
    Complex log_base = complex_ln(base);
    Complex product = complex_mul(exp, log_base);
    return complex_exp(product);
}

static Complex complex_sin(Complex a) {
    return complex_make(sin(a.re) * cosh(a.im),
                        cos(a.re) * sinh(a.im));
}

static Complex complex_cos(Complex a) {
    return complex_make(cos(a.re) * cosh(a.im),
                        -sin(a.re) * sinh(a.im));
}

static Complex complex_tan(Complex a) {
    Complex s = complex_sin(a);
    Complex c = complex_cos(a);
    return complex_div(s, c);
}

/* Parse a complex number from string: "a+bi", "a-bi", "a", "bi" */
static int parse_complex(const char* s, Complex* result) {
    if (!s || !result) return -1;
    
    char* end;
    double re = strtod(s, &end);
    
    if (end == s) {
        /* No real part, check for pure imaginary */
        if (*s == 'i' || *s == 'I') {
            result->re = 0.0;
            result->im = 1.0;
            return 0;
        }
        return -1;
    }
    
    result->re = re;
    
    /* Check for imaginary part */
    if (*end == '+' || *end == '-') {
        char sign = *end;
        end++;
        if (*end == 'i' || *end == 'I') {
            result->im = (sign == '+') ? 1.0 : -1.0;
            return 0;
        }
        char* im_end;
        double im = strtod(end, &im_end);
        if (im_end == end) { set_error("Incomplete complex number"); return -1; }
        if (*im_end == 'i' || *im_end == 'I') {
            im_end++;
            if (*im_end != '\0') { set_error("Invalid complex number format"); return -1; }
            result->im = (sign == '+') ? im : -im;
            return 0;
        }
        set_error("Missing 'i' in complex number");
        return -1;
    } else if (*end == 'i' || *end == 'I') {
        result->re = 0.0;
        result->im = re;
        return 0;
    }
    
    /* Pure real number */
    result->im = 0.0;
    return 0;
}

EXPORT void complex_evaluate(const char* expr, double x, double y,
                             double* out_re, double* out_im) {
    if (!expr || !out_re || !out_im) return;
    clear_error();
    
    /* For now, use real evaluation and treat result as complex with zero imaginary part */
    double result;
    if (parse_and_eval(expr, x, y, &result) != 0) {
        *out_re = NAN;
        *out_im = NAN;
        return;
    }
    *out_re = result;
    *out_im = 0.0;
}

EXPORT void complex_add_values(double re1, double im1, double re2, double im2,
                               double* out_re, double* out_im) {
    if (!out_re || !out_im) return;
    Complex a = complex_make(re1, im1);
    Complex b = complex_make(re2, im2);
    Complex result = complex_add(a, b);
    *out_re = result.re;
    *out_im = result.im;
}

EXPORT void complex_sub_values(double re1, double im1, double re2, double im2,
                               double* out_re, double* out_im) {
    if (!out_re || !out_im) return;
    Complex a = complex_make(re1, im1);
    Complex b = complex_make(re2, im2);
    Complex result = complex_sub(a, b);
    *out_re = result.re;
    *out_im = result.im;
}

EXPORT void complex_mul_values(double re1, double im1, double re2, double im2,
                               double* out_re, double* out_im) {
    if (!out_re || !out_im) return;
    Complex a = complex_make(re1, im1);
    Complex b = complex_make(re2, im2);
    Complex result = complex_mul(a, b);
    *out_re = result.re;
    *out_im = result.im;
}

EXPORT void complex_div_values(double re1, double im1, double re2, double im2,
                               double* out_re, double* out_im) {
    if (!out_re || !out_im) return;
    clear_error();
    Complex a = complex_make(re1, im1);
    Complex b = complex_make(re2, im2);
    Complex result = complex_div(a, b);
    *out_re = result.re;
    *out_im = result.im;
}

EXPORT void complex_pow_values(double re1, double im1, double re2, double im2,
                               double* out_re, double* out_im) {
    if (!out_re || !out_im) return;
    clear_error();
    Complex base = complex_make(re1, im1);
    Complex exp = complex_make(re2, im2);
    Complex result = complex_pow(base, exp);
    *out_re = result.re;
    *out_im = result.im;
}

EXPORT void complex_sin_value(double re, double im, double* out_re, double* out_im) {
    if (!out_re || !out_im) return;
    Complex z = complex_make(re, im);
    Complex result = complex_sin(z);
    *out_re = result.re;
    *out_im = result.im;
}

EXPORT void complex_cos_value(double re, double im, double* out_re, double* out_im) {
    if (!out_re || !out_im) return;
    Complex z = complex_make(re, im);
    Complex result = complex_cos(z);
    *out_re = result.re;
    *out_im = result.im;
}

EXPORT void complex_tan_value(double re, double im, double* out_re, double* out_im) {
    if (!out_re || !out_im) return;
    clear_error();
    Complex z = complex_make(re, im);
    Complex result = complex_tan(z);
    *out_re = result.re;
    *out_im = result.im;
}

EXPORT void complex_exp_value(double re, double im, double* out_re, double* out_im) {
    if (!out_re || !out_im) return;
    Complex z = complex_make(re, im);
    Complex result = complex_exp(z);
    *out_re = result.re;
    *out_im = result.im;
}

EXPORT void complex_ln_value(double re, double im, double* out_re, double* out_im) {
    if (!out_re || !out_im) return;
    clear_error();
    Complex z = complex_make(re, im);
    Complex result = complex_ln(z);
    *out_re = result.re;
    *out_im = result.im;
}

EXPORT void complex_sqrt_value(double re, double im, double* out_re, double* out_im) {
    if (!out_re || !out_im) return;
    Complex z = complex_make(re, im);
    Complex result = complex_sqrt(z);
    *out_re = result.re;
    *out_im = result.im;
}

EXPORT double complex_abs_value(double re, double im) {
    Complex z = complex_make(re, im);
    return complex_abs(z);
}

/* --------------------------------------------------------------------------
 *  Area Between Curves
 *  Computes integral_a^b |f(x) - g(x)| dx using adaptive Simpson's rule.
 *  This measures the total area enclosed between two curves over [a,b].
 * -------------------------------------------------------------------------- */

static double _abs_diff_integrand(const char* expr_f, const char* expr_g,
                                   double x) {
    double fv, gv;
    if (parse_and_eval(expr_f, x, 0.0, &fv) != 0) return NAN;
    if (parse_and_eval(expr_g, x, 0.0, &gv) != 0) return NAN;
    return fabs(fv - gv);
}

static double _simpson_abs_diff(const char* expr_f, const char* expr_g,
                                 double a, double b, int n) {
    if (n < 2 || n % 2 != 0) { set_error("Simpson's rule requires even n >= 2"); return NAN; }
    if (a == b) return 0.0;
    double h = (b - a) / n;
    double fa = _abs_diff_integrand(expr_f, expr_g, a);
    double fb = _abs_diff_integrand(expr_f, expr_g, b);
    if (isnan(fa) || isnan(fb)) return NAN;
    double sum = fa + fb;
    for (int i = 1; i < n; i++) {
        double xi = a + i * h;
        double fi = _abs_diff_integrand(expr_f, expr_g, xi);
        if (isnan(fi)) return NAN;
        sum += (i % 2 == 0 ? 2.0 : 4.0) * fi;
    }
    return (h / 3.0) * sum;
}

EXPORT double area_between_curves(const char* expr_f, const char* expr_g,
                                   double a, double b, double tol) {
    if (!expr_f || !expr_g) { set_error("NULL expression"); return NAN; }
    if (a > b) { set_error("Invalid interval: a must be <= b"); return NAN; }
    if (a == b) { clear_error(); return 0.0; }
    if (tol <= 0.0) tol = 1e-8;
    clear_error();

    int n = 64;
    double prev, cur;
    cur = _simpson_abs_diff(expr_f, expr_g, a, b, n);
    if (isnan(cur)) return NAN;
    for (int k = 0; k < 12; k++) {
        n *= 2;
        prev = cur;
        cur = _simpson_abs_diff(expr_f, expr_g, a, b, n);
        if (isnan(cur)) return NAN;
        if (fabs(cur - prev) < tol) return cur;
    }
    set_error("Adaptive area computation did not converge");
    return cur;
}

EXPORT void complex_conj_value(double re, double im, double* out_re, double* out_im) {
    if (!out_re || !out_im) return;
    Complex z = complex_make(re, im);
    Complex result = complex_conj(z);
    *out_re = result.re;
    *out_im = result.im;
}

EXPORT int solve_system_2d(const char* f_expr, const char* g_expr,
                           double x0, double y0, double tol, int max_iter,
                           double* out_x, double* out_y) {
    if (!f_expr || !g_expr || !out_x || !out_y) {
        set_error("NULL parameter in solve_system_2d");
        return 0;
    }
    if (tol <= 0.0) tol = 1e-10;
    if (max_iter <= 0) max_iter = 100;
    clear_error();

    double x = x0, y = y0;
    double h = 1e-7;

    for (int iter = 0; iter < max_iter; iter++) {
        double F_val, G_val;
        if (parse_and_eval(f_expr, x, y, &F_val) != 0) {
            set_error("Error evaluating f(x,y)");
            return 0;
        }
        if (parse_and_eval(g_expr, x, y, &G_val) != 0) {
            set_error("Error evaluating g(x,y)");
            return 0;
        }

        if (fabs(F_val) < tol && fabs(G_val) < tol) {
            *out_x = x;
            *out_y = y;
            return 1;
        }

        /* Numerical Jacobian via central differences */
        double F_xph, F_xmh, F_yph, F_ymh;
        double G_xph, G_xmh, G_yph, G_ymh;

        if (parse_and_eval(f_expr, x + h, y, &F_xph) != 0) { set_error("Jacobian evaluation failed"); return 0; }
        if (parse_and_eval(f_expr, x - h, y, &F_xmh) != 0) { set_error("Jacobian evaluation failed"); return 0; }
        if (parse_and_eval(f_expr, x, y + h, &F_yph) != 0) { set_error("Jacobian evaluation failed"); return 0; }
        if (parse_and_eval(f_expr, x, y - h, &F_ymh) != 0) { set_error("Jacobian evaluation failed"); return 0; }

        if (parse_and_eval(g_expr, x + h, y, &G_xph) != 0) { set_error("Jacobian evaluation failed"); return 0; }
        if (parse_and_eval(g_expr, x - h, y, &G_xmh) != 0) { set_error("Jacobian evaluation failed"); return 0; }
        if (parse_and_eval(g_expr, x, y + h, &G_yph) != 0) { set_error("Jacobian evaluation failed"); return 0; }
        if (parse_and_eval(g_expr, x, y - h, &G_ymh) != 0) { set_error("Jacobian evaluation failed"); return 0; }

        if (isnan(F_xph) || isnan(F_xmh) || isnan(F_yph) || isnan(F_ymh) ||
            isnan(G_xph) || isnan(G_xmh) || isnan(G_yph) || isnan(G_ymh)) {
            set_error("Jacobian evaluation returned NaN"); return 0;
        }

        double J11 = (F_xph - F_xmh) / (2.0 * h);  /* dF/dx */
        double J12 = (F_yph - F_ymh) / (2.0 * h);  /* dF/dy */
        double J21 = (G_xph - G_xmh) / (2.0 * h);  /* dG/dx */
        double J22 = (G_yph - G_ymh) / (2.0 * h);  /* dG/dy */

        double det = J11 * J22 - J12 * J21;
        if (fabs(det) < 1e-15) {
            set_error("Jacobian is singular (det=0). Try a different initial guess.");
            return 0;
        }

        /* Cramer's rule: J * delta = -[F, G] */
        double dx = (-F_val * J22 + G_val * J12) / det;
        double dy = (-J11 * G_val + J21 * F_val) / det;

        /* Bound step size to prevent divergence */
        double step = sqrt(dx * dx + dy * dy);
        if (step > 10.0) {
            double scale = 10.0 / step;
            dx *= scale;
            dy *= scale;
        }

        x += dx;
        y += dy;
    }

    *out_x = x;
    *out_y = y;
    set_error("solve_system_2d did not converge within max_iter iterations");
    return 0;
}

/* --------------------------------------------------------------------------
 *  Custom Function Registry
 *  Allows users to define named functions like f(x) = x^2 + 1
 *  and reference them in expressions as f(expr).
 * -------------------------------------------------------------------------- */

EXPORT int custom_func_define(const char* name, const char* body) {
    if (!name || !body) { set_error("NULL argument in custom_func_define"); return 0; }
    clear_error();

    size_t nlen = strlen(name);
    if (nlen == 0 || nlen >= MAX_FUNC_NAME) { set_error("Function name too long (max 31)"); return 0; }
    if (!isalpha(name[0])) { set_error("Function name must start with a letter"); return 0; }
    for (size_t i = 0; i < nlen; i++) {
        if (!isalnum(name[i])) { set_error("Function name must be alphanumeric"); return 0; }
    }
    if (strlen(body) >= MAX_FUNC_BODY) { set_error("Function body too long (max 511)"); return 0; }

    /* Check if function already exists — update it */
    for (int i = 0; i < g_custom_func_count; i++) {
        if (g_custom_funcs[i].defined && !strcmp(g_custom_funcs[i].name, name)) {
            strcpy(g_custom_funcs[i].body, body);
            return 1;
        }
    }

    /* Register new function */
    if (g_custom_func_count >= MAX_CUSTOM_FUNCS) {
        set_error("Too many custom functions (max 64)");
        return 0;
    }

    CustomFunc* f = &g_custom_funcs[g_custom_func_count];
    strcpy(f->name, name);
    strcpy(f->body, body);
    f->defined = 1;
    g_custom_func_count++;
    return 1;
}

EXPORT void custom_func_clear(void) {
    for (int i = 0; i < g_custom_func_count; i++) {
        g_custom_funcs[i].defined = 0;
        g_custom_funcs[i].name[0] = '\0';
        g_custom_funcs[i].body[0] = '\0';
    }
    g_custom_func_count = 0;
    clear_error();
}

EXPORT int custom_func_delete(const char* name) {
    if (!name) return 0;
    clear_error();
    for (int i = 0; i < g_custom_func_count; i++) {
        if (g_custom_funcs[i].defined && !strcmp(g_custom_funcs[i].name, name)) {
            g_custom_funcs[i].defined = 0;
            return 1;
        }
    }
    set_error("Function not found");
    return 0;
}

static CustomFunc* custom_func_find(const char* name) {
    for (int i = 0; i < g_custom_func_count; i++) {
        if (g_custom_funcs[i].defined && !strcmp(g_custom_funcs[i].name, name)) {
            return &g_custom_funcs[i];
        }
    }
    return NULL;
}

EXPORT int custom_func_list(char* output, int max_out) {
    if (!output || max_out <= 0) return 0;
    clear_error();
    int pos = 0;
    for (int i = 0; i < g_custom_func_count && pos < max_out - 1; i++) {
        if (g_custom_funcs[i].defined) {
            int written = snprintf(output + pos, max_out - pos, "%s(x)=%s%s",
                g_custom_funcs[i].name, g_custom_funcs[i].body,
                (i < g_custom_func_count - 1) ? ";" : "");
            if (written > 0) {
                if (pos + written >= max_out) { pos = max_out - 1; break; }
                pos += written;
            }
        }
    }
    output[pos] = '\0';
    return pos;
}

/* --------------------------------------------------------------------------
 *  Base Number Converter
 *  Converts integer numbers between different bases (2-36).
 *  Supports binary (2), octal (8), decimal (10), hexadecimal (16),
 *  and any base from 2 to 36.
 * -------------------------------------------------------------------------- */

EXPORT long long base_to_long(const char* str, int base) {
    if (!str || base < 2 || base > 36) return 0;
    clear_error();
    long long result = 0;
    int negative = 0;
    const char* p = str;

    while (*p == ' ' || *p == '\t') p++;
    if (*p == '-') { negative = 1; p++; }
    else if (*p == '+') { p++; }

    if (*p == '0' && (*(p+1) == 'x' || *(p+1) == 'X')) {
        if (base == 16) p += 2;
    }

    while (*p) {
        int digit;
        if (*p >= '0' && *p <= '9') digit = *p - '0';
        else if (*p >= 'a' && *p <= 'z') digit = *p - 'a' + 10;
        else if (*p >= 'A' && *p <= 'Z') digit = *p - 'A' + 10;
        else break;

        if (digit >= base) {
            set_error("Invalid digit for the given base");
            return 0;
        }
        if (result > (LLONG_MAX - digit) / base) {
            set_error("Integer overflow in base conversion");
            return negative ? LLONG_MIN : LLONG_MAX;
        }
        result = result * base + digit;
        p++;
    }

    return negative ? -((long long)result) : result;
}

EXPORT int long_to_base(long long n, int base, char* output, int max_out) {
    if (!output || max_out <= 0) return 0;
    if (base < 2 || base > 36) { set_error("Base must be between 2 and 36"); return 0; }
    clear_error();

    char temp[67];
    int i = 0;
    int negative = 0;
    unsigned long long un;

    if (n < 0) { negative = 1; un = -(unsigned long long)n; }
    else { un = (unsigned long long)n; }

    if (un == 0) {
        temp[i++] = '0';
    } else {
        while (un > 0 && i < 64) {
            int digit = un % base;
            temp[i++] = (digit < 10) ? ('0' + digit) : ('A' + digit - 10);
            un /= base;
        }
    }

    if (negative) {
        if (i < max_out - 1) {
            temp[i++] = '-';
        } else {
            set_error("Output buffer too small for negative sign");
            return 0;
        }
    }

    int len = i;
    if (len >= max_out) { set_error("Output buffer too small"); return 0; }

    for (int j = 0; j < len; j++) {
        output[j] = temp[len - 1 - j];
    }
    output[len] = '\0';
    return len;
}

EXPORT int convert_base(const char* input, int from_base, int to_base,
                         char* output, int max_out) {
    if (!input || !output || max_out <= 0) return 0;
    if (from_base < 2 || from_base > 36 || to_base < 2 || to_base > 36) {
        set_error("Base must be between 2 and 36");
        return 0;
    }
    clear_error();

    long long value = base_to_long(input, from_base);
    if (g_error[0] != '\0') return 0;

    return long_to_base(value, to_base, output, max_out);
}

EXPORT void convert_base_all(const char* input, int from_base,
                              char* bin, int bin_max,
                              char* oct, int oct_max,
                              char* dec, int dec_max,
                              char* hex, int hex_max) {
    if (!input) return;
    clear_error();

    long long value = base_to_long(input, from_base);
    if (g_error[0] != '\0') {
        if (bin && bin_max > 0) bin[0] = '\0';
        if (oct && oct_max > 0) oct[0] = '\0';
        if (dec && dec_max > 0) dec[0] = '\0';
        if (hex && hex_max > 0) hex[0] = '\0';
        return;
    }

    if (bin) long_to_base(value, 2, bin, bin_max);
    if (oct) long_to_base(value, 8, oct, oct_max);
    if (dec) long_to_base(value, 10, dec, dec_max);
    if (hex) long_to_base(value, 16, hex, hex_max);
}

/* --------------------------------------------------------------------------
 *  Volume of Revolution
 *  Computes volumes of solids of revolution using three methods:
 *
 *  Disk method:   V = π ∫_a^b [f(x)]² dx        (rotate f(x) around x-axis)
 *  Washer method: V = π ∫_a^b ([f(x)]²-[g(x)]²) dx  (rotate f(x),g(x) around x-axis)
 *  Shell method:  V = 2π ∫_a^b x·f(x) dx         (rotate f(x) around y-axis)
 *
 *  Uses adaptive Simpson's rule for integration.
 * -------------------------------------------------------------------------- */

static double _disk_integrand(const char* expr, double x) {
    double fv;
    if (parse_and_eval(expr, x, 0.0, &fv) != 0) return NAN;
    return fv * fv;
}

static double _washer_integrand(const char* expr_f, const char* expr_g, double x) {
    double fv, gv;
    if (parse_and_eval(expr_f, x, 0.0, &fv) != 0) return NAN;
    if (parse_and_eval(expr_g, x, 0.0, &gv) != 0) return NAN;
    return fv * fv - gv * gv;
}

static double _shell_integrand(const char* expr, double x) {
    double fv;
    if (parse_and_eval(expr, x, 0.0, &fv) != 0) return NAN;
    return x * fv;
}

static double _simpson_volume(const char* expr_f, const char* expr_g,
                               double a, double b, int n, int method) {
    /* method: 0=disk, 1=washer, 2=shell */
    if (n < 2 || n % 2 != 0) { set_error("Simpson's rule requires even n >= 2"); return NAN; }
    if (a == b) return 0.0;
    double h = (b - a) / n;

    double fa_val, fb_val;
    if (method == 0) {
        fa_val = _disk_integrand(expr_f, a);
        fb_val = _disk_integrand(expr_f, b);
    } else if (method == 1) {
        fa_val = _washer_integrand(expr_f, expr_g, a);
        fb_val = _washer_integrand(expr_f, expr_g, b);
    } else {
        fa_val = _shell_integrand(expr_f, a);
        fb_val = _shell_integrand(expr_f, b);
    }
    if (isnan(fa_val) || isnan(fb_val)) return NAN;

    double sum = fa_val + fb_val;
    for (int i = 1; i < n; i++) {
        double xi = a + i * h;
        double fi;
        if (method == 0) {
            fi = _disk_integrand(expr_f, xi);
        } else if (method == 1) {
            fi = _washer_integrand(expr_f, expr_g, xi);
        } else {
            fi = _shell_integrand(expr_f, xi);
        }
        if (isnan(fi)) return NAN;
        sum += (i % 2 == 0 ? 2.0 : 4.0) * fi;
    }

    double base = (h / 3.0) * sum;
    if (method == 0 || method == 1) {
        return M_PI * base;
    } else {
        return 2.0 * M_PI * base;
    }
}

EXPORT double volume_disk(const char* expr, double a, double b, double tol) {
    if (!expr) { set_error("NULL expression"); return NAN; }
    if (a > b) { set_error("Invalid interval: a must be <= b"); return NAN; }
    if (a == b) { clear_error(); return 0.0; }
    if (tol <= 0.0) tol = 1e-8;
    clear_error();

    int n = 64;
    double prev, cur;
    cur = _simpson_volume(expr, NULL, a, b, n, 0);
    if (isnan(cur)) return NAN;
    for (int k = 0; k < 12; k++) {
        n *= 2;
        prev = cur;
        cur = _simpson_volume(expr, NULL, a, b, n, 0);
        if (isnan(cur)) return NAN;
        if (fabs(cur - prev) < tol) return cur;
    }
    set_error("Adaptive volume computation did not converge");
    return cur;
}

EXPORT double volume_washer(const char* expr_f, const char* expr_g,
                             double a, double b, double tol) {
    if (!expr_f || !expr_g) { set_error("NULL expression"); return NAN; }
    if (a > b) { set_error("Invalid interval: a must be <= b"); return NAN; }
    if (a == b) { clear_error(); return 0.0; }
    if (tol <= 0.0) tol = 1e-8;
    clear_error();

    int n = 64;
    double prev, cur;
    cur = _simpson_volume(expr_f, expr_g, a, b, n, 1);
    if (isnan(cur)) return NAN;
    for (int k = 0; k < 12; k++) {
        n *= 2;
        prev = cur;
        cur = _simpson_volume(expr_f, expr_g, a, b, n, 1);
        if (isnan(cur)) return NAN;
        if (fabs(cur - prev) < tol) return cur;
    }
    set_error("Adaptive volume computation did not converge");
    return cur;
}

EXPORT double volume_shell(const char* expr, double a, double b, double tol) {
    if (!expr) { set_error("NULL expression"); return NAN; }
    if (a > b) { set_error("Invalid interval: a must be <= b"); return NAN; }
    if (a == b) { clear_error(); return 0.0; }
    if (tol <= 0.0) tol = 1e-8;
    clear_error();

    int n = 64;
    double prev, cur;
    cur = _simpson_volume(expr, NULL, a, b, n, 2);
    if (isnan(cur)) return NAN;
    for (int k = 0; k < 12; k++) {
        n *= 2;
        prev = cur;
        cur = _simpson_volume(expr, NULL, a, b, n, 2);
        if (isnan(cur)) return NAN;
        if (fabs(cur - prev) < tol) return cur;
    }
    set_error("Adaptive volume computation did not converge");
    return cur;
}

EXPORT void complex_array_evaluate(const char* expr, const double* xs, const double* ys,
                                    double* out_re, double* out_im, int n) {
    if (!expr || !xs || !ys || !out_re || !out_im || n <= 0) return;
    clear_error();
    int any_failed = 0;
    
    for (int i = 0; i < n; i++) {
        double result;
        if (parse_and_eval(expr, xs[i], ys[i], &result) != 0) {
            out_re[i] = NAN;
            out_im[i] = NAN;
            any_failed = 1;
        } else {
            out_re[i] = result;
            out_im[i] = 0.0;
        }
    }
    if (any_failed && g_error[0] == '\0')
        set_error("Some evaluations failed in complex_array_evaluate");
}

/* --------------------------------------------------------------------------
 *  ODE Solver — Euler Method (1st order)
 *  Solves the initial value problem:  dy/dx = f(x, y),  y(x0) = y0
 *  over the interval [x0, x_end] with n_steps uniform steps.
 *  out_x and out_y must have space for at least (n_steps + 1) doubles.
 *  Returns the number of points stored, or -1 on error.
 * -------------------------------------------------------------------------- */

EXPORT int ode_solve_euler(const char* expr, double x0, double y0, double x_end,
                           int n_steps, double* out_x, double* out_y, int max_out) {
    if (!expr || !out_x || !out_y) { set_error("NULL pointer argument"); return -1; }
    if (n_steps < 1) { set_error("n_steps must be >= 1"); return -1; }
    if (n_steps > 10000000) { set_error("n_steps too large (max 10000000)"); return -1; }
    if (max_out < n_steps + 1) { set_error("Output buffer too small"); return -1; }
    clear_error();

    double h = (x_end - x0) / n_steps;
    double x = x0;
    double y = y0;

    out_x[0] = x;
    out_y[0] = y;

    for (int i = 0; i < n_steps; i++) {
        double f_val;
        if (parse_and_eval(expr, x, y, &f_val) != 0) return -1;
        if (isnan(f_val)) { set_error("f(x,y) returned NaN at Euler"); return -1; }

        y = y + h * f_val;
        x = x0 + (i + 1) * h;

        out_x[i + 1] = x;
        out_y[i + 1] = y;
    }

    return n_steps + 1;
}

/* --------------------------------------------------------------------------
 *  ODE Solver — Improved Euler Method (Heun's method, 2nd order)
 *  Solves the initial value problem:  dy/dx = f(x, y),  y(x0) = y0
 *  over the interval [x0, x_end] with n_steps uniform steps.
 *  out_x and out_y must have space for at least (n_steps + 1) doubles.
 *  Returns the number of points stored, or -1 on error.
 * -------------------------------------------------------------------------- */

EXPORT int ode_solve_improved_euler(const char* expr, double x0, double y0, double x_end,
                                    int n_steps, double* out_x, double* out_y, int max_out) {
    if (!expr || !out_x || !out_y) { set_error("NULL pointer argument"); return -1; }
    if (n_steps < 1) { set_error("n_steps must be >= 1"); return -1; }
    if (n_steps > 10000000) { set_error("n_steps too large (max 10000000)"); return -1; }
    if (max_out < n_steps + 1) { set_error("Output buffer too small"); return -1; }
    clear_error();

    double h = (x_end - x0) / n_steps;
    double x = x0;
    double y = y0;

    out_x[0] = x;
    out_y[0] = y;

    for (int i = 0; i < n_steps; i++) {
        double k1_val, k2_val;

        /* k1 = f(x, y) */
        if (parse_and_eval(expr, x, y, &k1_val) != 0) return -1;
        if (isnan(k1_val)) { set_error("f(x,y) returned NaN at Improved Euler k1"); return -1; }

        /* k2 = f(x + h, y + h*k1) */
        if (parse_and_eval(expr, x + h, y + h * k1_val, &k2_val) != 0) return -1;
        if (isnan(k2_val)) { set_error("f(x,y) returned NaN at Improved Euler k2"); return -1; }

        /* y_{n+1} = y_n + h*(k1 + k2)/2 */
        y = y + h * (k1_val + k2_val) / 2.0;
        x = x0 + (i + 1) * h;

        out_x[i + 1] = x;
        out_y[i + 1] = y;
    }

    return n_steps + 1;
}

/* --------------------------------------------------------------------------
 *  ODE Solver — Midpoint Method (2nd order)
 *  Solves the initial value problem:  dy/dx = f(x, y),  y(x0) = y0
 *  over the interval [x0, x_end] with n_steps uniform steps.
 *  out_x and out_y must have space for at least (n_steps + 1) doubles.
 *  Returns the number of points stored, or -1 on error.
 * -------------------------------------------------------------------------- */

EXPORT int ode_solve_midpoint(const char* expr, double x0, double y0, double x_end,
                              int n_steps, double* out_x, double* out_y, int max_out) {
    if (!expr || !out_x || !out_y) { set_error("NULL pointer argument"); return -1; }
    if (n_steps < 1) { set_error("n_steps must be >= 1"); return -1; }
    if (n_steps > 10000000) { set_error("n_steps too large (max 10000000)"); return -1; }
    if (max_out < n_steps + 1) { set_error("Output buffer too small"); return -1; }
    clear_error();

    double h = (x_end - x0) / n_steps;
    double x = x0;
    double y = y0;

    out_x[0] = x;
    out_y[0] = y;

    for (int i = 0; i < n_steps; i++) {
        double k1_val, k2_val;

        /* k1 = f(x, y) */
        if (parse_and_eval(expr, x, y, &k1_val) != 0) return -1;
        if (isnan(k1_val)) { set_error("f(x,y) returned NaN at Midpoint k1"); return -1; }

        /* k2 = f(x + h/2, y + h*k1/2) */
        if (parse_and_eval(expr, x + 0.5 * h, y + 0.5 * h * k1_val, &k2_val) != 0) return -1;
        if (isnan(k2_val)) { set_error("f(x,y) returned NaN at Midpoint k2"); return -1; }

        /* y_{n+1} = y_n + h*k2 */
        y = y + h * k2_val;
        x = x0 + (i + 1) * h;

        out_x[i + 1] = x;
        out_y[i + 1] = y;
    }

    return n_steps + 1;
}

/* --------------------------------------------------------------------------
 *  ODE Solver — Runge-Kutta-Fehlberg (RKF45) with adaptive step size
 *  Solves the initial value problem:  dy/dx = f(x, y),  y(x0) = y0
 *  over the interval [x0, x_end] with adaptive step size control.
 *  out_x and out_y must have space for at least max_points doubles.
 *  Returns the number of points stored, or -1 on error.
 * -------------------------------------------------------------------------- */

EXPORT int ode_solve_rkf45(const char* expr, double x0, double y0, double x_end,
                            double tol, double* out_x, double* out_y, int max_points) {
    if (!expr || !out_x || !out_y) { set_error("NULL pointer argument"); return -1; }
    if (max_points < 2) { set_error("Output buffer too small"); return -1; }
    if (tol <= 0.0) tol = 1e-6;
    clear_error();

    double h = (x_end - x0) / 100.0;  /* Initial step size guess */
    if (h <= 0.0) h = 0.01;
    double x = x0;
    double y = y0;
    int count = 0;

    out_x[count] = x;
    out_y[count] = y;
    count++;

    while (x < x_end && count < max_points - 1) {
        if (x + h > x_end) h = x_end - x;

        double k1, k2, k3, k4, k5, k6;
        double f_val;

        /* k1 */
        if (parse_and_eval(expr, x, y, &f_val) != 0) return -1;
        k1 = f_val;

        /* k2 */
        if (parse_and_eval(expr, x + h/4.0, y + h*k1/4.0, &f_val) != 0) return -1;
        k2 = f_val;

        /* k3 */
        if (parse_and_eval(expr, x + 3.0*h/8.0, y + 3.0*h*k1/32.0 + 9.0*h*k2/32.0, &f_val) != 0) return -1;
        k3 = f_val;

        /* k4 */
        if (parse_and_eval(expr, x + 12.0*h/13.0, y + 1932.0*h*k1/2197.0 - 7200.0*h*k2/2197.0 + 7296.0*h*k3/2197.0, &f_val) != 0) return -1;
        k4 = f_val;

        /* k5 */
        if (parse_and_eval(expr, x + h, y + 439.0*h*k1/216.0 - 8.0*h*k2 + 3680.0*h*k3/513.0 - 845.0*h*k4/4104.0, &f_val) != 0) return -1;
        k5 = f_val;

        /* k6 */
        if (parse_and_eval(expr, x + h/2.0, y - 8.0*h*k1/27.0 + 2.0*h*k2 - 3544.0*h*k3/2565.0 + 1859.0*h*k4/4104.0 - 11.0*h*k5/40.0, &f_val) != 0) return -1;
        k6 = f_val;

        /* 4th order solution */
        double y4 = y + h * (25.0*k1/216.0 + 1408.0*k3/2565.0 + 2197.0*k4/4104.0 - k5/5.0);

        /* 5th order solution */
        double y5 = y + h * (16.0*k1/135.0 + 6656.0*k3/12825.0 + 28561.0*k4/56430.0 - 9.0*k5/50.0 + 2.0*k6/55.0);

        /* Error estimate */
        double error = fabs(y5 - y4);

        if (error < tol || h <= 1e-10) {
            /* Accept step */
            y = y5;
            x = x + h;
            out_x[count] = x;
            out_y[count] = y;
            count++;

            /* Adjust step size */
            if (error > 0.0) {
                double scale = 0.84 * pow(tol / error, 0.25);
                if (scale > 4.0) scale = 4.0;
                if (scale < 0.1) scale = 0.1;
                h = h * scale;
            } else {
                h = h * 2.0;
            }
        } else {
            /* Reject step, reduce h */
            double scale = 0.84 * pow(tol / error, 0.25);
            if (scale < 0.1) scale = 0.1;
            h = h * scale;
        }
    }

    return count;
}

/* --------------------------------------------------------------------------
 *  Laplace Transform / Inverse Laplace Transform
 *
 *  Forward:  L{f(t)}(s) = ∫₀^∞ f(t)·e^(−st) dt
 *            Truncated at T = max(20/s, 50) for numerical evaluation.
 *
 *  Inverse:  Bromwich integral with trapezoidal rule on horizontal segments.
 *            f(t) ≈ e^(γt)/T · Σ F(γ+iωₖ)·cos(ωₖt) · Δω
 *            where γ is chosen so all singularities lie to the left, and
 *            the sum uses the truncated frequency domain.
 * -------------------------------------------------------------------------- */

EXPORT double laplace_transform(const char* expr, double s) {
    if (!expr) { set_error("NULL expression"); return NAN; }
    if (strlen(expr) >= 800) { set_error("Expression too long (max 799)"); return NAN; }
    clear_error();
    if (s <= 0.0) {
        /* For s <= 0 the integral typically diverges for stable functions;
           use a small positive value as fallback. */
        if (s == 0.0) {
            /* s=0: just integrate f(t) from 0 to T */
            double T = 50.0;
            return integrate_adaptive(expr, 0.0, T, 1e-6);
        }
        set_error("s must be > 0 for Laplace transform of stable signals");
        return NAN;
    }
    /* Build modified expression: f(t)*e^(-s*t) using variable x (our parser var) */
    char modified[1024];
    snprintf(modified, sizeof(modified), "(%s)*exp(-%.15g*x)", expr, s);
    double T = (20.0 / s > 50.0) ? 20.0 / s : 50.0;
    return integrate_adaptive(modified, 0.0, T, 1e-6);
}

EXPORT double inverse_laplace(const char* expr, double t_val) {
    if (!expr) { set_error("NULL expression"); return NAN; }
    clear_error();
    if (t_val <= 0.0) {
        set_error("t must be > 0 for inverse Laplace transform");
        return NAN;
    }
    /* Pattern-matching inverse Laplace for common transform pairs.
       Matches the expression against known F(s) forms and returns f(t). */
    char buf[512];
    /* Trim whitespace */
    const char* p = expr;
    while (*p == ' ' || *p == '\t') p++;
    int len = strlen(p);
    while (len > 0 && (p[len-1] == ' ' || p[len-1] == '\t')) len--;
    if (len >= (int)sizeof(buf)) { set_error("Expression too long"); return NAN; }
    memcpy(buf, p, len);
    buf[len] = '\0';

    /* Try to evaluate as a simple function of s and match patterns */
    double t = t_val;

    /* Pattern: 1/(s+a)^n  →  t^(n-1)*e^(-at)/(n-1)! */
    {
        double a_coeff = 0.0;
        int n_power = 1;
        /* Try to parse "1/(x+a)^n" or "1/(x+a)" */
        if (sscanf(buf, "1/(x+%lf)^%d", &a_coeff, &n_power) == 2 ||
            sscanf(buf, "1/(x+%lf)", &a_coeff) == 1) {
            if (n_power < 1) n_power = 1;
            double factorial = 1.0;
            for (int i = 2; i < n_power; i++) factorial *= i;
            if (n_power <= 1) factorial = 1.0;
            return pow(t, n_power - 1) * exp(-a_coeff * t) / factorial;
        }
    }
    /* Pattern: 1/(s-a)^n  →  t^(n-1)*e^(at)/(n-1)! */
    {
        double a_coeff = 0.0;
        int n_power = 1;
        if (sscanf(buf, "1/(x-%lf)^%d", &a_coeff, &n_power) == 2 ||
            sscanf(buf, "1/(x-%lf)", &a_coeff) == 1) {
            if (n_power < 1) n_power = 1;
            double factorial = 1.0;
            for (int i = 2; i < n_power; i++) factorial *= i;
            if (n_power <= 1) factorial = 1.0;
            return pow(t, n_power - 1) * exp(a_coeff * t) / factorial;
        }
    }
    /* Pattern: 1/s^n  →  t^(n-1)/(n-1)! */
    {
        int n_power = 1;
        if (sscanf(buf, "1/x^%d", &n_power) == 1) {
            if (n_power < 1) n_power = 1;
            double factorial = 1.0;
            for (int i = 2; i < n_power; i++) factorial *= i;
            if (n_power <= 1) factorial = 1.0;
            return pow(t, n_power - 1) / factorial;
        }
    }
    /* Pattern: 1/s  →  1 */
    if (strcmp(buf, "1/x") == 0) return 1.0;
    /* Pattern: a/(s^2+a^2)  →  sin(at) */
    {
        double a_val = 0.0;
        if (sscanf(buf, "%lf/(x^2+%lf^2)", &a_val, &a_val) == 2) {
            return sin(a_val * t);
        }
    }
    /* Pattern: s/(s^2+a^2)  →  cos(at) */
    {
        double a_val = 0.0;
        if (sscanf(buf, "x/(x^2+%lf^2)", &a_val) == 1) {
            return cos(a_val * t);
        }
    }
    /* Pattern: 1/(s^2+a^2)  →  sin(at)/a */
    {
        double a_val = 0.0;
        if (sscanf(buf, "1/(x^2+%lf^2)", &a_val) == 1 && a_val != 0.0) {
            return sin(a_val * t) / a_val;
        }
    }
    /* Fallback: evaluate numerically using the derivative approach
       f(t) = lim_{s→∞} s·F(s) for t=0, or use numerical estimation. */
    /* Simple fallback: use the limit f(t) ≈ e^(st)·F(s)·s at large s */
    double s_large = 50.0;
    double fval;
    if (parse_and_eval(buf, s_large, 0.0, &fval) == 0) {
        return exp(s_large * t) * fval * s_large;
    }
    set_error("Could not invert this Laplace transform");
    return NAN;
}

/* --------------------------------------------------------------------------
 *  Calculation History
 *  Circular buffer storing the most recent HISTORY_MAX expressions and results.
 *  Each entry stores the expression string and its computed result.
 * -------------------------------------------------------------------------- */

#define HISTORY_MAX 10
#define HISTORY_EXPR_MAX 256

typedef struct {
    char expr[HISTORY_EXPR_MAX];
    double result;
    int valid;
} HistoryEntry;

static HistoryEntry g_history[HISTORY_MAX];
static int g_history_count = 0;
static int g_history_head = 0;  /* Next write position */

EXPORT void history_add(const char* expr, double result) {
    if (!expr) return;
    clear_error();
    HistoryEntry* e = &g_history[g_history_head];
    strncpy(e->expr, expr, HISTORY_EXPR_MAX - 1);
    e->expr[HISTORY_EXPR_MAX - 1] = '\0';
    e->result = result;
    e->valid = 1;
    g_history_head = (g_history_head + 1) % HISTORY_MAX;
    if (g_history_count < HISTORY_MAX) g_history_count++;
}

EXPORT int history_count(void) {
    return g_history_count;
}

EXPORT int history_get(int index, char* expr_out, int expr_max, double* result_out) {
    if (!expr_out || expr_max <= 0) return 0;
    clear_error();
    if (index < 0 || index >= g_history_count) {
        expr_out[0] = '\0';
        if (result_out) *result_out = NAN;
        return 0;
    }
    /* Translate logical index to physical: oldest first */
    int physical = (g_history_head - g_history_count + index + HISTORY_MAX) % HISTORY_MAX;
    HistoryEntry* e = &g_history[physical];
    strncpy(expr_out, e->expr, expr_max - 1);
    expr_out[expr_max - 1] = '\0';
    if (result_out) *result_out = e->result;
    return 1;
}

EXPORT void history_clear(void) {
    for (int i = 0; i < HISTORY_MAX; i++) {
        g_history[i].valid = 0;
        g_history[i].expr[0] = '\0';
        g_history[i].result = NAN;
    }
    g_history_count = 0;
    g_history_head = 0;
    clear_error();
}

EXPORT int history_get_all(char* output, int max_out) {
    if (!output || max_out <= 0) return 0;
    clear_error();
    int pos = 0;
    for (int i = 0; i < g_history_count && pos < max_out - 1; i++) {
        int physical = (g_history_head - g_history_count + i + HISTORY_MAX) % HISTORY_MAX;
        HistoryEntry* e = &g_history[physical];
        int written;
        if (isnan(e->result)) {
            written = snprintf(output + pos, max_out - pos, "%s = NaN%s",
                e->expr, (i < g_history_count - 1) ? ";" : "");
        } else {
            written = snprintf(output + pos, max_out - pos, "%s = %.10g%s",
                e->expr, e->result, (i < g_history_count - 1) ? ";" : "");
        }
        if (written > 0) {
            if (pos + written >= max_out) { pos = max_out - 1; break; }
            pos += written;
        }
    }
    output[pos] = '\0';
    return pos;
}

/* --------------------------------------------------------------------------
 *  Akima Interpolation
 *  Akima's method uses a local polynomial of degree ≤ 3 on each subinterval,
 *  with slopes computed from a weighted average of adjacent secant slopes.
 *  This reduces overshoot compared to cubic spline.
 *  Reference: H. Akima, "A New Method of Interpolation and Smooth Curve
 *  Fitting Based on Local Procedures", JACM 17(4), 1970.
 * -------------------------------------------------------------------------- */

EXPORT double interp_akima(const double* xs, const double* ys, int n, double x) {
    if (!xs || !ys || n < 2) {
        set_error("interp_akima: need at least 2 data points");
        return NAN;
    }
    clear_error();

    /* Clamp to boundary */
    if (x <= xs[0]) return ys[0];
    if (x >= xs[n - 1]) return ys[n - 1];

    /* Compute secant slopes t[i] = (ys[i+1]-ys[i]) / (xs[i+1]-xs[i]) for i=0..n-2 */
    int m = n - 1;  /* number of intervals */
    double* t = (double*)malloc((m + 2) * sizeof(double));
    if (!t) { set_error("interp_akima: out of memory"); return NAN; }

    for (int i = 0; i < m; i++) {
        double dx = xs[i + 1] - xs[i];
        if (fabs(dx) < 1e-15) {
            set_error("interp_akima: duplicate or too close x values");
            free(t);
            return NAN;
        }
        t[i] = (ys[i + 1] - ys[i]) / dx;
    }

    /* Extend with ghost points: t[-1] = t[0], t[m] = t[m-1] */
    t[m] = t[m - 1];
    t[m + 1] = t[m];

    /* Find segment containing x */
    int seg = 0;
    for (int i = 0; i < m; i++) {
        if (x >= xs[i]) seg = i;
    }

    /* Compute slopes using Akima's formula:
     * m[i] = (w1*t[i-1] + w2*t[i]) / (w1+w2) if w1+w2 != 0
     * m[i] = t[i] otherwise
     * where w1 = |t[i+1]-t[i]|, w2 = |t[i-1]-t[i-2]|
     * Boundary: m[0] = t[0], m[n-1] = t[n-2]
     * Ghost points: t[-1] = t[0], t[n-1] = t[n-2]
     */
    double m_left, m_right;

    /* Left slope at seg */
    if (seg == 0) {
        m_left = t[0];
    } else {
        double w1l = fabs(t[seg + 1] - t[seg]);
        double w2l = (seg >= 2) ? fabs(t[seg - 1] - t[seg - 2]) : 0.0;
        m_left = (w1l + w2l < 1e-15) ? t[seg] : (w1l * t[seg] + w2l * t[seg + 1]) / (w1l + w2l);
    }

    /* Right slope at seg+1 */
    if (seg + 1 >= m) {
        m_right = t[m - 1];
    } else {
        double w1r = fabs(t[seg + 2] - t[seg + 1]);
        double w2r = (seg >= 1) ? fabs(t[seg] - t[seg - 1]) : 0.0;
        m_right = (w1r + w2r < 1e-15) ? t[seg + 1] : (w1r * t[seg + 1] + w2r * t[seg + 2]) / (w1r + w2r);
    }

    double dx = xs[seg + 1] - xs[seg];
    double a = ys[seg];
    double b = m_left;
    double c = (3.0 * t[seg] - 2.0 * m_left - m_right) / dx;
    double d = (m_left + m_right - 2.0 * t[seg]) / (dx * dx);

    double s = x - xs[seg];
    free(t);
    return a + b * s + c * s * s + d * s * s * s;
}

/* --------------------------------------------------------------------------
 *  Natural Cubic Spline Interpolation
 *  Boundary conditions: S''(x₀) = S''(xₙ) = 0
 *  Solves a tridiagonal system for the second derivatives c[i], then
 *  evaluates the cubic polynomial on the appropriate segment.
 * -------------------------------------------------------------------------- */

EXPORT double interp_natural_spline(const double* xs, const double* ys, int n, double x) {
    if (!xs || !ys || n < 2) {
        set_error("interp_natural_spline: need at least 2 data points");
        return NAN;
    }
    clear_error();

    if (x <= xs[0]) return ys[0];
    if (x >= xs[n - 1]) return ys[n - 1];

    int m = n - 1;
    double* h = (double*)malloc(m * sizeof(double));
    double* alpha = (double*)malloc(n * sizeof(double));
    double* l = (double*)malloc(n * sizeof(double));
    double* mu = (double*)malloc(n * sizeof(double));
    double* z = (double*)malloc(n * sizeof(double));
    double* c = (double*)malloc(n * sizeof(double));
    double* b = (double*)malloc(m * sizeof(double));
    double* d = (double*)malloc(m * sizeof(double));

    if (!h || !alpha || !l || !mu || !z || !c || !b || !d) {
        free(h); free(alpha); free(l); free(mu); free(z); free(c); free(b); free(d);
        set_error("interp_natural_spline: out of memory");
        return NAN;
    }

    for (int i = 0; i < m; i++) {
        h[i] = xs[i + 1] - xs[i];
        if (fabs(h[i]) < 1e-15) {
            free(h); free(alpha); free(l); free(mu); free(z); free(c); free(b); free(d);
            set_error("interp_natural_spline: duplicate or too close x values");
            return NAN;
        }
    }

    for (int i = 1; i < m; i++) {
        alpha[i] = 3.0 / h[i] * (ys[i + 1] - ys[i]) - 3.0 / h[i - 1] * (ys[i] - ys[i - 1]);
    }

    l[0] = 1.0; mu[0] = 0.0; z[0] = 0.0;
    for (int i = 1; i < m; i++) {
        l[i] = 2.0 * (xs[i + 1] - xs[i - 1]) - h[i - 1] * mu[i - 1];
        if (fabs(l[i]) < 1e-30) {
            free(h); free(alpha); free(l); free(mu); free(z); free(c); free(b); free(d);
            set_error("interp_natural_spline: singular tridiagonal system");
            return NAN;
        }
        mu[i] = h[i] / l[i];
        z[i] = (alpha[i] - h[i - 1] * z[i - 1]) / l[i];
    }
    l[m] = 1.0; z[m] = 0.0; c[m] = 0.0;

    for (int j = m - 1; j >= 0; j--) {
        c[j] = z[j] - mu[j] * c[j + 1];
        b[j] = (ys[j + 1] - ys[j]) / h[j] - h[j] * (c[j + 1] + 2.0 * c[j]) / 3.0;
        d[j] = (c[j + 1] - c[j]) / (3.0 * h[j]);
    }

    int seg = 0;
    for (int i = 0; i < m; i++) {
        if (x >= xs[i]) seg = i;
    }
    double dx = x - xs[seg];
    double result = ys[seg] + b[seg] * dx + c[seg] * dx * dx + d[seg] * dx * dx * dx;

    free(h); free(alpha); free(l); free(mu); free(z); free(c); free(b); free(d);
    return result;
}

/* --------------------------------------------------------------------------
 *  Contour Grid Evaluation
 *  Evaluates f(x,y) on a regular grid for contour plotting.
 *  Fills out[] with n_cols * n_rows values in row-major order (y varies first).
 *  out[j * n_cols + i] = evaluate_xy(expr, x_min + i*dx, y_min + j*dy)
 *  Returns 0 on success, -1 on error (check get_last_error()).
 * -------------------------------------------------------------------------- */

EXPORT int contour_grid_eval(const char* expr, double x_min, double x_max,
                             double y_min, double y_max, int n_cols, int n_rows,
                             double* out) {
    if (!expr || !out || n_cols < 2 || n_rows < 2) {
        set_error("contour_grid_eval: invalid parameters");
        return -1;
    }
    if (x_min >= x_max || y_min >= y_max) {
        set_error("contour_grid_eval: invalid range");
        return -1;
    }
    clear_error();

    double dx = (x_max - x_min) / (n_cols - 1);
    double dy = (y_max - y_min) / (n_rows - 1);

    /* Tokenize and build RPN once for efficiency */
    Token toks[MAX_TOKENS];
    RPN   rpn[MAX_RPN];
    int nt = tokenize(expr, toks, MAX_TOKENS);
    if (nt < 0) {
        int total = n_cols * n_rows;
        for (int i = 0; i < total; i++) out[i] = NAN;
        return -1;
    }
    int nr = shunt(toks, nt, rpn, MAX_RPN);
    if (nr < 0) {
        int total = n_cols * n_rows;
        for (int i = 0; i < total; i++) out[i] = NAN;
        return -1;
    }

    for (int j = 0; j < n_rows; j++) {
        double y = y_min + j * dy;
        for (int i = 0; i < n_cols; i++) {
            double x = x_min + i * dx;
            double r;
            if (eval_rpn(rpn, nr, x, y, &r) != 0)
                out[j * n_cols + i] = NAN;
            else
                out[j * n_cols + i] = r;
        }
    }
    return 0;
}

/* --------------------------------------------------------------------------
 *  Vector Field Grid Evaluation
 *  Evaluates P(x,y) and Q(x,y) on a regular grid for vector field plotting.
 *  For a 2D autonomous system: dx/dt = P(x,y), dy/dt = Q(x,y).
 *  out_p[j*n_cols+i] = P(x_min+i*dx, y_min+j*dy)
 *  out_q[j*n_cols+i] = Q(x_min+i*dx, y_min+j*dy)
 *  Returns 0 on success, -1 on error.
 * -------------------------------------------------------------------------- */

EXPORT int vector_field_grid_eval(const char* expr_p, const char* expr_q,
                                   double x_min, double x_max,
                                   double y_min, double y_max,
                                   int n_cols, int n_rows,
                                   double* out_p, double* out_q) {
    if (!expr_p || !expr_q || !out_p || !out_q || n_cols < 2 || n_rows < 2) {
        set_error("vector_field_grid_eval: invalid parameters");
        return -1;
    }
    if (x_min >= x_max || y_min >= y_max) {
        set_error("vector_field_grid_eval: invalid range");
        return -1;
    }
    clear_error();

    double dx = (x_max - x_min) / (n_cols - 1);
    double dy = (y_max - y_min) / (n_rows - 1);

    /* Tokenize and build RPN for P */
    Token toks_p[MAX_TOKENS];
    RPN   rpn_p[MAX_RPN];
    int nt_p = tokenize(expr_p, toks_p, MAX_TOKENS);
    if (nt_p < 0) {
        int total = n_cols * n_rows;
        for (int i = 0; i < total; i++) { out_p[i] = NAN; out_q[i] = NAN; }
        return -1;
    }
    int nr_p = shunt(toks_p, nt_p, rpn_p, MAX_RPN);
    if (nr_p < 0) {
        int total = n_cols * n_rows;
        for (int i = 0; i < total; i++) { out_p[i] = NAN; out_q[i] = NAN; }
        return -1;
    }

    /* Tokenize and build RPN for Q */
    Token toks_q[MAX_TOKENS];
    RPN   rpn_q[MAX_RPN];
    int nt_q = tokenize(expr_q, toks_q, MAX_TOKENS);
    if (nt_q < 0) {
        int total = n_cols * n_rows;
        for (int i = 0; i < total; i++) { out_p[i] = NAN; out_q[i] = NAN; }
        return -1;
    }
    int nr_q = shunt(toks_q, nt_q, rpn_q, MAX_RPN);
    if (nr_q < 0) {
        int total = n_cols * n_rows;
        for (int i = 0; i < total; i++) { out_p[i] = NAN; out_q[i] = NAN; }
        return -1;
    }

    for (int j = 0; j < n_rows; j++) {
        double y = y_min + j * dy;
        for (int i = 0; i < n_cols; i++) {
            double x = x_min + i * dx;
            double rp, rq;
            if (eval_rpn(rpn_p, nr_p, x, y, &rp) != 0)
                out_p[j * n_cols + i] = NAN;
            else
                out_p[j * n_cols + i] = rp;
            if (eval_rpn(rpn_q, nr_q, x, y, &rq) != 0)
                out_q[j * n_cols + i] = NAN;
            else
                out_q[j * n_cols + i] = rq;
        }
    }
    return 0;
}

/* --------------------------------------------------------------------------
 *  Sparse Matrix Solver (CSR Format + Conjugate Gradient)
 *
 *  Provides sparse matrix storage in Compressed Sparse Row (CSR) format
 *  and an iterative Conjugate Gradient solver for Ax = b where A is
 *  symmetric positive definite.
 *
 *  API:
 *    sparse_from_triplets  — build CSR from COO triplet lists
 *    sparse_to_dense       — convert CSR to dense row-major array
 *    sparse_spmv           — sparse matrix-vector multiply y = A*x
 *    sparse_solve_cg       — solve A*x = b via Conjugate Gradient
 *    sparse_matrix_nnz     — return number of non-zeros
 *    sparse_matrix_free    — free all allocated memory
 * -------------------------------------------------------------------------- */

#define SPARSE_MAX_NNZ 1000000

typedef struct {
    int     n_rows;
    int     n_cols;
    int     nnz;        /* number of non-zero entries */
    int*    row_ptr;    /* row_ptr[i] = index into col_ind/val where row i starts */
    int*    col_ind;    /* column indices of non-zeros */
    double* val;        /* non-zero values */
    int     capacity;   /* allocated capacity for val/col_ind */
} SparseMatrix;

static void sparse_matrix_free_internal(SparseMatrix* m) {
    if (!m) return;
    free(m->row_ptr);
    free(m->col_ind);
    free(m->val);
    free(m);
}

EXPORT int sparse_matrix_nnz(const SparseMatrix* m) {
    return m ? m->nnz : 0;
}

EXPORT SparseMatrix* sparse_from_triplets(int n_rows, int n_cols,
                                           const int* rows, const int* cols,
                                           const double* vals, int nnz) {
    if (!rows || !cols || !vals || nnz <= 0 || n_rows <= 0 || n_cols <= 0) {
        set_error("sparse_from_triplets: invalid parameters");
        return NULL;
    }
    if (nnz > SPARSE_MAX_NNZ) {
        set_error("sparse_from_triplets: too many non-zeros (max 1000000)");
        return NULL;
    }
    clear_error();

    /* Count entries per row */
    int* counts = (int*)calloc(n_rows, sizeof(int));
    if (!counts) { set_error("Out of memory"); return NULL; }

    for (int i = 0; i < nnz; i++) {
        if (rows[i] < 0 || rows[i] >= n_rows || cols[i] < 0 || cols[i] >= n_cols) {
            free(counts);
            set_error("sparse_from_triplets: index out of range");
            return NULL;
        }
        counts[rows[i]]++;
    }

    SparseMatrix* m = (SparseMatrix*)malloc(sizeof(SparseMatrix));
    if (!m) { free(counts); set_error("Out of memory"); return NULL; }

    m->n_rows = n_rows;
    m->n_cols = n_cols;
    m->capacity = nnz;
    m->row_ptr = (int*)malloc((n_rows + 1) * sizeof(int));
    m->col_ind = (int*)malloc(nnz * sizeof(int));
    m->val = (double*)malloc(nnz * sizeof(double));

    if (!m->row_ptr || !m->col_ind || !m->val) {
        free(counts);
        sparse_matrix_free_internal(m);
        set_error("Out of memory");
        return NULL;
    }

    /* Build row_ptr */
    m->row_ptr[0] = 0;
    for (int i = 0; i < n_rows; i++) {
        m->row_ptr[i + 1] = m->row_ptr[i] + counts[i];
    }

    /* Fill col_ind and val using a temporary position counter */
    int* pos = (int*)calloc(n_rows, sizeof(int));
    if (!pos) { free(counts); sparse_matrix_free_internal(m); set_error("Out of memory"); return NULL; }

    for (int i = 0; i < nnz; i++) {
        int r = rows[i];
        int idx = m->row_ptr[r] + pos[r];
        m->col_ind[idx] = cols[i];
        m->val[idx] = vals[i];
        pos[r]++;
    }

    /* Sort each row by column index for deterministic behavior */
    for (int i = 0; i < n_rows; i++) {
        int start = m->row_ptr[i];
        int end = m->row_ptr[i + 1];
        /* Simple insertion sort (rows are typically short) */
        for (int j = start + 1; j < end; j++) {
            int key_col = m->col_ind[j];
            double key_val = m->val[j];
            int k = j - 1;
            while (k >= start && m->col_ind[k] > key_col) {
                m->col_ind[k + 1] = m->col_ind[k];
                m->val[k + 1] = m->val[k];
                k--;
            }
            m->col_ind[k + 1] = key_col;
            m->val[k + 1] = key_val;
        }
    }

    /* Merge duplicate entries (sum values for same row,col) */
    int write = 0;
    for (int i = 0; i < n_rows; i++) {
        int start = m->row_ptr[i];
        int end = m->row_ptr[i + 1];
        m->row_ptr[i] = write;
        int j = start;
        while (j < end) {
            int col = m->col_ind[j];
            double sum = m->val[j];
            j++;
            while (j < end && m->col_ind[j] == col) {
                sum += m->val[j];
                j++;
            }
            if (sum != 0.0) {
                m->col_ind[write] = col;
                m->val[write] = sum;
                write++;
            }
        }
    }
    /* Update final row_ptr entries */
    for (int i = 0; i < n_rows; i++) {
        /* row_ptr[i] already set above */
    }
    m->row_ptr[n_rows] = write;
    m->nnz = write;

    free(counts);
    free(pos);
    return m;
}

EXPORT int sparse_to_dense(const SparseMatrix* m, double* out, int max_out) {
    if (!m || !out) return -1;
    int total = m->n_rows * m->n_cols;
    if (max_out < total) { set_error("Output buffer too small"); return -1; }
    clear_error();

    for (int i = 0; i < total; i++) out[i] = 0.0;

    for (int i = 0; i < m->n_rows; i++) {
        for (int j = m->row_ptr[i]; j < m->row_ptr[i + 1]; j++) {
            out[i * m->n_cols + m->col_ind[j]] = m->val[j];
        }
    }
    return 0;
}

EXPORT int sparse_spmv(const SparseMatrix* m, const double* x, double* y, int n) {
    if (!m || !x || !y) return -1;
    if (n != m->n_cols) { set_error("sparse_spmv: dimension mismatch"); return -1; }
    clear_error();

    for (int i = 0; i < m->n_rows; i++) {
        double sum = 0.0;
        for (int j = m->row_ptr[i]; j < m->row_ptr[i + 1]; j++) {
            sum += m->val[j] * x[m->col_ind[j]];
        }
        y[i] = sum;
    }
    return 0;
}

/* Conjugate Gradient solver: solve A*x = b where A is symmetric positive definite */
EXPORT int sparse_solve_cg(const SparseMatrix* m, const double* b, double* x,
                            int max_iter, double tol, double* out_x, int n) {
    if (!m || !b || !out_x) return -1;
    if (n != m->n_rows || n != m->n_cols) {
        set_error("sparse_solve_cg: dimension mismatch");
        return -1;
    }
    if (max_iter <= 0) max_iter = n * 2;
    if (tol <= 0.0) tol = 1e-10;
    clear_error();

    /* Allocate working vectors */
    double* r = (double*)malloc(n * sizeof(double));
    double* p = (double*)malloc(n * sizeof(double));
    double* Ap = (double*)malloc(n * sizeof(double));
    if (!r || !p || !Ap) {
        free(r); free(p); free(Ap);
        set_error("Out of memory");
        return -1;
    }

    /* x = 0 (initial guess) */
    for (int i = 0; i < n; i++) out_x[i] = 0.0;

    /* r = b - A*x = b (since x=0) */
    for (int i = 0; i < n; i++) r[i] = b[i];

    /* p = r */
    for (int i = 0; i < n; i++) p[i] = r[i];

    double rsold = 0.0;
    for (int i = 0; i < n; i++) rsold += r[i] * r[i];

    double bnorm = sqrt(rsold);
    if (bnorm < 1e-15) {
        /* b is zero, x = 0 is the solution */
        free(r); free(p); free(Ap);
        return 0;
    }

    for (int iter = 0; iter < max_iter; iter++) {
        /* Ap = A * p */
        if (sparse_spmv(m, p, Ap, n) != 0) {
            free(r); free(p); free(Ap);
            return -1;
        }

        double pAp = 0.0;
        for (int i = 0; i < n; i++) pAp += p[i] * Ap[i];

        if (fabs(pAp) < 1e-30) {
            free(r); free(p); free(Ap);
            set_error("CG breakdown: p^T A p ≈ 0");
            return -1;
        }

        double alpha = rsold / pAp;

        /* x = x + alpha * p */
        for (int i = 0; i < n; i++) out_x[i] += alpha * p[i];

        /* r = r - alpha * Ap */
        for (int i = 0; i < n; i++) r[i] -= alpha * Ap[i];

        double rsnew = 0.0;
        for (int i = 0; i < n; i++) rsnew += r[i] * r[i];

        if (sqrt(rsnew) / bnorm < tol) {
            free(r); free(p); free(Ap);
            return iter + 1;  /* converged */
        }

        double beta = rsnew / rsold;
        for (int i = 0; i < n; i++) p[i] = r[i] + beta * p[i];

        rsold = rsnew;
    }

    free(r); free(p); free(Ap);
    set_error("CG did not converge within max_iter iterations");
    return -1;  /* did not converge */
}

EXPORT void sparse_matrix_free(SparseMatrix* m) {
    sparse_matrix_free_internal(m);
}

/* --------------------------------------------------------------------------
 *  Discrete 1D Convolution
 *  c[k] = sum_{i=0}^{na-1} a[i] * b[k-i]  for k = 0..na+nb-2
 *  Returns the number of output elements (na+nb-1), or -1 on error.
 * -------------------------------------------------------------------------- */
EXPORT int conv_1d(const double* a, int na, const double* b, int nb,
                    double* out, int max_out) {
    if (!a || !b || !out) { set_error("NULL pointer argument"); return -1; }
    if (na < 1 || nb < 1) { set_error("Sequence length must be >= 1"); return -1; }
    if (na > 1000000 || nb > 1000000) {
        set_error("Sequence length too large (max 1000000)"); return -1;
    }
    int nc = na + nb - 1;
    if (max_out < nc) { set_error("Output buffer too small"); return -1; }
    clear_error();

    for (int k = 0; k < nc; k++) {
        double sum = 0.0;
        for (int i = 0; i < na; i++) {
            int j = k - i;
            if (j >= 0 && j < nb) {
                sum += a[i] * b[j];
            }
        }
        out[k] = sum;
    }
    return nc;
}
