# AI社員デイリー — プロダクトバックログ

価値順。ログイン／コメントは後回し。

最終更新: 2026-09-30（フェーズ2本番 Done／#9〜#12）

スクラムイベント記録: [`docs/scrum/`](./docs/scrum/README.md)

## ブランチ方針

- 号データ（`data/`）は `main` が正。`develop` では収集しない。
- 収集仕様の変更は `main` から切ったブランチで手動収集 → preview 確認 → `main`。
- アプリのコードは従来どおり `feature` → `develop` → `main`。

## 契約（触らない）

`GET /api/daily?date=YYYY-MM-DD` → `{ date, featured, items[] }`

各 item: `{ time, headline, summary, handle, category, url, source, thumbnail }`  
category: `作り方` / `ツール` / `事例`  
source: `x` / `youtube` / `web`（必須）  
handle: X は @ハンドル、YouTube はチャンネル名、web はサイト名

## バックログ（価値順）

| # | 項目 | 状態 | Done（受け入れ） |
|---|------|------|------------------|
| 1〜7 | （X MVP） | **Done** | 本番URLで毎日の号。省略可 → 過去記録参照 |
| 8 | 空号の写真 | **Done**（#10 で置き換え） | 空号は「今日の特集はありません」・ナビ。写真は #10 で1枚固定に変更。 |
| 9 | 一つの誌面に出典を増やす（フェーズ2） | **Done**（2026-09-30 本番） | 同じ誌面に X／YouTube／Web。全件に `source`。目次は「via X · @handle」「via YouTube · チャンネル名」「via Web · サイト名」。特集には via を付けない。特集＋目次の型と画面3件キャップは維持。本番の朝の号で3ソースとも1件以上。 |
| 10 | マストヘッド写真 | **Done**（本番） | 号ありは曜日で `/masthead/0.jpg`〜`6.jpg`（Sun=0…Sat=6）。空号は `/masthead-empty.jpg` の1枚固定（メガネ）。 |
| 11 | 目次のサムネ | **Done**（2026-09-30 本番） | 全件にサムネ。元の画像があれば実画像、無ければ URL ハッシュで `/thumb-fallback/0〜5.jpg` を割り当て。サムネの空0。特集にはサムネを付けない。 |
| 12 | 90日鮮度 | **Done**（2026-09-30 本番） | 収集時に90日より古いものを除く（X／YouTube／Web 共通）。 |

## 朝の確認（本番の号）

- via が X・YouTube・Web とも1件以上
- サムネの空0
- 特集に via なし

## 本番URL

https://ai-company-news-potal-site.vercel.app

## 後回し

- ログイン
- コメント

## シゲッティ向けの見方

このファイルがバックログの正。チャットと食い違うときはここを更新してから話す。
