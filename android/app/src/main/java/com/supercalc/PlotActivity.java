package com.supercalc;

import android.content.Intent;
import android.graphics.Color;
import android.os.Bundle;
import android.view.MotionEvent;
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
import com.github.mikephil.charting.listener.OnChartGestureListener;
import com.github.mikephil.charting.listener.ChartTouchListener;
import com.github.mikephil.charting.utils.MPPointD;
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
    
    // Marked points for coordinate marking
    private ArrayList<Entry> markedPoints;
    private LineDataSet markedPointDataSet;
    
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
    private static final int MARK_COLOR = Color.parseColor("#f38ba8");
    
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
        markedPoints = new ArrayList<>();
        
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
        setupGestureListener();
        
        // Handle parametric curve from intent
        Intent intent = getIntent();
        if (intent != null && intent.getBooleanExtra("is_parametric", false)) {
            String xExpr = intent.getStringExtra("parametric_x");
            String yExpr = intent.getStringExtra("parametric_y");
            double tMin = intent.getDoubleExtra("t_min", 0);
            double tMax = intent.getDoubleExtra("t_max", 6.2832);
            if (xExpr != null && yExpr != null) {
                plotParametricCurve(xExpr, yExpr, tMin, tMax);
            }
        }
    }
    
    private void plotParametricCurve(String xExpr, String yExpr, double tMin, double tMax) {
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
            toast("Error: " + CalcEngine.getLastError());
            return;
        }
        
        ArrayList<Entry> entries = new ArrayList<>();
        double xMin = Double.MAX_VALUE, xMax = Double.MIN_VALUE;
        double yMin = Double.MAX_VALUE, yMax = Double.MIN_VALUE;
        for (int i = 0; i < n; i++) {
            if (!Double.isNaN(xs[i]) && !Double.isNaN(ys[i]) &&
                !Double.isInfinite(xs[i]) && !Double.isInfinite(ys[i])) {
                entries.add(new Entry((float) xs[i], (float) ys[i]));
                if (xs[i] < xMin) xMin = xs[i];
                if (xs[i] > xMax) xMax = xs[i];
                if (ys[i] < yMin) yMin = ys[i];
                if (ys[i] > yMax) yMax = ys[i];
            }
        }
        
        if (entries.isEmpty()) {
            toast("No valid points to plot");
            return;
        }
        
        // Set range with padding
        double xPad = (xMax - xMin) * 0.1;
        double yPad = (yMax - yMin) * 0.1;
        xMinInput.setText(String.valueOf(xMin - xPad));
        xMaxInput.setText(String.valueOf(xMax + xPad));
        yMinInput.setText(String.valueOf(yMin - yPad));
        yMaxInput.setText(String.valueOf(yMax + yPad));
        
        allEntries.clear();
        allExpressions.clear();
        curveColors.clear();
        allEntries.add(entries);
        String label = "P: x(t)=" + xExpr + ", y(t)=" + yExpr;
        allExpressions.add(label);
        curveColors.add(getNextColor());
        
        List<ILineDataSet> dataSets = new ArrayList<>();
        LineDataSet dataSet = new LineDataSet(entries, label);
        dataSet.setColor(curveColors.get(0));
        dataSet.setLineWidth(2f);
        dataSet.setDrawCircles(false);
        dataSet.setDrawValues(false);
        dataSets.add(dataSet);
        
        if (!dataSets.isEmpty()) {
            LineData lineData = new LineData(dataSets);
            lineChart.setData(lineData);
            lineChart.invalidate();
        }
        toast("Parametric curve plotted");
    }
    
    private void setupGestureListener() {
        lineChart.setOnChartGestureListener(new OnChartGestureListener() {
            @Override
            public void onChartGestureStart(MotionEvent me, ChartTouchListener.ChartGesture lastPerformedGesture) {}
            
            @Override
            public void onChartGestureEnd(MotionEvent me, ChartTouchListener.ChartGesture lastPerformedGesture) {}
            
            @Override
            public void onChartLongPressed(MotionEvent me) {
                if (markedPoints.isEmpty()) return;
                
                MPPointD point = lineChart.getTransformer(YAxis.AxisDependency.LEFT).getValuesByTouchPoint(me.getX(), me.getY());
                float x = (float) point.x;
                float y = (float) point.y;
                MPPointD.recycleInstance(point);
                
                float nearestDist = Float.MAX_VALUE;
                int nearestIdx = -1;
                for (int i = 0; i < markedPoints.size(); i++) {
                    Entry e = markedPoints.get(i);
                    float dx = e.getX() - x;
                    float dy = e.getY() - y;
                    float dist = (float) Math.sqrt(dx * dx + dy * dy);
                    if (dist < nearestDist) {
                        nearestDist = dist;
                        nearestIdx = i;
                    }
                }
                
                if (nearestIdx >= 0) {
                    float xRange = lineChart.getXAxis().getAxisMaximum() - lineChart.getXAxis().getAxisMinimum();
                    float yRange = lineChart.getAxisLeft().getAxisMaximum() - lineChart.getAxisLeft().getAxisMinimum();
                    float threshold = Math.max(xRange, yRange) * 0.05f;
                    if (nearestDist < threshold) {
                        markedPoints.remove(nearestIdx);
                        refreshMarkedPoints();
                        toast("Deleted marked point");
                    }
                }
            }
            
            @Override
            public void onChartDoubleTapped(MotionEvent me) {}
            
            @Override
            public void onChartSingleTapped(MotionEvent me) {
                MPPointD point = lineChart.getTransformer(YAxis.AxisDependency.LEFT).getValuesByTouchPoint(me.getX(), me.getY());
                float x = (float) point.x;
                float y = (float) point.y;
                MPPointD.recycleInstance(point);
                
                markedPoints.add(new Entry(x, y));
                refreshMarkedPoints();
                toast(String.format("Marked point: (%.4g, %.4g)", x, y));
            }
            
            @Override
            public void onChartFling(MotionEvent me1, MotionEvent me2, float velocityX, float velocityY) {}
            
            @Override
            public void onChartScale(MotionEvent me, float scaleX, float scaleY) {}
            
            @Override
            public void onChartTranslate(MotionEvent me, float dX, float dY) {}
        });
    }
    
    private void refreshMarkedPoints() {
        if (markedPointDataSet == null) {
            LineData data = lineChart.getData();
            if (data == null) return;
            
            markedPointDataSet = new LineDataSet(new ArrayList<>(), "Marked Points");
            markedPointDataSet.setColor(Color.TRANSPARENT);
            markedPointDataSet.setDrawCircles(true);
            markedPointDataSet.setCircleColor(MARK_COLOR);
            markedPointDataSet.setCircleRadius(6f);
            markedPointDataSet.setCircleHoleRadius(3f);
            markedPointDataSet.setCircleHoleColor(MARK_COLOR);
            markedPointDataSet.setDrawValues(false);
            markedPointDataSet.setHighlightEnabled(false);
            data.addDataSet(markedPointDataSet);
        }
        
        markedPointDataSet.clear();
        for (Entry e : markedPoints) {
            markedPointDataSet.addEntry(e);
        }
        markedPointDataSet.notifyDataSetChanged();
        lineChart.getData().notifyDataChanged();
        lineChart.notifyDataSetChanged();
        lineChart.invalidate();
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
        
        if (yMin >= yMax) {
            toast("Y min must be less than Y max");
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
        
        // Marked points dataset
        markedPointDataSet = new LineDataSet(new ArrayList<>(markedPoints), "Marked Points");
        markedPointDataSet.setColor(Color.TRANSPARENT);
        markedPointDataSet.setDrawCircles(true);
        markedPointDataSet.setCircleColor(MARK_COLOR);
        markedPointDataSet.setCircleRadius(6f);
        markedPointDataSet.setCircleHoleRadius(3f);
        markedPointDataSet.setCircleHoleColor(MARK_COLOR);
        markedPointDataSet.setDrawValues(false);
        markedPointDataSet.setHighlightEnabled(false);
        dataSets.add(markedPointDataSet);
        
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
            intent.putExtra("expressions", expressions);
            intent.putExtra("entries_data", entriesData);
            intent.putExtra("colors", colors);
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
