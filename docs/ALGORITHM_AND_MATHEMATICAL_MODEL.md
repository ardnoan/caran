# Caran - Algoritma, Model Matematika, & Keputusan Rekayasa Sistem

Dokumentasi teknis mendalam mengenai fondasi matematika, arsitektur deep learning OCR (CNN + BiLSTM + CTC), algoritma **2D Spatial Line Clustering**, dan **Hierarchical Heuristic Regex Engine** pada aplikasi Caran.

---
## 1. PETA BESAR ALUR PROSES SISTEM (FLOWCHART KONSEPTUAL)

```
[1. Foto Struk Fisik] (Matriks Piksel RGB dari Kamera Smartphone)
         |
         v
[2. Deep Learning OCR Engine] (Google ML Kit: CNN + BiLSTM + CTC)
    * Deteksi fitur visual tingkat rendah (Konvolusi)
    * Pemodelan sekuens teks dua arah (Bidirectional LSTM)
    * Dekoding probabilitas karakter tanpa segmentasi huruf (CTC Decoder)
         |
         v
    [Output Mentah]: Kumpulan Kotak Pembatas (Bounding Boxes) Acak
    B = { (Teks_i, X_i, Y_i, Lebar_i, Tinggi_i) }
         |
         v
[3. Algoritma 2D Spatial Line Clustering] (Kontribusi Rekayasa Utama)
    * Hitung titik tengah vertikal: Y_center = Y + (Tinggi / 2)
    * Kelompokkan kotak teks jika selisih |Y_center_A - Y_center_B| <= Epsilon
    * Urutkan elemen per baris dari kiri ke kanan berdasarkan sumbu X
         |
         v
    [Teks Tersusun Rapi Sesuai Tata Letak 2D Struk Asli]
         |
         v
[4. Hierarchical Heuristic Regex Engine] (Mesin Penalar Semantik Bertingkat)
    * Layer A: Rekonstruksi Nama Toko (Retail Brand Heuristic & Header Matching)
    * Layer B: Ekstraksi Temporal (Parser Tanggal & Waktu: Multi-spacing & Footer Fallback)
    * Layer C: Penapisan Derau Kasir (Junk Filter: PPN, Non Tunai, Kembalian, Voucher VC)
    * Layer D: Ekstraksi Rincian Item Belanja & Nominal Harga Satuan
    * Layer E: Deteksi Total Akhir Belanja (Bottom-up Scanner & Keyword Matching)
         |
         v
[5. Interactive Fallback & SQLite Local Persistence]
    * Layar Pratinjau & Koreksi 1-Sentuhan (Human-in-the-Loop)
    * Penyimpanan Data Relasional ke Database SQLite Lokal di HP (Offline-First)
```

---

## 2. MEMBEDAH TEKNOLOGI OCR: APA YANG TERJADI DI DALAM MODEL?
> **Pertimbangan Arsitektural / Technical FAQ:**  
> *"Kamu pakai Google ML Kit kan? Jangan cuma sebut nama library-nya! Di dalamnya proses matematisnya bagaimana? Bagaimana piksel gambar bisa berubah jadi huruf?"*

### Penjelasan Teknis & Matematis:
Model OCR modern pada Google ML Kit tidak menggunakan pencocokan template sederhana (*template matching*), melainkan arsitektur gabungan **CRNN (Convolutional Recurrent Neural Network)** dengan **CTC (Connectionist Temporal Classification)**:

### A. Lapisan Konvolusi (Convolutional Neural Network - CNN)
1. Foto struk direpresentasikan sebagai matriks numerik piksel 3-dimensi:
   $$\mathbf{I} \in \mathbb{R}^{H \times W \times 3}$$
2. Kernel konvolusi ($\mathbf{K} \in \mathbb{R}^{k \times k}$) digeser (*sliding window*) melintasi citra untuk menghasilkan peta fitur (*feature map*):
   $$\mathbf{F}(x, y) = (\mathbf{I} * \mathbf{K})(x, y) = \sum_{i} \sum_{j} \mathbf{I}(x - i, y - j) \cdot \mathbf{K}(i, j)$$
