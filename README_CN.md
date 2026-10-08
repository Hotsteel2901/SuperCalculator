# SuperCalculator - Next Era

SuperCalculator 正在迁移为一个统一的、空安全的 Flutter 应用，并通过可替换的
计算后端复用现有计算核心。项目名、窗口标题、关于页和包元数据统一为
**SuperCalculator - Next Era**。

> **迁移事实：** Flutter 工作台是唯一新增的主界面。完整的旧版功能清单位于
> [`docs/migration/feature-manifest.json`](docs/migration/feature-manifest.json)。
> `implemented`、`partial` 和 `planned` 是有明确验收边界的状态；没有任何旧功能
> 会在没有说明的情况下被宣称已经迁移。

## Flutter 工作台已交付内容

- Material 3 Expressive 兼容的主题 token、明暗主题、减少动态效果处理、响应式
  NavigationRail/NavigationBar 布局，以及英文/简体中文本地化。
- Riverpod 状态管理、go_router 路由和 `CalcBackend` 可替换后端契约。有可用 ABI
  动态库时优先使用 `dart:ffi`；Web 和不支持 FFI 的目标使用确定性的 Dart fallback。
- 表达式计算、函数和多曲线绘图、参数/极坐标/隐式采样、曲面/等高线/方向场/向量
  场预览、微积分、方程、ODE 五种方法（Euler、Improved-Euler/Heun、Midpoint、
  RK4、RKF45）、FFT/卷积、带直方图的统计、回归/插值、稠密矩阵、复数、分布、
  数论、进制/单位、金融、自定义函数、函数表和会话历史。
- 数值 golden vectors、边界/错误处理、原生 C ABI 冒烟测试，以及覆盖格式化、
  analyzer、测试和 Web release build 的 GitHub Actions 检查。

当计算核心已经存在但旧版预设、导出格式、交互式 3D 渲染或平台安装包尚未完成时，
功能仍会标记为 `partial`。具体边界以清单为准。

## 快速开始

```bash
cd flutter
flutter pub get
flutter gen-l10n
flutter run -d chrome
flutter analyze
flutter test
```

CI 会核对 Flutter stable 基线，并执行格式化、analyzer、测试和 Web 构建。若当前
迁移环境没有 Flutter 可执行文件，应以 GitHub Actions 结果为准，不要把未执行的本地
检查写成已通过。

在仓库根目录构建并冒烟测试保留的 C 核心：

```bash
./tool/build_native.sh
```

脚本会构建版本化 C ABI v2，并验证标量、数组、错误、微积分、求根和 RK4 vectors。
Web 开发不要求存在原生动态库；后端会在不改变功能契约的情况下 fallback。

## 架构

```text
功能页面
  └── Riverpod controller + go_router
        └── CalcBackend（可替换契约）
              ├── dart:ffi → C ABI v2 动态库
              └── Dart AST/isolate fallback → Web 和不支持目标
```

耗时的 Dart fallback 通过 `ComputationDispatcher` 执行；绘图限制采样量，非有限值
会形成断点，渲染由独立的 `CustomPainter` 负责。Flutter 主界面不再使用 Python
Tkinter 或 Matplotlib。迁移回滚期间仍保留 Python 文件作为旧版参考、脚本或 parity/
构建工具，但不会在第二套 UI 中新增功能。

## 功能对照与原 README 功能

原 README 和使用教程仍然属于迁移清单。每项功能都有 ID、优先级、旧版来源和状态：

- 绘图：函数、多曲线、参数曲线、极坐标、隐式曲线、曲面、等高线、方向场和向量场；
- 微积分与方程：导数、积分、极限、Taylor、弧长、面积/体积、求根、方程组、极值、
  交点和切线/法线；
- ODE 与信号：五种 ODE 方法、方向场、FFT/频谱和卷积；
- 数据与统计：描述统计、直方图、五种回归、六种插值，以及 CSV/TSV 文本输入；
  - 线性代数：稠密矩阵运算、RREF/秩/特征值，以及稀疏 COO/SpMV/共轭梯度工作流；
- 高级工具：复数、六种分布、数论、进制和位运算、九类单位、金融和自定义函数；
- 应用流程：函数表、可复制 CSV、快捷预设、历史记录和国际化；
- 平台与发布：Android、iOS、Windows、Linux、macOS 和 Web 验收门禁。

Flutter UI 是迁移目标。旧 Python/Android/Web 入口在 parity 签收前保留为回滚/对照
参考；不应在第二套 UI 中继续新增功能。

## 验证与发布文档

- [`docs/migration/golden_vectors.json`](docs/migration/golden_vectors.json)：跨后端
  数值契约。
- [`docs/reports/m1-validation.md`](docs/reports/m1-validation.md)：CI/原生验证及
  尚未测量的真机门禁。
- [`docs/performance.md`](docs/performance.md)：帧率、isolate、内存和采样目标；不编造
  真机数字。
- [`docs/compatibility.md`](docs/compatibility.md)：平台矩阵和 FFI 打包门禁。
- [`docs/accessibility.md`](docs/accessibility.md)：键盘、鼠标/触控/手写笔、大字体、
  减少动态效果和读屏验收矩阵。
- [`docs/design-system.md`](docs/design-system.md) 与 [`docs/ffi.md`](docs/ffi.md)：
  M3 Expressive token/组件和原生边界说明。
- [`docs/release-notes.md`](docs/release-notes.md)：本轮增量与已知缺口。

## 安全迁移与回滚

每个迁移增量都应可追加、可验证、可回滚。Flutter 验证期间保留 C 核心、旧版源码、
ABI 冒烟脚本和功能清单。如果需要撤回 Flutter 路由或 backend adapter，只撤回对应
路由/适配器改动并继续使用原入口，不删除旧计算实现。详见
[`docs/rollback.md`](docs/rollback.md)。

## 贡献约定

数值改动必须有确定性 vectors，验证有限值和错误边界；新增依赖或平台假设必须在合并
前记录。
