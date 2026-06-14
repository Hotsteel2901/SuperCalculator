package com.supercalc;

import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.text.method.ScrollingMovementMethod;
import android.widget.ArrayAdapter;
import android.widget.AutoCompleteTextView;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.widget.NestedScrollView;
import com.google.android.material.button.MaterialButton;
import com.google.android.material.chip.Chip;
import com.google.android.material.card.MaterialCardView;
import com.github.mikephil.charting.charts.LineChart;
import com.github.mikephil.charting.data.Entry;
import com.github.mikephil.charting.data.LineData;
import com.github.mikephil.charting.data.LineDataSet;
import com.github.mikephil.charting.components.XAxis;
import com.github.mikephil.charting.components.YAxis;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.time.LocalDate;
import java.time.temporal.ChronoUnit;
import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;

public class CalcActivity extends AppCompatActivity {

    private EditText exprInput, xInput, aInput, bInput, guessInput;
    private EditText xParamInput, yParamInput, tMinInput, tMaxInput;
    private EditText rPolarInput, thetaMinInput, thetaMaxInput;
    private EditText taylorOrderInput;
    private EditText odeExprInput, odeX0Input, odeY0Input, odeXEndInput, odeStepsInput;
    private EditText odeCompareExprInput, odeCompareX0Input, odeCompareY0Input, odeCompareXEndInput, odeCompareStepsInput;
    private EditText statsDataInput;
    private EditText areaGInput;
    private EditText volGInput;
    private String volMode = "disk";
    private EditText sysFInput, sysGInput, sysX0Input, sysY0Input;
    private EditText dfExprInput, dfGridInput, dfXminInput, dfXmaxInput, dfYminInput, dfYmaxInput, dfIcInput;
    private EditText matrixAInput, matrixBInput;
    private EditText laplaceExprInput, laplaceParamInput;
    private TextView resultView;
    private NestedScrollView scrollView;
    private LineChart lineChart;
    private MaterialCardView graphCard;
    private EditText dataXColInput, dataYColInput;
    private AutoCompleteTextView dataTrendSpinner;
    private TextView dataStatusView;
    private List<double[]> dataRows = new ArrayList<>();
    private String dataFileName = "";
    private TextView historyListView;
    private static final String PREFS_NAME = "SuperCalcPrefs";
    private static final String KEY_HISTORY = "calc_history";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_calc);

        exprInput  = findViewById(R.id.expr_input);
        xInput     = findViewById(R.id.x_input);
        aInput     = findViewById(R.id.a_input);
        bInput     = findViewById(R.id.b_input);
        guessInput = findViewById(R.id.guess_input);
        xParamInput = findViewById(R.id.x_param_input);
        yParamInput = findViewById(R.id.y_param_input);
        tMinInput  = findViewById(R.id.t_min_input);
        tMaxInput  = findViewById(R.id.t_max_input);
        rPolarInput = findViewById(R.id.r_polar_input);
        thetaMinInput = findViewById(R.id.theta_min_input);
        thetaMaxInput = findViewById(R.id.theta_max_input);
        taylorOrderInput = findViewById(R.id.taylor_order_input);
        odeExprInput = findViewById(R.id.ode_expr_input);
        odeX0Input = findViewById(R.id.ode_x0_input);
        odeY0Input = findViewById(R.id.ode_y0_input);
        odeXEndInput = findViewById(R.id.ode_xend_input);
        odeStepsInput = findViewById(R.id.ode_steps_input);
        resultView = findViewById(R.id.result_view);
        resultView.setMovementMethod(new ScrollingMovementMethod());
        scrollView = findViewById(R.id.main_scroll);
        lineChart  = findViewById(R.id.line_chart);
        graphCard  = findViewById(R.id.graph_card);

        // Operation buttons — MaterialButton extends Button, so findViewById works
        MaterialButton btnEval   = findViewById(R.id.btn_evaluate);
        MaterialButton btnDeriv  = findViewById(R.id.btn_derivative);
        MaterialButton btnDeriv2 = findViewById(R.id.btn_derivative2);
        MaterialButton btnInt    = findViewById(R.id.btn_integrate);
        MaterialButton btnSolve  = findViewById(R.id.btn_solve);
        MaterialButton btnPlot   = findViewById(R.id.btn_plot);
        MaterialButton btnFindMin = findViewById(R.id.btn_find_min);
        MaterialButton btnFindMax = findViewById(R.id.btn_find_max);
        MaterialButton btnClear  = findViewById(R.id.btn_clear);
        MaterialButton btnScanRoots = findViewById(R.id.btn_scan_roots);
        MaterialButton btnPlot3D = findViewById(R.id.btn_plot_3d);
        MaterialButton btnTable = findViewById(R.id.btn_table);
        MaterialButton btnTangent = findViewById(R.id.btn_tangent);
        MaterialButton btnNormal = findViewById(R.id.btn_normal);
        MaterialButton btnArcLength = findViewById(R.id.btn_arc_length);
        MaterialButton btnFFT = findViewById(R.id.btn_fft);
        MaterialButton btnLimit = findViewById(R.id.btn_limit);
        MaterialButton btnLimitLeft = findViewById(R.id.btn_limit_left);
        MaterialButton btnLimitRight = findViewById(R.id.btn_limit_right);

        btnEval  .setOnClickListener(v -> onEvaluate());
        btnDeriv .setOnClickListener(v -> onDerivative());
        btnDeriv2.setOnClickListener(v -> onDerivative2());
        btnInt   .setOnClickListener(v -> onIntegrate());
        btnSolve .setOnClickListener(v -> onSolve());
        btnPlot  .setOnClickListener(v -> openPlot());
        btnFindMin.setOnClickListener(v -> onFindExtremum(true));
        btnFindMax.setOnClickListener(v -> onFindExtremum(false));
        btnClear .setOnClickListener(v -> resultView.setText(""));
        btnScanRoots.setOnClickListener(v -> onScanRoots());
        btnPlot3D.setOnClickListener(v -> openPlot3D());
        btnTable.setOnClickListener(v -> onGenerateTable());
        btnTangent.setOnClickListener(v -> onTangentNormal(true));
        btnNormal.setOnClickListener(v -> onTangentNormal(false));
        btnArcLength.setOnClickListener(v -> onArcLength());
        btnFFT.setOnClickListener(v -> onFFT());
        btnLimit.setOnClickListener(v -> onLimit());
        btnLimitLeft.setOnClickListener(v -> onLimitSide(true));
        btnLimitRight.setOnClickListener(v -> onLimitSide(false));

        MaterialButton btnTaylor = findViewById(R.id.btn_taylor);
        MaterialButton btnTaylorPlot = findViewById(R.id.btn_taylor_plot);
        btnTaylor.setOnClickListener(v -> onTaylor());
        btnTaylorPlot.setOnClickListener(v -> onTaylorPlot());

        MaterialButton btnOdeSolve = findViewById(R.id.btn_ode_solve);
        MaterialButton btnOdePlot = findViewById(R.id.btn_ode_plot);
        btnOdeSolve.setOnClickListener(v -> onOdeSolve());
        btnOdePlot.setOnClickListener(v -> onOdePlot());

        // ODE Method Comparison
        odeCompareExprInput = findViewById(R.id.ode_compare_expr_input);
        odeCompareX0Input = findViewById(R.id.ode_compare_x0_input);
        odeCompareY0Input = findViewById(R.id.ode_compare_y0_input);
        odeCompareXEndInput = findViewById(R.id.ode_compare_xend_input);
        odeCompareStepsInput = findViewById(R.id.ode_compare_steps_input);
        MaterialButton btnOdeCompare = findViewById(R.id.btn_ode_compare);
        MaterialButton btnOdeComparePlot = findViewById(R.id.btn_ode_compare_plot);
        btnOdeCompare.setOnClickListener(v -> onOdeCompare());
        btnOdeComparePlot.setOnClickListener(v -> onOdeComparePlot());

        // Direction Field
        dfExprInput = findViewById(R.id.df_expr_input);
        dfGridInput = findViewById(R.id.df_grid_input);
        dfXminInput = findViewById(R.id.df_xmin_input);
        dfXmaxInput = findViewById(R.id.df_xmax_input);
        dfYminInput = findViewById(R.id.df_ymin_input);
        dfYmaxInput = findViewById(R.id.df_ymax_input);
        dfIcInput = findViewById(R.id.df_ic_input);
        MaterialButton btnDfPlot = findViewById(R.id.btn_df_plot);
        MaterialButton btnDfSolve = findViewById(R.id.btn_df_solve);
        btnDfPlot.setOnClickListener(v -> onDirectionField(false));
        btnDfSolve.setOnClickListener(v -> onDirectionField(true));

        // Statistics
        statsDataInput = findViewById(R.id.stats_data_input);
        MaterialButton btnStatsCompute = findViewById(R.id.btn_stats_compute);
        MaterialButton btnStatsSort = findViewById(R.id.btn_stats_sort);
        MaterialButton btnStatsHistogram = findViewById(R.id.btn_stats_histogram);
        btnStatsCompute.setOnClickListener(v -> onStatsCompute());
        btnStatsSort.setOnClickListener(v -> onStatsSort());
        btnStatsHistogram.setOnClickListener(v -> onStatsHistogram());

        // Curve Fitting / Regression
        EditText regXInput = findViewById(R.id.reg_x_input);
        EditText regYInput = findViewById(R.id.reg_y_input);
        EditText regDegreeInput = findViewById(R.id.reg_degree_input);
        MaterialButton btnRegLinear = findViewById(R.id.btn_reg_linear);
        MaterialButton btnRegQuad = findViewById(R.id.btn_reg_quad);
        MaterialButton btnRegPoly = findViewById(R.id.btn_reg_poly);
        MaterialButton btnRegExp = findViewById(R.id.btn_reg_exp);
        MaterialButton btnRegPower = findViewById(R.id.btn_reg_power);
        MaterialButton btnRegLog = findViewById(R.id.btn_reg_log);
        MaterialButton btnRegPlot = findViewById(R.id.btn_reg_plot);
        btnRegLinear.setOnClickListener(v -> onRegLinear(regXInput, regYInput));
        btnRegQuad.setOnClickListener(v -> onRegPoly(regXInput, regYInput, 2));
        btnRegPoly.setOnClickListener(v -> {
            int deg = 3;
            try { deg = Integer.parseInt(regDegreeInput.getText().toString().trim()); } catch (Exception ignored) {}
            onRegPoly(regXInput, regYInput, deg);
        });
        btnRegExp.setOnClickListener(v -> onRegExponential(regXInput, regYInput));
        btnRegPower.setOnClickListener(v -> onRegPower(regXInput, regYInput));
        btnRegLog.setOnClickListener(v -> onRegLogarithmic(regXInput, regYInput));
        btnRegPlot.setOnClickListener(v -> onRegPlot(regXInput, regYInput));

        // Area Between Curves
        areaGInput = findViewById(R.id.area_g_input);
        MaterialButton btnAreaBetween = findViewById(R.id.btn_area_between);
        btnAreaBetween.setOnClickListener(v -> onAreaBetweenCurves());

        // Volume of Revolution
        volGInput = findViewById(R.id.vol_g_input);
        MaterialButton btnVolDisk = findViewById(R.id.btn_vol_disk);
        MaterialButton btnVolWasher = findViewById(R.id.btn_vol_washer);
        MaterialButton btnVolShell = findViewById(R.id.btn_vol_shell);
        btnVolDisk.setOnClickListener(v -> { volMode = "disk"; onVolumeCompute(); });
        btnVolWasher.setOnClickListener(v -> { volMode = "washer"; onVolumeCompute(); });
        btnVolShell.setOnClickListener(v -> { volMode = "shell"; onVolumeCompute(); });

        // Nonlinear System Solver (2D)
        sysFInput = findViewById(R.id.sys_f_input);
        sysGInput = findViewById(R.id.sys_g_input);
        sysX0Input = findViewById(R.id.sys_x0_input);
        sysY0Input = findViewById(R.id.sys_y0_input);
        MaterialButton btnSolveSystem = findViewById(R.id.btn_solve_system);
        btnSolveSystem.setOnClickListener(v -> onSolveSystem2d());

        // Matrix Operations
        matrixAInput = findViewById(R.id.matrix_a_input);
        matrixBInput = findViewById(R.id.matrix_b_input);
        MaterialButton btnMatAdd = findViewById(R.id.btn_mat_add);
        MaterialButton btnMatSub = findViewById(R.id.btn_mat_sub);
        MaterialButton btnMatMul = findViewById(R.id.btn_mat_mul);
        MaterialButton btnMatDet = findViewById(R.id.btn_mat_det);
        MaterialButton btnMatInv = findViewById(R.id.btn_mat_inv);
        MaterialButton btnMatTrans = findViewById(R.id.btn_mat_trans);
        MaterialButton btnMatRank = findViewById(R.id.btn_mat_rank);
        MaterialButton btnMatEigen = findViewById(R.id.btn_mat_eigen);
        btnMatAdd.setOnClickListener(v -> onMatrixAdd());
        btnMatSub.setOnClickListener(v -> onMatrixSub());
        btnMatMul.setOnClickListener(v -> onMatrixMul());
        btnMatDet.setOnClickListener(v -> onMatrixDet());
        btnMatInv.setOnClickListener(v -> onMatrixInv());
        btnMatTrans.setOnClickListener(v -> onMatrixTranspose());
        btnMatRank.setOnClickListener(v -> onMatrixRank());
        btnMatEigen.setOnClickListener(v -> onMatrixEigen());

        // Number Theory Calculator
        EditText ntNInput = findViewById(R.id.nt_n_input);
        EditText ntAInput = findViewById(R.id.nt_a_input);
        EditText ntBInput = findViewById(R.id.nt_b_input);
        EditText ntModpowBaseInput = findViewById(R.id.nt_modpow_base_input);
        EditText ntModpowExpInput = findViewById(R.id.nt_modpow_exp_input);
        EditText ntModpowModInput = findViewById(R.id.nt_modpow_mod_input);
        MaterialButton btnNtFactorize = findViewById(R.id.btn_nt_factorize);
        MaterialButton btnNtIsPrime = findViewById(R.id.btn_nt_is_prime);
        MaterialButton btnNtGcd = findViewById(R.id.btn_nt_gcd);
        MaterialButton btnNtLcm = findViewById(R.id.btn_nt_lcm);
        MaterialButton btnNtFibonacci = findViewById(R.id.btn_nt_fibonacci);
        MaterialButton btnNtModPow = findViewById(R.id.btn_nt_mod_pow);
        MaterialButton btnNtTotient = findViewById(R.id.btn_nt_totient);
        btnNtFactorize.setOnClickListener(v -> onNtFactorize(ntNInput));
        btnNtIsPrime.setOnClickListener(v -> onNtIsPrime(ntNInput));
        btnNtGcd.setOnClickListener(v -> onNtGcd(ntAInput, ntBInput));
        btnNtLcm.setOnClickListener(v -> onNtLcm(ntAInput, ntBInput));
        btnNtFibonacci.setOnClickListener(v -> onNtFibonacci(ntNInput));
        btnNtModPow.setOnClickListener(v -> onNtModPow(ntModpowBaseInput, ntModpowExpInput, ntModpowModInput));
        btnNtTotient.setOnClickListener(v -> onNtTotient(ntNInput));

        // Bitwise Operations Calculator
        EditText bwAInput = findViewById(R.id.bw_a_input);
        EditText bwBInput = findViewById(R.id.bw_b_input);
        AutoCompleteTextView bwOpDropdown = findViewById(R.id.bw_op_dropdown);
        AutoCompleteTextView bwWidthDropdown = findViewById(R.id.bw_width_dropdown);
        MaterialButton btnBwCalc = findViewById(R.id.btn_bw_calc);
        MaterialButton btnBwClear = findViewById(R.id.btn_bw_clear);
        TextView bwResBin = findViewById(R.id.bw_res_bin);
        TextView bwResHex = findViewById(R.id.bw_res_hex);
        TextView bwResOct = findViewById(R.id.bw_res_oct);
        TextView bwResDec = findViewById(R.id.bw_res_dec);

        String[] bwOps = {"AND", "OR", "XOR", "NOT", "<<", ">>"};
        bwOpDropdown.setAdapter(new ArrayAdapter<>(this, android.R.layout.simple_dropdown_item_1line, bwOps));
        bwOpDropdown.setText("AND", false);
        bwOpDropdown.setOnItemClickListener((parent, view, position, id) -> {
            String op = bwOps[position];
            bwBInput.setEnabled(!op.equals("NOT"));
        });

        String[] bwWidths = {"8", "16", "32"};
        bwWidthDropdown.setAdapter(new ArrayAdapter<>(this, android.R.layout.simple_dropdown_item_1line, bwWidths));
        bwWidthDropdown.setText("16", false);

        btnBwCalc.setOnClickListener(v -> onBitwiseCalc(bwAInput, bwBInput, bwOpDropdown, bwWidthDropdown, bwResBin, bwResHex, bwResOct, bwResDec));
        btnBwClear.setOnClickListener(v -> {
            bwAInput.setText("0");
            bwBInput.setText("0");
            bwResBin.setText("");
            bwResHex.setText("");
            bwResOct.setText("");
            bwResDec.setText("");
        });

        // Parametric plotting
        MaterialButton btnPlotParametric = findViewById(R.id.btn_plot_parametric);
        Chip chipCircle = findViewById(R.id.chip_circle);
        Chip chipLissajous = findViewById(R.id.chip_lissajous);

        btnPlotParametric.setOnClickListener(v -> onPlotParametric());
        chipCircle.setOnClickListener(v -> {
            xParamInput.setText("cos(t)");
            yParamInput.setText("sin(t)");
            tMinInput.setText("0");
            tMaxInput.setText("6.2832");
        });
        chipLissajous.setOnClickListener(v -> {
            xParamInput.setText("sin(3*t)");
            yParamInput.setText("cos(2*t)");
            tMinInput.setText("0");
            tMaxInput.setText("6.2832");
        });

        // Polar plotting
        MaterialButton btnPlotPolar = findViewById(R.id.btn_plot_polar);
        Chip chipCardioid = findViewById(R.id.chip_cardioid);
        Chip chipClover = findViewById(R.id.chip_clover);

        btnPlotPolar.setOnClickListener(v -> onPlotPolar());
        chipCardioid.setOnClickListener(v -> {
            rPolarInput.setText("1+cos(theta)");
            thetaMinInput.setText("0");
            thetaMaxInput.setText("6.2832");
        });
        chipClover.setOnClickListener(v -> {
            rPolarInput.setText("sin(3*theta)");
            thetaMinInput.setText("0");
            thetaMaxInput.setText("6.2832");
        });

        // Implicit plotting
        EditText implicitExprInput = findViewById(R.id.implicit_expr_input);
        EditText implicitResInput = findViewById(R.id.implicit_resolution_input);
        MaterialButton btnPlotImplicit = findViewById(R.id.btn_plot_implicit);
        Chip chipImplicitCircle = findViewById(R.id.chip_implicit_circle);
        Chip chipImplicitHyperbola = findViewById(R.id.chip_implicit_hyperbola);

        btnPlotImplicit.setOnClickListener(v -> onPlotImplicit());
        chipImplicitCircle.setOnClickListener(v -> {
            implicitExprInput.setText("x^2+y^2-1");
        });
        chipImplicitHyperbola.setOnClickListener(v -> {
            implicitExprInput.setText("x^2-y^2-1");
        });

        // Preset chips — set expression text and auto-evaluate
        Chip chipSin = findViewById(R.id.chip_sin);
        Chip chipCos = findViewById(R.id.chip_cos);
        Chip chipX2  = findViewById(R.id.chip_x2);
        Chip chipExp = findViewById(R.id.chip_exp);
        Chip chip3D  = findViewById(R.id.chip_3d);

        chipSin.setOnClickListener(v -> { exprInput.setText("sin(x)"); onEvaluate(); });
        chipCos.setOnClickListener(v -> { exprInput.setText("cos(x)"); onEvaluate(); });
        chipX2 .setOnClickListener(v -> { exprInput.setText("x^2");     onEvaluate(); });
        chipExp.setOnClickListener(v -> { exprInput.setText("exp(-x)"); onEvaluate(); });
        chip3D .setOnClickListener(v -> { exprInput.setText("x^2+y^2"); });

        // Rounding & modulo chips
        Chip chipFloor = findViewById(R.id.chip_floor);
        Chip chipCeil  = findViewById(R.id.chip_ceil);
        Chip chipMod   = findViewById(R.id.chip_mod);

        chipFloor.setOnClickListener(v -> { exprInput.setText("floor(x)"); onEvaluate(); });
        chipCeil.setOnClickListener(v -> { exprInput.setText("ceil(x)"); onEvaluate(); });
        chipMod.setOnClickListener(v -> { exprInput.setText("x mod 3"); onEvaluate(); });

        // Unit Converter
        setupUnitConverter();

        // Base Converter
        setupBaseConverter();

        // Perpetual Calendar
        setupCalendar();

        // Statistical Distribution Calculator
        setupDistCalc();

        // Probability Calculator
        setupProbability();

        // Finance Calculator
        setupFinance();

        // Data Import & Scatter Plot
        setupDataImport();

        // Data Interpolation Calculator
        setupInterpolation();

        // Laplace Transform
        setupLaplace();

        // Custom Function Definition
        setupCustomFunctions();

        // Calculation History
        setupHistory();
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

    private void scrollToResult() {
        if (scrollView != null) {
            scrollView.post(() -> scrollView.scrollTo(0, resultView.getTop() - 100));
        }
    }

    private void appendResult(String label, double value) {
        String line = label + " = ";
        if (Double.isNaN(value)) {
            line += getString(R.string.result_error_prefix) + CalcEngine.getLastError();
        } else if (Double.isInfinite(value)) {
            line += (value > 0 ? getString(R.string.result_inf_pos) : getString(R.string.result_inf_neg));
        } else {
            line += String.format("%.10g", value);
        }
        resultView.append(line + "\n");
        scrollToResult();
    }

    private void appendResult(String label, int value) {
        String line = label + " = " + String.format(getString(R.string.result_points_plotted), value);
        resultView.append(line + "\n");
        scrollToResult();
    }

    private void onEvaluate() {
        String e = getExpr(); if (e.isEmpty()) { toast(getString(R.string.toast_enter_expr)); return; }
        double result = CalcEngine.evaluate(e, getX());
        appendResult(String.format(getString(R.string.result_fx), getX()), result);
        recordHistory(e + " @ x=" + fmt(getX()), result);
    }

    private void onDerivative() {
        String e = getExpr(); if (e.isEmpty()) { toast(getString(R.string.toast_enter_expr)); return; }
        double result = CalcEngine.derivative(e, getX(), 1e-6);
        appendResult(String.format(getString(R.string.result_f_prime_x), getX()), result);
        recordHistory("d/dx(" + e + ") @ x=" + fmt(getX()), result);
    }

    private void onDerivative2() {
        String e = getExpr(); if (e.isEmpty()) { toast(getString(R.string.toast_enter_expr)); return; }
        double result = CalcEngine.derivative2(e, getX(), 1e-6);
        appendResult(String.format(getString(R.string.result_f_double_prime_x), getX()), result);
        recordHistory("d²/dx²(" + e + ") @ x=" + fmt(getX()), result);
    }

    private void onIntegrate() {
        String e = getExpr(); if (e.isEmpty()) { toast(getString(R.string.toast_enter_expr)); return; }
        double result = CalcEngine.integrate(e, getA(), getB());
        appendResult(String.format(getString(R.string.result_integral), getA(), getB()), result);
        recordHistory("∫(" + e + ") [" + fmt(getA()) + "," + fmt(getB()) + "]", result);
    }

    private void onSolve() {
        String e = getExpr(); if (e.isEmpty()) { toast(getString(R.string.toast_enter_expr)); return; }
        double root = CalcEngine.solve(e, getGuess(), getA(), getB());
        if (Double.isNaN(root)) {
            appendResult(getString(R.string.label_root), Double.NaN);
        } else {
            resultView.append(String.format(getString(R.string.result_root), root) + "\n");
            resultView.append(String.format(getString(R.string.result_root_fval), CalcEngine.evaluate(e, root)) + "\n");
            scrollToResult();
        }
        recordHistory("solve(" + e + ")=0", root);
    }

    private void onFindExtremum(boolean minimum) {
        String e = getExpr(); if (e.isEmpty()) { toast(getString(R.string.toast_enter_expr)); return; }
        double a = getA();
        double b = getB();
        double result;
        if (minimum) {
            result = CalcEngine.findMinimum(e, a, b);
        } else {
            result = CalcEngine.findMaximum(e, a, b);
        }
        if (Double.isNaN(result)) {
            appendResult(minimum ? getString(R.string.label_min) : getString(R.string.label_max), Double.NaN);
        } else {
            resultView.append(String.format(getString(minimum ? R.string.result_min : R.string.result_max), result, CalcEngine.evaluate(e, result)) + "\n");
        }
        recordHistory((minimum ? "min" : "max") + "(" + e + ") [" + fmt(a) + "," + fmt(b) + "]", result);
    }

    private void openPlot() {
        Intent intent = new Intent(this, PlotActivity.class);
        String expr = getExpr();
        if (!expr.isEmpty()) {
            intent.putExtra("initial_expr", expr);
            intent.putExtra("x_min", getA());
            intent.putExtra("x_max", getB());
        }
        startActivity(intent);
    }

    private void onScanRoots() {
        String e = getExpr();
        if (e.isEmpty()) { toast(getString(R.string.toast_enter_expr)); return; }
        double a = getA();
        double b = getB();
        if (a >= b) { toast(getString(R.string.toast_a_less_b)); return; }

        int nSamples = 2000;
        double tolZero = 1e-6;
        double tolDup = 1e-4;
        double[] xs = new double[nSamples];
        double step = (b - a) / (nSamples - 1);
        for (int i = 0; i < nSamples; i++) {
            xs[i] = a + i * step;
        }
        double[] ys = CalcEngine.evaluateArray(e, xs);
        if (ys == null) {
            resultView.append(String.format(getString(R.string.scan_roots_error), CalcEngine.getLastError()) + "\n");
            return;
        }

        java.util.ArrayList<Double> roots = new java.util.ArrayList<>();
        for (int i = 0; i < nSamples; i++) {
            if (!Double.isNaN(ys[i]) && !Double.isInfinite(ys[i]) && Math.abs(ys[i]) < tolZero) {
                roots.add(xs[i]);
            }
        }
        for (int i = 0; i < nSamples - 1; i++) {
            if (Double.isNaN(ys[i]) || Double.isNaN(ys[i + 1])) continue;
            if (ys[i] == 0.0 || ys[i + 1] == 0.0) continue;
            if (ys[i] * ys[i + 1] < 0) {
                double root = CalcEngine.solveBisection(e, xs[i], xs[i + 1]);
                if (!Double.isNaN(root)) {
                    roots.add(root);
                }
            }
        }

        java.util.Collections.sort(roots);
        java.util.ArrayList<Double> uniqueRoots = new java.util.ArrayList<>();
        for (Double r : roots) {
            if (uniqueRoots.isEmpty() || Math.abs(r - uniqueRoots.get(uniqueRoots.size() - 1)) > tolDup) {
                uniqueRoots.add(r);
            }
        }

        if (uniqueRoots.isEmpty()) {
            resultView.append(String.format(getString(R.string.scan_roots_no_roots), a, b) + "\n");
        } else {
            resultView.append(String.format(getString(R.string.scan_roots_found), uniqueRoots.size(), a, b) + "\n");
            int limit = Math.min(uniqueRoots.size(), 20);
            for (int i = 0; i < limit; i++) {
                double r = uniqueRoots.get(i);
                double verify = CalcEngine.evaluate(e, r);
                String vStr = Double.isNaN(verify) ? "N/A" : String.format("%.2e", verify);
                resultView.append("  x" + (i + 1) + " = " + fmt(r) + "  (f=" + vStr + ")\n");
            }
            if (uniqueRoots.size() > 20) {
                resultView.append(String.format(getString(R.string.result_and_more), (uniqueRoots.size() - 20)) + "\n");
            }
        }
    }

    private void openPlot3D() {
        Intent intent = new Intent(this, Plot3DActivity.class);
        String expr = getExpr();
        if (!expr.isEmpty()) {
            intent.putExtra("initial_expr", expr);
        }
        startActivity(intent);
    }

    private void onTangentNormal(boolean tangent) {
        String e = getExpr();
        if (e.isEmpty()) { toast(getString(R.string.toast_enter_expr)); return; }
        double x0 = getX();
        double y0 = CalcEngine.evaluate(e, x0);
        double slope = CalcEngine.derivative(e, x0, 1e-6);
        if (Double.isNaN(y0) || Double.isNaN(slope)) {
            resultView.append(String.format(getString(tangent ? R.string.tangent_error : R.string.normal_error), CalcEngine.getLastError()) + "\n");
            return;
        }
        if (tangent) {
            resultView.append(String.format(getString(R.string.tangent_label), x0, slope, x0, y0) + "\n");
        } else {
            if (Math.abs(slope) < 1e-12) {
                resultView.append(String.format(getString(R.string.result_normal_vert), x0) + "\n");
            } else {
                double ns = -1.0 / slope;
                resultView.append(String.format(getString(R.string.normal_label), x0, ns, x0, y0) + "\n");
            }
        }
    }

    private void onArcLength() {
        String e = getExpr();
        if (e.isEmpty()) { toast(getString(R.string.toast_enter_expr)); return; }
        double a = getA();
        double b = getB();
        if (a >= b) { toast(getString(R.string.toast_a_less_b)); return; }

        int n = 5000;
        double h = (b - a) / n;
        double[] xs = new double[n + 1];
        for (int i = 0; i <= n; i++) {
            xs[i] = a + i * h;
        }
        double[] ys = CalcEngine.evaluateArray(e, xs);
        if (ys == null) {
            resultView.append(String.format(getString(R.string.arc_length_error), CalcEngine.getLastError()) + "\n");
            return;
        }
        double length = 0.0;
        for (int i = 0; i < n; i++) {
            double y1 = ys[i];
            double y2 = ys[i + 1];
            if (Double.isNaN(y1) || Double.isNaN(y2)) {
                continue;
            }
            double dx = h;
            double dy = y2 - y1;
            length += Math.sqrt(dx * dx + dy * dy);
        }
        resultView.append(String.format(getString(R.string.arc_length_result), a, b, length) + "\n");
    }

    private void onAreaBetweenCurves() {
        String eF = getExpr();
        String eG = areaGInput.getText().toString().trim();
        if (eF.isEmpty()) { toast(getString(R.string.toast_enter_fx)); return; }
        if (eG.isEmpty()) { toast(getString(R.string.toast_enter_gx)); return; }
        double a = getA();
        double b = getB();
        if (a >= b) { toast(getString(R.string.toast_a_less_b)); return; }

        double result = CalcEngine.areaBetweenCurves(eF, eG, a, b);
        if (Double.isNaN(result)) {
            String err = CalcEngine.getLastError();
            resultView.append(String.format(getString(R.string.area_between_error), (err.isEmpty() ? getString(R.string.result_computation_failed) : err)) + "\n");
            return;
        }
        resultView.append(String.format(getString(R.string.area_between_result), a, b, a, b, result) + "\n");
    }

    private void onVolumeCompute() {
        String eF = getExpr();
        if (eF.isEmpty()) { toast(getString(R.string.toast_enter_fx)); return; }
        double a = getA();
        double b = getB();
        if (a >= b) { toast(getString(R.string.toast_a_less_b)); return; }

        double result;
        if ("disk".equals(volMode)) {
            result = CalcEngine.volumeDisk(eF, a, b);
        } else if ("washer".equals(volMode)) {
            String eG = volGInput.getText().toString().trim();
            if (eG.isEmpty()) { toast(getString(R.string.toast_enter_gx)); return; }
            result = CalcEngine.volumeWasher(eF, eG, a, b);
        } else {
            result = CalcEngine.volumeShell(eF, a, b);
        }
        if (Double.isNaN(result)) {
            String err = CalcEngine.getLastError();
            resultView.append(String.format(getString(R.string.volume_error), (err.isEmpty() ? getString(R.string.result_computation_failed) : err)) + "\n");
            return;
        }
        String methodName;
        String formula;
        if ("disk".equals(volMode)) {
            methodName = getString(R.string.vol_disk);
            formula = "V = π∫[a,b] [f(x)]² dx";
        } else if ("washer".equals(volMode)) {
            methodName = getString(R.string.vol_washer);
            formula = "V = π∫[a,b] ([f(x)]²-[g(x)]²) dx";
        } else {
            methodName = getString(R.string.vol_shell);
            formula = "V = 2π∫[a,b] x·f(x) dx";
        }
        resultView.append(String.format(getString(R.string.volume_result), methodName, formula, a, b, result) + "\n");
    }

    @SuppressWarnings("unchecked")
    private void onSolveSystem2d() {
        String fExpr = sysFInput.getText().toString().trim();
        String gExpr = sysGInput.getText().toString().trim();
        if (fExpr.isEmpty() || gExpr.isEmpty()) {
            toast(getString(R.string.toast_enter_fg));
            return;
        }
        double x0, y0;
        try {
            x0 = Double.parseDouble(sysX0Input.getText().toString().trim());
            y0 = Double.parseDouble(sysY0Input.getText().toString().trim());
        } catch (NumberFormatException ex) {
            toast(getString(R.string.toast_invalid_guess));
            return;
        }

        HashMap<String, Object> result = CalcEngine.solveSystem2d(fExpr, gExpr, x0, y0);
        if (result == null) {
            String err = CalcEngine.getLastError();
            resultView.append(String.format(getString(R.string.system_solver_error), (err.isEmpty() ? getString(R.string.result_computation_failed) : err)) + "\n");
            return;
        }

        Object xObj = result.get("x");
        Object yObj = result.get("y");
        if (xObj == null || yObj == null) {
            resultView.append(getString(R.string.system_solver_invalid) + "\n");
            return;
        }

        double xSol = (double) xObj;
        double ySol = (double) yObj;
        double fVal = CalcEngine.evaluateXY(fExpr, xSol, ySol);
        double gVal = CalcEngine.evaluateXY(gExpr, xSol, ySol);

        StringBuilder sb = new StringBuilder();
        sb.append(String.format(getString(R.string.system_func_f), fExpr)).append("\n");
        sb.append(String.format(getString(R.string.system_func_g), gExpr)).append("\n\n");
        sb.append(getString(R.string.system_solution_label));
        sb.append(String.format(getString(R.string.system_sol_x), fmt(xSol))).append("\n");
        sb.append(String.format(getString(R.string.system_sol_y), fmt(ySol))).append("\n\n");
        sb.append(getString(R.string.system_residuals_label));
        sb.append(String.format(getString(R.string.system_resid_f), Double.isNaN(fVal) ? "N/A" : String.format("%.2e", fVal))).append("\n");
        sb.append(String.format(getString(R.string.system_resid_g), Double.isNaN(gVal) ? "N/A" : String.format("%.2e", gVal))).append("\n");

        android.widget.TextView tv = new android.widget.TextView(this);
        tv.setText(sb.toString());
        tv.setTypeface(android.graphics.Typeface.MONOSPACE);
        tv.setTextSize(13);
        tv.setPadding(40, 24, 40, 24);
        tv.setTextColor(android.graphics.Color.parseColor("#cdd6f4"));
        tv.setBackgroundColor(android.graphics.Color.parseColor("#181825"));

        android.widget.ScrollView sv = new android.widget.ScrollView(this);
        sv.addView(tv);

        new androidx.appcompat.app.AlertDialog.Builder(this, androidx.appcompat.R.style.ThemeOverlay_AppCompat_Dialog_Alert)
            .setTitle(getString(R.string.dialog_system_solution))
            .setView(sv)
            .setPositiveButton(getString(R.string.dialog_close), null)
            .show();

        resultView.append(String.format(getString(R.string.system_solved_toast), xSol, ySol) + "\n");
    }

    private void onFFT() {
        String e = getExpr();
        if (e.isEmpty()) { toast(getString(R.string.toast_enter_expr)); return; }
        double a = getA();
        double b = getB();
        if (a >= b) { toast(getString(R.string.toast_a_less_b)); return; }
        int n = 256; // default samples for DFT
        double step = (b - a) / n;
        double[] xs = new double[n];
        double[] ys = new double[n];
        for (int i = 0; i < n; i++) {
            xs[i] = a + i * step;
            double val = CalcEngine.evaluate(e, xs[i]);
            ys[i] = Double.isNaN(val) ? 0.0 : val;
        }
        // Remove DC offset
        double mean = 0.0;
        for (double v : ys) mean += v;
        mean /= n;
        for (int i = 0; i < n; i++) ys[i] -= mean;

        int m = n / 2 + 1;
        double[] amps = new double[m];
        double[] phases = new double[m];
        double[] freqs = new double[m];
        double df = 1.0 / (b - a); // frequency resolution
        for (int k = 0; k < m; k++) {
            double real = 0.0, imag = 0.0;
            for (int i = 0; i < n; i++) {
                double angle = -2.0 * Math.PI * k * i / n;
                real += ys[i] * Math.cos(angle);
                imag += ys[i] * Math.sin(angle);
            }
            double amp = (2.0 / n) * Math.sqrt(real * real + imag * imag);
            if (k == 0) amp /= 2.0;
            amps[k] = amp;
            phases[k] = Math.atan2(imag, real);
            freqs[k] = k * df;
        }

        // Find dominant frequency
        int peakIdx = 1;
        for (int i = 2; i < m; i++) {
            if (amps[i] > amps[peakIdx]) peakIdx = i;
        }

        StringBuilder sb = new StringBuilder();
        sb.append(String.format(getString(R.string.fft_spectrum_header), n)).append("\n");
        sb.append(String.format(getString(R.string.fft_dominant_freq), freqs[peakIdx]))
          .append(getString(R.string.fft_amplitude)).append(fmt(amps[peakIdx])).append("\n\n");
        int show = Math.min(m, 16);
        sb.append(getString(R.string.fft_header)).append("\n");
        sb.append("--------------------------------\n");
        for (int i = 0; i < show; i++) {
            sb.append(fmt(freqs[i])).append("\t")
              .append(fmt(amps[i])).append("\t")
              .append(fmt(phases[i])).append("\n");
        }
        if (m > show) sb.append(String.format(getString(R.string.fft_more_bins), m - show)).append("\n");

        android.widget.TextView tv = new android.widget.TextView(this);
        tv.setText(sb.toString());
        tv.setTypeface(android.graphics.Typeface.MONOSPACE);
        tv.setTextSize(13);
        tv.setPadding(40, 24, 40, 24);
        tv.setTextColor(android.graphics.Color.parseColor("#cdd6f4"));
        tv.setBackgroundColor(android.graphics.Color.parseColor("#181825"));

        android.widget.ScrollView sv = new android.widget.ScrollView(this);
        sv.addView(tv);

        new androidx.appcompat.app.AlertDialog.Builder(this, androidx.appcompat.R.style.ThemeOverlay_AppCompat_Dialog_Alert)
            .setTitle(getString(R.string.dialog_fft_spectrum))
            .setView(sv)
            .setPositiveButton(getString(R.string.dialog_close), null)
            .show();

        resultView.append(String.format(getString(R.string.fft_dominant_freq), freqs[peakIdx]) + " A=" + fmt(amps[peakIdx]) + "\n");
    }

    private void onLimit() {
        String e = getExpr();
        if (e.isEmpty()) { toast(getString(R.string.toast_enter_expr)); return; }
        double a = getX();

        double left  = CalcEngine.limitLeft(e, a);
        double right = CalcEngine.limitRight(e, a);

        if (Double.isNaN(left) && Double.isNaN(right)) {
            resultView.append(String.format(getString(R.string.limit_error), a, CalcEngine.getLastError()) + "\n");
            return;
        }

        if (!Double.isNaN(left) && !Double.isNaN(right) && Math.abs(left - right) < 1e-8) {
            double val = (left + right) / 2.0;
            resultView.append(String.format(getString(R.string.limit_result), a, val) + "\n");
            resultView.append(String.format(getString(R.string.limit_left), left) + "\n");
            resultView.append(String.format(getString(R.string.limit_right), right) + "\n");
        } else {
            if (!Double.isNaN(left) && !Double.isNaN(right)) {
                resultView.append(String.format(getString(R.string.limit_two_sided_not_exist), left, right) + "\n");
            } else {
                if (!Double.isNaN(left)) {
                    resultView.append(String.format(getString(R.string.limit_left_result), a, left) + "\n");
                } else {
                    resultView.append(String.format(getString(R.string.limit_left_dne), a) + "\n");
                }
                if (!Double.isNaN(right)) {
                    resultView.append(String.format(getString(R.string.limit_right_result), a, right) + "\n");
                } else {
                    resultView.append(String.format(getString(R.string.limit_right_dne), a) + "\n");
                }
                resultView.append(String.format(getString(R.string.limit_two_sided_not_exist), Double.isNaN(left) ? 0.0 : left, Double.isNaN(right) ? 0.0 : right) + "\n");
            }
        }
    }

    private void onLimitSide(boolean left) {
        String e = getExpr();
        if (e.isEmpty()) { toast(getString(R.string.toast_enter_expr)); return; }
        double a = getX();
        double result;
        String label;
        if (left) {
            result = CalcEngine.limitLeft(e, a);
            label = String.format(getString(R.string.limit_left_label), a);
        } else {
            result = CalcEngine.limitRight(e, a);
            label = String.format(getString(R.string.limit_right_label), a);
        }
        if (Double.isNaN(result)) {
            resultView.append(String.format(getString(R.string.limit_side_error), label, CalcEngine.getLastError()) + "\n");
        } else {
            resultView.append(label + " = " + fmt(result) + "\n");
        }
    }

    private int getTaylorOrder() {
        try {
            int order = Integer.parseInt(taylorOrderInput.getText().toString().trim());
            if (order < 1) return 5;
            if (order > 20) return 20;
            return order;
        } catch (NumberFormatException e) {
            return 5;
        }
    }

    private void onTaylor() {
        String e = getExpr();
        if (e.isEmpty()) { toast(getString(R.string.toast_enter_expr)); return; }
        double a = getX();
        int order = getTaylorOrder();

        double[] coeffs = CalcEngine.taylorCoefficients(e, a, order);
        if (coeffs == null) {
            resultView.append(String.format(getString(R.string.taylor_error), CalcEngine.getLastError()) + "\n");
            return;
        }

        StringBuilder polySb = new StringBuilder();
        // Build human-readable Taylor polynomial
        for (int k = 0; k < coeffs.length; k++) {
            if (Double.isNaN(coeffs[k])) continue;
            double c = coeffs[k];
            if (Math.abs(c) < 1e-15) continue;

            String cStr = fmt(c);
            if (k == 0) {
                polySb.append(cStr);
            } else if (k == 1) {
                polySb.append(" + ").append(cStr).append("*(x-").append(fmt(a)).append(")");
            } else {
                polySb.append(" + ").append(cStr).append("*(x-").append(fmt(a)).append(")^").append(k);
            }
        }
        StringBuilder sb = new StringBuilder();
        sb.append(String.format(getString(R.string.taylor_result), a, order, polySb.toString()));
        sb.append("\n\n");
        sb.append(getString(R.string.taylor_coefficients_header));
        for (int k = 0; k < coeffs.length; k++) {
            sb.append("c").append(k).append(" = ").append(fmt(coeffs[k])).append("\n");
        }

        // Show in dialog
        android.widget.TextView tv = new android.widget.TextView(this);
        tv.setText(sb.toString());
        tv.setTypeface(android.graphics.Typeface.MONOSPACE);
        tv.setTextSize(13);
        tv.setPadding(40, 24, 40, 24);
        tv.setTextColor(android.graphics.Color.parseColor("#cdd6f4"));
        tv.setBackgroundColor(android.graphics.Color.parseColor("#181825"));

        android.widget.ScrollView sv = new android.widget.ScrollView(this);
        sv.addView(tv);

        new androidx.appcompat.app.AlertDialog.Builder(this, androidx.appcompat.R.style.ThemeOverlay_AppCompat_Dialog_Alert)
            .setTitle(getString(R.string.dialog_taylor_series))
            .setView(sv)
            .setPositiveButton(getString(R.string.dialog_close), null)
            .show();

        resultView.append(String.format(getString(R.string.taylor_toast), a, order) + "\n");
    }

    private void onOdeSolve() {
        String expr = odeExprInput.getText().toString().trim();
        if (expr.isEmpty()) { toast(getString(R.string.toast_enter_ode)); return; }
        double x0, y0, xEnd;
        int steps;
        try {
            x0 = Double.parseDouble(odeX0Input.getText().toString().trim());
            y0 = Double.parseDouble(odeY0Input.getText().toString().trim());
            xEnd = Double.parseDouble(odeXEndInput.getText().toString().trim());
            steps = Integer.parseInt(odeStepsInput.getText().toString().trim());
        } catch (NumberFormatException ex) {
            toast(getString(R.string.toast_invalid_ode));
            return;
        }
        if (steps < 1 || steps > 100000) { toast(getString(R.string.toast_steps_range)); return; }
        if (x0 == xEnd) { toast(getString(R.string.toast_x0_xend)); return; }

        HashMap<String, Object> result = CalcEngine.odeSolveRk4(expr, x0, y0, xEnd, steps);
        if (result == null) {
            resultView.append(String.format(getString(R.string.ode_error), CalcEngine.getLastError()) + "\n");
            return;
        }

        Object xsObj = result.get("xs");
        Object ysObj = result.get("ys");
        Object countObj = result.get("count");
        if (xsObj == null || ysObj == null || countObj == null) {
            resultView.append(getString(R.string.ode_error_invalid) + "\n");
            return;
        }
        
        double[] xs = (double[]) xsObj;
        double[] ys = (double[]) ysObj;
        int count = (int) countObj;

        StringBuilder sb = new StringBuilder();
        sb.append(String.format(getString(R.string.ode_header), expr, x0, y0)).append("\n");
        sb.append(String.format(getString(R.string.ode_solved), x0, xEnd, steps)).append("\n\n");
        sb.append(String.format("%14s  %14s\n", getString(R.string.ode_col_x), getString(R.string.ode_col_y)));
        sb.append("--------------------------------\n");
        int show = Math.min(count, 30);
        int step = count > show ? count / show : 1;
        for (int i = 0; i < count; i += step) {
            String yStr = Double.isNaN(ys[i]) ? "N/A" : fmt(ys[i]);
            sb.append(String.format("%14s  %14s\n", fmt(xs[i]), yStr));
        }
        if (count > show) sb.append(String.format(getString(R.string.ode_truncated), count)).append("\n");

        android.widget.TextView tv = new android.widget.TextView(this);
        tv.setText(sb.toString());
        tv.setTypeface(android.graphics.Typeface.MONOSPACE);
        tv.setTextSize(13);
        tv.setPadding(40, 24, 40, 24);
        tv.setTextColor(android.graphics.Color.parseColor("#cdd6f4"));
        tv.setBackgroundColor(android.graphics.Color.parseColor("#181825"));

        android.widget.ScrollView sv = new android.widget.ScrollView(this);
        sv.addView(tv);

        new androidx.appcompat.app.AlertDialog.Builder(this, androidx.appcompat.R.style.ThemeOverlay_AppCompat_Dialog_Alert)
            .setTitle(getString(R.string.dialog_ode_solution))
            .setView(sv)
            .setPositiveButton(getString(R.string.dialog_close), null)
            .show();

        resultView.append(String.format(getString(R.string.ode_toast), count) + "\n");
    }

    private void onOdePlot() {
        String expr = odeExprInput.getText().toString().trim();
        if (expr.isEmpty()) { toast(getString(R.string.toast_enter_ode)); return; }
        double x0, y0, xEnd;
        int steps;
        try {
            x0 = Double.parseDouble(odeX0Input.getText().toString().trim());
            y0 = Double.parseDouble(odeY0Input.getText().toString().trim());
            xEnd = Double.parseDouble(odeXEndInput.getText().toString().trim());
            steps = Integer.parseInt(odeStepsInput.getText().toString().trim());
        } catch (NumberFormatException ex) {
            toast(getString(R.string.toast_invalid_ode));
            return;
        }
        if (steps < 1 || steps > 100000) { toast(getString(R.string.toast_steps_range)); return; }
        if (x0 == xEnd) { toast(getString(R.string.toast_x0_xend)); return; }

        HashMap<String, Object> result = CalcEngine.odeSolveRk4(expr, x0, y0, xEnd, steps);
        if (result == null) {
            resultView.append(String.format(getString(R.string.ode_error), CalcEngine.getLastError()) + "\n");
            return;
        }

        Object xsObj = result.get("xs");
        Object ysObj = result.get("ys");
        if (xsObj == null || ysObj == null) {
            resultView.append(getString(R.string.ode_error_invalid) + "\n");
            return;
        }

        double[] xsFull = (double[]) xsObj;
        double[] ysFull = (double[]) ysObj;

        // Downsample to avoid TransactionTooLargeException (~1MB Intent limit)
        int maxPoints = 2000;
        double[] xs, ys;
        if (xsFull.length > maxPoints) {
            int step = Math.max(1, xsFull.length / maxPoints);
            int arraySize = (xsFull.length + step - 1) / step + 1;
            xs = new double[arraySize];
            ys = new double[arraySize];
            int idx = 0;
            for (int i = 0; i < xsFull.length && idx < xs.length; i += step) {
                xs[idx] = xsFull[i];
                ys[idx] = ysFull[i];
                idx++;
            }
            // Always include the last point
            if ((xsFull.length - 1) % step != 0 && idx < xs.length) {
                xs[idx] = xsFull[xsFull.length - 1];
                ys[idx] = ysFull[ysFull.length - 1];
                idx++;
            }
            xs = java.util.Arrays.copyOf(xs, idx);
            ys = java.util.Arrays.copyOf(ys, idx);
        } else {
            xs = xsFull;
            ys = ysFull;
        }

        Intent intent = new Intent(this, PlotActivity.class);
        intent.putExtra("is_ode", true);
        intent.putExtra("ode_xs", xs);
        intent.putExtra("ode_ys", ys);
        intent.putExtra("ode_expr", expr);
        intent.putExtra("x_min", x0);
        intent.putExtra("x_max", xEnd);
        startActivity(intent);
    }

    @SuppressWarnings("unchecked")
    private void onOdeCompare() {
        String expr = odeCompareExprInput.getText().toString().trim();
        if (expr.isEmpty()) { toast(getString(R.string.toast_enter_ode)); return; }
        double x0, y0, xEnd;
        int steps;
        try {
            x0 = Double.parseDouble(odeCompareX0Input.getText().toString().trim());
            y0 = Double.parseDouble(odeCompareY0Input.getText().toString().trim());
            xEnd = Double.parseDouble(odeCompareXEndInput.getText().toString().trim());
            steps = Integer.parseInt(odeCompareStepsInput.getText().toString().trim());
        } catch (NumberFormatException ex) {
            toast(getString(R.string.toast_invalid_ode));
            return;
        }
        if (steps < 1 || steps > 100000) { toast(getString(R.string.toast_steps_range)); return; }
        if (x0 == xEnd) { toast(getString(R.string.toast_x0_xend)); return; }

        // Solve with all methods
        HashMap<String, Object> euler = CalcEngine.odeSolveEuler(expr, x0, y0, xEnd, steps);
        HashMap<String, Object> improvedEuler = CalcEngine.odeSolveImprovedEuler(expr, x0, y0, xEnd, steps);
        HashMap<String, Object> midpoint = CalcEngine.odeSolveMidpoint(expr, x0, y0, xEnd, steps);
        HashMap<String, Object> rk4 = CalcEngine.odeSolveRk4(expr, x0, y0, xEnd, steps);

        StringBuilder sb = new StringBuilder();
        sb.append(String.format(getString(R.string.ode_compare_header), expr, fmt(x0), fmt(y0), fmt(x0), fmt(xEnd), steps)).append("\n\n");

        String[] names = {
            getString(R.string.ode_compare_euler),
            getString(R.string.ode_compare_improved_euler),
            getString(R.string.ode_compare_midpoint),
            getString(R.string.ode_compare_rk4)
        };
        HashMap<String, Object>[] results = new HashMap[]{euler, improvedEuler, midpoint, rk4};

        for (int i = 0; i < names.length; i++) {
            HashMap<String, Object> result = results[i];
            if (result != null) {
                double[] ys = (double[]) result.get("ys");
                if (ys != null && ys.length > 0) {
                    double finalY = ys[ys.length - 1];
                    sb.append(String.format(getString(R.string.ode_compare_result), names[i], fmt(xEnd), fmt(finalY))).append("\n");
                }
            }
        }

        android.widget.TextView tv = new android.widget.TextView(this);
        tv.setText(sb.toString());
        tv.setTypeface(android.graphics.Typeface.MONOSPACE);
        tv.setTextSize(13);
        tv.setPadding(40, 24, 40, 24);
        tv.setTextColor(android.graphics.Color.parseColor("#cdd6f4"));
        tv.setBackgroundColor(android.graphics.Color.parseColor("#181825"));

        android.widget.ScrollView sv = new android.widget.ScrollView(this);
        sv.addView(tv);

        new androidx.appcompat.app.AlertDialog.Builder(this, androidx.appcompat.R.style.ThemeOverlay_AppCompat_Dialog_Alert)
            .setTitle(getString(R.string.ode_compare))
            .setView(sv)
            .setPositiveButton(getString(R.string.dialog_close), null)
            .show();

        resultView.append(String.format(getString(R.string.ode_compare_toast), 4, steps) + "\n");
    }

    @SuppressWarnings("unchecked")
    private void onOdeComparePlot() {
        String expr = odeCompareExprInput.getText().toString().trim();
        if (expr.isEmpty()) { toast(getString(R.string.toast_enter_ode)); return; }
        double x0, y0, xEnd;
        int steps;
        try {
            x0 = Double.parseDouble(odeCompareX0Input.getText().toString().trim());
            y0 = Double.parseDouble(odeCompareY0Input.getText().toString().trim());
            xEnd = Double.parseDouble(odeCompareXEndInput.getText().toString().trim());
            steps = Integer.parseInt(odeCompareStepsInput.getText().toString().trim());
        } catch (NumberFormatException ex) {
            toast(getString(R.string.toast_invalid_ode));
            return;
        }
        if (steps < 1 || steps > 100000) { toast(getString(R.string.toast_steps_range)); return; }
        if (x0 == xEnd) { toast(getString(R.string.toast_x0_xend)); return; }

        // Solve with all methods
        HashMap<String, Object> euler = CalcEngine.odeSolveEuler(expr, x0, y0, xEnd, steps);
        HashMap<String, Object> improvedEuler = CalcEngine.odeSolveImprovedEuler(expr, x0, y0, xEnd, steps);
        HashMap<String, Object> midpoint = CalcEngine.odeSolveMidpoint(expr, x0, y0, xEnd, steps);
        HashMap<String, Object> rk4 = CalcEngine.odeSolveRk4(expr, x0, y0, xEnd, steps);

        // Combine all data for plotting
        ArrayList<double[]> allXs = new ArrayList<>();
        ArrayList<double[]> allYs = new ArrayList<>();
        ArrayList<String> labels = new ArrayList<>();

        String[] names = {
            "Euler",
            "Improved Euler",
            "Midpoint",
            "RK4"
        };
        HashMap<String, Object>[] results = new HashMap[]{euler, improvedEuler, midpoint, rk4};

        for (int i = 0; i < names.length; i++) {
            HashMap<String, Object> result = results[i];
            if (result != null) {
                double[] xs = (double[]) result.get("xs");
                double[] ys = (double[]) result.get("ys");
                if (xs != null && ys != null && xs.length > 0) {
                    allXs.add(xs);
                    allYs.add(ys);
                    labels.add(names[i]);
                }
            }
        }

        if (allXs.isEmpty()) {
            resultView.append("No results to plot\n");
            return;
        }

        Intent intent = new Intent(this, PlotActivity.class);
        intent.putExtra("is_ode", true);
        intent.putExtra("ode_multi", true);
        intent.putExtra("ode_multi_xs", allXs);
        intent.putExtra("ode_multi_ys", allYs);
        intent.putExtra("ode_multi_labels", labels);
        intent.putExtra("ode_expr", expr);
        intent.putExtra("x_min", x0);
        intent.putExtra("x_max", xEnd);
        startActivity(intent);
    }

    @SuppressWarnings("unchecked")
    private void onDirectionField(boolean solveIC) {
        String expr = dfExprInput.getText().toString().trim();
        if (expr.isEmpty()) { toast(getString(R.string.toast_enter_df_expr)); return; }

        int grid;
        double xmin, xmax, ymin, ymax;
        try {
            grid = Integer.parseInt(dfGridInput.getText().toString().trim());
            xmin = Double.parseDouble(dfXminInput.getText().toString().trim());
            xmax = Double.parseDouble(dfXmaxInput.getText().toString().trim());
            ymin = Double.parseDouble(dfYminInput.getText().toString().trim());
            ymax = Double.parseDouble(dfYmaxInput.getText().toString().trim());
        } catch (NumberFormatException ex) {
            toast(getString(R.string.toast_invalid_ode));
            return;
        }
        if (grid < 3) grid = 3;
        if (grid > 40) grid = 40;
        if (xmin >= xmax || ymin >= ymax) {
            toast(getString(R.string.toast_min_max));
            return;
        }

        int n = grid * grid;
        double[] xs = new double[n];
        double[] ys = new double[n];
        int idx = 0;
        double dx = (xmax - xmin) / (grid - 1);
        double dy = (ymax - ymin) / (grid - 1);
        for (int j = 0; j < grid; j++) {
            for (int i = 0; i < grid; i++) {
                xs[idx] = xmin + i * dx;
                ys[idx] = ymin + j * dy;
                idx++;
            }
        }

        double[] slopes = CalcEngine.evaluateXYArray(expr, xs, ys);
        if (slopes == null) {
            resultView.append(String.format(getString(R.string.ode_error), CalcEngine.getLastError()) + "\n");
            return;
        }

        // Parse initial conditions: "x0,y0; x1,y1; ..."
        java.util.List<double[]> icList = new java.util.ArrayList<>();
        if (solveIC) {
            String icStr = dfIcInput.getText().toString().trim();
            if (!icStr.isEmpty()) {
                String[] pairs = icStr.split(";");
                for (String pair : pairs) {
                    pair = pair.trim();
                    if (pair.isEmpty()) continue;
                    String[] parts = pair.split(",");
                    if (parts.length == 2) {
                        try {
                            double icx = Double.parseDouble(parts[0].trim());
                            double icy = Double.parseDouble(parts[1].trim());
                            icList.add(new double[]{icx, icy});
                        } catch (NumberFormatException e) {
                            toast(String.format(getString(R.string.toast_invalid_ic), pair));
                            return;
                        }
                    }
                }
            }
        }

        // Solve ODE for each IC using RK4
        java.util.List<double[]> solutionCurves = new java.util.ArrayList<>();
        for (double[] ic : icList) {
            double icx = ic[0], icy = ic[1];
            int odeSteps = 500;
            HashMap<String, Object> result = CalcEngine.odeSolveRk4(expr, icx, icy, xmax, odeSteps);
            if (result != null) {
                Object xsObj = result.get("xs");
                Object ysObj = result.get("ys");
                if (xsObj != null && ysObj != null) {
                    double[] oxs = (double[]) xsObj;
                    double[] oys = (double[]) ysObj;
                    // Also solve backward from xmin
                    HashMap<String, Object> resultBack = CalcEngine.odeSolveRk4(expr, icx, icy, xmin, odeSteps);
                    double[] bxs = null, bys = null;
                    if (resultBack != null) {
                        Object bxsObj = resultBack.get("xs");
                        Object bysObj = resultBack.get("ys");
                        if (bxsObj != null && bysObj != null) {
                            bxs = (double[]) bxsObj;
                            bys = (double[]) bysObj;
                        }
                    }
                    // Combine: reverse backward part, then forward part
                    java.util.List<double[]> curve = new java.util.ArrayList<>();
                    if (bxs != null && bys != null) {
                        for (int i = bxs.length - 1; i >= 0; i--) {
                            if (bxs[i] >= xmin && bxs[i] <= xmax) {
                                curve.add(new double[]{bxs[i], bys[i]});
                            }
                        }
                    }
                    for (int i = 0; i < oxs.length; i++) {
                        if (oxs[i] > xmin && oxs[i] <= xmax) {
                            curve.add(new double[]{oxs[i], oys[i]});
                        }
                    }
                    if (!curve.isEmpty()) {
                        solutionCurves.add(new double[curve.size() * 2]);
                        double[] flat = solutionCurves.get(solutionCurves.size() - 1);
                        for (int i = 0; i < curve.size(); i++) {
                            flat[i * 2] = curve.get(i)[0];
                            flat[i * 2 + 1] = curve.get(i)[1];
                        }
                    }
                }
            }
        }

        // Show direction field in a dialog with custom Canvas drawing
        showDirectionFieldDialog(expr, xs, ys, slopes, grid, xmin, xmax, ymin, ymax, solutionCurves);
        resultView.append(getString(R.string.toast_direction_field_plotted) + "\n");
    }

    private void showDirectionFieldDialog(String expr, double[] gridXs, double[] gridYs, double[] slopes,
                                           int grid, double xmin, double xmax, double ymin, double ymax,
                                           java.util.List<double[]> solutionCurves) {
        android.app.Dialog dialog = new android.app.Dialog(this, androidx.appcompat.R.style.ThemeOverlay_AppCompat_Dialog_Alert);
        dialog.setTitle(getString(R.string.dialog_direction_field));

        android.widget.FrameLayout container = new android.widget.FrameLayout(this);
        container.setPadding(16, 16, 16, 16);

        android.view.View fieldView = new android.view.View(this) {
            @Override
            protected void onDraw(android.graphics.Canvas canvas) {
                super.onDraw(canvas);
                int w = getWidth();
                int h = getHeight();
                android.graphics.Paint bgPaint = new android.graphics.Paint();
                bgPaint.setColor(android.graphics.Color.parseColor("#181825"));
                canvas.drawRect(0, 0, w, h, bgPaint);

                // Scale from math coords to screen coords
                float margin = 20f;
                float plotW = w - 2 * margin;
                float plotH = h - 2 * margin;
                float scaleX = plotW / (float)(xmax - xmin);
                float scaleY = plotH / (float)(ymax - ymin);

                // Draw axes
                android.graphics.Paint axisPaint = new android.graphics.Paint();
                axisPaint.setColor(android.graphics.Color.parseColor("#585b70"));
                axisPaint.setStrokeWidth(1f);

                float axX = margin + (float)((0 - xmin) * scaleX);
                float axY = margin + (float)((ymax - 0) * scaleY);
                if (axX >= margin && axX <= margin + plotW) {
                    canvas.drawLine(axX, margin, axX, margin + plotH, axisPaint);
                }
                if (axY >= margin && axY <= margin + plotH) {
                    canvas.drawLine(margin, axY, margin + plotW, axY, axisPaint);
                }

                // Draw direction arrows
                android.graphics.Paint arrowPaint = new android.graphics.Paint();
                arrowPaint.setColor(android.graphics.Color.parseColor("#89b4fa"));
                arrowPaint.setStrokeWidth(2f);
                arrowPaint.setStyle(android.graphics.Paint.Style.STROKE);
                arrowPaint.setAntiAlias(true);

                float arrowLen = Math.min(plotW, plotH) / grid * 0.7f;

                for (int i = 0; i < gridXs.length; i++) {
                    if (Double.isNaN(slopes[i]) || Double.isInfinite(slopes[i])) continue;
                    float cx = margin + (float)((gridXs[i] - xmin) * scaleX);
                    float cy = margin + (float)((ymax - gridYs[i]) * scaleY);
                    if (cx < margin || cx > margin + plotW || cy < margin || cy > margin + plotH) continue;

                    double slope = slopes[i];
                    double normLen = arrowLen / Math.sqrt(1 + slope * slope);
                    double dxHalf = normLen * 0.5;
                    double dyHalf = normLen * slope * 0.5;

                    float x1 = (float)(cx - dxHalf * scaleX / plotW * plotW);
                    float y1 = (float)(cy + dyHalf * scaleY / plotH * plotH);
                    float x2 = (float)(cx + dxHalf * scaleX / plotW * plotW);
                    float y2 = (float)(cy - dyHalf * scaleY / plotH * plotH);

                    // Recalculate with proper scaling
                    double screenDx = dxHalf;
                    double screenDy = dxHalf * slope;
                    double screenLen = Math.sqrt(screenDx * screenDx + screenDy * screenDy);
                    if (screenLen > arrowLen / 2) {
                        double scale2 = (arrowLen / 2) / screenLen;
                        screenDx *= scale2;
                        screenDy *= scale2;
                    }
                    x1 = (float)(cx - screenDx);
                    y1 = (float)(cy + screenDy);
                    x2 = (float)(cx + screenDx);
                    y2 = (float)(cy - screenDy);

                    canvas.drawLine(x1, y1, x2, y2, arrowPaint);

                    // Draw arrowhead
                    double angle = Math.atan2(-(y2 - y1), x2 - x1);
                    double headLen = arrowLen * 0.2;
                    float hx1 = (float)(x2 - headLen * Math.cos(angle - 0.4));
                    float hy1 = (float)(y2 + headLen * Math.sin(angle - 0.4));
                    float hx2 = (float)(x2 - headLen * Math.cos(angle + 0.4));
                    float hy2 = (float)(y2 + headLen * Math.sin(angle + 0.4));
                    canvas.drawLine(x2, y2, hx1, hy1, arrowPaint);
                    canvas.drawLine(x2, y2, hx2, hy2, arrowPaint);
                }

                // Draw solution curves
                android.graphics.Paint curvePaint = new android.graphics.Paint();
                curvePaint.setColor(android.graphics.Color.parseColor("#f38ba8"));
                curvePaint.setStrokeWidth(2.5f);
                curvePaint.setStyle(android.graphics.Paint.Style.STROKE);
                curvePaint.setAntiAlias(true);

                for (double[] curve : solutionCurves) {
                    if (curve.length < 4) continue;
                    android.graphics.Path path = new android.graphics.Path();
                    boolean started = false;
                    for (int i = 0; i < curve.length; i += 2) {
                        float sx = margin + (float)((curve[i] - xmin) * scaleX);
                        float sy = margin + (float)((ymax - curve[i + 1]) * scaleY);
                        if (!started) {
                            path.moveTo(sx, sy);
                            started = true;
                        } else {
                            path.lineTo(sx, sy);
                        }
                    }
                    canvas.drawPath(path, curvePaint);
                }

                // Draw labels
                android.graphics.Paint labelPaint = new android.graphics.Paint();
                labelPaint.setColor(android.graphics.Color.parseColor("#a6adc8"));
                labelPaint.setTextSize(24f);
                canvas.drawText("dy/dx = " + expr, margin, h - margin / 2, labelPaint);
            }
        };

        container.addView(fieldView, new android.widget.FrameLayout.LayoutParams(
            android.widget.FrameLayout.LayoutParams.MATCH_PARENT,
            android.widget.FrameLayout.LayoutParams.MATCH_PARENT,
            android.view.Gravity.CENTER));

        dialog.setContentView(container);
        dialog.getWindow().setLayout(android.view.WindowManager.LayoutParams.MATCH_PARENT,
            android.view.WindowManager.LayoutParams.MATCH_PARENT);
        dialog.show();
    }

    private void onTaylorPlot() {
        String e = getExpr();
        if (e.isEmpty()) { toast(getString(R.string.toast_enter_expr)); return; }
        double a = getX();
        int order = getTaylorOrder();

        double rangeA = getA();
        double rangeB = getB();
        if (rangeA >= rangeB) { toast(getString(R.string.toast_set_ab)); return; }

        // Precompute Taylor coefficients once (avoids O(n*order) redundant derivative calls)
        double[] coeffs = new double[order + 1];
        double factorial = 1.0;
        for (int k = 0; k <= order; k++) {
            if (k > 0) factorial *= k;
            double dk = CalcEngine.nthDerivative(e, a, k, 1e-5);
            coeffs[k] = Double.isNaN(dk) ? 0.0 : dk / factorial;
        }

        int n = 500;
        double step = (rangeB - rangeA) / (n - 1);
        double[] xs = new double[n];
        double[] ysOrig = new double[n];
        double[] ysTaylor = new double[n];

        for (int i = 0; i < n; i++) {
            xs[i] = rangeA + i * step;
            double yOrig = CalcEngine.evaluate(e, xs[i]);
            ysOrig[i] = Double.isNaN(yOrig) ? 0.0 : yOrig;

            double dx = xs[i] - a;
            double taylorVal = 0.0;
            double dxPower = 1.0;
            for (int k = 0; k <= order; k++) {
                taylorVal += coeffs[k] * dxPower;
                dxPower *= dx;
            }
            ysTaylor[i] = taylorVal;
        }

        Intent intent = new Intent(this, PlotActivity.class);
        intent.putExtra("is_taylor", true);
        intent.putExtra("taylor_expr", e);
        intent.putExtra("taylor_a", a);
        intent.putExtra("taylor_order", order);
        intent.putExtra("taylor_xs", xs);
        intent.putExtra("taylor_ys_orig", ysOrig);
        intent.putExtra("taylor_ys_taylor", ysTaylor);
        intent.putExtra("x_min", rangeA);
        intent.putExtra("x_max", rangeB);
        startActivity(intent);
    }

    private double[] parseStatsData() {
        String raw = statsDataInput.getText().toString().trim();
        if (raw.isEmpty()) { toast(getString(R.string.toast_enter_data)); return null; }
        String[] tokens = raw.split("[,;\\s]+");
        java.util.ArrayList<Double> values = new java.util.ArrayList<>();
        for (String t : tokens) {
            t = t.trim();
            if (t.isEmpty()) continue;
            try {
                values.add(Double.parseDouble(t));
            } catch (NumberFormatException e) {
                toast(getString(R.string.toast_invalid_num, t));
                return null;
            }
        }
        if (values.isEmpty()) { toast(getString(R.string.toast_no_valid_nums)); return null; }
        double[] result = new double[values.size()];
        for (int i = 0; i < values.size(); i++) result[i] = values.get(i);
        return result;
    }

    private void onStatsCompute() {
        double[] data = parseStatsData();
        if (data == null) return;
        int n = data.length;

        double sum = 0;
        for (double v : data) sum += v;
        double mean = sum / n;

        double[] sorted = data.clone();
        java.util.Arrays.sort(sorted);
        double median;
        if (n % 2 == 0) {
            median = (sorted[n / 2 - 1] + sorted[n / 2]) / 2.0;
        } else {
            median = sorted[n / 2];
        }

        double min = sorted[0];
        double max = sorted[n - 1];
        double range = max - min;

        // Population variance & std
        double varPop = 0;
        for (double v : data) varPop += (v - mean) * (v - mean);
        varPop /= n;
        double stdPop = Math.sqrt(varPop);

        // Sample variance & std
        double varSam = 0;
        if (n > 1) {
            for (double v : data) varSam += (v - mean) * (v - mean);
            varSam /= (n - 1);
        }
        double stdSam = Math.sqrt(varSam);

        // Quartiles
        double q1 = sorted[n / 4];
        double q3 = sorted[Math.min(3 * n / 4, n - 1)];
        double iqr = q3 - q1;

        StringBuilder sb = new StringBuilder();
        sb.append(String.format(getString(R.string.stats_header), n)).append("\n\n");
        sb.append(String.format(getString(R.string.stats_sum), sum)).append("\n");
        sb.append(String.format(getString(R.string.stats_mean), mean)).append("\n");
        sb.append(String.format(getString(R.string.stats_median), median)).append("\n");
        sb.append(String.format(getString(R.string.stats_min), min)).append("\n");
        sb.append(String.format(getString(R.string.stats_max), max)).append("\n");
        sb.append(String.format(getString(R.string.stats_range), range)).append("\n");
        sb.append(String.format(getString(R.string.stats_q1), q1)).append("\n");
        sb.append(String.format(getString(R.string.stats_q3), q3)).append("\n");
        sb.append(String.format(getString(R.string.stats_iqr), iqr)).append("\n");
        sb.append(String.format(getString(R.string.stats_var_pop), varPop)).append("\n");
        if (n > 1) sb.append(String.format(getString(R.string.stats_var_sam), varSam)).append("\n");
        sb.append(String.format(getString(R.string.stats_std_pop), stdPop)).append("\n");
        if (n > 1) sb.append(String.format(getString(R.string.stats_std_sam), stdSam)).append("\n");
        sb.append(getString(R.string.stats_sorted));
        int show = Math.min(n, 20);
        for (int i = 0; i < show; i++) {
            if (i > 0) sb.append(", ");
            sb.append(fmt(sorted[i]));
        }
        if (n > show) sb.append(String.format(getString(R.string.stats_total), n));

        android.widget.TextView tv = new android.widget.TextView(this);
        tv.setText(sb.toString());
        tv.setTypeface(android.graphics.Typeface.MONOSPACE);
        tv.setTextSize(13);
        tv.setPadding(40, 24, 40, 24);
        tv.setTextColor(android.graphics.Color.parseColor("#cdd6f4"));
        tv.setBackgroundColor(android.graphics.Color.parseColor("#181825"));

        android.widget.ScrollView sv = new android.widget.ScrollView(this);
        sv.addView(tv);

        new androidx.appcompat.app.AlertDialog.Builder(this, androidx.appcompat.R.style.ThemeOverlay_AppCompat_Dialog_Alert)
            .setTitle(getString(R.string.dialog_statistics))
            .setView(sv)
            .setPositiveButton(getString(R.string.dialog_close), null)
            .show();

        resultView.append(String.format(getString(R.string.stats_toast), n, mean, stdPop) + "\n");
    }

    private void onStatsSort() {
        double[] data = parseStatsData();
        if (data == null) return;
        java.util.Arrays.sort(data);
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < data.length; i++) {
            if (i > 0) sb.append(", ");
            sb.append(fmt(data[i]));
        }
        statsDataInput.setText(sb.toString());
        toast(getString(R.string.toast_data_sorted, data.length));
    }

    // --- Matrix Operations ---

    private double[][] parseMatrix(String text) {
        text = text.trim();
        if (text.isEmpty()) return null;
        String[] rows = text.split(";");
        java.util.ArrayList<double[]> matrix = new java.util.ArrayList<>();
        int ncols = -1;
        for (String row : rows) {
            row = row.trim();
            if (row.isEmpty()) continue;
            String[] cols = row.split(",");
            java.util.ArrayList<Double> vals = new java.util.ArrayList<>();
            for (String c : cols) {
                c = c.trim();
                if (c.isEmpty()) continue;
                try {
                    vals.add(Double.parseDouble(c));
                } catch (NumberFormatException e) {
                    toast(getString(R.string.toast_invalid_num_matrix, c));
                    return null;
                }
            }
            if (vals.isEmpty()) continue;
            if (ncols < 0) ncols = vals.size();
            else if (vals.size() != ncols) {
                toast(getString(R.string.toast_cols_match));
                return null;
            }
            double[] rowArr = new double[vals.size()];
            for (int i = 0; i < vals.size(); i++) rowArr[i] = vals.get(i);
            matrix.add(rowArr);
        }
        if (matrix.isEmpty()) return null;
        return matrix.toArray(new double[0][]);
    }

    private String formatMatrix(double[][] mat) {
        StringBuilder sb = new StringBuilder();
        for (double[] row : mat) {
            sb.append("  ");
            for (int j = 0; j < row.length; j++) {
                if (j > 0) sb.append("  ");
                sb.append(String.format("%12.6g", row[j]));
            }
            sb.append("\n");
        }
        return sb.toString();
    }

    private void showMatrixResult(String title, String content) {
        android.widget.TextView tv = new android.widget.TextView(this);
        tv.setText(content);
        tv.setTypeface(android.graphics.Typeface.MONOSPACE);
        tv.setTextSize(13);
        tv.setPadding(40, 24, 40, 24);
        tv.setTextColor(android.graphics.Color.parseColor("#cdd6f4"));
        tv.setBackgroundColor(android.graphics.Color.parseColor("#181825"));
        android.widget.ScrollView sv = new android.widget.ScrollView(this);
        sv.addView(tv);
        new androidx.appcompat.app.AlertDialog.Builder(this, androidx.appcompat.R.style.ThemeOverlay_AppCompat_Dialog_Alert)
            .setTitle(title)
            .setView(sv)
            .setPositiveButton(getString(R.string.dialog_close), null)
            .show();
    }

    private double[][] getMatrixA() {
        return parseMatrix(matrixAInput.getText().toString());
    }

    private double[][] getMatrixB() {
        return parseMatrix(matrixBInput.getText().toString());
    }

    private void onMatrixAdd() {
        double[][] a = getMatrixA(); double[][] b = getMatrixB();
        if (a == null || b == null) return;
        if (a.length == 0 || b.length == 0) return;
        if (a.length != b.length || a[0].length != b[0].length) { toast(getString(R.string.toast_dims_match)); return; }
        double[][] r = new double[a.length][a[0].length];
        for (int i = 0; i < a.length; i++)
            for (int j = 0; j < a[0].length; j++)
                r[i][j] = a[i][j] + b[i][j];
        showMatrixResult(getString(R.string.mat_add_title), formatMatrix(r));
        resultView.append(getString(R.string.mat_add_result) + "\n");
    }

    private void onMatrixSub() {
        double[][] a = getMatrixA(); double[][] b = getMatrixB();
        if (a == null || b == null) return;
        if (a.length == 0 || b.length == 0) return;
        if (a.length != b.length || a[0].length != b[0].length) { toast(getString(R.string.toast_dims_match)); return; }
        double[][] r = new double[a.length][a[0].length];
        for (int i = 0; i < a.length; i++)
            for (int j = 0; j < a[0].length; j++)
                r[i][j] = a[i][j] - b[i][j];
        showMatrixResult(getString(R.string.mat_sub_title), formatMatrix(r));
        resultView.append(getString(R.string.mat_sub_result) + "\n");
    }

    private void onMatrixMul() {
        double[][] a = getMatrixA(); double[][] b = getMatrixB();
        if (a == null || b == null) return;
        if (a.length == 0 || b.length == 0) return;
        if (a[0].length != b.length) { toast(getString(R.string.toast_cols_rows)); return; }
        double[][] r = new double[a.length][b[0].length];
        for (int i = 0; i < a.length; i++)
            for (int j = 0; j < b[0].length; j++) {
                double sum = 0;
                for (int k = 0; k < a[0].length; k++) sum += a[i][k] * b[k][j];
                r[i][j] = sum;
            }
        showMatrixResult(getString(R.string.mat_mul_title), formatMatrix(r));
        resultView.append(getString(R.string.mat_mul_result) + "\n");
    }

    private void onMatrixDet() {
        double[][] a = getMatrixA();
        if (a == null) return;
        if (a.length == 0) return;
        if (a.length != a[0].length) { toast(getString(R.string.toast_det_square)); return; }
        double det = det(a);
        showMatrixResult(getString(R.string.mat_det_title), String.format(getString(R.string.mat_det_result), det));
        resultView.append(String.format(getString(R.string.mat_det_result), det) + "\n");
    }

    private double det(double[][] m) {
        int n = m.length;
        if (n == 1) return m[0][0];
        if (n == 2) return m[0][0]*m[1][1] - m[0][1]*m[1][0];
        // LU decomposition with partial pivoting for O(n³) complexity
        double[][] lu = new double[n][n];
        for (int i = 0; i < n; i++)
            System.arraycopy(m[i], 0, lu[i], 0, n);
        int[] piv = new int[n];
        for (int i = 0; i < n; i++) piv[i] = i;
        double det = 1.0;
        for (int j = 0; j < n; j++) {
            int maxRow = j;
            double maxVal = Math.abs(lu[j][j]);
            for (int i = j + 1; i < n; i++) {
                if (Math.abs(lu[i][j]) > maxVal) {
                    maxVal = Math.abs(lu[i][j]);
                    maxRow = i;
                }
            }
            if (maxRow != j) {
                double[] tmp = lu[j]; lu[j] = lu[maxRow]; lu[maxRow] = tmp;
                det = -det;
            }
            if (Math.abs(lu[j][j]) < 1e-15) return 0.0;
            det *= lu[j][j];
            for (int i = j + 1; i < n; i++) {
                lu[i][j] /= lu[j][j];
                for (int k = j + 1; k < n; k++) {
                    lu[i][k] -= lu[i][j] * lu[j][k];
                }
            }
        }
        return det;
    }

    private void onMatrixInv() {
        double[][] a = getMatrixA();
        if (a == null) return;
        if (a.length != a[0].length) { toast(getString(R.string.toast_inv_square)); return; }
        int n = a.length;
        // Use Gauss-Jordan elimination with partial pivoting for better accuracy
        double[][] aug = new double[n][2 * n];
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                aug[i][j] = a[i][j];
                aug[i][n + j] = (i == j) ? 1.0 : 0.0;
            }
        }
        for (int col = 0; col < n; col++) {
            // Find pivot
            int maxRow = col;
            double maxVal = Math.abs(aug[col][col]);
            for (int row = col + 1; row < n; row++) {
                if (Math.abs(aug[row][col]) > maxVal) {
                    maxVal = Math.abs(aug[row][col]);
                    maxRow = row;
                }
            }
            if (maxVal < 1e-12) { toast(getString(R.string.toast_singular)); return; }
            // Swap rows
            double[] tmp = aug[col]; aug[col] = aug[maxRow]; aug[maxRow] = tmp;
            // Scale pivot row
            double piv = aug[col][col];
            for (int j = 0; j < 2 * n; j++) aug[col][j] /= piv;
            // Eliminate column
            for (int row = 0; row < n; row++) {
                if (row == col) continue;
                double factor = aug[row][col];
                for (int j = 0; j < 2 * n; j++) aug[row][j] -= factor * aug[col][j];
            }
        }
        double[][] inv = new double[n][n];
        for (int i = 0; i < n; i++)
            for (int j = 0; j < n; j++)
                inv[i][j] = aug[i][n + j];
        showMatrixResult(getString(R.string.mat_inv_title), formatMatrix(inv));
        resultView.append(getString(R.string.mat_inv_result) + "\n");
    }

    private void onMatrixTranspose() {
        double[][] a = getMatrixA();
        if (a == null) return;
        int m = a.length, n = a[0].length;
        double[][] t = new double[n][m];
        for (int i = 0; i < m; i++)
            for (int j = 0; j < n; j++)
                t[j][i] = a[i][j];
        showMatrixResult(getString(R.string.mat_trans_title), formatMatrix(t));
        resultView.append(getString(R.string.mat_transpose_result) + "\n");
    }

    private void onMatrixRank() {
        double[][] a = getMatrixA();
        if (a == null) return;
        int m = a.length, n = a[0].length;
        double[][] rref = a.clone();
        for (int i = 0; i < m; i++) rref[i] = a[i].clone();
        int rank = 0;
        int pivotRow = 0;
        for (int col = 0; col < n && pivotRow < m; col++) {
            int maxRow = pivotRow;
            for (int row = pivotRow + 1; row < m; row++) {
                if (Math.abs(rref[row][col]) > Math.abs(rref[maxRow][col])) maxRow = row;
            }
            if (Math.abs(rref[maxRow][col]) < 1e-10) continue;
            double[] tmp = rref[pivotRow]; rref[pivotRow] = rref[maxRow]; rref[maxRow] = tmp;
            double piv = rref[pivotRow][col];
            for (int j = 0; j < n; j++) rref[pivotRow][j] /= piv;
            for (int row = 0; row < m; row++) {
                if (row == pivotRow) continue;
                double f = rref[row][col];
                for (int j = 0; j < n; j++) rref[row][j] -= f * rref[pivotRow][j];
            }
            rank++;
            pivotRow++;
        }
        showMatrixResult("rank(A)", String.format(getString(R.string.mat_rank_result), rank));
        resultView.append(String.format(getString(R.string.mat_rank_result), rank) + "\n");
    }

    private void onMatrixEigen() {
        double[][] a = getMatrixA();
        if (a == null) return;
        if (a.length != a[0].length) { toast(getString(R.string.toast_eig_square)); return; }
        int n = a.length;
        // For 2x2: use characteristic equation
        if (n == 2) {
            double trace = a[0][0] + a[1][1];
            double detA = a[0][0]*a[1][1] - a[0][1]*a[1][0];
            double disc = trace*trace - 4*detA;
            StringBuilder sb = new StringBuilder();
            sb.append(getString(R.string.mat_eigen_header)).append("\n\n");
            if (disc >= 0) {
                double l1 = (trace + Math.sqrt(disc)) / 2;
                double l2 = (trace - Math.sqrt(disc)) / 2;
                sb.append(String.format(getString(R.string.mat_eigen_lambda), 1, l1)).append("\n");
                sb.append(String.format(getString(R.string.mat_eigen_lambda), 2, l2)).append("\n");
            } else {
                double real = trace / 2;
                double imag = Math.sqrt(-disc) / 2;
                sb.append(String.format(getString(R.string.mat_eigen_lambda_complex), 1, real, imag)).append("\n");
                sb.append(String.format(getString(R.string.mat_eigen_lambda_complex), 2, real, -imag)).append("\n");
            }
            showMatrixResult(getString(R.string.mat_eigen_title), sb.toString());
        } else {
            // For larger matrices: use power iteration to find dominant eigenvalue
            // and deflate to find subsequent ones (QR algorithm simplified)
            StringBuilder sb = new StringBuilder();
            sb.append(getString(R.string.mat_eigen_approx_header)).append("\n\n");
            double[][] mat = new double[n][n];
            for (int i = 0; i < n; i++)
                for (int j = 0; j < n; j++)
                    mat[i][j] = a[i][j];
            double[] eigenvalues = new double[n];
            for (int e = 0; e < n; e++) {
                // Power iteration
                double[] v = new double[n];
                v[0] = 1.0;  // Initial guess
                double eigenval = 0;
                for (int iter = 0; iter < 1000; iter++) {
                    double[] newV = new double[n];
                    for (int i = 0; i < n; i++) {
                        double sum = 0;
                        for (int j = 0; j < n; j++) sum += mat[i][j] * v[j];
                        newV[i] = sum;
                    }
                    // Normalize
                    double norm = 0;
                    for (int i = 0; i < n; i++) norm += newV[i] * newV[i];
                    norm = Math.sqrt(norm);
                    if (norm < 1e-15) break;
                    for (int i = 0; i < n; i++) newV[i] /= norm;
                    // Estimate eigenvalue (Rayleigh quotient)
                    double[] Av = new double[n];
                    for (int i = 0; i < n; i++) {
                        double sum = 0;
                        for (int j = 0; j < n; j++) sum += mat[i][j] * newV[j];
                        Av[i] = sum;
                    }
                    double num = 0, den = 0;
                    for (int i = 0; i < n; i++) {
                        num += newV[i] * Av[i];
                        den += newV[i] * newV[i];
                    }
                    eigenval = num / den;
                    v = newV;
                }
                eigenvalues[e] = eigenval;
                sb.append(String.format(getString(R.string.mat_eigen_lambda), e + 1, eigenval)).append("\n");
                // Deflate: subtract eigenvalue * v * v^T
                for (int i = 0; i < n; i++)
                    for (int j = 0; j < n; j++)
                        mat[i][j] -= eigenval * v[i] * v[j];
            }
            showMatrixResult(getString(R.string.mat_eigen_title), sb.toString());
        }
        resultView.append(getString(R.string.mat_eigen_done) + "\n");
    }

    private void onStatsHistogram() {
        double[] data = parseStatsData();
        if (data == null) return;
        int n = data.length;

        // Calculate basic stats for text display
        double sum = 0;
        for (double v : data) sum += v;
        double mean = sum / n;

        java.util.Arrays.sort(data);
        double median;
        if (n % 2 == 0) {
            median = (data[n / 2 - 1] + data[n / 2]) / 2.0;
        } else {
            median = data[n / 2];
        }

        // Create histogram as text-based bar chart
        int nBins = Math.max(5, Math.min(15, (int) Math.sqrt(n) + 1));
        double min = data[0];
        double max = data[n - 1];
        double binWidth = (max - min) / nBins;
        if (binWidth == 0) binWidth = 1;

        int[] counts = new int[nBins];
        for (double v : data) {
            int bin = (int) ((v - min) / binWidth);
            if (bin >= nBins) bin = nBins - 1;
            counts[bin]++;
        }

        StringBuilder sb = new StringBuilder();
        sb.append(String.format(getString(R.string.histogram_title), nBins)).append("\n");
        sb.append(String.format(getString(R.string.histogram_stats), mean, median)).append("\n\n");

        int maxCount = 0;
        for (int c : counts) if (c > maxCount) maxCount = c;
        int barMaxLen = 30;

        for (int i = 0; i < nBins; i++) {
            double lo = min + i * binWidth;
            double hi = lo + binWidth;
            int barLen = maxCount > 0 ? (counts[i] * barMaxLen / maxCount) : 0;
            StringBuilder bar = new StringBuilder();
            for (int j = 0; j < barLen; j++) bar.append("\u2588");
            sb.append(String.format("[%6.3g,%6.3g) %3d |%s\n", lo, hi, counts[i], bar.toString()));
        }

        android.widget.TextView tv = new android.widget.TextView(this);
        tv.setText(sb.toString());
        tv.setTypeface(android.graphics.Typeface.MONOSPACE);
        tv.setTextSize(13);
        tv.setPadding(40, 24, 40, 24);
        tv.setTextColor(android.graphics.Color.parseColor("#cdd6f4"));
        tv.setBackgroundColor(android.graphics.Color.parseColor("#181825"));

        android.widget.ScrollView sv = new android.widget.ScrollView(this);
        sv.addView(tv);

        new androidx.appcompat.app.AlertDialog.Builder(this, androidx.appcompat.R.style.ThemeOverlay_AppCompat_Dialog_Alert)
            .setTitle(getString(R.string.dialog_histogram))
            .setView(sv)
            .setPositiveButton(getString(R.string.dialog_close), null)
            .show();

        resultView.append(String.format(getString(R.string.histogram_toast), nBins, mean) + "\n");
    }

    // ------------------------------------------------------------------
    //  Curve Fitting / Regression
    // ------------------------------------------------------------------
    private double[] parseRegData(EditText xInput, EditText yInput, boolean useX) {
        double[] ys;
        String yRaw = yInput.getText().toString().trim();
        if (!yRaw.isEmpty()) {
            ys = parseDataArray(yRaw);
        } else {
            ys = parseStatsData();
        }
        if (ys == null || ys.length < 2) {
            toast(getString(R.string.toast_need_2y));
            return null;
        }
        if (useX) {
            String xRaw = xInput.getText().toString().trim();
            if (!xRaw.isEmpty()) {
                return parseDataArray(xRaw);
            }
            double[] xs = new double[ys.length];
            for (int i = 0; i < ys.length; i++) xs[i] = i + 1;
            return xs;
        }
        return ys;
    }

    private double[] parseDataArray(String raw) {
        String[] tokens = raw.split("[,;\\s]+");
        java.util.ArrayList<Double> values = new java.util.ArrayList<>();
        for (String t : tokens) {
            t = t.trim();
            if (t.isEmpty()) continue;
            try { values.add(Double.parseDouble(t)); } catch (NumberFormatException e) { return null; }
        }
        double[] result = new double[values.size()];
        for (int i = 0; i < values.size(); i++) result[i] = values.get(i);
        return result;
    }

    private void showRegResult(String title, String equation, double r2) {
        StringBuilder sb = new StringBuilder();
        sb.append(title).append("\n\n");
        sb.append(getString(R.string.regression_prefix)).append(equation).append("\n");
        sb.append(String.format("R\u00B2 = %.8f", r2));
        android.widget.TextView tv = new android.widget.TextView(this);
        tv.setText(sb.toString());
        tv.setTypeface(android.graphics.Typeface.MONOSPACE);
        tv.setTextSize(14);
        tv.setPadding(40, 24, 40, 24);
        tv.setTextColor(android.graphics.Color.parseColor("#cdd6f4"));
        tv.setBackgroundColor(android.graphics.Color.parseColor("#181825"));
        new androidx.appcompat.app.AlertDialog.Builder(this, androidx.appcompat.R.style.ThemeOverlay_AppCompat_Dialog_Alert)
            .setTitle(title)
            .setView(tv)
            .setPositiveButton(getString(R.string.dialog_close), null)
            .show();
        resultView.append(String.format("%s: %s (R\u00B2=%.6f)\n", title, equation, r2));
    }

    private void onRegLinear(EditText xInput, EditText yInput) {
        double[] xs = parseRegData(xInput, yInput, true);
        double[] ys = parseRegData(xInput, yInput, false);
        if (xs == null || ys == null || xs.length != ys.length) return;
        int n = xs.length;
        double xMean = 0, yMean = 0;
        for (int i = 0; i < n; i++) { xMean += xs[i]; yMean += ys[i]; }
        xMean /= n; yMean /= n;
        double ssXY = 0, ssXX = 0;
        for (int i = 0; i < n; i++) {
            ssXY += (xs[i] - xMean) * (ys[i] - yMean);
            ssXX += (xs[i] - xMean) * (xs[i] - xMean);
        }
        if (ssXX == 0) { toast(getString(R.string.toast_zero_variance)); return; }
        double slope = ssXY / ssXX;
        double intercept = yMean - slope * xMean;
        double ssRes = 0, ssTot = 0;
        for (int i = 0; i < n; i++) {
            double yPred = slope * xs[i] + intercept;
            ssRes += (ys[i] - yPred) * (ys[i] - yPred);
            ssTot += (ys[i] - yMean) * (ys[i] - yMean);
        }
        double r2 = ssTot != 0 ? 1.0 - ssRes / ssTot : 0;
        String eq = String.format("y = %.6g*x %s %.6g", slope, intercept >= 0 ? "+" : "-", Math.abs(intercept));
        showRegResult(getString(R.string.regression_linear), eq, r2);
    }

    private void onRegPoly(EditText xInput, EditText yInput, int degree) {
        double[] xs = parseRegData(xInput, yInput, true);
        double[] ys = parseRegData(xInput, yInput, false);
        if (xs == null || ys == null || xs.length != ys.length) return;
        if (xs.length < degree + 1) { toast(getString(R.string.toast_need_n_points, degree + 1)); return; }
        // Vandermonde matrix approach for polynomial least squares
        int n = xs.length;
        int m = degree + 1;
        double[][] A = new double[n][m];
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < m; j++) {
                A[i][j] = Math.pow(xs[i], j);
            }
        }
        // Solve via normal equations: (A^T A) c = A^T y
        double[][] AtA = new double[m][m];
        double[] Aty = new double[m];
        for (int i = 0; i < m; i++) {
            for (int j = 0; j < m; j++) {
                double sum = 0;
                for (int k = 0; k < n; k++) sum += A[k][i] * A[k][j];
                AtA[i][j] = sum;
            }
            double sum = 0;
            for (int k = 0; k < n; k++) sum += A[k][i] * ys[k];
            Aty[i] = sum;
        }
        // Gaussian elimination
        double[] coeffs = solveLinearSystem(AtA, Aty);
        if (coeffs == null) { toast(getString(R.string.toast_cannot_fit)); return; }
        // R²
        double yMean = 0;
        for (double v : ys) yMean += v;
        yMean /= n;
        double ssRes = 0, ssTot = 0;
        for (int i = 0; i < n; i++) {
            double yPred = 0;
            for (int j = 0; j < m; j++) yPred += coeffs[j] * Math.pow(xs[i], j);
            ssRes += (ys[i] - yPred) * (ys[i] - yPred);
            ssTot += (ys[i] - yMean) * (ys[i] - yMean);
        }
        double r2 = ssTot != 0 ? 1.0 - ssRes / ssTot : 0;
        StringBuilder eq = new StringBuilder("y = ");
        for (int j = degree; j >= 0; j--) {
            if (Math.abs(coeffs[j]) < 1e-12) continue;
            if (j < degree) eq.append(coeffs[j] >= 0 ? " + " : " - ");
            eq.append(String.format("%.6g", Math.abs(coeffs[j])));
            if (j > 1) eq.append("*x^").append(j);
            else if (j == 1) eq.append("*x");
        }
        showRegResult(String.format(getString(R.string.regression_poly), degree), eq.toString(), r2);
    }

    private double[] solveLinearSystem(double[][] A, double[] b) {
        int n = A.length;
        double[][] aug = new double[n][n + 1];
        for (int i = 0; i < n; i++) {
            System.arraycopy(A[i], 0, aug[i], 0, n);
            aug[i][n] = b[i];
        }
        for (int col = 0; col < n; col++) {
            int maxRow = col;
            for (int row = col + 1; row < n; row++) {
                if (Math.abs(aug[row][col]) > Math.abs(aug[maxRow][col])) maxRow = row;
            }
            double[] tmp = aug[col]; aug[col] = aug[maxRow]; aug[maxRow] = tmp;
            if (Math.abs(aug[col][col]) < 1e-12) return null;
            for (int row = col + 1; row < n; row++) {
                double factor = aug[row][col] / aug[col][col];
                for (int j = col; j <= n; j++) aug[row][j] -= factor * aug[col][j];
            }
        }
        double[] x = new double[n];
        for (int i = n - 1; i >= 0; i--) {
            x[i] = aug[i][n];
            for (int j = i + 1; j < n; j++) x[i] -= aug[i][j] * x[j];
            x[i] /= aug[i][i];
        }
        return x;
    }

    private void onRegExponential(EditText xInput, EditText yInput) {
        double[] xs = parseRegData(xInput, yInput, true);
        double[] ys = parseRegData(xInput, yInput, false);
        if (xs == null || ys == null || xs.length != ys.length) return;
        // Filter positive y values for log transform
        java.util.ArrayList<Double> xList = new java.util.ArrayList<>();
        java.util.ArrayList<Double> yList = new java.util.ArrayList<>();
        for (int i = 0; i < xs.length; i++) {
            if (ys[i] > 0 && Double.isFinite(xs[i]) && Double.isFinite(ys[i])) {
                xList.add(xs[i]); yList.add(ys[i]);
            }
        }
        if (xList.size() < 2) { toast(getString(R.string.toast_need_2_pos_y)); return; }
        int n = xList.size();
        double[] lx = new double[n], ly = new double[n];
        for (int i = 0; i < n; i++) { lx[i] = xList.get(i); ly[i] = Math.log(yList.get(i)); }
        double xMean = 0, lyMean = 0;
        for (int i = 0; i < n; i++) { xMean += lx[i]; lyMean += ly[i]; }
        xMean /= n; lyMean /= n;
        double ssXY = 0, ssXX = 0;
        for (int i = 0; i < n; i++) {
            ssXY += (lx[i] - xMean) * (ly[i] - lyMean);
            ssXX += (lx[i] - xMean) * (lx[i] - xMean);
        }
        if (ssXX == 0) { toast(getString(R.string.toast_zero_variance)); return; }
        double b = ssXY / ssXX;
        double lnA = lyMean - b * xMean;
        double a = Math.exp(lnA);
        // R²
        double yMean = 0;
        for (double v : yList) yMean += v;
        yMean /= n;
        double ssRes = 0, ssTot = 0;
        for (int i = 0; i < n; i++) {
            double yPred = a * Math.exp(b * lx[i]);
            ssRes += (yList.get(i) - yPred) * (yList.get(i) - yPred);
            ssTot += (yList.get(i) - yMean) * (yList.get(i) - yMean);
        }
        double r2 = ssTot != 0 ? 1.0 - ssRes / ssTot : 0;
        String eq = String.format("y = %.6g * e^(%.6g*x)", a, b);
        showRegResult(getString(R.string.regression_exponential), eq, r2);
    }

    private void onRegPower(EditText xInput, EditText yInput) {
        double[] xs = parseRegData(xInput, yInput, true);
        double[] ys = parseRegData(xInput, yInput, false);
        if (xs == null || ys == null || xs.length != ys.length) return;
        java.util.ArrayList<Double> xList = new java.util.ArrayList<>();
        java.util.ArrayList<Double> yList = new java.util.ArrayList<>();
        for (int i = 0; i < xs.length; i++) {
            if (xs[i] > 0 && ys[i] > 0 && Double.isFinite(xs[i]) && Double.isFinite(ys[i])) {
                xList.add(xs[i]); yList.add(ys[i]);
            }
        }
        if (xList.size() < 2) { toast(getString(R.string.toast_need_2_pos)); return; }
        int n = xList.size();
        double[] lx = new double[n], ly = new double[n];
        for (int i = 0; i < n; i++) { lx[i] = Math.log(xList.get(i)); ly[i] = Math.log(yList.get(i)); }
        double xMean = 0, lyMean = 0;
        for (int i = 0; i < n; i++) { xMean += lx[i]; lyMean += ly[i]; }
        xMean /= n; lyMean /= n;
        double ssXY = 0, ssXX = 0;
        for (int i = 0; i < n; i++) {
            ssXY += (lx[i] - xMean) * (ly[i] - lyMean);
            ssXX += (lx[i] - xMean) * (lx[i] - xMean);
        }
        if (ssXX == 0) { toast(getString(R.string.toast_zero_variance)); return; }
        double b = ssXY / ssXX;
        double lnA = lyMean - b * xMean;
        double a = Math.exp(lnA);
        double yMean = 0;
        for (double v : yList) yMean += v;
        yMean /= n;
        double ssRes = 0, ssTot = 0;
        for (int i = 0; i < n; i++) {
            double yPred = a * Math.pow(xList.get(i), b);
            ssRes += (yList.get(i) - yPred) * (yList.get(i) - yPred);
            ssTot += (yList.get(i) - yMean) * (yList.get(i) - yMean);
        }
        double r2 = ssTot != 0 ? 1.0 - ssRes / ssTot : 0;
        String eq = String.format("y = %.6g * x^%.6g", a, b);
        showRegResult(getString(R.string.regression_power), eq, r2);
    }

    private void onRegLogarithmic(EditText xInput, EditText yInput) {
        double[] xs = parseRegData(xInput, yInput, true);
        double[] ys = parseRegData(xInput, yInput, false);
        if (xs == null || ys == null || xs.length != ys.length) return;
        java.util.ArrayList<Double> xList = new java.util.ArrayList<>();
        java.util.ArrayList<Double> yList = new java.util.ArrayList<>();
        for (int i = 0; i < xs.length; i++) {
            if (xs[i] > 0 && Double.isFinite(xs[i]) && Double.isFinite(ys[i])) {
                xList.add(xs[i]); yList.add(ys[i]);
            }
        }
        if (xList.size() < 2) { toast(getString(R.string.toast_need_2_pos_x)); return; }
        int n = xList.size();
        double[] lx = new double[n];
        for (int i = 0; i < n; i++) lx[i] = Math.log(xList.get(i));
        double xMean = 0, yMean = 0;
        for (int i = 0; i < n; i++) { xMean += lx[i]; yMean += yList.get(i); }
        xMean /= n; yMean /= n;
        double ssXY = 0, ssXX = 0;
        for (int i = 0; i < n; i++) {
            ssXY += (lx[i] - xMean) * (yList.get(i) - yMean);
            ssXX += (lx[i] - xMean) * (lx[i] - xMean);
        }
        if (ssXX == 0) { toast(getString(R.string.toast_zero_variance)); return; }
        double b = ssXY / ssXX;
        double a = yMean - b * xMean;
        double ssRes = 0, ssTot = 0;
        for (int i = 0; i < n; i++) {
            double yPred = a + b * lx[i];
            ssRes += (yList.get(i) - yPred) * (yList.get(i) - yPred);
            ssTot += (yList.get(i) - yMean) * (yList.get(i) - yMean);
        }
        double r2 = ssTot != 0 ? 1.0 - ssRes / ssTot : 0;
        String eq = String.format("y = %.6g %s %.6g*ln(x)", a, b >= 0 ? "+" : "-", Math.abs(b));
        showRegResult(getString(R.string.regression_logarithmic), eq, r2);
    }

    private double[] lastRegXs, lastRegYs;
    private String lastRegEquation = "";
    private void onRegPlot(EditText xInput, EditText yInput) {
        double[] xs = parseRegData(xInput, yInput, true);
        double[] ys = parseRegData(xInput, yInput, false);
        if (xs == null || ys == null || xs.length != ys.length) return;
        lastRegXs = xs; lastRegYs = ys;
        Intent intent = new Intent(this, PlotActivity.class);
        intent.putExtra("expr", "");  // We'll pass precomputed data
        intent.putExtra("xMin", xs[0]);
        intent.putExtra("xMax", xs[xs.length - 1]);
        intent.putExtra("regression", true);
        intent.putExtra("regXs", xs);
        intent.putExtra("regYs", ys);
        startActivity(intent);
    }

    private void onPlotParametric() {
        String xExpr = xParamInput.getText().toString().trim();
        String yExpr = yParamInput.getText().toString().trim();
        if (xExpr.isEmpty() || yExpr.isEmpty()) {
            toast(getString(R.string.toast_enter_xt_yt));
            return;
        }

        double tMin, tMax;
        try {
            tMin = Double.parseDouble(tMinInput.getText().toString().trim());
            tMax = Double.parseDouble(tMaxInput.getText().toString().trim());
        } catch (NumberFormatException ex) {
            toast(getString(R.string.toast_invalid_t_range));
            return;
        }
        if (tMin >= tMax) {
            toast(getString(R.string.toast_t_range));
            return;
        }

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
            resultView.append(String.format(getString(R.string.parametric_error), CalcEngine.getLastError()) + "\n");
            return;
        }

        Intent intent = new Intent(this, PlotActivity.class);
        intent.putExtra("parametric_x", xExpr);
        intent.putExtra("parametric_y", yExpr);
        intent.putExtra("t_min", tMin);
        intent.putExtra("t_max", tMax);
        intent.putExtra("is_parametric", true);
        startActivity(intent);
    }

    private void onPlotPolar() {
        String rExpr = rPolarInput.getText().toString().trim();
        if (rExpr.isEmpty()) {
            toast(getString(R.string.toast_enter_rtheta));
            return;
        }

        double thetaMin, thetaMax;
        try {
            thetaMin = Double.parseDouble(thetaMinInput.getText().toString().trim());
            thetaMax = Double.parseDouble(thetaMaxInput.getText().toString().trim());
        } catch (NumberFormatException ex) {
            toast(getString(R.string.toast_invalid_theta_range));
            return;
        }
        if (thetaMin >= thetaMax) {
            toast(getString(R.string.toast_theta_range));
            return;
        }

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
            resultView.append(String.format(getString(R.string.polar_error), CalcEngine.getLastError()) + "\n");
            return;
        }

        // Convert polar to Cartesian coordinates for plotting
        double[] xs = new double[n];
        double[] ys = new double[n];
        for (int i = 0; i < n; i++) {
            if (Double.isNaN(rs[i])) {
                xs[i] = Double.NaN;
                ys[i] = Double.NaN;
            } else {
                xs[i] = rs[i] * Math.cos(thetas[i]);
                ys[i] = rs[i] * Math.sin(thetas[i]);
            }
        }

        Intent intent = new Intent(this, PlotActivity.class);
        intent.putExtra("parametric_x", rExpr);
        intent.putExtra("is_polar", true);
        intent.putExtra("t_min", thetaMin);
        intent.putExtra("t_max", thetaMax);
        startActivity(intent);
    }

    private void onPlotImplicit() {
        EditText implicitExprInput = findViewById(R.id.implicit_expr_input);
        EditText implicitResInput = findViewById(R.id.implicit_resolution_input);
        String impExpr = implicitExprInput.getText().toString().trim();
        if (impExpr.isEmpty()) {
            toast(getString(R.string.toast_enter_implicit));
            return;
        }
        int resolution = 200;
        try {
            resolution = Integer.parseInt(implicitResInput.getText().toString().trim());
            if (resolution < 50) resolution = 50;
            if (resolution > 500) resolution = 500;
        } catch (NumberFormatException ex) {
            resolution = 200;
        }

        Intent intent = new Intent(this, PlotActivity.class);
        intent.putExtra("implicit_expr", impExpr);
        intent.putExtra("implicit_resolution", resolution);
        intent.putExtra("is_implicit", true);
        intent.putExtra("x_min", getA());
        intent.putExtra("x_max", getB());
        intent.putExtra("y_min", getA());
        intent.putExtra("y_max", getB());
        startActivity(intent);
    }

    private void onGenerateTable() {
        String e = getExpr();
        if (e.isEmpty()) { toast(getString(R.string.toast_enter_expr)); return; }
        double a = getA();
        double b = getB();
        if (a >= b) { toast(getString(R.string.toast_table_range)); return; }
        int n = 21; // default points

        double step = (b - a) / (n - 1);
        double[] xs = new double[n];
        for (int i = 0; i < n; i++) {
            xs[i] = a + i * step;
        }
        double[] ys = CalcEngine.evaluateArray(e, xs);
        if (ys == null) {
            resultView.append(String.format(getString(R.string.table_error), CalcEngine.getLastError()) + "\n");
            return;
        }

        StringBuilder sb = new StringBuilder();
        sb.append(getString(R.string.table_header)).append("\n");
        sb.append("----------------------------\n");
        int valid = 0;
        for (int i = 0; i < n; i++) {
            String yStr = Double.isNaN(ys[i]) ? "N/A" : fmt(ys[i]);
            sb.append(fmt(xs[i])).append("\t").append(yStr).append("\n");
            if (!Double.isNaN(ys[i])) valid++;
        }
        sb.append("----------------------------\n");
        sb.append(String.format(getString(R.string.table_valid_count), valid, n)).append("\n");

        // Build CSV for sharing
        StringBuilder csv = new StringBuilder();
        csv.append("x,f(x)=").append(e.replace(",", ";")).append("\n");
        for (int i = 0; i < n; i++) {
            csv.append(xs[i]).append(",").append(Double.isNaN(ys[i]) ? "" : ys[i]).append("\n");
        }

        final String tableText = sb.toString();
        final String csvText = csv.toString();

        android.widget.TextView textView = new android.widget.TextView(this);
        textView.setText(tableText);
        textView.setTypeface(android.graphics.Typeface.MONOSPACE);
        textView.setTextSize(13);
        textView.setPadding(40, 24, 40, 24);
        textView.setTextColor(android.graphics.Color.parseColor("#cdd6f4"));
        textView.setBackgroundColor(android.graphics.Color.parseColor("#181825"));

        android.widget.ScrollView scrollView = new android.widget.ScrollView(this);
        scrollView.addView(textView);
        scrollView.setPadding(0, 0, 0, 0);

        new androidx.appcompat.app.AlertDialog.Builder(this, androidx.appcompat.R.style.ThemeOverlay_AppCompat_Dialog_Alert)
            .setTitle(getString(R.string.dialog_function_table, n))
            .setView(scrollView)
            .setPositiveButton(getString(R.string.dialog_share_csv), (dialog, which) -> shareText(csvText, "SuperCalc Table"))
            .setNegativeButton(getString(R.string.dialog_close), null)
            .show();

        resultView.append(String.format(getString(R.string.table_generated), valid, n) + "\n");
    }

    private void shareText(String text, String title) {
        Intent shareIntent = new Intent(Intent.ACTION_SEND);
        shareIntent.setType("text/plain");
        shareIntent.putExtra(Intent.EXTRA_SUBJECT, title);
        shareIntent.putExtra(Intent.EXTRA_TEXT, text);
        startActivity(Intent.createChooser(shareIntent, getString(R.string.table_share)));
    }

    private static String fmt(double v) {
        if (Double.isNaN(v) || Double.isInfinite(v)) return String.valueOf(v);
        if (Math.abs(v) < 1e15 && v == (long) v && Math.abs(v) <= Long.MAX_VALUE) {
            return String.format("%d", (long) v);
        }
        return String.format("%.10g", v);
    }

    private void toast(String msg) {
        Toast.makeText(this, msg, Toast.LENGTH_SHORT).show();
    }

    // Unit Converter
    private AutoCompleteTextView unitCategoryDropdown, unitFromDropdown, unitToDropdown;
    private EditText unitValueInput, unitResultInput;
    private ArrayAdapter<String> unitCategoryAdapter, unitFromAdapter, unitToAdapter;

    // Statistical Distribution Calculator
    private AutoCompleteTextView distTypeDropdown;
    private EditText distParamsInput, distXInput;
    private ArrayAdapter<String> distTypeAdapter;

    private void setupDistCalc() {
        distTypeDropdown = findViewById(R.id.dist_type_dropdown);
        distParamsInput = findViewById(R.id.dist_params_input);
        distXInput = findViewById(R.id.dist_x_input);

        String[] distNames = StatDistCalc.getDistributionNames(this);
        distTypeAdapter = new ArrayAdapter<>(this, android.R.layout.simple_dropdown_item_1line, distNames);
        distTypeDropdown.setAdapter(distTypeAdapter);
        distTypeDropdown.setText(distNames[0], false);

        distTypeDropdown.setOnItemClickListener((parent, view, position, id) -> {
            String name = distTypeAdapter.getItem(position);
            updateDistParams(name);
        });

        MaterialButton btnDistPdf = findViewById(R.id.btn_dist_pdf);
        MaterialButton btnDistCdf = findViewById(R.id.btn_dist_cdf);
        MaterialButton btnDistPpf = findViewById(R.id.btn_dist_ppf);
        MaterialButton btnDistPlot = findViewById(R.id.btn_dist_plot);

        btnDistPdf.setOnClickListener(v -> onDistCompute("pdf"));
        btnDistCdf.setOnClickListener(v -> onDistCompute("cdf"));
        btnDistPpf.setOnClickListener(v -> onDistCompute("ppf"));
        btnDistPlot.setOnClickListener(v -> onDistPlot());
    }

    private void updateDistParams(String name) {
        if (name.equals(getString(R.string.dist_normal))) { distParamsInput.setText("0, 1"); }
        else if (name.equals(getString(R.string.dist_t))) { distParamsInput.setText("5"); }
        else if (name.equals(getString(R.string.dist_chi2))) { distParamsInput.setText("3"); }
        else if (name.equals(getString(R.string.dist_f))) { distParamsInput.setText("5, 10"); }
        else if (name.equals(getString(R.string.dist_binomial))) { distParamsInput.setText("20, 0.5"); }
        else if (name.equals(getString(R.string.dist_poisson))) { distParamsInput.setText("5"); }
        else { distParamsInput.setText("0, 1"); }
    }

    private void onDistCompute(String mode) {
        String distName = distTypeDropdown.getText().toString();
        StatDistCalc.DistType type = StatDistCalc.fromName(this, distName);
        double[] params = parseParams(distParamsInput.getText().toString());
        if (params == null) {
            toast(getString(R.string.toast_invalid_params));
            return;
        }
        double x;
        try {
            x = Double.parseDouble(distXInput.getText().toString().trim());
        } catch (NumberFormatException e) {
            toast(getString(R.string.toast_invalid_x_value));
            return;
        }

        double result;
        String label;
        switch (mode) {
            case "pdf":
                result = StatDistCalc.pdf(type, x, params);
                label = "PDF";
                break;
            case "cdf":
                result = StatDistCalc.cdf(type, x, params);
                label = "CDF";
                break;
            case "ppf":
                // PPF: binary search for inverse CDF
                result = computePpf(type, x, params);
                label = "PPF";
                break;
            default:
                return;
        }
        if (Double.isNaN(result) || Double.isInfinite(result)) {
            appendResult(distName + " " + label + "(" + fmt(x) + ")", Double.NaN);
        } else {
            appendResult(distName + " " + label + "(" + fmt(x) + ")", result);
        }
    }

    private double computePpf(StatDistCalc.DistType type, double q, double[] params) {
        if (q <= 0 || q >= 1) return Double.NaN;
        double lo = -10.0, hi = 10.0;
        // Dynamically expand search range to cover the full distribution support
        while (StatDistCalc.cdf(type, lo, params) > q) lo *= 2;
        while (StatDistCalc.cdf(type, hi, params) < q) hi *= 2;
        for (int i = 0; i < 100; i++) {
            double mid = (lo + hi) / 2.0;
            if (StatDistCalc.cdf(type, mid, params) < q) lo = mid; else hi = mid;
        }
        return (lo + hi) / 2.0;
    }

    private void onDistPlot() {
        String distName = distTypeDropdown.getText().toString();
        StatDistCalc.DistType type = StatDistCalc.fromName(this, distName);
        double[] params = parseParams(distParamsInput.getText().toString());
        if (params == null) {
            toast(getString(R.string.toast_invalid_params));
            return;
        }

        double xMin, xMax;
        switch (type) {
            case NORMAL:
                double mu = params[0], sigma = Math.abs(params[1]);
                xMin = mu - 4 * sigma; xMax = mu + 4 * sigma;
                break;
            case T:
                xMin = -6; xMax = 6;
                break;
            case CHI2:
                double k = params[0];
                xMin = 0; xMax = Math.max(k + 4 * Math.sqrt(2 * k), 1);
                break;
            case F:
                xMin = 0.01; xMax = 10;
                break;
            case BINOMIAL:
                xMin = 0; xMax = params[0];
                break;
            case POISSON:
                double lam = params[0];
                xMin = 0; xMax = (int)(lam + 4 * Math.sqrt(lam)) + 1;
                break;
            default:
                xMin = -5; xMax = 5; break;
        }

        int n = 200;
        double step = (xMax - xMin) / (n - 1);
        float[] xs = new float[n];
        float[] ys = new float[n];
        for (int i = 0; i < n; i++) {
            double x = xMin + i * step;
            xs[i] = (float) x;
            ys[i] = (float) StatDistCalc.pdf(type, x, params);
        }

        // Plot using MPAndroidChart
        java.util.ArrayList<Entry> entries = new java.util.ArrayList<>();
        for (int i = 0; i < n; i++) {
            entries.add(new Entry(xs[i], ys[i]));
        }
        LineDataSet dataSet = new LineDataSet(entries, distName + " PDF");
        dataSet.setColor(0xFF89B4FA);
        dataSet.setDrawCircles(false);
        dataSet.setLineWidth(2f);
        dataSet.setDrawValues(false);
        LineData lineData = new LineData(dataSet);
        lineChart.setData(lineData);
        lineChart.getDescription().setText(distName + " Distribution");
        lineChart.getDescription().setTextColor(0xFFCDD6F4);
        lineChart.getAxisRight().setEnabled(false);
        XAxis xAxis = lineChart.getXAxis();
        xAxis.setPosition(XAxis.XAxisPosition.BOTTOM);
        xAxis.setTextColor(0xFFCDD6F4);
        xAxis.setGridColor(0xFF45475A);
        YAxis yAxis = lineChart.getAxisLeft();
        yAxis.setTextColor(0xFFCDD6F4);
        yAxis.setGridColor(0xFF45475A);
        lineChart.invalidate();
        graphCard.setVisibility(android.view.View.VISIBLE);
        toast(getString(R.string.toast_dist_plotted, distName));
    }

    private double[] parseParams(String text) {
        if (text == null || text.trim().isEmpty()) return null;
        String[] parts = text.trim().split(",");
        double[] result = new double[parts.length];
        try {
            for (int i = 0; i < parts.length; i++) {
                result[i] = Double.parseDouble(parts[i].trim());
            }
            return result;
        } catch (NumberFormatException e) {
            return null;
        }
    }

    private void setupBaseConverter() {
        EditText baseInput = findViewById(R.id.base_input);
        AutoCompleteTextView baseFromDropdown = findViewById(R.id.base_from_dropdown);
        MaterialButton btnBaseConvert = findViewById(R.id.btn_base_convert);
        TextView baseBinResult = findViewById(R.id.base_bin_result);
        TextView baseOctResult = findViewById(R.id.base_oct_result);
        TextView baseDecResult = findViewById(R.id.base_dec_result);
        TextView baseHexResult = findViewById(R.id.base_hex_result);

        String[] bases = {"2", "8", "10", "16"};
        ArrayAdapter<String> baseAdapter = new ArrayAdapter<>(this, android.R.layout.simple_dropdown_item_1line, bases);
        baseFromDropdown.setAdapter(baseAdapter);
        baseFromDropdown.setText("10", false);

        btnBaseConvert.setOnClickListener(v -> {
            String input = baseInput.getText().toString().trim();
            if (input.isEmpty()) {
                Toast.makeText(this, R.string.toast_base_invalid, Toast.LENGTH_SHORT).show();
                return;
            }
            int fromBase;
            try {
                fromBase = Integer.parseInt(baseFromDropdown.getText().toString());
            } catch (NumberFormatException e) {
                fromBase = 10;
            }

            try {
                long value = CalcEngine.baseToLong(input, fromBase);
                baseBinResult.setText(CalcEngine.longToBase(value, 2));
                baseOctResult.setText(CalcEngine.longToBase(value, 8));
                baseDecResult.setText(CalcEngine.longToBase(value, 10));
                baseHexResult.setText(CalcEngine.longToBase(value, 16));
            } catch (Exception e) {
                Toast.makeText(this, R.string.toast_base_invalid, Toast.LENGTH_SHORT).show();
                baseBinResult.setText("");
                baseOctResult.setText("");
                baseDecResult.setText("");
                baseHexResult.setText("");
            }
        });
    }

    private void setupUnitConverter() {
        unitCategoryDropdown = findViewById(R.id.unit_category_dropdown);
        unitFromDropdown = findViewById(R.id.unit_from_dropdown);
        unitToDropdown = findViewById(R.id.unit_to_dropdown);
        unitValueInput = findViewById(R.id.unit_value_input);
        unitResultInput = findViewById(R.id.unit_result_input);

        // Category adapter
        java.util.List<String> categories = new java.util.ArrayList<>(UNIT_DATA.keySet());
        unitCategoryAdapter = new ArrayAdapter<>(this, android.R.layout.simple_dropdown_item_1line, categories);
        unitCategoryDropdown.setAdapter(unitCategoryAdapter);
        unitCategoryDropdown.setText(categories.get(0), false);

        // From/To adapters — populated based on selected category
        unitFromAdapter = new ArrayAdapter<>(this, android.R.layout.simple_dropdown_item_1line, new java.util.ArrayList<>());
        unitToAdapter = new ArrayAdapter<>(this, android.R.layout.simple_dropdown_item_1line, new java.util.ArrayList<>());
        unitFromDropdown.setAdapter(unitFromAdapter);
        unitToDropdown.setAdapter(unitToAdapter);

        // Refresh from/to when category changes
        unitCategoryDropdown.setOnItemClickListener((parent, view, position, id) -> {
            String cat = unitCategoryAdapter.getItem(position);
            updateUnitDropdowns(cat);
        });

        // Initialize from/to for default category
        updateUnitDropdowns(categories.get(0));

        MaterialButton btnUnitConvert = findViewById(R.id.btn_unit_convert);
        btnUnitConvert.setOnClickListener(v -> onUnitConvert());
    }

    private void updateUnitDropdowns(String category) {
        java.util.Map<String, Double> units = UNIT_DATA.get(category);
        if (units == null) return;
        java.util.List<String> unitNames = new java.util.ArrayList<>(units.keySet());
        unitFromAdapter.clear();
        unitFromAdapter.addAll(unitNames);
        unitToAdapter.clear();
        unitToAdapter.addAll(unitNames);
        unitFromDropdown.setText(unitNames.get(0), false);
        unitToDropdown.setText(unitNames.size() > 1 ? unitNames.get(1) : unitNames.get(0), false);
    }

    private static final java.util.Map<String, java.util.Map<String, Double>> UNIT_DATA = new java.util.HashMap<>();
    static {
        // Length
        java.util.Map<String, Double> length = new java.util.HashMap<>();
        length.put("Meter (m)", 1.0);
        length.put("Kilometer (km)", 1000.0);
        length.put("Centimeter (cm)", 0.01);
        length.put("Millimeter (mm)", 0.001);
        length.put("Mile (mi)", 1609.344);
        length.put("Yard (yd)", 0.9144);
        length.put("Foot (ft)", 0.3048);
        length.put("Inch (in)", 0.0254);
        length.put("Nautical Mile (nmi)", 1852.0);
        UNIT_DATA.put("Length", length);

        // Weight
        java.util.Map<String, Double> weight = new java.util.HashMap<>();
        weight.put("Kilogram (kg)", 1.0);
        weight.put("Gram (g)", 0.001);
        weight.put("Milligram (mg)", 0.000001);
        weight.put("Metric Ton (t)", 1000.0);
        weight.put("Pound (lb)", 0.45359237);
        weight.put("Ounce (oz)", 0.028349523125);
        UNIT_DATA.put("Weight", weight);

        // Area
        java.util.Map<String, Double> area = new java.util.HashMap<>();
        area.put("Square Meter (m²)", 1.0);
        area.put("Square Kilometer (km²)", 1000000.0);
        area.put("Hectare (ha)", 10000.0);
        area.put("Acre (ac)", 4046.8564224);
        area.put("Square Foot (ft²)", 0.09290304);
        area.put("Square Inch (in²)", 0.00064516);
        area.put("Square Mile (mi²)", 2589988.110336);
        UNIT_DATA.put("Area", area);

        // Volume
        java.util.Map<String, Double> volume = new java.util.HashMap<>();
        volume.put("Liter (L)", 1.0);
        volume.put("Milliliter (mL)", 0.001);
        volume.put("Cubic Meter (m³)", 1000.0);
        volume.put("Gallon (US)", 3.785411784);
        volume.put("Quart (US)", 0.946352946);
        volume.put("Pint (US)", 0.473176473);
        volume.put("Cup (US)", 0.2365882365);
        volume.put("Fluid Ounce (US)", 0.0295735295625);
        volume.put("Cubic Centimeter (cm³)", 0.001);
        UNIT_DATA.put("Volume", volume);

        // Time
        java.util.Map<String, Double> time = new java.util.HashMap<>();
        time.put("Second (s)", 1.0);
        time.put("Minute (min)", 60.0);
        time.put("Hour (h)", 3600.0);
        time.put("Day (d)", 86400.0);
        time.put("Week (wk)", 604800.0);
        time.put("Month (30 days)", 2592000.0);
        time.put("Year (365 days)", 31536000.0);
        UNIT_DATA.put("Time", time);

        // Data Storage
        java.util.Map<String, Double> data = new java.util.HashMap<>();
        data.put("Byte (B)", 1.0);
        data.put("Kilobyte (KB)", 1024.0);
        data.put("Megabyte (MB)", 1048576.0);
        data.put("Gigabyte (GB)", 1073741824.0);
        data.put("Terabyte (TB)", 1099511627776.0);
        data.put("Bit", 0.125);
        data.put("Kilobit (Kbit)", 128.0);
        data.put("Megabit (Mbit)", 131072.0);
        data.put("Gigabit (Gbit)", 134217728.0);
        UNIT_DATA.put("Data Storage", data);

        // Speed
        java.util.Map<String, Double> speed = new java.util.HashMap<>();
        speed.put("Meter/second (m/s)", 1.0);
        speed.put("Kilometer/hour (km/h)", 0.2777777778);
        speed.put("Mile/hour (mph)", 0.44704);
        speed.put("Knot (kn)", 0.5144444444);
        speed.put("Foot/second (ft/s)", 0.3048);
        speed.put("Mach (at sea level)", 340.29);
        UNIT_DATA.put("Speed", speed);

        // Angle
        java.util.Map<String, Double> angle = new java.util.HashMap<>();
        angle.put("Degree (°)", 1.0);
        angle.put("Radian (rad)", 57.29577951308232);
        angle.put("Gradian (grad)", 0.9);
        angle.put("Arcminute (')", 1.0/60.0);
        angle.put("Arcsecond (\")", 1.0/3600.0);
        UNIT_DATA.put("Angle", angle);

        // Temperature (dummy factors — actual conversion handled by convertTemperature)
        java.util.Map<String, Double> temperature = new java.util.HashMap<>();
        temperature.put("Celsius (°C)", 1.0);
        temperature.put("Fahrenheit (°F)", 1.0);
        temperature.put("Kelvin (K)", 1.0);
        UNIT_DATA.put("Temperature", temperature);
    }

    private void onUnitConvert() {
        String category = unitCategoryDropdown.getText().toString().trim();
        String fromUnit = unitFromDropdown.getText().toString().trim();
        String toUnit = unitToDropdown.getText().toString().trim();
        String valueStr = unitValueInput.getText().toString().trim();

        if (category.isEmpty() || fromUnit.isEmpty() || toUnit.isEmpty()) {
            toast(getString(R.string.toast_fill_fields));
            return;
        }

        double value;
        try {
            value = Double.parseDouble(valueStr);
        } catch (NumberFormatException e) {
            toast(getString(R.string.toast_invalid_value));
            return;
        }

        java.util.Map<String, Double> units = UNIT_DATA.get(category);
        if (units == null) {
            toast(getString(R.string.toast_unknown_category, category));
            return;
        }

        Double fromFactor = units.get(fromUnit);
        Double toFactor = units.get(toUnit);
        if (fromFactor == null || toFactor == null) {
            toast(getString(R.string.toast_invalid_unit));
            return;
        }

        double result;
        if ("Temperature".equals(category)) {
            result = convertTemperature(value, fromUnit, toUnit);
        } else {
            result = value * fromFactor / toFactor;
        }

        unitResultInput.setText(fmt(result));
        resultView.append(value + " " + fromUnit + " = " + fmt(result) + " " + toUnit + "\n");
    }

    private double convertTemperature(double value, String from, String to) {
        if (from.equals(to)) return value;
        double celsius;
        if (from.contains("Fahrenheit")) {
            celsius = (value - 32) * 5.0 / 9.0;
        } else if (from.contains("Kelvin")) {
            celsius = value - 273.15;
        } else {
            celsius = value;
        }
        if (to.contains("Fahrenheit")) {
            return celsius * 9.0 / 5.0 + 32;
        } else if (to.contains("Kelvin")) {
            return celsius + 273.15;
        } else {
            return celsius;
        }
    }

    // ------------------------------------------------------------------
    //  Perpetual Calendar / Date Calculator
    // ------------------------------------------------------------------
    private EditText calDate1Input, calDate2Input, calDaysInput;
    private TextView calResultView;

    private void setupCalendar() {
        calDate1Input = findViewById(R.id.cal_date1_input);
        calDate2Input = findViewById(R.id.cal_date2_input);
        calDaysInput = findViewById(R.id.cal_days_input);
        calResultView = findViewById(R.id.cal_result_view);

        MaterialButton btnToday = findViewById(R.id.btn_cal_today);
        btnToday.setOnClickListener(v -> onCalToday());

        MaterialButton btnDow = findViewById(R.id.btn_cal_dow);
        btnDow.setOnClickListener(v -> onCalDayOfWeek());

        MaterialButton btnDiff = findViewById(R.id.btn_cal_diff);
        btnDiff.setOnClickListener(v -> onCalDiff());

        MaterialButton btnAdd = findViewById(R.id.btn_cal_add);
        btnAdd.setOnClickListener(v -> onCalAddDays());
    }

    private LocalDate calParseDate(String text) {
        if (text == null) return null;
        String s = text.trim();
        if (s.isEmpty()) return null;
        try {
            return LocalDate.parse(s);
        } catch (Exception e) {
            return null;
        }
    }

    private void onCalToday() {
        calDate1Input.setText(LocalDate.now().toString());
    }

    private void onCalDayOfWeek() {
        LocalDate d = calParseDate(calDate1Input.getText().toString());
        if (d == null) {
            toast(getString(R.string.toast_cal_invalid_date));
            return;
        }
        String[] daysEn = {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"};
        String[] daysZh = {"一", "二", "三", "四", "五", "六", "日"};
        int dow = d.getDayOfWeek().getValue() - 1;
        boolean isZh = getResources().getConfiguration().locale.getLanguage().equals("zh");
        String dowStr = isZh ? daysZh[dow] : daysEn[dow];
        String msg = isZh
            ? d.getYear() + "年" + d.getMonthValue() + "月" + d.getDayOfMonth() + "日是星期" + dowStr
            : d + getString(R.string.cal_is_a) + dowStr;
        calResultView.setText(msg);
    }

    private void onCalDiff() {
        LocalDate d1 = calParseDate(calDate1Input.getText().toString());
        LocalDate d2 = calParseDate(calDate2Input.getText().toString());
        if (d1 == null || d2 == null) {
            toast(getString(R.string.toast_cal_invalid_date));
            return;
        }
        long diff = ChronoUnit.DAYS.between(d1, d2);
        calResultView.setText(String.format(getString(R.string.cal_days_between), diff));
    }

    private void onCalAddDays() {
        LocalDate d = calParseDate(calDate1Input.getText().toString());
        if (d == null) {
            toast(getString(R.string.toast_cal_invalid_date));
            return;
        }
        int add;
        try {
            add = Integer.parseInt(calDaysInput.getText().toString().trim());
        } catch (NumberFormatException e) {
            toast(getString(R.string.toast_cal_invalid_input));
            return;
        }
        LocalDate result = d.plusDays(add);
        calDate2Input.setText(result.toString());
        boolean isZh = getResources().getConfiguration().locale.getLanguage().equals("zh");
        String msg = isZh
            ? d.toString() + " 加 " + add + " 天 = " + result
            : d + " + " + String.format(getString(R.string.cal_days_added), add, result.toString());
        calResultView.setText(msg);
    }

    // ------------------------------------------------------------------
    //  Probability Calculator
    // ------------------------------------------------------------------
    private EditText probNInput, probRInput, probPInput;
    private EditText probPbaInput, probPaInput, probPbnaInput;
    private EditText probPbInput, probPabInput;
    private TextView probResultView;

    private void setupProbability() {
        probNInput = findViewById(R.id.prob_n_input);
        probRInput = findViewById(R.id.prob_r_input);
        probPInput = findViewById(R.id.prob_p_input);
        probPbaInput = findViewById(R.id.prob_pba_input);
        probPaInput = findViewById(R.id.prob_pa_input);
        probPbnaInput = findViewById(R.id.prob_pbna_input);
        probPbInput = findViewById(R.id.prob_pb_input);
        probPabInput = findViewById(R.id.prob_pab_input);
        probResultView = findViewById(R.id.prob_result_view);

        MaterialButton btnCombo = findViewById(R.id.btn_prob_combo);
        btnCombo.setOnClickListener(v -> onProbCombo());

        MaterialButton btnPerm = findViewById(R.id.btn_prob_perm);
        btnPerm.setOnClickListener(v -> onProbPerm());

        MaterialButton btnBayes = findViewById(R.id.btn_prob_bayes);
        btnBayes.setOnClickListener(v -> onProbBayes());

        MaterialButton btnBinom = findViewById(R.id.btn_prob_binom);
        btnBinom.setOnClickListener(v -> onProbBinom());

        MaterialButton btnUnion = findViewById(R.id.btn_prob_union);
        btnUnion.setOnClickListener(v -> onProbUnion());

        MaterialButton btnIntersect = findViewById(R.id.btn_prob_intersect);
        btnIntersect.setOnClickListener(v -> onProbIntersect());

        MaterialButton btnComplement = findViewById(R.id.btn_prob_complement);
        btnComplement.setOnClickListener(v -> onProbComplement());

        MaterialButton btnConditional = findViewById(R.id.btn_prob_conditional);
        btnConditional.setOnClickListener(v -> onProbConditional());
    }

    private long probParseLong(EditText e) {
        return Long.parseLong(e.getText().toString().trim());
    }

    private double probParseDouble(EditText e) {
        return Double.parseDouble(e.getText().toString().trim());
    }

    private void onProbCombo() {
        try {
            long n = probParseLong(probNInput);
            long r = probParseLong(probRInput);
            if (r > n) { toast(getString(R.string.prob_r_gt_n)); return; }
            long result = comb(n, r);
            probResultView.setText(String.format(getString(R.string.prob_result_combo), n, r, result));
        } catch (Exception ex) { toast(getString(R.string.prob_invalid_input)); }
    }

    private void onProbPerm() {
        try {
            long n = probParseLong(probNInput);
            long r = probParseLong(probRInput);
            if (r > n) { toast(getString(R.string.prob_r_gt_n)); return; }
            long result = perm(n, r);
            probResultView.setText(String.format(getString(R.string.prob_result_perm), n, r, result));
        } catch (Exception ex) { toast(getString(R.string.prob_invalid_input)); }
    }

    private void onProbUnion() {
        try {
            double pa = probParseDouble(probPaInput);
            double pb = probParseDouble(probPbInput);
            double pab = probParseDouble(probPabInput);
            double result = Math.max(0, Math.min(1, pa + pb - pab));
            probResultView.setText(String.format(getString(R.string.prob_result_union), result));
        } catch (Exception ex) { toast(getString(R.string.prob_invalid_input)); }
    }

    private void onProbIntersect() {
        try {
            double pa = probParseDouble(probPaInput);
            double pb = probParseDouble(probPbInput);
            double result = pa * pb;
            probResultView.setText(String.format(getString(R.string.prob_result_intersect), result));
        } catch (Exception ex) { toast(getString(R.string.prob_invalid_input)); }
    }

    private void onProbComplement() {
        try {
            double pa = probParseDouble(probPaInput);
            double result = 1.0 - pa;
            probResultView.setText(String.format(getString(R.string.prob_result_complement), result));
        } catch (Exception ex) { toast(getString(R.string.prob_invalid_input)); }
    }

    private void onProbConditional() {
        try {
            double pab = probParseDouble(probPabInput);
            double pb = probParseDouble(probPbInput);
            if (pb == 0) { toast(getString(R.string.prob_pb_zero)); return; }
            double result = pab / pb;
            probResultView.setText(String.format(getString(R.string.prob_result_conditional), result));
        } catch (Exception ex) { toast(getString(R.string.prob_invalid_input)); }
    }

    private void onProbBayes() {
        try {
            double pba = probParseDouble(probPbaInput);
            double pa = probParseDouble(probPaInput);
            double pbna = probParseDouble(probPbnaInput);
            double pNotA = 1.0 - pa;
            double pB = pba * pa + pbna * pNotA;
            if (pB == 0) { toast(getString(R.string.prob_pb_zero)); return; }
            double pAB = (pba * pa) / pB;
            probResultView.setText(String.format(getString(R.string.prob_result_bayes), pAB, pba, pa));
        } catch (Exception ex) { toast(getString(R.string.prob_invalid_input)); }
    }

    private void onProbBinom() {
        try {
            long n = probParseLong(probNInput);
            long k = probParseLong(probRInput);
            double p = probParseDouble(probPInput);
            if (k > n) { toast(getString(R.string.prob_r_gt_n)); return; }
            double result = binomialPMF(n, k, p);
            probResultView.setText(String.format(getString(R.string.prob_result_binom), k, result, n, p));
        } catch (Exception ex) { toast(getString(R.string.prob_invalid_input)); }
    }

    private long comb(long n, long r) {
        if (r > n) return 0;
        if (r == 0 || r == n) return 1;
        if (r > n - r) r = n - r;
        // Use BigInteger to avoid overflow
        java.math.BigInteger result = java.math.BigInteger.ONE;
        for (long i = 0; i < r; i++) {
            result = result.multiply(java.math.BigInteger.valueOf(n - i));
            result = result.divide(java.math.BigInteger.valueOf(i + 1));
        }
        try {
            return result.longValueExact();
        } catch (ArithmeticException e) {
            // Result too large for long
            return Long.MAX_VALUE;
        }
    }

    private long perm(long n, long r) {
        if (r > n) return 0;
        java.math.BigInteger result = java.math.BigInteger.ONE;
        for (long i = 0; i < r; i++) {
            result = result.multiply(java.math.BigInteger.valueOf(n - i));
        }
        try {
            return result.longValueExact();
        } catch (ArithmeticException e) {
            return Long.MAX_VALUE;
        }
    }

    private double binomialPMF(long n, long k, double p) {
        return comb(n, k) * Math.pow(p, k) * Math.pow(1 - p, n - k);
    }

    // ------------------------------------------------------------------
    //  Finance Calculator
    // ------------------------------------------------------------------
    private EditText finPrincipalInput, finRateInput, finMonthsInput;
    private EditText finYearsInput, finFlowsInput;
    private TextView finResultView;

    private void setupFinance() {
        finPrincipalInput = findViewById(R.id.fin_principal_input);
        finRateInput = findViewById(R.id.fin_rate_input);
        finMonthsInput = findViewById(R.id.fin_months_input);
        finYearsInput = findViewById(R.id.fin_years_input);
        finFlowsInput = findViewById(R.id.fin_flows_input);
        finResultView = findViewById(R.id.fin_result_view);

        MaterialButton btnLoan = findViewById(R.id.btn_fin_loan);
        btnLoan.setOnClickListener(v -> onFinLoan());

        MaterialButton btnFv = findViewById(R.id.btn_fin_fv);
        btnFv.setOnClickListener(v -> onFinFV());

        MaterialButton btnPv = findViewById(R.id.btn_fin_pv);
        btnPv.setOnClickListener(v -> onFinPV());

        MaterialButton btnNpv = findViewById(R.id.btn_fin_npv);
        btnNpv.setOnClickListener(v -> onFinNPV());

        MaterialButton btnIrr = findViewById(R.id.btn_fin_irr);
        btnIrr.setOnClickListener(v -> onFinIRR());

        MaterialButton btnDepr = findViewById(R.id.btn_fin_depr);
        btnDepr.setOnClickListener(v -> onFinDepr());

        MaterialButton btnBond = findViewById(R.id.btn_fin_bond);
        btnBond.setOnClickListener(v -> onFinBond());

        MaterialButton btnRetire = findViewById(R.id.btn_fin_retire);
        btnRetire.setOnClickListener(v -> onFinRetire());
    }

    private void onFinLoan() {
        try {
            double principal = Double.parseDouble(finPrincipalInput.getText().toString().trim());
            double rate = Double.parseDouble(finRateInput.getText().toString().trim());
            int months = Integer.parseInt(finMonthsInput.getText().toString().trim());
            if (principal <= 0 || months <= 0) { toast(getString(R.string.fin_invalid_input)); return; }
            double r = rate / 100.0 / 12.0;
            double pmt;
            if (rate == 0) {
                pmt = principal / months;
            } else {
                double factor = Math.pow(1 + r, months);
                pmt = principal * r * factor / (factor - 1);
            }
            double total = pmt * months;
            double interest = total - principal;
            finResultView.setText(String.format(getString(R.string.fin_result_loan), pmt, total, interest));
        } catch (Exception ex) { toast(getString(R.string.fin_invalid_input)); }
    }

    private void onFinFV() {
        try {
            double pv = Double.parseDouble(finPrincipalInput.getText().toString().trim());
            double rate = Double.parseDouble(finRateInput.getText().toString().trim());
            int years = Integer.parseInt(finYearsInput.getText().toString().trim());
            int n = 12;
            try { n = Integer.parseInt(finMonthsInput.getText().toString().trim()); } catch (Exception ignored) {}
            if (pv <= 0 || years < 0 || n <= 0) { toast(getString(R.string.fin_invalid_input)); return; }
            double r = rate / 100.0;
            double fv = pv * Math.pow(1 + r / n, n * years);
            finResultView.setText(String.format(getString(R.string.fin_result_fv), fv));
        } catch (Exception ex) { toast(getString(R.string.fin_invalid_input)); }
    }

    private void onFinPV() {
        try {
            double fv = Double.parseDouble(finPrincipalInput.getText().toString().trim());
            double rate = Double.parseDouble(finRateInput.getText().toString().trim());
            int years = Integer.parseInt(finYearsInput.getText().toString().trim());
            int n = 12;
            try { n = Integer.parseInt(finMonthsInput.getText().toString().trim()); } catch (Exception ignored) {}
            if (fv <= 0 || years < 0 || n <= 0) { toast(getString(R.string.fin_invalid_input)); return; }
            double r = rate / 100.0;
            double pv = fv / Math.pow(1 + r / n, n * years);
            finResultView.setText(String.format(getString(R.string.fin_result_pv), pv));
        } catch (Exception ex) { toast(getString(R.string.fin_invalid_input)); }
    }

    private void onFinNPV() {
        try {
            double rate = Double.parseDouble(finRateInput.getText().toString().trim());
            String flowsStr = finFlowsInput.getText().toString().trim();
            String[] parts = flowsStr.split(",");
            if (parts.length < 2) { toast(getString(R.string.fin_invalid_flows)); return; }
            double r = rate / 100.0;
            double npv = 0;
            for (int t = 0; t < parts.length; t++) {
                double cf = Double.parseDouble(parts[t].trim());
                npv += cf / Math.pow(1 + r, t);
            }
            finResultView.setText(String.format(getString(R.string.fin_result_npv), npv));
        } catch (Exception ex) { toast(getString(R.string.fin_invalid_input)); }
    }

    private void onFinIRR() {
        try {
            String flowsStr = finFlowsInput.getText().toString().trim();
            String[] parts = flowsStr.split(",");
            if (parts.length < 2) { toast(getString(R.string.fin_invalid_flows)); return; }
            double[] cf = new double[parts.length];
            for (int i = 0; i < parts.length; i++) {
                cf[i] = Double.parseDouble(parts[i].trim());
            }
            // Newton-Raphson
            double r = 0.1;
            for (int iter = 0; iter < 200; iter++) {
                double pv = 0, dpv = 0;
                for (int t = 0; t < cf.length; t++) {
                    pv += cf[t] / Math.pow(1 + r, t);
                    if (t > 0) dpv += -t * cf[t] / Math.pow(1 + r, t + 1);
                }
                if (Math.abs(dpv) < 1e-18) break;
                double rNew = r - pv / dpv;
                if (Math.abs(rNew - r) < 1e-10) { r = rNew; break; }
                r = rNew;
            }
            double irr = r * 100;
            finResultView.setText(String.format(getString(R.string.fin_result_irr), irr));
        } catch (Exception ex) { toast(getString(R.string.fin_invalid_input)); }
    }

    private void onFinDepr() {
        try {
            double cost = Double.parseDouble(finPrincipalInput.getText().toString().trim());
            double salvage = Double.parseDouble(finRateInput.getText().toString().trim());
            int life = Integer.parseInt(finYearsInput.getText().toString().trim());
            if (cost <= 0 || salvage < 0 || life <= 0 || salvage >= cost) {
                toast(getString(R.string.fin_depr_invalid)); return;
            }
            double annual = (cost - salvage) / life;
            double monthly = annual / 12;
            finResultView.setText(String.format(getString(R.string.fin_result_depr), annual, monthly));
        } catch (Exception ex) { toast(getString(R.string.fin_invalid_input)); }
    }

    private void onFinBond() {
        try {
            double face = Double.parseDouble(finPrincipalInput.getText().toString().trim());
            double coupon = Double.parseDouble(finRateInput.getText().toString().trim());
            double yld = Double.parseDouble(finYearsInput.getText().toString().trim());
            int years = Integer.parseInt(finMonthsInput.getText().toString().trim());
            if (face <= 0 || years <= 0) { toast(getString(R.string.fin_invalid_input)); return; }
            int m = 2;
            double c = face * coupon / 100.0 / m;
            double y = yld / 100.0 / m;
            int n = years * m;
            double pvCoupons = 0;
            for (int t = 1; t <= n; t++) {
                pvCoupons += c / Math.pow(1 + y, t);
            }
            double pvFace = face / Math.pow(1 + y, n);
            double price = pvCoupons + pvFace;
            finResultView.setText(String.format(getString(R.string.fin_result_bond), price));
        } catch (Exception ex) { toast(getString(R.string.fin_invalid_input)); }
    }

    private void onFinRetire() {
        try {
            double monthly = Double.parseDouble(finPrincipalInput.getText().toString().trim());
            double rate = Double.parseDouble(finRateInput.getText().toString().trim());
            int years = Integer.parseInt(finYearsInput.getText().toString().trim());
            double current = 0;
            try { current = Double.parseDouble(finMonthsInput.getText().toString().trim()); } catch (Exception ignored) {}
            if (monthly < 0 || years <= 0) { toast(getString(R.string.fin_invalid_input)); return; }
            double r = rate / 100.0 / 12;
            int n = years * 12;
            double fv;
            if (r == 0) {
                fv = current + monthly * n;
            } else {
                double factor = Math.pow(1 + r, n);
                fv = current * factor + monthly * (factor - 1) / r;
            }
            double contributions = current + monthly * n;
            double interest = fv - contributions;
            finResultView.setText(String.format(getString(R.string.fin_result_retire), fv, contributions, interest));
        } catch (Exception ex) { toast(getString(R.string.fin_invalid_input)); }
    }

    // ------------------------------------------------------------------
    //  Number Theory Calculator
    // ------------------------------------------------------------------
    private boolean ntIsPrime(long n) {
        if (n < 2) return false;
        if (n < 4) return true;
        if (n % 2 == 0 || n % 3 == 0) return false;
        long i = 5;
        while (i * i <= n) {
            if (n % i == 0 || n % (i + 2) == 0) return false;
            i += 6;
        }
        return true;
    }

    private String ntFactorize(long n) {
        if (n <= 1) return String.valueOf(n);
        java.util.List<String> parts = new java.util.ArrayList<>();
        long d = 2;
        while (d * d <= n) {
            int count = 0;
            while (n % d == 0) {
                count++;
                n /= d;
            }
            if (count > 0) {
                if (count == 1) parts.add(String.valueOf(d));
                else parts.add(d + "^" + count);
            }
            d++;
        }
        if (n > 1) parts.add(String.valueOf(n));
        return String.join(" × ", parts);
    }

    private long ntGcd(long a, long b) {
        a = Math.abs(a);
        b = Math.abs(b);
        while (b != 0) {
            long t = b;
            b = a % b;
            a = t;
        }
        return a;
    }

    private long ntLcm(long a, long b) {
        if (a == 0 || b == 0) return 0;
        return Math.abs(a / ntGcd(a, b) * b);
    }

    private long ntFibonacci(int n) {
        if (n <= 0) return 0;
        if (n == 1) return 1;
        if (n == 2) return 1;
        long a = 1, b = 1;
        for (int i = 3; i <= n; i++) {
            long t = a + b;
            a = b;
            b = t;
        }
        return b;
    }

    private long ntModPow(long base, long exp, long mod) {
        if (mod <= 0) throw new ArithmeticException("mod must be positive");
        if (mod == 1) return 0;
        
        // Handle negative exponents
        if (exp < 0) {
            // Compute modular inverse first
            long inv = ntModInverse(base, mod);
            if (inv == 0) throw new ArithmeticException("No modular inverse exists");
            base = inv;
            exp = -exp;
        }
        
        long result = 1;
        base = base % mod;
        while (exp > 0) {
            if ((exp & 1) == 1) {
                // Use BigInteger to avoid overflow
                result = java.math.BigInteger.valueOf(result)
                    .multiply(java.math.BigInteger.valueOf(base))
                    .mod(java.math.BigInteger.valueOf(mod))
                    .longValue();
            }
            exp >>= 1;
            base = java.math.BigInteger.valueOf(base)
                .multiply(java.math.BigInteger.valueOf(base))
                .mod(java.math.BigInteger.valueOf(mod))
                .longValue();
        }
        return result;
    }
    
    private long ntModInverse(long a, long m) {
        // Extended Euclidean Algorithm
        long m0 = m;
        long y = 0, x = 1;
        
        if (m == 1) return 0;
        
        a = a % m;
        if (a < 0) a += m;
        
        while (a > 1) {
            long q = a / m;
            long t = m;
            m = a % m;
            a = t;
            t = y;
            y = x - q * y;
            x = t;
        }
        
        if (a != 1) return 0; // No modular inverse exists
        
        if (x < 0) x += m0;
        
        return x;
    }

    private long ntTotient(long n) {
        if (n <= 0) return 0;
        long result = n;
        long temp = n;
        for (long p = 2; p * p <= temp; p++) {
            if (temp % p == 0) {
                while (temp % p == 0) temp /= p;
                result -= result / p;
            }
        }
        if (temp > 1) result -= result / temp;
        return result;
    }

    private void onNtFactorize(EditText nInput) {
        long n;
        try { n = Long.parseLong(nInput.getText().toString().trim()); }
        catch (NumberFormatException e) { toast(getString(R.string.toast_nt_invalid_n)); return; }
        if (n <= 0) { toast(getString(R.string.toast_nt_invalid_n)); return; }
        if (n > 1_000_000_000_000L) { toast(getString(R.string.toast_nt_n_too_large)); return; }
        String result = ntFactorize(n);
        resultView.append(String.format(getString(R.string.nt_factorize_result), n, result) + "\n");
    }

    private void onNtIsPrime(EditText nInput) {
        long n;
        try { n = Long.parseLong(nInput.getText().toString().trim()); }
        catch (NumberFormatException e) { toast(getString(R.string.toast_nt_invalid_n)); return; }
        if (n <= 0) { toast(getString(R.string.toast_nt_invalid_n)); return; }
        if (ntIsPrime(n)) {
            resultView.append(String.format(getString(R.string.nt_prime_result), n) + "\n");
        } else {
            resultView.append(String.format(getString(R.string.nt_composite_result), n, ntFactorize(n)) + "\n");
        }
    }

    private void onNtGcd(EditText aInput, EditText bInput) {
        long a, b;
        try {
            a = Long.parseLong(aInput.getText().toString().trim());
            b = Long.parseLong(bInput.getText().toString().trim());
        } catch (NumberFormatException e) { toast(getString(R.string.toast_nt_invalid_ab)); return; }
        resultView.append(String.format(getString(R.string.nt_gcd_result), a, b, ntGcd(a, b)) + "\n");
    }

    private void onNtLcm(EditText aInput, EditText bInput) {
        long a, b;
        try {
            a = Long.parseLong(aInput.getText().toString().trim());
            b = Long.parseLong(bInput.getText().toString().trim());
        } catch (NumberFormatException e) { toast(getString(R.string.toast_nt_invalid_ab)); return; }
        resultView.append(String.format(getString(R.string.nt_lcm_result), a, b, ntLcm(a, b)) + "\n");
    }

    private void onNtFibonacci(EditText nInput) {
        int n;
        try { n = Integer.parseInt(nInput.getText().toString().trim()); }
        catch (NumberFormatException e) { toast(getString(R.string.toast_nt_invalid_n)); return; }
        if (n <= 0 || n > 1000) { toast(getString(R.string.toast_nt_invalid_n)); return; }
        StringBuilder sb = new StringBuilder(String.format(getString(R.string.nt_fibonacci_result), n, ntFibonacci(n)) + ":\n");
        for (int i = 1; i <= Math.min(n, 20); i++) {
            sb.append("F(").append(i).append(") = ").append(ntFibonacci(i));
            if (i < Math.min(n, 20)) sb.append("\n");
        }
        if (n > 20) sb.append("\n").append(String.format(getString(R.string.nt_factorize_showing), n));
        resultView.append(sb.toString() + "\n");
    }

    private void onNtModPow(EditText baseInput, EditText expInput, EditText modInput) {
        long base, exp, mod;
        try {
            base = Long.parseLong(baseInput.getText().toString().trim());
            exp = Long.parseLong(expInput.getText().toString().trim());
            mod = Long.parseLong(modInput.getText().toString().trim());
        } catch (NumberFormatException e) { toast(getString(R.string.toast_nt_invalid_modpow)); return; }
        if (mod <= 0) { toast(getString(R.string.toast_nt_invalid_modpow)); return; }
        long result = ntModPow(base, exp, mod);
        resultView.append(String.format(getString(R.string.nt_modpow_result), base, exp, mod, result) + "\n");
    }

    private void onNtTotient(EditText nInput) {
        long n;
        try { n = Long.parseLong(nInput.getText().toString().trim()); }
        catch (NumberFormatException e) { toast(getString(R.string.toast_nt_invalid_n)); return; }
        if (n <= 0) { toast(getString(R.string.toast_nt_invalid_n)); return; }
        resultView.append(String.format(getString(R.string.nt_totient_result), n, ntTotient(n)) + "\n");
    }

    // ------------------------------------------------------------------
    //  Bitwise Operations Calculator
    // ------------------------------------------------------------------
    private int bwMask(int val, int width) {
        if (width >= 32) return val;
        int mask = (1 << width) - 1;
        return val & mask;
    }

    private int bwToSigned(int val, int width) {
        if (width >= 32) return val;
        int bit = width - 1;
        if ((val & (1 << bit)) != 0) {
            return val - (1 << width);
        }
        return val;
    }

    private String bwToBinPadded(int val, int width) {
        return String.format("%" + width + "s", Integer.toBinaryString(bwMask(val, width))).replace(' ', '0');
    }

    private void onBitwiseCalc(EditText aInput, EditText bInput, AutoCompleteTextView opDropdown,
                                AutoCompleteTextView widthDropdown, TextView resBin,
                                TextView resHex, TextView resOct, TextView resDec) {
        int a, b = 0, width;
        try {
            a = Integer.parseInt(aInput.getText().toString().trim());
            width = Integer.parseInt(widthDropdown.getText().toString().trim());
        } catch (NumberFormatException e) {
            toast(getString(R.string.bitwise_error));
            return;
        }

        String op = opDropdown.getText().toString().trim();
        if (!op.equals("NOT")) {
            try {
                b = Integer.parseInt(bInput.getText().toString().trim());
            } catch (NumberFormatException e) {
                toast(getString(R.string.bitwise_error));
                return;
            }
        }

        int aMasked = bwMask(a, width);
        int bMasked = op.equals("NOT") ? 0 : bwMask(b, width);
        int mask = width >= 32 ? -1 : (1 << width) - 1;
        int result;

        switch (op) {
            case "AND":  result = aMasked & bMasked; break;
            case "OR":   result = aMasked | bMasked; break;
            case "XOR":  result = aMasked ^ bMasked; break;
            case "NOT":  result = (~aMasked) & mask; break;
            case "<<":   result = (aMasked << (bMasked % width)) & mask; break;
            case ">>":   result = aMasked >>> (bMasked % width); break;
            default:     result = 0;
        }

        resBin.setText(bwToBinPadded(result, width));
        resHex.setText(String.format("%X", bwMask(result, width)));
        resOct.setText(String.format("%o", bwMask(result, width)));
        resDec.setText(String.valueOf(bwToSigned(result, width)));
        resultView.append(String.format(getString(R.string.bitwise_result_fmt), op, aInput.getText().toString().trim(), bInput.getText().toString().trim(), bwToSigned(result, width)) + "\n");
    }

    // ------------------------------------------------------------------
    //  Data Import & Scatter Plot
    // ------------------------------------------------------------------
    private void setupDataImport() {
        dataXColInput = findViewById(R.id.data_x_col);
        dataYColInput = findViewById(R.id.data_y_col);
        dataTrendSpinner = findViewById(R.id.data_trend_spinner);
        dataStatusView = findViewById(R.id.data_status_view);

        String[] trendTypes = {getString(R.string.data_trend_none), getString(R.string.data_trend_linear), getString(R.string.data_trend_quadratic), getString(R.string.data_trend_exponential)};
        ArrayAdapter<String> trendAdapter = new ArrayAdapter<>(this, android.R.layout.simple_dropdown_item_1line, trendTypes);
        dataTrendSpinner.setAdapter(trendAdapter);

        MaterialButton btnImport = findViewById(R.id.btn_data_import);
        MaterialButton btnPlot = findViewById(R.id.btn_data_plot);
        MaterialButton btnClear = findViewById(R.id.btn_data_clear);

        btnImport.setOnClickListener(v -> onDataImport());
        btnPlot.setOnClickListener(v -> onDataPlot());
        btnClear.setOnClickListener(v -> onDataClear());
    }

    private void onDataImport() {
        Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT);
        intent.addCategory(Intent.CATEGORY_OPENABLE);
        intent.setType("*/*");
        startActivityForResult(intent, 9001);
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == 9001 && resultCode == RESULT_OK && data != null && data.getData() != null) {
            try {
                InputStream is = getContentResolver().openInputStream(data.getData());
                BufferedReader reader = new BufferedReader(new InputStreamReader(is));
                dataRows.clear();
                String line;
                boolean firstLine = true;
                while ((line = reader.readLine()) != null) {
                    line = line.trim();
                    if (line.isEmpty()) continue;
                    String[] parts = line.split("[,\\t;]+");
                    if (firstLine) {
                        try {
                            for (String p : parts) Double.parseDouble(p.trim());
                            firstLine = false;
                        } catch (NumberFormatException e) {
                            firstLine = false;
                            continue;
                        }
                    }
                    double[] row = new double[parts.length];
                    boolean valid = true;
                    for (int i = 0; i < parts.length; i++) {
                        try { row[i] = Double.parseDouble(parts[i].trim()); }
                        catch (NumberFormatException e) { valid = false; break; }
                    }
                    if (valid) dataRows.add(row);
                }
                reader.close();
                is.close();
                dataFileName = data.getData().getLastPathSegment();
                if (dataFileName == null) dataFileName = "data";
                dataStatusView.setText(String.format(getString(R.string.data_imported), dataRows.size(), dataFileName));
            } catch (Exception e) {
                toast(String.format(getString(R.string.data_csv_error), e.getMessage()));
            }
        }
    }

    private void onDataPlot() {
        if (dataRows.isEmpty()) {
            toast(getString(R.string.data_no_data));
            return;
        }
        int xCol, yCol;
        try {
            xCol = Integer.parseInt(dataXColInput.getText().toString().trim());
            yCol = Integer.parseInt(dataYColInput.getText().toString().trim());
        } catch (NumberFormatException e) {
            toast(getString(R.string.data_invalid_col));
            return;
        }

        String trendType = dataTrendSpinner.getText().toString().trim();
        List<Entry> entries = new ArrayList<>();
        List<Double> xList = new ArrayList<>(), yList = new ArrayList<>();

        for (double[] row : dataRows) {
            if (xCol < row.length && yCol < row.length) {
                float x = (float) row[xCol];
                float y = (float) row[yCol];
                entries.add(new Entry(x, y));
                xList.add(row[xCol]);
                yList.add(row[yCol]);
            }
        }

        if (entries.isEmpty()) {
            toast(getString(R.string.data_invalid_col));
            return;
        }

        LineDataSet dataSet = new LineDataSet(entries, dataFileName);
        dataSet.setDrawValues(false);
        dataSet.setDrawCircles(true);
        dataSet.setCircleRadius(4f);
        dataSet.setCircleColor(0xFFF38BA8);
        dataSet.setColor(0xFFF38BA8);
        dataSet.setLineWidth(1.5f);
        dataSet.setMode(LineDataSet.Mode.LINEAR);

        if (!trendType.equals(getString(R.string.data_trend_none))) {
            double[] trendResult = computeTrendline(xList, yList, trendType);
            if (trendResult != null) {
                float xMin = Float.MAX_VALUE, xMax = Float.MIN_VALUE;
                for (Entry e : entries) {
                    if (e.getX() < xMin) xMin = e.getX();
                    if (e.getX() > xMax) xMax = e.getX();
                }
                List<Entry> trendEntries = new ArrayList<>();
                int steps = 100;
                for (int i = 0; i <= steps; i++) {
                    float x = xMin + (xMax - xMin) * i / steps;
                    float y = evalTrendline(trendResult, x, trendType);
                    if (Float.isFinite(y)) trendEntries.add(new Entry(x, y));
                }
                LineDataSet trendSet = new LineDataSet(trendEntries, trendType);
                trendSet.setDrawValues(false);
                trendSet.setDrawCircles(false);
                trendSet.setColor(0xFF89B4FA);
                trendSet.setLineWidth(2f);
                trendSet.enableDashedLine(10, 5, 0);

                LineData lineData = new LineData(dataSet, trendSet);
                showDataChart(lineData);
            } else {
                showDataChart(new LineData(dataSet));
            }
        } else {
            showDataChart(new LineData(dataSet));
        }
        dataStatusView.setText(String.format(getString(R.string.data_plotted), entries.size(), trendType));
    }

    private double[] computeTrendline(List<Double> xs, List<Double> ys, String type) {
        int n = xs.size();
        if (n < 2) return null;
        if (type.equals(getString(R.string.data_trend_linear))) {
            double sx = 0, sy = 0, sxy = 0, sxx = 0;
            for (int i = 0; i < n; i++) {
                sx += xs.get(i); sy += ys.get(i);
                sxy += xs.get(i) * ys.get(i);
                sxx += xs.get(i) * xs.get(i);
            }
            double b = (n * sxy - sx * sy) / (n * sxx - sx * sx);
            double a = (sy - b * sx) / n;
            return new double[]{b, a};
        } else if (type.equals(getString(R.string.data_trend_exponential))) {
            double slnx = 0, sy = 0, slnx2 = 0, sylnx = 0;
            int count = 0;
            for (int i = 0; i < n; i++) {
                if (ys.get(i) > 0) {
                    double lnx = Math.log(xs.get(i));
                    slnx += lnx; sy += Math.log(ys.get(i));
                    slnx2 += lnx * lnx; sylnx += Math.log(ys.get(i)) * lnx;
                    count++;
                }
            }
            if (count < 2) return null;
            double b = (count * sylnx - slnx * sy) / (count * slnx2 - slnx * slnx);
            double a = (sy - b * slnx) / count;
            return new double[]{Math.exp(a), b};
        } else if (type.equals(getString(R.string.data_trend_quadratic))) {
            double sx = 0, sx2 = 0, sx3 = 0, sx4 = 0, sy = 0, sxy = 0, sx2y = 0;
            for (int i = 0; i < n; i++) {
                double x = xs.get(i), y = ys.get(i);
                sx += x; sx2 += x*x; sx3 += x*x*x; sx4 += x*x*x*x;
                sy += y; sxy += x*y; sx2y += x*x*y;
            }
            double[][] mat = {{n, sx, sx2}, {sx, sx2, sx3}, {sx2, sx3, sx4}};
            double[] rhs = {sy, sxy, sx2y};
            double[] sol = solveLinear3(mat, rhs);
            if (sol != null) return new double[]{sol[2], sol[1], sol[0]};
        }
        return null;
    }

    private double[] solveLinear3(double[][] m, double[] b) {
        double[][] a = new double[3][4];
        for (int i = 0; i < 3; i++) { System.arraycopy(m[i], 0, a[i], 0, 3); a[i][3] = b[i]; }
        for (int i = 0; i < 3; i++) {
            int maxRow = i;
            for (int k = i + 1; k < 3; k++) if (Math.abs(a[k][i]) > Math.abs(a[maxRow][i])) maxRow = k;
            double[] tmp = a[i]; a[i] = a[maxRow]; a[maxRow] = tmp;
            if (Math.abs(a[i][i]) < 1e-12) return null;
            for (int k = i + 1; k < 3; k++) {
                double f = a[k][i] / a[i][i];
                for (int j = i; j < 4; j++) a[k][j] -= f * a[i][j];
            }
        }
        double[] x = new double[3];
        for (int i = 2; i >= 0; i--) {
            x[i] = a[i][3];
            for (int j = i + 1; j < 3; j++) x[i] -= a[i][j] * x[j];
            x[i] /= a[i][i];
        }
        return x;
    }

    private float evalTrendline(double[] p, float x, String type) {
        if (type.equals(getString(R.string.data_trend_linear))) {
            return (float)(p[0] * x + p[1]);
        } else if (type.equals(getString(R.string.data_trend_quadratic))) {
            return (float)(p[0] * x * x + p[1] * x + p[2]);
        } else if (type.equals(getString(R.string.data_trend_exponential)) && x > 0) {
            return (float)(p[0] * Math.exp(p[1] * x));
        }
        return Float.NaN;
    }

    private void showDataChart(LineData lineData) {
        graphCard.setVisibility(android.view.View.VISIBLE);
        lineChart.setData(lineData);
        lineChart.getDescription().setText("");
        XAxis xAxis = lineChart.getXAxis();
        xAxis.setPosition(XAxis.XAxisPosition.BOTTOM);
        xAxis.setDrawGridLines(true);
        xAxis.setGranularity(1f);
        YAxis leftAxis = lineChart.getAxisLeft();
        leftAxis.setDrawGridLines(true);
        lineChart.getAxisRight().setEnabled(false);
        lineChart.animateX(500);
        lineChart.invalidate();
    }

    private void onDataClear() {
        dataRows.clear();
        dataFileName = "";
        dataStatusView.setText("");
        lineChart.clear();
        graphCard.setVisibility(android.view.View.GONE);
    }

    // ------------------------------------------------------------------
    //  Data Interpolation Calculator
    // ------------------------------------------------------------------
    private AutoCompleteTextView interpMethodSpinner;
    private EditText interpDataInput, interpEvalXInput;
    private TextView interpResultView;
    private ArrayAdapter<String> interpMethodAdapter;

    private void setupInterpolation() {
        interpMethodSpinner = findViewById(R.id.interp_method_spinner);
        interpDataInput = findViewById(R.id.interp_data_input);
        interpEvalXInput = findViewById(R.id.interp_eval_x_input);
        interpResultView = findViewById(R.id.interp_result_view);

        String[] methods = {
            getString(R.string.interp_linear),
            getString(R.string.interp_lagrange),
            getString(R.string.interp_newton),
            getString(R.string.interp_spline)
        };
        interpMethodAdapter = new ArrayAdapter<>(this, android.R.layout.simple_dropdown_item_1line, methods);
        interpMethodSpinner.setAdapter(interpMethodAdapter);

        MaterialButton btnCompute = findViewById(R.id.btn_interp_compute);
        MaterialButton btnPlot = findViewById(R.id.btn_interp_plot);

        btnCompute.setOnClickListener(v -> onInterpCompute());
        btnPlot.setOnClickListener(v -> onInterpPlot());
    }

    private List<double[]> parseInterpPoints() {
        String raw = interpDataInput.getText().toString().trim();
        if (raw.isEmpty()) {
            toast(getString(R.string.interp_need_points));
            return null;
        }
        List<double[]> points = new ArrayList<>();
        String[] segments = raw.split(";");
        for (String seg : segments) {
            seg = seg.trim();
            if (seg.isEmpty()) continue;
            String[] parts = seg.split(",");
            if (parts.length != 2) {
                toast(getString(R.string.interp_invalid_format));
                return null;
            }
            try {
                double x = Double.parseDouble(parts[0].trim());
                double y = Double.parseDouble(parts[1].trim());
                points.add(new double[]{x, y});
            } catch (NumberFormatException e) {
                toast(getString(R.string.interp_invalid_format));
                return null;
            }
        }
        if (points.size() < 2) {
            toast(getString(R.string.interp_need_points));
            return null;
        }
        points.sort((a, b) -> Double.compare(a[0], b[0]));
        return points;
    }

    private void onInterpCompute() {
        List<double[]> points = parseInterpPoints();
        if (points == null) return;

        double xVal;
        try {
            xVal = Double.parseDouble(interpEvalXInput.getText().toString().trim());
        } catch (NumberFormatException e) {
            toast(getString(R.string.interp_invalid_format));
            return;
        }

        double[] xs = points.stream().mapToDouble(p -> p[0]).toArray();
        double[] ys = points.stream().mapToDouble(p -> p[1]).toArray();
        String method = interpMethodSpinner.getText().toString().trim();

        double result;
        if (method.equals(getString(R.string.interp_linear))) {
            result = interpLinear(xs, ys, xVal);
        } else if (method.equals(getString(R.string.interp_lagrange))) {
            result = interpLagrange(xs, ys, xVal);
        } else if (method.equals(getString(R.string.interp_newton))) {
            result = interpNewton(xs, ys, xVal);
        } else if (method.equals(getString(R.string.interp_spline))) {
            result = interpSpline(xs, ys, xVal);
        } else {
            result = interpLinear(xs, ys, xVal);
        }

        interpResultView.setText(String.format(getString(R.string.interp_result), fmt(xVal), fmt(result)));
    }

    private void onInterpPlot() {
        List<double[]> points = parseInterpPoints();
        if (points == null) return;

        double[] xs = points.stream().mapToDouble(p -> p[0]).toArray();
        double[] ys = points.stream().mapToDouble(p -> p[1]).toArray();
        String method = interpMethodSpinner.getText().toString().trim();

        float xMin = (float) xs[0];
        float xMax = (float) xs[xs.length - 1];
        float margin = Math.max((xMax - xMin) * 0.15f, 0.5f);
        float xLo = xMin - margin;
        float xHi = xMax + margin;
        int nPlot = 200;

        List<Entry> curveEntries = new ArrayList<>();
        for (int i = 0; i <= nPlot; i++) {
            float x = xLo + (xHi - xLo) * i / nPlot;
            double y;
            if (method.equals(getString(R.string.interp_linear))) {
                y = interpLinear(xs, ys, x);
            } else if (method.equals(getString(R.string.interp_lagrange))) {
                y = interpLagrange(xs, ys, x);
            } else if (method.equals(getString(R.string.interp_newton))) {
                y = interpNewton(xs, ys, x);
            } else if (method.equals(getString(R.string.interp_spline))) {
                y = interpSpline(xs, ys, x);
            } else {
                y = interpLinear(xs, ys, x);
            }
            if (Double.isFinite(y)) curveEntries.add(new Entry(x, (float) y));
        }

        LineDataSet curveSet = new LineDataSet(curveEntries, getString(R.string.interp_title));
        curveSet.setColor(android.graphics.Color.parseColor("#4f8cff"));
        curveSet.setLineWidth(2.5f);
        curveSet.setDrawCircles(false);
        curveSet.setMode(LineDataSet.Mode.CUBIC_BEZIER);

        List<Entry> pointEntries = new ArrayList<>();
        for (double[] p : points) {
            pointEntries.add(new Entry((float) p[0], (float) p[1]));
        }
        LineDataSet pointSet = new LineDataSet(pointEntries, "Data");
        pointSet.setColor(android.graphics.Color.parseColor("#ff6b6b"));
        pointSet.setLineWidth(0f);
        pointSet.setCircleRadius(5f);
        pointSet.setDrawCircleHole(false);
        pointSet.setDrawValues(true);
        pointSet.setValueTextSize(10f);

        LineData lineData = new LineData(curveSet, pointSet);
        showDataChart(lineData);

        String methodLabel = method;
        toast(String.format(getString(R.string.interp_plotted), points.size(), methodLabel));
    }

    private static double interpLinear(double[] xs, double[] ys, double x) {
        int n = xs.length;
        if (x <= xs[0]) return ys[0];
        if (x >= xs[n - 1]) return ys[n - 1];
        for (int i = 0; i < n - 1; i++) {
            if (x >= xs[i] && x <= xs[i + 1]) {
                double t = (x - xs[i]) / (xs[i + 1] - xs[i]);
                return ys[i] + t * (ys[i + 1] - ys[i]);
            }
        }
        return ys[n - 1];
    }

    private static double interpLagrange(double[] xs, double[] ys, double x) {
        int n = xs.length;
        double result = 0.0;
        for (int i = 0; i < n; i++) {
            double li = 1.0;
            for (int j = 0; j < n; j++) {
                if (i != j) li *= (x - xs[j]) / (xs[i] - xs[j]);
            }
            result += ys[i] * li;
        }
        return result;
    }

    private static double interpNewton(double[] xs, double[] ys, double x) {
        int n = xs.length;
        double[][] dd = new double[n][n];
        for (int i = 0; i < n; i++) dd[i][0] = ys[i];
        for (int j = 1; j < n; j++) {
            for (int i = 0; i < n - j; i++) {
                dd[i][j] = (dd[i + 1][j - 1] - dd[i][j - 1]) / (xs[i + j] - xs[i]);
            }
        }
        double result = dd[0][0];
        double product = 1.0;
        for (int j = 1; j < n; j++) {
            product *= (x - xs[j - 1]);
            result += dd[0][j] * product;
        }
        return result;
    }

    private static double interpSpline(double[] xs, double[] ys, double x) {
        int n = xs.length - 1;
        double[] h = new double[n];
        for (int i = 0; i < n; i++) h[i] = xs[i + 1] - xs[i];

        double[] alpha = new double[n + 1];
        for (int i = 1; i < n; i++) {
            alpha[i] = 3.0 / h[i] * (ys[i + 1] - ys[i]) - 3.0 / h[i - 1] * (ys[i] - ys[i - 1]);
        }

        double[] l = new double[n + 1], mu = new double[n + 1], z = new double[n + 1];
        l[0] = 1.0;
        for (int i = 1; i < n; i++) {
            l[i] = 2.0 * (xs[i + 1] - xs[i - 1]) - h[i - 1] * mu[i - 1];
            mu[i] = h[i] / l[i];
            z[i] = (alpha[i] - h[i - 1] * z[i - 1]) / l[i];
        }

        double[] c = new double[n + 1], b = new double[n], d = new double[n];
        for (int j = n - 1; j >= 0; j--) {
            c[j] = z[j] - mu[j] * c[j + 1];
            b[j] = (ys[j + 1] - ys[j]) / h[j] - h[j] * (c[j + 1] + 2.0 * c[j]) / 3.0;
            d[j] = (c[j + 1] - c[j]) / (3.0 * h[j]);
        }

        int seg = 0;
        for (int i = 0; i < n; i++) {
            if (x >= xs[i]) seg = i;
        }
        double dx = x - xs[seg];
        return ys[seg] + b[seg] * dx + c[seg] * dx * dx + d[seg] * dx * dx * dx;
    }

    // ---- Laplace Transform ----

    private void setupLaplace() {
        laplaceExprInput = findViewById(R.id.laplace_expr_input);
        laplaceParamInput = findViewById(R.id.laplace_param_input);
        MaterialButton btnLaplaceFwd = findViewById(R.id.btn_laplace_forward);
        MaterialButton btnLaplaceInv = findViewById(R.id.btn_laplace_inverse);
        btnLaplaceFwd.setOnClickListener(v -> onLaplaceForward());
        btnLaplaceInv.setOnClickListener(v -> onLaplaceInverse());
    }

    private void onLaplaceForward() {
        String expr = laplaceExprInput.getText().toString().trim();
        if (expr.isEmpty()) {
            toast(getString(R.string.laplace_empty_expr));
            return;
        }
        double s = parse(laplaceParamInput);
        if (Double.isNaN(s)) {
            toast(getString(R.string.laplace_invalid_param));
            return;
        }
        try {
            double result = CalcEngine.laplaceTransform(expr, s);
            if (Double.isNaN(result)) {
                String err = CalcEngine.getLastError();
                resultView.append("L{" + expr + "}(" + fmt(s) + ") = Error: " + (err != null ? err : "NaN") + "\n");
            } else {
                resultView.append("L{" + expr + "}(" + fmt(s) + ") = " + fmt(result) + "\n");
                recordHistory("L{" + expr + "}(" + fmt(s) + ")", result);
            }
        } catch (Exception e) {
            resultView.append("L{" + expr + "} = Error: " + e.getMessage() + "\n");
        }
        scrollToResult();
    }

    private void onLaplaceInverse() {
        String expr = laplaceExprInput.getText().toString().trim();
        if (expr.isEmpty()) {
            toast(getString(R.string.laplace_empty_expr));
            return;
        }
        double t = parse(laplaceParamInput);
        if (Double.isNaN(t) || t <= 0) {
            toast(getString(R.string.laplace_invalid_param));
            return;
        }
        try {
            double result = CalcEngine.inverseLaplace(expr, t);
            if (Double.isNaN(result)) {
                String err = CalcEngine.getLastError();
                resultView.append("L⁻¹{" + expr + "}(" + fmt(t) + ") = Error: " + (err != null ? err : "NaN") + "\n");
            } else {
                resultView.append("L⁻¹{" + expr + "}(" + fmt(t) + ") = " + fmt(result) + "\n");
                recordHistory("L⁻¹{" + expr + "}(" + fmt(t) + ")", result);
            }
        } catch (Exception e) {
            resultView.append("L⁻¹{" + expr + "} = Error: " + e.getMessage() + "\n");
        }
        scrollToResult();
    }

    // ---- Custom Function Definition ----
    private EditText customFuncNameInput, customFuncBodyInput;
    private TextView customFuncListView;

    private void setupCustomFunctions() {
        customFuncNameInput = findViewById(R.id.custom_func_name_input);
        customFuncBodyInput = findViewById(R.id.custom_func_body_input);
        customFuncListView = findViewById(R.id.custom_func_list_view);

        MaterialButton btnDefine = findViewById(R.id.btn_custom_func_define);
        MaterialButton btnClearAll = findViewById(R.id.btn_custom_func_clear);

        btnDefine.setOnClickListener(v -> onCustomFuncDefine());
        btnClearAll.setOnClickListener(v -> onCustomFuncClearAll());

        refreshCustomFuncList();
    }

    private void onCustomFuncDefine() {
        String name = customFuncNameInput.getText().toString().trim();
        String body = customFuncBodyInput.getText().toString().trim();
        if (name.isEmpty() || body.isEmpty()) {
            toast(getString(R.string.custom_func_enter_name_body));
            return;
        }
        boolean ok = CalcEngine.customFuncDefine(name, body);
        if (!ok) {
            String err = CalcEngine.getLastError();
            resultView.append(String.format(getString(R.string.custom_func_error), err.isEmpty() ? getString(R.string.result_computation_failed) : err) + "\n");
            scrollToResult();
            return;
        }
        resultView.append(String.format(getString(R.string.custom_func_defined), name, body) + "\n");
        scrollToResult();
        refreshCustomFuncList();
        customFuncNameInput.setText("");
        customFuncBodyInput.setText("");
    }

    private void onCustomFuncClearAll() {
        CalcEngine.customFuncClear();
        resultView.append(getString(R.string.custom_func_all_cleared) + "\n");
        scrollToResult();
        refreshCustomFuncList();
    }

    private void refreshCustomFuncList() {
        String list = CalcEngine.customFuncList();
        if (list == null || list.isEmpty()) {
            customFuncListView.setText(getString(R.string.custom_func_none));
        } else {
            customFuncListView.setText(list);
        }
    }

    // ------------------------------------------------------------------
    //  Calculation History
    // ------------------------------------------------------------------

    private void setupHistory() {
        historyListView = findViewById(R.id.history_list_view);
        MaterialButton btnHistoryClear = findViewById(R.id.btn_history_clear);
        btnHistoryClear.setOnClickListener(v -> onHistoryClear());
        loadHistoryFromPrefs();
        refreshHistoryList();
    }

    private void loadHistoryFromPrefs() {
        SharedPreferences prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);
        String saved = prefs.getString(KEY_HISTORY, "");
        if (saved.isEmpty()) return;
        String[] entries = saved.split(";");
        for (String entry : entries) {
            entry = entry.trim();
            if (entry.isEmpty()) continue;
            int eqIdx = entry.lastIndexOf('=');
            if (eqIdx < 0) continue;
            String expr = entry.substring(0, eqIdx).trim();
            String resultStr = entry.substring(eqIdx + 1).trim();
            try {
                double result = Double.parseDouble(resultStr);
                CalcEngine.historyAdd(expr, result);
            } catch (NumberFormatException e) {
                CalcEngine.historyAdd(expr, Double.NaN);
            }
        }
    }

    private void saveHistoryToPrefs() {
        String all = CalcEngine.historyGetAll();
        SharedPreferences prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);
        prefs.edit().putString(KEY_HISTORY, all).apply();
    }

    private void recordHistory(String expr, double result) {
        CalcEngine.historyAdd(expr, result);
        saveHistoryToPrefs();
        refreshHistoryList();
    }

    private void refreshHistoryList() {
        int count = CalcEngine.historyCount();
        if (count == 0) {
            historyListView.setText(getString(R.string.history_empty));
            return;
        }
        StringBuilder sb = new StringBuilder();
        for (int i = count - 1; i >= 0; i--) {
            HashMap<String, Object> entry = new HashMap<>();
            if (CalcEngine.historyGet(i, entry)) {
                String expr = (String) entry.get("expr");
                Object resultObj = entry.get("result");
                double result = resultObj instanceof Double ? (Double) resultObj : Double.NaN;
                String resultStr = Double.isNaN(result) ? "NaN" : fmt(result);
                sb.append(expr).append(" = ").append(resultStr);
                if (i > 0) sb.append("\n");
            }
        }
        historyListView.setText(sb.toString());
        historyListView.setOnClickListener(v -> {
            if (count > 0) {
                HashMap<String, Object> lastEntry = new HashMap<>();
                if (CalcEngine.historyGet(count - 1, lastEntry)) {
                    String lastExpr = (String) lastEntry.get("expr");
                    exprInput.setText(lastExpr);
                }
            }
        });
    }

    private void onHistoryClear() {
        CalcEngine.historyClear();
        saveHistoryToPrefs();
        refreshHistoryList();
        resultView.append(getString(R.string.history_cleared) + "\n");
        scrollToResult();
    }
}
