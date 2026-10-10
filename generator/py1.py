import os
from onnxruntime.quantization import quantize_dynamic, QuantType

model_dir = r'C:\Users\USER\Desktop\kuliah\skripsi\flutter_application_1\assets\models'
enc_path = os.path.join(model_dir, 'donut_encoder.onnx')
enc_backup = os.path.join(model_dir, 'donut_encoder_f32.onnx')
dec_path = os.path.join(model_dir, 'donut_decoder.onnx')
dec_backup = os.path.join(model_dir, 'donut_decoder_f32.onnx')

print('=' * 60)
print('PROSES KUANTISASI INT8 MODEL DONUT ONNX')
print('=' * 60)

# 1. Kuantisasi Encoder
if os.path.exists(enc_path):
    print('1. Menguantisasi Encoder (295 MB -> INT8)...')
    os.rename(enc_path, enc_backup)
    quantize_dynamic(model_input=enc_backup, model_output=enc_path, weight_type=QuantType.QUInt8)
    os.remove(enc_backup)
    print(f'   -> Selesai! Ukuran Encoder INT8: {os.path.getsize(enc_path) / (1024*1024):.2f} MB')

# 2. Kuantisasi Decoder
if os.path.exists(dec_path):
    print('\n2. Menguantisasi Decoder (709 MB -> INT8)...')
    os.rename(dec_path, dec_backup)
    quantize_dynamic(model_input=dec_backup, model_output=dec_path, weight_type=QuantType.QUInt8)
    os.remove(dec_backup)
    print(f'   -> Selesai! Ukuran Decoder INT8: {os.path.getsize(dec_path) / (1024*1024):.2f} MB')

print('\n' + '=' * 60)
print('=== SUKSES 100%! MODEL SEKARANG SUPER RINGAN & CEPAT ===')
print('=' * 60)
