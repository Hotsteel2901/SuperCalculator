import 'package:flutter/foundation.dart';

@immutable
class PlotPoint {
  const PlotPoint(this.x, this.y, {this.z});

  final double x;
  final double y;
  final double? z;

  bool get isFinite => x.isFinite && y.isFinite && (z == null || z!.isFinite);
}
