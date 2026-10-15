import 'package:flutter/material.dart';
import 'services/api_service.dart';
import 'theme/app_theme.dart';
import 'screens/scan_screen.dart';
import 'screens/batch_screen.dart';
import 'screens/scam_library_screen.dart';
import 'screens/history_screen.dart';
import 'screens/settings_screen.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const SpamShieldApp());
}

class SpamShieldApp extends StatefulWidget {
  const SpamShieldApp({super.key});

  @override
  State<SpamShieldApp> createState() => _SpamShieldAppState();
}

class _SpamShieldAppState extends State<SpamShieldApp> {
  ThemeMode _themeMode = ThemeMode.dark;
  final ApiService _apiService = ApiService();

  void _updateThemeMode(ThemeMode mode) {
    setState(() => _themeMode = mode);
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Spam Shield',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: _themeMode,
      home: MainNavigationScaffold(
        apiService: _apiService,
        currentThemeMode: _themeMode,
        onThemeChanged: _updateThemeMode,
      ),
    );
  }
}

class MainNavigationScaffold extends StatefulWidget {
  final ApiService apiService;
  final ThemeMode currentThemeMode;
  final ValueChanged<ThemeMode> onThemeChanged;

  const MainNavigationScaffold({
    super.key,
    required this.apiService,
    required this.currentThemeMode,
    required this.onThemeChanged,
  });

  @override
  State<MainNavigationScaffold> createState() => _MainNavigationScaffoldState();
}

class _MainNavigationScaffoldState extends State<MainNavigationScaffold> {
  int _currentIndex = 0;

  late final List<Widget> _screens;

  @override
  void initState() {
    super.initState();
    _screens = [
      ScanScreen(apiService: widget.apiService),
      BatchScreen(apiService: widget.apiService),
      const ScamLibraryScreen(),
      HistoryScreen(apiService: widget.apiService),
      SettingsScreen(
        apiService: widget.apiService,
        currentThemeMode: widget.currentThemeMode,
        onThemeChanged: widget.onThemeChanged,
      ),
    ];
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(
        index: _currentIndex,
        children: _screens,
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentIndex,
        onDestinationSelected: (idx) => setState(() => _currentIndex = idx),
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.shield_outlined),
            selectedIcon: Icon(Icons.shield_rounded),
            label: 'Scan',
          ),
          NavigationDestination(
            icon: Icon(Icons.all_inbox_outlined),
            selectedIcon: Icon(Icons.all_inbox_rounded),
            label: 'Batch',
          ),
          NavigationDestination(
            icon: Icon(Icons.menu_book_outlined),
            selectedIcon: Icon(Icons.menu_book_rounded),
            label: 'Library',
          ),
          NavigationDestination(
            icon: Icon(Icons.history_outlined),
            selectedIcon: Icon(Icons.history_rounded),
            label: 'History',
          ),
          NavigationDestination(
            icon: Icon(Icons.settings_outlined),
            selectedIcon: Icon(Icons.settings_rounded),
            label: 'Settings',
          ),
        ],
      ),
    );
  }
}
