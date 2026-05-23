# Super Function Graphing Calculator

> 超级函数绘图计算器 — 基于桥接模式(Bridge Pattern)，融合 C 与 Python 优势的高性能函数计算与可视化工具

[English](README.md) | **中文**
> **注意：** 本项目完全由 AI (Claude Code) 生成，请自行评估使用风险。

## 架构

```
+---------------------------------+
|  super_calc_bridged.py          |  Tkinter + Matplotlib GUI
|  (抽象层)                       |
+---------------------------------+
|  calc_bridge.py                 |  ctypes 桥接层
|  (桥接层)                       |
+---------------------------------+
|  calc_core.dll / .so            |  C 动态库
|  (实现层)                       |
+---------------------------------+
```

采用**桥接模式(Bridge Pattern)**设计，将 GUI 与计算核心解耦：
- **C 层**负责所有数值计算 —— 表达式解析、微积分、方程求解
- **Python 层**通过 `ctypes` 调用 C 核心，提供 Tkinter + Matplotlib 图形界面

## 功能特性

- **函数绘图** — 支持输入任意含 `x` 的数学表达式并绘制曲线
- **多曲线叠加** — 同时绘制多条函数曲线，自动分配不同颜色
- **数值微分** — 一阶导数 f'(x) 和二阶导数 f''(x)，采用中心差分法
- **数值积分** — 定积分计算，采用自适应 Simpson 复合法则
- **方程求解** — Newton-Raphson 法（二分法回退）+ 纯二分法
- **预设函数** — 内置 15 个常用函数，一键选择
- **自定义视图** — X/Y 坐标范围、采样步长、网格开关均可调节
- **交互式图表** — Matplotlib 工具栏支持缩放、平移、导出 PNG

## 环境要求

- **Python 3.9+** 并安装以下包：`numpy`、`matplotlib`
- **C 编译器** (Windows 推荐 MinGW-w64，Linux/macOS 使用 GCC)

安装 Python 依赖：

```bash
pip install numpy matplotlib
```

## 编译 C 核心

### Windows (MinGW-w64 / MSYS2)

```bash
gcc -shared -O2 -o calc_core.dll calc_core.c -lm
```

### Windows (MSVC - 开发者命令提示符)

```bash
cl /LD /O2 calc_core.c /Fe:calc_core.dll
```

### Linux

```bash
gcc -shared -O2 -fPIC -o calc_core.so calc_core.c -lm
```

### macOS

```bash
gcc -shared -O2 -fPIC -o calc_core.dylib calc_core.c -lm
```

### 从 Linux 交叉编译到 Windows

```bash
x86_64-w64-mingw32-gcc -shared -O2 -o calc_core.dll calc_core.c -lm
```

## 使用方法

```bash
cd SuperCalculator
python super_calc_bridged.py
```

### 表达式语法

| 类别       | 运算符 / 函数                    | 示例                |
|-----------|----------------------------------|---------------------|
| 算术运算    | `+` `-` `*` `/` `^` (乘方)      | `x^2 + 2*x - 1`    |
| 三角函数    | `sin` `cos` `tan`               | `sin(x) + cos(x)`   |
| 对数/指数   | `ln` `log` `exp`                | `ln(x)` `exp(-x)`   |
| 根号/绝对值 | `sqrt` `abs`                    | `sqrt(x)` `abs(x)`  |
| 数学常数    | `pi` `e`                        | `sin(pi*x)`         |

## 文件结构

```
SuperCalculator/
  calc_core.c            C 核心引擎 (表达式解析、微积分、方程求解)
  calc_bridge.py         Python ctypes 桥接层
  super_calc_bridged.py  GUI 主程序
  README.md              英文说明文档
  README_CN.md           中文说明文档 (本文件)
```

## API 参考

```python
from calc_bridge import CalcEngine

# 求值
CalcEngine.evaluate("x^2", 3.0)         # -> 9.0

# 批量求值 (绘图用)
CalcEngine.evaluate_array("sin(x)", [0, 0.5, 1.0])

# 一阶导数
CalcEngine.derivative("x^3", 2.0)       # -> ~12.0 (f'(x)=3x^2)

# 二阶导数
CalcEngine.derivative2("x^3", 2.0)      # -> ~12.0 (f''(x)=6x)

# 定积分
CalcEngine.integrate_adaptive("x^2", 0, 1)  # -> ~0.333 (∫x^2dx = 1/3)

# 方程求根 (Newton-Raphson)
CalcEngine.solve("x^2 - 4", guess=1, xmin=0, xmax=3)  # -> 2.0

# 方程求根 (二分法)
CalcEngine.solve_bisection("x^2 - 4", 0, 3)          # -> 2.0
```

## 数值方法

| 方法       | 算法                                | 误差      |
|-----------|-------------------------------------|----------|
| 一阶导数   | 中心差分: (f(x+h)-f(x-h)) / 2h     | O(h²)    |
| 二阶导数   | 中心差分: (f(x+h)-2f(x)+f(x-h)) / h² | O(h²)  |
| 定积分     | 自适应 Simpson 复合法则             | O(h⁴)    |
| 方程求根   | Newton-Raphson + 二分法回退         | —        |

## 设计说明

本项目采用**桥接模式(Bridge Pattern)**的核心思想：将抽象(GUI)与实现(计算引擎)分离，使两者可以独立变化。

- 如果需要更换 GUI 框架（如 PyQt、Web），只需修改 `super_calc_bridged.py`，无需改动 C 核心
- 如果需要增强计算能力（如偏微分、常微分方程），只需修改 `calc_core.c`，无需改动 GUI
- `calc_bridge.py` 作为桥接层，负责类型转换、错误处理和 API 封装
