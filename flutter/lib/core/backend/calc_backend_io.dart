import 'dart:ffi';
import 'dart:io';

import 'package:ffi/ffi.dart';

import '../compute/calculation_models.dart';
import '../compute/computation.dart';
import '../compute/computation_dispatcher.dart';
import 'calc_backend.dart';

CalcBackend createCalcBackend() {
  try {
    return FfiCalcBackend.open();
  } catch (_) {
    return const DartCalcBackend();
  }
}

typedef _AbiVersionNative = Int32 Function();
typedef _AbiVersion = int Function();
typedef _ContextCreateNative = Pointer<Void> Function();
typedef _ContextCreate = Pointer<Void> Function();
typedef _ContextDestroyNative = Void Function(Pointer<Void>);
typedef _ContextDestroy = void Function(Pointer<Void>);
typedef _EvaluateNative = Int32 Function(
  Pointer<Void>,
  Pointer<Utf8>,
  Double,
  Double,
  Pointer<Double>,
);
typedef _Evaluate = int Function(
  Pointer<Void>,
  Pointer<Utf8>,
  double,
  double,
  Pointer<Double>,
);
typedef _EvaluateArrayNative = Int32 Function(
  Pointer<Void>,
  Pointer<Utf8>,
  Pointer<Double>,
  Int32,
  Pointer<Double>,
);
typedef _EvaluateArray = int Function(
  Pointer<Void>,
  Pointer<Utf8>,
  Pointer<Double>,
  int,
  Pointer<Double>,
);
typedef _ScalarNative = Int32 Function(
  Pointer<Void>,
  Pointer<Utf8>,
  Double,
  Double,
  Pointer<Double>,
);
typedef _Scalar = int Function(
  Pointer<Void>,
  Pointer<Utf8>,
  double,
  double,
  Pointer<Double>,
);
typedef _IntegrateNative = Int32 Function(
  Pointer<Void>,
  Pointer<Utf8>,
  Double,
  Double,
  Double,
  Pointer<Double>,
);
typedef _Integrate = int Function(
  Pointer<Void>,
  Pointer<Utf8>,
  double,
  double,
  double,
  Pointer<Double>,
);
typedef _SolveNative = Int32 Function(
  Pointer<Void>,
  Pointer<Utf8>,
  Double,
  Double,
  Double,
  Double,
  Int32,
  Pointer<Double>,
);
typedef _Solve = int Function(
  Pointer<Void>,
  Pointer<Utf8>,
  double,
  double,
  double,
  double,
  int,
  Pointer<Double>,
);
typedef _OdeNative = Int32 Function(
  Pointer<Void>,
  Pointer<Utf8>,
  Double,
  Double,
  Double,
  Int32,
  Pointer<Double>,
  Pointer<Double>,
  Int32,
  Pointer<Int32>,
);
typedef _Ode = int Function(
  Pointer<Void>,
  Pointer<Utf8>,
  double,
  double,
  double,
  int,
  Pointer<Double>,
  Pointer<Double>,
  int,
  Pointer<Int32>,
);
typedef _LastErrorNative = Pointer<Utf8> Function(Pointer<Void>);
typedef _LastError = Pointer<Utf8> Function(Pointer<Void>);

class FfiCalcBackend implements CalcBackend {
  FfiCalcBackend._({required DynamicLibrary library, required this._context})
    : _evaluate = library.lookupFunction<_EvaluateNative, _Evaluate>(
        'sc_evaluate',
      ),
      _evaluateArray = library
          .lookupFunction<_EvaluateArrayNative, _EvaluateArray>(
            'sc_evaluate_array',
          ),
      _derivative = library.lookupFunction<_ScalarNative, _Scalar>(
        'sc_derivative',
      ),
      _derivative2 = library.lookupFunction<_ScalarNative, _Scalar>(
        'sc_derivative2',
      ),
      _integrate = library.lookupFunction<_IntegrateNative, _Integrate>(
        'sc_integrate',
      ),
      _solve = library.lookupFunction<_SolveNative, _Solve>('sc_solve'),
      _solveOde = library.lookupFunction<_OdeNative, _Ode>('sc_ode_rk4'),
      _destroy = library.lookupFunction<_ContextDestroyNative, _ContextDestroy>(
        'sc_context_destroy',
      ),
      _lastError = library.lookupFunction<_LastErrorNative, _LastError>(
        'sc_last_error',
      );

  final Pointer<Void> _context;
  final _Evaluate _evaluate;
  final _EvaluateArray _evaluateArray;
  final _Scalar _derivative;
  final _Scalar _derivative2;
  final _Integrate _integrate;
  final _Solve _solve;
  final _Ode _solveOde;
  final _ContextDestroy _destroy;
  final _LastError _lastError;
  bool _disposed = false;

