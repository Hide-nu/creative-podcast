#!/usr/bin/env python3
"""episodes.json + podcast.json から docs/feed.xml と docs/index.html を作る。
放送日（JST）が今日以前の回だけを載せる（未来の回は音声を置いておいても公開されない）。
使い方: python3 tools/build_feed.py [--all] [--today YYYY-MM-DD]
"""
import json, os, sys, html, datetime as dt
from email.utils import format_datetime
from xml.sax.saxutils import escape
import xml.dom.minidom

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JST = dt.timezone(dt.timedelta(hours=9))
cfg = json.load(open(os.path.join(ROOT, "podcast.json")))
eps = json.load(open(os.path.join(ROOT, "episodes.json")))

bad = [k for k, v in cfg.items() if isinstance(v, str) and "TODO" in v]
if bad:
    sys.exit(f"podcast.json の {bad} がまだ TODO のままです")
base = cfg["base_url"].rstrip("/") + "/"

today = dt.datetime.now(JST).date()
if "--today" in sys.argv:
    today = dt.date.fromisoformat(sys.argv[sys.argv.index("--today") + 1])
show_all = "--all" in sys.argv
live = [e for e in eps if show_all or dt.date.fromisoformat(e["date"]) <= today]
live.sort(key=lambda e: e["date"], reverse=True)

def hms(s):
    return f"{s//3600:02d}:{s%3600//60:02d}:{s%60:02d}"

def desc(e):
    parts = [e["summary"]]
    if e.get("award"):
        parts.append("評価：" + e["award"])
    parts.append("音声：VOICEVOX:玄野武宏")
    return "\n\n".join(p for p in parts if p)

items = []
for e in live:
    d = dt.date.fromisoformat(e["date"])
    pub = dt.datetime(d.year, d.month, d.day, cfg.get("release_hour_jst", 5), 0, tzinfo=JST)
    size = os.path.getsize(os.path.join(ROOT, "docs", e["file"]))
    items.append(f"""  <item>
    <title>{escape(e['title'])}</title>
    <description>{escape(desc(e))}</description>
    <itunes:summary>{escape(desc(e))}</itunes:summary>
    <enclosure url="{escape(base + e['file'])}" length="{size}" type="audio/mpeg"/>
    <guid isPermaLink="false">asa-pod-{e['date']}</guid>
    <pubDate>{format_datetime(pub)}</pubDate>
    <itunes:duration>{hms(e['duration'])}</itunes:duration>
    <itunes:episodeType>full</itunes:episodeType>
    <itunes:explicit>{'true' if cfg['explicit'] else 'false'}</itunes:explicit>
  </item>""")

last = format_datetime(dt.datetime.now(JST))
feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
  <title>{escape(cfg['title'])}</title>
  <link>{escape(base)}</link>
  <atom:link href="{escape(base + 'feed.xml')}" rel="self" type="application/rss+xml"/>
  <language>{cfg['language']}</language>
  <description>{escape(cfg['description'])}</description>
  <itunes:summary>{escape(cfg['description'])}</itunes:summary>
  <itunes:author>{escape(cfg['author'])}</itunes:author>
  <itunes:owner><itunes:name>{escape(cfg['author'])}</itunes:name><itunes:email>{escape(cfg['owner_email'])}</itunes:email></itunes:owner>
  <itunes:image href="{escape(base + 'cover.jpg')}"/>
  <image><url>{escape(base + 'cover.jpg')}</url><title>{escape(cfg['title'])}</title><link>{escape(base)}</link></image>
  <itunes:category text="{escape(cfg['category'])}"><itunes:category text="{escape(cfg['subcategory'])}"/></itunes:category>
  <itunes:explicit>{'true' if cfg['explicit'] else 'false'}</itunes:explicit>
  <itunes:type>episodic</itunes:type>
  <lastBuildDate>{last}</lastBuildDate>
{chr(10).join(items)}
</channel>
</rss>
"""
xml.dom.minidom.parseString(feed.encode())  # 壊れていれば例外で止まる
open(os.path.join(ROOT, "docs", "feed.xml"), "w").write(feed)

rows = "\n".join(f'<li><b>{html.escape(e["title"])}</b><br><audio controls preload="none" src="{html.escape(e["file"])}"></audio></li>' for e in live)
page = f"""<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(cfg['title'])}</title><link rel="alternate" type="application/rss+xml" href="feed.xml">
<style>body{{font-family:system-ui,sans-serif;max-width:720px;margin:2rem auto;padding:0 16px;line-height:1.6}}li{{margin:1rem 0;list-style:none}}audio{{width:100%}}img{{width:160px;border-radius:12px}}</style></head>
<body><img src="cover.jpg" alt=""><h1>{html.escape(cfg['title'])}</h1><p>{html.escape(cfg['description']).replace(chr(10),'<br>')}</p>
<p><a href="feed.xml">RSSフィード</a></p><ul>{rows}</ul></body></html>
"""
open(os.path.join(ROOT, "docs", "index.html"), "w").write(page)
print(f"feed.xml: {len(live)} 本（{today} 時点）")
