package com.supercalc;

import android.content.Intent;
import android.os.Bundle;
import android.text.method.ScrollingMovementMethod;
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
            line += "Error: " + CalcEngine.getLastError();
        } else if (Double.isInfinite(value)) {
            line += (value > 0 ? "+Inf" : "-Inf");
        } else {
            line += String.format("%.10g", value);
        }
        resultView.append(line + "\n");
    }

    private void appendResult(String label, int value) {
        String line = label + " = " + value + " points plotted";
        resultView.append(line + "\n");
    }

    private void onEvaluate() {
        String e = getExpr(); if (e.isEmpty()) { toast("Enter an expression"); return; }
        appendResult("f(" + fmt(getX()) + ")", CalcEngine.evaluate(e, getX()));
    }

    private void onDerivative() {
        String e = getExpr(); if (e.isEmpty()) { toast("Enter an expression"); return; }
        appendResult("f'(" + fmt(getX()) + ")", CalcEngine.derivative(e, getX(), 1e-6));
    }

    private void onDerivative2() {
        String e = getExpr(); if (e.isEmpty()) { toast("Enter an expression"); return; }
        appendResult("f''(" + fmt(getX()) + ")", CalcEngine.derivative2(e, getX(), 1e-6));
    }

    private void onIntegrate() {
        String e = getExpr(); if (e.isEmpty()) { toast("Enter an expression"); return; }
        appendResult("I[" + fmt(getA()) + "," + fmt(getB()) + "]",
                     CalcEngine.integrate(e, getA(), getB()));
    }

    private void onSolve() {
        String e = getExpr(); if (e.isEmpty()) { toast("Enter an expression"); return; }
        double root = CalcEngine.solve(e, getGuess(), getA(), getB());
        if (Double.isNaN(root)) {
            appendResult("Root", Double.NaN);
        } else {
            appendResult("Root", root);
            appendResult("  f(root)", CalcEngine.evaluate(e, root));
        }
    }

    private void onFindExtremum(boolean minimum) {
        String e = getExpr(); if (e.isEmpty()) { toast("Enter an expression"); return; }
        double a = getA();
        double b = getB();
        double result;
        String label;
        if (minimum) {
            result = CalcEngine.findMinimum(e, a, b);
            label = "Min";
        } else {
            result = CalcEngine.findMaximum(e, a, b);
            label = "Max";
        }
        if (Double.isNaN(result)) {
            appendResult(label, Double.NaN);
        } else {
            appendResult(label + " at x", result);
            appendResult("  f(" + fmt(result) + ")", CalcEngine.evaluate(e, result));
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
        if (e.isEmpty()) { toast("Enter an expression"); return; }
        double a = getA();
        double b = getB();
        if (a >= b) { toast("a must be less than b"); return; }

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
            resultView.append("Scan Roots: Error: " + CalcEngine.getLastError() + "\n");
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
            resultView.append("Scan Roots: No roots found in [" + fmt(a) + ", " + fmt(b) + "]\n");
        } else {
            resultView.append("Scan Roots: Found " + uniqueRoots.size() + " root(s) in [" + fmt(a) + ", " + fmt(b) + "]\n");
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
        if (e.isEmpty()) { toast("Enter an expression"); return; }
        double x0 = getX();
        double y0 = CalcEngine.evaluate(e, x0);
        double slope = CalcEngine.derivative(e, x0, 1e-6);
        if (Double.isNaN(y0) || Double.isNaN(slope)) {
            resultView.append((tangent ? "Tangent" : "Normal") + ": Error: " + CalcEngine.getLastError() + "\n");
            return;
        }
        String label = tangent ? "Tangent" : "Normal";
        if (tangent) {
            resultView.append(label + " at x=" + fmt(x0) + ": y = " + fmt(slope) + "*(x-" + fmt(x0) + ") + " + fmt(y0) + "\n");
        } else {
            if (Math.abs(slope) < 1e-12) {
                resultView.append(label + " at x=" + fmt(x0) + ": vertical line x = " + fmt(x0) + "\n");
            } else {
                double ns = -1.0 / slope;
                resultView.append(label + " at x=" + fmt(x0) + ": y = " + fmt(ns) + "*(x-" + fmt(x0) + ") + " + fmt(y0) + "\n");
            }
        }
    }

    private void onArcLength() {
        String e = getExpr();
        if (e.isEmpty()) { toast("Enter an expression"); return; }
        double a = getA();
        double b = getB();
        if (a >= b) { toast("a must be less than b"); return; }

        int n = 5000;
        double h = (b - a) / n;
        double[] xs = new double[n + 1];
        for (int i = 0; i <= n; i++) {
            xs[i] = a + i * h;
        }
        double[] ys = CalcEngine.evaluateArray(e, xs);
        if (ys == null) {
            resultView.append("Arc Length: Error: " + CalcEngine.getLastError() + "\n");
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
        resultView.append("Arc Length [" + fmt(a) + ", " + fmt(b) + "] = " + fmt(length) + "\n");
    }

    private void onAreaBetweenCurves() {
        String eF = getExpr();
        String eG = areaGInput.getText().toString().trim();
        if (eF.isEmpty()) { toast("Enter f(x) expression"); return; }
        if (eG.isEmpty()) { toast("Enter g(x) expression"); return; }
        double a = getA();
        double b = getB();
        if (a >= b) { toast("a must be less than b"); return; }

        double result = CalcEngine.areaBetweenCurves(eF, eG, a, b);
        if (Double.isNaN(result)) {
            String err = CalcEngine.getLastError();
            resultView.append("Area Between Curves: Error: " + (err.isEmpty() ? "computation failed" : err) + "\n");
            return;
        }
        resultView.append("Area between f(x)=" + eF + " and g(x)=" + eG + "\n  [" + fmt(a) + ", " + fmt(b) + "] = " + fmt(result) + "\n");
    }

    @SuppressWarnings("unchecked")
    private void onSolveSystem2d() {
        String fExpr = sysFInput.getText().toString().trim();
        String gExpr = sysGInput.getText().toString().trim();
        if (fExpr.isEmpty() || gExpr.isEmpty()) {
            toast("Enter both f(x,y) and g(x,y) expressions");
            return;
        }
        double x0, y0;
        try {
            x0 = Double.parseDouble(sysX0Input.getText().toString().trim());
            y0 = Double.parseDouble(sysY0Input.getText().toString().trim());
        } catch (NumberFormatException ex) {
            toast("Invalid initial guess");
            return;
        }

        HashMap<String, Object> result = CalcEngine.solveSystem2d(fExpr, gExpr, x0, y0);
        if (result == null) {
            String err = CalcEngine.getLastError();
            resultView.append("System Solver: Error: " + (err.isEmpty() ? "computation failed" : err) + "\n");
            return;
        }

        Object xObj = result.get("x");
        Object yObj = result.get("y");
        if (xObj == null || yObj == null) {
            resultView.append("System Solver: Invalid result\n");
            return;
        }

        double xSol = (double) xObj;
        double ySol = (double) yObj;
        double fVal = CalcEngine.evaluateXY(fExpr, xSol, ySol);
        double gVal = CalcEngine.evaluateXY(gExpr, xSol, ySol);

        StringBuilder sb = new StringBuilder();
        sb.append("f(x,y) = ").append(fExpr).append("\n");
        sb.append("g(x,y) = ").append(gExpr).append("\n\n");
        sb.append("Solution:\n");
        sb.append("  x = ").append(fmt(xSol)).append("\n");
        sb.append("  y = ").append(fmt(ySol)).append("\n\n");
        sb.append("Residuals:\n");
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
            .setTitle("System Solution")
            .setView(sv)
            .setPositiveButton("Close", null)
            .show();

        resultView.append("System solved: x=" + fmt(xSol) + ", y=" + fmt(ySol) + "\n");
    }

    private void onFFT() {
        String e = getExpr();
        if (e.isEmpty()) { toast("Enter an expression"); return; }
        double a = getA();
        double b = getB();
        if (a >= b) { toast("a must be less than b"); return; }
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
        sb.append("Dominant: f=").append(fmt(freqs[peakIdx]))
          .append(" A=").append(fmt(amps[peakIdx])).append("\n\n");
        int show = Math.min(m, 16);
        sb.append("Freq\t\tAmp\t\tPhase\n");
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
            .setTitle("FFT Spectrum")
            .setView(sv)
            .setPositiveButton("Close", null)
            .show();

        resultView.append("FFT: dominant f=" + fmt(freqs[peakIdx]) + " A=" + fmt(amps[peakIdx]) + "\n");
    }

    private void onLimit() {
        String e = getExpr();
        if (e.isEmpty()) { toast("Enter an expression"); return; }
        double a = getX();

        double left  = CalcEngine.limitLeft(e, a);
        double right = CalcEngine.limitRight(e, a);

        if (Double.isNaN(left) && Double.isNaN(right)) {
            resultView.append("lim(x→" + fmt(a) + "): Error: " + CalcEngine.getLastError() + "\n");
            return;
        }

        if (!Double.isNaN(left) && !Double.isNaN(right) && Math.abs(left - right) < 1e-8) {
            double val = (left + right) / 2.0;
            resultView.append("lim(x→" + fmt(a) + ") = " + fmt(val) + "\n");
            resultView.append("  Left:  " + fmt(left) + "\n");
            resultView.append("  Right: " + fmt(right) + "\n");
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
            resultView.append("Two-sided limit does not exist.\n");
        }
    }

    private void onLimitSide(boolean left) {
        String e = getExpr();
        if (e.isEmpty()) { toast("Enter an expression"); return; }
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
        if (e.isEmpty()) { toast("Enter an expression"); return; }
        double a = getX();
        int order = getTaylorOrder();

        double[] coeffs = CalcEngine.taylorCoefficients(e, a, order);
        if (coeffs == null) {
            resultView.append("Taylor: Error: " + CalcEngine.getLastError() + "\n");
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
            .setTitle("Taylor Series Expansion")
            .setView(sv)
            .setPositiveButton("Close", null)
            .show();

        resultView.append("Taylor at a=" + fmt(a) + " (order " + order + ")\n");
    }

    private void onOdeSolve() {
        String expr = odeExprInput.getText().toString().trim();
        if (expr.isEmpty()) { toast("Enter ODE expression dy/dx = f(x,y)"); return; }
        double x0, y0, xEnd;
        int steps;
        try {
            x0 = Double.parseDouble(odeX0Input.getText().toString().trim());
            y0 = Double.parseDouble(odeY0Input.getText().toString().trim());
            xEnd = Double.parseDouble(odeXEndInput.getText().toString().trim());
            steps = Integer.parseInt(odeStepsInput.getText().toString().trim());
        } catch (NumberFormatException ex) {
            toast("Invalid ODE parameters");
            return;
        }
        if (steps < 1 || steps > 100000) { toast("Steps must be 1-100000"); return; }
        if (x0 == xEnd) { toast("x0 must not equal x end"); return; }

        HashMap<String, Object> result = CalcEngine.odeSolveRk4(expr, x0, y0, xEnd, steps);
        if (result == null) {
            resultView.append("ODE Error: " + CalcEngine.getLastError() + "\n");
            return;
        }

        Object xsObj = result.get("xs");
        Object ysObj = result.get("ys");
        Object countObj = result.get("count");
        if (xsObj == null || ysObj == null || countObj == null) {
            resultView.append("ODE Error: Invalid result from solver\n");
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
            .setTitle("ODE Solution (RK4)")
            .setView(sv)
            .setPositiveButton("Close", null)
            .show();

        resultView.append("ODE solved: " + count + " points\n");
    }

    private void onOdePlot() {
        String expr = odeExprInput.getText().toString().trim();
        if (expr.isEmpty()) { toast("Enter ODE expression dy/dx = f(x,y)"); return; }
        double x0, y0, xEnd;
        int steps;
        try {
            x0 = Double.parseDouble(odeX0Input.getText().toString().trim());
            y0 = Double.parseDouble(odeY0Input.getText().toString().trim());
            xEnd = Double.parseDouble(odeXEndInput.getText().toString().trim());
            steps = Integer.parseInt(odeStepsInput.getText().toString().trim());
        } catch (NumberFormatException ex) {
            toast("Invalid ODE parameters");
            return;
        }
        if (steps < 1 || steps > 100000) { toast("Steps must be 1-100000"); return; }
        if (x0 == xEnd) { toast("x0 must not equal x end"); return; }

        HashMap<String, Object> result = CalcEngine.odeSolveRk4(expr, x0, y0, xEnd, steps);
        if (result == null) {
            resultView.append("ODE Error: " + CalcEngine.getLastError() + "\n");
            return;
        }

        Object xsObj = result.get("xs");
        Object ysObj = result.get("ys");
        if (xsObj == null || ysObj == null) {
            resultView.append("ODE Error: Invalid result from solver\n");
            return;
        }

        double[] xsFull = (double[]) xsObj;
        double[] ysFull = (double[]) ysObj;

        // Downsample to avoid TransactionTooLargeException (~1MB Intent limit)
        int maxPoints = 2000;
        double[] xs, ys;
        if (xsFull.length > maxPoints) {
            int step = Math.max(1, xsFull.length / maxPoints);
            xs = new double[xsFull.length / step + 1];
            ys = new double[ysFull.length / step + 1];
            int idx = 0;
            for (int i = 0; i < xsFull.length; i += step) {
                xs[idx] = xsFull[i];
                ys[idx] = ysFull[i];
                idx++;
            }
            // Always include the last point
            if ((xsFull.length - 1) % step != 0) {
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
        if (e.isEmpty()) { toast("Enter an expression"); return; }
        double a = getX();
        int order = getTaylorOrder();

        double rangeA = getA();
        double rangeB = getB();
        if (rangeA >= rangeB) { toast("Set a < b for plot range"); return; }

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
        if (raw.isEmpty()) { toast("Enter data points"); return null; }
        String[] tokens = raw.split("[,;\\s]+");
        java.util.ArrayList<Double> values = new java.util.ArrayList<>();
        for (String t : tokens) {
            t = t.trim();
            if (t.isEmpty()) continue;
            try {
                values.add(Double.parseDouble(t));
            } catch (NumberFormatException e) {
                toast("Invalid number: " + t);
                return null;
            }
        }
        if (values.isEmpty()) { toast("No valid numbers entered"); return null; }
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
        sb.append("Statistics for ").append(n).append(" data points:\n\n");
        sb.append(String.format("  Sum       = %.10g\n", sum));
        sb.append(String.format("  Mean      = %.10g\n", mean));
        sb.append(String.format("  Median    = %.10g\n", median));
        sb.append(String.format("  Min       = %.10g\n", min));
        sb.append(String.format("  Max       = %.10g\n", max));
        sb.append(String.format("  Range     = %.10g\n", range));
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
            .setTitle("Statistics Results")
            .setView(sv)
            .setPositiveButton("Close", null)
            .show();

        resultView.append("Stats: n=" + n + ", mean=" + fmt(mean) + ", std=" + fmt(stdPop) + "\n");
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
        toast("Data sorted (" + data.length + " values)");
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
                    toast("Invalid number: " + c);
                    return null;
                }
            }
            if (vals.isEmpty()) continue;
            if (ncols < 0) ncols = vals.size();
            else if (vals.size() != ncols) {
                toast("All rows must have same columns");
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
            .setPositiveButton("Close", null)
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
        if (a.length != b.length || a[0].length != b[0].length) { toast("Dimensions must match"); return; }
        double[][] r = new double[a.length][a[0].length];
        for (int i = 0; i < a.length; i++)
            for (int j = 0; j < a[0].length; j++)
                r[i][j] = a[i][j] + b[i][j];
        showMatrixResult("A + B", formatMatrix(r));
        resultView.append("Matrix A + B computed\n");
    }

    private void onMatrixSub() {
        double[][] a = getMatrixA(); double[][] b = getMatrixB();
        if (a == null || b == null) return;
        if (a.length != b.length || a[0].length != b[0].length) { toast("Dimensions must match"); return; }
        double[][] r = new double[a.length][a[0].length];
        for (int i = 0; i < a.length; i++)
            for (int j = 0; j < a[0].length; j++)
                r[i][j] = a[i][j] - b[i][j];
        showMatrixResult("A - B", formatMatrix(r));
        resultView.append("Matrix A - B computed\n");
    }

    private void onMatrixMul() {
        double[][] a = getMatrixA(); double[][] b = getMatrixB();
        if (a == null || b == null) return;
        if (a[0].length != b.length) { toast("Cols of A must equal rows of B"); return; }
        double[][] r = new double[a.length][b[0].length];
        for (int i = 0; i < a.length; i++)
            for (int j = 0; j < b[0].length; j++) {
                double sum = 0;
                for (int k = 0; k < a[0].length; k++) sum += a[i][k] * b[k][j];
                r[i][j] = sum;
            }
        showMatrixResult("A * B", formatMatrix(r));
        resultView.append("Matrix A * B computed\n");
    }

    private void onMatrixDet() {
        double[][] a = getMatrixA();
        if (a == null) return;
        if (a.length != a[0].length) { toast("Determinant requires square matrix"); return; }
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
        if (a.length != a[0].length) { toast("Inverse requires square matrix"); return; }
        double detA = det(a);
        if (Math.abs(detA) < 1e-12) { toast("Matrix is singular"); return; }
        int n = a.length;
        double[][] inv = new double[n][n];
        double[][] adj = new double[n][n];
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                double[][] sub = new double[n-1][n-1];
                int si = 0;
                for (int ii = 0; ii < n; ii++) {
                    if (ii == i) continue;
                    int sj = 0;
                    for (int jj = 0; jj < n; jj++) {
                        if (jj == j) continue;
                        sub[si][sj++] = a[ii][jj];
                    }
                    si++;
                }
                adj[j][i] = Math.pow(-1, i+j) * det(sub);
                inv[i][j] = adj[j][i] / detA;
            }
        }
        showMatrixResult("inv(A)", formatMatrix(inv));
        resultView.append("Matrix inverse computed\n");
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
        resultView.append("Matrix transpose computed\n");
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
        showMatrixResult("rank(A)", "rank(A) = " + rank);
        resultView.append("rank(A) = " + rank + "\n");
    }

    private void onMatrixEigen() {
        double[][] a = getMatrixA();
        if (a == null) return;
        if (a.length != a[0].length) { toast("Eigenvalues require square matrix"); return; }
        // For 2x2: use characteristic equation
        if (a.length == 2) {
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
            // For larger matrices: iterative power method approximation
            // Simple eigenvalue estimation using Gershgorin circles
            StringBuilder sb = new StringBuilder();
            sb.append("Gershgorin circle eigenvalue bounds:\n\n");
            for (int i = 0; i < a.length; i++) {
                double center = a[i][i];
                double radius = 0;
                for (int j = 0; j < a[0].length; j++) {
                    if (i != j) radius += Math.abs(a[i][j]);
                }
                sb.append("  Circle ").append(i+1).append(": center=")
                  .append(fmt(center)).append(", radius=").append(fmt(radius))
                  .append("\n");
                sb.append("    eigenvalue in [").append(fmt(center - radius))
                  .append(", ").append(fmt(center + radius)).append("]\n");
            }
            showMatrixResult("Eigenvalue Bounds", sb.toString());
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
        sb.append("Histogram (").append(nBins).append(" bins)\n");
        sb.append("Mean=").append(fmt(mean)).append(" Median=").append(fmt(median)).append("\n\n");

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
            .setTitle("Histogram")
            .setView(sv)
            .setPositiveButton("Close", null)
            .show();

        resultView.append("Histogram: " + nBins + " bins, mean=" + fmt(mean) + "\n");
    }

    private void onPlotParametric() {
        String xExpr = xParamInput.getText().toString().trim();
        String yExpr = yParamInput.getText().toString().trim();
        if (xExpr.isEmpty() || yExpr.isEmpty()) {
            toast("Enter both x(t) and y(t) expressions");
            return;
        }

        double tMin, tMax;
        try {
            tMin = Double.parseDouble(tMinInput.getText().toString().trim());
            tMax = Double.parseDouble(tMaxInput.getText().toString().trim());
        } catch (NumberFormatException ex) {
            toast("Invalid t range");
            return;
        }
        if (tMin >= tMax) {
            toast("t min must be less than t max");
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
            resultView.append("Parametric: Error: " + CalcEngine.getLastError() + "\n");
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
            toast("Enter an r(theta) expression");
            return;
        }

        double thetaMin, thetaMax;
        try {
            thetaMin = Double.parseDouble(thetaMinInput.getText().toString().trim());
            thetaMax = Double.parseDouble(thetaMaxInput.getText().toString().trim());
        } catch (NumberFormatException ex) {
            toast("Invalid theta range");
            return;
        }
        if (thetaMin >= thetaMax) {
            toast("theta min must be less than theta max");
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
            resultView.append("Polar: Error: " + CalcEngine.getLastError() + "\n");
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
        if (e.isEmpty()) { toast("Enter an expression"); return; }
        double a = getA();
        double b = getB();
        if (a >= b) { toast("a must be less than b for table range"); return; }
        int n = 21; // default points

        double step = (b - a) / (n - 1);
        double[] xs = new double[n];
        for (int i = 0; i < n; i++) {
            xs[i] = a + i * step;
        }
        double[] ys = CalcEngine.evaluateArray(e, xs);
        if (ys == null) {
            resultView.append("Table: Error: " + CalcEngine.getLastError() + "\n");
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
        sb.append("Valid: ").append(valid).append(" / ").append(n).append("\n");

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
            .setTitle("Function Table (" + n + " pts)")
            .setView(scrollView)
            .setPositiveButton("Share CSV", (dialog, which) -> shareText(csvText, "SuperCalc Table"))
            .setNegativeButton("Close", null)
            .show();

        resultView.append("Table generated: " + valid + "/" + n + " valid points\n");
    }

    private void shareText(String text, String title) {
        Intent shareIntent = new Intent(Intent.ACTION_SEND);
        shareIntent.setType("text/plain");
        shareIntent.putExtra(Intent.EXTRA_SUBJECT, title);
        shareIntent.putExtra(Intent.EXTRA_TEXT, text);
        startActivity(Intent.createChooser(shareIntent, "Share table"));
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
}
