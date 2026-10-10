import os
import json
import urllib.request
import time

def download_cord_100():
    out_dir = os.path.join(os.path.dirname(__file__), "cord_test_100")
    img_dir = os.path.join(out_dir, "images")
    os.makedirs(img_dir, exist_ok=True)

    url = "https://datasets-server.huggingface.co/rows?dataset=naver-clova-ix%2Fcord-v2&config=default&split=test&offset=0&limit=100"
    print(f"Fetching metadata for 100 CORD-v2 test samples from HuggingFace...")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        res = json.loads(resp.read().decode())
    
    rows = res.get("rows", [])
    print(f"Received {len(rows)} rows from dataset server.")

    metadata = []
    t_start = time.time()

    for idx, item in enumerate(rows):
        row = item["row"]
        img_info = row["image"]
        gt_raw = row["ground_truth"]
        
        try:
            gt_data = json.loads(gt_raw) if isinstance(gt_raw, str) else gt_raw
        except Exception:
            gt_data = {"raw": gt_raw}

        img_url = img_info["src"]
        filename = f"cord_{idx:03d}.jpg"
        target_path = os.path.join(img_dir, filename)

        if not os.path.exists(target_path) or os.path.getsize(target_path) == 0:
            urllib.request.urlretrieve(img_url, target_path)

        file_size = os.path.getsize(target_path)

        meta_entry = {
            "index": idx,
            "filename": filename,
            "size_bytes": file_size,
            "width": img_info.get("width"),
            "height": img_info.get("height"),
            "ground_truth": gt_data
        }
        metadata.append(meta_entry)

        if (idx + 1) % 10 == 0 or idx == len(rows) - 1:
            print(f"Downloaded {idx + 1}/{len(rows)} images ({file_size} bytes)")

    meta_file = os.path.join(out_dir, "cord_100_metadata.json")
    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    total_time = time.time() - t_start
    print(f"Successfully downloaded 100 images in {total_time:.2f} seconds!")
    print(f"Saved metadata to {meta_file}")

if __name__ == "__main__":
    download_cord_100()
