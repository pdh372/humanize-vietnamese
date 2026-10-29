---
name: humanize-vietnamese
description: Viết hoặc viết lại tiếng Việt cho tự nhiên như người thật nói, bỏ "giọng AI" (sáo rỗng, dịch từ tiếng Anh, câu đều đều, trang trọng gượng). Dùng khi người dùng viết/sửa văn tiếng Việt và muốn nó mượt, có hồn, "chơn chu", "giọng người", "đỡ AI", hoặc khi soạn caption, bài đăng Facebook/TikTok, kịch bản voice, tin nhắn, email, mô tả sản phẩm bằng tiếng Việt. Also use for any request to humanize, de-AI, or make Vietnamese text sound natural.
---

# Humanize Vietnamese

Viết tiếng Việt như một người Việt thật đang nói hoặc viết cho người khác đọc. Giữ nguyên ý và dữ kiện, chỉ đổi cách nói.

## Quy trình

1. **Chốt bối cảnh trước khi viết.** Ai đọc/nghe, đăng ở đâu, giọng gì, xưng hô gì. Người dùng không nói thì dùng mặc định bên dưới, không hỏi lại trừ khi thật sự mơ hồ (ví dụ không biết là gửi sếp hay gửi bạn).
2. **Viết hoặc viết lại.** Giữ đúng số liệu, tên riêng, ý chính. Không bịa trải nghiệm cá nhân ("mình xài rồi", "hôm qua mình thử") nếu người dùng không cung cấp.
3. **Soát lỗi giọng AI** theo [references/ai-tells.md](references/ai-tells.md). Sửa hết những gì khớp. Nếu chạy được lệnh, lưu bản nháp ra file tạm rồi chạy `python3 <thư mục skill này>/scripts/check_ai_tells.py <file>` (thêm `--voice` nếu là văn đọc thành tiếng) để quét nhanh. Script chỉ gợi ý: chỗ nào nó bắt mà đúng ý người dùng (ví dụ họ muốn giữ "chúng ta") thì giữ. Script sạch chưa có nghĩa là xong, vẫn làm bước 4.
4. **Đọc thầm một lượt.** Câu nào đọc vấp, câu nào ngoài đời không ai nói vậy thì viết lại.
5. **Trả kết quả.** Chỉ đưa văn bản cuối. Không giải thích đã sửa gì trừ khi được hỏi. Người dùng xin nhiều phiên bản thì đưa 2-3 bản khác giọng rõ rệt, không phải 3 bản na ná nhau.

## Mặc định

| Mục | Mặc định khi người dùng không nói |
|---|---|
| Xưng hô | mình - bạn |
| Giọng | thân thiện, gọn, hơi đời thường |
| Vùng miền | trung tính, dùng được cả Bắc lẫn Nam |
| Tiếng Anh | giữ thuật ngữ dân trong nghề hay nói (prompt, deploy, bug, livestream), không chen tiếng Anh vô cớ |

Văn bản gốc đã có giọng riêng (xưng hô, vùng miền, độ trang trọng) thì giữ giọng đó, đừng kéo về mặc định.

## Viết sao cho ra giọng người

**Nói thẳng, nói cụ thể.** Người thật nói "pin dùng được hai ngày", không nói "thời lượng pin ấn tượng". Có số thì đưa số, có tên thì gọi tên, có ví dụ thì kể ví dụ.

**Câu dài ngắn xen kẽ.** Ba câu dài liền nhau là mệt. Chen một câu cụt. Vậy thôi.

**Động từ thật thay cho động từ rỗng.** "thực hiện việc kiểm tra" thành "kiểm tra". "tiến hành cài đặt" thành "cài". "mang lại trải nghiệm tốt" thành "xài sướng" hoặc nói rõ tốt chỗ nào.

**Có thái độ.** Người thật dám khen, dám chê, dám nói "cái này hơi dở". Văn không có quan điểm nào là văn AI.

**Tiểu từ tình thái có liều lượng.** nha, nhé, nè, á, đó, luôn, mà, chứ, thôi, đâu. Một hai cái mỗi đoạn là đủ. Câu nào cũng "nha" thì lại thành giả.

**Từ láy và thành ngữ đúng chỗ.** lằng nhằng, lòng vòng, gọn gàng, lặt vặt, chỉn chu, "tiền nào của nấy", "đừng bỏ hết trứng vào một giỏ". Một hai cái cho có hồn, nhét nhiều thì thành văn mẫu.

**Mở bằng thứ người đọc quan tâm.** Bỏ hết câu dạo đầu kiểu "Trong thời đại ngày nay". Vào thẳng vấn đề, hoặc mở bằng một câu hỏi, một con số, một tình huống.

**Kết khi hết ý.** Không cần đoạn "Tóm lại" lặp lại những gì vừa nói. Không chúc "Hy vọng bài viết hữu ích".

## Độ trang trọng

Tự nhiên không có nghĩa là suồng sã. Chọn đúng mức theo người nhận:

| Mức | Dùng cho | Xưng hô | Đặc điểm |
|---|---|---|---|
| Thân | bạn bè, nhóm chat, caption cá nhân | tao - mày, tui - bà, mình - bạn | câu cụt, tiểu từ nhiều hơn, được dùng từ lóng nhẹ |
| Đời thường | bài đăng mạng xã hội, video, blog | mình - bạn, mình - mọi người | mặc định của skill này |
| Lịch sự | khách hàng, đồng nghiệp, email công việc | em - anh/chị, mình - bạn, bên em - anh/chị | đủ chủ vị, có "ạ" khi cần, vẫn ngắn gọn và cụ thể |
| Trang trọng | công văn, thông báo chính thức | chúng tôi - quý khách | đúng chuẩn, nhưng vẫn bỏ sáo ngữ và câu bị động thừa |

Ở mức nào cũng bỏ lỗi giọng AI. Văn trang trọng của người thật vẫn rõ ràng và cụ thể.

## Vùng miền

Chỉ dùng khi người dùng yêu cầu hoặc văn gốc đã có. Dùng nhẹ tay, vài từ là đủ ra chất, đừng biến thành giọng hài nhại.

- **Bắc:** nhé, nhỉ, thế, đấy, ạ, vâng, bố mẹ, cái gì
- **Nam:** nha, nè, hen, vậy, đó, ha, tui, ba má, cái gì vậy, dzữ chưa
- **Trung:** chỉ dùng khi người dùng xin rõ và biết cách dùng (mô, tê, răng, rứa), vì dùng sai rất lộ

## Kịch bản voice / video ngắn

Khi văn bản sẽ được đọc thành tiếng (TTS, lồng tiếng, TikTok, Reels, YouTube Shorts), đọc thêm [references/voice-script.md](references/voice-script.md).

## Đừng sửa quá tay

Làm "người" quá cũng lộ. Các lỗi hay gặp khi cố humanize:

- Nhét tiểu từ vào mọi câu ("nha", "nè", "á" liên tục)
- Từ lóng Gen Z không ai xin ("khum", "xỉu up xỉu down", "keo lỳ") trong văn không phải để giới trẻ đọc
- Thêm câu cảm thán và emoji cho "vui"
- Bịa kỷ niệm, trải nghiệm để có vẻ chân thật
- Đổi luôn ý hoặc bỏ dữ kiện của người dùng cho câu mượt hơn

Xem ví dụ trước/sau ở [references/examples.md](references/examples.md).
