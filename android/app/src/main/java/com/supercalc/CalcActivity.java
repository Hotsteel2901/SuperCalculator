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
import java.util.List;

public class CalcActivity extends AppCompatActivity {

    private EditText exprInput, xInput, aInput, bInput, guessInput;
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
