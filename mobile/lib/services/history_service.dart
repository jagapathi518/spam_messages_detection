import 'package:flutter/foundation.dart';
import '../models/scan_result.dart';

class HistoryService extends ChangeNotifier {
  static final HistoryService _instance = HistoryService._internal();
  factory HistoryService() => _instance;
  HistoryService._internal();

  final List<ScanResult> _history = [];

  List<ScanResult> get history => List.unmodifiable(_history);

  void add(ScanResult result) {
    // Avoid duplicate IDs
    _history.removeWhere((item) => item.id == result.id);
    _history.insert(0, result);
    if (_history.length > 200) {
      _history.removeLast();
    }
    notifyListeners();
  }

  void addAll(List<ScanResult> results) {
    for (final r in results) {
      _history.removeWhere((item) => item.id == r.id);
      _history.insert(0, r);
    }
    if (_history.length > 200) {
      _history.removeRange(200, _history.length);
    }
    notifyListeners();
  }

  void clear() {
    _history.clear();
    notifyListeners();
  }
}
