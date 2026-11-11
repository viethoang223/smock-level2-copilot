# smock-level2-copilot — Cấp 2 (GitHub Copilot)

Repo này là "bàn làm việc" của cấp 2 trong kiến trúc 3 cấp nhánh Smock (xem `quan-ly-facebook-sm/ops/KIEN-TRUC-3-CAP.md`). Copilot chỉ làm việc **trên file trong repo này**: không đăng nhập Facebook, không gửi gì ra ngoài.

```
Cấp 1 (n8n, 22:15) ── ghi việc ──► inbox/<loại>/<TASK_ID>.json ── git push
Cấp 2 (Copilot, 05:30) ─ git pull ─► xử lý từng file ─► outbox/<loại>/<TASK_ID>.json ─► scripts/validate.py ─► git push
Cấp 1 (n8n, 06:30) ─ git pull ─► kiểm lại ─► ghi sheet (caption = "Chờ duyệt caption") ─► chuyển file sang done/
```

## Ba loại việc

| Loại | File vào | File ra | Prompt | Ai duyệt |
| --- | --- | --- | --- | --- |
| Phái sinh caption | `inbox/captions/CAP-*.json` | `outbox/captions/CAP-*.json` (3 biến thể) | `.github/prompts/caption.prompt.md` | Người dùng duyệt trên tab Content Queue trước khi dùng |
| Chấm group | `inbox/groups/GRP-*.json` + `data/group-text/gNN.txt` | `outbox/groups/GRP-*.json` (điểm + bằng chứng) | `.github/prompts/cham-group.prompt.md` | Người dùng duyệt tier |
| Báo cáo tuần | `inbox/reports/RPT-*.json` + `data/weekly/*.csv` | `outbox/reports/RPT-*.json` + `.md` | `.github/prompts/bao-cao-tuan.prompt.md` | Người dùng đọc trước khi gửi sếp |

Định dạng file ra: `schemas/*.schema.json`. `scripts/validate.py` từ chối file sai định dạng, trùng task_id, hoặc có SĐT/email/mật khẩu.

## Chạy

**Tự động (khuyến nghị):** Task Scheduler trên máy cấp 2 chạy `scripts/run-level2.ps1` lúc 05:30 mỗi ngày. Script: `git pull` → với mỗi file inbox chưa có kết quả, gọi Copilot CLI ở chế độ không hỏi (`copilot -p … --no-ask-user`) với đúng prompt của loại việc → chạy `validate.py` → chỉ commit file hợp lệ → `git push`. File lỗi được ghi vào `logs/` và để lại cho lần sau.

**Bằng tay (khi muốn xem):** mở repo trong VS Code, Copilot Chat ở chế độ Agent, gõ `/caption` (hoặc `/cham-group`, `/bao-cao-tuan`) rồi chỉ file inbox cần xử lý. Xong chạy `py scripts/validate.py` và push.

## Cài đặt máy cấp 2 (một lần)
1. Cài Git, Python 3, Node.js 22+, VS Code + GitHub Copilot.
2. Cài Copilot CLI: `npm install -g @github/copilot`, đăng nhập `copilot` một lần (hoặc đặt biến `COPILOT_GITHUB_TOKEN` = fine-grained token có quyền "Copilot Requests").
3. `git clone` repo này về `C:\smock-level2-copilot`.
4. Chạy thử: `powershell -ExecutionPolicy Bypass -File scripts\run-level2.ps1 -DryRun`.
5. Task Scheduler → Create Task → chạy lúc 05:30, "Run whether user is logged on or not", action: `powershell -ExecutionPolicy Bypass -File C:\smock-level2-copilot\scripts\run-level2.ps1`.
6. Trên PC công ty (cấp 1), clone repo này vào `C:\smock-level2-copilot` để n8n ghi inbox và đọc outbox.

Kiểm cờ CLI bằng `copilot --help` sau mỗi lần cập nhật: tên cờ có thể đổi theo phiên bản.

## Giới hạn
- Từ 01/06/2026 Copilot tính theo GitHub AI Credits; hết hạn mức thì lệnh CLI báo lỗi (không tự chuyển sang model miễn phí). `run-level2.ps1` dừng khi gặp lỗi đầu tiên và ghi log, không chạy lại liên tục.
- Mọi kết quả cấp 2 là **bản nháp**: caption vào "Chờ duyệt caption", điểm group vào "Đã chấm" chờ người duyệt. Không có gì của cấp 2 tự đi ra Facebook.
