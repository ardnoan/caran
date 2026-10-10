import os
import json
import random
from datetime import datetime, timedelta
from faker import Faker
from playwright.sync_api import sync_playwright

fake = Faker("id_ID")

OUTPUT_DIR = "./synthetic_dataset"
IMAGES_DIR = os.path.join(OUTPUT_DIR, "train")
METADATA_FILE = os.path.join(IMAGES_DIR, "metadata.jsonl")

os.makedirs(IMAGES_DIR, exist_ok=True)

# ----------------- 1. TEMPLATE myBCA (QRIS) -----------------
HTML_MYBCA = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
  body { background: #f0f2f5; display: flex; justify-content: center; padding: 15px; }
  .ticket {
    width: 370px;
    background: #ffffff;
    background-image: radial-gradient(#d3e2f8 0.75px, transparent 0.75px), url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='100' height='70'><text x='10' y='40' fill='%23005baa' opacity='0.08' font-weight='900' font-size='16' transform='rotate(-20 20,40)'>BCA</text></svg>");
    padding: 24px 20px;
    border-radius: 12px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05);
  }
  .bca-logo { text-align: center; margin-bottom: 12px; color: #005baa; font-weight: 900; font-size: 22px; letter-spacing: 1px; }
  .check-circle {
    width: 60px; height: 60px; background: #00a499; border-radius: 50%;
    margin: 0 auto 12px auto; display: flex; align-items: center; justify-content: center;
    border: 3px solid #e0f2f1;
  }
  .check-icon { color: white; font-size: 32px; font-weight: bold; }
  .status-title { text-align: center; font-size: 15px; font-weight: 700; color: #0a2540; margin-bottom: 4px; }
  .timestamp { text-align: center; font-size: 11px; color: #697386; margin-bottom: 8px; }
  .amount { text-align: center; font-size: 22px; font-weight: 800; color: #003366; margin-bottom: 24px; }
  .row { display: flex; justify-content: space-between; margin-bottom: 10px; font-size: 12px; }
  .label { color: #525f7f; flex: 1; }
  .val { color: #0a2540; font-weight: 600; text-align: right; flex: 1.3; }
  .total-row { border-top: 1px solid #e6ebf1; padding-top: 12px; margin-top: 12px; font-weight: 700; }
</style>
</head>
<body>
  <div class="ticket">
    <div class="bca-logo">BCA</div>
    <div class="check-circle"><span class="check-icon">&#10003;</span></div>
    <div class="status-title">Pembayaran QRIS Berhasil</div>
    <div class="timestamp">{{WAKTU}}</div>
    <div class="amount">IDR {{NOMINAL}}.00</div>

    <div class="row"><span class="label">Pembayaran ke</span><span class="val">{{MERCHANT}}</span></div>
    <div class="row"><span class="label">Pengakuisisi</span><span class="val">{{PENGAKUISISI}}</span></div>
    <div class="row"><span class="label">RRN</span><span class="val">{{RRN}}</span></div>
    <div class="row"><span class="label">Jenis Transaksi</span><span class="val">Pembayaran QRIS</span></div>
    <div class="row"><span class="label">Lokasi Merchant</span><span class="val">{{LOKASI}}</span></div>
    <div class="row"><span class="label">Merchant PAN</span><span class="val">{{MERCHANT_PAN}}</span></div>
    <div class="row"><span class="label">Terminal ID</span><span class="val">A01</span></div>
    <div class="row"><span class="label">Sumber Dana</span><span class="val">TAHAPAN<br>{{REK_MASKED}}</span></div>
    <div class="row total-row"><span class="label">Total Bayar</span><span class="val">IDR {{NOMINAL}}.00</span></div>
    <div class="row"><span class="label">No. Referensi</span><span class="val" style="font-size: 10px;">{{REF_ID}}</span></div>
  </div>
</body>
</html>
"""

# ----------------- 2. TEMPLATE DANA (SEND MONEY) -----------------
HTML_DANA = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
  body { background: #f0f2f5; display: flex; justify-content: center; padding: 15px; }
  .dana-container { width: 370px; background: transparent; }
  .dana-header {
    background: #108ee9; color: white; padding: 22px 18px 25px 18px;
    border-top-left-radius: 14px; border-top-right-radius: 14px; text-align: center;
  }
  .dana-logo { font-size: 26px; font-weight: 900; letter-spacing: 1px; margin-bottom: 12px; }
  .header-sub { display: flex; justify-content: space-between; font-size: 11px; opacity: 0.9; }
  .dana-body {
    background: #ffffff;
    background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='110' height='70'><text x='15' y='45' fill='%23108ee9' opacity='0.08' font-weight='900' font-size='16' transform='rotate(-20 20,40)'>DANA</text></svg>");
    padding: 18px 20px;
  }
  .status-tag { display: flex; align-items: center; color: #00a499; font-size: 12px; font-weight: 700; margin-bottom: 6px; }
  .send-info { font-size: 13px; font-weight: 700; color: #1f2937; margin-bottom: 16px; }
  .total-box {
    background: #e8f3fc; border-radius: 8px; padding: 12px 16px;
    display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;
  }
  .total-box .lbl { font-size: 14px; font-weight: 700; color: #111827; }
  .total-box .amt { font-size: 17px; font-weight: 800; color: #111827; }
  .section-title { font-size: 13px; font-weight: 700; color: #111827; margin: 14px 0 8px 0; }
  .row { display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 12px; }
  .label { color: #6b7280; }
  .val { color: #1f2937; font-weight: 600; text-align: right; }
  .zigzag-bottom {
    background: #ffffff; height: 14px; position: relative;
    border-bottom-left-radius: 4px; border-bottom-right-radius: 4px;
    background: radial-gradient(circle, transparent, transparent 50%, #ffffff 50%, #ffffff 100% );
    background-size: 14px 14px;
  }
  .footer-safe { text-align: center; font-size: 11px; color: #6b7280; margin-top: 14px; font-weight: 600; }
</style>
</head>
<body>
  <div class="dana-container">
    <div class="dana-header">
      <div class="dana-logo">DANA</div>
      <div class="header-sub">
        <span>{{WAKTU}}</span>
        <span>DANA ID</span>
      </div>
    </div>
    <div class="dana-body">
      <div class="status-tag">&#10004; Transaction success!</div>
      <div class="send-info">Send Money Rp{{NOMINAL}} to {{PENERIMA}} - {{NO_HP}}</div>

      <div class="total-box">
        <span class="lbl">Total Payment</span>
        <span class="amt">Rp{{NOMINAL}}</span>
      </div>

      <div class="row"><span class="label">Payment Method</span><span class="val">DANA Balance (SmartPay)</span></div>

      <div class="section-title">Receiver Detail</div>
      <div class="row"><span class="label">Name</span><span class="val">{{PENERIMA_MASKED}}</span></div>
      <div class="row"><span class="label">DANA Account</span><span class="val">{{NO_HP}}</span></div>

      <div class="section-title">Transaction Detail</div>
      <div class="row"><span class="label">Transaction ID</span><span class="val" style="font-size: 10px;">{{TRX_ID}}</span></div>
    </div>
    <div class="footer-safe">Secured by <b>DANA</b> PROTECTION</div>
  </div>
</body>
</html>
"""

MERCHANTS = ["mie bakso restorja", "Kopi Kenangan", "Indomaret Point", "Mixue Sukajadi", "Roti O Stasiun", "Warung Nasi Padang"]
BANKS = ["BANK MANDIRI", "BANK BCA", "BANK BRI", "BANK BNI", "BANK PERMATA"]
CITIES = ["Bandung (Kota, 40122, ID)", "Jakarta Selatan (12190, ID)", "Surabaya (Kota, 60271, ID)", "Semarang (50241, ID)"]

def format_idr(val: int) -> str:
    return f"{val:,}".replace(",", ".")

def generate_mybca_data():
    nominal = random.randint(1, 50) * 5000
    merchant = random.choice(MERCHANTS)
    rrn = str(fake.random_number(digits=10, fix_len=True))
    ref_id = f"952712{fake.random_number(digits=12, fix_len=True)}QRS{fake.random_number(digits=6, fix_len=True)}"
    waktu = (datetime.now() - timedelta(days=random.randint(0, 30), minutes=random.randint(1, 500))).strftime("%d %b %Y %H:%M:%S")
    
    html = (
        HTML_MYBCA
        .replace("{{NOMINAL}}", format_idr(nominal))
        .replace("{{MERCHANT}}", merchant)
        .replace("{{PENGAKUISISI}}", random.choice(BANKS))
        .replace("{{RRN}}", rrn)
        .replace("{{LOKASI}}", random.choice(CITIES))
        .replace("{{MERCHANT_PAN}}", f"936000{fake.random_number(digits=10, fix_len=True)}")
        .replace("{{REK_MASKED}}", f"794 - 0** - **{random.randint(10, 99)}")
        .replace("{{REF_ID}}", ref_id)
        .replace("{{WAKTU}}", waktu)
    )

    gt = {
        "gt_parse": {
            "struk_qris": {
                "penyedia": "myBCA",
                "jenis_transaksi": "Pembayaran QRIS",
                "merchant": merchant,
                "nominal": f"IDR {format_idr(nominal)}.00",
                "waktu": waktu,
                "rrn": rrn,
                "no_referensi": ref_id
            }
        }
    }
    return html, gt

def generate_dana_data():
    nominal = random.randint(1, 100) * 5000
    penerima = fake.name()
    penerima_masked = f"{penerima.split()[0]} K••••a"
    no_hp = f"08{random.choice(['12','21','52','81'])}{fake.random_number(digits=8, fix_len=True)}"
    trx_id = f"2026{fake.random_number(digits=18, fix_len=True)}"
    waktu = (datetime.now() - timedelta(days=random.randint(0, 30), minutes=random.randint(1, 500))).strftime("%d %b %Y • %H:%M")

    html = (
        HTML_DANA
        .replace("{{NOMINAL}}", format_idr(nominal))
        .replace("{{PENERIMA}}", penerima)
        .replace("{{PENERIMA_MASKED}}", penerima_masked)
        .replace("{{NO_HP}}", no_hp)
        .replace("{{TRX_ID}}", trx_id)
        .replace("{{WAKTU}}", waktu)
    )

    gt = {
        "gt_parse": {
            "struk_transfer": {
                "penyedia": "DANA",
                "jenis_transaksi": "Send Money",
                "penerima": penerima,
                "no_tujuan": no_hp,
                "nominal": f"Rp{format_idr(nominal)}",
                "waktu": waktu,
                "transaction_id": trx_id
            }
        }
    }
    return html, gt

def main(num_samples=300):
    print(f"Memulai pembuatan {num_samples} struk sintetis (myBCA & DANA)...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 420, "height": 850})

        with open(METADATA_FILE, "w", encoding="utf-8") as f_meta:
            for i in range(1, num_samples + 1):
                is_bca = (i % 2 == 0)
                html_content, gt_json = generate_mybca_data() if is_bca else generate_dana_data()
                
                prefix = "mybca" if is_bca else "dana"
                filename = f"{prefix}_{i:04d}.png"
                filepath = os.path.join(IMAGES_DIR, filename)

                page.set_content(html_content)
                target_element = page.locator(".ticket") if is_bca else page.locator(".dana-container")
                target_element.screenshot(path=filepath)

                line = {
                    "file_name": filename,
                    "ground_truth": json.dumps(gt_json, ensure_ascii=False)
                }
                f_meta.write(json.dumps(line, ensure_ascii=False) + "\n")

                if i % 50 == 0 or i == num_samples:
                    print(f"Selesai {i}/{num_samples} gambar.")

        browser.close()
    print(f"\nSelesai! Hasil dataset tersimpan di: {IMAGES_DIR}")

if __name__ == "__main__":
    main(num_samples=300)