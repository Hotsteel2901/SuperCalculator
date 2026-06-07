package com.supercalc;

import android.content.Intent;
import android.os.Bundle;
import android.text.method.ScrollingMovementMethod;
import android.widget.ArrayAdapter;
import android.widget.AutoCompleteTextView;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import com.google.android.material.button.MaterialButton;
import com.google.android.material.chip.Chip;
import com.google.android.material.card.MaterialCardView;
import com.github.mikephil.charting.charts.LineChart;
import com.github.mikephil.charting.data.Entry;
import com.github.mikephil.charting.data.LineData;
import com.github.mikephil.charting.data.LineDataSet;
import com.github.mikephil.charting.components.XAxis;
import com.github.mikephil.charting.components.YAxis;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.time.LocalDate;
import java.time.temporal.ChronoUnit;

public class CalcActivity extends AppCompatActivity {

    private EditText exprInput, xInput, aInput, bInput, guessInput;
    private EditText xParamInput, yParamInput, tMinInput, tMaxInput;
    private EditText rPolarInput, thetaMinInput, thetaMaxInput;
    private EditText taylorOrderInput;
    private EditText odeExprInput, odeX0Input, odeY0Input, odeXEndInput, odeStepsInput;
    private EditText statsDataInput;
    private EditText areaGInput;
    private EditText sysFInput, sysGInput, sysX0Input, sysY0Input;
    private EditText matrixAInput, matrixBInput;
    private TextView resultView;
    private LineChart lineChart;
    private MaterialCardView graphCard;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_calc);

        exprInput  = findViewById(R.id.expr_input);
        xInput     = findViewById(R.id.x_input);
        aInput     = findViewById(R.id.a_input);
        bInput     = findViewById(R.id.b_input);
        guessInput = findViewById(R.id.guess_input);
        xParamInput = findViewById(R.id.x_param_input);
        yParamInput = findViewById(R.id.y_param_input);
        tMinInput  = findViewById(R.id.t_min_input);
        tMaxInput  = findViewById(R.id.t_max_input);
        rPolarInput = findViewById(R.id.r_polar_input);
        thetaMinInput = findViewById(R.id.theta_min_input);
        thetaMaxInput = findViewById(R.id.theta_max_input);
        taylorOrderInput = findViewById(R.id.taylor_order_input);
        odeExprInput = findViewById(R.id.ode_expr_input);
        odeX0Input = findViewById(R.id.ode_x0_input);
        odeY0Input = findViewById(R.id.ode_y0_input);
        odeXEndInput = findViewById(R.id.ode_xend_input);
        odeStepsInput = findViewById(R.id.ode_steps_input);
        resultView = findViewById(R.id.result_view);
        resultView.setMovementMethod(new ScrollingMovementMethod());
        lineChart  = findViewById(R.id.line_chart);
        graphCard  = findViewById(R.id.graph_card);

        // Operation buttons — MaterialButton extends Button, so findViewById works
        MaterialButton btnEval   = findViewById(R.id.btn_evaluate);
        MaterialButton btnDeriv  = findViewById(R.id.btn_derivative);
        MaterialButton btnDeriv2 = findViewById(R.id.btn_derivative2);
        MaterialButton btnInt    = findViewById(R.id.btn_integrate);
        MaterialButton btnSolve  = findViewById(R.id.btn_solve);
        MaterialButton btnPlot   = findViewById(R.id.btn_plot);
        MaterialButton btnFindMin = findViewById(R.id.btn_find_min);
        MaterialButton btnFindMax = findViewById(R.id.btn_find_max);
        MaterialButton btnClear  = findViewById(R.id.btn_clear);
        MaterialButton btnScanRoots = findViewById(R.id.btn_scan_roots);
        MaterialButton btnPlot3D = findViewById(R.id.btn_plot_3d);
        MaterialButton btnTable = findViewById(R.id.btn_table);
        MaterialButton btnTangent = findViewById(R.id.btn_tangent);
        MaterialButton btnNormal = findViewById(R.id.btn_normal);
        MaterialButton btnArcLength = findViewById(R.id.btn_arc_length);
        MaterialButton btnFFT = findViewById(R.id.btn_fft);
        MaterialButton btnLimit = findViewById(R.id.btn_limit);
        MaterialButton btnLimitLeft = findViewById(R.id.btn_limit_left);
        MaterialButton btnLimitRight = findViewById(R.id.btn_limit_right);

        btnEval  .setOnClickListener(v -> onEvaluate());
        btnDeriv .setOnClickListener(v -> onDerivative());
        btnDeriv2.setOnClickListener(v -> onDerivative2());
        btnInt   .setOnClickListener(v -> onIntegrate());
        btnSolve .setOnClickListener(v -> onSolve());
        btnPlot  .setOnClickListener(v -> openPlot());
        btnFindMin.setOnClickListener(v -> onFindExtremum(true));
        btnFindMax.setOnClickListener(v -> onFindExtremum(false));
        btnClear .setOnClickListener(v -> resultView.setText(""));
        btnScanRoots.setOnClickListener(v -> onScanRoots());
        btnPlot3D.setOnClickListener(v -> openPlot3D());
        btnTable.setOnClickListener(v -> onGenerateTable());
        btnTangent.setOnClickListener(v -> onTangentNormal(true));
        btnNormal.setOnClickListener(v -> onTangentNormal(false));
        btnArcLength.setOnClickListener(v -> onArcLength());
        btnFFT.setOnClickListener(v -> onFFT());
        btnLimit.setOnClickListener(v -> onLimit());
        btnLimitLeft.setOnClickListener(v -> onLimitSide(true));
        btnLimitRight.setOnClickListener(v -> onLimitSide(false));

        MaterialButton btnTaylor = findViewById(R.id.btn_taylor);
        MaterialButton btnTaylorPlot = findViewById(R.id.btn_taylor_plot);
        btnTaylor.setOnClickListener(v -> onTaylor());
        btnTaylorPlot.setOnClickListener(v -> onTaylorPlot());

        MaterialButton btnOdeSolve = findViewById(R.id.btn_ode_solve);
        MaterialButton btnOdePlot = findViewById(R.id.btn_ode_plot);
        btnOdeSolve.setOnClickListener(v -> onOdeSolve());
        btnOdePlot.setOnClickListener(v -> onOdePlot());

        // Statistics
        statsDataInput = findViewById(R.id.stats_data_input);
        MaterialButton btnStatsCompute = findViewById(R.id.btn_stats_compute);
        MaterialButton btnStatsSort = findViewById(R.id.btn_stats_sort);
        MaterialButton btnStatsHistogram = findViewById(R.id.btn_stats_histogram);
        btnStatsCompute.setOnClickListener(v -> onStatsCompute());
        btnStatsSort.setOnClickListener(v -> onStatsSort());
        btnStatsHistogram.setOnClickListener(v -> onStatsHistogram());

        // Curve Fitting / Regression
        EditText regXInput = findViewById(R.id.reg_x_input);
        EditText regYInput = findViewById(R.id.reg_y_input);
        EditText regDegreeInput = findViewById(R.id.reg_degree_input);
        MaterialButton btnRegLinear = findViewById(R.id.btn_reg_linear);
        MaterialButton btnRegQuad = findViewById(R.id.btn_reg_quad);
        MaterialButton btnRegPoly = findViewById(R.id.btn_reg_poly);
        MaterialButton btnRegExp = findViewById(R.id.btn_reg_exp);
        MaterialButton btnRegPower = findViewById(R.id.btn_reg_power);
        MaterialButton btnRegLog = findViewById(R.id.btn_reg_log);
        MaterialButton btnRegPlot = findViewById(R.id.btn_reg_plot);
        btnRegLinear.setOnClickListener(v -> onRegLinear(regXInput, regYInput));
        btnRegQuad.setOnClickListener(v -> onRegPoly(regXInput, regYInput, 2));
        btnRegPoly.setOnClickListener(v -> {
            int deg = 3;
            try { deg = Integer.parseInt(regDegreeInput.getText().toString().trim()); } catch (Exception ignored) {}
            onRegPoly(regXInput, regYInput, deg);
        });
        btnRegExp.setOnClickListener(v -> onRegExponential(regXInput, regYInput));
        btnRegPower.setOnClickListener(v -> onRegPower(regXInput, regYInput));
        btnRegLog.setOnClickListener(v -> onRegLogarithmic(regXInput, regYInput));
        btnRegPlot.setOnClickListener(v -> onRegPlot(regXInput, regYInput));

        // Area Between Curves
        areaGInput = findViewById(R.id.area_g_input);
        MaterialButton btnAreaBetween = findViewById(R.id.btn_area_between);
        btnAreaBetween.setOnClickListener(v -> onAreaBetweenCurves());

        // Nonlinear System Solver (2D)
        sysFInput = findViewById(R.id.sys_f_input);
        sysGInput = findViewById(R.id.sys_g_input);
        sysX0Input = findViewById(R.id.sys_x0_input);
        sysY0Input = findViewById(R.id.sys_y0_input);
        MaterialButton btnSolveSystem = findViewById(R.id.btn_solve_system);
        btnSolveSystem.setOnClickListener(v -> onSolveSystem2d());

        // Matrix Operations
        matrixAInput = findViewById(R.id.matrix_a_input);
        matrixBInput = findViewById(R.id.matrix_b_input);
        MaterialButton btnMatAdd = findViewById(R.id.btn_mat_add);
        MaterialButton btnMatSub = findViewById(R.id.btn_mat_sub);
        MaterialButton btnMatMul = findViewById(R.id.btn_mat_mul);
        MaterialButton btnMatDet = findViewById(R.id.btn_mat_det);
        MaterialButton btnMatInv = findViewById(R.id.btn_mat_inv);
        MaterialButton btnMatTrans = findViewById(R.id.btn_mat_trans);
        MaterialButton btnMatRank = findViewById(R.id.btn_mat_rank);
        MaterialButton btnMatEigen = findViewById(R.id.btn_mat_eigen);
        btnMatAdd.setOnClickListener(v -> onMatrixAdd());
        btnMatSub.setOnClickListener(v -> onMatrixSub());
        btnMatMul.setOnClickListener(v -> onMatrixMul());
        btnMatDet.setOnClickListener(v -> onMatrixDet());
        btnMatInv.setOnClickListener(v -> onMatrixInv());
        btnMatTrans.setOnClickListener(v -> onMatrixTranspose());
        btnMatRank.setOnClickListener(v -> onMatrixRank());
        btnMatEigen.setOnClickListener(v -> onMatrixEigen());

        // Number Theory Calculator
        EditText ntNInput = findViewById(R.id.nt_n_input);
        EditText ntAInput = findViewById(R.id.nt_a_input);
        EditText ntBInput = findViewById(R.id.nt_b_input);
        EditText ntModpowBaseInput = findViewById(R.id.nt_modpow_base_input);
        EditText ntModpowExpInput = findViewById(R.id.nt_modpow_exp_input);
        EditText ntModpowModInput = findViewById(R.id.nt_modpow_mod_input);
        MaterialButton btnNtFactorize = findViewById(R.id.btn_nt_factorize);
        MaterialButton btnNtIsPrime = findViewById(R.id.btn_nt_is_prime);
        MaterialButton btnNtGcd = findViewById(R.id.btn_nt_gcd);
        MaterialButton btnNtLcm = findViewById(R.id.btn_nt_lcm);
        MaterialButton btnNtFibonacci = findViewById(R.id.btn_nt_fibonacci);
        MaterialButton btnNtModPow = findViewById(R.id.btn_nt_mod_pow);
        MaterialButton btnNtTotient = findViewById(R.id.btn_nt_totient);
        btnNtFactorize.setOnClickListener(v -> onNtFactorize(ntNInput));
        btnNtIsPrime.setOnClickListener(v -> onNtIsPrime(ntNInput));
        btnNtGcd.setOnClickListener(v -> onNtGcd(ntAInput, ntBInput));
        btnNtLcm.setOnClickListener(v -> onNtLcm(ntAInput, ntBInput));
        btnNtFibonacci.setOnClickListener(v -> onNtFibonacci(ntNInput));
        btnNtModPow.setOnClickListener(v -> onNtModPow(ntModpowBaseInput, ntModpowExpInput, ntModpowModInput));
        btnNtTotient.setOnClickListener(v -> onNtTotient(ntNInput));

        // Parametric plotting
        MaterialButton btnPlotParametric = findViewById(R.id.btn_plot_parametric);
        Chip chipCircle = findViewById(R.id.chip_circle);
        Chip chipLissajous = findViewById(R.id.chip_lissajous);

        btnPlotParametric.setOnClickListener(v -> onPlotParametric());
        chipCircle.setOnClickListener(v -> {
            xParamInput.setText("cos(t)");
            yParamInput.setText("sin(t)");
            tMinInput.setText("0");
            tMaxInput.setText("6.2832");
        });
        chipLissajous.setOnClickListener(v -> {
            xParamInput.setText("sin(3*t)");
            yParamInput.setText("cos(2*t)");
            tMinInput.setText("0");
            tMaxInput.setText("6.2832");
        });

        // Polar plotting
        MaterialButton btnPlotPolar = findViewById(R.id.btn_plot_polar);
        Chip chipCardioid = findViewById(R.id.chip_cardioid);
        Chip chipClover = findViewById(R.id.chip_clover);

        btnPlotPolar.setOnClickListener(v -> onPlotPolar());
        chipCardioid.setOnClickListener(v -> {
            rPolarInput.setText("1+cos(theta)");
            thetaMinInput.setText("0");
            thetaMaxInput.setText("6.2832");
        });
        chipClover.setOnClickListener(v -> {
            rPolarInput.setText("sin(3*theta)");
            thetaMinInput.setText("0");
            thetaMaxInput.setText("6.2832");
        });

        // Preset chips — set expression text and auto-evaluate
        Chip chipSin = findViewById(R.id.chip_sin);
        Chip chipCos = findViewById(R.id.chip_cos);
        Chip chipX2  = findViewById(R.id.chip_x2);
        Chip chipExp = findViewById(R.id.chip_exp);
        Chip chip3D  = findViewById(R.id.chip_3d);

        chipSin.setOnClickListener(v -> { exprInput.setText("sin(x)"); onEvaluate(); });
        chipCos.setOnClickListener(v -> { exprInput.setText("cos(x)"); onEvaluate(); });
        chipX2 .setOnClickListener(v -> { exprInput.setText("x^2");     onEvaluate(); });
        chipExp.setOnClickListener(v -> { exprInput.setText("exp(-x)"); onEvaluate(); });
        chip3D .setOnClickListener(v -> { exprInput.setText("x^2+y^2"); });

        // Rounding & modulo chips
        Chip chipFloor = findViewById(R.id.chip_floor);
        Chip chipCeil  = findViewById(R.id.chip_ceil);
        Chip chipMod   = findViewById(R.id.chip_mod);

        chipFloor.setOnClickListener(v -> { exprInput.setText("floor(x)"); onEvaluate(); });
        chipCeil.setOnClickListener(v -> { exprInput.setText("ceil(x)"); onEvaluate(); });
        chipMod.setOnClickListener(v -> { exprInput.setText("x mod 3"); onEvaluate(); });

        // Unit Converter
        setupUnitConverter();

        // Base Converter
        setupBaseConverter();

        // Perpetual Calendar
        setupCalendar();

        // Statistical Distribution Calculator
        setupDistCalc();
    }

    private String getExpr()  { return exprInput.getText().toString().trim(); }
    private double getX()     { return parse(xInput); }
    private double getA()     { return parse(aInput); }
    private double getB()     { return parse(bInput); }
    private double getGuess() { return parse(guessInput); }

    private double parse(EditText e) {
        try { return Double.parseDouble(e.getText().toString().trim()); }
        catch (NumberFormatException ex) { return 0.0; }
    }

    private void appendResult(String label, double value) {
        String line = label + " = ";
        if (Double.isNaN(value)) {
            line += getString(R.string.result_error_prefix) + CalcEngine.getLastError();
        } else if (Double.isInfinite(value)) {
            line += (value > 0 ? "+Inf" : "-Inf");
        } else {
            line += String.format("%.10g", value);
        }
        resultView.append(line + "\n");
    }

    private void appendResult(String label, int value) {
        String line = label + " = " + String.format(getString(R.string.result_points_plotted), value);
        resultView.append(line + "\n");
    }

    private void onEvaluate() {
        String e = getExpr(); if (e.isEmpty()) { toast(getString(R.string.toast_enter_expr)); return; }
        appendResult(String.format(getString(R.string.result_fx), getX()), CalcEngine.evaluate(e, getX()));
    }

    private void onDerivative() {
        String e = getExpr(); if (e.isEmpty()) { toast(getString(R.string.toast_enter_expr)); return; }
        appendResult(String.format(getString(R.string.result_f_prime_x), getX()), CalcEngine.derivative(e, getX(), 1e-6));
    }

    private void onDerivative2() {
        String e = getExpr(); if (e.isEmpty()) { toast(getString(R.string.toast_enter_expr)); return; }
        appendResult(String.format(getString(R.string.result_f_double_prime_x), getX()), CalcEngine.derivative2(e, getX(), 1e-6));
    }

    private void onIntegrate() {
        String e = getExpr(); if (e.isEmpty()) { toast(getString(R.string.toast_enter_expr)); return; }
        appendResult(String.format(getString(R.string.result_integral), getA(), getB()),
                     CalcEngine.integrate(e, getA(), getB()));
    }

    private void onSolve() {
        String e = getExpr(); if (e.isEmpty()) { toast(getString(R.string.toast_enter_expr)); return; }
        double root = CalcEngine.solve(e, getGuess(), getA(), getB());
        if (Double.isNaN(root)) {
            appendResult("Root", Double.NaN);
        } else {
            resultView.append(String.format(getString(R.string.result_root), root) + "\n");
            resultView.append(String.format(getString(R.string.result_root_fval), CalcEngine.evaluate(e, root)) + "\n");
        }
    }

    private void onFindExtremum(boolean minimum) {
        String e = getExpr(); if (e.isEmpty()) { toast(getString(R.string.toast_enter_expr)); return; }
        double a = getA();
        double b = getB();
        double result;
        if (minimum) {
            result = CalcEngine.findMinimum(e, a, b);
        } else {
            result = CalcEngine.findMaximum(e, a, b);
        }
        if (Double.isNaN(result)) {
            appendResult(minimum ? "Min" : "Max", Double.NaN);
        } else {
            resultView.append(String.format(getString(minimum ? R.string.result_min : R.string.result_max), result, CalcEngine.evaluate(e, result)) + "\n");
        }
    }

    private void openPlot() {
        Intent intent = new Intent(this, PlotActivity.class);
        String expr = getExpr();
        if (!expr.isEmpty()) {
            intent.putExtra("initial_expr", expr);
            intent.putExtra("x_min", getA());
            intent.putExtra("x_max", getB());
        }
        startActivity(intent);
    }

    private void onScanRoots() {
        String e = getExpr();
        if (e.isEmpty()) { toast(getString(R.string.toast_enter_expr)); return; }
        double a = getA();
        double b = getB();
        if (a >= b) { toast(getString(R.string.toast_a_less_b)); return; }

        int nSamples = 2000;
        double tolZero = 1e-6;
        double tolDup = 1e-4;
        double[] xs = new double[nSamples];
        double step = (b - a) / (nSamples - 1);
        for (int i = 0; i < nSamples; i++) {
            xs[i] = a + i * step;
        }
        double[] ys = CalcEngine.evaluateArray(e, xs);
        if (ys == null) {
            resultView.append(String.format(getString(R.string.scan_roots_error), CalcEngine.getLastError()) + "\n");
            return;
        }

        java.util.ArrayList<Double> roots = new java.util.ArrayList<>();
        for (int i = 0; i < nSamples; i++) {
            if (!Double.isNaN(ys[i]) && !Double.isInfinite(ys[i]) && Math.abs(ys[i]) < tolZero) {
                roots.add(xs[i]);
            }
        }
        for (int i = 0; i < nSamples - 1; i++) {
            if (Double.isNaN(ys[i]) || Double.isNaN(ys[i + 1])) continue;
            if (ys[i] == 0.0 || ys[i + 1] == 0.0) continue;
            if (ys[i] * ys[i + 1] < 0) {
                double root = CalcEngine.solveBisection(e, xs[i], xs[i + 1]);
                if (!Double.isNaN(root)) {
                    roots.add(root);
                }
            }
        }

        java.util.Collections.sort(roots);
        java.util.ArrayList<Double> uniqueRoots = new java.util.ArrayList<>();
        for (Double r : roots) {
            if (uniqueRoots.isEmpty() || Math.abs(r - uniqueRoots.get(uniqueRoots.size() - 1)) > tolDup) {
                uniqueRoots.add(r);
            }
        }

        if (uniqueRoots.isEmpty()) {
            resultView.append(String.format(getString(R.string.scan_roots_no_roots), a, b) + "\n");
        } else {
            resultView.append(String.format(getString(R.string.scan_roots_found), uniqueRoots.size(), a, b) + "\n");
            int limit = Math.min(uniqueRoots.size(), 20);
            for (int i = 0; i < limit; i++) {
                double r = uniqueRoots.get(i);
                double verify = CalcEngine.evaluate(e, r);
                String vStr = Double.isNaN(verify) ? "N/A" : String.format("%.2e", verify);
                resultView.append("  x" + (i + 1) + " = " + fmt(r) + "  (f=" + vStr + ")\n");
            }
            if (uniqueRoots.size() > 20) {
                resultView.append("  ... and " + (uniqueRoots.size() - 20) + " more\n");
            }
        }
    }

    private void openPlot3D() {
        Intent intent = new Intent(this, Plot3DActivity.class);
        String expr = getExpr();
        if (!expr.isEmpty()) {
            intent.putExtra("initial_expr", expr);
        }
        startActivity(intent);
    }

    private void onTangentNormal(boolean tangent) {
        String e = getExpr();
        if (e.isEmpty()) { toast(getString(R.string.toast_enter_expr)); return; }
        double x0 = getX();
        double y0 = CalcEngine.evaluate(e, x0);
        double slope = CalcEngine.derivative(e, x0, 1e-6);
        if (Double.isNaN(y0) || Double.isNaN(slope)) {
            resultView.append(String.format(getString(tangent ? R.string.tangent_error : R.string.normal_error), CalcEngine.getLastError()) + "\n");
            return;
        }
        if (tangent) {
            resultView.append(String.format(getString(R.string.tangent_label), x0, slope, x0, y0) + "\n");
        } else {
            if (Math.abs(slope) < 1e-12) {
                resultView.append("Normal: vertical line x = " + fmt(x0) + "\n");
            } else {
                double ns = -1.0 / slope;
                resultView.append(String.format(getString(R.string.normal_label), x0, ns, x0, y0) + "\n");
            }
        }
    }

    private void onArcLength() {
        String e = getExpr();
        if (e.isEmpty()) { toast(getString(R.string.toast_enter_expr)); return; }
        double a = getA();
        double b = getB();
        if (a >= b) { toast(getString(R.string.toast_a_less_b)); return; }

        int n = 5000;
        double h = (b - a) / n;
        double[] xs = new double[n + 1];
        for (int i = 0; i <= n; i++) {
            xs[i] = a + i * h;
        }
        double[] ys = CalcEngine.evaluateArray(e, xs);
        if (ys == null) {
            resultView.append(String.format(getString(R.string.arc_length_error), CalcEngine.getLastError()) + "\n");
            return;
        }
        double length = 0.0;
        for (int i = 0; i < n; i++) {
            double y1 = ys[i];
            double y2 = ys[i + 1];
            if (Double.isNaN(y1) || Double.isNaN(y2)) {
                continue;
            }
            double dx = h;
            double dy = y2 - y1;
            length += Math.sqrt(dx * dx + dy * dy);
        }
        resultView.append(String.format(getString(R.string.arc_length_result), a, b, length) + "\n");
    }

    private void onAreaBetweenCurves() {
        String eF = getExpr();
        String eG = areaGInput.getText().toString().trim();
        if (eF.isEmpty()) { toast(getString(R.string.toast_enter_fx)); return; }
        if (eG.isEmpty()) { toast(getString(R.string.toast_enter_gx)); return; }
        double a = getA();
        double b = getB();
        if (a >= b) { toast(getString(R.string.toast_a_less_b)); return; }

        double result = CalcEngine.areaBetweenCurves(eF, eG, a, b);
        if (Double.isNaN(result)) {
            String err = CalcEngine.getLastError();
            resultView.append(String.format(getString(R.string.area_between_error), (err.isEmpty() ? "computation failed" : err)) + "\n");
            return;
        }
        resultView.append(String.format(getString(R.string.area_between_result), a, b, a, b, result) + "\n");
    }

    @SuppressWarnings("unchecked")
    private void onSolveSystem2d() {
        String fExpr = sysFInput.getText().toString().trim();
        String gExpr = sysGInput.getText().toString().trim();
        if (fExpr.isEmpty() || gExpr.isEmpty()) {
            toast(getString(R.string.toast_enter_fg));
            return;
        }
        double x0, y0;
        try {
            x0 = Double.parseDouble(sysX0Input.getText().toString().trim());
            y0 = Double.parseDouble(sysY0Input.getText().toString().trim());
        } catch (NumberFormatException ex) {
            toast(getString(R.string.toast_invalid_guess));
            return;
        }

        HashMap<String, Object> result = CalcEngine.solveSystem2d(fExpr, gExpr, x0, y0);
        if (result == null) {
            String err = CalcEngine.getLastError();
            resultView.append(String.format(getString(R.string.system_solver_error), (err.isEmpty() ? "computation failed" : err)) + "\n");
            return;
        }

        Object xObj = result.get("x");
        Object yObj = result.get("y");
        if (xObj == null || yObj == null) {
            resultView.append(getString(R.string.system_solver_invalid) + "\n");
            return;
        }

        double xSol = (double) xObj;
        double ySol = (double) yObj;
        double fVal = CalcEngine.evaluateXY(fExpr, xSol, ySol);
        double gVal = CalcEngine.evaluateXY(gExpr, xSol, ySol);

        StringBuilder sb = new StringBuilder();
        sb.append("f(x,y) = ").append(fExpr).append("\n");
        sb.append("g(x,y) = ").append(gExpr).append("\n\n");
        sb.append(getString(R.string.system_solution_label));
        sb.append("  x = ").append(fmt(xSol)).append("\n");
        sb.append("  y = ").append(fmt(ySol)).append("\n\n");
        sb.append(getString(R.string.system_residuals_label));
        sb.append("  f(x,y) = ").append(Double.isNaN(fVal) ? "N/A" : String.format("%.2e", fVal)).append("\n");
        sb.append("  g(x,y) = ").append(Double.isNaN(gVal) ? "N/A" : String.format("%.2e", gVal)).append("\n");

        android.widget.TextView tv = new android.widget.TextView(this);
        tv.setText(sb.toString());
        tv.setTypeface(android.graphics.Typeface.MONOSPACE);
        tv.setTextSize(13);
        tv.setPadding(40, 24, 40, 24);
        tv.setTextColor(android.graphics.Color.parseColor("#cdd6f4"));
        tv.setBackgroundColor(android.graphics.Color.parseColor("#181825"));

        android.widget.ScrollView sv = new android.widget.ScrollView(this);
        sv.addView(tv);

        new androidx.appcompat.app.AlertDialog.Builder(this, androidx.appcompat.R.style.ThemeOverlay_AppCompat_Dialog_Alert)
            .setTitle(getString(R.string.dialog_system_solution))
            .setView(sv)
            .setPositiveButton(getString(R.string.dialog_close), null)
            .show();

        resultView.append(String.format(getString(R.string.system_solved_toast), xSol, ySol) + "\n");
    }

    private void onFFT() {
        String e = getExpr();
        if (e.isEmpty()) { toast(getString(R.string.toast_enter_expr)); return; }
        double a = getA();
        double b = getB();
        if (a >= b) { toast(getString(R.string.toast_a_less_b)); return; }
        int n = 256; // default samples for DFT
        double step = (b - a) / n;
        double[] xs = new double[n];
        double[] ys = new double[n];
        for (int i = 0; i < n; i++) {
            xs[i] = a + i * step;
            double val = CalcEngine.evaluate(e, xs[i]);
            ys[i] = Double.isNaN(val) ? 0.0 : val;
        }
        // Remove DC offset
        double mean = 0.0;
        for (double v : ys) mean += v;
        mean /= n;
        for (int i = 0; i < n; i++) ys[i] -= mean;

        int m = n / 2 + 1;
        double[] amps = new double[m];
        double[] phases = new double[m];
        double[] freqs = new double[m];
        double df = 1.0 / (b - a); // frequency resolution
        for (int k = 0; k < m; k++) {
            double real = 0.0, imag = 0.0;
            for (int i = 0; i < n; i++) {
                double angle = -2.0 * Math.PI * k * i / n;
                real += ys[i] * Math.cos(angle);
                imag += ys[i] * Math.sin(angle);
            }
            double amp = (2.0 / n) * Math.sqrt(real * real + imag * imag);
            if (k == 0) amp /= 2.0;
            amps[k] = amp;
            phases[k] = Math.atan2(imag, real);
            freqs[k] = k * df;
        }

        // Find dominant frequency
        int peakIdx = 1;
        for (int i = 2; i < m; i++) {
            if (amps[i] > amps[peakIdx]) peakIdx = i;
        }

        StringBuilder sb = new StringBuilder();
        sb.append("DFT Spectrum (").append(n).append(" samples)\n");
        sb.append(String.format(getString(R.string.fft_dominant_freq), freqs[peakIdx]))
          .append(" A=").append(fmt(amps[peakIdx])).append("\n\n");
        int show = Math.min(m, 16);
        sb.append(getString(R.string.fft_header)).append("\n");
        sb.append("--------------------------------\n");
        for (int i = 0; i < show; i++) {
            sb.append(fmt(freqs[i])).append("\t")
              .append(fmt(amps[i])).append("\t")
              .append(fmt(phases[i])).append("\n");
        }
        if (m > show) sb.append("... and ").append(m - show).append(" more bins\n");

        android.widget.TextView tv = new android.widget.TextView(this);
        tv.setText(sb.toString());
        tv.setTypeface(android.graphics.Typeface.MONOSPACE);
        tv.setTextSize(13);
        tv.setPadding(40, 24, 40, 24);
        tv.setTextColor(android.graphics.Color.parseColor("#cdd6f4"));
        tv.setBackgroundColor(android.graphics.Color.parseColor("#181825"));

        android.widget.ScrollView sv = new android.widget.ScrollView(this);
        sv.addView(tv);

        new androidx.appcompat.app.AlertDialog.Builder(this, androidx.appcompat.R.style.ThemeOverlay_AppCompat_Dialog_Alert)
            .setTitle(getString(R.string.dialog_fft_spectrum))
            .setView(sv)
            .setPositiveButton(getString(R.string.dialog_close), null)
            .show();

        resultView.append(String.format(getString(R.string.fft_dominant_freq), freqs[peakIdx]) + " A=" + fmt(amps[peakIdx]) + "\n");
    }

    private void onLimit() {
        String e = getExpr();
        if (e.isEmpty()) { toast(getString(R.string.toast_enter_expr)); return; }
        double a = getX();

        double left  = CalcEngine.limitLeft(e, a);
        double right = CalcEngine.limitRight(e, a);

        if (Double.isNaN(left) && Double.isNaN(right)) {
            resultView.append("lim(x→" + fmt(a) + "): Error: " + CalcEngine.getLastError() + "\n");
            return;
        }

        if (!Double.isNaN(left) && !Double.isNaN(right) && Math.abs(left - right) < 1e-8) {
            double val = (left + right) / 2.0;
            resultView.append(String.format(getString(R.string.limit_result), a, val) + "\n");
            resultView.append("  Left:  " + fmt(left) + "\n");
            resultView.append("  Right: " + fmt(right) + "\n");
        } else {
            if (!Double.isNaN(left) && !Double.isNaN(right)) {
                resultView.append(String.format(getString(R.string.limit_two_sided_not_exist), left, right) + "\n");
            } else {
                if (!Double.isNaN(left)) {
                    resultView.append("lim(x→" + fmt(a) + "⁻) = " + fmt(left) + "\n");
                } else {
                    resultView.append("lim(x→" + fmt(a) + "⁻) = DNE\n");
                }
                if (!Double.isNaN(right)) {
                    resultView.append("lim(x→" + fmt(a) + "⁺) = " + fmt(right) + "\n");
                } else {
                    resultView.append("lim(x→" + fmt(a) + "⁺) = DNE\n");
                }
                resultView.append(getString(R.string.limit_two_sided_not_exist) + "\n");
            }
        }
    }

    private void onLimitSide(boolean left) {
        String e = getExpr();
        if (e.isEmpty()) { toast(getString(R.string.toast_enter_expr)); return; }
        double a = getX();
        double result;
        String label;
        if (left) {
            result = CalcEngine.limitLeft(e, a);
            label = "lim(x→" + fmt(a) + "⁻)";
        } else {
            result = CalcEngine.limitRight(e, a);
            label = "lim(x→" + fmt(a) + "⁺)";
        }
        if (Double.isNaN(result)) {
            resultView.append(label + ": Error: " + CalcEngine.getLastError() + "\n");
        } else {
            resultView.append(label + " = " + fmt(result) + "\n");
        }
    }

    private int getTaylorOrder() {
        try {
            int order = Integer.parseInt(taylorOrderInput.getText().toString().trim());
            if (order < 1) return 5;
            if (order > 20) return 20;
            return order;
        } catch (NumberFormatException e) {
            return 5;
        }
    }

    private void onTaylor() {
        String e = getExpr();
        if (e.isEmpty()) { toast(getString(R.string.toast_enter_expr)); return; }
        double a = getX();
        int order = getTaylorOrder();

        double[] coeffs = CalcEngine.taylorCoefficients(e, a, order);
        if (coeffs == null) {
            resultView.append(String.format(getString(R.string.taylor_error), CalcEngine.getLastError()) + "\n");
            return;
        }

        StringBuilder sb = new StringBuilder();
        sb.append("Taylor series at a=").append(fmt(a)).append(" (order ").append(order).append(")\n\n");

        // Build human-readable Taylor polynomial
        for (int k = 0; k < coeffs.length; k++) {
            if (Double.isNaN(coeffs[k])) continue;
            double c = coeffs[k];
            if (Math.abs(c) < 1e-15) continue;

            String cStr = fmt(c);
            if (k == 0) {
                sb.append(cStr);
            } else if (k == 1) {
                sb.append(" + ").append(cStr).append("*(x-").append(fmt(a)).append(")");
            } else {
                sb.append(" + ").append(cStr).append("*(x-").append(fmt(a)).append(")^").append(k);
            }
        }
        sb.append("\n\nCoefficients (c_k = f^(k)(a)/k!):\n");
        for (int k = 0; k < coeffs.length; k++) {
            sb.append("c").append(k).append(" = ").append(fmt(coeffs[k])).append("\n");
        }

        // Show in dialog
        android.widget.TextView tv = new android.widget.TextView(this);
        tv.setText(sb.toString());
        tv.setTypeface(android.graphics.Typeface.MONOSPACE);
        tv.setTextSize(13);
        tv.setPadding(40, 24, 40, 24);
        tv.setTextColor(android.graphics.Color.parseColor("#cdd6f4"));
        tv.setBackgroundColor(android.graphics.Color.parseColor("#181825"));

        android.widget.ScrollView sv = new android.widget.ScrollView(this);
        sv.addView(tv);

        new androidx.appcompat.app.AlertDialog.Builder(this, androidx.appcompat.R.style.ThemeOverlay_AppCompat_Dialog_Alert)
            .setTitle(getString(R.string.dialog_taylor_series))
            .setView(sv)
            .setPositiveButton(getString(R.string.dialog_close), null)
            .show();

        resultView.append(String.format(getString(R.string.taylor_toast), a, order) + "\n");
    }

    private void onOdeSolve() {
        String expr = odeExprInput.getText().toString().trim();
        if (expr.isEmpty()) { toast(getString(R.string.toast_enter_ode)); return; }
        double x0, y0, xEnd;
        int steps;
        try {
            x0 = Double.parseDouble(odeX0Input.getText().toString().trim());
            y0 = Double.parseDouble(odeY0Input.getText().toString().trim());
            xEnd = Double.parseDouble(odeXEndInput.getText().toString().trim());
            steps = Integer.parseInt(odeStepsInput.getText().toString().trim());
        } catch (NumberFormatException ex) {
            toast(getString(R.string.toast_invalid_ode));
            return;
        }
        if (steps < 1 || steps > 100000) { toast(getString(R.string.toast_steps_range)); return; }
        if (x0 == xEnd) { toast(getString(R.string.toast_x0_xend)); return; }

        HashMap<String, Object> result = CalcEngine.odeSolveRk4(expr, x0, y0, xEnd, steps);
        if (result == null) {
            resultView.append(String.format(getString(R.string.ode_error), CalcEngine.getLastError()) + "\n");
            return;
        }

        Object xsObj = result.get("xs");
        Object ysObj = result.get("ys");
        Object countObj = result.get("count");
        if (xsObj == null || ysObj == null || countObj == null) {
            resultView.append(getString(R.string.ode_error_invalid) + "\n");
            return;
        }
        
        double[] xs = (double[]) xsObj;
        double[] ys = (double[]) ysObj;
        int count = (int) countObj;

        StringBuilder sb = new StringBuilder();
        sb.append("dy/dx = ").append(expr).append(", y(").append(fmt(x0)).append(") = ").append(fmt(y0)).append("\n");
        sb.append("Solved over [").append(fmt(x0)).append(", ").append(fmt(xEnd)).append("] with ").append(steps).append(" steps (RK4)\n\n");
        sb.append(String.format("%14s  %14s\n", "x", "y(x)"));
        sb.append("--------------------------------\n");
        int show = Math.min(count, 30);
        int step = count > show ? count / show : 1;
        for (int i = 0; i < count; i += step) {
            String yStr = Double.isNaN(ys[i]) ? "N/A" : fmt(ys[i]);
            sb.append(String.format("%14s  %14s\n", fmt(xs[i]), yStr));
        }
        if (count > show) sb.append("  ... (").append(count).append(" total points)\n");

        android.widget.TextView tv = new android.widget.TextView(this);
        tv.setText(sb.toString());
        tv.setTypeface(android.graphics.Typeface.MONOSPACE);
        tv.setTextSize(13);
        tv.setPadding(40, 24, 40, 24);
        tv.setTextColor(android.graphics.Color.parseColor("#cdd6f4"));
        tv.setBackgroundColor(android.graphics.Color.parseColor("#181825"));

        android.widget.ScrollView sv = new android.widget.ScrollView(this);
        sv.addView(tv);

        new androidx.appcompat.app.AlertDialog.Builder(this, androidx.appcompat.R.style.ThemeOverlay_AppCompat_Dialog_Alert)
            .setTitle(getString(R.string.dialog_ode_solution))
            .setView(sv)
            .setPositiveButton(getString(R.string.dialog_close), null)
            .show();

        resultView.append(String.format(getString(R.string.ode_toast), count) + "\n");
    }

    private void onOdePlot() {
        String expr = odeExprInput.getText().toString().trim();
        if (expr.isEmpty()) { toast(getString(R.string.toast_enter_ode)); return; }
        double x0, y0, xEnd;
        int steps;
        try {
            x0 = Double.parseDouble(odeX0Input.getText().toString().trim());
            y0 = Double.parseDouble(odeY0Input.getText().toString().trim());
            xEnd = Double.parseDouble(odeXEndInput.getText().toString().trim());
            steps = Integer.parseInt(odeStepsInput.getText().toString().trim());
        } catch (NumberFormatException ex) {
            toast(getString(R.string.toast_invalid_ode));
            return;
        }
        if (steps < 1 || steps > 100000) { toast(getString(R.string.toast_steps_range)); return; }
        if (x0 == xEnd) { toast(getString(R.string.toast_x0_xend)); return; }

        HashMap<String, Object> result = CalcEngine.odeSolveRk4(expr, x0, y0, xEnd, steps);
        if (result == null) {
            resultView.append(String.format(getString(R.string.ode_error), CalcEngine.getLastError()) + "\n");
            return;
        }

        Object xsObj = result.get("xs");
        Object ysObj = result.get("ys");
        if (xsObj == null || ysObj == null) {
            resultView.append(getString(R.string.ode_error_invalid) + "\n");
            return;
        }

        double[] xsFull = (double[]) xsObj;
        double[] ysFull = (double[]) ysObj;

        // Downsample to avoid TransactionTooLargeException (~1MB Intent limit)
        int maxPoints = 2000;
        double[] xs, ys;
        if (xsFull.length > maxPoints) {
            int step = Math.max(1, xsFull.length / maxPoints);
            int arraySize = (xsFull.length + step - 1) / step + 1;
            xs = new double[arraySize];
            ys = new double[arraySize];
            int idx = 0;
            for (int i = 0; i < xsFull.length && idx < xs.length; i += step) {
                xs[idx] = xsFull[i];
                ys[idx] = ysFull[i];
                idx++;
            }
            // Always include the last point
            if ((xsFull.length - 1) % step != 0 && idx < xs.length) {
                xs[idx] = xsFull[xsFull.length - 1];
                ys[idx] = ysFull[ysFull.length - 1];
                idx++;
            }
            xs = java.util.Arrays.copyOf(xs, idx);
            ys = java.util.Arrays.copyOf(ys, idx);
        } else {
            xs = xsFull;
            ys = ysFull;
        }

        Intent intent = new Intent(this, PlotActivity.class);
        intent.putExtra("is_ode", true);
        intent.putExtra("ode_xs", xs);
        intent.putExtra("ode_ys", ys);
        intent.putExtra("ode_expr", expr);
        intent.putExtra("x_min", x0);
        intent.putExtra("x_max", xEnd);
        startActivity(intent);
    }

    private void onTaylorPlot() {
        String e = getExpr();
        if (e.isEmpty()) { toast(getString(R.string.toast_enter_expr)); return; }
        double a = getX();
        int order = getTaylorOrder();

        double rangeA = getA();
        double rangeB = getB();
        if (rangeA >= rangeB) { toast(getString(R.string.toast_set_ab)); return; }

        // Precompute Taylor coefficients once (avoids O(n*order) redundant derivative calls)
        double[] coeffs = new double[order + 1];
        double factorial = 1.0;
        for (int k = 0; k <= order; k++) {
            if (k > 0) factorial *= k;
            double dk = CalcEngine.nthDerivative(e, a, k, 1e-5);
            coeffs[k] = Double.isNaN(dk) ? 0.0 : dk / factorial;
        }

        int n = 500;
        double step = (rangeB - rangeA) / (n - 1);
        double[] xs = new double[n];
        double[] ysOrig = new double[n];
        double[] ysTaylor = new double[n];

        for (int i = 0; i < n; i++) {
            xs[i] = rangeA + i * step;
            double yOrig = CalcEngine.evaluate(e, xs[i]);
            ysOrig[i] = Double.isNaN(yOrig) ? 0.0 : yOrig;

            double dx = xs[i] - a;
            double taylorVal = 0.0;
            double dxPower = 1.0;
            for (int k = 0; k <= order; k++) {
                taylorVal += coeffs[k] * dxPower;
                dxPower *= dx;
            }
            ysTaylor[i] = taylorVal;
        }

        Intent intent = new Intent(this, PlotActivity.class);
        intent.putExtra("is_taylor", true);
        intent.putExtra("taylor_expr", e);
        intent.putExtra("taylor_a", a);
        intent.putExtra("taylor_order", order);
        intent.putExtra("taylor_xs", xs);
        intent.putExtra("taylor_ys_orig", ysOrig);
        intent.putExtra("taylor_ys_taylor", ysTaylor);
        intent.putExtra("x_min", rangeA);
        intent.putExtra("x_max", rangeB);
        startActivity(intent);
    }

    private double[] parseStatsData() {
        String raw = statsDataInput.getText().toString().trim();
        if (raw.isEmpty()) { toast(getString(R.string.toast_enter_data)); return null; }
        String[] tokens = raw.split("[,;\\s]+");
        java.util.ArrayList<Double> values = new java.util.ArrayList<>();
        for (String t : tokens) {
            t = t.trim();
            if (t.isEmpty()) continue;
            try {
                values.add(Double.parseDouble(t));
            } catch (NumberFormatException e) {
                toast(getString(R.string.toast_invalid_num, t));
                return null;
            }
        }
        if (values.isEmpty()) { toast(getString(R.string.toast_no_valid_nums)); return null; }
        double[] result = new double[values.size()];
        for (int i = 0; i < values.size(); i++) result[i] = values.get(i);
        return result;
    }

    private void onStatsCompute() {
        double[] data = parseStatsData();
        if (data == null) return;
        int n = data.length;

        double sum = 0;
        for (double v : data) sum += v;
        double mean = sum / n;

        java.util.Arrays.sort(data);
        double median;
        if (n % 2 == 0) {
            median = (data[n / 2 - 1] + data[n / 2]) / 2.0;
        } else {
            median = data[n / 2];
        }

        double min = data[0];
        double max = data[n - 1];
        double range = max - min;

        // Population variance & std
        double varPop = 0;
        for (double v : data) varPop += (v - mean) * (v - mean);
        varPop /= n;
        double stdPop = Math.sqrt(varPop);

        // Sample variance & std
        double varSam = 0;
        if (n > 1) {
            for (double v : data) varSam += (v - mean) * (v - mean);
            varSam /= (n - 1);
        }
        double stdSam = Math.sqrt(varSam);

        // Quartiles
        double q1 = data[n / 4];
        double q3 = data[Math.min(3 * n / 4, n - 1)];
        double iqr = q3 - q1;

        StringBuilder sb = new StringBuilder();
        sb.append(String.format(getString(R.string.stats_header), n)).append("\n\n");
        sb.append(String.format(getString(R.string.stats_sum), sum)).append("\n");
        sb.append(String.format(getString(R.string.stats_mean), mean)).append("\n");
        sb.append(String.format(getString(R.string.stats_median), median)).append("\n");
        sb.append(String.format(getString(R.string.stats_min), min)).append("\n");
        sb.append(String.format(getString(R.string.stats_max), max)).append("\n");
        sb.append(String.format(getString(R.string.stats_range), range)).append("\n");
        sb.append(String.format("  Q1 (25%%)  = %.10g\n", q1));
        sb.append(String.format("  Q3 (75%%)  = %.10g\n", q3));
        sb.append(String.format("  IQR       = %.10g\n", iqr));
        sb.append(String.format("  Var (pop) = %.10g\n", varPop));
        if (n > 1) sb.append(String.format("  Var (sam) = %.10g\n", varSam));
        sb.append(String.format("  Std (pop) = %.10g\n", stdPop));
        if (n > 1) sb.append(String.format("  Std (sam) = %.10g\n", stdSam));
        sb.append("\nSorted: ");
        int show = Math.min(n, 20);
        for (int i = 0; i < show; i++) {
            if (i > 0) sb.append(", ");
            sb.append(fmt(data[i]));
        }
        if (n > show) sb.append(" ... (").append(n).append(" total)");

        android.widget.TextView tv = new android.widget.TextView(this);
        tv.setText(sb.toString());
        tv.setTypeface(android.graphics.Typeface.MONOSPACE);
        tv.setTextSize(13);
        tv.setPadding(40, 24, 40, 24);
        tv.setTextColor(android.graphics.Color.parseColor("#cdd6f4"));
        tv.setBackgroundColor(android.graphics.Color.parseColor("#181825"));

        android.widget.ScrollView sv = new android.widget.ScrollView(this);
        sv.addView(tv);

        new androidx.appcompat.app.AlertDialog.Builder(this, androidx.appcompat.R.style.ThemeOverlay_AppCompat_Dialog_Alert)
            .setTitle(getString(R.string.dialog_statistics))
            .setView(sv)
            .setPositiveButton(getString(R.string.dialog_close), null)
            .show();

        resultView.append(String.format(getString(R.string.stats_toast), n, mean, stdPop) + "\n");
    }

    private void onStatsSort() {
        double[] data = parseStatsData();
        if (data == null) return;
        java.util.Arrays.sort(data);
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < data.length; i++) {
            if (i > 0) sb.append(", ");
            sb.append(fmt(data[i]));
        }
        statsDataInput.setText(sb.toString());
        toast(getString(R.string.toast_data_sorted, data.length));
    }

    // --- Matrix Operations ---

    private double[][] parseMatrix(String text) {
        text = text.trim();
        if (text.isEmpty()) return null;
        String[] rows = text.split(";");
        java.util.ArrayList<double[]> matrix = new java.util.ArrayList<>();
        int ncols = -1;
        for (String row : rows) {
            row = row.trim();
            if (row.isEmpty()) continue;
            String[] cols = row.split(",");
            java.util.ArrayList<Double> vals = new java.util.ArrayList<>();
            for (String c : cols) {
                c = c.trim();
                if (c.isEmpty()) continue;
                try {
                    vals.add(Double.parseDouble(c));
                } catch (NumberFormatException e) {
                    toast(getString(R.string.toast_invalid_num_matrix, c));
                    return null;
                }
            }
            if (vals.isEmpty()) continue;
            if (ncols < 0) ncols = vals.size();
            else if (vals.size() != ncols) {
                toast(getString(R.string.toast_cols_match));
                return null;
            }
            double[] rowArr = new double[vals.size()];
            for (int i = 0; i < vals.size(); i++) rowArr[i] = vals.get(i);
            matrix.add(rowArr);
        }
        if (matrix.isEmpty()) return null;
        return matrix.toArray(new double[0][]);
    }

    private String formatMatrix(double[][] mat) {
        StringBuilder sb = new StringBuilder();
        for (double[] row : mat) {
            sb.append("  ");
            for (int j = 0; j < row.length; j++) {
                if (j > 0) sb.append("  ");
                sb.append(String.format("%12.6g", row[j]));
            }
            sb.append("\n");
        }
        return sb.toString();
    }

    private void showMatrixResult(String title, String content) {
        android.widget.TextView tv = new android.widget.TextView(this);
        tv.setText(content);
        tv.setTypeface(android.graphics.Typeface.MONOSPACE);
        tv.setTextSize(13);
        tv.setPadding(40, 24, 40, 24);
        tv.setTextColor(android.graphics.Color.parseColor("#cdd6f4"));
        tv.setBackgroundColor(android.graphics.Color.parseColor("#181825"));
        android.widget.ScrollView sv = new android.widget.ScrollView(this);
        sv.addView(tv);
        new androidx.appcompat.app.AlertDialog.Builder(this, androidx.appcompat.R.style.ThemeOverlay_AppCompat_Dialog_Alert)
            .setTitle(title)
            .setView(sv)
            .setPositiveButton(getString(R.string.dialog_close), null)
            .show();
    }

    private double[][] getMatrixA() {
        return parseMatrix(matrixAInput.getText().toString());
    }

    private double[][] getMatrixB() {
        return parseMatrix(matrixBInput.getText().toString());
    }

    private void onMatrixAdd() {
        double[][] a = getMatrixA(); double[][] b = getMatrixB();
        if (a == null || b == null) return;
        if (a.length == 0 || b.length == 0) return;
        if (a.length != b.length || a[0].length != b[0].length) { toast(getString(R.string.toast_dims_match)); return; }
        double[][] r = new double[a.length][a[0].length];
        for (int i = 0; i < a.length; i++)
            for (int j = 0; j < a[0].length; j++)
                r[i][j] = a[i][j] + b[i][j];
        showMatrixResult("A + B", formatMatrix(r));
        resultView.append(getString(R.string.mat_add_result) + "\n");
    }

    private void onMatrixSub() {
        double[][] a = getMatrixA(); double[][] b = getMatrixB();
        if (a == null || b == null) return;
        if (a.length == 0 || b.length == 0) return;
        if (a.length != b.length || a[0].length != b[0].length) { toast(getString(R.string.toast_dims_match)); return; }
        double[][] r = new double[a.length][a[0].length];
        for (int i = 0; i < a.length; i++)
            for (int j = 0; j < a[0].length; j++)
                r[i][j] = a[i][j] - b[i][j];
        showMatrixResult("A - B", formatMatrix(r));
        resultView.append(getString(R.string.mat_sub_result) + "\n");
    }

    private void onMatrixMul() {
        double[][] a = getMatrixA(); double[][] b = getMatrixB();
        if (a == null || b == null) return;
        if (a.length == 0 || b.length == 0) return;
        if (a[0].length != b.length) { toast(getString(R.string.toast_cols_rows)); return; }
        double[][] r = new double[a.length][b[0].length];
        for (int i = 0; i < a.length; i++)
            for (int j = 0; j < b[0].length; j++) {
                double sum = 0;
                for (int k = 0; k < a[0].length; k++) sum += a[i][k] * b[k][j];
                r[i][j] = sum;
            }
        showMatrixResult("A * B", formatMatrix(r));
        resultView.append(getString(R.string.mat_mul_result) + "\n");
    }

    private void onMatrixDet() {
        double[][] a = getMatrixA();
        if (a == null) return;
        if (a.length == 0) return;
        if (a.length != a[0].length) { toast(getString(R.string.toast_det_square)); return; }
        double det = det(a);
        showMatrixResult("det(A)", "det(A) = " + fmt(det));
        resultView.append("det(A) = " + fmt(det) + "\n");
    }

    private double det(double[][] m) {
        int n = m.length;
        if (n == 1) return m[0][0];
        if (n == 2) return m[0][0]*m[1][1] - m[0][1]*m[1][0];
        double d = 0;
        for (int j = 0; j < n; j++) {
            double[][] sub = new double[n-1][n-1];
            for (int i = 1; i < n; i++) {
                int col = 0;
                for (int k = 0; k < n; k++) {
                    if (k == j) continue;
                    sub[i-1][col++] = m[i][k];
                }
            }
            d += Math.pow(-1, j) * m[0][j] * det(sub);
        }
        return d;
    }

    private void onMatrixInv() {
        double[][] a = getMatrixA();
        if (a == null) return;
        if (a.length != a[0].length) { toast(getString(R.string.toast_inv_square)); return; }
        int n = a.length;
        // Use Gauss-Jordan elimination with partial pivoting for better accuracy
        double[][] aug = new double[n][2 * n];
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                aug[i][j] = a[i][j];
                aug[i][n + j] = (i == j) ? 1.0 : 0.0;
            }
        }
        for (int col = 0; col < n; col++) {
            // Find pivot
            int maxRow = col;
            double maxVal = Math.abs(aug[col][col]);
            for (int row = col + 1; row < n; row++) {
                if (Math.abs(aug[row][col]) > maxVal) {
                    maxVal = Math.abs(aug[row][col]);
                    maxRow = row;
                }
            }
            if (maxVal < 1e-12) { toast(getString(R.string.toast_singular)); return; }
            // Swap rows
            double[] tmp = aug[col]; aug[col] = aug[maxRow]; aug[maxRow] = tmp;
            // Scale pivot row
            double piv = aug[col][col];
            for (int j = 0; j < 2 * n; j++) aug[col][j] /= piv;
            // Eliminate column
            for (int row = 0; row < n; row++) {
                if (row == col) continue;
                double factor = aug[row][col];
                for (int j = 0; j < 2 * n; j++) aug[row][j] -= factor * aug[col][j];
            }
        }
        double[][] inv = new double[n][n];
        for (int i = 0; i < n; i++)
            for (int j = 0; j < n; j++)
                inv[i][j] = aug[i][n + j];
        showMatrixResult("inv(A)", formatMatrix(inv));
        resultView.append(getString(R.string.mat_inv_result) + "\n");
    }

    private void onMatrixTranspose() {
        double[][] a = getMatrixA();
        if (a == null) return;
        int m = a.length, n = a[0].length;
        double[][] t = new double[n][m];
        for (int i = 0; i < m; i++)
            for (int j = 0; j < n; j++)
                t[j][i] = a[i][j];
        showMatrixResult("A^T (Transpose)", formatMatrix(t));
        resultView.append(getString(R.string.mat_transpose_result) + "\n");
    }

    private void onMatrixRank() {
        double[][] a = getMatrixA();
        if (a == null) return;
        int m = a.length, n = a[0].length;
        double[][] rref = a.clone();
        for (int i = 0; i < m; i++) rref[i] = a[i].clone();
        int rank = 0;
        int pivotRow = 0;
        for (int col = 0; col < n && pivotRow < m; col++) {
            int maxRow = pivotRow;
            for (int row = pivotRow + 1; row < m; row++) {
                if (Math.abs(rref[row][col]) > Math.abs(rref[maxRow][col])) maxRow = row;
            }
            if (Math.abs(rref[maxRow][col]) < 1e-10) continue;
            double[] tmp = rref[pivotRow]; rref[pivotRow] = rref[maxRow]; rref[maxRow] = tmp;
            double piv = rref[pivotRow][col];
            for (int j = 0; j < n; j++) rref[pivotRow][j] /= piv;
            for (int row = 0; row < m; row++) {
                if (row == pivotRow) continue;
                double f = rref[row][col];
                for (int j = 0; j < n; j++) rref[row][j] -= f * rref[pivotRow][j];
            }
            rank++;
            pivotRow++;
        }
        showMatrixResult("rank(A)", String.format(getString(R.string.mat_rank_result), rank));
        resultView.append(String.format(getString(R.string.mat_rank_result), rank) + "\n");
    }

    private void onMatrixEigen() {
        double[][] a = getMatrixA();
        if (a == null) return;
        if (a.length != a[0].length) { toast(getString(R.string.toast_eig_square)); return; }
        int n = a.length;
        // For 2x2: use characteristic equation
        if (n == 2) {
            double trace = a[0][0] + a[1][1];
            double detA = a[0][0]*a[1][1] - a[0][1]*a[1][0];
            double disc = trace*trace - 4*detA;
            StringBuilder sb = new StringBuilder();
            sb.append("Eigenvalues for 2x2 matrix:\n\n");
            if (disc >= 0) {
                double l1 = (trace + Math.sqrt(disc)) / 2;
                double l2 = (trace - Math.sqrt(disc)) / 2;
                sb.append("  lambda1 = ").append(fmt(l1)).append("\n");
                sb.append("  lambda2 = ").append(fmt(l2)).append("\n");
            } else {
                double real = trace / 2;
                double imag = Math.sqrt(-disc) / 2;
                sb.append("  lambda1 = ").append(fmt(real)).append(" + ").append(fmt(imag)).append("i\n");
                sb.append("  lambda2 = ").append(fmt(real)).append(" - ").append(fmt(imag)).append("i\n");
            }
            showMatrixResult("Eigenvalues", sb.toString());
        } else {
            // For larger matrices: use power iteration to find dominant eigenvalue
            // and deflate to find subsequent ones (QR algorithm simplified)
            StringBuilder sb = new StringBuilder();
            sb.append("Eigenvalue approximation (power iteration):\n\n");
            double[][] mat = new double[n][n];
            for (int i = 0; i < n; i++)
                for (int j = 0; j < n; j++)
                    mat[i][j] = a[i][j];
            double[] eigenvalues = new double[n];
            for (int e = 0; e < n; e++) {
                // Power iteration
                double[] v = new double[n];
                v[0] = 1.0;  // Initial guess
                double eigenval = 0;
                for (int iter = 0; iter < 1000; iter++) {
                    double[] newV = new double[n];
                    for (int i = 0; i < n; i++) {
                        double sum = 0;
                        for (int j = 0; j < n; j++) sum += mat[i][j] * v[j];
                        newV[i] = sum;
                    }
                    // Normalize
                    double norm = 0;
                    for (int i = 0; i < n; i++) norm += newV[i] * newV[i];
                    norm = Math.sqrt(norm);
                    if (norm < 1e-15) break;
                    for (int i = 0; i < n; i++) newV[i] /= norm;
                    // Estimate eigenvalue (Rayleigh quotient)
                    double[] Av = new double[n];
                    for (int i = 0; i < n; i++) {
                        double sum = 0;
                        for (int j = 0; j < n; j++) sum += mat[i][j] * newV[j];
                        Av[i] = sum;
                    }
                    double num = 0, den = 0;
                    for (int i = 0; i < n; i++) {
                        num += newV[i] * Av[i];
                        den += newV[i] * newV[i];
                    }
                    eigenval = num / den;
                    v = newV;
                }
                eigenvalues[e] = eigenval;
                sb.append("  lambda").append(e + 1).append(" = ").append(fmt(eigenval)).append("\n");
                // Deflate: subtract eigenvalue * v * v^T
                for (int i = 0; i < n; i++)
                    for (int j = 0; j < n; j++)
                        mat[i][j] -= eigenval * v[i] * v[j];
            }
            showMatrixResult("Eigenvalues", sb.toString());
        }
        resultView.append("Eigenvalue computation done\n");
    }

    private void onStatsHistogram() {
        double[] data = parseStatsData();
        if (data == null) return;
        int n = data.length;

        // Calculate basic stats for text display
        double sum = 0;
        for (double v : data) sum += v;
        double mean = sum / n;

        java.util.Arrays.sort(data);
        double median;
        if (n % 2 == 0) {
            median = (data[n / 2 - 1] + data[n / 2]) / 2.0;
        } else {
            median = data[n / 2];
        }

        // Create histogram as text-based bar chart
        int nBins = Math.max(5, Math.min(15, (int) Math.sqrt(n) + 1));
        double min = data[0];
        double max = data[n - 1];
        double binWidth = (max - min) / nBins;
        if (binWidth == 0) binWidth = 1;

        int[] counts = new int[nBins];
        for (double v : data) {
            int bin = (int) ((v - min) / binWidth);
            if (bin >= nBins) bin = nBins - 1;
            counts[bin]++;
        }

        StringBuilder sb = new StringBuilder();
        sb.append(String.format(getString(R.string.histogram_title), nBins)).append("\n");
        sb.append(String.format(getString(R.string.histogram_stats), mean, median)).append("\n\n");

        int maxCount = 0;
        for (int c : counts) if (c > maxCount) maxCount = c;
        int barMaxLen = 30;

        for (int i = 0; i < nBins; i++) {
            double lo = min + i * binWidth;
            double hi = lo + binWidth;
            int barLen = maxCount > 0 ? (counts[i] * barMaxLen / maxCount) : 0;
            StringBuilder bar = new StringBuilder();
            for (int j = 0; j < barLen; j++) bar.append("\u2588");
            sb.append(String.format("[%6.3g,%6.3g) %3d |%s\n", lo, hi, counts[i], bar.toString()));
        }

        android.widget.TextView tv = new android.widget.TextView(this);
        tv.setText(sb.toString());
        tv.setTypeface(android.graphics.Typeface.MONOSPACE);
        tv.setTextSize(13);
        tv.setPadding(40, 24, 40, 24);
        tv.setTextColor(android.graphics.Color.parseColor("#cdd6f4"));
        tv.setBackgroundColor(android.graphics.Color.parseColor("#181825"));

        android.widget.ScrollView sv = new android.widget.ScrollView(this);
        sv.addView(tv);

        new androidx.appcompat.app.AlertDialog.Builder(this, androidx.appcompat.R.style.ThemeOverlay_AppCompat_Dialog_Alert)
            .setTitle(getString(R.string.dialog_histogram))
            .setView(sv)
            .setPositiveButton(getString(R.string.dialog_close), null)
            .show();

        resultView.append(String.format(getString(R.string.histogram_toast), nBins, mean) + "\n");
    }

    // ------------------------------------------------------------------
    //  Curve Fitting / Regression
    // ------------------------------------------------------------------
    private double[] parseRegData(EditText xInput, EditText yInput, boolean useX) {
        double[] ys;
        String yRaw = yInput.getText().toString().trim();
        if (!yRaw.isEmpty()) {
            ys = parseDataArray(yRaw);
        } else {
            ys = parseStatsData();
        }
        if (ys == null || ys.length < 2) {
            toast(getString(R.string.toast_need_2y));
            return null;
        }
        if (useX) {
            String xRaw = xInput.getText().toString().trim();
            if (!xRaw.isEmpty()) {
                return parseDataArray(xRaw);
            }
            double[] xs = new double[ys.length];
            for (int i = 0; i < ys.length; i++) xs[i] = i + 1;
            return xs;
        }
        return ys;
    }

    private double[] parseDataArray(String raw) {
        String[] tokens = raw.split("[,;\\s]+");
        java.util.ArrayList<Double> values = new java.util.ArrayList<>();
        for (String t : tokens) {
            t = t.trim();
            if (t.isEmpty()) continue;
            try { values.add(Double.parseDouble(t)); } catch (NumberFormatException e) { return null; }
        }
        double[] result = new double[values.size()];
        for (int i = 0; i < values.size(); i++) result[i] = values.get(i);
        return result;
    }

    private void showRegResult(String title, String equation, double r2) {
        StringBuilder sb = new StringBuilder();
        sb.append(title).append("\n\n");
        sb.append(getString(R.string.regression_prefix)).append(equation).append("\n");
        sb.append(String.format("R\u00B2 = %.8f", r2));
        android.widget.TextView tv = new android.widget.TextView(this);
        tv.setText(sb.toString());
        tv.setTypeface(android.graphics.Typeface.MONOSPACE);
        tv.setTextSize(14);
        tv.setPadding(40, 24, 40, 24);
        tv.setTextColor(android.graphics.Color.parseColor("#cdd6f4"));
        tv.setBackgroundColor(android.graphics.Color.parseColor("#181825"));
        new androidx.appcompat.app.AlertDialog.Builder(this, androidx.appcompat.R.style.ThemeOverlay_AppCompat_Dialog_Alert)
            .setTitle(title)
            .setView(tv)
            .setPositiveButton(getString(R.string.dialog_close), null)
            .show();
        resultView.append(String.format("%s: %s (R\u00B2=%.6f)\n", title, equation, r2));
    }

    private void onRegLinear(EditText xInput, EditText yInput) {
        double[] xs = parseRegData(xInput, yInput, true);
        double[] ys = parseRegData(xInput, yInput, false);
        if (xs == null || ys == null || xs.length != ys.length) return;
        int n = xs.length;
        double xMean = 0, yMean = 0;
        for (int i = 0; i < n; i++) { xMean += xs[i]; yMean += ys[i]; }
        xMean /= n; yMean /= n;
        double ssXY = 0, ssXX = 0;
        for (int i = 0; i < n; i++) {
            ssXY += (xs[i] - xMean) * (ys[i] - yMean);
            ssXX += (xs[i] - xMean) * (xs[i] - xMean);
        }
        if (ssXX == 0) { toast(getString(R.string.toast_zero_variance)); return; }
        double slope = ssXY / ssXX;
        double intercept = yMean - slope * xMean;
        double ssRes = 0, ssTot = 0;
        for (int i = 0; i < n; i++) {
            double yPred = slope * xs[i] + intercept;
            ssRes += (ys[i] - yPred) * (ys[i] - yPred);
            ssTot += (ys[i] - yMean) * (ys[i] - yMean);
        }
        double r2 = ssTot != 0 ? 1.0 - ssRes / ssTot : 0;
        String eq = String.format("y = %.6g*x %s %.6g", slope, intercept >= 0 ? "+" : "-", Math.abs(intercept));
        showRegResult(getString(R.string.regression_linear), eq, r2);
    }

    private void onRegPoly(EditText xInput, EditText yInput, int degree) {
        double[] xs = parseRegData(xInput, yInput, true);
        double[] ys = parseRegData(xInput, yInput, false);
        if (xs == null || ys == null || xs.length != ys.length) return;
        if (xs.length < degree + 1) { toast(getString(R.string.toast_need_n_points, degree + 1)); return; }
        // Vandermonde matrix approach for polynomial least squares
        int n = xs.length;
        int m = degree + 1;
        double[][] A = new double[n][m];
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < m; j++) {
                A[i][j] = Math.pow(xs[i], j);
            }
        }
        // Solve via normal equations: (A^T A) c = A^T y
        double[][] AtA = new double[m][m];
        double[] Aty = new double[m];
        for (int i = 0; i < m; i++) {
            for (int j = 0; j < m; j++) {
                double sum = 0;
                for (int k = 0; k < n; k++) sum += A[k][i] * A[k][j];
                AtA[i][j] = sum;
            }
            double sum = 0;
            for (int k = 0; k < n; k++) sum += A[k][i] * ys[k];
            Aty[i] = sum;
        }
        // Gaussian elimination
        double[] coeffs = solveLinearSystem(AtA, Aty);
        if (coeffs == null) { toast(getString(R.string.toast_cannot_fit)); return; }
        // R²
        double yMean = 0;
        for (double v : ys) yMean += v;
        yMean /= n;
        double ssRes = 0, ssTot = 0;
        for (int i = 0; i < n; i++) {
            double yPred = 0;
            for (int j = 0; j < m; j++) yPred += coeffs[j] * Math.pow(xs[i], j);
            ssRes += (ys[i] - yPred) * (ys[i] - yPred);
            ssTot += (ys[i] - yMean) * (ys[i] - yMean);
        }
        double r2 = ssTot != 0 ? 1.0 - ssRes / ssTot : 0;
        StringBuilder eq = new StringBuilder("y = ");
        for (int j = degree; j >= 0; j--) {
            if (Math.abs(coeffs[j]) < 1e-12) continue;
            if (j < degree) eq.append(coeffs[j] >= 0 ? " + " : " - ");
            eq.append(String.format("%.6g", Math.abs(coeffs[j])));
            if (j > 1) eq.append("*x^").append(j);
            else if (j == 1) eq.append("*x");
        }
        showRegResult(String.format(getString(R.string.regression_poly), degree), eq.toString(), r2);
    }

    private double[] solveLinearSystem(double[][] A, double[] b) {
        int n = A.length;
        double[][] aug = new double[n][n + 1];
        for (int i = 0; i < n; i++) {
            System.arraycopy(A[i], 0, aug[i], 0, n);
            aug[i][n] = b[i];
        }
        for (int col = 0; col < n; col++) {
            int maxRow = col;
            for (int row = col + 1; row < n; row++) {
                if (Math.abs(aug[row][col]) > Math.abs(aug[maxRow][col])) maxRow = row;
            }
            double[] tmp = aug[col]; aug[col] = aug[maxRow]; aug[maxRow] = tmp;
            if (Math.abs(aug[col][col]) < 1e-12) return null;
            for (int row = col + 1; row < n; row++) {
                double factor = aug[row][col] / aug[col][col];
                for (int j = col; j <= n; j++) aug[row][j] -= factor * aug[col][j];
            }
        }
        double[] x = new double[n];
        for (int i = n - 1; i >= 0; i--) {
            x[i] = aug[i][n];
            for (int j = i + 1; j < n; j++) x[i] -= aug[i][j] * x[j];
            x[i] /= aug[i][i];
        }
        return x;
    }

    private void onRegExponential(EditText xInput, EditText yInput) {
        double[] xs = parseRegData(xInput, yInput, true);
        double[] ys = parseRegData(xInput, yInput, false);
        if (xs == null || ys == null || xs.length != ys.length) return;
        // Filter positive y values for log transform
        java.util.ArrayList<Double> xList = new java.util.ArrayList<>();
        java.util.ArrayList<Double> yList = new java.util.ArrayList<>();
        for (int i = 0; i < xs.length; i++) {
            if (ys[i] > 0 && Double.isFinite(xs[i]) && Double.isFinite(ys[i])) {
                xList.add(xs[i]); yList.add(ys[i]);
            }
        }
        if (xList.size() < 2) { toast(getString(R.string.toast_need_2_pos_y)); return; }
        int n = xList.size();
        double[] lx = new double[n], ly = new double[n];
        for (int i = 0; i < n; i++) { lx[i] = xList.get(i); ly[i] = Math.log(yList.get(i)); }
        double xMean = 0, lyMean = 0;
        for (int i = 0; i < n; i++) { xMean += lx[i]; lyMean += ly[i]; }
        xMean /= n; lyMean /= n;
        double ssXY = 0, ssXX = 0;
        for (int i = 0; i < n; i++) {
            ssXY += (lx[i] - xMean) * (ly[i] - lyMean);
            ssXX += (lx[i] - xMean) * (lx[i] - xMean);
        }
        if (ssXX == 0) { toast(getString(R.string.toast_zero_variance)); return; }
        double b = ssXY / ssXX;
        double lnA = lyMean - b * xMean;
        double a = Math.exp(lnA);
        // R²
        double yMean = 0;
        for (double v : yList) yMean += v;
        yMean /= n;
        double ssRes = 0, ssTot = 0;
        for (int i = 0; i < n; i++) {
            double yPred = a * Math.exp(b * lx[i]);
            ssRes += (yList.get(i) - yPred) * (yList.get(i) - yPred);
            ssTot += (yList.get(i) - yMean) * (yList.get(i) - yMean);
        }
        double r2 = ssTot != 0 ? 1.0 - ssRes / ssTot : 0;
        String eq = String.format("y = %.6g * e^(%.6g*x)", a, b);
        showRegResult(getString(R.string.regression_exponential), eq, r2);
    }

    private void onRegPower(EditText xInput, EditText yInput) {
        double[] xs = parseRegData(xInput, yInput, true);
        double[] ys = parseRegData(xInput, yInput, false);
        if (xs == null || ys == null || xs.length != ys.length) return;
        java.util.ArrayList<Double> xList = new java.util.ArrayList<>();
        java.util.ArrayList<Double> yList = new java.util.ArrayList<>();
        for (int i = 0; i < xs.length; i++) {
            if (xs[i] > 0 && ys[i] > 0 && Double.isFinite(xs[i]) && Double.isFinite(ys[i])) {
                xList.add(xs[i]); yList.add(ys[i]);
            }
        }
        if (xList.size() < 2) { toast(getString(R.string.toast_need_2_pos)); return; }
        int n = xList.size();
        double[] lx = new double[n], ly = new double[n];
        for (int i = 0; i < n; i++) { lx[i] = Math.log(xList.get(i)); ly[i] = Math.log(yList.get(i)); }
        double xMean = 0, lyMean = 0;
        for (int i = 0; i < n; i++) { xMean += lx[i]; lyMean += ly[i]; }
        xMean /= n; lyMean /= n;
        double ssXY = 0, ssXX = 0;
        for (int i = 0; i < n; i++) {
            ssXY += (lx[i] - xMean) * (ly[i] - lyMean);
            ssXX += (lx[i] - xMean) * (lx[i] - xMean);
        }
        if (ssXX == 0) { toast(getString(R.string.toast_zero_variance)); return; }
        double b = ssXY / ssXX;
        double lnA = lyMean - b * xMean;
        double a = Math.exp(lnA);
        double yMean = 0;
        for (double v : yList) yMean += v;
        yMean /= n;
        double ssRes = 0, ssTot = 0;
        for (int i = 0; i < n; i++) {
            double yPred = a * Math.pow(xList.get(i), b);
            ssRes += (yList.get(i) - yPred) * (yList.get(i) - yPred);
            ssTot += (yList.get(i) - yMean) * (yList.get(i) - yMean);
        }
        double r2 = ssTot != 0 ? 1.0 - ssRes / ssTot : 0;
        String eq = String.format("y = %.6g * x^%.6g", a, b);
        showRegResult(getString(R.string.regression_power), eq, r2);
    }

    private void onRegLogarithmic(EditText xInput, EditText yInput) {
        double[] xs = parseRegData(xInput, yInput, true);
        double[] ys = parseRegData(xInput, yInput, false);
        if (xs == null || ys == null || xs.length != ys.length) return;
        java.util.ArrayList<Double> xList = new java.util.ArrayList<>();
        java.util.ArrayList<Double> yList = new java.util.ArrayList<>();
        for (int i = 0; i < xs.length; i++) {
            if (xs[i] > 0 && Double.isFinite(xs[i]) && Double.isFinite(ys[i])) {
                xList.add(xs[i]); yList.add(ys[i]);
            }
        }
        if (xList.size() < 2) { toast(getString(R.string.toast_need_2_pos_x)); return; }
        int n = xList.size();
        double[] lx = new double[n];
        for (int i = 0; i < n; i++) lx[i] = Math.log(xList.get(i));
        double xMean = 0, yMean = 0;
        for (int i = 0; i < n; i++) { xMean += lx[i]; yMean += yList.get(i); }
        xMean /= n; yMean /= n;
        double ssXY = 0, ssXX = 0;
        for (int i = 0; i < n; i++) {
            ssXY += (lx[i] - xMean) * (yList.get(i) - yMean);
            ssXX += (lx[i] - xMean) * (lx[i] - xMean);
        }
        if (ssXX == 0) { toast(getString(R.string.toast_zero_variance)); return; }
        double b = ssXY / ssXX;
        double a = yMean - b * xMean;
        double ssRes = 0, ssTot = 0;
        for (int i = 0; i < n; i++) {
            double yPred = a + b * lx[i];
            ssRes += (yList.get(i) - yPred) * (yList.get(i) - yPred);
            ssTot += (yList.get(i) - yMean) * (yList.get(i) - yMean);
        }
        double r2 = ssTot != 0 ? 1.0 - ssRes / ssTot : 0;
        String eq = String.format("y = %.6g %s %.6g*ln(x)", a, b >= 0 ? "+" : "-", Math.abs(b));
        showRegResult(getString(R.string.regression_logarithmic), eq, r2);
    }

    private double[] lastRegXs, lastRegYs;
    private String lastRegEquation = "";
    private void onRegPlot(EditText xInput, EditText yInput) {
        double[] xs = parseRegData(xInput, yInput, true);
        double[] ys = parseRegData(xInput, yInput, false);
        if (xs == null || ys == null || xs.length != ys.length) return;
        lastRegXs = xs; lastRegYs = ys;
        Intent intent = new Intent(this, PlotActivity.class);
        intent.putExtra("expr", "");  // We'll pass precomputed data
        intent.putExtra("xMin", xs[0]);
        intent.putExtra("xMax", xs[xs.length - 1]);
        intent.putExtra("regression", true);
        intent.putExtra("regXs", xs);
        intent.putExtra("regYs", ys);
        startActivity(intent);
    }

    private void onPlotParametric() {
        String xExpr = xParamInput.getText().toString().trim();
        String yExpr = yParamInput.getText().toString().trim();
        if (xExpr.isEmpty() || yExpr.isEmpty()) {
            toast(getString(R.string.toast_enter_xt_yt));
            return;
        }

        double tMin, tMax;
        try {
            tMin = Double.parseDouble(tMinInput.getText().toString().trim());
            tMax = Double.parseDouble(tMaxInput.getText().toString().trim());
        } catch (NumberFormatException ex) {
            toast(getString(R.string.toast_invalid_t_range));
            return;
        }
        if (tMin >= tMax) {
            toast(getString(R.string.toast_t_range));
            return;
        }

        int n = 500;
        double step = (tMax - tMin) / (n - 1);
        double[] ts = new double[n];
        for (int i = 0; i < n; i++) {
            ts[i] = tMin + i * step;
        }

        // C core only supports x/y variables; replace t -> x for evaluation
        String xExprSub = xExpr.replaceAll("\\bt\\b", "x");
        String yExprSub = yExpr.replaceAll("\\bt\\b", "x");
        double[] xs = CalcEngine.evaluateArray(xExprSub, ts);
        double[] ys = CalcEngine.evaluateArray(yExprSub, ts);
        if (xs == null || ys == null) {
            resultView.append(String.format(getString(R.string.parametric_error), CalcEngine.getLastError()) + "\n");
            return;
        }

        Intent intent = new Intent(this, PlotActivity.class);
        intent.putExtra("parametric_x", xExpr);
        intent.putExtra("parametric_y", yExpr);
        intent.putExtra("t_min", tMin);
        intent.putExtra("t_max", tMax);
        intent.putExtra("is_parametric", true);
        startActivity(intent);
    }

    private void onPlotPolar() {
        String rExpr = rPolarInput.getText().toString().trim();
        if (rExpr.isEmpty()) {
            toast(getString(R.string.toast_enter_rtheta));
            return;
        }

        double thetaMin, thetaMax;
        try {
            thetaMin = Double.parseDouble(thetaMinInput.getText().toString().trim());
            thetaMax = Double.parseDouble(thetaMaxInput.getText().toString().trim());
        } catch (NumberFormatException ex) {
            toast(getString(R.string.toast_invalid_theta_range));
            return;
        }
        if (thetaMin >= thetaMax) {
            toast(getString(R.string.toast_theta_range));
            return;
        }

        int n = 500;
        double step = (thetaMax - thetaMin) / (n - 1);
        double[] thetas = new double[n];
        for (int i = 0; i < n; i++) {
            thetas[i] = thetaMin + i * step;
        }

        // C core only supports x/y variables; replace theta -> x for evaluation
        String rExprSub = rExpr.replaceAll("\\btheta\\b", "x");
        double[] rs = CalcEngine.evaluateArray(rExprSub, thetas);
        if (rs == null) {
            resultView.append(String.format(getString(R.string.polar_error), CalcEngine.getLastError()) + "\n");
            return;
        }

        // Convert polar to Cartesian coordinates for plotting
        double[] xs = new double[n];
        double[] ys = new double[n];
        for (int i = 0; i < n; i++) {
            if (Double.isNaN(rs[i])) {
                xs[i] = Double.NaN;
                ys[i] = Double.NaN;
            } else {
                xs[i] = rs[i] * Math.cos(thetas[i]);
                ys[i] = rs[i] * Math.sin(thetas[i]);
            }
        }

        Intent intent = new Intent(this, PlotActivity.class);
        intent.putExtra("parametric_x", rExpr);
        intent.putExtra("is_polar", true);
        intent.putExtra("t_min", thetaMin);
        intent.putExtra("t_max", thetaMax);
        startActivity(intent);
    }

    private void onGenerateTable() {
        String e = getExpr();
        if (e.isEmpty()) { toast(getString(R.string.toast_enter_expr)); return; }
        double a = getA();
        double b = getB();
        if (a >= b) { toast(getString(R.string.toast_table_range)); return; }
        int n = 21; // default points

        double step = (b - a) / (n - 1);
        double[] xs = new double[n];
        for (int i = 0; i < n; i++) {
            xs[i] = a + i * step;
        }
        double[] ys = CalcEngine.evaluateArray(e, xs);
        if (ys == null) {
            resultView.append(String.format(getString(R.string.table_error), CalcEngine.getLastError()) + "\n");
            return;
        }

        StringBuilder sb = new StringBuilder();
        sb.append("x\t\tf(x)\n");
        sb.append("----------------------------\n");
        int valid = 0;
        for (int i = 0; i < n; i++) {
            String yStr = Double.isNaN(ys[i]) ? "N/A" : fmt(ys[i]);
            sb.append(fmt(xs[i])).append("\t").append(yStr).append("\n");
            if (!Double.isNaN(ys[i])) valid++;
        }
        sb.append("----------------------------\n");
        sb.append(String.format(getString(R.string.table_valid_count), valid, n)).append("\n");

        // Build CSV for sharing
        StringBuilder csv = new StringBuilder();
        csv.append("x,f(x)=").append(e.replace(",", ";")).append("\n");
        for (int i = 0; i < n; i++) {
            csv.append(xs[i]).append(",").append(Double.isNaN(ys[i]) ? "" : ys[i]).append("\n");
        }

        final String tableText = sb.toString();
        final String csvText = csv.toString();

        android.widget.TextView textView = new android.widget.TextView(this);
        textView.setText(tableText);
        textView.setTypeface(android.graphics.Typeface.MONOSPACE);
        textView.setTextSize(13);
        textView.setPadding(40, 24, 40, 24);
        textView.setTextColor(android.graphics.Color.parseColor("#cdd6f4"));
        textView.setBackgroundColor(android.graphics.Color.parseColor("#181825"));

        android.widget.ScrollView scrollView = new android.widget.ScrollView(this);
        scrollView.addView(textView);
        scrollView.setPadding(0, 0, 0, 0);

        new androidx.appcompat.app.AlertDialog.Builder(this, androidx.appcompat.R.style.ThemeOverlay_AppCompat_Dialog_Alert)
            .setTitle(getString(R.string.dialog_function_table, n))
            .setView(scrollView)
            .setPositiveButton(getString(R.string.dialog_share_csv), (dialog, which) -> shareText(csvText, "SuperCalc Table"))
            .setNegativeButton(getString(R.string.dialog_close), null)
            .show();

        resultView.append(String.format(getString(R.string.table_generated), valid, n) + "\n");
    }

    private void shareText(String text, String title) {
        Intent shareIntent = new Intent(Intent.ACTION_SEND);
        shareIntent.setType("text/plain");
        shareIntent.putExtra(Intent.EXTRA_SUBJECT, title);
        shareIntent.putExtra(Intent.EXTRA_TEXT, text);
        startActivity(Intent.createChooser(shareIntent, getString(R.string.table_share)));
    }

    private static String fmt(double v) {
        if (Double.isNaN(v) || Double.isInfinite(v)) return String.valueOf(v);
        if (Math.abs(v) < 1e15 && v == (long) v && Math.abs(v) <= Long.MAX_VALUE) {
            return String.format("%d", (long) v);
        }
        return String.format("%.10g", v);
    }

    private void toast(String msg) {
        Toast.makeText(this, msg, Toast.LENGTH_SHORT).show();
    }

    // Unit Converter
    private AutoCompleteTextView unitCategoryDropdown, unitFromDropdown, unitToDropdown;
    private EditText unitValueInput, unitResultInput;
    private ArrayAdapter<String> unitCategoryAdapter, unitFromAdapter, unitToAdapter;

    // Statistical Distribution Calculator
    private AutoCompleteTextView distTypeDropdown;
    private EditText distParamsInput, distXInput;
    private ArrayAdapter<String> distTypeAdapter;

    private void setupDistCalc() {
        distTypeDropdown = findViewById(R.id.dist_type_dropdown);
        distParamsInput = findViewById(R.id.dist_params_input);
        distXInput = findViewById(R.id.dist_x_input);

        String[] distNames = StatDistCalc.getDistributionNames(this);
        distTypeAdapter = new ArrayAdapter<>(this, android.R.layout.simple_dropdown_item_1line, distNames);
        distTypeDropdown.setAdapter(distTypeAdapter);
        distTypeDropdown.setText(distNames[0], false);

        distTypeDropdown.setOnItemClickListener((parent, view, position, id) -> {
            String name = distTypeAdapter.getItem(position);
            updateDistParams(name);
        });

        MaterialButton btnDistPdf = findViewById(R.id.btn_dist_pdf);
        MaterialButton btnDistCdf = findViewById(R.id.btn_dist_cdf);
        MaterialButton btnDistPpf = findViewById(R.id.btn_dist_ppf);
        MaterialButton btnDistPlot = findViewById(R.id.btn_dist_plot);

        btnDistPdf.setOnClickListener(v -> onDistCompute("pdf"));
        btnDistCdf.setOnClickListener(v -> onDistCompute("cdf"));
        btnDistPpf.setOnClickListener(v -> onDistCompute("ppf"));
        btnDistPlot.setOnClickListener(v -> onDistPlot());
    }

    private void updateDistParams(String name) {
        if (name.equals(getString(R.string.dist_normal))) { distParamsInput.setText("0, 1"); }
        else if (name.equals(getString(R.string.dist_t))) { distParamsInput.setText("5"); }
        else if (name.equals(getString(R.string.dist_chi2))) { distParamsInput.setText("3"); }
        else if (name.equals(getString(R.string.dist_f))) { distParamsInput.setText("5, 10"); }
        else if (name.equals(getString(R.string.dist_binomial))) { distParamsInput.setText("20, 0.5"); }
        else if (name.equals(getString(R.string.dist_poisson))) { distParamsInput.setText("5"); }
        else { distParamsInput.setText("0, 1"); }
    }

    private void onDistCompute(String mode) {
        String distName = distTypeDropdown.getText().toString();
        StatDistCalc.DistType type = StatDistCalc.fromName(this, distName);
        double[] params = parseParams(distParamsInput.getText().toString());
        if (params == null) {
            toast(getString(R.string.toast_invalid_params));
            return;
        }
        double x;
        try {
            x = Double.parseDouble(distXInput.getText().toString().trim());
        } catch (NumberFormatException e) {
            toast(getString(R.string.toast_invalid_x_value));
            return;
        }

        double result;
        String label;
        switch (mode) {
            case "pdf":
                result = StatDistCalc.pdf(type, x, params);
                label = "PDF";
                break;
            case "cdf":
                result = StatDistCalc.cdf(type, x, params);
                label = "CDF";
                break;
            case "ppf":
                // PPF: binary search for inverse CDF
                result = computePpf(type, x, params);
                label = "PPF";
                break;
            default:
                return;
        }
        if (Double.isNaN(result) || Double.isInfinite(result)) {
            appendResult(distName + " " + label + "(" + fmt(x) + ")", Double.NaN);
        } else {
            appendResult(distName + " " + label + "(" + fmt(x) + ")", result);
        }
    }

    private double computePpf(StatDistCalc.DistType type, double q, double[] params) {
        if (q <= 0 || q >= 1) return Double.NaN;
        double lo = -10.0, hi = 10.0;
        // Dynamically expand search range to cover the full distribution support
        while (StatDistCalc.cdf(type, lo, params) > q) lo *= 2;
        while (StatDistCalc.cdf(type, hi, params) < q) hi *= 2;
        for (int i = 0; i < 100; i++) {
            double mid = (lo + hi) / 2.0;
            if (StatDistCalc.cdf(type, mid, params) < q) lo = mid; else hi = mid;
        }
        return (lo + hi) / 2.0;
    }

    private void onDistPlot() {
        String distName = distTypeDropdown.getText().toString();
        StatDistCalc.DistType type = StatDistCalc.fromName(this, distName);
        double[] params = parseParams(distParamsInput.getText().toString());
        if (params == null) {
            toast(getString(R.string.toast_invalid_params));
            return;
        }

        double xMin, xMax;
        switch (type) {
            case NORMAL:
                double mu = params[0], sigma = Math.abs(params[1]);
                xMin = mu - 4 * sigma; xMax = mu + 4 * sigma;
                break;
            case T:
                xMin = -6; xMax = 6;
                break;
            case CHI2:
                double k = params[0];
                xMin = 0; xMax = Math.max(k + 4 * Math.sqrt(2 * k), 1);
                break;
            case F:
                xMin = 0.01; xMax = 10;
                break;
            case BINOMIAL:
                xMin = 0; xMax = params[0];
                break;
            case POISSON:
                double lam = params[0];
                xMin = 0; xMax = (int)(lam + 4 * Math.sqrt(lam)) + 1;
                break;
            default:
                xMin = -5; xMax = 5; break;
        }

        int n = 200;
        double step = (xMax - xMin) / (n - 1);
        float[] xs = new float[n];
        float[] ys = new float[n];
        for (int i = 0; i < n; i++) {
            double x = xMin + i * step;
            xs[i] = (float) x;
            ys[i] = (float) StatDistCalc.pdf(type, x, params);
        }

        // Plot using MPAndroidChart
        java.util.ArrayList<Entry> entries = new java.util.ArrayList<>();
        for (int i = 0; i < n; i++) {
            entries.add(new Entry(xs[i], ys[i]));
        }
        LineDataSet dataSet = new LineDataSet(entries, distName + " PDF");
        dataSet.setColor(0xFF89B4FA);
        dataSet.setDrawCircles(false);
        dataSet.setLineWidth(2f);
        dataSet.setDrawValues(false);
        LineData lineData = new LineData(dataSet);
        lineChart.setData(lineData);
        lineChart.getDescription().setText(distName + " Distribution");
        lineChart.getDescription().setTextColor(0xFFCDD6F4);
        lineChart.getAxisRight().setEnabled(false);
        XAxis xAxis = lineChart.getXAxis();
        xAxis.setPosition(XAxis.XAxisPosition.BOTTOM);
        xAxis.setTextColor(0xFFCDD6F4);
        xAxis.setGridColor(0xFF45475A);
        YAxis yAxis = lineChart.getAxisLeft();
        yAxis.setTextColor(0xFFCDD6F4);
        yAxis.setGridColor(0xFF45475A);
        lineChart.invalidate();
        graphCard.setVisibility(android.view.View.VISIBLE);
        toast(getString(R.string.toast_dist_plotted, distName));
    }

    private double[] parseParams(String text) {
        if (text == null || text.trim().isEmpty()) return null;
        String[] parts = text.trim().split(",");
        double[] result = new double[parts.length];
        try {
            for (int i = 0; i < parts.length; i++) {
                result[i] = Double.parseDouble(parts[i].trim());
            }
            return result;
        } catch (NumberFormatException e) {
            return null;
        }
    }

    private void setupBaseConverter() {
        EditText baseInput = findViewById(R.id.base_input);
        AutoCompleteTextView baseFromDropdown = findViewById(R.id.base_from_dropdown);
        MaterialButton btnBaseConvert = findViewById(R.id.btn_base_convert);
        TextView baseBinResult = findViewById(R.id.base_bin_result);
        TextView baseOctResult = findViewById(R.id.base_oct_result);
        TextView baseDecResult = findViewById(R.id.base_dec_result);
        TextView baseHexResult = findViewById(R.id.base_hex_result);

        String[] bases = {"2", "8", "10", "16"};
        ArrayAdapter<String> baseAdapter = new ArrayAdapter<>(this, android.R.layout.simple_dropdown_item_1line, bases);
        baseFromDropdown.setAdapter(baseAdapter);
        baseFromDropdown.setText("10", false);

        btnBaseConvert.setOnClickListener(v -> {
            String input = baseInput.getText().toString().trim();
            if (input.isEmpty()) {
                Toast.makeText(this, R.string.toast_base_invalid, Toast.LENGTH_SHORT).show();
                return;
            }
            int fromBase;
            try {
                fromBase = Integer.parseInt(baseFromDropdown.getText().toString());
            } catch (NumberFormatException e) {
                fromBase = 10;
            }

            try {
                long value = CalcEngine.baseToLong(input, fromBase);
                baseBinResult.setText(CalcEngine.longToBase(value, 2));
                baseOctResult.setText(CalcEngine.longToBase(value, 8));
                baseDecResult.setText(CalcEngine.longToBase(value, 10));
                baseHexResult.setText(CalcEngine.longToBase(value, 16));
            } catch (Exception e) {
                Toast.makeText(this, R.string.toast_base_invalid, Toast.LENGTH_SHORT).show();
                baseBinResult.setText("");
                baseOctResult.setText("");
                baseDecResult.setText("");
                baseHexResult.setText("");
            }
        });
    }

    private void setupUnitConverter() {
        unitCategoryDropdown = findViewById(R.id.unit_category_dropdown);
        unitFromDropdown = findViewById(R.id.unit_from_dropdown);
        unitToDropdown = findViewById(R.id.unit_to_dropdown);
        unitValueInput = findViewById(R.id.unit_value_input);
        unitResultInput = findViewById(R.id.unit_result_input);

        // Category adapter
        java.util.List<String> categories = new java.util.ArrayList<>(UNIT_DATA.keySet());
        unitCategoryAdapter = new ArrayAdapter<>(this, android.R.layout.simple_dropdown_item_1line, categories);
        unitCategoryDropdown.setAdapter(unitCategoryAdapter);
        unitCategoryDropdown.setText(categories.get(0), false);

        // From/To adapters — populated based on selected category
        unitFromAdapter = new ArrayAdapter<>(this, android.R.layout.simple_dropdown_item_1line, new java.util.ArrayList<>());
        unitToAdapter = new ArrayAdapter<>(this, android.R.layout.simple_dropdown_item_1line, new java.util.ArrayList<>());
        unitFromDropdown.setAdapter(unitFromAdapter);
        unitToDropdown.setAdapter(unitToAdapter);

        // Refresh from/to when category changes
        unitCategoryDropdown.setOnItemClickListener((parent, view, position, id) -> {
            String cat = unitCategoryAdapter.getItem(position);
            updateUnitDropdowns(cat);
        });

        // Initialize from/to for default category
        updateUnitDropdowns(categories.get(0));

        MaterialButton btnUnitConvert = findViewById(R.id.btn_unit_convert);
        btnUnitConvert.setOnClickListener(v -> onUnitConvert());
    }

    private void updateUnitDropdowns(String category) {
        java.util.Map<String, Double> units = UNIT_DATA.get(category);
        if (units == null) return;
        java.util.List<String> unitNames = new java.util.ArrayList<>(units.keySet());
        unitFromAdapter.clear();
        unitFromAdapter.addAll(unitNames);
        unitToAdapter.clear();
        unitToAdapter.addAll(unitNames);
        unitFromDropdown.setText(unitNames.get(0), false);
        unitToDropdown.setText(unitNames.size() > 1 ? unitNames.get(1) : unitNames.get(0), false);
    }

    private static final java.util.Map<String, java.util.Map<String, Double>> UNIT_DATA = new java.util.HashMap<>();
    static {
        // Length
        java.util.Map<String, Double> length = new java.util.HashMap<>();
        length.put("Meter (m)", 1.0);
        length.put("Kilometer (km)", 1000.0);
        length.put("Centimeter (cm)", 0.01);
        length.put("Millimeter (mm)", 0.001);
        length.put("Mile (mi)", 1609.344);
        length.put("Yard (yd)", 0.9144);
        length.put("Foot (ft)", 0.3048);
        length.put("Inch (in)", 0.0254);
        length.put("Nautical Mile (nmi)", 1852.0);
        UNIT_DATA.put("Length", length);

        // Weight
        java.util.Map<String, Double> weight = new java.util.HashMap<>();
        weight.put("Kilogram (kg)", 1.0);
        weight.put("Gram (g)", 0.001);
        weight.put("Milligram (mg)", 0.000001);
        weight.put("Metric Ton (t)", 1000.0);
        weight.put("Pound (lb)", 0.45359237);
        weight.put("Ounce (oz)", 0.028349523125);
        UNIT_DATA.put("Weight", weight);

        // Area
        java.util.Map<String, Double> area = new java.util.HashMap<>();
        area.put("Square Meter (m²)", 1.0);
        area.put("Square Kilometer (km²)", 1000000.0);
        area.put("Hectare (ha)", 10000.0);
        area.put("Acre (ac)", 4046.8564224);
        area.put("Square Foot (ft²)", 0.09290304);
        area.put("Square Inch (in²)", 0.00064516);
        area.put("Square Mile (mi²)", 2589988.110336);
        UNIT_DATA.put("Area", area);

        // Volume
        java.util.Map<String, Double> volume = new java.util.HashMap<>();
        volume.put("Liter (L)", 1.0);
        volume.put("Milliliter (mL)", 0.001);
        volume.put("Cubic Meter (m³)", 1000.0);
        volume.put("Gallon (US)", 3.785411784);
        volume.put("Quart (US)", 0.946352946);
        volume.put("Pint (US)", 0.473176473);
        volume.put("Cup (US)", 0.2365882365);
        volume.put("Fluid Ounce (US)", 0.0295735295625);
        volume.put("Cubic Centimeter (cm³)", 0.001);
        UNIT_DATA.put("Volume", volume);

        // Time
        java.util.Map<String, Double> time = new java.util.HashMap<>();
        time.put("Second (s)", 1.0);
        time.put("Minute (min)", 60.0);
        time.put("Hour (h)", 3600.0);
        time.put("Day (d)", 86400.0);
        time.put("Week (wk)", 604800.0);
        time.put("Month (30 days)", 2592000.0);
        time.put("Year (365 days)", 31536000.0);
        UNIT_DATA.put("Time", time);

        // Data Storage
        java.util.Map<String, Double> data = new java.util.HashMap<>();
        data.put("Byte (B)", 1.0);
        data.put("Kilobyte (KB)", 1024.0);
        data.put("Megabyte (MB)", 1048576.0);
        data.put("Gigabyte (GB)", 1073741824.0);
        data.put("Terabyte (TB)", 1099511627776.0);
        data.put("Bit", 0.125);
        data.put("Kilobit (Kbit)", 128.0);
        data.put("Megabit (Mbit)", 131072.0);
        data.put("Gigabit (Gbit)", 134217728.0);
        UNIT_DATA.put("Data Storage", data);

        // Speed
        java.util.Map<String, Double> speed = new java.util.HashMap<>();
        speed.put("Meter/second (m/s)", 1.0);
        speed.put("Kilometer/hour (km/h)", 0.2777777778);
        speed.put("Mile/hour (mph)", 0.44704);
        speed.put("Knot (kn)", 0.5144444444);
        speed.put("Foot/second (ft/s)", 0.3048);
        speed.put("Mach (at sea level)", 340.29);
        UNIT_DATA.put("Speed", speed);

        // Angle
        java.util.Map<String, Double> angle = new java.util.HashMap<>();
        angle.put("Degree (°)", 1.0);
        angle.put("Radian (rad)", 57.29577951308232);
        angle.put("Gradian (grad)", 0.9);
        angle.put("Arcminute (')", 1.0/60.0);
        angle.put("Arcsecond (\")", 1.0/3600.0);
        UNIT_DATA.put("Angle", angle);

        // Temperature (dummy factors — actual conversion handled by convertTemperature)
        java.util.Map<String, Double> temperature = new java.util.HashMap<>();
        temperature.put("Celsius (°C)", 1.0);
        temperature.put("Fahrenheit (°F)", 1.0);
        temperature.put("Kelvin (K)", 1.0);
        UNIT_DATA.put("Temperature", temperature);
    }

    private void onUnitConvert() {
        String category = unitCategoryDropdown.getText().toString().trim();
        String fromUnit = unitFromDropdown.getText().toString().trim();
        String toUnit = unitToDropdown.getText().toString().trim();
        String valueStr = unitValueInput.getText().toString().trim();

        if (category.isEmpty() || fromUnit.isEmpty() || toUnit.isEmpty()) {
            toast(getString(R.string.toast_fill_fields));
            return;
        }

        double value;
        try {
            value = Double.parseDouble(valueStr);
        } catch (NumberFormatException e) {
            toast(getString(R.string.toast_invalid_value));
            return;
        }

        java.util.Map<String, Double> units = UNIT_DATA.get(category);
        if (units == null) {
            toast(getString(R.string.toast_unknown_category, category));
            return;
        }

        Double fromFactor = units.get(fromUnit);
        Double toFactor = units.get(toUnit);
        if (fromFactor == null || toFactor == null) {
            toast(getString(R.string.toast_invalid_unit));
            return;
        }

        double result;
        if ("Temperature".equals(category)) {
            result = convertTemperature(value, fromUnit, toUnit);
        } else {
            result = value * fromFactor / toFactor;
        }

        unitResultInput.setText(fmt(result));
        resultView.append(value + " " + fromUnit + " = " + fmt(result) + " " + toUnit + "\n");
    }

    private double convertTemperature(double value, String from, String to) {
        if (from.equals(to)) return value;
        double celsius;
        if (from.contains("Fahrenheit")) {
            celsius = (value - 32) * 5.0 / 9.0;
        } else if (from.contains("Kelvin")) {
            celsius = value - 273.15;
        } else {
            celsius = value;
        }
        if (to.contains("Fahrenheit")) {
            return celsius * 9.0 / 5.0 + 32;
        } else if (to.contains("Kelvin")) {
            return celsius + 273.15;
        } else {
            return celsius;
        }
    }

    // ------------------------------------------------------------------
    //  Perpetual Calendar / Date Calculator
    // ------------------------------------------------------------------
    private EditText calDate1Input, calDate2Input, calDaysInput;
    private TextView calResultView;

    private void setupCalendar() {
        calDate1Input = findViewById(R.id.cal_date1_input);
        calDate2Input = findViewById(R.id.cal_date2_input);
        calDaysInput = findViewById(R.id.cal_days_input);
        calResultView = findViewById(R.id.cal_result_view);

        MaterialButton btnToday = findViewById(R.id.btn_cal_today);
        btnToday.setOnClickListener(v -> onCalToday());

        MaterialButton btnDow = findViewById(R.id.btn_cal_dow);
        btnDow.setOnClickListener(v -> onCalDayOfWeek());

        MaterialButton btnDiff = findViewById(R.id.btn_cal_diff);
        btnDiff.setOnClickListener(v -> onCalDiff());

        MaterialButton btnAdd = findViewById(R.id.btn_cal_add);
        btnAdd.setOnClickListener(v -> onCalAddDays());
    }

    private LocalDate calParseDate(String text) {
        if (text == null) return null;
        String s = text.trim();
        if (s.isEmpty()) return null;
        try {
            return LocalDate.parse(s);
        } catch (Exception e) {
            return null;
        }
    }

    private void onCalToday() {
        calDate1Input.setText(LocalDate.now().toString());
    }

    private void onCalDayOfWeek() {
        LocalDate d = calParseDate(calDate1Input.getText().toString());
        if (d == null) {
            toast(getString(R.string.toast_cal_invalid_date));
            return;
        }
        String[] daysEn = {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"};
        String[] daysZh = {"一", "二", "三", "四", "五", "六", "日"};
        int dow = d.getDayOfWeek().getValue() - 1;
        boolean isZh = getResources().getConfiguration().locale.getLanguage().equals("zh");
        String dowStr = isZh ? daysZh[dow] : daysEn[dow];
        String msg = isZh
            ? d.getYear() + "年" + d.getMonthValue() + "月" + d.getDayOfMonth() + "日是星期" + dowStr
            : d + " is a " + dowStr;
        calResultView.setText(msg);
    }

    private void onCalDiff() {
        LocalDate d1 = calParseDate(calDate1Input.getText().toString());
        LocalDate d2 = calParseDate(calDate2Input.getText().toString());
        if (d1 == null || d2 == null) {
            toast(getString(R.string.toast_cal_invalid_date));
            return;
        }
        long diff = ChronoUnit.DAYS.between(d1, d2);
        boolean isZh = getResources().getConfiguration().locale.getLanguage().equals("zh");
        String msg = isZh ? "两日期相差：" + diff + " 天" : "Days between dates: " + diff;
        calResultView.setText(msg);
    }

    private void onCalAddDays() {
        LocalDate d = calParseDate(calDate1Input.getText().toString());
        if (d == null) {
            toast(getString(R.string.toast_cal_invalid_date));
            return;
        }
        int add;
        try {
            add = Integer.parseInt(calDaysInput.getText().toString().trim());
        } catch (NumberFormatException e) {
            toast(getString(R.string.toast_cal_invalid_input));
            return;
        }
        LocalDate result = d.plusDays(add);
        calDate2Input.setText(result.toString());
        boolean isZh = getResources().getConfiguration().locale.getLanguage().equals("zh");
        String msg = isZh
            ? d.toString() + " 加 " + add + " 天 = " + result
            : d + " + " + add + " days = " + result;
        calResultView.setText(msg);
    }

    // ------------------------------------------------------------------
    //  Number Theory Calculator
    // ------------------------------------------------------------------
    private boolean ntIsPrime(long n) {
        if (n < 2) return false;
        if (n < 4) return true;
        if (n % 2 == 0 || n % 3 == 0) return false;
        long i = 5;
        while (i * i <= n) {
            if (n % i == 0 || n % (i + 2) == 0) return false;
            i += 6;
        }
        return true;
    }

    private String ntFactorize(long n) {
        if (n <= 1) return String.valueOf(n);
        java.util.List<String> parts = new java.util.ArrayList<>();
        long d = 2;
        while (d * d <= n) {
            int count = 0;
            while (n % d == 0) {
                count++;
                n /= d;
            }
            if (count > 0) {
                if (count == 1) parts.add(String.valueOf(d));
                else parts.add(d + "^" + count);
            }
            d++;
        }
        if (n > 1) parts.add(String.valueOf(n));
        return String.join(" × ", parts);
    }

    private long ntGcd(long a, long b) {
        a = Math.abs(a);
        b = Math.abs(b);
        while (b != 0) {
            long t = b;
            b = a % b;
            a = t;
        }
        return a;
    }

    private long ntLcm(long a, long b) {
        if (a == 0 || b == 0) return 0;
        return Math.abs(a / ntGcd(a, b) * b);
    }

    private long ntFibonacci(int n) {
        if (n <= 0) return 0;
        if (n == 1) return 1;
        if (n == 2) return 1;
        long a = 1, b = 1;
        for (int i = 3; i <= n; i++) {
            long t = a + b;
            a = b;
            b = t;
        }
        return b;
    }

    private long ntModPow(long base, long exp, long mod) {
        if (mod <= 0) throw new ArithmeticException("mod must be positive");
        if (mod == 1) return 0;
        
        // Handle negative exponents
        if (exp < 0) {
            // Compute modular inverse first
            long inv = ntModInverse(base, mod);
            if (inv == -1) throw new ArithmeticException("No modular inverse exists");
            base = inv;
            exp = -exp;
        }
        
        long result = 1;
        base = base % mod;
        while (exp > 0) {
            if ((exp & 1) == 1) {
                // Use BigInteger to avoid overflow
                result = java.math.BigInteger.valueOf(result)
                    .multiply(java.math.BigInteger.valueOf(base))
                    .mod(java.math.BigInteger.valueOf(mod))
                    .longValue();
            }
            exp >>= 1;
            base = java.math.BigInteger.valueOf(base)
                .multiply(java.math.BigInteger.valueOf(base))
                .mod(java.math.BigInteger.valueOf(mod))
                .longValue();
        }
        return result;
    }
    
    private long ntModInverse(long a, long m) {
        // Extended Euclidean Algorithm
        long m0 = m;
        long y = 0, x = 1;
        
        if (m == 1) return 0;
        
        while (a > 1) {
            long q = a / m;
            long t = m;
            m = a % m;
            a = t;
            t = y;
            y = x - q * y;
            x = t;
        }
        
        if (x < 0) x += m0;
        
        return x;
    }

    private long ntTotient(long n) {
        if (n <= 0) return 0;
        long result = n;
        long temp = n;
        for (long p = 2; p * p <= temp; p++) {
            if (temp % p == 0) {
                while (temp % p == 0) temp /= p;
                result -= result / p;
            }
        }
        if (temp > 1) result -= result / temp;
        return result;
    }

    private void onNtFactorize(EditText nInput) {
        long n;
        try { n = Long.parseLong(nInput.getText().toString().trim()); }
        catch (NumberFormatException e) { toast(getString(R.string.toast_nt_invalid_n)); return; }
        if (n <= 0) { toast(getString(R.string.toast_nt_invalid_n)); return; }
        if (n > 1_000_000_000_000L) { toast(getString(R.string.toast_nt_n_too_large)); return; }
        String result = ntFactorize(n);
        resultView.append(String.format(getString(R.string.nt_factorize_result), n, result) + "\n");
    }

    private void onNtIsPrime(EditText nInput) {
        long n;
        try { n = Long.parseLong(nInput.getText().toString().trim()); }
        catch (NumberFormatException e) { toast(getString(R.string.toast_nt_invalid_n)); return; }
        if (n <= 0) { toast(getString(R.string.toast_nt_invalid_n)); return; }
        if (ntIsPrime(n)) {
            resultView.append(String.format(getString(R.string.nt_prime_result), n) + "\n");
        } else {
            resultView.append(String.format(getString(R.string.nt_composite_result), n, ntFactorize(n)) + "\n");
        }
    }

    private void onNtGcd(EditText aInput, EditText bInput) {
        long a, b;
        try {
            a = Long.parseLong(aInput.getText().toString().trim());
            b = Long.parseLong(bInput.getText().toString().trim());
        } catch (NumberFormatException e) { toast(getString(R.string.toast_nt_invalid_ab)); return; }
        resultView.append(String.format(getString(R.string.nt_gcd_result), a, b, ntGcd(a, b)) + "\n");
    }

    private void onNtLcm(EditText aInput, EditText bInput) {
        long a, b;
        try {
            a = Long.parseLong(aInput.getText().toString().trim());
            b = Long.parseLong(bInput.getText().toString().trim());
        } catch (NumberFormatException e) { toast(getString(R.string.toast_nt_invalid_ab)); return; }
        resultView.append(String.format(getString(R.string.nt_lcm_result), a, b, ntLcm(a, b)) + "\n");
    }

    private void onNtFibonacci(EditText nInput) {
        int n;
        try { n = Integer.parseInt(nInput.getText().toString().trim()); }
        catch (NumberFormatException e) { toast(getString(R.string.toast_nt_invalid_n)); return; }
        if (n <= 0 || n > 1000) { toast(getString(R.string.toast_nt_invalid_n)); return; }
        StringBuilder sb = new StringBuilder(String.format(getString(R.string.nt_fibonacci_result), n, ntFibonacci(n)) + ":\n");
        for (int i = 1; i <= Math.min(n, 20); i++) {
            sb.append("F(").append(i).append(") = ").append(ntFibonacci(i));
            if (i < Math.min(n, 20)) sb.append("\n");
        }
        if (n > 20) sb.append("\n").append(String.format(getString(R.string.nt_factorize_showing), n));
        resultView.append(sb.toString() + "\n");
    }

    private void onNtModPow(EditText baseInput, EditText expInput, EditText modInput) {
        long base, exp, mod;
        try {
            base = Long.parseLong(baseInput.getText().toString().trim());
            exp = Long.parseLong(expInput.getText().toString().trim());
            mod = Long.parseLong(modInput.getText().toString().trim());
        } catch (NumberFormatException e) { toast(getString(R.string.toast_nt_invalid_modpow)); return; }
        if (mod <= 0) { toast(getString(R.string.toast_nt_invalid_modpow)); return; }
        long result = ntModPow(base, exp, mod);
        resultView.append(String.format(getString(R.string.nt_modpow_result), base, exp, mod, result) + "\n");
    }

    private void onNtTotient(EditText nInput) {
        long n;
        try { n = Long.parseLong(nInput.getText().toString().trim()); }
        catch (NumberFormatException e) { toast(getString(R.string.toast_nt_invalid_n)); return; }
        if (n <= 0) { toast(getString(R.string.toast_nt_invalid_n)); return; }
        resultView.append(String.format(getString(R.string.nt_totient_result), n, ntTotient(n)) + "\n");
    }
}
