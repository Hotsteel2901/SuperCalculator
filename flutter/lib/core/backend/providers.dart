import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'calc_backend.dart';
import 'calc_backend_factory.dart';

final calcBackendProvider = Provider<CalcBackend>((ref) {
  final backend = createCalcBackend();
  ref.onDispose(backend.dispose);
  return backend;
});
