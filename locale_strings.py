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
        default = locale.getlocale()[0]
        if default:
            lower = default.lower()
            # Windows may return 'Chinese (Simplified)_China' instead of 'zh_CN'
            if "zh" in lower or "chinese" in lower:
                return "zh"
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
        "zh": "绘图",
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
    "histogram_title": {
        "en": "Histogram",
        "zh": "直方图",
    },
    "histogram_xlabel": {
        "en": "Value",
        "zh": "值",
    },
    "histogram_ylabel": {
        "en": "Frequency",
        "zh": "频率",
    },
    "stat_mean_label": {
        "en": "Mean = {0}",
        "zh": "均值 = {0}",
    },
    "stat_median_label": {
        "en": "Median = {0}",
        "zh": "中位数 = {0}",
    },
    "stat_for_n": {
        "en": "Statistics for {0} data points:",
        "zh": "{0} 个数据点的统计：",
    },
    "stat_sum": {
        "en": "  Sum       = {0}",
        "zh": "  总和      = {0}",
    },
    "stat_mean": {
        "en": "  Mean      = {0}",
        "zh": "  均值      = {0}",
    },
    "stat_median": {
        "en": "  Median    = {0}",
        "zh": "  中位数    = {0}",
    },
    "stat_mode": {
        "en": "  Mode      = {0}",
        "zh": "  众数      = {0}",
    },
    "stat_mode_na": {
        "en": "N/A (all unique)",
        "zh": "无（全部唯一）",
    },
    "stat_min": {
        "en": "  Min       = {0}",
        "zh": "  最小值    = {0}",
    },
    "stat_max": {
        "en": "  Max       = {0}",
        "zh": "  最大值    = {0}",
    },
    "stat_range": {
        "en": "  Range     = {0}",
        "zh": "  极差      = {0}",
    },
    "stat_q1": {
        "en": "  Q1 (25%)  = {0}",
        "zh": "  Q1 (25%)  = {0}",
    },
    "stat_q3": {
        "en": "  Q3 (75%)  = {0}",
        "zh": "  Q3 (75%)  = {0}",
    },
    "stat_iqr": {
        "en": "  IQR       = {0}",
        "zh": "  四分位距  = {0}",
    },
    "stat_var_pop": {
        "en": "  Var (pop) = {0}",
        "zh": "  方差(总体)= {0}",
    },
    "stat_var_sam": {
        "en": "  Var (sam) = {0}",
        "zh": "  方差(样本)= {0}",
    },
    "stat_std_pop": {
        "en": "  Std (pop) = {0}",
        "zh": "  标准差(总体)= {0}",
    },
    "stat_std_sam": {
        "en": "  Std (sam) = {0}",
        "zh": "  标准差(样本)= {0}",
    },
    "stat_sorted": {
        "en": "Sorted: {0}",
        "zh": "已排序：{0}",
    },
    "stat_sorted_more": {
        "en": " ... ({0} total)",
        "zh": " ...（共 {0} 个）",
    },
    "curve_fit_title": {
        "en": "Curve Fitting",
        "zh": "曲线拟合",
    },
    "curve_fit_data_label": {
        "en": "Data",
        "zh": "数据",
    },
    "found_roots_msg": {
        "en": "Found {0} root(s):",
        "zh": "找到 {0} 个根：",
    },
    "valid_points": {
        "en": "Valid points: {0} / {1}",
        "zh": "有效点：{0} / {1}",
    },
    "status_fin_depr_ddb": {
        "en": "DDB: Depr={0:.2f}, Monthly={1:.2f}",
        "zh": "双倍余额递减：折旧={0:.2f}, 月折旧={1:.2f}",
    },
    "label_fin_depr_ddb_header": {
        "en": "Year  Depreciation  Book Value",
        "zh": "年份  折旧额      账面价值",
    },
    "status_bw_result": {
        "en": "A {0} B = {1} (dec)",
        "zh": "A {0} B = {1}（十进制）",
    },
    "title_export_table": {
        "en": "Export Function Table",
        "zh": "导出函数表",
    },
    "title_export_fft": {
        "en": "Export FFT Spectrum",
        "zh": "导出FFT频谱",
    },
    "title_export_stats": {
        "en": "Export Statistics Data",
        "zh": "导出统计数据",
    },
    "title_import_csv": {
        "en": "Import CSV Data",
        "zh": "导入CSV数据",
    },
    "title_export_plot": {
        "en": "Export Data Plot",
        "zh": "导出数据图",
    },
    "data_label_fallback": {
        "en": "Data",
        "zh": "数据",
    },
    "data_preview_headers": {
        "en": "  Headers: {0}",
        "zh": "  表头：{0}",
    },
    "data_preview_columns": {
        "en": "  Columns: {0}",
        "zh": "  列数：{0}",
    },
    "title_cdf": {
        "en": "CDF",
        "zh": "累积分布函数",
    },
    "title_ppf": {
        "en": "PPF",
        "zh": "百分点函数",
    },
    "label_cdf": {
        "en": "CDF",
        "zh": "累积分布函数",
    },
    "label_x": {
        "en": "x",
        "zh": "x",
    },
    "label_dec": {
        "en": "(Dec)",
        "zh": "（十进制）",
    },
    "csv_header_frequency": {
        "en": "Frequency",
        "zh": "频率",
    },
    "csv_header_amplitude": {
        "en": "Amplitude",
        "zh": "幅度",
    },
    "csv_header_phase_rad": {
        "en": "Phase_rad",
        "zh": "相位_弧度",
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
    "status_exported": {
        "en": "Exported to {0}",
        "zh": "已导出到 {0}",
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
    "err_limit_dne": {
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
    "msg_no_ode_points": {
        "en": "No ODE data points available.",
        "zh": "没有可用的ODE数据点。",
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
        "en": "Could not find {0}.\n{1}",
        "zh": "无法找到{0}。\n{1}",
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
        "en": "X data length ({0}) does not match Y data length ({1}).",
        "zh": "X数据长度（{0}）与Y数据长度（{1}）不匹配。",
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

    # ---- Statistical Distribution Calculator ----
    "sec_dist": {
        "en": "Statistical Distributions",
        "zh": "统计分布",
    },
    "label_dist_type": {
        "en": "Distribution:",
        "zh": "分布类型：",
    },
    "label_x_value": {
        "en": "x / q:",
        "zh": "x / q：",
    },
    "btn_dist_pdf": {
        "en": "PDF",
        "zh": "PDF",
    },
    "btn_dist_cdf": {
        "en": "CDF",
        "zh": "CDF",
    },
    "btn_dist_ppf": {
        "en": "PPF",
        "zh": "PPF",
    },
    "btn_dist_plot": {
        "en": "Plot",
        "zh": "绘图",
    },
    "btn_dist_compare": {
        "en": "Compare",
        "zh": "对比",
    },
    "msg_invalid_param": {
        "en": "Invalid value for parameter '{0}'.",
        "zh": "参数 '{0}' 的值无效。",
    },
    "msg_invalid_x_value": {
        "en": "Please enter a valid number for x.",
        "zh": "请输入有效的 x 值。",
    },
    "msg_invalid_q_value": {
        "en": "Please enter a valid probability q (0 < q < 1).",
        "zh": "请输入有效的概率值 q（0 < q < 1）。",
    },
    "msg_q_range": {
        "en": "q must be in the range (0, 1).",
        "zh": "q 必须在 (0, 1) 范围内。",
    },
    "msg_dist_compare_prompt": {
        "en": "Distribution: {0}\nCurrent params: {1}\n\nEnter new values (comma-separated):",
        "zh": "分布：{0}\n当前参数：{1}\n\n输入新值（逗号分隔）：",
    },
    "msg_dist_param_count": {
        "en": "Expected {0} parameter(s).",
        "zh": "需要 {0} 个参数。",
    },
    "status_dist_plot": {
        "en": "Distribution plot: {0}",
        "zh": "分布图：{0}",
    },
    "status_dist_compare": {
        "en": "Distribution comparison: {0}",
        "zh": "分布对比：{0}",
    },

    # ---- Status messages for matrix/other operations ----
    "status_table_copied": {
        "en": "Table copied to clipboard.",
        "zh": "表格已复制到剪贴板。",
    },
    "status_no_roots": {
        "en": "No roots found",
        "zh": "未找到根",
    },
    "status_matrix_add": {
        "en": "Matrix A + B computed",
        "zh": "矩阵 A + B 已计算",
    },
    "status_matrix_sub": {
        "en": "Matrix A - B computed",
        "zh": "矩阵 A - B 已计算",
    },
    "status_matrix_mul": {
        "en": "Matrix A * B computed",
        "zh": "矩阵 A * B 已计算",
    },
    "status_matrix_inv": {
        "en": "Matrix inverse computed",
        "zh": "矩阵逆已计算",
    },
    "status_matrix_trans": {
        "en": "Matrix transpose computed",
        "zh": "矩阵转置已计算",
    },
    "status_matrix_cleared": {
        "en": "Matrix inputs cleared.",
        "zh": "矩阵输入已清除。",
    },
    "status_unit_select": {
        "en": "Unit converter: please select category and units.",
        "zh": "单位换算：请选择类别和单位。",
    },

    # ---- Number Theory Calculator ----
    "sec_number_theory": {
        "en": "Number Theory Calculator",
        "zh": "数论计算器",
    },
    "label_nt_n": {
        "en": "n:",
        "zh": "n：",
    },
    "label_nt_a": {
        "en": "a:",
        "zh": "a：",
    },
    "label_nt_b": {
        "en": "b:",
        "zh": "b：",
    },
    "label_nt_base": {
        "en": "base:",
        "zh": "底数：",
    },
    "label_nt_exp": {
        "en": "exp:",
        "zh": "指数：",
    },
    "label_nt_mod": {
        "en": "mod:",
        "zh": "模：",
    },
    "label_nt_count": {
        "en": "count:",
        "zh": "个数：",
    },
    "btn_nt_factorize": {
        "en": "Factorize",
        "zh": "因式分解",
    },
    "btn_nt_is_prime": {
        "en": "Is Prime?",
        "zh": "是否素数？",
    },
    "btn_nt_gcd": {
        "en": "GCD(a,b)",
        "zh": "GCD(a,b)",
    },
    "btn_nt_lcm": {
        "en": "LCM(a,b)",
        "zh": "LCM(a,b)",
    },
    "btn_nt_fibonacci": {
        "en": "Fibonacci(n)",
        "zh": "Fibonacci(n)",
    },
    "btn_nt_mod_pow": {
        "en": "modPow",
        "zh": "模幂",
    },
    "btn_nt_totient": {
        "en": "φ(n)",
        "zh": "φ(n)",
    },
    "btn_nt_clear": {
        "en": "Clear",
        "zh": "清除",
    },
    "label_nt_result": {
        "en": "Result:",
        "zh": "结果：",
    },
    "status_nt_prime": {
        "en": "{0} is prime",
        "zh": "{0} 是素数",
    },
    "status_nt_composite": {
        "en": "{0} is composite = {1}",
        "zh": "{0} 是合数 = {1}",
    },
    "status_nt_gcd": {
        "en": "gcd({0}, {1}) = {2}",
        "zh": "gcd({0}, {1}) = {2}",
    },
    "status_nt_lcm": {
        "en": "lcm({0}, {1}) = {2}",
        "zh": "lcm({0}, {1}) = {2}",
    },
    "status_nt_fibonacci": {
        "en": "fibonacci({0}) = {1}",
        "zh": "fibonacci({0}) = {1}",
    },
    "status_nt_mod_pow": {
        "en": "{0}^{1} mod {2} = {3}",
        "zh": "{0}^{1} mod {2} = {3}",
    },
    "status_nt_totient": {
        "en": "φ({0}) = {1}",
        "zh": "φ({0}) = {1}",
    },
    "status_nt_factorize": {
        "en": "{0} = {1}",
        "zh": "{0} = {1}",
    },
    "err_nt_input": {
        "en": "Number Theory Error",
        "zh": "数论错误",
    },
    "msg_nt_invalid_n": {
        "en": "Please enter a valid positive integer for n.",
        "zh": "请输入有效的正整数 n。",
    },
    "msg_nt_invalid_ab": {
        "en": "Please enter valid integers for a and b.",
        "zh": "请输入有效的整数 a 和 b。",
    },
    "msg_nt_invalid_modpow": {
        "en": "Please enter valid base, exponent, and modulus (mod > 0).",
        "zh": "请输入有效的底数、指数和模数（模 > 0）。",
    },
    "msg_nt_n_too_large": {
        "en": "n is too large (max 10^12 for factorization).",
        "zh": "n 太大（因式分解最大支持 10^12）。",
    },

    # ---- Bitwise Operations Calculator ----
    "sec_bitwise": {
        "en": "Bitwise Operations",
        "zh": "位运算计算器",
    },
    "label_bw_a": {
        "en": "Operand A:",
        "zh": "操作数 A：",
    },
    "label_bw_b": {
        "en": "Operand B:",
        "zh": "操作数 B：",
    },
    "label_bw_width": {
        "en": "Bit width:",
        "zh": "位宽：",
    },
    "label_bw_op": {
        "en": "Operation:",
        "zh": "运算：",
    },
    "btn_bw_and": {
        "en": "AND",
        "zh": "AND",
    },
    "btn_bw_or": {
        "en": "OR",
        "zh": "OR",
    },
    "btn_bw_xor": {
        "en": "XOR",
        "zh": "XOR",
    },
    "btn_bw_not": {
        "en": "NOT",
        "zh": "NOT",
    },
    "btn_bw_lshift": {
        "en": "<<",
        "zh": "<<",
    },
    "btn_bw_rshift": {
        "en": ">>",
        "zh": ">>",
    },
    "btn_bw_calc": {
        "en": "Calculate",
        "zh": "计算",
    },
    "btn_bw_clear": {
        "en": "Clear",
        "zh": "清除",
    },
    "label_bw_result": {
        "en": "Result:",
        "zh": "结果：",
    },
    "label_bw_res_bin": {
        "en": "Binary:",
        "zh": "二进制：",
    },
    "label_bw_res_oct": {
        "en": "Octal:",
        "zh": "八进制：",
    },
    "label_bw_res_dec": {
        "en": "Decimal:",
        "zh": "十进制：",
    },
    "label_bw_res_hex": {
        "en": "Hex:",
        "zh": "十六进制：",
    },
    "err_bw_input": {
        "en": "Bitwise Error",
        "zh": "位运算错误",
    },
    "msg_bw_invalid": {
        "en": "Please enter valid integers for operands.",
        "zh": "请输入有效的整数操作数。",
    },

    # ---- Base Number Converter ----
    "sec_base_converter": {
        "en": "Base Number Converter",
        "zh": "进制转换器",
    },
    "label_base_input": {
        "en": "Input number:",
        "zh": "输入数字：",
    },
    "label_base_from": {
        "en": "From base:",
        "zh": "源进制：",
    },
    "label_base_to": {
        "en": "To base:",
        "zh": "目标进制：",
    },
    "btn_base_convert": {
        "en": "Convert",
        "zh": "转换",
    },
    "btn_base_clear": {
        "en": "Clear",
        "zh": "清除",
    },
    "label_base_result": {
        "en": "Result:",
        "zh": "结果：",
    },
    "label_base_all": {
        "en": "All bases:",
        "zh": "所有进制：",
    },
    "label_base_binary": {
        "en": "Binary (2):",
        "zh": "二进制 (2)：",
    },
    "label_base_octal": {
        "en": "Octal (8):",
        "zh": "八进制 (8)：",
    },
    "label_base_decimal": {
        "en": "Decimal (10):",
        "zh": "十进制 (10)：",
    },
    "label_base_hex": {
        "en": "Hex (16):",
        "zh": "十六进制 (16)：",
    },
    "status_base_convert": {
        "en": "{0} (base {1}) = {2} (base {3})",
        "zh": "{0} (进制{1}) = {2} (进制{3})",
    },
    "err_base": {
        "en": "Base Conversion Error",
        "zh": "进制转换错误",
    },
    "msg_base_invalid_input": {
        "en": "Invalid input for the given base.",
        "zh": "输入内容在该进制下无效。",
    },
    "msg_base_invalid_base": {
        "en": "Base must be between 2 and 36.",
        "zh": "进制必须在 2 到 36 之间。",
    },

    # ---- Perpetual Calendar / Date Calculator ----
    "sec_calendar": {
        "en": "Perpetual Calendar",
        "zh": "万年历",
    },
    "label_cal_date": {
        "en": "Date (YYYY-MM-DD):",
        "zh": "日期（年-月-日）：",
    },
    "label_cal_year": {
        "en": "Year:",
        "zh": "年：",
    },
    "label_cal_month": {
        "en": "Month:",
        "zh": "月：",
    },
    "label_cal_day": {
        "en": "Day:",
        "zh": "日：",
    },
    "label_cal_date2": {
        "en": "End date (YYYY-MM-DD):",
        "zh": "结束日期（年-月-日）：",
    },
    "label_cal_year2": {
        "en": "End year:",
        "zh": "结束年：",
    },
    "label_cal_month2": {
        "en": "End month:",
        "zh": "结束月：",
    },
    "label_cal_day2": {
        "en": "End day:",
        "zh": "结束日：",
    },
    "label_cal_add_days": {
        "en": "Add days:",
        "zh": "加上天数：",
    },
    "btn_cal_day_of_week": {
        "en": "Day of Week",
        "zh": "查询星期",
    },
    "btn_cal_diff": {
        "en": "Date Difference",
        "zh": "日期差",
    },
    "btn_cal_add_days": {
        "en": "Add/Subtract Days",
        "zh": "加减天数",
    },
    "btn_cal_today": {
        "en": "Today",
        "zh": "今天",
    },
    "btn_cal_clear": {
        "en": "Clear",
        "zh": "清除",
    },
    "status_cal_day_of_week": {
        "en": "{0}-{1}-{2} is a {3}",
        "zh": "{0}年{1}月{2}日是星期{3}",
    },
    "status_cal_diff": {
        "en": "Days between dates: {0}",
        "zh": "两日期相差：{0} 天",
    },
    "status_cal_add": {
        "en": "{0} + {1} days = {2}",
        "zh": "{0} 加 {1} 天 = {2}",
    },
    "err_cal": {
        "en": "Date Error",
        "zh": "日期错误",
    },
    "msg_cal_invalid_date": {
        "en": "Invalid date. Please check year, month, and day.",
        "zh": "无效日期，请检查年、月、日。",
    },
    "msg_cal_invalid_input": {
        "en": "Invalid input. Please enter valid numbers.",
        "zh": "无效输入，请输入有效数字。",
    },
    "msg_cal_date_range": {
        "en": "Year must be 1-9999, Month 1-12, Day 1-31.",
        "zh": "年份1-9999，月份1-12，日期1-31。",
    },

    # ---- Implicit Function Plotting ----
    "sec_implicit": {
        "en": "Implicit Mode f(x,y)=0",
        "zh": "隐函数模式 f(x,y)=0",
    },
    "btn_enable_implicit": {
        "en": "Enable implicit curve",
        "zh": "启用隐函数曲线",
    },
    "label_implicit_expr": {
        "en": "f(x,y) =",
        "zh": "f(x,y) =",
    },
    "label_implicit_resolution": {
        "en": "Resolution:",
        "zh": "分辨率：",
    },
    "msg_enter_implicit_expr": {
        "en": "Please enter an implicit equation f(x,y) = 0.",
        "zh": "请输入隐函数方程 f(x,y) = 0。",
    },
    "msg_implicit_empty": {
        "en": "Implicit curve expression cannot be empty.",
        "zh": "隐函数曲线表达式不能为空。",
    },
    "status_implicit_plotted": {
        "en": "Implicit curve plotted: f(x,y)=0 [{0}×{1} grid]",
        "zh": "隐函数曲线已绘制：f(x,y)=0 [{0}×{1} 网格]",
    },
    "implicit_curve_label": {
        "en": "Implicit: {0} = 0",
        "zh": "隐函数：{0} = 0",
    },

    # ---- Probability Calculator ----
    "sec_probability": {
        "en": "Probability Calculator",
        "zh": "概率计算器",
    },
    "label_prob_n": {
        "en": "n:",
        "zh": "n：",
    },
    "label_prob_r": {
        "en": "r:",
        "zh": "r：",
    },
    "label_prob_k": {
        "en": "k:",
        "zh": "k：",
    },
    "label_prob_p": {
        "en": "p (0-1):",
        "zh": "概率p (0-1)：",
    },
    "label_prob_pa": {
        "en": "P(A):",
        "zh": "P(A)：",
    },
    "label_prob_pb": {
        "en": "P(B):",
        "zh": "P(B)：",
    },
    "label_prob_pa_and_b": {
        "en": "P(A∩B):",
        "zh": "P(A∩B)：",
    },
    "label_prob_pb_given_a": {
        "en": "P(B|A):",
        "zh": "P(B|A)：",
    },
    "label_prob_pb_given_not_a": {
        "en": "P(B|A'):",
        "zh": "P(B|A')：",
    },
    "label_prob_pa_given_b": {
        "en": "P(A|B):",
        "zh": "P(A|B)：",
    },
    "label_prob_lambda": {
        "en": "λ (lambda):",
        "zh": "λ (lambda)：",
    },
    "label_prob_pop_n": {
        "en": "N (population):",
        "zh": "N (总体)：",
    },
    "label_prob_pop_k": {
        "en": "K (successes):",
        "zh": "K (成功数)：",
    },
    "label_prob_sample_n": {
        "en": "n (sample):",
        "zh": "n (样本)：",
    },
    "label_prob_sample_k": {
        "en": "k (observed):",
        "zh": "k (观测)：",
    },
    "btn_prob_combo": {
        "en": "C(n,r)",
        "zh": "组合C(n,r)",
    },
    "btn_prob_perm": {
        "en": "P(n,r)",
        "zh": "排列P(n,r)",
    },
    "btn_prob_union": {
        "en": "P(A∪B)",
        "zh": "P(A∪B)",
    },
    "btn_prob_intersect": {
        "en": "P(A∩B)",
        "zh": "P(A∩B)",
    },
    "btn_prob_complement": {
        "en": "P(A')",
        "zh": "P(A')",
    },
    "btn_prob_conditional": {
        "en": "P(A|B)",
        "zh": "P(A|B)",
    },
    "btn_prob_bayes": {
        "en": "Bayes P(A|B)",
        "zh": "贝叶斯P(A|B)",
    },
    "btn_prob_binom_pmf": {
        "en": "P(X=k)",
        "zh": "P(X=k)",
    },
    "btn_prob_binom_cdf": {
        "en": "P(X≤k)",
        "zh": "P(X≤k)",
    },
    "btn_prob_poisson": {
        "en": "Poisson P(X=k)",
        "zh": "泊松P(X=k)",
    },
    "btn_prob_geometric": {
        "en": "Geometric P(X=k)",
        "zh": "几何P(X=k)",
    },
    "btn_prob_hypergeo": {
        "en": "Hypergeo P(X=k)",
        "zh": "超几何P(X=k)",
    },
    "btn_prob_clear": {
        "en": "Clear",
        "zh": "清除",
    },
    "label_prob_mode_combo": {
        "en": "Mode: Combinatorics",
        "zh": "模式：组合数学",
    },
    "label_prob_mode_event": {
        "en": "Mode: Event Probability",
        "zh": "模式：事件概率",
    },
    "label_prob_mode_bayes": {
        "en": "Mode: Bayes Theorem",
        "zh": "模式：贝叶斯定理",
    },
    "label_prob_mode_binomial": {
        "en": "Mode: Binomial Distribution",
        "zh": "模式：二项分布",
    },
    "label_prob_mode_poisson": {
        "en": "Mode: Poisson Distribution",
        "zh": "模式：泊松分布",
    },
    "label_prob_mode_geometric": {
        "en": "Mode: Geometric Distribution",
        "zh": "模式：几何分布",
    },
    "label_prob_mode_hypergeo": {
        "en": "Mode: Hypergeometric Distribution",
        "zh": "模式：超几何分布",
    },
    "label_prob_independent": {
        "en": "Independent events",
        "zh": "独立事件",
    },
    "status_prob_combo": {
        "en": "C({0}, {1}) = {2}",
        "zh": "C({0}, {1}) = {2}",
    },
    "status_prob_perm": {
        "en": "P({0}, {1}) = {2}",
        "zh": "P({0}, {1}) = {2}",
    },
    "status_prob_union": {
        "en": "P(A∪B) = {0}",
        "zh": "P(A∪B) = {0}",
    },
    "status_prob_intersect": {
        "en": "P(A∩B) = {0}",
        "zh": "P(A∩B) = {0}",
    },
    "status_prob_complement": {
        "en": "P(A') = {0}",
        "zh": "P(A') = {0}",
    },
    "status_prob_conditional": {
        "en": "P(A|B) = {0}",
        "zh": "P(A|B) = {0}",
    },
    "status_prob_bayes": {
        "en": "P(A|B) = {0}\nP(B|A)={1}, P(A)={2}, P(B)={3}",
        "zh": "P(A|B) = {0}\nP(B|A)={1}, P(A)={2}, P(B)={3}",
    },
    "status_prob_binom_pmf": {
        "en": "P(X={2}) = {0}  [Binomial({1}, p={3})]",
        "zh": "P(X={2}) = {0}  [二项({1}, p={3})]",
    },
    "status_prob_binom_cdf": {
        "en": "P(X≤{2}) = {0}  [Binomial({1}, p={3})]",
        "zh": "P(X≤{2}) = {0}  [二项({1}, p={3})]",
    },
    "status_prob_poisson": {
        "en": "P(X={1}) = {0}  [Poisson(λ={2})]",
        "zh": "P(X={1}) = {0}  [泊松(λ={2})]",
    },
    "status_prob_geometric": {
        "en": "P(X={1}) = {0}  [Geometric(p={2})]",
        "zh": "P(X={1}) = {0}  [几何(p={2})]",
    },
    "status_prob_hypergeo": {
        "en": "P(X={3}) = {0}  [Hypergeo(N={1}, K={2}, n={4})]",
        "zh": "P(X={3}) = {0}  [超几何(N={1}, K={2}, n={4})]",
    },
    "err_prob": {
        "en": "Probability Error",
        "zh": "概率错误",
    },
    "msg_prob_invalid_n": {
        "en": "Please enter a valid non-negative integer for n.",
        "zh": "请输入有效的非负整数 n。",
    },
    "msg_prob_invalid_r": {
        "en": "Please enter a valid non-negative integer for r (r ≤ n).",
        "zh": "请输入有效的非负整数 r（r ≤ n）。",
    },
    "msg_prob_invalid_p": {
        "en": "Please enter a valid probability p (0 ≤ p ≤ 1).",
        "zh": "请输入有效的概率 p（0 ≤ p ≤ 1）。",
    },
    "msg_prob_invalid_pa_pb": {
        "en": "Please enter valid probabilities P(A) and P(B) (0 to 1).",
        "zh": "请输入有效的概率 P(A) 和 P(B)（0 到 1）。",
    },
    "msg_prob_invalid_bayes": {
        "en": "Please enter valid values for P(B|A), P(A), and P(B|A').",
        "zh": "请输入有效的 P(B|A)、P(A) 和 P(B|A')。",
    },
    "msg_prob_pb_zero": {
        "en": "P(B) cannot be zero for conditional probability.",
        "zh": "P(B) 不能为零（条件概率分母）。",
    },

    # ---- Finance Calculator ----
    "sec_finance": {
        "en": "Finance Calculator",
        "zh": "金融计算器",
    },
    "label_fin_loan_principal": {
        "en": "Loan Amount",
        "zh": "贷款金额",
    },
    "label_fin_loan_rate": {
        "en": "Annual Rate (%)",
        "zh": "年利率 (%)",
    },
    "label_fin_loan_months": {
        "en": "Months",
        "zh": "期数（月）",
    },
    "btn_fin_loan_calc": {
        "en": "Calculate Loan",
        "zh": "计算贷款",
    },
    "btn_fin_loan_schedule": {
        "en": "Amortization",
        "zh": "还款计划",
    },
    "label_fin_fv_pv": {
        "en": "Amount",
        "zh": "金额",
    },
    "label_fin_compound_rate": {
        "en": "Annual Rate (%)",
        "zh": "年利率 (%)",
    },
    "label_fin_compound_years": {
        "en": "Years",
        "zh": "年数",
    },
    "label_fin_compound_n": {
        "en": "Compounds/Year",
        "zh": "每年复利次数",
    },
    "btn_fin_fv": {
        "en": "Future Value",
        "zh": "计算终值",
    },
    "btn_fin_pv": {
        "en": "Present Value",
        "zh": "计算现值",
    },
    "label_fin_npv_rate": {
        "en": "Discount Rate (%)",
        "zh": "折现率 (%)",
    },
    "label_fin_npv_flows": {
        "en": "Cash Flows (comma)",
        "zh": "现金流（逗号分隔）",
    },
    "btn_fin_npv": {
        "en": "NPV",
        "zh": "净现值",
    },
    "btn_fin_irr": {
        "en": "IRR",
        "zh": "内部收益率",
    },
    "label_fin_depr_cost": {
        "en": "Cost",
        "zh": "资产原值",
    },
    "label_fin_depr_salvage": {
        "en": "Salvage Value",
        "zh": "残值",
    },
    "label_fin_depr_life": {
        "en": "Useful Life (years)",
        "zh": "使用寿命（年）",
    },
    "btn_fin_depr_sl": {
        "en": "Straight-Line",
        "zh": "直线折旧",
    },
    "btn_fin_depr_ddb": {
        "en": "Double Declining",
        "zh": "双倍余额递减",
    },
    "label_fin_bond_face": {
        "en": "Face Value",
        "zh": "面值",
    },
    "label_fin_bond_coupon": {
        "en": "Coupon Rate (%)",
        "zh": "票面利率 (%)",
    },
    "label_fin_bond_yield": {
        "en": "Yield (%)",
        "zh": "收益率 (%)",
    },
    "label_fin_bond_years": {
        "en": "Years to Maturity",
        "zh": "到期年限",
    },
    "btn_fin_bond_price": {
        "en": "Bond Price",
        "zh": "债券价格",
    },
    "label_fin_retire_monthly": {
        "en": "Monthly Contribution",
        "zh": "每月定投",
    },
    "label_fin_retire_rate": {
        "en": "Annual Return (%)",
        "zh": "年回报率 (%)",
    },
    "label_fin_retire_years": {
        "en": "Years",
        "zh": "年数",
    },
    "label_fin_retire_current": {
        "en": "Current Savings",
        "zh": "当前存款",
    },
    "btn_fin_retire": {
        "en": "Calculate Savings",
        "zh": "计算储蓄",
    },
    "status_fin_loan": {
        "en": "Monthly Payment: {0:.2f}\nTotal Payment: {1:.2f}\nTotal Interest: {2:.2f}",
        "zh": "月供: {0:.2f}\n还款总额: {1:.2f}\n总利息: {2:.2f}",
    },
    "status_fin_fv": {
        "en": "Future Value: {0:.6g}",
        "zh": "终值: {0:.6g}",
    },
    "status_fin_pv": {
        "en": "Present Value: {0:.6g}",
        "zh": "现值: {0:.6g}",
    },
    "status_fin_npv": {
        "en": "NPV: {0:.6g}",
        "zh": "净现值: {0:.6g}",
    },
    "status_fin_irr": {
        "en": "IRR: {0:.6g}%",
        "zh": "内部收益率: {0:.6g}%",
    },
    "status_fin_depr_sl": {
        "en": "Annual Depreciation: {0:.2f}\nMonthly Depreciation: {1:.2f}",
        "zh": "年折旧额: {0:.2f}\n月折旧额: {1:.2f}",
    },
    "status_fin_bond": {
        "en": "Bond Price: {0:.6g}",
        "zh": "债券价格: {0:.6g}",
    },
    "status_fin_retire": {
        "en": "Future Value: {0:.2f}\nTotal Contributions: {1:.2f}\nTotal Interest: {2:.2f}",
        "zh": "终值: {0:.2f}\n总投入: {1:.2f}\n总收益: {2:.2f}",
    },
    "err_finance": {
        "en": "Finance Error",
        "zh": "金融计算错误",
    },
    "msg_fin_invalid_input": {
        "en": "Please enter valid numeric values.",
        "zh": "请输入有效的数值。",
    },
    "msg_fin_invalid_flows": {
        "en": "Please enter at least 2 comma-separated cash flows.",
        "zh": "请输入至少2个逗号分隔的现金流。",
    },
    "msg_fin_depr_invalid": {
        "en": "Salvage value must be less than cost, and useful life > 0.",
        "zh": "残值必须小于原值，使用寿命须大于0。",
    },
    "btn_mat_add": {
        "en": "A + B",
        "zh": "A + B",
    },
    "btn_mat_sub": {
        "en": "A - B",
        "zh": "A - B",
    },
    "btn_mat_mul": {
        "en": "A * B",
        "zh": "A × B",
    },
    "btn_mat_det": {
        "en": "det(A)",
        "zh": "det(A)",
    },
    "btn_mat_inv": {
        "en": "inv(A)",
        "zh": "inv(A)",
    },
    "btn_mat_trans": {
        "en": "A^T",
        "zh": "A^T",
    },
    "btn_mat_rank": {
        "en": "rank(A)",
        "zh": "rank(A)",
    },
    "btn_mat_rref": {
        "en": "rref(A)",
        "zh": "rref(A)",
    },
    "btn_mat_eigen": {
        "en": "eig(A)",
        "zh": "eig(A)",
    },
    "btn_mat_clear": {
        "en": "Clear",
        "zh": "清除",
    },
    "btn_complex_add": {
        "en": "z1 + z2",
        "zh": "z1 + z2",
    },
    "btn_complex_sub": {
        "en": "z1 - z2",
        "zh": "z1 - z2",
    },
    "btn_complex_mul": {
        "en": "z1 * z2",
        "zh": "z1 × z2",
    },
    "btn_complex_div": {
        "en": "z1 / z2",
        "zh": "z1 / z2",
    },
    "btn_complex_pow": {
        "en": "z1 ^ z2",
        "zh": "z1 ^ z2",
    },
    "btn_complex_sin": {
        "en": "sin(z)",
        "zh": "sin(z)",
    },
    "btn_complex_cos": {
        "en": "cos(z)",
        "zh": "cos(z)",
    },
    "btn_complex_tan": {
        "en": "tan(z)",
        "zh": "tan(z)",
    },
    "btn_complex_exp": {
        "en": "exp(z)",
        "zh": "exp(z)",
    },
    "btn_complex_ln": {
        "en": "ln(z)",
        "zh": "ln(z)",
    },
    "btn_complex_sqrt": {
        "en": "sqrt(z)",
        "zh": "sqrt(z)",
    },
    "btn_complex_abs": {
        "en": "|z|",
        "zh": "|z|",
    },
    "btn_complex_conj": {
        "en": "conj(z)",
        "zh": "conj(z)",
    },
    "btn_complex_re": {
        "en": "Re(z)",
        "zh": "Re(z)",
    },
    "btn_complex_im": {
        "en": "Im(z)",
        "zh": "Im(z)",
    },
    "mat_title_add": {
        "en": "A + B",
        "zh": "A + B",
    },
    "mat_title_sub": {
        "en": "A - B",
        "zh": "A - B",
    },
    "mat_title_mul": {
        "en": "A * B",
        "zh": "A × B",
    },
    "mat_title_det": {
        "en": "det(A)",
        "zh": "det(A)",
    },
    "mat_title_inv": {
        "en": "inv(A)",
        "zh": "inv(A)",
    },
    "mat_title_trans": {
        "en": "A^T (Transpose)",
        "zh": "A^T (转置)",
    },
    "mat_title_rank": {
        "en": "rank(A)",
        "zh": "rank(A)",
    },
    "mat_title_rref": {
        "en": "RREF(A)",
        "zh": "RREF(A)",
    },
    "mat_title_eigen": {
        "en": "Eigenvalues & Eigenvectors",
        "zh": "特征值和特征向量",
    },
    "mat_eigen_header": {
        "en": "Eigenvalues:",
        "zh": "特征值:",
    },
    "mat_eigen_vec_header": {
        "en": "Eigenvectors (columns):",
        "zh": "特征向量 (列):",
    },
    "mat_result_det": {
        "en": "det(A) = {0:.10g}",
        "zh": "det(A) = {0:.10g}",
    },
    "mat_result_rank": {
        "en": "rank(A) = {0}",
        "zh": "rank(A) = {0}",
    },
    "mat_result_rref": {
        "en": "Rank = {0}",
        "zh": "Rank = {0}",
    },
    "complex_result_abs": {
        "en": "|z| = {0:.10g}",
        "zh": "|z| = {0:.10g}",
    },
    "complex_result_conj": {
        "en": "conj(z) = {0}",
        "zh": "conj(z) = {0}",
    },
    "complex_result_re": {
        "en": "Re(z) = {0:.10g}",
        "zh": "Re(z) = {0:.10g}",
    },
    "complex_result_im": {
        "en": "Im(z) = {0:.10g}",
        "zh": "Im(z) = {0:.10g}",
    },
    "complex_result_error": {
        "en": "Error",
        "zh": "错误",
    },

    # ---- CSV Data Import & Scatter Plot ----
    "sec_data_import": {
        "en": "Data Import & Scatter Plot",
        "zh": "数据导入与散点图",
    },
    "btn_import_csv": {
        "en": "Import CSV",
        "zh": "导入CSV",
    },
    "btn_plot_data": {
        "en": "Plot Data",
        "zh": "绘制数据",
    },
    "btn_fit_trendline": {
        "en": "Fit Trendline",
        "zh": "拟合趋势线",
    },
    "btn_clear_data": {
        "en": "Clear Data",
        "zh": "清除数据",
    },
    "btn_export_data_plot": {
        "en": "Export Plot",
        "zh": "导出图表",
    },
    "label_x_column": {
        "en": "X column",
        "zh": "X列",
    },
    "label_y_column": {
        "en": "Y column",
        "zh": "Y列",
    },
    "label_chart_type": {
        "en": "Chart type",
        "zh": "图表类型",
    },
    "chart_scatter": {
        "en": "Scatter",
        "zh": "散点图",
    },
    "chart_line": {
        "en": "Line",
        "zh": "折线图",
    },
    "chart_bar": {
        "en": "Bar",
        "zh": "柱状图",
    },
    "status_data_imported": {
        "en": "Imported {0} data points from {1}",
        "zh": "已从 {1} 导入 {0} 个数据点",
    },
    "status_data_plotted": {
        "en": "Plotted {0} data points ({1})",
        "zh": "已绘制 {0} 个数据点（{1}）",
    },
    "status_trendline_fit": {
        "en": "Trendline: {0} (R²={1:.6f})",
        "zh": "趋势线：{0}（R²={1:.6f}）",
    },
    "err_no_data": {
        "en": "No data to plot. Import a CSV file first.",
        "zh": "没有可绘制的数据，请先导入CSV文件。",
    },
    "err_csv_parse": {
        "en": "Failed to parse CSV file: {0}",
        "zh": "解析CSV文件失败：{0}",
    },
    "err_invalid_column": {
        "en": "Invalid column index.",
        "zh": "列索引无效。",
    },
    "msg_data_stats": {
        "en": "Data Statistics for column \"{0}\":\n  Count = {1}\n  Mean = {2:.10g}\n  Std Dev = {3:.10g}\n  Min = {4:.10g}\n  Max = {5:.10g}\n  Median = {6:.10g}",
        "zh": "数据列 \"{0}\" 统计：\n  数量 = {1}\n  均值 = {2:.10g}\n  标准差 = {3:.10g}\n  最小值 = {4:.10g}\n  最大值 = {5:.10g}\n  中位数 = {6:.10g}",
    },
    "trendline_linear": {
        "en": "y = {0:.6g}x + {1:.6g}",
        "zh": "y = {0:.6g}x + {1:.6g}",
    },
    "trendline_quadratic": {
        "en": "y = {0:.6g}x² + {1:.6g}x + {2:.6g}",
        "zh": "y = {0:.6g}x² + {1:.6g}x + {2:.6g}",
    },
    "trendline_exponential": {
        "en": "y = {0:.6g}·e^({1:.6g}x)",
        "zh": "y = {0:.6g}·e^({1:.6g}x)",
    },
    "trendline_power": {
        "en": "y = {0:.6g}·x^{1:.6g}",
        "zh": "y = {0:.6g}·x^{1:.6g}",
    },
    "trendline_logarithmic": {
        "en": "y = {0:.6g}·ln(x) + {1:.6g}",
        "zh": "y = {0:.6g}·ln(x) + {1:.6g}",
    },
    "label_trendline_type": {
        "en": "Trendline",
        "zh": "趋势线类型",
    },
    "trend_none": {
        "en": "None",
        "zh": "无",
    },
    "trend_linear": {
        "en": "Linear",
        "zh": "线性",
    },
    "trend_quadratic": {
        "en": "Quadratic",
        "zh": "二次",
    },
    "trend_exponential": {
        "en": "Exponential",
        "zh": "指数",
    },
    "trend_power": {
        "en": "Power",
        "zh": "幂",
    },
    "trend_logarithmic": {
        "en": "Logarithmic",
        "zh": "对数",
    },
    "label_delimiter": {
        "en": "Delimiter",
        "zh": "分隔符",
    },
    "delim_comma": {
        "en": "Comma",
        "zh": "逗号",
    },
    "delim_tab": {
        "en": "Tab",
        "zh": "制表符",
    },
    "delim_semicolon": {
        "en": "Semicolon",
        "zh": "分号",
    },
    "delim_space": {
        "en": "Space",
        "zh": "空格",
    },
    "label_has_header": {
        "en": "Has header row",
        "zh": "包含标题行",
    },
    "label_data_preview": {
        "en": "Data preview ({0} rows):",
        "zh": "数据预览（{0}行）：",
    },

    # ---- Volume of Revolution Calculator ----
    "sec_volume": {
        "en": "Volume of Revolution",
        "zh": "旋转体体积",
    },
    "label_vol_method": {
        "en": "Method:",
        "zh": "方法：",
    },
    "vol_method_disk": {
        "en": "Disk (x-axis)",
        "zh": "圆盘法 (绕x轴)",
    },
    "vol_method_washer": {
        "en": "Washer (x-axis)",
        "zh": "垫圈法 (绕x轴)",
    },
    "vol_method_shell": {
        "en": "Shell (y-axis)",
        "zh": "壳法 (绕y轴)",
    },
    "label_vol_fx": {
        "en": "f(x) =",
        "zh": "f(x) =",
    },
    "label_vol_gx": {
        "en": "g(x) =",
        "zh": "g(x) =",
    },
    "label_vol_interval": {
        "en": "Interval [a, b]:",
        "zh": "区间 [a, b]：",
    },
    "btn_vol_compute": {
        "en": "Compute Volume",
        "zh": "计算体积",
    },
    "status_vol_disk": {
        "en": "Disk method: V = π∫[{0},{1}] [f(x)]² dx = {2}",
        "zh": "圆盘法：V = π∫[{0},{1}] [f(x)]² dx = {2}",
    },
    "status_vol_washer": {
        "en": "Washer method: V = π∫[{0},{1}] ([f(x)]²-[g(x)]²) dx = {2}",
        "zh": "垫圈法：V = π∫[{0},{1}] ([f(x)]²-[g(x)]²) dx = {2}",
    },
    "status_vol_shell": {
        "en": "Shell method: V = 2π∫[{0},{1}] x·f(x) dx = {2}",
        "zh": "壳法：V = 2π∫[{0},{1}] x·f(x) dx = {2}",
    },
    "err_vol": {
        "en": "Volume Error",
        "zh": "体积计算错误",
    },
    "msg_vol_enter_fx": {
        "en": "Please enter an f(x) expression.",
        "zh": "请输入 f(x) 表达式。",
    },
    "msg_vol_enter_gx": {
        "en": "Please enter a g(x) expression for the washer method.",
        "zh": "请输入垫圈法所需的 g(x) 表达式。",
    },
    "msg_vol_invalid_interval": {
        "en": "Invalid interval. a must be less than b.",
        "zh": "区间无效，a 必须小于 b。",
    },
    "msg_vol_failed": {
        "en": "Could not compute volume.\n{0}",
        "zh": "无法计算体积。\n{0}",
    },
    # ---- Direction Field / Vector Field ----
    "sec_direction_field": {
        "en": "Direction Field (dy/dx = f(x,y))",
        "zh": "方向场 (dy/dx = f(x,y))",
    },
    "label_df_expr": {
        "en": "dy/dx =",
        "zh": "dy/dx =",
    },
    "label_df_grid": {
        "en": "Grid:",
        "zh": "网格：",
    },
    "label_df_arrows": {
        "en": "Arrows:",
        "zh": "箭头数：",
    },
    "label_df_sol_ic": {
        "en": "Solution ICs (x0,y0 pairs):",
        "zh": "解曲线初值 (x0,y0 对)：",
    },
    "btn_df_plot": {
        "en": "Plot Direction Field",
        "zh": "绘制方向场",
    },
    "btn_df_clear": {
        "en": "Clear",
        "zh": "清除",
    },
    "status_df_plotted": {
        "en": "Direction field plotted: {0}×{1} grid, {2} solution curve(s)",
        "zh": "方向场已绘制：{0}×{1} 网格，{2} 条解曲线",
    },
    "err_df": {
        "en": "Direction Field Error",
        "zh": "方向场错误",
    },
    "msg_df_invalid_expr": {
        "en": "Please enter a valid dy/dx expression using x and y.",
        "zh": "请输入有效的 dy/dx 表达式（使用 x 和 y）。",
    },
    "msg_df_invalid_grid": {
        "en": "Grid size must be between 5 and 50.",
        "zh": "网格大小必须在 5 到 50 之间。",
    },
    "msg_df_plot_failed": {
        "en": "Could not plot direction field.\n{0}",
        "zh": "无法绘制方向场。\n{0}",
    },
    "df_preset_decay": {
        "en": "Exponential decay (-y)",
        "zh": "指数衰减 (-y)",
    },
    "df_preset_logistic": {
        "en": "Logistic growth (y*(1-y))",
        "zh": "逻辑斯蒂增长 (y*(1-y))",
    },
    "df_preset_harmonic": {
        "en": "Harmonic (-y-sin(x))",
        "zh": "简谐运动 (-y-sin(x))",
    },
    "df_preset_predprey": {
        "en": "Predator-prey (x*y-0.5*x, -x*y+y)",
        "zh": "捕食者-猎物 (x*y-0.5*x, -x*y+y)",
    },
    "df_preset_vanderpol": {
        "en": "Van der Pol (y-(y^3)/3+x)",
        "zh": "范德波尔 (y-(y^3)/3+x)",
    },
    "df_preset_lotka": {
        "en": "Lotka-Volterra (x*(1-y), y*(x-1))",
        "zh": "Lotka-Volterra (x*(1-y), y*(x-1))",
    },

    # --- Custom Function Definition ---
    "sec_custom_func": {
        "en": "Custom Function Definition",
        "zh": "自定义函数",
    },
    "label_custom_func_name": {
        "en": "f",
        "zh": "f",
    },
    "btn_custom_func_define": {
        "en": "Define",
        "zh": "定义",
    },
    "btn_custom_func_delete": {
        "en": "Delete",
        "zh": "删除",
    },
    "btn_custom_func_clear": {
        "en": "Clear All",
        "zh": "清除全部",
    },
    "label_custom_func_defined": {
        "en": "Defined",
        "zh": "已定义",
    },
    "label_custom_func_none": {
        "en": "No custom functions defined",
        "zh": "暂无自定义函数",
    },
    "msg_custom_func_enter_name_body": {
        "en": "Please enter both function name and body expression.",
        "zh": "请输入函数名和表达式。",
    },
    "msg_custom_func_enter_name": {
        "en": "Please enter a function name to delete.",
        "zh": "请输入要删除的函数名。",
    },
    "msg_custom_func_error": {
        "en": "Could not define function: {0}",
        "zh": "无法定义函数：{0}",
    },
    "msg_custom_func_not_found": {
        "en": "Function not found.",
        "zh": "未找到该函数。",
    },
    "err_custom_func": {
        "en": "Custom Function Error",
        "zh": "自定义函数错误",
    },

    # --- Laplace Transform ---
    "sec_laplace": {
        "en": "Laplace Transform",
        "zh": "拉普拉斯变换",
    },
    "label_laplace_expr": {
        "en": "Expression f(t) or F(s):",
        "zh": "表达式 f(t) 或 F(s)：",
    },
    "label_laplace_param": {
        "en": "s or t:",
        "zh": "s 或 t：",
    },
    "btn_laplace_forward": {
        "en": "L{f(t)}",
        "zh": "L{f(t)}",
    },
    "btn_laplace_inverse": {
        "en": "L⁻¹{F(s)}",
        "zh": "L⁻¹{F(s)}",
    },
    "laplace_empty_expr": {
        "en": "Enter an expression for the Laplace transform.",
        "zh": "请输入拉普拉斯变换的表达式。",
    },
    "laplace_invalid_param": {
        "en": "Enter a valid positive parameter value.",
        "zh": "请输入有效的正参数值。",
    },

    # --- Calculation History ---
    "sec_history": {
        "en": "Calculation History",
        "zh": "计算历史",
    },
    "label_history_empty": {
        "en": "No history entries",
        "zh": "暂无历史记录",
    },
    "label_history_entries": {
        "en": "Recent calculations",
        "zh": "最近的计算",
    },
    "btn_history_clear": {
        "en": "Clear History",
        "zh": "清除历史",
    },
    "btn_history_use_last": {
        "en": "Use Last Expression",
        "zh": "使用上次表达式",
    },

    "sec_volume_presets": {
        "en": "Volume Presets",
        "zh": "体积预设",
    },
    "vol_preset_sphere": {
        "en": "Sphere (r=1)",
        "zh": "球体 (r=1)",
    },
    "vol_preset_cone": {
        "en": "Cone (h=1, r=1)",
        "zh": "圆锥 (h=1, r=1)",
    },
    "vol_preset_cylinder": {
        "en": "Cylinder (h=1, r=1)",
        "zh": "圆柱 (h=1, r=1)",
    },
    "vol_preset_torus": {
        "en": "Torus (R=2, r=0.5)",
        "zh": "圆环 (R=2, r=0.5)",
    },

    # --- Data Interpolation ---
    "sec_interpolation": {
        "en": "Data Interpolation",
        "zh": "数据插值",
    },
    "label_interp_method": {
        "en": "Method:",
        "zh": "方法：",
    },
    "interp_method_linear": {
        "en": "Linear",
        "zh": "线性插值",
    },
    "interp_method_lagrange": {
        "en": "Polynomial (Lagrange)",
        "zh": "多项式 (拉格朗日)",
    },
    "interp_method_newton": {
        "en": "Polynomial (Newton)",
        "zh": "多项式 (牛顿)",
    },
    "interp_method_spline": {
        "en": "Cubic Spline",
        "zh": "三次样条",
    },
    "interp_method_akima": {
        "en": "Akima Spline",
        "zh": "Akima 样条",
    },
    "label_interp_data": {
        "en": "Data points (x,y):",
        "zh": "数据点 (x,y)：",
    },
    "label_interp_data_hint": {
        "en": "e.g. 0,1; 1,4; 2,9; 3,16",
        "zh": "如 0,1; 1,4; 2,9; 3,16",
    },
    "label_interp_eval_x": {
        "en": "Evaluate at x =",
        "zh": "在 x = 处求值",
    },
    "btn_interp_compute": {
        "en": "Interpolate",
        "zh": "插值计算",
    },
    "btn_interp_plot": {
        "en": "Plot",
        "zh": "绘图",
    },
    "btn_interp_clear": {
        "en": "Clear",
        "zh": "清除",
    },
    "label_interp_result": {
        "en": "Result:",
        "zh": "结果：",
    },
    "label_interp_formula": {
        "en": "Formula:",
        "zh": "公式：",
    },
    "status_interp_ok": {
        "en": "f({0}) = {1}",
        "zh": "f({0}) = {1}",
    },
    "status_interp_plotted": {
        "en": "Interpolation plotted ({0} points, {1} method)",
        "zh": "已绘制插值曲线（{0} 个点，{1} 方法）",
    },
    "err_interp": {
        "en": "Interpolation Error",
        "zh": "插值错误",
    },
    "msg_interp_need_points": {
        "en": "Please enter at least 2 data points.",
        "zh": "请至少输入 2 个数据点。",
    },
    "msg_interp_invalid_format": {
        "en": "Invalid data format. Use: x1,y1; x2,y2; ...",
        "zh": "数据格式无效。请使用：x1,y1; x2,y2; ...",
    },
    "msg_interp_duplicate_x": {
        "en": "Duplicate x values are not allowed.",
        "zh": "不允许重复的 x 值。",
    },
    "msg_interp_x_not_sorted": {
        "en": "Warning: x values are not in ascending order. They will be sorted automatically.",
        "zh": "警告：x 值未按升序排列，将自动排序。",
    },
    # Numerical method comparison strings
    "sec_ode_compare": {
        "en": "ODE Method Comparison",
        "zh": "ODE数值方法对比",
    },
    "label_compare_expr": {
        "en": "dy/dx =",
        "zh": "dy/dx =",
    },
    "btn_compare_methods": {
        "en": "Compare Methods",
        "zh": "对比方法",
    },
    "btn_compare_plot": {
        "en": "Plot Comparison",
        "zh": "绘制对比图",
    },
    "status_compare_plotted": {
        "en": "Method comparison plotted ({0} methods, {1} steps each)",
        "zh": "方法对比已绘制（{0} 种方法，每种 {1} 步）",
    },
    "err_compare": {
        "en": "Method Comparison Error",
        "zh": "方法对比错误",
    },
    "msg_compare_invalid_steps": {
        "en": "Number of steps must be between 1 and 100000.",
        "zh": "步数必须在 1 到 100000 之间。",
    },
    "compare_euler": {
        "en": "Euler (1st order)",
        "zh": "欧拉法（1阶）",
    },
    "compare_improved_euler": {
        "en": "Improved Euler (2nd order)",
        "zh": "改进欧拉法（2阶）",
    },
    "compare_midpoint": {
        "en": "Midpoint (2nd order)",
        "zh": "中点法（2阶）",
    },
    "compare_rk4": {
        "en": "RK4 (4th order)",
        "zh": "RK4（4阶）",
    },
    "compare_rkf45": {
        "en": "RKF45 (Adaptive)",
        "zh": "RKF45（自适应）",
    },
}


def t(key: str, *args: object) -> str:
    """Return the translated string for *key* in the current locale.

    Positional *args* are interpolated via ``str.format()`` using
    ``{0}``, ``{1}``, etc.  If the key is not found, the key itself is
    returned.  If the current locale is not present for a key the English
    fallback is tried; if even that is missing the key is returned.
    """
    entry = STRINGS.get(key)
    if entry is None:
        return key

    text = entry.get(CURRENT_LANG, entry.get("en", key))

    if args:
        try:
            text = text.format(*args)
        except (IndexError, KeyError, ValueError):
            pass

    return text
