import os
import json
import torch
import onnx
from transformers import DonutProcessor, VisionEncoderDecoderModel

MODEL_DIR = r"C:\Users\USER\Desktop\kuliah\skripsi\generator\donut_finetuned_indo_final"
OUTPUT_DIR = r"C:\Users\USER\Desktop\kuliah\skripsi\flutter_application_1\assets\models"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 60)
print("1. MEMUAT PROCESSOR & MODEL HASIL FINE-TUNING")
print("=" * 60)
processor = DonutProcessor.from_pretrained(MODEL_DIR)
model = VisionEncoderDecoderModel.from_pretrained(
    MODEL_DIR,
    attn_implementation="eager"
)
model.eval()

img_h = processor.image_processor.size.get("height", 768)
img_w = processor.image_processor.size.get("width", 576)
hidden_size = model.config.encoder.hidden_size
seq_len = (img_h // 32) * (img_w // 32)  # 24 * 18 = 432
start_token_id = model.config.decoder_start_token_id or processor.tokenizer.convert_tokens_to_ids(["<s_cord-v2>"])[0]

print(f"Resolusi input: {img_w}x{img_h}, seq_len: {seq_len}, start_id: {start_token_id}")

# -------------------------------------------------------------
# 2. EKSPOR ENCODER
# -------------------------------------------------------------
print("\n2. Mengekspor Encoder ke donut_encoder.onnx...")
class EncoderWrapper(torch.nn.Module):
    def __init__(self, encoder):
        super().__init__()
        self.encoder = encoder

    def forward(self, pixel_values):
        out = self.encoder(pixel_values)
        return out.last_hidden_state

wrapped_encoder = EncoderWrapper(model.encoder)
wrapped_encoder.eval()

encoder_path = os.path.join(OUTPUT_DIR, "donut_encoder.onnx")
dummy_pixel_values = torch.randn(1, 3, img_h, img_w, dtype=torch.float32)

with torch.no_grad():
    torch.onnx.export(
        wrapped_encoder,
        dummy_pixel_values,
        encoder_path,
        export_params=True,
        opset_version=14,
        do_constant_folding=True,
        input_names=["pixel_values"],
        output_names=["last_hidden_state"],
        dynamic_axes={
            "pixel_values": {0: "batch_size"},
            "last_hidden_state": {0: "batch_size", 1: "sequence_length"}
        },
        dynamo=False
    )

# Satukan bobot ke dalam single-file ONNX (agar tidak membutuhkan .data terpisah)
enc_data_path = encoder_path + ".data"
if os.path.exists(enc_data_path):
    print("Menyatukan external data ke dalam single file...")
    loaded_model = onnx.load(encoder_path, load_external_data=True)
    onnx.save_model(loaded_model, encoder_path, save_as_external_data=False)
    if os.path.exists(enc_data_path):
        os.remove(enc_data_path)
print(f"-> Selesai! Ukuran donut_encoder.onnx: {os.path.getsize(encoder_path) / (1024*1024):.2f} MB")

# -------------------------------------------------------------
# 3. EKSPOR DECODER
# -------------------------------------------------------------
print("\n3. Mengekspor Decoder ke donut_decoder.onnx...")
class DecoderWrapper(torch.nn.Module):
    def __init__(self, decoder):
        super().__init__()
        self.decoder = decoder

    def forward(self, input_ids, encoder_hidden_states):
        out = self.decoder(input_ids=input_ids, encoder_hidden_states=encoder_hidden_states)
        return out.logits

wrapped_decoder = DecoderWrapper(model.decoder)
wrapped_decoder.eval()

decoder_path = os.path.join(OUTPUT_DIR, "donut_decoder.onnx")
dummy_input_ids = torch.tensor([[start_token_id]], dtype=torch.long)
dummy_encoder_hidden_states = torch.randn(1, seq_len, hidden_size, dtype=torch.float32)

with torch.no_grad():
    torch.onnx.export(
        wrapped_decoder,
        (dummy_input_ids, dummy_encoder_hidden_states),
        decoder_path,
        export_params=True,
        opset_version=14,
        do_constant_folding=True,
        input_names=["input_ids", "encoder_hidden_states"],
        output_names=["logits"],
        dynamic_axes={
            "input_ids": {0: "batch_size", 1: "target_length"},
            "encoder_hidden_states": {0: "batch_size", 1: "source_length"},
            "logits": {0: "batch_size", 1: "target_length"}
        },
        dynamo=False
    )

dec_data_path = decoder_path + ".data"
if os.path.exists(dec_data_path):
    loaded_dec = onnx.load(decoder_path, load_external_data=True)
    onnx.save_model(loaded_dec, decoder_path, save_as_external_data=False)
    if os.path.exists(dec_data_path):
        os.remove(dec_data_path)
print(f"-> Selesai! Ukuran donut_decoder.onnx: {os.path.getsize(decoder_path) / (1024*1024):.2f} MB")

# -------------------------------------------------------------
# 4. EKSPOR VOCABULARY TOKENIZER
# -------------------------------------------------------------
print("\n4. Mengekspor Vocabulary...")
vocab_path = os.path.join(OUTPUT_DIR, "donut_vocab.json")
raw_vocab = processor.tokenizer.get_vocab()
# Format { "token_id": "token_str" } sesuai DonutOnnxService
inverted_vocab = {str(token_id): token_str for token_str, token_id in raw_vocab.items()}

with open(vocab_path, "w", encoding="utf-8") as f:
    json.dump(inverted_vocab, f, ensure_ascii=False)

print(f"-> Selesai! Total token: {len(inverted_vocab)}")
print("\n=== SEMUA FILE BERHASIL DI-EXPORT KE FLUTTER ASSETS! ===")