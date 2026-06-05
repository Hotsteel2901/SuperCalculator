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

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif
#ifndef M_E
#define M_E  2.71828182845904523536
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
    T_NUMBER, T_VARIABLE_X, T_VARIABLE_Y, T_OP, T_FUNC, T_LPAREN, T_RPAREN, T_COMMA, T_END
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
} Token;

typedef struct {
    int      tag;
    double   num;
    char     op;
    FuncId   func;
} RPN;

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
            else { set_error("Unknown function"); return -1; }
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
        } else if (t.kind == T_COMMA) {
            while (sp > 0 && stack[sp-1].kind != T_LPAREN) {
                Token top = stack[--sp];
                if (top.kind == T_OP) {
                    output[out_n].tag=2; output[out_n].op=top.op; out_n++;
                } else if (top.kind == T_FUNC) {
                    output[out_n].tag=3; output[out_n].func=top.func; out_n++;
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
                Token top = stack[--sp];
                if (top.kind == T_OP) {
                    output[out_n].tag=2; output[out_n].op=top.op; out_n++;
                } else if (top.kind == T_FUNC) {
                    output[out_n].tag=3; output[out_n].func=top.func; out_n++;
                }
            }
            if (t.kind == T_RPAREN && sp > 0 && stack[sp-1].kind == T_LPAREN)
                sp--;
            else if (t.kind == T_RPAREN) {
                set_error("Mismatched parentheses"); return -1;
            }
            if (t.kind == T_RPAREN || t.kind == T_END) {
                while (sp > 0 && stack[sp-1].kind == T_OP && stack[sp-1].op == '!') {
                    Token top = stack[--sp];
                    output[out_n].tag=2; output[out_n].op=top.op; out_n++;
                }
            }
            if (t.kind == T_END) {
                while (sp > 0) {
                    Token top = stack[--sp];
                    if (top.kind == T_OP) {
                        output[out_n].tag=2; output[out_n].op=top.op; out_n++;
                    } else if (top.kind == T_FUNC) {
                        output[out_n].tag=3; output[out_n].func=top.func; out_n++;
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
                if (a < 0 || floor(a) != a) { set_error("Factorial requires non-negative integer"); stack[sp++] = NAN; }
                else if (a > 170) { set_error("Factorial overflow (max 170!)"); stack[sp++] = INFINITY; }
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
                    case '/': stack[sp++] = b ? a/b : (set_error("Division by zero"),NAN); break;
                    case '%': stack[sp++] = b ? fmod(a,b) : (set_error("Modulo by zero"),NAN); break;
                    case '^': stack[sp++] = pow(a,b); break;
                    default:  set_error("Unknown operator"); return -1;
                }
            }
        } else if (t.tag == 3) {
            if (sp < 1) { set_error("Invalid expression"); return -1; }
            stack[sp-1] = apply_func(t.func, stack[sp-1]);
        }
    }
    if (sp != 1) { set_error("Invalid expression"); return -1; }
    *result = stack[0];
    return 0;
}

static int parse_and_eval(const char* expr, double x, double y, double* result) {
    g_error[0] = '\0';
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
    if (parse_and_eval(expr, x, 0.0, &r) != 0) return NAN;
    return r;
}

EXPORT double evaluate_xy(const char* expr, double x, double y) {
    double r;
    clear_error();
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
    if (parse_and_eval(expr, x+h, 0.0, &fp) != 0) return NAN;
    if (parse_and_eval(expr, x-h, 0.0, &fm) != 0) return NAN;
    return (fp - fm) / (2.0 * h);
}

EXPORT double derivative2(const char* expr, double x, double h) {
    double fc, fp, fm;
    clear_error();
    if (parse_and_eval(expr, x,   0.0, &fc) != 0) return NAN;
    if (parse_and_eval(expr, x+h, 0.0, &fp) != 0) return NAN;
    if (parse_and_eval(expr, x-h, 0.0, &fm) != 0) return NAN;
    return (fp - 2.0*fc + fm) / (h*h);
}

EXPORT double integrate(const char* expr, double a, double b, int n) {
    if (n < 2 || n % 2 != 0) { set_error("n must be even and >= 2"); return NAN; }
    if (a > b) { set_error("Invalid interval: a must be <= b"); return NAN; }
    if (a == b) return 0.0;
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
    if (xmin >= xmax) { set_error("Invalid interval: xmin must be < xmax"); return NAN; }
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
            if (isnan(nx)) { set_error("Newton step produced NaN"); return NAN; }
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
    if (a >= b) { set_error("Invalid interval: a must be < b"); return NAN; }
    clear_error();
    double fa, fb, fc, c;
    if (parse_and_eval(expr, a, 0.0, &fa) != 0) return NAN;
    if (isnan(fa)) { set_error("Function returned NaN at interval endpoint"); return NAN; }
    if (parse_and_eval(expr, b, 0.0, &fb) != 0) return NAN;
    if (isnan(fb)) { set_error("Function returned NaN at interval endpoint"); return NAN; }
    if (fabs(fa) < tol) return a;
    if (fabs(fb) < tol) return b;
    if (fa == 0.0) return a;
    if (fb == 0.0) return b;
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
    if (a > b) { set_error("Invalid interval: a must be <= b"); return NAN; }
    if (a == b) return 0.0;
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
    double table[16][16];
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
    if (max_level <= 0) max_level = 10;
    clear_error();
    return richardson_limit(expr, a, -1.0, max_level);
}

EXPORT double limit_right(const char* expr, double a, int max_level) {
    if (max_level <= 0) max_level = 10;
    clear_error();
    return richardson_limit(expr, a, 1.0, max_level);
}

EXPORT double limit(const char* expr, double a, double tol, int max_level) {
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
    if (!fvals) return NAN;

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
    return sum / h2n;
}

EXPORT double nth_derivative(const char* expr, double x, int n, double h) {
    if (n < 0) { set_error("Derivative order must be non-negative"); return NAN; }
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
    if (order < 0) { set_error("Order must be non-negative"); return -1; }
    if (!out_coeffs || max_out < order + 1) { set_error("Output buffer too small"); return -1; }
    clear_error();

    double h = 1e-5;
    double factorial = 1.0;

    for (int k = 0; k <= order; k++) {
        if (k > 0) factorial *= k;
        double dk = nth_derivative(expr, a, k, h);
        if (isnan(dk)) return -1;
        out_coeffs[k] = dk / factorial;
    }
    return order + 1;
}

EXPORT double find_maximum(const char* expr, double a, double b, double tol, int max_iter) {
    if (a >= b) { set_error("Invalid interval: a must be < b"); return NAN; }
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
    if (a >= b) { set_error("Invalid interval: a must be < b"); return NAN; }
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
    if (denom == 0.0) {
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
    double im = (a.im >= 0 ? 1.0 : -1.0) * sqrt((r - a.re) / 2.0);
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
        else
            return complex_make(INFINITY, INFINITY);
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
        double im = strtod(end, &end);
        if (*end == 'i' || *end == 'I') {
            result->im = (sign == '+') ? im : -im;
            return 0;
        }
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
    Complex a = complex_make(re1, im1);
    Complex b = complex_make(re2, im2);
    Complex result = complex_div(a, b);
    *out_re = result.re;
    *out_im = result.im;
}

EXPORT void complex_pow_values(double re1, double im1, double re2, double im2,
                               double* out_re, double* out_im) {
    if (!out_re || !out_im) return;
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

        x += dx;
        y += dy;
    }

    *out_x = x;
    *out_y = y;
    set_error("solve_system_2d did not converge within max_iter iterations");
    return 0;
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
