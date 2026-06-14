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
- **极坐标绘图** — 支持以 r(theta) 定义的极坐标曲线，内置 12 种预设（心形线、玫瑰线、三叶草、螺旋线、双纽线等）
- **隐函数绘图** — 支持绘制 f(x,y)=0 形式的隐函数方程（如圆、椭圆、双曲线、心形线、双纽线、笛卡尔叶形线等），基于等高线渲染，内置 8 种预设，支持自定义分辨率
- **多曲线叠加** — 同时绘制多条函数曲线，自动分配不同颜色
- **数值微分** — 一阶导数 f'(x) 和二阶导数 f''(x)，采用中心差分法
- **数值积分** — 定积分计算，采用自适应 Simpson 复合法则
- **方程求解** — Newton-Raphson 法（二分法回退）+ 纯二分法
- **非线性方程组求解 (2D)** — 求解两个未知数的非线性方程组 f(x,y)=0, g(x,y)=0，采用 Newton 法配合数值雅可比矩阵与克莱默法则，桌面端（Python）与 Android 端（JNI）均已同步
- **极值查找** — 黄金分割搜索法，在指定区间内寻找局部最小值与最大值
- **极限计算** — 左极限、右极限与双侧极限，采用 Richardson 外推法提高精度
 - **零点自动扫描** — 在指定区间内自动扫描函数的所有零点，符号变化检测 + 二分法精确定位
 - **曲线交点查找** — 在任意两条 2D 曲线之间查找所有交点，符号变化检测 + 二分法精确定位，结果自动标注在图上
 - **切线与法线绘制** — 在 2D 曲线任意点处一键绘制切线与法线，以虚线形式直观标注在图上，便于分析函数局部特征
 - **弧长计算** — 在任意区间上通过自适应弦长累加法逼近曲线弧长
  - **曲线间面积** — 使用自适应辛普森法则计算任意两条曲线 f(x) 和 g(x) 在 [a,b] 上的封闭面积
  - **傅里叶变换与频谱分析** — 对任意函数进行 FFT 频谱分析，自动识别主频分量，绘制幅度谱与相位谱，支持 CSV 导出
  - **泰勒级数展开** — 将任意函数在指定点展开为泰勒多项式，支持自定义阶数、系数展示以及泰勒近似与原函数对比绘图
  - **预设函数** — 内置 21 个常用函数（含 3D 与 FFT 预设）+ 10 个参数曲线预设，一键选择
    - **ODE 求解器 (RK4)** — 使用四阶 Runge-Kutta 方法求解一阶常微分方程初值问题，支持自定义步数与解曲线绘制
    - **ODE 数值方法对比** — 对比不同数值方法（欧拉法、改进欧拉法、中点法、RK4、RKF45）在同一 ODE 问题上的求解结果，叠加绘制解曲线以直观展示精度与收敛性差异。桌面端（Python）、Android 端（Java）及项目主页交互式网页演示均已支持。
    - **方向场绘制** — 可视化 ODE dy/dx = f(x,y) 的方向场（矢量场），在每个点绘制方向箭头，支持叠加多条从不同初始条件出发的解曲线，内置 8 种预设（指数衰减、逻辑斯蒂增长、简谐运动、Van der Pol、Lotka-Volterra 等）。桌面端（Python）已支持。
    - **自定义函数定义** — 定义用户命名函数如 `f(x) = x^2 + 1`，可在任意表达式中引用 `f(expr)`，支持任意嵌套和组合。全平台支持（C 核心、Android、Python、Web）。
    - **计算历史** — 自动记录最近 10 次计算（表达式与结果），Android 端通过 SharedPreferences 持久化存储。支持清空历史记录和获取上次表达式。全平台支持（C 核心、JNI、Java、Python）。
   - **统计计算器** — 计算均值、中位数、众数、方差、标准差、四分位数 (Q1/Q3/IQR)、最小值、最大值、极差；支持数据排序、直方图可视化与 CSV 导出
  - **矩阵运算（线性代数）** — 支持矩阵加法、减法、乘法、行列式、逆矩阵、转置、秩、行最简形（RREF）及特征值计算；输入格式：行用 `;` 分隔，列用 `,` 分隔（如 `1,2;3,4` 表示 2×2 矩阵）
  - **参数系统** — 自动检测表达式中的额外参数（如 `a`、`b`），动态生成输入框实时调节
  - **坐标标记** — 左键点击图表标记坐标点，右键点击删除已标之点，或输入 x 值自动定位
 - **快速输入面板** — 弹出式快捷按钮面板，一键输入运算符、函数与常数
 - **阶乘支持** — 后置运算符 `!`，支持非负整数阶乘
 - **取整与取模运算** — 内置 `floor(x)`、`ceil(x)` 取整函数和 `mod`（或 `%`）取模运算符
 - **自定义视图** — X/Y/Z 坐标范围、采样步长、网格开关均可调节
 - **交互式图表** — Matplotlib 工具栏支持缩放、平移、导出 PNG
  - **函数数据表与 CSV 导出** — 在任意区间一键生成 x-f(x) 数据表格，支持导出为 CSV 或复制到剪贴板
  - **FFT 频谱导出** — 将频率、幅度与相位数据导出为 CSV，便于外部分析
   - **复数计算器** — 支持复数四则运算（+、-、*、/、^）、三角函数（sin、cos、tan）、指数、对数、平方根、绝对值与共轭运算。桌面端（Python）与 Android 端（JNI）均已同步。
    - **单位转换器** — 支持不同单位之间的转换，包括长度、重量、温度、面积、体积、时间、数据存储、速度和角度等 9 个单位类别，提供全面的转换因子。
     - **曲线拟合 / 回归分析** — 支持多种数据拟合模型：线性 (y=ax+b)、多项式（可配置阶数）、指数 (y=ae^(bx))、幂函数 (y=ax^b) 和对数 (y=a+b·ln(x))。显示方程、R² 拟合优度、散点图 + 拟合曲线可视化。桌面端（Python/numpy）与 Android 端（Java）均已同步。
     - **CSV 数据导入与散点图** — 支持导入 CSV/TSV 数据文件，可配置分隔符（逗号、制表符、分号、空格）和列选择。支持绘制散点图、折线图和柱状图。支持趋势线拟合（线性、二次、指数），显示 R² 拟合优度。支持导出图表为 PNG。桌面端（Python）与 Android 端（Java）均已同步。项目主页提供交互式网页演示。
     - **统计分布计算器** — 计算 6 种常见概率分布的 PDF/PMF、CDF 和 PPF（逆 CDF）：正态分布（高斯）、学生 t 分布、卡方分布、F 分布、二项分布和泊松分布。支持参数化输入、分布绘图和多参数对比可视化。桌面端（Python）与 Android 端（Java）均已同步。
     - **数论计算器** — 支持整数因式分解、素数判定（试除法）、最大公约数/最小公倍数、Fibonacci 数列、模幂运算（快速二进制幂）和欧拉函数 φ(n)。桌面端（Python）与 Android 端（Java）均已同步。
     - **进制转换器** — 支持二进制（2）、八进制（8）、十进制（10）、十六进制（16）以及 2-36 任意进制之间的数字转换。支持同时显示所有常用进制的转换结果，支持负数。项目主页提供交互式网页演示。桌面端（Python）与 Android 端（Java）均已同步。
     - **位运算计算器** — 支持 AND、OR、XOR、NOT、左移（<<）、右移（>>）运算，可配置位宽（8/16/32），实时显示二进制、八进制、十进制和十六进制结果。项目主页提供交互式二进制位图演示。桌面端（Python）与 Android 端（Java）均已同步。
      - **万年历** — 查询任意日期（YYYY-MM-DD）是星期几，计算两个日期之间的精确天数差，以及对任意日期加减指定天数。支持公元 1 年至 9999 年的日期。桌面端（Python）与 Android 端（Java）均已同步。
      - **概率计算器** — 计算组合数 C(n,r)、排列数 P(n,r)、事件概率（并集 P(A∪B)、交集 P(A∩B)、补集 P(A')）、条件概率 P(A|B)、贝叶斯定理及完整后验概率计算、二项分布 P(X=k) 及均值/方差。项目主页提供交互式网页演示。桌面端（Python）与 Android 端（Java）均已同步。
      - **金融计算器** — 贷款月供/总利息计算、复利终值/现值、NPV/IRR 投资分析、直线折旧与双倍余额递减折旧、债券定价、退休储蓄规划。桌面端（Python）、Android 端（Java）及项目主页交互式网页演示均已支持。
      - **旋转体体积计算器** — 使用三种方法计算旋转体体积：圆盘法 (V = π∫[f(x)]²dx)、垫圈法 (V = π∫([f(x)]²-[g(x)]²)dx) 和壳法 (V = 2π∫x·f(x)dx)。内置预设示例（球体、圆锥、圆柱、圆环）。桌面端（Python）、Android 端（Java）及项目主页交互式网页演示均已支持。
      - **数据插值计算器** — 支持四种插值方法：线性插值、拉格朗日多项式插值、牛顿多项式插值和三次样条插值。可在任意 x 值处求值，可视化插值曲线与数据点。项目主页提供交互式网页演示。桌面端（Python）、Android 端（Java）及项目主页均已支持。
    - **Windows EXE** — 提供独立 Windows 可执行文件，无需安装 Python
 - **Android 应用** — 独立 APK，Material Design 3 界面 + JNI 桥接，现已支持 3D 曲面绘图与触控旋转及参数曲线绘制
 - **中文语言支持** — 桌面端（Python）与 Android 端均支持完整中文 (zh-CN) 本地化。桌面端自动检测系统语言或通过环境变量 `SUPERCALC_LANG=zh` 指定。Android 端跟随系统语言自动切换。

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

## 📖 使用教程

**第一次使用？** 查看我们详细的保姆级教程：

- **[中文使用教程](docs/usage_cn.md)** — 涵盖所有功能的详细使用方法，从安装到高级操作
- **[English Usage Guide](docs/usage_en.md)** — Comprehensive tutorial covering all features, from installation to advanced usage

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
| 取模运算    | `mod` `%` (取余)                 | `10 mod 3`, `7%2`   |
| 取整函数    | `floor` `ceil`                   | `floor(x)` `ceil(x)` |
| 三角函数    | `sin` `cos` `tan`               | `sin(x) + cos(x)`   |
| 对数/指数   | `ln` `log` `exp`                | `ln(x)` `exp(-x)`   |
| 根号/绝对值 | `sqrt` `abs`                    | `sqrt(x)` `abs(x)`  |
| 阶乘        | `!` (后置运算符)                 | `x!` `5!`           |
| 数学常数    | `pi` `e`                        | `sin(pi*x)`         |
| 复数        | `i` (虚数单位)                   | `1+2i`, `3-4i`      |

## 文件结构

```
SuperCalculator/
  calc_core.c              C 核心引擎 (表达式解析、微积分、方程求解)
  calc_bridge.py           Python ctypes 桥接层 (多架构自动检测)
  super_calc_bridged.py    GUI 主程序 (Tkinter + Matplotlib)
  locale_strings.py        国际化模块 (英文 + 中文，自动语言检测)
  stat_dist.py             统计分布计算器 (正态、t、卡方、F、二项、泊松分布)
  probability_calc.py      概率计算器 (组合、排列、贝叶斯、二项分布)
  SuperCalculator.ico      Windows EXE 图标
  SuperCalculator.spec     PyInstaller 构建配置 (Windows EXE)
  android/                 Android 项目 (Gradle + JNI + M3 UI)
  .github/workflows/       CI: 多平台构建 + Android APK + Windows EXE
  README.md               英文说明文档
  README_CN.md            中文说明文档 (本文件)
  index.html               项目展示页面
```

## 更新日志

- **概率计算器** — 计算组合数 C(n,r)、排列数 P(n,r)、事件概率（并集 P(A∪B)、交集 P(A∩B)、补集 P(A')）、条件概率 P(A|B)、贝叶斯定理及完整后验概率计算、二项分布 P(X=k) 及均值/方差。项目主页提供交互式网页演示。桌面端（Python）与 Android 端（Java）均已同步。
- **位运算计算器** — 支持 AND、OR、XOR、NOT、左移（<<）、右移（>>）运算，可配置位宽（8/16/32），实时显示二进制、八进制、十进制和十六进制结果。项目主页提供交互式二进制位图演示。桌面端（Python）与 Android 端（Java）均已同步。
- **进制转换器** — 支持二进制、八进制、十进制与十六进制之间的数字转换，同时支持 2-36 任意进制。支持同时显示所有常用进制的转换结果，支持负数，项目主页提供交互式网页演示。桌面端（Python）与 Android 端（Java）均已同步。
- **万年历** — 查询任意日期是星期几，计算两个日期之间的精确天数差，以及对任意日期加减指定天数。支持公元 1 年至 9999 年。桌面端（Python）与 Android 端（Java）均已同步。
- **统计分布计算器** — 计算 6 种常见概率分布的 PDF/PMF、CDF 和 PPF（逆 CDF）：正态分布（高斯）、学生 t 分布、卡方分布、F 分布、二项分布和泊松分布。支持参数化输入、分布绘图和多参数对比可视化。桌面端（Python）与 Android 端（Java）均已同步。
- **中文语言支持** — 桌面端与 Android 端均支持完整中文 (zh-CN) 本地化。桌面端使用 `locale_strings.py` 模块，自动检测系统语言（或通过 `SUPERCALC_LANG` 环境变量指定）。Android 端使用标准 `values-zh-rCN/` 字符串资源，跟随系统语言自动切换。所有界面标签、按钮、错误提示和对话框文本均已翻译。
- **曲线拟合 / 回归分析** — 支持线性、多项式、指数、幂函数和对数拟合模型，显示方程与 R² 拟合优度，支持散点图 + 拟合曲线可视化。桌面端（Python/numpy）与 Android 端（Java）均已同步。
- **CSV 数据导入与散点图** — 支持导入 CSV/TSV 数据文件，可配置分隔符和列选择。支持绘制散点图、折线图和柱状图。支持趋势线拟合（线性、二次、指数），显示 R² 拟合优度。桌面端（Python）与 Android 端（Java）均已同步。项目主页提供交互式网页演示。
- **非线性方程组求解 (2D)** — 求解两个未知数的非线性方程组 f(x,y)=0, g(x,y)=0，采用 Newton 法配合数值雅可比矩阵与克莱默法则。桌面端（Python）与 Android 端（JNI）均已同步。
- **曲线间面积** — 使用自适应辛普森法则计算任意两条曲线 f(x) 和 g(x) 在区间 [a,b] 上的封闭面积。桌面端（Python）与 Android 端（JNI）均已同步。
- **复数计算器** — 支持复数四则运算（+、-、*、/、^）、三角函数（sin、cos、tan）、指数、对数、平方根、绝对值与共轭运算。输入格式：`a+bi`（如 `1+2i`、`3-4i`）。桌面端（Python）与 Android 端（JNI）均已同步。
- **矩阵运算（线性代数）** — 支持矩阵加法、减法、乘法、行列式、逆矩阵、转置、秩、行最简形（RREF）及特征值计算。输入格式：行用 `;` 分隔，列用 `,` 分隔（如 `1,2;3,4` 表示 2×2 矩阵）。桌面端（Python/numpy）与 Android 端（Java）均已同步。
- **ODE 求解器 (RK4)** — 使用四阶 Runge-Kutta 方法求解一阶常微分方程初值问题 dy/dx = f(x,y)，支持自定义步数与解曲线绘制。桌面端（Python）与 Android 端（JNI）均已同步。
- **方向场绘制** — 可视化 ODE dy/dx = f(x,y) 的方向场（矢量场），在每个点绘制方向箭头，支持叠加多条从不同初始条件出发的解曲线。内置 8 种预设（指数衰减、逻辑斯蒂增长、简谐运动、Van der Pol、Lotka-Volterra 等）。桌面端（Python）已支持。
- **泰勒级数展开** — 将任意函数在指定点展开为泰勒多项式，支持自定义阶数，展示系数、多项式表达式，并可将泰勒近似与原函数进行对比绘图。桌面端（Python）与 Android 端（JNI）均已同步。
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

# 曲线间面积
CalcEngine.area_between_curves("sin(x)", "0", 0, 3.141592653589793)  # -> 2.0
CalcEngine.area_between_curves("x^2", "x", 0, 1)  # -> ~0.1667

# 非线性方程组求解 (2D)
result = CalcEngine.solve_system_2d("x^2+y^2-1", "x-y", x0=0.7, y0=0.7)
# result -> {'x': 0.7071..., 'y': 0.7071...} (单位圆与 y=x 的交点)

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

# 泰勒级数
coeffs = CalcEngine.taylor_coefficients("sin(x)", 0, 6)  # c_k = f^(k)(0)/k!
# coeffs -> [0, 1, 0, -0.1667, 0, 0.00833, 0]

# 求值泰勒多项式
taylor_val = CalcEngine.taylor_evaluate("sin(x)", 0, 0.5, 8)  # ~0.4794

# n 阶导数
d5 = CalcEngine.nth_derivative("sin(x)", 1.0, 5)  # sin 在 x=1 处的 5 阶导数

# ODE 求解器 (RK4)
result = CalcEngine.ode_solve_rk4("-y", x0=0, y0=1, x_end=5, n_steps=200)
# result['xs'] -> x 值列表
# result['ys'] -> y 值列表

# 复数运算
z1 = complex(1, 2)  # 1+2i
z2 = complex(3, 4)  # 3+4i
result = CalcEngine.complex_add(z1, z2)  # (4+6j)
result = CalcEngine.complex_mul(z1, z2)  # (-5+10j)
result = CalcEngine.complex_sin(z1)      # sin(1+2i)
result = CalcEngine.complex_exp(z1)      # exp(1+2i)
result = CalcEngine.complex_abs(z1)      # |1+2i| = 2.236...
result = CalcEngine.complex_conj(z1)     # conj(1+2i) = (1-2j)

# 矩阵运算（使用 numpy）
import numpy as np
A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])
A + B              # 矩阵加法
A - B              # 矩阵减法
A @ B              # 矩阵乘法
np.linalg.det(A)   # 行列式
np.linalg.inv(A)   # 逆矩阵
A.T                # 转置
np.linalg.matrix_rank(A)  # 秩
np.linalg.eig(A)   # 特征值和特征向量

