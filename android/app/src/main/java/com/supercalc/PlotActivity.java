package com.supercalc;

import android.content.Intent;
import android.graphics.Color;
import android.os.Bundle;
import android.text.SpannableStringBuilder;
import android.text.Spanned;
import android.text.TextWatcher;
import android.text.Editable;
import android.text.style.ForegroundColorSpan;
import android.view.MotionEvent;
import android.view.View;
import android.view.ViewGroup;
import android.view.ViewParent;
import android.widget.EditText;
import android.widget.HorizontalScrollView;
import android.widget.LinearLayout;
import android.widget.TextView;
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
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public class PlotActivity extends AppCompatActivity {

    private LineChart lineChart;
    private TextInputEditText xMinInput, xMaxInput, yMinInput, yMaxInput;
    private TextInputEditText exprInput;
    private MaterialButton btnZoom;

    /** Curve list + intersection report shown under the expression input. */
    private View curveListContainer;
    private TextView curveListView;
    private TextView intersectResultView;
    private View intersectCard;
    private LinearLayout paramRow;
    private HorizontalScrollView paramScroll;
    private TextView paramHint;
    private final Map<String, EditText> paramFields = new LinkedHashMap<>();
    /** Intersection markers, kept so the full-screen view can draw them too. */
    private final ArrayList<Entry> intersectionMarkers = new ArrayList<>();
    
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
    /** The replaceable marker dataset keeps a second intersection query from stacking old dots. */
    private LineDataSet intersectionDataSet;
    /** Values survive the input box being cleared after a curve is added. */
    private final Map<String, String> parameterValues = new LinkedHashMap<>();
    
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
        curveListContainer = findViewById(R.id.curve_list_container);
        curveListView = findViewById(R.id.curve_list_view);
        intersectResultView = findViewById(R.id.intersect_result_view);
        intersectCard = findViewById(R.id.intersect_card);
        paramRow = findViewById(R.id.param_row);
        paramScroll = findViewById(R.id.param_scroll);
        paramHint = findViewById(R.id.param_hint);
        if (exprInput != null) {
            exprInput.addTextChangedListener(new TextWatcher() {
                @Override
                public void beforeTextChanged(CharSequence s, int a, int b, int c) { }
                @Override
                public void onTextChanged(CharSequence s, int a, int b, int c) { }
                @Override
                public void afterTextChanged(Editable s) { updateParams(); }
            });
        }
        updateParams();
        refreshCurveList();

        // The toolbar's back arrow is drawn from app:navigationIcon; without a
        // click listener it looks tappable but does nothing.
        com.google.android.material.appbar.MaterialToolbar toolbar = findViewById(R.id.toolbar);
        if (toolbar != null) toolbar.setNavigationOnClickListener(v -> finish());

        // This button existed in the layout but was never wired up.
        MaterialButton btnIntersect = findViewById(R.id.btn_find_intersections);
        if (btnIntersect != null) btnIntersect.setOnClickListener(v -> onFindIntersections());
        
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
        
        configureChartInteraction();
        
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
        
        // Handle initial expression from CalcActivity
        if (intent != null && intent.hasExtra("initial_expr")) {
            String initialExpr = intent.getStringExtra("initial_expr");
            if (initialExpr != null && exprInput != null) {
                exprInput.setText(initialExpr);
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
    
    /**
     * Sampling a (resolution+1)^2 grid used to run on the UI thread with one JNI
     * call per point, which froze the screen for seconds at high resolutions.
     * Now the grid is evaluated in a single batched call, off the main thread.
     */
    private void plotImplicitCurve(final String impExpr, int resolution,
                                   final double xMin, final double xMax,
                                   final double yMin, final double yMax) {
        final int res = Math.max(20, Math.min(resolution, 200));
        toast(getString(R.string.implicit_computing));
        new Thread(() -> {
            final ArrayList<Entry> entries =
                    buildImplicitEntries(impExpr, res, xMin, xMax, yMin, yMax);
            runOnUiThread(() -> showImplicitCurve(impExpr, entries));
        }, "implicit-plot").start();
    }

    /** Dense level sets can explode into hundreds of thousands of segments. */
    private static final int MAX_IMPLICIT_ENTRIES = 12000;
    private static final long IMPLICIT_TIME_BUDGET_MS = 3000;
    private boolean implicitTruncated = false;

    /** Pure computation: batched grid sampling + marching squares. */
    private ArrayList<Entry> buildImplicitEntries(String expr, int resolution,
                                                  double xMin, double xMax,
                                                  double yMin, double yMax) {
        ArrayList<Entry> entries = new ArrayList<>();
        implicitTruncated = false;
        final long deadline = System.currentTimeMillis() + IMPLICIT_TIME_BUDGET_MS;
        int side = resolution + 1;
        double dx = (xMax - xMin) / resolution;
        double dy = (yMax - yMin) / resolution;

        // One batched JNI call instead of (resolution+1)^2 single-point calls.
        double[] gx = new double[side * side];
        double[] gy = new double[side * side];
        int k = 0;
        for (int i = 0; i < side; i++) {
            double y = yMin + i * dy;
            for (int j = 0; j < side; j++) {
                gx[k] = xMin + j * dx;
                gy[k] = y;
                k++;
            }
        }
        double[] values = CalcEngine.evaluateXYArray(expr, gx, gy);

        double[][] grid = new double[side][side];
        for (int i = 0; i < side; i++) {
            for (int j = 0; j < side; j++) {
                double val = values == null ? Double.NaN : values[i * side + j];
                grid[i][j] = (Double.isNaN(val) || Double.isInfinite(val)) ? Double.NaN : val;
            }
        }

        outer:
        for (int i = 0; i < resolution; i++) {
            if (System.currentTimeMillis() > deadline
                    || entries.size() >= MAX_IMPLICIT_ENTRIES) {
                implicitTruncated = true;
                break;
            }
            for (int j = 0; j < resolution; j++) {
                if (entries.size() >= MAX_IMPLICIT_ENTRIES) {
                    implicitTruncated = true;
                    break outer;
                }
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
        
        return entries;
    }

    /** UI update for a finished implicit plot, back on the main thread. */
    private void showImplicitCurve(String impExpr, ArrayList<Entry> entries) {
        if (isFinishing() || isDestroyed()) return;
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
        refreshCurveList();
        toast(getString(R.string.toast_implicit_plotted) + ": " + impExpr + " = 0");
        if (implicitTruncated) {
            toast(getString(R.string.implicit_truncated));
        }
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
        curveColors.add(Color.parseColor("#22D3EE"));
        curveTypes.add("ode");
        
        List<ILineDataSet> dataSets = new ArrayList<>();
        LineDataSet dataSet = new LineDataSet(entries, label);
        dataSet.setColor(Color.parseColor("#22D3EE"));
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
            Color.parseColor("#F472B6"),
            Color.parseColor("#FB923C"),
            Color.parseColor("#FBBF24"),
            Color.parseColor("#34D399"),
            Color.parseColor("#60A5FA")
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
        int scatterColor = Color.parseColor("#F472B6");
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
    
    /**
     * Keep MPAndroidChart's native interaction model intact inside the
     * NestedScrollView: one finger drags the complete coordinate viewport and
     * two fingers pinch-zoom both axes around the focal point. The parent used
     * to win vertical MOVE events, which made the grid look static on phones.
     */
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
        lineChart.setOnTouchListener((view, event) -> {
            switch (event.getActionMasked()) {
                case MotionEvent.ACTION_DOWN:
                case MotionEvent.ACTION_MOVE:
                case MotionEvent.ACTION_POINTER_DOWN:
                    requestChartParentsNotToIntercept(true);
                    break;
                case MotionEvent.ACTION_UP:
                case MotionEvent.ACTION_CANCEL:
                    requestChartParentsNotToIntercept(false);
                    break;
                default:
                    break;
            }
            // Returning false lets LineChart consume the event and perform its
            // built-in drag/pinch transform after the parent is disarmed.
            return false;
        });
    }

    private void requestChartParentsNotToIntercept(boolean disallow) {
        ViewParent parent = lineChart.getParent();
        while (parent != null) {
            parent.requestDisallowInterceptTouchEvent(disallow);
            parent = parent.getParent();
        }
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
        LineData lineData = lineChart.getData();
        if (lineData != null) lineData.notifyDataChanged();
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
        rememberParameterValues();
        boolean hadVisiblePlot = lineChart.getLineData() != null
                && lineChart.getLineData().getDataSetCount() > 0;
        // Keep the symbolic expression (with parameters) in the list; values are
        // substituted when plotting so the controls stay live.
        allExpressions.add(expr);
        curveColors.add(getNextColor());
        curveTypes.add("regular");
        // Add empty entries list for the new curve (keep existing ODE/Taylor data)
        allEntries.add(new ArrayList<Entry>());
        clearIntersectionMarkers();
        toast(getString(R.string.toast_added_curve, expr));
        exprInput.setText("");
        updateParams();
        refreshCurveList();
        if (hadVisiblePlot) onPlotAll();
    }

    /**
     * Rebuild the parameter fields for the expression currently being typed and
     * for every curve already in the list. This is important after Add Curve:
     * the input is cleared, but a parameter such as `a` still belongs to the
     * saved curve and must remain editable.
     */
    private void updateParams() {
        if (paramRow == null || exprInput == null) return;
        rememberParameterValues();
        StringBuilder source = new StringBuilder(exprInput.getText().toString());
        if (allExpressions != null) {
            for (int i = 0; i < allExpressions.size(); i++) {
                String type = i < curveTypes.size() ? curveTypes.get(i) : "regular";
                if ("regular".equals(type)) {
                    source.append('\n').append(allExpressions.get(i));
                } else if ("parametric".equals(type)) {
                    int index = parameterIndexBefore(i, "parametric");
                    if (index < parametricXExprs.size()) {
                        source.append('\n').append(parametricXExprs.get(index));
                        source.append('\n').append(parametricYExprs.get(index));
                    }
                } else if ("polar".equals(type)) {
                    int index = parameterIndexBefore(i, "polar");
                    if (index < polarExprs.size()) source.append('\n').append(polarExprs.get(index));
                }
            }
        }
        ParamSupport.rebuild(this, paramRow, paramHint, paramScroll, paramFields,
                source.toString());
        for (Map.Entry<String, EditText> entry : paramFields.entrySet()) {
            String saved = parameterValues.get(entry.getKey());
            if (saved != null && !saved.equals(entry.getValue().getText().toString())) {
                entry.getValue().setText(saved);
            }
        }
    }

    private void rememberParameterValues() {
        for (Map.Entry<String, EditText> entry : paramFields.entrySet()) {
            parameterValues.put(entry.getKey(), entry.getValue().getText().toString().trim());
        }
    }

    private int parameterIndexBefore(int curveIndex, String type) {
        int index = 0;
        for (int i = 0; i < curveIndex; i++) {
            if (i < curveTypes.size() && type.equals(curveTypes.get(i))) index++;
        }
        return index;
    }

    private String withParams(String expr) {
        rememberParameterValues();
        return ParamSupport.substitute(expr, paramFields);
    }
    
    private void onRemoveCurve() {
        if (allExpressions.isEmpty()) {
            toast(getString(R.string.toast_no_curves_remove));
            return;
        }
        int idx = allExpressions.size() - 1;
        boolean hadVisiblePlot = lineChart.getLineData() != null
                && lineChart.getLineData().getDataSetCount() > 0;
        String removedExpression = allExpressions.get(idx);
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
        clearIntersectionMarkers();
        updateParams();
        toast(getString(R.string.toast_removed_curve, removedExpression));
        refreshCurveList();
        if (hadVisiblePlot) {
            if (allExpressions.isEmpty()) {
                lineChart.clear();
                lineChart.invalidate();
            } else {
                onPlotAll();
            }
        }
    }

    /** Colour-coded list of the curves currently on the plot. */
    private void refreshCurveList() {
        if (curveListContainer == null || curveListView == null) return;
        if (allExpressions == null || allExpressions.isEmpty()) {
            curveListContainer.setVisibility(View.GONE);
            return;
        }
        curveListContainer.setVisibility(View.VISIBLE);
        SpannableStringBuilder sb = new SpannableStringBuilder();
        for (int i = 0; i < allExpressions.size(); i++) {
            int color = (curveColors != null && i < curveColors.size())
                    ? curveColors.get(i) : Color.parseColor("#E6EAFF");
            sb.append(String.valueOf(i + 1)).append(". ");
            int start = sb.length();
            sb.append("\u25CF");
            sb.setSpan(new ForegroundColorSpan(color), start, sb.length(),
                    Spanned.SPAN_EXCLUSIVE_EXCLUSIVE);
            sb.append(" ").append(allExpressions.get(i));
            if (i < allExpressions.size() - 1) sb.append("\n");
        }
        curveListView.setText(sb);
    }

    /** Remove stale intersection dots when the curve set changes or is re-plotted. */
    private void clearIntersectionMarkers() {
        intersectionMarkers.clear();
        LineData data = lineChart == null ? null : lineChart.getLineData();
        if (data != null && intersectionDataSet != null) {
            data.removeDataSet(intersectionDataSet);
            data.notifyDataChanged();
            lineChart.notifyDataSetChanged();
            lineChart.invalidate();
        }
        intersectionDataSet = null;
        if (intersectCard != null) intersectCard.setVisibility(View.GONE);
    }

    /** Draw the current intersection list as a replaceable marker dataset. */
    private void renderIntersectionMarkers() {
        LineData data = lineChart == null ? null : lineChart.getLineData();
        if (data == null) return;
        if (intersectionDataSet != null) data.removeDataSet(intersectionDataSet);
        intersectionDataSet = null;
        if (intersectionMarkers.isEmpty()) {
            data.notifyDataChanged();
            lineChart.notifyDataSetChanged();
            lineChart.invalidate();
            return;
        }
        intersectionDataSet = new LineDataSet(
                new ArrayList<>(intersectionMarkers), getString(R.string.intersect));
        intersectionDataSet.setColor(Color.TRANSPARENT);
        intersectionDataSet.setCircleColor(Color.parseColor("#FBBF24"));
        intersectionDataSet.setCircleRadius(5f);
        intersectionDataSet.setDrawCircles(true);
        intersectionDataSet.setDrawValues(false);
        intersectionDataSet.setLineWidth(0f);
        intersectionDataSet.setHighlightEnabled(false);
        data.addDataSet(intersectionDataSet);
        data.notifyDataChanged();
        lineChart.notifyDataSetChanged();
        lineChart.invalidate();
    }

    /**
     * Intersections of the first two function curves over the current X range.
     * Mirrors the desktop implementation: sample the difference, look for sign
     * changes, refine with bisection, then deduplicate.
     */
    private void onFindIntersections() {
        if (allExpressions == null || allExpressions.size() < 2) {
            toast(getString(R.string.toast_need_two_curves));
            return;
        }
        int first = -1, second = -1;
        for (int i = 0; i < allExpressions.size(); i++) {
            String type = i < curveTypes.size() ? curveTypes.get(i) : "regular";
            if (!"regular".equals(type)) continue;      // function curves only
            if (first < 0) {
                first = i;
            } else if (second < 0) {
                second = i;
                break;
            }
        }
        if (first < 0 || second < 0) {
            toast(getString(R.string.toast_need_two_curves));
            return;
        }

        double xMin, xMax;
        try {
            xMin = Double.parseDouble(xMinInput.getText().toString().trim());
            xMax = Double.parseDouble(xMaxInput.getText().toString().trim());
        } catch (NumberFormatException e) {
            toast(getString(R.string.toast_invalid_range));
            return;
        }
        if (xMin >= xMax) {
            toast(getString(R.string.toast_xmin_xmax));
            return;
        }

        List<double[]> points = findIntersections(
                withParams(allExpressions.get(first)), withParams(allExpressions.get(second)),
                xMin, xMax);
        if (points.isEmpty()) {
            clearIntersectionMarkers();
            toast(getString(R.string.toast_no_intersections));
            return;
        }

        StringBuilder report = new StringBuilder(getString(R.string.intersect_result_title)).append(":\n");
        ArrayList<Entry> markers = new ArrayList<>();
        for (int i = 0; i < points.size(); i++) {
            double[] p = points.get(i);
            report.append("(").append(String.format("%.4g", p[0]))
                  .append(", ").append(String.format("%.4g", p[1])).append(")");
            if (i < points.size() - 1) report.append("\n");
            markers.add(new Entry((float) p[0], (float) p[1]));
        }
        // Keep them so the full-screen view can draw the same markers.
        intersectionMarkers.clear();
        intersectionMarkers.addAll(markers);
        if (intersectResultView != null) {
            intersectResultView.setText(report.toString());
        }
        if (intersectCard != null) intersectCard.setVisibility(View.VISIBLE);

        // Mark them on the chart: circles only, the connecting line is invisible.
        // If the user queried before pressing Plot All, build the curves first so
        // the result is visible rather than only appearing in the report card.
        if (lineChart.getLineData() == null
                || lineChart.getLineData().getDataSetCount() == 0) onPlotAll();
        renderIntersectionMarkers();
        toast(getString(R.string.toast_found_intersections, points.size()));
    }

    private static boolean isFinite(double value) {
        return !Double.isNaN(value) && !Double.isInfinite(value);
    }

    private List<double[]> findIntersections(String fa, String fb, double xMin, double xMax) {
        List<double[]> result = new ArrayList<>();
        int n = 400;
        double step = (xMax - xMin) / (n - 1);
        double[] xs = new double[n];
        for (int i = 0; i < n; i++) xs[i] = xMin + i * step;

        double[] ya = CalcEngine.evaluateArray(fa, xs);
        double[] yb = CalcEngine.evaluateArray(fb, xs);
        if (ya == null || yb == null) return result;

        final double tolZero = 1e-6;
        final double tolDup = 1e-4;
        List<Double> foundX = new ArrayList<>();
        List<Double> foundY = new ArrayList<>();

        for (int i = 0; i < n; i++) {
            if (!isFinite(ya[i]) || !isFinite(yb[i])) continue;
            if (Math.abs(ya[i] - yb[i]) < tolZero) {
                foundX.add(xs[i]);
                foundY.add((ya[i] + yb[i]) / 2.0);
            }
        }

        String diff = "(" + fa + ")-(" + fb + ")";
        for (int i = 0; i < n - 1; i++) {
            if (!isFinite(ya[i]) || !isFinite(yb[i])
                    || !isFinite(ya[i + 1]) || !isFinite(yb[i + 1])) continue;
            double d1 = ya[i] - yb[i];
            double d2 = ya[i + 1] - yb[i + 1];
            if (d1 == 0.0 || d2 == 0.0 || d1 * d2 >= 0) continue;
            double root = CalcEngine.solveBisection(diff, xs[i], xs[i + 1]);
            if (Double.isNaN(root)) continue;
            double y = CalcEngine.evaluate(fa, root);
            if (isFinite(y)) {
                foundX.add(root);
                foundY.add(y);
            }
        }

        // Sort by x, then drop duplicates that are closer than tolDup.
        Integer[] order = new Integer[foundX.size()];
        for (int i = 0; i < order.length; i++) order[i] = i;
        java.util.Arrays.sort(order, (p, q) -> Double.compare(foundX.get(p), foundX.get(q)));
        double lastX = Double.NaN;
        for (int idx : order) {
            double x = foundX.get(idx);
            if (!Double.isNaN(lastX) && Math.abs(x - lastX) <= tolDup) continue;
            lastX = x;
            result.add(new double[]{x, foundY.get(idx)});
        }
        return result;
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
        // Sample density is a function of the visible x range, NOT a constant.
        //
        // The old code used `(xMax - xMin) / 0.02` clamped to 1500. That is
        // fine at small ranges but collapses as the window grows: tan(x) over
        // [-10,10] got ~157 samples per branch, over [-100,100] only ~47, and
        // over [-1000,1000] barely 2.4 -- at which point the branches alias
        // into a comb of near-vertical strokes. Zooming out must add samples,
        // not stretch a fixed budget thinner.
        int numPoints = PlotSampling.sampleCount2D(xMin, xMax);
        
        int paramIdx = 0;  // index into parametric lists
        int polarIdx = 0;  // index into polar lists
        
        for (int curveIdx = 0; curveIdx < allExpressions.size(); curveIdx++) {
            String type = curveIdx < curveTypes.size() ? curveTypes.get(curveIdx) : "regular";
            
            if ("parametric".equals(type) && paramIdx < parametricXExprs.size()) {
                // Re-evaluate parametric curve
                double tMin = parametricTMin.get(paramIdx);
                double tMax = parametricTMax.get(paramIdx);
                String xExpr = withParams(parametricXExprs.get(paramIdx));
                String yExpr = withParams(parametricYExprs.get(paramIdx));
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
                String rExpr = withParams(polarExprs.get(polarIdx));
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
                // Substituted here (not when added) so parameters stay live.
                String expr = withParams(allExpressions.get(curveIdx));
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

                // Add extra samples next to any pole so every tan branch reaches
                // the same clipped height, then re-evaluate on the finer grid.
                double[] fineXs = CurveBreak.refineNearPoles(
                        xs, ys, (float) yMin, (float) yMax, 8);
                if (fineXs.length != xs.length) {
                    double[] fineYs = CalcEngine.evaluateArray(expr, fineXs);
                    if (fineYs != null) {
                        xs = fineXs;
                        ys = fineYs;
                    }
                }

                ArrayList<Entry> entries = new ArrayList<>();
                for (int i = 0; i < xs.length; i++) {
                    if (!Double.isNaN(ys[i]) && !Double.isInfinite(ys[i])) {
                        // Keep every finite sample (even far outside the visible
                        // band) so CurveBreak can locate the poles; the renderer
                        // splits the polyline there instead of connecting across.
                        entries.add(new Entry((float) xs[i], (float) ys[i]));
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
            String kind = i < curveTypes.size() ? curveTypes.get(i) : "regular";
            boolean xyBreaks = "parametric".equals(kind) || "polar".equals(kind);
            addCurveDataSets(dataSets, allEntries.get(i), allExpressions.get(i),
                    curveColors.get(i), (float) yMin, (float) yMax, xyBreaks);
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
        // setData replaces the previous marker datasets; restore intersection
        // dots from the query model so re-plotting never hides the result.
        intersectionDataSet = null;
        if (!intersectionMarkers.isEmpty()) renderIntersectionMarkers();
        
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
        legend.setTextColor(Color.parseColor("#E6EAFF"));
        
        Description desc = lineChart.getDescription();
        desc.setEnabled(false);
        
        lineChart.invalidate();
        refreshCurveList();
        toast(getString(R.string.toast_plotted_curves, dataSets.size()));
    }

    /**
     * Add one curve to {@code dataSets}, split into continuous segments so a
     * polyline never connects across an asymptote (tan(x), 1/x, ...).  The first
     * segment carries the legend label; the rest are anonymous so the legend
     * stays readable.
     */
    private void addCurveDataSets(List<ILineDataSet> dataSets, ArrayList<Entry> entries,
                                  String label, int color, float yLo, float yHi) {
        addCurveDataSets(dataSets, entries, label, color, yLo, yHi, false);
    }

    private void addCurveDataSets(List<ILineDataSet> dataSets, ArrayList<Entry> entries,
                                  String label, int color, float yLo, float yHi,
                                  boolean xyBreaks) {
        if (entries.isEmpty()) return;
        double[] xs = new double[entries.size()];
        double[] ys = new double[entries.size()];
        for (int i = 0; i < entries.size(); i++) {
            xs[i] = entries.get(i).getX();
            ys[i] = entries.get(i).getY();
        }
        List<CurveBreak.Segment> segments = xyBreaks
                ? CurveBreak.splitXY(xs, ys)
                : CurveBreak.split(xs, ys, yLo, yHi);
        if (segments.isEmpty()) {
            // Nothing finite: fall back to a plain dataset so nothing disappears.
            segments = new ArrayList<>();
            CurveBreak.Segment all = new CurveBreak.Segment();
            for (Entry e : entries) { all.xs.add(e.getX()); all.ys.add(e.getY()); }
            segments.add(all);
        }
        boolean first = true;
        for (CurveBreak.Segment seg : segments) {
            if (seg.size() < 1) continue;
            LineDataSet ds = new LineDataSet(seg.toEntries(), first ? label : "");
            ds.setColor(color);
            ds.setLineWidth(2f);
            ds.setDrawCircles(false);
            ds.setDrawValues(false);
            dataSets.add(ds);
            first = false;
        }
    }

    /**
     * Serialize one curve's entries as continuous segments.
     * Format: {@code "x,y;x,y| x,y;x,y| ..."} -- segments separated by '|',
     * points inside a segment separated by ';'.  {@code step} > 1 downsamples.
     */
    private String serializeSegments(ArrayList<Entry> entries, int step) {
        return serializeSegments(entries, step, false);
    }

    private String serializeSegments(ArrayList<Entry> entries, int step, boolean xyBreaks) {
        if (entries.isEmpty()) return "";
        double[] xs = new double[entries.size()];
        double[] ys = new double[entries.size()];
        for (int i = 0; i < entries.size(); i++) {
            xs[i] = entries.get(i).getX();
            ys[i] = entries.get(i).getY();
        }
        // Split using the current y-range so poles are cut consistently.
        float yLo = Float.NEGATIVE_INFINITY, yHi = Float.POSITIVE_INFINITY;
        try {
            yLo = Float.parseFloat(yMinInput.getText().toString().trim());
            yHi = Float.parseFloat(yMaxInput.getText().toString().trim());
        } catch (Exception ignored) { /* keep infinite band */ }

        List<CurveBreak.Segment> segments = xyBreaks
                ? CurveBreak.splitXY(xs, ys)
                : CurveBreak.split(xs, ys, yLo, yHi);
        if (segments.isEmpty()) return "";

        StringBuilder out = new StringBuilder();
        for (CurveBreak.Segment seg : segments) {
            if (seg.size() == 0) continue;
            if (out.length() > 0) out.append("|");
            boolean firstPoint = true;
            for (int j = 0; j < seg.size(); j += Math.max(1, step)) {
                if (!firstPoint) out.append(";");
                out.append(String.format("%.6g,%.6g", seg.xs.get(j), seg.ys.get(j)));
                firstPoint = false;
            }
        }
        return out.toString();
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
        // Hard cap on how many points we hand to the full-screen Intent. The
        // chart library re-renders every Entry on each draw, so an unbounded
        // transfer would make full screen stutter.
        final int maxTotalPoints = 60000; // Safe limit for Intent
        int totalPoints = 0;
        for (ArrayList<Entry> entries : allEntries) {
            totalPoints += entries.size();
        }

        String[] entriesData;
        // Encode each curve as its continuous segments joined by '|', with the
        // points inside a segment joined by ';'.  This carries the break
        // information across the Intent so the full-screen view also draws clean
        // gaps at asymptotes.
        entriesData = new String[allEntries.size()];
        if (totalPoints > maxTotalPoints && !allEntries.isEmpty()) {
            // Decimate to the budget. Crucially the stride is derived from the
            // visible x range (pixel-width work), not from a constant -- a fixed
            // "1500 points" budget is exactly what made large ranges alias, and
            // repeating that mistake here would undo the fix in full screen.
            int pointsPerCurve = Math.max(1, maxTotalPoints / allEntries.size());
            int screenCols = Math.max(1, Math.min(pointsPerCurve, 3000));
            for (int i = 0; i < allEntries.size(); i++) {
                ArrayList<Entry> entries = allEntries.get(i);
                int step = Math.max(1, entries.size() / screenCols);
                String kind = i < curveTypes.size() ? curveTypes.get(i) : "regular";
                boolean xyBreaks = "parametric".equals(kind) || "polar".equals(kind);
                entriesData[i] = serializeSegments(entries, step, xyBreaks);
            }
            toast(getString(R.string.toast_downsampled));
        } else {
            for (int i = 0; i < allEntries.size(); i++) {
                String kind = i < curveTypes.size() ? curveTypes.get(i) : "regular";
                boolean xyBreaks = "parametric".equals(kind) || "polar".equals(kind);
                entriesData[i] = serializeSegments(allEntries.get(i), 1, xyBreaks);
            }
        }
        
        int[] colors = new int[curveColors.size()];
        for (int i = 0; i < curveColors.size(); i++) {
            colors[i] = curveColors.get(i);
        }

        // Intersection markers must survive the jump to full screen.
        StringBuilder markerData = new StringBuilder();
        for (Entry e : intersectionMarkers) {
            if (markerData.length() > 0) markerData.append(";");
            markerData.append(String.format("%.4g,%.4g", e.getX(), e.getY()));
        }
        intent.putExtra("intersect_points", markerData.toString());
        StringBuilder markedData = new StringBuilder();
        for (Entry e : markedPoints) {
            if (markedData.length() > 0) markedData.append(";");
            markedData.append(String.format("%.6g,%.6g", e.getX(), e.getY()));
        }
        intent.putExtra("marked_points", markedData.toString());
        
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
