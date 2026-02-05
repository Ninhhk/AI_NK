from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


MD_PATH = Path("docs/CHUONG_4_THIET_KE_TRIEN_KHAI.md")
OUT_CH4_TEX = Path("docs/CHUONG_4_THIET_KE_TRIEN_KHAI.tex")
OUT_APP_C_TEX = Path("docs/PHU_LUC_C.tex")


@dataclass
class ConvertState:
    fig_no: int = 10
    table_no: int = 1
    last_heading: str | None = None


_LATEX_SPECIALS = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}


def escape_latex(text: str) -> str:
    return "".join(_LATEX_SPECIALS.get(ch, ch) for ch in text)


def md_inline_to_latex(line: str) -> str:
    # Escape first, then do lightweight Markdown -> LaTeX for bold + inline code.
    s = escape_latex(line)
    # Inline code: `...`
    s = re.sub(r"`([^`]+)`", r"\\texttt{\1}", s)
    # Bold: **...**
    s = re.sub(r"\*\*([^*]+)\*\*", r"\\textbf{\1}", s)
    return s


def make_figure(state: ConvertState) -> list[str]:
    n = state.fig_no
    state.fig_no += 1
    return [
        r"\begin{figure}[H]",
        r"    \centering",
        rf"    \includegraphics{{Hinhve/Picture{n}.png}}",
        r"    \caption{Ví dụ biểu đồ phụ thuộc gói}",
        rf"    \label{{fig:Fig{n}}}",
        r"\end{figure}",
    ]


def is_table_row(line: str) -> bool:
    # Markdown pipe table row
    stripped = line.strip()
    return stripped.startswith("|") and stripped.endswith("|") and stripped.count("|") >= 3


def is_table_sep(line: str) -> bool:
    stripped = line.strip()
    if not stripped.startswith("|"):
        return False
    # separator row like |---|---|
    cells = [c.strip() for c in stripped.strip("|").split("|")]
    return all(re.fullmatch(r":?-{3,}:?", c or "---") for c in cells)


def parse_table(lines: list[str], start: int) -> tuple[list[list[str]], int]:
    rows: list[list[str]] = []
    i = start
    while i < len(lines) and is_table_row(lines[i]):
        rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
        i += 1
    return rows, i


def table_to_latex(state: ConvertState, rows: list[list[str]]) -> list[str]:
    if not rows:
        return []

    # Remove separator row if present as second row
    if len(rows) >= 2 and all(re.fullmatch(r":?-{3,}:?", c or "---") for c in rows[1]):
        header = rows[0]
        body = rows[2:]
    else:
        header = rows[0]
        body = rows[1:]

    col_count = max(len(header), *(len(r) for r in body))
    header = header + [""] * (col_count - len(header))
    body = [r + [""] * (col_count - len(r)) for r in body]

    spec = "|" + "|".join(["p{3.3cm}"] * col_count) + "|"

    caption = state.last_heading or "Bảng"
    label = f"tab:chuong4_{state.table_no}"
    state.table_no += 1

    out: list[str] = [
        r"\begin{table}[H]",
        r"\centering{}",
        rf"    \begin{{tabular}}{{{spec}}}",
        r"        \hline",
        "        " + " & ".join(r"\textbf{" + md_inline_to_latex(c) + "}" for c in header) + r" \\ \\hline",
    ]

    for row in body:
        out.append("        " + " & ".join(md_inline_to_latex(c) for c in row) + r" \\ \\hline")

    out += [
        r"    \end{tabular}",
        rf"    \caption{{{md_inline_to_latex(caption)}}}",
        rf"    \label{{{label}}}",
        r"\end{table}",
    ]
    return out


