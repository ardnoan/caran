# Caran - Arsitektur Sistem & Tracing Kode Program

**Proyek:** Caran (Catat Pengeluaran) — On-Device Offline Receipt Scanner & Expense Tracker  
**Tech Stack:** Flutter 3.19+ (Dart), Google ML Kit Native Bundled C++, SQLite, Python 3.11/3.14  
**Lisensi:** MIT License  

---
## 1. JAWABAN TENTANG GENERASI GAMBAR & DIAGRAM
> **"Apakah gambarnya digenerate sendiri?"**
> **YA, 100% diprogram dan digenerate secara mandiri** menggunakan skrip Python (`generator/generate_visual_proofs.py` dan `generator/bab4_evaluasi_dan_eliminasi.py`) dengan pustaka `matplotlib`, `patches` (vektor bentuk geometris), dan `PIL` (Pillow) berstandar publikasi ilmiah resolusi tinggi (**300 DPI**).
> 
> Tidak ada gambar hasil copas atau template internet. Setiap diagram dibuat berdasarkan data empiris riil:
> - **Diagram 1 (`diagram_1_alur_pemilihan_dan_eliminasi_model.png`)**: Alur 4 fase keputusan rekayasa eliminasi model Donut dan pemilihan ML Kit.
> - **Diagram 2 (`diagram_2_pipeline_spatial_clustering_caran.png`)**: Pipa pemrosesan citra dari input kamera hingga penyimpanan SQLite.
> - **Visualisasi Spasial (`visualisasi_spatial_line_clustering_sample.png`)**: Ilustrasi visual struk Alfamart 2 kolom yang menunjukkan koordinat bounding box kolom nama dan harga disatukan oleh algoritma *Spatial Line Clustering*.
> - **Grafik 1-4 (`grafik_1_perbandingan_latensi.png`, `grafik_4_distribusi_latensi_100_struk.png`, dll.)**: Digambar langsung dari data metrik kuantitatif pengujian 100 struk CORD-v2 pada chip MediaTek Helio G99 (`benchmark_cord_100_on_device_tecno.json`).

---

## 2. DIAGRAM ALUR EKSEKUSI APLIKASI (END-TO-END FLOW TRACING)

```
[1. Entry Point: main.dart]
   │
   ├─► WidgetsFlutterBinding & initializeDateFormatting('id_ID')
   └─► OfflineReceiptService.warmUp()  <-- Memuat model C++ ML Kit ke RAM
         │
         ▼
[2. Beranda: screens/dashboard_screen.dart]
   │
   ├─► DatabaseHelper.instance.getAllTransactions() -> Load data SQLite
   ├─► Menampilkan Total Saldo, Grafik fl_chart, & Filter Rentang Tanggal
   │
   ├─► [Aksi 1: Klik FAB Kamera] ──────────────┐
   ├─► [Aksi 2: Klik Catat Manual] ────┐       │
   └─► [Aksi 3: Klik Baris Transaksi]  │       ▼
              │                        │   [3. Pengambilan Foto: screens/scanner_screen.dart]
              ▼                        │      │
      [screens/item_detail_screen.dart]│      ├─► Kamera High-Res / Viewfinder Kotak Panduan
                                       │      ├─► Toggle Senter (Torch Mode)
                                       │      └─► controller.takePicture() -> Navigator.pop(imagePath)
                                       │             │
                                       │             ▼
                                       │   [4. Pipa Inferensi: services/offline_receipt_service.dart]
                                       │      │
                                       │      ├─► Google ML Kit processImage() (Native C++)
                                       │      ├─► _reconstructSpatialLines() (Spatial Clustering)
                                       │      ├─► parseReceiptText() (Regex Toko, Tanggal, Item, Total)
                                       │      └─► DatabaseHelper.insertScanLog() (Audit Log SQLite)
                                       │             │
                                       │             ▼ (Return OfflineExtractionResult)
                                       └────────────►│
                                                     ▼
                                           [5. Form Review: screens/preview_edit_screen.dart]
                                              │
                                              ├─► CurrencyTextInputFormatter (Live titik ribuan '18.000')
                                              ├─► Subtotal per baris item (Qty x Harga = Subtotal)
                                              ├─► Auto-Sync Total Σ(item) & Banner Koreksi Selisih
                                              ├─► Dropdown Kategori (Belanja Harian, Makanan, dsb.)
                                              └─► Klik "Simpan Transaksi" -> _saveTransaction()
                                                     │
                                                     ▼
                                           [6. Persistensi Data: db/database_helper.dart]
                                              │
                                              ├─► SQLite: INSERT INTO transactions (...)
                                              └─► SQLite: INSERT INTO transaction_items (...)
                                                     │
                                                     ▼
                                           [7. Kembali ke Beranda: screens/dashboard_screen.dart]
                                              └─► _loadTransactions() -> State ter-update instan!
```

