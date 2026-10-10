"""
inspect_model_config.py

Cetak semua angka/konfigurasi yang saya butuhkan buat menyesuaikan
lib/services/donut_onnx_service.dart dengan model hasil fine-tuning-mu.
Jalankan sekali, lalu tempel SELURUH outputnya ke chat.

Cara pakai:
    pip install onnx transformers
    python inspect_model_config.py
"""

import onnx
from transformers import DonutProcessor

# --- SESUAIKAN 2 PATH INI KALAU BEDA DARI YANG DI SCRIPT EXPORT-MU ---
MODEL_DIR = r"C:\Users\USER\Desktop\kuliah\skripsi\generator\donut_finetuned_indo_final"
ENCODER_ONNX_PATH = r"C:\Users\USER\Desktop\kuliah\skripsi\flutter_application_1\assets\models\donut_encoder.onnx"

print("=" * 60)
print("INFO DARI PROCESSOR (buat isi decoderStartTokenId, eosTokenId, dll)")
print("=" * 60)
processor = DonutProcessor.from_pretrained(MODEL_DIR)
tok = processor.tokenizer

decoder_start_id = tok.convert_tokens_to_ids(["<s_cord-v2>"])[0]
print("decoder_start_token_id (<s_cord-v2>):", decoder_start_id)
print("eos_token_id:", tok.eos_token_id)
print("pad_token_id:", tok.pad_token_id)
print("vocab size (len tokenizer):", len(tok))
print("image_mean:", processor.image_processor.image_mean)
print("image_std:", processor.image_processor.image_std)
print("image size (h, w):", processor.image_processor.size)

print()
print("=" * 60)
print("INFO DARI FILE donut_encoder.onnx (buat cek nama tensor)")
print("=" * 60)
m = onnx.load(ENCODER_ONNX_PATH, load_external_data=False)
print("encoder inputs :", [i.name for i in m.graph.input])
print("encoder outputs:", [o.name for o in m.graph.output])