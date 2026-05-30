# Super Function Graphing Calculator

> 超级函数绘图计算器 — 基于桥接模式(Bridge Pattern)，融合 C 与 Python 优势的高性能函数计算与可视化工具

[![Build Windows EXE](https://github.com/Hotsteel2901/SuperCalculator/actions/workflows/build-windows-exe.yml/badge.svg)](https://github.com/Hotsteel2901/SuperCalculator/actions/workflows/build-windows-exe.yml)

[![Build Android APK](https://github.com/Hotsteel2901/SuperCalculator/actions/workflows/build-android-apk.yml/badge.svg)](https://github.com/Hotsteel2901/SuperCalculator/actions/workflows/build-android-apk.yml)

[English](README.md) | **中文**
同时包含一个基于 Material Design 3 的 **Android APK** (aarch64)。

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

采用**桥接模式(Bridge Pattern)**设计：
- **C 层**负责所有数值计算 — 表达式解析、微积分、方程求解
- **Python 层**通过 `ctypes` 调用 C 核心，提供 Tkinter + Matplotlib 图形界面
- 桥接层启动时自动检测平台和 CPU 架构，选择正确的预编译二进制文件

## 功能特性

- **函数绘图** — 支持输入任意含 `x` 的数学表达式并绘制曲线
- **3D 函数绘图** — 支持含 `x` 和 `y` 的三维函数表达式，绘制 3D 曲面图
- **参数曲线绘图** — 支持以 x(t) 和 y(t) 定义的参数曲线，内置 10 种预设（圆、椭圆、李萨如图形、螺旋线、心形线等）
- **多曲线叠加** — 同时绘制多条函数曲线，自动分配不同颜色
- **数值微分** — 一阶导数 f'(x) 和二阶导数 f''(x)，采用中心差分法
- **数值积分** — 定积分计算，采用自适应 Simpson 复合法则
- **方程求解** — Newton-Raphson 法（二分法回退）+ 纯二分法
- **极值查找** — 黄金分割搜索法，在指定区间内寻找局部最小值与最大值
- **极限计算** — 左极限、右极限与双侧极限，采用 Richardson 外推法提高精度
 - **零点自动扫描** — 在指定区间内自动扫描函数的所有零点，符号变化检测 + 二分法精确定位
 - **曲线交点查找** — 在任意两条 2D 曲线之间查找所有交点，符号变化检测 + 二分法精确定位，结果自动标注在图上
 - **切线与法线绘制** — 在 2D 曲线任意点处一键绘制切线与法线，以虚线形式直观标注在图上，便于分析函数局部特征
 - **弧长计算** — 在任意区间上通过自适应弦长累加法逼近曲线弧长
  - **傅里叶变换与频谱分析** — 对任意函数进行 FFT 频谱分析，自动识别主频分量，绘制幅度谱与相位谱，支持 CSV 导出
  - **预设函数** — 内置 21 个常用函数（含 3D 与 FFT 预设）+ 10 个参数曲线预设，一键选择
  - **参数系统** — 自动检测表达式中的额外参数（如 `a`、`b`），动态生成输入框实时调节
  - **坐标标记** — 左键点击图表标记坐标点，右键点击删除已标之点，或输入 x 值自动定位
 - **快速输入面板** — 弹出式快捷按钮面板，一键输入运算符、函数与常数
 - **阶乘支持** — 后置运算符 `!`，支持非负整数阶乘
 - **自定义视图** — X/Y/Z 坐标范围、采样步长、网格开关均可调节
 - **交互式图表** — Matplotlib 工具栏支持缩放、平移、导出 PNG
  - **函数数据表与 CSV 导出** — 在任意区间一键生成 x-f(x) 数据表格，支持导出为 CSV 或复制到剪贴板
  - **FFT 频谱导出** — 将频率、幅度与相位数据导出为 CSV，便于外部分析
  - **Windows EXE** — 提供独立 Windows 可执行文件，无需安装 Python
 - **Android 应用** — 独立 APK，Material Design 3 界面 + JNI 桥接，现已支持 3D 曲面绘图与触控旋转及参数曲线绘制

## 预编译二进制文件

预编译文件可在 [Releases](https://github.com/Hotsteel2901/SuperCalculator/releases) 中下载。

| 平台 | 架构 | 文件 | 预编译 |
|------|------|------|:---:|
| Windows | x64 | `calc_core.dll` / `SuperCalculator.exe` | 是 |
| Linux | x86_64 | `calc_core_x86_64.so` | 是 |
| Linux | ARM64 | `calc_core_aarch64.so` | 是 |
| macOS | x86_64 / ARM64 | `calc_core.dylib` | 需自行编译 |
| Android | ARM64 | `SuperCalculator-*.apk` | 是 (工作流) |

## 快速开始

### Windows（EXE — 无需 Python）

在 [Releases](https://github.com/Hotsteel2901/SuperCalculator/releases) 页面下载 `SuperCalculator.exe`，双击即可运行，保留命令行窗口用于输出与调试。

### Python 源码运行

```bash
pip install numpy matplotlib
python super_calc_bridged.py
```

## 环境要求

- **Python 3.9+** 并安装以下包：`numpy`、`matplotlib`
- **C 编译器**（如需从源码重新编译）：Windows 推荐 MinGW-w64，Linux 使用 GCC

## 从源码编译

### Windows (MinGW-w64 / MSYS2)

```bash
gcc -shared -O2 -o calc_core.dll calc_core.c -lm
```

### Windows (MSVC)

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

## 表达式语法

| 类别       | 运算符 / 函数                    | 示例                |
|-----------|----------------------------------|---------------------|
| 算术运算    | `+` `-` `*` `/` `^` (乘方)      | `x^2 + 2*x - 1`    |
| 三角函数    | `sin` `cos` `tan`               | `sin(x) + cos(x)`   |
| 对数/指数   | `ln` `log` `exp`                | `ln(x)` `exp(-x)`   |
| 根号/绝对值 | `sqrt` `abs`                    | `sqrt(x)` `abs(x)`  |
| 阶乘        | `!` (后置运算符)                 | `x!` `5!`           |
| 数学常数    | `pi` `e`                        | `sin(pi*x)`         |

## 文件结构

```
SuperCalculator/
  calc_core.c              C 核心引擎 (表达式解析、微积分、方程求解)
  calc_bridge.py           Python ctypes 桥接层 (多架构自动检测)
  super_calc_bridged.py    GUI 主程序 (Tkinter + Matplotlib)
  SuperCalculator.ico      Windows EXE 图标
  SuperCalculator.spec     PyInstaller 构建配置 (Windows EXE)
  android/                 Android 项目 (Gradle + JNI + M3 UI)
  .github/workflows/       CI: 多平台构建 + Android APK + Windows EXE
  README.md               英文说明文档
  README_CN.md            中文说明文档 (本文件)
  index.html               项目展示页面
```

## 更新日志

- **极限计算** — 支持左极限、右极限与双侧极限计算，采用 Richardson 外推法提高精度。桌面端（Python）与 Android 端（JNI）均已同步。
- **参数曲线绘图** — 支持以 x(t) 和 y(t) 定义的参数曲线，内置 10 种预设（圆、椭圆、李萨如图形、螺旋线、心形线、蝴蝶曲线等）。桌面端（Python）与 Android 端（JNI）均已同步。
- **傅里叶变换与频谱分析** — 支持 FFT 幅度谱与相位谱计算，自动识别主频分量，支持 CSV 导出。桌面端（Python）与 Android 端（DFT 实现）均已同步。
- **21 个预设函数** — 新增 FFT 演示表达式，一键体验频谱分析功能。

## CI / CD

GitHub Actions 工作流均需手动触发：

| 工作流 | 功能 | 推送 Release |
|--------|------|:---:|
| `Build All Platforms` | 构建 Win x64 DLL, Linux x86_64, Linux ARM64 | 可选 |
| `Build Android APK` | 构建 Android aarch64 APK | 否 |
| `Build Windows EXE` | 构建独立 Windows 可执行文件（含图标） | 可选 |

## API 参考

```python
from calc_bridge import CalcEngine

# 求值
CalcEngine.evaluate("x^2", 3.0)         # -> 9.0

# 二元函数求值
CalcEngine.evaluate_xy("x^2+y^2", 3.0, 4.0)  # -> 25.0

# 批量求值 (绘图用)
CalcEngine.evaluate_array("sin(x)", [0, 0.5, 1.0])

# 一阶导数
CalcEngine.derivative("x^3", 2.0)       # -> ~12.0 (f'(x)=3x^2)

# 二阶导数
CalcEngine.derivative2("x^3", 2.0)      # -> ~12.0 (f''(x)=6x)

# 定积分
CalcEngine.integrate_adaptive("x^2", 0, 1)  # -> ~0.333

# 方程求根
CalcEngine.solve("x^2 - 4", guess=1, xmin=0, xmax=3)  # -> 2.0

# 极值查找
CalcEngine.find_minimum("x^2", -5, 5)   # -> ~0.0
CalcEngine.find_maximum("sin(x)", 0, 6) # -> ~1.571

# 极限计算
CalcEngine.limit("sin(x)/x", 0)          # -> ~1.0
CalcEngine.limit_left("1/x", 0)          # -> -inf
CalcEngine.limit_right("1/x", 0)         # -> +inf

# 曲线交点（构造差值表达式后求解）
# 示例：求 sin(x) 与 cos(x) 在 [0, pi] 区间的交点
CalcEngine.solve_bisection("(sin(x))-(cos(x))", 0, 3.14)  # -> ~0.785

# 弧长计算
CalcEngine.arc_length("sin(x)", 0, 3.141592653589793)  # -> ~3.820

# 参数曲线求值
spec = CalcEngine.evaluate_parametric("cos(t)", "sin(t)", 0, 2*pi, 500)
# spec['xs'] -> x 值列表
# spec['ys'] -> y 值列表
# spec['ts'] -> t 值列表

# 傅里叶变换频谱
spec = CalcEngine.fft_spectrum("sin(2*pi*x)+0.5*sin(6*pi*x)", 0, 2, 1024)
# spec['freqs'] -> 频率列表
# spec['amps']  -> 幅度列表
# spec['phases']-> 相位列表（弧度）
```

## 数值方法

| 方法       | 算法                                | 误差      |
|-----------|-------------------------------------|----------|
| 一阶导数   | 中心差分: (f(x+h)-f(x-h)) / 2h     | O(h²)    |
| 二阶导数   | 中心差分: (f(x+h)-2f(x)+f(x-h)) / h² | O(h²)  |
| 定积分     | 自适应 Simpson 复合法则             | O(h⁴)    |
| 方程求根   | Newton-Raphson + 二分法回退         | —        |
| 极值查找   | 黄金分割搜索法                       | 线性收敛  |
| 极限计算   | Richardson 外推法                    | O(h²ᵏ)   |

## 设计说明

本项目采用**桥接模式(Bridge Pattern)**的核心思想：将抽象(GUI)与实现(计算引擎)分离，使两者可以独立变化。

- 更换 GUI 框架只需修改 `super_calc_bridged.py`，无需改动 C 核心
- 增强计算能力只需修改 `calc_core.c`，无需改动 GUI
- `calc_bridge.py` 作为桥接层，负责类型转换、错误处理和 API 封装