---

## 3. BEDAH FILE SUMBER & FUNGSINYA (FILE-BY-FILE TRACING)

### A. Titik Masuk Aplikasi: `flutter_application_1/lib/main.dart`
- **Fungsi Utama:** Bootstrapping Flutter engine, inisialisasi lokalisasi tanggal Indonesia (`id_ID`), dan memicu *warm-up* model ML Kit.
- **Fungsi Kunci:**
  ```dart
  OfflineReceiptService.warmUp(); // Menginisialisasi TextRecognizer di latar belakang
  ```
  *Mengapa penting untuk sidang?* Mencegah *cold-start delay*. Saat pengguna pertama kali memotret struk, model C++ Google ML Kit sudah aktif di memori RAM sehingga ekstraksi selesai dalam < 200 ms.

---

### B. Antarmuka Beranda: `flutter_application_1/lib/screens/dashboard_screen.dart`
- **Fungsi Utama:** Dashboard keuangan, menampilkan kartu total pengeluaran bulanan, grafik tren pengeluaran (`fl_chart`), chip filter rentang tanggal (*Semua, Hari Ini, 7 Hari, Bulan Ini*), live search bar, dan daftar riwayat belanja.
- **Titik Pemicu Scan Struk:**
  - Metode `_openScanner(context)` membuka `ScannerScreen()`.
  - Menerima hasil `imagePath` dari kamera.
  - Memanggil `_processReceipt(imagePath)`:
    ```dart
    final result = await OfflineReceiptService.extractReceipt(imagePath);
    await DatabaseHelper.instance.insertScanLog(...);
    Navigator.push(context, MaterialPageRoute(builder: (_) => PreviewEditScreen(transaction: result.transaction)));
    ```

---

### C. Kamera & Pengambilan Citra: `flutter_application_1/lib/screens/scanner_screen.dart`
- **Fungsi Utama:** Mengendalikan sensor kamera perangkat keras secara langsung melalui paket `camera`.
- **Fitur Khusus:**
  1. `ResolutionPreset.high` (Full HD 1080p) agar teks kasir berukuran kecil tetap tajam.
  2. `_toggleFlash()`: Mengubah mode senter (`FlashMode.torch` / `FlashMode.off`) untuk kondisi redup.
  3. Kotak panduan (*viewfinder overlay*) untuk memposisikan struk tegak lurus dan simetris.
- **Output:** Mengembalikan `shot.path` (string lokasi file foto di HP) ke caller via `Navigator.pop(context, shot.path)`.

---

### D. Otak Ekstraksi Edge ML: `flutter_application_1/lib/services/offline_receipt_service.dart`
- **Fungsi Utama:** Mesin inti proyek yang mengekstraksi teks visual struk menjadi data terstruktur tanpa internet.
- **Tahapan Detail:**
  1. **Google ML Kit OCR (Baris 60-73):**
     ```dart
     final inputImage = InputImage.fromFilePath(imagePath);
     final recognizedText = await recognizer.processImage(inputImage);
     ```
  2. **Spatial Line Clustering (`_reconstructSpatialLines`, Baris 520-580):**
     - Menganalisis koordinat bounding box setiap elemen teks: `(rect.top, rect.bottom, rect.left, rect.right)`.
     - Mengelompokkan blok teks yang berada pada rentang vertikal Y yang sama (toleransi tumpang tindih ~60%).
     - Mengurutkan teks dalam satu baris dari kiri ke kanan (sumbu X).
     - *Hasilnya:* Kolom kiri ("INDOMIE AYAM BAWANG 2") dan kolom kanan ("6.200") disatukan menjadi satu baris horizontal utuh.
  3. **Hierarchical Heuristic Regex Engine (`parseReceiptText`, Baris 92-300):**
     - **Toko:** Rekonstruksi brand ritel nasional (`Alfamart`, `Indomaret`, `Superindo`, `Yogya`, dll.) di 8 baris teratas.
     - **Tanggal:** Regex multi-pola tanggal kasir (`DD-MM-YYYY`, `DD/MM/YYYY`, teks nama bulan Indonesia).
     - **Filter Derau:** Menyingkirkan teks non-produk seperti NPWP, nomor bon, kasir, alamat toko, dan ucapan terima kasih.
     - **Item Belanja:** Parsing nama barang, harga satuan, perkalian kuantitas (`2 x 3.100`), serta penanganan diskon minus (`-200`).
     - **Total Belanja:** Deteksi kata kunci `TOTAL`, `TOTAL ITEM`, `TOTAL BELANJA`, `SUBTOTAL`, atau rekonsiliasi nilai terbesar.
  4. **Output:** Objek `OfflineExtractionResult` yang berisi model data `Transaction` terisi otomatis.

