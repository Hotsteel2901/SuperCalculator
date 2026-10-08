import 'package:flutter_test/flutter_test.dart';

import 'package:supercalculator_next_era/core/history/history_repository.dart';

void main() {
  test('history codec round-trips bounded entries and CSV escaping', () {
    final entries = <HistoryEntry>[
      HistoryEntry(
        expression: 'f("x"), x',
        result: '1,2',
        backend: 'Dart fallback',
        createdAt: DateTime.utc(2026, 10, 8, 1, 2, 3),
      ),
      HistoryEntry(
        expression: 'x^2',
        result: '4',
        backend: 'Native FFI',
        createdAt: DateTime.utc(2026, 10, 8, 1, 2, 4),
      ),
    ];
    final encoded = HistoryCodec.toJson(entries);
    final restored = HistoryCodec.fromJson(encoded);
    expect(restored, hasLength(2));
    expect(restored.first.expression, 'f("x"), x');
    expect(restored.first.createdAt, entries.first.createdAt);

    final csv = HistoryCodec.toCsv(entries);
    expect(csv.split('\n'), hasLength(3));
    expect(csv, contains('"f(""x""), x"'));
    expect(csv, contains('"1,2"'));
  });

  test('history codec discards malformed entries and enforces the limit', () {
    const encoded =
        '[{"expression":"x","result":"1","backend":"Dart","createdAt":"2026-10-08T00:00:00Z"},'
        '{"expression":"bad","result":1,"backend":"Dart","createdAt":"2026-10-08T00:00:00Z"}]';
    expect(HistoryCodec.fromJson(encoded), hasLength(1));
    expect(HistoryCodec.fromJson('[]', limit: 0), isEmpty);
  });
}
