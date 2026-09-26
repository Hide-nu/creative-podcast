# Claude Code への引き継ぎ

このリポジトリは、Notion「ネタ帳」の台本から作った朝のポッドキャスト（2026/9/25〜11/3の40本、音声作成済み）を、
GitHub Pages で RSS 配信し、Spotify に載せるためのもの。README.md に全体像がある。

## 決まっていること
- 公開番組として Spotify に載せる（ユーザー了承済み）。
- フィードの連絡先は、個人の Gmail ではなく**番組用に新しく作るアドレス**を使う。
- 番組名は「アイデアの分岐点」（2026/9/26 決定。旧仮称「朝のポッドキャスト」）。
- 音声のクレジット「VOICEVOX:玄野武宏」は必須。`podcast.json` の description と各回の説明に入れてあるので消さない。

## やること（上から順に）

1. **ユーザーに聞いて `podcast.json` の TODO を埋める**
   - `title`（番組名。カバーの改行位置を指定したければ `"cover_lines": ["1行目", "2行目"]` を足す）
   - `author`（公開される名義。本名でなくてよい）
   - `owner_email`（番組用アドレス。Spotify の所有確認コードがここに届く。フィード上で公開される）
   - `base_url` は手順2で決まる `https://<user>.github.io/<repo>/`（末尾スラッシュ付き）
2. **GitHub にリポジトリを作る**（Public。Pages 無料枠のため）
   ```bash
   git init -b main && git add -A && git commit -m "Initial import: 40 episodes and pipeline"
   gh repo create <repo> --public --source . --push
   gh api -X POST repos/<user>/<repo>/pages -f "source[branch]=main" -f "source[path]=/docs"
   ```
   - 音声が約300MBあるので push に数分かかる。1ファイルは最大約9MBなので LFS は不要。
   - Settings → Actions → General → Workflow permissions が「Read and write」になっているか確認（毎朝の自動公開が push するため）。
3. **カバーとフィードを作って push**
   ```bash
   python3 tools/make_cover.py      # 生成後に画像を開いて見た目をユーザーに確認してもらう
   python3 tools/build_feed.py      # 今日までの回だけが載る
   git add -A && git commit -m "Set show info, cover and feed" && git push
   ```
4. **公開を確認**：数分後に `curl -I <base_url>feed.xml` と `curl -I <base_url>ep/2026-09-25.mp3` が 200 を返すこと。
   可能なら https://podba.se/validate/ などでフィードを検証する。
5. **Spotify に登録（ユーザー本人の操作）**
   - https://creators.spotify.com にログイン → 既存の番組を追加（RSS フィードで追加）→ `<base_url>feed.xml` を貼る
   - `owner_email` に届いた確認コードを入力 → カテゴリ・言語を確認して送信
   - 反映まで数時間かかることがある。Apple Podcasts にも載せるなら Podcasts Connect に同じ URL を登録。
6. **毎朝の自動公開を確認**：Actions の「Publish today's episode」を一度手動実行（workflow_dispatch）して、成功すること。

## 注意
- `build_feed.py` は放送日（JST）が今日以前の回だけを載せる。`--all` は確認用なので、そのまま push しない。
- guid は `asa-pod-YYYY-MM-DD` で固定。一度公開した回の guid や音声URLは変えない（Spotify上で重複や再配信が起きる）。
- 2026/9/26 時点で Notion 側のメモに「Spotify Wrapped（10/11）はカンヌ・グランプリではない」という確認メモがある。題材を差し替える場合は `episodes.json` の該当回と `docs/ep/2026-10-11.mp3` を置き換える（放送前なら guid はそのままでよい）。
- 新しい回の追加は `tools/add_episode.py`。台本・音声の作り方は README と `pipeline/`。
- トークンやパスワードをファイルやコミットに残さない。

## 2026/9/26 時点の状態
- 全40本を「アイデアの分岐点」の新形式（経緯中心、pipeline/BRIEF.md）で書き直し、`podcast.json` の `batch` で一括公開済み（guid・音声URLは従来どおり）。10/1 は Slack、10/8 はユニクロックに差し替え（Notion にはまだページがない）。
- 毎朝の自動公開ワークフローは無効化中（`gh workflow enable feed.yml` で再開）。11/4 以降の新しい回を日次で出すときに再開する。
- 音声合成はこの Mac で動く（~/vv に VOICEVOX、`SCRIPTS_DIR=<repo>/scripts bash pipeline/worker.sh N`、~/pod/STOP で停止）。
- 下調べと題名・説明文の元データは drafts/（screening.md, episode_texts.json）。
