// =============================================================================
// ALUR SISTEM: DASHBOARD SCREEN (BERANDA & ORKESTRATOR ALUR PENGGUNA)
// =============================================================================
// Peran dalam Arsitektur:
// 1. INPUT DARI DATABASE:
//    - _loadTransactions() -> Membaca data pengeluaran dari SQLite lokal
//    - Menghitung total belanja bulan ini & data tren pengeluaran mingguan/bulanan
// 2. NAVIGASI KE SCANNER (ALUR SCAN STRUK):
//    - Pengguna menekan tombol Floating Action Button (Kamera)
//    - Membuka ScannerScreen() -> menerima kembalian String imagePath
//    - Memanggil _processReceipt(imagePath):
//        a. Mengeksekusi OfflineReceiptService.extractReceipt(imagePath)
//        b. Mencatat log audit ke DatabaseHelper.insertScanLog(...)
//        c. Membuka PreviewEditScreen(initialTransaction: parsedTrx)
// 3. NAVIGASI KE CATAT MANUAL:
//    - Membuka PreviewEditScreen() dengan form kosong
// 4. NAVIGASI KE DETAIL / EDIT TRANSAKSI:
//    - Membuka ItemDetailScreen(transactionId: txn.id)
// 5. OUTPUT:
//    - Menyajikan visualisasi grafik pengeluaran, daftar riwayat terfilter, dan ekspor CSV
// =============================================================================

import 'dart:convert';
import 'dart:io';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:intl/intl.dart';
import 'package:path_provider/path_provider.dart';

import '../db/database_helper.dart';
import '../models/transaction.dart';
import '../models/transaction_item.dart';
import '../services/offline_receipt_service.dart';
import '../utils/currency_format_helper.dart';
import 'item_detail_screen.dart';
import 'preview_edit_screen.dart';
import 'scanner_screen.dart';
import 'benchmark_screen.dart';

