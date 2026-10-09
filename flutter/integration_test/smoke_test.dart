import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';

import 'package:supercalculator_next_era/main.dart' as app;

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('application starts on the home route', (tester) async {
    app.main();
    await tester.pumpAndSettle();
    expect(find.text('SuperCalculator - Next Era'), findsOneWidget);
  });
}
