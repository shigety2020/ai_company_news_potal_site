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
  - **items（develop）**: **必須・非空**。実画像の HTTPS URL、または欠落時の URL-stable フォールバック `"/thumb-fallback/{0..5}.jpg"`。空文字・フィールド省略は不可（目次 TOC が常にサムネを出せるようにする）
  - **featured**: **任意**。FE は TOC のみにサムネを出すため、特集は省略してよい（無いキーは追加しない）
  - **main**: `thumbnail` フィールドなしのまま（本番は要求しない）

ルール:

- `featured` は `items` に重複させない
- 特集1＋目次最大20
- 無い日は `{ date, featured: null, items: [] }`

画面側の出典行（目次のみ）は FE/UX 仕様。特集は従来どおり via なし。

### `thumbnail` の取り方（develop）

- `youtube`: `https://i.ytimg.com/vi/{VIDEO_ID}/hqdefault.jpg`（`watch?v=` / `youtu.be` から ID）
- `x`: 投稿にメディアがあればその画像 URL。無ければ URL-hash フォールバック
- `web`: `og:image` など取得できた HTTPS 画像 URL。無ければ URL-hash フォールバック
- 既存の実 HTTPS URL（`/thumb-fallback` で始まらないもの）はそのまま残す
- 欠け・空・旧 `"/thumb-fallback.jpg"` のときだけ、次の **6-way URL-hash フォールバック** を入れる

### 6-way URL-hash フォールバック（develop）

単一の `/thumb-fallback.jpg` は使わない。同じ `item.url` なら常に同じ番号になる安定ハッシュで振り分ける:

1. `n = (sum of char codes of item.url) % 6`（0..5）
2. `thumbnail = "/thumb-fallback/" + n + ".jpg"`

例: `/thumb-fallback/0.jpg` … `/thumb-fallback/5.jpg`

- 実メディアイメージがある X / YouTube / web は HTTPS のまま
- 実画像が無い X（および youtube/web で画像欠落）は上記ハッシュパス
- featured に `thumbnail` が無い場合は追加しない

## ブランチ

- **`main`（本番）**: Xだけの号。毎朝収集はここへ push。従来形を壊さない（**`thumbnail` フィールドなし**のまま。要求しない）
- **`develop`**: X／YouTube／web の多ソース。シードと #9 実装はここ。**items は常に非空 `thumbnail`（実 URL または `/thumb-fallback/{0..5}.jpg`）**。featured は任意

`2026-08-31.json` はモック。レスポンスの骨格（date / featured / items）は変えない。
