# daily seed

`YYYY-MM-DD.json` を `GET /api/daily?date=` がそのまま返す。

仕様は `{ date, featured, items[] }`。item は `time` / `headline` / `summary` / `handle` / `category` / `url`。

- `time`: JST の `HH:mm`
- `handle`: `@` なし
- `category`: `作り方` | `ツール` | `事例`
- `featured` は `items` に重複させない

毎朝 07:00 JST にバックエンドの自動収集が、その日の `data/YYYY-MM-DD.json` を `main`（本番 https://ai-company-news-potal-site.vercel.app ）に載せる（人手 push なし）。収集前に残高確認。失敗時はファイルを置かず、無い日の空号（`featured: null`＋空目次）を壊さない。

`2026-08-31.json` はモックシード（仮想handle）。レスポンス形は変えない。
