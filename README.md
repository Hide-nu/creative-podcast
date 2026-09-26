# アイデアの分岐点

毎朝1本、人の行動を変えたプロダクト・キャンペーン・人物を、歴史と行動科学の理論で読み解く約18分の日本語ポッドキャスト。
台本はAIとWeb調査で書き、音声は VOICEVOX（玄野武宏）で合成しています。

音声：VOICEVOX:玄野武宏

## 仕組み

```
Notion「ネタ帳」(題材・放送日)
   │  pipeline/BRIEF.md に沿って台本を調査・執筆（1本 6,500〜7,000字）
   ▼
scripts/*.txt ・ meta/*.json
   │  pipeline/synth.py + worker.sh（VOICEVOX / 玄野武宏 style 11）
   ▼
64kbps MP3 ──► docs/ep/YYYY-MM-DD.mp3 ──► tools/build_feed.py ──► docs/feed.xml
   │                                           ▲
   │                                           └─ GitHub Actions が毎朝 04:50 JST に実行し、
   │                                              放送日を迎えた回だけをフィードに載せる
   ▼
32kbps MP3 ──► Notion ネタ帳の各ページ先頭に音声として貼り付け（pipeline/send.sh）

docs/ を GitHub Pages で公開 → feed.xml を Spotify for Creators に登録 → Spotify / Apple などで配信
```

## フォルダ

| パス | 中身 |
|---|---|
| `podcast.json` | 番組名・名義・連絡先メール・公開URLなどの設定 |
| `episodes.json` | 全エピソードの一覧（放送日、タイトル、説明、長さ、Notionページ） |
| `docs/` | GitHub Pages の公開物。`ep/`（音声）、`feed.xml`、`index.html`、`cover.jpg` |
| `scripts/`, `meta/` | 台本本文と、出典・受賞歴・事実確認メモ |
| `pipeline/` | 台本ブリーフ、Notion書き込みブリーフ、VOICEVOX導入・合成・並列ワーカー、Notionアップロード |
| `tools/` | `build_feed.py`（フィード生成）、`make_cover.py`（3000×3000のカバー）、`add_episode.py`（回の追加） |
| `.github/workflows/feed.yml` | 毎朝の自動公開 |

## よく使うコマンド

```bash
python3 tools/make_cover.py                 # 番組名からカバー画像を作る
python3 tools/build_feed.py                 # 今日までの回でフィードを作る
python3 tools/build_feed.py --all           # 未来の回も含めて確認用に作る（公開前に戻すこと）
python3 tools/add_episode.py 1104_水_xxx.mp3 2026-11-04 "題材名" --script scripts/1104_水_xxx.txt
```

## 新しい回の作り方

1. Notion「ネタ帳」に題材と放送日の行を用意する
2. `pipeline/BRIEF.md` のルールで台本を書き `scripts/` と `meta/` に置く
3. Linux 環境で `pipeline/setup_voicevox.sh` → `pipeline/worker.sh 1`（コア数だけ並列）で合成
4. `tools/add_episode.py` で `docs/ep/` と `episodes.json` に追加して push
5. 放送日の朝、Actions がフィードに載せ、Spotify に届く

## 容量のめやす

64kbps・約18分で1本約8.7MB、週7本で約60MB。GitHub Pages の公開サイトは1GBまでなので、およそ3か月で上限に近づく。
近づいたら、古い回を消す／音声だけ Cloudflare R2 などに移す／Spotify for Creators のホスティングに切り替える、のどれかを選ぶ。

## クレジットと権利

- 音声は VOICEVOX の「玄野武宏」。公開時は「VOICEVOX:玄野武宏」の表記が必要（番組説明と各回の説明に自動で入る）。
- 台本は各回の出典（`meta/*.json` の sources）をもとに書いたオリジナル。
