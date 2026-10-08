import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';

@immutable
class PresetDefinition {
  const PresetDefinition({
    required this.mode,
    required this.label,
    required this.expression,
    this.secondary,
    this.start = 0,
    this.end = 6.283185307179586,
  });

  final String mode;
  final String label;
  final String expression;
  final String? secondary;
  final double start;
  final double end;
}

class PresetCatalog {
  const PresetCatalog._();

  static const assetPath = 'assets/presets/function_presets.json';

  static Future<Map<String, List<PresetDefinition>>> load([
    AssetBundle? bundle,
  ]) async {
    final raw = await (bundle ?? rootBundle).loadString(assetPath);
    return parse(raw);
  }

  static Map<String, List<PresetDefinition>> parse(String raw) {
    final decoded = jsonDecode(raw);
    if (decoded is! Map) {
      throw const FormatException('Preset catalog must be a JSON object.');
    }
    final result = <String, List<PresetDefinition>>{};
    void add(Object? value, String defaultMode) {
      if (value is! List) return;
      for (final item in value) {
        if (item is! Map ||
            item['label'] is! String ||
            item['expression'] is! String) {
          throw const FormatException('Preset entries require label and expression.');
        }
        final mode = item['mode'] is String ? item['mode'] as String : defaultMode;
        final start = _finiteNumber(item['start']) ?? 0;
        final end = _finiteNumber(item['end']) ?? 6.283185307179586;
        if (start >= end) {
          throw const FormatException('Preset parameter ranges must increase.');
        }
        final secondary = item['secondary'];
        if (secondary != null && secondary is! String) {
          throw const FormatException('Preset secondary expressions must be strings.');
        }
        result.putIfAbsent(mode, () => <PresetDefinition>[]).add(
          PresetDefinition(
            mode: mode,
            label: item['label'] as String,
            expression: item['expression'] as String,
            secondary: secondary as String?,
            start: start,
            end: end,
          ),
        );
      }
    }

    add(decoded['presets'], 'function');
    add(decoded['parameterPresets'], 'function');
    for (final entries in result.values) {
      final labels = <String>{};
      for (final entry in entries) {
        if (!labels.add(entry.label)) {
          throw FormatException('Duplicate preset label in ${entry.mode}.');
        }
      }
    }
    return result;
  }

  static double? _finiteNumber(Object? value) {
    if (value is num && value.isFinite) return value.toDouble();
    return null;
  }
}
