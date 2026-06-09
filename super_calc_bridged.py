#!/usr/bin/env python3
"""
Super Function Graphing Calculator - GUI

A full-featured function graphing calculator using the Bridge Pattern:
  GUI (Tkinter + Matplotlib)  ->  calc_bridge.py (ctypes)  ->  calc_core.dll (C)

Features:
  - Multi-curve function plotting with custom colors
  - Numerical derivative & integral computation
  - Equation solving (root finding)
  - Preset functions library
  - Adjustable coordinate ranges, step size, and tolerances
  - Export plot as PNG
  - Factorial support (!)
  - 3D function plotting for z=f(x,y) in a separate window
  - Parameter detection and dynamic input
  - Input panel with quick buttons (all C-core supported operations)
  - Coordinate marking on click and by x input
  - Polar coordinate plotting r(theta) with preset library
"""

import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, List
import math
import re
import csv
import os
import statistics

try:
    import matplotlib
except ImportError as e:
    print(f"[ERROR] matplotlib is required but not installed.", file=sys.stderr)
    print("Please install: pip install numpy matplotlib", file=sys.stderr)
    sys.exit(1)

# Dynamically select backend: try TkAgg first, fallback to Agg for headless environments
try:
    import tkinter
    matplotlib.use("TkAgg")
