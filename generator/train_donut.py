import os
import json
import torch
from datasets import load_dataset
from transformers import (
    DonutProcessor, 
    VisionEncoderDecoderModel, 
    Seq2SeqTrainingArguments, 
    Seq2SeqTrainer
)

# 1. LOAD DATASET
print("Memuat dataset...")
dataset = load_dataset("imagefolder", data_dir="./synthetic_dataset")

# Bagi dataset: 80% train, 20% validation
dataset = dataset["train"].train_test_split(test_size=0.2, seed=42)
train_dataset = dataset["train"]
val_dataset = dataset["test"]

# 2. LOAD PROCESSOR & MODEL
print("Mengunduh/Memuat model Donut dari Hugging Face cache...")
model_id = "naver-clova-ix/donut-base-finetuned-cord-v2"
processor = DonutProcessor.from_pretrained(model_id)
model = VisionEncoderDecoderModel.from_pretrained(model_id)

# Optimasi resolusi agar VRAM 8GB RTX 5060 sangat aman & hemat
processor.image_processor.size = {
    "height": 768,
    "width": 576
}

# 3. TAMBAHKAN SPECIAL TOKENS
new_tokens = [
    "<s_struk_qris>", "</s_struk_qris>",
    "<s_struk_transfer>", "</s_struk_transfer>",
    "<s_penyedia>", "</s_penyedia>",
    "<s_jenis_transaksi>", "</s_jenis_transaksi>",
    "<s_merchant>", "</s_merchant>",
    "<s_nominal>", "</s_nominal>",
    "<s_waktu>", "</s_waktu>",
    "<s_rrn>", "</s_rrn>",
    "<s_no_referensi>", "</s_no_referensi>",
    "<s_penerima>", "</s_penerima>",
    "<s_no_tujuan>", "</s_no_tujuan>",
    "<s_transaction_id>", "</s_transaction_id>"
]

processor.tokenizer.add_special_tokens({"additional_special_tokens": new_tokens})
model.decoder.resize_token_embeddings(len(processor.tokenizer))

# Fungsi pembantu mengubah dict JSON menjadi urutan token XML Donut
def json2token(obj):
    if isinstance(obj, dict):
        text = ""
        for k, v in obj.items():
            text += f"<s_{k}>" + json2token(v) + f"</s_{k}>"
        return text
    elif isinstance(obj, list):
        return "".join([json2token(item) for item in obj])
    else:
        return str(obj)

# 4. FUNGSI PRE-PROCESSING DATA
def preprocess_function(examples):
    pixel_values = []
    labels = []
    
    for img, gt_string in zip(examples["image"], examples["ground_truth"]):
        # A. Proses Gambar
        pixel_value = processor(img.convert("RGB"), return_tensors="pt").pixel_values
        pixel_values.append(pixel_value.squeeze(0))
        
        # B. Proses Teks Ground Truth
        task_prompt = "<s_cord-v2>"
        gt_json = json.loads(gt_string)
        
        # Ubah dict JSON -> urutan tag XML token Donut
        target_token_str = json2token(gt_json["gt_parse"])
        target_sequence = task_prompt + target_token_str + processor.tokenizer.eos_token
        
        # Tokenisasi target
        input_ids = processor.tokenizer(
            target_sequence,
            add_special_tokens=False,
            max_length=512,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )["input_ids"].squeeze(0)
        
        # Ganti pad_token_id dengan -100 agar loss mengabaikan padding
        input_ids[input_ids == processor.tokenizer.pad_token_id] = -100
        labels.append(input_ids)
        
    return {"pixel_values": pixel_values, "labels": labels}

print("Memproses gambar dan teks ke dalam tensor...")
train_dataset = train_dataset.map(preprocess_function, batched=True, remove_columns=train_dataset.column_names)
val_dataset = val_dataset.map(preprocess_function, batched=True, remove_columns=val_dataset.column_names)

# 5. KONFIGURASI MODEL
model.config.pad_token_id = processor.tokenizer.pad_token_id
model.config.decoder_start_token_id = processor.tokenizer.convert_tokens_to_ids(["<s_cord-v2>"])[0]

# 6. PENGATURAN TRAINING
training_args = Seq2SeqTrainingArguments(
    output_dir="./donut_finetuned_indo",
    eval_strategy="steps",
    eval_steps=50,
    save_steps=100,
    logging_steps=20,
    max_steps=300,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=4,
    learning_rate=2e-5,
    weight_decay=0.01,
    fp16=True,
    save_total_limit=2,
    dataloader_num_workers=0,  # Nilai 0 lebih stabil untuk environment Windows
)

# 7. MULAI TRAINING
trainer = Seq2SeqTrainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
)

print("Memulai proses fine-tuning...")
trainer.train()

# 8. SIMPAN MODEL HASIL TRAINING
print("Menyimpan model ke folder ./donut_finetuned_indo_final")
model.save_pretrained("./donut_finetuned_indo_final")
processor.save_pretrained("./donut_finetuned_indo_final")
print("Selesai 100%! Model siap digunakan.")