package com.supercalc;

import android.graphics.Color;
import android.os.Bundle;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import com.google.android.material.button.MaterialButton;
import com.google.android.material.textfield.TextInputEditText;
import com.github.mikephil.charting.charts.LineChart;
import com.github.mikephil.charting.data.Entry;
import com.github.mikephil.charting.data.LineData;
import com.github.mikephil.charting.data.LineDataSet;
import com.github.mikephil.charting.interfaces.datasets.ILineDataSet;
import com.github.mikephil.charting.components.XAxis;
import com.github.mikephil.charting.components.YAxis;
import com.github.mikephil.charting.components.Legend;
import com.github.mikephil.charting.components.Description;
import java.util.ArrayList;
import java.util.List;

public class PlotActivity extends AppCompatActivity {

    private LineChart lineChart;
    private TextInputEditText xMinInput, xMaxInput, yMinInput, yMaxInput;
    private TextInputEditText exprInput;
    
    private ArrayList<ArrayList<Entry>> allEntries;
    private ArrayList<String> allExpressions;
    private ArrayList<Integer> curveColors;
    
    private static final int[] COLOR_PALETTE = {
        Color.parseColor("#1f77b4"),
        Color.parseColor("#ff7f0e"),
        Color.parseColor("#2ca02c"),
        Color.parseColor("#d62728"),
        Color.parseColor("#9467bd"),
        Color.parseColor("#8c564b"),
        Color.parseColor("#e377c2"),
        Color.parseColor("#7f7f7f"),
        Color.parseColor("#bcbd22"),
        Color.parseColor("#17becf")
    };
    
