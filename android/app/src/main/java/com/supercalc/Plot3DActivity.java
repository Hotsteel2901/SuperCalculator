package com.supercalc;

import android.content.Intent;
import android.os.Bundle;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import com.google.android.material.appbar.MaterialToolbar;
import com.google.android.material.button.MaterialButton;
import com.google.android.material.textfield.TextInputEditText;

public class Plot3DActivity extends AppCompatActivity {

    private Surface3DView surface3DView;
    private TextInputEditText exprInput, xMinInput, xMaxInput, yMinInput, yMaxInput, zMinInput, zMaxInput;

    private String lastExpression;
    private float lastXMin, lastXMax, lastYMin, lastYMax, lastZMin, lastZMax;
    private boolean hasPlot = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_plot_3d);

        MaterialToolbar toolbar = findViewById(R.id.toolbar);
        toolbar.setNavigationOnClickListener(v -> finish());

        surface3DView = findViewById(R.id.surface_3d_view);
        exprInput = findViewById(R.id.expr_3d_input);
        xMinInput = findViewById(R.id.x_min_3d_input);
        xMaxInput = findViewById(R.id.x_max_3d_input);
        yMinInput = findViewById(R.id.y_min_3d_input);
        yMaxInput = findViewById(R.id.y_max_3d_input);
        zMinInput = findViewById(R.id.z_min_3d_input);
        zMaxInput = findViewById(R.id.z_max_3d_input);

        MaterialButton btnPlot = findViewById(R.id.btn_plot_3d);
        MaterialButton btnReset = findViewById(R.id.btn_reset_3d_view);
        MaterialButton btnFullScreen = findViewById(R.id.btn_full_screen_3d);
        MaterialButton btnBack = findViewById(R.id.btn_back_3d);

        btnPlot.setOnClickListener(v -> onPlot3D());
        btnReset.setOnClickListener(v -> surface3DView.resetRotation());
        btnFullScreen.setOnClickListener(v -> openFullScreen3D());
        btnBack.setOnClickListener(v -> finish());

        // Default ranges
        xMinInput.setText("-10");
        xMaxInput.setText("10");
        yMinInput.setText("-10");
        yMaxInput.setText("10");
        zMinInput.setText("-10");
        zMaxInput.setText("10");

        // Pre-fill expression if passed from CalcActivity
        String initialExpr = getIntent().getStringExtra("initial_expr");
        if (initialExpr != null && !initialExpr.isEmpty()) {
            exprInput.setText(initialExpr);
        }
    }

    private void onPlot3D() {
        String expr = exprInput.getText().toString().trim();
        if (expr.isEmpty()) {
            toast("Enter an expression with x and y");
            return;
        }

        float xMin, xMax, yMin, yMax, zMin, zMax;
        try {
            xMin = Float.parseFloat(xMinInput.getText().toString().trim());
            xMax = Float.parseFloat(xMaxInput.getText().toString().trim());
            yMin = Float.parseFloat(yMinInput.getText().toString().trim());
            yMax = Float.parseFloat(yMaxInput.getText().toString().trim());
            zMin = Float.parseFloat(zMinInput.getText().toString().trim());
            zMax = Float.parseFloat(zMaxInput.getText().toString().trim());
        } catch (NumberFormatException e) {
            toast("Invalid range values");
            return;
        }

        if (xMin >= xMax || yMin >= yMax || zMin >= zMax) {
            toast("Min must be less than max for each axis");
            return;
        }

        // Determine grid size: keep total points reasonable for mobile
        int gridSize = 35;
        int cols = gridSize;
        int rows = gridSize;

        float[][] zValues = new float[rows][cols];
        boolean hasValid = false;
        float actualZMin = Float.POSITIVE_INFINITY;
        float actualZMax = Float.NEGATIVE_INFINITY;

        // Batch evaluation: flatten the grid and evaluate all points in one JNI call
        double[] xs = new double[rows * cols];
        double[] ys = new double[rows * cols];
        for (int i = 0; i < rows; i++) {
            double y = yMin + (yMax - yMin) * i / (rows - 1);
            for (int j = 0; j < cols; j++) {
                double x = xMin + (xMax - xMin) * j / (cols - 1);
                int idx = i * cols + j;
                xs[idx] = x;
                ys[idx] = y;
            }
        }
        double[] zs = CalcEngine.evaluateXYArray(expr, xs, ys);
        if (zs == null) {
            toast("Error evaluating expression");
            return;
        }

        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                int idx = i * cols + j;
                double z = zs[idx];
                if (Double.isNaN(z) || Double.isInfinite(z)) {
                    zValues[i][j] = Float.NaN;
                } else {
                    float zf = (float) z;
                    zValues[i][j] = zf;
                    hasValid = true;
                    if (zf < actualZMin) actualZMin = zf;
                    if (zf > actualZMax) actualZMax = zf;
                }
            }
        }

        if (!hasValid) {
            toast("Could not evaluate expression");
            return;
        }

        // Auto-adjust Z range if all values fit within user-specified tighter bounds
        if (actualZMin > zMin) zMin = actualZMin;
        if (actualZMax < zMax) zMax = actualZMax;
        // Ensure zMin < zMax
        if (zMin >= zMax) {
            zMax = zMin + 1f;
        }

        surface3DView.setData(zValues, xMin, xMax, yMin, yMax, zMin, zMax);
        lastExpression = expr;
        lastXMin = xMin;
        lastXMax = xMax;
        lastYMin = yMin;
        lastYMax = yMax;
        lastZMin = zMin;
        lastZMax = zMax;
        hasPlot = true;
        toast("Plotted 3D surface");
    }

    private void openFullScreen3D() {
        if (!hasPlot) {
            toast("Plot a surface first");
            return;
        }

        Intent intent = new Intent(this, FullScreenPlot3DActivity.class);
        intent.putExtra("expression", lastExpression);
        intent.putExtra("x_min", lastXMin);
        intent.putExtra("x_max", lastXMax);
        intent.putExtra("y_min", lastYMin);
        intent.putExtra("y_max", lastYMax);
        intent.putExtra("z_min", lastZMin);
        intent.putExtra("z_max", lastZMax);
        startActivity(intent);
    }

    private void toast(String msg) {
        Toast.makeText(this, msg, Toast.LENGTH_SHORT).show();
    }
}
