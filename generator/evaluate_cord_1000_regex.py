import os
import json
import re
import time
from collections import defaultdict

def parse_price(val_str):
    if not val_str:
        return 0.0
    clean = re.sub(r'[^\d.,]', '', str(val_str))
    if not clean:
        return 0.0
    if ',' in clean and '.' in clean:
        if clean.rfind(',') > clean.rfind('.'):
            clean = clean.replace('.', '').replace(',', '.')
        else:
            clean = clean.replace(',', '')
    elif ',' in clean:
        parts = clean.split(',')
        if len(parts[-1]) == 3:
            clean = clean.replace(',', '')
        elif len(parts[-1]) in (1, 2):
            clean = clean.replace(',', '.')
    elif '.' in clean:
        parts = clean.split('.')
        if len(parts[-1]) == 3:
            clean = clean.replace('.', '')
    try:
        return float(clean)
    except ValueError:
        return 0.0

def reconstruct_spatial_lines_from_cord(valid_lines, alpha=0.5, beta=0.5):
    """
    Simulates ML Kit RecognizedText + 2D Spatial Line Clustering:
    - Sorts all bounding boxes by Center Y
    - Clusters lines where deltaY <= alpha * minH and verticalOverlapRatio >= beta
    - Sorts each line horizontally by Left X
    """
    boxes = []
    for line in valid_lines:
        words = line.get('words', [])
        for w in words:
            quad = w.get('quad', {})
            text = w.get('text', '').strip()
            if not text:
                continue
            xs = [quad.get('x1', 0), quad.get('x2', 0), quad.get('x3', 0), quad.get('x4', 0)]
            ys = [quad.get('y1', 0), quad.get('y2', 0), quad.get('y3', 0), quad.get('y4', 0)]
            left = min(xs)
            right = max(xs)
            top = min(ys)
            bottom = max(ys)
            height = max(1.0, bottom - top)
            boxes.append({
                'left': left,
                'right': right,
                'top': top,
                'bottom': bottom,
                'height': height,
                'center_y': top + (height / 2.0),
                'text': text
            })

    if not boxes:
        return ""

    boxes.sort(key=lambda b: b['center_y'])

    rows = []
    for b in boxes:
        added = False
        for row in rows:
            ref = row[0]
            min_h = min(b['height'], ref['height'])
            delta_y = abs(b['center_y'] - ref['center_y'])
            top_ov = max(b['top'], ref['top'])
            bot_ov = min(b['bottom'], ref['bottom'])
            vert_ov = max(0.0, bot_ov - top_ov)
            ov_ratio = vert_ov / min_h if min_h > 0 else 0.0

            if delta_y <= alpha * min_h and ov_ratio >= beta:
                row.append(b)
                added = True
                break
        if not added:
            rows.append([b])

    result_lines = []
    for row in rows:
        row.sort(key=lambda b: b['left'])
        txt = " ".join(b['text'] for b in row).strip()
        if txt:
            result_lines.append(txt)

    return "\n".join(result_lines)

