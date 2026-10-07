import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/history/history_repository.dart';
import '../../core/ui/feature_widgets.dart';

class HistoryPage extends ConsumerWidget {
  const HistoryPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final entries = ref.watch(calculationHistoryProvider);
    final controller = ref.read(calculationHistoryProvider.notifier);
    return FeaturePageFrame(
      title: nextEraText(context, 'History', '历史记录'),
      icon: Icons.history,
      subtitle: nextEraText(
        context,
        'The most recent ten successful calculations are kept in the app session.',
        '应用会在当前会话保留最近十次成功计算。',
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: <Widget>[
          FeatureCard(
            title: nextEraText(context, 'Recent calculations', '最近计算'),
            icon: Icons.list_alt,
            child: entries.isEmpty
                ? Text(nextEraText(context, 'No calculations yet.', '暂无计算记录。'))
                : Column(
                    children: entries
                        .map(
                          (entry) => ListTile(
                            contentPadding: EdgeInsets.zero,
                            leading: const Icon(Icons.calculate_outlined),
                            title: Text(
                              entry.expression,
                              style: const TextStyle(fontFamily: 'monospace'),
                            ),
                            subtitle: Text(
                              '${entry.backend} · ${entry.createdAt}',
                            ),
                            trailing: Text(
                              entry.result,
                              style: const TextStyle(fontFamily: 'monospace'),
                            ),
                          ),
                        )
                        .toList(growable: false),
                  ),
          ),
          const SizedBox(height: 16),
          Wrap(
            spacing: 12,
            runSpacing: 12,
            children: <Widget>[
              OutlinedButton.icon(
                onPressed: entries.isEmpty
                    ? null
                    : () async {
                        await Clipboard.setData(
                          ClipboardData(text: controller.exportCsv()),
                        );
                        if (context.mounted) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(
                              content: Text(
                                nextEraText(context, 'CSV copied.', 'CSV 已复制。'),
                              ),
                            ),
                          );
                        }
                      },
                icon: const Icon(Icons.copy),
                label: Text(nextEraText(context, 'Copy CSV', '复制 CSV')),
              ),
              TextButton.icon(
                onPressed: entries.isEmpty ? null : controller.clear,
                icon: const Icon(Icons.delete_outline),
                label: Text(nextEraText(context, 'Clear history', '清空历史')),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            nextEraText(
              context,
              'History is intentionally session-scoped until the platform storage adapter is enabled.',
              '在平台存储适配器启用前，历史记录仅限当前会话。',
            ),
            style: Theme.of(context).textTheme.bodySmall,
          ),
        ],
      ),
    );
  }
}
