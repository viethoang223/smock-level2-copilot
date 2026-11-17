# Chạy cấp 2 không cần người: git pull -> Copilot CLI xử lý từng file inbox -> validate -> push.
# Task Scheduler: powershell -ExecutionPolicy Bypass -File C:\smock-level2-copilot\scripts\run-level2.ps1
param([switch]$DryRun, [int]$MaxTasks = 15)
$ErrorActionPreference = 'Stop'
$Repo = Split-Path -Parent $PSScriptRoot
Set-Location $Repo
$log = Join-Path $Repo ("logs\run-" + (Get-Date -Format 'yyyyMMdd-HHmm') + ".log")
function Log($m) { $line = "$(Get-Date -Format 'HH:mm:ss') $m"; Add-Content -Path $log -Value $line -Encoding utf8; Write-Host $line }

# Khoá: không chạy chồng 2 phiên
$lock = Join-Path $Repo 'logs\.lock'
if (Test-Path $lock) { if ((Get-Item $lock).LastWriteTime -gt (Get-Date).AddHours(-2)) { Log 'Đang có phiên khác chạy, thoát.'; exit 0 } }
New-Item -ItemType File -Force $lock | Out-Null
try {
  $ErrorActionPreference = 'Continue'; git pull --rebase --quiet 2>&1 | Out-Null; $ErrorActionPreference = 'Stop'
  $prompts = @{ captions = '.github/prompts/caption.prompt.md'; groups = '.github/prompts/cham-group.prompt.md'; reports = '.github/prompts/bao-cao-tuan.prompt.md' }
  $todo = Get-ChildItem inbox -Recurse -Filter *.json | Where-Object {
    -not (Test-Path (Join-Path $Repo ("outbox\" + $_.Directory.Name + "\" + $_.Name))) -and -not (Test-Path (Join-Path $Repo ("done\" + $_.Name)))
  } | Select-Object -First $MaxTasks
  Log "Có $($todo.Count) việc."
  $done = 0
  foreach ($f in $todo) {
    $kind = $f.Directory.Name
    $rel = "inbox/$kind/$($f.Name)"
    # Prompt 1 dòng (copilot.cmd không nhận tham số nhiều dòng; dòng '---' của front-matter bị hiểu là cờ)
    $prompt = "Doc va lam dung huong dan trong $($prompts[$kind]) va .github/copilot-instructions.md. File can xu ly: $rel. Ghi ket qua vao outbox cung ten, chay py scripts/validate.py cho file do, lam dung mot file nay roi dung."
    if ($DryRun) { Log "[thử] sẽ xử lý $rel"; continue }
    Log "Xử lý $rel"
    $ErrorActionPreference = 'Continue'   # PowerShell 5.1: stderr của chương trình ngoài không được làm dừng script
    # Chỉ cho đọc/ghi file và chạy validate; cấm git, mạng, xoá. Kiểm lại tên cờ bằng: copilot --help
    copilot.cmd -p $prompt --no-ask-user `
      --allow-tool 'write' --allow-tool 'shell(py scripts/validate.py:*)' `
      --deny-tool 'shell(git:*)' --deny-tool 'shell(rm:*)' --deny-tool 'shell(Remove-Item:*)' --deny-tool 'shell(curl:*)' 2>&1 |
      Out-File -Append -FilePath $log -Encoding utf8
    $code = $LASTEXITCODE; $ErrorActionPreference = 'Stop'
    if ($code -ne 0) { Log "Copilot lỗi (mã $code) - có thể hết hạn mức. Dừng."; break }
    $out = "outbox/$kind/$($f.Name)"
    if (-not (Test-Path $out)) { Log "Không thấy $out - bỏ qua lần này."; continue }
    py -I -X utf8 scripts/validate.py $out | Out-File -Append -FilePath $log -Encoding utf8
    if ($LASTEXITCODE -ne 0) { Log "File $out không hợp lệ - chuyển sang logs/, không commit."; Move-Item $out (Join-Path $Repo "logs\$($f.BaseName).invalid.json") -Force; continue }
    git add $out
    if ($kind -eq 'reports') { git add ("outbox/reports/" + $f.BaseName + ".md") 2>$null }
    $done++
  }
  if ($done -gt 0) { git commit -m "outbox $(Get-Date -Format 'yyyy-MM-dd HH:mm'): $done việc" --quiet; git push --quiet; Log "Đã đẩy $done kết quả." }
} catch { Log "LỖI: $_" } finally { Remove-Item $lock -Force -ErrorAction SilentlyContinue }
