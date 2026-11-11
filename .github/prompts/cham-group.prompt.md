---
mode: agent
description: Chấm một Facebook group theo thang 100 điểm từ file text đã lấy sẵn
---
Đọc file inbox được chỉ định (hoặc file `inbox/groups/*.json` đầu tiên chưa có kết quả), mở file text ở trường `text_file` (trong `data/group-text/`), đọc `docs/thang-diem-group.md`.

Chấm đúng theo thang:
- Chỉ dựa vào nội dung file text (nội quy + các bài gần nhất). Không suy đoán ngoài file.
- Đếm thật khi tiêu chí cần đếm (số bài/ngày, số bài ISO, trung vị tương tác) và ghi con số vào `evidence`.
- Thiếu dữ liệu cho một khoá → để `null` và ghi lý do trong `notes`; khi đó `total` và `tier` là `null`.

Ghi `outbox/groups/<task_id>.json` theo `schemas/group.result.schema.json`:
`{"task_id","kind":"group","stt","sheet_row","scores":{"gates","icp","sell","active","engage","buyer","geo","spam"},"total","tier","evidence","notes"}`.
Sau đó chạy `python scripts/validate.py outbox/groups/<task_id>.json`.
