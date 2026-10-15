import 'package:flutter/material.dart';
import '../models/scan_result.dart';
import '../services/api_service.dart';
import '../services/history_service.dart';
import '../widgets/message_card.dart';
import 'feedback_dialog.dart';

class HistoryScreen extends StatefulWidget {
  final ApiService apiService;

  const HistoryScreen({super.key, required this.apiService});

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  String _activeFilter = 'ALL';
  String _searchQuery = '';
  final TextEditingController _searchCtrl = TextEditingController();

  @override
  void dispose() {
    _searchCtrl.dispose();
    super.dispose();
  }

  void _confirmClear() {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Clear Scan History?'),
        content: const Text('This will delete all past scan records on this device.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              HistoryService().clear();
              Navigator.pop(ctx);
            },
            child: const Text('Clear All', style: TextStyle(color: Colors.red)),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return ListenableBuilder(
      listenable: HistoryService(),
      builder: (context, _) {
        final allItems = HistoryService().history;
        final filtered = allItems.where((item) {
          final matchesFilter = _activeFilter == 'ALL' || item.label == _activeFilter;
          final matchesSearch = _searchQuery.isEmpty ||
              item.text.toLowerCase().contains(_searchQuery.toLowerCase()) ||
              item.senderId.toLowerCase().contains(_searchQuery.toLowerCase());
          return matchesFilter && matchesSearch;
        }).toList();

        return Scaffold(
          appBar: AppBar(
            title: const Text('Scan History'),
            actions: [
              if (allItems.isNotEmpty)
                IconButton(
                  icon: const Icon(Icons.delete_outline_rounded),
                  onPressed: _confirmClear,
                  tooltip: 'Clear history',
                ),
            ],
          ),
          body: Column(
            children: [
              // Search input
              Padding(
                padding: const EdgeInsets.fromLTRB(16, 8, 16, 8),
                child: TextField(
                  controller: _searchCtrl,
                  decoration: InputDecoration(
                    hintText: 'Search by keyword or sender...',
                    prefixIcon: const Icon(Icons.search_rounded, size: 20),
                    suffixIcon: _searchQuery.isNotEmpty
                        ? IconButton(
                            icon: const Icon(Icons.clear_rounded, size: 18),
                            onPressed: () {
                              setState(() {
                                _searchCtrl.clear();
                                _searchQuery = '';
                              });
                            },
                          )
                        : null,
                    isDense: true,
                    contentPadding: const EdgeInsets.symmetric(vertical: 10),
                  ),
                  onChanged: (val) => setState(() => _searchQuery = val),
                ),
              ),

              // Filter Chips
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                child: Row(
                  children: [
                    _buildFilterChip('ALL', 'All (${allItems.length})'),
                    const SizedBox(width: 8),
                    _buildFilterChip('SPAM', 'Spam (${allItems.where((i) => i.label == 'SPAM').length})'),
                    const SizedBox(width: 8),
                    _buildFilterChip('SUSPICIOUS', 'Suspicious (${allItems.where((i) => i.label == 'SUSPICIOUS').length})'),
                    const SizedBox(width: 8),
                    _buildFilterChip('SAFE', 'Safe (${allItems.where((i) => i.label == 'SAFE').length})'),
                  ],
                ),
              ),

              // List of history cards
              Expanded(
                child: filtered.isEmpty
                    ? Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(Icons.history_rounded, size: 64, color: Colors.grey.withValues(alpha: 0.3)),
                            const SizedBox(height: 12),
                            Text(
                              allItems.isEmpty ? 'No scan history yet' : 'No matching results',
                              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.grey),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              allItems.isEmpty
                                  ? 'Messages you scan will appear here automatically.'
                                  : 'Try adjusting your search or filters.',
                              style: const TextStyle(fontSize: 13, color: Colors.grey),
                            ),
                          ],
                        ),
                      )
                    : ListView.builder(
                        padding: const EdgeInsets.all(16),
                        itemCount: filtered.length,
                        itemBuilder: (context, i) {
                          final item = filtered[i];
                          return MessageCard(
                            result: item,
                            onTap: () {
                              FeedbackDialog.show(
                                context,
                                text: item.text,
                                predictedLabel: item.label,
                                apiService: widget.apiService,
                              );
                            },
                          );
                        },
                      ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildFilterChip(String key, String label) {
    final isSelected = _activeFilter == key;
    return GestureDetector(
      onTap: () => setState(() => _activeFilter = key),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
        decoration: BoxDecoration(
          color: isSelected ? Theme.of(context).colorScheme.primary : Colors.transparent,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: isSelected ? Theme.of(context).colorScheme.primary : Colors.grey.withValues(alpha: 0.3),
          ),
        ),
        child: Text(
          label,
          style: TextStyle(
            fontSize: 11,
            fontWeight: FontWeight.bold,
            color: isSelected ? Colors.white : Colors.grey,
          ),
        ),
      ),
    );
  }
}
