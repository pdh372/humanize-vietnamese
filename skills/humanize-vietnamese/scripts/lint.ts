#!/usr/bin/env node
// Flag mechanical "AI tells" in Vietnamese text. Rules mirror references/ai-tells.md.
//
//   node --experimental-strip-types lint.ts file.txt
//   echo "text" | node --experimental-strip-types lint.ts
//
// Exit code 1 when something is flagged, 0 when clean.
import { readFileSync } from "node:fs";

interface Rule {
  id: string;
  re: RegExp;
  hint: string;
}

const rules: Rule[] = [
  { id: "opener", re: /trong (thời đại|kỷ nguyên)|xã hội hiện đại|bạn đã bao giờ tự hỏi|hãy cùng (nhau )?(tìm hiểu|khám phá)/gi, hint: "Câu dạo đầu sáo rỗng. Xóa, vào thẳng vấn đề" },
  { id: "closer", re: /\b(tóm lại|nói tóm lại|nhìn chung)\b|hy vọng bài viết|chúc bạn thành công|đừng ngần ngại/gi, hint: "Câu kết sáo. Xóa hoặc thay bằng lời kêu gọi cụ thể" },
  { id: "not-only", re: /không (chỉ|những)[^.!?\n]{0,80}mà còn/gi, hint: "\"Không chỉ... mà còn...\". Nói thẳng hai ý" },
  { id: "connector", re: /(^|[.!?]\s+|\n)(bên cạnh đó|ngoài ra|hơn thế nữa|không những thế|đặc biệt),/gi, hint: "Từ nối dồn dập. Dùng \"Mà\", \"Còn\", hoặc bỏ" },
  { id: "cliche", re: /đóng vai trò (quan trọng|then chốt)|không thể thiếu|nâng tầm|kiến tạo|giải pháp toàn diện|hệ sinh thái|giá trị cốt lõi|tối ưu hóa|đột phá|vượt trội|ấn tượng/gi, hint: "Từ phóng đại. Thay bằng số liệu hoặc ý cụ thể" },
  { id: "translationese", re: /một cách (nhanh chóng|hiệu quả|dễ dàng)|(thực hiện|tiến hành) (việc )?\p{L}+|được phát triển bởi|sở hữu|một trong những/giu, hint: "Văn dịch từ tiếng Anh. Dùng động từ trần" },
  { id: "nominalization", re: /\b(việc|sự) \p{L}+ (là|sẽ|đóng)|điều (quan trọng|đáng chú ý) (cần lưu ý )?là|một điều thú vị là/giu, hint: "Danh từ hóa / rào đón. Nói thẳng điều đó" },
  { id: "chatbot", re: /chắc chắn rồi!|câu hỏi (rất )?hay|dưới đây là|sau đây (mình|tôi) sẽ/gi, hint: "Giọng chatbot. Xóa" },
  { id: "em-dash", re: /—/g, hint: "Gạch dài giữa câu. Dùng dấu phẩy hoặc ngắt câu" },
  { id: "lead-emoji", re: /^\s*[-*]?\s*[🚀✨💡👉🔥✅📌🎯]/gmu, hint: "Emoji đầu dòng. Bỏ, trừ caption mạng xã hội khi người dùng muốn" },
  { id: "bold-label", re: /^\s*[-*]\s+\*\*[^*]+:\*\*/gm, hint: "Gạch đầu dòng nhãn đậm. Chuyển thành câu văn" },
  { id: "title-case", re: /^#{1,6}\s+(\p{Lu}\p{Ll}*\s+){3,}\p{Lu}\p{Ll}*\s*$/gmu, hint: "Viết Hoa Mọi Chữ trong tiêu đề. Chỉ hoa chữ đầu và tên riêng" },
];

const input = process.argv[2] ? readFileSync(process.argv[2], "utf8") : readFileSync(0, "utf8");

// Skip fenced code blocks so we never flag code.
const text = input.replace(/```[\s\S]*?```/g, (block) => block.replace(/[^\n]/g, " "));

let hits = 0;
for (const { id, re, hint } of rules) {
  for (const m of text.matchAll(re)) {
    const idx = m.index ?? 0;
    const line = text.slice(0, idx).split("\n").length;
    console.log(`line ${line} [${id}] "${m[0].trim()}" -> ${hint}`);
    hits++;
  }
}

// Curly quotes only matter when mixed with straight quotes.
if (/[“”]/.test(text) && /"/.test(text)) {
  console.log("[curly-quotes] ngoặc kép cong lẫn thẳng -> thống nhất một kiểu");
  hits++;
}

console.log(hits ? `\n${hits} issue(s)` : "clean");
process.exit(hits ? 1 : 0);
