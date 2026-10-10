import os
import json
import base64
import io
import time
import socket
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from PIL import Image
import torch
from transformers import DonutProcessor, VisionEncoderDecoderModel

# Daftar Model yang Didukung (Multi-Model Hub untuk Skripsi)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOADED_DIR = os.path.join(BASE_DIR, "downloaded_donut_models")

SUPPORTED_MODELS = {
    "donut_receipts": {
        "name": "Donut Invoice & Receipts (mychen76 - Terbaik)",
        "path": os.path.join(DOWNLOADED_DIR, "donut_invoices_receipts_mychen"),
        "description": "Model terbaik untuk struk belanja fisik ber-itemized (Indo & Internasional)",
        "is_local": True,
        "start_token_id": 57595, # <s_receipt>
    },
    "donut_cord": {
        "name": "Donut Base CORD-v2 (Model Baseline)",
        "path": os.path.join(DOWNLOADED_DIR, "donut_cord_v2"),
        "description": "Model baseline default standar CORD (dataset ribuan struk toko fisik Indonesia)",
        "is_local": True,
        "start_prompt": "<s_cord-v2>",
    },
    "donut_sroie": {
        "name": "Donut SROIE (Receipt Benchmark)",
        "path": os.path.join(DOWNLOADED_DIR, "donut_sroie_unstructured"),
        "description": "Model benchmark ICDAR SROIE struk internasional (Company, Date, Address, Total)",
        "is_local": True,
        "start_token_id": 0, # <s>
    },
    "donut_indo": {
        "name": "Donut Fine-Tuned (QRIS & Transfer)",
        "path": os.path.join(BASE_DIR, "donut_finetuned_indo_final"),
        "description": "Model kustom hasil fine-tuning struk transfer bank & QRIS",
        "is_local": True,
        "start_prompt": "<s_cord-v2>",
    },
    "donut_docvqa": {
        "name": "Donut DocVQA (Question Answering)",
        "path": os.path.join(DOWNLOADED_DIR, "donut_docvqa"),
        "description": "Model Document Visual Question Answering",
        "is_local": True,
        "start_prompt": "<s_docvqa><s_question>what is the total amount?</s_question><s_answer>",
    },
}

device = "cuda" if torch.cuda.is_available() else "cpu"
print("=" * 60)
print(f"DEVICE INFERENSI AKTIF: {device.upper()}")
print("=" * 60)

# Cache penyimpanan model agar tidak perlu re-load berulang kali
model_cache = {}

def get_or_load_model(model_key="donut_receipts"):
    if model_key not in SUPPORTED_MODELS:
        model_key = "donut_receipts"

    if model_key in model_cache:
        return model_cache[model_key]

    cfg = SUPPORTED_MODELS[model_key]
    model_path = cfg["path"]
    print(f"\n[SERVER] Memuat model '{cfg['name']}' dari {model_path}...")
    t0 = time.time()

    processor = DonutProcessor.from_pretrained(model_path)
    model = VisionEncoderDecoderModel.from_pretrained(model_path)
    model.eval()
    model.to(device)

    print(f"[SERVER] Model '{model_key}' berhasil dimuat dalam {time.time() - t0:.2f} detik!")
    loaded = {"processor": processor, "model": model, "config": cfg}
    model_cache[model_key] = loaded
    return loaded

