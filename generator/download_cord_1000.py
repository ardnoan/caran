import os
import json
import urllib.request
import time

def fetch_split(split_name, total_count):
    rows = []
    offset = 0
    limit = 100
    while offset < total_count:
        url = f"https://datasets-server.huggingface.co/rows?dataset=naver-clova-ix%2Fcord-v2&config=default&split={split_name}&offset={offset}&limit={limit}"
        print(f"Fetching {split_name} [offset={offset}, limit={limit}]...")
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=45) as resp:
                    data = json.loads(resp.read().decode())
                batch = data.get("rows", [])
                rows.extend(batch)
                print(f"  Received {len(batch)} rows (total so far: {len(rows)})")
                break
            except Exception as e:
                print(f"  Attempt {attempt+1} failed: {e}. Retrying in 2s...")
                time.sleep(2)
        offset += limit
        time.sleep(0.5)
    return rows

def main():
    out_dir = os.path.join(os.path.dirname(__file__), "cord_dataset_1000")
    os.makedirs(out_dir, exist_ok=True)
    meta_file = os.path.join(out_dir, "cord_1000_metadata.json")

    all_samples = []
    
    # Check if test split already exists in cord_test_100
    test_100_path = os.path.join(os.path.dirname(__file__), "cord_test_100", "cord_100_metadata.json")
    
    splits = [
        ("train", 800),
        ("validation", 100),
        ("test", 100)
    ]

    global_idx = 0
    for split_name, count in splits:
        t0 = time.time()
        print(f"\n=== Downloading split: {split_name} ({count} samples) ===")
        rows = fetch_split(split_name, count)
        print(f"Done split {split_name} in {time.time() - t0:.2f}s with {len(rows)} rows.")

        for item in rows:
            row = item["row"]
            img_info = row.get("image", {})
            gt_raw = row.get("ground_truth", "")
            try:
                gt_data = json.loads(gt_raw) if isinstance(gt_raw, str) else gt_raw
            except Exception:
                gt_data = {"raw": gt_raw}

            entry = {
                "index": global_idx,
                "split": split_name,
                "row_idx": item.get("row_idx", global_idx),
                "image_url": img_info.get("src") if isinstance(img_info, dict) else "",
                "width": img_info.get("width") if isinstance(img_info, dict) else None,
                "height": img_info.get("height") if isinstance(img_info, dict) else None,
                "ground_truth": gt_data
            }
            all_samples.append(entry)
            global_idx += 1

    print(f"\nTotal collected samples: {len(all_samples)}")
    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump(all_samples, f, indent=2, ensure_ascii=False)
    print(f"Saved complete metadata to {meta_file} ({os.path.getsize(meta_file)} bytes)")

if __name__ == "__main__":
    main()
