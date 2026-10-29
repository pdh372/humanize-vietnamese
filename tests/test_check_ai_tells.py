"""Test cho skills/humanize-vietnamese/scripts/check_ai_tells.py.

Chạy:  python3 -m unittest discover -s tests
"""

import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "humanize-vietnamese"
SCRIPT = SKILL / "scripts" / "check_ai_tells.py"
EXAMPLES = SKILL / "references" / "examples.md"
STYLES = SKILL / "references" / "styles.md"

sys.path.insert(0, str(SCRIPT.parent))
import check_ai_tells  # noqa: E402


def example_blocks():
    """Trả về list (tiêu đề mục, 'truoc'|'sau', đoạn trích) từ examples.md."""
    blocks = []
    heading = ""
    kind = None
    buf = []

    def flush():
        if kind and buf:
            blocks.append((heading, kind, "\n".join(buf)))

    for line in EXAMPLES.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            flush()
            heading, kind, buf = line[3:].strip(), None, []
        elif re.match(r"\*\*Trước", line):
            flush()
            kind, buf = "truoc", []
        elif re.match(r"\*\*Sau", line):
            flush()
            kind, buf = "sau", []
        elif line.startswith(">") and kind:
            buf.append(re.sub(r"^>\s?", "", line))
        elif line.strip() and buf:
            flush()
            kind, buf = None, []
    flush()
    return blocks


class ExamplesAgreeWithChecker(unittest.TestCase):
    def test_examples_file_has_pairs(self):
        blocks = example_blocks()
        self.assertGreaterEqual(sum(k == "truoc" for _, k, _ in blocks), 9)
        self.assertEqual(sum(k == "truoc" for _, k, _ in blocks), sum(k == "sau" for _, k, _ in blocks))

    def test_before_is_flagged(self):
        for heading, kind, text in example_blocks():
            if kind != "truoc":
                continue
            with self.subTest(heading=heading):
                self.assertTrue(check_ai_tells.check(text), f"Không bắt được lỗi nào trong bản Trước: {heading}")

    def test_after_is_clean(self):
        for heading, kind, text in example_blocks():
            if kind != "sau":
                continue
            voice = "voice" in heading.lower()
            with self.subTest(heading=heading):
                findings = check_ai_tells.check(text, voice=voice)
                self.assertEqual([], [(f.group, f.match) for f in findings], f"Bản Sau vẫn bị bắt lỗi: {heading}")


class StylesAgreeWithChecker(unittest.TestCase):
    def sections(self):
        """Trả về list (tiêu đề, ví dụ trong blockquote) từ styles.md."""
        out = []
        for part in re.split(r"^## (?=\d+\.)", STYLES.read_text(encoding="utf-8"), flags=re.MULTILINE)[1:]:
            heading = part.splitlines()[0].strip()
            quote = "\n".join(re.sub(r"^>\s?", "", l) for l in part.splitlines() if l.startswith(">"))
            out.append((heading, quote))
        return out

    def test_ten_styles_each_with_example(self):
        sections = self.sections()
        self.assertEqual(10, len(sections))
        for heading, quote in sections:
            with self.subTest(heading=heading):
                self.assertTrue(quote.strip(), f"Thiếu ví dụ: {heading}")

    def test_examples_are_clean(self):
        for heading, quote in self.sections():
            with self.subTest(heading=heading):
                findings = check_ai_tells.check(quote)
                self.assertEqual([], [(f.group, f.match) for f in findings], f"Ví dụ vẫn bị bắt lỗi: {heading}")


