package com.supercalc;

import android.content.Intent;
import android.graphics.Color;
import android.os.Bundle;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.widget.NestedScrollView;
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
    private MaterialButton btnZoom;
    
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
    
    private static final int COLOR_GRID = Color.parseColor("#45475a");
    private static final int COLOR_TEXT = Color.parseColor("#cdd6f4");
    private static final int COLOR_BG = Color.parseColor("#181825");
    
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
        btnZoom = findViewById(R.id.btn_zoom);
        
        MaterialButton btnAddCurve = findViewById(R.id.btn_add_curve);
        MaterialButton btnPlot = findViewById(R.id.btn_plot_all);
        MaterialButton btnRemoveCurve = findViewById(R.id.btn_remove_curve);
        MaterialButton btnBack = findViewById(R.id.btn_back);
        
        allEntries = new ArrayList<>();
        allExpressions = new ArrayList<>();
        curveColors = new ArrayList<>();
        
        // Restore state after configuration change
        if (savedInstanceState != null) {
            ArrayList<String> savedExprs = savedInstanceState.getStringArrayList("expressions");
            if (savedExprs != null) allExpressions = savedExprs;
            ArrayList<Integer> savedColors = savedInstanceState.getIntegerArrayList("colors");
            if (savedColors != null) curveColors = savedColors;
            // Note: entries need to be recalculated from expressions
        }
        
        btnAddCurve.setOnClickListener(v -> onAddCurve());
        btnPlot.setOnClickListener(v -> onPlotAll());
        btnRemoveCurve.setOnClickListener(v -> onRemoveCurve());
        btnBack.setOnClickListener(v -> finish());
        btnZoom.setOnClickListener(v -> openFullScreen());
        
        NestedScrollView scrollView = findViewById(R.id.scroll_view);
        scrollView.setNestedScrollingEnabled(false);
        
        lineChart.setTouchEnabled(true);
        lineChart.setPinchZoom(true);
        lineChart.setDoubleTapToZoomEnabled(true);
        
        setupChart();
    }
    
    @Override
    protected void onSaveInstanceState(Bundle outState) {
        super.onSaveInstanceState(outState);
        outState.putStringArrayList("expressions", allExpressions);
        outState.putIntegerArrayList("colors", curveColors);
        outState.putString("x_min", xMinInput.getText().toString());
        outState.putString("x_max", xMaxInput.getText().toString());
        outState.putString("y_min", yMinInput.getText().toString());
        outState.putString("y_max", yMaxInput.getText().toString());
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
        if (idx < curveColors.size()) {
            curveColors.remove(idx);
        }
        if (idx < allEntries.size()) {
            allEntries.remove(idx);
        }
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
        // Limit points to avoid TransactionTooLargeException (1MB limit)
        // Each point is ~8 bytes (float pair), 300 points * 10 curves = ~24KB safe
        int numPoints = Math.min(300, (int)((xMax - xMin) / 0.1));
        numPoints = Math.max(50, Math.min(500, numPoints));
        
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
        yAxisLeft.setGridColor(COLOR_GRID);
        
        YAxis yAxisRight = lineChart.getAxisRight();
        yAxisRight.setEnabled(false);
        
        XAxis xAxis = lineChart.getXAxis();
        xAxis.setPosition(XAxis.XAxisPosition.BOTTOM);
        xAxis.setDrawGridLines(true);
        xAxis.setGridColor(COLOR_GRID);
        
        Legend legend = lineChart.getLegend();
        legend.setEnabled(true);
        legend.setTextColor(Color.parseColor("#cdd6f4"));
        
        Description desc = lineChart.getDescription();
        desc.setEnabled(false);
        
        lineChart.invalidate();
        toast("Plotted " + dataSets.size() + " curve(s)");
    }
    
    private void openFullScreen() {
        if (allEntries.isEmpty()) {
            toast("Plot some curves first");
            return;
        }
        
        Intent intent = new Intent(this, FullScreenPlotActivity.class);
        
        String[] expressions = allExpressions.toArray(new String[0]);
        
        // Limit data to avoid TransactionTooLargeException (~1MB limit)
        // Estimate size: each entry ~50 chars in string form
        int maxTotalPoints = 10000; // Safe limit for Intent
        int totalPoints = 0;
        for (ArrayList<Entry> entries : allEntries) {
            totalPoints += entries.size();
        }
        
        String[] entriesData;
        if (totalPoints > maxTotalPoints) {
            // Downsample
            entriesData = new String[allEntries.size()];
            for (int i = 0; i < allEntries.size(); i++) {
                StringBuilder sb = new StringBuilder();
                ArrayList<Entry> entries = allEntries.get(i);
                int step = Math.max(1, entries.size() / (maxTotalPoints / allEntries.size()));
                for (int j = 0; j < entries.size(); j += step) {
                    Entry e = entries.get(j);
                    if (sb.length() > 0) sb.append(";");
                    sb.append(String.format("%.4g,%.4g", e.getX(), e.getY()));
                }
                entriesData[i] = sb.toString();
            }
            toast("Downsampled for full screen view");
        } else {
            entriesData = new String[allEntries.size()];
            for (int i = 0; i < allEntries.size(); i++) {
                StringBuilder sb = new StringBuilder();
                for (Entry e : allEntries.get(i)) {
                    if (sb.length() > 0) sb.append(";");
                    sb.append(String.format("%.4g,%.4g", e.getX(), e.getY()));
                }
                entriesData[i] = sb.toString();
            }
        }
        
        int[] colors = new int[curveColors.size()];
        for (int i = 0; i < curveColors.size(); i++) {
            colors[i] = curveColors.get(i);
        }
        
        try {
            float xMin = Float.parseFloat(xMinInput.getText().toString().trim());
            float xMax = Float.parseFloat(xMaxInput.getText().toString().trim());
            float yMin = Float.parseFloat(yMinInput.getText().toString().trim());
            float yMax = Float.parseFloat(yMaxInput.getText().toString().trim());
            
            intent.putExtra("expressions", expressions);
            intent.putExtra("entries_data", entriesData);
            intent.putExtra("colors", colors);
            intent.putExtra("x_min", xMin);
            intent.putExtra("x_max", xMax);
            intent.putExtra("y_min", yMin);
            intent.putExtra("y_max", yMax);
        } catch (NumberFormatException e) {
            intent.putExtra("x_min", -10f);
            intent.putExtra("x_max", 10f);
            intent.putExtra("y_min", -10f);
            intent.putExtra("y_max", 10f);
        }
        
        startActivity(intent);
    }
    
    private void setupChart() {
        lineChart.setBackgroundColor(COLOR_BG);
        lineChart.setGridBackgroundColor(COLOR_BG);
        
        XAxis xAxis = lineChart.getXAxis();
        xAxis.setTextColor(COLOR_TEXT);
        
        YAxis yAxisLeft = lineChart.getAxisLeft();
        yAxisLeft.setTextColor(COLOR_TEXT);
        
        YAxis yAxisRight = lineChart.getAxisRight();
        yAxisRight.setEnabled(false);
        
        Legend legend = lineChart.getLegend();
        legend.setTextColor(COLOR_TEXT);
        
        xMinInput.setText("-10");
        xMaxInput.setText("10");
        yMinInput.setText("-10");
        yMaxInput.setText("10");
    }
    
    private void toast(String msg) {
        Toast.makeText(this, msg, Toast.LENGTH_SHORT).show();
    }
}
