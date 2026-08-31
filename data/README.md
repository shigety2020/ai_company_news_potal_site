# daily seed

`YYYY-MM-DD.json` を `GET /api/daily?date=` がそのまま返す。

仕様は `{ date, featured, items[] }`。item は `time` / `headline` / `summary` / `handle` / `category` / `url`。

- `time`: JST の `HH:mm`
- `handle`: `@` なし
- `category`: `作り方` | `ツール` | `事例`
- `featured` は `items` に重複させない

`2026-08-31.json` はモックシード（仮想handle）。X収集が動いたら同じ形のJSONに差し替える。レスポンス形は変えない。
