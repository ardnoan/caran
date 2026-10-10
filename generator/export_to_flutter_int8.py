import os
import sys
import json
import argparse
import torch
import onnx
from PIL import Image
import numpy as np
from transformers import DonutProcessor, VisionEncoderDecoderModel
from onnxruntime.quantization import quantize_dynamic, QuantType
import onnxruntime as ort

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOADED_DIR = os.path.join(BASE_DIR, "downloaded_donut_models")
DEFAULT_FLUTTER_ASSETS = os.path.join(BASE_DIR, "..", "flutter_application_1", "assets", "models")

MODEL_OPTIONS = {
    "cord": {
        "name": "naver-clova-ix/donut-base-finetuned-cord-v2",
        "path": os.path.join(DOWNLOADED_DIR, "donut_cord_v2"),
        "start_token_id": 57579, # <s_cord-v2>
        "prompt": "<s_cord-v2>",
        "desc": "Baseline resmi CORD (ribuan struk supermarket & resto Indonesia)"
    },
    "mychen": {
        "name": "mychen76/invoice-and-receipts_donut_v1",
        "path": os.path.join(DOWNLOADED_DIR, "donut_invoices_receipts_mychen"),
        "start_token_id": 57595, # <s_receipt>
        "prompt": None,
        "desc": "Model receipt & invoice ber-itemized (Indo & Internasional)"
    }
}

def export_model_to_flutter(choice="cord", target_dir=DEFAULT_FLUTTER_ASSETS):
    if choice not in MODEL_OPTIONS:
        print(f"Pilihan tidak valid: {choice}. Gunakan 'cord' atau 'mychen'.")
        return False
        
    cfg = MODEL_OPTIONS[choice]
    model_path = cfg["path"]
    
    if not os.path.exists(model_path):
        print(f"Model path tidak ditemukan: {model_path}")
        return False
        
    os.makedirs(target_dir, exist_ok=True)
    
    print("=" * 70)
    print(f"EKSPOR MODEL KE FLUTTER ONNX (INT8)")
    print(f"Pilihan Model: {cfg['name']}")
    print(f"Deskripsi    : {cfg['desc']}")
    print(f"Target Folder: {target_dir}")
    print("=" * 70)
    
    # 1. Load Model
    print("\n1. Memuat Processor & PyTorch Model...")
    processor = DonutProcessor.from_pretrained(model_path)
    model = VisionEncoderDecoderModel.from_pretrained(model_path, attn_implementation="eager")
    model.eval()
    
    img_h, img_w = 768, 576
    hidden_size = model.config.encoder.hidden_size
    seq_len = (img_h // 32) * (img_w // 32)
    start_token_id = cfg["start_token_id"]
    
    # 2. Export Encoder
    print("\n2. Mengekspor Encoder ke ONNX...")
    class EncoderWrapper(torch.nn.Module):
        def __init__(self, enc):
            super().__init__()
            self.enc = enc
        def forward(self, pixel_values):
            return self.enc(pixel_values).last_hidden_state

    wrapped_encoder = EncoderWrapper(model.encoder).eval()
    enc_f32 = os.path.join(target_dir, "donut_encoder_f32.onnx")
    enc_int8 = os.path.join(target_dir, "donut_encoder.onnx")
    dummy_pixel = torch.randn(1, 3, img_h, img_w, dtype=torch.float32)

    with torch.no_grad():
        torch.onnx.export(
            wrapped_encoder, dummy_pixel, enc_f32,
            export_params=True, opset_version=14, do_constant_folding=True,
            input_names=["pixel_values"], output_names=["last_hidden_state"],
            dynamic_axes={"pixel_values": {0: "batch_size"}, "last_hidden_state": {0: "batch_size", 1: "sequence_length"}},
            dynamo=False
        )

    if os.path.exists(enc_f32 + ".data"):
        m = onnx.load(enc_f32, load_external_data=True)
        onnx.save_model(m, enc_f32, save_as_external_data=False)
        os.remove(enc_f32 + ".data")

    print("   Menguantisasi Encoder ke INT8...")
    quantize_dynamic(model_input=enc_f32, model_output=enc_int8, weight_type=QuantType.QUInt8)
    if os.path.exists(enc_f32):
        os.remove(enc_f32)
    print(f"   -> Selesai! Ukuran Encoder INT8: {os.path.getsize(enc_int8)/(1024*1024):.2f} MB")

    # 3. Export Decoder
    print("\n3. Mengekspor Decoder ke ONNX...")
    class DecoderWrapper(torch.nn.Module):
        def __init__(self, dec):
            super().__init__()
            self.dec = dec
        def forward(self, input_ids, encoder_hidden_states):
            return self.dec(input_ids=input_ids, encoder_hidden_states=encoder_hidden_states).logits

    wrapped_decoder = DecoderWrapper(model.decoder).eval()
    dec_f32 = os.path.join(target_dir, "donut_decoder_f32.onnx")
    dec_int8 = os.path.join(target_dir, "donut_decoder.onnx")
    dummy_ids = torch.tensor([[start_token_id]], dtype=torch.long)
    dummy_hidden = torch.randn(1, seq_len, hidden_size, dtype=torch.float32)

    with torch.no_grad():
        torch.onnx.export(
            wrapped_decoder, (dummy_ids, dummy_hidden), dec_f32,
            export_params=True, opset_version=14, do_constant_folding=True,
            input_names=["input_ids", "encoder_hidden_states"], output_names=["logits"],
            dynamic_axes={"input_ids": {0: "batch_size", 1: "target_length"},
                          "encoder_hidden_states": {0: "batch_size", 1: "source_length"},
                          "logits": {0: "batch_size", 1: "target_length"}},
            dynamo=False
        )

    if os.path.exists(dec_f32 + ".data"):
        m = onnx.load(dec_f32, load_external_data=True)
        onnx.save_model(m, dec_f32, save_as_external_data=False)
        os.remove(dec_f32 + ".data")

    print("   Menguantisasi Decoder ke INT8...")
    quantize_dynamic(model_input=dec_f32, model_output=dec_int8, weight_type=QuantType.QUInt8)
    if os.path.exists(dec_f32):
        os.remove(dec_f32)
    print(f"   -> Selesai! Ukuran Decoder INT8: {os.path.getsize(dec_int8)/(1024*1024):.2f} MB")

    # 4. Save Vocabulary
    print("\n4. Menyimpan Vocabulary...")
    vocab_path = os.path.join(target_dir, "donut_vocab.json")
    raw_vocab = processor.tokenizer.get_vocab()
    inv_vocab = {int(v): k for k, v in raw_vocab.items()}
    with open(vocab_path, "w", encoding="utf-8") as f:
        json.dump({str(k): v for k, v in inv_vocab.items()}, f, ensure_ascii=False)
    print(f"   -> Selesai! Total Vocab: {len(inv_vocab)} token.")

    print("\n" + "=" * 70)
    print("HASIL: SEMUA FILE BERHASIL DI-EXPORT KE ASSETS FLUTTER!")
    print(f"1. Encoder INT8 : {enc_int8}")
    print(f"2. Decoder INT8 : {dec_int8}")
    print(f"3. Vocab JSON   : {vocab_path}")
    print("=" * 70)
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=["cord", "mychen"], default="cord", help="Pilih model untuk diekspor ke Flutter")
    args = parser.parse_args()
    export_model_to_flutter(args.model)