def convert_block(lines: list[str], state: ConvertState) -> list[str]:
    out: list[str] = []

    in_code = False
    code_fence_lang: str | None = None
    code_fence_ticks: int | None = None
    code_buf: list[str] = []

    in_itemize = False

    i = 0
    while i < len(lines):
        line = lines[i].rstrip("\n")

        # Fenced code blocks
        fence_match = re.match(r"^(`{3,})(.*)$", line.strip())
        if fence_match:
            ticks = len(fence_match.group(1))
            fence_tail = fence_match.group(2).strip().lower()
            if not in_code:
                in_code = True
                code_fence_ticks = ticks
                code_fence_lang = fence_tail
                code_buf = []
                i += 1
                continue
            if code_fence_ticks is not None and ticks >= code_fence_ticks:
                # close fence
                in_code = False
                block_text = "\n".join(code_buf)
                is_plantuml = (code_fence_lang == "plantuml") or ("@startuml" in block_text and "@enduml" in block_text)
                if in_itemize:
                    out.append(r"\end{itemize}")
                    in_itemize = False
                if is_plantuml:
                    out.extend(make_figure(state))
                else:
                    out.append(r"\begin{verbatim}")
                    out.extend(code_buf)
                    out.append(r"\end{verbatim}")
                code_fence_lang = None
                code_fence_ticks = None
                code_buf = []
                i += 1
                continue

        if in_code:
            code_buf.append(line)
            i += 1
            continue

        # Markdown headings -> LaTeX
        if line.startswith("#### "):
            title = line[5:].strip()
            state.last_heading = title
            if in_itemize:
                out.append(r"\end{itemize}")
                in_itemize = False
            out.append(rf"\subsubsection{{{md_inline_to_latex(title)}}}")
            out.append("")
            i += 1
            continue

        if line.startswith("### "):
            title = line[4:].strip()
            # Strip numbering like 4.2.1
            title = re.sub(r"^\d+(?:\.\d+)*\s+", "", title)
            state.last_heading = title
            if in_itemize:
                out.append(r"\end{itemize}")
                in_itemize = False
            out.append(rf"\subsection{{{md_inline_to_latex(title)}}}")
            out.append("")
            i += 1
            continue

        if line.startswith("## "):
            title = line[3:].strip()
            title = re.sub(r"^\d+(?:\.\d+)*\s+", "", title)
            state.last_heading = title
            if in_itemize:
                out.append(r"\end{itemize}")
                in_itemize = False
            # Keep template: do not create a standalone section for the chapter intro.
            if title.lower() == "mở đầu chương":
                out.append(r"\noindent\textbf{Mở đầu chương.}")
            else:
                out.append(rf"\section{{{md_inline_to_latex(title)}}}")
            out.append("")
            i += 1
            continue

        if line.startswith("# "):
            # drop top-level chapter title; template controls it
            i += 1
            continue

        # Horizontal rule
        if line.strip() in {"---", "***"}:
            if in_itemize:
                out.append(r"\end{itemize}")
                in_itemize = False
            out.append(r"\noindent\rule{\linewidth}{0.4pt}")
            out.append("")
            i += 1
            continue

        # Tables
        if is_table_row(line) and i + 1 < len(lines) and (is_table_sep(lines[i + 1]) or is_table_row(lines[i + 1])):
            if in_itemize:
                out.append(r"\end{itemize}")
                in_itemize = False
            rows, j = parse_table(lines, i)
            out.extend(table_to_latex(state, rows))
            out.append("")
            i = j
            continue

        # Bullet lists
        if line.lstrip().startswith("- "):
            if not in_itemize:
                out.append(r"\begin{itemize}")
                in_itemize = True
            item = line.lstrip()[2:].strip()
            out.append(rf"    \item {md_inline_to_latex(item)}")
            i += 1
            continue
        else:
            if in_itemize and line.strip() == "":
                # allow blank inside list without closing
                out.append("")
                i += 1
                continue
            if in_itemize and not line.lstrip().startswith("- ") and line.strip() != "":
                out.append(r"\end{itemize}")
                in_itemize = False

        # Blank lines
        if line.strip() == "":
            out.append("")
            i += 1
            continue

        # Default paragraph line
        out.append(md_inline_to_latex(line))
        i += 1

    if in_itemize:
        out.append(r"\end{itemize}")

    return out


