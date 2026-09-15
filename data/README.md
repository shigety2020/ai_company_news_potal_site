# daily seed

`YYYY-MM-DD.json` を `GET /api/daily?date=` がそのまま返す。

## 契約（develop / PB#9）

`{ date, featured, items[] }`

各 item / featured:

- `time`: JST の `HH:mm`
- `headline` / `summary`
- `handle`: X は `@` なし。YouTube はチャンネル名、web はサイト名（無いときは `""`）
- `category`: `作り方` | `ツール` | `事例`
- `url`: 出典の正規URL
- `source`: `"x"` | `"youtube"` | `"web"`（**必須**）
- `thumbnail`（**任意**）: HTTPS の画像 URL。目次（TOC）表示用のみ。取得できないときはフィールド省略または `""`（どちらも可。空／無し = プレースホルダなし）。特集（featured）は FE が TOC のみにサムネを出すため省略してよい

ルール:

- `featured` は `items` に重複させない
- 特集1＋目次最大20
- 無い日は `{ date, featured: null, items: [] }`

画面側の出典行（目次のみ）は FE/UX 仕様。特集は従来どおり via なし。

### `thumbnail` の取り方（develop）

- `youtube`: `https://i.ytimg.com/vi/{VIDEO_ID}/hqdefault.jpg`（`watch?v=` / `youtu.be` から ID）
- `x`: 投稿にメディアがあればその画像 URL。無ければ省略／`""`
- `web`: `og:image` など取得できた HTTPS 画像 URL。無ければ省略／`""`

## ブランチ

- **`main`（本番）**: Xだけの号。毎朝収集はここへ push。従来形を壊さない（**`thumbnail` フィールドなし**のまま）
- **`develop`**: X／YouTube／web の多ソース。シードと #9 実装はここ。任意の `thumbnail` は develop のみ

`2026-08-31.json` はモック。レスポンスの骨格（date / featured / items）は変えない。
