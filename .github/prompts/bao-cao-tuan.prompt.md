---
mode: agent
description: Viết báo cáo tuần từ số liệu đã tính sẵn
---
Đọc file inbox `inbox/reports/RPT-*.json` và các file CSV trong `data/weekly/` (cấp 1 L1-06 xuất mỗi Chủ nhật: `bao-cao-ngay.csv` = số theo nick/ngày tính từ Nhật Ký SM, `lead-hunter.csv` = chỉ cột Trạng thái).

**Không tự tính lại số khác với CSV.** Nếu cần tổng/tỷ lệ, chạy `python scripts/weekly_numbers.py` (script tính từ CSV) và chỉ dùng kết quả của nó.

Viết `outbox/reports/<task_id>.md` (tiếng Việt, tối đa 1 trang):
1. Một câu kết luận có số (QI tuần, so với tuần trước).
2. Bảng: chỉ số · tuần này · tuần trước · KPI.
3. Ba điều tốt nhất, ba vấn đề, ba việc đề xuất cho tuần tới — mỗi ý dẫn số từ CSV.

Ghi kèm `outbox/reports/<task_id>.json`: `{"task_id","kind":"weekly_report","report_file","numbers_source","notes"}`. Chạy `python scripts/validate.py`.
