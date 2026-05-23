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
        MaterialButton btnClear  = findViewById(R.id.btn_clear);

        btnEval  .setOnClickListener(v -> onEvaluate());
        btnDeriv .setOnClickListener(v -> onDerivative());
        btnDeriv2.setOnClickListener(v -> onDerivative2());
        btnInt   .setOnClickListener(v -> onIntegrate());
        btnSolve .setOnClickListener(v -> onSolve());
        btnPlot  .setOnClickListener(v -> openPlot());
        btnClear .setOnClickListener(v -> resultView.setText(""));

        // Preset chips — set expression text and auto-evaluate
        Chip chipSin = findViewById(R.id.chip_sin);
        Chip chipCos = findViewById(R.id.chip_cos);
        Chip chipX2  = findViewById(R.id.chip_x2);
        Chip chipExp = findViewById(R.id.chip_exp);

        chipSin.setOnClickListener(v -> { exprInput.setText("sin(x)"); onEvaluate(); });
        chipCos.setOnClickListener(v -> { exprInput.setText("cos(x)"); onEvaluate(); });
        chipX2 .setOnClickListener(v -> { exprInput.setText("x^2");     onEvaluate(); });
        chipExp.setOnClickListener(v -> { exprInput.setText("exp(-x)"); onEvaluate(); });
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

    private static String fmt(double v) {
        if (v == (long) v) return String.format("%d", (long) v);
        return String.format("%.6g", v);
    }

    private void toast(String msg) {
        Toast.makeText(this, msg, Toast.LENGTH_SHORT).show();
    }
}
