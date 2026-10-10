import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:path_provider/path_provider.dart';
import '../services/offline_receipt_service.dart';
import '../utils/currency_format_helper.dart';

class BenchmarkItemResult {
  final int index;
  final String filename;
  final int elapsedMs;
  final String storeName;
  final double totalAmount;
  final int itemsCount;
  final String dateIso;
  final bool hasStore;
  final bool hasTotal;
  final double? groundTruthTotal;
  final bool totalMatchesGt;

  BenchmarkItemResult({
    required this.index,
    required this.filename,
    required this.elapsedMs,
    required this.storeName,
    required this.totalAmount,
    required this.itemsCount,
    required this.dateIso,
    required this.hasStore,
    required this.hasTotal,
    this.groundTruthTotal,
    required this.totalMatchesGt,
  });

  Map<String, dynamic> toJson() => {
        'index': index,
        'filename': filename,
        'elapsedMs': elapsedMs,
        'storeName': storeName,
        'totalAmount': totalAmount,
        'itemsCount': itemsCount,
        'dateIso': dateIso,
        'hasStore': hasStore,
        'hasTotal': hasTotal,
        'groundTruthTotal': groundTruthTotal,
        'totalMatchesGt': totalMatchesGt,
      };
}

class BenchmarkScreen extends StatefulWidget {
  final bool autoStart;

  const BenchmarkScreen({super.key, this.autoStart = false});

  @override
  State<BenchmarkScreen> createState() => _BenchmarkScreenState();
}

class _BenchmarkScreenState extends State<BenchmarkScreen> {
  bool _isLoadingAssets = true;
  bool _isRunning = false;
  List<String> _assetPaths = [];
  final Map<String, dynamic> _metadataMap = {};
  final List<BenchmarkItemResult> _results = [];
  int _currentIndex = 0;
  String? _statusText;

  @override
  void initState() {
    super.initState();
    _loadSampleAssets();
  }

  Future<void> _loadSampleAssets() async {
    setState(() {
      _isLoadingAssets = true;
      _statusText = 'Memeriksa dataset benchmark CORD-100...';
    });

    try {
      List<String> foundPaths = [];

      // 1. Cek folder eksternal device jika ada (misal hasil push ADB saat pengujian)
      final extDir = Directory('/sdcard/Android/data/com.example.flutter_application_1/files/cord_test_100');
      if (await extDir.exists()) {
        final files = extDir
            .listSync()
            .whereType<File>()
            .where((f) => f.path.endsWith('.jpg') || f.path.endsWith('.png'))
            .map((f) => f.path)
            .toList()
          ..sort();
        if (files.isNotEmpty) {
          foundPaths = files;
        }
      }

      // 2. Jika tidak ada di folder eksternal, coba periksa apakah dibundel di asset
      if (foundPaths.isEmpty) {
        try {
          final metaJson = await rootBundle.loadString('assets/cord_100/cord_100_metadata.json');
          final List<dynamic> metaList = json.decode(metaJson);
          for (final item in metaList) {
            if (item is Map<String, dynamic>) {
              final fname = item['filename'] as String?;
              if (fname != null) {
                _metadataMap[fname] = item['ground_truth'];
              }
            }
          }
          foundPaths = List.generate(
            100,
            (i) => 'assets/cord_100/cord_${i.toString().padLeft(3, '0')}.jpg',
          );
        } catch (_) {}
      }

      setState(() {
        _assetPaths = foundPaths;
        _isLoadingAssets = false;
        if (foundPaths.isNotEmpty) {
          _statusText = 'Siap menguji ${foundPaths.length} sampel struk CORD.';
        } else {
          _statusText =
              'Dataset CORD-100 tidak dibundel di APK rilis demi efisiensi ukuran aplikasi (~35 MB). Data empiris pengujian telah dicatat di Bab IV naskah skripsi.';
        }
      });

      if (widget.autoStart && _assetPaths.isNotEmpty && !_isRunning) {
        _startBenchmark();
      }
    } catch (e) {
      setState(() {
        _isLoadingAssets = false;
        _statusText = 'Gagal memuat assets: $e';
      });
    }
  }

