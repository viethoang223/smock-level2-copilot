---
mode: agent
description: Quy trình hằng ngày cấp 2 — gõ /tiep-tuc (hoặc "tiếp tục công việc")
---
Làm ngay, không hỏi lại:
1. `git pull`.
2. Mọi file trong `inbox/` chưa có file cùng tên trong `outbox/` hoặc `done/`: caption → theo `caption.prompt.md`; group → `cham-group.prompt.md`; report → `bao-cao-tuan.prompt.md`. Chép nguyên `image_link`, `sheet_row`, `source_code` từ inbox.
3. `py scripts/validate.py` từng file, sửa tới khi hợp lệ.
4. `git add outbox logs`, `git commit -m "outbox <ngày>"`, `git push`.
5. Báo tối đa 3 dòng: xong mấy việc, file lỗi, còn gì. Inbox trống → "Inbox trống, không có việc."
Không sửa n8n, không mở repo cấp 1, không hỏi credential.
