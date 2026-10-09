import 'calc_backend.dart';

/// Web adapter boundary. M2 will replace the fallback with the generated
/// WebAssembly bridge without changing feature repositories or widgets.
CalcBackend createCalcBackend() =>
    const DartCalcBackend(displayName: 'Dart fallback');
