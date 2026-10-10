import os
import json
import time
import fsspec
import pyarrow.parquet as pq

def compile_cord_1000():
    out_dir = os.path.join(os.path.dirname(__file__), "cord_dataset_1000")
    os.makedirs(out_dir, exist_ok=True)
    out_json = os.path.join(out_dir, "cord_1000_metadata.json")

    urls = [
        ("train", "https://huggingface.co/api/datasets/naver-clova-ix/cord-v2/parquet/default/train/0.parquet"),
        ("train", "https://huggingface.co/api/datasets/naver-clova-ix/cord-v2/parquet/default/train/1.parquet"),
        ("train", "https://huggingface.co/api/datasets/naver-clova-ix/cord-v2/parquet/default/train/2.parquet"),
        ("train", "https://huggingface.co/api/datasets/naver-clova-ix/cord-v2/parquet/default/train/3.parquet"),
        ("validation", "https://huggingface.co/api/datasets/naver-clova-ix/cord-v2/parquet/default/validation/0.parquet"),
        ("test", "https://huggingface.co/api/datasets/naver-clova-ix/cord-v2/parquet/default/test/0.parquet"),
    ]

    print("=== Downloading all 1,000 CORD-v2 ground truths via Parquet Range Requests ===")
    fs = fsspec.filesystem("http")
    all_samples = []
    global_idx = 0
    t0 = time.time()

    for split, url in urls:
        part_name = f"{split}/{url.split('/')[-1]}"
        print(f"Reading {part_name}...")
        t_part = time.time()
        with fs.open(url, "rb") as f:
            pf = pq.ParquetFile(f)
            tab = pf.read(columns=["ground_truth"])
            gts = tab["ground_truth"].to_pylist()
            for g in gts:
                try:
                    gt_obj = json.loads(g) if isinstance(g, str) else g
                except Exception:
                    gt_obj = {"raw": g}

                entry = {
                    "index": global_idx,
                    "split": split,
                    "filename": f"cord_{global_idx:04d}.jpg",
                    "ground_truth": gt_obj
                }
                all_samples.append(entry)
                global_idx += 1
        print(f"  -> Done {len(gts)} records in {time.time()-t_part:.2f}s (Total: {len(all_samples)})")

    print(f"\nWriting {len(all_samples)} records to {out_json}...")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(all_samples, f, indent=2, ensure_ascii=False)

    size_mb = os.path.getsize(out_json) / (1024 * 1024)
    print(f"SUCCESS! Saved {len(all_samples)} records in {time.time()-t0:.2f}s ({size_mb:.2f} MB)")

if __name__ == "__main__":
    compile_cord_1000()