# 曲线拟合 / 回归分析
result = CalcEngine.linear_regression([1,2,3,4,5], [2,4,5,4,5])
# result -> {'slope': ..., 'intercept': ..., 'r_squared': ..., 'equation': '...', 'xs_fit': [...], 'ys_fit': [...]}

result = CalcEngine.polynomial_regression(xs, ys, degree=3)
# result -> {'coeffs': [...], 'r_squared': ..., 'equation': '...', 'xs_fit': [...], 'ys_fit': [...]}

result = CalcEngine.exponential_regression(xs, ys)
# result -> {'a': ..., 'b': ..., 'r_squared': ..., 'equation': '...', 'xs_fit': [...], 'ys_fit': [...]}

result = CalcEngine.power_regression(xs, ys)
# result -> {'a': ..., 'b': ..., 'r_squared': ..., 'equation': '...', 'xs_fit': [...], 'ys_fit': [...]}

result = CalcEngine.logarithmic_regression(xs, ys)
# result -> {'a': ..., 'b': ..., 'r_squared': ..., 'equation': '...', 'xs_fit': [...], 'ys_fit': [...]}

# 进制转换
result = CalcEngine.convert_base("FF", 16, 10)    # -> "255"
result = CalcEngine.convert_base("255", 10, 2)     # -> "11111111"
result = CalcEngine.convert_base_all("255", 10)     # -> {'bin': '11111111', 'oct': '377', 'dec': '255', 'hex': 'FF'}
value = CalcEngine.base_to_long("FF", 16)           # -> 255
result = CalcEngine.long_to_base(255, 16)           # -> "FF"
```

## 数值方法

| 方法       | 算法                                | 误差      |
|-----------|-------------------------------------|----------|
| 一阶导数   | 中心差分: (f(x+h)-f(x-h)) / 2h     | O(h²)    |
| 二阶导数   | 中心差分: (f(x+h)-2f(x)+f(x-h)) / h² | O(h²)  |
| n 阶导数   | 递归中心差分                        | O(h²)    |
| 泰勒系数   | n 阶导数 / k! 递归中心差分          | O(h²)    |
| 定积分     | 自适应 Simpson 复合法则             | O(h⁴)    |
| 方程求根   | Newton-Raphson + 二分法回退         | —        |
| 方程组求解 (2D) | Newton 法 + 数值雅可比矩阵 + 克莱默法则 | —    |
| 极值查找   | 黄金分割搜索法                       | 线性收敛  |
| 极限计算   | Richardson 外推法                    | O(h²ᵏ)   |
| ODE 求解   | 四阶 Runge-Kutta (RK4)              | O(h⁴)    |
| 线性回归   | 最小二乘法（闭式解）                   | —        |
| 多项式回归 | 最小二乘法（正规方程 / Vandermonde）    | —        |
| 指数/幂/对数回归 | 线性化最小二乘法                   | —        |

## 设计说明

本项目采用**桥接模式(Bridge Pattern)**的核心思想：将抽象(GUI)与实现(计算引擎)分离，使两者可以独立变化。

- 更换 GUI 框架只需修改 `super_calc_bridged.py`，无需改动 C 核心
- 增强计算能力只需修改 `calc_core.c`，无需改动 GUI
- `calc_bridge.py` 作为桥接层，负责类型转换、错误处理和 API 封装
