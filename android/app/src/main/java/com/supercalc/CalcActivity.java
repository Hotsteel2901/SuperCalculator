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

        double[] xs = (double[]) result.get("xs");
        double[] ys = (double[]) result.get("ys");
        int count = (int) result.get("count");

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

        double[] xs = (double[]) result.get("xs");
        double[] ys = (double[]) result.get("ys");

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
        intent.putExtra("initial_expr", e);
        intent.putExtra("x_min", rangeA);
        intent.putExtra("x_max", rangeB);
        intent.putExtra("taylor_order", order);
        intent.putExtra("taylor_a", a);
        intent.putExtra("is_taylor", true);
        startActivity(intent);
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
