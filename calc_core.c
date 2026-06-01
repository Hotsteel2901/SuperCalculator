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

#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT
#endif

static char g_error[256] = {0};

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

EXPORT const char* get_last_error(void) { return g_error; }

#define MAX_TOKENS 512
#define MAX_RPN    512

typedef enum {
    T_NUMBER, T_VARIABLE_X, T_VARIABLE_Y, T_OP, T_FUNC, T_LPAREN, T_RPAREN, T_COMMA, T_END
} TokenKind;

typedef enum {
    F_SIN, F_COS, F_TAN, F_LOG, F_LN, F_SQRT, F_EXP, F_ABS
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
            else if (!strcmp(name, "abs"))  { toks[n].kind=T_FUNC; toks[n].func=F_ABS;  n++; continue; }
            else { set_error("Unknown function"); return -1; }
        }
        switch (*s) {
            case '+': case '-': case '*': case '/': case '^':
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
    if (op == '*' || op == '/') return 2;
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
    if (parse_and_eval(expr, x, 0.0, &r) != 0) return NAN;
    return r;
}

EXPORT double evaluate_xy(const char* expr, double x, double y) {
    double r;
    if (parse_and_eval(expr, x, y, &r) != 0) return NAN;
    return r;
}

EXPORT void evaluate_array(const char* expr, const double* xs, double* out, int n) {
    if (!expr || !xs || !out || n <= 0) return;
    Token toks[MAX_TOKENS];
    RPN   rpn[MAX_RPN];
    g_error[0] = '\0';
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
    Token toks[MAX_TOKENS];
    RPN   rpn[MAX_RPN];
    g_error[0] = '\0';
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
    if (parse_and_eval(expr, x+h, 0.0, &fp) != 0) return NAN;
    if (parse_and_eval(expr, x-h, 0.0, &fm) != 0) return NAN;
    return (fp - fm) / (2.0 * h);
}

EXPORT double derivative2(const char* expr, double x, double h) {
    double fc, fp, fm;
    if (parse_and_eval(expr, x,   0.0, &fc) != 0) return NAN;
    if (parse_and_eval(expr, x+h, 0.0, &fp) != 0) return NAN;
    if (parse_and_eval(expr, x-h, 0.0, &fm) != 0) return NAN;
    return (fp - 2.0*fc + fm) / (h*h);
}

EXPORT double integrate(const char* expr, double a, double b, int n) {
    if (n < 2 || n % 2 != 0) { set_error("n must be even and >= 2"); return NAN; }
    if (a > b) { set_error("Invalid interval: a must be <= b"); return NAN; }
    if (a == b) return 0.0;
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
    if (a > b) { set_error("Invalid interval: a must be <= b"); return NAN; }
    if (a == b) return 0.0;
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

static double golden_section_min(const char* expr, double a, double b, double tol, int max_iter) {
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
    return richardson_limit(expr, a, -1.0, max_level);
}

EXPORT double limit_right(const char* expr, double a, int max_level) {
    if (max_level <= 0) max_level = 10;
    return richardson_limit(expr, a, 1.0, max_level);
}

EXPORT double limit(const char* expr, double a, double tol, int max_level) {
    if (max_level <= 0) max_level = 10;
    if (tol <= 0.0) tol = 1e-8;

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
    if (n == 1) {
        double fp = _eval_or_nan(expr, x + h);
        double fm = _eval_or_nan(expr, x - h);
        if (isnan(fp) || isnan(fm)) return NAN;
        return (fp - fm) / (2.0 * h);
    }
    double fp = _central_diff_nth(expr, x + h, n - 1, h);
    double fm = _central_diff_nth(expr, x - h, n - 1, h);
    if (isnan(fp) || isnan(fm)) return NAN;
    return (fp - fm) / (2.0 * h);
}

EXPORT double nth_derivative(const char* expr, double x, int n, double h) {
    if (n < 0) { set_error("Derivative order must be non-negative"); return NAN; }
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