# Pra-muat model utama (Donut CORD Baseline) saat server pertama kali start
print("Memuat Model Utama (donut_cord)...")
get_or_load_model("donut_cord")

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def extract_structured_data(token_json):
    if isinstance(token_json, list):
        data = {}
        for item in token_json:
            if isinstance(item, dict):
                data.update(item)
    elif isinstance(token_json, dict):
        data = token_json.get("cord-v2", token_json.get("receipt", token_json))
        if isinstance(data, list):
            merged = {}
            for item in data:
                if isinstance(item, dict):
                    merged.update(item)
            data = merged
    else:
        return {"store_name": "Toko Retail", "total": "0", "items": []}

    store_name = data.get("store_name", "") or data.get("company", "") or data.get("store", "")
    total_str = ""
    items = []

    # CORD style menu
    menu = data.get("menu", [])
    if isinstance(menu, list):
        for m in menu:
            if isinstance(m, dict):
                nm = str(m.get("nm", "")).strip()
                price = str(m.get("price", "") or m.get("unitprice", "")).strip()
                cnt = str(m.get("cnt", "1")).strip()
                is_metadata = any(meta in nm.lower() for meta in ["tower", "bon b", "kasir", "npup", "npwp", "rt 0", "rw "])
                has_valid_price = any(c.isdigit() for c in price) and not price.startswith("0812")
                if nm and not is_metadata and has_valid_price:
                    items.append({"name": nm, "price": price, "quantity": cnt})
                elif not store_name and any(brand in nm.lower() for brand in ["alfa", "indomaret", "spbu"]):
                    store_name = nm

    # mychen style line_items
    line_items = data.get("line_items", [])
    if isinstance(line_items, list):
        for li in line_items:
            if isinstance(li, dict):
                nm = str(li.get("item_name", "")).strip()
                val = str(li.get("item_value", "")).strip()
                qty = str(li.get("item_quantity", "1")).strip()
                if nm:
                    items.append({"name": nm, "price": val, "quantity": qty})

    total_obj = data.get("total", "")
    if isinstance(total_obj, dict):
        total_str = total_obj.get("total_price", "") or total_obj.get("cashprice", "")
    elif isinstance(total_obj, str):
        total_str = total_obj
    if not total_str:
        total_str = str(data.get("total_price", "") or data.get("subtotal_price", "") or data.get("subtotal", ""))

    return {
        "store_name": store_name or "Toko Retail",
        "total": total_str,
        "items": items
    }

class MultiModelApiHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200)

    def do_GET(self):
        if self.path == "/health":
            self._set_headers(200)
            self.wfile.write(json.dumps({
                "status": "ok",
                "device": device,
                "loaded_models": list(model_cache.keys()),
            }).encode("utf-8"))
        elif self.path == "/models":
            self._set_headers(200)
            models_info = {
                k: {"name": v["name"], "description": v["description"], "is_loaded": k in model_cache}
                for k, v in SUPPORTED_MODELS.items()
            }
            self.wfile.write(json.dumps(models_info).encode("utf-8"))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Endpoint tidak ditemukan"}).encode("utf-8"))

    def do_POST(self):
        if self.path in ("/predict_receipt", "/api/scan_receipt", "/predict"):
            transfer_encoding = self.headers.get("Transfer-Encoding", "").lower()
            content_length = self.headers.get("Content-Length")

            try:
                if "chunked" in transfer_encoding:
                    body = bytearray()
                    while True:
                        line = self.rfile.readline().strip()
                        if not line:
                            break
                        chunk_len = int(line, 16)
                        if chunk_len == 0:
                            self.rfile.readline()
                            break
                        body.extend(self.rfile.read(chunk_len))
                        self.rfile.readline()
                    body = bytes(body)
                elif content_length is not None and int(content_length) > 0:
                    body = self.rfile.read(int(content_length))
                else:
                    body = self.rfile.read()

                if not body:
                    raise ValueError("Body request kosong (0 byte diterima dari client)")

                data = json.loads(body.decode("utf-8"))
                image_b64 = data.get("image_base64", "")
                image_path = data.get("image_path", "")
                model_id = data.get("model_id", "donut_receipts")

                if image_path and os.path.exists(image_path):
                    image = Image.open(image_path).convert("RGB")
                elif image_b64:
                    image_bytes = base64.b64decode(image_b64)
                    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
                else:
                    self._set_headers(400)
                    self.wfile.write(json.dumps({"error": "image_base64 atau image_path diperlukan"}).encode("utf-8"))
                    return

                # Dapatkan model yang dipilih
                loaded = get_or_load_model(model_id)
                processor = loaded["processor"]
                model = loaded["model"]
                cfg = loaded["config"]

                # Inference
                start_infer = time.time()
                pixel_values = processor(image, return_tensors="pt").pixel_values.to(device)

                # Tentukan start token yang sesuai per model
                tok = processor.tokenizer
                if cfg.get("start_prompt"):
                    decoder_input_ids = tok(cfg["start_prompt"], add_special_tokens=False, return_tensors="pt").input_ids.to(device)
                elif cfg.get("start_token_id") is not None:
                    decoder_input_ids = torch.tensor([[cfg["start_token_id"]]], device=device)
                elif "<s_cord-v2>" in tok.get_vocab():
                    start_token_id = tok.convert_tokens_to_ids(["<s_cord-v2>"])[0]
                    decoder_input_ids = torch.tensor([[start_token_id]], device=device)
                else:
                    start_token_id = tok.bos_token_id if tok.bos_token_id is not None else 0
                    decoder_input_ids = torch.tensor([[start_token_id]], device=device)

                with torch.no_grad():
                    outputs = model.generate(
                        pixel_values,
                        decoder_input_ids=decoder_input_ids,
                        max_length=512,  # Diperpanjang agar seluruh item struk + subtotal + total terbaca lengkap!
                        pad_token_id=processor.tokenizer.pad_token_id,
                        eos_token_id=processor.tokenizer.eos_token_id,
                        use_cache=True,
                        num_beams=1,
                    )

                seq = processor.batch_decode(outputs)[0]
                seq = seq.replace(processor.tokenizer.eos_token, "").replace(processor.tokenizer.pad_token, "")
                seq = seq.strip()
                if seq.startswith(("<s_cord-v2>", "<s_struk_qris>", "<s_struk_transfer>", "<s_receipt>", "<s>", "<s_company>")):
                    raw_output = seq
                else:
                    raw_output = f"<s_cord-v2>{seq}</s_cord-v2>"

                infer_duration_ms = int((time.time() - start_infer) * 1000)
                print(f"[API] [{cfg['name']}] Inferensi selesai dalam {infer_duration_ms} ms")
                print(f"[API] Hasil Mentah:\n{raw_output}\n")

                # Parse ke JSON terstruktur
                try:
                    token_json = processor.token2json(raw_output)
                    structured = extract_structured_data(token_json)
                except Exception as ex:
                    print(f"[API] token2json note: {ex}")
                    structured = {"store_name": "Toko Retail", "total": "0", "items": []}

                response_payload = {
                    "status": "success",
                    "model_id": model_id,
                    "model_name": cfg["name"],
                    "inference_time_ms": infer_duration_ms,
                    "raw_output": raw_output,
                    "structured": structured,
                }

                self._set_headers(200)
                self.wfile.write(json.dumps(response_payload).encode("utf-8"))

            except Exception as e:
                print(f"[API ERROR] {e}")
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Endpoint tidak ditemukan"}).encode("utf-8"))

def run_server(port=8000):
    local_ip = get_local_ip()
    ThreadingHTTPServer.allow_reuse_address = True
    server_address = ("0.0.0.0", port)
    httpd = ThreadingHTTPServer(server_address, MultiModelApiHandler)
    print("\n" + "=" * 60)
    print("SERVER MULTI-MODEL API DONUT BERJALAN!")
    print(f"Alamat Lokal Laptop  : http://localhost:{port}")
    print(f"Alamat untuk HP WiFi : http://{local_ip}:{port}")
    print("Daftar Model:")
    for k, v in SUPPORTED_MODELS.items():
        print(f"  • [{k}] : {v['name']}")
    print("=" * 60 + "\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer dimatikan.")
        httpd.server_close()

if __name__ == "__main__":
    run_server(8000)
