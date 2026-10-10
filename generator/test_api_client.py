import os
import sys
import json
import time
import urllib.request
import argparse

SERVER_URL = "http://127.0.0.1:8000"

SAMPLE_IMAGES = [
    {
        "id": "alfamart_gardenia",
        "name": "Struk Alfamart Gardenia (Fisik Bersih)",
        "path": r"C:\Users\USER\AppData\Local\hermes\images\clip_20260927_103946_2.png",
    },
    {
        "id": "alfamart_jalaprang_camera",
        "name": "Struk Alfamart Jalaprang (Foto Kamera HP dengan Jari)",
        "path": r"C:\Users\USER\AppData\Local\hermes\images\clip_20260927_111203_4.png",
    },
]

def scan_receipt(image_path, model_id="donut_receipts"):
    if not os.path.exists(image_path):
        return {"status": "error", "message": f"File gambar tidak ditemukan: {image_path}"}

    payload = {
        "image_path": image_path,
        "model_id": model_id,
    }

    req = urllib.request.Request(
        f"{SERVER_URL}/api/scan_receipt",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )

    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            data["client_latency_ms"] = int((time.time() - t0) * 1000)
            return data
    except Exception as e:
        return {"status": "error", "message": str(e), "client_latency_ms": int((time.time() - t0) * 1000)}

def print_result(img_label, res):
    print("\n" + "=" * 65)
    print(f"PENGUJIAN STRUK: {img_label}")
    print("=" * 65)

    if res.get("status") != "success":
        print(f"❌ GAGAL: {res.get('message') or res.get('error')}")
        return

    model_name = res.get("model_name", "-")
    infer_ms = res.get("inference_time_ms", 0)
    client_ms = res.get("client_latency_ms", 0)
    structured = res.get("structured", {})
    store = structured.get("store_name", "-")
    total = structured.get("total", "-")
    items = structured.get("items", [])

    print(f"Model Digunakan   : {model_name}")
    print(f"Waktu Inferensi   : {infer_ms} ms (Total Round-Trip: {client_ms} ms)")
    print(f"Nama Toko / Kasir : {store}")
    print(f"Total Belanja     : Rp {total}")
    print("-" * 65)
    print(f"{'NO':<4} | {'NAMA BARANG':<35} | {'QTY':<4} | {'HARGA (RP)':<12}")
    print("-" * 65)

    if items:
        for idx, it in enumerate(items, 1):
            nm = it.get("name", "-")[:35]
            q = it.get("quantity", "1")
            p = it.get("price", "-")
            print(f"{idx:<4} | {nm:<35} | {q:<4} | {p:<12}")
    else:
        print("  (Tidak ada rincian item atau struk non-itemized)")
    print("-" * 65)
    raw_snippet = res.get("raw_output", "")[:120].strip()
    print(f"Snippet XML Token : {raw_snippet}...")
    print("=" * 65)

def main():
    parser = argparse.ArgumentParser(description="Test Client REST API Donut Receipt Scanner")
    parser.add_argument("--image", type=str, help="Path ke file gambar struk")
    parser.add_argument("--model", type=str, default="donut_receipts", choices=["donut_receipts", "donut_cord", "donut_sroie"], help="Model Donut yang digunakan")
    parser.add_argument("--all", action="store_true", help="Uji semua sampel struk")
    args = parser.parse_args()

    # Cek kesehatan server
    try:
        with urllib.request.urlopen(f"{SERVER_URL}/health", timeout=3) as r:
            pass
    except Exception:
        print(f"❌ Server di {SERVER_URL} tidak merespons! Pastikan server python berjalan.")
        sys.exit(1)

    if args.all:
        print("\n🚀 MEMULAI PENGUJIAN OTOMATIS SELURUH SAMPEL STRUK...")
        for sample in SAMPLE_IMAGES:
            for m in ["donut_receipts", "donut_cord"]:
                res = scan_receipt(sample["path"], model_id=m)
                print_result(f"{sample['name']} [Model: {m}]", res)
    elif args.image:
        res = scan_receipt(args.image, model_id=args.model)
        print_result(f"File Kustom: {args.image}", res)
    else:
        # Default test 2 sample
        for sample in SAMPLE_IMAGES:
            res = scan_receipt(sample["path"], model_id=args.model)
            print_result(sample["name"], res)

if __name__ == "__main__":
    main()
