// =============================================================================
// ALUR SISTEM: DATABASE HELPER (LAPISAN PERSISTENSI RELASIONAL SQLITE LOKAL)
// =============================================================================
// Peran dalam Arsitektur:
// Penyimpanan basis data relasional SQLite lokal bernama `receipt_scanner.db`.
// 100% Offline-First: Tidak ada panggilan jaringan, server, atau cloud.
//
// SKEMA RELASI TABEL:
// 1. Tabel `transactions`:
//    - id (INTEGER PRIMARY KEY AUTOINCREMENT)
//    - store_name (TEXT)
//    - category (TEXT DEFAULT 'Belanja Harian')
//    - total_amount (REAL)
//    - transaction_date (TEXT ISO-8601)
//    - image_path (TEXT nullable)
//    - created_at (TEXT)
// 2. Tabel `transaction_items` (Foreign Key ON DELETE CASCADE):
//    - id (INTEGER PRIMARY KEY)
//    - transaction_id (INTEGER FK -> transactions.id)
//    - item_name (TEXT)
//    - item_price (REAL)
//    - quantity (INTEGER)
// 3. Tabel `scan_logs` (Audit Log Pengujian & Riset On-Device):
//    - id, timestamp, execution_time_ms, detected_store, detected_total, status, error_message
// 4. Indeks Relasional (Kueri Cepat & Skalabilitas - BAB 3.6.3):
//    - idx_transactions_date ON transactions(transaction_date)
//    - idx_items_transaction_id ON transaction_items(transaction_id)
// =============================================================================

import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:path/path.dart';
import 'package:path_provider/path_provider.dart';
// sqflite juga punya kelas bernama `Transaction` (dipakai untuk parameter
// `txn` di dalam callback db.transaction()), yang bentrok dengan model
// `Transaction` kita sendiri di bawah. Kita sembunyikan versi sqflite-nya
// karena kita tidak pernah menulis tipe `Transaction` itu secara eksplisit
// (parameter `txn` cukup diinfer otomatis dari closure-nya).
import 'package:sqflite/sqflite.dart' hide Transaction;

import '../models/transaction.dart';
import '../models/transaction_item.dart';

/// Helper basis data SQLite lokal, sesuai rancangan BAB 3.3 pada naskah
/// skripsi:
/// - transactions(id, store_name, total_amount, transaction_date, image_path, created_at)
/// - transaction_items(id, transaction_id FK, item_name, item_price, quantity)
///
/// Pendekatan Offline-First: tidak ada satu pun panggilan jaringan di file
/// ini — seluruh data tersimpan di device (BAB II.5).
class DatabaseHelper {
  DatabaseHelper._internal();
  static final DatabaseHelper instance = DatabaseHelper._internal();

  static Database? _db;

  Future<Database> get database async {
    if (_db != null) return _db!;
    _db = await _initDb();
    return _db!;
  }