    private int colorIndex = 0;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_plot);

        lineChart = findViewById(R.id.full_line_chart);
        xMinInput = findViewById(R.id.x_min_input);
        xMaxInput = findViewById(R.id.x_max_input);
        yMinInput = findViewById(R.id.y_min_input);
        yMaxInput = findViewById(R.id.y_max_input);
        exprInput = findViewById(R.id.plot_expr_input);
        
        MaterialButton btnAddCurve = findViewById(R.id.btn_add_curve);
        MaterialButton btnPlot = findViewById(R.id.btn_plot_all);
        MaterialButton btnRemoveCurve = findViewById(R.id.btn_remove_curve);
        MaterialButton btnBack = findViewById(R.id.btn_back);
        
        allEntries = new ArrayList<>();
        allExpressions = new ArrayList<>();
        curveColors = new ArrayList<>();
        
        btnAddCurve.setOnClickListener(v -> onAddCurve());
        btnPlot.setOnClickListener(v -> onPlotAll());
        btnRemoveCurve.setOnClickListener(v -> onRemoveCurve());
        btnBack.setOnClickListener(v -> finish());
        
        lineChart.setTouchEnabled(true);
        lineChart.setPinchZoom(true);
        lineChart.setDoubleTapToZoomEnabled(true);
        
        setupChart();
    }
    
    private int getNextColor() {
        int color = COLOR_PALETTE[colorIndex % COLOR_PALETTE.length];
        colorIndex++;
        return color;
    }
    
    private void onAddCurve() {
        String expr = exprInput.getText().toString().trim();
        if (expr.isEmpty()) {
            toast("Enter an expression");
            return;
        }
        allExpressions.add(expr);
        curveColors.add(getNextColor());
        toast("Added curve: " + expr);
        exprInput.setText("");
    }
    
    private void onRemoveCurve() {
        if (allExpressions.isEmpty()) {
            toast("No curves to remove");
            return;
        }
        int idx = allExpressions.size() - 1;
        allExpressions.remove(idx);
        curveColors.remove(idx);
        allEntries.remove(idx);
        toast("Removed last curve");
    }
    
    private void onPlotAll() {
        if (allExpressions.isEmpty()) {
            toast("Add curves first");
            return;
        }
        
        double xMin, xMax, yMin, yMax;
        try {
            xMin = Double.parseDouble(xMinInput.getText().toString().trim());
            xMax = Double.parseDouble(xMaxInput.getText().toString().trim());
            yMin = Double.parseDouble(yMinInput.getText().toString().trim());
            yMax = Double.parseDouble(yMaxInput.getText().toString().trim());
        } catch (NumberFormatException e) {
            toast("Invalid range values");
            return;
        }
        
        if (xMin >= xMax) {
            toast("X min must be less than X max");
            return;
        }
        
        allEntries.clear();
        int numPoints = 300;
        
        for (int curveIdx = 0; curveIdx < allExpressions.size(); curveIdx++) {
            String expr = allExpressions.get(curveIdx);
            double[] xs = new double[numPoints];
            for (int i = 0; i < numPoints; i++) {
                xs[i] = xMin + (xMax - xMin) * i / (numPoints - 1);
            }
            
            double[] ys = CalcEngine.evaluateArray(expr, xs);
            if (ys == null) {
                toast("Error in " + expr + ": " + CalcEngine.getLastError());
                continue;
            }
            
            ArrayList<Entry> entries = new ArrayList<>();
            for (int i = 0; i < numPoints; i++) {
                if (!Double.isNaN(ys[i]) && !Double.isInfinite(ys[i])) {
                    float y = (float) ys[i];
                    if (y >= yMin && y <= yMax) {
                        entries.add(new Entry((float) xs[i], y));
                    }
                }
            }
            allEntries.add(entries);
        }
        
        if (allEntries.isEmpty()) {
            toast("No valid points to plot");
            return;
        }
        
        List<ILineDataSet> dataSets = new ArrayList<>();
        for (int i = 0; i < allEntries.size(); i++) {
            if (allEntries.get(i).isEmpty()) continue;
            
            LineDataSet dataSet = new LineDataSet(allEntries.get(i), allExpressions.get(i));
            dataSet.setColor(curveColors.get(i));
            dataSet.setLineWidth(2f);
            dataSet.setDrawCircles(false);
            dataSet.setDrawValues(false);
            dataSets.add(dataSet);
        }
        
        if (dataSets.isEmpty()) {
            toast("No valid data to display");
            return;
        }
        
        LineData lineData = new LineData(dataSets);
        lineChart.setData(lineData);
        
        YAxis yAxisLeft = lineChart.getAxisLeft();
        yAxisLeft.setAxisMinimum((float) yMin);
        yAxisLeft.setAxisMaximum((float) yMax);
        yAxisLeft.setDrawGridLines(true);
        yAxisLeft.setGridColor(Color.parseColor("#45475a"));
        
        YAxis yAxisRight = lineChart.getAxisRight();
        yAxisRight.setEnabled(false);
        
        XAxis xAxis = lineChart.getXAxis();
        xAxis.setPosition(XAxis.XAxisPosition.BOTTOM);
        xAxis.setDrawGridLines(true);
        xAxis.setGridColor(Color.parseColor("#45475a"));
        
        Legend legend = lineChart.getLegend();
        legend.setEnabled(true);
        legend.setTextColor(Color.parseColor("#cdd6f4"));
        
        Description desc = lineChart.getDescription();
        desc.setEnabled(false);
        
        lineChart.invalidate();
        toast("Plotted " + dataSets.size() + " curve(s)");
    }
    
    private void setupChart() {
        lineChart.setBackgroundColor(Color.parseColor("#181825"));
        lineChart.setGridBackgroundColor(Color.parseColor("#181825"));
        
        XAxis xAxis = lineChart.getXAxis();
        xAxis.setTextColor(Color.parseColor("#cdd6f4"));
        
        YAxis yAxisLeft = lineChart.getAxisLeft();
        yAxisLeft.setTextColor(Color.parseColor("#cdd6f4"));
        
        YAxis yAxisRight = lineChart.getAxisRight();
        yAxisRight.setEnabled(false);
        
        Legend legend = lineChart.getLegend();
        legend.setTextColor(Color.parseColor("#cdd6f4"));
        
        xMinInput.setText("-10");
        xMaxInput.setText("10");
        yMinInput.setText("-10");
        yMaxInput.setText("10");
    }
    
    private void toast(String msg) {
        Toast.makeText(this, msg, Toast.LENGTH_SHORT).show();
    }
}
