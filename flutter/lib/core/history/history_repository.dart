import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final calculationHistoryProvider =
    NotifierProvider<CalculationHistoryController, List<HistoryEntry>>(
      CalculationHistoryController.new,
    );

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
}

class CalculationHistoryController extends Notifier<List<HistoryEntry>> {
  @override
  List<HistoryEntry> build() => const <HistoryEntry>[];

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
    state = <HistoryEntry>[entry, ...state].take(10).toList(growable: false);
  }

  void clear() => state = const <HistoryEntry>[];

  String exportCsv() {
    final rows = <String>['expression,result,backend,createdAt'];
    for (final entry in state) {
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

  String exportJson() =>
      jsonEncode(state.map((entry) => entry.toJson()).toList());

  String _escape(String value) => '"${value.replaceAll('"', '""')}"';
}
