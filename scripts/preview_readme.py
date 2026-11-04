"""Render a GitHub-like, self-contained preview of a README file.

Usage:
    python scripts/preview_readme.py README.fa.md preview-fa.html
"""

from __future__ import annotations

import base64
import mimetypes
import re
import sys
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parents[1]

CSS = """
:root { color-scheme: light; }
* { box-sizing: border-box; }
body {
  margin: 0; background: #f6f8fa; color: #1f2328;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial,
    "Vazirmatn", "IRANSans", Tahoma, sans-serif;
  font-size: 16px; line-height: 1.65;
}
.topbar {
  background: #24292f; color: #fff; padding: 12px 20px; font-size: 14px;
  display: flex; align-items: center; gap: 10px; flex-wrap: wrap;
}
.topbar .repo { font-weight: 600; }
.topbar .pill {
  border: 1px solid #57606a; border-radius: 999px; padding: 1px 10px;
  font-size: 12px; color: #d0d7de;
}
.wrap { max-width: 1012px; margin: 24px auto 64px; padding: 0 16px; }
.filebox { background: #fff; border: 1px solid #d0d7de; border-radius: 8px; overflow: hidden; }
.filehead {
  background: #f6f8fa; border-bottom: 1px solid #d0d7de; padding: 10px 16px;
  font-size: 13px; color: #57606a; display: flex; gap: 8px; align-items: center;
}
.markdown { padding: 32px 40px 48px; }
.markdown h1, .markdown h2, .markdown h3 {
  margin: 26px 0 14px; font-weight: 600; line-height: 1.3;
}
.markdown h1 { font-size: 2em; padding-bottom: .3em; border-bottom: 1px solid #d8dee4; }
.markdown h2 { font-size: 1.5em; padding-bottom: .3em; border-bottom: 1px solid #d8dee4; }
.markdown h3 { font-size: 1.2em; }
.markdown p { margin: 0 0 16px; }
.markdown a { color: #0969da; text-decoration: none; }
.markdown a:hover { text-decoration: underline; }
.markdown img { max-width: 100%; border-radius: 6px; }
.markdown hr { height: 1px; background: #d8dee4; border: 0; margin: 26px 0; }
.markdown ul { padding-inline-start: 2em; margin: 0 0 16px; }
.markdown li { margin: 4px 0; }
.markdown code {
  background: rgba(129,139,152,.16); border-radius: 6px; padding: .18em .4em;
  font-size: 85%; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  direction: ltr; unicode-bidi: embed;
}
.markdown pre {
  background: #f6f8fa; border-radius: 8px; padding: 16px; overflow: auto;
  direction: ltr; text-align: left; margin: 0 0 16px;
}
.markdown pre code { background: none; padding: 0; font-size: 85%; }
.markdown blockquote {
  margin: 0 0 16px; padding: 0 1em; color: #57606a;
  border-inline-start: .25em solid #d0d7de;
}
.markdown table {
  border-collapse: collapse; width: 100%; margin: 0 0 16px;
  display: block; overflow: auto;
}
.markdown th, .markdown td { border: 1px solid #d0d7de; padding: 8px 13px; }
.markdown th { background: #f6f8fa; font-weight: 600; }
.markdown tr:nth-child(2n) td { background: #f6f8fa; }
.markdown [dir="rtl"] { text-align: right; }
.markdown [dir="rtl"] table { direction: rtl; }
.markdown [align="center"] { text-align: center; }
.note {
  max-width: 1012px; margin: 0 auto 16px; padding: 12px 16px; font-size: 13px;
  background: #fff8c5; border: 1px solid #d4a72c66; border-radius: 8px; color: #4d2d00;
}
"""


def embed_images(html: str) -> str:
    def repl(match: re.Match[str]) -> str:
        src = match.group(1)
        if src.startswith(("http://", "https://", "data:")):
            # Remote badges cannot load offline; swap in a small inline placeholder.
            if src.startswith("data:"):
                return match.group(0)
            return (
                'src="data:image/svg+xml;base64,'
                + base64.b64encode(
                    b'<svg xmlns="http://www.w3.org/2000/svg" width="96" height="20">'
                    b'<rect width="96" height="20" rx="3" fill="#57606a"/>'
                    b'<text x="48" y="14" font-size="11" fill="#fff" text-anchor="middle"'
                    b' font-family="sans-serif">badge</text></svg>'
                ).decode()
                + '"'
            )
        path = ROOT / src
        if not path.exists():
            return match.group(0)
        mime = mimetypes.guess_type(path.name)[0] or "image/png"
        data = base64.b64encode(path.read_bytes()).decode()
        return f'src="data:{mime};base64,{data}"'

    return re.sub(r'src="([^"]+)"', repl, html)


def main() -> None:
    src_name = sys.argv[1] if len(sys.argv) > 1 else "README.fa.md"
    out_name = sys.argv[2] if len(sys.argv) > 2 else "preview-fa.html"
    text = (ROOT / src_name).read_text(encoding="utf-8")
    # GitHub parses markdown inside block-level HTML separated by blank lines.
    # Python-Markdown needs an explicit hint to do the same; add it for preview only.
    text = re.sub(r"<div(?![^>]*markdown=)([^>]*)>", r'<div\1 markdown="1">', text)
    body = markdown.markdown(
        text,
        extensions=["tables", "fenced_code", "md_in_html", "sane_lists", "attr_list"],
    )
    body = embed_images(body)
    lang = "fa" if ".fa." in src_name else "en"
    html = f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{src_name} — preview</title>
<style>{CSS}</style>
</head>
<body>
<div class="topbar">
  <span class="repo">WMiliya / pytest-fixture-lens</span>
  <span class="pill">Public</span>
  <span class="pill">{src_name}</span>
</div>
<div class="wrap">
  <div class="note">GitHub-style preview. Badges are placeholders here;
  on GitHub they load normally.</div>
  <div class="filebox">
    <div class="filehead">📄 {src_name}</div>
    <div class="markdown">{body}</div>
  </div>
</div>
</body>
</html>
"""
    (ROOT / out_name).write_text(html, encoding="utf-8")
    print(f"wrote {out_name} ({len(html) // 1024} KB)")


if __name__ == "__main__":
    main()
