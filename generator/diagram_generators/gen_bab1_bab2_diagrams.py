"""
=============================================================================
MODUL GENERATOR DIAGRAM BAB I & BAB II (300 DPI)
Menghasilkan diagram ilmiah, arsitektural, dan visualisasi teoritis.
=============================================================================
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "output_bab4"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["axes.edgecolor"] = "#CBD5E1"
plt.rcParams["axes.linewidth"] = 1.0

# ---------------------------------------------------------------------------
# 1. Gambar 1.1: Grafik Tren Transaksi Non-Tunai di Indonesia (2019-2024)
# ---------------------------------------------------------------------------
def generate_gambar_1_1():
    out_path = os.path.join(OUTPUT_DIR, "gambar_1_1_tren_transaksi_digital.png")
    fig, ax1 = plt.subplots(figsize=(10, 5.5), dpi=300)

    years = ["2019", "2020", "2021", "2022", "2023", "2024"]
    volume = [5.2, 8.4, 15.6, 26.8, 41.2, 59.8] # Miliar transaksi
    nominal = [145, 205, 305, 480, 680, 920]    # Triliun Rupiah

    x = np.arange(len(years))
    width = 0.42

    bars = ax1.bar(x - width/2, volume, width, label="Volume Transaksi (Miliar)", color="#2563EB", alpha=0.88, edgecolor="#1E40AF", lw=1.2)
    ax1.set_xlabel("Tahun", fontsize=11, fontweight="bold", labelpad=8)
    ax1.set_ylabel("Volume Transaksi (Miliar Transaksi)", fontsize=11, fontweight="bold", color="#1E40AF", labelpad=8)
    ax1.tick_params(axis="y", labelcolor="#1E40AF")
    ax1.set_xticks(x)
    ax1.set_xticklabels(years, fontsize=10, fontweight="bold")
    ax1.grid(axis="y", linestyle="--", alpha=0.4)

    for bar in bars:
        h = bar.get_height()
        ax1.annotate(f"{h:.1f}", xy=(bar.get_x() + bar.get_width() / 2, h),
                     xytext=(0, 4), textcoords="offset points", ha="center", va="bottom",
                     fontsize=9, fontweight="bold", color="#1E40AF")

    ax2 = ax1.twinx()
    line = ax2.plot(x + width/2, nominal, color="#D97706", marker="o", lw=2.5, markersize=8,
                    label="Nilai Transaksi (Triliun Rp)", markeredgecolor="#78350F", markeredgewidth=1.5)
    ax2.set_ylabel("Nilai Transaksi (Triliun Rupiah)", fontsize=11, fontweight="bold", color="#D97706", labelpad=8)
    ax2.tick_params(axis="y", labelcolor="#D97706")

    for i, val in enumerate(nominal):
        ax2.annotate(f"Rp {val}T", xy=(x[i] + width/2, val), xytext=(0, 7),
                     textcoords="offset points", ha="center", va="bottom",
                     fontsize=9, fontweight="bold", color="#B45309")

    plt.title("Tren Pertumbuhan Transaksi Non-Tunai dan Pembayaran Digital di Indonesia (2019-2024)\n(Sumber: Statistik Sistem Pembayaran Bank Indonesia, 2024)",
              fontsize=11.5, fontweight="bold", pad=14, color="#0F172A")

    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc="upper left", framealpha=0.95, edgecolor="#94A3B8")

    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"[OK] Gambar 1.1 digenerate: {out_path}")

# ---------------------------------------------------------------------------
# 2. Gambar 1.3: Paradigma Cloud-Based AI vs On-Device Edge ML
# ---------------------------------------------------------------------------
def generate_gambar_1_3():
    out_path = os.path.join(OUTPUT_DIR, "gambar_1_3_paradigma_cloud_vs_ondevice.png")
    fig, ax = plt.subplots(figsize=(12, 6.5), dpi=300)
    ax.axis("off")
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7)

    # Title
    ax.text(6, 6.6, "Perbandingan Paradigma: Cloud-Based Document AI vs On-Device Edge ML",
            fontsize=13, fontweight="bold", ha="center", va="center", color="#0F172A")

    # Box 1: Cloud-Based (Left)
    rect1 = patches.FancyBboxPatch((0.5, 0.6), 5.2, 5.6, boxstyle="round,pad=0.2",
                                   ec="#EF4444", fc="#FEF2F2", lw=2.0)
    ax.add_patch(rect1)
    ax.text(3.1, 5.8, "PARADIGMA CLOUD-BASED AI\n(AWS Textract, Azure Form, Google Cloud)",
            fontsize=10.5, fontweight="bold", ha="center", va="center", color="#991B1B")

    steps_cloud = [
        "1. Citra Struk Diunggah via Internet (Upload)",
        "2. Melewati Jaringan Publik & Gateway (Risiko Privasi)",
        "3. Diproses Server GPU Cloud Terpusat",
        "4. Menunggu Hasil Ekstraksi JSON (Network Latency)",
        "5. Mengunduh Respon ke Ponsel Klien"
    ]
    for i, s in enumerate(steps_cloud):
        y = 5.0 - (i * 0.52)
        ax.text(0.8, y, s, fontsize=9, color="#7F1D1D")

    # Karakteristik Cloud
    box_c_kar = patches.FancyBboxPatch((0.7, 0.9), 4.8, 1.35, boxstyle="round,pad=0.1",
                                       ec="#FCA5A5", fc="#FFFFFF", lw=1.2)
    ax.add_patch(box_c_kar)
    ax.text(0.9, 2.0, "Karakteristik & Kelemahan:", fontsize=9.5, fontweight="bold", color="#B91C1C")
    ax.text(0.9, 1.65, "• Latensi Tinggi: 1.500 ms - 4.000 ms\n• Biaya Langganan API Bulanan ($1.50/1.000 struk)\n• Privasi Finansial Rentan di Server Pihak Ketiga\n• Gagal Total di Area Basemen / Tanpa Kuota Internet",
            fontsize=8.5, color="#991B1B")

    # Box 2: On-Device Edge ML (Right)
    rect2 = patches.FancyBboxPatch((6.3, 0.6), 5.2, 5.6, boxstyle="round,pad=0.2",
                                   ec="#10B981", fc="#ECFDF5", lw=2.0)
    ax.add_patch(rect2)
    ax.text(8.9, 5.8, "PARADIGMA ON-DEVICE EDGE ML\n(Google ML Kit + Algoritma Caran)",
            fontsize=10.5, fontweight="bold", ha="center", va="center", color="#065F46")

    steps_edge = [
        "1. Citra Ditangkap Langsung Kamera Ponsel",
        "2. Aliran Buffer Memori Lokal (Zero Internet)",
        "3. Inferensi OCR C++ Binary di Chipset (Helio G99)",
        "4. Rekonstruksi Spasial 2D & Regex Heuristik di CPU",
        "5. Disimpan Seketika ke Database SQLite Lokal"
    ]
    for i, s in enumerate(steps_edge):
        y = 5.0 - (i * 0.52)
        ax.text(6.6, y, s, fontsize=9, color="#064E3B")

    # Karakteristik Edge
    box_e_kar = patches.FancyBboxPatch((6.5, 0.9), 4.8, 1.35, boxstyle="round,pad=0.1",
                                       ec="#6EE7B7", fc="#FFFFFF", lw=1.2)
    ax.add_patch(box_e_kar)
    ax.text(6.7, 2.0, "Keunggulan Nyata Arsitektur Caran:", fontsize=9.5, fontweight="bold", color="#047857")
    ax.text(6.7, 1.65, "• Latensi Instan: Rata-rata 151,1 ms (10x Lebih Cepat)\n• Biaya Operasional: Rp 0 (Zero Server / Cloud Cost)\n• 100% Privasi Terjamin (Data Finansial di Ponsel User)\n• Berjalan Penuh Tanpa Sinyal Seluler / Mode Pesawat",
            fontsize=8.5, color="#065F46")

    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"[OK] Gambar 1.3 digenerate: {out_path}")

# ---------------------------------------------------------------------------
# 3. Gambar 2.1: Arsitektur Ekosistem Offline-First
# ---------------------------------------------------------------------------
def generate_gambar_2_1():
    out_path = os.path.join(OUTPUT_DIR, "gambar_2_1_arsitektur_offline_first.png")
    fig, ax = plt.subplots(figsize=(11, 6), dpi=300)
    ax.axis("off")
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 6)

    ax.text(5.5, 5.6, "Arsitektur Ekosistem Offline-First dengan Local-First Persistence",
            fontsize=12, fontweight="bold", ha="center", va="center", color="#0F172A")

    layers = [
        ("Layer 1: Input & Interaksi Pengguna", "Kamera Fisik, Pemindai Struk, Formulir Entri Manual, Filter Tanggal", "#DBEAFE", "#1E40AF"),
        ("Layer 2: Presentasi & Manajemen State (Flutter)", "DashboardScreen, ScannerScreen, PreviewEditScreen, State Controller", "#E0E7FF", "#3730A3"),
        ("Layer 3: Mesin Kecerdasan Buatan On-Device", "Google ML Kit Text Recognition v2, 2D Spatial Line Clustering, Regex Heuristik", "#FEF3C7", "#92400E"),
        ("Layer 4: Data & Persistensi Lokal (Local-First)", "SQLite C-Engine (receipt_scanner.db), Wal Mode, Prepared Statements", "#D1FAE5", "#065F46"),
        ("Layer 5: Portabilitas & Ekspor Mandiri", "Ekspor Laporan Format CSV Lokal, Manajemen Log Audit Pengujian", "#F3E8FF", "#6B21A8"),
    ]

    for i, (title, desc, bg, fg) in enumerate(layers):
        y = 4.6 - (i * 0.95)
        rect = patches.FancyBboxPatch((1.0, y), 9.0, 0.75, boxstyle="round,pad=0.15",
                                       ec=fg, fc=bg, lw=1.5)
        ax.add_patch(rect)
        ax.text(1.3, y + 0.45, title, fontsize=10, fontweight="bold", color=fg)
        ax.text(1.3, y + 0.18, desc, fontsize=8.5, color="#334155")

        if i < len(layers) - 1:
            ax.annotate("", xy=(5.5, y - 0.05), xytext=(5.5, y + 0.05),
                        arrowprops=dict(arrowstyle="->", color="#64748B", lw=1.8))

    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"[OK] Gambar 2.1 digenerate: {out_path}")

# ---------------------------------------------------------------------------
# 4. Gambar 2.4: Perbandingan Bundled vs Unbundled Google ML Kit
# ---------------------------------------------------------------------------
def generate_gambar_2_4():
    out_path = os.path.join(OUTPUT_DIR, "gambar_2_4_arsitektur_mlkit_bundled_vs_unbundled.png")
    fig, ax = plt.subplots(figsize=(11, 5.5), dpi=300)
    ax.axis("off")
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 6)

    ax.text(5.5, 5.6, "Perbandingan Mode Distribusi Google ML Kit: Bundled vs Unbundled",
            fontsize=12, fontweight="bold", ha="center", va="center", color="#0F172A")

    # Bundled Mode (Left) - Rekomendasi
    rect1 = patches.FancyBboxPatch((0.6, 0.6), 4.7, 4.6, boxstyle="round,pad=0.15",
                                   ec="#2563EB", fc="#EFF6FF", lw=1.8)
    ax.add_patch(rect1)
    ax.text(2.95, 4.8, "BUNDLED MODE (Direkomendasikan)", fontsize=10, fontweight="bold",
            ha="center", color="#1E40AF")
    ax.text(2.95, 4.5, "(Dipilih dalam Penelitian Aplikasi Caran)", fontsize=8.5,
            fontstyle="italic", ha="center", color="#3B82F6")

    b_content = [
        "• Model C++ dan Bobot Termasuk di Dalam APK",
        "• Ukuran Berkas APK Bertambah (+35 MB)",
        "• Waktu Kesiapan: Instan (0 detik sejak instalasi)",
        "• Ketergantungan Jaringan: Nol (100% Offline)",
        "• Kompatibilitas: Mendukung Ponsel Non-GMS\n  (Huawei HarmonyOS, Custom ROM Android)",
        "• Keandalan: Dijamin Berfungsi di Kondisi Apapun"
    ]
    for idx, text in enumerate(b_content):
        ax.text(0.9, 3.8 - (idx * 0.55), text, fontsize=8.5, color="#1E293B")

    # Unbundled Mode (Right)
    rect2 = patches.FancyBboxPatch((5.7, 0.6), 4.7, 4.6, boxstyle="round,pad=0.15",
                                   ec="#94A3B8", fc="#F8FAFC", lw=1.5)
    ax.add_patch(rect2)
    ax.text(8.05, 4.8, "UNBUNDLED MODE (Google Play Services)", fontsize=10, fontweight="bold",
            ha="center", color="#475569")
    ax.text(8.05, 4.5, "(Model Diunduh Dinamis oleh Layanan Google)", fontsize=8.5,
            fontstyle="italic", ha="center", color="#64748B")

    u_content = [
        "• APK Awal Sangat Ringan (~15 MB)",
        "• Model Diunduh Saat Aplikasi Pertama Kali Dibuka",
        "• Waktu Kesiapan: Bergantung Kecepatan Unduh",
        "• Ketergantungan Jaringan: Butuh Akses Internet Awal",
        "• Kompatibilitas: Wajib Ada Google Play Services\n  (Gagal jika Play Store dinonaktifkan)",
        "• Risiko: Gagal OCR jika Pengguna Langsung Buka\n  di Wilayah Basemen / Tanpa Sinyal"
    ]
    for idx, text in enumerate(u_content):
        ax.text(6.0, 3.8 - (idx * 0.55), text, fontsize=8.5, color="#475569")

    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"[OK] Gambar 2.4 digenerate: {out_path}")

# ---------------------------------------------------------------------------
# 5. Gambar 2.10: Ilustrasi Masalah 1D Text Flattening
# ---------------------------------------------------------------------------
def generate_gambar_2_10():
    out_path = os.path.join(OUTPUT_DIR, "gambar_2_10_masalah_1d_text_flattening.png")
    fig, ax = plt.subplots(figsize=(11, 5.5), dpi=300)
    ax.axis("off")
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 6)

    ax.text(5.5, 5.6, "Ilustrasi Masalah 1D Text Flattening vs Rekonstruksi 2D Spasial",
            fontsize=12, fontweight="bold", ha="center", va="center", color="#0F172A")

    # Kolom 1: Struk Kasir Asli Dua Kolom
    r1 = patches.FancyBboxPatch((0.5, 0.6), 3.0, 4.6, boxstyle="round,pad=0.1", ec="#94A3B8", fc="#FFFFFF", lw=1.5)
    ax.add_patch(r1)
    ax.text(2.0, 4.8, "Struk Kasir Asli (2D)", fontsize=9.5, fontweight="bold", ha="center", color="#0F172A")
    ax.text(0.7, 4.0, "INDOMILK UHT 1L\nROTI TAWAR SARI\nMINYAK GOR 2L\nTEH BOTOL SOSRO\nTOTAL", fontsize=8.5, color="#1E293B", family="monospace")
    ax.text(2.4, 4.0, "18.500\n15.000\n34.000\n 4.500\n72.000", fontsize=8.5, color="#1E293B", family="monospace")

    # Kolom 2: Masalah 1D Text Flattening (OCR Polos)
    r2 = patches.FancyBboxPatch((4.0, 0.6), 3.0, 4.6, boxstyle="round,pad=0.1", ec="#EF4444", fc="#FEF2F2", lw=1.5)
    ax.add_patch(r2)
    ax.text(5.5, 4.8, "1D Flattening (Gagal)", fontsize=9.5, fontweight="bold", ha="center", color="#991B1B")
    raw_text = "INDOMILK UHT 1L\nROTI TAWAR SARI\nMINYAK GOR 2L\nTEH BOTOL SOSRO\n18.500\n15.000\n34.000\n4.500\nTOTAL 72.000"
    ax.text(4.2, 4.1, raw_text, fontsize=7.8, color="#7F1D1D", family="monospace")
    ax.text(5.5, 0.9, "[ERROR]\nNama dan Harga Terpisah!", fontsize=8.5, fontweight="bold", ha="center", color="#B91C1C")

    # Kolom 3: Hasil 2D Spatial Clustering (Aplikasi Caran)
    r3 = patches.FancyBboxPatch((7.5, 0.6), 3.0, 4.6, boxstyle="round,pad=0.1", ec="#10B981", fc="#ECFDF5", lw=1.5)
    ax.add_patch(r3)
    ax.text(9.0, 4.8, "2D Spatial Pairing (Sukses)", fontsize=9.5, fontweight="bold", ha="center", color="#065F46")
    success_text = "INDOMILK -> 18.500 [OK]\nROTI TAWAR -> 15.000 [OK]\nMINYAK GOR -> 34.000 [OK]\nTEH BOTOL ->  4.500 [OK]\n----------------------\nTOTAL: Rp 72.000 [OK]"
    ax.text(7.6, 3.8, success_text, fontsize=7.8, color="#064E3B", family="monospace")
    ax.text(9.0, 0.9, "[SUKSES]\nRelasi Baris Terpasang!", fontsize=8.5, fontweight="bold", ha="center", color="#047857")

    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"[OK] Gambar 2.10 digenerate: {out_path}")

# ---------------------------------------------------------------------------
# 6. Gambar 2.11: Diagram Geometris Koordinat Bounding Box
# ---------------------------------------------------------------------------
def generate_gambar_2_11():
    out_path = os.path.join(OUTPUT_DIR, "gambar_2_11_geometri_bounding_box.png")
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
    ax.axis("off")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)

    ax.text(5.0, 5.6, "Diagram Geometris Toleransi Spasial Baris (2D Spatial Clustering)",
            fontsize=12, fontweight="bold", ha="center", va="center", color="#0F172A")

    # Bounding Box A (Item Name)
    rectA = patches.Rectangle((1.0, 2.8), 3.8, 1.4, linewidth=1.8, edgecolor="#2563EB", facecolor="#DBEAFE", alpha=0.8)
    ax.add_patch(rectA)
    ax.text(2.9, 3.5, "KOTAK A: 'INDOMILK UHT 1L'\nB_A = (x_A, y_A, w_A, h_A)", fontsize=8.5, fontweight="bold",
            ha="center", va="center", color="#1E40AF")

    # Centroid A
    ax.plot([1.0, 4.8], [3.5, 3.5], color="#2563EB", linestyle="--", lw=1.2)
    ax.plot(2.9, 3.5, marker="o", color="#1E40AF", markersize=6)
    ax.text(0.8, 3.5, "c_y(A)", fontsize=8.5, fontweight="bold", ha="right", va="center", color="#1E40AF")

    # Bounding Box B (Price)
    rectB = patches.Rectangle((5.8, 2.6), 2.8, 1.3, linewidth=1.8, edgecolor="#059669", facecolor="#D1FAE5", alpha=0.8)
    ax.add_patch(rectB)
    ax.text(7.2, 3.25, "KOTAK B: '18.500'\nB_B = (x_B, y_B, w_B, h_B)", fontsize=8.5, fontweight="bold",
            ha="center", va="center", color="#065F46")

    # Centroid B
    ax.plot([5.8, 8.6], [3.25, 3.25], color="#059669", linestyle="--", lw=1.2)
    ax.plot(7.2, 3.25, marker="o", color="#065F46", markersize=6)
    ax.text(8.8, 3.25, "c_y(B)", fontsize=8.5, fontweight="bold", ha="left", va="center", color="#065F46")

    # Delta Y line
    ax.annotate("", xy=(5.2, 3.25), xytext=(5.2, 3.5),
                arrowprops=dict(arrowstyle="<->", color="#DC2626", lw=1.5))
    ax.text(5.35, 3.37, "|Δy| ≤ α · min(h_A, h_B)", fontsize=8.5, fontweight="bold", color="#DC2626", va="center")

    # Formulas explanation box
    r_f = patches.FancyBboxPatch((1.0, 0.5), 8.0, 1.6, boxstyle="round,pad=0.1", ec="#94A3B8", fc="#F8FAFC", lw=1.2)
    ax.add_patch(r_f)
    ax.text(1.2, 1.8, "Syarat Pengelompokan Baris Horizontal yang Sama:", fontsize=9.5, fontweight="bold", color="#0F172A")
    ax.text(1.2, 1.45, "1. Selisih Titik Tengah Vertikal:  |c_y(A) - c_y(B)| ≤ 0.55 × min(h_A, h_B)", fontsize=8.5, color="#1E293B")
    ax.text(1.2, 1.15, "2. Rasio Tumpang Tindih Vertikal:   VOR(A, B) = [Overlap(y)] / min(h_A, h_B) ≥ 0.45", fontsize=8.5, color="#1E293B")
    ax.text(1.2, 0.85, "3. Pengurutan Horizontal (Kiri ke Kanan): x_A < x_B (Nama Item mendahului Nominal)", fontsize=8.5, color="#1E293B")

    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"[OK] Gambar 2.11 digenerate: {out_path}")

# ---------------------------------------------------------------------------
# 7. Gambar 2.12: Kerangka Pemikiran Teoritis Penelitian
# ---------------------------------------------------------------------------
def generate_gambar_2_12():
    out_path = os.path.join(OUTPUT_DIR, "gambar_2_12_kerangka_pemikiran.png")
    fig, ax = plt.subplots(figsize=(11, 7), dpi=300)
    ax.axis("off")
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 7)

    ax.text(5.5, 6.7, "Kerangka Pemikiran Penelitian Aplikasi Caran",
            fontsize=13, fontweight="bold", ha="center", va="center", color="#0F172A")

    blocks = [
        ("1. Identifikasi Masalah", "• Pengeluaran kasir fisik sering tidak tercatat karena pencatatan manual memakan waktu.\n• Solusi Cloud AI mahal, lambat (>2 detik), dan mengekspos data privasi pengguna.\n• Model end-to-end VLM (Donut) terlalu berat (>1 GB RAM) untuk ponsel mid-range.", "#FEE2E2", "#991B1B"),
        ("2. Pendekatan Teoretis", "• Paradigma Offline-First & Local-First Architecture.\n• Kombinasi Google ML Kit Text Recognition v2 + 2D Spatial Line Clustering.\n• Regex Leksikal Khusus Karakteristik Struk Kasir Ritel Indonesia.", "#FEF3C7", "#92400E"),
        ("3. Rekayasa Prototipe (Aplikasi Caran)", "• Mobile Framework: Flutter SDK & Clean Architecture 3-Tier.\n• Basis Data Lokal: SQLite C-Engine (receipt_scanner.db).\n• Modul UI: Dashboard Analytics, Live Camera OCR, PreviewEdit, CSV Export.", "#DBEAFE", "#1E40AF"),
        ("4. Pengujian Empiris & Evaluasi", "• Uji Beban 100 Sampel CORD-v2 pada Smartphone Fisik TECNO Helio G99.\n• Metrik Akurasi: Entity Precision, Recall, F1-Score, dan Item Pairing Rate.\n• Metrik Efisiensi: Latensi Inferensi (ms), Penggunaan Memori RAM, Baterai, dan Suhu CPU.", "#E0E7FF", "#3730A3"),
        ("5. Hasil & Kontribusi Riset", "• Rata-rata Latensi 151,1 ms (100% Offline, Zero Cloud Cost).\n• Akurasi Ekstraksi Entitas Mencapai 90% pada Struk Standar Ritel Indonesia.\n• Pembuktian Ilmiah Kelayakan Edge Document AI pada Smartphone Menengah.", "#D1FAE5", "#065F46"),
    ]

    for i, (title, content, bg, fg) in enumerate(blocks):
        y = 5.3 - (i * 1.25)
        rect = patches.FancyBboxPatch((0.8, y), 9.4, 1.05, boxstyle="round,pad=0.1", ec=fg, fc=bg, lw=1.5)
        ax.add_patch(rect)
        ax.text(1.0, y + 0.85, title, fontsize=9.5, fontweight="bold", color=fg)
        ax.text(1.0, y + 0.45, content, fontsize=8.0, color="#1E293B")

        if i < len(blocks) - 1:
            ax.annotate("", xy=(5.5, y - 0.18), xytext=(5.5, y - 0.02),
                        arrowprops=dict(arrowstyle="->", color="#64748B", lw=1.5))

    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"[OK] Gambar 2.12 digenerate: {out_path}")

def run_all():
    print("--- GENERATING BAB I & BAB II DIAGRAMS ---")
    generate_gambar_1_1()
    generate_gambar_1_3()
    generate_gambar_2_1()
    generate_gambar_2_4()
    generate_gambar_2_10()
    generate_gambar_2_11()
    generate_gambar_2_12()
    print("--- BAB I & BAB II COMPLETE ---")

if __name__ == "__main__":
    run_all()