  Future<Database> _initDb() async {
    final dbPath = await getDatabasesPath();
    final path = join(dbPath, 'receipt_scanner.db');

    return openDatabase(
      path,
      version: 1,
      onConfigure: (db) async {
        // Wajib agar ON DELETE CASCADE pada transaction_items berjalan.
        await db.execute('PRAGMA foreign_keys = ON');
      },
      onOpen: (db) async {
        // Buat tabel scan_logs jika belum ada (audit trail / debugging log)
        await db.execute('''
          CREATE TABLE IF NOT EXISTS scan_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            image_path TEXT,
            inference_mode TEXT NOT NULL,
            execution_time_ms INTEGER NOT NULL,
            detected_store TEXT NOT NULL,
            detected_total REAL NOT NULL,
            item_count INTEGER NOT NULL,
            raw_snippet TEXT,
            status TEXT NOT NULL,
            error_message TEXT
          )
        ''');

        // Pastikan kolom category ada di tabel transactions (migrasi non-destruktif)
        try {
          await db.execute("ALTER TABLE transactions ADD COLUMN category TEXT NOT NULL DEFAULT 'Belanja Harian'");
        } catch (_) {
          // Kolom category sudah ada sebelumnya
        }

        // Indeks relasional untuk mempercepat query berdasarkan tanggal dan relasi item (BAB 3.6.3)
        await db.execute('CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date)');
        await db.execute('CREATE INDEX IF NOT EXISTS idx_items_transaction_id ON transaction_items(transaction_id)');
      },
      onCreate: (db, version) async {
        await db.execute('''
          CREATE TABLE transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            store_name TEXT NOT NULL,
            category TEXT NOT NULL DEFAULT 'Belanja Harian',
            total_amount REAL NOT NULL DEFAULT 0,
            transaction_date TEXT NOT NULL,
            image_path TEXT,
            created_at TEXT NOT NULL
          )
        ''');

        await db.execute('''
          CREATE TABLE transaction_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id INTEGER NOT NULL,
            item_name TEXT NOT NULL,
            item_price REAL NOT NULL DEFAULT 0,
            quantity INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (transaction_id) REFERENCES transactions (id)
              ON DELETE CASCADE
          )
        ''');

        await db.execute('''
          CREATE TABLE IF NOT EXISTS scan_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            image_path TEXT,
            inference_mode TEXT NOT NULL,
            execution_time_ms INTEGER NOT NULL,
            detected_store TEXT NOT NULL,
            detected_total REAL NOT NULL,
            item_count INTEGER NOT NULL,
            raw_snippet TEXT,
            status TEXT NOT NULL,
            error_message TEXT
          )
        ''');

        // Indeks Relasional (BAB 3.6.3)
        await db.execute('CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date)');
        await db.execute('CREATE INDEX IF NOT EXISTS idx_items_transaction_id ON transaction_items(transaction_id)');
      },
    );
  }

  /// Menyimpan transaksi hasil scan (atau input manual) beserta seluruh
  /// item-nya dalam satu database transaction (atomic).
  Future<int> insertTransaction(Transaction trx) async {
    final db = await database;
    return db.transaction<int>((txn) async {
      final trxId = await txn.insert('transactions', trx.toMap()..remove('id'));
      for (final item in trx.items) {
        await txn.insert(
          'transaction_items',
          item.copyWith(transactionId: trxId).toMap()..remove('id'),
        );
      }
      return trxId;
    });
  }

  Future<void> updateTransaction(Transaction trx) async {
    if (trx.id == null) {
      throw ArgumentError('Transaction.id tidak boleh null saat update');
    }
    final db = await database;
    await db.transaction((txn) async {
      await txn.update(
        'transactions',
        trx.toMap()..remove('id'),
        where: 'id = ?',
        whereArgs: [trx.id],
      );
      await txn.delete(
        'transaction_items',
        where: 'transaction_id = ?',
        whereArgs: [trx.id],
      );
      for (final item in trx.items) {
        await txn.insert(
          'transaction_items',
          item.copyWith(transactionId: trx.id).toMap()..remove('id'),
        );
      }
    });
  }

  Future<void> deleteTransaction(int id) async {
    final db = await database;
    // Hapus file fisik gambar jika sebelumnya pernah tersimpan di sistem
    final rows = await db.query('transactions', columns: ['image_path'], where: 'id = ?', whereArgs: [id]);
    if (rows.isNotEmpty && rows.first['image_path'] != null) {
      final imgPath = rows.first['image_path'] as String;
      try {
        final f = File(imgPath);
        if (await f.exists()) await f.delete();
      } catch (_) {}
    }
    await db.delete('transactions', where: 'id = ?', whereArgs: [id]);
  }

  /// Membersihkan sisa folder foto struk warisan (legacy) jika masih ada di internal storage
  Future<void> cleanLegacyReceiptImages() async {
    await auditAndCleanStorage(performCleanup: true);
  }

