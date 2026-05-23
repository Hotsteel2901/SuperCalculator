package com.supercalc;

import android.os.Bundle;
import android.text.method.ScrollingMovementMethod;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;

public class CalcActivity extends AppCompatActivity {

    private EditText exprInput, xInput, aInput, bInput, guessInput;
    private TextView resultView;

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

        Button btnEval  = findViewById(R.id.btn_evaluate);
        Button btnDeriv = findViewById(R.id.btn_derivative);
        Button btnDeriv2= findViewById(R.id.btn_derivative2);
        Button btnInt   = findViewById(R.id.btn_integrate);
        Button btnSolve = findViewById(R.id.btn_solve);
        Button btnClear = findViewById(R.id.btn_clear);

        btnEval  .setOnClickListener(v -> onEvaluate());
        btnDeriv .setOnClickListener(v -> onDerivative());
        btnDeriv2.setOnClickListener(v -> onDerivative2());
        btnInt   .setOnClickListener(v -> onIntegrate());
        btnSolve .setOnClickListener(v -> onSolve());
        btnClear .setOnClickListener(v -> resultView.setText(""));

        // presets
        findViewById(R.id.btn_sin)  .setOnClickListener(v -> exprInput.setText("sin(x)"));
        findViewById(R.id.btn_cos)  .setOnClickListener(v -> exprInput.setText("cos(x)"));
        findViewById(R.id.btn_x2)   .setOnClickListener(v -> exprInput.setText("x^2"));
        findViewById(R.id.btn_exp)  .setOnClickListener(v -> exprInput.setText("exp(-x)"));
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

    private void onEvaluate() {
        String e = getExpr(); if (e.isEmpty()) { toast("Enter an expression"); return; }
        double x = getX();
        appendResult("f(" + x + ")", CalcEngine.evaluate(e, x));
    }

    private void onDerivative() {
        String e = getExpr(); if (e.isEmpty()) { toast("Enter an expression"); return; }
        double x = getX();
        appendResult("f'(" + x + ")", CalcEngine.derivative(e, x, 1e-6));
    }

    private void onDerivative2() {
        String e = getExpr(); if (e.isEmpty()) { toast("Enter an expression"); return; }
        double x = getX();
        appendResult("f''(" + x + ")", CalcEngine.derivative2(e, x, 1e-6));
    }

    private void onIntegrate() {
        String e = getExpr(); if (e.isEmpty()) { toast("Enter an expression"); return; }
        double a = getA(), b = getB();
        appendResult("I[" + a + "," + b + "]", CalcEngine.integrate(e, a, b));
    }

    private void onSolve() {
        String e = getExpr(); if (e.isEmpty()) { toast("Enter an expression"); return; }
        double g = getGuess(), lo = getA(), hi = getB();
        double root = CalcEngine.solve(e, g, lo, hi);
        if (Double.isNaN(root)) {
            appendResult("Root", Double.NaN);
        } else {
            appendResult("Root", root);
            double fv = CalcEngine.evaluate(e, root);
            appendResult("  f(root)", fv);
        }
    }

    private void toast(String msg) {
        Toast.makeText(this, msg, Toast.LENGTH_SHORT).show();
    }
}