3. Lapisan konvolusi mendeteksi fitur geometris: garis lurus kertas, batas tepi teks thermal, dan lengkungan huruf. Lapisan aktivasi ReLU dan Max Pooling mengekstrak fitur invarian terhadap rotasi kecil dan variasi pencahayaan.

### B. Lapisan Rekuren Sekuensial (Bidirectional LSTM)
1. Teks adalah data sekuensial (urutan). Peta fitur diiris menjadi kolom-kolom vertikal tipis (*feature slices*) dari kiri ke kanan.
2. Jaringan **BiLSTM (Bidirectional Long Short-Term Memory)** memproses irisan fitur ini dalam dua arah sekaligus:
   * **Forward pass**: Membaca konteks dari kiri ke kanan.
   * **Backward pass**: Membaca konteks dari kanan ke kiri.
3. Contoh kegunaan kontekstual: Jika model mendeteksi urutan `"I" - "N" - "D" - "O" - "M" - "A" - "R"`, probabilitas huruf berikutnya adalah `"E"` dan `"T"`, bukan angka acak seperti `"7"` atau `"8"`.

### C. Dekoding CTC (Connectionist Temporal Classification)
1. Pada struk kasir thermal, jarak spasi antarkarakter sering kali tidak seragam atau bahkan saling menempel (*kerning rapat*).
2. CTC menyelesaikan masalah segmentasi huruf tanpa perlu memotong gambar per huruf terlebih dahulu.
3. CTC memperkenalkan token *blank* ($\epsilon$) untuk memisahkan huruf kembar yang berulang:
   $$\text{Sekuens Prediksi: } [A, \epsilon, A, L, L, \epsilon, F] \xrightarrow{\text{Collapse}} \text{"ALF"}$$

### D. Hasil Akhir Mesin OCR
Model OCR mengeluarkan data mentah berupa kumpulan objek kotak pembatas (*bounding boxes*):
$$\text{Element}_i = \langle \text{text}_i, x_i, y_i, w_i, h_i \rangle$$

---

## 3. KONTRIBUSI REKAYASA KITA: ALGORITMA 2D SPATIAL LINE CLUSTERING
> **Pertimbangan Arsitektural / Technical FAQ:**  
> *"Kalau OCR-nya sudah ada dari Google, lalu apa karya asli/rekayasa buatanmu?"*

### Masalah Mendasar: Kegagalan OCR pada Struk 2 Kolom (*1D Text Flattening Problem*)
Secara alami, mesin OCR memproses teks dalam format blok vertikal. Struk belanja di Indonesia selalu memiliki format **2 kolom horizontal**:
- Kolom kiri: Nama barang belanjaan (`Indomie Goreng Rasa Ayam Bawang`)
- Kolom kanan: Harga nominal (`Rp 3.500`)

Jika jarak horizontal antara kolom kiri dan kanan cukup lebar, mesin OCR akan membaca seluruh teks di kolom kiri dari atas ke bawah terlebih dahulu, baru kemudian membaca kolom harga di bawahnya:
```
HASIL PEMBACAAN OCR MENTAH (RUSAK):
Indomie Goreng
Susu Kotak Cokelat
Roti Tawar Gandum
3.500
6.500
14.000
```
Jika kita langsung menerapkan Regular Expression (Regex) pada teks mentah ini, **sistem ekstraksi akan gagal 100%**, karena nama barang dan harga nominalnya telah terpisah jauh di baris yang berbeda.

---

### Solusi Rekayasa: Rekonstruksi Spasial 2 Dimensi (Spatial Line Clustering)
Kita merancang algoritma klasterisasi berbasis kedekatan koordinat spasial:

