#!/usr/bin/env python3
"""新しい回を追加する: 音声を docs/ep/YYYY-MM-DD.mp3 にコピーし、episodes.json に1件足す。
使い方: python3 tools/add_episode.py 元.mp3 2026-11-04 "題材名" --summary "説明文" [--award "受賞歴"] [--script scripts/xxx.txt] [--page NotionページID]
台本(--script)を渡すと、summary を省略したとき台本の2〜4行目を説明文に使う。
"""
import argparse, json, os, shutil, subprocess, datetime as dt
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ap = argparse.ArgumentParser()
ap.add_argument("mp3"); ap.add_argument("date"); ap.add_argument("name")
ap.add_argument("--summary", default=""); ap.add_argument("--award", default="")
ap.add_argument("--script"); ap.add_argument("--page", default="")
a = ap.parse_args()
d = dt.date.fromisoformat(a.date)
wd = "月火水木金土日"[d.weekday()]
dst = f"ep/{a.date}.mp3"
shutil.copy(a.mp3, os.path.join(ROOT, "docs", dst))
dur = round(float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", a.mp3]).decode()))
summary = a.summary
if not summary and a.script:
    lines = [l.strip() for l in open(a.script) if l.strip()]
    summary = "".join(lines[1:4])
p = os.path.join(ROOT, "episodes.json")
eps = [e for e in json.load(open(p)) if e["date"] != a.date]
eps.append({"date": a.date, "weekday": wd, "title": f"{d.month}/{d.day}（{wd}）{a.name}", "name": a.name,
            "file": dst, "duration": dur, "summary": summary, "award": a.award, "notion_page_id": a.page,
            "script": a.script, "source_name": os.path.basename(a.mp3)[:-4]})
eps.sort(key=lambda e: e["date"])
json.dump(eps, open(p, "w"), ensure_ascii=False, indent=1)
print("added", a.date, a.name, dur, "s")
