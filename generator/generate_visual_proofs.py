"""
=============================================================================
GENERATOR DIAGRAM & GRAFIK BUKTI ILMIAH SKRIPSI (RESOLUSI TINGGI 300 DPI)
Judul Skripsi:
RANCANG BANGUN APLIKASI PENCATATAN PENGELUARAN PRIBADI BERBASIS OFFLINE-FIRST
MENGGUNAKAN ON-DEVICE MACHINE LEARNING DENGAN EKSTRAKSI STRUK BELANJA FISIK
Caran Architecture & Empirical Proof Generator
=============================================================================
"""

import os
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.gridspec import GridSpec

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output_bab4")
os.makedirs(OUTPUT_DIR, exist_ok=True)

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.family'] = 'sans-serif'

def generate_diagram_alur_pemilihan():
    """Diagram Alur Keputusan Rekayasa Pemilihan & Eliminasi Model (Bab III/IV)"""
    fig, ax = plt.subplots(figsize=(13, 8), dpi=300)
    ax.axis('off')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)

    # Header Title
    ax.text(50, 96, "METODOLOGI EKSPERIMEN & KEPUTUSAN ELIMINASI MODEL ARSITEKTUR",
            ha='center', va='center', fontsize=14, fontweight='bold', color='#1A365D')
    ax.text(50, 92, "Studi Komparasi Vision Transformer (Donut) vs Native On-Device Edge ML (Caran v0.9.0)",
            ha='center', va='center', fontsize=10, style='italic', color='#4A5568')

    # Step 1: Pretrained Donut
    box1 = patches.FancyBboxPatch((4, 60), 26, 25, boxstyle="round,pad=1.5",
                                  facecolor='#EBF8FF', edgecolor='#3182CE', linewidth=2)
    ax.add_patch(box1)
    ax.text(17, 81, "FASE 1: PRETRAINED DONUT", ha='center', va='center', fontsize=11, fontweight='bold', color='#2B6CB0')
    ax.text(17, 72, "Model: CORD-v2 & mychen76\nLingkungan: GPU Server (PyTorch)\nHasil: Akurasi Tinggi (100%)\nLatensi: 1,1 - 1,4 detik",
            ha='center', va='center', fontsize=9, color='#2D3748')
    ax.text(17, 63, "[DIELIMINASI]\nKetergantungan Cloud/Internet,\nBiaya Server & Kebocoran Privasi",
            ha='center', va='center', fontsize=8.5, fontweight='bold', color='#C53030')

    # Arrow 1 -> 2
    ax.annotate('', xy=(34, 72.5), xytext=(30, 72.5),
                arrowprops=dict(facecolor='#718096', edgecolor='#718096', width=2, headwidth=8))

    # Step 2: Fine-Tuning From Scratch / Transfer
    box2 = patches.FancyBboxPatch((35, 60), 28, 25, boxstyle="round,pad=1.5",
                                  facecolor='#FEFCBF', edgecolor='#D69E2E', linewidth=2)
    ax.add_patch(box2)
    ax.text(49, 81, "FASE 2: FINE-TUNING 300 STEPS", ha='center', va='center', fontsize=11, fontweight='bold', color='#B7791F')
    ax.text(49, 72, "Dataset: Bukti Transfer Lokal (128)\nEksperimen: Fine-tuning LoRA/Full\nMasalah: Catastrophic Forgetting\n& Infinite Looping Token <s_cord-v2>",
            ha='center', va='center', fontsize=9, color='#2D3748')
    ax.text(49, 63, "[DIELIMINASI]\nKehilangan pemahaman struk fisik ritel,\nButuh jutaan data untuk scratch",
            ha='center', va='center', fontsize=8.5, fontweight='bold', color='#C53030')

    # Arrow 2 -> 3
    ax.annotate('', xy=(67, 72.5), xytext=(63, 72.5),
                arrowprops=dict(facecolor='#718096', edgecolor='#718096', width=2, headwidth=8))

    # Step 3: On-Device INT8 Quantization
    box3 = patches.FancyBboxPatch((68, 60), 28, 25, boxstyle="round,pad=1.5",
                                  facecolor='#FED7D7', edgecolor='#E53E3E', linewidth=2)
    ax.add_patch(box3)
    ax.text(82, 81, "FASE 3: DONUT ON-DEVICE INT8", ha='center', va='center', fontsize=11, fontweight='bold', color='#9B2C2C')
    ax.text(82, 72, "Teknik: Dynamic Quantization ONNX\nBobot: 1 GB -> 263,5 MB\nUji HP: MediaTek Helio G99 CPU\nLatensi: 28,4 - 40 detik / struk",
            ha='center', va='center', fontsize=9, color='#2D3748')
    ax.text(82, 63, "[DIELIMINASI]\nThermal Throttling HP, ANR Freeze,\n& Quantization Drift (Total Rp 0)",
            ha='center', va='center', fontsize=8.5, fontweight='bold', color='#C53030')

    # Big Down Arrow from Step 3 to Final Phase
    ax.annotate('', xy=(50, 48), xytext=(82, 58),
                arrowprops=dict(facecolor='#319795', edgecolor='#319795', width=3, headwidth=10))

    # Final Selected Architecture: Google ML Kit + Spatial Clustering
    box_final = patches.FancyBboxPatch((12, 10), 76, 36, boxstyle="round,pad=2",
                                       facecolor='#E6FFFA', edgecolor='#319795', linewidth=3)
    ax.add_patch(box_final)
    ax.text(50, 42, "FASE 4: ARSITEKTUR TERPILIH SKRIPSI (100% ON-DEVICE OFFLINE)",
            ha='center', va='center', fontsize=12.5, fontweight='bold', color='#234E52')
    ax.text(50, 37, "Pipeline Terpadu: Google ML Kit (Native C++) + Spatial Line Clustering + Heuristic Regex Engine",
            ha='center', va='center', fontsize=10.5, fontweight='bold', color='#2C7A7B')

    metrics_text = (
        "* 100% Offline-First (Tanpa Internet / Zero Cloud Leak)\n"
        "* Latensi Rata-Rata: 151,1 ms (~0,15 detik) pada MediaTek Helio G99\n"
        "* Ukuran APK Ringan: 35,7 MB (Hemat 88% dibanding Donut INT8)\n"
        "* Alokasi Memori RAM: 68 MB (Tanpa Overheat & 0 Crash / 0 ANR)\n"
        "* Akurasi Deteksi Total: 90,0% | Akurasi Toko: 82,0% (Uji 100 Struk CORD-v2)\n"
        "* Fitur Khusus Indonesia: Normalisasi Tanggal, Filter Derau NPWP, & Diskon VC Kasir"
    )
    ax.text(50, 23, metrics_text, ha='center', va='center', fontsize=10, color='#1A202C', linespacing=1.4)

    plt.tight_layout()
    out_file = os.path.join(OUTPUT_DIR, "diagram_1_alur_pemilihan_dan_eliminasi_model.png")
    plt.savefig(out_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Diagram 1 tersimpan di: {out_file}")

def generate_diagram_pipeline_spatial():
    """Diagram Arsitektur Pipeline Ekstraksi Spasial Caran (Bab III)"""
    fig, ax = plt.subplots(figsize=(14, 7), dpi=300)
    ax.axis('off')
    ax.set_xlim(0, 140)
    ax.set_ylim(0, 80)

    ax.text(70, 75, "PIPELINE ON-DEVICE EDGE ML DENGAN SPATIAL LINE CLUSTERING",
            ha='center', va='center', fontsize=13, fontweight='bold', color='#1A365D')

    stages = [
        {"x": 5, "w": 22, "title": "1. INPUT CITRA", "desc": "Kamera Fisik / Galeri\nViewfinder Panduan\nTorch Lighting\nResolusi Full HD", "color": "#EDF2F7", "border": "#4A5568"},
        {"x": 32, "w": 24, "title": "2. ML KIT OCR", "desc": "Native C++ TFLite\nCNN + BiLSTM CTC\nDeteksi Bounding Box\n(Xmin, Ymin, W, H)", "color": "#EBF8FF", "border": "#3182CE"},
        {"x": 61, "w": 26, "title": "3. SPATIAL CLUSTER", "desc": "Klasterisasi Sumbu Y\nGrouping Irisan Baris\nPenggabungan Kolom Kiri\n(Barang) & Kanan (Harga)", "color": "#FEFCBF", "border": "#D69E2E"},
        {"x": 92, "w": 24, "title": "4. HEURISTIC REGEX", "desc": "Filter Derau NPWP/Kasir\nParser Tanggal Struk\nIdentifikasi Nama & Qty\nPenanganan Diskon VC", "color": "#E6FFFA", "border": "#319795"},
        {"x": 120, "w": 16, "title": "5. OUTPUT", "desc": "Preview Edit\nAuto Formatter\nSQLite DB\nDashboard CSV", "color": "#FEEBC8", "border": "#DD6B20"}
    ]

    for i, stg in enumerate(stages):
        box = patches.FancyBboxPatch((stg["x"], 20), stg["w"], 45, boxstyle="round,pad=1.2",
                                      facecolor=stg["color"], edgecolor=stg["border"], linewidth=2)
        ax.add_patch(box)
        ax.text(stg["x"] + stg["w"]/2, 60, stg["title"], ha='center', va='center', fontsize=10.5, fontweight='bold', color='#1A202C')
        ax.text(stg["x"] + stg["w"]/2, 38, stg["desc"], ha='center', va='center', fontsize=9, color='#2D3748', linespacing=1.4)

        if i < len(stages) - 1:
            next_x = stages[i+1]["x"]
            curr_right = stg["x"] + stg["w"]
            mid_x = (curr_right + next_x) / 2
            ax.annotate('', xy=(next_x, 42.5), xytext=(curr_right, 42.5),
                        arrowprops=dict(facecolor='#718096', edgecolor='#718096', width=2, headwidth=6))

    ax.text(70, 8, "Prinsip Utama: 100% On-Device Offline | Zero Network Latency | Privasi Finansial Terjamin Mutlak",
            ha='center', va='center', fontsize=10, style='italic', color='#4A5568')

    plt.tight_layout()
    out_file = os.path.join(OUTPUT_DIR, "diagram_2_pipeline_spatial_clustering_caran.png")
    plt.savefig(out_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Diagram 2 tersimpan di: {out_file}")

def generate_visual_spatial_clustering_sample():
    """Visualisasi Ilustrasi Masalah 2 Kolom Struk Kasir & Solusi Bounding Box Spasial"""
    fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
    ax.set_facecolor('#FAF5FF')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)

    ax.set_title("Visualisasi Spatial Line Clustering pada Struk Kasir 2 Kolom (Nama vs Harga)",
                 fontsize=12, fontweight='bold', pad=15, color='#2D3748')

    # Receipt paper mockup
    receipt_bg = patches.Rectangle((10, 5), 80, 88, facecolor='#FFFFFF', edgecolor='#CBD5E0', linewidth=1.5)
    ax.add_patch(receipt_bg)

    # Store Header
    ax.text(50, 87, "ALFAMART JALAPRANG", ha='center', va='center', fontsize=12, fontweight='bold', color='#2D3748')
    ax.text(50, 83, "JL. JALAPRANG NO. 20, BANDUNG", ha='center', va='center', fontsize=8.5, color='#718096')
    ax.text(50, 79, "Tgl. 09-09-2026 18:29:51", ha='center', va='center', fontsize=8.5, color='#718096')
    ax.plot([15, 85], [76, 76], color='#E2E8F0', linestyle='--', linewidth=1)

    # Sample Items with Bounding Boxes
    items = [
        {"y": 68, "name": "SR TUR SP J555G 1", "price": "18.000", "h": 5},
        {"y": 58, "name": "INDOMIE AYAM BAWANG 2", "price": "6.200", "h": 5},
        {"y": 48, "name": "ULTRA MILK COKLAT 200ML 1", "price": "6.500", "h": 5},
        {"y": 38, "name": "KP BRANDING (M) -1", "price": "-200", "h": 5}
    ]

    for it in items:
        # Box Name (Left Column)
        b_name = patches.Rectangle((15, it["y"] - 2.5), 45, it["h"],
                                   facecolor='#EBF8FF', edgecolor='#3182CE', linewidth=1.5, linestyle='-')
        ax.add_patch(b_name)
        ax.text(17, it["y"], it["name"], ha='left', va='center', fontsize=9, fontweight='bold', color='#2B6CB0')

        # Box Price (Right Column)
        b_price = patches.Rectangle((67, it["y"] - 2.5), 18, it["h"],
                                    facecolor='#FEFCBF', edgecolor='#D69E2E', linewidth=1.5, linestyle='-')
        ax.add_patch(b_price)
        ax.text(76, it["y"], it["price"], ha='center', va='center', fontsize=9, fontweight='bold', color='#B7791F')

        # Spatial Line Connector Arrow (Merging them into 1 line)
        ax.annotate('', xy=(67, it["y"]), xytext=(60, it["y"]),
                    arrowprops=dict(facecolor='#38A169', edgecolor='#38A169', width=1.5, headwidth=5))

    # Total Section
    ax.plot([15, 85], [30, 30], color='#CBD5E0', linewidth=1)
    b_total_label = patches.Rectangle((15, 20), 40, 6, facecolor='#E6FFFA', edgecolor='#319795', linewidth=1.5)
    ax.add_patch(b_total_label)
    ax.text(17, 23, "TOTAL BELANJA", ha='left', va='center', fontsize=10, fontweight='bold', color='#234E52')

    b_total_val = patches.Rectangle((62, 20), 23, 6, facecolor='#C6F6D5', edgecolor='#38A169', linewidth=2)
    ax.add_patch(b_total_val)
    ax.text(73.5, 23, "30.500", ha='center', va='center', fontsize=11, fontweight='bold', color='#22543D')

    # Legend / Annotation
    ax.text(50, 10, "[Analisis Spasial]: Kolom Nama (Biru) & Kolom Harga (Kuning) disatukan berdasarkan irisan koordinat vertikal Y\nsehingga mesin regex membaca satu baris utuh secara horizontal dari kiri ke kanan.",
            ha='center', va='center', fontsize=8.5, style='italic', color='#4A5568')

    ax.axis('off')
    plt.tight_layout()
    out_file = os.path.join(OUTPUT_DIR, "visualisasi_spatial_line_clustering_sample.png")
    plt.savefig(out_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Visualisasi spasial tersimpan di: {out_file}")

def generate_grafik_distribusi_latensi():
    """Grafik Distribusi Latensi Pengujian 100 Sampel CORD-v2 pada Helio G99"""
    json_path = os.path.join(OUTPUT_DIR, "benchmark_cord_100_on_device_tecno.json")
    if not os.path.exists(json_path):
        print("[WARN] Data json 100 struk tidak ditemukan.")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    latencies = [r['elapsedMs'] for r in data['results']]

    fig, (ax_box, ax_hist) = plt.subplots(2, 1, figsize=(9, 6.5), dpi=300, gridspec_kw={'height_ratios': [0.25, 0.75]})

    # 1. Boxplot
    bp = ax_box.boxplot(latencies, vert=False, patch_artist=True,
                        boxprops=dict(facecolor='#81E6D9', color='#319795', linewidth=1.5),
                        medianprops=dict(color='#234E52', linewidth=2),
                        whiskerprops=dict(color='#319795', linewidth=1.5),
                        capprops=dict(color='#319795', linewidth=1.5),
                        flierprops=dict(marker='o', markerfacecolor='#E53E3E', markersize=4))
    ax_box.set_facecolor('#F7FAFC')
    ax_box.set_yticks([])
    ax_box.set_xlim(50, 380)
    ax_box.set_title("Distribusi Empiris Latensi Pemrosesan 100 Struk CORD-v2 (TECNO Helio G99)", fontsize=11, fontweight='bold')

    # 2. Histogram
    n, bins, patches_hist = ax_hist.hist(latencies, bins=16, color='#319795', edgecolor='white', alpha=0.85)
    ax_hist.axvline(np.mean(latencies), color='#E53E3E', linestyle='--', linewidth=2, label=f"Rata-rata: {np.mean(latencies):.1f} ms")
    ax_hist.axvline(np.median(latencies), color='#2B6CB0', linestyle='-', linewidth=2, label=f"Median: {np.median(latencies):.1f} ms")
    ax_hist.axvline(71, color='#38A169', linestyle=':', linewidth=1.5, label="Min: 71 ms")
    ax_hist.axvline(353, color='#DD6B20', linestyle=':', linewidth=1.5, label="Max: 353 ms")

    ax_hist.set_facecolor('#F7FAFC')
    ax_hist.set_xlabel("Latensi Inferensi On-Device (Milidetik)", fontweight='bold')
    ax_hist.set_ylabel("Frekuensi Struk", fontweight='bold')
    ax_hist.set_xlim(50, 380)
    ax_hist.legend(loc='upper right', frameon=True, facecolor='white')

    plt.tight_layout()
    out_file = os.path.join(OUTPUT_DIR, "grafik_4_distribusi_latensi_100_struk.png")
    plt.savefig(out_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Grafik 4 tersimpan di: {out_file}")

if __name__ == "__main__":
    print("=" * 60)
    print("MEMPROSES GENERASI DIAGRAM & GRAFIK BUKTI ILMIAH SKRIPSI...")
    print("=" * 60)
    generate_diagram_alur_pemilihan()
    generate_diagram_pipeline_spatial()
    generate_visual_spatial_clustering_sample()
    generate_grafik_distribusi_latensi()
    print("=" * 60)
    print("SEMUA BUKTI GRAFIS BERHASIL DIBUAT DENGAN RESOLUSI 300 DPI!")
    print("=" * 60)
