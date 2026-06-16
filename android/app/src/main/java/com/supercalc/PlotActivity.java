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
    // Track curve type: "regular", "parametric", "polar", "ode", "taylor"
    private ArrayList<String> curveTypes;
    // Store parametric/polar parameters for re-plotting
    private ArrayList<String> parametricXExprs;
    private ArrayList<String> parametricYExprs;
    private ArrayList<Double> parametricTMin;
    private ArrayList<Double> parametricTMax;
    private ArrayList<String> polarExprs;
    private ArrayList<Double> polarThetaMin;
    private ArrayList<Double> polarThetaMax;
    
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
        curveTypes = new ArrayList<>();
        parametricXExprs = new ArrayList<>();
        parametricYExprs = new ArrayList<>();
        parametricTMin = new ArrayList<>();
        parametricTMax = new ArrayList<>();
        polarExprs = new ArrayList<>();
        polarThetaMin = new ArrayList<>();
        polarThetaMax = new ArrayList<>();
        markedPoints = new ArrayList<>();
        
        // Restore state if available
        if (savedInstanceState != null) {
            ArrayList<String> savedExprs = savedInstanceState.getStringArrayList("expressions");
            if (savedExprs != null) allExpressions.addAll(savedExprs);
            ArrayList<Integer> savedColors = savedInstanceState.getIntegerArrayList("colors");
            if (savedColors != null) curveColors.addAll(savedColors);
            ArrayList<String> savedTypes = savedInstanceState.getStringArrayList("curve_types");
            if (savedTypes != null) curveTypes.addAll(savedTypes);
            ArrayList<String> savedParamX = savedInstanceState.getStringArrayList("param_x_exprs");
            if (savedParamX != null) parametricXExprs.addAll(savedParamX);
            ArrayList<String> savedParamY = savedInstanceState.getStringArrayList("param_y_exprs");
            if (savedParamY != null) parametricYExprs.addAll(savedParamY);
            ArrayList<String> savedPolar = savedInstanceState.getStringArrayList("polar_exprs");
            if (savedPolar != null) polarExprs.addAll(savedPolar);
            colorIndex = savedInstanceState.getInt("color_index", 0);
            
            // Restore axis ranges
            String savedXMin = savedInstanceState.getString("x_min");
            String savedXMax = savedInstanceState.getString("x_max");
            String savedYMin = savedInstanceState.getString("y_min");
            String savedYMax = savedInstanceState.getString("y_max");
            if (savedXMin != null) xMinInput.setText(savedXMin);
            if (savedXMax != null) xMaxInput.setText(savedXMax);
            if (savedYMin != null) yMinInput.setText(savedYMin);
            if (savedYMax != null) yMaxInput.setText(savedYMax);
            
            // Restore parametric/polar parameters
            ArrayList<String> savedParamTMin = savedInstanceState.getStringArrayList("param_t_min");
            ArrayList<String> savedParamTMax = savedInstanceState.getStringArrayList("param_t_max");
            if (savedParamTMin != null && savedParamTMax != null) {
                for (String s : savedParamTMin) {
                    try {
                        parametricTMin.add(Double.parseDouble(s));
                    } catch (NumberFormatException e) {
                        parametricTMin.add(0.0);
                    }
                }
                for (String s : savedParamTMax) {
                    try {
                        parametricTMax.add(Double.parseDouble(s));
                    } catch (NumberFormatException e) {
                        parametricTMax.add(2 * Math.PI);
                    }
                }
            }
            ArrayList<String> savedPolarThetaMin = savedInstanceState.getStringArrayList("polar_theta_min");
            ArrayList<String> savedPolarThetaMax = savedInstanceState.getStringArrayList("polar_theta_max");
            if (savedPolarThetaMin != null && savedPolarThetaMax != null) {
                for (String s : savedPolarThetaMin) {
                    try {
                        polarThetaMin.add(Double.parseDouble(s));
                    } catch (NumberFormatException e) {
                        polarThetaMin.add(0.0);
                    }
                }
                for (String s : savedPolarThetaMax) {
                    try {
                        polarThetaMax.add(Double.parseDouble(s));
                    } catch (NumberFormatException e) {
                        polarThetaMax.add(2 * Math.PI);
                    }
                }
            }
        }
        
        btnAddCurve.setOnClickListener(v -> onAddCurve());
        btnPlot.setOnClickListener(v -> onPlotAll());
        btnRemoveCurve.setOnClickListener(v -> onRemoveCurve());
        btnBack.setOnClickListener(v -> finish());
        btnZoom.setOnClickListener(v -> openFullScreen());
        
        NestedScrollView scrollView = findViewById(R.id.scroll_view);
        if (scrollView != null) scrollView.setNestedScrollingEnabled(false);
        
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
        
        // Handle polar curve from intent
        if (intent != null && intent.getBooleanExtra("is_polar", false)) {
            String rExpr = intent.getStringExtra("polar_r");
            double thetaMin = intent.getDoubleExtra("t_min", 0);
            double thetaMax = intent.getDoubleExtra("t_max", 6.2832);
            if (rExpr != null) {
                plotPolarCurve(rExpr, thetaMin, thetaMax);
            }
        }
        
        // Handle implicit curve from intent
        if (intent != null && intent.getBooleanExtra("is_implicit", false)) {
            String impExpr = intent.getStringExtra("implicit_expr");
            int resolution = intent.getIntExtra("implicit_resolution", 200);
            double xMin = intent.getDoubleExtra("x_min", -10.0);
            double xMax = intent.getDoubleExtra("x_max", 10.0);
            double yMin = intent.getDoubleExtra("y_min", -10.0);
            double yMax = intent.getDoubleExtra("y_max", 10.0);
            if (impExpr != null) {
                plotImplicitCurve(impExpr, resolution, xMin, xMax, yMin, yMax);
            }
        }
        
        // Handle ODE solution plot from intent
        if (intent != null && intent.getBooleanExtra("is_ode", false)) {
            // Check for multi-method comparison first
            boolean isMulti = intent.getBooleanExtra("ode_multi", false);
            if (isMulti) {
                ArrayList<double[]> multiXs = (ArrayList<double[]>) intent.getSerializableExtra("ode_multi_xs");
                ArrayList<double[]> multiYs = (ArrayList<double[]>) intent.getSerializableExtra("ode_multi_ys");
                ArrayList<String> multiLabels = (ArrayList<String>) intent.getSerializableExtra("ode_multi_labels");
                String odeExpr = intent.getStringExtra("ode_expr");
                if (multiXs != null && multiYs != null && multiLabels != null) {
                    plotOdeComparison(multiXs, multiYs, multiLabels, odeExpr != null ? odeExpr : "dy/dx");
                }
            } else {
                double[] odeXs = intent.getDoubleArrayExtra("ode_xs");
                double[] odeYs = intent.getDoubleArrayExtra("ode_ys");
                String odeExpr = intent.getStringExtra("ode_expr");
                if (odeXs != null && odeYs != null) {
                    plotOdeSolution(odeXs, odeYs, odeExpr != null ? odeExpr : "dy/dx");
                }
            }
        }
        
        // Handle Taylor series plot from intent
        if (intent != null && intent.getBooleanExtra("is_taylor", false)) {
            String taylorExpr = intent.getStringExtra("taylor_expr");
            double taylorA = intent.getDoubleExtra("taylor_a", 0);
            int taylorOrder = intent.getIntExtra("taylor_order", 5);
            double[] taylorXs = intent.getDoubleArrayExtra("taylor_xs");
            double[] taylorYsOrig = intent.getDoubleArrayExtra("taylor_ys_orig");
            double[] taylorYsTaylor = intent.getDoubleArrayExtra("taylor_ys_taylor");
            if (taylorXs != null && taylorYsOrig != null && taylorYsTaylor != null) {
                plotTaylorSeries(taylorExpr, taylorA, taylorOrder, taylorXs, taylorYsOrig, taylorYsTaylor);
            }
        }
        
        // Handle regression scatter + fit curve from intent
        if (intent != null && intent.getBooleanExtra("regression", false)) {
            double[] regXs = intent.getDoubleArrayExtra("regXs");
            double[] regYs = intent.getDoubleArrayExtra("regYs");
            if (regXs != null && regYs != null) {
                plotRegressionData(regXs, regYs);
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
            toast(getString(R.string.toast_error_prefix, CalcEngine.getLastError()));
            return;
        }

        ArrayList<Entry> entries = new ArrayList<>();
        double xMin = Double.POSITIVE_INFINITY, xMax = Double.NEGATIVE_INFINITY;
        double yMin = Double.POSITIVE_INFINITY, yMax = Double.NEGATIVE_INFINITY;
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
            toast(getString(R.string.toast_no_valid_points));
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
        curveTypes.clear();
        parametricXExprs.clear();
        parametricYExprs.clear();
        parametricTMin.clear();
        parametricTMax.clear();
        polarExprs.clear();
        polarThetaMin.clear();
        polarThetaMax.clear();
        allEntries.add(entries);
        String label = "P: x(t)=" + xExpr + ", y(t)=" + yExpr;
        allExpressions.add(label);
        curveColors.add(getNextColor());
        curveTypes.add("parametric");
        parametricXExprs.add(xExpr);
        parametricYExprs.add(yExpr);
        parametricTMin.add(tMin);
        parametricTMax.add(tMax);
        
        List<ILineDataSet> dataSets = new ArrayList<>();
        LineDataSet dataSet = new LineDataSet(entries, label);
        dataSet.setColor(curveColors.get(curveColors.size() - 1));
        dataSet.setLineWidth(2f);
        dataSet.setDrawCircles(false);
        dataSet.setDrawValues(false);
        dataSets.add(dataSet);
        
        if (!dataSets.isEmpty()) {
            LineData lineData = new LineData(dataSets);
            lineChart.setData(lineData);
            lineChart.invalidate();
        }
        toast(getString(R.string.toast_parametric_plotted));
    }
    
    private void plotPolarCurve(String rExpr, double thetaMin, double thetaMax) {
        int n = 500;
        double step = (thetaMax - thetaMin) / (n - 1);
        double[] thetas = new double[n];
        for (int i = 0; i < n; i++) {
            thetas[i] = thetaMin + i * step;
        }
        
        // C core only supports x/y variables; replace theta -> x for evaluation
        String rExprSub = rExpr.replaceAll("\\btheta\\b", "x");
        double[] rs = CalcEngine.evaluateArray(rExprSub, thetas);
        if (rs == null) {
            toast(getString(R.string.toast_error_prefix, CalcEngine.getLastError()));
            return;
        }
        
        // Convert polar to Cartesian coordinates
        ArrayList<Entry> entries = new ArrayList<>();
        double xMin = Double.POSITIVE_INFINITY, xMax = Double.NEGATIVE_INFINITY;
        double yMin = Double.POSITIVE_INFINITY, yMax = Double.NEGATIVE_INFINITY;
        for (int i = 0; i < n; i++) {
            if (!Double.isNaN(rs[i]) && !Double.isInfinite(rs[i])) {
                double x = rs[i] * Math.cos(thetas[i]);
                double y = rs[i] * Math.sin(thetas[i]);
                entries.add(new Entry((float) x, (float) y));
                if (x < xMin) xMin = x;
                if (x > xMax) xMax = x;
                if (y < yMin) yMin = y;
                if (y > yMax) yMax = y;
            }
        }
        
        if (entries.isEmpty()) {
            toast(getString(R.string.toast_no_valid_points));
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
        curveTypes.clear();
        parametricXExprs.clear();
        parametricYExprs.clear();
        parametricTMin.clear();
        parametricTMax.clear();
        polarExprs.clear();
        polarThetaMin.clear();
        polarThetaMax.clear();
        allEntries.add(entries);
        String label = "Pol: r(theta)=" + rExpr;
        allExpressions.add(label);
        curveColors.add(getNextColor());
        curveTypes.add("polar");
        polarExprs.add(rExpr);
        polarThetaMin.add(thetaMin);
        polarThetaMax.add(thetaMax);
        
        List<ILineDataSet> dataSets = new ArrayList<>();
        LineDataSet dataSet = new LineDataSet(entries, label);
        dataSet.setColor(curveColors.get(curveColors.size() - 1));
        dataSet.setLineWidth(2f);
        dataSet.setDrawCircles(false);
        dataSet.setDrawValues(false);
        dataSets.add(dataSet);
        
        if (!dataSets.isEmpty()) {
            LineData lineData = new LineData(dataSets);
            lineChart.setData(lineData);
            lineChart.invalidate();
        }
        toast(getString(R.string.toast_polar_plotted));
    }
    
    private void plotImplicitCurve(String impExpr, int resolution, double xMin, double xMax, double yMin, double yMax) {
        ArrayList<Entry> entries = new ArrayList<>();
        
        double dx = (xMax - xMin) / resolution;
        double dy = (yMax - yMin) / resolution;
        
        double[][] grid = new double[resolution + 1][resolution + 1];
        for (int i = 0; i <= resolution; i++) {
            double y = yMin + i * dy;
            for (int j = 0; j <= resolution; j++) {
                double x = xMin + j * dx;
                double val = CalcEngine.evaluateXY(impExpr, x, y);
                grid[i][j] = (!Double.isNaN(val) && !Double.isInfinite(val)) ? val : Double.NaN;
            }
        }
        
        for (int i = 0; i < resolution; i++) {
            for (int j = 0; j < resolution; j++) {
                double v00 = grid[i][j];
                double v10 = grid[i][j + 1];
                double v01 = grid[i + 1][j];
                double v11 = grid[i + 1][j + 1];
                
                if (Double.isNaN(v00) || Double.isNaN(v10) || Double.isNaN(v01) || Double.isNaN(v11)) {
                    continue;
                }
                
                int idx = 0;
                if (v00 < 0) idx |= 1;
                if (v10 < 0) idx |= 2;
                if (v11 < 0) idx |= 4;
                if (v01 < 0) idx |= 8;
                
                if (idx == 0 || idx == 15) continue;
                
                double x0 = xMin + j * dx;
                double y0 = yMin + i * dy;
                double ix, iy;
                
                List<double[]> segs = new ArrayList<>();
                switch (idx) {
                    case 1: case 14:
                        iy = y0 + dy * (-v00 / (v01 - v00));
                        ix = x0 + dx * (-v00 / (v10 - v00));
                        segs.add(new double[]{x0, iy, ix, y0});
                        break;
                    case 2: case 13:
                        ix = x0 + dx * (-v00 / (v10 - v00));
                        iy = y0 + dy * (-v10 / (v11 - v10));
                        segs.add(new double[]{ix, y0, x0 + dx, iy});
                        break;
                    case 3: case 12:
                        iy = y0 + dy * (-v00 / (v01 - v00));
                        double iy2 = y0 + dy * (-v10 / (v11 - v10));
                        segs.add(new double[]{x0, iy, x0 + dx, iy2});
                        break;
                    case 4: case 11:
                        iy = y0 + dy * (-v10 / (v11 - v10));
                        double ix2 = x0 + dx * (-v01 / (v11 - v01));
                        segs.add(new double[]{x0 + dx, iy, ix2, y0 + dy});
                        break;
                    case 5: case 10:
                        iy = y0 + dy * (-v00 / (v01 - v00));
                        ix = x0 + dx * (-v00 / (v10 - v00));
                        double iy2b = y0 + dy * (-v10 / (v11 - v10));
                        double ix2b = x0 + dx * (-v01 / (v11 - v01));
                        segs.add(new double[]{x0, iy, x0 + dx, iy2b});
                        segs.add(new double[]{ix, y0, ix2b, y0 + dy});
                        break;
                    case 6: case 9:
                        ix = x0 + dx * (-v00 / (v10 - v00));
                        iy = y0 + dy * (-v01 / (v11 - v01));
                        segs.add(new double[]{ix, y0, x0 + dx * (-v01 / (v11 - v01)), y0 + dy});
                        break;
                    case 7: case 8:
                        iy = y0 + dy * (-v00 / (v01 - v00));
                        ix = x0 + dx * (-v01 / (v11 - v01));
                        segs.add(new double[]{x0, iy, ix, y0 + dy});
                        break;
                }
                
                for (double[] seg : segs) {
                    entries.add(new Entry((float) seg[0], (float) seg[1]));
                    entries.add(new Entry((float) seg[2], (float) seg[3]));
                    entries.add(new Entry(Float.NaN, Float.NaN));
                }
            }
        }
        
        allEntries.add(entries);
        String label = "Imp: " + impExpr + " = 0";
        allExpressions.add(label);
        curveColors.add(getNextColor());
        curveTypes.add("implicit");
        
        List<ILineDataSet> dataSets = new ArrayList<>();
        LineDataSet dataSet = new LineDataSet(entries, label);
        dataSet.setColor(curveColors.get(curveColors.size() - 1));
        dataSet.setLineWidth(2f);
        dataSet.setDrawCircles(false);
        dataSet.setDrawValues(false);
        dataSets.add(dataSet);
        
        if (!dataSets.isEmpty()) {
            LineData lineData = new LineData(dataSets);
            lineChart.setData(lineData);
            lineChart.invalidate();
        }
        toast(getString(R.string.toast_implicit_plotted) + ": " + impExpr + " = 0");
    }
    
    private void plotOdeSolution(double[] xs, double[] ys, String expr) {
        ArrayList<Entry> entries = new ArrayList<>();
        double xMin = Double.POSITIVE_INFINITY, xMax = Double.NEGATIVE_INFINITY;
        double yMin = Double.POSITIVE_INFINITY, yMax = Double.NEGATIVE_INFINITY;
        for (int i = 0; i < xs.length; i++) {
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
            toast(getString(R.string.toast_no_ode_points));
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
        curveTypes.clear();
        parametricXExprs.clear();
        parametricYExprs.clear();
        parametricTMin.clear();
        parametricTMax.clear();
        polarExprs.clear();
        polarThetaMin.clear();
        polarThetaMax.clear();
        allEntries.add(entries);
        String label = "ODE: " + expr;
        allExpressions.add(label);
        curveColors.add(Color.parseColor("#00e5c9"));
        curveTypes.add("ode");
        
        List<ILineDataSet> dataSets = new ArrayList<>();
        LineDataSet dataSet = new LineDataSet(entries, label);
        dataSet.setColor(Color.parseColor("#00e5c9"));
        dataSet.setLineWidth(2f);
        dataSet.setDrawCircles(false);
        dataSet.setDrawValues(false);
        dataSets.add(dataSet);
        
        if (!dataSets.isEmpty()) {
            LineData lineData = new LineData(dataSets);
            lineChart.setData(lineData);
            lineChart.invalidate();
        }
        toast(getString(R.string.toast_ode_plotted));
    }

    private void plotOdeComparison(ArrayList<double[]> multiXs, ArrayList<double[]> multiYs,
                                   ArrayList<String> labels, String expr) {
        int[] colors = {
            Color.parseColor("#f38ba8"),
            Color.parseColor("#fab387"),
            Color.parseColor("#f9e2af"),
            Color.parseColor("#a6e3a1")
        };

        allEntries.clear();
        allExpressions.clear();
        curveColors.clear();
        curveTypes.clear();
        parametricXExprs.clear();
        parametricYExprs.clear();
        parametricTMin.clear();
        parametricTMax.clear();
        polarExprs.clear();
        polarThetaMin.clear();
        polarThetaMax.clear();

        double xMin = Double.POSITIVE_INFINITY, xMax = Double.NEGATIVE_INFINITY;
        double yMin = Double.POSITIVE_INFINITY, yMax = Double.NEGATIVE_INFINITY;

        List<ILineDataSet> dataSets = new ArrayList<>();
        for (int i = 0; i < multiXs.size() && i < labels.size(); i++) {
            double[] xs = multiXs.get(i);
            double[] ys = multiYs.get(i);
            String label = labels.get(i);
            int color = colors[i % colors.length];

            ArrayList<Entry> entries = new ArrayList<>();
            for (int j = 0; j < xs.length; j++) {
                if (!Double.isNaN(xs[j]) && !Double.isNaN(ys[j]) &&
                    !Double.isInfinite(xs[j]) && !Double.isInfinite(ys[j])) {
                    entries.add(new Entry((float) xs[j], (float) ys[j]));
                    if (xs[j] < xMin) xMin = xs[j];
                    if (xs[j] > xMax) xMax = xs[j];
                    if (ys[j] < yMin) yMin = ys[j];
                    if (ys[j] > yMax) yMax = ys[j];
                }
            }

            if (!entries.isEmpty()) {
                allEntries.add(entries);
                allExpressions.add(label);
                curveColors.add(color);
                curveTypes.add("ode");

                LineDataSet dataSet = new LineDataSet(entries, label);
                dataSet.setColor(color);
                dataSet.setLineWidth(2f);
                dataSet.setDrawCircles(false);
                dataSet.setDrawValues(false);
                dataSets.add(dataSet);
            }
        }

        if (dataSets.isEmpty()) {
            toast(getString(R.string.toast_no_valid_points));
            return;
        }

        double xPad = (xMax - xMin) * 0.1;
        double yPad = (yMax - yMin) * 0.1;
        xMinInput.setText(String.valueOf(xMin - xPad));
        xMaxInput.setText(String.valueOf(xMax + xPad));
        yMinInput.setText(String.valueOf(yMin - yPad));
        yMaxInput.setText(String.valueOf(yMax + yPad));

        LineData lineData = new LineData(dataSets);
        lineChart.setData(lineData);
        lineChart.invalidate();
        toast(getString(R.string.ode_compare_toast, labels.size(), 0));
    }
    
    private void plotTaylorSeries(String expr, double a, int order, double[] xs, double[] ysOrig, double[] ysTaylor) {
        // Plot original function
        ArrayList<Entry> entriesOrig = new ArrayList<>();
        for (int i = 0; i < xs.length; i++) {
            if (!Double.isNaN(ysOrig[i]) && !Double.isInfinite(ysOrig[i])) {
                entriesOrig.add(new Entry((float) xs[i], (float) ysOrig[i]));
            }
        }
        
        // Plot Taylor approximation
        ArrayList<Entry> entriesTaylor = new ArrayList<>();
        for (int i = 0; i < xs.length; i++) {
            if (!Double.isNaN(ysTaylor[i]) && !Double.isInfinite(ysTaylor[i])) {
                entriesTaylor.add(new Entry((float) xs[i], (float) ysTaylor[i]));
            }
        }
        
        if (entriesOrig.isEmpty() && entriesTaylor.isEmpty()) {
            toast(getString(R.string.toast_no_valid_points));
            return;
        }

        allEntries.clear();
        allExpressions.clear();
        curveColors.clear();
        curveTypes.clear();
        parametricXExprs.clear();
        parametricYExprs.clear();
        parametricTMin.clear();
        parametricTMax.clear();
        polarExprs.clear();
        polarThetaMin.clear();
        polarThetaMax.clear();

        List<ILineDataSet> dataSets = new ArrayList<>();
        
        // Original function (blue)
        if (!entriesOrig.isEmpty()) {
            allEntries.add(entriesOrig);
            String origLabel = "Original: " + expr;
            allExpressions.add(origLabel);
            int origColor = getNextColor();
            curveColors.add(origColor);
            curveTypes.add("regular");
            LineDataSet dsOrig = new LineDataSet(entriesOrig, origLabel);
            dsOrig.setColor(origColor);
            dsOrig.setLineWidth(2f);
            dsOrig.setDrawCircles(false);
            dsOrig.setDrawValues(false);
            dataSets.add(dsOrig);
        }
        
        // Taylor approximation (orange)
        if (!entriesTaylor.isEmpty()) {
            allEntries.add(entriesTaylor);
            String taylorLabel = "Taylor (order " + order + ") at a=" + String.format("%.4g", a);
            allExpressions.add(taylorLabel);
            int taylorColor = getNextColor();
            curveColors.add(taylorColor);
            curveTypes.add("taylor");
            LineDataSet dsTaylor = new LineDataSet(entriesTaylor, taylorLabel);
            dsTaylor.setColor(taylorColor);
            dsTaylor.setLineWidth(2f);
            dsTaylor.setDrawCircles(false);
            dsTaylor.setDrawValues(false);
            dataSets.add(dsTaylor);
        }
        
        if (!dataSets.isEmpty()) {
            LineData lineData = new LineData(dataSets);
            lineChart.setData(lineData);
            
            // Set axis ranges based on original function data
            if (!entriesOrig.isEmpty()) {
                float xMin = Float.POSITIVE_INFINITY, xMax = Float.NEGATIVE_INFINITY;
                float yMin = Float.POSITIVE_INFINITY, yMax = Float.NEGATIVE_INFINITY;
                for (Entry e : entriesOrig) {
                    if (e.getX() < xMin) xMin = e.getX();
                    if (e.getX() > xMax) xMax = e.getX();
                    if (e.getY() < yMin) yMin = e.getY();
                    if (e.getY() > yMax) yMax = e.getY();
                }
                float xPad = (xMax - xMin) * 0.1f;
                float yPad = (yMax - yMin) * 0.1f;
                xMinInput.setText(String.valueOf(xMin - xPad));
                xMaxInput.setText(String.valueOf(xMax + xPad));
                yMinInput.setText(String.valueOf(yMin - yPad));
                yMaxInput.setText(String.valueOf(yMax + yPad));
                
                YAxis yAxisLeft = lineChart.getAxisLeft();
                yAxisLeft.setAxisMinimum(yMin - yPad);
                yAxisLeft.setAxisMaximum(yMax + yPad);
            }
            
            lineChart.invalidate();
        }
        toast(getString(R.string.toast_taylor_plotted, order, String.format("%.4g", a)));
    }
    
    private void plotRegressionData(double[] xs, double[] ys) {
        // Plot scatter points
        ArrayList<Entry> scatterEntries = new ArrayList<>();
        for (int i = 0; i < xs.length; i++) {
            if (!Double.isNaN(xs[i]) && !Double.isInfinite(xs[i]) &&
                !Double.isNaN(ys[i]) && !Double.isInfinite(ys[i])) {
                scatterEntries.add(new Entry((float) xs[i], (float) ys[i]));
            }
        }
        
        if (scatterEntries.isEmpty()) {
            toast(getString(R.string.toast_no_data_points));
            return;
        }
        
        allEntries.clear();
        allExpressions.clear();
        curveColors.clear();
        curveTypes.clear();
        parametricXExprs.clear();
        parametricYExprs.clear();
        parametricTMin.clear();
        parametricTMax.clear();
        polarExprs.clear();
        polarThetaMin.clear();
        polarThetaMax.clear();
        
        List<ILineDataSet> dataSets = new ArrayList<>();
        
        // Scatter data points (pink)
        allEntries.add(scatterEntries);
        String scatterLabel = "Data Points";
        allExpressions.add(scatterLabel);
        int scatterColor = Color.parseColor("#f38ba8");
        curveColors.add(scatterColor);
        curveTypes.add("regular");
        LineDataSet dsScatter = new LineDataSet(scatterEntries, scatterLabel);
        dsScatter.setColor(scatterColor);
        dsScatter.setLineWidth(0f);
        dsScatter.setDrawCircles(true);
        dsScatter.setCircleRadius(4f);
        dsScatter.setCircleColor(scatterColor);
        dsScatter.setDrawValues(false);
        dsScatter.setMode(LineDataSet.Mode.LINEAR);
        dataSets.add(dsScatter);
        
        if (!dataSets.isEmpty()) {
            LineData lineData = new LineData(dataSets);
            lineChart.setData(lineData);
            
            float xMin = Float.POSITIVE_INFINITY, xMax = Float.NEGATIVE_INFINITY;
            float yMin = Float.POSITIVE_INFINITY, yMax = Float.NEGATIVE_INFINITY;
            for (Entry e : scatterEntries) {
                if (e.getX() < xMin) xMin = e.getX();
                if (e.getX() > xMax) xMax = e.getX();
                if (e.getY() < yMin) yMin = e.getY();
                if (e.getY() > yMax) yMax = e.getY();
            }
            float xPad = (xMax - xMin) * 0.1f;
            float yPad = (yMax - yMin) * 0.1f;
            xMinInput.setText(String.valueOf(xMin - xPad));
            xMaxInput.setText(String.valueOf(xMax + xPad));
            yMinInput.setText(String.valueOf(yMin - yPad));
            yMaxInput.setText(String.valueOf(yMax + yPad));
            
            YAxis yAxisLeft = lineChart.getAxisLeft();
            yAxisLeft.setAxisMinimum(yMin - yPad);
            yAxisLeft.setAxisMaximum(yMax + yPad);
        }
        lineChart.invalidate();
        toast(getString(R.string.toast_regression_plotted, xs.length));
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
                        toast(getString(R.string.toast_deleted_mark));
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
                toast(getString(R.string.toast_marked_point, String.format("%.4g", x), String.format("%.4g", y)));
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
        outState.putStringArrayList("curve_types", curveTypes);
        outState.putStringArrayList("param_x_exprs", parametricXExprs);
        outState.putStringArrayList("param_y_exprs", parametricYExprs);
        outState.putStringArrayList("polar_exprs", polarExprs);
        outState.putString("x_min", xMinInput.getText().toString());
        outState.putString("x_max", xMaxInput.getText().toString());
        outState.putString("y_min", yMinInput.getText().toString());
        outState.putString("y_max", yMaxInput.getText().toString());
        outState.putInt("color_index", colorIndex);
        
        // Save parametric and polar parameters
        ArrayList<String> paramTMinStrs = new ArrayList<>();
        ArrayList<String> paramTMaxStrs = new ArrayList<>();
        for (Double d : parametricTMin) paramTMinStrs.add(String.valueOf(d));
        for (Double d : parametricTMax) paramTMaxStrs.add(String.valueOf(d));
        outState.putStringArrayList("param_t_min", paramTMinStrs);
        outState.putStringArrayList("param_t_max", paramTMaxStrs);
        
        ArrayList<String> polarThetaMinStrs = new ArrayList<>();
        ArrayList<String> polarThetaMaxStrs = new ArrayList<>();
        for (Double d : polarThetaMin) polarThetaMinStrs.add(String.valueOf(d));
        for (Double d : polarThetaMax) polarThetaMaxStrs.add(String.valueOf(d));
        outState.putStringArrayList("polar_theta_min", polarThetaMinStrs);
        outState.putStringArrayList("polar_theta_max", polarThetaMaxStrs);
    }
    
    private int getNextColor() {
        int color = COLOR_PALETTE[colorIndex % COLOR_PALETTE.length];
        colorIndex++;
        return color;
    }
    
    private void onAddCurve() {
        String expr = exprInput.getText().toString().trim();
        if (expr.isEmpty()) {
            toast(getString(R.string.toast_enter_expr));
            return;
        }
        allExpressions.add(expr);
        curveColors.add(getNextColor());
        curveTypes.add("regular");
        // Add empty entries list for the new curve (keep existing ODE/Taylor data)
        allEntries.add(new ArrayList<Entry>());
        toast(getString(R.string.toast_added_curve, expr));
        exprInput.setText("");
    }
    
    private void onRemoveCurve() {
        if (allExpressions.isEmpty()) {
            toast(getString(R.string.toast_no_curves_remove));
            return;
        }
        int idx = allExpressions.size() - 1;
        allExpressions.remove(idx);
        if (idx < curveColors.size()) {
            curveColors.remove(idx);
        }
        if (idx < curveTypes.size()) {
            String type = curveTypes.remove(idx);
            // Clean up parametric/polar data if applicable
            // Need to find the correct index in parametric/polar lists
            if ("parametric".equals(type)) {
                // Count parametric curves before this index
                int paramIdx = 0;
                for (int i = 0; i < idx; i++) {
                    if (i < curveTypes.size() && "parametric".equals(curveTypes.get(i))) {
                        paramIdx++;
                    }
                }
                if (paramIdx < parametricXExprs.size()) {
                    parametricXExprs.remove(paramIdx);
                    parametricYExprs.remove(paramIdx);
                    parametricTMin.remove(paramIdx);
                    parametricTMax.remove(paramIdx);
                }
            } else if ("polar".equals(type)) {
                // Count polar curves before this index
                int polarIdx = 0;
                for (int i = 0; i < idx; i++) {
                    if (i < curveTypes.size() && "polar".equals(curveTypes.get(i))) {
                        polarIdx++;
                    }
                }
                if (polarIdx < polarExprs.size()) {
                    polarExprs.remove(polarIdx);
                    polarThetaMin.remove(polarIdx);
                    polarThetaMax.remove(polarIdx);
                }
            }
        }
        if (idx < allEntries.size()) {
            allEntries.remove(idx);
        }
        toast(getString(R.string.toast_removed_curve, idx < allExpressions.size() ? allExpressions.get(idx) : "last"));
    }
    
    private void onPlotAll() {
        if (allExpressions.isEmpty()) {
            toast(getString(R.string.toast_add_curves_first));
            return;
        }
        
        double xMin, xMax, yMin, yMax;
        try {
            xMin = Double.parseDouble(xMinInput.getText().toString().trim());
            xMax = Double.parseDouble(xMaxInput.getText().toString().trim());
            yMin = Double.parseDouble(yMinInput.getText().toString().trim());
            yMax = Double.parseDouble(yMaxInput.getText().toString().trim());
        } catch (NumberFormatException e) {
            toast(getString(R.string.toast_invalid_range));
            return;
        }
        
        if (xMin >= xMax) {
            toast(getString(R.string.toast_xmin_xmax));
            return;
        }
        
        if (yMin >= yMax) {
            toast(getString(R.string.toast_ymin_ymax));
            return;
        }
        
        // Save ODE/Taylor entries before clearing (they have pre-computed data)
        // Use curveTypes.size() as reference since allEntries may be out of sync with allExpressions
        ArrayList<ArrayList<Entry>> savedOdeTaylorEntries = new ArrayList<>();
        for (int i = 0; i < curveTypes.size(); i++) {
            String type = curveTypes.get(i);
            if (("ode".equals(type) || "taylor".equals(type) || "implicit".equals(type)) && i < allEntries.size()) {
                savedOdeTaylorEntries.add(new ArrayList<>(allEntries.get(i)));
            } else {
                savedOdeTaylorEntries.add(null);
            }
        }
        
        allEntries.clear();
        // Limit points to avoid TransactionTooLargeException (1MB limit)
        // Each point is ~8 bytes (float pair), 300 points * 10 curves = ~24KB safe
        int numPoints = Math.min(300, (int)((xMax - xMin) / 0.1));
        numPoints = Math.max(50, Math.min(500, numPoints));
        
        int paramIdx = 0;  // index into parametric lists
        int polarIdx = 0;  // index into polar lists
        
        for (int curveIdx = 0; curveIdx < allExpressions.size(); curveIdx++) {
            String type = curveIdx < curveTypes.size() ? curveTypes.get(curveIdx) : "regular";
            
            if ("parametric".equals(type) && paramIdx < parametricXExprs.size()) {
                // Re-evaluate parametric curve
                double tMin = parametricTMin.get(paramIdx);
                double tMax = parametricTMax.get(paramIdx);
                String xExpr = parametricXExprs.get(paramIdx);
                String yExpr = parametricYExprs.get(paramIdx);
                int n = numPoints;
                double step = (tMax - tMin) / (n - 1);
                double[] ts = new double[n];
                for (int i = 0; i < n; i++) ts[i] = tMin + i * step;
                String xExprSub = xExpr.replaceAll("\\bt\\b", "x");
                String yExprSub = yExpr.replaceAll("\\bt\\b", "x");
                double[] xs = CalcEngine.evaluateArray(xExprSub, ts);
                double[] ys = CalcEngine.evaluateArray(yExprSub, ts);
                if (xs != null && ys != null) {
                    ArrayList<Entry> entries = new ArrayList<>();
                    for (int i = 0; i < n; i++) {
                        if (!Double.isNaN(xs[i]) && !Double.isNaN(ys[i]) &&
                            !Double.isInfinite(xs[i]) && !Double.isInfinite(ys[i])) {
                            entries.add(new Entry((float) xs[i], (float) ys[i]));
                        }
                    }
                    allEntries.add(entries);
                } else {
                    allEntries.add(new ArrayList<Entry>());
                    toast(getString(R.string.toast_error_parametric, CalcEngine.getLastError()));
                }
                paramIdx++;
            } else if ("polar".equals(type) && polarIdx < polarExprs.size()) {
                // Re-evaluate polar curve
                double thetaMin = polarThetaMin.get(polarIdx);
                double thetaMax = polarThetaMax.get(polarIdx);
                String rExpr = polarExprs.get(polarIdx);
                int n = numPoints;
                double step = (thetaMax - thetaMin) / (n - 1);
                double[] thetas = new double[n];
                for (int i = 0; i < n; i++) thetas[i] = thetaMin + i * step;
                String rExprSub = rExpr.replaceAll("\\btheta\\b", "x");
                double[] rs = CalcEngine.evaluateArray(rExprSub, thetas);
                if (rs != null) {
                    ArrayList<Entry> entries = new ArrayList<>();
                    for (int i = 0; i < n; i++) {
                        if (!Double.isNaN(rs[i]) && !Double.isInfinite(rs[i])) {
                            double x = rs[i] * Math.cos(thetas[i]);
                            double y = rs[i] * Math.sin(thetas[i]);
                            entries.add(new Entry((float) x, (float) y));
                        }
                    }
                    allEntries.add(entries);
                } else {
                    allEntries.add(new ArrayList<Entry>());
                    toast(getString(R.string.toast_error_polar, CalcEngine.getLastError()));
                }
                polarIdx++;
            } else if ("ode".equals(type) || "taylor".equals(type)) {
                // ODE and Taylor curves have pre-computed entries, restore them
                // curveIdx should match savedOdeTaylorEntries index since both are based on curveTypes
                if (curveIdx < savedOdeTaylorEntries.size() && savedOdeTaylorEntries.get(curveIdx) != null) {
                    allEntries.add(savedOdeTaylorEntries.get(curveIdx));
                } else {
                    // Data was lost (e.g., allEntries cleared by onAddCurve), try to preserve what we can
                    allEntries.add(new ArrayList<Entry>());
                }
            } else if ("implicit".equals(type)) {
                // Re-plot implicit curve
                // For now, add empty entries (implicit curves are complex to re-plot)
                allEntries.add(new ArrayList<Entry>());
            } else {
                // Regular expression curve
                String expr = allExpressions.get(curveIdx);
                double[] xs = new double[numPoints];
                for (int i = 0; i < numPoints; i++) {
                    xs[i] = xMin + (xMax - xMin) * i / (numPoints - 1);
                }
                
                double[] ys = CalcEngine.evaluateArray(expr, xs);
                if (ys == null) {
                    toast(getString(R.string.toast_error_expr, expr, CalcEngine.getLastError()));
                    allEntries.add(new ArrayList<Entry>());
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
        }
        
        if (allEntries.isEmpty()) {
            toast(getString(R.string.toast_no_valid_points));
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
            toast(getString(R.string.toast_no_data_display));
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
        toast(getString(R.string.toast_plotted_curves, dataSets.size()));
    }
    
    private void openFullScreen() {
        if (allEntries.isEmpty()) {
            toast(getString(R.string.toast_plot_first));
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
        if (totalPoints > maxTotalPoints && !allEntries.isEmpty()) {
            // Downsample
            entriesData = new String[allEntries.size()];
            int pointsPerCurve = Math.max(1, maxTotalPoints / allEntries.size());
            for (int i = 0; i < allEntries.size(); i++) {
                StringBuilder sb = new StringBuilder();
                ArrayList<Entry> entries = allEntries.get(i);
                int step = Math.max(1, entries.size() / pointsPerCurve);
                for (int j = 0; j < entries.size(); j += step) {
                    Entry e = entries.get(j);
                    if (sb.length() > 0) sb.append(";");
                    sb.append(String.format("%.4g,%.4g", e.getX(), e.getY()));
                }
                entriesData[i] = sb.toString();
            }
            toast(getString(R.string.toast_downsampled));
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
