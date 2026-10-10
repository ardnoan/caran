# Caran Mobile Application (Flutter)

Aplikasi pencatatan pengeluaran pribadi cerdas berbasis **100% Offline-First** dengan ekstraksi struk belanja fisik secara instan di perangkat (*on-device machine learning*).

---

## Fitur Utama

- **100% On-Device & Zero Cloud Dependency**: Seluruh inferensi teks dan parsing berjalan lokal di ponsel tanpa koneksi internet, tanpa biaya API peladen awan, dan menjamin privasi penuh data finansial pengguna.
- **Native Bundled C++ OCR Pipeline**: Menggunakan Google ML Kit Native Bundled C++ pipeline untuk performa ekstraksi teks sub-150ms.
- **2D Spatial Bounding-Box Line Clustering**: Mengelompokkan token teks 2D berdasar kedekatan sumbu vertikal ($\Delta Y$) dan rasio tumpang tindih ($eta$-overlap), menyelesaikan masalah *1D text flattening* pada struk kasir 2 kolom.
- **Universal Receipt Taxonomy Engine**: Mengenali format struk minimarket & ritel modern di Indonesia (Alfamart, Alfamidi, Indomaret, Superindo, SPBU, apotek, dan kafe), termasuk diskon/potongan harga dan tanggal multi-format.
- **SQLite Offline Database**: Penyimpanan relasional lokal (`transactions` dan `transaction_items`) dengan query agregasi pengeluaran bulanan yang cepat.
- **Zero-Bloat Image Lifecycle**: Foto struk otomatis dihapus dari memori internal setelah ekstraksi selesai, menjaga konsumsi memori aplikasi tetap minimal (< 0,2 MB user data).
- **Benchmark Suite Screen**: Halaman pengujian terintegrasi untuk menguji akurasi ekstraksi pada 100 sampel struk dataset CORD-v2 secara langsung di perangkat.

---

## Struktur Folder

```
lib/
├── db/
│   └── database_helper.dart        # Lapisan basis data SQLite lokal & pembersihan foto
├── models/
│   ├── transaction.dart            # Entitas data transaksi induk
│   └── transaction_item.dart       # Entitas data rincian item barang belanja
├── screens/
│   ├── dashboard_screen.dart       # Beranda grafik pengeluaran bulanan & riwayat
│   ├── scanner_screen.dart         # Jendela bidik kamera dengan pemandu & senter
│   ├── preview_edit_screen.dart    # Pratinjau, pengeditan item, diskon, & kalkulasi
│   ├── item_detail_screen.dart     # Rincian item per transaksi belanja
│   └── benchmark_screen.dart       # Layar pengujian performa 100 sampel CORD-v2
├── services/
│   └── offline_receipt_service.dart# Mesin OCR ML Kit + 2D Spatial Clustering + Regex Engine
└── utils/
    └── currency_format_helper.dart # Pemformat dan parser mata uang Rupiah (IDR)
```

---

## Cara Menjalankan

### 1. Prasyarat
- Flutter SDK 3.19.0 atau lebih baru
- Android SDK (API level 24 / Android 7.0 ke atas)
- Perangkat Android fisik atau emulator

### 2. Mengunduh Dependencies
```bash
flutter pub get
```

### 3. Menjalankan Uji Statis & Unit Test
```bash
flutter analyze
flutter test
```

### 4. Menjalankan Aplikasi di Perangkat
```bash
flutter run
```

### 5. Membangun APK Rilis (Optimal arm64-v8a)
```bash
flutter build apk --release --target-platform android-arm64
```
Berkas biner APK rilis berada di:
`build/app/outputs/flutter-apk/app-arm64-v8a-release.apk`
Ukuran biner APK: ~36,2 MB (100% mandiri tanpa download model runtime tambahan).
