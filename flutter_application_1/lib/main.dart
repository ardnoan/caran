// =============================================================================
// ALUR SISTEM APLIKASI "CARAN" (CATAT PENGELUARAN - OFFLINE-FIRST EDGE ML)
// =============================================================================
// File ini adalah Titik Masuk Utama (Application Bootstrap / Entry Point).
//
// DIAGRAM ALUR EKSEKUSI APLIKASI (END-TO-END FLOW TRACING):
//
// 1. [main.dart] (Entry Point)
//    │   • WidgetsFlutterBinding & locale id_ID diinisialisasi
//    │   • OfflineReceiptService.warmUp() dipanggil di latar belakang
//    │     (memuat mesin C++ Google ML Kit TextRecognizer ke RAM agar inferensi instan < 200 ms)
//    ▼
// 2. [screens/dashboard_screen.dart] (Beranda & Pusat Navigasi)
//    │   • Membaca data transaksi bulan ini & ringkasan saldo dari SQLite lokal
//    │   • Menampilkan grafik tren fl_chart, filter rentang tanggal, & live search
//    │   • Aksi Pengguna:
//    │       ├── Tombol Kamera FloatingActionButton -> Buka [3. ScannerScreen]
//    │       ├── Tombol Catat Manual -> Buka [5. PreviewEditScreen] (form kosong)
//    │       └── Klik Baris Riwayat Transaksi -> Buka [screens/item_detail_screen.dart]
//    ▼
// 3. [screens/scanner_screen.dart] (Pengambilan Citra Struk)
//    │   • Mengaktifkan kamera fisik (Resolusi High, Viewfinder Kotak Panduan, Toggle Senter/Torch)
//    │   • Pengguna memotret struk atau memilih dari galeri HP
//    │   • Mengembalikan path file gambar lokal (String imagePath) ke DashboardScreen
//    ▼
// 4. [services/offline_receipt_service.dart] (Pipa Ekstraksi Edge ML On-Device)
//    │   • Dipanggil oleh DashboardScreen._processReceipt(imagePath)
//    │   • Langkah A: Ekstraksi teks & koordinat bounding box via Google ML Kit Native C++
//    │   • Langkah B: Spatial Line Clustering (_reconstructSpatialLines) -> menyatukan kolom
//    │                kiri (nama barang) dan kanan (harga) berdasarkan irisan koordinat vertikal Y
//    │   • Langkah C: Hierarchical Heuristic Regex Engine:
//    │                - Brand ritel (Alfamart, Indomaret, Superindo, dsb.)
//    │                - Tanggal transaksi (DD-MM-YYYY, teks bulan Indonesia)
//    │                - Nominal total belanja & filter baris derau (NPWP, kasir, PPN)
//    │                - Pemilahan item barang, kuantitas, harga, dan diskon minus VC kasir
//    │   • Langkah D: Rekam log audit inferensi ke tabel SQLite 'scan_logs'
//    │   • Output: Objek Transaction & raw XML snippet CORD-v2
//    ▼
// 5. [screens/preview_edit_screen.dart] (Form Verifikasi & Koreksi Pengguna)
//    │   • Menerima data hasil ekstraksi otomatis ML Kit
//    │   • CurrencyTextInputFormatter: Live formatting pemisah ribuan titik (contoh: 18.000)
//    │   • Tampilan visual Subtotal per baris item (Qty x Harga = Subtotal)
//    │   • Auto-sync total kalkulasi Σ(item) & banner peringatan jika total struk berbeda
//    │   • Dropdown Kategori Pengeluaran (Belanja Harian, Makanan, Transportasi, dsb.)
//    │   • Proteksi pembatalan tak disengaja via PopScope
//    │   • Pengguna menekan tombol "Simpan Transaksi"
//    ▼
// 6. [db/database_helper.dart] (Persistensi Basis Data Relasional SQLite Lokal)
//    │   • Menyimpan transaksi ke tabel 'transactions' & rincian barang ke 'transaction_items'
//    │   • Database disimpan di internal storage: receipt_scanner.db (100% Offline)
//    ▼
// 7. [screens/dashboard_screen.dart] (Sinkronisasi Tampilan)
//        • Kembali ke beranda, memicu _loadTransactions(), saldo & grafik ter-update instan.
// =============================================================================

import 'package:flutter/material.dart';
import 'package:intl/date_symbol_data_local.dart';

import 'db/database_helper.dart';
import 'screens/dashboard_screen.dart';
import 'services/offline_receipt_service.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await initializeDateFormatting('id_ID', null);

  // Inisialisasi awal mesin ekstraksi offline-first agar warm start (< 200 ms)
  OfflineReceiptService.warmUp();

  // Pembersihan folder legacy foto struk & artefak dev agar penyimpanan tetap bersih
  await DatabaseHelper.instance.cleanLegacyReceiptImages();

  runApp(const ReceiptScannerApp());
}

class ReceiptScannerApp extends StatelessWidget {
  const ReceiptScannerApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Caran',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.teal),
        useMaterial3: true,
      ),
      home: const DashboardScreen(),
    );
  }
}