  static FfiCalcBackend open() {
    final library = DynamicLibrary.open(_libraryName());
    final abiVersion = library.lookupFunction<_AbiVersionNative, _AbiVersion>(
      'sc_abi_version',
    )();
    if (abiVersion != 2) {
      throw StateError('Unsupported SuperCalculator native ABI: $abiVersion');
    }
    final create = library.lookupFunction<_ContextCreateNative, _ContextCreate>(
      'sc_context_create',
    );
    final context = create();
    if (context == nullptr) {
      throw StateError('Could not create native calculation context.');
    }
    return FfiCalcBackend._(library: library, context: context);
  }

  @override
  String get name => 'Native FFI';

  @override
  Future<CalcEvaluation> evaluate(
    String expression,
    double x, [
    double y = 0,
  ]) async {
    if (_disposed) {
      return _closedResult();
    }
    final expressionPointer = expression.toNativeUtf8();
    final output = calloc<Double>();
    try {
      final status = _evaluate(_context, expressionPointer, x, y, output);
      return _resultFromStatus(status, output.value);
    } finally {
      calloc.free(output);
      calloc.free(expressionPointer);
    }
  }

  @override
  Future<List<double?>> evaluateArray(
    String expression,
    List<double> xs,
  ) async {
    if (_disposed || xs.isEmpty) {
      return <double?>[];
    }
    final expressionPointer = expression.toNativeUtf8();
    final input = calloc<Double>(xs.length);
    final output = calloc<Double>(xs.length);
    try {
      input.asTypedList(xs.length).setAll(0, xs);
      final status = _evaluateArray(
        _context,
        expressionPointer,
        input,
        xs.length,
        output,
      );
      if (status != 0) {
        return List<double?>.filled(xs.length, null);
      }
      return output
          .asTypedList(xs.length)
          .map<double?>((value) => value.isFinite ? value : null)
          .toList(growable: false);
    } finally {
      calloc.free(input);
      calloc.free(output);
      calloc.free(expressionPointer);
    }
  }

  @override
  Future<CalcEvaluation> derivative(
    String expression,
    double x, {
    double? step,
    bool second = false,
  }) async {
    if (_disposed) {
      return _closedResult();
    }
    return _callScalar(
      expression,
      x,
      step ?? 1e-6 * (x.abs() + 1),
      second ? _derivative2 : _derivative,
    );
  }

  @override
  Future<CalcEvaluation> integrate(
    String expression,
    double a,
    double b, {
    double tolerance = 1e-8,
  }) async {
    if (_disposed) {
      return _closedResult();
    }
    final expressionPointer = expression.toNativeUtf8();
    final output = calloc<Double>();
    try {
      final status = _integrate(
        _context,
        expressionPointer,
        a,
        b,
        tolerance,
        output,
      );
      return _resultFromStatus(status, output.value);
    } finally {
      calloc.free(output);
      calloc.free(expressionPointer);
    }
  }

  @override
  Future<CalcEvaluation> limit(
    String expression,
    double point, {
    double tolerance = 1e-8,
    int maxLevel = 10,
    String side = 'two-sided',
  }) async {
    try {
      final value = await ComputationDispatcher.limit(
        expression,
        point,
        tolerance: tolerance,
        maxLevel: maxLevel,
        side: side,
      );
      return value == null
          ? CalcEvaluation.failure(
              backend: name,
              message: 'The limit does not exist or is not finite.',
            )
          : CalcEvaluation(value: value, backend: name);
    } on FormatException catch (error) {
      return CalcEvaluation.failure(backend: name, message: error.message);
    }
  }

  @override
  Future<CalcEvaluation> nthDerivative(
    String expression,
    double point,
    int order, {
    double step = 1e-4,
  }) async {
    try {
      final value = await ComputationDispatcher.nthDerivative(
        expression,
        point,
        order,
        step: step,
      );
      return value == null
          ? CalcEvaluation.failure(
              backend: name,
              message: 'The derivative could not be evaluated.',
            )
          : CalcEvaluation(value: value, backend: name);
    } on FormatException catch (error) {
      return CalcEvaluation.failure(backend: name, message: error.message);
    }
  }

  @override
  Future<CalcEvaluation> extremum(
    String expression,
    double start,
    double end, {
    bool minimum = true,
    double tolerance = 1e-8,
  }) async {
    try {
      final value = await ComputationDispatcher.extremum(
        expression,
        start,
        end,
        minimum: minimum,
        tolerance: tolerance,
      );
      return value == null
          ? CalcEvaluation.failure(
              backend: name,
              message: 'No finite extremum was found in the interval.',
            )
          : CalcEvaluation(value: value, backend: name);
    } on FormatException catch (error) {
      return CalcEvaluation.failure(backend: name, message: error.message);
    }
  }

  @override
  Future<CalcEvaluation> areaBetweenCurves(
    String expressionF,
    String expressionG,
    double start,
    double end, {
    double tolerance = 1e-8,
  }) async {
    try {
      final value = await ComputationDispatcher.areaBetweenCurves(
        expressionF,
        expressionG,
        start,
        end,
        tolerance: tolerance,
      );
      return value == null
          ? CalcEvaluation.failure(
              backend: name,
              message: 'The area could not be evaluated.',
            )
          : CalcEvaluation(value: value, backend: name);
    } on FormatException catch (error) {
      return CalcEvaluation.failure(backend: name, message: error.message);
    }
  }