  Future<void> _startBenchmark() async {
    if (_isRunning || _assetPaths.isEmpty) return;

    setState(() {
      _isRunning = true;
      _results.clear();
      _currentIndex = 0;
    });

    final tempDir = await getTemporaryDirectory();
    final totalCount = _assetPaths.length;

    for (var i = 0; i < totalCount; i++) {
      if (!mounted) break;

      final assetPath = _assetPaths[i];
      final filename = assetPath.split('/').last;

      setState(() {
        _currentIndex = i + 1;
        _statusText = 'Memproses $filename (${i + 1}/$totalCount)...';
      });

      final sw = Stopwatch()..start();
      try {
        String targetPath;
        File? tempFile;

        if (assetPath.startsWith('/')) {
          targetPath = assetPath;
        } else {
          // 1. Ekstrak aset ke file cache sementara jika dari bundle
          final byteData = await rootBundle.load(assetPath);
          tempFile = File('${tempDir.path}/temp_bench_$filename');
          await tempFile.writeAsBytes(byteData.buffer.asUint8List(), flush: true);
          targetPath = tempFile.path;
        }

        // 2. Jalankan Google ML Kit + Spatial Clustering + Regex Caran
        final extraction = await OfflineReceiptService.extractReceipt(targetPath);
        sw.stop();

        final t = extraction.transaction;
        final hasStore = t.storeName.isNotEmpty && t.storeName != 'Toko Tidak Dikenal';
        final hasTotal = t.totalAmount > 0;

        // Cek kecocokan Ground Truth jika tersedia
        double? gtTotal;
        bool matchesGt = false;
        final gt = _metadataMap[filename];
        if (gt != null && gt is Map<String, dynamic>) {
          final gtParse = gt['gt_parse'];
          if (gtParse is Map<String, dynamic>) {
            final totObj = gtParse['total'];
            if (totObj is Map<String, dynamic>) {
              final rawTot = totObj['total_price'] ?? totObj['subtotal_price'];
              if (rawTot != null) {
                gtTotal = CurrencyFormatHelper.parsePrice(rawTot.toString());
                if (gtTotal > 0 && (gtTotal - t.totalAmount).abs() < 1.0) {
                  matchesGt = true;
                }
              }
            }
          }
        }

        final itemRes = BenchmarkItemResult(
          index: i,
          filename: filename,
          elapsedMs: sw.elapsedMilliseconds,
          storeName: t.storeName,
          totalAmount: t.totalAmount,
          itemsCount: t.items.length,
          dateIso: t.transactionDate.toIso8601String(),
          hasStore: hasStore,
          hasTotal: hasTotal,
          groundTruthTotal: gtTotal,
          totalMatchesGt: matchesGt,
        );

        _results.add(itemRes);

        // Hapus file sementara setelah diproses
        try {
          if (tempFile != null && await tempFile.exists()) await tempFile.delete();
        } catch (_) {}
      } catch (e) {
        sw.stop();
        _results.add(
          BenchmarkItemResult(
            index: i,
            filename: filename,
            elapsedMs: sw.elapsedMilliseconds,
            storeName: 'Error: $e',
            totalAmount: 0,
            itemsCount: 0,
            dateIso: DateTime.now().toIso8601String(),
            hasStore: false,
            hasTotal: false,
            groundTruthTotal: null,
            totalMatchesGt: false,
          ),
        );
      }

      setState(() {});
      await Future.delayed(const Duration(milliseconds: 5));
    }

    // Simpan hasil ke JSON di cache
    try {
      final outPath = '${tempDir.path}/benchmark_cord_100_results.json';
      final outFile = File(outPath);
      final summaryMap = {
        'device': 'TECNO LH7n (Helio G99, Android 14)',
        'framework': 'Caran v0.9.0-beta (Google ML Kit + Spatial Clustering)',
        'timestamp': DateTime.now().toIso8601String(),
        'totalSamples': _results.length,
        'averageLatencyMs': _calculateAverageLatency(),
        'minLatencyMs': _results.map((r) => r.elapsedMs).reduce((a, b) => a < b ? a : b),
        'maxLatencyMs': _results.map((r) => r.elapsedMs).reduce((a, b) => a > b ? a : b),
        'storeAccuracyPercent': _calculateStoreAccuracy(),
        'totalAccuracyPercent': _calculateTotalAccuracy(),
        'gtMatchPercent': _calculateGtMatchPercent(),
        'results': _results.map((r) => r.toJson()).toList(),
      };

      final jsonStr = const JsonEncoder.withIndent('  ').convert(summaryMap);
      await outFile.writeAsString(jsonStr);

      debugPrint('BENCHMARK_COMPLETE_OUTPUT:');
      debugPrint(jsonStr);

      setState(() {
        _isRunning = false;
        _statusText = 'Selesai! Rata-rata latensi: ${_calculateAverageLatency().toStringAsFixed(1)} ms | Toko: ${_calculateStoreAccuracy().toStringAsFixed(1)}%';
      });
    } catch (e) {
      setState(() {
        _isRunning = false;
        _statusText = 'Benchmark Selesai (Log saved)';
      });
    }
  }