def split_for_appendix(md_text: str) -> tuple[str, str]:
    # Heuristic: Move everything from '## 4.3' onwards into Appendix C.
    marker = re.search(r"^##\s+4\.3\s+Xây dựng ứng dụng\s*$", md_text, flags=re.MULTILINE)
    if not marker:
        return md_text, ""
    return md_text[: marker.start()], md_text[marker.start() :]


def write_chuong4(main_md: str, state: ConvertState) -> str:
    lines = main_md.splitlines()
    body = convert_block(lines, state)

    # Ensure we follow the required template section names.
    # We keep converted sections up to 4.2, then add template sections with pointers.
    # Also start figure numbering at 10.
    out: list[str] = [
        r"\documentclass[../DoAn.tex]{subfiles}",
        r"\begin{document}",
        "",
        r"\setcounter{figure}{9}",
        "",
    ]

    out.extend(body)

    # Add required template sections for the moved content.
    out += [
        "",
        r"\section{Xây dựng ứng dụng}",
        r"\subsection{Thư viện và công cụ sử dụng}",
        r"Nội dung chi tiết được chuyển sang Phụ lục C.",
        r"\subsection{Kết quả đạt được}",
        r"Nội dung chi tiết được chuyển sang Phụ lục C.",
        r"\subsection{Minh họa các chức năng chính}",
        r"Nội dung chi tiết được chuyển sang Phụ lục C.",
        "",
        r"\section{Kiểm thử}",
        r"Nội dung chi tiết được chuyển sang Phụ lục C.",
        "",
        r"\section{Triển khai}",
        r"Nội dung chi tiết được chuyển sang Phụ lục C.",
        "",
        r"\end{document}",
    ]
    return "\n".join(out) + "\n"


def write_appendix_c(appendix_md: str, state: ConvertState) -> str:
    lines = appendix_md.splitlines()
    body = convert_block(lines, state)

    out: list[str] = [
        r"\documentclass[../DoAn.tex]{subfiles}",
        r"\begin{document}",
        r"Nếu trong nội dung chính không đủ không gian cho các use case khác (ngoài các use case nghiệp vụ chính) thì đặc tả thêm cho các use case đó ở đây.",
        "",
    ]
    # Put overflow content here.
    out.extend(body)
    out += [
        "",
        r"\section{Đặc tả use case ``Thống kê tình hình mượn sách''}",
        r"\ldots",
        "",
        r"\section{Đặc tả use case ``Đăng ký làm thẻ mượn''}",
        r"\ldots",
        "",
        r"\end{document}",
    ]
    return "\n".join(out) + "\n"


def main() -> int:
    md_text = MD_PATH.read_text(encoding="utf-8")
    main_md, appendix_md = split_for_appendix(md_text)

    state = ConvertState(fig_no=10)

    OUT_CH4_TEX.write_text(write_chuong4(main_md, state), encoding="utf-8")
    if appendix_md.strip():
        OUT_APP_C_TEX.write_text(write_appendix_c(appendix_md, state), encoding="utf-8")
    else:
        # still create Appendix C file in requested template form
        OUT_APP_C_TEX.write_text(
            "\n".join(
                [
                    r"\documentclass[../DoAn.tex]{subfiles}",
                    r"\begin{document}",
                    r"Nếu trong nội dung chính không đủ không gian cho các use case khác (ngoài các use case nghiệp vụ chính) thì đặc tả thêm cho các use case đó ở đây.",
                    "",
                    r"\section{Đặc tả use case ``Thống kê tình hình mượn sách''}",
                    r"\ldots",
                    "",
                    r"\section{Đặc tả use case ``Đăng ký làm thẻ mượn''}",
                    r"\ldots",
                    "",
                    r"\end{document}",
                    "",
                ]
            ),
            encoding="utf-8",
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
