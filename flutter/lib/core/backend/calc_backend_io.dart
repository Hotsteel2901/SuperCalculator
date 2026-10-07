import 'dart:ffi';
import 'dart:io';

import 'package:ffi/ffi.dart';

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
typedef _LastErrorNative = Pointer<Utf8> Function(Pointer<Void>);
typedef _LastError = Pointer<Utf8> Function(Pointer<Void>);

class FfiCalcBackend implements CalcBackend {
  FfiCalcBackend._({required DynamicLibrary library, required Pointer<Void> context})
      : _context = context,
        _evaluate = library.lookupFunction<_EvaluateNative, _Evaluate>('sc_evaluate'),
        _evaluateArray = library.lookupFunction<_EvaluateArrayNative, _EvaluateArray>('sc_evaluate_array'),
        _destroy = library.lookupFunction<_ContextDestroyNative, _ContextDestroy>('sc_context_destroy'),
        _lastError = library.lookupFunction<_LastErrorNative, _LastError>('sc_last_error');

  final Pointer<Void> _context;
  final _Evaluate _evaluate;
  final _EvaluateArray _evaluateArray;
  final _ContextDestroy _destroy;
  final _LastError _lastError;
  bool _disposed = false;

  static FfiCalcBackend open() {
    final library = DynamicLibrary.open(_libraryName());
    final abiVersion = library.lookupFunction<_AbiVersionNative, _AbiVersion>('sc_abi_version')();
    if (abiVersion != 1) {
      throw StateError('Unsupported SuperCalculator native ABI: $abiVersion');
    }
    final create = library.lookupFunction<_ContextCreateNative, _ContextCreate>('sc_context_create');
    final context = create();
    if (context == nullptr) throw StateError('Could not create native calculation context.');
    return FfiCalcBackend._(library: library, context: context);
  }

  @override
  String get name => 'Native FFI';

  @override
  Future<CalcEvaluation> evaluate(String expression, double x) async {
    if (_disposed) return const CalcEvaluation.failure(backend: 'Native FFI', message: 'Backend is closed.');
    final expressionPointer = expression.toNativeUtf8();
    final output = calloc<Double>();
    try {
      final status = _evaluate(_context, expressionPointer, x, 0, output);
      if (status != 0) {
        return CalcEvaluation.failure(backend: name, message: _readLastError());
      }
      return CalcEvaluation(value: output.value, backend: name);
    } finally {
      calloc.free(output);
      calloc.free(expressionPointer);
    }
  }

  @override
  Future<List<double?>> evaluateArray(String expression, List<double> xs) async {
    if (_disposed || xs.isEmpty) return <double?>[];
    final expressionPointer = expression.toNativeUtf8();
    final input = calloc<Double>(xs.length);
    final output = calloc<Double>(xs.length);
    try {
      input.asTypedList(xs.length).setAll(0, xs);
      final status = _evaluateArray(_context, expressionPointer, input, xs.length, output);
      if (status != 0) return List<double?>.filled(xs.length, null);
      return output.asTypedList(xs.length).map<double?>((value) => value.isFinite ? value : null).toList();
    } finally {
      calloc.free(input);
      calloc.free(output);
      calloc.free(expressionPointer);
    }
  }

  String _readLastError() {
    final pointer = _lastError(_context);
    return pointer == nullptr ? 'Native calculation failed.' : pointer.toDartString();
  }

  @override
  void dispose() {
    if (_disposed) return;
    _disposed = true;
    _destroy(_context);
  }

  static String _libraryName() {
    if (Platform.isAndroid) return 'libsupercalc_core.so';
    if (Platform.isWindows) return 'supercalc_core.dll';
    if (Platform.isMacOS || Platform.isIOS) return 'libsupercalc_core.dylib';
    if (Platform.isLinux) return 'libsupercalc_core.so';
    throw UnsupportedError('Native FFI is not configured for this platform.');
  }
}
