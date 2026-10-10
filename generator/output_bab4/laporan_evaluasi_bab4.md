# DATA DAN ANALISIS PEMBUKTIAN BAB IV SKRIPSI

## 4.1 Studi Kelayakan dan Eliminasi Model Arsitektur

|    | Nama Model / Pipeline                                  | Lingkungan Eksekusi                       |   Latensi (ms) |   Ukuran (MB) |   RAM (MB) | Internet?                      | Keputusan Bab IV                                                       |
|----|--------------------------------------------------------|-------------------------------------------|----------------|---------------|------------|--------------------------------|------------------------------------------------------------------------|
|  0 | Donut CORD-v2 (Server GPU)                             | Cloud / Server GPU (PyTorch)              |           1450 |           0   |       2150 | Wajib (Koneksi Server / Cloud) | DIELIMINASI (Butuh server, melanggar prinsip offline-first & privasi)  |
|  1 | Donut Receipts / mychen76 (Server GPU)                 | Cloud / Server GPU (PyTorch)              |           1180 |           0   |       2120 | Wajib (Koneksi Server / Cloud) | DIELIMINASI (Ketergantungan infrastruktur server GPU mahal)            |
|  2 | Donut Transformer INT8 (On-Device Mobile)              | On-Device Smartphone (CPU Helio G99)      |          28450 |         282.5 |       1120 | 100% Offline                   | DIELIMINASI (Latensi >25 detik tidak layak pakai, APK bengkak >300 MB) |
|  3 | Google ML Kit + Spatial Clustering (On-Device Edge ML) | On-Device Smartphone (NPU/CPU Native C++) |            242 |          11.8 |         68 | 100% Offline (Murni On-Device) | DIPILIH SEBAGAI ARSITEKTUR PRODUKSI SKRIPSI                            |

---

## 4.2 Hasil Pengujian Empiris Sampel Struk Fisik Menggunakan Arsitektur Terpilih

|    | ID Sampel   | Nama Sampel Struk                                     |   Target Total (Rp) |   Hasil Total (Rp) |   Target Item |   Hasil Item |   Waktu (ms) | Status Pengujian                                             |
|----|-------------|-------------------------------------------------------|---------------------|--------------------|---------------|--------------|--------------|--------------------------------------------------------------|
|  0 | SMP-01      | Alfamart Jalaprang (Transaksi Normal + Void Item)     |               18000 |              18000 |             2 |            2 |          224 | Lolos Sempurna (100% Match + Filter Void Berhasil)           |
|  1 | SMP-02      | Alfamart Gardenia (Multi-item Roti & Berat Gramasi)   |               12200 |              12200 |             2 |            2 |          258 | Lolos Sempurna (Gramasi tidak merusak harga)                 |
|  2 | SMP-03      | Struk Kasir Indomaret (Footer Noise & PPN)            |               34500 |              34500 |             3 |            3 |          235 | Lolos Sempurna (Junk line regex memblokir noise footer)      |
|  3 | SMP-04      | Struk SPBU Pertamina (Format Horizontal Ringkas)      |               50000 |              50000 |             1 |            1 |          198 | Lolos Sempurna (Total nominal liter akurat)                  |
|  4 | SMP-05      | Struk Fotokopi & ATK (Struk Non-Ritel Terpotong Atas) |               15000 |              15000 |             2 |            2 |          215 | Toko Fallback (Total & Item Akurat 100%, Toko diedit manual) |

---

## 4.3 Kesimpulan Keputusan Rekayasa Perangkat Lunak (Engineering Decision)

Berdasarkan pengujian empiris kuantitatif:
1. **Eliminasi Model Vision-Language Transformer (Donut) On-Device**: Model Donut INT8 terbukti tidak layak diimplementasikan pada perangkat bergerak mandiri (standalone mobile device) karena latensi inferensi mencapai 28,4 detik per lembar struk, memakan memori RAM > 1 GB, dan menghasilkan quantization drift yang merusak keluaran teks (total bernilai Rp 0).
2. **Eliminasi Model Donut Server/Cloud**: Meskipun memiliki akurasi semantik tinggi di GPU, model ini menggugurkan prinsip arsitektur Offline-First, melanggar privasi data finansial pengguna, serta membutuhkan biaya hosting infrastruktur GPU yang mahal.
3. **Pemilihan Google ML Kit + Spatial Line Clustering**: Terpilih sebagai arsitektur final skripsi karena menghasilkan latensi rata-rata hanya 242 ms (< 0.3 detik), ukuran library ringan (11.8 MB), hemat memori RAM (68 MB), serta mampu beroperasi 100% offline tanpa kebocoran data keluar perangkat.
