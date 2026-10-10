import os
import time
import json
import torch
from PIL import Image
from transformers import DonutProcessor, VisionEncoderDecoderModel

# Setup device
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Menggunakan Device: {device.upper()}")

BASE_MODELS_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOADED_DIR = os.path.join(BASE_MODELS_DIR, "downloaded_donut_models")

MODELS = {
    "mychen_receipts": {
        "name": "mychen76/invoice-and-receipts_donut_v1",
        "path": os.path.join(DOWNLOADED_DIR, "donut_invoices_receipts_mychen"),
        "task_prompt": None,
        "start_token_id": 57595, # <s_receipt>
        "description": "Model terbaik untuk struk & invoice (Ekstraksi Itemized, Toko, Tanggal, Total)"
    },
    "cord_v2": {
        "name": "naver-clova-ix/donut-base-finetuned-cord-v2",
        "path": os.path.join(DOWNLOADED_DIR, "donut_cord_v2"),
        "task_prompt": "<s_cord-v2>",
        "start_token_id": None,
        "description": "Model baseline resmi CORD (dataset ribuan struk toko fisik Indonesia)"
    },
    "sroie_unstructured": {
        "name": "unstructuredio/donut-base-sroie",
        "path": os.path.join(DOWNLOADED_DIR, "donut_sroie_unstructured"),
        "task_prompt": None,
        "start_token_id": 0, # <s>
        "description": "Model benchmark struk internasional (Company, Date, Address, Total)"
    },
    "docvqa": {
        "name": "naver-clova-ix/donut-base-finetuned-docvqa",
        "path": os.path.join(DOWNLOADED_DIR, "donut_docvqa"),
        "task_prompt": "<s_docvqa><s_question>what is the total amount?</s_question><s_answer>",
        "start_token_id": None,
        "description": "Model Document Visual Question Answering"
    },
    "tobe_invoices": {
        "name": "to-be/donut-base-finetuned-invoices",
        "path": os.path.join(DOWNLOADED_DIR, "donut_invoices_tobe"),
        "task_prompt": None,
        "start_token_id": 0,
        "description": "Model ekstraksi faktur/invoice komersial"
    },
    "user_finetuned": {
        "name": "donut_finetuned_indo_final (Lokal Anda)",
        "path": os.path.join(BASE_MODELS_DIR, "donut_finetuned_indo_final"),
        "task_prompt": "<s_cord-v2>",
        "start_token_id": None,
        "description": "Model hasil fine-tuning lokal 300 steps (QRIS/Transfer)"
    }
}

def run_benchmark(image_paths):
    results = {}
    
    for model_key, mcfg in MODELS.items():
        if not os.path.exists(mcfg["path"]):
            print(f"[SKIP] Model {model_key} tidak ditemukan di {mcfg['path']}")
            continue
            
        print("\n" + "=" * 75)
        print(f"MEMUAT MODEL: {mcfg['name']}")
        print(f"Deskripsi   : {mcfg['description']}")
        print("=" * 75)
        
        try:
            t0_load = time.time()
            processor = DonutProcessor.from_pretrained(mcfg["path"])
            model = VisionEncoderDecoderModel.from_pretrained(mcfg["path"]).to(device)
            model.eval()
            print(f"Model berhasil dimuat dalam {time.time() - t0_load:.2f} detik.")
            
            results[model_key] = {
                "name": mcfg["name"],
                "inferences": []
            }
            
            for label, img_path in image_paths:
                if not os.path.exists(img_path):
                    continue
                    
                image = Image.open(img_path).convert("RGB")
                pixel_values = processor(image, return_tensors="pt").pixel_values.to(device)
                
                if mcfg["task_prompt"]:
                    dec_ids = processor.tokenizer(
                        mcfg["task_prompt"], 
                        add_special_tokens=False, 
                        return_tensors="pt"
                    ).input_ids.to(device)
                else:
                    dec_ids = torch.tensor([[mcfg["start_token_id"]]], device=device)
                    
                t0_inf = time.time()
                with torch.no_grad():
                    output_ids = model.generate(
                        pixel_values,
                        decoder_input_ids=dec_ids,
                        max_length=256,
                        pad_token_id=processor.tokenizer.pad_token_id,
                        eos_token_id=processor.tokenizer.eos_token_id,
                        use_cache=True,
                        num_beams=1,
                    )
                latency_ms = int((time.time() - t0_inf) * 1000)
                
                raw_text = processor.batch_decode(output_ids)[0]
                clean_text = raw_text.replace(processor.tokenizer.eos_token, "").replace(processor.tokenizer.pad_token, "").strip()
                token_count = output_ids.shape[1]
                
                print(f"\n--- [Gambar: {label}] | Latensi: {latency_ms} ms | Tokens: {token_count} ---")
                print(clean_text)
                
                results[model_key]["inferences"].append({
                    "image": label,
                    "latency_ms": latency_ms,
                    "tokens": token_count,
                    "output": clean_text
                })
                
        except Exception as e:
            print(f"[ERROR] Gagal menjalankan model {model_key}: {e}")
            
    return results

if __name__ == "__main__":
    test_images = [
        ("Struk Alfamart Gardenia (User)", r"C:\Users\USER\AppData\Local\hermes\images\clip_20260927_103314_1.png"),
        ("Struk Alfamart Jalaprang (Proyek)", r"C:\Users\USER\Desktop\kuliah\skripsi\flutter_application_1\test_receipt_crop.jpg"),
        ("Struk Internasional SROIE 1", r"C:\Users\USER\Desktop\kuliah\skripsi\generator\test_images\sroie_sample.jpg"),
        ("Struk Internasional SROIE 2", r"C:\Users\USER\Desktop\kuliah\skripsi\generator\test_images\sroie_001.jpg"),
    ]
    
    print("Memulai Uji Komparasi Model Donut...")
    res = run_benchmark(test_images)
    
    # Simpan hasil komparasi ke JSON
    out_file = os.path.join(BASE_MODELS_DIR, "hasil_benchmark_donut.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2, ensure_ascii=False)
    print(f"\n[SELESAI] Hasil lengkap telah disimpan ke: {out_file}")
