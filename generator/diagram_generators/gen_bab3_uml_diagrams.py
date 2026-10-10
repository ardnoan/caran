"""
=============================================================================
MODUL GENERATOR DIAGRAM BAB III: UML & REKAYASA PERANGKAT LUNAK (300 DPI)
Menghasilkan Activity Diagram, Sequence Diagram, Class Diagram, State Machine,
Flowchart Regex/NPWP, serta Wireframe UI Aplikasi Caran.
=============================================================================
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches

OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "output_bab4"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

plt.rcParams["font.sans-serif"] = "DejaVu Sans"

# ---------------------------------------------------------------------------
# 1. Gambar 3.3: Activity Diagram Alur Pemindaian dan Ekstraksi Struk
# ---------------------------------------------------------------------------
def generate_gambar_3_3():
    out_path = os.path.join(OUTPUT_DIR, "gambar_3_3_activity_scan_ekstraksi.png")
    fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
    ax.axis("off")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)

    ax.text(5.0, 9.6, "Activity Diagram: Alur Pemindaian dan Ekstraksi Struk Belanja",
            fontsize=12, fontweight="bold", ha="center", color="#0F172A")

    # Start Node
    start_circle = patches.Circle((5.0, 9.0), 0.22, fc="#0F172A", ec="#0F172A")
    ax.add_patch(start_circle)
    ax.text(5.0, 9.3, "Mulai", fontsize=8.5, ha="center", color="#475569")

    nodes = [
        ("Membuka ScannerScreen dari Dashboard", 8.2, "#DBEAFE", "#1E40AF"),
        ("Mengarahkan Kamera & Menekan Tombol Jepret", 7.2, "#DBEAFE", "#1E40AF"),
        ("Menyimpan Frame Citra ke Temporary Storage", 6.2, "#E0E7FF", "#3730A3"),
        ("Mengirim Citra ke Google ML Kit C++ Engine", 5.2, "#FEF3C7", "#92400E"),
        ("Ekstraksi Raw Text & Bounding Box Koordinat", 4.2, "#FEF3C7", "#92400E"),
        ("Menjalankan Algoritma 2D Spatial Line Clustering", 3.2, "#D1FAE5", "#065F46"),
        ("Parsing Heuristik: Merchant, Tanggal, Item, Total", 2.2, "#D1FAE5", "#065F46"),
        ("Membuka Layar Pratinjau (PreviewEditScreen)", 1.2, "#DBEAFE", "#1E40AF"),
    ]

    for text, y, bg, fg in nodes:
        rect = patches.FancyBboxPatch((1.5, y - 0.35), 7.0, 0.7, boxstyle="round,pad=0.1", ec=fg, fc=bg, lw=1.5)
        ax.add_patch(rect)
        ax.text(5.0, y, text, fontsize=9, fontweight="bold", ha="center", va="center", color=fg)

    # Connecting arrows
    ax.annotate("", xy=(5.0, 8.55), xytext=(5.0, 8.78), arrowprops=dict(arrowstyle="->", color="#475569", lw=1.5))
    for i in range(len(nodes) - 1):
        y_top = nodes[i][1] - 0.35
        y_bot = nodes[i+1][1] + 0.35
        ax.annotate("", xy=(5.0, y_bot), xytext=(5.0, y_top), arrowprops=dict(arrowstyle="->", color="#475569", lw=1.5))

    # End Node
    end_outer = patches.Circle((5.0, 0.35), 0.22, fc="none", ec="#0F172A", lw=1.5)
    end_inner = patches.Circle((5.0, 0.35), 0.14, fc="#0F172A", ec="#0F172A")
    ax.add_patch(end_outer)
    ax.add_patch(end_inner)
    ax.annotate("", xy=(5.0, 0.6), xytext=(5.0, 0.85), arrowprops=dict(arrowstyle="->", color="#475569", lw=1.5))
    ax.text(5.0, 0.05, "Selesai", fontsize=8.5, ha="center", color="#475569")

    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"[OK] Gambar 3.3 digenerate: {out_path}")

# ---------------------------------------------------------------------------
# 2. Gambar 3.4: Activity Diagram Alur Pratinjau dan Koreksi Data Interaktif
# ---------------------------------------------------------------------------
def generate_gambar_3_4():
    out_path = os.path.join(OUTPUT_DIR, "gambar_3_4_activity_preview_edit.png")
    fig, ax = plt.subplots(figsize=(10, 8.5), dpi=300)
    ax.axis("off")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10.5)

    ax.text(5.0, 10.1, "Activity Diagram: Alur Pratinjau dan Koreksi Data Interaktif",
            fontsize=12, fontweight="bold", ha="center", color="#0F172A")

    # Start Node
    start_circle = patches.Circle((5.0, 9.5), 0.2, fc="#0F172A", ec="#0F172A")
    ax.add_patch(start_circle)

    # 1. Menampilkan Hasil Ekstraksi
    r1 = patches.FancyBboxPatch((2.0, 8.4), 6.0, 0.65, boxstyle="round,pad=0.1", ec="#1E40AF", fc="#DBEAFE", lw=1.5)
    ax.add_patch(r1)
    ax.text(5.0, 8.72, "Menampilkan Hasil Ekstraksi pada Form PreviewEditScreen", fontsize=8.5, fontweight="bold", ha="center", color="#1E40AF")
    ax.annotate("", xy=(5.0, 9.05), xytext=(5.0, 9.3), arrowprops=dict(arrowstyle="->", color="#475569", lw=1.5))

    # 2. Validasi Selisih Subtotal vs Total
    r2 = patches.FancyBboxPatch((2.0, 7.3), 6.0, 0.65, boxstyle="round,pad=0.1", ec="#3730A3", fc="#E0E7FF", lw=1.5)
    ax.add_patch(r2)
    ax.text(5.0, 7.62, "Sistem Memverifikasi: Subtotal Item == Total Struk?", fontsize=8.5, fontweight="bold", ha="center", color="#3730A3")
    ax.annotate("", xy=(5.0, 7.95), xytext=(5.0, 8.4), arrowprops=dict(arrowstyle="->", color="#475569", lw=1.5))

    # Decision Diamond
    diamond = patches.Polygon([[5.0, 6.7], [6.2, 6.1], [5.0, 5.5], [3.8, 6.1]], ec="#D97706", fc="#FEF3C7", lw=1.5)
    ax.add_patch(diamond)
    ax.text(5.0, 6.1, "Total\nCocok?", fontsize=8.5, fontweight="bold", ha="center", va="center", color="#92400E")
    ax.annotate("", xy=(5.0, 6.7), xytext=(5.0, 7.3), arrowprops=dict(arrowstyle="->", color="#475569", lw=1.5))

    # Branch Tidak: Banner Peringatan
    r_warn = patches.FancyBboxPatch((0.5, 4.8), 3.2, 0.65, boxstyle="round,pad=0.1", ec="#DC2626", fc="#FEE2E2", lw=1.2)
    ax.add_patch(r_warn)
    ax.text(2.1, 5.12, "Tampilkan Banner Kuning/Merah:\n'Selisih Subtotal Terdeteksi'", fontsize=7.5, fontweight="bold", ha="center", color="#991B1B")
    ax.annotate("", xy=(2.1, 5.45), xytext=(3.8, 6.1), arrowprops=dict(arrowstyle="->", color="#DC2626", lw=1.3))
    ax.text(2.6, 6.0, "[Tidak Cocok]", fontsize=7.5, color="#DC2626", fontweight="bold")

    # Branch Ya
    ax.text(6.4, 6.0, "[Cocok]", fontsize=7.5, color="#059669", fontweight="bold")

    # Koreksi Manual Pengguna
    r_edit = patches.FancyBboxPatch((2.0, 3.8), 6.0, 0.65, boxstyle="round,pad=0.1", ec="#2563EB", fc="#EFF6FF", lw=1.5)
    ax.add_patch(r_edit)
    ax.text(5.0, 4.12, "Pengguna Melakukan Koreksi Nama/Harga/Kategori Transaksi", fontsize=8.5, fontweight="bold", ha="center", color="#1E40AF")
    ax.annotate("", xy=(5.0, 4.45), xytext=(5.0, 5.5), arrowprops=dict(arrowstyle="->", color="#475569", lw=1.5))
    ax.annotate("", xy=(3.5, 4.45), xytext=(2.1, 4.8), arrowprops=dict(arrowstyle="->", color="#475569", lw=1.3))

    # Simpan ke SQLite
    r_save = patches.FancyBboxPatch((2.0, 2.7), 6.0, 0.65, boxstyle="round,pad=0.1", ec="#059669", fc="#D1FAE5", lw=1.5)
    ax.add_patch(r_save)
    ax.text(5.0, 3.02, "Menekan Tombol 'Simpan Transaksi' -> Eksekusi SQLite Insert", fontsize=8.5, fontweight="bold", ha="center", color="#065F46")
    ax.annotate("", xy=(5.0, 3.35), xytext=(5.0, 3.8), arrowprops=dict(arrowstyle="->", color="#475569", lw=1.5))

    # Update Dashboard
    r_dash = patches.FancyBboxPatch((2.0, 1.6), 6.0, 0.65, boxstyle="round,pad=0.1", ec="#059669", fc="#D1FAE5", lw=1.5)
    ax.add_patch(r_dash)
    ax.text(5.0, 1.92, "Kembali ke Dashboard & Refresh Data Pengeluaran", fontsize=8.5, fontweight="bold", ha="center", color="#065F46")
    ax.annotate("", xy=(5.0, 2.25), xytext=(5.0, 2.7), arrowprops=dict(arrowstyle="->", color="#475569", lw=1.5))

    # End
    end_outer = patches.Circle((5.0, 0.8), 0.2, fc="none", ec="#0F172A", lw=1.5)
    end_inner = patches.Circle((5.0, 0.8), 0.12, fc="#0F172A", ec="#0F172A")
    ax.add_patch(end_outer)
    ax.add_patch(end_inner)
    ax.annotate("", xy=(5.0, 1.0), xytext=(5.0, 1.6), arrowprops=dict(arrowstyle="->", color="#475569", lw=1.5))
    ax.text(5.0, 0.45, "Selesai", fontsize=8.5, ha="center", color="#475569")

    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"[OK] Gambar 3.4 digenerate: {out_path}")

# ---------------------------------------------------------------------------
# 3. Gambar 3.9: Sequence Diagram Skenario Pemindaian ML Kit
# ---------------------------------------------------------------------------
def generate_gambar_3_9():
    out_path = os.path.join(OUTPUT_DIR, "gambar_3_9_sequence_scan_mlkit.png")
    fig, ax = plt.subplots(figsize=(11, 7), dpi=300)
    ax.axis("off")
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 8)

    ax.text(5.5, 7.6, "Sequence Diagram: Skenario Pemindaian & Inferensi ML Kit On-Device",
            fontsize=12, fontweight="bold", ha="center", color="#0F172A")

    lifelines = [
        ("User (Pengguna)", 1.2),
        ("ScannerScreen", 3.4),
        ("CameraPlugin", 5.6),
        ("ML Kit OCR Service", 7.8),
        ("PreviewEditScreen", 10.0),
    ]

    for name, x in lifelines:
        rect = patches.FancyBboxPatch((x - 0.9, 6.7), 1.8, 0.55, boxstyle="round,pad=0.08", ec="#1E40AF", fc="#DBEAFE", lw=1.2)
        ax.add_patch(rect)
        ax.text(x, 6.97, name, fontsize=8.2, fontweight="bold", ha="center", color="#1E40AF")
        ax.plot([x, x], [0.6, 6.7], color="#94A3B8", linestyle="--", lw=1.2)

    messages = [
        (1.2, 3.4, 6.2, "1. Tekan Tombol Jepret Kamera", True),
        (3.4, 5.6, 5.6, "2. takePicture()", True),
        (5.6, 3.4, 5.1, "3. Mengembalikan XFile Citra Struk", False),
        (3.4, 7.8, 4.5, "4. processImage(InputImage)", True),
        (7.8, 7.8, 3.9, "5. C++ CRNN/CTC Native Execution (151 ms)", True),
        (7.8, 3.4, 3.3, "6. Mengembalikan RecognizedText & BoundingBoxes", False),
        (3.4, 10.0, 2.5, "7. Navigator.push(PreviewEditScreen(parsedData))", True),
        (10.0, 1.2, 1.7, "8. Menampilkan Form Koreksi Interaktif", True),
    ]

    for x1, x2, y, text, is_call in messages:
        if x1 == x2: # self call
            ax.annotate("", xy=(x1 + 0.1, y - 0.25), xytext=(x1 + 0.1, y + 0.05),
                        arrowprops=dict(arrowstyle="->", color="#D97706", lw=1.3, connectionstyle="arc3,rad=-0.5"))
            ax.text(x1 + 0.5, y - 0.1, text, fontsize=7.8, color="#92400E", fontweight="bold")
        else:
            color = "#1E40AF" if is_call else "#059669"
            ax.annotate("", xy=(x2, y), xytext=(x1, y),
                        arrowprops=dict(arrowstyle="->", color=color, lw=1.3, linestyle="solid" if is_call else "dashed"))
            mid_x = (x1 + x2) / 2
            ax.text(mid_x, y + 0.12, text, fontsize=7.8, ha="center", color=color, fontweight="bold")

    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"[OK] Gambar 3.9 digenerate: {out_path}")

# ---------------------------------------------------------------------------
# 4. Gambar 3.13: Class Diagram Struktur Perangkat Lunak Caran
# ---------------------------------------------------------------------------
def generate_gambar_3_13():
    out_path = os.path.join(OUTPUT_DIR, "gambar_3_13_class_diagram_caran.png")
    fig, ax = plt.subplots(figsize=(12, 7.5), dpi=300)
    ax.axis("off")
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)

    ax.text(6.0, 7.6, "Class Diagram: Struktur Perangkat Lunak Aplikasi Caran",
            fontsize=12, fontweight="bold", ha="center", color="#0F172A")

    classes = [
        ("DashboardScreen", 0.5, 4.5, 3.2, 2.4, "#EFF6FF", "#1E40AF",
         "- _totalSpending: double\n- _transactions: List<Tx>\n- _selectedRange: DateRange",
         "+ build(): Widget\n+ _loadData(): void\n+ _exportCsv(): void"),

        ("PreviewEditScreen", 4.3, 4.5, 3.4, 2.4, "#EFF6FF", "#1E40AF",
         "- _merchantCtrl: TextCtrl\n- _totalCtrl: TextCtrl\n- _items: List<TxItem>\n- _category: String",
         "+ _saveTransaction(): void\n+ _addNewItem(): void\n+ _calculateSubtotal(): void"),

        ("OfflineReceiptService", 8.3, 4.5, 3.4, 2.4, "#FEF3C7", "#92400E",
         "- _textRecognizer: TextRecognizer\n- _brandKeywords: Map",
         "+ parseReceipt(file): ParsedReceipt\n+ _clusterLines(blocks): List\n+ _extractDateTime(): DateTime"),

        ("TransactionItem", 1.5, 1.0, 3.6, 2.4, "#ECFDF5", "#065F46",
         "+ id: int?\n+ merchantName: String\n+ totalAmount: double\n+ transactionDate: String\n+ category: String\n+ items: List<Map>",
         "+ toMap(): Map<String, dynamic>\n+ fromMap(map): TransactionItem"),

        ("DatabaseHelper", 6.8, 1.0, 3.8, 2.4, "#F3E8FF", "#6B21A8",
         "- _database: Database?\n- static instance: DatabaseHelper",
         "+ insertTransaction(tx): int\n+ getAllTransactions(): List<tx>\n+ deleteTransaction(id): int\n+ getSpendingByCategory(): Map"),
    ]

    for title, x, y, w, h, bg, border, attrs, methods in classes:
        rect = patches.Rectangle((x, y), w, h, linewidth=1.4, edgecolor=border, facecolor=bg)
        ax.add_patch(rect)
        # Header
        h_rect = patches.Rectangle((x, y + h - 0.5), w, 0.5, linewidth=1.4, edgecolor=border, facecolor=border)
        ax.add_patch(h_rect)
        ax.text(x + w/2, y + h - 0.25, title, fontsize=8.5, fontweight="bold", ha="center", va="center", color="#FFFFFF")
        # Attributes
        ax.text(x + 0.15, y + h - 0.7, attrs, fontsize=7.2, va="top", color="#1E293B", family="monospace")
        # Divider
        ax.plot([x, x + w], [y + h/2 - 0.1, y + h/2 - 0.1], color=border, lw=1.0)
        # Methods
        ax.text(x + 0.15, y + h/2 - 0.25, methods, fontsize=7.2, va="top", color="#1E293B", family="monospace")

    # Connectors
    ax.annotate("", xy=(4.3, 5.7), xytext=(3.7, 5.7), arrowprops=dict(arrowstyle="->", color="#64748B", lw=1.2))
    ax.annotate("", xy=(8.3, 5.7), xytext=(7.7, 5.7), arrowprops=dict(arrowstyle="->", color="#64748B", lw=1.2))
    ax.annotate("", xy=(3.3, 3.4), xytext=(5.5, 4.5), arrowprops=dict(arrowstyle="->", color="#64748B", lw=1.2))
    ax.annotate("", xy=(7.5, 3.4), xytext=(6.5, 4.5), arrowprops=dict(arrowstyle="->", color="#64748B", lw=1.2))

    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"[OK] Gambar 3.13 digenerate: {out_path}")

# ---------------------------------------------------------------------------
# 5. Gambar 3.14: State Machine Diagram Siklus Transaksi
# ---------------------------------------------------------------------------
def generate_gambar_3_14():
    out_path = os.path.join(OUTPUT_DIR, "gambar_3_14_state_machine_transaksi.png")
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    ax.axis("off")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)

    ax.text(5.0, 5.6, "State Machine Diagram: Siklus Hidup Transaksi dan Parsing",
            fontsize=12, fontweight="bold", ha="center", color="#0F172A")

    # Start
    start = patches.Circle((0.8, 3.2), 0.2, fc="#0F172A", ec="#0F172A")
    ax.add_patch(start)

    states = [
        ("IDLE / UNCAPTURED", 1.8, 2.7, 2.0, 1.0, "#F1F5F9", "#475569"),
        ("PROCESSING OCR", 4.3, 2.7, 2.0, 1.0, "#FEF3C7", "#92400E"),
        ("PARSED (REVIEW)", 6.8, 2.7, 2.2, 1.0, "#DBEAFE", "#1E40AF"),
        ("PERSISTED (SQLITE)", 6.8, 0.7, 2.2, 1.0, "#D1FAE5", "#065F46"),
    ]

    for title, x, y, w, h, bg, border in states:
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1", ec=border, fc=bg, lw=1.5)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h/2, title, fontsize=8.5, fontweight="bold", ha="center", va="center", color=border)

    # Transitions
    ax.annotate("", xy=(1.8, 3.2), xytext=(1.0, 3.2), arrowprops=dict(arrowstyle="->", color="#475569", lw=1.2))

    ax.annotate("", xy=(4.3, 3.2), xytext=(3.8, 3.2), arrowprops=dict(arrowstyle="->", color="#475569", lw=1.2))
    ax.text(4.05, 3.4, "Jepret Kamera", fontsize=7.5, ha="center", color="#334155")

    ax.annotate("", xy=(6.8, 3.2), xytext=(6.3, 3.2), arrowprops=dict(arrowstyle="->", color="#475569", lw=1.2))
    ax.text(6.55, 3.4, "OCR & Cluster Selesai", fontsize=7.5, ha="center", color="#334155")

    ax.annotate("", xy=(7.9, 1.7), xytext=(7.9, 2.7), arrowprops=dict(arrowstyle="->", color="#059669", lw=1.5))
    ax.text(8.0, 2.2, "User Tekan Simpan", fontsize=7.5, va="center", color="#065F46", fontweight="bold")

    # Delete / End
    end_outer = patches.Circle((4.5, 1.2), 0.2, fc="none", ec="#0F172A", lw=1.5)
    end_inner = patches.Circle((4.5, 1.2), 0.12, fc="#0F172A", ec="#0F172A")
    ax.add_patch(end_outer)
    ax.add_patch(end_inner)
    ax.annotate("", xy=(4.7, 1.2), xytext=(6.8, 1.2), arrowprops=dict(arrowstyle="->", color="#DC2626", lw=1.2))
    ax.text(5.75, 1.4, "User Hapus Transaksi", fontsize=7.5, ha="center", color="#DC2626")

    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"[OK] Gambar 3.14 digenerate: {out_path}")

# ---------------------------------------------------------------------------
# 6. Gambar 3.18: Flowchart Modul Date-Time Parser dengan NPWP Exclusion
# ---------------------------------------------------------------------------
def generate_gambar_3_18():
    out_path = os.path.join(OUTPUT_DIR, "gambar_3_18_flowchart_datetime_npwp.png")
    fig, ax = plt.subplots(figsize=(10, 8.5), dpi=300)
    ax.axis("off")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)

    ax.text(5.0, 9.6, "Flowchart: Modul Automated Date-Time Parser dengan NPWP Exclusion",
            fontsize=11.5, fontweight="bold", ha="center", color="#0F172A")

    # Start
    start = patches.Circle((5.0, 8.9), 0.2, fc="#0F172A", ec="#0F172A")
    ax.add_patch(start)

    # Step 1: Input text lines
    r1 = patches.FancyBboxPatch((2.5, 7.8), 5.0, 0.65, boxstyle="round,pad=0.1", ec="#1E40AF", fc="#DBEAFE", lw=1.4)
    ax.add_patch(r1)
    ax.text(5.0, 8.12, "Iterasi Seluruh Baris Teks Hasil Klastering Spasial", fontsize=8.5, fontweight="bold", ha="center", color="#1E40AF")
    ax.annotate("", xy=(5.0, 8.45), xytext=(5.0, 8.7), arrowprops=dict(arrowstyle="->", color="#475569", lw=1.3))

    # Diamond 1: Apakah mengandung kata kunci / format NPWP 15 digit?
    d1 = patches.Polygon([[5.0, 7.3], [6.8, 6.6], [5.0, 5.9], [3.2, 6.6]], ec="#DC2626", fc="#FEE2E2", lw=1.5)
    ax.add_patch(d1)
    ax.text(5.0, 6.6, "Format NPWP\n15 Digit / Kata 'NPWP'?", fontsize=8.0, fontweight="bold", ha="center", va="center", color="#991B1B")
    ax.annotate("", xy=(5.0, 7.3), xytext=(5.0, 7.8), arrowprops=dict(arrowstyle="->", color="#475569", lw=1.3))

    # Branch Ya NPWP: Abaikan Baris
    r_drop = patches.FancyBboxPatch((7.5, 6.25), 2.2, 0.7, boxstyle="round,pad=0.1", ec="#DC2626", fc="#FEF2F2", lw=1.2)
    ax.add_patch(r_drop)
    ax.text(8.6, 6.6, "Abaikan Baris!\n(Derau Fiskal Kasir)", fontsize=7.5, fontweight="bold", ha="center", color="#991B1B")
    ax.annotate("", xy=(7.5, 6.6), xytext=(6.8, 6.6), arrowprops=dict(arrowstyle="->", color="#DC2626", lw=1.3))
    ax.text(7.15, 6.8, "[Ya]", fontsize=7.5, color="#DC2626", fontweight="bold")

    # Branch Tidak: Diamond 2: Cocok Pola Tanggal?
    ax.text(5.15, 5.65, "[Tidak]", fontsize=7.5, color="#059669", fontweight="bold")
    d2 = patches.Polygon([[5.0, 5.3], [6.8, 4.6], [5.0, 3.9], [3.2, 4.6]], ec="#D97706", fc="#FEF3C7", lw=1.5)
    ax.add_patch(d2)
    ax.text(5.0, 4.6, "Cocok Pola Tanggal?\n(dd/mm/yy atau Teks Bulan)", fontsize=8.0, fontweight="bold", ha="center", va="center", color="#92400E")
    ax.annotate("", xy=(5.0, 5.3), xytext=(5.0, 5.9), arrowprops=dict(arrowstyle="->", color="#475569", lw=1.3))

    # Branch Ya Date: Ekstraksi DateTime
    r_parse = patches.FancyBboxPatch((2.0, 2.5), 6.0, 0.7, boxstyle="round,pad=0.1", ec="#059669", fc="#D1FAE5", lw=1.5)
    ax.add_patch(r_parse)
    ax.text(5.0, 2.85, "Normalisasi Tanggal & Waktu (HH:mm) -> Simpan Objek DateTime", fontsize=8.5, fontweight="bold", ha="center", color="#065F46")
    ax.annotate("", xy=(5.0, 3.2), xytext=(5.0, 3.9), arrowprops=dict(arrowstyle="->", color="#059669", lw=1.5))
    ax.text(5.15, 3.55, "[Cocok]", fontsize=7.5, color="#059669", fontweight="bold")

    # Fallback jika tidak ditemukan
    r_fb = patches.FancyBboxPatch((0.2, 4.25), 2.5, 0.7, boxstyle="round,pad=0.1", ec="#64748B", fc="#F8FAFC", lw=1.2)
    ax.add_patch(r_fb)
    ax.text(1.45, 4.6, "Fallback:\nDateTime.now()", fontsize=7.5, fontweight="bold", ha="center", color="#475569")
    ax.annotate("", xy=(2.7, 4.6), xytext=(3.2, 4.6), arrowprops=dict(arrowstyle="<-", color="#64748B", lw=1.3))
    ax.text(2.8, 4.8, "[Nihil]", fontsize=7.5, color="#64748B", fontweight="bold")

    # End
    end_outer = patches.Circle((5.0, 1.2), 0.2, fc="none", ec="#0F172A", lw=1.5)
    end_inner = patches.Circle((5.0, 1.2), 0.12, fc="#0F172A", ec="#0F172A")
    ax.add_patch(end_outer)
    ax.add_patch(end_inner)
    ax.annotate("", xy=(5.0, 1.4), xytext=(5.0, 2.5), arrowprops=dict(arrowstyle="->", color="#475569", lw=1.3))

    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"[OK] Gambar 3.18 digenerate: {out_path}")

# ---------------------------------------------------------------------------
# 7. Wireframe Mockup UI: Dashboard, Scanner, PreviewEdit, Detail (3.21 - 3.24)
# ---------------------------------------------------------------------------
def generate_wireframes_3_21_to_3_24():
    screens = [
        ("gambar_3_21_wireframe_dashboard.png", "Gambar 3.21: Wireframe Dashboard Utama Caran", "dashboard"),
        ("gambar_3_22_wireframe_scanner.png", "Gambar 3.22: Wireframe Scanner Viewfinder Kamera", "scanner"),
        ("gambar_3_23_wireframe_preview_edit.png", "Gambar 3.23: Wireframe Pratinjau & Koreksi Interaktif", "preview"),
        ("gambar_3_24_wireframe_item_detail.png", "Gambar 3.24: Wireframe Detail Transaksi Tersimpan", "detail"),
    ]

    for filename, title, mode in screens:
        out_path = os.path.join(OUTPUT_DIR, filename)
        fig, ax = plt.subplots(figsize=(6, 10), dpi=300)
        ax.axis("off")
        ax.set_xlim(0, 6)
        ax.set_ylim(0, 10)

        # Phone Frame (Potret)
        frame = patches.FancyBboxPatch((0.4, 0.4), 5.2, 9.2, boxstyle="round,pad=0.2", ec="#1E293B", fc="#FFFFFF", lw=2.5)
        ax.add_patch(frame)

        # Notch / Camera
        notch = patches.Rectangle((2.4, 9.4), 1.2, 0.15, facecolor="#0F172A")
        ax.add_patch(notch)

        # Title
        ax.text(3.0, 9.8, title, fontsize=9.5, fontweight="bold", ha="center", color="#0F172A")

        if mode == "dashboard":
            # Header
            ax.text(0.8, 8.8, "Caran Expense", fontsize=12, fontweight="bold", color="#1E40AF")
            ax.text(0.8, 8.5, "Pencatatan Finansial Offline", fontsize=8, color="#64748B")

            # Balance Card
            card = patches.FancyBboxPatch((0.8, 6.9), 4.4, 1.4, boxstyle="round,pad=0.1", ec="#2563EB", fc="#1E40AF")
            ax.add_patch(card)
            ax.text(1.1, 7.9, "Total Pengeluaran Bulan Ini", fontsize=8.5, color="#DBEAFE")
            ax.text(1.1, 7.3, "Rp 2.450.000", fontsize=15, fontweight="bold", color="#FFFFFF")

            # Filter Chips
            chips = ["Semua", "Hari Ini", "Minggu Ini", "Bulan Ini"]
            for i, c in enumerate(chips):
                chip_r = patches.FancyBboxPatch((0.8 + i*1.1, 6.3), 1.0, 0.35, boxstyle="round,pad=0.05",
                                                ec="#3B82F6" if i==3 else "#CBD5E1", fc="#EFF6FF" if i==3 else "#FFFFFF")
                ax.add_patch(chip_r)
                ax.text(0.8 + i*1.1 + 0.5, 6.47, c, fontsize=6.8, ha="center", color="#1E40AF" if i==3 else "#475569", fontweight="bold" if i==3 else "normal")

            # Chart Placeholder
            chart_r = patches.Rectangle((0.8, 4.4), 4.4, 1.6, ec="#E2E8F0", fc="#F8FAFC")
            ax.add_patch(chart_r)
            ax.text(3.0, 5.2, "[Diagram Pengeluaran per Kategori]\nMakanan 45% | Kebutuhan 35% | Lain 20%", fontsize=7.5, ha="center", color="#64748B")

            # Transaction List
            ax.text(0.8, 3.9, "Riwayat Transaksi Terkini", fontsize=9, fontweight="bold", color="#1E293B")
            txs = [("INDOMARET", "14 Mei 2024", "Rp 72.000", "Belanja Bulanan"),
                   ("ALFAMART", "12 Mei 2024", "Rp 34.500", "Makanan & Minuman"),
                   ("SUPERINDO", "10 Mei 2024", "Rp 215.000", "Kebutuhan Rumah")]
            for idx, (m, d, a, c) in enumerate(txs):
                y_t = 3.3 - (idx * 0.8)
                tx_r = patches.FancyBboxPatch((0.8, y_t), 4.4, 0.65, boxstyle="round,pad=0.05", ec="#E2E8F0", fc="#FFFFFF")
                ax.add_patch(tx_r)
                ax.text(1.0, y_t + 0.4, m, fontsize=8, fontweight="bold", color="#0F172A")
                ax.text(1.0, y_t + 0.15, f"{d} • {c}", fontsize=7, color="#64748B")
                ax.text(4.9, y_t + 0.28, a, fontsize=8, fontweight="bold", ha="right", color="#1E40AF")

            # Floating Action Button
            fab = patches.Circle((4.7, 1.2), 0.38, fc="#2563EB", ec="#1D4ED8")
            ax.add_patch(fab)
            ax.text(4.7, 1.2, "+", fontsize=18, fontweight="bold", ha="center", va="center", color="#FFFFFF")

        elif mode == "scanner":
            # Viewfinder Area
            vf = patches.Rectangle((0.8, 2.5), 4.4, 5.5, facecolor="#0F172A")
            ax.add_patch(vf)

            # Corner guides
            ax.text(3.0, 5.5, "[ AREA STRUK BELANJA ]\nPosisikan struk tegak lurus\ndi dalam batas panduan",
                    fontsize=8.5, ha="center", color="#94A3B8")

            # Flash / Torch Button
            btn_t = patches.Circle((4.7, 8.3), 0.25, fc="#334155", ec="#64748B")
            ax.add_patch(btn_t)
            ax.text(4.7, 8.3, "⚡", fontsize=10, ha="center", va="center", color="#FDE047")

            # Shutter Button
            btn_s_out = patches.Circle((3.0, 1.4), 0.5, fc="none", ec="#3B82F6", lw=2.5)
            btn_s_in = patches.Circle((3.0, 1.4), 0.38, fc="#2563EB", ec="#1D4ED8")
            ax.add_patch(btn_s_out)
            ax.add_patch(btn_s_in)
            ax.text(3.0, 0.65, "Jepret Struk (Inferensi On-Device)", fontsize=7.5, ha="center", color="#64748B")

        elif mode == "preview":
            ax.text(0.8, 8.8, "Pratinjau Hasil Pindaian", fontsize=11, fontweight="bold", color="#1E40AF")

            # Store & Date inputs
            f1 = patches.FancyBboxPatch((0.8, 7.9), 4.4, 0.6, boxstyle="round,pad=0.05", ec="#CBD5E1", fc="#FFFFFF")
            ax.add_patch(f1)
            ax.text(1.0, 8.15, "Nama Toko: INDOMARET POINT", fontsize=8, fontweight="bold", color="#0F172A")

            f2 = patches.FancyBboxPatch((0.8, 7.1), 4.4, 0.6, boxstyle="round,pad=0.05", ec="#CBD5E1", fc="#FFFFFF")
            ax.add_patch(f2)
            ax.text(1.0, 7.35, "Tanggal: 14 Mei 2024 (14:32)", fontsize=8, color="#0F172A")

            # Mismatch Banner (Active Feature!)
            banner = patches.FancyBboxPatch((0.8, 6.3), 4.4, 0.65, boxstyle="round,pad=0.05", ec="#F59E0B", fc="#FEF3C7")
            ax.add_patch(banner)
            ax.text(1.0, 6.6, "✓ Verifikasi Subtotal: Cocok Sempurna (Rp 72.000)", fontsize=7.5, fontweight="bold", color="#B45309")

            # Editable Items
            ax.text(0.8, 5.9, "Daftar Item Belanjaan (Dapat Diedit)", fontsize=8.5, fontweight="bold", color="#334155")
            items = [("1. INDOMILK UHT 1L", "Rp 18.500"), ("2. ROTI TAWAR SARI", "Rp 15.000"),
                     ("3. MINYAK GORENG 2L", "Rp 34.000"), ("4. TEH BOTOL SOSRO", "Rp 4.500")]
            for idx, (it, pr) in enumerate(items):
                y_i = 5.2 - (idx * 0.6)
                it_r = patches.FancyBboxPatch((0.8, y_i), 4.4, 0.48, boxstyle="round,pad=0.03", ec="#E2E8F0", fc="#F8FAFC")
                ax.add_patch(it_r)
                ax.text(1.0, y_i + 0.18, it, fontsize=7.5, color="#1E293B")
                ax.text(4.9, y_i + 0.18, pr, fontsize=7.5, fontweight="bold", ha="right", color="#1E40AF")

            # Category Dropdown
            cat_b = patches.FancyBboxPatch((0.8, 2.3), 4.4, 0.55, boxstyle="round,pad=0.05", ec="#3B82F6", fc="#EFF6FF")
            ax.add_patch(cat_b)
            ax.text(1.0, 2.52, "Kategori: Kebutuhan Rumah Tangga ▼", fontsize=7.8, fontweight="bold", color="#1E40AF")

            # Save Button
            save_b = patches.FancyBboxPatch((0.8, 1.2), 4.4, 0.75, boxstyle="round,pad=0.08", ec="#1D4ED8", fc="#2563EB")
            ax.add_patch(save_b)
            ax.text(3.0, 1.55, "SIMPAN KE DATABASE SQLITE", fontsize=9, fontweight="bold", ha="center", color="#FFFFFF")

        elif mode == "detail":
            ax.text(0.8, 8.8, "Rincian Transaksi", fontsize=11, fontweight="bold", color="#1E40AF")

            # Receipt Card
            rc = patches.FancyBboxPatch((0.8, 3.2), 4.4, 5.3, boxstyle="round,pad=0.08", ec="#CBD5E1", fc="#FAFAFA")
            ax.add_patch(rc)
            ax.text(3.0, 8.1, "INDOMARET POINT", fontsize=11, fontweight="bold", ha="center", color="#0F172A")
            ax.text(3.0, 7.7, "Jl. Supratman No. 45, Bandung\n14 Mei 2024 • 14:32 WIB", fontsize=7.2, ha="center", color="#64748B")
            ax.plot([1.0, 5.0], [7.3, 7.3], color="#CBD5E1", linestyle="--", lw=1.0)

            items_d = [("INDOMILK UHT 1L", "1", "18.500"), ("ROTI TAWAR SARI", "1", "15.000"),
                       ("MINYAK GORENG 2L", "1", "34.000"), ("TEH BOTOL SOSRO", "1", "4.500")]
            for idx, (n, q, p) in enumerate(items_d):
                y_d = 6.8 - (idx * 0.5)
                ax.text(1.1, y_d, f"{q}x {n}", fontsize=7.2, color="#1E293B")
                ax.text(4.9, y_d, f"Rp {p}", fontsize=7.2, fontweight="bold", ha="right", color="#1E293B")

            ax.plot([1.0, 5.0], [4.6, 4.6], color="#CBD5E1", lw=1.2)
            ax.text(1.1, 4.2, "TOTAL TRANSAKSI", fontsize=8.5, fontweight="bold", color="#0F172A")
            ax.text(4.9, 4.2, "Rp 72.000", fontsize=10, fontweight="bold", ha="right", color="#1E40AF")

            # Action Buttons
            btn_del = patches.FancyBboxPatch((0.8, 1.5), 2.0, 0.65, boxstyle="round,pad=0.05", ec="#EF4444", fc="#FEE2E2")
            ax.add_patch(btn_del)
            ax.text(1.8, 1.8, "Hapus", fontsize=8, fontweight="bold", ha="center", color="#DC2626")

            btn_edit = patches.FancyBboxPatch((3.2, 1.5), 2.0, 0.65, boxstyle="round,pad=0.05", ec="#2563EB", fc="#DBEAFE")
            ax.add_patch(btn_edit)
            ax.text(4.2, 1.8, "Edit Transaksi", fontsize=8, fontweight="bold", ha="center", color="#1E40AF")

        plt.tight_layout()
        plt.savefig(out_path, dpi=300)
        plt.close()
        print(f"[OK] Wireframe {filename} digenerate: {out_path}")

def run_all():
    print("--- GENERATING BAB III UML & WIREFRAME DIAGRAMS ---")
    generate_gambar_3_3()
    generate_gambar_3_4()
    generate_gambar_3_9()
    generate_gambar_3_13()
    generate_gambar_3_14()
    generate_gambar_3_18()
    generate_wireframes_3_21_to_3_24()
    print("--- BAB III COMPLETE ---")

if __name__ == "__main__":
    run_all()