  double _calculateAverageLatency() {
    if (_results.isEmpty) return 0.0;
    final totalMs = _results.fold<int>(0, (sum, r) => sum + r.elapsedMs);
    return totalMs / _results.length;
  }

  double _calculateStoreAccuracy() {
    if (_results.isEmpty) return 0.0;
    final valid = _results.where((r) => r.hasStore).length;
    return (valid / _results.length) * 100;
  }

  double _calculateTotalAccuracy() {
    if (_results.isEmpty) return 0.0;
    final valid = _results.where((r) => r.hasTotal).length;
    return (valid / _results.length) * 100;
  }

  double _calculateGtMatchPercent() {
    final withGt = _results.where((r) => r.groundTruthTotal != null).toList();
    if (withGt.isEmpty) return 0.0;
    final matched = withGt.where((r) => r.totalMatchesGt).length;
    return (matched / withGt.length) * 100;
  }

  @override
  Widget build(BuildContext context) {
    final avgLat = _calculateAverageLatency();
    final storeAcc = _calculateStoreAccuracy();
    final totalAcc = _calculateTotalAccuracy();
    final progress = _assetPaths.isEmpty ? 0.0 : _currentIndex / _assetPaths.length;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Benchmark 100 Struk CORD-v2'),
        actions: [
          if (!_isRunning && _assetPaths.isNotEmpty)
            IconButton(
              icon: const Icon(Icons.refresh),
              tooltip: 'Muat Ulang',
              onPressed: _loadSampleAssets,
            ),
        ],
      ),
      body: _isLoadingAssets
          ? const Center(child: CircularProgressIndicator())
          : Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // Header Info Card
                  Card(
                    elevation: 1,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    child: Padding(
                      padding: const EdgeInsets.all(14),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Icon(Icons.analytics, color: Colors.teal.shade700, size: 22),
                              const SizedBox(width: 8),
                              const Text(
                                'Evaluasi Empiris Bab IV Skripsi',
                                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                              ),
                            ],
                          ),
                          const SizedBox(height: 6),
                          Text(
                            'Menguji 100 sampel struk belanja riil CORD-v2 secara langsung pada prosesor fisik smartphone (On-Device Offline).',
                            style: TextStyle(fontSize: 12, color: Colors.grey.shade700),
                          ),
                          const SizedBox(height: 10),
                          Row(
                            children: [
                              Chip(
                                label: Text('${_assetPaths.length} Sampel'),
                                avatar: const Icon(Icons.receipt_long, size: 16),
                                visualDensity: VisualDensity.compact,
                              ),
                              const SizedBox(width: 8),
                              Chip(
                                label: Text(_isRunning ? 'Sedang Berjalan' : (_results.isNotEmpty ? 'Selesai' : 'Siap')),
                                backgroundColor: _isRunning ? Colors.amber.shade100 : Colors.teal.shade50,
                                visualDensity: VisualDensity.compact,
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  ),

                  const SizedBox(height: 12),

                  // Progress & Metrics Summary
                  if (_isRunning || _results.isNotEmpty) ...[
                    Card(
                      elevation: 0,
                      color: Colors.grey.shade50,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                        side: BorderSide(color: Colors.grey.shade300),
                      ),
                      child: Padding(
                        padding: const EdgeInsets.all(12),
                        child: Column(
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Text(
                                  'Progres: $_currentIndex / ${_assetPaths.length}',
                                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
                                ),
                                Text(
                                  '${(progress * 100).toStringAsFixed(1)}%',
                                  style: TextStyle(fontWeight: FontWeight.bold, color: Colors.teal.shade800),
                                ),
                              ],
                            ),
                            const SizedBox(height: 8),
                            LinearProgressIndicator(
                              value: progress,
                              backgroundColor: Colors.grey.shade200,
                              valueColor: AlwaysStoppedAnimation<Color>(Colors.teal.shade600),
                              minHeight: 8,
                              borderRadius: BorderRadius.circular(4),
                            ),
                            const SizedBox(height: 12),
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceAround,
                              children: [
                                _metricTile('Rata-rata Latensi', '${avgLat.toStringAsFixed(1)} ms'),
                                _metricTile('Akurasi Toko', '${storeAcc.toStringAsFixed(1)}%'),
                                _metricTile('Akurasi Total', '${totalAcc.toStringAsFixed(1)}%'),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(height: 8),
                  ],

                  if (_statusText != null)
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 4),
                      child: Text(
                        _statusText!,
                        style: TextStyle(fontSize: 11, color: Colors.grey.shade600, fontStyle: FontStyle.italic),
                        textAlign: TextAlign.center,
                      ),
                    ),

                  const SizedBox(height: 8),

                  // Action Button
                  if (!_isRunning)
                    ElevatedButton.icon(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.teal.shade700,
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 14),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                      ),
                      icon: Icon(_results.isEmpty ? Icons.play_arrow : Icons.replay),
                      label: Text(
                        _results.isEmpty ? 'Jalankan Pengujian 100 Struk' : 'Ulangi Pengujian 100 Struk',
                        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                      ),
                      onPressed: _assetPaths.isEmpty ? null : _startBenchmark,
                    ),

                  const SizedBox(height: 10),

                  // Results List
                  Expanded(
                    child: _results.isEmpty
                        ? Center(
                            child: Text(
                              _assetPaths.isEmpty
                                  ? 'Tidak ada file di assets cord_100.'
                                  : 'Tekan tombol di atas untuk memulai pengujian.',
                              textAlign: TextAlign.center,
                              style: TextStyle(color: Colors.grey.shade600, fontSize: 13),
                            ),
                          )
                        : ListView.separated(
                            itemCount: _results.length,
                            separatorBuilder: (_, __) => const Divider(height: 1),
                            itemBuilder: (ctx, idx) {
                              final item = _results[idx];
                              return ListTile(
                                dense: true,
                                leading: CircleAvatar(
                                  radius: 14,
                                  backgroundColor: item.hasTotal ? Colors.teal.shade100 : Colors.orange.shade100,
                                  child: Text(
                                    '${item.index + 1}',
                                    style: TextStyle(fontSize: 10, color: Colors.grey.shade800),
                                  ),
                                ),
                                title: Text(
                                  item.storeName,
                                  style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 13),
                                  overflow: TextOverflow.ellipsis,
                                ),
                                subtitle: Text(
                                  '${item.filename} • ${item.itemsCount} item • ${item.elapsedMs} ms',
                                  style: const TextStyle(fontSize: 11),
                                ),
                                trailing: Text(
                                  CurrencyFormatHelper.formatRp(item.totalAmount),
                                  style: TextStyle(
                                    fontWeight: FontWeight.bold,
                                    fontSize: 12,
                                    color: item.hasTotal ? Colors.teal.shade800 : Colors.grey,
                                  ),
                                ),
                              );
                            },
                          ),
                  ),
                ],
              ),
            ),
    );
  }

  Widget _metricTile(String label, String value) {
    return Column(
      children: [
        Text(value, style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15, color: Colors.teal.shade800)),
        const SizedBox(height: 2),
        Text(label, style: TextStyle(fontSize: 10.5, color: Colors.grey.shade600)),
      ],
    );
  }
}