/// Halaman Utama (Dashboard) Aplikasi Pencatat Pengeluaran Pribadi
///
/// Berbasis arsitektur **Offline-First**:
/// - Pemrosesan struk 100% lokal di perangkat (On-Device ML Kit)
/// - Waktu ekstraksi super cepat (< 300 ms)
/// - Penyimpanan transaksi lokal SQLite tanpa internet / server
class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  List<Transaction> _transactions = [];
  Map<String, double> _monthlyTotals = {};

  // Pencarian Riwayat & Filter
  String _searchQuery = '';
  String _selectedFilter = 'Semua';
  final TextEditingController _searchController = TextEditingController();

  // Status pemrosesan struk offline
  bool _isProcessing = false;
  String _processingStatus = '';

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final trxList = await DatabaseHelper.instance.getAllTransactions(includeItems: true);
    final monthly = await DatabaseHelper.instance.getMonthlyTotals();
    if (mounted) {
      setState(() {
        _transactions = trxList;
        _monthlyTotals = monthly;
      });
    }
  }

  Future<void> _openScanner() async {
    if (_isProcessing) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Sedang memproses struk sebelumnya, mohon tunggu...'),
          duration: Duration(seconds: 2),
        ),
      );
      return;
    }

    final imagePath = await Navigator.of(context).push<String>(
      MaterialPageRoute(
        builder: (_) => const ScannerScreen(),
      ),
    );

    if (imagePath != null && mounted) {
      _processReceipt(imagePath);
    }
  }

  /// Ekstraksi struk 100% lokal On-Device via Google ML Kit (< 300 ms)
  Future<void> _processReceipt(String imagePath) async {
    setState(() {
      _isProcessing = true;
      _processingStatus = 'Mengekstraksi teks struk di perangkat (< 300 ms)...';
    });

    try {
      final result = await OfflineReceiptService.extractReceipt(imagePath);
      final parsedTrx = result.transaction;
      final executionTimeMs = result.executionTimeMs;
      final rawOutput = result.rawOutput;

      // Catat log audit / debugging ke database SQLite
      await DatabaseHelper.instance.insertScanLog(
        imagePath: imagePath,
        inferenceMode: 'on_device_mlkit',
        executionTimeMs: executionTimeMs,
        detectedStore: parsedTrx.storeName,
        detectedTotal: parsedTrx.totalAmount,
        itemCount: parsedTrx.items.length,
        rawSnippet: rawOutput,
        status: parsedTrx.totalAmount > 0 && parsedTrx.storeName != 'Toko Tidak Dikenal'
            ? 'SUCCESS'
            : 'WARNING',
      );

      if (!mounted) return;
      setState(() => _isProcessing = false);

      // Buka layar Pratinjau & Edit dengan data yang sudah terisi otomatis
      await Navigator.of(context).push<bool>(
        MaterialPageRoute(
          builder: (_) => PreviewEditScreen(
            transaction: parsedTrx,
            executionTimeMs: executionTimeMs,
            modelName: 'On-Device Machine Learning (ML Kit)',
            isDateEstimated: result.isDateEstimated,
          ),
        ),
      );

      // Selalu refresh dashboard setelah kembali dari form edit / item detail
      if (mounted) {
        _load();
      }
    } catch (e) {
      try {
        await DatabaseHelper.instance.insertScanLog(
          imagePath: imagePath,
          inferenceMode: 'on_device_mlkit',
          executionTimeMs: 0,
          detectedStore: 'ERROR',
          detectedTotal: 0,
          itemCount: 0,
          rawSnippet: '',
          status: 'ERROR',
          errorMessage: e.toString(),
        );
      } catch (_) {}

      if (mounted) {
        setState(() => _isProcessing = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Gagal memproses struk: $e'),
            backgroundColor: Colors.red.shade700,
            duration: const Duration(seconds: 4),
          ),
        );
      }
    } finally {
      // Hapus file citra sementara di cache kamera/galeri untuk mencegah kebocoran penyimpanan
      try {
        final tempFile = File(imagePath);
        if (await tempFile.exists()) {
          await tempFile.delete();
        }
      } catch (_) {}
    }
  }

  /// Membuka form pencatatan manual tanpa struk fisik (Full CRUD)
  Future<void> _openManualInput() async {
    final now = DateTime.now();
    final manualTrx = Transaction(
      storeName: '',
      totalAmount: 0,
      transactionDate: now,
      items: [
        TransactionItem(itemName: 'Item belanja', itemPrice: 0, quantity: 1),
      ],
    );

    await Navigator.of(context).push<bool>(
      MaterialPageRoute(
        builder: (_) => PreviewEditScreen(
          transaction: manualTrx,
        ),
      ),
    );

    if (mounted) {
      _load();
    }
  }

  /// Ekspor Riwayat Transaksi ke File CSV (Excel Compatible)
  Future<void> _exportToCsv() async {
    if (_transactions.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Belum ada transaksi untuk diekspor.')),
      );
      return;
    }

    try {
      final allTrx = await DatabaseHelper.instance.getAllTransactions(includeItems: true);
      final sb = StringBuffer();
      // Baris Header CSV
      sb.writeln('ID_Transaksi,Tanggal,Toko_Merchant,Nama_Barang,Qty,Harga_Satuan,Subtotal_Barang,Total_Transaksi');

      var totalItemCount = 0;
      var grandTotal = 0.0;

      for (final trx in allTrx) {
        grandTotal += trx.totalAmount;
        final dateStr = DateFormat('yyyy-MM-dd HH:mm').format(trx.transactionDate);
        final safeStore = '"${trx.storeName.replaceAll('"', '""')}"';

        if (trx.items.isEmpty) {
          sb.writeln('${trx.id},$dateStr,$safeStore,"-",0,0,0,${trx.totalAmount.toStringAsFixed(0)}');
        } else {
          for (var itemIdx = 0; itemIdx < trx.items.length; itemIdx++) {
            final item = trx.items[itemIdx];
            totalItemCount++;
            final safeItemName = '"${item.itemName.replaceAll('"', '""')}"';
            // Tulis Total_Transaksi hanya pada baris pertama item agar tidak terhitung ganda saat di-SUM di spreadsheet
            final totalField = itemIdx == 0 ? trx.totalAmount.toStringAsFixed(0) : '';
            sb.writeln(
                '${trx.id},$dateStr,$safeStore,$safeItemName,${item.quantity},${item.itemPrice.toStringAsFixed(0)},${item.subtotal.toStringAsFixed(0)},$totalField');
          }
        }
      }

      Directory? targetDir;
      try {
        final downloadDir = Directory('/storage/emulated/0/Download');
        if (await downloadDir.exists()) {
          targetDir = downloadDir;
        }
      } catch (_) {}

      try {
        targetDir ??= await getExternalStorageDirectory();
      } catch (_) {}
      targetDir ??= await getApplicationDocumentsDirectory();

      final timestamp = DateFormat('yyyyMMdd_HHmmss').format(DateTime.now());
      final filePath = '${targetDir.path}/laporan_pengeluaran_$timestamp.csv';
      final file = File(filePath);
      await file.writeAsString(sb.toString(), encoding: utf8);

      if (!mounted) return;
      showDialog(
        context: context,
        builder: (ctx) => AlertDialog(
          title: const Row(
            children: [
              Icon(Icons.check_circle, color: Colors.teal),
              SizedBox(width: 8),
              Text('Ekspor CSV Berhasil!'),
            ],
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Total Transaksi : ${allTrx.length} data'),
              Text('Total Baris Item : $totalItemCount item'),
              Text('Total Pengeluaran: ${CurrencyFormatHelper.formatRp(grandTotal)}'),
              const SizedBox(height: 12),
              const Text('Lokasi File Tersimpan:', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
              SelectableText(
                filePath,
                style: const TextStyle(fontSize: 11, color: Colors.teal),
              ),
              const SizedBox(height: 8),
              const Text(
                '💡 File CSV ini dapat dibuka langsung menggunakan Microsoft Excel atau Google Sheets.',
                style: TextStyle(fontSize: 11, color: Colors.grey),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(ctx),
              child: const Text('Tutup'),
            ),
          ],
        ),
      );
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Gagal mengekspor CSV: $e'),
            backgroundColor: Colors.red.shade700,
          ),
        );
      }
    }
  }

  Future<void> _showStorageCleanDialog() async {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (ctx) => const Center(child: CircularProgressIndicator()),
    );

    final report = await DatabaseHelper.instance.auditAndCleanStorage(performCleanup: true);

    if (!mounted) return;
    Navigator.of(context).pop();

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Row(
          children: [
            Icon(Icons.cleaning_services, color: Colors.teal),
            SizedBox(width: 8),
            Text('Pembersihan Penyimpanan', style: TextStyle(fontSize: 16)),
          ],
        ),
        content: SizedBox(
          width: double.maxFinite,
          child: SingleChildScrollView(
            child: Text(
              report,
              style: const TextStyle(fontFamily: 'monospace', fontSize: 11),
            ),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: const Text('Tutup'),
          ),
        ],
      ),
    );
  }

  Future<void> _showScanLogsDialog() async {
    final logs = await DatabaseHelper.instance.getScanLogs();
    if (!mounted) return;

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) {
        return DraggableScrollableSheet(
          initialChildSize: 0.7,
          minChildSize: 0.4,
          maxChildSize: 0.95,
          expand: false,
          builder: (_, scrollController) {
            return StatefulBuilder(
              builder: (sheetContext, setSheetState) {
                return Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Text(
                            'Audit & Log Scan Struk',
                            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                          ),
                          IconButton(
                            icon: const Icon(Icons.delete_sweep_outlined, color: Colors.red),
                            tooltip: 'Bersihkan Log',
                            onPressed: () async {
                              await DatabaseHelper.instance.clearScanLogs();
                              if (sheetContext.mounted) {
                                Navigator.pop(sheetContext);
                              }
                            },
                          ),
                        ],
                      ),
                      const Text(
                        'Jejak komputasi, deteksi toko, total, waktu, dan teks mentah:',
                        style: TextStyle(fontSize: 12, color: Colors.grey),
                      ),
                      const Divider(height: 16),
                      Expanded(
                        child: logs.isEmpty
                            ? const Center(
                                child: Text('Belum ada riwayat log scan.'),
                              )
                            : ListView.separated(
                                controller: scrollController,
                                itemCount: logs.length,
                                separatorBuilder: (_, __) => const Divider(),
                                itemBuilder: (_, idx) {
                                  final log = logs[idx];
                                  final isSuccess = log['status'] == 'SUCCESS';
                                  return ListTile(
                                    dense: true,
                                    leading: CircleAvatar(
                                      radius: 16,
                                      backgroundColor: isSuccess
                                          ? Colors.green.shade100
                                          : Colors.orange.shade100,
                                      child: Icon(
                                        isSuccess ? Icons.check : Icons.warning_amber,
                                        size: 18,
                                        color: isSuccess
                                            ? Colors.green.shade800
                                            : Colors.orange.shade800,
                                      ),
                                    ),
                                    title: Text(
                                      '${log['detected_store']} • ${CurrencyFormatHelper.formatRp((log['detected_total'] as num).toDouble())}',
                                      style: const TextStyle(fontWeight: FontWeight.bold),
                                    ),
                                    subtitle: Text(
                                      'Waktu: ${log['execution_time_ms']} ms • Items: ${log['item_count']} • Mode: ${log['inference_mode']}\n${log['timestamp']}',
                                      style: const TextStyle(fontSize: 11),
                                    ),
                                    trailing: Text(
                                      log['status'] as String? ?? '',
                                      style: TextStyle(
                                        fontSize: 11,
                                        fontWeight: FontWeight.bold,
                                        color: isSuccess ? Colors.green : Colors.orange,
                                      ),
                                    ),
                                  );
                                },
                              ),
                      ),
                    ],
                  ),
                );
              },
            );
          },
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final months = _monthlyTotals.keys.toList()..sort();
    final barGroups = <BarChartGroupData>[
      for (var i = 0; i < months.length; i++)
        BarChartGroupData(x: i, barRods: [
          BarChartRodData(
            toY: _monthlyTotals[months[i]]!,
            width: 18,
            borderRadius: BorderRadius.circular(4),
            color: Colors.teal.shade700,
          ),
        ]),
    ];

    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Caran',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 19),
            ),
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: Colors.teal.shade700,
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: const Text(
                    'BETA v0.10.0',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 9,
                      fontWeight: FontWeight.bold,
                      letterSpacing: 0.5,
                    ),
                  ),
                ),
                const SizedBox(width: 6),
                Text(
                  'Catat Pengeluaran • Secara Offline',
                  style: TextStyle(fontSize: 10.5, color: Colors.grey.shade600),
                ),
              ],
            ),
          ],
        ),
        actions: [
          if (kDebugMode)
            IconButton(
              icon: const Icon(Icons.analytics_outlined),
              tooltip: 'Uji Benchmark CORD (Bab IV)',
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (_) => const BenchmarkScreen()),
                );
              },
            ),
          IconButton(
            icon: const Icon(Icons.cleaning_services_outlined),
            tooltip: 'Diagnostik & Bersihkan Penyimpanan',
            onPressed: _showStorageCleanDialog,
          ),
          IconButton(
            icon: const Icon(Icons.history_edu),
            tooltip: 'Riwayat Pemindaian Struk',
            onPressed: _showScanLogsDialog,
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            tooltip: 'Muat Ulang Data',
            onPressed: _load,
          ),
        ],
      ),
      floatingActionButton: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          FloatingActionButton.small(
            heroTag: 'fab_manual_input',
            backgroundColor: Colors.teal.shade50,
            foregroundColor: Colors.teal.shade800,
            tooltip: 'Catat Manual Tanpa Struk',
            onPressed: _openManualInput,
            child: const Icon(Icons.edit),
          ),
          const SizedBox(height: 10),
          FloatingActionButton.extended(
            heroTag: 'fab_scan_receipt',
            onPressed: _openScanner,
            icon: const Icon(Icons.document_scanner),
            label: const Text('Scan Struk'),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _load,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // Banner Arsitektur Offline-First
            Card(
              elevation: 0,
              color: Colors.teal.shade50.withValues(alpha: 0.8),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
                side: BorderSide(color: Colors.teal.shade200),
              ),
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                child: Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: Colors.teal.shade100,
                        shape: BoxShape.circle,
                      ),
                      child: Icon(
                        Icons.shield_outlined,
                        color: Colors.teal.shade800,
                        size: 22,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Text(
                                'Sistem: Offline On-Device',
                                style: TextStyle(
                                  fontSize: 13,
                                  fontWeight: FontWeight.bold,
                                  color: Colors.teal.shade900,
                                ),
                              ),
                              const SizedBox(width: 6),
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                decoration: BoxDecoration(
                                  color: Colors.teal.shade700,
                                  borderRadius: BorderRadius.circular(4),
                                ),
                                child: const Text(
                                  'ON-DEVICE ML',
                                  style: TextStyle(
                                    color: Colors.white,
                                    fontSize: 9,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 2),
                          Text(
                            'Ekstraksi struk diproses privat di HP • Tanpa kuota internet • ~0.2 detik',
                            style: TextStyle(
                              fontSize: 11,
                              color: Colors.teal.shade800,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 14),

            // Indikator Pemrosesan Struk
            if (_isProcessing) ...[
              Card(
                color: Colors.teal.shade50,
                elevation: 2,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                  side: BorderSide(color: Colors.teal.shade300),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(14),
                  child: Row(
                    children: [
                      const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(
                          strokeWidth: 2.5,
                          color: Colors.teal,
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          _processingStatus,
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w600,
                            color: Colors.teal.shade900,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 14),
            ],

            // Card Total Pengeluaran Bulan Ini
            Card(
              elevation: 1,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Total Pengeluaran Bulan Ini',
                      style: Theme.of(context).textTheme.titleSmall?.copyWith(
                            color: Colors.grey.shade600,
                          ),
                    ),
                    const SizedBox(height: 8),
                    Builder(builder: (context) {
                      final currentYm = DateFormat('yyyy-MM').format(DateTime.now());
                      final currentMonthTotal = _monthlyTotals[currentYm] ?? 0.0;
                      return Text(
                        CurrencyFormatHelper.formatRp(currentMonthTotal),
                        style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                              fontWeight: FontWeight.bold,
                              color: Colors.teal.shade800,
                            ),
                      );
                    }),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),

            // Card Grafik Tren Pengeluaran
            if (months.isNotEmpty) ...[
              Card(
                elevation: 1,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Tren Pengeluaran per Bulan',
                        style: Theme.of(context).textTheme.titleMedium,
                      ),
                      const SizedBox(height: 16),
                      SizedBox(
                        height: 200,
                        child: BarChart(
                          BarChartData(
                            barGroups: barGroups,
                            titlesData: FlTitlesData(
                              bottomTitles: AxisTitles(
                                sideTitles: SideTitles(
                                  showTitles: true,
                                  getTitlesWidget: (val, meta) {
                                    final idx = val.toInt();
                                    if (idx < 0 || idx >= months.length) {
                                      return const SizedBox.shrink();
                                    }
                                    return Padding(
                                      padding: const EdgeInsets.only(top: 8),
                                      child: Text(
                                        months[idx],
                                        style: const TextStyle(fontSize: 10),
                                      ),
                                    );
                                  },
                                ),
                              ),
                              leftTitles: const AxisTitles(
                                sideTitles: SideTitles(showTitles: false),
                              ),
                              topTitles: const AxisTitles(
                                sideTitles: SideTitles(showTitles: false),
                              ),
                              rightTitles: const AxisTitles(
                                sideTitles: SideTitles(showTitles: false),
                              ),
                            ),
                            borderData: FlBorderData(show: false),
                            gridData: const FlGridData(show: false),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),
            ],

            // Header Riwayat Transaksi & Ekspor CSV
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Riwayat Transaksi',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
                TextButton.icon(
                  onPressed: _exportToCsv,
                  icon: const Icon(Icons.file_download_outlined, size: 18),
                  label: const Text('Ekspor CSV', style: TextStyle(fontSize: 12)),
                  style: TextButton.styleFrom(
                    foregroundColor: Colors.teal.shade800,
                    visualDensity: VisualDensity.compact,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 6),

            // Kolom Pencarian Riwayat Transaksi
            TextField(
              controller: _searchController,
              decoration: InputDecoration(
                hintText: 'Cari nama toko atau barang...',
                prefixIcon: const Icon(Icons.search, size: 20),
                suffixIcon: _searchQuery.isNotEmpty
                    ? IconButton(
                        icon: const Icon(Icons.clear, size: 18),
                        onPressed: () {
                          _searchController.clear();
                          setState(() => _searchQuery = '');
                        },
                      )
                    : null,
                contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                isDense: true,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(10),
                  borderSide: BorderSide(color: Colors.grey.shade300),
                ),
                enabledBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(10),
                  borderSide: BorderSide(color: Colors.grey.shade300),
                ),
                filled: true,
                fillColor: Colors.grey.shade50,
              ),
              onChanged: (val) => setState(() => _searchQuery = val),
            ),
            const SizedBox(height: 10),

            // Filter Rentang Tanggal Cepat
            SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: ['Semua', 'Hari Ini', '7 Hari Terakhir', 'Bulan Ini'].map((filterName) {
                  final isSelected = _selectedFilter == filterName;
                  return Padding(
                    padding: const EdgeInsets.only(right: 8),
                    child: FilterChip(
                      selected: isSelected,
                      label: Text(filterName, style: TextStyle(fontSize: 12, fontWeight: isSelected ? FontWeight.bold : FontWeight.normal)),
                      selectedColor: Colors.teal.shade100,
                      checkmarkColor: Colors.teal.shade800,
                      onSelected: (val) {
                        if (val) setState(() => _selectedFilter = filterName);
                      },
                    ),
                  );
                }).toList(),
              ),
            ),
            const SizedBox(height: 12),

            Builder(
              builder: (ctx) {
                final filteredList = _transactions.where((t) {
                  // 1. Filter Waktu
                  final now = DateTime.now();
                  if (_selectedFilter == 'Hari Ini') {
                    if (t.transactionDate.year != now.year ||
                        t.transactionDate.month != now.month ||
                        t.transactionDate.day != now.day) {
                      return false;
                    }
                  } else if (_selectedFilter == '7 Hari Terakhir') {
                    final diff = now.difference(t.transactionDate).inDays;
                    if (diff < 0 || diff > 7) return false;
                  } else if (_selectedFilter == 'Bulan Ini') {
                    if (t.transactionDate.year != now.year ||
                        t.transactionDate.month != now.month) {
                      return false;
                    }
                  }

                  // 2. Filter Pencarian
                  if (_searchQuery.trim().isEmpty) return true;
                  final q = _searchQuery.toLowerCase().trim();
                  final matchStore = t.storeName.toLowerCase().contains(q);
                  final matchCategory = t.category.toLowerCase().contains(q);
                  final matchItem =
                      t.items.any((it) => it.itemName.toLowerCase().contains(q));
                  return matchStore || matchCategory || matchItem;
                }).toList();

                if (filteredList.isEmpty) {
                  return Padding(
                    padding: const EdgeInsets.all(32),
                    child: Column(
                      children: [
                        Icon(Icons.receipt_long_outlined,
                            size: 48, color: Colors.grey.shade400),
                        const SizedBox(height: 12),
                        Text(
                          _searchQuery.isEmpty && _selectedFilter == 'Semua'
                              ? 'Belum ada transaksi tersimpan.\nTekan tombol "Scan Struk" untuk memulai.'
                              : 'Tidak ditemukan transaksi yang cocok dengan filter.',
                          textAlign: TextAlign.center,
                          style: TextStyle(color: Colors.grey.shade600),
                        ),
                      ],
                    ),
                  );
                }

                return ListView.builder(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  itemCount: filteredList.length,
                  itemBuilder: (ctx, idx) {
                    final trx = filteredList[idx];
                    return Card(
                      margin: const EdgeInsets.only(bottom: 8),
                      elevation: 0.5,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(10),
                        side: BorderSide(color: Colors.grey.shade200),
                      ),
                      child: ListTile(
                        leading: CircleAvatar(
                          backgroundColor: Colors.teal.shade50,
                          child: Icon(Icons.store, color: Colors.teal.shade700),
                        ),
                        title: Row(
                          children: [
                            Expanded(
                              child: Text(
                                trx.storeName,
                                style: const TextStyle(fontWeight: FontWeight.bold),
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                              decoration: BoxDecoration(
                                color: Colors.teal.shade50,
                                borderRadius: BorderRadius.circular(6),
                                border: Border.all(color: Colors.teal.shade200),
                              ),
                              child: Text(
                                trx.category,
                                style: TextStyle(
                                  fontSize: 10,
                                  color: Colors.teal.shade800,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                            ),
                          ],
                        ),
                        subtitle: Text(
                          '${DateFormat('dd MMM yyyy').format(trx.transactionDate)} • ${trx.items.length} item',
                          style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
                        ),
                        trailing: Text(
                          CurrencyFormatHelper.formatRp(trx.totalAmount),
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            color: Colors.teal.shade800,
                            fontSize: 14,
                          ),
                        ),
                        onTap: () async {
                          if (trx.id != null) {
                            await Navigator.of(context).push(
                              MaterialPageRoute(
                                builder: (_) => ItemDetailScreen(transactionId: trx.id!),
                              ),
                            );
                            _load();
                          }
                        },
                      ),
                    );
                  },
                );
              },
            ),
          ],
        ),
      ),
    );
  }
}
