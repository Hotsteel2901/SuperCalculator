package com.supercalc;

import android.graphics.Color;
import android.os.Bundle;
import android.view.MotionEvent;
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
import com.github.mikephil.charting.listener.OnChartGestureListener;
import com.github.mikephil.charting.listener.ChartTouchListener;
import com.github.mikephil.charting.listener.OnChartValueSelectedListener;
import com.github.mikephil.charting.utils.MPPointD;
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
    /** Maps each chart dataset index to the curve index it belongs to. */
    private final ArrayList<Integer> datasetCurveIndex = new ArrayList<>();
    /** Intersection points handed over by the plot screen, so full screen keeps them. */
    private final ArrayList<Entry> intersectionMarkers = new ArrayList<>();
    
    // Marked points for coordinate marking
    private ArrayList<Entry> markedPoints;
    private LineDataSet markedPointDataSet;
    
    private static final int[] COLOR_PALETTE = {
        Color.parseColor("#6366F1"),
        Color.parseColor("#FB923C"),
        Color.parseColor("#34D399"),
        Color.parseColor("#F87171"),
        Color.parseColor("#A78BFA"),
        Color.parseColor("#A16207"),
        Color.parseColor("#F472B6"),
        Color.parseColor("#94A3B8"),
        Color.parseColor("#FBBF24"),
        Color.parseColor("#22D3EE")
    };
    
    private static final int COLOR_GRID = Color.parseColor("#2B3350");
    private static final int COLOR_TEXT = Color.parseColor("#E6EAFF");
    private static final int COLOR_BG = Color.parseColor("#0B0E1C");
    private static final int MARK_COLOR = Color.parseColor("#F472B6");

    /** Sentinel entry that separates two continuous segments of one curve. */
    private static final Entry NaN_MARKER = new Entry(Float.NaN, Float.NaN);

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
        markedPoints = new ArrayList<>();
        
        btnExit.setOnClickListener(v -> finish());
        
        configureChartInteraction();
        lineChart.setOnChartValueSelectedListener(this);
        
        setupChart();
        setupGestureListener();
        loadPlotData();
    }
    
    /** Full-screen chart keeps the original one-finger pan/two-finger zoom model. */
    private void configureChartInteraction() {
        lineChart.setTouchEnabled(true);
        lineChart.setDragEnabled(true);
        lineChart.setScaleEnabled(true);
        lineChart.setScaleXEnabled(true);
        lineChart.setScaleYEnabled(true);
        lineChart.setAutoScaleMinMaxEnabled(false);
        lineChart.setPinchZoom(true);
        lineChart.setDoubleTapToZoomEnabled(true);
        lineChart.setHighlightPerDragEnabled(false);
        lineChart.setHighlightPerTapEnabled(true);
        // InteractiveLineChart owns dispatch and locks every ancestor for the
        // complete stream, including both pointers in a pinch gesture.
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
                        coordinateDisplay.setText(getString(R.string.toast_deleted_mark));
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
                coordinateDisplay.setText(String.format(getString(R.string.toast_marked_point), x, y));
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
    
    private void loadPlotData() {
        String[] expressions = getIntent().getStringArrayExtra("expressions");
        String[] entriesData = getIntent().getStringArrayExtra("entries_data");
        int[] colors = getIntent().getIntArrayExtra("colors");
        float xMin = getIntent().getFloatExtra("x_min", -10f);
        float xMax = getIntent().getFloatExtra("x_max", 10f);
        float yMin = getIntent().getFloatExtra("y_min", -10f);
        float yMax = getIntent().getFloatExtra("y_max", 10f);
        
        if (expressions == null || entriesData == null) {
            toast(getString(R.string.toast_no_plot_data));
            return;
        }
        
        for (int i = 0; i < expressions.length && i < entriesData.length; i++) {
            allExpressions.add(expressions[i]);
            if (colors != null && i < colors.length) {
                curveColors.add(colors[i]);
            } else {
                curveColors.add(COLOR_PALETTE[i % COLOR_PALETTE.length]);
            }

            ArrayList<Entry> entries = new ArrayList<>();
            // Each curve is encoded as continuous segments separated by '|',
            // points inside a segment separated by ';' (see PlotActivity).
            // MPAndroidChart v3.1.0 does NOT break a line at a NaN entry, so we
            // must keep the segments apart as separate datasets.  We store them
            // here as one flat list with NaN markers and expand into separate
            // datasets in renderChart().
            String[] segments = entriesData[i].split("\\|", -1);
            for (String seg : segments) {
                if (seg.isEmpty()) continue;
                ArrayList<Entry> segEntries = new ArrayList<>();
                String[] points = seg.split(";");
                for (String point : points) {
                    String[] coords = point.split(",");
                    if (coords.length == 2) {
                        try {
                            float x = Float.parseFloat(coords[0]);
                            float y = Float.parseFloat(coords[1]);
                            segEntries.add(new Entry(x, y));
                        } catch (NumberFormatException e) {
                            // Skip invalid points
                        }
                    }
                }
                if (!segEntries.isEmpty()) {
                    if (!entries.isEmpty()) entries.add(NaN_MARKER);
                    entries.addAll(segEntries);
                }
            }
            allEntries.add(entries);
        }

        String intersectData = getIntent().getStringExtra("intersect_points");
        if (intersectData != null && !intersectData.isEmpty()) {
            for (String point : intersectData.split(";")) {
                String[] coords = point.split(",");
                if (coords.length != 2) continue;
                try {
                    intersectionMarkers.add(new Entry(
                            Float.parseFloat(coords[0]), Float.parseFloat(coords[1])));
                } catch (NumberFormatException ignored) {
                    // skip malformed pair
                }
            }
        }
        String markedData = getIntent().getStringExtra("marked_points");
        if (markedData != null && !markedData.isEmpty()) {
            for (String point : markedData.split(";")) {
                String[] coords = point.split(",");
                if (coords.length != 2) continue;
                try {
                    markedPoints.add(new Entry(
                            Float.parseFloat(coords[0]), Float.parseFloat(coords[1])));
                } catch (NumberFormatException ignored) {
                    // skip malformed pair
                }
            }
        }

        renderChart(xMin, xMax, yMin, yMax);
    }
    
    private void renderChart(float xMin, float xMax, float yMin, float yMax) {
        List<ILineDataSet> dataSets = new ArrayList<>();
        datasetCurveIndex.clear();
        for (int i = 0; i < allEntries.size(); i++) {
            if (allEntries.get(i).isEmpty()) continue;

            // Split the flat list back into segments at the NaN markers and
            // create one dataset per segment: this is what actually produces a
            // clean gap at each asymptote in MPAndroidChart.
            ArrayList<ArrayList<Entry>> segments = new ArrayList<>();
            ArrayList<Entry> cur = new ArrayList<>();
            for (Entry e : allEntries.get(i)) {
                if (Float.isNaN(e.getX()) && Float.isNaN(e.getY())) {
                    if (!cur.isEmpty()) { segments.add(cur); cur = new ArrayList<>(); }
                } else {
                    cur.add(e);
                }
            }
            if (!cur.isEmpty()) segments.add(cur);

            boolean first = true;
            String label = allExpressions.get(i);
            for (ArrayList<Entry> seg : segments) {
                if (seg.isEmpty()) continue;
                LineDataSet dataSet = new LineDataSet(seg, first ? label : "");
                dataSet.setColor(curveColors.get(i));
                dataSet.setLineWidth(2f);
                dataSet.setDrawCircles(false);
                dataSet.setDrawValues(false);
                dataSets.add(dataSet);
                datasetCurveIndex.add(i);
                first = false;
            }
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

        // Intersection markers carried over from the plot screen.
        if (!intersectionMarkers.isEmpty()) {
            LineDataSet intersectSet =
                    new LineDataSet(new ArrayList<>(intersectionMarkers), getString(R.string.intersect));
            intersectSet.setColor(Color.TRANSPARENT);
            intersectSet.setDrawCircles(true);
            intersectSet.setCircleColor(Color.parseColor("#FBBF24"));
            intersectSet.setCircleRadius(6f);
            intersectSet.setDrawValues(false);
            intersectSet.setLineWidth(0f);
            intersectSet.setHighlightEnabled(false);
            dataSets.add(intersectSet);
        }

        if (dataSets.isEmpty()) {
            toast(getString(R.string.toast_no_data_display));
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
        xAxis.setAxisMinimum(xMin);
        xAxis.setAxisMaximum(xMax);
        
        Legend legend = lineChart.getLegend();
        legend.setEnabled(true);
        legend.setTextColor(Color.parseColor("#E6EAFF"));
        
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
            int idx = highlight.getDataSetIndex();
            // Several datasets can belong to one curve (one per continuous
            // segment); map the dataset index back to its curve label.
            String curveLabel = datasetToExpression(idx);
            if (curveLabel != null && !curveLabel.isEmpty()) {
                coordText.append(" - ").append(curveLabel);
            }
        }
        
        coordinateDisplay.setText(coordText.toString());
    }

    /** Curve label for a given chart dataset index, or null if out of range. */
    private String datasetToExpression(int datasetIndex) {
        if (datasetIndex < 0 || datasetIndex >= datasetCurveIndex.size()) return null;
        int curveIdx = datasetCurveIndex.get(datasetIndex);
        if (curveIdx < 0 || curveIdx >= allExpressions.size()) return null;
        return allExpressions.get(curveIdx);
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