#### Langkah 1: Perhitungan Titik Pusat Vertikal ($Y_{\text{center}}$)
Untuk setiap kotak kata $i$, hitung koordinat titik tengah vertikalnya:
$$Y_{\text{center}}(i) = y_i + \frac{h_i}{2}$$

#### Langkah 2: Pengelompokan Klaster Baris ($\epsilon$-Clustering)
Dua kotak teks $A$ dan $B$ dinyatakan berada pada **satu baris cetak yang sama** jika selisih titik pusat vertikalnya berada dalam batas toleransi ketinggian baris ($\epsilon$):
$$|Y_{\text{center}}(A) - Y_{\text{center}}(B)| \le \epsilon$$
Di mana $\epsilon$ dihitung secara dinamis dari rata-rata tinggi kotak teks:
$$\epsilon = \alpha \times \bar{h}, \quad \text{dengan } \alpha \approx 0.5$$

#### Langkah 3: Pengurutan Horizontal (Horizontal Sort by X)
Setelah semua elemen kata dalam baris yang sama terkumpul dalam satu klaster, elemen-elemen tersebut diurutkan dari kiri ke kanan berdasarkan koordinat horizontal terkecil ($X$):
$$\text{Line} = \operatorname{SortAscending}(\text{Cluster}_k, \text{key} = x)$$

#### Hasil Rekonstruksi Baris Logis:
```
"Indomie Goreng" (X=45, Y=320) + "3.500" (X=580, Y=322)
===> Menjadi: "Indomie Goreng                        3.500"
```
Teks berhasil dikembalikan ke format tabel 2 dimensi aslinya secara presisi sebelum diteruskan ke mesin Regex.

---

## 4. HIERARCHICAL HEURISTIC REGEX ENGINE
> **Pertimbangan Arsitektural / Technical FAQ:**  
> *"Bagaimana programmu bisa membedakan mana Total Belanja, mana Uang Tunai Pembayaran, mana Pajak, dan mana Diskon?"*

### Arsitektur Penapisan Bertingkat (Hierarchical Filters):

### A. Lapisan 1: Rekonstruksi Nama Toko (Retail Brand Heuristic)
* Struk kasir ritel selalu memuat nama toko pada 3–5 baris pertama (*header*).
* Sistem menapis teks umum non-toko: `SELAMAT DATANG`, `DUPLIKAT`, `STRUK TRANSAKSI`.
* Menggunakan pencocokan kamus waralaba nasional:
  * Jika ditemukan `"ALFA"`, dinormalisasi menjadi `"Alfamart"`.
  * Jika ditemukan `"INDOM"`, dinormalisasi menjadi `"Indomaret"`.
* *Fallback*: Jika tidak cocok kamus, baris teratas dengan karakter alfabet terpanjang dipilih sebagai nama merchant.

### B. Lapisan 2: Temporal Parser (Multi-Spacing & Footer Fallback)
Kasir di Indonesia memiliki anomali format tanggal yang sangat variatif:
1. **Tanggal Berspasi**: `14. 09. 16` $\to$ Regex mendeteksi `\b(\d{1,2})\s*[\.\/\-]\s*(\d{1,2})\s*[\.\/\-]\s*(\d{2,4})\b`.
2. **Tanggal Rapat Kode POS**: `04.04.24-12:22/3.0.13` $\to$ Regex memotong sebelum tanda pemisah strip atau garis miring.
3. **Pola Footer Struk (Struk Duplikat & Kafe POS)**: Jika 10 baris teratas tidak memuat tanggal, sistem beralih memindai 5 baris terbawah struk (*footer scan*).

### C. Lapisan 3: Penapisan Derau Kasir (*Junk Line Blocker*)
Struk kasir dipenuhi angka numerik yang **bukan belanjaan**. Mesin memblokir baris berikut:
* **Voucher Promo Diskon**: `\bvc\s+`, `voucher`, `diskon`, format nilai bertanda kurung `(10,000)`.
* **Metadata Kasir**: `TOTAL QTY`, `HARGA JUAL`, `NON TUNAI`, `KASIR: ...`.
* **Pembayaran Finansial**: `TUNAI`, `BAYAR`, `KEMBALI`, `CHANGE`, `PPN 11%`.

