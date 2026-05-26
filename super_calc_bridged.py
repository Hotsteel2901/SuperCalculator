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
  - 3D function plotting for z=f(x,y)
  - Parameter detection and dynamic input
  - Input panel with quick buttons
  - Coordinate marking on click and by x input
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
import math
import re

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np

from calc_bridge import CalcEngine

# ---------------------------------------------------------------------------
#  Constants
# ---------------------------------------------------------------------------
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

PARAM_PATTERN = re.compile(r'\b([a-zA-Z]+)\b')
KNOWN_FUNCTIONS = {'sin', 'cos', 'tan', 'log', 'ln', 'exp', 'sqrt', 'abs'}
KNOWN_CONSTANTS = {'pi', 'e'}

def _detect_parameters_static(expr: str) -> list:
    params = set()
    expr_lower = expr.lower()
    for func in KNOWN_FUNCTIONS:
        expr_lower = re.sub(r'\b' + func + r'\b', '', expr_lower)
    for const in KNOWN_CONSTANTS:
        expr_lower = re.sub(r'\b' + const + r'\b', '', expr_lower)
    for match in PARAM_PATTERN.finditer(expr_lower):
        word = match.group(1)
        if len(word) == 1 and word not in ('x', 'y'):
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
        self.root.geometry("1400x800")
        self.root.minsize(1000, 600)
        self.root.configure(bg="#1e1e2e")

        self.curves: list[CurveModel] = []
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

        self._build_ui()
        self._add_curve("sin(x)")

    # ------------------------------------------------------------------
    #  UI Construction
    # ------------------------------------------------------------------
    def _build_ui(self):
        paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        left = ttk.Frame(paned, width=400, style="Dark.TFrame")
        paned.add(left, weight=0)

        right = ttk.Frame(paned, style="Dark.TFrame")
        paned.add(right, weight=1)

        self._build_control_panel(left)
        self._build_plot_panel(right)

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
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # --- Expression Input ---
        frm_expr = ttk.LabelFrame(scroll_frame, text="Function Input",
                                  style="Dark.TLabelframe")
        frm_expr.pack(fill=tk.X, padx=8, pady=(8, 4))

        ttk.Label(frm_expr, text="Expression f(x):",
                  style="Dark.TLabel").pack(anchor=tk.W, padx=6, pady=(6, 0))
        
        input_row = ttk.Frame(frm_expr, style="Dark.TFrame")
        input_row.pack(fill=tk.X, padx=6, pady=2)
        
        self.entry_expr = ttk.Entry(input_row, font=("Consolas", 12), width=25)
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
        for col, (lbl, var_attr) in enumerate(
            [("X min", "x_min"), ("X max", "x_max"),
             ("Y min", "y_min"), ("Y max", "y_max")]):
            ttk.Label(grid, text=lbl, style="Dark.TLabel").grid(
                row=0, column=col, padx=2, sticky=tk.W)
            v = tk.StringVar(value=str(getattr(self, var_attr)))
            e = ttk.Entry(grid, textvariable=v, width=7)
            e.grid(row=1, column=col, padx=2)
            setattr(self, f"_var_{var_attr}", v)

        ttk.Label(frm_range, text="Step:",
                  style="Dark.TLabel").pack(side=tk.LEFT, padx=(6, 2), pady=(0, 4))
        self._var_step = tk.StringVar(value=str(self.step_size))
        ttk.Entry(frm_range, textvariable=self._var_step, width=6).pack(
            side=tk.LEFT, pady=(0, 4))
        ttk.Button(frm_range, text="Apply",
                   command=self._on_apply_range).pack(side=tk.RIGHT, padx=6, pady=(0, 4))

        self._var_grid = tk.BooleanVar(value=True)
        ttk.Checkbutton(frm_range, text="Grid",
                        variable=self._var_grid).pack(
            side=tk.LEFT, padx=(12, 0), pady=(0, 4))

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

        # --- Coordinate Marking ---
        frm_mark = ttk.LabelFrame(scroll_frame, text="Coordinate Marking",
                                  style="Dark.TLabelframe")
        frm_mark.pack(fill=tk.X, padx=8, pady=4)
        
        ttk.Label(frm_mark, text="Click on plot to mark, or enter x:",
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

    def _build_plot_panel(self, parent):
        self.fig = Figure(figsize=(10, 8), dpi=100, facecolor="#1e1e2e")
        self.ax = self.fig.add_subplot(111, projection='3d')
        self._setup_axes()

        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.draw()

        toolbar = NavigationToolbar2Tk(self.canvas, parent)
        toolbar.update()

        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        self.canvas.mpl_connect('button_press_event', self._on_canvas_click)

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
        
        style = ttk.Style()
        style.configure("Dark.TButton", background="#313244", foreground="#cdd6f4")
        
        main_frame = ttk.Frame(panel, style="Dark.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        buttons_config = [
            ("Basic", [
                ("x²", "x^2"), ("x³", "x^3"), ("xⁿ", "x^n"),
                ("√", "sqrt("), ("³√", "x^(1/3)"), ("|x|", "abs("),
            ]),
            ("Operators", [
                ("÷", "/"), ("×", "*"), ("%", "%"), ("-", "-"), ("+", "+"),
            ]),
            ("Log/Exp", [
                ("㏑", "ln("), ("㏒", "log("), ("lg", "log("), ("eˣ", "exp("), ("e", "e"),
            ]),
            ("Trig", [
                ("sin", "sin("), ("cos", "cos("), ("tan", "tan("),
                ("π", "pi"), ("°", "*pi/180"),
            ]),
            ("Special", [
                ("!", "!"), ("(", "("), (")", ")"), (",", ","),
                ("σ", "sigma"), ("μ", "mu"),
            ]),
            ("Constants", [
                ("π", "pi"), ("e", "e"), ("φ", "1.6180339887"),
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
        expr = self.entry_expr.get()
        pos = self.entry_expr.index(tk.INSERT)
        self.entry_expr.insert(pos, text)
        self.entry_expr.focus()

    # ------------------------------------------------------------------
    #  Parameter handling
    # ------------------------------------------------------------------
    def _update_param_inputs(self):
        expr = self.entry_expr.get().strip()
        params = CurveModel._detect_parameters(expr)
        
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
        self.ax.clear()
        self._setup_axes()
        self.canvas.draw()

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
            self.x_min = float(self._var_x_min.get())
            self.x_max = float(self._var_x_max.get())
            self.y_min = float(self._var_y_min.get())
            self.y_max = float(self._var_y_max.get())
            self.step_size = float(self._var_step.get())
            self.grid_on = self._var_grid.get()
            self._plot_all()
        except ValueError:
            messagebox.showerror("Error", "Invalid range values.")

    def _plot_all(self):
        if not self.curves:
            return

        try:
            self.x_min = float(self._var_x_min.get())
            self.x_max = float(self._var_x_max.get())
            self.y_min = float(self._var_y_min.get())
            self.y_max = float(self._var_y_max.get())
            self.step_size = float(self._var_step.get())
            self.grid_on = self._var_grid.get()
        except ValueError:
            pass

        has_3d = any(c.is_3d for c in self.curves)
        
        if has_3d:
            self._plot_3d()
        else:
            self._plot_2d()

    def _plot_2d(self):
        self.ax.clear()
        self.ax = self.fig.add_subplot(111)
        self._setup_axes()

        n_pts = max(10, min(5000, int((self.x_max - self.x_min) / self.step_size)))
        xs_np = np.linspace(self.x_min, self.x_max, n_pts)
        xs_list = xs_np.tolist()

        for curve in self.curves:
            if not curve.visible:
                continue
            expr = self._substitute_params(curve.expression)
            ys = CalcEngine.evaluate_array(expr, xs_list)
            ys_clean = np.array([y if y is not None else np.nan for y in ys])
            self.ax.plot(xs_np, ys_clean, color=curve.color,
                         linewidth=curve.linewidth, linestyle=curve.linestyle,
                         label=curve.label, alpha=0.9)

        for point in self.marked_points:
            self.ax.plot(point[0], point[1], 'ro', markersize=8)
            self.ax.annotate(f"({point[0]:.3f}, {point[1]:.3f})",
                           xy=(point[0], point[1]), xytext=(10, 10),
                           textcoords='offset points', color='#f38ba8')

        if self.auto_mark_point:
            x = self.auto_mark_point
            expr = self._get_active_expression()
            if expr:
                expr_sub = self._substitute_params(expr)
                y = CalcEngine.evaluate(expr_sub, x)
                if y is not None:
                    self.ax.plot(x, y, 'go', markersize=10)
                    self.ax.annotate(f"({x:.3f}, {y:.3f})",
                                   xy=(x, y), xytext=(10, -15),
                                   textcoords='offset points', color='#a6e3a1')

        if any(c.visible for c in self.curves):
            self.ax.legend(loc="upper right", facecolor="#313244",
                           edgecolor="#585b70", labelcolor="#cdd6f4",
                           fontsize=9)

        self.canvas.draw()
        self.status_var.set(
            f"Plotted {len(self.curves)} curve(s) on [{self.x_min}, {self.x_max}]")

    def _plot_3d(self):
        self.ax.clear()
        self.ax = self.fig.add_subplot(111, projection='3d')
        self._setup_axes()

        n_pts = max(10, min(200, int((self.x_max - self.x_min) / self.step_size)))
        x_vals = np.linspace(self.x_min, self.x_max, n_pts)
        y_vals = np.linspace(self.y_min, self.y_max, n_pts)
        X, Y = np.meshgrid(x_vals, y_vals)

        for curve in self.curves:
            if not curve.visible:
                continue
            if not curve.is_3d:
                continue
            expr = self._substitute_params(curve.expression)
            Z = np.zeros_like(X)
            for i in range(n_pts):
                for j in range(n_pts):
                    Z[i, j] = CalcEngine.evaluate(expr, X[i, j]) or np.nan
            
            self.ax.plot_surface(X, Y, Z, cmap='viridis', alpha=0.8,
                                label=curve.label)

        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')

        self.canvas.draw()
        self.status_var.set(f"Plotted 3D surface(s)")

    def _setup_axes(self):
        try:
            if hasattr(self.ax, 'set_xlim'):
                self.ax.set_xlim(self.x_min, self.x_max)
                self.ax.set_ylim(self.y_min, self.y_max)
        except ValueError:
            pass
        if hasattr(self.ax, 'grid'):
            self.ax.grid(self.grid_on, color="#45475a", alpha=0.5, linestyle="--")
        if hasattr(self.ax, 'axhline'):
            self.ax.axhline(y=0, color="#585b70", linewidth=0.8)
            self.ax.axvline(x=0, color="#585b70", linewidth=0.8)
        self.ax.set_xlabel("x")
        self.ax.set_ylabel("f(x)")
        self.ax.tick_params(colors="#cdd6f4")
        self.ax.set_facecolor("#181825")

    # ------------------------------------------------------------------
    #  Coordinate marking
    # ------------------------------------------------------------------
    def _on_canvas_click(self, event):
        if event.inaxes != self.ax:
            return
        if hasattr(self.ax, 'zaxis'):
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


# ---------------------------------------------------------------------------
#  Entry point
# ---------------------------------------------------------------------------
def main():
    root = tk.Tk()
    app = SuperCalcApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
