package com.supercalc;

import android.graphics.Color;
import android.os.Bundle;
import android.widget.TextView;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import com.github.mikephil.charting.charts.LineChart;
import com.github.mikephil.charting.data.Entry;
import com.github.mikephil.charting.data.LineData;
import com.github.mikephil.charting.data.LineDataSet;
import com.github.mikephil.charting.interfaces.datasets.ILineDataSet;
import com.github.mikephil.charting.components.XAxis;
import com.github.mikephil.charting.components.YAxis;
import com.github.mikephil.charting.components.Legend;
import com.github.mikephil.charting.components.Description;
import com.github.mikephil.charting.highlight.Highlight;
import com.github.mikephil.charting.listener.OnChartValueSelectedListener;
import com.google.android.material.button.MaterialButton;
import java.util.ArrayList;
import java.util.List;

public class FullScreenPlotActivity extends AppCompatActivity implements OnChartValueSelectedListener {

    private LineChart lineChart;
    private TextView coordinateDisplay;
    private MaterialButton btnExit;
    
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

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_full_screen_plot);

        lineChart = findViewById(R.id.full_screen_chart);
        coordinateDisplay = findViewById(R.id.coordinate_display);
        btnExit = findViewById(R.id.btn_exit);
        
        allEntries = new ArrayList<>();
        allExpressions = new ArrayList<>();
        curveColors = new ArrayList<>();
        
        btnExit.setOnClickListener(v -> finish());
        
        lineChart.setTouchEnabled(true);
        lineChart.setPinchZoom(true);
        lineChart.setDoubleTapToZoomEnabled(true);
        lineChart.setOnChartValueSelectedListener(this);
        
        setupChart();
        loadPlotData();
    }
    
    private void loadPlotData() {
        String[] expressions = getIntent().getStringArrayExtra("expressions");
        String[] entriesData = getIntent().getStringArrayExtra("entries_data");
        int[] colors = getIntent().getIntArrayExtra("colors");
        float xMin = getIntent().getFloatExtra("x_min", -10f);
        float xMax = getIntent().getFloatExtra("x_max", 10f);
        float yMin = getIntent().getFloatExtra("y_min", -10f);
        float yMax = getIntent().getFloatExtra("y_max", 10f);
        
        if (expressions == null || entriesData == null) {
            toast("No plot data received");
            return;
        }
        
        for (int i = 0; i < expressions.length; i++) {
            allExpressions.add(expressions[i]);
            if (colors != null && i < colors.length) {
                curveColors.add(colors[i]);
            } else {
                curveColors.add(COLOR_PALETTE[i % COLOR_PALETTE.length]);
            }
            
            ArrayList<Entry> entries = new ArrayList<>();
            String[] points = entriesData[i].split(";");
            for (String point : points) {
                String[] coords = point.split(",");
                if (coords.length == 2) {
                    try {
                        float x = Float.parseFloat(coords[0]);
                        float y = Float.parseFloat(coords[1]);
                        if (y >= yMin && y <= yMax) {
                            entries.add(new Entry(x, y));
                        }
                    } catch (NumberFormatException e) {
                        // Skip invalid points
                    }
                }
            }
            allEntries.add(entries);
        }
        
        renderChart(xMin, xMax, yMin, yMax);
    }
    
    private void renderChart(float xMin, float xMax, float yMin, float yMax) {
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
        yAxisLeft.setAxisMinimum(yMin);
        yAxisLeft.setAxisMaximum(yMax);
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
    }
    
    @Override
    public void onValueSelected(Entry e, Highlight highlight) {
        float x = e.getX();
        float y = e.getY();
        
        StringBuilder coordText = new StringBuilder();
        coordText.append(String.format("(%.6g, %.6g)", x, y));
        
        if (allExpressions.size() > 1) {
            coordText.append(" - ").append(allExpressions.get(highlight.getDataSetIndex()));
        }
        
        coordinateDisplay.setText(coordText.toString());
    }
    
    @Override
    public void onNothingSelected() {
        coordinateDisplay.setText("");
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
    }
    
    private void toast(String msg) {
        Toast.makeText(this, msg, Toast.LENGTH_SHORT).show();
    }
}
