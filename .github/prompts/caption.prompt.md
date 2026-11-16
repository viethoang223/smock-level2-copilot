---
mode: agent
description: Phái sinh 3 biến thể caption từ một bài gốc trong inbox/captions
---
Đọc file inbox được chỉ định (hoặc file `inbox/captions/*.json` đầu tiên chưa có kết quả trong `outbox/captions/`), đọc `docs/brand-facts.md`.

Viết **3 biến thể** caption tiếng Anh từ `source_caption`, mỗi biến thể:
- Giữ đúng sản phẩm và sự thật của bài gốc; đổi góc kể (ví dụ: chi tiết đường thêu · quy trình xưởng · gợi ý collection theo mùa cho boutique).
- Nhắc rõ MOQ 15 pieces per style, free unlimited 2D mock-ups, production timing, và cam kết giao đúng hẹn; không tự bịa con số thời gian hoặc phí ship.
- 60–120 từ, tối đa 5 hashtag, không link, không số điện thoại, không xin like/comment/share/tag.
- Kết bằng lời mời nhắn tin có mã: `DM or WhatsApp us code {{MA_BAI}} for the catalog` (giữ nguyên chữ `{{MA_BAI}}`; cấp 1 sẽ thay khi xếp lịch).
- Ba biến thể phải khác nhau rõ ràng (không chỉ đổi vài từ).

Ghi `outbox/captions/<task_id>.json` theo `schemas/caption.result.schema.json`. Chép nguyên `image_link` từ file inbox vào kết quả:
`{"task_id", "kind":"caption", "source_code", "sheet_row", "image_link", "type": "group"|"wall", "variants":[{"angle","caption"}×3], "notes"}`.
Sau đó chạy `python scripts/validate.py outbox/captions/<task_id>.json`.
