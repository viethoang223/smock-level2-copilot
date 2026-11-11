"""Kiểm file outbox trước khi commit. Không cần thư viện ngoài.

    python scripts/validate.py                 # kiểm mọi file trong outbox/
    python scripts/validate.py outbox/x.json   # kiểm một file
Thoát mã 0 = tất cả hợp lệ; 1 = có file lỗi (in lý do từng file).
"""
import json, re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
FORBID_KEYS = {"phone", "email", "sdt", "so_dien_thoai", "password", "mat_khau", "2fa"}
PHONE = re.compile(r"(\+?\d[\d\s.\-]{8,}\d)")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
BAIT = re.compile(r"\b(comment|type)\s+\S+\s+(below|if)\b|\btag\s+(a|your)\s+\w*\s*friend|\b(like|share)\s+(this|if)\b", re.I)


def check(value, schema, path, errs):
    t = schema.get("type")
    if "const" in schema and value != schema["const"]:
        errs.append(f"{path}: phải là {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        errs.append(f"{path}: {value!r} không thuộc {schema['enum']}")
    types = t if isinstance(t, list) else ([t] if t else [])
    pymap = {"string": str, "integer": int, "object": dict, "array": list, "boolean": bool, "null": type(None)}
    if types and not any(isinstance(value, pymap[x]) and not (x == "integer" and isinstance(value, bool)) for x in types):
        errs.append(f"{path}: sai kiểu, cần {types}")
        return
    if isinstance(value, str):
        if "pattern" in schema and not re.search(schema["pattern"], value): errs.append(f"{path}: sai mẫu {schema['pattern']}")
        if "minLength" in schema and len(value) < schema["minLength"]: errs.append(f"{path}: ngắn hơn {schema['minLength']} ký tự")
        if "maxLength" in schema and len(value) > schema["maxLength"]: errs.append(f"{path}: dài hơn {schema['maxLength']} ký tự")
    if isinstance(value, int) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]: errs.append(f"{path}: nhỏ hơn {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]: errs.append(f"{path}: lớn hơn {schema['maximum']}")
    if isinstance(value, dict):
        props = schema.get("properties", {})
        for k in schema.get("required", []):
            if k not in value: errs.append(f"{path}.{k}: thiếu")
        if schema.get("additionalProperties") is False:
            for k in value:
                if k not in props: errs.append(f"{path}.{k}: trường không cho phép")
        for k, v in value.items():
            if k in props: check(v, props[k], f"{path}.{k}", errs)
    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]: errs.append(f"{path}: cần ít nhất {schema['minItems']} phần tử")
        if "maxItems" in schema and len(value) > schema["maxItems"]: errs.append(f"{path}: tối đa {schema['maxItems']} phần tử")
        for i, v in enumerate(value): check(v, schema.get("items", {}), f"{path}[{i}]", errs)


def walk_keys(o, out):
    if isinstance(o, dict):
        for k, v in o.items(): out.add(k.lower()); walk_keys(v, out)
    elif isinstance(o, list):
        for v in o: walk_keys(v, out)


def validate(p: pathlib.Path):
    errs = []
    try:
        o = json.loads(p.read_text(encoding="utf8"))
    except Exception as e:
        return [f"không đọc được JSON: {e}"]
    kind = o.get("kind")
    schema_file = {"caption": "caption", "group": "group", "weekly_report": "report"}.get(kind)
    if not schema_file:
        return [f"kind không hợp lệ: {kind!r}"]
    check(o, json.loads((ROOT / "schemas" / f"{schema_file}.result.schema.json").read_text(encoding="utf8")), "$", errs)
    if p.stem != o.get("task_id"): errs.append(f"tên file phải trùng task_id ({o.get('task_id')})")
    inbox = ROOT / "inbox" / p.parent.name / p.name
    if not inbox.exists() and not (ROOT / "done" / p.name).exists(): errs.append("không có file inbox tương ứng")
    keys = set(); walk_keys(o, keys)
    if keys & FORBID_KEYS: errs.append(f"có trường bị cấm: {sorted(keys & FORBID_KEYS)}")
    text = json.dumps(o, ensure_ascii=False)
    if EMAIL.search(text): errs.append("có địa chỉ email")
    if PHONE.search(text): errs.append("có số giống số điện thoại")
    if kind == "caption":
        caps = [v.get("caption", "") for v in o.get("variants", [])]
        for i, c in enumerate(caps):
            if BAIT.search(c): errs.append(f"variants[{i}]: có câu xin like/comment/share/tag")
            if re.search(r"https?://|www\.", c): errs.append(f"variants[{i}]: có link")
            if "{{MA_BAI}}" not in c: errs.append(f"variants[{i}]: thiếu {{{{MA_BAI}}}} trong lời mời nhắn tin")
        if len(set(caps)) < len(caps): errs.append("các biến thể bị trùng nhau")
    if kind == "group" and o.get("total") is not None:
        s = o.get("scores", {})
        vals = [s.get(k) for k in ("icp", "sell", "active", "engage", "buyer", "geo", "spam")]
        if None not in vals and sum(vals) != o["total"]: errs.append(f"total {o['total']} khác tổng điểm {sum(vals)}")
        exp = "Loại" if s.get("gates") else ("A" if o["total"] >= 75 else "B" if o["total"] >= 50 else "C" if o["total"] >= 30 else "Loại")
        if o.get("tier") != exp: errs.append(f"tier phải là {exp}")
    return errs


def main(argv):
    files = [pathlib.Path(a) for a in argv] or sorted((ROOT / "outbox").glob("*/*.json"))
    bad = 0; seen = set()
    for f in files:
        f = f if f.is_absolute() else (ROOT / f)
        errs = validate(f)
        if f.stem in seen: errs.append("task_id trùng trong outbox")
        seen.add(f.stem)
        print(("OK   " if not errs else "LỖI ") + str(f.relative_to(ROOT)) + ("" if not errs else "\n     - " + "\n     - ".join(errs)))
        bad += bool(errs)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
