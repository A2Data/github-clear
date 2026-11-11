"""Render a review-only GitHub Clear website composition. No application changes."""

from pathlib import Path
from html import escape
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
W, H = 1600, 1080
parts = [
    f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
 <filter id="shadow" x="-20%" y="-20%" width="140%" height="160%"><feDropShadow dx="0" dy="4" stdDeviation="9" flood-color="#25243b" flood-opacity=".045"/></filter>
 <filter id="float" x="-40%" y="-40%" width="180%" height="200%"><feDropShadow dx="0" dy="16" stdDeviation="13" flood-color="#131422" flood-opacity=".24"/></filter>
 <filter id="small-shadow" x="-30%" y="-30%" width="170%" height="170%"><feDropShadow dx="0" dy="6" stdDeviation="7" flood-color="#716393" flood-opacity=".12"/></filter>
 <linearGradient id="folder-front" x1="0" y1="0" x2="0.9" y2="1"><stop stop-color="#e9e3ff"/><stop offset=".5" stop-color="#bcb1ed"/><stop offset="1" stop-color="#8d80bf"/></linearGradient>
 <linearGradient id="folder-side" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#8c7fc6"/><stop offset="1" stop-color="#524776"/></linearGradient>
 <linearGradient id="sheet" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#ffffff"/><stop offset="1" stop-color="#d9d7ed"/></linearGradient>
 <linearGradient id="folder-rim" x1="0" y1="0" x2="1" y2="0"><stop stop-color="#f7f4ff"/><stop offset="1" stop-color="#b8ace9"/></linearGradient>
</defs>
<rect width="1600" height="1080" fill="#f5f5f8"/>
'''
]


def raw(s):
    parts.append(s)


def rect(x, y, w, h, fill, r=0, stroke=None, extra=""):
    raw(
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}"'
        + (f' stroke="{stroke}"' if stroke else "")
        + f" {extra}/>"
    )


def line(x1, y1, x2, y2, color="#ececf1", width=1):
    raw(
        f'<path d="M{x1} {y1}H{x2}" stroke="{color}" stroke-width="{width}"/>'
        if y1 == y2
        else f'<path d="M{x1} {y1}L{x2} {y2}" fill="none" stroke="{color}" stroke-width="{width}"/>'
    )


def text(
    x,
    y,
    t,
    size=14,
    color="#2b2b38",
    weight=400,
    anchor="start",
    spacing=0,
    family=None,
):
    family = family or "'Hiragino Sans GB','Helvetica Neue',sans-serif"
    raw(
        f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" font-weight="{weight}" fill="{color}" text-anchor="{anchor}" letter-spacing="{spacing}">{escape(t)}</text>'
    )


def dot(x, y, r, color):
    raw(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}"/>')


def card(x, y, w, h, fill="#fff", stroke="#e8e8ef", r=16):
    rect(x, y, w, h, fill, r, stroke, 'filter="url(#shadow)"')


def pill(x, y, w, label, color="#777382", bg="#f0eef4"):
    rect(x, y, w, 25, bg, 6)
    text(x + w / 2, y + 17, label, 11, color, 500, "middle")


def arrow(x, y, color="#777382"):
    raw(
        f'<path d="M{x - 6} {y}h12m-4-4 4 4-4 4" fill="none" stroke="{color}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>'
    )


sheet = ET.parse(ROOT / "static/icons.svg").getroot()
icons = {
    e.attrib["id"]: "".join(ET.tostring(child, encoding="unicode") for child in e)
    for e in sheet
}


def icon(name, x, y, size=20, ink="#787586", wash="none", solid=None):
    s = icons.get(name, icons["repo"])
    s = re.sub(r"<(/?)ns\d+:", r"<\1", s)
    s = re.sub(r'\s+xmlns:ns\d+="[^"]*"', "", s)
    for a, b in [
        ("var(--icon-ink, currentColor)", ink),
        ("var(--icon-wash, transparent)", wash),
        ("var(--icon-solid, currentColor)", solid or ink),
        ("var(--icon-light, white)", "#ffffff"),
        ("currentColor", ink),
    ]:
        s = s.replace(a, b)
    raw(
        f'<svg x="{x}" y="{y}" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{ink}" stroke-width="1.65" stroke-linecap="round" stroke-linejoin="round">{s}</svg>'
    )


# Sidebar: preserve the existing brand mark, use a different surface hierarchy.
rect(0, 0, 220, H, "#20212b")
logo = (ROOT / "static/favicon.svg").read_text()
logo = re.sub(
    r"<svg[^>]*>",
    '<svg x="27" y="28" width="39" height="39" viewBox="0 0 64 64">',
    logo,
    count=1,
)
raw(logo)
text(78, 46, "GitHub Clear", 17, "#f8f8fc", 600, family="'Helvetica Neue',sans-serif")
text(
    79,
    65,
    "REPOSITORY WORKSPACE",
    8.5,
    "#8c8d9e",
    500,
    spacing=0.8,
    family="'Helvetica Neue',sans-serif",
)
text(28, 121, "工作空间", 10.5, "#7f8193", 500)
nav = [
    ("chart", "工作台", True),
    ("repo", "仓库管理", False),
    ("profile", "主页编辑", False),
    ("code", "Git 工具箱", False),
    ("settings", "设置", False),
]
for i, (symbol, label, active) in enumerate(nav):
    y = 143 + i * 54
    if active:
        rect(16, y, 188, 44, "#363442", 9)
        rect(16, y + 12, 3, 20, "#b7a5f8", 1.5)
    icon(
        symbol,
        31,
        y + 12,
        20,
        "#c8b9f9" if active else "#9798a9",
        "#494453" if active else "none",
    )
    text(
        64,
        y + 28,
        label,
        13,
        "#f2edff" if active else "#b9bac6",
        600 if active else 400,
    )
    if active:
        dot(185, y + 22, 2.5, "#b7a5f8")
line(28, 453, 192, 453, "#34353f")
text(28, 486, "快捷访问", 10.5, "#7f8193", 500)
icon("book", 31, 509, 18, "#9395a6")
text(63, 524, "使用指南", 12, "#b9bac6")
icon("github", 31, 548, 18, "#9395a6")
text(63, 563, "项目源码", 12, "#b9bac6")
arrow(183, 558, "#77798c")
rect(20, 844, 180, 112, "#292a35", 10, "#373843")
text(35, 871, "平台连接", 11, "#999baa")
icon("github", 35, 889, 16, "#dddde7")
text(60, 902, "GitHub", 12, "#d5d6e0", family="'Helvetica Neue',sans-serif")
dot(179, 897, 3, "#8fc7a4")
icon("gitee", 35, 922, 16, "#e77e85")
text(60, 935, "Gitee", 12, "#d5d6e0", family="'Helvetica Neue',sans-serif")
dot(179, 930, 3, "#8fc7a4")
line(24, 982, 196, 982, "#34353f")
dot(43, 1016, 17, "#494254")
text(43, 1021, "J", 15, "#e9dcff", 600, "middle", family="'Helvetica Neue',sans-serif")
text(72, 1012, "Jack", 13, "#e6e6ee", 500, family="'Helvetica Neue',sans-serif")
text(72, 1031, "个人工作空间", 10, "#86899a")
raw('<path d="m185 1013 4 4-4 4" fill="none" stroke="#858798" stroke-width="1.5"/>')

# Global chrome.
rect(220, 0, 1380, 76, "#ffffff")
line(220, 76, 1600, 76, "#e8e8ee")
text(260, 46, "工作空间", 12, "#8c8c99")
text(337, 46, "/", 12, "#c4c4cf")
text(362, 46, "概览", 12, "#444451", 500)
icon("book", 1318, 29, 17, "#777383")
text(1344, 43, "使用指南", 12, "#777383")
line(1423, 27, 1423, 50, "#e5e5ec")
text(1442, 43, "中", 12, "#4a455d", 600)
text(1475, 43, "EN", 10, "#a5a3b0", family="'Helvetica Neue',sans-serif")
dot(1539, 38, 17, "#eeebf4")
text(1539, 43, "J", 14, "#7e6c9d", 600, "middle", family="'Helvetica Neue',sans-serif")

# Page heading.
text(260, 132, "工作台", 32, "#2b2937", 600)
text(260, 161, "项目、主页和开发工具，都在这里。", 13, "#8a8798")
rect(1434, 112, 126, 38, "#7562ac", 8)
icon("repo", 1448, 121, 18, "#ffffff", "none")
text(1474, 137, "管理仓库", 12, "#fff", 500)

# Main repository card: the visual focus is confined to one useful module.
card(260, 194, 820, 312, "#272936", "#272936", 18)
icon("repo", 288, 220, 22, "#d1c9ed", "none")
text(321, 237, "仓库概览", 15, "#e9e6f5", 600)
rect(610, 219, 135, 28, "#343643", 7, "#464653")
dot(626, 233, 3, "#a0c5ad")
text(638, 237, "GitHub + Gitee", 11, "#c6c5d4", family="'Helvetica Neue',sans-serif")
text(288, 323, "42", 65, "#ffffff", 500, family="'Helvetica Neue',sans-serif")
text(384, 320, "个仓库", 14, "#a7a7ba")
text(289, 356, "把时间留给正在做的项目。", 13, "#a5a6b7")
for x, value, label in [(289, "18", "公开"), (405, "8", "私有"), (512, "16", "Fork")]:
    text(x, 397, value, 20, "#f1eefb", 500, family="'Helvetica Neue',sans-serif")
    text(x + 34, 396, label, 11, "#9c9dae")
line(379, 380, 379, 402, "#414250")
line(486, 380, 486, 402, "#414250")
rect(288, 439, 130, 39, "#f6f3ff", 8)
text(305, 463, "打开仓库", 12, "#49405e", 600)
arrow(397, 458, "#72608d")
text(442, 463, "查看协作仓库", 12, "#b7b4c8")
arrow(543, 458, "#b7b4c8")

# Procedural folded repository object: geometry, bevels and directional light.
raw("""<g transform="translate(765 264)">
 <ellipse cx="145" cy="182" rx="126" ry="14" fill="#171820" opacity=".42"/>
 <g transform="translate(28 -24) rotate(-10 110 90)">
  <rect x="39" y="7" width="161" height="127" rx="10" fill="#8175a6"/>
  <rect x="35" y="0" width="161" height="127" rx="10" fill="url(#sheet)"/>
  <path d="M58 28h88m-88 16h108m-108 16h69" stroke="#bfc1d5" stroke-width="5" stroke-linecap="round"/>
 </g>
 <g transform="translate(5 8) rotate(4 114 88)" filter="url(#float)">
  <path d="M14 37h69l20-20h117c9 0 14 5 14 14v132c0 9-5 14-14 14H14c-9 0-14-5-14-14V51c0-9 5-14 14-14Z" fill="url(#folder-side)"/>
  <path d="M3 31h69l20-20h117c9 0 14 5 14 14v132c0 9-5 14-14 14H3c-9 0-14-5-14-14V45c0-9 5-14 14-14Z" fill="url(#folder-front)"/>
  <path d="M-10 47c0-9 5-14 14-14h69l20-20h114c8 0 13 5 13 13" fill="none" stroke="url(#folder-rim)" stroke-width="2.2"/>
  <path d="M77 67v52m0-29h44V67" fill="none" stroke="#f7f4ff" stroke-width="5" stroke-linecap="round"/>
  <circle cx="77" cy="65" r="8" fill="#eeebfb"/>
  <circle cx="121" cy="65" r="8" fill="#eeebfb"/>
  <circle cx="77" cy="120" r="8" fill="#eeebfb"/>
  <path d="M155 137h36" stroke="#786aab" stroke-width="4" stroke-linecap="round" opacity=".5"/>
 </g>
 <g transform="translate(207 103) rotate(12)" filter="url(#small-shadow)"><rect width="46" height="46" rx="12" fill="#f1eff9"/><path d="m13 23 7 7 14-15" fill="none" stroke="#7d6b9d" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></g>
</g>""")

# Profile card: a real preview shape, not another identically sized metric.
card(1104, 194, 456, 312, "#eeeaf5", "#e6e0ef", 18)
icon("profile", 1132, 220, 22, "#8973a8", "#e2d8ee")
text(1165, 237, "我的主页", 15, "#524563", 600)
text(1133, 267, "用一个 README，介绍你正在创造的东西。", 11.5, "#9a8ca9")
raw("""<g transform="translate(1151 290) rotate(-3 180 63)" filter="url(#small-shadow)">
 <rect width="358" height="111" rx="10" fill="#ffffff" stroke="#e4ddeb"/>
 <path d="M0 21h358" stroke="#efedf3"/>
 <circle cx="14" cy="10.5" r="2.5" fill="#dbd5e5"/><circle cx="24" cy="10.5" r="2.5" fill="#dbd5e5"/><circle cx="34" cy="10.5" r="2.5" fill="#dbd5e5"/>
 <circle cx="43" cy="62" r="22" fill="#ede7f4"/>
 <text x="43" y="67" text-anchor="middle" font-family="Helvetica Neue" font-size="15" font-weight="500" fill="#8a73a6">JF</text>
 <text x="80" y="54" font-family="Helvetica Neue" font-size="15" font-weight="600" fill="#494153">Jack Feng</text>
 <text x="80" y="73" font-family="Helvetica Neue" font-size="10" fill="#a39aaa">Developer · Open source enthusiast</text>
 <rect x="80" y="85" width="47" height="15" rx="4" fill="#f2f0f6"/><rect x="133" y="85" width="66" height="15" rx="4" fill="#eff3f8"/><rect x="205" y="85" width="29" height="15" rx="4" fill="#edf5f0"/>
 <text x="103.5" y="96" text-anchor="middle" font-family="Helvetica Neue" font-size="8" fill="#89769d">Python</text><text x="166" y="96" text-anchor="middle" font-family="Helvetica Neue" font-size="8" fill="#6e8aa4">TypeScript</text><text x="219.5" y="96" text-anchor="middle" font-family="Helvetica Neue" font-size="8" fill="#65917a">Go</text>
</g>""")
rect(1132, 439, 163, 39, "#fff", 8, "#e2d9ed")
icon("profile", 1146, 450, 17, "#8c77a6", "none")
text(1172, 463, "编辑我的主页", 12, "#6b587e", 600)
arrow(1274, 458, "#9b8aaa")
text(1335, 463, "实时预览", 11, "#9f92ac")
dot(1323, 459, 3, "#ac9cbe")

# Main project area and two secondary modules.
card(260, 532, 820, 414)
text(288, 570, "最近更新的仓库", 17, "#393543", 600)
text(978, 569, "查看全部", 11, "#948ca3")
arrow(1051, 565, "#948ca3")
for x, label, active in [
    (288, "全部", True),
    (353, "GitHub", False),
    (436, "Gitee", False),
]:
    if active:
        rect(x - 9, 588, 52, 28, "#efebf6", 6)
    text(x, 607, label, 11, "#7d679f" if active else "#9b98a6", 500)
line(288, 630, 1052, 630)
rows = [
    (
        "repo",
        "github-clear",
        "GitHub / Gitee 仓库管理与主页编辑",
        "Python",
        "12",
        "2 小时前",
        "#e9edf7",
        "#7186b0",
    ),
    (
        "book",
        "developer-notes",
        "开发记录、读书笔记和常用脚本",
        "Markdown",
        "8",
        "昨天",
        "#f5efe4",
        "#b39b6e",
    ),
    (
        "profile",
        "readme-studio",
        "A little corner of the open-source world.",
        "TypeScript",
        "24",
        "3 天前",
        "#f0eaf6",
        "#a48bb6",
    ),
    (
        "code",
        "toolkit",
        "让日常开发更轻松的一组小工具",
        "Go",
        "6",
        "5 天前",
        "#eaf3ef",
        "#7aa18d",
    ),
]
for i, (sym, name, desc, lang, stars, time, bg, fg) in enumerate(rows):
    y = 650 + i * 69
    rect(288, y + 2, 36, 36, bg, 9)
    icon(sym, 296, y + 10, 20, fg, "none")
    text(339, y + 16, name, 13, "#55515f", 500, family="'Helvetica Neue',sans-serif")
    text(339, y + 36, desc, 10.5, "#928b9d")
    dot(772, y + 14, 3, fg)
    text(782, y + 18, lang, 10, "#8c8396", family="'Helvetica Neue',sans-serif")
    icon("star", 895, y + 6, 12, "#aaa4b2", "none")
    text(913, y + 17, stars, 10, "#9b95a5", family="'Helvetica Neue',sans-serif")
    text(1051, y + 18, time, 10, "#928b9d", anchor="end")
    if i < 3:
        line(288, y + 54, 1052, y + 54, "#f0eef3")

card(1104, 532, 456, 244)
text(1132, 570, "开发者工具", 17, "#393543", 600)
pill(1440, 549, 92, "日常开发", "#9a8da8", "#f3eff7")
rect(1132, 591, 400, 42, "#f7f6f9", 8, "#eeecf2")
icon("search", 1146, 603, 17, "#a69dae", "none")
text(1173, 618, "查找 Git 命令，例如 merge、remote…", 10.5, "#ada5b6")
for x, sym, title, sub in [
    (1132, "code", "Git 速查", "102 条命令"),
    (1271, "key", "SSH 密钥", "查看与管理"),
    (1410, "people", "多账号", "完整配置指南"),
]:
    rect(x, 653, 122, 96, "#ffffff", 10, "#eeebf2")
    icon(sym, x + 13, 666, 24, "#90829f", "#f3eff7")
    text(x + 13, 711, title, 11.5, "#696071", 500)
    text(x + 13, 731, sub, 9.5, "#94899f")

card(1104, 800, 456, 146)
text(1132, 837, "账户连接", 15, "#494252", 600)
pill(1436, 818, 96, "2 / 2 已配置", "#789b87", "#eff6f1")
for x, sym, label in [(1132, "github", "GitHub"), (1344, "gitee", "Gitee")]:
    icon(sym, x, 867, 24, "#766e83", "none")
    text(x + 37, 878, label, 12, "#777080", 500, family="'Helvetica Neue',sans-serif")
    dot(x + 39, 897, 2.5, "#8db49d")
    text(x + 48, 901, "Token 已配置", 9.5, "#958b9f")
line(1320, 862, 1320, 912, "#eeebf2")

# Footer makes the distinction between proposal and real account data explicit.
text(260, 991, "GitHub Clear", 11, "#9e96aa", 500, family="'Helvetica Neue',sans-serif")
text(260, 1014, "设计提案 01  ·  展示数据为示例", 10, "#9c92a7")
text(
    1560,
    991,
    "有层次的卡片  /  定制立体图形  /  操作驱动的动效",
    11,
    "#9f96aa",
    anchor="end",
)
text(
    1560,
    1014,
    "WEBSITE CONCEPT — NOT THE LIVE INTERFACE",
    8,
    "#b7b1bf",
    anchor="end",
    spacing=1,
    family="'Helvetica Neue',sans-serif",
)
raw("</svg>")
(OUT / "workspace-concept.svg").write_text("\n".join(parts), encoding="utf-8")
print(OUT / "workspace-concept.svg")