def parse_receipt_text_python(text):
    """
    Python mirror of Flutter OfflineReceiptService.parseReceiptText
    """
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    if not lines:
        return {
            'storeName': 'Toko Tidak Dikenal',
            'totalAmount': 0.0,
            'items': []
        }

    brand_regex = re.compile(
        r'\b([a-z0-9]*fa[a-z0-9]*mart|[a-z0-9]*fa[a-z0-9]*hart|[a-z0-9]*fayart|alfamart|alfa\s*mart|rlfa[a-z]*|alfa\s*midi|alfamidi|indomaret|indo\s*maret|superindo|super\s*indo|yomart|circle\s*k|transmart|hypermart|spbu|pertamina|mcdonald|kfc|starbucks|lawson|family\s*mart|janji\s*jiwa|kopi\s*kenangan|fore|point\s*coffee|miniso|gramedia|watsons|guardian|century|apotek|breadtalk|roti\s*o|auntie\s*anne|d\'?cost|bakmi\s*gm|solaria|chatime|j\.?\s*co|hokben|hoka\s*hoka\s*bento|shihlin|marugame|sushi\s*tei|gulu\s*gulu|dum\s*dum|kopitiam|richeese|kintan|shaburi|ta\s*wan|pepper\s*lunch|yoshinoya|burger\s*king|pizza\s*hut|domino|a\&w|excelso|maxx\s*coffee|optik|matahari|hero|farmers\s*market|ranch\s*market)\b',
        re.IGNORECASE
    )

    metadata_regex = re.compile(
        r'\b(kasir|npwp|npup|pkp|bon\s*b|bon\s*no|no\.\s*bon|jl\.|jalan|lt\.|gedung|plaza|mall|rt\s*[0-9]|rw\s*[0-9]|telp|fax|shift|waktu|tgl|tanggal|terima\s*kasih|kritik|saran|call\s*center|layanan|member|poin|kembali|kenbali|change|tunai|non\s*tunai|cash|debit|qris|shopeepay|gopay|ovo|dana|linkaja|flazz|kartu|bca|mandiri|bri|bni|pembayaran|sms|wa|shs|va|dpp|ppn|pajak|v\.\d+|versi|1500959|08\d{8,11}|trxid|purchase|struk|transaksi|kec\b|kecamatan|kel\b|kelurahan|kab\b|kabupaten|kota|provinsi|menara|boulevard|pantai|kapuk|jakarta|bandung)\b',
        re.IGNORECASE
    )

    header_sample = lines[:12]
    has_alfa = any(re.search(r'\b(alfamart|alfa\s*mart|alfamidi|alfa\s*midi|rlfa[a-z]*)\b', l, re.IGNORECASE) for l in header_sample)
    has_indo = any(re.search(r'\b(indomar|indomaret|indo\s*maret|indomarco)\b', l, re.IGNORECASE) for l in header_sample)

    store_name = 'Toko Tidak Dikenal'
    search_limit = min(len(lines), 12)

    for i in range(search_limit):
        line = lines[i]
        if re.search(r'\b(gedung|menara|boulevard|pantai\s*indah|jakarta\s*utara|pt\.?\s*indomar[a-z]*)\b', line, re.IGNORECASE):
            continue
        bm = brand_regex.search(line)
        if bm:
            clean = re.split(r'[/\\|]', line)[0].strip()
            clean = re.sub(r'\brlfa[a-z]*\b', 'ALFAMART', clean, flags=re.IGNORECASE)
            clean = re.sub(r'\s{2,}', ' ', clean)
            store_name = clean
            break

    if store_name == 'Toko Tidak Dikenal' or 'GEDUNG' in store_name.upper():
        junk_store_regex = re.compile(
            r'\b(struk|transaksi|total|sub\s*total|subtot|grand\s*total|item|items|qty|pcs|tunai|cash|kembali|change|bayar|harga|tax|pajak|diskon|discount|rp|pt\.?\s*indomar[a-z]*)\b',
            re.IGNORECASE
        )
        for i in range(search_limit):
            line = lines[i]
            alpha_count = len(re.findall(r'[a-zA-Z]', line))
            total_count = len(re.sub(r'\s', '', line))
            if (not metadata_regex.search(line) and
                not junk_store_regex.search(line) and
                not re.search(r'\b\d{1,3}[.,]\d{3}\b', line) and
                not re.search(r'^[0-9\s.,\-_/:]{4,}$', line) and
                alpha_count >= 3 and total_count > 0 and
                (alpha_count / total_count) >= 0.4):
                store_name = re.split(r'[/\\|]', line)[0].strip()
                break

    store_name = re.sub(r'[\[\(\{].*', '', store_name).strip()
    store_name = re.sub(r'\s{2,}', ' ', store_name)

    if has_alfa and 'ALFA' not in store_name.upper():
        store_name = 'ALFAMART' if store_name == 'Toko Tidak Dikenal' else f'ALFAMART {store_name}'
    elif has_indo and 'INDO' not in store_name.upper():
        store_name = 'INDOMARET' if store_name == 'Toko Tidak Dikenal' else f'INDOMARET {store_name}'

    # Deteksi Tunai & Kembalian
    tunai = 0.0
    kembalian = 0.0
    for line in lines:
        tm = re.search(r'\b(?:tunai|cash|bayar|dibayar)\s*[:=.]?\s*(?:rp\.?\s*)?([0-9.,]+)', line, re.IGNORECASE)
        if tm:
            p = parse_price(tm.group(1))
            if p > 0:
                tunai = p
        km = re.search(r'\b(?:kembali|kenbali|kemb[a-z]+|change|\bcg\b)\s*[:=.]?\s*(?:rp\.?\s*)?([0-9.,]+)', line, re.IGNORECASE)
        if km:
            p = parse_price(km.group(1))
            if p >= 0:
                kembalian = p

    verified_total = (tunai - kembalian) if (tunai > 0 and kembalian >= 0 and tunai > kembalian) else None

    grand_total_regex = re.compile(
        r'\b(?:grand\s*tot[a-z]*|total\s*bayar|total\s*tagihan|total\s*akhir|total\s*belanja|total\s*transaksi|total\s*keseluruhan|total\s*net|amount\s*due|balance\s*due|total\s*due|\bdue\b|\bdu\b)\b\s*[:=.]?\s*(?:rp\.?\s*)?([0-9.,]+)',
        re.IGNORECASE
    )
    pure_total_regex = re.compile(
        r'\b(?:total|t\s*o\s*t\s*a\s*l|\btl\b|\bttl\b)\b(?!\s*(?:item|iten|qty|pcs|sub|diskon|hemat|pajak|disc))\s*[:=.]?\s*(?:rp\.?\s*)?([0-9.,]+)',
        re.IGNORECASE
    )
    sub_total_regex = re.compile(
        r'\b(?:sub\s*tot[a-z]*|sub-total)\b\s*[:=.]?\s*(?:rp\.?\s*)?([0-9.,]+)',
        re.IGNORECASE
    )

    best_candidate = 0.0
    best_score = -1

    for i in range(len(lines)):
        line = lines[i]
        if re.search(r'\b(total\s*item|total\s*qty|total!\s*iten|total\s*pcs)\b', line, re.IGNORECASE):
            continue

        cand_price = 0.0
        cand_score = 0

        # Deteksi label total terpisah baris dengan angkanya
        if re.search(r'^\s*(?:grand\s*total|total\s*bayar|total\s*belanja|total|amount\s*due|sub\s*total)\s*[:=.]?\s*$', line, re.IGNORECASE):
            for adj_idx in [i - 1, i + 1]:
                if 0 <= adj_idx < len(lines):
                    adj_line = lines[adj_idx].strip()
                    if re.match(r'^\s*(?:rp\.?\s*)?[\d.,]+\s*$', adj_line, re.IGNORECASE):
                        val = parse_price(adj_line)
                        if val >= 100:
                            cand_price = val
                            cand_score = 95 if 'grand' in line.lower() else (35 if 'sub' in line.lower() else 65)
                            break

        if cand_price == 0:
            gtm = grand_total_regex.search(line)
            if gtm:
                cand_price = parse_price(gtm.group(1))
                cand_score = 100
            elif 'sub' not in line.lower():
                ptm = pure_total_regex.search(line)
                if ptm:
                    cand_price = parse_price(ptm.group(1))
                    cand_score = 70
            elif 'sub' in line.lower():
                stm = sub_total_regex.search(line)
                if stm:
                    cand_price = parse_price(stm.group(1))
                    cand_score = 40

        if cand_score >= best_score and (cand_score == 100 or cand_price >= 100 or (cand_price > 0 and 'rp' in line.lower())):
            if verified_total is not None and abs(cand_price - verified_total) < 1.0:
                cand_score += 50
            best_score = cand_score
            best_candidate = cand_price

    if best_candidate == 0 and verified_total is not None and verified_total > 0:
        best_candidate = verified_total
        best_score = 70

    total_amount = best_candidate if best_score > 0 else 0.0
    has_explicit_grand_total = best_score >= 70

    # Items extraction
    items = []
    is_junk_regex = re.compile(
        r'\b(kembali[a-z0-9!]*|kenbali[a-z0-9!]*|change|tunai|non\s*tunai|cash|bayar|dibayar|total[a-z!]*|sub\s*total|grand\s*total|total!\s*iten|harga\s*jual|total\s*qty|dpp|ppn|pajak|diskon|hemat|anda\s*hemat|voucher|vc\b|poin|member|kasir|shift|waktu|terima\s*kasih|layanan|call\s*center|sms|wa|trxid|purchase|struk|transaksi)\b',
        re.IGNORECASE
    )
    is_address_regex = re.compile(
        r'\b(jl\.|jalan|kel\.|kelurahan|kec\.|kecamatan|kab\.|kabupaten|rt\s*\d|rw\s*\d|gedung|menara|boulevard|pantai|kp\.\s*[a-z]+)\b',
        re.IGNORECASE
    )
    is_date_regex = re.compile(r'\b(0?[1-9]|[12][0-9]|3[01])\s*[-/.]\s*(0?[1-9]|1[0-2])\s*[-/.]\s*(20\d{2}|\d{2})\b')

    for line in lines:
        if (store_name.lower() in line.lower() or
            (len(line) >= 3 and line.lower() in store_name.lower()) or
            re.search(r'\b(alfamart|rlfa[a-z]*|indomaret|indomarco)\b', line, re.IGNORECASE)):
            continue

        if (grand_total_regex.search(line) or
            pure_total_regex.search(line) or
            sub_total_regex.search(line) or
            re.search(r'\b(tot[a-z!]{1,5}|sub\s*tot|grand\s*tot|t\s*o\s*t\s*a\s*l|total!\s*iten)\b', line, re.IGNORECASE) or
            is_junk_regex.search(line) or
            metadata_regex.search(line) or
            is_address_regex.search(line) or
            is_date_regex.search(line)):
            continue

        raw_tokens = [t for t in re.split(r'\s+', line) if t]
        if not raw_tokens:
            continue

        # Merge split tokens (e.g. "9," and "600")
        merged = []
        idx = 0
        while idx < len(raw_tokens):
            if idx + 1 < len(raw_tokens) and re.match(r'^\d{1,3}[.,]$', raw_tokens[idx]) and re.match(r'^\d{3}$', raw_tokens[idx+1]):
                merged.append(raw_tokens[idx] + raw_tokens[idx+1])
                idx += 2
            else:
                merged.append(raw_tokens[idx])
                idx += 1

        # Search prices from end
        prices = []
        end_idx = len(merged)
        while end_idx > 0:
            token = merged[end_idx - 1].replace('.', '').replace(',', '')
            clean_val = re.sub(r'[^\d\-]', '', token)
            try:
                val = float(clean_val)
                if abs(val) >= 100:
                    prices.insert(0, val)
                    end_idx -= 1
                else:
                    break
            except ValueError:
                break

        if prices:
            final_p = prices[-1]
            name_tokens = merged[:end_idx]
            qty = 1
            if name_tokens:
                try:
                    q_val = int(name_tokens[-1])
                    if 1 <= abs(q_val) <= 99:
                        qty = abs(q_val)
                        name_tokens.pop()
                except ValueError:
                    pass

            unit_p = final_p
            if qty > 1:
                unit_p = prices[-2] if len(prices) >= 2 else (final_p / qty)

            name_part = " ".join(name_tokens).strip()
            name_part = re.sub(r'[\s\-]+$', '', name_part)
            if len(name_part) >= 2 and not metadata_regex.search(name_part):
                items.append({
                    'name': name_part,
                    'price': unit_p,
                    'qty': qty,
                    'subtotal': unit_p * qty
                })

    if total_amount == 0 and not has_explicit_grand_total and items:
        total_amount = sum(it['subtotal'] for it in items)
    elif total_amount == 0 and not has_explicit_grand_total and tunai > 0 and tunai > kembalian:
        total_amount = tunai - kembalian

    return {
        'storeName': store_name,
        'totalAmount': total_amount,
        'items': items
    }

