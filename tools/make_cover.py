#!/usr/bin/env python3
"""podcast.json の番組名から 3000x3000 のカバー画像 docs/cover.jpg を作る（Spotify/Apple の要件）。"""
import json, os
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cfg = json.load(open(os.path.join(ROOT, "podcast.json")))
title = cfg["title"]
FONTS = ["/System/Library/Fonts/ヒラギノ角ゴシック W7.ttc", "/System/Library/Fonts/Hiragino Sans GB.ttc",
         "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc", "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"]
font = next(f for f in FONTS if os.path.exists(f))
S = 3000
img = Image.new("RGB", (S, S))
d = ImageDraw.Draw(img)
for y in range(S):  # 夜明けのグラデーション
    t = y / S
    d.line([(0, y), (S, y)], fill=(int(20 + 230 * t), int(30 + 140 * t), int(70 + 40 * t)))
d.ellipse([S*0.3, S*0.62, S*0.7, S*1.02], fill=(255, 214, 120))
n = -(-len(title) // 8)  # 1行8字までで均等に分ける
step = -(-len(title) // n)
lines = cfg.get("cover_lines") or [title[i:i + step] for i in range(0, len(title), step)]  # 改行位置は podcast.json の cover_lines で指定できる
size = int(S * 0.8 / max(len(l) for l in lines))
size = min(size, 460)
f = ImageFont.truetype(font, size)
y = S * 0.18
for l in lines:
    w = d.textlength(l, font=f)
    d.text(((S - w) / 2, y), l, font=f, fill=(255, 255, 255))
    y += size * 1.25
img.save(os.path.join(ROOT, "docs", "cover.jpg"), quality=88)
print("docs/cover.jpg", os.path.getsize(os.path.join(ROOT, "docs", "cover.jpg")) // 1024, "KB")
