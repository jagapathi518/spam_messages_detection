import 'package:flutter_test/flutter_test.dart';
import 'package:spam_shield/main.dart';

void main() {
  testWidgets('SpamShieldApp renders with navigation destinations', (WidgetTester tester) async {
    await tester.pumpWidget(const SpamShieldApp());
    await tester.pump();

    // Verify Navigation destinations exist
    expect(find.text('Scan'), findsWidgets);
    expect(find.text('Batch'), findsWidgets);
    expect(find.text('Library'), findsWidgets);
    expect(find.text('History'), findsWidgets);
    expect(find.text('Settings'), findsWidgets);
  });
}
