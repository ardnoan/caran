"""
=============================================================================
GENERATOR DIAGRAM TAMBAHAN RESMI SKRIPSI (RESOLUSI TINGGI 300 DPI)
1. Gambar 3.2: Use Case Diagram Sistem Aplikasi Caran (10 Use Case)
2. Gambar 3.15: Arsitektur Bersih Tiga Lapisan (Clean Architecture 3-Tier)
3. Gambar 3.19: Entity-Relationship Diagram (ERD) receipt_scanner.db
4. Gambar 4.2: Diagram Alur Eksperimen Donut pada Workstation GPU RTX
=============================================================================
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output_bab4")
os.makedirs(OUTPUT_DIR, exist_ok=True)

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.family'] = 'sans-serif'

def generate_use_case_diagram():
    """Gambar 3.2: Use Case Diagram Sistem Aplikasi Caran"""
    fig, ax = plt.subplots(figsize=(12, 8), dpi=300)
    ax.axis('off')
    ax.set_xlim(0, 120)
    ax.set_ylim(0, 100)

    # Title
    ax.text(60, 96, "USE CASE DIAGRAM APLIKASI 'CARAN' (OFFLINE-FIRST ON-DEVICE ML)",
            ha='center', va='center', fontsize=12, fontweight='bold', color='#1A365D')

    # Boundary Box (System Boundary)
    sys_box = patches.FancyBboxPatch((35, 5), 75, 87, boxstyle="round,pad=1.5",
                                      facecolor='#F7FAFC', edgecolor='#2B6CB0', linewidth=2)
    ax.add_patch(sys_box)
    ax.text(72.5, 89, "Batas Sistem Aplikasi Caran (Mobile Client)", ha='center', va='center',
            fontsize=10.5, fontweight='bold', color='#2B6CB0')

    # Actor (Pengguna)
    ax.plot([15, 15], [52, 60], color='#2D3748', linewidth=2.5) # body
    ax.plot([8, 22], [57, 57], color='#2D3748', linewidth=2.5) # arms
    ax.plot([15, 10], [52, 43], color='#2D3748', linewidth=2.5) # left leg
    ax.plot([15, 20], [52, 43], color='#2D3748', linewidth=2.5) # right leg
    head = plt.Circle((15, 64), 4, color='#2D3748', fill=False, linewidth=2.5)
    ax.add_patch(head)
    ax.text(15, 36, "Pengguna\n(User)", ha='center', va='center', fontsize=10, fontweight='bold', color='#1A202C')

    # 10 Use Cases (Ellipses)
    use_cases = [
        (72.5, 81, "UC-01: Memindai Struk Fisik via Kamera"),
        (72.5, 73, "UC-02: Memilih Citra Struk dari Galeri"),
        (72.5, 65, "UC-03: Menjalankan Ekstraksi ML Kit On-Device"),
        (72.5, 57, "UC-04: Meninjau & Mengoreksi Data Struk"),
        (72.5, 49, "UC-05: Mencatat Transaksi Pengeluaran Manual"),
        (72.5, 41, "UC-06: Mengelola Kategori & Riwayat Belanja"),
        (72.5, 33, "UC-07: Mengedit & Menghapus Transaksi"),
        (72.5, 25, "UC-08: Mengekspor Laporan Keuangan ke CSV"),
        (72.5, 17, "UC-09: Melihat Log Riwayat Audit Pemindaian"),
        (72.5, 9,  "UC-10: Menjalankan On-Device Benchmark 100 Struk"),
    ]

    for (x, y, text) in use_cases:
        ellipse = patches.Ellipse((x, y), 54, 5.8, facecolor='#EBF8FF', edgecolor='#3182CE', linewidth=1.5)
        ax.add_patch(ellipse)
        ax.text(x, y, text, ha='center', va='center', fontsize=8.5, fontweight='bold', color='#2C5282')

        # Connect actor to use case
        ax.plot([18, 45], [54, y], color='#718096', linestyle='-', linewidth=1)

    plt.tight_layout()
    out_file = os.path.join(OUTPUT_DIR, "diagram_use_case_caran.png")
    plt.savefig(out_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Use Case Diagram tersimpan di: {out_file}")

def generate_clean_architecture_diagram():
    """Gambar 3.15: Clean Architecture 3-Tier Aplikasi Caran"""
    fig, ax = plt.subplots(figsize=(11, 7.5), dpi=300)
    ax.axis('off')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)

    ax.text(50, 96, "ARSITEKTUR BERSIH TIGA LAPISAN (CLEAN ARCHITECTURE 3-TIER)",
            ha='center', va='center', fontsize=12, fontweight='bold', color='#1A365D')
    ax.text(50, 92, "Penerapan Pola Desain Pemisahan Tanggung Jawab pada Aplikasi Caran",
            ha='center', va='center', fontsize=9.5, style='italic', color='#4A5568')

    # Tier 1: Presentation Layer
    tier1 = patches.FancyBboxPatch((10, 64), 80, 24, boxstyle="round,pad=1.2",
                                   facecolor='#EBF8FF', edgecolor='#3182CE', linewidth=2)
    ax.add_patch(tier1)
    ax.text(50, 83, "1. PRESENTATION LAYER (ANTARMUKA PENGGUNA - FLUTTER)",
            ha='center', va='center', fontsize=11, fontweight='bold', color='#2B6CB0')
    desc_t1 = "Widgets UI: DashboardScreen, ScannerScreen, PreviewEditScreen, ItemDetailScreen\nState Management & Formatter: CurrencyTextInputFormatter, DateFormat id_ID\nVisual Charting: fl_chart Library & Interactive Mismatch Banner"
    ax.text(50, 72, desc_t1, ha='center', va='center', fontsize=8.5, color='#2D3748', linespacing=1.4)

    # Arrow Tier 1 -> Tier 2
    ax.annotate('', xy=(50, 59), xytext=(50, 64),
                arrowprops=dict(facecolor='#4A5568', edgecolor='#4A5568', width=2, headwidth=7))

    # Tier 2: Domain & Service Layer
    tier2 = patches.FancyBboxPatch((10, 34), 80, 24, boxstyle="round,pad=1.2",
                                   facecolor='#FEFCBF', edgecolor='#D69E2E', linewidth=2)
    ax.add_patch(tier2)
    ax.text(50, 53, "2. DOMAIN & APPLICATION SERVICE LAYER (LOGIKA BISNIS & ML)",
            ha='center', va='center', fontsize=11, fontweight='bold', color='#B7791F')
    desc_t2 = "On-Device Engine: OfflineReceiptService (Singleton Native C++ TFLite Google ML Kit)\nSpasial & Heuristik: Spatial Line Clustering (_reconstructSpatialLines)\nRegex Engine: Retail Brand Reconstruction, Date-Time Regex, & Junk-Line Filter"
    ax.text(50, 42, desc_t2, ha='center', va='center', fontsize=8.5, color='#2D3748', linespacing=1.4)

    # Arrow Tier 2 -> Tier 3
    ax.annotate('', xy=(50, 29), xytext=(50, 34),
                arrowprops=dict(facecolor='#4A5568', edgecolor='#4A5568', width=2, headwidth=7))

    # Tier 3: Data & Persistence Layer
    tier3 = patches.FancyBboxPatch((10, 5), 80, 23, boxstyle="round,pad=1.2",
                                   facecolor='#E6FFFA', edgecolor='#319795', linewidth=2)
    ax.add_patch(tier3)
    ax.text(50, 23, "3. DATA & PERSISTENCE LAYER (PENYIMPANAN DATA LOKAL)",
            ha='center', va='center', fontsize=11, fontweight='bold', color='#234E52')
    desc_t3 = "Repository SQLite: DatabaseHelper.dart (receipt_scanner.db)\nRelational Tables: transactions, transaction_items (Cascade FK), scan_logs\nFile Storage: Local Android App Internal Storage (Foto Struk & Ekspor CSV)"
    ax.text(50, 13, desc_t3, ha='center', va='center', fontsize=8.5, color='#2D3748', linespacing=1.4)

    plt.tight_layout()
    out_file = os.path.join(OUTPUT_DIR, "diagram_clean_architecture_3tier.png")
    plt.savefig(out_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Clean Architecture Diagram tersimpan di: {out_file}")

def generate_erd_diagram():
    """Gambar 3.19: Entity-Relationship Diagram (ERD) receipt_scanner.db"""
    fig, ax = plt.subplots(figsize=(12, 7), dpi=300)
    ax.axis('off')
    ax.set_xlim(0, 120)
    ax.set_ylim(0, 80)

    ax.text(60, 76, "ENTITY-RELATIONSHIP DIAGRAM (ERD) BASIS DATA 'receipt_scanner.db'",
            ha='center', va='center', fontsize=12, fontweight='bold', color='#1A365D')

    # Table 1: TRANSACTIONS
    t1 = patches.FancyBboxPatch((8, 15), 32, 53, boxstyle="round,pad=1",
                                facecolor='#FFFFFF', edgecolor='#2B6CB0', linewidth=2)
    ax.add_patch(t1)
    ax.plot([8, 40], [61, 61], color='#2B6CB0', linewidth=1.5)
    ax.text(24, 64, "TABLE: transactions", ha='center', va='center', fontsize=9.5, fontweight='bold', color='#2B6CB0')
    t1_fields = (
        "[PK] id: INTEGER (PK Auto)\n"
        "* store_name: TEXT\n"
        "* total_amount: REAL\n"
        "* transaction_date: TEXT (ISO)\n"
        "* image_path: TEXT (Nullable)\n"
        "* raw_ocr_text: TEXT\n"
        "* category: TEXT ('Belanja Harian')\n"
        "* created_at: TEXT"
    )
    ax.text(10, 37, t1_fields, ha='left', va='center', fontsize=8.5, color='#2D3748', linespacing=1.4)

    # Table 2: TRANSACTION_ITEMS
    t2 = patches.FancyBboxPatch((46, 18), 32, 47, boxstyle="round,pad=1",
                                facecolor='#FFFFFF', edgecolor='#38A169', linewidth=2)
    ax.add_patch(t2)
    ax.plot([46, 78], [58, 58], color='#38A169', linewidth=1.5)
    ax.text(62, 61, "TABLE: transaction_items", ha='center', va='center', fontsize=9.5, fontweight='bold', color='#22543D')
    t2_fields = (
        "[PK] id: INTEGER (PK Auto)\n"
        "[FK] transaction_id: INTEGER (FK)\n"
        "* item_name: TEXT\n"
        "* item_price: REAL\n"
        "* quantity: INTEGER\n"
        "* subtotal: REAL\n"
        "-> ON DELETE CASCADE"
    )
    ax.text(48, 38, t2_fields, ha='left', va='center', fontsize=8.5, color='#2D3748', linespacing=1.4)

    # Connector 1 to Many (transactions 1 -> N transaction_items)
    ax.annotate('', xy=(46, 42), xytext=(40, 42),
                arrowprops=dict(facecolor='#E53E3E', edgecolor='#E53E3E', width=2, headwidth=7))
    ax.text(40.5, 45, "1", fontsize=9, fontweight='bold', color='#E53E3E')
    ax.text(44.5, 45, "N", fontsize=9, fontweight='bold', color='#E53E3E')

    # Table 3: SCAN_LOGS (Audit & Research Benchmarking)
    t3 = patches.FancyBboxPatch((84, 15), 32, 53, boxstyle="round,pad=1",
                                facecolor='#FFFFFF', edgecolor='#DD6B20', linewidth=2)
    ax.add_patch(t3)
    ax.plot([84, 116], [61, 61], color='#DD6B20', linewidth=1.5)
    ax.text(100, 64, "TABLE: scan_logs", ha='center', va='center', fontsize=9.5, fontweight='bold', color='#C05621')
    t3_fields = (
        "[PK] id: INTEGER (PK Auto)\n"
        "* timestamp: TEXT\n"
        "* image_path: TEXT\n"
        "* inference_mode: TEXT\n"
        "* execution_time_ms: INTEGER\n"
        "* detected_store: TEXT\n"
        "* detected_total: REAL\n"
        "* item_count: INTEGER\n"
        "* status: TEXT (SUCCESS/WARN)"
    )
    ax.text(86, 37, t3_fields, ha='left', va='center', fontsize=8.5, color='#2D3748', linespacing=1.4)

    plt.tight_layout()
    out_file = os.path.join(OUTPUT_DIR, "diagram_erd_receipt_scanner.png")
    plt.savefig(out_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] ERD Diagram tersimpan di: {out_file}")

if __name__ == "__main__":
    print("=" * 60)
    print("MEMPROSES DIAGRAM TEKNIS TAMBAHAN SKRIPSI...")
    print("=" * 60)
    generate_use_case_diagram()
    generate_clean_architecture_diagram()
    generate_erd_diagram()
    print("=" * 60)
    print("SEMUA DIAGRAM TAMBAHAN BERHASIL DIBUAT!")
    print("=" * 60)
