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
KNOWN_FUNCTIONS = {'sin', 'cos', 'tan', 'log', 'ln', 'exp', 'sqrt', 'abs'}
KNOWN_CONSTANTS = {'pi', 'e'}
INDEPENDENT_VARS = {'x', 'y'}  # variables used by the engine, not parameters

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
                 "is_polar", "r_param_expr")

    def __init__(self, expr, color, label="", lw=2, ls="-",
                 is_parametric=False, x_param_expr="", y_param_expr="",
                 is_polar=False, r_param_expr=""):
        self.is_parametric = is_parametric
        self.x_param_expr = x_param_expr
        self.y_param_expr = y_param_expr
        self.is_polar = is_polar
        self.r_param_expr = r_param_expr
        if is_parametric:
            self.expression = f"x(t)={x_param_expr}, y(t)={y_param_expr}"
            self.is_3d = False
        elif is_polar:
            self.expression = f"r(theta)={r_param_expr}"
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
            expr if not is_parametric and not is_polar else
            (x_param_expr + " " + y_param_expr if is_parametric else r_param_expr))

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
        self.root.title("Super Function Graphing Calculator")
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
            # Windows / macOS
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
        frm_expr = ttk.LabelFrame(scroll_frame, text="Function Input",
                                  style="Dark.TLabelframe")
        frm_expr.pack(fill=tk.X, padx=8, pady=(8, 4))

        ttk.Label(frm_expr, text="Expression f(x):",
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
        ttk.Button(btn_row, text="+ Add Curve",
                   command=self._on_add_curve).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(btn_row, text="Plot",
                   command=self._on_plot).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_row, text="Clear All",
                   command=self._on_clear_all).pack(side=tk.LEFT, padx=4)

        # --- Parametric Mode ---
        self._var_parametric = tk.BooleanVar(value=False)
        frm_param = ttk.LabelFrame(scroll_frame, text="Parametric Mode x(t), y(t)",
                                   style="Dark.TLabelframe")
        frm_param.pack(fill=tk.X, padx=8, pady=4)

        ptog = ttk.Frame(frm_param, style="Dark.TFrame")
        ptog.pack(fill=tk.X, padx=6, pady=(4, 2))
        ttk.Checkbutton(ptog, text="Enable parametric curve",
                        variable=self._var_parametric,
                        command=self._on_parametric_toggle).pack(side=tk.LEFT)

        self._frame_param_inputs = ttk.Frame(frm_param, style="Dark.TFrame")
        self._frame_param_inputs.pack(fill=tk.X, padx=6, pady=2)

        pr1 = ttk.Frame(self._frame_param_inputs, style="Dark.TFrame")
        pr1.pack(fill=tk.X, pady=2)
        ttk.Label(pr1, text="x(t) =", style="Dark.TLabel", width=6).pack(side=tk.LEFT)
        self._var_x_param = tk.StringVar(value="cos(t)")
        ttk.Entry(pr1, textvariable=self._var_x_param, width=22).pack(side=tk.LEFT, padx=2)

        pr2 = ttk.Frame(self._frame_param_inputs, style="Dark.TFrame")
        pr2.pack(fill=tk.X, pady=2)
        ttk.Label(pr2, text="y(t) =", style="Dark.TLabel", width=6).pack(side=tk.LEFT)
        self._var_y_param = tk.StringVar(value="sin(t)")
        ttk.Entry(pr2, textvariable=self._var_y_param, width=22).pack(side=tk.LEFT, padx=2)

        pr3 = ttk.Frame(self._frame_param_inputs, style="Dark.TFrame")
        pr3.pack(fill=tk.X, pady=2)
        ttk.Label(pr3, text="t range:", style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_t_min = tk.StringVar(value="0")
        ttk.Entry(pr3, textvariable=self._var_t_min, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Label(pr3, text="to", style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_t_max = tk.StringVar(value="2*pi")
        ttk.Entry(pr3, textvariable=self._var_t_max, width=8).pack(side=tk.LEFT, padx=2)

        # Parametric presets
        pr4 = ttk.Frame(self._frame_param_inputs, style="Dark.TFrame")
        pr4.pack(fill=tk.X, pady=(4, 2))
        ttk.Label(pr4, text="Preset:", style="Dark.TLabel").pack(side=tk.LEFT)
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
        frm_polar = ttk.LabelFrame(scroll_frame, text="Polar Mode r(theta)",
                                   style="Dark.TLabelframe")
        frm_polar.pack(fill=tk.X, padx=8, pady=4)

        ptog2 = ttk.Frame(frm_polar, style="Dark.TFrame")
        ptog2.pack(fill=tk.X, padx=6, pady=(4, 2))
        ttk.Checkbutton(ptog2, text="Enable polar curve",
                        variable=self._var_polar,
                        command=self._on_polar_toggle).pack(side=tk.LEFT)

        self._frame_polar_inputs = ttk.Frame(frm_polar, style="Dark.TFrame")
        self._frame_polar_inputs.pack(fill=tk.X, padx=6, pady=2)

        pr1p = ttk.Frame(self._frame_polar_inputs, style="Dark.TFrame")
        pr1p.pack(fill=tk.X, pady=2)
        ttk.Label(pr1p, text="r(theta) =", style="Dark.TLabel", width=8).pack(side=tk.LEFT)
        self._var_r_param = tk.StringVar(value="1")
        ttk.Entry(pr1p, textvariable=self._var_r_param, width=22).pack(side=tk.LEFT, padx=2)

        pr3p = ttk.Frame(self._frame_polar_inputs, style="Dark.TFrame")
        pr3p.pack(fill=tk.X, pady=2)
        ttk.Label(pr3p, text="theta range:", style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_theta_min = tk.StringVar(value="0")
        ttk.Entry(pr3p, textvariable=self._var_theta_min, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Label(pr3p, text="to", style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_theta_max = tk.StringVar(value="2*pi")
        ttk.Entry(pr3p, textvariable=self._var_theta_max, width=8).pack(side=tk.LEFT, padx=2)

        # Polar presets
        pr4p = ttk.Frame(self._frame_polar_inputs, style="Dark.TFrame")
        pr4p.pack(fill=tk.X, pady=(4, 2))
        ttk.Label(pr4p, text="Preset:", style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_polar_preset = tk.StringVar()
        polar_combo = ttk.Combobox(pr4p, textvariable=self._var_polar_preset,
                                   values=list(POLAR_PRESETS.keys()),
                                   state="readonly", font=("Consolas", 10), width=18)
        polar_combo.pack(side=tk.LEFT, padx=4)
        polar_combo.bind("<<ComboboxSelected>>",
                         lambda e: self._on_polar_preset(self._var_polar_preset.get()))

        # Initially hide polar inputs
        self._on_polar_toggle()

        # --- Parameter Inputs ---
        self.frm_params = ttk.LabelFrame(scroll_frame, text="Parameters",
                                         style="Dark.TLabelframe")
        self.frm_params.pack(fill=tk.X, padx=8, pady=4)
        self.param_widgets = {}
        ttk.Label(self.frm_params, text="No parameters detected",
                  style="Dark.TLabel").pack(padx=6, pady=8)

        # --- Presets ---
        frm_preset = ttk.LabelFrame(scroll_frame, text="Preset Functions",
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
        frm_curves = ttk.LabelFrame(scroll_frame, text="Curves (click to select)",
                                    style="Dark.TLabelframe")
        frm_curves.pack(fill=tk.X, padx=8, pady=4)
        self.listbox_curves = tk.Listbox(
            frm_curves, bg="#313244", fg="#cdd6f4",
            selectbackground="#89b4fa", selectforeground="#1e1e2e",
            font=("Consolas", 10), height=6, exportselection=False)
        self.listbox_curves.pack(fill=tk.X, padx=6, pady=4)
        ttk.Button(frm_curves, text="Remove Selected",
                   command=self._on_remove_curve).pack(padx=6, pady=(0, 4))
        ttk.Button(frm_curves, text="Find Intersections...",
                   command=self._show_intersection_dialog).pack(padx=6, pady=(0, 4))

        # --- Range ---
        frm_range = ttk.LabelFrame(scroll_frame, text="Coordinate Range",
                                   style="Dark.TLabelframe")
        frm_range.pack(fill=tk.X, padx=8, pady=4)

        grid = ttk.Frame(frm_range, style="Dark.TFrame")
        grid.pack(fill=tk.X, padx=6, pady=4)
        range_fields = [
            ("X min", "x_min"), ("X max", "x_max"),
            ("Y min", "y_min"), ("Y max", "y_max"),
            ("Z min", "z_min"), ("Z max", "z_max"),
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
        ttk.Label(range_row2, text="Step:",
                  style="Dark.TLabel").pack(side=tk.LEFT, padx=(6, 2))
        self._var_step = tk.StringVar(value=str(self.step_size))
        ttk.Entry(range_row2, textvariable=self._var_step, width=6).pack(
            side=tk.LEFT)
        ttk.Button(range_row2, text="Apply",
                    command=self._on_apply_range).pack(side=tk.RIGHT, padx=6)

        self._var_grid = tk.BooleanVar(value=True)
        ttk.Checkbutton(range_row2, text="Grid",
                         variable=self._var_grid).pack(
            side=tk.LEFT, padx=(12, 0))

        ttk.Label(range_row2, text="3D Grid:", style="Dark.TLabel").pack(side=tk.LEFT, padx=(12, 0))
        self._var_3d_res = tk.StringVar(value=str(DEFAULT_3D_POINTS))
        ttk.Entry(range_row2, textvariable=self._var_3d_res, width=5).pack(side=tk.LEFT)

        # --- Calculus ---
        frm_calc = ttk.LabelFrame(scroll_frame, text="Calculus Operations",
                                  style="Dark.TLabelframe")
        frm_calc.pack(fill=tk.X, padx=8, pady=4)

        row1 = ttk.Frame(frm_calc, style="Dark.TFrame")
        row1.pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(row1, text="At x =", style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_diff_x = tk.StringVar(value="0")
        ttk.Entry(row1, textvariable=self._var_diff_x, width=8).pack(
            side=tk.LEFT, padx=4)
        ttk.Button(row1, text="f'(x) Derivative",
                   command=lambda: self._on_derivative()).pack(side=tk.LEFT, padx=2)
        ttk.Button(row1, text="f''(x) 2nd Deriv",
                   command=lambda: self._on_derivative2()).pack(side=tk.LEFT, padx=2)

        row2 = ttk.Frame(frm_calc, style="Dark.TFrame")
        row2.pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(row2, text="Integrate [", style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_int_a = tk.StringVar(value="0")
        ttk.Entry(row2, textvariable=self._var_int_a, width=6).pack(side=tk.LEFT)
        ttk.Label(row2, text=" , ", style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_int_b = tk.StringVar(value="1")
        ttk.Entry(row2, textvariable=self._var_int_b, width=6).pack(side=tk.LEFT)
        ttk.Label(row2, text=" ]", style="Dark.TLabel").pack(side=tk.LEFT)
        ttk.Button(row2, text="Integrate",
                   command=self._on_integrate).pack(side=tk.LEFT, padx=8)

        row_limit = ttk.Frame(frm_calc, style="Dark.TFrame")
        row_limit.pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(row_limit, text="Limit x→", style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_limit_a = tk.StringVar(value="0")
        ttk.Entry(row_limit, textvariable=self._var_limit_a, width=8).pack(
            side=tk.LEFT, padx=4)
        ttk.Button(row_limit, text="lim f(x)",
                   command=lambda: self._on_limit(two_sided=True)).pack(side=tk.LEFT, padx=2)
        ttk.Button(row_limit, text="Left lim",
                   command=lambda: self._on_limit(two_sided=False, side="left")).pack(side=tk.LEFT, padx=2)
        ttk.Button(row_limit, text="Right lim",
                   command=lambda: self._on_limit(two_sided=False, side="right")).pack(side=tk.LEFT, padx=2)

        # --- Equation Solver ---
        frm_solve = ttk.LabelFrame(scroll_frame, text="Equation Solver f(x)=0",
                                   style="Dark.TLabelframe")
        frm_solve.pack(fill=tk.X, padx=8, pady=4)

        srow1 = ttk.Frame(frm_solve, style="Dark.TFrame")
        srow1.pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(srow1, text="Guess:", style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_guess = tk.StringVar(value="0")
        ttk.Entry(srow1, textvariable=self._var_guess, width=8).pack(
            side=tk.LEFT, padx=2)
        ttk.Label(srow1, text="Range:",
                  style="Dark.TLabel").pack(side=tk.LEFT, padx=(6, 0))
        self._var_solve_a = tk.StringVar(value="-10")
        ttk.Entry(srow1, textvariable=self._var_solve_a, width=6).pack(side=tk.LEFT)
        ttk.Label(srow1, text="to", style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_solve_b = tk.StringVar(value="10")
        ttk.Entry(srow1, textvariable=self._var_solve_b, width=6).pack(side=tk.LEFT)

        srow2 = ttk.Frame(frm_solve, style="Dark.TFrame")
        srow2.pack(fill=tk.X, padx=6, pady=2)
        ttk.Button(srow2, text="Find Root (Newton)",
                   command=lambda: self._on_solve()).pack(side=tk.LEFT, padx=2)
        ttk.Button(srow2, text="Find Root (Bisection)",
                   command=lambda: self._on_solve_bisection()).pack(side=tk.LEFT, padx=2)

        # --- Nonlinear System Solver (2D) ---
        frm_sys = ttk.LabelFrame(scroll_frame, text="Nonlinear System Solver f(x,y)=0, g(x,y)=0",
                                 style="Dark.TLabelframe")
        frm_sys.pack(fill=tk.X, padx=8, pady=4)

        sysrow1 = ttk.Frame(frm_sys, style="Dark.TFrame")
        sysrow1.pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(sysrow1, text="f(x,y) =", style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_sys_f = tk.StringVar(value="x^2+y^2-1")
        ttk.Entry(sysrow1, textvariable=self._var_sys_f, width=20).pack(side=tk.LEFT, padx=4)
        ttk.Label(sysrow1, text="g(x,y) =", style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_sys_g = tk.StringVar(value="x-y")
        ttk.Entry(sysrow1, textvariable=self._var_sys_g, width=20).pack(side=tk.LEFT, padx=4)

        sysrow2 = ttk.Frame(frm_sys, style="Dark.TFrame")
        sysrow2.pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(sysrow2, text="Initial guess:", style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_sys_x0 = tk.StringVar(value="0.7")
        ttk.Entry(sysrow2, textvariable=self._var_sys_x0, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Label(sysrow2, text=",", style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_sys_y0 = tk.StringVar(value="0.7")
        ttk.Entry(sysrow2, textvariable=self._var_sys_y0, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Button(sysrow2, text="Solve System",
                   command=self._on_solve_system_2d).pack(side=tk.LEFT, padx=8)

        sysrow3 = ttk.Frame(frm_sys, style="Dark.TFrame")
        sysrow3.pack(fill=tk.X, padx=6, pady=(0, 4))
        ttk.Label(sysrow3, text="Solves f(x,y)=0, g(x,y)=0 simultaneously (Newton's method for systems)",
                  style="Dark.TLabel").pack(side=tk.LEFT)

        # --- Extremum Finder ---
        frm_extremum = ttk.LabelFrame(scroll_frame, text="Extremum Finder on [a,b]",
                                      style="Dark.TLabelframe")
        frm_extremum.pack(fill=tk.X, padx=8, pady=4)

        erow1 = ttk.Frame(frm_extremum, style="Dark.TFrame")
        erow1.pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(erow1, text="a:", style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_ext_a = tk.StringVar(value="-10")
        ttk.Entry(erow1, textvariable=self._var_ext_a, width=7).pack(side=tk.LEFT, padx=2)
        ttk.Label(erow1, text="b:", style="Dark.TLabel").pack(side=tk.LEFT, padx=(6, 0))
        self._var_ext_b = tk.StringVar(value="10")
        ttk.Entry(erow1, textvariable=self._var_ext_b, width=7).pack(side=tk.LEFT, padx=2)

        erow2 = ttk.Frame(frm_extremum, style="Dark.TFrame")
        erow2.pack(fill=tk.X, padx=6, pady=2)
        ttk.Button(erow2, text="Find Minimum",
                   command=lambda: self._on_find_extremum(minimum=True)).pack(side=tk.LEFT, padx=2)
        ttk.Button(erow2, text="Find Maximum",
                   command=lambda: self._on_find_extremum(minimum=False)).pack(side=tk.LEFT, padx=2)

        # --- Auto Root Scanner ---
        frm_scan = ttk.LabelFrame(scroll_frame, text="Auto Root Scanner",
                                  style="Dark.TLabelframe")
        frm_scan.pack(fill=tk.X, padx=8, pady=4)

        srow = ttk.Frame(frm_scan, style="Dark.TFrame")
        srow.pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(srow, text="Scan interval [a,b] for all roots f(x)=0",
                  style="Dark.TLabel").pack(side=tk.LEFT, padx=2)
        ttk.Button(srow, text="Scan Roots",
                   command=self._on_scan_roots).pack(side=tk.RIGHT, padx=2)

        # --- Coordinate Marking ---
        frm_mark = ttk.LabelFrame(scroll_frame, text="Coordinate Marking",
                                  style="Dark.TLabelframe")
        frm_mark.pack(fill=tk.X, padx=8, pady=4)

        ttk.Label(frm_mark, text="Left-click to mark, right-click to delete, or enter x:",
                  style="Dark.TLabel").pack(anchor=tk.W, padx=6, pady=(6, 0))

        mark_row = ttk.Frame(frm_mark, style="Dark.TFrame")
        mark_row.pack(fill=tk.X, padx=6, pady=2)
        self._var_mark_x = tk.StringVar(value="")
        ttk.Entry(mark_row, textvariable=self._var_mark_x, width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(mark_row, text="Mark Point",
                   command=self._on_mark_point).pack(side=tk.LEFT, padx=2)
        ttk.Button(mark_row, text="Clear Marks",
                   command=self._clear_marks).pack(side=tk.LEFT, padx=2)

        # --- Tangent & Normal Lines ---
        frm_tan = ttk.LabelFrame(scroll_frame, text="Tangent & Normal Lines",
                                 style="Dark.TLabelframe")
        frm_tan.pack(fill=tk.X, padx=8, pady=4)

        trow_tan = ttk.Frame(frm_tan, style="Dark.TFrame")
        trow_tan.pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(trow_tan, text="At x =", style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_tan_x = tk.StringVar(value="0")
        ttk.Entry(trow_tan, textvariable=self._var_tan_x, width=8).pack(side=tk.LEFT, padx=4)
        ttk.Button(trow_tan, text="Draw Tangent",
                   command=self._on_draw_tangent).pack(side=tk.LEFT, padx=2)
        ttk.Button(trow_tan, text="Draw Normal",
                   command=self._on_draw_normal).pack(side=tk.LEFT, padx=2)
        ttk.Button(trow_tan, text="Clear Lines",
                   command=self._clear_tangent_normal).pack(side=tk.LEFT, padx=2)

        # --- Arc Length ---
        frm_arc = ttk.LabelFrame(scroll_frame, text="Arc Length",
                                 style="Dark.TLabelframe")
        frm_arc.pack(fill=tk.X, padx=8, pady=4)

        arow = ttk.Frame(frm_arc, style="Dark.TFrame")
        arow.pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(arow, text="Uses integration bounds [a,b] above",
                  style="Dark.TLabel").pack(side=tk.LEFT, padx=2)
        ttk.Button(arow, text="Compute Arc Length",
                   command=self._on_arc_length).pack(side=tk.RIGHT, padx=2)

        # --- Area Between Curves ---
        frm_area = ttk.LabelFrame(scroll_frame, text="Area Between Curves",
                                  style="Dark.TLabelframe")
        frm_area.pack(fill=tk.X, padx=8, pady=4)

        area_row1 = ttk.Frame(frm_area, style="Dark.TFrame")
        area_row1.pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(area_row1, text="f(x) =", style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_area_f = tk.StringVar(value="sin(x)")
        ttk.Entry(area_row1, textvariable=self._var_area_f, width=18).pack(
            side=tk.LEFT, padx=4)
        ttk.Label(area_row1, text="g(x) =", style="Dark.TLabel").pack(
            side=tk.LEFT, padx=(8, 0))
        self._var_area_g = tk.StringVar(value="0")
        ttk.Entry(area_row1, textvariable=self._var_area_g, width=18).pack(
            side=tk.LEFT, padx=4)

        area_row2 = ttk.Frame(frm_area, style="Dark.TFrame")
        area_row2.pack(fill=tk.X, padx=6, pady=(0, 4))
        ttk.Label(area_row2, text="Interval [a,b]:",
                  style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_area_a = tk.StringVar(value="0")
        ttk.Entry(area_row2, textvariable=self._var_area_a, width=7).pack(
            side=tk.LEFT, padx=2)
        ttk.Label(area_row2, text="to", style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_area_b = tk.StringVar(value="pi")
        ttk.Entry(area_row2, textvariable=self._var_area_b, width=7).pack(
            side=tk.LEFT, padx=2)
        ttk.Button(area_row2, text="Compute Area",
                   command=self._on_area_between_curves).pack(side=tk.RIGHT, padx=2)

        # --- Function Table ---
        frm_table = ttk.LabelFrame(scroll_frame, text="Function Table & Export",
                                   style="Dark.TLabelframe")
        frm_table.pack(fill=tk.X, padx=8, pady=4)

        trow = ttk.Frame(frm_table, style="Dark.TFrame")
        trow.pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(trow, text="From:", style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_tbl_from = tk.StringVar(value="-10")
        ttk.Entry(trow, textvariable=self._var_tbl_from, width=7).pack(side=tk.LEFT, padx=2)
        ttk.Label(trow, text="To:", style="Dark.TLabel").pack(side=tk.LEFT, padx=(6, 0))
        self._var_tbl_to = tk.StringVar(value="10")
        ttk.Entry(trow, textvariable=self._var_tbl_to, width=7).pack(side=tk.LEFT, padx=2)
        ttk.Label(trow, text="Points:", style="Dark.TLabel").pack(side=tk.LEFT, padx=(6, 0))
        self._var_tbl_n = tk.StringVar(value="21")
        ttk.Entry(trow, textvariable=self._var_tbl_n, width=5).pack(side=tk.LEFT, padx=2)

        trow2 = ttk.Frame(frm_table, style="Dark.TFrame")
        trow2.pack(fill=tk.X, padx=6, pady=(0, 4))
        ttk.Button(trow2, text="Generate Table",
                   command=self._on_generate_table).pack(side=tk.LEFT, padx=2)
        ttk.Button(trow2, text="Export CSV",
                   command=self._on_export_csv).pack(side=tk.LEFT, padx=2)
        ttk.Button(trow2, text="Copy Table",
                   command=self._on_copy_table).pack(side=tk.LEFT, padx=2)

        self._table_data = []   # list of (x, y) tuples
        self._table_expr = ""   # expression used for last table
        self._fft_data = {}     # last FFT result dict

        # --- Fourier Transform & Spectrum ---
        frm_fft = ttk.LabelFrame(scroll_frame, text="Fourier Transform & Spectrum",
                                 style="Dark.TLabelframe")
        frm_fft.pack(fill=tk.X, padx=8, pady=4)

        fft_row1 = ttk.Frame(frm_fft, style="Dark.TFrame")
        fft_row1.pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(fft_row1, text="Samples:", style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_fft_n = tk.StringVar(value="1024")
        ttk.Entry(fft_row1, textvariable=self._var_fft_n, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Label(fft_row1, text="Uses [a,b] from Integrate bounds",
                  style="Dark.TLabel").pack(side=tk.LEFT, padx=(8, 0))

        fft_row2 = ttk.Frame(frm_fft, style="Dark.TFrame")
        fft_row2.pack(fill=tk.X, padx=6, pady=(0, 4))
        ttk.Button(fft_row2, text="Compute FFT",
                   command=self._on_fft_compute).pack(side=tk.LEFT, padx=2)
        ttk.Button(fft_row2, text="Export Spectrum CSV",
                   command=self._on_export_fft_csv).pack(side=tk.LEFT, padx=2)

        # --- Taylor Series Expansion ---
        frm_taylor = ttk.LabelFrame(scroll_frame, text="Taylor Series Expansion",
                                    style="Dark.TLabelframe")
        frm_taylor.pack(fill=tk.X, padx=8, pady=4)

        trow1 = ttk.Frame(frm_taylor, style="Dark.TFrame")
        trow1.pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(trow1, text="Expand at a =", style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_taylor_a = tk.StringVar(value="0")
        ttk.Entry(trow1, textvariable=self._var_taylor_a, width=8).pack(
            side=tk.LEFT, padx=4)
        ttk.Label(trow1, text="Order:", style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_taylor_order = tk.StringVar(value="5")
        ttk.Entry(trow1, textvariable=self._var_taylor_order, width=5).pack(
            side=tk.LEFT, padx=4)

        trow2 = ttk.Frame(frm_taylor, style="Dark.TFrame")
        trow2.pack(fill=tk.X, padx=6, pady=(0, 4))
        ttk.Button(trow2, text="Expand Taylor",
                   command=self._on_taylor_expand).pack(side=tk.LEFT, padx=2)
        ttk.Button(trow2, text="Plot Taylor + Original",
                   command=self._on_taylor_plot).pack(side=tk.LEFT, padx=2)

        # --- ODE Solver (RK4) ---
        frm_ode = ttk.LabelFrame(scroll_frame, text="ODE Solver (dy/dx = f(x,y))",
                                  style="Dark.TLabelframe")
        frm_ode.pack(fill=tk.X, padx=8, pady=4)

        ode_row1 = ttk.Frame(frm_ode, style="Dark.TFrame")
        ode_row1.pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(ode_row1, text="dy/dx =", style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_ode_expr = tk.StringVar(value="-y")
        ttk.Entry(ode_row1, textvariable=self._var_ode_expr, width=22).pack(
            side=tk.LEFT, padx=4)

        ode_row2 = ttk.Frame(frm_ode, style="Dark.TFrame")
        ode_row2.pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(ode_row2, text="x0:", style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_ode_x0 = tk.StringVar(value="0")
        ttk.Entry(ode_row2, textvariable=self._var_ode_x0, width=6).pack(
            side=tk.LEFT, padx=2)
        ttk.Label(ode_row2, text="y0:", style="Dark.TLabel").pack(side=tk.LEFT, padx=(6, 0))
        self._var_ode_y0 = tk.StringVar(value="1")
        ttk.Entry(ode_row2, textvariable=self._var_ode_y0, width=6).pack(
            side=tk.LEFT, padx=2)
        ttk.Label(ode_row2, text="x_end:", style="Dark.TLabel").pack(side=tk.LEFT, padx=(6, 0))
        self._var_ode_xend = tk.StringVar(value="5")
        ttk.Entry(ode_row2, textvariable=self._var_ode_xend, width=6).pack(
            side=tk.LEFT, padx=2)
        ttk.Label(ode_row2, text="Steps:", style="Dark.TLabel").pack(side=tk.LEFT, padx=(6, 0))
        self._var_ode_steps = tk.StringVar(value="200")
        ttk.Entry(ode_row2, textvariable=self._var_ode_steps, width=6).pack(
            side=tk.LEFT, padx=2)

        ode_row3 = ttk.Frame(frm_ode, style="Dark.TFrame")
        ode_row3.pack(fill=tk.X, padx=6, pady=(0, 4))
        ttk.Button(ode_row3, text="Solve ODE",
                   command=self._on_ode_solve).pack(side=tk.LEFT, padx=2)
        ttk.Button(ode_row3, text="Plot Solution",
                   command=self._on_ode_plot).pack(side=tk.LEFT, padx=2)

        # ODE presets
        ode_row4 = ttk.Frame(frm_ode, style="Dark.TFrame")
        ode_row4.pack(fill=tk.X, padx=6, pady=(0, 4))
        ttk.Label(ode_row4, text="Preset:", style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_ode_preset = tk.StringVar()
        ode_combo = ttk.Combobox(ode_row4, textvariable=self._var_ode_preset,
                                  values=list(ODE_PRESETS.keys()),
                                  state="readonly", font=("Consolas", 10), width=24)
        ode_combo.pack(side=tk.LEFT, padx=4)
        ode_combo.bind("<<ComboboxSelected>>",
                        lambda e: self._on_ode_preset(self._var_ode_preset.get()))

        self._ode_data = None  # last ODE solution dict

        # --- Statistics Calculator ---
        frm_stats = ttk.LabelFrame(scroll_frame, text="Statistics Calculator",
                                    style="Dark.TLabelframe")
        frm_stats.pack(fill=tk.X, padx=8, pady=4)

        stats_row1 = ttk.Frame(frm_stats, style="Dark.TFrame")
        stats_row1.pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(stats_row1, text="Data (comma/space separated):",
                  style="Dark.TLabel").pack(anchor=tk.W, padx=2)

        self._var_stats_data = tk.StringVar(value="1, 2, 3, 4, 5, 6, 7, 8, 9, 10")
        stats_entry = ttk.Entry(stats_row1, textvariable=self._var_stats_data, width=36,
                                font=("Consolas", 10))
        stats_entry.pack(fill=tk.X, padx=2, pady=(0, 4))

        stats_row2 = ttk.Frame(frm_stats, style="Dark.TFrame")
        stats_row2.pack(fill=tk.X, padx=6, pady=(0, 4))
        ttk.Button(stats_row2, text="Compute Stats",
                   command=self._on_stats_compute).pack(side=tk.LEFT, padx=2)
        ttk.Button(stats_row2, text="Sort Data",
                   command=self._on_stats_sort).pack(side=tk.LEFT, padx=2)
        ttk.Button(stats_row2, text="Plot Histogram",
                   command=self._on_stats_histogram).pack(side=tk.LEFT, padx=2)
        ttk.Button(stats_row2, text="Export CSV",
                   command=self._on_stats_export_csv).pack(side=tk.LEFT, padx=2)

        # --- Matrix Operations ---
        frm_matrix = ttk.LabelFrame(scroll_frame, text="Matrix Operations (Linear Algebra)",
                                    style="Dark.TLabelframe")
        frm_matrix.pack(fill=tk.X, padx=8, pady=4)

        mrow1 = ttk.Frame(frm_matrix, style="Dark.TFrame")
        mrow1.pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(mrow1, text="Matrix A (rows separated by ;, cols by ,):",
                  style="Dark.TLabel").pack(anchor=tk.W, padx=2)
        self._var_matrix_a = tk.StringVar(value="1,2;3,4")
        ttk.Entry(mrow1, textvariable=self._var_matrix_a, width=36,
                  font=("Consolas", 10)).pack(fill=tk.X, padx=2, pady=(0, 4))

        mrow2 = ttk.Frame(frm_matrix, style="Dark.TFrame")
        mrow2.pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(mrow2, text="Matrix B (for binary operations):",
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
        frm_complex = ttk.LabelFrame(scroll_frame, text="Complex Number Calculator",
                                     style="Dark.TLabelframe")
        frm_complex.pack(fill=tk.X, padx=8, pady=4)

        crow1 = ttk.Frame(frm_complex, style="Dark.TFrame")
        crow1.pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(crow1, text="z1 (a+bi):", style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_complex_z1 = tk.StringVar(value="1+2i")
        ttk.Entry(crow1, textvariable=self._var_complex_z1, width=15,
                  font=("Consolas", 10)).pack(side=tk.LEFT, padx=2)
        ttk.Label(crow1, text="z2 (c+di):", style="Dark.TLabel").pack(side=tk.LEFT, padx=(8, 0))
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
        ttk.Label(crow3, text="Single z:", style="Dark.TLabel").pack(side=tk.LEFT)
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
        ttk.Label(crow6, text="Result:", style="Dark.TLabel").pack(side=tk.LEFT)
        self._var_complex_result = tk.StringVar(value="")
        ttk.Entry(crow6, textvariable=self._var_complex_result, width=30,
                  font=("Consolas", 10), state="readonly").pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)

        # --- Status ---
        self.status_var = tk.StringVar(value="Ready.")
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
        self.window_2d.title("2D Function Plot")
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
        self.window_3d.title("3D Function Plot")
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
        self.window_fft.title("FFT Spectrum Analysis")
        self.window_fft.geometry("900x750")
        self.window_fft.minsize(600, 500)
        self.window_fft.configure(bg="#1e1e2e")
        self.window_fft.protocol("WM_DELETE_WINDOW", self._on_fft_window_close)

        self.fig_fft = Figure(figsize=(9, 7.5), dpi=100, facecolor="#1e1e2e")
        self.ax_fft_amp = self.fig_fft.add_subplot(211)
        self.ax_fft_phase = self.fig_fft.add_subplot(212)
        self._setup_axes(self.ax_fft_amp, is_3d=False)
        self._setup_axes(self.ax_fft_phase, is_3d=False)
        self.ax_fft_amp.set_title("Amplitude Spectrum", color="#cdd6f4", fontsize=11)
        self.ax_fft_phase.set_title("Phase Spectrum", color="#cdd6f4", fontsize=11)
        self.ax_fft_amp.set_xlabel("Frequency")
        self.ax_fft_amp.set_ylabel("Amplitude")
        self.ax_fft_phase.set_xlabel("Frequency")
        self.ax_fft_phase.set_ylabel("Phase (rad)")

        self.canvas_fft = FigureCanvasTkAgg(self.fig_fft, master=self.window_fft)
        self.canvas_fft.draw()
        self.toolbar_fft = NavigationToolbar2Tk(self.canvas_fft, self.window_fft)
        self.toolbar_fft.update()
        self.canvas_fft.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

    def _on_fft_window_close(self):
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
        panel.title("Quick Input Panel")
        panel.geometry("500x400")
        panel.configure(bg="#1e1e2e")
        panel.transient(self.root)
        panel.grab_set()
        
        main_frame = ttk.Frame(panel, style="Dark.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Only include operators/functions/constants supported by the C core
        buttons_config = [
            ("Basic", [
                ("x²", "x^2"), ("x³", "x^3"), ("xⁿ", "x^n"),
                ("√", "sqrt("), ("|x|", "abs("),
            ]),
            ("Operators", [
                ("÷", "/"), ("×", "*"), ("^", "^"), ("-", "-"), ("+", "+"),
            ]),
            ("Log/Exp", [
                ("ln", "ln("), ("log", "log("), ("eˣ", "exp("), ("e", "e"),
            ]),
            ("Trig", [
                ("sin", "sin("), ("cos", "cos("), ("tan", "tan("),
                ("π", "pi"), ("°", "*pi/180"),
            ]),
            ("Special", [
                ("!", "!"), ("(", "("), (")", ")"), (",", ","),
            ]),
            ("Constants", [
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

        ttk.Button(main_frame, text="Close", command=panel.destroy).pack(pady=10)

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
            ttk.Label(self.frm_params, text="No parameters detected",
                      style="Dark.TLabel").pack(padx=6, pady=8)
            return

        ttk.Label(self.frm_params, text="Set parameter values:",
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
                messagebox.showwarning("Input Error", "Please enter both x(t) and y(t) expressions.")
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
                messagebox.showwarning("Input Error", "Please enter an r(theta) expression.")
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
        else:
            expr = self.entry_expr.get().strip()
            if not expr:
                messagebox.showwarning("Input Error", "Please enter an expression.")
                return
            self._add_curve(expr)
            self._plot_all()

    def _on_remove_curve(self):
        sel = self.listbox_curves.curselection()
        if not sel:
            messagebox.showinfo("Info", "Select a curve to remove.")
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
        self.status_var.set("Cleared all curves.")

    def _on_preset(self, name: str):
        expr = PRESET_FUNCTIONS.get(name, "")
        if expr:
            self.entry_expr.delete(0, tk.END)
            self.entry_expr.insert(0, expr)
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
                messagebox.showwarning("Input Error", "Please enter both x(t) and y(t) expressions.")
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
                messagebox.showwarning("Input Error", "Please enter an r(theta) expression.")
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
                messagebox.showerror("Error", "X min must be less than X max.")
                return
            if y_min >= y_max:
                messagebox.showerror("Error", "Y min must be less than Y max.")
                return
            if z_min >= z_max:
                messagebox.showerror("Error", "Z min must be less than Z max.")
                return
            if step <= 0:
                messagebox.showerror("Error", "Step size must be positive.")
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
            messagebox.showerror("Error", "Invalid range values.")

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
                self.status_var.set("Invalid range or step values; using previous settings.")
                return
        except ValueError:
            self.status_var.set("Invalid numeric values; using previous settings.")
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
            self.status_var.set("No curves to plot.")
            return

        has_2d = any((not c.is_3d and not c.is_polar and c.visible) or 
                     (c.is_parametric and c.visible) or 
                     (c.is_polar and c.visible) for c in self.curves)
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
            self.status_var.set("Invalid plot range or step size")
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
        for t in getattr(self, 'tangent_data', []):
            x0, y0, slope = t["x0"], t["y0"], t["slope"]
            # Tangent line: y = slope*(x - x0) + y0
            x_left = max(self.x_min, x0 - (self.x_max - self.x_min) * 0.3)
            x_right = min(self.x_max, x0 + (self.x_max - self.x_min) * 0.3)
            y_left = slope * (x_left - x0) + y0
            y_right = slope * (x_right - x0) + y0
            self.ax_2d.plot([x_left, x_right], [y_left, y_right], 'c--',
                           linewidth=1.5, alpha=0.8, label=f"Tangent at x={x0:.3g}")
            self.ax_2d.plot(x0, y0, 'co', markersize=6)

        # Draw normal lines
        for n in getattr(self, 'normal_data', []):
            x0, y0, slope = n["x0"], n["y0"], n["slope"]
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
            f"Plotted {len(visible_2d)} 2D curve(s) on [{self.x_min}, {self.x_max}]")

    def _plot_3d(self):
        if self.ax_3d is None:
            return
        self.ax_3d.clear()
        self._setup_axes(self.ax_3d, is_3d=True)

        if self.x_min >= self.x_max or self.y_min >= self.y_max or self.n_pts_3d < 2:
            self.status_var.set("Invalid 3D plot range or resolution")
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
        self.status_var.set(f"Plotted 3D surface(s) [{n_pts}×{n_pts} grid]")

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
            self.status_var.set(f"Marked point: ({x:.4f}, {y:.4f})")

        # Right click (button 3) – delete nearest marked point
        elif event.button == 3:
            if not self.marked_points:
                self.status_var.set("No points to delete")
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
                self.status_var.set(f"Deleted point: ({removed[0]:.4f}, {removed[1]:.4f})")
            else:
                self.status_var.set("Right-click: no point nearby to delete")

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
                self.status_var.set(f"Marked point at x={x}: ({x:.4f}, {y:.4f})")
            else:
                messagebox.showerror("Error", "Could not evaluate function at this x")
        except ValueError:
            messagebox.showerror("Error", "Invalid x value")

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
            messagebox.showerror("Error", "Invalid x value.")
            return
        expr_sub = self._substitute_params(expr)
        y0 = CalcEngine.evaluate(expr_sub, x0)
        slope = CalcEngine.derivative(expr_sub, x0)
        if y0 is None or slope is None:
            err = CalcEngine.get_last_error()
            messagebox.showerror("Error", f"Could not compute tangent.\n{err}")
            return
        self.tangent_data.append({"x0": x0, "y0": y0, "slope": slope, "expr": expr})
        self._plot_all()
        self.status_var.set(f"Tangent at x={x0}: y = {slope:.4g}(x-{x0:.4g}) + {y0:.4g}")

    def _on_draw_normal(self):
        expr = self._get_active_expression()
        if not expr:
            return
        try:
            x0 = float(self._var_tan_x.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid x value.")
            return
        expr_sub = self._substitute_params(expr)
        y0 = CalcEngine.evaluate(expr_sub, x0)
        slope = CalcEngine.derivative(expr_sub, x0)
        if y0 is None or slope is None:
            err = CalcEngine.get_last_error()
            messagebox.showerror("Error", f"Could not compute normal.\n{err}")
            return
        self.normal_data.append({"x0": x0, "y0": y0, "slope": slope, "expr": expr})
        self._plot_all()
        if abs(slope) < 1e-12:
            self.status_var.set(f"Normal at x={x0}: vertical line x = {x0}")
        else:
            normal_slope = -1.0 / slope
            self.status_var.set(f"Normal at x={x0}: y = {normal_slope:.4g}(x-{x0:.4g}) + {y0:.4g}")

    def _clear_tangent_normal(self):
        self.tangent_data.clear()
        self.normal_data.clear()
        self._plot_all()
        self.status_var.set("Cleared tangent and normal lines.")

    # ------------------------------------------------------------------
    #  Intersection Finder
    # ------------------------------------------------------------------
    def _show_intersection_dialog(self):
        curves_2d = [c for c in self.curves if not c.is_3d]
        if len(curves_2d) < 2:
            messagebox.showinfo("Info", "Add at least two 2D curves to find intersections.")
            return
        win = tk.Toplevel(self.root)
        win.title("Find Curve Intersections")
        win.geometry("420x420")
        win.configure(bg="#1e1e2e")
        win.minsize(320, 300)
        win.transient(self.root)
        win.grab_set()

        ttk.Label(win, text="Select two curves to find their intersections:",
                  style="Dark.TLabel").pack(anchor=tk.W, padx=10, pady=(10, 4))

        # Curve A
        ttk.Label(win, text="Curve A:", style="Dark.TLabel").pack(anchor=tk.W, padx=10, pady=(8, 0))
        var_a = tk.StringVar()
        combo_a = ttk.Combobox(win, textvariable=var_a,
                               values=[c.label for c in curves_2d],
                               state="readonly", font=("Consolas", 10), width=40)
        combo_a.pack(fill=tk.X, padx=10, pady=2)
        combo_a.current(0)

        # Curve B
        ttk.Label(win, text="Curve B:", style="Dark.TLabel").pack(anchor=tk.W, padx=10, pady=(8, 0))
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
                messagebox.showwarning("Input", "Please select both curves.", parent=win)
                return
            if label_a == label_b:
                messagebox.showwarning("Input", "Please select two different curves.", parent=win)
                return
            curve_a = None
            curve_b = None
            for c in self.curves:
                if c.label == label_a:
                    curve_a = c
                if c.label == label_b:
                    curve_b = c
            if curve_a is None or curve_b is None:
                messagebox.showerror("Error", "Could not locate selected curves.", parent=win)
                return
            intersections = self._find_intersections(curve_a, curve_b)
            result_text.configure(state=tk.NORMAL)
            result_text.delete("1.0", tk.END)
            if intersections:
                result_text.insert(tk.END, f"Found {len(intersections)} intersection(s):\n\n")
                for i, (xi, yi) in enumerate(intersections, 1):
                    result_text.insert(tk.END, f"  {i}. x = {xi:.10g}, y = {yi:.10g}\n")
            else:
                result_text.insert(tk.END, "No intersections found in the current X range.\n")
            result_text.configure(state=tk.DISABLED)
            self._plot_all()

        btn_frame = ttk.Frame(win, style="Dark.TFrame")
        btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        ttk.Button(btn_frame, text="Find Intersections", command=do_find).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Clear Marks", command=lambda: (self.intersection_marks.clear(), self._plot_all())).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Close", command=win.destroy).pack(side=tk.RIGHT, padx=2)

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
            messagebox.showerror("Error", "Invalid table parameters.")
            return
        if a >= b:
            messagebox.showerror("Error", "From must be less than To.")
            return
        if n < 2 or n > 5000:
            messagebox.showerror("Error", "Points must be between 2 and 5000.")
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
        self.status_var.set(f"Table generated: {valid_count}/{n} valid points.")

    def _show_table_window(self, expr, valid_count):
        win = tk.Toplevel(self.root)
        win.title("Function Table")
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

        ttk.Button(win, text="Close", command=win.destroy).pack(pady=(0, 10))

    def _on_export_csv(self):
        if not self._table_data:
            messagebox.showinfo("Info", "Generate a table first.")
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
            self.status_var.set(f"Exported table to {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    def _on_copy_table(self):
        if not self._table_data:
            messagebox.showinfo("Info", "Generate a table first.")
            return
        lines = [f"x\tf(x) = {self._table_expr}"]
        for x, y in self._table_data:
            lines.append(f"{x:.10g}\t{y if y is not None else 'N/A'}")
        text = "\n".join(lines)
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.status_var.set("Table copied to clipboard.")

    # ------------------------------------------------------------------
    #  Calculus operations
    # ------------------------------------------------------------------
    def _get_active_expression(self) -> Optional[str]:
        sel = self.listbox_curves.curselection()
        if sel:
            curve = self.curves[sel[0]]
            if curve.is_parametric:
                messagebox.showwarning("Parametric Curve",
                    "Calculus operations are not available for parametric curves.\n"
                    "Select a regular (non-parametric) curve.")
                return None
            if curve.is_polar:
                messagebox.showwarning("Polar Curve",
                    "Calculus operations are not available for polar curves.\n"
                    "Select a regular (non-polar, non-parametric) curve.")
                return None
            return curve.expression
        for c in reversed(self.curves):
            if not c.is_parametric and not c.is_polar:
                return c.expression
        expr = self.entry_expr.get().strip()
        if expr:
            return expr
        messagebox.showwarning("No Expression", "Add a function first.")
        return None

    def _on_derivative(self):
        expr = self._get_active_expression()
        if not expr:
            return
        try:
            x_val = float(self._var_diff_x.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid x value.")
            return
        expr_sub = self._substitute_params(expr)
        result = CalcEngine.derivative(expr_sub, x_val)
        if result is None:
            err = CalcEngine.get_last_error()
            messagebox.showerror("Error", f"Derivative failed.\n{err}")
            return
        messagebox.showinfo(
            "Derivative Result",
            f"f(x) = {expr}\n"
            f"f'({x_val}) = {result:.10g}")
        self.status_var.set(f"f'({x_val}) = {result:.10g}")

    def _on_derivative2(self):
        expr = self._get_active_expression()
        if not expr:
            return
        try:
            x_val = float(self._var_diff_x.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid x value.")
            return
        expr_sub = self._substitute_params(expr)
        result = CalcEngine.derivative2(expr_sub, x_val)
        if result is None:
            err = CalcEngine.get_last_error()
            messagebox.showerror("Error", f"Second derivative failed.\n{err}")
            return
        messagebox.showinfo(
            "Second Derivative Result",
            f"f(x) = {expr}\n"
            f"f''({x_val}) = {result:.10g}")
        self.status_var.set(f"f''({x_val}) = {result:.10g}")

    def _on_integrate(self):
        expr = self._get_active_expression()
        if not expr:
            return
        try:
            a = float(self._var_int_a.get())
            b = float(self._var_int_b.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid integration bounds.")
            return
        expr_sub = self._substitute_params(expr)
        result = CalcEngine.integrate_adaptive(expr_sub, a, b)
        if result is None:
            err = CalcEngine.get_last_error()
            messagebox.showerror("Error", f"Integration failed.\n{err}")
            return
        messagebox.showinfo(
            "Integration Result",
            f"f(x) = {expr}\n"
            f"Integrate [{a}, {b}] f(x) dx = {result:.10g}")
        self.status_var.set(f"Integrate [{a},{b}] = {result:.10g}")

    def _on_arc_length(self):
        expr = self._get_active_expression()
        if not expr:
            return
        try:
            a = float(self._var_int_a.get())
            b = float(self._var_int_b.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid arc length bounds.")
            return
        if a >= b:
            messagebox.showerror("Error", "a must be less than b.")
            return
        expr_sub = self._substitute_params(expr)
        result = CalcEngine.arc_length(expr_sub, a, b)
        if result is None:
            messagebox.showerror("Error", "Could not compute arc length.")
            return
        messagebox.showinfo(
            "Arc Length Result",
            f"f(x) = {expr}\n"
            f"Arc length from {a} to {b} = {result:.10g}")
        self.status_var.set(f"Arc length [{a},{b}] = {result:.10g}")

    def _on_area_between_curves(self):
        expr_f = self._var_area_f.get().strip()
        expr_g = self._var_area_g.get().strip()
        if not expr_f or not expr_g:
            messagebox.showwarning("Input Error", "Please enter both f(x) and g(x) expressions.")
            return
        try:
            a_str = self._resolve_t_range(self._var_area_a.get())
            b_str = self._resolve_t_range(self._var_area_b.get())
            a = float(a_str)
            b = float(b_str)
        except ValueError:
            messagebox.showerror("Error", "Invalid interval bounds.")
            return
        if a >= b:
            messagebox.showerror("Error", "a must be less than b.")
            return
        f_sub = self._substitute_params(expr_f)
        g_sub = self._substitute_params(expr_g)
        result = CalcEngine.area_between_curves(f_sub, g_sub, a, b)
        if result is None:
            err = CalcEngine.get_last_error()
            messagebox.showerror("Error", f"Could not compute area between curves.\n{err}")
            return
        messagebox.showinfo(
            "Area Between Curves",
            f"f(x) = {expr_f}\n"
            f"g(x) = {expr_g}\n"
            f"Area from {a} to {b} = {result:.10g}")
        self.status_var.set(f"Area between curves [{a},{b}] = {result:.10g}")

    def _on_limit(self, two_sided=True, side=None):
        expr = self._get_active_expression()
        if not expr:
            return
        try:
            a = float(self._var_limit_a.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid limit point.")
            return
        expr_sub = self._substitute_params(expr)

        if two_sided:
            left  = CalcEngine.limit_left(expr_sub, a)
            right = CalcEngine.limit_right(expr_sub, a)
            if left is None and right is None:
                err = CalcEngine.get_last_error()
                messagebox.showerror("Limit Error", f"Could not compute limit.\n{err}")
                return
            if left is not None and right is not None and abs(left - right) < 1e-8:
                val = (left + right) / 2.0
                messagebox.showinfo(
                    "Limit Result",
                    f"f(x) = {expr}\n"
                    f"lim(x→{a}) f(x) = {val:.10g}\n"
                    f"Left:  {left:.10g}\n"
                    f"Right: {right:.10g}")
                self.status_var.set(f"lim(x→{a}) = {val:.10g}")
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
                messagebox.showwarning("Limit Does Not Exist", msg)
                self.status_var.set(f"lim(x→{a}) does not exist")
        elif side == "left":
            result = CalcEngine.limit_left(expr_sub, a)
            if result is None:
                err = CalcEngine.get_last_error()
                messagebox.showerror("Limit Error", f"Could not compute left limit.\n{err}")
                return
            messagebox.showinfo(
                "Left Limit Result",
                f"f(x) = {expr}\n"
                f"lim(x→{a}⁻) f(x) = {result:.10g}")
            self.status_var.set(f"lim(x→{a}⁻) = {result:.10g}")
        else:
            result = CalcEngine.limit_right(expr_sub, a)
            if result is None:
                err = CalcEngine.get_last_error()
                messagebox.showerror("Limit Error", f"Could not compute right limit.\n{err}")
                return
            messagebox.showinfo(
                "Right Limit Result",
                f"f(x) = {expr}\n"
                f"lim(x→{a}⁺) f(x) = {result:.10g}")
            self.status_var.set(f"lim(x→{a}⁺) = {result:.10g}")

    def _on_fft_compute(self):
        expr = self._get_active_expression()
        if not expr:
            return
        try:
            a = float(self._var_int_a.get())
            b = float(self._var_int_b.get())
            n = int(self._var_fft_n.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid FFT parameters.")
            return
        if a >= b:
            messagebox.showerror("Error", "a must be less than b.")
            return
        if n < 2 or n > 65536:
            messagebox.showerror("Error", "Samples must be between 2 and 65536.")
            return

        expr_sub = self._substitute_params(expr)
        result = CalcEngine.fft_spectrum(expr_sub, a, b, n)
        if result is None:
            messagebox.showerror("Error", "Could not compute FFT spectrum.")
            return
        self._fft_data = result
        self._ensure_fft_window()
        self._plot_fft(result, expr)
        self.status_var.set(f"FFT computed: {len(result['freqs'])} frequency bins")

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
            messagebox.showinfo("Info", "Compute FFT first.")
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
            self.status_var.set(f"Exported FFT to {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

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
            messagebox.showerror("Error", "Invalid Taylor parameters.")
            return
        if order < 1 or order > 20:
            messagebox.showerror("Error", "Order must be between 1 and 20.")
            return

        expr_sub = self._substitute_params(expr)
        coeffs = CalcEngine.taylor_coefficients(expr_sub, a, order)
        if coeffs is None:
            err = CalcEngine.get_last_error()
            messagebox.showerror("Taylor Error", f"Could not compute Taylor expansion.\n{err}")
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
        messagebox.showinfo("Taylor Series", result_msg)
        self.status_var.set(f"Taylor series at a={a}, order={order}")

    def _on_taylor_plot(self):
        expr = self._get_active_expression()
        if not expr:
            return
        try:
            a = float(self._var_taylor_a.get())
            order = int(self._var_taylor_order.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid Taylor parameters.")
            return
        if order < 1 or order > 20:
            messagebox.showerror("Error", "Order must be between 1 and 20.")
            return

        expr_sub = self._substitute_params(expr)
        coeffs = CalcEngine.taylor_coefficients(expr_sub, a, order)
        if coeffs is None:
            err = CalcEngine.get_last_error()
            messagebox.showerror("Taylor Error", f"Could not compute Taylor expansion.\n{err}")
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
        self.status_var.set(f"Taylor plot at a={a}, order={order}")

    # ------------------------------------------------------------------
    #  ODE Solver (RK4)
    # ------------------------------------------------------------------
    def _on_ode_solve(self):
        expr = self._var_ode_expr.get().strip()
        if not expr:
            messagebox.showwarning("Input Error", "Please enter an ODE expression dy/dx = f(x,y).")
            return
        try:
            x0 = float(self._var_ode_x0.get())
            y0 = float(self._var_ode_y0.get())
            x_end = float(self._var_ode_xend.get())
            n_steps = int(self._var_ode_steps.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid ODE parameters.")
            return
        if n_steps < 1 or n_steps > 100000:
            messagebox.showerror("Error", "Steps must be between 1 and 100000.")
            return
        if x0 == x_end:
            messagebox.showerror("Error", "x0 must not equal x_end.")
            return

        result = CalcEngine.ode_solve_rk4(expr, x0, y0, x_end, n_steps)
        if result is None:
            err = CalcEngine.get_last_error()
            messagebox.showerror("ODE Error", f"Could not solve ODE.\n{err}")
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
        messagebox.showinfo("ODE Solution", msg)
        self.status_var.set(f"ODE solved: {len(result['xs'])} points")

    def _on_ode_plot(self):
        if self._ode_data is None:
            messagebox.showinfo("Info", "Solve an ODE first.")
            return
        self._ensure_2d_window()
        self.ax_2d.clear()
        self._setup_axes(self.ax_2d, is_3d=False)

        xs = np.array(self._ode_data['xs'])
        ys = np.array([y if y is not None else np.nan for y in self._ode_data['ys']])

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
        self.status_var.set(f"ODE solution plotted ({len(xs)} points)")

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
            messagebox.showerror("Error", "Invalid solver parameters.")
            return
        expr_sub = self._substitute_params(expr)
        result = CalcEngine.solve(expr_sub, guess=guess, xmin=a, xmax=b)
        if result is None:
            err = CalcEngine.get_last_error()
            messagebox.showerror("Solver Error",
                                 f"Could not find root.\n{err}")
            return
        verify = CalcEngine.evaluate(expr_sub, result)
        verify_str = f"{verify:.2e}" if verify is not None else "N/A"
        messagebox.showinfo(
            "Root Found",
            f"f(x) = {expr} = 0\n"
            f"Root: x = {result:.12g}\n"
            f"Verification: f({result:.6g}) = {verify_str}")
        self.status_var.set(f"Root: x = {result:.12g}")

    def _on_solve_bisection(self):
        expr = self._get_active_expression()
        if not expr:
            return
        try:
            a = float(self._var_solve_a.get())
            b = float(self._var_solve_b.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid bounds.")
            return
        expr_sub = self._substitute_params(expr)
        result = CalcEngine.solve_bisection(expr_sub, a, b)
        if result is None:
            err = CalcEngine.get_last_error()
            messagebox.showerror("Bisection Error",
                                 f"Could not find root.\n{err}")
            return
        messagebox.showinfo(
            "Root Found (Bisection)",
            f"f(x) = {expr} = 0\n"
            f"Root: x = {result:.12g}")
        self.status_var.set(f"Root: x = {result:.12g}")

    def _on_solve_system_2d(self):
        f_expr = self._var_sys_f.get().strip()
        g_expr = self._var_sys_g.get().strip()
        if not f_expr or not g_expr:
            messagebox.showerror("Error", "Enter both f(x,y) and g(x,y) expressions.")
            return
        try:
            x0 = float(self._var_sys_x0.get())
            y0 = float(self._var_sys_y0.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid initial guess.")
            return
        result = CalcEngine.solve_system_2d(f_expr, g_expr, x0, y0)
        if result is None:
            err = CalcEngine.get_last_error()
            messagebox.showerror("System Solver Error",
                                 f"Could not solve system.\n{err}")
            return
        x_sol = result['x']
        y_sol = result['y']
        f_val = CalcEngine.evaluate_xy(f_expr, x_sol, y_sol)
        g_val = CalcEngine.evaluate_xy(g_expr, x_sol, y_sol)
        f_str = f"{f_val:.2e}" if f_val is not None else "N/A"
        g_str = f"{g_val:.2e}" if g_val is not None else "N/A"
        messagebox.showinfo(
            "System Solved",
            f"f(x,y) = {f_expr}\ng(x,y) = {g_expr}\n\n"
            f"Solution:\n  x = {x_sol:.12g}\n  y = {y_sol:.12g}\n\n"
            f"Residuals:\n  f(x,y) = {f_str}\n  g(x,y) = {g_str}")
        self.status_var.set(f"System: x={x_sol:.10g}, y={y_sol:.10g}")

    def _on_find_extremum(self, minimum: bool = True):
        expr = self._get_active_expression()
        if not expr:
            return
        try:
            a = float(self._var_ext_a.get())
            b = float(self._var_ext_b.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid interval bounds.")
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
            messagebox.showerror("Extremum Error",
                                 f"Could not find {label.lower()}.\n{err}")
            return
        f_val = CalcEngine.evaluate(expr_sub, result)
        verify_str = f"{f_val:.10g}" if f_val is not None else "N/A"
        messagebox.showinfo(
            f"{label} Found",
            f"f(x) = {expr}\n"
            f"{label}: x = {result:.12g}\n"
            f"f({result:.6g}) = {verify_str}")
        self.status_var.set(f"{label}: x = {result:.12g}, f(x) = {verify_str}")

    def _on_scan_roots(self):
        expr = self._get_active_expression()
        if not expr:
            return
        try:
            a = float(self._var_ext_a.get())
            b = float(self._var_ext_b.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid interval bounds.")
            return
        if a >= b:
            messagebox.showerror("Error", "a must be less than b.")
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
            messagebox.showinfo("Root Scan Results", msg)
            self.status_var.set(f"Found {len(unique_roots)} root(s)")
        else:
            messagebox.showinfo("Root Scan Results", "No roots found in the interval.")
            self.status_var.set("No roots found")

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
        for t in tokens:
            t = t.strip()
            if not t:
                continue
            try:
                values.append(float(t))
            except ValueError:
                messagebox.showerror("Input Error", f"Invalid number: '{t}'")
                return None
        if not values:
            messagebox.showerror("Input Error", "No valid numbers entered.")
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
        data_var_sam = _stats.variance(values)
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
        messagebox.showinfo("Statistics Results", msg)
        self.status_var.set(f"Stats: n={n}, mean={data_mean:.6g}, std={data_std_pop:.6g}")

    def _on_stats_sort(self):
        values = self._parse_stats_data()
        if values is None:
            return
        sorted_vals = sorted(values)
        self._var_stats_data.set(", ".join(f"{v:g}" for v in sorted_vals))
        self.status_var.set(f"Data sorted ({len(values)} values)")

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
        self.status_var.set(f"Histogram plotted ({len(values)} values, {n_bins} bins)")

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
            self.status_var.set(f"Exported {len(values)} values to {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Could not export: {e}")

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
                    messagebox.showerror("Matrix Error", f"Invalid number: '{c}'")
                    return None
            if vals:
                matrix.append(vals)
        if not matrix:
            return None
        ncols = len(matrix[0])
        for row in matrix:
            if len(row) != ncols:
                messagebox.showerror("Matrix Error", "All rows must have the same number of columns.")
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
        ttk.Button(win, text="Close", command=win.destroy).pack(pady=(0, 10))

    def _on_matrix_add(self):
        a = self._parse_matrix(self._var_matrix_a.get())
        b = self._parse_matrix(self._var_matrix_b.get())
        if a is None or b is None:
            return
        try:
            result = np.array(a) + np.array(b)
            self._show_matrix_result("A + B", self._format_matrix(result))
            self.status_var.set("Matrix A + B computed")
        except Exception as e:
            messagebox.showerror("Matrix Error", f"Addition failed: {e}")

    def _on_matrix_sub(self):
        a = self._parse_matrix(self._var_matrix_a.get())
        b = self._parse_matrix(self._var_matrix_b.get())
        if a is None or b is None:
            return
        try:
            result = np.array(a) - np.array(b)
            self._show_matrix_result("A - B", self._format_matrix(result))
            self.status_var.set("Matrix A - B computed")
        except Exception as e:
            messagebox.showerror("Matrix Error", f"Subtraction failed: {e}")

    def _on_matrix_mul(self):
        a = self._parse_matrix(self._var_matrix_a.get())
        b = self._parse_matrix(self._var_matrix_b.get())
        if a is None or b is None:
            return
        try:
            result = np.array(a) @ np.array(b)
            self._show_matrix_result("A * B", self._format_matrix(result))
            self.status_var.set("Matrix A * B computed")
        except Exception as e:
            messagebox.showerror("Matrix Error", f"Multiplication failed: {e}")

    def _on_matrix_det(self):
        a = self._parse_matrix(self._var_matrix_a.get())
        if a is None:
            return
        try:
            arr = np.array(a)
            if arr.shape[0] != arr.shape[1]:
                messagebox.showerror("Matrix Error", "Determinant requires a square matrix.")
                return
            det = np.linalg.det(arr)
            self._show_matrix_result("det(A)", f"det(A) = {det:.10g}")
            self.status_var.set(f"det(A) = {det:.10g}")
        except Exception as e:
            messagebox.showerror("Matrix Error", f"Determinant failed: {e}")

    def _on_matrix_inv(self):
        a = self._parse_matrix(self._var_matrix_a.get())
        if a is None:
            return
        try:
            arr = np.array(a)
            if arr.shape[0] != arr.shape[1]:
                messagebox.showerror("Matrix Error", "Inverse requires a square matrix.")
                return
            result = np.linalg.inv(arr)
            self._show_matrix_result("inv(A)", self._format_matrix(result))
            self.status_var.set("Matrix inverse computed")
        except np.linalg.LinAlgError:
            messagebox.showerror("Matrix Error", "Matrix is singular, inverse does not exist.")
        except Exception as e:
            messagebox.showerror("Matrix Error", f"Inverse failed: {e}")

    def _on_matrix_transpose(self):
        a = self._parse_matrix(self._var_matrix_a.get())
        if a is None:
            return
        try:
            result = np.array(a).T
            self._show_matrix_result("A^T (Transpose)", self._format_matrix(result))
            self.status_var.set("Matrix transpose computed")
        except Exception as e:
            messagebox.showerror("Matrix Error", f"Transpose failed: {e}")

    def _on_matrix_rank(self):
        a = self._parse_matrix(self._var_matrix_a.get())
        if a is None:
            return
        try:
            arr = np.array(a)
            rank = np.linalg.matrix_rank(arr)
            self._show_matrix_result("rank(A)", f"rank(A) = {rank}")
            self.status_var.set(f"rank(A) = {rank}")
        except Exception as e:
            messagebox.showerror("Matrix Error", f"Rank computation failed: {e}")

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
            self.status_var.set(f"RREF computed, rank = {len(pivot_cols)}")
        except Exception as e:
            messagebox.showerror("Matrix Error", f"RREF failed: {e}")

    def _on_matrix_eigen(self):
        a = self._parse_matrix(self._var_matrix_a.get())
        if a is None:
            return
        try:
            arr = np.array(a)
            if arr.shape[0] != arr.shape[1]:
                messagebox.showerror("Matrix Error", "Eigenvalues require a square matrix.")
                return
            eigenvalues, eigenvectors = np.linalg.eig(arr)
            lines = ["Eigenvalues:"]
            for i, val in enumerate(eigenvalues):
                lines.append(f"  λ{i+1} = {val:.10g}")
            lines.append("")
            lines.append("Eigenvectors (columns):")
            lines.append(self._format_matrix(eigenvectors))
            self._show_matrix_result("Eigenvalues & Eigenvectors", "\n".join(lines))
            self.status_var.set(f"Eigenvalues: {[f'{v:.6g}' for v in eigenvalues]}")
        except np.linalg.LinAlgError:
            messagebox.showerror("Matrix Error", "Eigenvalue computation failed.")
        except Exception as e:
            messagebox.showerror("Matrix Error", f"Eigenvalue failed: {e}")

    def _on_matrix_clear(self):
        self._var_matrix_a.set("")
        self._var_matrix_b.set("")
        self.status_var.set("Matrix inputs cleared.")

    # ------------------------------------------------------------------
    #  Complex Number Operations
    # ------------------------------------------------------------------
    def _parse_complex(self, s: str):
        """Parse a complex number from string (a+bi format)."""
        s = s.strip().replace(' ', '')
        if not s:
            return None
        try:
            # Handle 'i' at the end
            if s.endswith('i') or s.endswith('I'):
                s = s[:-1]
                if not s or s == '+':
                    return complex(0, 1)
                elif s == '-':
                    return complex(0, -1)
                # Handle cases like "3+2i" -> "3+2j"
                # Python's complex() expects 'j' suffix
                if '+' in s:
                    parts = s.split('+')
                    real_part = parts[0]
                    imag_part = parts[1]
                    if imag_part:
                        return complex(float(real_part), float(imag_part))
                    else:
                        return complex(float(real_part), 0)
                elif s.startswith('-') and '-' in s[1:]:
                    # Handle "-3-2i" -> "-3-2j"
                    idx = s[1:].index('-') + 1
                    real_part = s[:idx]
                    imag_part = s[idx:]
                    if imag_part:
                        return complex(float(real_part), float(imag_part))
                    else:
                        return complex(float(real_part), 0)
                else:
                    # Pure imaginary like "2i" -> "2j"
                    return complex(float(s), 0) if s else complex(0, 1)
            else:
                return complex(float(s), 0)
        except ValueError:
            try:
                return complex(s)
            except ValueError:
                messagebox.showerror("Complex Error", f"Invalid complex number: {s}")
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
        self.status_var.set(f"Result: {result}")

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
            if z2 == 0:
                messagebox.showerror("Complex Error", "Division by zero")
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
                messagebox.showerror("Complex Error", "ln(0) is undefined")
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
            self._show_complex_result(f"|z| = {result:.10g}")

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


# ---------------------------------------------------------------------------
#  Entry point
# ---------------------------------------------------------------------------
def main():
    root = tk.Tk()
    app = SuperCalcApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
