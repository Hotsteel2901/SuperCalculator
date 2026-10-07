import 'package:flutter/material.dart';

import '../../core/compute/computation.dart';
import '../../core/ui/feature_widgets.dart';
import '../../l10n/generated/app_localizations.dart';

class ToolsPage extends StatefulWidget {
  const ToolsPage({super.key});

  @override
  State<ToolsPage> createState() => _ToolsPageState();
}

class _ToolsPageState extends State<ToolsPage> {
  final _baseInput = TextEditingController(text: 'FF');
  final _baseFrom = TextEditingController(text: '16');
  final _baseTo = TextEditingController(text: '2');
  final _unitValue = TextEditingController(text: '10');
  String _category = 'Length';
  String _fromUnit = 'm';
  String _toUnit = 'ft';
  String? _baseResult;
  String? _unitResult;
  String? _error;

  static const _units = <String, List<String>>{
    'Length': <String>['m', 'km', 'cm', 'mm', 'in', 'ft'],
    'Weight': <String>['kg', 'g', 'lb', 'oz'],
    'Temperature': <String>['°C', '°F', 'K'],
    'Time': <String>['s', 'min', 'h', 'day'],
    'Data': <String>['B', 'KB', 'MB', 'GB'],
    'Speed': <String>['m/s', 'km/h', 'mph'],
    'Angle': <String>['rad', 'deg'],
    'Area': <String>['m²', 'km²', 'ft²'],
    'Volume': <String>['L', 'mL', 'm³', 'gal'],
  };

  @override
  void dispose() {
    _baseInput.dispose();
    _baseFrom.dispose();
    _baseTo.dispose();
    _unitValue.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final units = _units[_category]!;
    if (!units.contains(_fromUnit)) _fromUnit = units.first;
    if (!units.contains(_toUnit)) _toUnit = units.last;
    return FeaturePageFrame(
      title: AppLocalizations.of(context).tools,
      icon: Icons.build,
      subtitle: nextEraText(
        context,
        'Small, offline-first utilities for number bases and everyday units.',
        '提供离线优先的进制转换和常用单位换算工具。',
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: <Widget>[
          FeatureCard(
            title: nextEraText(context, 'Base converter', '进制转换'),
            icon: Icons.numbers,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: <Widget>[
                TextField(
                  controller: _baseInput,
                  decoration: InputDecoration(
                    labelText: nextEraText(context, 'Input', '输入'),
                  ),
                  style: const TextStyle(fontFamily: 'monospace'),
                ),
                const SizedBox(height: 12),
                FormRow(
                  children: <Widget>[
                    _baseField(
                      _baseFrom,
                      nextEraText(context, 'From base', '源进制'),
                    ),
                    _baseField(
                      _baseTo,
                      nextEraText(context, 'To base', '目标进制'),
                    ),
                    FilledButton.icon(
                      onPressed: _convertBase,
                      icon: const Icon(Icons.transform),
                      label: Text(nextEraText(context, 'Convert', '转换')),
                    ),
                  ],
                ),
                if (_baseResult != null)
                  SelectableText(
                    _baseResult!,
                    style: Theme.of(context).textTheme.titleLarge
                        ?.copyWith(fontFamily: 'monospace'),
                  ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          FeatureCard(
            title: nextEraText(context, 'Unit converter', '单位换算'),
            icon: Icons.swap_horiz,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: <Widget>[
                DropdownButtonFormField<String>(
                  initialValue: _category,
                  decoration: InputDecoration(
                    labelText: nextEraText(context, 'Category', '类别'),
                  ),
                  items: _units.keys
                      .map(
                        (item) => DropdownMenuItem<String>(
                          value: item,
                          child: Text(item),
                        ),
                      )
                      .toList(growable: false),
                  onChanged: (value) {
                    if (value != null) {
                      setState(() => _category = value);
                    }
                  },
                ),
                const SizedBox(height: 12),
                FormRow(
                  children: <Widget>[
                    TextField(
                      controller: _unitValue,
                      decoration: InputDecoration(
                        labelText: nextEraText(context, 'Value', '数值'),
                      ),
                      keyboardType: const TextInputType.numberWithOptions(
                        decimal: true,
                        signed: true,
                      ),
                    ),
                    _unitDropdown(
                      units,
                      _fromUnit,
                      nextEraText(context, 'From', '从'),
                      (value) => setState(() => _fromUnit = value),
                    ),
                    _unitDropdown(
                      units,
                      _toUnit,
                      nextEraText(context, 'To', '到'),
                      (value) => setState(() => _toUnit = value),
                    ),
                  ],
                ),
                FilledButton.icon(
                  onPressed: _convertUnit,
                  icon: const Icon(Icons.swap_horiz),
                  label: Text(nextEraText(context, 'Convert unit', '换算单位')),
                ),
                if (_unitResult != null)
                  Padding(
                    padding: const EdgeInsets.only(top: 12),
                    child: Text(
                      _unitResult!,
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                  ),
              ],
            ),
          ),
          if (_error != null) ...<Widget>[
            const SizedBox(height: 16),
            ResultCard(value: '', error: _error),
          ],
        ],
      ),
    );
  }

  Widget _baseField(TextEditingController controller, String label) {
    return TextField(
      controller: controller,
      decoration: InputDecoration(labelText: label),
      keyboardType: TextInputType.number,
    );
  }

  Widget _unitDropdown(
    List<String> units,
    String value,
    String label,
    ValueChanged<String> onChanged,
  ) {
    return DropdownButtonFormField<String>(
      initialValue: value,
      decoration: InputDecoration(labelText: label),
      items: units
          .map(
            (unit) => DropdownMenuItem<String>(value: unit, child: Text(unit)),
          )
          .toList(growable: false),
      onChanged: (next) {
        if (next != null) {
          onChanged(next);
        }
      },
    );
  }

  void _convertBase() {
    final from = int.tryParse(_baseFrom.text.trim());
    final to = int.tryParse(_baseTo.text.trim());
    if (from == null || to == null) {
      _showError(nextEraText(context, 'Bases must be integers.', '进制必须是整数。'));
      return;
    }
    try {
      final value = DartComputation.convertBase(_baseInput.text, from, to);
      setState(() {
        _baseResult = value;
        _error = null;
      });
    } on FormatException catch (error) {
      _showError(error.message);
    }
  }

  void _convertUnit() {
    final value = double.tryParse(_unitValue.text.trim());
    if (value == null) {
      _showError(nextEraText(context, 'Enter a numeric value.', '请输入数字。'));
      return;
    }
    try {
      final result = DartComputation.convertUnit(
        _category,
        _fromUnit,
        _toUnit,
        value,
      );
      setState(() {
        _unitResult = '${result.toStringAsPrecision(12)} $_toUnit';
        _error = null;
      });
    } on FormatException catch (error) {
      _showError(error.message);
    }
  }

  void _showError(String message) {
    setState(() {
      _error = message;
      _baseResult = null;
      _unitResult = null;
    });
  }
}
