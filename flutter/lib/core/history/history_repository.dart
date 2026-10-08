import 'dart:async';
import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

const _historyStorageKey = 'supercalculator.next_era.history.v1';

final calculationHistoryProvider =
    NotifierProvider<CalculationHistoryController, List<HistoryEntry>>(
      CalculationHistoryController.new,
    );

void recordCalculationHistory(
  WidgetRef ref, {
  required String expression,
  required String result,
  required String backend,
}) {
  ref
      .read(calculationHistoryProvider.notifier)
      .add(expression: expression, result: result, backend: backend);
}

@immutable
class HistoryEntry {
  const HistoryEntry({
    required this.expression,
    required this.result,
    required this.backend,
    required this.createdAt,
  });

  final String expression;
  final String result;
  final String backend;
  final DateTime createdAt;

  Map<String, Object> toJson() => <String, Object>{
    'expression': expression,
    'result': result,
    'backend': backend,
    'createdAt': createdAt.toIso8601String(),
  };

  static HistoryEntry? fromJson(Object? source) {
    if (source is! Map) return null;
    final expression = source['expression'];
    final result = source['result'];
    final backend = source['backend'];
    final createdAt = source['createdAt'];
    if (expression is! String ||
        result is! String ||
        backend is! String ||
        createdAt is! String) {
      return null;
    }
    final parsedDate = DateTime.tryParse(createdAt);
    if (parsedDate == null) return null;
    return HistoryEntry(
      expression: expression,
      result: result,
      backend: backend,
      createdAt: parsedDate,
    );
  }
}

class HistoryCodec {
  const HistoryCodec._();

  static String toCsv(Iterable<HistoryEntry> entries) {
    final rows = <String>['expression,result,backend,createdAt'];
    for (final entry in entries) {
      rows.add(
        <String>[
          _escape(entry.expression),
          _escape(entry.result),
          _escape(entry.backend),
          entry.createdAt.toIso8601String(),
        ].join(','),
      );
    }
    return rows.join('\n');
  }

  static String toJson(Iterable<HistoryEntry> entries) => jsonEncode(
    entries.map((entry) => entry.toJson()).toList(growable: false),
  );

  static List<HistoryEntry> fromJson(String encoded, {int limit = 10}) {
    if (limit < 1) return const <HistoryEntry>[];
    final decoded = jsonDecode(encoded);
    if (decoded is! List) return const <HistoryEntry>[];
    return decoded
        .map(HistoryEntry.fromJson)
        .whereType<HistoryEntry>()
        .take(limit)
        .toList(growable: false);
  }

  static String _escape(String value) => '"${value.replaceAll('"', '""')}"';
}

class CalculationHistoryController extends Notifier<List<HistoryEntry>> {
  late Future<void> _ready;
  bool _hasLocalChanges = false;

  @override
  List<HistoryEntry> build() {
    _ready = _restore();
    ref.onDispose(() {
      // The storage calls are deliberately best-effort and do not block route
      // disposal or application shutdown.
    });
    return const <HistoryEntry>[];
  }

  void add({
    required String expression,
    required String result,
    required String backend,
  }) {
    final entry = HistoryEntry(
      expression: expression,
      result: result,
      backend: backend,
      createdAt: DateTime.now(),
    );
    _hasLocalChanges = true;
    state = <HistoryEntry>[entry, ...state].take(10).toList(growable: false);
    unawaited(_persist());
  }

  void clear() {
    _hasLocalChanges = true;
    state = const <HistoryEntry>[];
    unawaited(_persist());
  }

  String exportCsv() => HistoryCodec.toCsv(state);

  String exportJson() => HistoryCodec.toJson(state);

  Future<void> _restore() async {
    try {
      final preferences = await SharedPreferences.getInstance();
      final encoded = preferences.getString(_historyStorageKey);
      if (encoded == null || _hasLocalChanges) return;
      final entries = HistoryCodec.fromJson(encoded);
      if (!_hasLocalChanges) state = entries;
    } catch (_) {
      // Corrupt or unavailable storage must never prevent the calculator from
      // starting. The in-memory repository remains the fallback.
    }
  }

  Future<void> _persist() async {
    try {
      await _ready;
      final preferences = await SharedPreferences.getInstance();
      await preferences.setString(_historyStorageKey, exportJson());
    } catch (_) {
      // Web private mode and restricted desktop profiles may reject storage;
      // history remains usable for the current session in that case.
    }
  }

}
