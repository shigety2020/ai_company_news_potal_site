# ai_company_news_potal_site
AI社員を特集したニュース記事のまとめサイト

## 毎朝の号の自動収集（PB1）

`.github/workflows/daily-collect.yml` が毎朝 7:00 JST（cron `0 22 * * *` UTC）に `scripts/daily/collect.py` を動かし、
`data/YYYY-MM-DD.json` の1ファイルだけを `main` に commit・push します。Actions タブの「Run workflow」から手で試せます（既定は dry run で、commit・push しません）。

### 必要な secrets（Settings → Secrets and variables → Actions）

| 名前 | 中身 | 無いとき |
| --- | --- | --- |
| `X_BEARER_TOKEN` | X API v2 の Bearer Token（検索は1回の収集で3回まで・max_results 20・次ページなし） | X なしで20件を作り、`"collection": "no-x"` を付ける |
| `OPENAI_API_KEY` | OpenAI の API キー（AI社員の話かの判定・カテゴリ・見出し・要約） | 収集が失敗し、何も push しない |

任意の variable：`OPENAI_MODEL`（既定 `gpt-4o-mini`）。

### 決まり（`validate()` で push 前に確かめる）

- 20件（目安 X9・YouTube6・Web5）＋特集1件、公開3か月以内、前の号とのだぶりなし
- 1号で同じ X アカウント・同じ YouTube チャンネルは1件まで
- サムネに `pbs.twimg.com/card_img` は使わず、無いときは `/thumb-fallback/{sum(ord(c) for c in url) % 6}.jpg`

ローカル確認（キー不要）：`python3 -m unittest scripts/daily/test_collect.py`、`python3 scripts/daily/collect.py --validate data/2026-10-20.json`
