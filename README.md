# Caran (Catat Pengeluaran)

> **100% Offline-First On-Device AI Receipt Scanner & Personal Expense Tracker**  
> Digitalisasi struk belanja fisik secara instan, aman, dan tanpa ketergantungan internet maupun server cloud.

[![Flutter](https://img.shields.io/badge/Flutter-3.19+-02569B?logo=flutter&logoColor=white)](https://flutter.dev)
[![Dart](https://img.shields.io/badge/Dart-3.3+-0175C2?logo=dart&logoColor=white)](https://dart.dev)
[![ML Engine](https://img.shields.io/badge/Edge%20AI-Google%20ML%20Kit%20C%2B%2B-orange)](#)
[![Architecture](https://img.shields.io/badge/Architecture-100%25%20Offline--First-teal)](#)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Release](https://img.shields.io/badge/Release-v1.0.0-emerald)](#)

---

## 📌 Gambaran Umum

**Caran** (*Catat Pengeluaran*) adalah aplikasi mobile manajemen pengeluaran pribadi yang mengintegrasikan kecerdasan buatan langsung di dalam ponsel pintar (*On-Device Edge Machine Learning*). 

Berbeda dengan solusi pemindai komersial yang mengunggah foto struk ke peladen awan (Cloud OCR API seperti Google Cloud Vision atau AWS Textract), Caran beroperasi **murni 100% offline di perangkat**. Pendekatan ini menjamin tiga keunggulan mendasar:
1. **Privasi Penuh Data Finansial (*Zero Data Leak*)**: Data transaksi, nama toko, dan rincian belanja tidak pernah meninggalkan perangkat pengguna.
2. **Nol Biaya Operasional (*Zero Cloud Cost*)**: Bebas biaya langganan API berulang dan tidak membutuhkan sewa server GPU.
3. **Keandalan Tanpa Sinyal (*Zero Network Dependency*)**: Tetap dapat memindai dan mencatat transaksi di lokasi tanpa sinyal internet, seperti lantai bawah tanah (*basement*), area parkir, maupun minimarket pelosok.

---

## 🚀 Fitur Unggulan

- **Native Bundled C++ OCR Inference**: Inferensi pengenalan teks di perangkat dengan latensi rata-rata **sub-150 ms** per struk pada prosesor mid-range (MediaTek Helio G99).
- **2D Spatial Bounding-Box Line Clustering**: Algoritma pengelompokan spasial token teks 2D berbasis kedekatan vertikal ($\Delta Y$) dan rasio tumpang tindih ($eta$-overlap) untuk menyatukan baris nama barang dan harga pada struk 2 kolom tanpa mengalami masalah *1D text flattening*.
- **Taksonomi Struk Ritel Indonesia**: Dilengkapi mesin parsing berbasis *hierarchical regex heuristics* untuk mengenali struk ritel modern di Indonesia:
  - Format Alfamart / Alfamidi (format tanggal `Tgl. DD-MM-YYYY`, diskon minus, rincian multiline).
  - Format Indomaret (format tanggal berjarak spasi `DD. MM. YY - HH:mm`, harga jual, potongan hemat).
  - Format Supermarket (Superindo, Hypermart), SPBU Pertamina, apotek, dan kafe modern.
- **Pembersihan Otomatis Tanpa Sampah (*Zero-Bloat Image Lifecycle*)**: Berkas foto kamera langsung dihapus otomatis dari memori internal setelah proses ekstraksi selesai, menjaga konsumsi memori aplikasi tetap hemat (< 0,2 MB data pengguna).
- **Penyimpanan Relasional Lokal SQLite**: Skema basis data terstruktur (`transactions` dan `transaction_items`) dengan query agregasi pengeluaran per bulan yang responsif.
- **Antarmuka Material 3 Modern**: Dilengkapi grafik fluktuasi pengeluaran bulanan, riwayat belanja, dan formulir pengeditan transaksi sebelum disimpan.
- **Layar Benchmark Terintegrasi**: Fitur pengujian mandiri di dalam aplikasi untuk menguji akurasi ekstraksi pada 100 sampel struk belanja dataset CORD-v2 secara instan.

---

## 🏗️ Arsitektur Sistem

```
[Kamera Smartphone] ──► [Foto Struk Fisik]
                                │
                                ▼
         [Google ML Kit Bundled C++ Engine (Native)]
                (Deteksi Teks CNN + BiLSTM + CTC)
                                │
                                ▼
            [Koleksi Bounding Boxes Token 2D]
                                │
                                ▼
         [Algoritma 2D Spatial Line Clustering]
         (Penyatuan Baris Nama Barang & Kolom Harga)
                                │
                                ▼
       [Hierarchical Heuristic Indonesian Regex Engine]
       (Nama Toko, Tanggal/Waktu, Item Belanja, Diskon, Total)
                                │
                                ▼
         [Pratinjau, Verifikasi, & Koreksi Pengguna]
                                │
                                ▼
         [Penyimpanan Relasional Basis Data SQLite Lokal]
                                │
                                ▼
          [Pembersihan Otomatis Foto (Zero-Bloat)]
```

---

## 📁 Struktur Repositori

```
skripsi/
├── docs/                                    # Dokumentasi arsitektur & rekayasa teknis
│   ├── ARCHITECTURE_AND_CODE_TRACING.md     # Alur end-to-end tracing kode sistem
│   ├── ALGORITHM_AND_MATHEMATICAL_MODEL.md  # Teori matematika & spatial clustering
│   ├── APP_STORAGE_ANALYSIS.md              # Audit jejak penyimpanan Android & dex2oat
│   ├── RECEIPT_TAXONOMY_AND_BENCHMARKS.md   # Taksonomi struk ritel & komparasi Donut vs ML Kit
│   └── BENCHMARK_REPORT.md                  # Laporan kuantitatif evaluasi empiris
├── flutter_application_1/                   # Proyek Aplikasi Mobile Flutter
│   ├── lib/
│   │   ├── db/database_helper.dart          # Basis data SQLite & lifecycle cleanup
│   │   ├── models/                          # Model transaksi & item belanja
│   │   ├── screens/                         # Layar Scanner, Preview, Dashboard, Benchmark
│   │   ├── services/offline_receipt_service.dart # Mesin OCR & spatial line clustering
│   │   └── utils/currency_format_helper.dart# Parser & pemformat Rupiah
│   └── test/                                # Rangkaian Unit Test (Alfamart, Indomaret, dll.)
├── generator/                               # Lingkungan Evaluasi, Dataset, & Benchmark Python
│   ├── app_benchmark_streamlit.py           # Dashboard web evaluasi model Streamlit
│   ├── bab4_evaluasi_dan_eliminasi.py       # Pembangkit grafik & tabel benchmark evaluasi
│   ├── benchmark_donut_models.py            # Pengujian komparasi model Vision Transformer Donut
│   ├── evaluate_cord_1000_regex.py          # Evaluasi pengujian skala 1.000 sampel CORD-v2
│   ├── output_bab4/                         # Berkas JSON hasil uji & grafik resolusi tinggi
│   └── diagram_generators/                  # Skrip pembangkit diagram alur & arsitektur sistem
├── LICENSE                                  # Lisensi Open-Source MIT
└── README.md                                # Dokumentasi utama repositori
```

---

## 💻 Memulai Penggunaan (Getting Started)

### Prasyarat
- [Flutter SDK](https://docs.flutter.dev/get-started/install) v3.19.0 atau lebih baru
- [Android SDK](https://developer.android.com/studio) (Android 7.0 / API 24 ke atas)
- Python 3.10+ (opsional, untuk menjalankan rangkaian benchmark visual)

### 1. Menjalankan Aplikasi Flutter

```bash
# Masuk ke direktori aplikasi
cd flutter_application_1

# Unduh seluruh dependencies
flutter pub get

# Jalankan static code analyzer (memastikan 0 error / warning)
flutter analyze

# Jalankan pengujian unit test
flutter test

# Jalankan aplikasi pada perangkat Android fisik atau emulator
flutter run
```

### 2. Membangun Berkas APK Rilis (Optimal arm64-v8a)

```bash
cd flutter_application_1
flutter build apk --release --target-platform android-arm64
```
Berkas APK siap pasang akan tersedia di:
`flutter_application_1/build/app/outputs/flutter-apk/app-arm64-v8a-release.apk`
Ukuran biner APK rilis: **~36,2 MB**.

### 3. Menjalankan Dashboard Benchmark Python (Streamlit)

```bash
cd generator
streamlit run app_benchmark_streamlit.py
```
Akses dashboard visualisasi evaluasi model pada peramban melalui alamat `http://localhost:8501`.

---

## 📊 Ringkasan Hasil Evaluasi Empiris

Berdasarkan pengujian komparatif terhadap model Vision Transformer (Donut) dan arsitektur terpilih Caran (On-Device ML Kit + Spatial Clustering) pada ponsel fisik **TECNO LH7n (MediaTek Helio G99, RAM 8 GB)**:

| Parameter Evaluasi | Donut Transformer (INT8 On-Device) | Caran On-Device ML Kit (Terpilih) | Keunggulan Caran |
| :--- | :---: | :---: | :---: |
| **Latensi Rata-rata per Struk** | 28.450 ms (~28,5 detik) | **148,4 ms (< 0,2 detik)** | **~191x Lebih Cepat** |
| **Alokasi Memori RAM Volatil** | 1.120 MB (1,1 GB) | **68,0 MB** | **Hemat RAM 94%** |
| **Dampak Tambahan Ukuran APK** | +282,5 MB | **+11,8 MB** | **Hemat Ukuran 96%** |
| **Kebutuhan Koneksi Internet** | 100% Offline | **100% Offline** | Zero Cloud Leaks |
| **Akurasi Ekstraksi Nama Toko** | 78,0% | **92,0%** | Unggul pada struk ritel lokal |
| **Akurasi Ekstraksi Total Belanja** | 71,0% | **88,0%** | Bottom-up heuristic akurat |

Dokumentasi lengkap dan metodologi pengujian dapat dibaca pada [docs/RECEIPT_TAXONOMY_AND_BENCHMARKS.md](docs/RECEIPT_TAXONOMY_AND_BENCHMARKS.md) dan [docs/BENCHMARK_REPORT.md](docs/BENCHMARK_REPORT.md).

---

## 📚 Dokumentasi Lanjutan

- [Arsitektur Sistem & Tracing Kode Program](docs/ARCHITECTURE_AND_CODE_TRACING.md)
- [Algoritma 2D Spatial Line Clustering & Model Matematika](docs/ALGORITHM_AND_MATHEMATICAL_MODEL.md)
- [Analisis Jejak Memori Android & Optimasi Penyimpanan](docs/APP_STORAGE_ANALYSIS.md)
- [Taksonomi Struk Ritel Indonesia & Studi Komparasi Model](docs/RECEIPT_TAXONOMY_AND_BENCHMARKS.md)
- [Laporan Data Evaluasi Empiris](docs/BENCHMARK_REPORT.md)

---

## 📄 Lisensi

Proyek ini dirilis di bawah lisensi terbuka [MIT License](LICENSE). Bebas digunakan, dimodifikasi, dan didistribusikan untuk keperluan riset maupun pengembangan komersial.