---

### E. Form Pratinjau & Koreksi: `flutter_application_1/lib/screens/preview_edit_screen.dart`
- **Fungsi Utama:** Memastikan pengguna memiliki kendali mutlak (human-in-the-loop) untuk memverifikasi atau mengoreksi hasil bacaan mesin sebelum disimpan.
- **Fitur Baru v1.3:**
  1. `CurrencyTextInputFormatter`: Angka otomatis berformat titik ribuan kasir Indonesia (misal: `18.000`) saat pengguna mengetik harga atau total.
  2. **Subtotal Live:** Menampilkan `Qty × Harga = Subtotal` secara otomatis di tiap kartu barang.
  3. **Auto-Sync Total:** Total transaksi otomatis menghitung penjumlahan seluruh item, namun tetap fleksibel untuk diedit manual.
  4. **Dropdown Kategori:** Pengguna dapat memilih kategori pengeluaran (*Belanja Harian, Makanan & Minuman, Transportasi, dsb.*).
  5. **PopScope:** Mencegah pengguna keluar tanpa sengaja saat form sudah terisi data.
- **Aksi Simpan:**
  ```dart
  await DatabaseHelper.instance.insertTransaction(txn, items);
  Navigator.pop(context, true); // Memberitahu Dashboard untuk reload data
  ```

---

### F. Lapisan Basis Data Lokal: `flutter_application_1/lib/db/database_helper.dart`
- **Fungsi Utama:** Pengelola SQLite lokal (`receipt_scanner.db`) dengan arsitektur relasional:
  - Tabel `transactions`: Menyimpan metadata transaksi (toko, total, tanggal, kategori, foto).
  - Tabel `transaction_items`: Menyimpan daftar barang belanja (foreign key berelasi ke `transactions.id` dengan aturan `ON DELETE CASCADE`).
  - Tabel `scan_logs`: Menyimpan catatan audit benchmarking (waktu eksekusi ms, status SUCCESS/WARNING) untuk keperluan analisis riset.
- **Migrasi Non-Destruktif:**
  ```dart
  // Kolom category ditambahkan secara otomatis di onOpen tanpa merusak database yang sudah ada
  await db.execute("ALTER TABLE transactions ADD COLUMN category TEXT NOT NULL DEFAULT 'Belanja Harian'");
  ```

---

## 4. RANGKUMAN ALUR DI SISI PYTHON (RISET & PEMBUKTIAN SKRIPSI)

| File Script Python | Fungsi & Peran dalam Proyek |
| :--- | :--- |
| `generator/bab4_evaluasi_dan_eliminasi.py` | Menghitung metrik komparasi kuantitatif (Donut vs ML Kit), mengekspor tabel Markdown/CSV, dan membuat grafik publikasi resolusi tinggi. |
| `generator/generate_visual_proofs.py` | Menggambar Diagram Alur Keputusan Eliminasi Model, Diagram Arsitektur Pipeline Caran, Visualisasi Bounding Box Spasial, dan Distribusi Latensi 100 Struk CORD-v2. |
| `generator/app_benchmark_streamlit.py` | Aplikasi web riset interaktif (Streamlit) dengan 4 Tab: Peta Alur Riset, Pipeline Spasial Caran, Uji Multi-Model Donut di GPU, dan Data Empiris 100 Struk Bab IV. |
| `generator/generate_proyek_v1_3.py` | Mengompilasi naskah proyek lengkap Word (`.docx`) Bab I sampai Bab V dengan menyematkan langsung seluruh 7 diagram & grafik visual 300 DPI ke dalam dokumen. |