except (ImportError, RuntimeError):
    matplotlib.use("Agg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

try:
    import numpy as np
except ImportError as e:
    print(f"[ERROR] numpy is required but not installed.", file=sys.stderr)
    print("Please install: pip install numpy matplotlib", file=sys.stderr)
    sys.exit(1)

from calc_bridge import CalcEngine
from locale_strings import t, CURRENT_LANG


def _get_lang():
    return CURRENT_LANG


# ---------------------------------------------------------------------------
#  Constants
# ---------------------------------------------------------------------------
MIN_PLOT_POINTS = 10
MAX_PLOT_POINTS = 5000
MIN_3D_POINTS = 10
MAX_3D_POINTS = 120
DEFAULT_3D_POINTS = 50
PRESET_FUNCTIONS = {
    "sin(x)":              "sin(x)",
    "cos(x)":              "cos(x)",
    "tan(x)":              "tan(x)",
    "x^2 (square)":        "x^2",
    "x^3 (cube)":          "x^3",
    "sqrt(x)":             "sqrt(x)",
    "ln(x)":               "ln(x)",
    "log10(x)":            "log(x)",
    "exp(x)":              "exp(x)",
    "1/x":                 "1/x",
    "abs(x)":              "abs(x)",
    "sin(x) + cos(x)":     "sin(x)+cos(x)",
    "x*sin(x)":            "x*sin(x)",
    "exp(-x)*sin(2*pi*x)": "exp(-x)*sin(2*pi*x)",
    "x^2/2 - cos(x)":      "x^2/2-cos(x)",
    "x! (factorial)":      "x!",
    "3D: x^2+y^2":         "x^2+y^2",
    "3D: sin(x)*cos(y)":   "sin(x)*cos(y)",
    "3D: sin(sqrt(x^2+y^2))": "sin(sqrt(x^2+y^2))",
    "FFT: sin(2*pi*x) + 0.5*sin(6*pi*x)": "sin(2*pi*x)+0.5*sin(6*pi*x)",
    "FFT: sin(5*x) + cos(10*x)": "sin(5*x)+cos(10*x)",
    "floor(x) (staircase)": "floor(x)",
    "ceil(x) (staircase)": "ceil(x)",
    "x mod 1 (sawtooth)": "x mod 1",
    "sin(x) mod 1": "sin(x) mod 1",
}

PARAMETRIC_PRESETS = {
    "Circle":              ("cos(t)", "sin(t)", "0", "2*pi"),
    "Ellipse":             ("2*cos(t)", "sin(t)", "0", "2*pi"),
    "Lissajous (3:2)":     ("sin(3*t)", "cos(2*t)", "0", "2*pi"),
    "Lissajous (5:4)":     ("sin(5*t)", "cos(4*t)", "0", "2*pi"),
    "Spiral":              ("t*cos(t)", "t*sin(t)", "0", "6*pi"),
    "Cardioid":            ("2*(1-cos(t))*cos(t)", "2*(1-cos(t))*sin(t)", "0", "2*pi"),
    "Trefoil Knot":        ("sin(2*t)+2*sin(4*t)", "cos(2*t)-2*cos(4*t)", "0", "2*pi"),
    "Butterfly Curve":     ("sin(t)*(exp(cos(t))-2*cos(4*t)-sin(t/12)^5)", "cos(t)*(exp(cos(t))-2*cos(4*t)-sin(t/12)^5)", "0", "12*pi"),
    "Heart":               ("16*sin(t)^3", "13*cos(t)-5*cos(2*t)-2*cos(3*t)-cos(4*t)", "0", "2*pi"),
    "Star (5-pointed)":    ("cos(t)+0.5*cos(3*t)+0.3*cos(5*t)", "sin(t)+0.5*sin(3*t)+0.3*sin(5*t)", "0", "2*pi"),
}

POLAR_PRESETS = {
    "Circle (r=1)":              ("1", "0", "2*pi"),
    "Circle (r=2)":              ("2", "0", "2*pi"),
    "Cardioid":                  ("1+cos(theta)", "0", "2*pi"),
    "Lemniscate":                ("sqrt(2*cos(2*theta))", "0", "2*pi"),
    "Three-leaf Clover":         ("sin(3*theta)", "0", "2*pi"),
    "Four-leaf Clover":          ("sin(2*theta)", "0", "2*pi"),
    "Rose (5 petals)":           ("cos(5*theta)", "0", "2*pi"),
    "Rose (3 petals)":           ("cos(3*theta)", "0", "2*pi"),
    "Archimedean Spiral":        ("theta", "0", "6*pi"),
    "Logarithmic Spiral":        ("exp(0.2*theta)", "0", "4*pi"),
    "Limaçon":                   ("1+2*cos(theta)", "0", "2*pi"),
    "Butterfly":                 ("sin(theta)*(exp(cos(theta))-2*cos(4*theta))", "0", "2*pi"),
}

ODE_PRESETS = {
    "Exponential decay (-y)":           ("-y", "0", "1", "5", "200"),
    "Simple harmonic (-y)":             ("-y", "0", "0", "6.2832", "500"),
    "Damped oscillator (-0.1*y-sin(x))": ("-0.1*y-sin(x)", "0", "1", "30", "1000"),
    "Logistic growth (y*(1-y))":        ("y*(1-y)", "0", "0.01", "10", "500"),
    "Newton cooling (-0.5*(y-20))":     ("-0.5*(y-20)", "0", "100", "20", "500"),
    "Autonomous (y-y^2)":              ("y-y^2", "0", "0.5", "10", "500"),
    "Van der Pol mu=1":                 ("y-((y^3)/3)+x", "0", "0.5", "20", "2000"),
    "Predator-prey (-x*y+0.5*x)":      ("-x*y+0.5*x", "0", "4", "20", "1000"),
}

DEFAULT_COLORS = [
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728",
    "#9467bd", "#8c564b", "#e377c2", "#7f7f7f",
    "#bcbd22", "#17becf",
]

CMAP_3D_OPTIONS = [
    'viridis', 'plasma', 'inferno', 'magma', 'cividis',
    'coolwarm', 'twilight', 'turbo',
]

PARAM_PATTERN = re.compile(r'\b([a-zA-Z]+)\b')
KNOWN_FUNCTIONS = {'sin', 'cos', 'tan', 'log', 'ln', 'exp', 'sqrt', 'abs', 'floor', 'ceil'}
KNOWN_CONSTANTS = {'pi', 'e'}
INDEPENDENT_VARS = {'x', 'y', 't'}  # variables used by the engine, not parameters

def _detect_parameters_static(expr: str) -> list:
    params = set()
    expr_lower = expr.lower()
    for func in KNOWN_FUNCTIONS:
        expr_lower = re.sub(r'\b' + func + r'\b', '', expr_lower)
    for const in KNOWN_CONSTANTS:
        expr_lower = re.sub(r'\b' + const + r'\b', '', expr_lower)
    for match in PARAM_PATTERN.finditer(expr_lower):
        word = match.group(1)
        if len(word) == 1 and word not in INDEPENDENT_VARS:
            params.add(word)
        elif len(word) > 1 and word not in KNOWN_FUNCTIONS and word not in KNOWN_CONSTANTS:
            params.add(word)
    return sorted(list(params))


# ---------------------------------------------------------------------------
#  Curve data model
# ---------------------------------------------------------------------------
class CurveModel:
    """Holds the configuration for a single plotted curve."""
    __slots__ = ("expression", "color", "linewidth", "linestyle",
                 "visible", "label", "is_3d", "parameters",
                 "is_parametric", "x_param_expr", "y_param_expr",
                 "is_polar", "r_param_expr",
                 "is_implicit", "implicit_expr", "implicit_resolution")

    def __init__(self, expr, color, label="", lw=2, ls="-",
                 is_parametric=False, x_param_expr="", y_param_expr="",
                 is_polar=False, r_param_expr="",
                 is_implicit=False, implicit_expr="", implicit_resolution=200):
        self.is_parametric = is_parametric
        self.x_param_expr = x_param_expr
        self.y_param_expr = y_param_expr
        self.is_polar = is_polar
        self.r_param_expr = r_param_expr
        self.is_implicit = is_implicit
        self.implicit_expr = implicit_expr
        self.implicit_resolution = implicit_resolution
        if is_parametric:
            self.expression = f"x(t)={x_param_expr}, y(t)={y_param_expr}"
            self.is_3d = False
        elif is_polar:
            self.expression = f"r(theta)={r_param_expr}"
            self.is_3d = False
        elif is_implicit:
            self.expression = implicit_expr
            self.is_3d = False
        else:
            self.expression = expr
            self.is_3d = self._detect_3d(expr)
        self.color = color
        self.linewidth = lw
        self.linestyle = ls
        self.visible = True
        self.label = label or self.expression
        self.parameters = self._detect_parameters(
            expr if not is_parametric and not is_polar and not is_implicit else
            (x_param_expr + " " + y_param_expr if is_parametric else
             r_param_expr if is_polar else implicit_expr))

    def _detect_3d(self, expr: str) -> bool:
        expr_lower = expr.lower()
        has_x = bool(re.search(r'\bx\b', expr_lower))
        has_y = bool(re.search(r'\by\b', expr_lower))
        return has_x and has_y

    def _detect_parameters(self, expr: str) -> list:
        return _detect_parameters_static(expr)


# ---------------------------------------------------------------------------
#  Main Application
# ---------------------------------------------------------------------------
class SuperCalcApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(t("win_title"))
        self.root.geometry("520x900")
        self.root.minsize(450, 700)
        self.root.configure(bg="#1e1e2e")

        self.curves: List[CurveModel] = []
        self.color_index = 0
        self.x_min = -10.0
        self.x_max = 10.0
        self.y_min = -10.0
        self.y_max = 10.0
        self.z_min = -10.0
        self.z_max = 10.0
        self.step_size = 0.05
        self.n_pts_3d = DEFAULT_3D_POINTS
        self.grid_on = True
        self.param_values = {}
        self.marked_points = []
        self.auto_mark_point = None
        self.root_markers = []
        self.intersection_marks = []  # list of (x, y) tuples for curve intersections
        self.tangent_data = []   # list of dicts: {x0, y0, slope, expr}
        self.normal_data = []    # list of dicts: {x0, y0, slope, expr}

        # Separate windows for 2D and 3D plots
        self.window_2d = None
        self.fig_2d = None
        self.ax_2d = None
        self.canvas_2d = None
        self.toolbar_2d = None

        self.window_3d = None
        self.fig_3d = None
        self.ax_3d = None
        self.canvas_3d = None
        self.toolbar_3d = None

        # FFT spectrum window
        self.window_fft = None
        self.fig_fft = None
        self.ax_fft_amp = None
        self.ax_fft_phase = None
        self.canvas_fft = None
        self.toolbar_fft = None

        self.root.protocol("WM_DELETE_WINDOW", self._on_main_close)
        self._build_ui()
        self._add_curve("sin(x)")

    def _on_main_close(self):
        """Clean up child plot windows before exiting."""
        if self.window_2d is not None and self.window_2d.winfo_exists():
            self.window_2d.destroy()
        if self.window_3d is not None and self.window_3d.winfo_exists():
            self.window_3d.destroy()
        if self.window_fft is not None and self.window_fft.winfo_exists():
            self.window_fft.destroy()
        self.root.destroy()

    # ------------------------------------------------------------------
    #  UI Construction
    # ------------------------------------------------------------------
    def _build_ui(self):
        self._build_control_panel(self.root)

    def _build_control_panel(self, parent):
        canvas = tk.Canvas(parent, bg="#1e1e2e", highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=canvas.yview)
        scroll_frame = ttk.Frame(canvas, style="Dark.TFrame")

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        def _on_mousewheel(event):
            import platform
            if platform.system() == "Darwin":
                # macOS: event.delta is ±1
                canvas.yview_scroll(int(-1 * event.delta), "units")
            else:
                # Windows: event.delta is ±120
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _on_mousewheel_linux(event):
            # Linux (Button-4 = scroll up, Button-5 = scroll down)
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")

        canvas.bind("<MouseWheel>", _on_mousewheel)
        canvas.bind("<Button-4>", _on_mousewheel_linux)
        canvas.bind("<Button-5>", _on_mousewheel_linux)

        # --- Expression Input ---
        frm_expr = ttk.LabelFrame(scroll_frame, text=t("sec_function_input"),
                                  style="Dark.TLabelframe")
        frm_expr.pack(fill=tk.X, padx=8, pady=(8, 4))

        ttk.Label(frm_expr, text=t("label_expr"),
                  style="Dark.TLabel").pack(anchor=tk.W, padx=6, pady=(6, 0))
        
        input_row = ttk.Frame(frm_expr, style="Dark.TFrame")
        input_row.pack(fill=tk.X, padx=6, pady=2)
        
        self.entry_expr = ttk.Entry(input_row, font=("Consolas", 12), width=28)
        self.entry_expr.pack(side=tk.LEFT, padx=(0, 4))
        self.entry_expr.insert(0, "sin(x)")
        self.entry_expr.bind("<Return>", lambda e: self._on_plot())
        
        ttk.Button(input_row, text="📝", width=2,
                   command=self._open_input_panel).pack(side=tk.RIGHT)
        
        self.entry_expr.bind("<FocusIn>", lambda e: self._update_param_inputs())

        btn_row = ttk.Frame(frm_expr, style="Dark.TFrame")
        btn_row.pack(fill=tk.X, padx=6, pady=4)
        ttk.Button(btn_row, text=t("btn_add_curve"),
                   command=self._on_add_curve).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(btn_row, text=t("btn_plot"),
                   command=self._on_plot).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_row, text=t("btn_clear_all"),
                   command=self._on_clear_all).pack(side=tk.LEFT, padx=4)

        # --- Parametric Mode ---
        self._var_parametric = tk.BooleanVar(value=False)
        frm_param = ttk.LabelFrame(scroll_frame, text=t("sec_parametric"),
                                   style="Dark.TLabelframe")
        frm_param.pack(fill=tk.X, padx=8, pady=4)

        ptog = ttk.Frame(frm_param, style="Dark.TFrame")
        ptog.pack(fill=tk.X, padx=6, pady=(4, 2))
        ttk.Checkbutton(ptog, text=t("btn_enable_parametric"),
                        variable=self._var_parametric,
                        command=self._on_parametric_toggle).pack(side=tk.LEFT)

        self._frame_param_inputs = ttk.Frame(frm_param, style="Dark.TFrame")
        self._frame_param_inputs.pack(fill=tk.X, padx=6, pady=2)

        pr1 = ttk.Frame(self._frame_param_inputs, style="Dark.TFrame")
        pr1.pack(fill=tk.X, pady=2)
        ttk.Label(pr1, text=t("label_xt"), style="Dark.TLabel", width=6).pack(side=tk.LEFT)
        self._var_x_param = tk.StringVar(value="cos(t)")
        ttk.Entry(pr1, textvariable=self._var_x_param, width=22).pack(side=tk.LEFT, padx=2)

        pr2 = ttk.Frame(self._frame_param_inputs, style="Dark.TFrame")
        pr2.pack(fill=tk.X, pady=2)
        ttk.Label(pr2, text=t("label_yt"), style="Dark.TLabel", width=6).pack(side=tk.LEFT)
        self._var_y_param = tk.StringVar(value="sin(t)")
        ttk.Entry(pr2, textvariable=self._var_y_param, width=22).pack(side=tk.LEFT, padx=2)

        pr3 = ttk.Frame(self._frame_param_inputs, style="Dark.TFrame")
        pr3.pack(fill=tk.X, pady=2)
        ttk.Label(pr3, text=t("label_t_range"), style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_t_min = tk.StringVar(value="0")
        ttk.Entry(pr3, textvariable=self._var_t_min, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Label(pr3, text=t("label_to"), style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_t_max = tk.StringVar(value="2*pi")
        ttk.Entry(pr3, textvariable=self._var_t_max, width=8).pack(side=tk.LEFT, padx=2)

        # Parametric presets
        pr4 = ttk.Frame(self._frame_param_inputs, style="Dark.TFrame")
        pr4.pack(fill=tk.X, pady=(4, 2))
        ttk.Label(pr4, text=t("label_preset"), style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_param_preset = tk.StringVar()
        param_combo = ttk.Combobox(pr4, textvariable=self._var_param_preset,
                                   values=list(PARAMETRIC_PRESETS.keys()),
                                   state="readonly", font=("Consolas", 10), width=18)
        param_combo.pack(side=tk.LEFT, padx=4)
        param_combo.bind("<<ComboboxSelected>>",
                         lambda e: self._on_parametric_preset(self._var_param_preset.get()))

        # Initially hide parametric inputs
        self._on_parametric_toggle()

        # --- Polar Mode ---
        self._var_polar = tk.BooleanVar(value=False)
        frm_polar = ttk.LabelFrame(scroll_frame, text=t("sec_polar"),
                                   style="Dark.TLabelframe")
        frm_polar.pack(fill=tk.X, padx=8, pady=4)

        ptog2 = ttk.Frame(frm_polar, style="Dark.TFrame")
        ptog2.pack(fill=tk.X, padx=6, pady=(4, 2))
        ttk.Checkbutton(ptog2, text=t("btn_enable_polar"),
                        variable=self._var_polar,
                        command=self._on_polar_toggle).pack(side=tk.LEFT)

        self._frame_polar_inputs = ttk.Frame(frm_polar, style="Dark.TFrame")
        self._frame_polar_inputs.pack(fill=tk.X, padx=6, pady=2)

        pr1p = ttk.Frame(self._frame_polar_inputs, style="Dark.TFrame")
        pr1p.pack(fill=tk.X, pady=2)
        ttk.Label(pr1p, text=t("label_rtheta"), style="Dark.TLabel", width=8).pack(side=tk.LEFT)
        self._var_r_param = tk.StringVar(value="1")
        ttk.Entry(pr1p, textvariable=self._var_r_param, width=22).pack(side=tk.LEFT, padx=2)

        pr3p = ttk.Frame(self._frame_polar_inputs, style="Dark.TFrame")
        pr3p.pack(fill=tk.X, pady=2)
        ttk.Label(pr3p, text=t("label_theta_range"), style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_theta_min = tk.StringVar(value="0")
        ttk.Entry(pr3p, textvariable=self._var_theta_min, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Label(pr3p, text=t("label_to"), style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_theta_max = tk.StringVar(value="2*pi")
        ttk.Entry(pr3p, textvariable=self._var_theta_max, width=8).pack(side=tk.LEFT, padx=2)

        # Polar presets
        pr4p = ttk.Frame(self._frame_polar_inputs, style="Dark.TFrame")
        pr4p.pack(fill=tk.X, pady=(4, 2))
        ttk.Label(pr4p, text=t("label_preset"), style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_polar_preset = tk.StringVar()
        polar_combo = ttk.Combobox(pr4p, textvariable=self._var_polar_preset,
                                   values=list(POLAR_PRESETS.keys()),
                                   state="readonly", font=("Consolas", 10), width=18)
        polar_combo.pack(side=tk.LEFT, padx=4)
        polar_combo.bind("<<ComboboxSelected>>",
                         lambda e: self._on_polar_preset(self._var_polar_preset.get()))

        # Initially hide polar inputs
        self._on_polar_toggle()

        # --- Implicit Mode ---
        self._var_implicit = tk.BooleanVar(value=False)
        frm_implicit = ttk.LabelFrame(scroll_frame, text=t("sec_implicit"),
                                      style="Dark.TLabelframe")
        frm_implicit.pack(fill=tk.X, padx=8, pady=4)

        itog = ttk.Frame(frm_implicit, style="Dark.TFrame")
        itog.pack(fill=tk.X, padx=6, pady=(4, 2))
        ttk.Checkbutton(itog, text=t("btn_enable_implicit"),
                        variable=self._var_implicit,
                        command=self._on_implicit_toggle).pack(side=tk.LEFT)

        self._frame_implicit_inputs = ttk.Frame(frm_implicit, style="Dark.TFrame")
        self._frame_implicit_inputs.pack(fill=tk.X, padx=6, pady=2)

        ir1 = ttk.Frame(self._frame_implicit_inputs, style="Dark.TFrame")
        ir1.pack(fill=tk.X, pady=2)
        ttk.Label(ir1, text=t("label_implicit_expr"), style="Dark.TLabel", width=8).pack(side=tk.LEFT)
        self._var_implicit_expr = tk.StringVar(value="x^2+y^2-1")
        ttk.Entry(ir1, textvariable=self._var_implicit_expr, width=22).pack(side=tk.LEFT, padx=2)

        ir2 = ttk.Frame(self._frame_implicit_inputs, style="Dark.TFrame")
        ir2.pack(fill=tk.X, pady=2)
        ttk.Label(ir2, text=t("label_implicit_resolution"), style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_implicit_res = tk.StringVar(value="200")
        ttk.Entry(ir2, textvariable=self._var_implicit_res, width=8).pack(side=tk.LEFT, padx=2)

        # Implicit presets
        ir3 = ttk.Frame(self._frame_implicit_inputs, style="Dark.TFrame")
        ir3.pack(fill=tk.X, pady=(4, 2))
        ttk.Label(ir3, text=t("label_preset"), style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_implicit_preset = tk.StringVar()
        implicit_preset_list = [
            "Circle: x^2+y^2-1",
            "Ellipse: x^2/4+y^2-1",
            "Hyperbola: x^2-y^2-1",
            "Parabola: y-x^2",
            "Lemniscate: (x^2+y^2)^2-(x^2-y^2)",
            "Cardioid: (x^2+y^2-x)^2-(x^2+y^2)",
            "Folium: x^3+y^3-3*x*y",
            "Cubic: y^2-x^3+x",
        ]
        implicit_combo = ttk.Combobox(ir3, textvariable=self._var_implicit_preset,
                                      values=implicit_preset_list,
                                      state="readonly", font=("Consolas", 10), width=20)
        implicit_combo.pack(side=tk.LEFT, padx=4)
        implicit_combo.bind("<<ComboboxSelected>>",
                            lambda e: self._on_implicit_preset(self._var_implicit_preset.get()))

        # Initially hide implicit inputs
        self._on_implicit_toggle()

        # --- Parameter Inputs ---
        self.frm_params = ttk.LabelFrame(scroll_frame, text=t("sec_parameters"),
                                         style="Dark.TLabelframe")
        self.frm_params.pack(fill=tk.X, padx=8, pady=4)
        self.param_widgets = {}
        ttk.Label(self.frm_params, text=t("label_no_params"),
                  style="Dark.TLabel").pack(padx=6, pady=8)

        # --- Presets ---
        frm_preset = ttk.LabelFrame(scroll_frame, text=t("sec_preset"),
                                    style="Dark.TLabelframe")
        frm_preset.pack(fill=tk.X, padx=8, pady=4)

        self.preset_var = tk.StringVar()
        combo = ttk.Combobox(frm_preset, textvariable=self.preset_var,
                             values=list(PRESET_FUNCTIONS.keys()),
                             state="readonly", font=("Consolas", 10))
        combo.pack(fill=tk.X, padx=6, pady=4)
        combo.bind("<<ComboboxSelected>>",
                   lambda e: self._on_preset(self.preset_var.get()))

        # --- Curve List ---
        frm_curves = ttk.LabelFrame(scroll_frame, text=t("sec_curves"),
                                    style="Dark.TLabelframe")
        frm_curves.pack(fill=tk.X, padx=8, pady=4)
        self.listbox_curves = tk.Listbox(
            frm_curves, bg="#313244", fg="#cdd6f4",
            selectbackground="#89b4fa", selectforeground="#1e1e2e",
            font=("Consolas", 10), height=6, exportselection=False)
        self.listbox_curves.pack(fill=tk.X, padx=6, pady=4)
        ttk.Button(frm_curves, text=t("btn_remove"),
                   command=self._on_remove_curve).pack(padx=6, pady=(0, 4))
        ttk.Button(frm_curves, text=t("btn_find_intersections"),
                   command=self._show_intersection_dialog).pack(padx=6, pady=(0, 4))

        # --- Range ---
        frm_range = ttk.LabelFrame(scroll_frame, text=t("sec_range"),
                                   style="Dark.TLabelframe")
        frm_range.pack(fill=tk.X, padx=8, pady=4)

        grid = ttk.Frame(frm_range, style="Dark.TFrame")
        grid.pack(fill=tk.X, padx=6, pady=4)
        range_fields = [
            (t("range_xmin"), "x_min"), (t("range_xmax"), "x_max"),
            (t("range_ymin"), "y_min"), (t("range_ymax"), "y_max"),
            (t("range_zmin"), "z_min"), (t("range_zmax"), "z_max"),
        ]
        for col, (lbl, var_attr) in enumerate(range_fields):
            ttk.Label(grid, text=lbl, style="Dark.TLabel").grid(
                row=0, column=col, padx=2, sticky=tk.W)
            v = tk.StringVar(value=str(getattr(self, var_attr)))
            e = ttk.Entry(grid, textvariable=v, width=7)
            e.grid(row=1, column=col, padx=2)
            setattr(self, f"_var_{var_attr}", v)

        range_row2 = ttk.Frame(frm_range, style="Dark.TFrame")
        range_row2.pack(fill=tk.X, padx=6, pady=(0, 4))
        ttk.Label(range_row2, text=t("label_step"),
                  style="Dark.TLabel").pack(side=tk.LEFT, padx=(6, 2))
        self._var_step = tk.StringVar(value=str(self.step_size))
        ttk.Entry(range_row2, textvariable=self._var_step, width=6).pack(
            side=tk.LEFT)
        ttk.Button(range_row2, text=t("btn_apply"),
                    command=self._on_apply_range).pack(side=tk.RIGHT, padx=6)

        self._var_grid = tk.BooleanVar(value=True)
        ttk.Checkbutton(range_row2, text=t("label_grid"),
                         variable=self._var_grid).pack(
            side=tk.LEFT, padx=(12, 0))

        ttk.Label(range_row2, text=t("label_3d_grid"), style="Dark.TLabel").pack(side=tk.LEFT, padx=(12, 0))
        self._var_3d_res = tk.StringVar(value=str(DEFAULT_3D_POINTS))
        ttk.Entry(range_row2, textvariable=self._var_3d_res, width=5).pack(side=tk.LEFT)

        # --- Calculus ---
        frm_calc = ttk.LabelFrame(scroll_frame, text=t("sec_calculus"),
                                  style="Dark.TLabelframe")
        frm_calc.pack(fill=tk.X, padx=8, pady=4)

        row1 = ttk.Frame(frm_calc, style="Dark.TFrame")
        row1.pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(row1, text=t("label_at_x"), style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_diff_x = tk.StringVar(value="0")
        ttk.Entry(row1, textvariable=self._var_diff_x, width=8).pack(
            side=tk.LEFT, padx=4)
        ttk.Button(row1, text=t("btn_deriv"),
                   command=lambda: self._on_derivative()).pack(side=tk.LEFT, padx=2)
        ttk.Button(row1, text=t("btn_deriv2"),
                   command=lambda: self._on_derivative2()).pack(side=tk.LEFT, padx=2)

        row2 = ttk.Frame(frm_calc, style="Dark.TFrame")
        row2.pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(row2, text=t("label_integrate"), style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_int_a = tk.StringVar(value="0")
        ttk.Entry(row2, textvariable=self._var_int_a, width=6).pack(side=tk.LEFT)
        ttk.Label(row2, text=t("label_comma"), style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_int_b = tk.StringVar(value="1")
        ttk.Entry(row2, textvariable=self._var_int_b, width=6).pack(side=tk.LEFT)
        ttk.Label(row2, text=t("label_close_bracket"), style="Dark.TLabel").pack(side=tk.LEFT)
        ttk.Button(row2, text=t("btn_integrate"),
                   command=self._on_integrate).pack(side=tk.LEFT, padx=8)

        row_limit = ttk.Frame(frm_calc, style="Dark.TFrame")
        row_limit.pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(row_limit, text=t("label_limit"), style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_limit_a = tk.StringVar(value="0")
        ttk.Entry(row_limit, textvariable=self._var_limit_a, width=8).pack(
            side=tk.LEFT, padx=4)
        ttk.Button(row_limit, text=t("btn_lim"),
                   command=lambda: self._on_limit(two_sided=True)).pack(side=tk.LEFT, padx=2)
        ttk.Button(row_limit, text=t("btn_left_lim"),
                   command=lambda: self._on_limit(two_sided=False, side="left")).pack(side=tk.LEFT, padx=2)
        ttk.Button(row_limit, text=t("btn_right_lim"),
                   command=lambda: self._on_limit(two_sided=False, side="right")).pack(side=tk.LEFT, padx=2)

        # --- Equation Solver ---
        frm_solve = ttk.LabelFrame(scroll_frame, text=t("sec_solver"),
                                   style="Dark.TLabelframe")
        frm_solve.pack(fill=tk.X, padx=8, pady=4)

        srow1 = ttk.Frame(frm_solve, style="Dark.TFrame")
        srow1.pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(srow1, text=t("label_guess"), style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_guess = tk.StringVar(value="0")
        ttk.Entry(srow1, textvariable=self._var_guess, width=8).pack(
            side=tk.LEFT, padx=2)
        ttk.Label(srow1, text=t("label_range"),
                  style="Dark.TLabel").pack(side=tk.LEFT, padx=(6, 0))
        self._var_solve_a = tk.StringVar(value="-10")
        ttk.Entry(srow1, textvariable=self._var_solve_a, width=6).pack(side=tk.LEFT)
        ttk.Label(srow1, text=t("label_to"), style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_solve_b = tk.StringVar(value="10")
        ttk.Entry(srow1, textvariable=self._var_solve_b, width=6).pack(side=tk.LEFT)

        srow2 = ttk.Frame(frm_solve, style="Dark.TFrame")
        srow2.pack(fill=tk.X, padx=6, pady=2)
        ttk.Button(srow2, text=t("btn_solve_newton"),
                   command=lambda: self._on_solve()).pack(side=tk.LEFT, padx=2)
        ttk.Button(srow2, text=t("btn_solve_bisection"),
                   command=lambda: self._on_solve_bisection()).pack(side=tk.LEFT, padx=2)

        # --- Nonlinear System Solver (2D) ---
        frm_sys = ttk.LabelFrame(scroll_frame, text=t("sec_system"),
                                 style="Dark.TLabelframe")
        frm_sys.pack(fill=tk.X, padx=8, pady=4)

        sysrow1 = ttk.Frame(frm_sys, style="Dark.TFrame")
        sysrow1.pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(sysrow1, text=t("label_sys_f"), style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_sys_f = tk.StringVar(value="x^2+y^2-1")
        ttk.Entry(sysrow1, textvariable=self._var_sys_f, width=20).pack(side=tk.LEFT, padx=4)
        ttk.Label(sysrow1, text=t("label_sys_g"), style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_sys_g = tk.StringVar(value="x-y")
        ttk.Entry(sysrow1, textvariable=self._var_sys_g, width=20).pack(side=tk.LEFT, padx=4)

        sysrow2 = ttk.Frame(frm_sys, style="Dark.TFrame")
        sysrow2.pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(sysrow2, text=t("label_init_guess"), style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_sys_x0 = tk.StringVar(value="0.7")
        ttk.Entry(sysrow2, textvariable=self._var_sys_x0, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Label(sysrow2, text=",", style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_sys_y0 = tk.StringVar(value="0.7")
        ttk.Entry(sysrow2, textvariable=self._var_sys_y0, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Button(sysrow2, text=t("btn_solve_system"),
                   command=self._on_solve_system_2d).pack(side=tk.LEFT, padx=8)

        sysrow3 = ttk.Frame(frm_sys, style="Dark.TFrame")
        sysrow3.pack(fill=tk.X, padx=6, pady=(0, 4))
        ttk.Label(sysrow3, text=t("label_sys_desc"),
                  style="Dark.TLabel").pack(side=tk.LEFT)

        # --- Extremum Finder ---
        frm_extremum = ttk.LabelFrame(scroll_frame, text=t("sec_extremum"),
                                      style="Dark.TLabelframe")
        frm_extremum.pack(fill=tk.X, padx=8, pady=4)

        erow1 = ttk.Frame(frm_extremum, style="Dark.TFrame")
        erow1.pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(erow1, text=t("label_a"), style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_ext_a = tk.StringVar(value="-10")
        ttk.Entry(erow1, textvariable=self._var_ext_a, width=7).pack(side=tk.LEFT, padx=2)
        ttk.Label(erow1, text=t("label_b"), style="Dark.TLabel").pack(side=tk.LEFT, padx=(6, 0))
        self._var_ext_b = tk.StringVar(value="10")
        ttk.Entry(erow1, textvariable=self._var_ext_b, width=7).pack(side=tk.LEFT, padx=2)

        erow2 = ttk.Frame(frm_extremum, style="Dark.TFrame")
        erow2.pack(fill=tk.X, padx=6, pady=2)
        ttk.Button(erow2, text=t("btn_find_min"),
                   command=lambda: self._on_find_extremum(minimum=True)).pack(side=tk.LEFT, padx=2)
        ttk.Button(erow2, text=t("btn_find_max"),
                   command=lambda: self._on_find_extremum(minimum=False)).pack(side=tk.LEFT, padx=2)

        # --- Auto Root Scanner ---
        frm_scan = ttk.LabelFrame(scroll_frame, text=t("sec_scan"),
                                  style="Dark.TLabelframe")
        frm_scan.pack(fill=tk.X, padx=8, pady=4)

        srow = ttk.Frame(frm_scan, style="Dark.TFrame")
        srow.pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(srow, text=t("label_scan_desc"),
                  style="Dark.TLabel").pack(side=tk.LEFT, padx=2)
        ttk.Button(srow, text=t("btn_scan_roots"),
                   command=self._on_scan_roots).pack(side=tk.RIGHT, padx=2)

        # --- Coordinate Marking ---
        frm_mark = ttk.LabelFrame(scroll_frame, text=t("sec_mark"),
                                  style="Dark.TLabelframe")
        frm_mark.pack(fill=tk.X, padx=8, pady=4)

        ttk.Label(frm_mark, text=t("label_mark_hint"),
                  style="Dark.TLabel").pack(anchor=tk.W, padx=6, pady=(6, 0))

        mark_row = ttk.Frame(frm_mark, style="Dark.TFrame")
        mark_row.pack(fill=tk.X, padx=6, pady=2)
        self._var_mark_x = tk.StringVar(value="")
        ttk.Entry(mark_row, textvariable=self._var_mark_x, width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(mark_row, text=t("btn_mark_point"),
                   command=self._on_mark_point).pack(side=tk.LEFT, padx=2)
        ttk.Button(mark_row, text=t("btn_clear_marks"),
                   command=self._clear_marks).pack(side=tk.LEFT, padx=2)

        # --- Tangent & Normal Lines ---
        frm_tan = ttk.LabelFrame(scroll_frame, text=t("sec_tangent"),
                                 style="Dark.TLabelframe")
        frm_tan.pack(fill=tk.X, padx=8, pady=4)

        trow_tan = ttk.Frame(frm_tan, style="Dark.TFrame")
        trow_tan.pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(trow_tan, text=t("label_tan_at_x"), style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_tan_x = tk.StringVar(value="0")
        ttk.Entry(trow_tan, textvariable=self._var_tan_x, width=8).pack(side=tk.LEFT, padx=4)
        ttk.Button(trow_tan, text=t("btn_draw_tangent"),
                   command=self._on_draw_tangent).pack(side=tk.LEFT, padx=2)
        ttk.Button(trow_tan, text=t("btn_draw_normal"),
                   command=self._on_draw_normal).pack(side=tk.LEFT, padx=2)
        ttk.Button(trow_tan, text=t("btn_clear_lines"),
                   command=self._clear_tangent_normal).pack(side=tk.LEFT, padx=2)

        # --- Arc Length ---
        frm_arc = ttk.LabelFrame(scroll_frame, text=t("sec_arc"),
                                 style="Dark.TLabelframe")
        frm_arc.pack(fill=tk.X, padx=8, pady=4)

        arow = ttk.Frame(frm_arc, style="Dark.TFrame")
        arow.pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(arow, text=t("label_arc_uses"),
                  style="Dark.TLabel").pack(side=tk.LEFT, padx=2)
        ttk.Button(arow, text=t("btn_compute_arc"),
                   command=self._on_arc_length).pack(side=tk.RIGHT, padx=2)

        # --- Area Between Curves ---
        frm_area = ttk.LabelFrame(scroll_frame, text=t("sec_area"),
                                  style="Dark.TLabelframe")
        frm_area.pack(fill=tk.X, padx=8, pady=4)

        area_row1 = ttk.Frame(frm_area, style="Dark.TFrame")
        area_row1.pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(area_row1, text=t("label_area_fx"), style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_area_f = tk.StringVar(value="sin(x)")
        ttk.Entry(area_row1, textvariable=self._var_area_f, width=18).pack(
            side=tk.LEFT, padx=4)
        ttk.Label(area_row1, text=t("label_area_gx"), style="Dark.TLabel").pack(
            side=tk.LEFT, padx=(8, 0))
        self._var_area_g = tk.StringVar(value="0")
        ttk.Entry(area_row1, textvariable=self._var_area_g, width=18).pack(
            side=tk.LEFT, padx=4)

        area_row2 = ttk.Frame(frm_area, style="Dark.TFrame")
        area_row2.pack(fill=tk.X, padx=6, pady=(0, 4))
        ttk.Label(area_row2, text=t("label_interval_ab"),
                  style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_area_a = tk.StringVar(value="0")
        ttk.Entry(area_row2, textvariable=self._var_area_a, width=7).pack(
            side=tk.LEFT, padx=2)
        ttk.Label(area_row2, text=t("label_to"), style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_area_b = tk.StringVar(value="pi")
        ttk.Entry(area_row2, textvariable=self._var_area_b, width=7).pack(
            side=tk.LEFT, padx=2)
        ttk.Button(area_row2, text=t("btn_compute_area"),
                   command=self._on_area_between_curves).pack(side=tk.RIGHT, padx=2)

        # --- Function Table ---
        frm_table = ttk.LabelFrame(scroll_frame, text=t("sec_table"),
                                   style="Dark.TLabelframe")
        frm_table.pack(fill=tk.X, padx=8, pady=4)

        trow = ttk.Frame(frm_table, style="Dark.TFrame")
        trow.pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(trow, text=t("label_from"), style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_tbl_from = tk.StringVar(value="-10")
        ttk.Entry(trow, textvariable=self._var_tbl_from, width=7).pack(side=tk.LEFT, padx=2)
        ttk.Label(trow, text=t("label_to2"), style="Dark.TLabel").pack(side=tk.LEFT, padx=(6, 0))
        self._var_tbl_to = tk.StringVar(value="10")
        ttk.Entry(trow, textvariable=self._var_tbl_to, width=7).pack(side=tk.LEFT, padx=2)
        ttk.Label(trow, text=t("label_points"), style="Dark.TLabel").pack(side=tk.LEFT, padx=(6, 0))
        self._var_tbl_n = tk.StringVar(value="21")
        ttk.Entry(trow, textvariable=self._var_tbl_n, width=5).pack(side=tk.LEFT, padx=2)

        trow2 = ttk.Frame(frm_table, style="Dark.TFrame")
        trow2.pack(fill=tk.X, padx=6, pady=(0, 4))
        ttk.Button(trow2, text=t("btn_gen_table"),
                   command=self._on_generate_table).pack(side=tk.LEFT, padx=2)
        ttk.Button(trow2, text=t("btn_export_csv"),
                   command=self._on_export_csv).pack(side=tk.LEFT, padx=2)
        ttk.Button(trow2, text=t("btn_copy_table"),
                   command=self._on_copy_table).pack(side=tk.LEFT, padx=2)

        self._table_data = []   # list of (x, y) tuples
        self._table_expr = ""   # expression used for last table
        self._fft_data = {}     # last FFT result dict

        # --- Fourier Transform & Spectrum ---
        frm_fft = ttk.LabelFrame(scroll_frame, text=t("sec_fft"),
                                 style="Dark.TLabelframe")
        frm_fft.pack(fill=tk.X, padx=8, pady=4)

        fft_row1 = ttk.Frame(frm_fft, style="Dark.TFrame")
        fft_row1.pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(fft_row1, text=t("label_samples"), style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_fft_n = tk.StringVar(value="1024")
        ttk.Entry(fft_row1, textvariable=self._var_fft_n, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Label(fft_row1, text=t("label_fft_uses"),
                  style="Dark.TLabel").pack(side=tk.LEFT, padx=(8, 0))

        fft_row2 = ttk.Frame(frm_fft, style="Dark.TFrame")
        fft_row2.pack(fill=tk.X, padx=6, pady=(0, 4))
        ttk.Button(fft_row2, text=t("btn_compute_fft"),
                   command=self._on_fft_compute).pack(side=tk.LEFT, padx=2)
        ttk.Button(fft_row2, text=t("btn_export_spectrum"),
                   command=self._on_export_fft_csv).pack(side=tk.LEFT, padx=2)

        # --- Taylor Series Expansion ---
        frm_taylor = ttk.LabelFrame(scroll_frame, text=t("sec_taylor"),
                                    style="Dark.TLabelframe")
        frm_taylor.pack(fill=tk.X, padx=8, pady=4)

        trow1 = ttk.Frame(frm_taylor, style="Dark.TFrame")
        trow1.pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(trow1, text=t("label_expand_at"), style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_taylor_a = tk.StringVar(value="0")
        ttk.Entry(trow1, textvariable=self._var_taylor_a, width=8).pack(
            side=tk.LEFT, padx=4)
        ttk.Label(trow1, text=t("label_order"), style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_taylor_order = tk.StringVar(value="5")
        ttk.Entry(trow1, textvariable=self._var_taylor_order, width=5).pack(
            side=tk.LEFT, padx=4)

        trow2 = ttk.Frame(frm_taylor, style="Dark.TFrame")
        trow2.pack(fill=tk.X, padx=6, pady=(0, 4))
        ttk.Button(trow2, text=t("btn_expand_taylor"),
                   command=self._on_taylor_expand).pack(side=tk.LEFT, padx=2)
        ttk.Button(trow2, text=t("btn_plot_taylor"),
                   command=self._on_taylor_plot).pack(side=tk.LEFT, padx=2)

        # --- ODE Solver (RK4) ---
        frm_ode = ttk.LabelFrame(scroll_frame, text=t("sec_ode"),
                                  style="Dark.TLabelframe")
        frm_ode.pack(fill=tk.X, padx=8, pady=4)

        ode_row1 = ttk.Frame(frm_ode, style="Dark.TFrame")
        ode_row1.pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(ode_row1, text=t("label_dydx"), style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_ode_expr = tk.StringVar(value="-y")
        ttk.Entry(ode_row1, textvariable=self._var_ode_expr, width=22).pack(
            side=tk.LEFT, padx=4)

        ode_row2 = ttk.Frame(frm_ode, style="Dark.TFrame")
        ode_row2.pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(ode_row2, text=t("label_x0"), style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_ode_x0 = tk.StringVar(value="0")
        ttk.Entry(ode_row2, textvariable=self._var_ode_x0, width=6).pack(
            side=tk.LEFT, padx=2)
        ttk.Label(ode_row2, text=t("label_y0"), style="Dark.TLabel").pack(side=tk.LEFT, padx=(6, 0))
        self._var_ode_y0 = tk.StringVar(value="1")
        ttk.Entry(ode_row2, textvariable=self._var_ode_y0, width=6).pack(
            side=tk.LEFT, padx=2)
        ttk.Label(ode_row2, text=t("label_xend"), style="Dark.TLabel").pack(side=tk.LEFT, padx=(6, 0))
        self._var_ode_xend = tk.StringVar(value="5")
        ttk.Entry(ode_row2, textvariable=self._var_ode_xend, width=6).pack(
            side=tk.LEFT, padx=2)
        ttk.Label(ode_row2, text=t("label_steps"), style="Dark.TLabel").pack(side=tk.LEFT, padx=(6, 0))
        self._var_ode_steps = tk.StringVar(value="200")
        ttk.Entry(ode_row2, textvariable=self._var_ode_steps, width=6).pack(
            side=tk.LEFT, padx=2)

        ode_row3 = ttk.Frame(frm_ode, style="Dark.TFrame")
        ode_row3.pack(fill=tk.X, padx=6, pady=(0, 4))
        ttk.Button(ode_row3, text=t("btn_solve_ode"),
                   command=self._on_ode_solve).pack(side=tk.LEFT, padx=2)
        ttk.Button(ode_row3, text=t("btn_plot_solution"),
                   command=self._on_ode_plot).pack(side=tk.LEFT, padx=2)

        # ODE presets
        ode_row4 = ttk.Frame(frm_ode, style="Dark.TFrame")
        ode_row4.pack(fill=tk.X, padx=6, pady=(0, 4))
        ttk.Label(ode_row4, text=t("label_preset"), style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_ode_preset = tk.StringVar()
        ode_combo = ttk.Combobox(ode_row4, textvariable=self._var_ode_preset,
                                  values=list(ODE_PRESETS.keys()),
                                  state="readonly", font=("Consolas", 10), width=24)
        ode_combo.pack(side=tk.LEFT, padx=4)
        ode_combo.bind("<<ComboboxSelected>>",
                        lambda e: self._on_ode_preset(self._var_ode_preset.get()))

        self._ode_data = None  # last ODE solution dict (None or dict)
        self._last_reg_result = None  # last regression result dict

        # --- Statistics Calculator ---
        frm_stats = ttk.LabelFrame(scroll_frame, text=t("sec_stats"),
                                    style="Dark.TLabelframe")
        frm_stats.pack(fill=tk.X, padx=8, pady=4)

        stats_row1 = ttk.Frame(frm_stats, style="Dark.TFrame")
        stats_row1.pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(stats_row1, text=t("label_data"),
                  style="Dark.TLabel").pack(anchor=tk.W, padx=2)

        self._var_stats_data = tk.StringVar(value="1, 2, 3, 4, 5, 6, 7, 8, 9, 10")
        stats_entry = ttk.Entry(stats_row1, textvariable=self._var_stats_data, width=36,
                                font=("Consolas", 10))
        stats_entry.pack(fill=tk.X, padx=2, pady=(0, 4))

        stats_row2 = ttk.Frame(frm_stats, style="Dark.TFrame")
        stats_row2.pack(fill=tk.X, padx=6, pady=(0, 4))
        ttk.Button(stats_row2, text=t("btn_compute_stats"),
                   command=self._on_stats_compute).pack(side=tk.LEFT, padx=2)
        ttk.Button(stats_row2, text=t("btn_sort_data"),
                   command=self._on_stats_sort).pack(side=tk.LEFT, padx=2)
        ttk.Button(stats_row2, text=t("btn_plot_histogram"),
                   command=self._on_stats_histogram).pack(side=tk.LEFT, padx=2)
        ttk.Button(stats_row2, text=t("btn_export_csv"),
                   command=self._on_stats_export_csv).pack(side=tk.LEFT, padx=2)

        # --- Statistical Distribution Calculator ---
        try:
            from stat_dist import DISTRIBUTIONS as _STAT_DIST_REGISTRY
            _HAS_STAT_DIST = True
        except ImportError:
            _STAT_DIST_REGISTRY = {}
            _HAS_STAT_DIST = False

        frm_dist = ttk.LabelFrame(scroll_frame, text=t("sec_dist"),
                                  style="Dark.TLabelframe")
        frm_dist.pack(fill=tk.X, padx=8, pady=4)

        drow1 = ttk.Frame(frm_dist, style="Dark.TFrame")
        drow1.pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(drow1, text=t("label_dist_type"),
                  style="Dark.TLabel").pack(side=tk.LEFT, padx=2)
        self._var_dist_type = tk.StringVar(value="normal")
        self._dist_names_map = {}
        _dist_display_names = []
        for _k, _v in _STAT_DIST_REGISTRY.items():
            _dn = _v.get(f"name_{_get_lang()}", _v["name_en"])
            self._dist_names_map[_dn] = _k
            _dist_display_names.append(_dn)
        self._dist_combo = ttk.Combobox(drow1, textvariable=self._var_dist_type,
                                         values=_dist_display_names, width=22,
                                         state="readonly")
        self._dist_combo.pack(side=tk.LEFT, padx=4)
        self._dist_combo.bind("<<ComboboxSelected>>", self._on_dist_type_change)

        self._dist_param_frames = {}
        self._dist_param_vars = {}

        for _dk, _dv in _STAT_DIST_REGISTRY.items():
            _pframe = ttk.Frame(frm_dist, style="Dark.TFrame")
            _pvars = {}
            for _pname, _plabel, _psym, _pdef in _dv["params"]:
                _sv = tk.StringVar(value=str(_pdef))
                _pvars[_pname] = _sv
                ttk.Label(_pframe, text=f"{_psym}=",
                          style="Dark.TLabel").pack(side=tk.LEFT, padx=2)
                ttk.Entry(_pframe, textvariable=_sv, width=6,
                          font=("Consolas", 10)).pack(side=tk.LEFT, padx=2)
            self._dist_param_frames[_dk] = _pframe
            self._dist_param_vars[_dk] = _pvars

        self._on_dist_type_change()

        drow2 = ttk.Frame(frm_dist, style="Dark.TFrame")
        drow2.pack(fill=tk.X, padx=6, pady=(2, 4))

        ttk.Label(drow2, text=t("label_x_value"),
                  style="Dark.TLabel").pack(side=tk.LEFT, padx=2)
        self._var_dist_x = tk.StringVar(value="0")
        ttk.Entry(drow2, textvariable=self._var_dist_x, width=8,
                  font=("Consolas", 10)).pack(side=tk.LEFT, padx=2)
        ttk.Button(drow2, text=t("btn_dist_pdf"),
                   command=self._on_dist_pdf).pack(side=tk.LEFT, padx=2)
        ttk.Button(drow2, text=t("btn_dist_cdf"),
                   command=self._on_dist_cdf).pack(side=tk.LEFT, padx=2)
        ttk.Button(drow2, text=t("btn_dist_ppf"),
                   command=self._on_dist_ppf).pack(side=tk.LEFT, padx=2)
        ttk.Button(drow2, text=t("btn_dist_plot"),
                   command=self._on_dist_plot).pack(side=tk.LEFT, padx=2)
        ttk.Button(drow2, text=t("btn_dist_compare"),
                   command=self._on_dist_compare).pack(side=tk.LEFT, padx=2)

        # --- Curve Fitting / Regression ---
        frm_regression = ttk.LabelFrame(scroll_frame, text=t("sec_regression"),
                                        style="Dark.TLabelframe")
        frm_regression.pack(fill=tk.X, padx=8, pady=4)

        reg_row1 = ttk.Frame(frm_regression, style="Dark.TFrame")
        reg_row1.pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(reg_row1, text=t("label_xdata"),
                  style="Dark.TLabel").pack(anchor=tk.W, padx=2)
        self._var_reg_xdata = tk.StringVar(value="")
        ttk.Entry(reg_row1, textvariable=self._var_reg_xdata, width=36,
                  font=("Consolas", 10)).pack(fill=tk.X, padx=2, pady=(0, 4))

        reg_row1b = ttk.Frame(frm_regression, style="Dark.TFrame")
        reg_row1b.pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(reg_row1b, text=t("label_ydata"),
                  style="Dark.TLabel").pack(anchor=tk.W, padx=2)
        self._var_reg_ydata = tk.StringVar(value="")
        ttk.Entry(reg_row1b, textvariable=self._var_reg_ydata, width=36,
                  font=("Consolas", 10)).pack(fill=tk.X, padx=2, pady=(0, 4))

        reg_row2 = ttk.Frame(frm_regression, style="Dark.TFrame")
        reg_row2.pack(fill=tk.X, padx=6, pady=2)
        ttk.Button(reg_row2, text=t("btn_linear"),
                   command=self._on_reg_linear).pack(side=tk.LEFT, padx=2)
        ttk.Button(reg_row2, text=t("btn_quadratic"),
                   command=self._on_reg_quadratic).pack(side=tk.LEFT, padx=2)
        ttk.Button(reg_row2, text=t("btn_polynomial"),
                   command=self._on_reg_polynomial).pack(side=tk.LEFT, padx=2)

        reg_row3 = ttk.Frame(frm_regression, style="Dark.TFrame")
        reg_row3.pack(fill=tk.X, padx=6, pady=2)
        ttk.Button(reg_row3, text=t("btn_exponential"),
                   command=self._on_reg_exponential).pack(side=tk.LEFT, padx=2)
        ttk.Button(reg_row3, text=t("btn_power"),
                   command=self._on_reg_power).pack(side=tk.LEFT, padx=2)
        ttk.Button(reg_row3, text=t("btn_logarithmic"),
                   command=self._on_reg_logarithmic).pack(side=tk.LEFT, padx=2)

        reg_row4 = ttk.Frame(frm_regression, style="Dark.TFrame")
        reg_row4.pack(fill=tk.X, padx=6, pady=(0, 4))
        ttk.Label(reg_row4, text=t("label_poly_degree"), style="Dark.TLabel").pack(side=tk.LEFT, padx=2)
        self._var_reg_degree = tk.StringVar(value="3")
        ttk.Entry(reg_row4, textvariable=self._var_reg_degree, width=5,
                  font=("Consolas", 10)).pack(side=tk.LEFT, padx=2)
        ttk.Button(reg_row4, text=t("btn_plot_fit"),
                   command=self._on_reg_plot).pack(side=tk.LEFT, padx=(8, 2))

        # --- Matrix Operations ---
        frm_matrix = ttk.LabelFrame(scroll_frame, text=t("sec_matrix"),
                                    style="Dark.TLabelframe")
        frm_matrix.pack(fill=tk.X, padx=8, pady=4)

        mrow1 = ttk.Frame(frm_matrix, style="Dark.TFrame")
        mrow1.pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(mrow1, text=t("label_matrix_a"),
                  style="Dark.TLabel").pack(anchor=tk.W, padx=2)
        self._var_matrix_a = tk.StringVar(value="1,2;3,4")
        ttk.Entry(mrow1, textvariable=self._var_matrix_a, width=36,
                  font=("Consolas", 10)).pack(fill=tk.X, padx=2, pady=(0, 4))

        mrow2 = ttk.Frame(frm_matrix, style="Dark.TFrame")
        mrow2.pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(mrow2, text=t("label_matrix_b"),
                  style="Dark.TLabel").pack(anchor=tk.W, padx=2)
        self._var_matrix_b = tk.StringVar(value="5,6;7,8")
        ttk.Entry(mrow2, textvariable=self._var_matrix_b, width=36,
                  font=("Consolas", 10)).pack(fill=tk.X, padx=2, pady=(0, 4))

        mrow3 = ttk.Frame(frm_matrix, style="Dark.TFrame")
        mrow3.pack(fill=tk.X, padx=6, pady=2)
        ttk.Button(mrow3, text="A + B", command=self._on_matrix_add).pack(side=tk.LEFT, padx=2)
        ttk.Button(mrow3, text="A - B", command=self._on_matrix_sub).pack(side=tk.LEFT, padx=2)
        ttk.Button(mrow3, text="A * B", command=self._on_matrix_mul).pack(side=tk.LEFT, padx=2)
        ttk.Button(mrow3, text="det(A)", command=self._on_matrix_det).pack(side=tk.LEFT, padx=2)

        mrow4 = ttk.Frame(frm_matrix, style="Dark.TFrame")
        mrow4.pack(fill=tk.X, padx=6, pady=2)
        ttk.Button(mrow4, text="inv(A)", command=self._on_matrix_inv).pack(side=tk.LEFT, padx=2)
        ttk.Button(mrow4, text="A^T", command=self._on_matrix_transpose).pack(side=tk.LEFT, padx=2)
        ttk.Button(mrow4, text="rank(A)", command=self._on_matrix_rank).pack(side=tk.LEFT, padx=2)
        ttk.Button(mrow4, text="rref(A)", command=self._on_matrix_rref).pack(side=tk.LEFT, padx=2)

        mrow5 = ttk.Frame(frm_matrix, style="Dark.TFrame")
        mrow5.pack(fill=tk.X, padx=6, pady=(0, 4))
        ttk.Button(mrow5, text="eig(A)", command=self._on_matrix_eigen).pack(side=tk.LEFT, padx=2)
        ttk.Button(mrow5, text="Clear", command=self._on_matrix_clear).pack(side=tk.RIGHT, padx=2)

        self._matrix_result = None

        # --- Complex Number Calculator ---
        frm_complex = ttk.LabelFrame(scroll_frame, text=t("sec_complex"),
                                     style="Dark.TLabelframe")
        frm_complex.pack(fill=tk.X, padx=8, pady=4)

        crow1 = ttk.Frame(frm_complex, style="Dark.TFrame")
        crow1.pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(crow1, text=t("label_z1"), style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_complex_z1 = tk.StringVar(value="1+2i")
        ttk.Entry(crow1, textvariable=self._var_complex_z1, width=15,
                  font=("Consolas", 10)).pack(side=tk.LEFT, padx=2)
        ttk.Label(crow1, text=t("label_z2"), style="Dark.TLabel").pack(side=tk.LEFT, padx=(8, 0))
        self._var_complex_z2 = tk.StringVar(value="3+4i")
        ttk.Entry(crow1, textvariable=self._var_complex_z2, width=15,
                  font=("Consolas", 10)).pack(side=tk.LEFT, padx=2)

        crow2 = ttk.Frame(frm_complex, style="Dark.TFrame")
        crow2.pack(fill=tk.X, padx=6, pady=2)
        ttk.Button(crow2, text="z1 + z2", command=self._on_complex_add).pack(side=tk.LEFT, padx=2)
        ttk.Button(crow2, text="z1 - z2", command=self._on_complex_sub).pack(side=tk.LEFT, padx=2)
        ttk.Button(crow2, text="z1 * z2", command=self._on_complex_mul).pack(side=tk.LEFT, padx=2)
        ttk.Button(crow2, text="z1 / z2", command=self._on_complex_div).pack(side=tk.LEFT, padx=2)
        ttk.Button(crow2, text="z1 ^ z2", command=self._on_complex_pow).pack(side=tk.LEFT, padx=2)

        crow3 = ttk.Frame(frm_complex, style="Dark.TFrame")
        crow3.pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(crow3, text=t("label_single_z"), style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_complex_z = tk.StringVar(value="1+1i")
        ttk.Entry(crow3, textvariable=self._var_complex_z, width=15,
                  font=("Consolas", 10)).pack(side=tk.LEFT, padx=2)

        crow4 = ttk.Frame(frm_complex, style="Dark.TFrame")
        crow4.pack(fill=tk.X, padx=6, pady=2)
        ttk.Button(crow4, text="sin(z)", command=self._on_complex_sin).pack(side=tk.LEFT, padx=2)
        ttk.Button(crow4, text="cos(z)", command=self._on_complex_cos).pack(side=tk.LEFT, padx=2)
        ttk.Button(crow4, text="tan(z)", command=self._on_complex_tan).pack(side=tk.LEFT, padx=2)
        ttk.Button(crow4, text="exp(z)", command=self._on_complex_exp).pack(side=tk.LEFT, padx=2)
        ttk.Button(crow4, text="ln(z)", command=self._on_complex_ln).pack(side=tk.LEFT, padx=2)

        crow5 = ttk.Frame(frm_complex, style="Dark.TFrame")
        crow5.pack(fill=tk.X, padx=6, pady=2)
        ttk.Button(crow5, text="sqrt(z)", command=self._on_complex_sqrt).pack(side=tk.LEFT, padx=2)
        ttk.Button(crow5, text="|z|", command=self._on_complex_abs).pack(side=tk.LEFT, padx=2)
        ttk.Button(crow5, text="conj(z)", command=self._on_complex_conj).pack(side=tk.LEFT, padx=2)
        ttk.Button(crow5, text="Re(z)", command=self._on_complex_real).pack(side=tk.LEFT, padx=2)
        ttk.Button(crow5, text="Im(z)", command=self._on_complex_imag).pack(side=tk.LEFT, padx=2)

        crow6 = ttk.Frame(frm_complex, style="Dark.TFrame")
        crow6.pack(fill=tk.X, padx=6, pady=(0, 4))
        ttk.Label(crow6, text=t("label_result"), style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_complex_result = tk.StringVar(value="")
        ttk.Entry(crow6, textvariable=self._var_complex_result, width=30,
                  font=("Consolas", 10), state="readonly").pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)

        # --- Number Theory Calculator ---
        frm_nt = ttk.LabelFrame(scroll_frame, text=t("sec_number_theory"),
                                style="Dark.TLabelframe")
        frm_nt.pack(fill=tk.X, padx=8, pady=4)

        # Row 1: n input
        nt_row1 = ttk.Frame(frm_nt, style="Dark.TFrame")
        nt_row1.pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(nt_row1, text=t("label_nt_n"), style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_nt_n = tk.StringVar(value="12")
        ttk.Entry(nt_row1, textvariable=self._var_nt_n, width=15,
                  font=("Consolas", 10)).pack(side=tk.LEFT, padx=4)
        ttk.Button(nt_row1, text=t("btn_nt_factorize"),
                   command=self._on_nt_factorize).pack(side=tk.LEFT, padx=2)
        ttk.Button(nt_row1, text=t("btn_nt_is_prime"),
                   command=self._on_nt_is_prime).pack(side=tk.LEFT, padx=2)

        # Row 2: a, b inputs for GCD/LCM
        nt_row2 = ttk.Frame(frm_nt, style="Dark.TFrame")
        nt_row2.pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(nt_row2, text=t("label_nt_a"), style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_nt_a = tk.StringVar(value="12")
        ttk.Entry(nt_row2, textvariable=self._var_nt_a, width=10,
                  font=("Consolas", 10)).pack(side=tk.LEFT, padx=4)
        ttk.Label(nt_row2, text=t("label_nt_b"), style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_nt_b = tk.StringVar(value="18")
        ttk.Entry(nt_row2, textvariable=self._var_nt_b, width=10,
                  font=("Consolas", 10)).pack(side=tk.LEFT, padx=4)
        ttk.Button(nt_row2, text=t("btn_nt_gcd"),
                   command=self._on_nt_gcd).pack(side=tk.LEFT, padx=2)
        ttk.Button(nt_row2, text=t("btn_nt_lcm"),
                   command=self._on_nt_lcm).pack(side=tk.LEFT, padx=2)

        # Row 3: Fibonacci
        nt_row3 = ttk.Frame(frm_nt, style="Dark.TFrame")
        nt_row3.pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(nt_row3, text=t("label_nt_count"), style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_nt_fib_count = tk.StringVar(value="20")
        ttk.Entry(nt_row3, textvariable=self._var_nt_fib_count, width=10,
                  font=("Consolas", 10)).pack(side=tk.LEFT, padx=4)
        ttk.Button(nt_row3, text=t("btn_nt_fibonacci"),
                   command=self._on_nt_fibonacci).pack(side=tk.LEFT, padx=2)
        ttk.Button(nt_row3, text=t("btn_nt_totient"),
                   command=self._on_nt_totient).pack(side=tk.LEFT, padx=2)

        # Row 4: modPow: base^exp mod m
        nt_row4 = ttk.Frame(frm_nt, style="Dark.TFrame")
        nt_row4.pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(nt_row4, text=t("label_nt_base"), style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_nt_modpow_base = tk.StringVar(value="2")
        ttk.Entry(nt_row4, textvariable=self._var_nt_modpow_base, width=8,
                  font=("Consolas", 10)).pack(side=tk.LEFT, padx=2)
        ttk.Label(nt_row4, text=t("label_nt_exp"), style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_nt_modpow_exp = tk.StringVar(value="10")
        ttk.Entry(nt_row4, textvariable=self._var_nt_modpow_exp, width=8,
                  font=("Consolas", 10)).pack(side=tk.LEFT, padx=2)
        ttk.Label(nt_row4, text=t("label_nt_mod"), style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_nt_modpow_mod = tk.StringVar(value="1000")
        ttk.Entry(nt_row4, textvariable=self._var_nt_modpow_mod, width=8,
                  font=("Consolas", 10)).pack(side=tk.LEFT, padx=2)
        ttk.Button(nt_row4, text=t("btn_nt_mod_pow"),
                   command=self._on_nt_mod_pow).pack(side=tk.LEFT, padx=2)

        # Row 5: Result display
        nt_row5 = ttk.Frame(frm_nt, style="Dark.TFrame")
        nt_row5.pack(fill=tk.X, padx=6, pady=(0, 4))
        ttk.Label(nt_row5, text=t("label_nt_result"), style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_nt_result = tk.StringVar(value="")
        ttk.Entry(nt_row5, textvariable=self._var_nt_result, width=40,
                  font=("Consolas", 10), state="readonly").pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        ttk.Button(nt_row5, text=t("btn_nt_clear"),
                   command=self._on_nt_clear).pack(side=tk.LEFT, padx=2)

        # --- Bitwise Operations Calculator ---
        frm_bw = ttk.LabelFrame(scroll_frame, text=t("sec_bitwise"),
                                style="Dark.TLabelframe")
        frm_bw.pack(fill=tk.X, padx=8, pady=4)

        # Row 1: Bit width selector
        bw_row1 = ttk.Frame(frm_bw, style="Dark.TFrame")
        bw_row1.pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(bw_row1, text=t("label_bw_width"), style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_bw_width = tk.StringVar(value="16")
        bw_width_combo = ttk.Combobox(bw_row1, textvariable=self._var_bw_width,
                                       values=["8", "16", "32"], width=5,
                                       state="readonly", font=("Consolas", 10))
        bw_width_combo.pack(side=tk.LEFT, padx=4)

        ttk.Label(bw_row1, text=t("label_bw_op"), style="Dark.TLabel").pack(side=tk.LEFT, padx=(12, 0))
        self._var_bw_op = tk.StringVar(value="AND")
        bw_op_combo = ttk.Combobox(bw_row1, textvariable=self._var_bw_op,
                                    values=["AND", "OR", "XOR", "NOT", "<<", ">>"], width=5,
                                    state="readonly", font=("Consolas", 10))
        bw_op_combo.pack(side=tk.LEFT, padx=4)

        # Row 2: Operand A
        bw_row2 = ttk.Frame(frm_bw, style="Dark.TFrame")
        bw_row2.pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(bw_row2, text=t("label_bw_a"), style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_bw_a = tk.StringVar(value="12")
        ttk.Entry(bw_row2, textvariable=self._var_bw_a, width=15,
                  font=("Consolas", 10)).pack(side=tk.LEFT, padx=4)
        ttk.Label(bw_row2, text="(Dec)", style="Dark.TLabel").pack(side=tk.LEFT)

        # Row 3: Operand B
        bw_row3 = ttk.Frame(frm_bw, style="Dark.TFrame")
        bw_row3.pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(bw_row3, text=t("label_bw_b"), style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_bw_b = tk.StringVar(value="5")
        ttk.Entry(bw_row3, textvariable=self._var_bw_b, width=15,
                  font=("Consolas", 10)).pack(side=tk.LEFT, padx=4)
        ttk.Label(bw_row3, text="(Dec)", style="Dark.TLabel").pack(side=tk.LEFT)

        # Row 4: Calculate + Clear
        bw_row4 = ttk.Frame(frm_bw, style="Dark.TFrame")
        bw_row4.pack(fill=tk.X, padx=6, pady=2)
        ttk.Button(bw_row4, text=t("btn_bw_calc"),
                   command=self._on_bw_calc).pack(side=tk.LEFT, padx=2)
        ttk.Button(bw_row4, text=t("btn_bw_clear"),
                   command=self._on_bw_clear).pack(side=tk.LEFT, padx=2)

        # Row 5: Result (binary)
        bw_row5 = ttk.Frame(frm_bw, style="Dark.TFrame")
        bw_row5.pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(bw_row5, text=t("label_bw_res_bin"), style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_bw_res_bin = tk.StringVar(value="")
        ttk.Entry(bw_row5, textvariable=self._var_bw_res_bin, width=35,
                  font=("Consolas", 10), state="readonly").pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)

        # Row 6: Result (hex, oct, dec)
        bw_row6 = ttk.Frame(frm_bw, style="Dark.TFrame")
        bw_row6.pack(fill=tk.X, padx=6, pady=(0, 4))
        ttk.Label(bw_row6, text=t("label_bw_res_hex"), style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_bw_res_hex = tk.StringVar(value="")
        ttk.Entry(bw_row6, textvariable=self._var_bw_res_hex, width=10,
                  font=("Consolas", 10), state="readonly").pack(side=tk.LEFT, padx=2)
        ttk.Label(bw_row6, text=t("label_bw_res_oct"), style="Dark.TLabel").pack(side=tk.LEFT, padx=(8, 0))
        self._var_bw_res_oct = tk.StringVar(value="")
        ttk.Entry(bw_row6, textvariable=self._var_bw_res_oct, width=10,
                  font=("Consolas", 10), state="readonly").pack(side=tk.LEFT, padx=2)
        ttk.Label(bw_row6, text=t("label_bw_res_dec"), style="Dark.TLabel").pack(side=tk.LEFT, padx=(8, 0))
        self._var_bw_res_dec = tk.StringVar(value="")
        ttk.Entry(bw_row6, textvariable=self._var_bw_res_dec, width=10,
                  font=("Consolas", 10), state="readonly").pack(side=tk.LEFT, padx=2)

        # --- Unit Converter ---
        UNIT_CATEGORIES = {
            "Length": {
                "Meter (m)": 1.0,
                "Kilometer (km)": 1000.0,
                "Centimeter (cm)": 0.01,
                "Millimeter (mm)": 0.001,
                "Mile (mi)": 1609.344,
                "Yard (yd)": 0.9144,
                "Foot (ft)": 0.3048,
                "Inch (in)": 0.0254,
                "Nautical Mile (nmi)": 1852.0,
            },
            "Weight": {
                "Kilogram (kg)": 1.0,
                "Gram (g)": 0.001,
                "Milligram (mg)": 0.000001,
                "Metric Ton (t)": 1000.0,
                "Pound (lb)": 0.45359237,
                "Ounce (oz)": 0.028349523125,
            },
            "Temperature": {
                "Celsius (°C)": "C",
                "Fahrenheit (°F)": "F",
                "Kelvin (K)": "K",
            },
            "Area": {
                "Square Meter (m²)": 1.0,
                "Square Kilometer (km²)": 1000000.0,
                "Hectare (ha)": 10000.0,
                "Acre (ac)": 4046.8564224,
                "Square Foot (ft²)": 0.09290304,
                "Square Inch (in²)": 0.00064516,
                "Square Mile (mi²)": 2589988.110336,
            },
            "Volume": {
                "Liter (L)": 1.0,
                "Milliliter (mL)": 0.001,
                "Cubic Meter (m³)": 1000.0,
                "Gallon (US)": 3.785411784,
                "Quart (US)": 0.946352946,
                "Pint (US)": 0.473176473,
                "Cup (US)": 0.2365882365,
                "Fluid Ounce (US)": 0.0295735295625,
                "Cubic Centimeter (cm³)": 0.001,
            },
            "Time": {
                "Second (s)": 1.0,
                "Minute (min)": 60.0,
                "Hour (h)": 3600.0,
                "Day (d)": 86400.0,
                "Week (wk)": 604800.0,
                "Month (30 days)": 2592000.0,
                "Year (365 days)": 31536000.0,
            },
            "Data Storage": {
                "Byte (B)": 1.0,
                "Kilobyte (KB)": 1024.0,
                "Megabyte (MB)": 1048576.0,
                "Gigabyte (GB)": 1073741824.0,
                "Terabyte (TB)": 1099511627776.0,
                "Bit": 0.125,
                "Kilobit (Kbit)": 128.0,
                "Megabit (Mbit)": 131072.0,
                "Gigabit (Gbit)": 134217728.0,
            },
            "Speed": {
                "Meter/second (m/s)": 1.0,
                "Kilometer/hour (km/h)": 0.2777777778,
                "Mile/hour (mph)": 0.44704,
                "Knot (kn)": 0.5144444444,
                "Foot/second (ft/s)": 0.3048,
                "Mach (at sea level)": 340.29,
            },
            "Angle": {
                "Degree (°)": 1.0,
                "Radian (rad)": 57.29577951308232,
                "Gradian (grad)": 0.9,
                "Arcminute (')": 1/60.0,
                "Arcsecond (\")": 1/3600.0,
            },
        }

        self._unit_categories = UNIT_CATEGORIES

        frm_unit = ttk.LabelFrame(scroll_frame, text=t("sec_unit"),
                                  style="Dark.TLabelframe")
        frm_unit.pack(fill=tk.X, padx=8, pady=4)

        urow1 = ttk.Frame(frm_unit, style="Dark.TFrame")
        urow1.pack(fill=tk.X, padx=6, pady=(4, 2))
        ttk.Label(urow1, text=t("label_category"), style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_unit_cat = tk.StringVar(value="Length")
        self._unit_cat_combo = ttk.Combobox(urow1, textvariable=self._var_unit_cat,
                                            values=list(UNIT_CATEGORIES.keys()),
                                            state="readonly", font=("Consolas", 10), width=14)
        self._unit_cat_combo.pack(side=tk.LEFT, padx=4)
        self._unit_cat_combo.bind("<<ComboboxSelected>>",
                                  lambda e: self._on_unit_category_change())

        urow2 = ttk.Frame(frm_unit, style="Dark.TFrame")
        urow2.pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(urow2, text=t("label_from_unit"), style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_unit_from = tk.StringVar()
        self._unit_from_combo = ttk.Combobox(urow2, textvariable=self._var_unit_from,
                                             state="readonly", font=("Consolas", 10), width=20)
        self._unit_from_combo.pack(side=tk.LEFT, padx=4)

        urow3 = ttk.Frame(frm_unit, style="Dark.TFrame")
        urow3.pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(urow3, text=t("label_to_unit"), style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_unit_to = tk.StringVar()
        self._unit_to_combo = ttk.Combobox(urow3, textvariable=self._var_unit_to,
                                           state="readonly", font=("Consolas", 10), width=20)
        self._unit_to_combo.pack(side=tk.LEFT, padx=4)

        urow4 = ttk.Frame(frm_unit, style="Dark.TFrame")
        urow4.pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(urow4, text=t("label_value"), style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_unit_value = tk.StringVar(value="1")
        ttk.Entry(urow4, textvariable=self._var_unit_value, width=15,
                  font=("Consolas", 10)).pack(side=tk.LEFT, padx=4)
        ttk.Button(urow4, text=t("btn_convert"),
                   command=self._on_unit_convert).pack(side=tk.LEFT, padx=8)

        urow5 = ttk.Frame(frm_unit, style="Dark.TFrame")
        urow5.pack(fill=tk.X, padx=6, pady=(0, 4))
        ttk.Label(urow5, text=t("label_result"), style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_unit_result = tk.StringVar(value="")
        ttk.Entry(urow5, textvariable=self._var_unit_result, width=30,
                  font=("Consolas", 10), state="readonly").pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)

        # Initialize unit dropdowns
        self._on_unit_category_change()

        # --- Perpetual Calendar ---
        frm_cal = ttk.LabelFrame(scroll_frame, text=t("sec_calendar"),
                                  style="Dark.TLabelframe")
        frm_cal.pack(fill=tk.X, padx=8, pady=4)

        # Row 1: Date 1 (YYYY-MM-DD)
        cal_row1 = ttk.Frame(frm_cal, style="Dark.TFrame")
        cal_row1.pack(fill=tk.X, padx=6, pady=(4, 2))
        ttk.Label(cal_row1, text=t("label_cal_date"), style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_cal_date1 = tk.StringVar(value="2026-01-01")
        ttk.Entry(cal_row1, textvariable=self._var_cal_date1, width=14,
                  font=("Consolas", 10)).pack(side=tk.LEFT, padx=4)
        ttk.Button(cal_row1, text=t("btn_cal_today"),
                   command=self._on_cal_today).pack(side=tk.LEFT, padx=4)

        # Row 2: Date 2 (YYYY-MM-DD) for difference
        cal_row2 = ttk.Frame(frm_cal, style="Dark.TFrame")
        cal_row2.pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(cal_row2, text=t("label_cal_date2"), style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_cal_date2 = tk.StringVar(value="2026-12-31")
        ttk.Entry(cal_row2, textvariable=self._var_cal_date2, width=14,
                  font=("Consolas", 10)).pack(side=tk.LEFT, padx=4)

        # Row 3: Add/Subtract days
        cal_row3 = ttk.Frame(frm_cal, style="Dark.TFrame")
        cal_row3.pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(cal_row3, text=t("label_cal_add_days"), style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_cal_add_days = tk.StringVar(value="0")
        ttk.Entry(cal_row3, textvariable=self._var_cal_add_days, width=10,
                  font=("Consolas", 10)).pack(side=tk.LEFT, padx=4)

        # Row 4: Buttons
        cal_row4 = ttk.Frame(frm_cal, style="Dark.TFrame")
        cal_row4.pack(fill=tk.X, padx=6, pady=2)
        ttk.Button(cal_row4, text=t("btn_cal_day_of_week"),
                   command=self._on_cal_day_of_week).pack(side=tk.LEFT, padx=2)
        ttk.Button(cal_row4, text=t("btn_cal_diff"),
                   command=self._on_cal_diff).pack(side=tk.LEFT, padx=2)
        ttk.Button(cal_row4, text=t("btn_cal_add_days"),
                   command=self._on_cal_add_days).pack(side=tk.LEFT, padx=2)
        ttk.Button(cal_row4, text=t("btn_cal_clear"),
                   command=self._on_cal_clear).pack(side=tk.LEFT, padx=2)

        # Row 5: Result
        cal_row5 = ttk.Frame(frm_cal, style="Dark.TFrame")
        cal_row5.pack(fill=tk.X, padx=6, pady=(0, 4))
        ttk.Label(cal_row5, text=t("label_result"), style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_cal_result = tk.StringVar(value="")
        ttk.Entry(cal_row5, textvariable=self._var_cal_result, width=35,
                  font=("Consolas", 10), state="readonly").pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)

        # --- Probability Calculator ---
        frm_prob = ttk.LabelFrame(scroll_frame, text=t("sec_probability"),
                                   style="Dark.TLabelframe")
        frm_prob.pack(fill=tk.X, padx=8, pady=4)

        # Mode selector
        prob_mode_row = ttk.Frame(frm_prob, style="Dark.TFrame")
        prob_mode_row.pack(fill=tk.X, padx=6, pady=(4, 2))
        ttk.Label(prob_mode_row, text=t("label_preset"), style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_prob_mode = tk.StringVar(value="combo")
        prob_modes = [
            ("C(n,r)/P(n,r)", "combo"),
            ("P(A∪B)/P(A∩B)/P(A')", "event"),
            ("P(A|B) Conditional", "conditional"),
            ("Bayes P(A|B)", "bayes"),
            ("Binomial", "binomial"),
            ("Poisson", "poisson"),
            ("Geometric", "geometric"),
            ("Hypergeometric", "hypergeo"),
        ]
        prob_combo = ttk.Combobox(prob_mode_row, textvariable=self._var_prob_mode,
                                   values=[m[0] for m in prob_modes],
                                   state="readonly", font=("Consolas", 10), width=22)
        prob_combo.pack(side=tk.LEFT, padx=4)
        self._prob_mode_map = {m[0]: m[1] for m in prob_modes}
        prob_combo.bind("<<ComboboxSelected>>",
                        lambda e: self._on_prob_mode_change())

        # Combinatorics frame (n, r)
        self._frame_prob_combo = ttk.Frame(frm_prob, style="Dark.TFrame")
        self._frame_prob_combo.pack(fill=tk.X, padx=6, pady=2)
        c_row1 = ttk.Frame(self._frame_prob_combo, style="Dark.TFrame")
        c_row1.pack(fill=tk.X, pady=2)
        ttk.Label(c_row1, text=t("label_prob_n"), style="Dark.TLabel", width=4).pack(side=tk.LEFT)
        self._var_prob_n = tk.StringVar(value="10")
        ttk.Entry(c_row1, textvariable=self._var_prob_n, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Label(c_row1, text=t("label_prob_r"), style="Dark.TLabel", width=4).pack(side=tk.LEFT, padx=(8,0))
        self._var_prob_r = tk.StringVar(value="3")
        ttk.Entry(c_row1, textvariable=self._var_prob_r, width=8).pack(side=tk.LEFT, padx=2)
        c_row2 = ttk.Frame(self._frame_prob_combo, style="Dark.TFrame")
        c_row2.pack(fill=tk.X, pady=2)
        ttk.Button(c_row2, text=t("btn_prob_combo"),
                   command=self._on_prob_combo).pack(side=tk.LEFT, padx=2)
        ttk.Button(c_row2, text=t("btn_prob_perm"),
                   command=self._on_prob_perm).pack(side=tk.LEFT, padx=2)

        # Event probability frame (P(A), P(B), P(A∩B))
        self._frame_prob_event = ttk.Frame(frm_prob, style="Dark.TFrame")
        e_row1 = ttk.Frame(self._frame_prob_event, style="Dark.TFrame")
        e_row1.pack(fill=tk.X, pady=2)
        ttk.Label(e_row1, text=t("label_prob_pa"), style="Dark.TLabel", width=8).pack(side=tk.LEFT)
        self._var_prob_pa = tk.StringVar(value="0.5")
        ttk.Entry(e_row1, textvariable=self._var_prob_pa, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Label(e_row1, text=t("label_prob_pb"), style="Dark.TLabel", width=8).pack(side=tk.LEFT, padx=(8,0))
        self._var_prob_pb = tk.StringVar(value="0.3")
        ttk.Entry(e_row1, textvariable=self._var_prob_pb, width=8).pack(side=tk.LEFT, padx=2)
        e_row2 = ttk.Frame(self._frame_prob_event, style="Dark.TFrame")
        e_row2.pack(fill=tk.X, pady=2)
        ttk.Label(e_row2, text=t("label_prob_pa_and_b"), style="Dark.TLabel", width=12).pack(side=tk.LEFT)
        self._var_prob_pa_and_b = tk.StringVar(value="0.1")
        ttk.Entry(e_row2, textvariable=self._var_prob_pa_and_b, width=8).pack(side=tk.LEFT, padx=2)
        e_row3 = ttk.Frame(self._frame_prob_event, style="Dark.TFrame")
        e_row3.pack(fill=tk.X, pady=2)
        ttk.Button(e_row3, text=t("btn_prob_union"),
                   command=self._on_prob_union).pack(side=tk.LEFT, padx=2)
        ttk.Button(e_row3, text=t("btn_prob_intersect"),
                   command=self._on_prob_intersect).pack(side=tk.LEFT, padx=2)
        ttk.Button(e_row3, text=t("btn_prob_complement"),
                   command=self._on_prob_complement_a).pack(side=tk.LEFT, padx=2)

        # Conditional probability frame (P(A|B))
        self._frame_prob_cond = ttk.Frame(frm_prob, style="Dark.TFrame")
        con_row1 = ttk.Frame(self._frame_prob_cond, style="Dark.TFrame")
        con_row1.pack(fill=tk.X, pady=2)
        ttk.Label(con_row1, text=t("label_prob_pa_and_b"), style="Dark.TLabel", width=12).pack(side=tk.LEFT)
        self._var_prob_cond_a_and_b = tk.StringVar(value="0.1")
        ttk.Entry(con_row1, textvariable=self._var_prob_cond_a_and_b, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Label(con_row1, text=t("label_prob_pb"), style="Dark.TLabel", width=8).pack(side=tk.LEFT, padx=(8,0))
        self._var_prob_cond_pb = tk.StringVar(value="0.3")
        ttk.Entry(con_row1, textvariable=self._var_prob_cond_pb, width=8).pack(side=tk.LEFT, padx=2)
        con_row2 = ttk.Frame(self._frame_prob_cond, style="Dark.TFrame")
        con_row2.pack(fill=tk.X, pady=2)
        ttk.Button(con_row2, text=t("btn_prob_conditional"),
                   command=self._on_prob_conditional).pack(side=tk.LEFT, padx=2)

        # Bayes frame (P(B|A), P(A), P(B|A'))
        self._frame_prob_bayes = ttk.Frame(frm_prob, style="Dark.TFrame")
        bay_row1 = ttk.Frame(self._frame_prob_bayes, style="Dark.TFrame")
        bay_row1.pack(fill=tk.X, pady=2)
        ttk.Label(bay_row1, text=t("label_prob_pb_given_a"), style="Dark.TLabel", width=12).pack(side=tk.LEFT)
        self._var_prob_bayes_pba = tk.StringVar(value="0.9")
        ttk.Entry(bay_row1, textvariable=self._var_prob_bayes_pba, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Label(bay_row1, text=t("label_prob_pa"), style="Dark.TLabel", width=8).pack(side=tk.LEFT, padx=(8,0))
        self._var_prob_bayes_pa = tk.StringVar(value="0.01")
        ttk.Entry(bay_row1, textvariable=self._var_prob_bayes_pa, width=8).pack(side=tk.LEFT, padx=2)
        bay_row2 = ttk.Frame(self._frame_prob_bayes, style="Dark.TFrame")
        bay_row2.pack(fill=tk.X, pady=2)
        ttk.Label(bay_row2, text=t("label_prob_pb_given_not_a"), style="Dark.TLabel", width=12).pack(side=tk.LEFT)
        self._var_prob_bayes_pbna = tk.StringVar(value="0.1")
        ttk.Entry(bay_row2, textvariable=self._var_prob_bayes_pbna, width=8).pack(side=tk.LEFT, padx=2)
        bay_row3 = ttk.Frame(self._frame_prob_bayes, style="Dark.TFrame")
        bay_row3.pack(fill=tk.X, pady=2)
        ttk.Button(bay_row3, text=t("btn_prob_bayes"),
                   command=self._on_prob_bayes).pack(side=tk.LEFT, padx=2)

        # Binomial frame (n, k, p)
        self._frame_prob_binom = ttk.Frame(frm_prob, style="Dark.TFrame")
        bin_row1 = ttk.Frame(self._frame_prob_binom, style="Dark.TFrame")
        bin_row1.pack(fill=tk.X, pady=2)
        ttk.Label(bin_row1, text=t("label_prob_n"), style="Dark.TLabel", width=4).pack(side=tk.LEFT)
        self._var_prob_binom_n = tk.StringVar(value="20")
        ttk.Entry(bin_row1, textvariable=self._var_prob_binom_n, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Label(bin_row1, text=t("label_prob_k"), style="Dark.TLabel", width=4).pack(side=tk.LEFT, padx=(8,0))
        self._var_prob_binom_k = tk.StringVar(value="5")
        ttk.Entry(bin_row1, textvariable=self._var_prob_binom_k, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Label(bin_row1, text=t("label_prob_p"), style="Dark.TLabel", width=10).pack(side=tk.LEFT, padx=(8,0))
        self._var_prob_binom_p = tk.StringVar(value="0.3")
        ttk.Entry(bin_row1, textvariable=self._var_prob_binom_p, width=8).pack(side=tk.LEFT, padx=2)
        bin_row2 = ttk.Frame(self._frame_prob_binom, style="Dark.TFrame")
        bin_row2.pack(fill=tk.X, pady=2)
        ttk.Button(bin_row2, text=t("btn_prob_binom_pmf"),
                   command=self._on_prob_binom_pmf).pack(side=tk.LEFT, padx=2)
        ttk.Button(bin_row2, text=t("btn_prob_binom_cdf"),
                   command=self._on_prob_binom_cdf).pack(side=tk.LEFT, padx=2)

        # Poisson frame (lambda, k)
        self._frame_prob_poisson = ttk.Frame(frm_prob, style="Dark.TFrame")
        poi_row1 = ttk.Frame(self._frame_prob_poisson, style="Dark.TFrame")
        poi_row1.pack(fill=tk.X, pady=2)
        ttk.Label(poi_row1, text=t("label_prob_lambda"), style="Dark.TLabel", width=10).pack(side=tk.LEFT)
        self._var_prob_poisson_lam = tk.StringVar(value="5")
        ttk.Entry(poi_row1, textvariable=self._var_prob_poisson_lam, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Label(poi_row1, text=t("label_prob_k"), style="Dark.TLabel", width=4).pack(side=tk.LEFT, padx=(8,0))
        self._var_prob_poisson_k = tk.StringVar(value="3")
        ttk.Entry(poi_row1, textvariable=self._var_prob_poisson_k, width=8).pack(side=tk.LEFT, padx=2)
        poi_row2 = ttk.Frame(self._frame_prob_poisson, style="Dark.TFrame")
        poi_row2.pack(fill=tk.X, pady=2)
        ttk.Button(poi_row2, text=t("btn_prob_poisson"),
                   command=self._on_prob_poisson).pack(side=tk.LEFT, padx=2)

        # Geometric frame (p, k)
        self._frame_prob_geometric = ttk.Frame(frm_prob, style="Dark.TFrame")
        geo_row1 = ttk.Frame(self._frame_prob_geometric, style="Dark.TFrame")
        geo_row1.pack(fill=tk.X, pady=2)
        ttk.Label(geo_row1, text=t("label_prob_p"), style="Dark.TLabel", width=10).pack(side=tk.LEFT)
        self._var_prob_geo_p = tk.StringVar(value="0.5")
        ttk.Entry(geo_row1, textvariable=self._var_prob_geo_p, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Label(geo_row1, text=t("label_prob_k"), style="Dark.TLabel", width=4).pack(side=tk.LEFT, padx=(8,0))
        self._var_prob_geo_k = tk.StringVar(value="3")
        ttk.Entry(geo_row1, textvariable=self._var_prob_geo_k, width=8).pack(side=tk.LEFT, padx=2)
        geo_row2 = ttk.Frame(self._frame_prob_geometric, style="Dark.TFrame")
        geo_row2.pack(fill=tk.X, pady=2)
        ttk.Button(geo_row2, text=t("btn_prob_geometric"),
                   command=self._on_prob_geometric).pack(side=tk.LEFT, padx=2)

        # Hypergeometric frame (N, K, n, k)
        self._frame_prob_hypergeo = ttk.Frame(frm_prob, style="Dark.TFrame")
        hyp_row1 = ttk.Frame(self._frame_prob_hypergeo, style="Dark.TFrame")
        hyp_row1.pack(fill=tk.X, pady=2)
        ttk.Label(hyp_row1, text=t("label_prob_pop_n"), style="Dark.TLabel", width=14).pack(side=tk.LEFT)
        self._var_prob_hyp_N = tk.StringVar(value="50")
        ttk.Entry(hyp_row1, textvariable=self._var_prob_hyp_N, width=6).pack(side=tk.LEFT, padx=2)
        ttk.Label(hyp_row1, text=t("label_prob_pop_k"), style="Dark.TLabel", width=14).pack(side=tk.LEFT, padx=(4,0))
        self._var_prob_hyp_K = tk.StringVar(value="10")
        ttk.Entry(hyp_row1, textvariable=self._var_prob_hyp_K, width=6).pack(side=tk.LEFT, padx=2)
        hyp_row2 = ttk.Frame(self._frame_prob_hypergeo, style="Dark.TFrame")
        hyp_row2.pack(fill=tk.X, pady=2)
        ttk.Label(hyp_row2, text=t("label_prob_sample_n"), style="Dark.TLabel", width=14).pack(side=tk.LEFT)
        self._var_prob_hyp_n = tk.StringVar(value="5")
        ttk.Entry(hyp_row2, textvariable=self._var_prob_hyp_n, width=6).pack(side=tk.LEFT, padx=2)
        ttk.Label(hyp_row2, text=t("label_prob_sample_k"), style="Dark.TLabel", width=14).pack(side=tk.LEFT, padx=(4,0))
        self._var_prob_hyp_k = tk.StringVar(value="2")
        ttk.Entry(hyp_row2, textvariable=self._var_prob_hyp_k, width=6).pack(side=tk.LEFT, padx=2)
        hyp_row3 = ttk.Frame(self._frame_prob_hypergeo, style="Dark.TFrame")
        hyp_row3.pack(fill=tk.X, pady=2)
        ttk.Button(hyp_row3, text=t("btn_prob_hypergeo"),
                   command=self._on_prob_hypergeo).pack(side=tk.LEFT, padx=2)

        # Result
        prob_res_row = ttk.Frame(frm_prob, style="Dark.TFrame")
        prob_res_row.pack(fill=tk.X, padx=6, pady=(0, 4))
        ttk.Label(prob_res_row, text=t("label_result"), style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_prob_result = tk.StringVar(value="")
        ttk.Entry(prob_res_row, textvariable=self._var_prob_result, width=38,
                  font=("Consolas", 10), state="readonly").pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        ttk.Button(prob_res_row, text=t("btn_prob_clear"),
                   command=lambda: self._var_prob_result.set("")).pack(side=tk.LEFT, padx=2)

        # Initially show only combinatorics frame
        self._on_prob_mode_change()

        # --- Status ---
        self.status_var = tk.StringVar(value=t("status_ready"))
        status_bar = ttk.Label(scroll_frame, textvariable=self.status_var,
                               style="Dark.TLabel", relief=tk.SUNKEN,
                               anchor=tk.W, padding=(8, 2))
        status_bar.pack(fill=tk.X, padx=8, pady=8)

        # --- Styles ---
        style = ttk.Style()
        style.configure("Dark.TFrame", background="#1e1e2e")
        style.configure("Dark.TLabelframe", background="#1e1e2e",
                        foreground="#cdd6f4", bordercolor="#45475a")
        style.configure("Dark.TLabelframe.Label", background="#1e1e2e",
                        foreground="#cdd6f4")
        style.configure("Dark.TLabel", background="#1e1e2e",
                        foreground="#cdd6f4")

    # ------------------------------------------------------------------
    #  2D / 3D Window Management
    # ------------------------------------------------------------------
    def _ensure_2d_window(self):
        if self.window_2d is not None and self.window_2d.winfo_exists():
            return
        self.window_2d = tk.Toplevel(self.root)
        self.window_2d.title(t("win_2d"))
        self.window_2d.geometry("900x700")
        self.window_2d.minsize(600, 400)
        self.window_2d.configure(bg="#1e1e2e")
        self.window_2d.protocol("WM_DELETE_WINDOW", self._on_2d_window_close)

        self.fig_2d = Figure(figsize=(9, 7), dpi=100, facecolor="#1e1e2e")
        self.ax_2d = self.fig_2d.add_subplot(111)
        self._setup_axes(self.ax_2d, is_3d=False)

        self.canvas_2d = FigureCanvasTkAgg(self.fig_2d, master=self.window_2d)
        self.canvas_2d.draw()
        self.toolbar_2d = NavigationToolbar2Tk(self.canvas_2d, self.window_2d)
        self.toolbar_2d.update()
        self.canvas_2d.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        self.canvas_2d.mpl_connect('button_press_event', self._on_canvas_click)

    def _on_2d_window_close(self):
        if self.fig_2d is not None:
            import matplotlib.pyplot as plt
            plt.close(self.fig_2d)
        if self.window_2d is not None:
            self.window_2d.destroy()
        self.window_2d = None
        self.fig_2d = None
        self.ax_2d = None
        self.canvas_2d = None
        self.toolbar_2d = None

    def _ensure_3d_window(self):
        if self.window_3d is not None and self.window_3d.winfo_exists():
            return
        self.window_3d = tk.Toplevel(self.root)
        self.window_3d.title(t("win_3d"))
        self.window_3d.geometry("900x700")
        self.window_3d.minsize(600, 400)
        self.window_3d.configure(bg="#1e1e2e")
        self.window_3d.protocol("WM_DELETE_WINDOW", self._on_3d_window_close)

        self.fig_3d = Figure(figsize=(9, 7), dpi=100, facecolor="#1e1e2e")
        self.ax_3d = self.fig_3d.add_subplot(111, projection='3d')
        self._setup_axes(self.ax_3d, is_3d=True)

        self.canvas_3d = FigureCanvasTkAgg(self.fig_3d, master=self.window_3d)
        self.canvas_3d.draw()
        self.toolbar_3d = NavigationToolbar2Tk(self.canvas_3d, self.window_3d)
        self.toolbar_3d.update()
        self.canvas_3d.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

    def _on_3d_window_close(self):
        if self.fig_3d is not None:
            import matplotlib.pyplot as plt
            plt.close(self.fig_3d)
        if self.window_3d is not None:
            self.window_3d.destroy()
        self.window_3d = None
        self.fig_3d = None
        self.ax_3d = None
        self.canvas_3d = None
        self.toolbar_3d = None

    def _ensure_fft_window(self):
        if self.window_fft is not None and self.window_fft.winfo_exists():
            return
        self.window_fft = tk.Toplevel(self.root)
        self.window_fft.title(t("win_fft"))
        self.window_fft.geometry("900x750")
        self.window_fft.minsize(600, 500)
        self.window_fft.configure(bg="#1e1e2e")
        self.window_fft.protocol("WM_DELETE_WINDOW", self._on_fft_window_close)

        self.fig_fft = Figure(figsize=(9, 7.5), dpi=100, facecolor="#1e1e2e")
        self.ax_fft_amp = self.fig_fft.add_subplot(211)
        self.ax_fft_phase = self.fig_fft.add_subplot(212)
        self._setup_axes(self.ax_fft_amp, is_3d=False)
        self._setup_axes(self.ax_fft_phase, is_3d=False)
        self.ax_fft_amp.set_title(t("fft_amp_title"), color="#cdd6f4", fontsize=11)
        self.ax_fft_phase.set_title(t("fft_phase_title"), color="#cdd6f4", fontsize=11)
        self.ax_fft_amp.set_xlabel(t("fft_freq"))
        self.ax_fft_amp.set_ylabel(t("fft_amp"))
        self.ax_fft_phase.set_xlabel(t("fft_freq"))
        self.ax_fft_phase.set_ylabel(t("fft_phase_rad"))

        self.canvas_fft = FigureCanvasTkAgg(self.fig_fft, master=self.window_fft)
        self.canvas_fft.draw()
        self.toolbar_fft = NavigationToolbar2Tk(self.canvas_fft, self.window_fft)
        self.toolbar_fft.update()
        self.canvas_fft.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

    def _on_fft_window_close(self):
        if self.fig_fft is not None:
            import matplotlib.pyplot as plt
            plt.close(self.fig_fft)
        if self.window_fft is not None:
            self.window_fft.destroy()
        self.window_fft = None
        self.fig_fft = None
        self.ax_fft_amp = None
        self.ax_fft_phase = None
        self.canvas_fft = None
        self.toolbar_fft = None

    # ------------------------------------------------------------------
    #  Input Panel
    # ------------------------------------------------------------------
    def _open_input_panel(self):
        panel = tk.Toplevel(self.root)
        panel.title(t("win_input_panel"))
        panel.geometry("500x400")
        panel.configure(bg="#1e1e2e")
        panel.transient(self.root)
        panel.grab_set()
        
        main_frame = ttk.Frame(panel, style="Dark.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Only include operators/functions/constants supported by the C core
        buttons_config = [
            (t("cat_basic"), [
                ("x²", "x^2"), ("x³", "x^3"), ("xⁿ", "x^n"),
                ("√", "sqrt("), ("|x|", "abs("),
            ]),
            (t("cat_operators"), [
                ("÷", "/"), ("×", "*"), ("^", "^"), ("-", "-"), ("+", "+"),
                ("mod", " mod "),
            ]),
            (t("cat_logexp"), [
                ("ln", "ln("), ("log", "log("), ("eˣ", "exp("), ("e", "e"),
            ]),
            (t("cat_trig"), [
                ("sin", "sin("), ("cos", "cos("), ("tan", "tan("),
                ("π", "pi"), ("°", "*pi/180"),
            ]),
            (t("cat_rounding"), [
                ("floor", "floor("), ("ceil", "ceil("),
            ]),
            (t("cat_special"), [
                ("!", "!"), ("(", "("), (")", ")"), (",", ","),
            ]),
            (t("cat_constants"), [
                ("π", "pi"), ("e", "e"),
            ]),
        ]
        
        for category, buttons in buttons_config:
            frame = ttk.LabelFrame(main_frame, text=category, style="Dark.TLabelframe")
            frame.pack(fill=tk.X, pady=4)
            
            btn_frame = ttk.Frame(frame, style="Dark.TFrame")
            btn_frame.pack(fill=tk.X, padx=4, pady=4)
            
            for i, (label, text) in enumerate(buttons):
                btn = ttk.Button(btn_frame, text=label, width=5,
                                command=lambda t=text: self._insert_text(t))
                btn.grid(row=0, column=i, padx=2, pady=2)

        ttk.Button(main_frame, text=t("btn_close"), command=panel.destroy).pack(pady=10)

    def _insert_text(self, text):
        """Insert text at cursor, replacing any selected text."""
        expr = self.entry_expr.get()
        try:
            sel_start = self.entry_expr.index(tk.SEL_FIRST)
            sel_end = self.entry_expr.index(tk.SEL_LAST)
            self.entry_expr.delete(sel_start, sel_end)
            self.entry_expr.insert(sel_start, text)
        except tk.TclError:
            # No selection
            pos = self.entry_expr.index(tk.INSERT)
            self.entry_expr.insert(pos, text)
        self.entry_expr.focus()

    # ------------------------------------------------------------------
    #  Parameter handling
    # ------------------------------------------------------------------
    def _update_param_inputs(self):
        expr = self.entry_expr.get().strip()
        params = _detect_parameters_static(expr)

        saved_values = {param: var.get() for param, var in self.param_widgets.items()}

        for widget in self.frm_params.winfo_children():
            widget.destroy()
        self.param_widgets.clear()

        if not params:
            ttk.Label(self.frm_params, text=t("label_no_params"),
                      style="Dark.TLabel").pack(padx=6, pady=8)
            return

        ttk.Label(self.frm_params, text=t("label_set_params"),
                  style="Dark.TLabel").pack(anchor=tk.W, padx=6, pady=(6, 0))

        for param in params:
            frame = ttk.Frame(self.frm_params, style="Dark.TFrame")
            frame.pack(fill=tk.X, padx=6, pady=2)

            ttk.Label(frame, text=f"{param} =", width=5,
                      style="Dark.TLabel").pack(side=tk.LEFT, padx=2)
            default_val = saved_values.get(param, "1")
            var = tk.StringVar(value=default_val)
            entry = ttk.Entry(frame, textvariable=var, width=10)
            entry.pack(side=tk.LEFT, padx=2)
            entry.bind("<KeyRelease>", lambda e: self._on_param_change())
            self.param_widgets[param] = var

        self._on_param_change()

    def _on_param_change(self):
        self.param_values = {}
        for param, var in self.param_widgets.items():
            try:
                self.param_values[param] = float(var.get())
            except ValueError:
                self.param_values[param] = 1.0

    def _on_parametric_toggle(self):
        """Show or hide parametric input fields."""
        if self._var_parametric.get():
            for child in self._frame_param_inputs.winfo_children():
                child.pack()
        else:
            for child in self._frame_param_inputs.winfo_children():
                child.pack_forget()

    def _on_parametric_preset(self, name: str):
        """Load a parametric preset into the input fields."""
        preset = PARAMETRIC_PRESETS.get(name)
        if preset:
            x_expr, y_expr, t_min, t_max = preset
            self._var_x_param.set(x_expr)
            self._var_y_param.set(y_expr)
            self._var_t_min.set(t_min)
            self._var_t_max.set(t_max)
            self._var_parametric.set(True)
            self._on_parametric_toggle()

    def _on_polar_toggle(self):
        """Show or hide polar input fields."""
        if self._var_polar.get():
            for child in self._frame_polar_inputs.winfo_children():
                child.pack()
        else:
            for child in self._frame_polar_inputs.winfo_children():
                child.pack_forget()

    def _on_polar_preset(self, name: str):
        """Load a polar preset into the input fields."""
        preset = POLAR_PRESETS.get(name)
        if preset:
            r_expr, theta_min, theta_max = preset
            self._var_r_param.set(r_expr)
            self._var_theta_min.set(theta_min)
            self._var_theta_max.set(theta_max)
            self._var_polar.set(True)
            self._on_polar_toggle()

    def _on_implicit_toggle(self):
        """Show or hide implicit input fields."""
        if self._var_implicit.get():
            for child in self._frame_implicit_inputs.winfo_children():
                child.pack()
        else:
            for child in self._frame_implicit_inputs.winfo_children():
                child.pack_forget()

    def _on_implicit_preset(self, name: str):
        """Load an implicit preset into the input fields."""
        expr = name.split(": ", 1)[1] if ": " in name else name
        self._var_implicit_expr.set(expr)
        self._var_implicit.set(True)
        self._on_implicit_toggle()

    def _resolve_t_range(self, expr: str) -> str:
        """Resolve 'pi' and 'e' references in t-range expressions."""
        result = expr.strip()
        result = re.sub(r'\bpi\b', str(math.pi), result)
        result = re.sub(r'\be\b', str(math.e), result)
        return result

    def _substitute_params(self, expr: str) -> str:
        result = expr
        skip_words = KNOWN_FUNCTIONS | KNOWN_CONSTANTS | INDEPENDENT_VARS
        for param, value in self.param_values.items():
            def _replace_if_not_func(match):
                word = match.group(0)
                if word.lower() in skip_words or param.lower() in skip_words:
                    return word
                return str(value)
            result = re.sub(r'\b' + re.escape(param) + r'\b', _replace_if_not_func,
                            result, flags=re.IGNORECASE)
        return result

    # ------------------------------------------------------------------
    #  Curve management
    # ------------------------------------------------------------------
    def _add_curve(self, expr: str):
        color = DEFAULT_COLORS[self.color_index % len(DEFAULT_COLORS)]
        self.color_index += 1
        curve = CurveModel(expr.strip(), color)
        self.curves.append(curve)
        self.listbox_curves.insert(tk.END, f"  {curve.label}")
        self.listbox_curves.itemconfig(tk.END, fg=color)
        self._update_param_inputs()

    def _on_add_curve(self):
        if self._var_parametric.get():
            x_expr = self._var_x_param.get().strip()
            y_expr = self._var_y_param.get().strip()
            if not x_expr or not y_expr:
                messagebox.showwarning(t("err_input"), t("msg_enter_xt_yt"))
                return
            color = DEFAULT_COLORS[self.color_index % len(DEFAULT_COLORS)]
            self.color_index += 1
            label = f"x(t)={x_expr}, y(t)={y_expr}"
            curve = CurveModel("", color, label=label, is_parametric=True,
                               x_param_expr=x_expr, y_param_expr=y_expr)
            self.curves.append(curve)
            self.listbox_curves.insert(tk.END, f"  [P] {label}")
            self.listbox_curves.itemconfig(tk.END, fg=color)
            self._plot_all()
        elif self._var_polar.get():
            r_expr = self._var_r_param.get().strip()
            if not r_expr:
                messagebox.showwarning(t("err_input"), t("msg_enter_rtheta"))
                return
            color = DEFAULT_COLORS[self.color_index % len(DEFAULT_COLORS)]
            self.color_index += 1
            label = f"r(theta)={r_expr}"
            curve = CurveModel("", color, label=label, is_polar=True,
                               r_param_expr=r_expr)
            self.curves.append(curve)
            self.listbox_curves.insert(tk.END, f"  [Pol] {label}")
            self.listbox_curves.itemconfig(tk.END, fg=color)
            self._plot_all()
        elif self._var_implicit.get():
            imp_expr = self._var_implicit_expr.get().strip()
            if not imp_expr:
                messagebox.showwarning(t("err_input"), t("msg_enter_implicit_expr"))
                return
            try:
                imp_res = int(self._var_implicit_res.get())
                imp_res = max(50, min(500, imp_res))
            except ValueError:
                imp_res = 200
            color = DEFAULT_COLORS[self.color_index % len(DEFAULT_COLORS)]
            self.color_index += 1
            label = t("implicit_curve_label", imp_expr)
            curve = CurveModel("", color, label=label, is_implicit=True,
                               implicit_expr=imp_expr, implicit_resolution=imp_res)
            self.curves.append(curve)
            self.listbox_curves.insert(tk.END, f"  [Imp] {label}")
            self.listbox_curves.itemconfig(tk.END, fg=color)
            self._plot_all()
        else:
            expr = self.entry_expr.get().strip()
            if not expr:
                messagebox.showwarning(t("err_input"), t("msg_enter_expr"))
                return
            self._add_curve(expr)
            self._plot_all()

    def _on_remove_curve(self):
        sel = self.listbox_curves.curselection()
        if not sel:
            messagebox.showinfo(t("err_info"), t("msg_select_remove"))
            return
        idx = sel[0]
        del self.curves[idx]
        self.listbox_curves.delete(idx)
        self._plot_all()

    def _on_clear_all(self):
        self.curves.clear()
        self.listbox_curves.delete(0, tk.END)
        self.marked_points.clear()
        self.auto_mark_point = None
        self.root_markers = []
        self.intersection_marks.clear()
        self.tangent_data.clear()
        self.normal_data.clear()
        self._var_mark_x.set("")
        self._fft_data = {}
        self._table_data = []
        self._table_expr = ""
        self._ode_data = None
        if self.ax_2d is not None and self.canvas_2d is not None:
            self.ax_2d.clear()
            self._setup_axes(self.ax_2d, is_3d=False)
            self.canvas_2d.draw()
        if self.ax_3d is not None and self.canvas_3d is not None:
            self.ax_3d.clear()
            self._setup_axes(self.ax_3d, is_3d=True)
            self.canvas_3d.draw()
        if self.ax_fft_amp is not None and self.canvas_fft is not None:
            self.ax_fft_amp.clear()
            self.ax_fft_phase.clear()
            self._setup_axes(self.ax_fft_amp, is_3d=False)
            self._setup_axes(self.ax_fft_phase, is_3d=False)
            self.canvas_fft.draw()
        self.status_var.set(t("status_cleared"))

    def _on_preset(self, name: str):
        expr = PRESET_FUNCTIONS.get(name, "")
        if expr:
            self.entry_expr.delete(0, tk.END)
            self.entry_expr.insert(0, expr)
            if not any(c.expression == expr for c in self.curves):
                self._add_curve(expr)
            self._plot_all()

    # ------------------------------------------------------------------
    #  Plotting
    # ------------------------------------------------------------------
    def _on_plot(self):
        if self._var_parametric.get():
            x_expr = self._var_x_param.get().strip()
            y_expr = self._var_y_param.get().strip()
            if not x_expr or not y_expr:
                messagebox.showwarning(t("err_input"), t("msg_enter_xt_yt"))
                return
            label = f"x(t)={x_expr}, y(t)={y_expr}"
            if not any(c.is_parametric and c.label == label for c in self.curves):
                color = DEFAULT_COLORS[self.color_index % len(DEFAULT_COLORS)]
                self.color_index += 1
                curve = CurveModel("", color, label=label, is_parametric=True,
                                   x_param_expr=x_expr, y_param_expr=y_expr)
                self.curves.append(curve)
                self.listbox_curves.insert(tk.END, f"  [P] {label}")
                self.listbox_curves.itemconfig(tk.END, fg=color)
                self._update_param_inputs()
        elif self._var_polar.get():
            r_expr = self._var_r_param.get().strip()
            if not r_expr:
                messagebox.showwarning(t("err_input"), t("msg_enter_rtheta"))
                return
            label = f"r(theta)={r_expr}"
            if not any(c.is_polar and c.label == label for c in self.curves):
                color = DEFAULT_COLORS[self.color_index % len(DEFAULT_COLORS)]
                self.color_index += 1
                curve = CurveModel("", color, label=label, is_polar=True,
                                   r_param_expr=r_expr)
                self.curves.append(curve)
                self.listbox_curves.insert(tk.END, f"  [Pol] {label}")
                self.listbox_curves.itemconfig(tk.END, fg=color)
                self._update_param_inputs()
        elif self._var_implicit.get():
            imp_expr = self._var_implicit_expr.get().strip()
            if not imp_expr:
                messagebox.showwarning(t("err_input"), t("msg_enter_implicit_expr"))
                return
            label = t("implicit_curve_label", imp_expr)
            if not any(c.is_implicit and c.label == label for c in self.curves):
                try:
                    imp_res = int(self._var_implicit_res.get())
                    imp_res = max(50, min(500, imp_res))
                except ValueError:
                    imp_res = 200
                color = DEFAULT_COLORS[self.color_index % len(DEFAULT_COLORS)]
                self.color_index += 1
                curve = CurveModel("", color, label=label, is_implicit=True,
                                   implicit_expr=imp_expr, implicit_resolution=imp_res)
                self.curves.append(curve)
                self.listbox_curves.insert(tk.END, f"  [Imp] {label}")
                self.listbox_curves.itemconfig(tk.END, fg=color)
                self._update_param_inputs()
        else:
            expr = self.entry_expr.get().strip()
            if expr:
                if not any(not c.is_parametric and not c.is_polar and c.expression == expr for c in self.curves):
                    self._add_curve(expr)
        self._plot_all()

    def _on_apply_range(self):
        try:
            x_min = float(self._var_x_min.get())
            x_max = float(self._var_x_max.get())
            y_min = float(self._var_y_min.get())
            y_max = float(self._var_y_max.get())
            z_min = float(self._var_z_min.get())
            z_max = float(self._var_z_max.get())
            step = float(self._var_step.get())
            
            if x_min >= x_max:
                messagebox.showerror(t("err_error"), t("msg_xmin_xmax"))
                return
            if y_min >= y_max:
                messagebox.showerror(t("err_error"), t("msg_ymin_ymax"))
                return
            if z_min >= z_max:
                messagebox.showerror(t("err_error"), t("msg_zmin_zmax"))
                return
            if step <= 0:
                messagebox.showerror(t("err_error"), t("msg_step_positive"))
                return
                
            self.x_min = x_min
            self.x_max = x_max
            self.y_min = y_min
            self.y_max = y_max
            self.z_min = z_min
            self.z_max = z_max
            self.step_size = step
            self.n_pts_3d = max(MIN_3D_POINTS, min(MAX_3D_POINTS, int(self._var_3d_res.get())))
            self.grid_on = self._var_grid.get()
            self._plot_all()
        except ValueError:
            messagebox.showerror(t("err_error"), t("msg_invalid_range"))

    def _plot_all(self):
        try:
            self.x_min = float(self._var_x_min.get())
            self.x_max = float(self._var_x_max.get())
            self.y_min = float(self._var_y_min.get())
            self.y_max = float(self._var_y_max.get())
            self.z_min = float(self._var_z_min.get())
            self.z_max = float(self._var_z_max.get())
            self.step_size = float(self._var_step.get())
            self.n_pts_3d = max(MIN_3D_POINTS, min(MAX_3D_POINTS, int(self._var_3d_res.get())))
            self.grid_on = self._var_grid.get()
            if self.x_min >= self.x_max or self.y_min >= self.y_max or self.z_min >= self.z_max or self.step_size <= 0:
                self.status_var.set(t("status_invalid_range"))
                return
        except ValueError:
            self.status_var.set(t("status_invalid_numeric"))
            return

        if not self.curves:
            # Clear both plot windows when no curves remain
            if self.ax_2d is not None:
                self.ax_2d.clear()
                self._setup_axes(self.ax_2d, is_3d=False)
                self.canvas_2d.draw()
            if self.ax_3d is not None:
                self.ax_3d.clear()
                self._setup_axes(self.ax_3d, is_3d=True)
                self.canvas_3d.draw()
            self.status_var.set(t("status_no_curves"))
            return

        has_2d = any((not c.is_3d and not c.is_polar and not c.is_implicit and c.visible) or 
                     (c.is_parametric and c.visible) or 
                     (c.is_polar and c.visible) or
                     (c.is_implicit and c.visible) for c in self.curves)
        has_3d = any(c.is_3d and c.visible for c in self.curves)
        
        if has_2d:
            self._ensure_2d_window()
            self._plot_2d()
        elif self.window_2d is not None and self.window_2d.winfo_exists():
            # Keep window open but clear it if no 2D curves
            self.ax_2d.clear()
            self._setup_axes(self.ax_2d, is_3d=False)
            self.canvas_2d.draw()
            
        if has_3d:
            self._ensure_3d_window()
            self._plot_3d()
        elif self.window_3d is not None and self.window_3d.winfo_exists():
            # Keep window open but clear it if no 3D curves
            self.ax_3d.clear()
            self._setup_axes(self.ax_3d, is_3d=True)
            self.canvas_3d.draw()

    def _plot_2d(self):
        if self.ax_2d is None:
            return
        self.ax_2d.clear()
        self._setup_axes(self.ax_2d, is_3d=False)

        if self.x_min >= self.x_max or self.step_size <= 0:
            self.status_var.set(t("status_invalid_plot"))
            return
        n_pts = max(MIN_PLOT_POINTS, min(MAX_PLOT_POINTS, int((self.x_max - self.x_min) / self.step_size)))
        xs_np = np.linspace(self.x_min, self.x_max, n_pts)
        xs_list = xs_np.tolist()

        for curve in self.curves:
            if not curve.visible or curve.is_3d:
                continue
            if curve.is_parametric:
                try:
                    t_min = float(self._resolve_t_range(self._var_t_min.get()))
                    t_max = float(self._resolve_t_range(self._var_t_max.get()))
                except ValueError:
                    t_min = 0.0
                    t_max = 6.283185307179586
                t_np = np.linspace(t_min, t_max, n_pts)
                t_list = t_np.tolist()
                x_expr = self._substitute_params(curve.x_param_expr)
                y_expr = self._substitute_params(curve.y_param_expr)
                # C core only supports x/y variables; replace t -> x for evaluation
                x_expr_sub = re.sub(r'\bt\b', 'x', x_expr)
                y_expr_sub = re.sub(r'\bt\b', 'x', y_expr)
                xs_param = CalcEngine.evaluate_array(x_expr_sub, t_list)
                ys_param = CalcEngine.evaluate_array(y_expr_sub, t_list)
                x_arr = np.array([x if x is not None else np.nan for x in xs_param])
                y_arr = np.array([y if y is not None else np.nan for y in ys_param])
                self.ax_2d.plot(x_arr, y_arr, color=curve.color,
                             linewidth=curve.linewidth, linestyle=curve.linestyle,
                             label=curve.label, alpha=0.9)
            elif curve.is_polar:
                try:
                    theta_min = float(self._resolve_t_range(self._var_theta_min.get()))
                    theta_max = float(self._resolve_t_range(self._var_theta_max.get()))
                except ValueError:
                    theta_min = 0.0
                    theta_max = 6.283185307179586
                theta_np = np.linspace(theta_min, theta_max, n_pts)
                theta_list = theta_np.tolist()
                r_expr = self._substitute_params(curve.r_param_expr)
                # C core only supports x/y variables; replace theta -> x for evaluation
                r_expr_sub = re.sub(r'\btheta\b', 'x', r_expr)
                rs = CalcEngine.evaluate_array(r_expr_sub, theta_list)
                # Convert polar to Cartesian coordinates
                x_arr = np.array([r * math.cos(t) if r is not None else np.nan 
                                  for r, t in zip(rs, theta_list)])
                y_arr = np.array([r * math.sin(t) if r is not None else np.nan 
                                  for r, t in zip(rs, theta_list)])
                self.ax_2d.plot(x_arr, y_arr, color=curve.color,
                             linewidth=curve.linewidth, linestyle=curve.linestyle,
                             label=curve.label, alpha=0.9)
            elif curve.is_implicit:
                try:
                    imp_expr = self._substitute_params(curve.implicit_expr)
                    res = curve.implicit_resolution
                    x_range = np.linspace(self.x_min, self.x_max, res)
                    y_range = np.linspace(self.y_min, self.y_max, res)
                    X, Y = np.meshgrid(x_range, y_range)
                    # Evaluate f(x,y) on the grid using evaluate_xy_array
                    flat_x = X.ravel().tolist()
                    flat_y = Y.ravel().tolist()
                    flat_z = CalcEngine.evaluate_xy_array(imp_expr, flat_x, flat_y)
                    Z = np.array([v if v is not None else np.nan for v in flat_z]).reshape(X.shape)
                    # Use contour to plot the zero level set
                    cs = self.ax_2d.contour(X, Y, Z, levels=[0], colors=[curve.color],
                                            linewidths=[curve.linewidth])
                    # Add a proxy artist for legend
                    self.ax_2d.plot([], [], color=curve.color, linewidth=curve.linewidth,
                                   label=curve.label)
                except Exception:
                    pass
            else:
                expr = self._substitute_params(curve.expression)
                ys = CalcEngine.evaluate_array(expr, xs_list)
                ys_clean = np.array([y if y is not None else np.nan for y in ys])
                self.ax_2d.plot(xs_np, ys_clean, color=curve.color,
                             linewidth=curve.linewidth, linestyle=curve.linestyle,
                             label=curve.label, alpha=0.9)

        for point in self.marked_points:
            self.ax_2d.plot(point[0], point[1], 'ro', markersize=8)
            self.ax_2d.annotate(f"({point[0]:.3f}, {point[1]:.3f})",
                           xy=(point[0], point[1]), xytext=(10, 10),
                           textcoords='offset points', color='#f38ba8')

        if self.auto_mark_point is not None:
            x = self.auto_mark_point
            expr = self._get_active_expression()
            if expr:
                expr_sub = self._substitute_params(expr)
                y = CalcEngine.evaluate(expr_sub, x)
                if y is not None:
                    self.ax_2d.plot(x, y, 'go', markersize=10)
                    self.ax_2d.annotate(f"({x:.3f}, {y:.3f})",
                                   xy=(x, y), xytext=(10, -15),
                                   textcoords='offset points', color='#a6e3a1')

        for rx in getattr(self, 'root_markers', []):
            self.ax_2d.plot(rx, 0, 'rD', markersize=10)
            self.ax_2d.annotate(f"x={rx:.4g}", xy=(rx, 0), xytext=(5, 15),
                           textcoords='offset points', color='#f38ba8', fontsize=8)

        for ix, iy in getattr(self, 'intersection_marks', []):
            self.ax_2d.plot(ix, iy, 'mP', markersize=10)
            self.ax_2d.annotate(f"({ix:.3g}, {iy:.3g})", xy=(ix, iy), xytext=(8, -12),
                           textcoords='offset points', color='#cba6f7', fontsize=8)

        # Draw tangent lines
        for td in getattr(self, 'tangent_data', []):
            x0, y0, slope = td["x0"], td["y0"], td["slope"]
            # Tangent line: y = slope*(x - x0) + y0
            x_left = max(self.x_min, x0 - (self.x_max - self.x_min) * 0.3)
            x_right = min(self.x_max, x0 + (self.x_max - self.x_min) * 0.3)
            y_left = slope * (x_left - x0) + y0
            y_right = slope * (x_right - x0) + y0
            self.ax_2d.plot([x_left, x_right], [y_left, y_right], 'c--',
                           linewidth=1.5, alpha=0.8, label=f"Tangent at x={x0:.3g}")
            self.ax_2d.plot(x0, y0, 'co', markersize=6)

        # Draw normal lines
        for nd in getattr(self, 'normal_data', []):
            x0, y0, slope = nd["x0"], nd["y0"], nd["slope"]
            if abs(slope) < 1e-12:
                # Vertical normal line
                y_bottom = max(self.y_min, y0 - (self.y_max - self.y_min) * 0.3)
                y_top = min(self.y_max, y0 + (self.y_max - self.y_min) * 0.3)
                self.ax_2d.plot([x0, x0], [y_bottom, y_top], 'y--',
                               linewidth=1.5, alpha=0.8, label=f"Normal at x={x0:.3g}")
            else:
                normal_slope = -1.0 / slope
                x_left = max(self.x_min, x0 - (self.x_max - self.x_min) * 0.3)
                x_right = min(self.x_max, x0 + (self.x_max - self.x_min) * 0.3)
                y_left = normal_slope * (x_left - x0) + y0
                y_right = normal_slope * (x_right - x0) + y0
                self.ax_2d.plot([x_left, x_right], [y_left, y_right], 'y--',
                               linewidth=1.5, alpha=0.8, label=f"Normal at x={x0:.3g}")
            self.ax_2d.plot(x0, y0, 'yo', markersize=6)

        visible_2d = [c for c in self.curves if c.visible and not c.is_3d]
        if visible_2d or self.tangent_data or self.normal_data:
            self.ax_2d.legend(loc="upper right", facecolor="#313244",
                           edgecolor="#585b70", labelcolor="#cdd6f4",
                           fontsize=9)

        self.canvas_2d.draw()
        self.status_var.set(
            t("status_plotted_2d", len(visible_2d), self.x_min, self.x_max))

    def _plot_3d(self):
        if self.ax_3d is None:
            return
        self.ax_3d.clear()
        self._setup_axes(self.ax_3d, is_3d=True)

        if self.x_min >= self.x_max or self.y_min >= self.y_max or self.n_pts_3d < 2:
            self.status_var.set(t("status_invalid_3d"))
            return
        n_pts = self.n_pts_3d
        x_vals = np.linspace(self.x_min, self.x_max, n_pts)
        y_vals = np.linspace(self.y_min, self.y_max, n_pts)
        X, Y = np.meshgrid(x_vals, y_vals)

        cmap_idx = 0
        for curve in self.curves:
            if not curve.visible or not curve.is_3d:
                continue
            expr = self._substitute_params(curve.expression)

            X_flat = X.flatten().tolist()
            Y_flat = Y.flatten().tolist()
            Z_flat = CalcEngine.evaluate_xy_array(expr, X_flat, Y_flat)
            Z = np.array([np.nan if z is None else z for z in Z_flat]).reshape(n_pts, n_pts)

            cmap = CMAP_3D_OPTIONS[cmap_idx % len(CMAP_3D_OPTIONS)]
            cmap_idx += 1
            rstride = max(1, n_pts // 40)
            cstride = max(1, n_pts // 40)
            self.ax_3d.plot_surface(X, Y, Z, cmap=cmap, alpha=0.8,
                                     rstride=rstride, cstride=cstride,
                                     antialiased=False)

        self.canvas_3d.draw()
        self.status_var.set(t("status_plotted_3d", n_pts, n_pts))

    def _setup_axes(self, ax, is_3d=False):
        try:
            ax.set_xlim(self.x_min, self.x_max)
            ax.set_ylim(self.y_min, self.y_max)
            if is_3d and hasattr(ax, 'set_zlim'):
                ax.set_zlim(self.z_min, self.z_max)
        except (ValueError, AttributeError):
            pass
        if hasattr(ax, 'grid'):
            ax.grid(self.grid_on, color="#45475a", alpha=0.5, linestyle="--")
        if not is_3d and hasattr(ax, 'axhline'):
            ax.axhline(y=0, color="#585b70", linewidth=0.8)
            ax.axvline(x=0, color="#585b70", linewidth=0.8)
        if is_3d:
            ax.set_xlabel("X")
            ax.set_ylabel("Y")
            ax.set_zlabel("Z")
        else:
            ax.set_xlabel("x")
            ax.set_ylabel("f(x)")
        ax.tick_params(colors="#cdd6f4")
        ax.set_facecolor("#181825")

    # ------------------------------------------------------------------
    #  Coordinate marking
    # ------------------------------------------------------------------
    def _on_canvas_click(self, event):
        if self.ax_2d is None or event.inaxes != self.ax_2d:
            return
        x, y = event.xdata, event.ydata
        if x is None or y is None:
            return

        # Left click (button 1) – add point
        if event.button == 1:
            self.marked_points.append((x, y))
            self._plot_all()
            self.status_var.set(t("status_marked", f"{x:.4f}", f"{y:.4f}"))

        # Right click (button 3) – delete nearest marked point
        elif event.button == 3:
            if not self.marked_points:
                self.status_var.set(t("status_no_points_del"))
                return

            nearest_idx = 0
            nearest_dist = float('inf')
            for i, (px, py) in enumerate(self.marked_points):
                dist = ((px - x) ** 2 + (py - y) ** 2) ** 0.5
                if dist < nearest_dist:
                    nearest_dist = dist
                    nearest_idx = i

            # Threshold = ~15 pixels converted to data coordinates
            pt_px = self.ax_2d.transData.transform((x, y))
            pt_px_away = (pt_px[0] + 15, pt_px[1])
            data_away = self.ax_2d.transData.inverted().transform(pt_px_away)
            threshold = abs(data_away[0] - x)

            if nearest_dist < threshold:
                removed = self.marked_points.pop(nearest_idx)
                self._plot_all()
                self.status_var.set(t("status_deleted", f"{removed[0]:.4f}", f"{removed[1]:.4f}"))
            else:
                self.status_var.set(t("status_right_no_point"))

    def _on_mark_point(self):
        try:
            x = float(self._var_mark_x.get())
            expr = self._get_active_expression()
            if not expr:
                return
            expr_sub = self._substitute_params(expr)
            y = CalcEngine.evaluate(expr_sub, x)
            if y is not None:
                self.auto_mark_point = x
                self._plot_all()
                self.status_var.set(t("status_marked_at", x, f"{x:.4f}", f"{y:.4f}"))
            else:
                messagebox.showerror(t("err_error"), t("msg_could_not_eval"))
        except ValueError:
            messagebox.showerror(t("err_error"), t("msg_invalid_x"))

    def _clear_marks(self):
        self.marked_points.clear()
        self.auto_mark_point = None
        self.intersection_marks.clear()
        self._var_mark_x.set("")
        self._plot_all()

    # ------------------------------------------------------------------
    #  Tangent & Normal Lines
    # ------------------------------------------------------------------
    def _on_draw_tangent(self):
        expr = self._get_active_expression()
        if not expr:
            return
        try:
            x0 = float(self._var_tan_x.get())
        except ValueError:
            messagebox.showerror(t("err_error"), t("msg_invalid_x"))
            return
        expr_sub = self._substitute_params(expr)
        y0 = CalcEngine.evaluate(expr_sub, x0)
        slope = CalcEngine.derivative(expr_sub, x0)
        if y0 is None or slope is None:
            err = CalcEngine.get_last_error()
            messagebox.showerror(t("err_error"), t("msg_could_not_tangent", err))
            return
        self.tangent_data.append({"x0": x0, "y0": y0, "slope": slope, "expr": expr})
        self._plot_all()
        self.status_var.set(t("status_tangent", x0, f"{slope:.4g}", f"{x0:.4g}", f"{y0:.4g}"))

    def _on_draw_normal(self):
        expr = self._get_active_expression()
        if not expr:
            return
        try:
            x0 = float(self._var_tan_x.get())
        except ValueError:
            messagebox.showerror(t("err_error"), t("msg_invalid_x"))
            return
        expr_sub = self._substitute_params(expr)
        y0 = CalcEngine.evaluate(expr_sub, x0)
        slope = CalcEngine.derivative(expr_sub, x0)
        if y0 is None or slope is None:
            err = CalcEngine.get_last_error()
            messagebox.showerror(t("err_error"), t("msg_could_not_normal", err))
            return
        self.normal_data.append({"x0": x0, "y0": y0, "slope": slope, "expr": expr})
        self._plot_all()
        if abs(slope) < 1e-12:
            self.status_var.set(t("status_normal_vert", x0, x0))
        else:
            normal_slope = -1.0 / slope
            self.status_var.set(t("status_normal_line", x0, f"{normal_slope:.4g}", f"{x0:.4g}", f"{y0:.4g}"))

    def _clear_tangent_normal(self):
        self.tangent_data.clear()
        self.normal_data.clear()
        self._plot_all()
        self.status_var.set(t("status_cleared_tan"))

    # ------------------------------------------------------------------
    #  Intersection Finder
    # ------------------------------------------------------------------
    def _show_intersection_dialog(self):
        curves_2d = [c for c in self.curves if not c.is_3d]
        if len(curves_2d) < 2:
            messagebox.showinfo(t("err_info"), t("msg_add_two_curves"))
            return
        win = tk.Toplevel(self.root)
        win.title(t("win_intersect"))
        win.geometry("420x420")
        win.configure(bg="#1e1e2e")
        win.minsize(320, 300)
        win.transient(self.root)
        win.grab_set()

        ttk.Label(win, text=t("intersect_select"),
                  style="Dark.TLabel").pack(anchor=tk.W, padx=10, pady=(10, 4))

        # Curve A
        ttk.Label(win, text=t("intersect_curve_a"), style="Dark.TLabel").pack(anchor=tk.W, padx=10, pady=(8, 0))
        var_a = tk.StringVar()
        combo_a = ttk.Combobox(win, textvariable=var_a,
                               values=[c.label for c in curves_2d],
                               state="readonly", font=("Consolas", 10), width=40)
        combo_a.pack(fill=tk.X, padx=10, pady=2)
        combo_a.current(0)

        # Curve B
        ttk.Label(win, text=t("intersect_curve_b"), style="Dark.TLabel").pack(anchor=tk.W, padx=10, pady=(8, 0))
        var_b = tk.StringVar()
        combo_b = ttk.Combobox(win, textvariable=var_b,
                               values=[c.label for c in curves_2d],
                               state="readonly", font=("Consolas", 10), width=40)
        combo_b.pack(fill=tk.X, padx=10, pady=2)
        if len(curves_2d) > 1:
            combo_b.current(1)
        else:
            combo_b.current(0)

        result_text = tk.Text(win, height=10, bg="#313244", fg="#cdd6f4",
                              font=("Consolas", 10), wrap=tk.WORD, state=tk.DISABLED)
        result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        def do_find():
            label_a = var_a.get()
            label_b = var_b.get()
            if not label_a or not label_b:
                messagebox.showwarning(t("err_input"), t("msg_select_both"), parent=win)
                return
            if label_a == label_b:
                messagebox.showwarning(t("err_input"), t("msg_select_different"), parent=win)
                return
            curve_a = None
            curve_b = None
            for c in self.curves:
                if c.label == label_a:
                    curve_a = c
                if c.label == label_b:
                    curve_b = c
            if curve_a is None or curve_b is None:
                messagebox.showerror(t("err_error"), t("msg_could_not_locate"), parent=win)
                return
            intersections = self._find_intersections(curve_a, curve_b)
            result_text.configure(state=tk.NORMAL)
            result_text.delete("1.0", tk.END)
            if intersections:
                result_text.insert(tk.END, t("msg_found_intersect", len(intersections)) + "\n\n")
                for i, (xi, yi) in enumerate(intersections, 1):
                    result_text.insert(tk.END, f"  {i}. x = {xi:.10g}, y = {yi:.10g}\n")
            else:
                result_text.insert(tk.END, t("msg_no_intersect") + "\n")
            result_text.configure(state=tk.DISABLED)
            self._plot_all()

        btn_frame = ttk.Frame(win, style="Dark.TFrame")
        btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        ttk.Button(btn_frame, text=t("btn_find_intersections2"), command=do_find).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text=t("btn_clear_marks"), command=lambda: (self.intersection_marks.clear(), self._plot_all())).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text=t("btn_close"), command=win.destroy).pack(side=tk.RIGHT, padx=2)

    def _find_intersections(self, curve_a, curve_b):
        """Find intersections of two 2D curves within the current X range."""
        if curve_a.is_parametric or curve_b.is_parametric or curve_a.is_polar or curve_b.is_polar:
            self.intersection_marks = []
            return []
        if self.x_min >= self.x_max or self.step_size <= 0:
            self.intersection_marks = []
            return []
        expr_a = self._substitute_params(curve_a.expression)
        expr_b = self._substitute_params(curve_b.expression)

        n_samples = max(MIN_PLOT_POINTS, min(MAX_PLOT_POINTS, int((self.x_max - self.x_min) / self.step_size)))
        xs = np.linspace(self.x_min, self.x_max, n_samples)
        xs_list = xs.tolist()

        ys_a = CalcEngine.evaluate_array(expr_a, xs_list)
        ys_b = CalcEngine.evaluate_array(expr_b, xs_list)

        tol_zero = 1e-6
        tol_dup = 1e-4
        intersections = []

        # Detect near-zero differences
        for i, (ya, yb) in enumerate(zip(ys_a, ys_b)):
            if ya is not None and yb is not None and abs(ya - yb) < tol_zero:
                intersections.append((float(xs[i]), float((ya + yb) / 2.0)))

        # Detect sign changes and refine with bisection
        for i in range(n_samples - 1):
            y1a = ys_a[i]
            y1b = ys_b[i]
            y2a = ys_a[i + 1]
            y2b = ys_b[i + 1]
            if y1a is None or y1b is None or y2a is None or y2b is None:
                continue
            diff1 = y1a - y1b
            diff2 = y2a - y2b
            if diff1 == 0.0 or diff2 == 0.0:
                continue
            if diff1 * diff2 < 0:
                diff_expr = f"({expr_a})-({expr_b})"
                root = CalcEngine.solve_bisection(diff_expr, float(xs[i]), float(xs[i + 1]))
                if root is not None:
                    y_at_root = CalcEngine.evaluate(expr_a, root)
                    if y_at_root is not None:
                        intersections.append((root, y_at_root))

        # Deduplicate and sort by x
        intersections.sort(key=lambda p: p[0])
        unique = []
        for p in intersections:
            if not unique or abs(p[0] - unique[-1][0]) > tol_dup:
                unique.append(p)

        self.intersection_marks = unique
        return unique

    # ------------------------------------------------------------------
    #  Function Table
    # ------------------------------------------------------------------
    def _on_generate_table(self):
        expr = self._get_active_expression()
        if not expr:
            return
        try:
            a = float(self._var_tbl_from.get())
            b = float(self._var_tbl_to.get())
            n = int(self._var_tbl_n.get())
        except ValueError:
            messagebox.showerror(t("err_error"), t("msg_invalid_table"))
            return
        if a >= b:
            messagebox.showerror(t("err_error"), t("msg_from_less_to"))
            return
        if n < 2 or n > 5000:
            messagebox.showerror(t("err_error"), t("msg_points_range"))
            return

        expr_sub = self._substitute_params(expr)
        xs = [a + (b - a) * i / (n - 1) for i in range(n)]
        ys = CalcEngine.evaluate_array(expr_sub, xs)

        self._table_data = []
        valid_count = 0
        for x, y in zip(xs, ys):
            self._table_data.append((x, y))
            if y is not None:
                valid_count += 1
        self._table_expr = expr

        self._show_table_window(expr, valid_count)
        self.status_var.set(t("status_table_gen", valid_count, n))

    def _show_table_window(self, expr, valid_count):
        win = tk.Toplevel(self.root)
        win.title(t("win_table"))
        win.geometry("420x500")
        win.configure(bg="#1e1e2e")
        win.minsize(320, 300)

        ttk.Label(win, text=f"f(x) = {expr}", style="Dark.TLabel").pack(anchor=tk.W, padx=10, pady=(10, 4))
        ttk.Label(win, text=f"Valid points: {valid_count} / {len(self._table_data)}", style="Dark.TLabel").pack(anchor=tk.W, padx=10, pady=(0, 6))

        # Use a treeview for clean tabular display
        cols = ("x", "f(x)")
        tree = ttk.Treeview(win, columns=cols, show="headings", height=18)
        tree.heading("x", text="x")
        tree.heading("f(x)", text="f(x)")
        tree.column("x", width=180, anchor="center")
        tree.column("f(x)", width=180, anchor="center")
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Style the treeview for dark theme
        style = ttk.Style(win)
        style.configure("Treeview", background="#313244", foreground="#cdd6f4",
                        fieldbackground="#313244", rowheight=22)
        style.configure("Treeview.Heading", background="#45475a", foreground="#cdd6f4")

        for x, y in self._table_data:
            xv = f"{x:.10g}"
            yv = f"{y:.10g}" if y is not None else "N/A"
            tree.insert("", tk.END, values=(xv, yv))

        ttk.Button(win, text=t("btn_close"), command=win.destroy).pack(pady=(0, 10))

    def _on_export_csv(self):
        if not self._table_data:
            messagebox.showinfo(t("err_info"), t("msg_generate_table"))
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export Function Table"
        )
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["x", f"f(x) = {self._table_expr}"])
                for x, y in self._table_data:
                    writer.writerow([x, y if y is not None else ""])
            self.status_var.set(t("status_exported_table", os.path.basename(path)))
        except Exception as e:
            messagebox.showerror(t("err_export"), str(e))

    def _on_copy_table(self):
        if not self._table_data:
            messagebox.showinfo(t("err_info"), t("msg_generate_table"))
            return
        lines = [f"x\tf(x) = {self._table_expr}"]
        for x, y in self._table_data:
            lines.append(f"{x:.10g}\t{y if y is not None else 'N/A'}")
        text = "\n".join(lines)
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.status_var.set(t("status_table_copied"))

    # ------------------------------------------------------------------
    #  Calculus operations
    # ------------------------------------------------------------------
    def _get_active_expression(self) -> Optional[str]:
        sel = self.listbox_curves.curselection()
        if sel:
            curve = self.curves[sel[0]]
            if curve.is_parametric:
                messagebox.showwarning(t("err_parametric"),
                    t("msg_parametric_no_calc"))
                return None
            if curve.is_polar:
                messagebox.showwarning(t("err_polar"),
                    t("msg_polar_no_calc"))
                return None
            return curve.expression
        for c in reversed(self.curves):
            if not c.is_parametric and not c.is_polar:
                return c.expression
        expr = self.entry_expr.get().strip()
        if expr:
            return expr
        messagebox.showwarning(t("err_no_expr"), t("msg_add_func"))
        return None

    def _on_derivative(self):
        expr = self._get_active_expression()
        if not expr:
            return
        try:
            x_val = float(self._var_diff_x.get())
        except ValueError:
            messagebox.showerror(t("err_error"), t("msg_invalid_x"))
            return
        expr_sub = self._substitute_params(expr)
        result = CalcEngine.derivative(expr_sub, x_val)
        if result is None:
            err = CalcEngine.get_last_error()
            messagebox.showerror(t("err_error"), t("msg_deriv_failed", err))
            return
        messagebox.showinfo(
            t("msg_deriv_result"),
            f"f(x) = {expr}\n"
            f"f'({x_val}) = {result:.10g}")
        self.status_var.set(t("status_deriv_result", x_val, f"{result:.10g}"))

    def _on_derivative2(self):
        expr = self._get_active_expression()
        if not expr:
            return
        try:
            x_val = float(self._var_diff_x.get())
        except ValueError:
            messagebox.showerror(t("err_error"), t("msg_invalid_x"))
            return
        expr_sub = self._substitute_params(expr)
        result = CalcEngine.derivative2(expr_sub, x_val)
        if result is None:
            err = CalcEngine.get_last_error()
            messagebox.showerror(t("err_error"), t("msg_deriv2_failed", err))
            return
        messagebox.showinfo(
            t("msg_deriv2_result"),
            f"f(x) = {expr}\n"
            f"f''({x_val}) = {result:.10g}")
        self.status_var.set(t("status_deriv2_result", x_val, f"{result:.10g}"))

    def _on_integrate(self):
        expr = self._get_active_expression()
        if not expr:
            return
        try:
            a = float(self._var_int_a.get())
            b = float(self._var_int_b.get())
        except ValueError:
            messagebox.showerror(t("err_error"), t("msg_invalid_bounds"))
            return
        expr_sub = self._substitute_params(expr)
        result = CalcEngine.integrate_adaptive(expr_sub, a, b)
        if result is None:
            err = CalcEngine.get_last_error()
            messagebox.showerror(t("err_error"), t("msg_integ_failed", err))
            return
        messagebox.showinfo(
            t("msg_integ_result"),
            f"f(x) = {expr}\n"
            f"Integrate [{a}, {b}] f(x) dx = {result:.10g}")
        self.status_var.set(t("status_integrate", a, b, f"{result:.10g}"))

    def _on_arc_length(self):
        expr = self._get_active_expression()
        if not expr:
            return
        try:
            a = float(self._var_int_a.get())
            b = float(self._var_int_b.get())
        except ValueError:
            messagebox.showerror(t("err_error"), t("msg_invalid_arc_bounds"))
            return
        if a >= b:
            messagebox.showerror(t("err_error"), t("msg_a_less_b"))
            return
        expr_sub = self._substitute_params(expr)
        result = CalcEngine.arc_length(expr_sub, a, b)
        if result is None:
            messagebox.showerror(t("err_error"), t("msg_could_not_arc"))
            return
        messagebox.showinfo(
            t("msg_arc_result"),
            f"f(x) = {expr}\n"
            f"Arc length from {a} to {b} = {result:.10g}")
        self.status_var.set(t("status_arc", a, b, f"{result:.10g}"))

    def _on_area_between_curves(self):
        expr_f = self._var_area_f.get().strip()
        expr_g = self._var_area_g.get().strip()
        if not expr_f or not expr_g:
            messagebox.showwarning(t("err_input"), t("msg_enter_fg"))
            return
        try:
            a_str = self._resolve_t_range(self._var_area_a.get())
            b_str = self._resolve_t_range(self._var_area_b.get())
            a = float(a_str)
            b = float(b_str)
        except ValueError:
            messagebox.showerror(t("err_error"), t("msg_invalid_interval"))
            return
        if a >= b:
            messagebox.showerror(t("err_error"), t("msg_a_less_b"))
            return
        f_sub = self._substitute_params(expr_f)
        g_sub = self._substitute_params(expr_g)
        result = CalcEngine.area_between_curves(f_sub, g_sub, a, b)
        if result is None:
            err = CalcEngine.get_last_error()
            messagebox.showerror(t("err_error"), t("msg_could_not_area", err))
            return
        messagebox.showinfo(
            t("msg_area_result"),
            f"f(x) = {expr_f}\n"
            f"g(x) = {expr_g}\n"
            f"Area from {a} to {b} = {result:.10g}")
        self.status_var.set(t("status_area", a, b, f"{result:.10g}"))

    def _on_limit(self, two_sided=True, side=None):
        expr = self._get_active_expression()
        if not expr:
            return
        try:
            a = float(self._var_limit_a.get())
        except ValueError:
            messagebox.showerror(t("err_error"), t("msg_invalid_limit"))
            return
        expr_sub = self._substitute_params(expr)

        if two_sided:
            left  = CalcEngine.limit_left(expr_sub, a)
            right = CalcEngine.limit_right(expr_sub, a)
            if left is None and right is None:
                err = CalcEngine.get_last_error()
                messagebox.showerror(t("err_limit"), t("msg_could_not_limit", err))
                return
            if left is not None and right is not None and abs(left - right) < 1e-8:
                val = (left + right) / 2.0
                messagebox.showinfo(
                    t("msg_limit_result"),
                    f"f(x) = {expr}\n"
                    f"lim(x→{a}) f(x) = {val:.10g}\n"
                    f"Left:  {left:.10g}\n"
                    f"Right: {right:.10g}")
                self.status_var.set(t("status_limit", a, f"{val:.10g}"))
            else:
                msg = f"f(x) = {expr}\n\n"
                if left is not None:
                    msg += f"lim(x→{a}⁻) = {left:.10g}\n"
                else:
                    msg += f"lim(x→{a}⁻) = DNE (undefined)\n"
                if right is not None:
                    msg += f"lim(x→{a}⁺) = {right:.10g}\n"
                else:
                    msg += f"lim(x→{a}⁺) = DNE (undefined)\n"
                msg += "\nTwo-sided limit does not exist."
                messagebox.showwarning(t("err_limit_dne"), msg)
                self.status_var.set(t("status_limit_dne", a))
        elif side == "left":
            result = CalcEngine.limit_left(expr_sub, a)
            if result is None:
                err = CalcEngine.get_last_error()
                messagebox.showerror(t("err_limit"), t("msg_could_not_left_limit", err))
                return
            messagebox.showinfo(
                t("msg_left_limit_result"),
                f"f(x) = {expr}\n"
                f"lim(x→{a}⁻) f(x) = {result:.10g}")
            self.status_var.set(t("status_left_limit", a, f"{result:.10g}"))
        else:
            result = CalcEngine.limit_right(expr_sub, a)
            if result is None:
                err = CalcEngine.get_last_error()
                messagebox.showerror(t("err_limit"), t("msg_could_not_right_limit", err))
                return
            messagebox.showinfo(
                t("msg_right_limit_result"),
                f"f(x) = {expr}\n"
                f"lim(x→{a}⁺) f(x) = {result:.10g}")
            self.status_var.set(t("status_right_limit", a, f"{result:.10g}"))

    def _on_fft_compute(self):
        expr = self._get_active_expression()
        if not expr:
            return
        try:
            a = float(self._var_int_a.get())
            b = float(self._var_int_b.get())
            n = int(self._var_fft_n.get())
        except ValueError:
            messagebox.showerror(t("err_error"), t("msg_invalid_fft"))
            return
        if a >= b:
            messagebox.showerror(t("err_error"), t("msg_a_less_b"))
            return
        if n < 2 or n > 65536:
            messagebox.showerror(t("err_error"), t("msg_samples_range"))
            return

        expr_sub = self._substitute_params(expr)
        result = CalcEngine.fft_spectrum(expr_sub, a, b, n)
        if result is None:
            messagebox.showerror(t("err_error"), t("msg_could_not_fft"))
            return
        self._fft_data = result
        self._ensure_fft_window()
        self._plot_fft(result, expr)
        self.status_var.set(t("status_fft_computed", len(result['freqs'])))

    def _plot_fft(self, result, expr):
        if self.ax_fft_amp is None or self.ax_fft_phase is None:
            return
        freqs = np.array(result['freqs'])
        amps = np.array(result['amps'])
        phases = np.array(result['phases'])

        self.ax_fft_amp.clear()
        self.ax_fft_phase.clear()
        self._setup_axes(self.ax_fft_amp, is_3d=False)
        self._setup_axes(self.ax_fft_phase, is_3d=False)

        self.ax_fft_amp.set_title(f"Amplitude Spectrum — {expr}", color="#cdd6f4", fontsize=11)
        self.ax_fft_phase.set_title(f"Phase Spectrum — {expr}", color="#cdd6f4", fontsize=11)
        self.ax_fft_amp.set_xlabel("Frequency")
        self.ax_fft_amp.set_ylabel("Amplitude")
        self.ax_fft_phase.set_xlabel("Frequency")
        self.ax_fft_phase.set_ylabel("Phase (rad)")

        # Amplitude plot with stem-like visualization using vlines for performance
        self.ax_fft_amp.plot(freqs, amps, color="#00e5c9", linewidth=1.2, alpha=0.9)
        self.ax_fft_amp.fill_between(freqs, amps, color="#00e5c9", alpha=0.15)
        # Highlight dominant frequencies
        if len(amps) > 1:
            peak_idx = int(np.argmax(amps[1:])) + 1
            if peak_idx < len(freqs) and peak_idx < len(amps):
                self.ax_fft_amp.plot(freqs[peak_idx], amps[peak_idx], 'ro', markersize=8)
                self.ax_fft_amp.annotate(f"f={freqs[peak_idx]:.4g}, A={amps[peak_idx]:.4g}",
                                         xy=(freqs[peak_idx], amps[peak_idx]),
                                         xytext=(10, 10), textcoords='offset points',
                                         color='#f38ba8', fontsize=9)

        # Phase plot
        self.ax_fft_phase.plot(freqs, phases, color="#4f8cff", linewidth=1.0, alpha=0.8)
        self.ax_fft_phase.axhline(y=0, color="#585b70", linewidth=0.5, linestyle="--")

        self.canvas_fft.draw()

    def _on_export_fft_csv(self):
        if not self._fft_data or not self._fft_data.get('freqs'):
            messagebox.showinfo(t("err_info"), t("msg_compute_fft"))
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export FFT Spectrum"
        )
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Frequency", "Amplitude", "Phase_rad"])
                for fr, am, ph in zip(self._fft_data['freqs'],
                                      self._fft_data['amps'],
                                      self._fft_data['phases']):
                    writer.writerow([fr, am, ph])
            self.status_var.set(t("status_exported_fft", os.path.basename(path)))
        except Exception as e:
            messagebox.showerror(t("err_export"), str(e))

    # ------------------------------------------------------------------
    #  Taylor Series Expansion
    # ------------------------------------------------------------------
    def _on_taylor_expand(self):
        expr = self._get_active_expression()
        if not expr:
            return
        try:
            a = float(self._var_taylor_a.get())
            order = int(self._var_taylor_order.get())
        except ValueError:
            messagebox.showerror(t("err_error"), t("msg_invalid_taylor"))
            return
        if order < 1 or order > 20:
            messagebox.showerror(t("err_error"), t("msg_order_range"))
            return

        expr_sub = self._substitute_params(expr)
        coeffs = CalcEngine.taylor_coefficients(expr_sub, a, order)
        if coeffs is None:
            err = CalcEngine.get_last_error()
            messagebox.showerror(t("err_taylor"), t("msg_could_not_taylor", err))
            return

        terms = []
        for k, c in enumerate(coeffs):
            if c is None or abs(c) < 1e-15:
                continue
            if k == 0:
                terms.append(f"{c:.10g}")
            elif k == 1:
                terms.append(f"{c:.10g}·(x-{a:.10g})")
            else:
                terms.append(f"{c:.10g}·(x-{a:.10g})^{k}")

        poly_str = " + ".join(terms) if terms else "0"

        coeff_lines = []
        for k, c in enumerate(coeffs):
            if c is not None:
                coeff_lines.append(f"  c_{k} = {c:.12g}")
            else:
                coeff_lines.append(f"  c_{k} = N/A")
        coeff_str = "\n".join(coeff_lines)

        result_msg = (
            f"f(x) = {expr}\n"
            f"Taylor expansion at a = {a}, order = {order}:\n\n"
            f"T(x) = {poly_str}\n\n"
            f"Coefficients (c_k = f^(k)(a)/k!):\n{coeff_str}"
        )
        messagebox.showinfo(t("msg_taylor_series"), result_msg)
        self.status_var.set(t("status_taylor", a, order))

    def _on_taylor_plot(self):
        expr = self._get_active_expression()
        if not expr:
            return
        try:
            a = float(self._var_taylor_a.get())
            order = int(self._var_taylor_order.get())
        except ValueError:
            messagebox.showerror(t("err_error"), t("msg_invalid_taylor"))
            return
        if order < 1 or order > 20:
            messagebox.showerror(t("err_error"), t("msg_order_range"))
            return

        expr_sub = self._substitute_params(expr)
        coeffs = CalcEngine.taylor_coefficients(expr_sub, a, order)
        if coeffs is None:
            err = CalcEngine.get_last_error()
            messagebox.showerror(t("err_taylor"), t("msg_could_not_taylor", err))
            return

        n_pts = max(MIN_PLOT_POINTS, min(MAX_PLOT_POINTS, int((self.x_max - self.x_min) / self.step_size)))
        xs_np = np.linspace(self.x_min, self.x_max, n_pts)
        xs_list = xs_np.tolist()

        # Original function
        ys_orig = CalcEngine.evaluate_array(expr_sub, xs_list)
        ys_orig_np = np.array([y if y is not None else np.nan for y in ys_orig])

        # Taylor polynomial
        dx_arr = xs_np - a
        ys_taylor = np.zeros(n_pts)
        dx_power = np.ones(n_pts)
        for k, c in enumerate(coeffs):
            if c is not None:
                ys_taylor += c * dx_power
            dx_power *= dx_arr

        self._ensure_2d_window()
        self.ax_2d.clear()
        self._setup_axes(self.ax_2d, is_3d=False)

        self.ax_2d.plot(xs_np, ys_orig_np, color="#1f77b4", linewidth=2,
                        label=f"Original: {expr}", alpha=0.9)
        self.ax_2d.plot(xs_np, ys_taylor, color="#ff7f0e", linewidth=2, linestyle="--",
                        label=f"Taylor (order {order})", alpha=0.9)

        # Mark expansion point
        y_at_a = CalcEngine.evaluate(expr_sub, a)
        if y_at_a is not None:
            self.ax_2d.plot(a, y_at_a, 'go', markersize=8)
            self.ax_2d.annotate(f"a={a:.3g}", xy=(a, y_at_a), xytext=(10, 10),
                                textcoords='offset points', color='#a6e3a1', fontsize=9)

        self.ax_2d.legend(loc="upper right", facecolor="#313244",
                          edgecolor="#585b70", labelcolor="#cdd6f4", fontsize=9)
        self.canvas_2d.draw()
        self.status_var.set(t("status_taylor_plot", a, order))

    # ------------------------------------------------------------------
    #  ODE Solver (RK4)
    # ------------------------------------------------------------------
    def _on_ode_solve(self):
        expr = self._var_ode_expr.get().strip()
        if not expr:
            messagebox.showwarning(t("err_input"), t("msg_enter_ode"))
            return
        try:
            x0 = float(self._var_ode_x0.get())
            y0 = float(self._var_ode_y0.get())
            x_end = float(self._var_ode_xend.get())
            n_steps = int(self._var_ode_steps.get())
        except ValueError:
            messagebox.showerror(t("err_error"), t("msg_invalid_ode"))
            return
        if n_steps < 1 or n_steps > 100000:
            messagebox.showerror(t("err_error"), t("msg_steps_range"))
            return
        if x0 == x_end:
            messagebox.showerror(t("err_error"), t("msg_x0_neq_xend"))
            return

        result = CalcEngine.ode_solve_rk4(expr, x0, y0, x_end, n_steps)
        if result is None:
            err = CalcEngine.get_last_error()
            messagebox.showerror(t("err_ode"), t("msg_could_not_ode", err))
            return
        self._ode_data = result

        lines = [f"dy/dx = {expr},  y({x0}) = {y0}"]
        lines.append(f"Solved over [{x0}, {x_end}] with {n_steps} steps (RK4)\n")
        lines.append(f"{'x':>14s}  {'y(x)':>14s}")
        lines.append("-" * 30)
        n_show = min(len(result['xs']), 50)
        step = max(1, len(result['xs']) // n_show) if len(result['xs']) > n_show else 1
        for i in range(0, len(result['xs']), step):
            xi = result['xs'][i]
            yi = result['ys'][i]
            y_str = f"{yi:.10g}" if yi is not None else "N/A"
            lines.append(f"{xi:14.10g}  {y_str:>14s}")
        if len(result['xs']) > n_show:
            lines.append(f"  ... ({len(result['xs'])} total points)")

        msg = "\n".join(lines)
        messagebox.showinfo(t("msg_ode_solution"), msg)
        self.status_var.set(t("status_ode_solved", len(result['xs'])))

    def _on_ode_plot(self):
        if self._ode_data is None:
            messagebox.showinfo(t("err_info"), t("msg_solve_ode_first"))
            return
        self._ensure_2d_window()
        self.ax_2d.clear()
        self._setup_axes(self.ax_2d, is_3d=False)

        xs = np.array(self._ode_data['xs'])
        ys = np.array([y if y is not None else np.nan for y in self._ode_data['ys']])

        if len(xs) == 0 or len(ys) == 0:
            self.status_var.set(t("msg_no_ode_points"))
            return

        expr = self._var_ode_expr.get().strip()
        x0 = self._var_ode_x0.get()
        y0 = self._var_ode_y0.get()
        self.ax_2d.plot(xs, ys, color="#00e5c9", linewidth=2,
                        label=f"RK4: dy/dx={expr}", alpha=0.9)
        self.ax_2d.plot(xs[0], ys[0], 'go', markersize=8,
                        label=f"y({x0})={y0}")

        self.ax_2d.legend(loc="upper right", facecolor="#313244",
                          edgecolor="#585b70", labelcolor="#cdd6f4", fontsize=9)
        self.canvas_2d.draw()
        self.status_var.set(t("status_ode_plotted", len(xs)))

    def _on_ode_preset(self, name: str):
        """Load an ODE preset into the input fields."""
        preset = ODE_PRESETS.get(name)
        if preset:
            expr, x0, y0, x_end, steps = preset
            self._var_ode_expr.set(expr)
            self._var_ode_x0.set(x0)
            self._var_ode_y0.set(y0)
            self._var_ode_xend.set(x_end)
            self._var_ode_steps.set(steps)

    # ------------------------------------------------------------------
    #  Equation Solver
    # ------------------------------------------------------------------
    def _on_solve(self):
        expr = self._get_active_expression()
        if not expr:
            return
        try:
            guess = float(self._var_guess.get())
            a = float(self._var_solve_a.get())
            b = float(self._var_solve_b.get())
        except ValueError:
            messagebox.showerror(t("err_error"), t("msg_invalid_solver"))
            return
        if a >= b:
            messagebox.showerror(t("err_error"), t("msg_left_less_right"))
            return
        expr_sub = self._substitute_params(expr)
        result = CalcEngine.solve(expr_sub, guess=guess, xmin=a, xmax=b)
        if result is None:
            err = CalcEngine.get_last_error()
            messagebox.showerror(t("err_solver"),
                                 t("msg_could_not_root", err))
            return
        verify = CalcEngine.evaluate(expr_sub, result)
        verify_str = f"{verify:.2e}" if verify is not None else "N/A"
        messagebox.showinfo(
            t("msg_root_found"),
            f"f(x) = {expr} = 0\n"
            f"Root: x = {result:.12g}\n"
            f"Verification: f({result:.6g}) = {verify_str}")
        self.status_var.set(t("status_root", f"{result:.12g}"))

    def _on_solve_bisection(self):
        expr = self._get_active_expression()
        if not expr:
            return
        try:
            a = float(self._var_solve_a.get())
            b = float(self._var_solve_b.get())
        except ValueError:
            messagebox.showerror(t("err_error"), t("msg_invalid_bounds_val"))
            return
        if a >= b:
            messagebox.showerror(t("err_error"), t("msg_left_less_right"))
            return
        expr_sub = self._substitute_params(expr)
        result = CalcEngine.solve_bisection(expr_sub, a, b)
        if result is None:
            err = CalcEngine.get_last_error()
            messagebox.showerror(t("err_bisection"),
                                 t("msg_could_not_root", err))
            return
        messagebox.showinfo(
            t("msg_root_found_bisection"),
            f"f(x) = {expr} = 0\n"
            f"Root: x = {result:.12g}")
        self.status_var.set(t("status_root", f"{result:.12g}"))

    def _on_solve_system_2d(self):
        f_expr = self._var_sys_f.get().strip()
        g_expr = self._var_sys_g.get().strip()
        if not f_expr or not g_expr:
            messagebox.showerror(t("err_error"), t("msg_enter_fg_xy"))
            return
        try:
            x0 = float(self._var_sys_x0.get())
            y0 = float(self._var_sys_y0.get())
        except ValueError:
            messagebox.showerror(t("err_error"), t("msg_invalid_guess"))
            return
        f_sub = self._substitute_params(f_expr)
        g_sub = self._substitute_params(g_expr)
        if not f_sub or not g_sub:
            messagebox.showerror(t("err_error"), t("msg_empty_after_sub"))
            return
        result = CalcEngine.solve_system_2d(f_sub, g_sub, x0, y0)
        if result is None:
            err = CalcEngine.get_last_error()
            messagebox.showerror(t("err_system"),
                                 t("msg_could_not_system", err))
            return
        x_sol = result['x']
        y_sol = result['y']
        f_val = CalcEngine.evaluate_xy(f_sub, x_sol, y_sol)
        g_val = CalcEngine.evaluate_xy(g_sub, x_sol, y_sol)
        f_str = f"{f_val:.2e}" if f_val is not None else "N/A"
        g_str = f"{g_val:.2e}" if g_val is not None else "N/A"
        messagebox.showinfo(
            t("msg_system_solved"),
            f"f(x,y) = {f_expr}\ng(x,y) = {g_expr}\n\n"
            f"Solution:\n  x = {x_sol:.12g}\n  y = {y_sol:.12g}\n\n"
            f"Residuals:\n  f(x,y) = {f_str}\n  g(x,y) = {g_str}")
        self.status_var.set(t("status_system", f"{x_sol:.10g}", f"{y_sol:.10g}"))

    def _on_find_extremum(self, minimum: bool = True):
        expr = self._get_active_expression()
        if not expr:
            return
        try:
            a = float(self._var_ext_a.get())
            b = float(self._var_ext_b.get())
        except ValueError:
            messagebox.showerror(t("err_error"), t("msg_invalid_interval"))
            return
        if a >= b:
            messagebox.showerror(t("err_error"), t("msg_left_less_right"))
            return
        expr_sub = self._substitute_params(expr)
        if minimum:
            result = CalcEngine.find_minimum(expr_sub, a, b)
            label = "Minimum"
            short = "min"
        else:
            result = CalcEngine.find_maximum(expr_sub, a, b)
            label = "Maximum"
            short = "max"
        if result is None:
            err = CalcEngine.get_last_error()
            messagebox.showerror(t("err_extremum"),
                                 t("msg_could_not_extremum", label.lower(), err))
            return
        f_val = CalcEngine.evaluate(expr_sub, result)
        verify_str = f"{f_val:.10g}" if f_val is not None else "N/A"
        messagebox.showinfo(
            t("msg_extremum_found", label),
            f"f(x) = {expr}\n"
            f"{label}: x = {result:.12g}\n"
            f"f({result:.6g}) = {verify_str}")
        self.status_var.set(t("status_extremum", label, f"{result:.12g}", verify_str))

    def _on_scan_roots(self):
        expr = self._get_active_expression()
        if not expr:
            return
        try:
            a = float(self._var_ext_a.get())
            b = float(self._var_ext_b.get())
        except ValueError:
            messagebox.showerror(t("err_error"), t("msg_invalid_interval"))
            return
        if a >= b:
            messagebox.showerror(t("err_error"), t("msg_a_less_b"))
            return

        expr_sub = self._substitute_params(expr)
        n_samples = 2000
        tol_zero = 1e-6
        tol_dup = 1e-4

        xs = np.linspace(a, b, n_samples)
        ys = CalcEngine.evaluate_array(expr_sub, xs.tolist())

        roots = []
        # Detect points close to zero
        for i, y in enumerate(ys):
            if y is not None and abs(y) < tol_zero:
                roots.append(float(xs[i]))

        # Detect sign changes and refine with bisection
        for i in range(n_samples - 1):
            y1 = ys[i]
            y2 = ys[i + 1]
            if y1 is None or y2 is None:
                continue
            if y1 == 0.0 or y2 == 0.0:
                continue
            if y1 * y2 < 0:
                root = CalcEngine.solve_bisection(expr_sub, float(xs[i]), float(xs[i + 1]))
                if root is not None:
                    roots.append(root)

        # Deduplicate and sort
        roots.sort()
        unique_roots = []
        for r in roots:
            if not unique_roots or abs(r - unique_roots[-1]) > tol_dup:
                unique_roots.append(r)

        self.root_markers = unique_roots
        self._plot_all()

        if unique_roots:
            lines = [f"Found {len(unique_roots)} root(s):"]
            for i, r in enumerate(unique_roots[:20], 1):
                verify = CalcEngine.evaluate(expr_sub, r)
                v_str = f"{verify:.2e}" if verify is not None else "N/A"
                lines.append(f"  x{i} = {r:.12g}  (f={v_str})")
            if len(unique_roots) > 20:
                lines.append(f"  ... and {len(unique_roots) - 20} more")
            msg = "\n".join(lines)
            messagebox.showinfo(t("err_root_scan"), msg)
            self.status_var.set(t("status_found_roots", len(unique_roots)))
        else:
            messagebox.showinfo(t("err_root_scan"), t("msg_no_roots"))
            self.status_var.set(t("status_no_roots"))

    # ------------------------------------------------------------------
    #  Statistics Calculator
    # ------------------------------------------------------------------
    def _parse_stats_data(self):
        """Parse comma/space/semicolon separated data from input."""
        raw = self._var_stats_data.get().strip()
        if not raw:
            return None
        import re as _re
        tokens = _re.split(r'[,;\s]+', raw)
        values = []
        for tok in tokens:
            tok = tok.strip()
            if not tok:
                continue
            try:
                values.append(float(tok))
            except ValueError:
                messagebox.showerror(t("err_input"), t("msg_invalid_number", tok))
                return None
        if not values:
            messagebox.showerror(t("err_input"), t("msg_no_valid_nums"))
            return None
        return values

    def _on_stats_compute(self):
        values = self._parse_stats_data()
        if values is None:
            return
        import statistics as _stats

        n = len(values)
        data_sorted = sorted(values)
        data_sum = sum(values)
        data_mean = _stats.mean(values)
        data_median = _stats.median(values)

        try:
            data_mode = _stats.mode(values)
        except _stats.StatisticsError:
            data_mode = None

        data_min = min(values)
        data_max = max(values)
        data_range = data_max - data_min

        data_var_pop = _stats.pvariance(values)
        data_var_sam = _stats.variance(values) if n > 1 else None
        data_std_pop = _stats.pstdev(values)
        data_std_sam = _stats.stdev(values) if n > 1 else None

        q1_idx = n // 4
        q3_idx = 3 * n // 4
        data_q1 = data_sorted[q1_idx]
        data_q3 = data_sorted[min(q3_idx, n - 1)]
        data_iqr = data_q3 - data_q1

        lines = [
            f"Statistics for {n} data points:",
            f"  Sum       = {data_sum:.10g}",
            f"  Mean      = {data_mean:.10g}",
            f"  Median    = {data_median:.10g}",
            f"  Mode      = {data_mode if data_mode is not None else 'N/A (all unique)'}",
            f"  Min       = {data_min:.10g}",
            f"  Max       = {data_max:.10g}",
            f"  Range     = {data_range:.10g}",
            f"  Q1 (25%)  = {data_q1:.10g}",
            f"  Q3 (75%)  = {data_q3:.10g}",
            f"  IQR       = {data_iqr:.10g}",
            f"  Var (pop) = {data_var_pop:.10g}",
            f"  Var (sam) = {data_var_sam:.10g}" if n > 1 else "",
            f"  Std (pop) = {data_std_pop:.10g}",
            f"  Std (sam) = {data_std_sam:.10g}" if data_std_sam is not None else "",
            f"",
            f"Sorted: {[f'{v:.6g}' for v in data_sorted[:20]]}" +
            (f" ... ({n} total)" if n > 20 else ""),
        ]

        msg = "\n".join(line for line in lines if line)
        messagebox.showinfo(t("msg_stats_results"), msg)
        self.status_var.set(t("status_stats", n, f"{data_mean:.6g}", f"{data_std_pop:.6g}"))

    def _on_stats_sort(self):
        values = self._parse_stats_data()
        if values is None:
            return
        sorted_vals = sorted(values)
        self._var_stats_data.set(", ".join(f"{v:g}" for v in sorted_vals))
        self.status_var.set(t("status_data_sorted", len(values)))

    def _on_stats_histogram(self):
        values = self._parse_stats_data()
        if values is None:
            return
        self._ensure_2d_window()
        self.ax_2d.clear()
        self._setup_axes(self.ax_2d, is_3d=False)

        import statistics as _stats
        n_bins = max(5, min(20, int(len(values) ** 0.5) + 1))
        self.ax_2d.hist(values, bins=n_bins, color="#89b4fa", edgecolor="#313244",
                        alpha=0.85, linewidth=1.2)

        data_mean = _stats.mean(values)
        data_median = _stats.median(values)
        self.ax_2d.axvline(data_mean, color="#f38ba8", linestyle="--", linewidth=2,
                           label=f"Mean = {data_mean:.4g}")
        self.ax_2d.axvline(data_median, color="#a6e3a1", linestyle=":", linewidth=2,
                           label=f"Median = {data_median:.4g}")

        self.ax_2d.legend(loc="upper right", facecolor="#313244",
                          edgecolor="#585b70", labelcolor="#cdd6f4", fontsize=9)
        self.ax_2d.set_title("Histogram", color="#cdd6f4", fontsize=12)
        self.ax_2d.set_xlabel("Value", color="#cdd6f4")
        self.ax_2d.set_ylabel("Frequency", color="#cdd6f4")

        self.canvas_2d.draw()
        self.status_var.set(t("status_histogram", len(values), n_bins))

    def _on_stats_export_csv(self):
        values = self._parse_stats_data()
        if values is None:
            return
        import csv as _csv
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export Statistics Data")
        if not path:
            return
        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = _csv.writer(f)
                writer.writerow(["index", "value"])
                for i, v in enumerate(values):
                    writer.writerow([i + 1, v])
            self.status_var.set(t("status_exported_stats", len(values), os.path.basename(path)))
        except Exception as e:
            messagebox.showerror(t("err_export"), t("msg_could_not_export", e))

    # ------------------------------------------------------------------
    #  Statistical Distribution Calculator
    # ------------------------------------------------------------------
    def _get_dist_info(self):
        """Get current distribution key and info dict."""
        try:
            from stat_dist import DISTRIBUTIONS as _REG
        except ImportError:
            return None, None
        display_name = self._var_dist_type.get()
        key = self._dist_names_map.get(display_name)
        if key is None or key not in _REG:
            return None, None
        return key, _REG[key]

    def _get_dist_params(self):
        """Get current parameter values as a dict."""
        try:
            from stat_dist import DISTRIBUTIONS as _REG
        except ImportError:
            return None
        display_name = self._var_dist_type.get()
        key = self._dist_names_map.get(display_name)
        if key is None:
            return None
        pvars = self._dist_param_vars.get(key, {})
        params = {}
        for pname, sv in pvars.items():
            try:
                params[pname] = float(sv.get())
            except ValueError:
                messagebox.showerror(t("err_input"),
                                     t("msg_invalid_param", pname))
                return None
        return params

    def _on_dist_type_change(self, event=None):
        """Show/hide parameter frames based on selected distribution."""
        display_name = self._var_dist_type.get()
        key = self._dist_names_map.get(display_name)
        for dk, frame in self._dist_param_frames.items():
            if dk == key:
                frame.pack(fill=tk.X, padx=6, pady=1)
            else:
                frame.pack_forget()

    def _on_dist_pdf(self):
        """Compute PDF/PMF at a given x value."""
        key, info = self._get_dist_info()
        if key is None:
            return
        params = self._get_dist_params()
        if params is None:
            return
        x_str = self._var_dist_x.get().strip()
        try:
            x_val = float(x_str)
        except ValueError:
            messagebox.showerror(t("err_input"), t("msg_invalid_x_value"))
            return
        try:
            from stat_dist import create_distribution
            dist = create_distribution(key, **params)
            if key in ("binomial", "poisson"):
                result = float(dist.pmf(int(round(x_val))))
                label = info.get(f"pdf_label_{_get_lang()}", "PMF")
            else:
                result = float(dist.pdf(x_val))
                label = info.get(f"pdf_label_{_get_lang()}", "PDF")
            dist_name = info.get(f"name_{_get_lang()}", info["name_en"])
            msg = f"{dist_name} {label}({x_str}) = {result:.10g}"
            messagebox.showinfo(label, msg)
            self.status_var.set(msg)
        except Exception as e:
            messagebox.showerror(t("err_error"), str(e))

    def _on_dist_cdf(self):
        """Compute CDF at a given x value."""
        key, info = self._get_dist_info()
        if key is None:
            return
        params = self._get_dist_params()
        if params is None:
            return
        x_str = self._var_dist_x.get().strip()
        try:
            x_val = float(x_str)
        except ValueError:
            messagebox.showerror(t("err_input"), t("msg_invalid_x_value"))
            return
        try:
            from stat_dist import create_distribution
            dist = create_distribution(key, **params)
            result = float(dist.cdf(x_val))
            dist_name = info.get(f"name_{_get_lang()}", info["name_en"])
            msg = f"{dist_name} CDF({x_str}) = {result:.10g}"
            messagebox.showinfo("CDF", msg)
            self.status_var.set(msg)
        except Exception as e:
            messagebox.showerror(t("err_error"), str(e))

    def _on_dist_ppf(self):
        """Compute PPF (inverse CDF) at a given q value."""
        key, info = self._get_dist_info()
        if key is None:
            return
        params = self._get_dist_params()
        if params is None:
            return
        x_str = self._var_dist_x.get().strip()
        try:
            q_val = float(x_str)
        except ValueError:
            messagebox.showerror(t("err_input"), t("msg_invalid_q_value"))
            return
        if q_val <= 0 or q_val >= 1:
            messagebox.showerror(t("err_input"), t("msg_q_range"))
            return
        try:
            from stat_dist import create_distribution
            dist = create_distribution(key, **params)
            result = float(dist.ppf(q_val))
            dist_name = info.get(f"name_{_get_lang()}", info["name_en"])
            msg = f"{dist_name} PPF({x_str}) = {result:.10g}"
            messagebox.showinfo("PPF", msg)
            self.status_var.set(msg)
        except Exception as e:
            messagebox.showerror(t("err_error"), str(e))

    def _on_dist_plot(self):
        """Plot the PDF/PMF and CDF of the selected distribution."""
        key, info = self._get_dist_info()
        if key is None:
            return
        params = self._get_dist_params()
        if params is None:
            return
        try:
            from stat_dist import create_distribution, get_pdf_x_range
            dist = create_distribution(key, **params)
            dist_name = info.get(f"name_{_get_lang()}", info["name_en"])
            pdf_label = info.get(f"pdf_label_{_get_lang()}", "PDF")
            is_discrete = key in ("binomial", "poisson")

            xs = get_pdf_x_range(key, params, n_points=500)
            pdf_vals = dist.pmf(xs) if is_discrete else dist.pdf(xs)
            cdf_vals = dist.cdf(xs)

            self._ensure_2d_window()
            self.fig_2d.clear()
            self.ax_2d = self.fig_2d.add_subplot(211)
            ax2 = self.fig_2d.add_subplot(212)
            self.fig_2d.subplots_adjust(hspace=0.4)

            # Dark theme colors
            bg_color = "#1e1e2e"
            text_color = "#cdd6f4"
            grid_color = "#45475a"
            self.fig_2d.set_facecolor(bg_color)

            for ax in (self.ax_2d, ax2):
                ax.set_facecolor(bg_color)
                ax.tick_params(colors=text_color, labelsize=9)
                ax.spines['bottom'].set_color(grid_color)
                ax.spines['left'].set_color(grid_color)
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.grid(True, alpha=0.3, color=grid_color)

            if is_discrete:
                self.ax_2d.bar(xs, pdf_vals, color="#89b4fa", alpha=0.85, width=0.6,
                        edgecolor="#313244", linewidth=0.8)
                ax2.step(xs, cdf_vals, where="post", color="#a6e3a1", linewidth=2)
            else:
                self.ax_2d.fill_between(xs, pdf_vals, alpha=0.3, color="#89b4fa")
                self.ax_2d.plot(xs, pdf_vals, color="#89b4fa", linewidth=2)
                ax2.fill_between(xs, cdf_vals, alpha=0.3, color="#a6e3a1")
                ax2.plot(xs, cdf_vals, color="#a6e3a1", linewidth=2)

            self.ax_2d.set_title(f"{dist_name} — {pdf_label}", color=text_color, fontsize=11)
            self.ax_2d.set_ylabel(pdf_label, color=text_color, fontsize=10)
            ax2.set_title(f"{dist_name} — CDF", color=text_color, fontsize=11)
            ax2.set_ylabel("CDF", color=text_color, fontsize=10)
            ax2.set_xlabel("x", color=text_color, fontsize=10)

            self.canvas_2d.draw()
            self.status_var.set(t("status_dist_plot", dist_name))
        except Exception as e:
            messagebox.showerror(t("err_error"), str(e))

    def _on_dist_compare(self):
        """Compare PDF/PMF of multiple parameter sets for the same distribution."""
        key, info = self._get_dist_info()
        if key is None:
            return
        params = self._get_dist_params()
        if params is None:
            return
        try:
            from stat_dist import create_distribution, get_pdf_x_range
            dist_name = info.get(f"name_{_get_lang()}", info["name_en"])
            pdf_label = info.get(f"pdf_label_{_get_lang()}", "PDF")
            is_discrete = key in ("binomial", "poisson")

            # Ask user for comparison parameter values
            param_defs = info["params"]
            prompt_parts = []
            for pname, plabel, psym, pdef in param_defs:
                prompt_parts.append(f"{psym}={pdef}")
            prompt = t("msg_dist_compare_prompt", dist_name, ", ".join(prompt_parts))

            from tkinter import simpledialog
            param_str = simpledialog.askstring(
                t("btn_dist_compare"), prompt,
                initialvalue=",".join(str(p[3]) for p in param_defs))
            if not param_str:
                return

            values_list = [v.strip() for v in param_str.split(",")]
            if len(values_list) != len(param_defs):
                messagebox.showerror(t("err_input"), t("msg_dist_param_count", len(param_defs)))
                return

            param_sets = []
            for i, (pname, plabel, psym, pdef) in enumerate(param_defs):
                try:
                    param_sets.append((pname, float(values_list[i])))
                except ValueError:
                    messagebox.showerror(t("err_input"), t("msg_invalid_param", psym))
                    return

            # Generate plots for each parameter combination
            colors = ["#89b4fa", "#f38ba8", "#a6e3a1", "#f9e2af", "#cba6f7", "#fab387"]
            self._ensure_2d_window()
            self.fig_2d.clear()
            self.ax_2d = self.fig_2d.add_subplot(211)
            ax2 = self.fig_2d.add_subplot(212)
            self.fig_2d.subplots_adjust(hspace=0.4)

            bg_color = "#1e1e2e"
            text_color = "#cdd6f4"
            grid_color = "#45475a"
            self.fig_2d.set_facecolor(bg_color)

            for ax in (self.ax_2d, ax2):
                ax.set_facecolor(bg_color)
                ax.tick_params(colors=text_color, labelsize=9)
                ax.spines['bottom'].set_color(grid_color)
                ax.spines['left'].set_color(grid_color)
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.grid(True, alpha=0.3, color=grid_color)

            # Default comparison: vary first parameter, including user's value
            pname0 = param_defs[0][0]
            pval0 = param_sets[0][1]
            default_values = [pval0, 0.5, 1.0, 2.0, 3.0, 5.0] if key == "normal" else \
                             [pval0, 1.0, 3.0, 5.0, 10.0, 30.0] if key == "t" else \
                             [pval0, 1.0, 3.0, 5.0, 10.0] if key == "chi2" else \
                             [pval0, 1.0, 2.0, 5.0, 10.0] if key == "f" else \
                             [pval0, 0.1, 0.3, 0.5, 0.7, 0.9] if pname0 == "p" else \
                             [pval0, 1, 3, 5, 10, 20]

            for idx, val in enumerate(default_values):
                p = {pname: v for pname, v in param_sets}
                p[pname0] = val
                try:
                    dist = create_distribution(key, **p)
                    xs = get_pdf_x_range(key, p, n_points=500)
                    pdf_vals = dist.pmf(xs) if is_discrete else dist.pdf(xs)
                    cdf_vals = dist.cdf(xs)
                    c = colors[idx % len(colors)]
                    label = f"{pname0}={val:g}"
                    if is_discrete:
                        self.ax_2d.bar(xs, pdf_vals, color=c, alpha=0.6, width=0.4,
                                label=label, edgecolor="none")
                        ax2.step(xs, cdf_vals, where="post", color=c,
                                 linewidth=1.5, label=label)
                    else:
                        self.ax_2d.plot(xs, pdf_vals, color=c, linewidth=2, label=label)
                        ax2.plot(xs, cdf_vals, color=c, linewidth=2, label=label)
                except Exception:
                    continue

            self.ax_2d.set_title(f"{dist_name} — {pdf_label} Comparison", color=text_color, fontsize=11)
            self.ax_2d.set_ylabel(pdf_label, color=text_color, fontsize=10)
            self.ax_2d.legend(facecolor="#313244", edgecolor="#585b70",
                       labelcolor=text_color, fontsize=8)
            ax2.set_title(f"{dist_name} — CDF Comparison", color=text_color, fontsize=11)
            ax2.set_ylabel("CDF", color=text_color, fontsize=10)
            ax2.set_xlabel("x", color=text_color, fontsize=10)
            ax2.legend(facecolor="#313244", edgecolor="#585b70",
                       labelcolor=text_color, fontsize=8)

            self.canvas_2d.draw()
            self.status_var.set(t("status_dist_compare", dist_name))
        except Exception as e:
            messagebox.showerror(t("err_error"), str(e))

    # ------------------------------------------------------------------
    #  Curve Fitting / Regression
    # ------------------------------------------------------------------
    def _get_reg_data(self):
        """Get X and Y data for regression. Falls back to statistics data for Y if X is empty."""
        x_text = self._var_reg_xdata.get().strip()
        y_text = self._var_reg_ydata.get().strip()
        if y_text:
            ys = self._parse_data_list(y_text)
        else:
            ys = self._parse_stats_data()
        if ys is None or len(ys) < 2:
            messagebox.showerror(t("err_error"), t("msg_need_2_ydata"))
            return None, None
        if x_text:
            xs = self._parse_data_list(x_text)
            if xs is None or len(xs) != len(ys):
                messagebox.showerror(t("err_error"),
                    t("msg_xdata_length", len(xs) if xs else 0, len(ys)))
                return None, None
        else:
            xs = list(range(1, len(ys) + 1))
        return xs, ys

    def _parse_data_list(self, text: str):
        """Parse comma/space/semicolon separated numbers."""
        import re as _re
        text = text.strip()
        if not text:
            return None
        parts = _re.split(r'[,;\s]+', text)
        vals = []
        for p in parts:
            p = p.strip()
            if not p:
                continue
            try:
                vals.append(float(p))
            except ValueError:
                return None
        return vals if vals else None

    def _show_reg_result(self, title, result):
        """Show regression result and optionally store for plotting."""
        if result is None:
            messagebox.showerror(t("err_error"), t("msg_regression_failed"))
            return
        self._last_reg_result = result
        lines = [
            f"{title}",
            t("reg_equation", result['equation']),
            f"R² = {result['r_squared']:.8f}",
        ]
        msg = "\n".join(lines)
        messagebox.showinfo(title, msg)
        self.status_var.set(t("status_fit", result['equation'], f"{result['r_squared']:.6f}"))

    def _on_reg_linear(self):
        xs, ys = self._get_reg_data()
        if xs is None:
            return
        result = CalcEngine.linear_regression(xs, ys)
        self._show_reg_result(t("reg_linear"), result)

    def _on_reg_quadratic(self):
        xs, ys = self._get_reg_data()
        if xs is None:
            return
        result = CalcEngine.polynomial_regression(xs, ys, degree=2)
        self._show_reg_result(t("reg_quadratic"), result)

    def _on_reg_polynomial(self):
        xs, ys = self._get_reg_data()
        if xs is None:
            return
        try:
            degree = int(self._var_reg_degree.get())
            if degree < 1 or degree > 10:
                messagebox.showerror(t("err_error"), t("msg_degree_range"))
                return
        except ValueError:
            messagebox.showerror(t("err_error"), t("msg_invalid_degree"))
            return
        result = CalcEngine.polynomial_regression(xs, ys, degree=degree)
        self._show_reg_result(t("reg_polynomial", degree), result)

    def _on_reg_exponential(self):
        xs, ys = self._get_reg_data()
        if xs is None:
            return
        result = CalcEngine.exponential_regression(xs, ys)
        self._show_reg_result(t("reg_exponential"), result)

    def _on_reg_power(self):
        xs, ys = self._get_reg_data()
        if xs is None:
            return
        result = CalcEngine.power_regression(xs, ys)
        self._show_reg_result(t("reg_power"), result)

    def _on_reg_logarithmic(self):
        xs, ys = self._get_reg_data()
        if xs is None:
            return
        result = CalcEngine.logarithmic_regression(xs, ys)
        self._show_reg_result(t("reg_logarithmic"), result)

    def _on_reg_plot(self):
        """Plot data points and fitted curve."""
        if not hasattr(self, '_last_reg_result') or self._last_reg_result is None:
            messagebox.showinfo(t("err_info"), t("msg_run_regression"))
            return
        result = self._last_reg_result
        xs_fit = result.get('xs_fit', [])
        ys_fit = result.get('ys_fit', [])
        if not xs_fit or not ys_fit:
            return
        self._ensure_2d_window()
        self.ax_2d.clear()
        self._setup_axes(self.ax_2d, is_3d=False)

        # Plot original data points
        x_text = self._var_reg_xdata.get().strip()
        y_text = self._var_reg_ydata.get().strip()
        if y_text:
            ys = self._parse_data_list(y_text)
        else:
            ys = self._parse_stats_data()
        if x_text:
            xs = self._parse_data_list(x_text)
        else:
            xs = list(range(1, len(ys) + 1)) if ys else []

        if xs and ys:
            self.ax_2d.scatter(xs, ys, color="#f38ba8", s=30, zorder=5,
                             label="Data", edgecolors="#313244", linewidths=0.5)

        # Plot fitted curve
        self.ax_2d.plot(xs_fit, ys_fit, color="#89b4fa", linewidth=2,
                       label=f"Fit: {result['equation']}\nR²={result['r_squared']:.6f}")

        self.ax_2d.legend(loc="best", facecolor="#313244",
                          edgecolor="#585b70", labelcolor="#cdd6f4", fontsize=9)
        self.ax_2d.set_title("Curve Fitting", color="#cdd6f4", fontsize=12)
        self.ax_2d.set_xlabel("X", color="#cdd6f4")
        self.ax_2d.set_ylabel("Y", color="#cdd6f4")

        self.canvas_2d.draw()
        self.status_var.set(t("status_fit_plotted", result['equation']))

    # ------------------------------------------------------------------
    #  Matrix Operations
    # ------------------------------------------------------------------
    def _parse_matrix(self, text: str):
        """Parse matrix from text format: rows separated by ';', cols by ','."""
        text = text.strip()
        if not text:
            return None
        rows = text.split(';')
        matrix = []
        for row in rows:
            row = row.strip()
            if not row:
                continue
            cols = row.split(',')
            vals = []
            for c in cols:
                c = c.strip()
                if not c:
                    continue
                try:
                    vals.append(float(c))
                except ValueError:
                    messagebox.showerror(t("err_matrix"), t("msg_invalid_num", c))
                    return None
            if vals:
                matrix.append(vals)
        if not matrix:
            return None
        ncols = len(matrix[0])
        for row in matrix:
            if len(row) != ncols:
                messagebox.showerror(t("err_matrix"), t("msg_matrix_cols"))
                return None
        return matrix

    def _format_matrix(self, mat) -> str:
        """Format a numpy matrix or list of lists as a readable string."""
        if hasattr(mat, 'tolist'):
            mat = mat.tolist()
        lines = []
        for row in mat:
            lines.append("  " + "  ".join(f"{v:12.6g}" for v in row))
        return "\n".join(lines)

    def _show_matrix_result(self, title: str, result_str: str):
        """Show matrix result in a dialog."""
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("450x350")
        win.configure(bg="#1e1e2e")
        win.minsize(300, 200)
        ttk.Label(win, text=title, style="Dark.TLabel").pack(anchor=tk.W, padx=10, pady=(10, 4))
        text = tk.Text(win, height=15, bg="#313244", fg="#cdd6f4",
                       font=("Consolas", 11), wrap=tk.WORD)
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=4)
        text.insert("1.0", result_str)
        text.configure(state=tk.DISABLED)
        ttk.Button(win, text=t("btn_close"), command=win.destroy).pack(pady=(0, 10))

    def _on_matrix_add(self):
        a = self._parse_matrix(self._var_matrix_a.get())
        b = self._parse_matrix(self._var_matrix_b.get())
        if a is None or b is None:
            return
        try:
            result = np.array(a) + np.array(b)
            self._show_matrix_result("A + B", self._format_matrix(result))
            self.status_var.set(t("status_matrix_add"))
        except Exception as e:
            messagebox.showerror(t("err_matrix"), t("msg_add_failed", e))

    def _on_matrix_sub(self):
        a = self._parse_matrix(self._var_matrix_a.get())
        b = self._parse_matrix(self._var_matrix_b.get())
        if a is None or b is None:
            return
        try:
            result = np.array(a) - np.array(b)
            self._show_matrix_result("A - B", self._format_matrix(result))
            self.status_var.set(t("status_matrix_sub"))
        except Exception as e:
            messagebox.showerror(t("err_matrix"), t("msg_sub_failed", e))

    def _on_matrix_mul(self):
        a = self._parse_matrix(self._var_matrix_a.get())
        b = self._parse_matrix(self._var_matrix_b.get())
        if a is None or b is None:
            return
        try:
            result = np.array(a) @ np.array(b)
            self._show_matrix_result("A * B", self._format_matrix(result))
            self.status_var.set(t("status_matrix_mul"))
        except Exception as e:
            messagebox.showerror(t("err_matrix"), t("msg_mul_failed", e))

    def _on_matrix_det(self):
        a = self._parse_matrix(self._var_matrix_a.get())
        if a is None:
            return
        try:
            arr = np.array(a)
            if arr.shape[0] != arr.shape[1]:
                messagebox.showerror(t("err_matrix"), t("msg_det_square"))
                return
            det = np.linalg.det(arr)
            self._show_matrix_result("det(A)", f"det(A) = {det:.10g}")
            self.status_var.set(t("status_det", f"{det:.10g}"))
        except Exception as e:
            messagebox.showerror(t("err_matrix"), t("msg_det_failed", e))

    def _on_matrix_inv(self):
        a = self._parse_matrix(self._var_matrix_a.get())
        if a is None:
            return
        try:
            arr = np.array(a)
            if arr.shape[0] != arr.shape[1]:
                messagebox.showerror(t("err_matrix"), t("msg_inv_square"))
                return
            result = np.linalg.inv(arr)
            self._show_matrix_result("inv(A)", self._format_matrix(result))
            self.status_var.set(t("status_matrix_inv"))
        except np.linalg.LinAlgError:
            messagebox.showerror(t("err_matrix"), t("msg_singular"))
        except Exception as e:
            messagebox.showerror(t("err_matrix"), t("msg_inv_failed", e))

    def _on_matrix_transpose(self):
        a = self._parse_matrix(self._var_matrix_a.get())
        if a is None:
            return
        try:
            result = np.array(a).T
            self._show_matrix_result("A^T (Transpose)", self._format_matrix(result))
            self.status_var.set(t("status_matrix_trans"))
        except Exception as e:
            messagebox.showerror(t("err_matrix"), t("msg_transpose_failed", e))

    def _on_matrix_rank(self):
        a = self._parse_matrix(self._var_matrix_a.get())
        if a is None:
            return
        try:
            arr = np.array(a)
            rank = np.linalg.matrix_rank(arr)
            self._show_matrix_result("rank(A)", f"rank(A) = {rank}")
            self.status_var.set(t("status_rank", rank))
        except Exception as e:
            messagebox.showerror(t("err_matrix"), t("msg_rank_failed", e))

    def _on_matrix_rref(self):
        a = self._parse_matrix(self._var_matrix_a.get())
        if a is None:
            return
        try:
            arr = np.array(a, dtype=float)
            m, n = arr.shape
            pivot_row = 0
            pivot_cols = []
            for col in range(n):
                if pivot_row >= m:
                    break
                max_row = pivot_row
                for row in range(pivot_row + 1, m):
                    if abs(arr[row, col]) > abs(arr[max_row, col]):
                        max_row = row
                if abs(arr[max_row, col]) < 1e-10:
                    continue
                arr[[pivot_row, max_row]] = arr[[max_row, pivot_row]]
                arr[pivot_row] = arr[pivot_row] / arr[pivot_row, col]
                for row in range(m):
                    if row != pivot_row and abs(arr[row, col]) > 1e-10:
                        arr[row] = arr[row] - arr[row, col] * arr[pivot_row]
                pivot_cols.append(col)
                pivot_row += 1
            result_str = self._format_matrix(arr.tolist())
            info = f"Rank = {len(pivot_cols)}\n\n{result_str}"
            self._show_matrix_result("RREF(A)", info)
            self.status_var.set(t("status_rref", len(pivot_cols)))
        except Exception as e:
            messagebox.showerror(t("err_matrix"), t("msg_rref_failed", e))

    def _on_matrix_eigen(self):
        a = self._parse_matrix(self._var_matrix_a.get())
        if a is None:
            return
        try:
            arr = np.array(a)
            if arr.shape[0] != arr.shape[1]:
                messagebox.showerror(t("err_matrix"), t("msg_eigen_square"))
                return
            eigenvalues, eigenvectors = np.linalg.eig(arr)
            lines = ["Eigenvalues:"]
            for i, val in enumerate(eigenvalues):
                lines.append(f"  λ{i+1} = {val:.10g}")
            lines.append("")
            lines.append("Eigenvectors (columns):")
            lines.append(self._format_matrix(eigenvectors))
            self._show_matrix_result("Eigenvalues & Eigenvectors", "\n".join(lines))
            self.status_var.set(t("status_eigenvalues", str([f'{v:.6g}' for v in eigenvalues])))
        except np.linalg.LinAlgError:
            messagebox.showerror(t("err_matrix"), t("msg_eigen_failed"))
        except Exception as e:
            messagebox.showerror(t("err_matrix"), t("msg_eigen_error", e))

    def _on_matrix_clear(self):
        self._var_matrix_a.set("")
        self._var_matrix_b.set("")
        self.status_var.set(t("status_matrix_cleared"))

    # ------------------------------------------------------------------
    #  Complex Number Operations
    # ------------------------------------------------------------------
    def _parse_complex(self, s: str):
        """Parse a complex number from string (a+bi format).

        Supports: "3+4i", "3-4i", "2i", "-2i", "1+i", "1-i",
                   "i", "-i", "3", "-2.5", etc.
        """
        s = s.strip().replace(' ', '')
        if not s:
            return None
        # Strip trailing 'i' or 'I'
        if s.endswith('i') or s.endswith('I'):
            s = s[:-1]
            if not s or s == '+':
                return complex(0, 1)
            elif s == '-':
                return complex(0, -1)
            # Find the last +/- that separates real and imaginary parts
            # We scan from right to left, skipping the first char (which may be a sign)
            split_pos = -1
            for i in range(len(s) - 1, 0, -1):
                if s[i] == '+' or s[i] == '-':
                    split_pos = i
                    break
            if split_pos > 0:
                real_part = s[:split_pos]
                imag_part = s[split_pos:]
                if imag_part in ('+', '-'):
                    imag_part += '1'
                try:
                    return complex(float(real_part), float(imag_part))
                except ValueError:
                    pass
            # Pure imaginary (e.g. "2", "-3", "0.5")
            try:
                return complex(0, float(s))
            except ValueError:
                pass
            # Fallback: try Python's complex() with 'j' suffix
            try:
                return complex(s + 'j')
            except ValueError:
                messagebox.showerror(t("err_complex"), t("msg_invalid_complex", s, '' if s else 'i'))
                return None
        else:
            # No 'i' suffix — pure real number
            try:
                return complex(float(s), 0)
            except ValueError:
                try:
                    return complex(s)
                except ValueError:
                    messagebox.showerror(t("err_complex"), t("msg_invalid_complex2", s))
                    return None

    def _format_complex(self, z: complex) -> str:
        """Format complex number for display."""
        if z.imag == 0:
            return f"{z.real:.10g}"
        elif z.real == 0:
            if z.imag == 1:
                return "i"
            elif z.imag == -1:
                return "-i"
            else:
                return f"{z.imag:.10g}i"
        else:
            if z.imag > 0:
                if z.imag == 1:
                    return f"{z.real:.10g} + i"
                else:
                    return f"{z.real:.10g} + {z.imag:.10g}i"
            else:
                if z.imag == -1:
                    return f"{z.real:.10g} - i"
                else:
                    return f"{z.real:.10g} - {abs(z.imag):.10g}i"

    def _show_complex_result(self, result: str):
        """Display complex result in the result field."""
        self._var_complex_result.set(result)
        self.status_var.set(t("status_complex_result", result))

    def _on_complex_add(self):
        z1 = self._parse_complex(self._var_complex_z1.get())
        z2 = self._parse_complex(self._var_complex_z2.get())
        if z1 is not None and z2 is not None:
            result = CalcEngine.complex_add(z1, z2)
            self._show_complex_result(self._format_complex(result))

    def _on_complex_sub(self):
        z1 = self._parse_complex(self._var_complex_z1.get())
        z2 = self._parse_complex(self._var_complex_z2.get())
        if z1 is not None and z2 is not None:
            result = CalcEngine.complex_sub(z1, z2)
            self._show_complex_result(self._format_complex(result))

    def _on_complex_mul(self):
        z1 = self._parse_complex(self._var_complex_z1.get())
        z2 = self._parse_complex(self._var_complex_z2.get())
        if z1 is not None and z2 is not None:
            result = CalcEngine.complex_mul(z1, z2)
            self._show_complex_result(self._format_complex(result))

    def _on_complex_div(self):
        z1 = self._parse_complex(self._var_complex_z1.get())
        z2 = self._parse_complex(self._var_complex_z2.get())
        if z1 is not None and z2 is not None:
            if abs(z2) == 0:
                messagebox.showerror(t("err_complex"), t("msg_cplx_div_zero"))
                return
            result = CalcEngine.complex_div(z1, z2)
            self._show_complex_result(self._format_complex(result))

    def _on_complex_pow(self):
        z1 = self._parse_complex(self._var_complex_z1.get())
        z2 = self._parse_complex(self._var_complex_z2.get())
        if z1 is not None and z2 is not None:
            result = CalcEngine.complex_pow(z1, z2)
            self._show_complex_result(self._format_complex(result))

    def _on_complex_sin(self):
        z = self._parse_complex(self._var_complex_z.get())
        if z is not None:
            result = CalcEngine.complex_sin(z)
            self._show_complex_result(self._format_complex(result))

    def _on_complex_cos(self):
        z = self._parse_complex(self._var_complex_z.get())
        if z is not None:
            result = CalcEngine.complex_cos(z)
            self._show_complex_result(self._format_complex(result))

    def _on_complex_tan(self):
        z = self._parse_complex(self._var_complex_z.get())
        if z is not None:
            result = CalcEngine.complex_tan(z)
            self._show_complex_result(self._format_complex(result))

    def _on_complex_exp(self):
        z = self._parse_complex(self._var_complex_z.get())
        if z is not None:
            result = CalcEngine.complex_exp(z)
            self._show_complex_result(self._format_complex(result))

    def _on_complex_ln(self):
        z = self._parse_complex(self._var_complex_z.get())
        if z is not None:
            if abs(z) == 0:
                messagebox.showerror(t("err_complex"), t("msg_ln_zero"))
                return
            result = CalcEngine.complex_ln(z)
            self._show_complex_result(self._format_complex(result))

    def _on_complex_sqrt(self):
        z = self._parse_complex(self._var_complex_z.get())
        if z is not None:
            result = CalcEngine.complex_sqrt(z)
            self._show_complex_result(self._format_complex(result))

    def _on_complex_abs(self):
        z = self._parse_complex(self._var_complex_z.get())
        if z is not None:
            result = CalcEngine.complex_abs(z)
            if result is not None:
                self._show_complex_result(f"|z| = {result:.10g}")
            else:
                self._show_complex_result("Error")

    def _on_complex_conj(self):
        z = self._parse_complex(self._var_complex_z.get())
        if z is not None:
            result = CalcEngine.complex_conj(z)
            self._show_complex_result(f"conj(z) = {self._format_complex(result)}")

    def _on_complex_real(self):
        z = self._parse_complex(self._var_complex_z.get())
        if z is not None:
            self._show_complex_result(f"Re(z) = {z.real:.10g}")

    def _on_complex_imag(self):
        z = self._parse_complex(self._var_complex_z.get())
        if z is not None:
            self._show_complex_result(f"Im(z) = {z.imag:.10g}")

    # ------------------------------------------------------------------
    #  Number Theory Calculator
    # ------------------------------------------------------------------
    @staticmethod
    def _nt_is_prime(n):
        if n < 2:
            return False
        if n < 4:
            return True
        if n % 2 == 0 or n % 3 == 0:
            return False
        i = 5
        while i * i <= n:
            if n % i == 0 or n % (i + 2) == 0:
                return False
            i += 6
        return True

    @staticmethod
    def _nt_factorize(n):
        factors = []
        d = 2
        while d * d <= n:
            while n % d == 0:
                factors.append(d)
                n //= d
            d += 1
        if n > 1:
            factors.append(n)
        return factors

    @staticmethod
    def _nt_format_factors(factors):
        if not factors:
            return "1"
        parts = []
        i = 0
        while i < len(factors):
            p = factors[i]
            count = 1
            while i + count < len(factors) and factors[i + count] == p:
                count += 1
            if count == 1:
                parts.append(str(p))
            else:
                parts.append(f"{p}^{count}")
            i += count
        return " × ".join(parts)

    @staticmethod
    def _nt_gcd(a, b):
        a, b = abs(a), abs(b)
        while b:
            a, b = b, a % b
        return a

    @staticmethod
    def _nt_lcm(a, b):
        if a == 0 or b == 0:
            return 0
        return abs(a * b) // SuperCalcApp._nt_gcd(a, b)

    @staticmethod
    def _nt_fibonacci(n):
        if n <= 0:
            return 0
        if n == 1:
            return 0
        if n == 2:
            return 1
        a, b = 0, 1
        for _ in range(2, n):
            a, b = b, a + b
        return b

    @staticmethod
    def _nt_mod_pow(base, exp, mod):
        if mod <= 0:
            raise ValueError("mod must be positive")
        result = 1
        base = base % mod
        while exp > 0:
            if exp % 2 == 1:
                result = (result * base) % mod
            exp >>= 1
            base = (base * base) % mod
        return result

    @staticmethod
    def _nt_totient(n):
        if n <= 0:
            return 0
        result = n
        p = 2
        temp = n
        while p * p <= temp:
            if temp % p == 0:
                while temp % p == 0:
                    temp //= p
                result -= result // p
            p += 1
        if temp > 1:
            result -= result // temp
        return result

    def _nt_show_result(self, result_str):
        self._var_nt_result.set(result_str)

    def _on_nt_factorize(self):
        try:
            n = int(self._var_nt_n.get().strip())
        except ValueError:
            messagebox.showerror(t("err_nt_input"), t("msg_nt_invalid_n"))
            return
        if n <= 0:
            messagebox.showerror(t("err_nt_input"), t("msg_nt_invalid_n"))
            return
        if n > 10**12:
            messagebox.showerror(t("err_nt_input"), t("msg_nt_n_too_large"))
            return
        factors = self._nt_factorize(n)
        formatted = self._nt_format_factors(factors)
        self._nt_show_result(formatted)
        self.status_var.set(t("status_nt_factorize", n, formatted))

    def _on_nt_is_prime(self):
        try:
            n = int(self._var_nt_n.get().strip())
        except ValueError:
            messagebox.showerror(t("err_nt_input"), t("msg_nt_invalid_n"))
            return
        if n <= 0:
            messagebox.showerror(t("err_nt_input"), t("msg_nt_invalid_n"))
            return
        if self._nt_is_prime(n):
            self._nt_show_result(f"{n} is prime")
            self.status_var.set(t("status_nt_prime", n))
        else:
            factors = self._nt_factorize(n)
            formatted = self._nt_format_factors(factors)
            self._nt_show_result(f"{n} = {formatted}")
            self.status_var.set(t("status_nt_composite", n, formatted))

    def _on_nt_gcd(self):
        try:
            a = int(self._var_nt_a.get().strip())
            b = int(self._var_nt_b.get().strip())
        except ValueError:
            messagebox.showerror(t("err_nt_input"), t("msg_nt_invalid_ab"))
            return
        result = self._nt_gcd(a, b)
        self._nt_show_result(str(result))
        self.status_var.set(t("status_nt_gcd", a, b, result))

    def _on_nt_lcm(self):
        try:
            a = int(self._var_nt_a.get().strip())
            b = int(self._var_nt_b.get().strip())
        except ValueError:
            messagebox.showerror(t("err_nt_input"), t("msg_nt_invalid_ab"))
            return
        result = self._nt_lcm(a, b)
        self._nt_show_result(str(result))
        self.status_var.set(t("status_nt_lcm", a, b, result))

    def _on_nt_fibonacci(self):
        try:
            count = int(self._var_nt_fib_count.get().strip())
        except ValueError:
            messagebox.showerror(t("err_nt_input"), t("msg_nt_invalid_n"))
            return
        if count <= 0 or count > 1000:
            messagebox.showerror(t("err_nt_input"), t("msg_nt_invalid_n"))
            return
        seq = [self._nt_fibonacci(i) for i in range(1, count + 1)]
        if count <= 20:
            result_str = ", ".join(str(x) for x in seq)
        else:
            result_str = ", ".join(str(x) for x in seq[:15]) + f", ... ({count} terms)"
        self._nt_show_result(result_str)
        self.status_var.set(t("status_nt_fibonacci", count, seq[-1]))

    def _on_nt_mod_pow(self):
        try:
            base = int(self._var_nt_modpow_base.get().strip())
            exp = int(self._var_nt_modpow_exp.get().strip())
            mod = int(self._var_nt_modpow_mod.get().strip())
        except ValueError:
            messagebox.showerror(t("err_nt_input"), t("msg_nt_invalid_modpow"))
            return
        if mod <= 0:
            messagebox.showerror(t("err_nt_input"), t("msg_nt_invalid_modpow"))
            return
        result = self._nt_mod_pow(base, exp, mod)
        self._nt_show_result(str(result))
        self.status_var.set(t("status_nt_mod_pow", base, exp, mod, result))

    def _on_nt_totient(self):
        try:
            n = int(self._var_nt_n.get().strip())
        except ValueError:
            messagebox.showerror(t("err_nt_input"), t("msg_nt_invalid_n"))
            return
        if n <= 0:
            messagebox.showerror(t("err_nt_input"), t("msg_nt_invalid_n"))
            return
        result = self._nt_totient(n)
        self._nt_show_result(str(result))
        self.status_var.set(t("status_nt_totient", n, result))

    def _on_nt_clear(self):
        self._var_nt_result.set("")

    # ------------------------------------------------------------------
    #  Bitwise Operations Calculator
    # ------------------------------------------------------------------
    def _bw_mask(self, val, width):
        mask_val = (1 << width) - 1
        return val & mask_val

    def _bw_to_signed(self, val, width):
        bit = width - 1
        if val & (1 << bit):
            return val - (1 << width)
        return val

    def _bw_to_bin_padded(self, val, width):
        bits = format(self._bw_mask(val, width), f'0{width}b')
        return bits

    def _on_bw_calc(self):
        try:
            a = int(self._var_bw_a.get().strip())
            width = int(self._var_bw_width.get())
        except ValueError:
            messagebox.showerror(t("err_bw_input"), t("msg_bw_invalid"))
            return

        op = self._var_bw_op.get()
        b = 0
        if op != "NOT":
            try:
                b = int(self._var_bw_b.get().strip())
            except ValueError:
                messagebox.showerror(t("err_bw_input"), t("msg_bw_invalid"))
                return

        a_masked = self._bw_mask(a, width)
        if op != "NOT":
            b_masked = self._bw_mask(b, width)

        if op == "AND":
            result = a_masked & b_masked
        elif op == "OR":
            result = a_masked | b_masked
        elif op == "XOR":
            result = a_masked ^ b_masked
        elif op == "NOT":
            result = (~a_masked) & ((1 << width) - 1)
        elif op == "<<":
            result = (a_masked << b_masked) & ((1 << width) - 1)
        elif op == ">>":
            result = a_masked >> b_masked
        else:
            result = 0

        self._var_bw_res_bin.set(self._bw_to_bin_padded(result, width))
        self._var_bw_res_hex.set(format(self._bw_mask(result, width), 'X'))
        self._var_bw_res_oct.set(format(self._bw_mask(result, width), 'o'))
        self._var_bw_res_dec.set(str(self._bw_to_signed(result, width)))
        self.status_var.set(f"A {op} B = {self._bw_to_signed(result, width)} (dec)")

    def _on_bw_clear(self):
        self._var_bw_a.set("0")
        self._var_bw_b.set("0")
        self._var_bw_res_bin.set("")
        self._var_bw_res_hex.set("")
        self._var_bw_res_oct.set("")
        self._var_bw_res_dec.set("")

    # ------------------------------------------------------------------
    #  Unit Converter Operations
    # ------------------------------------------------------------------
    def _on_unit_category_change(self):
        cat = self._var_unit_cat.get()
        if cat in self._unit_categories:
            units = list(self._unit_categories[cat].keys())
            self._unit_from_combo["values"] = units
            self._unit_to_combo["values"] = units
            if len(units) > 0:
                self._var_unit_from.set(units[0])
            if len(units) > 1:
                self._var_unit_to.set(units[1])
            self._var_unit_result.set("")

    def _on_unit_convert(self):
        cat = self._var_unit_cat.get()
        from_unit = self._var_unit_from.get()
        to_unit = self._var_unit_to.get()
        value_str = self._var_unit_value.get()

        if not cat or not from_unit or not to_unit:
            self.status_var.set(t("status_unit_select"))
            return

        try:
            value = float(value_str)
        except ValueError:
            messagebox.showerror(t("err_unit"), t("msg_invalid_value"))
            return

        units = self._unit_categories[cat]
        from_factor = units[from_unit]
        to_factor = units[to_unit]

        # Handle temperature separately (non-linear conversion)
        if cat == "Temperature":
            result = self._convert_temperature(value, from_factor, to_factor)
        else:
            # Standard linear conversion: value * from_factor / to_factor
            result = value * from_factor / to_factor

        # Format result nicely
        if abs(result) >= 1e10 or (abs(result) < 1e-6 and result != 0):
            result_str = f"{result:.10e}"
        else:
            result_str = f"{result:.10g}"

        self._var_unit_result.set(result_str)
        self.status_var.set(t("status_unit_convert", value, from_unit, result_str, to_unit))

    def _convert_temperature(self, value, from_type, to_type):
        if from_type == to_type:
            return value
        # Convert to Celsius first
        if from_type == "F":
            celsius = (value - 32) * 5.0 / 9.0
        elif from_type == "K":
            celsius = value - 273.15
        else:
            celsius = value
        # Convert from Celsius to target
        if to_type == "F":
            return celsius * 9.0 / 5.0 + 32
        elif to_type == "K":
            return celsius + 273.15
        else:
            return celsius

    # ------------------------------------------------------------------
    #  Perpetual Calendar / Date Calculator
    # ------------------------------------------------------------------
    @staticmethod
    def _cal_parse_date(date_str):
        """Parse YYYY-MM-DD string and return (year, month, day) as ints."""
        parts = date_str.strip().split("-")
        if len(parts) != 3:
            return None
        try:
            y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
            return (y, m, d)
        except ValueError:
            return None

    @staticmethod
    def _cal_day_of_week(year, month, day):
        """Zeller-like calculation: returns 0=Mon .. 6=Sun."""
        import calendar
        return calendar.weekday(year, month, day)

    @staticmethod
    def _cal_days_in_month(year, month):
        import calendar
        return calendar.monthrange(year, month)[1]

    def _on_cal_today(self):
        from datetime import date
        today = date.today()
        self._var_cal_date1.set(f"{today.year:04d}-{today.month:02d}-{today.day:02d}")

    def _on_cal_clear(self):
        self._var_cal_date1.set("")
        self._var_cal_date2.set("")
        self._var_cal_add_days.set("0")
        self._var_cal_result.set("")

    def _on_cal_day_of_week(self):
        d1 = self._cal_parse_date(self._var_cal_date1.get())
        if d1 is None:
            messagebox.showerror(t("err_cal"), t("msg_cal_invalid_date"))
            return
        y, m, day = d1
        if m < 1 or m > 12 or day < 1 or day > 31:
            messagebox.showerror(t("err_cal"), t("msg_cal_date_range"))
            return
        try:
            dow = self._cal_day_of_week(y, m, day)
        except ValueError:
            messagebox.showerror(t("err_cal"), t("msg_cal_invalid_date"))
            return
        days_en = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        days_zh = ["一", "二", "三", "四", "五", "六", "日"]
        lang = _get_lang()
        if lang == "zh":
            dow_str = days_zh[dow]
        else:
            dow_str = days_en[dow]
        self._var_cal_result.set(t("status_cal_day_of_week", y, m, day, dow_str))
        self.status_var.set(t("status_cal_day_of_week", y, m, day, dow_str))

    def _on_cal_diff(self):
        d1 = self._cal_parse_date(self._var_cal_date1.get())
        d2 = self._cal_parse_date(self._var_cal_date2.get())
        if d1 is None or d2 is None:
            messagebox.showerror(t("err_cal"), t("msg_cal_invalid_date"))
            return
        from datetime import date
        try:
            dt1 = date(d1[0], d1[1], d1[2])
            dt2 = date(d2[0], d2[1], d2[2])
        except ValueError:
            messagebox.showerror(t("err_cal"), t("msg_cal_invalid_date"))
            return
        diff = (dt2 - dt1).days
        self._var_cal_result.set(t("status_cal_diff", diff))
        self.status_var.set(t("status_cal_diff", diff))

    def _on_cal_add_days(self):
        d1 = self._cal_parse_date(self._var_cal_date1.get())
        if d1 is None:
            messagebox.showerror(t("err_cal"), t("msg_cal_invalid_date"))
            return
        try:
            add = int(self._var_cal_add_days.get())
        except ValueError:
            messagebox.showerror(t("err_cal"), t("msg_cal_invalid_input"))
            return
        from datetime import date, timedelta
        try:
            dt1 = date(d1[0], d1[1], d1[2])
        except ValueError:
            messagebox.showerror(t("err_cal"), t("msg_cal_invalid_date"))
            return
        dt2 = dt1 + timedelta(days=add)
        self._var_cal_date2.set(f"{dt2.year:04d}-{dt2.month:02d}-{dt2.day:02d}")
        self._var_cal_result.set(t("status_cal_add", dt1.isoformat(), add, dt2.isoformat()))
        self.status_var.set(t("status_cal_add", dt1.isoformat(), add, dt2.isoformat()))

    # ------------------------------------------------------------------
    #  Probability Calculator
    # ------------------------------------------------------------------
    def _on_prob_mode_change(self):
        """Show/hide probability sub-sections based on selected mode."""
        mode_name = self._var_prob_mode.get()
        mode = self._prob_mode_map.get(mode_name, "combo")
        all_frames = [
            self._frame_prob_combo,
            self._frame_prob_event,
            self._frame_prob_cond,
            self._frame_prob_bayes,
            self._frame_prob_binom,
            self._frame_prob_poisson,
            self._frame_prob_geometric,
            self._frame_prob_hypergeo,
        ]
        for f in all_frames:
            for child in f.winfo_children():
                child.pack_forget()

        mode_to_frame = {
            "combo": self._frame_prob_combo,
            "event": self._frame_prob_event,
            "conditional": self._frame_prob_cond,
            "bayes": self._frame_prob_bayes,
            "binomial": self._frame_prob_binom,
            "poisson": self._frame_prob_poisson,
            "geometric": self._frame_prob_geometric,
            "hypergeo": self._frame_prob_hypergeo,
        }
        target = mode_to_frame.get(mode, self._frame_prob_combo)
        for child in target.winfo_children():
            child.pack(fill=tk.X, pady=2)

    def _prob_parse_int(self, val, name="n"):
        try:
            v = int(val.strip())
            if v < 0:
                raise ValueError
            return v
        except ValueError:
            messagebox.showerror(t("err_prob"), t("msg_prob_invalid_n"))
            return None

    def _prob_parse_float(self, val, name="p"):
        try:
            return float(val.strip())
        except ValueError:
            messagebox.showerror(t("err_prob"), t("msg_prob_invalid_p"))
            return None

    def _prob_parse_prob(self, val, name="p"):
        try:
            v = float(val.strip())
            if not (0 <= v <= 1):
                raise ValueError
            return v
        except ValueError:
            messagebox.showerror(t("err_prob"), t("msg_prob_invalid_p"))
            return None

    def _on_prob_combo(self):
        from probability_calc import combinations
        n = self._prob_parse_int(self._var_prob_n.get(), "n")
        r = self._prob_parse_int(self._var_prob_r.get(), "r")
        if n is None or r is None:
            return
        if r > n:
            messagebox.showerror(t("err_prob"), t("msg_prob_invalid_r"))
            return
        result = combinations(n, r)
        self._var_prob_result.set(t("status_prob_combo", n, r, result))
        self.status_var.set(t("status_prob_combo", n, r, result))

    def _on_prob_perm(self):
        from probability_calc import permutations
        n = self._prob_parse_int(self._var_prob_n.get(), "n")
        r = self._prob_parse_int(self._var_prob_r.get(), "r")
        if n is None or r is None:
            return
        if r > n:
            messagebox.showerror(t("err_prob"), t("msg_prob_invalid_r"))
            return
        result = permutations(n, r)
        self._var_prob_result.set(t("status_prob_perm", n, r, result))
        self.status_var.set(t("status_prob_perm", n, r, result))

    def _on_prob_union(self):
        from probability_calc import event_union
        pa = self._prob_parse_prob(self._var_prob_pa.get(), "P(A)")
        pb = self._prob_parse_prob(self._var_prob_pb.get(), "P(B)")
        pab = self._prob_parse_prob(self._var_prob_pa_and_b.get(), "P(A∩B)")
        if pa is None or pb is None or pab is None:
            return
        result = event_union(pa, pb, pab)
        if result is None:
            messagebox.showerror(t("err_prob"), t("msg_prob_invalid_pa_pb"))
            return
        self._var_prob_result.set(t("status_prob_union", result))
        self.status_var.set(t("status_prob_union", result))

    def _on_prob_intersect(self):
        from probability_calc import event_intersection
        pa = self._prob_parse_prob(self._var_prob_pa.get(), "P(A)")
        pb = self._prob_parse_prob(self._var_prob_pb.get(), "P(B)")
        if pa is None or pb is None:
            return
        result = event_intersection(pa, pb, independent=True)
        self._var_prob_result.set(t("status_prob_intersect", result))
        self.status_var.set(t("status_prob_intersect", result))

    def _on_prob_complement_a(self):
        from probability_calc import event_complement
        pa = self._prob_parse_prob(self._var_prob_pa.get(), "P(A)")
        if pa is None:
            return
        result = event_complement(pa)
        self._var_prob_result.set(t("status_prob_complement", result))
        self.status_var.set(t("status_prob_complement", result))

    def _on_prob_conditional(self):
        from probability_calc import conditional_probability
        pab = self._prob_parse_prob(self._var_prob_cond_a_and_b.get(), "P(A∩B)")
        pb = self._prob_parse_prob(self._var_prob_cond_pb.get(), "P(B)")
        if pab is None or pb is None:
            return
        if pb == 0:
            messagebox.showerror(t("err_prob"), t("msg_prob_pb_zero"))
            return
        result = conditional_probability(pab, pb)
        self._var_prob_result.set(t("status_prob_conditional", result))
        self.status_var.set(t("status_prob_conditional", result))

    def _on_prob_bayes(self):
        from probability_calc import bayes_theorem_full
        pba = self._prob_parse_prob(self._var_prob_bayes_pba.get(), "P(B|A)")
        pa = self._prob_parse_prob(self._var_prob_bayes_pa.get(), "P(A)")
        pbna = self._prob_parse_prob(self._var_prob_bayes_pbna.get(), "P(B|A')")
        if pba is None or pa is None or pbna is None:
            return
        result = bayes_theorem_full(pba, pa, pbna)
        if result is None:
            messagebox.showerror(t("err_prob"), t("msg_prob_invalid_bayes"))
            return
        self._var_prob_result.set(
            t("status_prob_bayes", result['p_a_given_b'], pba, pa, result['p_b']))
        self.status_var.set(
            t("status_prob_bayes", result['p_a_given_b'], pba, pa, result['p_b']))

    def _on_prob_binom_pmf(self):
        from probability_calc import binomial_probability
        n = self._prob_parse_int(self._var_prob_binom_n.get(), "n")
        k = self._prob_parse_int(self._var_prob_binom_k.get(), "k")
        p = self._prob_parse_prob(self._var_prob_binom_p.get(), "p")
        if n is None or k is None or p is None:
            return
        if k > n:
            messagebox.showerror(t("err_prob"), t("msg_prob_invalid_r"))
            return
        result = binomial_probability(n, k, p)
        self._var_prob_result.set(t("status_prob_binom_pmf", result, n, k, p))
        self.status_var.set(t("status_prob_binom_pmf", result, n, k, p))

    def _on_prob_binom_cdf(self):
        from probability_calc import binomial_cdf
        n = self._prob_parse_int(self._var_prob_binom_n.get(), "n")
        k = self._prob_parse_int(self._var_prob_binom_k.get(), "k")
        p = self._prob_parse_prob(self._var_prob_binom_p.get(), "p")
        if n is None or k is None or p is None:
            return
        result = binomial_cdf(n, k, p)
        self._var_prob_result.set(t("status_prob_binom_cdf", result, n, k, p))
        self.status_var.set(t("status_prob_binom_cdf", result, n, k, p))

    def _on_prob_poisson(self):
        from probability_calc import poisson_probability
        lam = self._prob_parse_float(self._var_prob_poisson_lam.get(), "lambda")
        k = self._prob_parse_int(self._var_prob_poisson_k.get(), "k")
        if lam is None or k is None:
            return
        if lam < 0:
            messagebox.showerror(t("err_prob"), t("msg_prob_invalid_p"))
            return
        result = poisson_probability(lam, k)
        self._var_prob_result.set(t("status_prob_poisson", result, k, lam))
        self.status_var.set(t("status_prob_poisson", result, k, lam))

    def _on_prob_geometric(self):
        from probability_calc import geometric_probability
        p = self._prob_parse_prob(self._var_prob_geo_p.get(), "p")
        k = self._prob_parse_int(self._var_prob_geo_k.get(), "k")
        if p is None or k is None:
            return
        if k < 1:
            messagebox.showerror(t("err_prob"), t("msg_prob_invalid_r"))
            return
        result = geometric_probability(p, k)
        self._var_prob_result.set(t("status_prob_geometric", result, k, p))
        self.status_var.set(t("status_prob_geometric", result, k, p))

    def _on_prob_hypergeo(self):
        from probability_calc import hypergeometric_probability
        N = self._prob_parse_int(self._var_prob_hyp_N.get(), "N")
        K = self._prob_parse_int(self._var_prob_hyp_K.get(), "K")
        n = self._prob_parse_int(self._var_prob_hyp_n.get(), "n")
        k = self._prob_parse_int(self._var_prob_hyp_k.get(), "k")
        if N is None or K is None or n is None or k is None:
            return
        result = hypergeometric_probability(N, K, n, k)
        self._var_prob_result.set(t("status_prob_hypergeo", result, N, K, k, n))
        self.status_var.set(t("status_prob_hypergeo", result, N, K, k, n))


# ---------------------------------------------------------------------------
#  Entry point
# ---------------------------------------------------------------------------
def main():
    root = tk.Tk()
    app = SuperCalcApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
