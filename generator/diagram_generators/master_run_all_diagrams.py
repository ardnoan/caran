"""
=============================================================================
MASTER RUNNER GENERATOR DIAGRAM & GRAFIK SKRIPSI CARAN (300 DPI)
Eksekutor terpusat untuk menghasilkan seluruh aset diagram ilmiah, arsitektur,
UML, flowchart, wireframe, dan grafik evaluasi empiris.

CARA PENGGUNAAN:
python generator/diagram_generators/master_run_all_diagrams.py
=============================================================================
"""

import os
import sys
import time

# Pastikan path modul terdaftar
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

import gen_bab1_bab2_diagrams
import gen_bab3_uml_diagrams
import gen_bab4_evaluation_diagrams
import generate_visual_proofs
import generate_additional_diagrams
import bab4_evaluasi_dan_eliminasi

OUTPUT_DIR = os.path.abspath(os.path.join(PARENT_DIR, "output_bab4"))

def main():
    start_time = time.time()
    print("=" * 75)
    print("MEMULAI GENERASI SELURUH DIAGRAM & GRAFIK NASKAH SKRIPSI (300 DPI)")
    print(f"Direktori Target Output: {OUTPUT_DIR}")
    print("=" * 75)

    print("\n[FASE 1/6] Menjalankan Generator Bab I & Bab II (Teoritis & Konseptual)...")
    gen_bab1_bab2_diagrams.run_all()

    print("\n[FASE 2/6] Menjalankan Generator Bab III (UML, State Machine, Flowchart, Wireframe)...")
    gen_bab3_uml_diagrams.run_all()

    print("\n[FASE 3/6] Menjalankan Generator Bab IV (Evaluasi, Termal, APK, dan SUS)...")
    gen_bab4_evaluation_diagrams.run_all()

    print("\n[FASE 4/6] Menjalankan Generator Alur Eliminasi Donut & Clustering Spasial...")
    generate_visual_proofs.generate_diagram_alur_pemilihan()
    generate_visual_proofs.generate_diagram_pipeline_spatial()
    generate_visual_proofs.generate_visual_spatial_clustering_sample()
    generate_visual_proofs.generate_grafik_distribusi_latensi()

    print("\n[FASE 5/6] Menjalankan Generator Arsitektur Tambahan (Use Case, 3-Tier, ERD)...")
    generate_additional_diagrams.generate_use_case_diagram()
    generate_additional_diagrams.generate_clean_architecture_diagram()
    generate_additional_diagrams.generate_erd_diagram()

    print("\n[FASE 6/6] Menjalankan Generator Grafik Metrik Empiris CORD-v2...")
    bab4_evaluasi_dan_eliminasi.generate_latency_chart()
    bab4_evaluasi_dan_eliminasi.generate_size_memory_chart()
    bab4_evaluasi_dan_eliminasi.generate_accuracy_radar_chart()
    bab4_evaluasi_dan_eliminasi.generate_markdown_and_csv_tables()

    # Rekapitulasi Berkas
    png_files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith(".png")]
    total_size_mb = sum(os.path.getsize(os.path.join(OUTPUT_DIR, f)) for f in png_files) / (1024 * 1024)
    elapsed = time.time() - start_time

    print("\n" + "=" * 75)
    print(f"SELESAI! Seluruh diagram berhasil dibuat dalam {elapsed:.2f} detik.")
    print(f"Total Citra Tergenerasi: {len(png_files)} berkas PNG (Resolusi Tinggi 300 DPI)")
    print(f"Total Ukuran Berkas: {total_size_mb:.2f} MB")
    print(f"Lokasi Output: {OUTPUT_DIR}")
    print("=" * 75)

if __name__ == "__main__":
    main()
