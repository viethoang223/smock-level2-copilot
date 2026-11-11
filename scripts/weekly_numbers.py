"""Tính số cho báo cáo tuần từ CSV trong data/weekly/ (cấp 1 xuất). Copilot chỉ dùng số in ra ở đây.

CSV kỳ vọng: bao-cao-ngay.csv (cột như tab Báo cáo ngày), lead-hunter.csv (cột như tab Lead Hunter).
"""
import csv, json, pathlib, collections

D = pathlib.Path(__file__).resolve().parent.parent / "data" / "weekly"
out = {}
p = D / "bao-cao-ngay.csv"
if p.exists():
    rows = list(csv.DictReader(p.open(encoding="utf8")))
    tot = collections.Counter()
    for r in rows:
        for k in ("Việc xong", "Việc lỗi", "Bài tường", "Bài group", "Join", "Kết bạn", "Tương tác"):
            try: tot[k] += float(r.get(k) or 0)
            except ValueError: pass
    out["hoat_dong"] = dict(tot)
    out["den_do"] = sum(1 for r in rows if r.get("Đèn") == "Đỏ")
p = D / "lead-hunter.csv"
if p.exists():
    rows = list(csv.DictReader(p.open(encoding="utf8")))
    out["lead"] = dict(collections.Counter(r.get("Trạng thái", "") for r in rows))
print(json.dumps(out, ensure_ascii=False, indent=2))