  /// Audit dan bersihkan sisa file cache, foto struk warisan, atau artefak dev
  /// tanpa merusak tabel database SQLite (receipt_scanner.db) dan preferensi pengguna.
  Future<String> auditAndCleanStorage({bool performCleanup = true}) async {
    final sb = StringBuffer();
    sb.writeln('=== CARAN STORAGE DIAGNOSTIC & CLEANUP AUDIT ===');
    sb.writeln('Waktu: ${DateTime.now().toIso8601String()}');

    int totalBytesBefore = 0;
    int totalFreedBytes = 0;
    int filesFound = 0;
    int filesDeleted = 0;

    try {
      final docDir = await getApplicationDocumentsDirectory();
      final rootDir = docDir.parent; // /data/user/0/com.example.flutter_application_1/

      sb.writeln('Root App Data: ${rootDir.path}');

      if (await rootDir.exists()) {
        final entries = rootDir.listSync(recursive: true, followLinks: false);
        for (final entry in entries) {
          if (entry is File) {
            filesFound++;
            int size = 0;
            try {
              size = entry.lengthSync();
            } catch (_) {}
            totalBytesBefore += size;
            final relPath = entry.path.replaceFirst('${rootDir.path}/', '');
            final fileName = basename(entry.path).toLowerCase();
            final isDb = fileName.contains('receipt_scanner.db') ||
                fileName.contains('.db') ||
                fileName.contains('.db-wal') ||
                fileName.contains('.db-shm');
            final isPref = relPath.startsWith('shared_prefs');

            // Kriteria file yang aman dibersihkan:
            // 1. Sisa artefak debug development (kernel_blob.bin, isolate_snapshot_data)
            //    yang tertinggal saat pernah dijalankan via `flutter run`
            // 2. Gambar (.jpg, .jpeg, .png, .webp)
            // 3. Berada di folder cache / code_cache / receipt_images
            // 4. File temporary (temp_*, *.tmp, *.temp, benchmark_*)
            final isDebugArtifact = fileName == 'kernel_blob.bin' ||
                fileName == 'isolate_snapshot_data' ||
                fileName == 'vm_snapshot_data' ||
                fileName.startsWith('res_timestamp-');
            final isImage = fileName.endsWith('.jpg') ||
                fileName.endsWith('.jpeg') ||
                fileName.endsWith('.png') ||
                fileName.endsWith('.webp');
            final isInCache = relPath.startsWith('cache/') || relPath.startsWith('code_cache/');
            final isInReceiptImages = relPath.contains('receipt_images');
            final isTempArtifact = fileName.startsWith('temp_') ||
                fileName.startsWith('benchmark_') ||
                fileName.startsWith('cord_') ||
                fileName.endsWith('.tmp') ||
                fileName.endsWith('.temp');

            final shouldDelete = performCleanup &&
                !isDb &&
                !isPref &&
                (isDebugArtifact || isImage || isInCache || isInReceiptImages || isTempArtifact);

            if (shouldDelete) {
              try {
                entry.deleteSync();
                filesDeleted++;
                totalFreedBytes += size;
                sb.writeln('[DELETED] $relPath (${(size / 1024).toStringAsFixed(1)} KB)');
              } catch (e) {
                sb.writeln('[FAILED TO DELETE] $relPath: $e');
              }
            } else {
              sb.writeln('[KEPT] $relPath (${(size / 1024).toStringAsFixed(1)} KB)');
            }
          }
        }
      }

      // Bersihkan juga cache directory resmi jika ada sisa
      try {
        final cacheDir = await getTemporaryDirectory();
        if (await cacheDir.exists()) {
          final cacheEntries = cacheDir.listSync(recursive: true, followLinks: false);
          for (final ce in cacheEntries) {
            if (ce is File) {
              try {
                final sz = ce.lengthSync();
                ce.deleteSync();
                totalFreedBytes += sz;
                filesDeleted++;
              } catch (_) {}
            }
          }
        }
      } catch (_) {}

      // Sanitasi database: lepaskan image_path pada transaksi lama agar bebas dari dangling path
      if (performCleanup) {
        try {
          final db = await database;
          await db.update('transactions', {'image_path': null});
          await db.execute('VACUUM;');
          sb.writeln('SQLite database disanitasi: image_path di-reset ke null & VACUUM dieksekusi.');
        } catch (e) {
          sb.writeln('Gagal sanitasi SQLite: $e');
        }
      }

      sb.writeln('--------------------------------------------------');
      sb.writeln('Total File Terdeteksi : $filesFound');
      sb.writeln('Total Ukuran Awal     : ${(totalBytesBefore / (1024 * 1024)).toStringAsFixed(2)} MB');
      sb.writeln('Total File Dihapus    : $filesDeleted');
      sb.writeln('Total Ruang Dibebaskan: ${(totalFreedBytes / (1024 * 1024)).toStringAsFixed(2)} MB');
      sb.writeln('Sisa Ukuran Data      : ${((totalBytesBefore - totalFreedBytes) / (1024 * 1024)).toStringAsFixed(2)} MB');

      // Tulis salinan laporan ke folder publik Download agar mudah diinspeksi via ADB
      try {
        final dlDir = Directory('/storage/emulated/0/Download');
        if (await dlDir.exists()) {
          final auditFile = File('${dlDir.path}/caran_storage_audit.txt');
          await auditFile.writeAsString(sb.toString());
        }
      } catch (_) {}
    } catch (e, stack) {
      sb.writeln('Error during auditAndCleanStorage: $e\n$stack');
    }

    final resultStr = sb.toString();
    debugPrint(resultStr);
    return resultStr;
  }

