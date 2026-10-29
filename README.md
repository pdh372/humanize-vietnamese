# humanize-vietnamese

Skill giúp Claude Code và GitHub Copilot viết tiếng Việt tự nhiên như người thật nói. Bỏ giọng AI: câu dạo đầu sáo rỗng, văn dịch từ tiếng Anh, "không chỉ... mà còn...", câu đều đều, từ ngữ phóng đại. Có thêm hướng dẫn riêng cho kịch bản voice, TTS và video ngắn.

A skill that makes Claude Code and GitHub Copilot write Vietnamese that sounds like a real person, not a chatbot.

## Cài đặt

### Claude Code

Chạy trong Claude Code:

```
/plugin marketplace add pdh372/humanize-vietnamese
/plugin install humanize-vietnamese@humanize-vietnamese
```

### GitHub Copilot CLI

Chạy trong terminal:

```bash
copilot plugin marketplace add pdh372/humanize-vietnamese
copilot plugin install humanize-vietnamese@humanize-vietnamese
```

Mở session mới sau khi cài.

### Cách khác: symlink (cho cả hai, cập nhật bằng `git pull`)

Dùng cách này nếu Copilot của bạn (ví dụ chat trong VS Code) đọc `~/.copilot/skills` nhưng không đọc plugin của CLI. Đừng cài cả hai cách cùng lúc, kẻo skill bị nhận hai lần.

```bash
git clone https://github.com/pdh372/humanize-vietnamese.git ~/humanize-vietnamese
~/humanize-vietnamese/install.sh
```

Gỡ: `~/humanize-vietnamese/install.sh --uninstall`

## Cách dùng

Skill tự kích hoạt khi bạn nhờ viết hoặc sửa văn tiếng Việt cho "tự nhiên", "giọng người", "đỡ AI", hoặc khi soạn caption, bài đăng, kịch bản voice. Ví dụ:

- `Viết lại đoạn này cho tự nhiên: ...`
- `Viết caption TikTok giới thiệu app này, giọng miền Nam, xưng tui`
- `Soạn kịch bản voice một phút về 3 tin công nghệ tuần này`
- `Viết email báo sếp dự án trễ hai ngày, lịch sự nhưng đừng cứng`

## Nội dung

| File | Nội dung |
|---|---|
| `skills/humanize-vietnamese/SKILL.md` | Quy trình, giọng mặc định, độ trang trọng, vùng miền |
| `references/ai-tells.md` | Danh sách dấu hiệu giọng AI trong tiếng Việt và cách sửa |
| `references/voice-script.md` | Quy tắc viết cho tai: số, ký hiệu, nhịp, hook |
| `references/examples.md` | Ví dụ trước / sau |
| `scripts/check_ai_tells.py` | Script quét dấu hiệu giọng AI, chỉ cần Python 3.8+, không cài thêm gì |

## Tự soát bằng script

Agent sẽ tự chạy script này ở bước soát lỗi. Bạn cũng chạy tay được:

```bash
python3 skills/humanize-vietnamese/scripts/check_ai_tells.py bai-viet.md
pbpaste | python3 skills/humanize-vietnamese/scripts/check_ai_tells.py        # soát chữ vừa copy
python3 skills/humanize-vietnamese/scripts/check_ai_tells.py --voice kich-ban.txt
```

Kết quả dạng `file:dòng:cột  [nhóm] "cụm bị bắt"  →  gợi ý sửa`. Mã thoát 0 là sạch, 1 là có chỗ cần xem, nên gắn vào CI hay pre-commit được. Thêm `--format json` nếu muốn xử lý tiếp.

Script chỉ bắt được cụm từ và dấu hiệu hình thức. Mấy lỗi cần hiểu ý như gom ba cho tròn hay đoạn nào cũng một khuôn thì vẫn phải tự đọc.

## Đóng góp

Thấy cụm từ nào "nghe là biết AI" mà chưa có trong `ai-tells.md` thì mở issue hoặc PR nhé. Nếu thêm vào script, nhớ thêm cả vào `ai-tells.md` cho hai bên khớp nhau, rồi chạy test:

```bash
python3 -m unittest discover -s tests
```

Test lấy `examples.md` làm chuẩn: bản "Trước" phải bị script bắt, bản "Sau" phải sạch. Thêm ví dụ mới cứ theo đúng khuôn `**Trước:**` / `**Sau:**` với đoạn trích bắt đầu bằng `>`.

## License

MIT