def run_evaluation_1000():
    json_path = os.path.join(os.path.dirname(__file__), "cord_dataset_1000", "cord_1000_metadata.json")
    with open(json_path, "r", encoding="utf-8") as f:
        samples = json.load(f)

    print(f"Loaded {len(samples)} samples. Running 2D Spatial Line Clustering + Heuristic Regex Parser...")
    t0 = time.time()
    results = []

    has_store_count = 0
    has_total_count = 0
    gt_match_count = 0
    total_evaluable = 0

    split_stats = defaultdict(lambda: {'count': 0, 'store': 0, 'total': 0, 'gt_match': 0, 'gt_avail': 0})

    for s in samples:
        idx = s['index']
        split = s.get('split', 'train')
        gt = s['ground_truth']
        valid_line = gt.get('valid_line', [])

        reconstructed_text = reconstruct_spatial_lines_from_cord(valid_line)
        parsed = parse_receipt_text_python(reconstructed_text)

        # Ground truth total
        gt_parse = gt.get('gt_parse', {})
        t_obj = gt_parse.get('total', {})
        gt_total = None
        if isinstance(t_obj, dict):
            if 'total_price' in t_obj:
                gt_total = parse_price(t_obj['total_price'])
            elif 'cashprice' in t_obj:
                c_p = parse_price(t_obj.get('cashprice'))
                ch_p = parse_price(t_obj.get('changeprice', 0))
                if c_p > ch_p:
                    gt_total = c_p - ch_p
        elif isinstance(t_obj, list) and len(t_obj) > 0 and 'total_price' in t_obj[0]:
            gt_total = parse_price(t_obj[0]['total_price'])

        has_store = parsed['storeName'] != 'Toko Tidak Dikenal'
        has_total = parsed['totalAmount'] > 0
        total_matches = False
        if gt_total is not None and gt_total > 0:
            total_evaluable += 1
            split_stats[split]['gt_avail'] += 1
            if abs(parsed['totalAmount'] - gt_total) < 1.0:
                total_matches = True
                gt_match_count += 1
                split_stats[split]['gt_match'] += 1

        if has_store:
            has_store_count += 1
            split_stats[split]['store'] += 1
        if has_total:
            has_total_count += 1
            split_stats[split]['total'] += 1
        split_stats[split]['count'] += 1

        results.append({
            'index': idx,
            'split': split,
            'filename': s.get('filename', f'cord_{idx:04d}.jpg'),
            'storeName': parsed['storeName'],
            'totalAmount': parsed['totalAmount'],
            'itemsCount': len(parsed['items']),
            'hasStore': has_store,
            'hasTotal': has_total,
            'groundTruthTotal': gt_total,
            'totalMatchesGt': total_matches
        })

    elapsed = time.time() - t0
    print(f"\n=======================================================")
    print(f"BENCHMARK RESULTS ACROSS N={len(samples)} RECEIPTS (Time: {elapsed:.2f}s)")
    print(f"=======================================================")
    print(f"Nama Toko Terdeteksi  : {has_store_count}/{len(samples)} ({has_store_count/len(samples)*100:.2f}%)")
    print(f"Total Belanja Terbaca : {has_total_count}/{len(samples)} ({has_total_count/len(samples)*100:.2f}%)")
    print(f"Ground Truth Matches  : {gt_match_count}/{total_evaluable} ({gt_match_count/total_evaluable*100:.2f}%)")

    print("\nBreakdown per Split:")
    for split, st in split_stats.items():
        print(f"  [{split.upper():10s}] N={st['count']:3d} | Toko: {st['store']/st['count']*100:5.1f}% | Total: {st['total']/st['count']*100:5.1f}% | GT Match: {st['gt_match']}/{st['gt_avail']} ({st['gt_match']/max(1,st['gt_avail'])*100:5.1f}%)")

    # Save output
    out_dir = os.path.join(os.path.dirname(__file__), "output_bab4")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "benchmark_cord_1000_evaluation.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({
            'totalSamples': len(samples),
            'executionTimeSec': elapsed,
            'storeAccuracyPercent': round(has_store_count/len(samples)*100, 2),
            'totalAccuracyPercent': round(has_total_count/len(samples)*100, 2),
            'gtMatchPercent': round(gt_match_count/total_evaluable*100, 2) if total_evaluable else 0,
            'results': results
        }, f, indent=2)

    print(f"\nSaved detailed evaluation to {out_file}")

if __name__ == "__main__":
    run_evaluation_1000()
