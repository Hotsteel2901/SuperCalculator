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
"""

import sys
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List
import math
import re

import matplotlib
# Dynamically select backend: try TkAgg first, fallback to Agg for headless environments
try:
    import tkinter
    matplotlib.use("TkAgg")
except (ImportError, RuntimeError):
    matplotlib.use("Agg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np

from calc_bridge import CalcEngine

# ---------------------------------------------------------------------------
#  Constants
# ---------------------------------------------------------------------------
MIN_PLOT_POINTS = 10
MAX_PLOT_POINTS = 5000
MAX_3D_POINTS = 200
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
                 "visible", "label", "is_3d", "parameters")

    def __init__(self, expr, color, label="", lw=2, ls="-"):
        self.expression = expr
        self.color = color
        self.linewidth = lw
        self.linestyle = ls
        self.visible = True
        self.label = label or expr
        self.is_3d = self._detect_3d(expr)
        self.parameters = self._detect_parameters(expr)

    def _detect_3d(self, expr: str) -> bool:
        has_x = 'x' in expr.lower()
        has_y = 'y' in expr.lower()
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
        self.grid_on = True
        self.param_values = {}
        self.marked_points = []
        self.auto_mark_point = None
        self.root_markers = []

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

        self.root.protocol("WM_DELETE_WINDOW", self._on_main_close)
        self._build_ui()
        self._add_curve("sin(x)")

    def _on_main_close(self):
        """Clean up child plot windows before exiting."""
        if self.window_2d is not None and self.window_2d.winfo_exists():
            self.window_2d.destroy()
        if self.window_3d is not None and self.window_3d.winfo_exists():
            self.window_3d.destroy()
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
        
        ttk.Label(frm_mark, text="Click on 2D plot to mark, or enter x:",
                  style="Dark.TLabel").pack(anchor=tk.W, padx=6, pady=(6, 0))
        
        mark_row = ttk.Frame(frm_mark, style="Dark.TFrame")
        mark_row.pack(fill=tk.X, padx=6, pady=2)
        self._var_mark_x = tk.StringVar(value="")
        ttk.Entry(mark_row, textvariable=self._var_mark_x, width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(mark_row, text="Mark Point",
                   command=self._on_mark_point).pack(side=tk.LEFT, padx=2)
        ttk.Button(mark_row, text="Clear Marks",
                   command=self._clear_marks).pack(side=tk.LEFT, padx=2)

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
            var = tk.StringVar(value="1")
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

    def _substitute_params(self, expr: str) -> str:
        result = expr
        for param, value in self.param_values.items():
            result = re.sub(r'\b' + param + r'\b', str(value), result, flags=re.IGNORECASE)
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
        self._var_mark_x.set("")
        if self.ax_2d is not None:
            self.ax_2d.clear()
            self._setup_axes(self.ax_2d, is_3d=False)
            self.canvas_2d.draw()
        if self.ax_3d is not None:
            self.ax_3d.clear()
            self._setup_axes(self.ax_3d, is_3d=True)
            self.canvas_3d.draw()
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
        expr = self.entry_expr.get().strip()
        if expr:
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
            self.grid_on = self._var_grid.get()
        except ValueError:
            pass

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

        has_2d = any(not c.is_3d and c.visible for c in self.curves)
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

        n_pts = max(MIN_PLOT_POINTS, min(MAX_PLOT_POINTS, int((self.x_max - self.x_min) / self.step_size)))
        xs_np = np.linspace(self.x_min, self.x_max, n_pts)
        xs_list = xs_np.tolist()

        for curve in self.curves:
            if not curve.visible or curve.is_3d:
                continue
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

        visible_2d = [c for c in self.curves if c.visible and not c.is_3d]
        if visible_2d:
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

        n_pts = max(MIN_PLOT_POINTS, min(MAX_3D_POINTS, int((self.x_max - self.x_min) / self.step_size)))
        x_vals = np.linspace(self.x_min, self.x_max, n_pts)
        y_vals = np.linspace(self.y_min, self.y_max, n_pts)
        X, Y = np.meshgrid(x_vals, y_vals)

        cmap_idx = 0
        for curve in self.curves:
            if not curve.visible or not curve.is_3d:
                continue
            expr = self._substitute_params(curve.expression)

            def eval_xy(xv, yv):
                val = CalcEngine.evaluate_xy(expr, xv, yv)
                return val if val is not None else np.nan

            vfunc = np.vectorize(eval_xy)
            Z = vfunc(X, Y)

            cmap = CMAP_3D_OPTIONS[cmap_idx % len(CMAP_3D_OPTIONS)]
            cmap_idx += 1
            self.ax_3d.plot_surface(X, Y, Z, cmap=cmap, alpha=0.8)

        self.canvas_3d.draw()
        self.status_var.set(f"Plotted 3D surface(s)")

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
        if x is not None and y is not None:
            self.marked_points.append((x, y))
            self._plot_all()
            self.status_var.set(f"Marked point: ({x:.4f}, {y:.4f})")

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
        self._var_mark_x.set("")
        self._plot_all()

    # ------------------------------------------------------------------
    #  Calculus operations
    # ------------------------------------------------------------------
    def _get_active_expression(self) -> Optional[str]:
        sel = self.listbox_curves.curselection()
        if sel:
            return self.curves[sel[0]].expression
        if self.curves:
            return self.curves[-1].expression
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

    # ------------------------------------------------------------------
    #  Equation solving
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


# ---------------------------------------------------------------------------
#  Entry point
# ---------------------------------------------------------------------------
def main():
    root = tk.Tk()
    app = SuperCalcApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
