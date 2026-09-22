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
- `thumbnail`:
  - **items（develop）**: **必須・非空**。実画像の HTTPS URL、または欠落時の `"/thumb-fallback.jpg"`。空文字・フィールド省略は不可（目次 TOC が常にサムネを出せるようにする）
  - **featured**: **任意**。FE は TOC のみにサムネを出すため、特集は省略してよい
  - **main**: `thumbnail` フィールドなしのまま（本番は要求しない）

ルール:

- `featured` は `items` に重複させない
- 特集1＋目次最大20
- 無い日は `{ date, featured: null, items: [] }`

画面側の出典行（目次のみ）は FE/UX 仕様。特集は従来どおり via なし。

### `thumbnail` の取り方（develop）

- `youtube`: `https://i.ytimg.com/vi/{VIDEO_ID}/hqdefault.jpg`（`watch?v=` / `youtu.be` から ID）
- `x`: 投稿にメディアがあればその画像 URL。無ければ `"/thumb-fallback.jpg"`
- `web`: `og:image` など取得できた HTTPS 画像 URL。無ければ `"/thumb-fallback.jpg"`
- 既存の非空 URL はそのまま残す。欠け・空のときだけ `"/thumb-fallback.jpg"` を入れる

## ブランチ

- **`main`（本番）**: Xだけの号。毎朝収集はここへ push。従来形を壊さない（**`thumbnail` フィールドなし**のまま。要求しない）
- **`develop`**: X／YouTube／web の多ソース。シードと #9 実装はここ。**items は常に非空 `thumbnail`（実 URL または `/thumb-fallback.jpg`）**。featured は任意

`2026-08-31.json` はモック。レスポンスの骨格（date / featured / items）は変えない。