  /// Daftar transaksi terbaru dulu.
  /// Jika [includeItems] bernilai true, rincian barang ikut dimuat secara efisien
  /// menggunakan satu kali query batch (dibutuhkan untuk pencarian item & ekspor CSV).
  Future<List<Transaction>> getAllTransactions({bool includeItems = false}) async {
    final db = await database;
    final rows = await db.query('transactions', orderBy: 'transaction_date DESC');
    if (!includeItems || rows.isEmpty) {
      return rows.map((r) => Transaction.fromMap(r)).toList();
    }

    final itemRows = await db.query('transaction_items', orderBy: 'id ASC');
    final itemsByTrx = <int, List<TransactionItem>>{};
    for (final ir in itemRows) {
      final tId = ir['transaction_id'] as int;
      itemsByTrx.putIfAbsent(tId, () => []).add(TransactionItem.fromMap(ir));
    }

    return rows.map((r) {
      final tId = r['id'] as int;
      return Transaction.fromMap(r, items: itemsByTrx[tId] ?? const []);
    }).toList();
  }

  /// Satu transaksi lengkap dengan itemized breakdown-nya
  /// (untuk Halaman Detail Rincian Barang).
  Future<Transaction?> getTransactionWithItems(int id) async {
    final db = await database;
    final trxRows = await db.query('transactions', where: 'id = ?', whereArgs: [id]);
    if (trxRows.isEmpty) return null;

    final itemRows = await db.query(
      'transaction_items',
      where: 'transaction_id = ?',
      whereArgs: [id],
    );
    final items = itemRows.map((r) => TransactionItem.fromMap(r)).toList();
    return Transaction.fromMap(trxRows.first, items: items);
  }

  /// Total pengeluaran per bulan (format 'yyyy-MM') untuk grafik dashboard
  /// (BAB 4.2 poin 4).
  Future<Map<String, double>> getMonthlyTotals({int monthsBack = 6}) async {
    final db = await database;
    final rows = await db.rawQuery('''
      SELECT substr(transaction_date, 1, 7) AS ym, SUM(total_amount) AS total
      FROM transactions
      GROUP BY ym
      ORDER BY ym DESC
      LIMIT ?
    ''', [monthsBack]);

    final map = <String, double>{
      for (final r in rows) (r['ym'] as String): (r['total'] as num).toDouble(),
    };
    return map;
  }

  /// Menambahkan log scan baru ke tabel audit/debugging `scan_logs`
  Future<int> insertScanLog({
    required String imagePath,
    required String inferenceMode,
    required int executionTimeMs,
    required String detectedStore,
    required double detectedTotal,
    required int itemCount,
    required String rawSnippet,
    required String status,
    String? errorMessage,
  }) async {
    final db = await database;
    return db.insert('scan_logs', {
      'timestamp': DateTime.now().toIso8601String(),
      'image_path': imagePath,
      'inference_mode': inferenceMode,
      'execution_time_ms': executionTimeMs,
      'detected_store': detectedStore,
      'detected_total': detectedTotal,
      'item_count': itemCount,
      'raw_snippet': rawSnippet.length > 500 ? rawSnippet.substring(0, 500) : rawSnippet,
      'status': status,
      'error_message': errorMessage,
    });
  }

  /// Mengambil daftar riwayat audit/debugging log scan
  Future<List<Map<String, dynamic>>> getScanLogs({int limit = 50}) async {
    final db = await database;
    return db.query('scan_logs', orderBy: 'id DESC', limit: limit);
  }

  Future<void> clearScanLogs() async {
    final db = await database;
    await db.delete('scan_logs');
  }
}
