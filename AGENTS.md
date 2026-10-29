# Hướng dẫn cho AI agent

## Commit và push

- Tác giả commit chỉ là chủ repo (`pdh372 <phamduchuy372000h@gmail.com>`, lấy từ `git config`). Không đổi author hay committer.
- Không thêm trailer `Co-authored-by`, `Generated-by`, `Signed-off-by` của bot, hay dòng kiểu "Generated with ..." vào commit message, PR, hoặc bất kỳ file nào trong repo.

## Test

```bash
python3 -m unittest discover -s tests
```

Thêm cụm từ vào `scripts/check_ai_tells.py` thì thêm cả vào `references/ai-tells.md`. Thêm ví dụ vào `references/examples.md` thì bản "Trước" phải bị script bắt, bản "Sau" phải sạch.
