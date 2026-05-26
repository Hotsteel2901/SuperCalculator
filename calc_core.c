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
    while (*s && n < max_toks) {
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
    if (op == '!' ) return 4;
    if (op == '+' || op == '-') return 1;
    if (op == '*' || op == '/') return 2;
    if (op == '^')              return 3;
    return 0;
}

static int is_right_assoc(char op) { return op == '^'; }

static int shunt(Token* toks, int ntoks, RPN* output, int max_out) {
    Token stack[256]; int sp = 0;
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
            if (t.op == '-' && prev_was_op_or_lp) t.op = '~';
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
                stack[sp++] = t;
                prev_was_op_or_lp = 1;
            }
        } else if (t.kind == T_LPAREN) {
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
            if (sp > 0 && stack[sp-1].kind == T_LPAREN)
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
            prev_was_op_or_lp = 0;
        }
    }
    if (out_n >= max_out) { set_error("Expression too long"); return -1; }
    return out_n;
}

static double apply_func(FuncId f, double v) {
    switch (f) {
        case F_SIN:  return sin(v);
        case F_COS:  return cos(v);
        case F_TAN:  return tan(v);
        case F_LOG:  return log10(v);
        case F_LN:   return log(v);
        case F_SQRT: return sqrt(v);
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
                    for (int i = 2; i <= (int)a; i++) r *= i;
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
    for (int i = 0; i < n; i++) {
        double r;
        if (parse_and_eval(expr, xs[i], 0.0, &r) != 0) out[i] = NAN;
        else out[i] = r;
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
    double x = guess, fp, fm;
    if (x < xmin) x = xmin + 0.1*(xmax-xmin);
    if (x > xmax) x = xmax - 0.1*(xmax-xmin);

    for (int iter = 0; iter < max_iter; iter++) {
        double f, df;
        if (parse_and_eval(expr, x, 0.0, &f) != 0) return NAN;
        if (fabs(f) < tol) return x;
        double h = 1e-6 * (fabs(x) + 1.0);
        if (parse_and_eval(expr, x+h, 0.0, &fp) != 0) return NAN;
        if (parse_and_eval(expr, x-h, 0.0, &fm) != 0) return NAN;
        df = (fp - fm) / (2.0*h);
        if (fabs(df) < 1e-15) {
            double fa; if (parse_and_eval(expr, xmin, 0.0, &fa) != 0) return NAN;
            double mid = (xmin + xmax)/2.0, fmid;
            if (parse_and_eval(expr, mid, 0.0, &fmid) != 0) return NAN;
            if (fa*fmid <= 0) xmax = mid;
            else xmin = mid;
            x = mid;
        } else {
            double nx = x - f/df;
            if (nx < xmin || nx > xmax) {
                double fa; if (parse_and_eval(expr, xmin, 0.0, &fa) != 0) return NAN;
                double mid = (xmin+xmax)/2.0, fmid;
                if (parse_and_eval(expr, mid, 0.0, &fmid) != 0) return NAN;
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
    double fa, fb, fc, c;
    if (parse_and_eval(expr, a, 0.0, &fa) != 0) return NAN;
    if (parse_and_eval(expr, b, 0.0, &fb) != 0) return NAN;
    if (signbit(fa) == signbit(fb)) { set_error("f(a) and f(b) must have opposite signs"); return NAN; }
    for (int i = 0; i < max_iter; i++) {
        c = (a+b)/2.0;
        if (parse_and_eval(expr, c, 0.0, &fc) != 0) return NAN;
        if (fabs(fc) < tol || (b-a)/2.0 < tol) return c;
        if (signbit(fa) != signbit(fc)) { b = c; fb = fc; }
        else { a = c; fa = fc; }
    }
    set_error("Bisection did not converge");
    return (a+b)/2.0;
}

EXPORT double integrate_adaptive(const char* expr, double a, double b, double tol) {
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
    if (parse_and_eval(expr, d, 0.0, &fd) != 0) return NAN;

    for (int i = 0; i < max_iter && fabs(b - a) > tol; i++) {
        if (fc < fd) {
            b = d; d = c; fd = fc;
            c = a + resphi * (b - a);
            if (parse_and_eval(expr, c, 0.0, &fc) != 0) return NAN;
        } else {
            a = c; c = d; fc = fd;
            d = b - resphi * (b - a);
            if (parse_and_eval(expr, d, 0.0, &fd) != 0) return NAN;
        }
    }
    return (b + a) / 2.0;
}

EXPORT double find_minimum(const char* expr, double a, double b, double tol, int max_iter) {
    if (a >= b) { set_error("Invalid interval: a must be < b"); return NAN; }
    return golden_section_min(expr, a, b, tol, max_iter);
}

EXPORT double find_maximum(const char* expr, double a, double b, double tol, int max_iter) {
    if (a >= b) { set_error("Invalid interval: a must be < b"); return NAN; }
    const double resphi = GOLDEN_RATIO_RES;
    double c = a + resphi * (b - a);
    double d = b - resphi * (b - a);
    double fc, fd;

    if (parse_and_eval(expr, c, 0.0, &fc) != 0) return NAN;
    if (parse_and_eval(expr, d, 0.0, &fd) != 0) return NAN;
    fc = -fc; fd = -fd;

    for (int i = 0; i < max_iter && fabs(b - a) > tol; i++) {
        if (fc < fd) {
            b = d; d = c; fd = fc;
            c = a + resphi * (b - a);
            if (parse_and_eval(expr, c, 0.0, &fc) != 0) return NAN;
            fc = -fc;
        } else {
            a = c; c = d; fc = fd;
            d = b - resphi * (b - a);
            if (parse_and_eval(expr, d, 0.0, &fd) != 0) return NAN;
            fd = -fd;
        }
    }
    return (b + a) / 2.0;
}