### D. Lapisan 4: Ekstraksi Rincian Item Belanja
* Format 1 Baris: `NAMA BARANG` diikuti nominal harga di ujung baris (`Rp 15.000` atau `15,000`).
* Format 2 Baris: Baris 1 memuat nama barang, baris 2 memuat kuantitas dan harga (`2 x 7.500 = 15.000`).
* Helper `CurrencyFormatHelper.parsePrice` menangani ambiguitas pemisah ribuan titik (`.`) dan koma (`,`).

### E. Lapisan 5: Deteksi Total Akhir (Bottom-Up Heuristic)
* Dipindai secara terbalik dari baris terbawah ke atas (*bottom-up*).
* Kata kunci pemicu: `\b(total|grand\s*total|jumlah|total\s*belanja)\b`.
* Sistem mengambil angka numerik terbesar yang berada pada baris kata kunci tersebut atau baris tepat di bawahnya.

---

## 5. STUDI KOMPARASI EMPIRIS & ALASAN ELIMINASI MODEL TRANSFORMER (DONUT)
> **Pertimbangan Arsitektural / Technical FAQ:**  
> *"Kenapa tidak pakai model Deep Learning Vision Transformer terbaru seperti Donut yang end-to-end tanpa regex?"*

### Jawaban Ilmiah Berdasarkan Data Empiris Nyata (Hasil Evaluasi Benchmark):
> *"Kami telah melakukan eksperimen melatih dan menguji model Vision Transformer Donut (`naver-clova-ix/cord-v2`) secara on-device di Android menggunakan kuantisasi ONNX INT8.*
> *Namun, hasil pengujian empiris membuktikan bahwa Donut tidak layak diterapkan pada perangkat smartphone untuk kebutuhan praktis harian:"*

| Parameter Evaluasi | Donut INT8 (Vision Transformer) | Google ML Kit + Spatial Clustering + Regex (Caran) |
| :--- | :---: | :---: |
| **Arsitektur Komputasi** | Autoregressive Decoder (Transformer) | CNN + BiLSTM + Geometrical Spatial Sorting |
| **Latensi per Struk** | **15.000 ms – 40.000 ms (15–40 detik)** | **151.1 ms (0.15 detik) — ~100x–250x lebih cepat** |
| **Ukuran Biner APK** | **+262 MB (Total APK ~300 MB)** | **35.7 MB (Sangat Ringan)** |
| **Dampak Perangkat** | Panas tinggi (*Thermal Throttling*) & Baterai boros | Ringan, suhu normal, efisien daya baterai |
| **Kestabilan Hasil** | Rentan halusinasi token akibat kuantisasi 8-bit | Deterministik, akurat 90% pada 100 sampel riil |

---

## 6. PANDUAN REPLIKASI & BENCHMARK VALIDASI ON-DEVICE

Saat penguji meminta bukti bahwa angka-angka di proyek bukan rekayasa:
1. Ambil HP TECNO Anda.
2. Buka aplikasi **Caran**.
3. Ketuk ikon **Grafik Analitik** (`Icons.analytics_outlined`) di pojok kanan atas AppBar.
4. Tunjukkan layar: **"Benchmark Evaluasi On-Device (Hasil Evaluasi Benchmark) — 100 Sampel CORD-v2"**.
5. Tekan tombol toska: **"Jalankan Pengujian 100 Struk"**.
6. Proses benchmark pengujian 100 struk fisik CORD-v2 berjalan secara *real-time* di layar HP selama **~15 detik**.
7. Layar akan menampilkan indikator hijau: **Rata-rata Latensi 151.1 ms, Akurasi Total 90.0%, Akurasi Toko 82.0%**.

Ini akan menjadi bukti validasi paling kuat dalam sidang proyek Anda.
