"""
i18n module for SuperCalculator.
Auto-detects system locale; override with SUPERCALC_LANG environment variable.
Supports 'en' and 'zh' locales.
"""

import locale
import os


def _detect_language():
    """Detect the language to use from environment or system locale."""
    env_lang = os.environ.get("SUPERCALC_LANG", "").strip().lower()
    if env_lang:
        return env_lang
    try:
        default = locale.getdefaultlocale()[0]
        if default:
            lang = default.split("_")[0].lower()
            return lang
    except Exception:
        pass
    return "en"


CURRENT_LANG = _detect_language()

# ---------------------------------------------------------------------------
# Translation tables
# ---------------------------------------------------------------------------

STRINGS = {
    # ---- Window titles ----
    "win_title": {
        "en": "Super Function Graphing Calculator",
        "zh": "超级函数绘图计算器",
    },
    "win_2d": {
        "en": "2D Function Plot",
        "zh": "二维函数图像",
    },
    "win_3d": {
        "en": "3D Function Plot",
        "zh": "三维函数图像",
    },
    "win_fft": {
        "en": "FFT Spectrum Analysis",
        "zh": "FFT频谱分析",
    },
    "win_table": {
        "en": "Function Table",
        "zh": "函数表",
    },
    "win_intersect": {
        "en": "Find Curve Intersections",
        "zh": "求曲线交点",
    },
    "win_input_panel": {
        "en": "Quick Input Panel",
        "zh": "快速输入面板",
    },

    # ---- Section headers (LabelFrame text) ----
    "sec_function_input": {
        "en": "Function Input",
        "zh": "函数输入",
    },
    "sec_parametric": {
        "en": "Parametric Mode x(t), y(t)",
        "zh": "参数方程模式 x(t), y(t)",
    },
    "sec_polar": {
        "en": "Polar Mode r(theta)",
        "zh": "极坐标模式 r(theta)",
    },
    "sec_parameters": {
        "en": "Parameters",
        "zh": "参数",
    },
    "sec_preset": {
        "en": "Preset Functions",
        "zh": "预设函数",
    },
    "sec_curves": {
        "en": "Curves (click to select)",
        "zh": "曲线（点击选择）",
    },
    "sec_range": {
        "en": "Coordinate Range",
        "zh": "坐标范围",
    },
    "sec_calculus": {
        "en": "Calculus Operations",
        "zh": "微积分运算",
    },
    "sec_solver": {
        "en": "Equation Solver f(x)=0",
        "zh": "方程求解 f(x)=0",
    },
    "sec_system": {
        "en": "Nonlinear System Solver f(x,y)=0, g(x,y)=0",
        "zh": "非线性方程组求解 f(x,y)=0, g(x,y)=0",
    },
    "sec_extremum": {
        "en": "Extremum Finder on [a,b]",
        "zh": "极值查找 [a,b]",
    },
    "sec_scan": {
        "en": "Auto Root Scanner",
        "zh": "自动根扫描",
    },
    "sec_mark": {
        "en": "Coordinate Marking",
        "zh": "坐标标记",
    },
    "sec_tangent": {
        "en": "Tangent & Normal Lines",
        "zh": "切线与法线",
    },
    "sec_arc": {
        "en": "Arc Length",
        "zh": "弧长",
    },
    "sec_area": {
        "en": "Area Between Curves",
        "zh": "曲线间面积",
    },
    "sec_table": {
        "en": "Function Table & Export",
        "zh": "函数表与导出",
    },
    "sec_fft": {
        "en": "Fourier Transform & Spectrum",
        "zh": "傅里叶变换与频谱",
    },
    "sec_taylor": {
        "en": "Taylor Series Expansion",
        "zh": "泰勒展开",
    },
    "sec_ode": {
        "en": "ODE Solver (dy/dx = f(x,y))",
        "zh": "ODE求解器 (dy/dx = f(x,y))",
    },
    "sec_stats": {
        "en": "Statistics Calculator",
        "zh": "统计计算器",
    },
    "sec_regression": {
        "en": "Curve Fitting / Regression",
        "zh": "曲线拟合/回归",
    },
    "sec_matrix": {
        "en": "Matrix Operations (Linear Algebra)",
        "zh": "矩阵运算（线性代数）",
    },
    "sec_complex": {
        "en": "Complex Number Calculator",
        "zh": "复数计算器",
    },
    "sec_unit": {
        "en": "Unit Converter",
        "zh": "单位换算",
    },

    # ---- Labels ----
    "label_expr": {
        "en": "Expression f(x):",
        "zh": "表达式 f(x)：",
    },
    "label_xt": {
        "en": "x(t) =",
        "zh": "x(t) =",
    },
    "label_yt": {
        "en": "y(t) =",
        "zh": "y(t) =",
    },
    "label_t_range": {
        "en": "t range:",
        "zh": "t范围：",
    },
    "label_rtheta": {
        "en": "r(theta) =",
        "zh": "r(theta) =",
    },
    "label_theta_range": {
        "en": "theta range:",
        "zh": "theta范围：",
    },
    "label_preset": {
        "en": "Preset:",
        "zh": "预设：",
    },
    "label_at_x": {
        "en": "At x =",
        "zh": "在 x =",
    },
    "label_integrate": {
        "en": "Integrate [",
        "zh": "积分 [",
    },
    "label_comma": {
        "en": " , ",
        "zh": " , ",
    },
    "label_close_bracket": {
        "en": " ]",
        "zh": " ]",
    },
    "label_limit": {
        "en": "Limit x→",
        "zh": "极限 x→",
    },
    "label_guess": {
        "en": "Guess:",
        "zh": "猜测值：",
    },
    "label_range": {
        "en": "Range:",
        "zh": "范围：",
    },
    "label_to": {
        "en": "to",
        "zh": "到",
    },
    "label_a": {
        "en": "a:",
        "zh": "a：",
    },
    "label_b": {
        "en": "b:",
        "zh": "b：",
    },
    "label_interval_ab": {
        "en": "Interval [a,b]:",
        "zh": "区间 [a,b]：",
    },
    "label_from": {
        "en": "From:",
        "zh": "从：",
    },
    "label_to2": {
        "en": "To:",
        "zh": "到：",
    },
    "label_points": {
        "en": "Points:",
        "zh": "点数：",
    },
    "label_samples": {
        "en": "Samples:",
        "zh": "采样数：",
    },
    "label_expand_at": {
        "en": "Expand at a =",
        "zh": "展开点 a =",
    },
    "label_order": {
        "en": "Order:",
        "zh": "阶数：",
    },
    "label_dydx": {
        "en": "dy/dx =",
        "zh": "dy/dx =",
    },
    "label_x0": {
        "en": "x0:",
        "zh": "x0：",
    },
    "label_y0": {
        "en": "y0:",
        "zh": "y0：",
    },
    "label_xend": {
        "en": "x_end:",
        "zh": "x_end：",
    },
    "label_steps": {
        "en": "Steps:",
        "zh": "步数：",
    },
    "label_data": {
        "en": "Data (comma/space separated):",
        "zh": "数据（逗号/空格分隔）：",
    },
    "label_xdata": {
        "en": "X data (comma/space separated, optional):",
        "zh": "X数据（逗号/空格分隔，可选）：",
    },
    "label_ydata": {
        "en": "Y data (uses Statistics data if X is empty):",
        "zh": "Y数据（X为空时使用统计数据）：",
    },
    "label_poly_degree": {
        "en": "Poly degree:",
        "zh": "多项式阶数：",
    },
    "label_matrix_a": {
        "en": "Matrix A (rows separated by ;, cols by ,):",
        "zh": "矩阵A（行用;分隔，列用,分隔）：",
    },
    "label_matrix_b": {
        "en": "Matrix B (for binary operations):",
        "zh": "矩阵B（用于二元运算）：",
    },
    "label_z1": {
        "en": "z1 (a+bi):",
        "zh": "z1 (a+bi)：",
    },
    "label_z2": {
        "en": "z2 (c+di):",
        "zh": "z2 (c+di)：",
    },
    "label_single_z": {
        "en": "Single z:",
        "zh": "单个z：",
    },
    "label_result": {
        "en": "Result:",
        "zh": "结果：",
    },
    "label_category": {
        "en": "Category:",
        "zh": "类别：",
    },
    "label_from_unit": {
        "en": "From:",
        "zh": "从：",
    },
    "label_to_unit": {
        "en": "To:",
        "zh": "到：",
    },
    "label_value": {
        "en": "Value:",
        "zh": "数值：",
    },
    "label_step": {
        "en": "Step:",
        "zh": "步长：",
    },
    "label_3d_grid": {
        "en": "3D Grid:",
        "zh": "3D网格：",
    },
    "label_grid": {
        "en": "Grid",
        "zh": "网格",
    },
    "label_no_params": {
        "en": "No parameters detected",
        "zh": "未检测到参数",
    },
    "label_set_params": {
        "en": "Set parameter values:",
        "zh": "设置参数值：",
    },
    "label_sys_desc": {
        "en": "Solves f(x,y)=0, g(x,y)=0 simultaneously (Newton's method for systems)",
        "zh": "同时求解 f(x,y)=0, g(x,y)=0（牛顿法）",
    },
    "label_sys_f": {
        "en": "f(x,y) =",
        "zh": "f(x,y) =",
    },
    "label_sys_g": {
        "en": "g(x,y) =",
        "zh": "g(x,y) =",
    },
    "label_init_guess": {
        "en": "Initial guess:",
        "zh": "初始猜测：",
    },
    "label_scan_desc": {
        "en": "Scan interval [a,b] for all roots f(x)=0",
        "zh": "扫描区间 [a,b] 内所有 f(x)=0 的根",
    },
    "label_mark_hint": {
        "en": "Left-click to mark, right-click to delete, or enter x:",
        "zh": "左键标记，右键删除，或输入x：",
    },
    "label_tan_at_x": {
        "en": "At x =",
        "zh": "在 x =",
    },
    "label_arc_uses": {
        "en": "Uses integration bounds [a,b] above",
        "zh": "使用上方积分界 [a,b]",
    },
    "label_area_fx": {
        "en": "f(x) =",
        "zh": "f(x) =",
    },
    "label_area_gx": {
        "en": "g(x) =",
        "zh": "g(x) =",
    },
    "label_fft_uses": {
        "en": "Uses [a,b] from Integrate bounds",
        "zh": "使用积分区间的 [a,b]",
    },
    "label_ode_expr": {
        "en": "dy/dx =",
        "zh": "dy/dx =",
    },
    "label_complex_result": {
        "en": "Result:",
        "zh": "结果：",
    },

    # ---- Buttons ----
    "btn_add_curve": {
        "en": "+ Add Curve",
        "zh": "+ 添加曲线",
    },
    "btn_plot": {
        "en": "Plot",
        "zh": "绘制",
    },
    "btn_clear_all": {
        "en": "Clear All",
        "zh": "全部清除",
    },
    "btn_enable_parametric": {
        "en": "Enable parametric curve",
        "zh": "启用参数曲线",
    },
    "btn_enable_polar": {
        "en": "Enable polar curve",
        "zh": "启用极坐标曲线",
    },
    "btn_remove": {
        "en": "Remove Selected",
        "zh": "删除选中",
    },
    "btn_find_intersections": {
        "en": "Find Intersections...",
        "zh": "查找交点...",
    },
    "btn_apply": {
        "en": "Apply",
        "zh": "应用",
    },
    "btn_deriv": {
        "en": "f'(x) Derivative",
        "zh": "f'(x) 导数",
    },
    "btn_deriv2": {
        "en": "f''(x) 2nd Deriv",
        "zh": "f''(x) 二阶导",
    },
    "btn_integrate": {
        "en": "Integrate",
        "zh": "积分",
    },
    "btn_lim": {
        "en": "lim f(x)",
        "zh": "lim f(x)",
    },
    "btn_left_lim": {
        "en": "Left lim",
        "zh": "左极限",
    },
    "btn_right_lim": {
        "en": "Right lim",
        "zh": "右极限",
    },
    "btn_solve_newton": {
        "en": "Find Root (Newton)",
        "zh": "求根（牛顿法）",
    },
    "btn_solve_bisection": {
        "en": "Find Root (Bisection)",
        "zh": "求根（二分法）",
    },
    "btn_solve_system": {
        "en": "Solve System",
        "zh": "求解方程组",
    },
    "btn_find_min": {
        "en": "Find Minimum",
        "zh": "求最小值",
    },
    "btn_find_max": {
        "en": "Find Maximum",
        "zh": "求最大值",
    },
    "btn_scan_roots": {
        "en": "Scan Roots",
        "zh": "扫描根",
    },
    "btn_mark_point": {
        "en": "Mark Point",
        "zh": "标记点",
    },
    "btn_clear_marks": {
        "en": "Clear Marks",
        "zh": "清除标记",
    },
    "btn_draw_tangent": {
        "en": "Draw Tangent",
        "zh": "画切线",
    },
    "btn_draw_normal": {
        "en": "Draw Normal",
        "zh": "画法线",
    },
    "btn_clear_lines": {
        "en": "Clear Lines",
        "zh": "清除线",
    },
    "btn_compute_arc": {
        "en": "Compute Arc Length",
        "zh": "计算弧长",
    },
    "btn_compute_area": {
        "en": "Compute Area",
        "zh": "计算面积",
    },
    "btn_gen_table": {
        "en": "Generate Table",
        "zh": "生成表格",
    },
    "btn_export_csv": {
        "en": "Export CSV",
        "zh": "导出CSV",
    },
    "btn_copy_table": {
        "en": "Copy Table",
        "zh": "复制表格",
    },
    "btn_compute_fft": {
        "en": "Compute FFT",
        "zh": "计算FFT",
    },
    "btn_export_spectrum": {
        "en": "Export Spectrum CSV",
        "zh": "导出频谱CSV",
    },
    "btn_expand_taylor": {
        "en": "Expand Taylor",
        "zh": "泰勒展开",
    },
    "btn_plot_taylor": {
        "en": "Plot Taylor + Original",
        "zh": "绘制泰勒+原函数",
    },
    "btn_solve_ode": {
        "en": "Solve ODE",
        "zh": "求解ODE",
    },
    "btn_plot_solution": {
        "en": "Plot Solution",
        "zh": "绘制解",
    },
    "btn_compute_stats": {
        "en": "Compute Stats",
        "zh": "计算统计",
    },
    "btn_sort_data": {
        "en": "Sort Data",
        "zh": "排序数据",
    },
    "btn_plot_histogram": {
        "en": "Plot Histogram",
        "zh": "绘制直方图",
    },
    "btn_linear": {
        "en": "Linear (y=ax+b)",
        "zh": "线性 (y=ax+b)",
    },
    "btn_quadratic": {
        "en": "Quadratic",
        "zh": "二次",
    },
    "btn_polynomial": {
        "en": "Polynomial",
        "zh": "多项式",
    },
    "btn_exponential": {
        "en": "Exponential",
        "zh": "指数",
    },
    "btn_power": {
        "en": "Power",
        "zh": "幂",
    },
    "btn_logarithmic": {
        "en": "Logarithmic",
        "zh": "对数",
    },
    "btn_plot_fit": {
        "en": "Plot Fit",
        "zh": "绘制拟合",
    },
    "btn_convert": {
        "en": "Convert",
        "zh": "换算",
    },
    "btn_close": {
        "en": "Close",
        "zh": "关闭",
    },
    "btn_find_intersections2": {
        "en": "Find Intersections",
        "zh": "查找交点",
    },

    # ---- Input Panel categories ----
    "cat_basic": {
        "en": "Basic",
        "zh": "基本",
    },
    "cat_operators": {
        "en": "Operators",
        "zh": "运算符",
    },
    "cat_logexp": {
        "en": "Log/Exp",
        "zh": "对数/指数",
    },
    "cat_trig": {
        "en": "Trig",
        "zh": "三角",
    },
    "cat_rounding": {
        "en": "Rounding",
        "zh": "取整",
    },
    "cat_special": {
        "en": "Special",
        "zh": "特殊",
    },
    "cat_constants": {
        "en": "Constants",
        "zh": "常数",
    },

    # ---- Range labels ----
    "range_xmin": {
        "en": "X min",
        "zh": "X最小",
    },
    "range_xmax": {
        "en": "X max",
        "zh": "X最大",
    },
    "range_ymin": {
        "en": "Y min",
        "zh": "Y最小",
    },
    "range_ymax": {
        "en": "Y max",
        "zh": "Y最大",
    },
    "range_zmin": {
        "en": "Z min",
        "zh": "Z最小",
    },
    "range_zmax": {
        "en": "Z max",
        "zh": "Z最大",
    },

    # ---- Status messages ----
    "status_ready": {
        "en": "Ready.",
        "zh": "就绪。",
    },
    "status_cleared": {
        "en": "Cleared all curves.",
        "zh": "已清除所有曲线。",
    },
    "status_no_curves": {
        "en": "No curves to plot.",
        "zh": "没有曲线可绘制。",
    },
    "status_invalid_range": {
        "en": "Invalid range or step values; using previous settings.",
        "zh": "范围或步长无效；使用之前的设置。",
    },
    "status_invalid_numeric": {
        "en": "Invalid numeric values; using previous settings.",
        "zh": "数值无效；使用之前的设置。",
    },
    "status_plotted_2d": {
        "en": "Plotted {0} 2D curve(s) on [{1}, {2}]",
        "zh": "已绘制 {0} 条二维曲线，范围 [{1}, {2}]",
    },
    "status_plotted_3d": {
        "en": "Plotted 3D surface(s) [{0}×{1} grid]",
        "zh": "已绘制三维曲面 [{0}×{1} 网格]",
    },
    "status_marked": {
        "en": "Marked point: ({0}, {1})",
        "zh": "已标记点：({0}, {1})",
    },
    "status_no_points_del": {
        "en": "No points to delete",
        "zh": "没有可删除的点",
    },
    "status_deleted": {
        "en": "Deleted point: ({0}, {1})",
        "zh": "已删除点：({0}, {1})",
    },
    "status_right_no_point": {
        "en": "Right-click: no point nearby to delete",
        "zh": "右键：附近没有可删除的点",
    },
    "status_marked_at": {
        "en": "Marked point at x={0}: ({1}, {2})",
        "zh": "已标记 x={0} 处的点：({1}, {2})",
    },
    "status_tangent": {
        "en": "Tangent at x={0}: y = {1}(x-{2}) + {3}",
        "zh": "切线在 x={0}：y = {1}(x-{2}) + {3}",
    },
    "status_normal": {
        "en": "Normal at x={0}: y = {1}(x-{2}) + {3}",
        "zh": "法线在 x={0}：y = {1}(x-{2}) + {3}",
    },
    "status_normal_vert": {
        "en": "Normal at x={0}: vertical line x = {1}",
        "zh": "法线在 x={0}：垂直线 x = {1}",
    },
    "status_cleared_tan": {
        "en": "Cleared tangent and normal lines.",
        "zh": "已清除切线和法线。",
    },
    "status_invalid_plot": {
        "en": "Invalid plot range or step size",
        "zh": "绘图范围或步长无效",
    },
    "status_invalid_3d": {
        "en": "Invalid 3D plot range or resolution",
        "zh": "三维绘图范围或分辨率无效",
    },
    "status_normal_line": {
        "en": "Normal at x={0}: y = {1}(x-{2}) + {3}",
        "zh": "法线在 x={0}：y = {1}(x-{2}) + {3}",
    },
    "status_table_gen": {
        "en": "Table generated: {0}/{1} valid points.",
        "zh": "表格已生成：{0}/{1} 个有效点。",
    },
    "status_exported_table": {
        "en": "Exported table to {0}",
        "zh": "已导出表格到 {0}",
    },
    "status_deriv_result": {
        "en": "f'({0}) = {1}",
        "zh": "f'({0}) = {1}",
    },
    "status_deriv2_result": {
        "en": "f''({0}) = {1}",
        "zh": "f''({0}) = {1}",
    },
    "status_integrate": {
        "en": "Integrate [{0},{1}] = {2}",
        "zh": "积分 [{0},{1}] = {2}",
    },
    "status_arc": {
        "en": "Arc length [{0},{1}] = {2}",
        "zh": "弧长 [{0},{1}] = {2}",
    },
    "status_area": {
        "en": "Area between curves [{0},{1}] = {2}",
        "zh": "曲线间面积 [{0},{1}] = {2}",
    },
    "status_limit": {
        "en": "lim(x→{0}) = {1}",
        "zh": "lim(x→{0}) = {1}",
    },
    "status_limit_dne": {
        "en": "lim(x→{0}) does not exist",
        "zh": "lim(x→{0}) 不存在",
    },
    "status_left_limit": {
        "en": "lim(x→{0}⁻) = {1}",
        "zh": "lim(x→{0}⁻) = {1}",
    },
    "status_right_limit": {
        "en": "lim(x→{0}⁺) = {1}",
        "zh": "lim(x→{0}⁺) = {1}",
    },
    "status_fft_computed": {
        "en": "FFT computed: {0} frequency bins",
        "zh": "FFT已计算：{0} 个频率分量",
    },
    "status_exported_fft": {
        "en": "Exported FFT to {0}",
        "zh": "已导出FFT到 {0}",
    },
    "status_taylor": {
        "en": "Taylor series at a={0}, order={1}",
        "zh": "泰勒级数在 a={0}，阶数={1}",
    },
    "status_taylor_plot": {
        "en": "Taylor plot at a={0}, order={1}",
        "zh": "泰勒绘图在 a={0}，阶数={1}",
    },
    "status_ode_solved": {
        "en": "ODE solved: {0} points",
        "zh": "ODE已求解：{0} 个点",
    },
    "status_ode_plotted": {
        "en": "ODE solution plotted ({0} points)",
        "zh": "ODE解已绘制（{0} 个点）",
    },
    "status_root": {
        "en": "Root: x = {0}",
        "zh": "根：x = {0}",
    },
    "status_system": {
        "en": "System: x={0}, y={1}",
        "zh": "方程组：x={0}, y={1}",
    },
    "status_extremum": {
        "en": "{0}: x = {1}, f(x) = {2}",
        "zh": "{0}：x = {1}, f(x) = {2}",
    },
    "status_found_roots": {
        "en": "Found {0} root(s)",
        "zh": "找到 {0} 个根",
    },
    "status_stats": {
        "en": "Stats: n={0}, mean={1}, std={2}",
        "zh": "统计：n={0}, 均值={1}, 标准差={2}",
    },
    "status_data_sorted": {
        "en": "Data sorted ({0} values)",
        "zh": "数据已排序（{0} 个值）",
    },
    "status_histogram": {
        "en": "Histogram plotted ({0} values, {1} bins)",
        "zh": "直方图已绘制（{0} 个值, {1} 个区间）",
    },
    "status_exported_stats": {
        "en": "Exported {0} values to {1}",
        "zh": "已导出 {0} 个值到 {1}",
    },
    "status_fit": {
        "en": "Fit: {0}  R²={1}",
        "zh": "拟合：{0}  R²={1}",
    },
    "status_fit_plotted": {
        "en": "Fit curve plotted: {0}",
        "zh": "拟合曲线已绘制：{0}",
    },
    "status_det": {
        "en": "det(A) = {0}",
        "zh": "det(A) = {0}",
    },
    "status_rank": {
        "en": "rank(A) = {0}",
        "zh": "rank(A) = {0}",
    },
    "status_rref": {
        "en": "RREF computed, rank = {0}",
        "zh": "RREF已计算，秩 = {0}",
    },
    "status_eigenvalues": {
        "en": "Eigenvalues: {0}",
        "zh": "特征值：{0}",
    },
    "status_complex_result": {
        "en": "Result: {0}",
        "zh": "结果：{0}",
    },
    "status_unit_convert": {
        "en": "{0} {1} = {2} {3}",
        "zh": "{0} {1} = {2} {3}",
    },

    # ---- Error/Info dialog titles ----
    "err_input": {
        "en": "Input Error",
        "zh": "输入错误",
    },
    "err_error": {
        "en": "Error",
        "zh": "错误",
    },
    "err_export": {
        "en": "Export Error",
        "zh": "导出错误",
    },
    "info_info": {
        "en": "Info",
        "zh": "信息",
    },
    "err_no_expr": {
        "en": "No Expression",
        "zh": "无表达式",
    },
    "err_limit": {
        "en": "Limit Error",
        "zh": "极限错误",
    },
    "warn_limit_dne": {
        "en": "Limit Does Not Exist",
        "zh": "极限不存在",
    },
    "err_taylor": {
        "en": "Taylor Error",
        "zh": "泰勒错误",
    },
    "err_ode": {
        "en": "ODE Error",
        "zh": "ODE错误",
    },
    "err_solver": {
        "en": "Solver Error",
        "zh": "求解器错误",
    },
    "err_bisection": {
        "en": "Bisection Error",
        "zh": "二分法错误",
    },
    "err_system": {
        "en": "System Solver Error",
        "zh": "方程组求解错误",
    },
    "err_extremum": {
        "en": "Extremum Error",
        "zh": "极值错误",
    },
    "err_matrix": {
        "en": "Matrix Error",
        "zh": "矩阵错误",
    },
    "err_complex": {
        "en": "Complex Error",
        "zh": "复数错误",
    },
    "err_unit": {
        "en": "Unit Converter",
        "zh": "单位换算",
    },
    "info_taylor": {
        "en": "Taylor Series",
        "zh": "泰勒级数",
    },
    "info_ode": {
        "en": "ODE Solution",
        "zh": "ODE解",
    },
    "info_root_scan": {
        "en": "Root Scan Results",
        "zh": "根扫描结果",
    },
    "info_stats": {
        "en": "Statistics Results",
        "zh": "统计结果",
    },
    "info_regression": {
        "en": "Regression Results",
        "zh": "回归结果",
    },

    "err_info": {
        "en": "Info",
        "zh": "信息",
    },
    "err_limit_dne": {
        "en": "Limit Does Not Exist",
        "zh": "极限不存在",
    },
    "err_parametric": {
        "en": "Parametric Curve",
        "zh": "参数曲线",
    },
    "err_polar": {
        "en": "Polar Curve",
        "zh": "极坐标曲线",
    },
    "err_root_scan": {
        "en": "Root Scan Results",
        "zh": "根扫描结果",
    },

    # ---- Dialog message strings ----
    "msg_enter_xt_yt": {
        "en": "Please enter both x(t) and y(t) expressions.",
        "zh": "请输入 x(t) 和 y(t) 表达式。",
    },
    "msg_enter_rtheta": {
        "en": "Please enter an r(theta) expression.",
        "zh": "请输入 r(theta) 表达式。",
    },
    "msg_enter_expr": {
        "en": "Please enter an expression.",
        "zh": "请输入表达式。",
    },
    "msg_select_curve": {
        "en": "Select a curve to remove.",
        "zh": "请选择要删除的曲线。",
    },
    "msg_xmin_xmax": {
        "en": "X min must be less than X max.",
        "zh": "X最小值必须小于X最大值。",
    },
    "msg_ymin_ymax": {
        "en": "Y min must be less than Y max.",
        "zh": "Y最小值必须小于Y最大值。",
    },
    "msg_zmin_zmax": {
        "en": "Z min must be less than Z max.",
        "zh": "Z最小值必须小于Z最大值。",
    },
    "msg_step_positive": {
        "en": "Step size must be positive.",
        "zh": "步长必须为正数。",
    },
    "msg_invalid_range": {
        "en": "Invalid range values.",
        "zh": "范围值无效。",
    },
    "msg_could_not_eval": {
        "en": "Could not evaluate function at this x",
        "zh": "无法在此x处求值",
    },
    "msg_invalid_x": {
        "en": "Invalid x value",
        "zh": "x值无效",
    },
    "msg_invalid_x2": {
        "en": "Invalid x value.",
        "zh": "x值无效。",
    },
    "msg_could_not_tangent": {
        "en": "Could not compute tangent.\n{0}",
        "zh": "无法计算切线。\n{0}",
    },
    "msg_could_not_normal": {
        "en": "Could not compute normal.\n{0}",
        "zh": "无法计算法线。\n{0}",
    },
    "msg_add_two_curves": {
        "en": "Add at least two 2D curves to find intersections.",
        "zh": "至少添加两条二维曲线才能查找交点。",
    },
    "msg_select_both": {
        "en": "Please select both curves.",
        "zh": "请选择两条曲线。",
    },
    "msg_select_diff": {
        "en": "Please select two different curves.",
        "zh": "请选择两条不同的曲线。",
    },
    "msg_could_not_locate": {
        "en": "Could not locate selected curves.",
        "zh": "无法定位所选曲线。",
    },
    "msg_found_intersect": {
        "en": "Found {0} intersection(s):",
        "zh": "找到 {0} 个交点：",
    },
    "msg_no_intersect": {
        "en": "No intersections found in the current X range.",
        "zh": "在当前X范围内未找到交点。",
    },
    "msg_invalid_table": {
        "en": "Invalid table parameters.",
        "zh": "表格参数无效。",
    },
    "msg_from_less_to": {
        "en": "From must be less than To.",
        "zh": "起始值必须小于结束值。",
    },
    "msg_pts_range": {
        "en": "Points must be between 2 and 5000.",
        "zh": "点数必须在2到5000之间。",
    },
    "msg_gen_first": {
        "en": "Generate a table first.",
        "zh": "请先生成表格。",
    },
    "msg_parametric_curve": {
        "en": "Parametric Curve",
        "zh": "参数曲线",
    },
    "msg_polar_curve": {
        "en": "Polar Curve",
        "zh": "极坐标曲线",
    },
    "msg_add_func_first": {
        "en": "Add a function first.",
        "zh": "请先添加函数。",
    },
    "msg_deriv_failed": {
        "en": "Derivative failed.\n{0}",
        "zh": "求导失败。\n{0}",
    },
    "msg_deriv_result": {
        "en": "f'({0}) = {1}",
        "zh": "f'({0}) = {1}",
    },
    "msg_deriv2_result": {
        "en": "f''({0}) = {1}",
        "zh": "f''({0}) = {1}",
    },
    "msg_int_invalid": {
        "en": "Invalid integration bounds.",
        "zh": "积分边界无效。",
    },
    "msg_int_failed": {
        "en": "Integration failed.\n{0}",
        "zh": "积分失败。\n{0}",
    },
    "msg_int_result": {
        "en": "∫f(x)dx [{0}, {1}] = {2}",
        "zh": "∫f(x)dx [{0}, {1}] = {2}",
    },
    "msg_arc_invalid": {
        "en": "Invalid arc length bounds.",
        "zh": "弧长边界无效。",
    },
    "msg_a_less_b": {
        "en": "a must be less than b.",
        "zh": "a必须小于b。",
    },
    "msg_arc_failed": {
        "en": "Could not compute arc length.",
        "zh": "无法计算弧长。",
    },
    "msg_arc_result": {
        "en": "Arc length [{0}, {1}] ≈ {2}",
        "zh": "弧长 [{0}, {1}] ≈ {2}",
    },
    "msg_enter_fx_gx": {
        "en": "Please enter both f(x) and g(x) expressions.",
        "zh": "请输入 f(x) 和 g(x) 表达式。",
    },
    "msg_area_failed": {
        "en": "Could not compute area between curves.\n{0}",
        "zh": "无法计算曲线间面积。\n{0}",
    },
    "msg_area_result": {
        "en": "Area between f(x) and g(x) [{0}, {1}] ≈ {2}",
        "zh": "f(x)与g(x)之间的面积 [{0}, {1}] ≈ {2}",
    },
    "msg_invalid_limit": {
        "en": "Invalid limit point.",
        "zh": "极限点无效。",
    },
    "msg_limit_failed": {
        "en": "Could not compute limit.\n{0}",
        "zh": "无法计算极限。\n{0}",
    },
    "msg_limit_result": {
        "en": "lim(x→{0}) f(x) = {1}",
        "zh": "lim(x→{0}) f(x) = {1}",
    },
    "msg_limit_dne_detail": {
        "en": "Limit does not exist at x={0}.\nLeft: {1}\nRight: {2}",
        "zh": "x={0}处极限不存在。\n左极限：{1}\n右极限：{2}",
    },
    "msg_left_limit_failed": {
        "en": "Could not compute left limit.\n{0}",
        "zh": "无法计算左极限。\n{0}",
    },
    "msg_left_limit_result": {
        "en": "Left limit at x={0} = {1}",
        "zh": "x={0}处左极限 = {1}",
    },
    "msg_right_limit_failed": {
        "en": "Could not compute right limit.\n{0}",
        "zh": "无法计算右极限。\n{0}",
    },
    "msg_right_limit_result": {
        "en": "Right limit at x={0} = {1}",
        "zh": "x={0}处右极限 = {1}",
    },
    "msg_fft_invalid": {
        "en": "Invalid FFT parameters.",
        "zh": "FFT参数无效。",
    },
    "msg_samples_range": {
        "en": "Samples must be between 2 and 65536.",
        "zh": "采样数必须在2到65536之间。",
    },
    "msg_fft_failed": {
        "en": "Could not compute FFT spectrum.",
        "zh": "无法计算FFT频谱。",
    },
    "msg_compute_fft_first": {
        "en": "Compute FFT first.",
        "zh": "请先计算FFT。",
    },
    "msg_taylor_invalid": {
        "en": "Invalid Taylor parameters.",
        "zh": "泰勒参数无效。",
    },
    "msg_order_range": {
        "en": "Order must be between 1 and 20.",
        "zh": "阶数必须在1到20之间。",
    },
    "msg_taylor_failed": {
        "en": "Could not compute Taylor expansion.\n{0}",
        "zh": "无法计算泰勒展开。\n{0}",
    },
    "msg_ode_enter": {
        "en": "Please enter an ODE expression dy/dx = f(x,y).",
        "zh": "请输入ODE表达式 dy/dx = f(x,y)。",
    },
    "msg_ode_invalid": {
        "en": "Invalid ODE parameters.",
        "zh": "ODE参数无效。",
    },
    "msg_ode_steps": {
        "en": "Steps must be between 1 and 100000.",
        "zh": "步数必须在1到100000之间。",
    },
    "msg_ode_x0_xend": {
        "en": "x0 must not equal x_end.",
        "zh": "x0不能等于x_end。",
    },
    "msg_ode_failed": {
        "en": "Could not solve ODE.\n{0}",
        "zh": "无法求解ODE。\n{0}",
    },
    "msg_ode_first": {
        "en": "Solve an ODE first.",
        "zh": "请先求解ODE。",
    },
    "msg_solve_invalid": {
        "en": "Invalid solver parameters.",
        "zh": "求解器参数无效。",
    },
    "msg_left_less_right": {
        "en": "Left bound must be less than right bound.",
        "zh": "左边界必须小于右边界。",
    },
    "msg_newton_failed": {
        "en": "Newton's method did not converge.\n{0}",
        "zh": "牛顿法未收敛。\n{0}",
    },
    "msg_newton_root": {
        "en": "Root (Newton): x ≈ {0}\nf(x) ≈ {1}",
        "zh": "根（牛顿法）：x ≈ {0}\nf(x) ≈ {1}",
    },
    "msg_bisection_failed": {
        "en": "Bisection method failed.\n{0}",
        "zh": "二分法失败。\n{0}",
    },
    "msg_bisection_root": {
        "en": "Root (Bisection): x ≈ {0}\nf(x) ≈ {1}",
        "zh": "根（二分法）：x ≈ {0}\nf(x) ≈ {1}",
    },
    "msg_enter_fg": {
        "en": "Enter both f(x,y) and g(x,y) expressions.",
        "zh": "请输入 f(x,y) 和 g(x,y) 表达式。",
    },
    "msg_invalid_guess": {
        "en": "Invalid initial guess.",
        "zh": "初始猜测无效。",
    },
    "msg_system_failed": {
        "en": "System solver did not converge.\n{0}",
        "zh": "方程组求解未收敛。\n{0}",
    },
    "msg_system_result": {
        "en": "System solution:\nx ≈ {0}\ny ≈ {1}",
        "zh": "方程组解：\nx ≈ {0}\ny ≈ {1}",
    },
    "msg_ext_invalid": {
        "en": "Invalid interval bounds.",
        "zh": "区间边界无效。",
    },
    "msg_ext_failed": {
        "en": "Extremum finder failed.\n{0}",
        "zh": "极值查找失败。\n{0}",
    },
    "msg_min_result": {
        "en": "Minimum at x ≈ {0}\nf(x) ≈ {1}",
        "zh": "最小值在 x ≈ {0}\nf(x) ≈ {1}",
    },
    "msg_max_result": {
        "en": "Maximum at x ≈ {0}\nf(x) ≈ {1}",
        "zh": "最大值在 x ≈ {0}\nf(x) ≈ {1}",
    },
    "msg_scan_invalid": {
        "en": "Invalid interval bounds.",
        "zh": "区间边界无效。",
    },
    "msg_roots_found": {
        "en": "Found {0} root(s) in [{1}, {2}]:",
        "zh": "在 [{1}, {2}] 中找到 {0} 个根：",
    },
    "msg_no_roots": {
        "en": "No roots found in the interval.",
        "zh": "区间内未找到根。",
    },
    "msg_invalid_num": {
        "en": "Invalid number: '{0}'",
        "zh": "无效数字：'{0}'",
    },
    "msg_no_valid_nums": {
        "en": "No valid numbers entered.",
        "zh": "未输入有效数字。",
    },
    "msg_stats_result": {
        "en": "Statistics Results",
        "zh": "统计结果",
    },
    "msg_need_2y": {
        "en": "Need at least 2 Y data points.",
        "zh": "至少需要2个Y数据点。",
    },
    "msg_reg_failed": {
        "en": "Regression failed. Check your data.",
        "zh": "回归失败。请检查数据。",
    },
    "msg_regression_failed": {
        "en": "Regression failed. Check your data.",
        "zh": "回归失败。请检查数据。",
    },
    "reg_linear": {
        "en": "Linear Regression",
        "zh": "线性回归",
    },
    "reg_quadratic": {
        "en": "Quadratic Regression",
        "zh": "二次回归",
    },
    "reg_polynomial": {
        "en": "Polynomial Regression (degree {0})",
        "zh": "多项式回归（{0}阶）",
    },
    "reg_exponential": {
        "en": "Exponential Regression",
        "zh": "指数回归",
    },
    "reg_power": {
        "en": "Power Regression",
        "zh": "幂回归",
    },
    "reg_logarithmic": {
        "en": "Logarithmic Regression",
        "zh": "对数回归",
    },
    "reg_equation": {
        "en": "Equation: {0}",
        "zh": "方程：{0}",
    },
    "msg_degree_range": {
        "en": "Degree must be between 1 and 10.",
        "zh": "阶数必须在1到10之间。",
    },
    "msg_invalid_degree": {
        "en": "Invalid degree value.",
        "zh": "阶数值无效。",
    },
    "msg_run_reg_first": {
        "en": "Run a regression first to generate fit data.",
        "zh": "请先运行回归以生成拟合数据。",
    },
    "msg_mat_invalid_num": {
        "en": "Invalid number: '{0}'",
        "zh": "无效数字：'{0}'",
    },
    "msg_mat_cols_match": {
        "en": "All rows must have the same number of columns.",
        "zh": "所有行必须具有相同的列数。",
    },
    "msg_mat_add_failed": {
        "en": "Addition failed: {0}",
        "zh": "加法失败：{0}",
    },
    "msg_mat_sub_failed": {
        "en": "Subtraction failed: {0}",
        "zh": "减法失败：{0}",
    },
    "msg_mat_mul_failed": {
        "en": "Multiplication failed: {0}",
        "zh": "乘法失败：{0}",
    },
    "msg_mat_square": {
        "en": "Determinant requires a square matrix.",
        "zh": "行列式需要方阵。",
    },
    "msg_mat_det_failed": {
        "en": "Determinant failed: {0}",
        "zh": "行列式计算失败：{0}",
    },
    "msg_mat_inv_square": {
        "en": "Inverse requires a square matrix.",
        "zh": "逆矩阵需要方阵。",
    },
    "msg_mat_singular": {
        "en": "Matrix is singular, inverse does not exist.",
        "zh": "矩阵奇异，逆矩阵不存在。",
    },
    "msg_mat_inv_failed": {
        "en": "Inverse failed: {0}",
        "zh": "求逆失败：{0}",
    },
    "msg_mat_trans_failed": {
        "en": "Transpose failed: {0}",
        "zh": "转置失败：{0}",
    },
    "msg_mat_rank_failed": {
        "en": "Rank computation failed: {0}",
        "zh": "秩计算失败：{0}",
    },
    "msg_mat_rref_failed": {
        "en": "RREF failed: {0}",
        "zh": "RREF失败：{0}",
    },
    "msg_mat_eig_square": {
        "en": "Eigenvalues require a square matrix.",
        "zh": "特征值需要方阵。",
    },
    "msg_mat_eig_failed": {
        "en": "Eigenvalue computation failed.",
        "zh": "特征值计算失败。",
    },
    "msg_mat_eig_err": {
        "en": "Eigenvalue failed: {0}",
        "zh": "特征值计算失败：{0}",
    },
    "msg_cplx_invalid": {
        "en": "Invalid complex number: {0}",
        "zh": "无效复数：{0}",
    },
    "msg_cplx_div_zero": {
        "en": "Division by zero",
        "zh": "除以零",
    },
    "msg_cplx_ln0": {
        "en": "ln(0) is undefined",
        "zh": "ln(0) 未定义",
    },
    "msg_empty_after_sub": {
        "en": "Empty expression after parameter substitution.",
        "zh": "参数替换后表达式为空。",
    },
    "msg_unit_invalid": {
        "en": "Invalid value. Please enter a number.",
        "zh": "无效值，请输入数字。",
    },
    "msg_add_failed": {
        "en": "Addition failed: {0}",
        "zh": "加法失败：{0}",
    },
    "msg_add_func": {
        "en": "Add a function first.",
        "zh": "请先添加函数。",
    },
    "msg_compute_fft": {
        "en": "Compute FFT first.",
        "zh": "请先计算FFT。",
    },
    "msg_could_not_arc": {
        "en": "Could not compute arc length.",
        "zh": "无法计算弧长。",
    },
    "msg_could_not_area": {
        "en": "Could not compute area between curves.\n{0}",
        "zh": "无法计算曲线间面积。\n{0}",
    },
    "msg_could_not_export": {
        "en": "Could not export: {0}",
        "zh": "无法导出：{0}",
    },
    "msg_could_not_extremum": {
        "en": "Extremum finder failed.\n{0}",
        "zh": "极值查找失败。\n{0}",
    },
    "msg_could_not_fft": {
        "en": "Could not compute FFT spectrum.",
        "zh": "无法计算FFT频谱。",
    },
    "msg_could_not_left_limit": {
        "en": "Could not compute left limit.\n{0}",
        "zh": "无法计算左极限。\n{0}",
    },
    "msg_could_not_limit": {
        "en": "Could not compute limit.\n{0}",
        "zh": "无法计算极限。\n{0}",
    },
    "msg_could_not_ode": {
        "en": "Could not solve ODE.\n{0}",
        "zh": "无法求解ODE。\n{0}",
    },
    "msg_could_not_right_limit": {
        "en": "Could not compute right limit.\n{0}",
        "zh": "无法计算右极限。\n{0}",
    },
    "msg_could_not_root": {
        "en": "Could not locate selected curves.",
        "zh": "无法定位所选曲线。",
    },
    "msg_could_not_system": {
        "en": "System solver did not converge.\n{0}",
        "zh": "方程组求解未收敛。\n{0}",
    },
    "msg_could_not_taylor": {
        "en": "Could not compute Taylor expansion.\n{0}",
        "zh": "无法计算泰勒展开。\n{0}",
    },
    "msg_deriv2_failed": {
        "en": "Second derivative failed.\n{0}",
        "zh": "二阶求导失败。\n{0}",
    },
    "msg_det_failed": {
        "en": "Determinant failed: {0}",
        "zh": "行列式计算失败：{0}",
    },
    "msg_det_square": {
        "en": "Determinant requires a square matrix.",
        "zh": "行列式需要方阵。",
    },
    "msg_eigen_error": {
        "en": "Eigenvalue computation failed.",
        "zh": "特征值计算失败。",
    },
    "msg_eigen_failed": {
        "en": "Eigenvalue failed: {0}",
        "zh": "特征值计算失败：{0}",
    },
    "msg_eigen_square": {
        "en": "Eigenvalues require a square matrix.",
        "zh": "特征值需要方阵。",
    },
    "msg_enter_fg_xy": {
        "en": "Enter both f(x,y) and g(x,y) expressions.",
        "zh": "请输入 f(x,y) 和 g(x,y) 表达式。",
    },
    "msg_enter_ode": {
        "en": "Please enter an ODE expression dy/dx = f(x,y).",
        "zh": "请输入ODE表达式 dy/dx = f(x,y)。",
    },
    "msg_extremum_found": {
        "en": "{0} at x ≈ {1}\nf(x) ≈ {2}",
        "zh": "{0}在 x ≈ {1}\nf(x) ≈ {2}",
    },
    "msg_generate_table": {
        "en": "Generate a table first.",
        "zh": "请先生成表格。",
    },
    "msg_integ_failed": {
        "en": "Integration failed.\n{0}",
        "zh": "积分失败。\n{0}",
    },
    "msg_integ_result": {
        "en": "∫f(x)dx [{0}, {1}] = {2}",
        "zh": "∫f(x)dx [{0}, {1}] = {2}",
    },
    "msg_inv_failed": {
        "en": "Inverse failed: {0}",
        "zh": "求逆失败：{0}",
    },
    "msg_inv_square": {
        "en": "Inverse requires a square matrix.",
        "zh": "逆矩阵需要方阵。",
    },
    "msg_invalid_arc_bounds": {
        "en": "Invalid arc length bounds.",
        "zh": "弧长边界无效。",
    },
    "msg_invalid_bounds": {
        "en": "Invalid interval bounds.",
        "zh": "区间边界无效。",
    },
    "msg_invalid_bounds_val": {
        "en": "Invalid integration bounds.",
        "zh": "积分边界无效。",
    },
    "msg_invalid_complex": {
        "en": "Invalid complex number: {0}{1}",
        "zh": "无效复数：{0}{1}",
    },
    "msg_invalid_complex2": {
        "en": "Invalid complex number: {0}",
        "zh": "无效复数：{0}",
    },
    "msg_invalid_fft": {
        "en": "Invalid FFT parameters.",
        "zh": "FFT参数无效。",
    },
    "msg_invalid_interval": {
        "en": "Invalid interval bounds.",
        "zh": "区间边界无效。",
    },
    "msg_invalid_number": {
        "en": "Invalid number: '{0}'",
        "zh": "无效数字：'{0}'",
    },
    "msg_invalid_ode": {
        "en": "Invalid ODE parameters.",
        "zh": "ODE参数无效。",
    },
    "msg_invalid_solver": {
        "en": "Invalid solver parameters.",
        "zh": "求解器参数无效。",
    },
    "msg_invalid_taylor": {
        "en": "Invalid Taylor parameters.",
        "zh": "泰勒参数无效。",
    },
    "msg_invalid_value": {
        "en": "Invalid value. Please enter a number.",
        "zh": "无效值，请输入数字。",
    },
    "msg_ln_zero": {
        "en": "ln(0) is undefined",
        "zh": "ln(0) 未定义",
    },
    "msg_matrix_cols": {
        "en": "All rows must have the same number of columns.",
        "zh": "所有行必须具有相同的列数。",
    },
    "msg_mul_failed": {
        "en": "Multiplication failed: {0}",
        "zh": "乘法失败：{0}",
    },
    "msg_need_2_ydata": {
        "en": "Need at least 2 Y data points.",
        "zh": "至少需要2个Y数据点。",
    },
    "msg_ode_solution": {
        "en": "ODE Solution",
        "zh": "ODE解",
    },
    "msg_parametric_no_calc": {
        "en": "Parametric curves do not support this operation.",
        "zh": "参数曲线不支持此操作。",
    },
    "msg_points_range": {
        "en": "Points must be between 2 and 5000.",
        "zh": "点数必须在2到5000之间。",
    },
    "msg_polar_no_calc": {
        "en": "Polar curves do not support this operation.",
        "zh": "极坐标曲线不支持此操作。",
    },
    "msg_rank_failed": {
        "en": "Rank computation failed: {0}",
        "zh": "秩计算失败：{0}",
    },
    "msg_root_found": {
        "en": "Root (Newton): x ≈ {0}\nf(x) ≈ {1}",
        "zh": "根（牛顿法）：x ≈ {0}\nf(x) ≈ {1}",
    },
    "msg_root_found_bisection": {
        "en": "Root (Bisection): x ≈ {0}\nf(x) ≈ {1}",
        "zh": "根（二分法）：x ≈ {0}\nf(x) ≈ {1}",
    },
    "msg_rref_failed": {
        "en": "RREF failed: {0}",
        "zh": "RREF失败：{0}",
    },
    "msg_run_regression": {
        "en": "Run a regression first to generate fit data.",
        "zh": "请先运行回归以生成拟合数据。",
    },
    "msg_select_different": {
        "en": "Please select two different curves.",
        "zh": "请选择两条不同的曲线。",
    },
    "msg_select_remove": {
        "en": "Select a curve to remove.",
        "zh": "请选择要删除的曲线。",
    },
    "msg_singular": {
        "en": "Matrix is singular, inverse does not exist.",
        "zh": "矩阵奇异，逆矩阵不存在。",
    },
    "msg_solve_ode_first": {
        "en": "Solve an ODE first.",
        "zh": "请先求解ODE。",
    },
    "msg_stats_results": {
        "en": "Statistics Results",
        "zh": "统计结果",
    },
    "msg_steps_range": {
        "en": "Steps must be between 1 and 100000.",
        "zh": "步数必须在1到100000之间。",
    },
    "msg_sub_failed": {
        "en": "Subtraction failed: {0}",
        "zh": "减法失败：{0}",
    },
    "msg_system_solved": {
        "en": "System Solution",
        "zh": "方程组解",
    },
    "msg_taylor_series": {
        "en": "Taylor Series",
        "zh": "泰勒级数",
    },
    "msg_transpose_failed": {
        "en": "Transpose failed: {0}",
        "zh": "转置失败：{0}",
    },
    "msg_x0_neq_xend": {
        "en": "x0 must not equal x_end.",
        "zh": "x0不能等于x_end。",
    },
    "msg_xdata_length": {
        "en": "X and Y data must have the same length.",
        "zh": "X和Y数据长度必须相同。",
    },

    # ---- FFT axis labels ----
    "fft_amp_title": {
        "en": "Amplitude Spectrum",
        "zh": "幅度谱",
    },
    "fft_phase_title": {
        "en": "Phase Spectrum",
        "zh": "相位谱",
    },
    "fft_freq": {
        "en": "Frequency",
        "zh": "频率",
    },
    "fft_amp": {
        "en": "Amplitude",
        "zh": "幅度",
    },
    "fft_phase_rad": {
        "en": "Phase (rad)",
        "zh": "相位（弧度）",
    },

    # ---- Intersection dialog ----
    "intersect_select": {
        "en": "Select two curves to find their intersections:",
        "zh": "选择两条曲线求交点：",
    },
    "intersect_curve_a": {
        "en": "Curve A:",
        "zh": "曲线A：",
    },
    "intersect_curve_b": {
        "en": "Curve B:",
        "zh": "曲线B：",
    },

    # ---- Unit categories ----
    "unit_length": {
        "en": "Length",
        "zh": "长度",
    },
    "unit_weight": {
        "en": "Weight",
        "zh": "质量",
    },
    "unit_temperature": {
        "en": "Temperature",
        "zh": "温度",
    },
    "unit_area": {
        "en": "Area",
        "zh": "面积",
    },
    "unit_volume": {
        "en": "Volume",
        "zh": "体积",
    },
    "unit_time": {
        "en": "Time",
        "zh": "时间",
    },
    "unit_data": {
        "en": "Data Storage",
        "zh": "数据存储",
    },
    "unit_speed": {
        "en": "Speed",
        "zh": "速度",
    },
    "unit_angle": {
        "en": "Angle",
        "zh": "角度",
    },
}


def t(key, *args):
    """Return the translated string for *key* in the current locale.

    Positional *args* are interpolated via ``str.format()`` using
    ``{0}``, ``{1}``, etc.  If the key is not found, the key itself is
    returned.  If the current locale is not present for a key the English
    fallback is tried; if even that is missing the key is returned.
    """
    entry = STRINGS.get(key)
    if entry is None:
        return key

    if isinstance(entry, dict):
        text = entry.get(CURRENT_LANG, entry.get("en", key))
    else:
        text = str(entry)

    if args:
        try:
            text = text.format(*args)
        except (IndexError, KeyError, ValueError):
            pass

    return text
