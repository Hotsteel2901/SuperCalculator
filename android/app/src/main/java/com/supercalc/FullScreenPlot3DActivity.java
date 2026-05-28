package com.supercalc;

import android.os.Bundle;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import com.google.android.material.button.MaterialButton;

public class FullScreenPlot3DActivity extends AppCompatActivity {

    private Surface3DView surface3DView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_full_screen_plot_3d);

        surface3DView = findViewById(R.id.full_screen_3d_view);
        MaterialButton btnExit = findViewById(R.id.btn_exit_3d);

        btnExit.setOnClickListener(v -> finish());

        loadAndPlotData();
    }

    private void loadAndPlotData() {
        String expr = getIntent().getStringExtra("expression");
        float xMin = getIntent().getFloatExtra("x_min", -10f);
        float xMax = getIntent().getFloatExtra("x_max", 10f);
        float yMin = getIntent().getFloatExtra("y_min", -10f);
        float yMax = getIntent().getFloatExtra("y_max", 10f);
        float zMin = getIntent().getFloatExtra("z_min", -10f);
        float zMax = getIntent().getFloatExtra("z_max", 10f);

        if (expr == null || expr.isEmpty()) {
            toast("No plot data received");
            return;
        }

        int targetPoints = 50;
        int cols = Math.max(targetPoints, 2);
        int rows = Math.max(targetPoints, 2);

        float[][] zValues = new float[rows][cols];
        boolean hasValid = false;
        float actualZMin = Float.POSITIVE_INFINITY;
        float actualZMax = Float.NEGATIVE_INFINITY;

        for (int i = 0; i < rows; i++) {
            double y = yMin + (yMax - yMin) * i / (rows - 1);
            for (int j = 0; j < cols; j++) {
                double x = xMin + (xMax - xMin) * j / (cols - 1);
                double z = CalcEngine.evaluateXY(expr, x, y);
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

        if (actualZMin > zMin) zMin = actualZMin;
        if (actualZMax < zMax) zMax = actualZMax;
        if (zMin >= zMax) {
            zMax = zMin + 1f;
        }

        surface3DView.setData(zValues, xMin, xMax, yMin, yMax, zMin, zMax);
    }

    private void toast(String msg) {
        Toast.makeText(this, msg, Toast.LENGTH_SHORT).show();
    }
}