class Rules(unittest.TestCase):
    def groups(self, text, **kw):
        return [(f.group, f.match.lower()) for f in check_ai_tells.check(text, **kw)]

    def assertFlags(self, text, phrase, **kw):
        hits = [m for _, m in self.groups(text, **kw)]
        self.assertTrue(any(phrase in m for m in hits), f"{phrase!r} không bị bắt trong {text!r}: {hits}")

    def test_known_tells(self):
        cases = {
            "Trong thời đại công nghệ 4.0, ai cũng cần học AI.": "trong thời đại",
            "App được phát triển bởi Google.": "được phát triển bởi",
            "Máy sở hữu camera 50MP.": "sở hữu",
            "Bên em tiến hành cài đặt ngay.": "tiến hành",
            "Nó không chỉ nhanh mà còn rẻ.": "không chỉ nhanh mà còn",
            "Chắc chắn rồi! Đây là bản sửa.": "chắc chắn rồi",
            "Kết quả thực sự vô cùng ấn tượng.": "thực sự vô cùng",
            "Pin tốt — sạc nhanh.": "—",
            "Hy vọng bài viết hữu ích với bạn.": "hy vọng bài viết",
            "Khum biết nữa.": "khum",
            "Như chúng ta đã biết, nước chiếm 70% cơ thể.": "như chúng ta đã biết",
            "Ngày nay, mạng xã hội ngày càng phổ biến.": "ngày nay,",
            "Thị trường thương mại điện tử đang bùng nổ.": "bùng nổ",
            "Xin chân thành cảm ơn quý khách đã tin tưởng!": "xin chân thành cảm ơn",
            "Trong bối cảnh kinh tế khó khăn, nhiều công ty cắt giảm nhân sự.": "trong bối cảnh",
            "Đối với tôi, gia đình là quan trọng nhất.": "đối với tôi",
            "Đây không phải là một chiếc điện thoại, mà là một người bạn.": "mà là",
            "Vậy bí quyết là gì? Câu trả lời là: kiên trì.": "câu trả lời là:",
            "Tuyệt vời! Mình sẽ giúp bạn viết lại.": "tuyệt vời!",
            "Rất vui được hỗ trợ bạn!": "rất vui được hỗ trợ",
            "Món này đỉnh của chóp luôn.": "đỉnh của chóp",
        }
        for text, phrase in cases.items():
            with self.subTest(text=text):
                self.assertFlags(text, phrase)

    def test_sentence_start_only(self):
        self.assertFlags("Việc này để mai làm.", "việc")
        self.assertFalse(self.groups("Mai mình làm nốt việc này."))

    def test_new_rules_keep_normal_text(self):
        # "Tuyệt vời," trong văn châm biếm và "mà nằm ở" không phải lỗi
        self.assertFalse(self.groups("Tuyệt vời, deploy xong là cả team được nghỉ."))
        self.assertFalse(self.groups("Vấn đề không nằm ở database, mà nằm ở API."))
        self.assertFalse(self.groups("Với mình, gia đình là trên hết."))

    def test_word_boundaries(self):
        # "ấn tượng" nằm trong từ khác hoặc "việc" giữa câu không được bắt nhầm
        self.assertFalse(self.groups("Công việc hôm nay xong sớm."))
        self.assertFalse(self.groups("Chúng tôi gửi hàng trong ngày."))

    def test_unicode_nfd_input(self):
        import unicodedata
        self.assertFlags(unicodedata.normalize("NFD", "Máy sở hữu camera tốt."), "sở hữu")

    def test_stacked_connectors(self):
        text = "Máy nhẹ. Ngoài ra, pin lâu. Bên cạnh đó, giá rẻ."
        self.assertEqual(2, sum(g == check_ai_tells.STRUCTURE for g, _ in self.groups(text)))
        self.assertFalse(self.groups("Máy nhẹ. Ngoài ra, pin lâu."))

    def test_particle_overuse(self):
        text = "Mua đi nha. Rẻ lắm nè. Giao nhanh nha. Còn ít á."
        self.assertIn(check_ai_tells.OVERDONE, [g for g, _ in self.groups(text)])
        self.assertFalse(self.groups("Mua đi nha. Rẻ lắm. Giao trong ngày. Còn ít thôi."))

    def test_title_case_heading(self):
        self.assertFlags("# Cách Viết Caption Hay\n", "cách viết caption hay")
        self.assertFalse(self.groups("# Cách viết caption hay\n"))

    def test_code_is_ignored(self):
        self.assertFalse(self.groups("Chạy lệnh `tiến hành --sở-hữu`.\n\n```\nTrong thời đại số\n```\n"))

    def test_voice_mode(self):
        text = "Giảm 50% cho 20/10, vd áo thun."
        self.assertFalse(self.groups(text))
        hits = [m for _, m in self.groups(text, voice=True)]
        for phrase in ("50%", "20/10", "vd"):
            self.assertIn(phrase, hits)

    def test_line_and_column(self):
        f = check_ai_tells.check("Dòng một.\nMáy sở hữu pin to.")[0]
        self.assertEqual((2, 5), (f.line, f.col))


class Cli(unittest.TestCase):
    def run_cli(self, stdin, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *args], input=stdin.encode("utf-8"),
                              capture_output=True)

    def test_exit_codes(self):
        self.assertEqual(0, self.run_cli("Pin xài được hai ngày.").returncode)
        self.assertEqual(1, self.run_cli("Máy sở hữu pin trâu.").returncode)
        self.assertEqual(2, subprocess.run([sys.executable, str(SCRIPT), "/khong/co/file.txt"],
                                           capture_output=True).returncode)

    def test_json_output(self):
        import json
        out = self.run_cli("Máy sở hữu pin trâu.", "--format", "json").stdout.decode("utf-8")
        data = json.loads(out)
        self.assertEqual("sở hữu", data[0]["match"])


if __name__ == "__main__":
    unittest.main()
