#!/usr/bin/env python3
"""Soát "giọng AI" trong văn bản tiếng Việt.

Quét theo danh sách trong references/ai-tells.md và in ra những chỗ nghi vấn.
Kết quả chỉ là gợi ý: người viết vẫn quyết định sửa hay giữ.

    python3 check_ai_tells.py bai-viet.md
    cat caption.txt | python3 check_ai_tells.py
    python3 check_ai_tells.py --voice kich-ban.txt     # thêm luật cho văn đọc thành tiếng
    python3 check_ai_tells.py --format json bai.md

Mã thoát: 0 nếu sạch, 1 nếu có chỗ cần xem, 2 nếu lỗi đọc file.
Chỉ dùng thư viện chuẩn, chạy được với Python 3.8 trở lên.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
import unicodedata
from dataclasses import asdict, dataclass
from typing import Iterable, List, Optional, Sequence, Tuple

W = r"(?<![\w])"  # đầu từ
E = r"(?![\w])"  # cuối từ
# Đầu dòng (kể cả sau dấu ">" của blockquote) hoặc ngay sau dấu kết câu.
SENT_START = r"(?:^[ \t]*(?:>[ \t]*)?|(?<=[.!?…:][ \t]))"


@dataclass
class Finding:
    file: str
    line: int
    col: int
    group: str
    match: str
    hint: str


@dataclass
class Rule:
    group: str
    pattern: "re.Pattern[str]"
    hint: str


def _words(*phrases: str) -> str:
    return "(?P<hit>" + W + "(?:" + "|".join(phrases) + ")" + E + ")"


def _sentence_start(*phrases: str) -> str:
    return SENT_START + _words(*phrases)


def _compile(regex: str) -> "re.Pattern[str]":
    return re.compile(regex, re.IGNORECASE | re.MULTILINE)


def _rule(group: str, regex: str, hint: str) -> Rule:
    return Rule(group, _compile(regex), hint)


OPENER = "mở/kết sáo"
CLICHE = "từ sáo"
TRANSLATED = "văn dịch"
STRUCTURE = "cấu trúc AI"
FORMAT = "trình bày"
CHATBOT = "giọng chatbot"
OVERDONE = "sửa quá tay"
VOICE = "văn đọc"

RULES: List[Rule] = [
    # 1. Câu dạo đầu và kết sáo rỗng
    _rule(OPENER, _words(r"trong (?:thời đại|kỷ nguyên)(?: [\w.]+){1,4}", r"kỷ nguyên số", r"xã hội hiện đại ngày nay"),
          "Xóa câu dạo đầu, vào thẳng vấn đề"),
    _rule(OPENER, _words(r"bạn (?:đã |có )?(?:bao giờ|từng) tự hỏi"), "Hỏi thẳng câu hỏi thật, hoặc xóa"),
    _rule(OPENER, _words(r"(?:hãy )?cùng (?:nhau )?(?:tìm hiểu|khám phá)"), "Xóa"),
    _rule(OPENER, _sentence_start(r"tóm lại", r"nói tóm lại", r"nhìn chung", r"có thể nói", r"tổng kết lại"),
          "Đoạn tóm tắt không thêm ý mới thì xóa"),
    _rule(OPENER, _words(r"h[yi] vọng (?:bài viết|những chia sẻ|thông tin|báo cáo)", r"chúc (?:bạn|các bạn) thành công"),
          "Xóa, hoặc thay bằng một lời kêu gọi cụ thể"),
    _rule(OPENER, _words(r"như (?:chúng ta|mọi người|các bạn) đã biết", r"không có gì (?:ngạc nhiên|lạ) khi",
                         r"trong bài viết này", r"cảm ơn (?:bạn|các bạn|mọi người) đã (?:dành thời gian )?(?:đọc|theo dõi)",
                         r"(?:hãy )?để lại bình luận(?: bên dưới| phía dưới)?"),
          "Câu dẫn hoặc câu kết khuôn mẫu. Xóa, hoặc hỏi một câu cụ thể"),
    _rule(OPENER, _sentence_start(r"ngày nay,"), "Mở bài văn mẫu. Xóa, vào thẳng vấn đề"),
    _rule(OPENER, _words(r"tương lai đầy hứa hẹn", r"(?:sẽ )?(?:còn )?phát triển hơn nữa"),
          "Nêu kế hoạch, mốc thời gian cụ thể, hoặc xóa"),
    # 2. Từ ngữ sáo, phóng đại
    _rule(CLICHE, _words(r"đóng vai trò (?:vô cùng |cực kỳ |rất )?(?:quan trọng|then chốt)", r"không thể thiếu",
                         r"là chìa khóa", r"mở ra cánh cửa", r"bước ngoặt", r"đòn bẩy", r"bức tranh toàn cảnh",
                         r"nâng tầm", r"kiến tạo", r"lan tỏa", r"chạm đến trái tim", r"trọn vẹn",
                         r"đột phá", r"vượt trội", r"hoàn hảo", r"đáng kinh ngạc", r"ấn tượng",
                         r"hệ sinh thái", r"giá trị cốt lõi", r"giải pháp toàn diện", r"tối ưu hóa",
                         r"đầy tiềm năng", r"đầy màu sắc", r"đa dạng và phong phú", r"như vũ bão",
                         r"sang trọng(?:,| và) tinh tế", r"hành trình (?:dài|đầy)", r"thật ý nghĩa",
                         r"nhằm nâng cao", r"góp phần (?:quan trọng|không nhỏ)", r"trong thời gian sớm nhất",
                         r"trải nghiệm (?:tuyệt vời|không tốt|người dùng tốt)"),
          "Thay bằng từ thường hoặc nói rõ cụ thể là gì"),
    _rule(CLICHE, _words(r"vô vàn", r"đỉnh cao", r"bùng nổ", r"bứt phá", r"cách mạng hóa", r"mang tính cách mạng",
                         r"tiên phong", r"khẳng định vị thế", r"chinh phục", r"không ngừng nỗ lực", r"cầu nối",
                         r"nền tảng vững chắc", r"liền mạch", r"sứ mệnh", r"chất lượng hàng đầu",
                         r"tạo (?:ra )?sự khác biệt"),
          "Từ to mà rỗng. Thay bằng từ thường hoặc nói rõ cụ thể là gì"),
    _rule(CLICHE, _words(r"(?:xin )?trân trọng thông báo", r"rất mong nhận được sự (?:quan tâm|ủng hộ|hợp tác)",
                         r"(?:xin )?chân thành cảm ơn", r"sự hài lòng của khách hàng", r"nhu cầu ngày càng cao"),
          "Văn công sở khuôn mẫu. Nói thẳng, hoặc nêu cam kết cụ thể"),
    _rule(CLICHE, _words(r"(?:thực sự|vô cùng|cực kỳ|hoàn toàn|rất) (?:vô cùng|cực kỳ|rất|hoàn toàn|thực sự)"),
          "Chồng từ nhấn mạnh. Giữ một từ, hoặc đưa số liệu"),
    # 3. Văn dịch từ tiếng Anh
    _rule(TRANSLATED, _words(r"được(?: \w+){1,3} bởi"), "Bị động kiểu tiếng Anh. Viết: do X làm / X làm ra"),
    _rule(TRANSLATED, _sentence_start(r"việc"), "Bỏ \"việc\" đầu câu, dùng thẳng động từ"),
    _rule(TRANSLATED, _words(r"trong việc"), "Thường bỏ được \"trong việc\""),
    _rule(TRANSLATED, _words(r"một cách \w+"), "\"một cách nhanh chóng\" thành \"nhanh\""),
    _rule(TRANSLATED, _words(r"thực hiện", r"tiến hành"), "Dùng thẳng động từ chính"),
    _rule(TRANSLATED, _words(r"sở hữu", r"mang (?:lại|đến|tới)"), "Viết \"có\", \"cho\", \"giúp\""),
    _rule(TRANSLATED, _words(r"là một trong những"), "Nói rõ đứng thứ mấy, hoặc bỏ \"một trong những\""),
    _rule(TRANSLATED, _words(r"khi (?:nói|nhắc) (?:đến|tới|về)"), "Viết \"Về X thì...\" hoặc \"X thì...\""),
    _rule(TRANSLATED, _words(r"điều (?:này|đó) (?:cho thấy|có nghĩa là|giúp)"),
          "Viết \"Vậy là...\", \"Nghĩa là...\" hoặc xóa"),
    _rule(TRANSLATED, _words(r"có khả năng"), "Viết \"được\", \"có thể\", hoặc động từ trần"),
    _rule(TRANSLATED, _words(r"trở nên"), "Thường bỏ được \"trở nên\""),
    _rule(TRANSLATED, _words(r"giảm thiểu"), "Viết \"giảm\", \"bớt\""),
    _rule(TRANSLATED, _words(r"đây là lý do (?:tại sao|vì sao)"), "Viết \"Vì vậy\", \"Thế nên\""),
    _rule(TRANSLATED, _words(r"có (?:một số|nhiều) cách để"), "Có mấy cách thì nói luôn số"),
    _rule(TRANSLATED, _words(r"ở mức độ cao"), "Viết \"rất\", \"nhiều\""),
    _rule(TRANSLATED, _sentence_start(r"đối với (?:tôi|mình)"), "Viết \"Với mình\""),
    _rule(TRANSLATED, _words(r"với sự (?:hỗ trợ|giúp đỡ) của"), "Viết \"nhờ\", \"có X giúp\""),
    _rule(TRANSLATED, _words(r"trong bối cảnh"), "Viết \"khi\", \"lúc\""),
    _rule(TRANSLATED, _words(r"nhằm mục đích"), "Viết \"để\""),
    _rule(TRANSLATED, _words(r"sự (?:phát triển|thay đổi|gia tăng|xuất hiện|ra đời) của"),
          "Danh từ hóa kiểu tiếng Anh. Viết \"X phát triển\""),
    _rule(TRANSLATED, _words(r"đóng góp vào"), "Viết \"giúp\""),
    # 4. Cấu trúc kiểu AI
    _rule(STRUCTURE, "(?P<hit>" + W + r"không (?:chỉ|những)" + E + r"[^.!?\n]{0,120}?" + W + r"mà còn" + E + ")",
          "Nói thẳng hai ý, hoặc chọn ý mạnh hơn"),
    _rule(STRUCTURE, _words(r"điều đáng chú ý là", r"một điều thú vị là", r"điều quan trọng là", r"đáng chú ý hơn"),
          "Nói luôn điều đó"),
    _rule(STRUCTURE, _words(r"cần lưu ý (?:rằng|là)", r"điều quan trọng cần nhớ", r"không thể phủ nhận"),
          "Câu dẫn thừa. Nói luôn điều đó"),
    _rule(STRUCTURE, _sentence_start(r"nói cách khác", r"hãy tưởng tượng"), "Bỏ, hoặc kể tình huống thật"),
    _rule(STRUCTURE, "(?P<hit>" + W + r"không phải (?:là )?[^.!?\n]{1,60}?, mà là" + E + ")",
          "\"Không phải X, mà là Y\" dùng hoài thành kịch. Nói thẳng Y"),
    _rule(STRUCTURE, _words(r"câu trả lời là:"), "Giật gân bằng dấu hai chấm. Nói thẳng câu trả lời"),
    _rule(STRUCTURE, _words(r"có thể phần nào", r"phần nào giúp"), "Rào đón quá đà. Viết \"giúp được\""),
    # 5. Trình bày
    _rule(FORMAT, r"(?P<hit>—|(?<=\s)–(?=\s))", "Gạch dài giữa câu. Thay bằng dấu phẩy hoặc ngắt câu"),
    _rule(FORMAT, r"^[ \t]*(?:[-*][ \t]*)?(?P<hit>\*\*[^*\n]{1,30}:\*\*)(?=[ \t]*[^\s*])", "Nhãn in đậm đầu dòng. Chuyển thành câu văn"),
    # 6. Giọng chatbot
    _rule(CHATBOT, _words(r"chắc chắn rồi", r"câu hỏi rất hay", r"bạn nói hoàn toàn đúng", r"dưới đây là",
                          r"sau đây (?:mình|tôi|chúng ta|chúng tôi) sẽ", r"đừng ngần ngại", r"xin chào (?:các bạn|mọi người)"),
          "Xóa"),
    _rule(CHATBOT, _sentence_start(r"tuyệt vời!"), "Xóa"),
    _rule(CHATBOT, _words(r"(?:mình|tôi) hiểu cảm giác của bạn", r"h[yi] vọng điều (?:này|đó) (?:giúp ích|hữu ích|có ích)",
                          r"nếu (?:bạn|anh chị|quý khách) có bất kỳ (?:câu hỏi|thắc mắc)",
                          r"rất vui được (?:hỗ trợ|giúp đỡ|giúp)"),
          "Câu xã giao của chatbot. Xóa, hoặc nói cụ thể"),
    _rule(CHATBOT, _words(r"chúng ta"), "Đang nói một chiều với người đọc thì đừng xưng \"chúng ta\""),
    # Sửa quá tay
    _rule(OVERDONE, _words(r"khum", r"xỉu up xỉu down", r"keo lỳ", r"keo lì", r"u là trời", r"đỉnh của chóp", r"mãi mận"),
          "Từ lóng Gen Z không ai xin. Bỏ, trừ khi người đọc là giới trẻ"),
]

VOICE_RULES: List[Rule] = [
    _rule(VOICE, r"(?P<hit>\d+(?:[.,/:]\d+)*\s*%?)", "Viết số thành chữ để TTS đọc đúng"),
    _rule(VOICE, r"(?P<hit>[%&→/$€₫+=])", "Ký hiệu. Viết ra đúng như cách nói"),
    _rule(VOICE, _words(r"vd", r"ko", r"k", r"tp", r"sp", r"đc", r"dc", r"vs"), "Không viết tắt trong bản đọc"),
    _rule(VOICE, r"(?P<hit>\*\*|^[ \t]*[-*•][ \t])", "Bỏ in đậm và gạch đầu dòng trong bản đọc"),
    _rule(VOICE, r"(?P<hit>\([^)\n]*\))", "Bỏ ngoặc, viết thành câu"),
]

CONNECTORS = _compile(_sentence_start(r"bên cạnh đó", r"ngoài ra", r"hơn thế nữa", r"hơn nữa", r"đặc biệt",
                                      r"không những thế", r"thêm vào đó", r"song song với đó"))
PARTICLES = _compile(_words(r"nha", r"nhé", r"nè", r"á", r"hen", r"nhỉ"))
EMOJI_LINE_START = _compile(r"^[ \t]*(?:[-*>][ \t]*)?(?P<hit>[\U0001F300-\U0001FAFF\u2600-\u27BF])")
HEADING = _compile(r"^#{1,6}[ \t]+(?P<hit>.+)$")
SENTENCE_SPLIT = re.compile(r"(?<=[.!?…])\s+")
FENCE = re.compile(r"^\s*```")


def _strip_code(text: str) -> str:
    """Thay code block và inline code bằng khoảng trắng, giữ nguyên vị trí dòng/cột."""
    out_lines = []
    in_fence = False
    for line in text.split("\n"):
        if FENCE.match(line):
            in_fence = not in_fence
            out_lines.append(" " * len(line))
        elif in_fence:
            out_lines.append(" " * len(line))
        else:
            out_lines.append(re.sub(r"`[^`\n]*`", lambda m: " " * len(m.group(0)), line))
    return "\n".join(out_lines)


def _pos(text: str, offset: int) -> Tuple[int, int]:
    line = text.count("\n", 0, offset) + 1
    col = offset - (text.rfind("\n", 0, offset) + 1) + 1
    return line, col


def _paragraphs(text: str) -> Iterable[Tuple[int, str]]:
    for m in re.finditer(r"(?:[^\n]*\S[^\n]*(?:\n|$))+", text):
        yield m.start(), m.group(0)


def _sentences(paragraph: str) -> List[str]:
    flat = re.sub(r"^[ \t]*>[ \t]?", "", paragraph, flags=re.MULTILINE).replace("\n", " ")
    return [s for s in SENTENCE_SPLIT.split(flat.strip()) if s]


def check(text: str, name: str = "<stdin>", voice: bool = False) -> List[Finding]:
    """Trả về danh sách chỗ nghi là giọng AI trong `text`."""
    text = unicodedata.normalize("NFC", text)
    scan = _strip_code(text)
    findings: List[Finding] = []

    def add(offset: int, group: str, match: str, hint: str) -> None:
        line, col = _pos(text, offset)
        findings.append(Finding(name, line, col, group, match.strip(), hint))

    def add_match(m: "re.Match[str]", group: str, hint: str) -> None:
        add(m.start("hit"), group, m.group("hit"), hint)

    for rule in RULES + (VOICE_RULES if voice else []):
        for m in rule.pattern.finditer(scan):
            add_match(m, rule.group, rule.hint)

    connectors = list(CONNECTORS.finditer(scan))
    if len(connectors) >= 2:
        for m in connectors:
            add_match(m, STRUCTURE, "Từ nối dồn dập. Nối bằng \"Mà\", \"Còn\", hoặc bỏ")

    for m in EMOJI_LINE_START.finditer(scan):
        add_match(m, FORMAT, "Emoji đầu dòng. Bỏ, trừ khi là caption và người dùng muốn")

    for m in HEADING.finditer(scan):
        words = [w for w in re.findall(r"[^\W\d_]+", m.group("hit")) if len(w) > 1]
        if len(words) >= 3 and all(w[0].isupper() for w in words):
            add_match(m, FORMAT, "Tiêu đề viết hoa mọi chữ. Chỉ viết hoa chữ đầu và tên riêng")

    curly = re.search(r"[“”]", scan)
    if curly and '"' in scan:
        add(curly.start(), FORMAT, curly.group(0), "Ngoặc kép cong lẫn ngoặc thẳng. Dùng một kiểu")

    for offset, para in _paragraphs(scan):
        sentences = _sentences(para)
        lead = para.lstrip(" \t>")
        start = offset + len(para) - len(lead)
        if len(sentences) >= 3:
            with_particle = sum(1 for s in sentences if PARTICLES.search(s))
            if with_particle / len(sentences) > 0.6:
                add(start, OVERDONE, sentences[0][:40] + "…",
                    "Câu nào cũng có tiểu từ (nha, nhé, nè...). Một hai cái mỗi đoạn là đủ")
        if len(sentences) >= 4:
            lengths = [len(s.split()) for s in sentences]
            mean = statistics.mean(lengths)
            if mean >= 8 and statistics.pstdev(lengths) / mean < 0.2:
                add(start, STRUCTURE, sentences[0][:40] + "…", "Câu dài đều đều. Chen một câu ngắn")

    findings.sort(key=lambda f: (f.line, f.col))
    return findings


def _read(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Soát dấu hiệu giọng AI trong văn bản tiếng Việt.")
    parser.add_argument("files", nargs="*", default=["-"], help="file cần soát, bỏ trống hoặc - để đọc stdin")
    parser.add_argument("--voice", action="store_true", help="thêm luật cho văn đọc thành tiếng (TTS, video)")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    for stream in (sys.stdin, sys.stdout):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")

    all_findings: List[Finding] = []
    for path in args.files:
        try:
            text = _read(path)
        except OSError as exc:
            print(f"không đọc được {path}: {exc}", file=sys.stderr)
            return 2
        all_findings.extend(check(text, "<stdin>" if path == "-" else path, voice=args.voice))

    if args.format == "json":
        print(json.dumps([asdict(f) for f in all_findings], ensure_ascii=False, indent=2))
    else:
        for f in all_findings:
            print(f"{f.file}:{f.line}:{f.col}  [{f.group}] \"{f.match}\"  →  {f.hint}")
        print(f"{len(all_findings)} chỗ cần xem" if all_findings else "Không thấy dấu hiệu giọng AI.")
    return 1 if all_findings else 0


if __name__ == "__main__":
    sys.exit(main())