  @override
  Future<CalcEvaluation> solve(
    String expression, {
    double guess = 0,
    double minimum = -100,
    double maximum = 100,
    double tolerance = 1e-10,
    int maxIterations = 100,
  }) async {
    if (_disposed) {
      return _closedResult();
    }
    final expressionPointer = expression.toNativeUtf8();
    final output = calloc<Double>();
    try {
      final status = _solve(
        _context,
        expressionPointer,
        guess,
        minimum,
        maximum,
        tolerance,
        maxIterations,
        output,
      );
      return _resultFromStatus(status, output.value);
    } finally {
      calloc.free(output);
      calloc.free(expressionPointer);
    }
  }

  @override
  Future<CalcOdeSolution> solveOde(
    String expression, {
    required double x0,
    required double y0,
    required double xEnd,
    int steps = 200,
  }) async {
    if (_disposed || steps < 1) {
      return const CalcOdeSolution(
        xs: <double>[],
        ys: <double?>[],
        method: 'RK4',
      );
    }
    final expressionPointer = expression.toNativeUtf8();
    final xs = calloc<Double>(steps + 1);
    final ys = calloc<Double>(steps + 1);
    final count = calloc<Int32>();
    try {
      final status = _solveOde(
        _context,
        expressionPointer,
        x0,
        y0,
        xEnd,
        steps,
        xs,
        ys,
        steps + 1,
        count,
      );
      if (status != 0 || count.value <= 0) {
        return const CalcOdeSolution(
          xs: <double>[],
          ys: <double?>[],
          method: 'RK4',
        );
      }
      final length = count.value.clamp(0, steps + 1).toInt();
      return CalcOdeSolution(
        xs: xs.asTypedList(length).toList(growable: false),
        ys: ys
            .asTypedList(length)
            .map<double?>((value) => value.isFinite ? value : null)
            .toList(growable: false),
        method: 'RK4 · Native FFI',
      );
    } finally {
      calloc.free(count);
      calloc.free(xs);
      calloc.free(ys);
      calloc.free(expressionPointer);
    }
  }

  @override
  Future<CalcSpectrum> spectrum(
    String expression, {
    required double a,
    required double b,
    int samples = 1024,
  }) =>
      ComputationDispatcher.spectrum(expression, a: a, b: b, samples: samples);

  @override
  Future<CalcStatistics> statistics(List<double> values) =>
      ComputationDispatcher.statistics(values);

  @override
  Future<CalcRegression> linearRegression(List<double> xs, List<double> ys) =>
      ComputationDispatcher.linearRegression(xs, ys);

  @override
  Future<CalcMatrix> parseMatrix(String input) async =>
      DartComputation.parseMatrix(input);

  @override
  Future<CalcMatrix> multiplyMatrices(String left, String right) async =>
      DartComputation.matrixMultiply(
        DartComputation.parseMatrix(left),
        DartComputation.parseMatrix(right),
      );

  @override
  Future<double> determinant(String input) async =>
      DartComputation.matrixDeterminant(DartComputation.parseMatrix(input));

  @override
  Future<CalcMatrix> inverseMatrix(String input) async =>
      DartComputation.matrixInverse(DartComputation.parseMatrix(input));

  Future<CalcEvaluation> _callScalar(
    String expression,
    double x,
    double y,
    _Scalar function,
  ) async {
    final expressionPointer = expression.toNativeUtf8();
    final output = calloc<Double>();
    try {
      final status = function(_context, expressionPointer, x, y, output);
      return _resultFromStatus(status, output.value);
    } finally {
      calloc.free(output);
      calloc.free(expressionPointer);
    }
  }

  CalcEvaluation _resultFromStatus(int status, double value) {
    if (status == 0 && value.isFinite) {
      return CalcEvaluation(value: value, backend: name);
    }
    return CalcEvaluation.failure(backend: name, message: _readLastError());
  }

  CalcEvaluation _closedResult() => const CalcEvaluation.failure(
    backend: 'Native FFI',
    message: 'Backend is closed.',
  );

  String _readLastError() {
    final pointer = _lastError(_context);
    return pointer == nullptr
        ? 'Native calculation failed.'
        : pointer.toDartString();
  }

  @override
  void dispose() {
    if (_disposed) {
      return;
    }
    _disposed = true;
    _destroy(_context);
  }

  static String _libraryName() {
    if (Platform.isAndroid) {
      return 'libsupercalc_core.so';
    }
    if (Platform.isWindows) {
      return 'supercalc_core.dll';
    }
    if (Platform.isMacOS || Platform.isIOS) {
      return 'libsupercalc_core.dylib';
    }
    if (Platform.isLinux) {
      return 'libsupercalc_core.so';
    }
    throw UnsupportedError('Native FFI is not configured for this platform.');
  }
}
