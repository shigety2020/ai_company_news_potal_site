# AI社員デイリー — プロダクトバックログ

価値順。ログイン／コメントは後回し。

最終更新: 2026-09-14（Sprint 8 Done／PB#8）

スクラムイベント記録: [`docs/scrum/`](./docs/scrum/README.md)

## ブランチ方針

- **本番 `main`** ＝ Xだけ
- **`develop`** ＝ X＋YouTube（＋ネット記事）開発中。feature は develop 起点

## 契約（触らない）

`GET /api/daily?date=YYYY-MM-DD` → `{ date, featured, items[] }`

各 item: `{ time, headline, summary, handle, category, url }`  
category: `作り方` / `ツール` / `事例`

## バックログ（価値順）

| # | 項目 | 状態 | Done（受け入れ） |
|---|------|------|------------------|
| 1〜7 | （X MVP） | **Done** | 本番URLで毎日の号。省略可 → 過去記録参照 |
| 8 | 空号の写真ローテ | **Done**（Sprint 8／develop） | 号ありは `/masthead`。空号のみ `/masthead-empty/0.jpg`〜`6.jpg`（Sun=0…Sat=6）。同じ枠・コピー「今日の特集はありません」・ナビ。契約・レイアウト・3件キャップ触らない。 |
| 9 | 一つの誌面に出典を増やす（フェーズ2） | **Ready（仮）** | 同じ誌面に X／YouTube／ネット記事。出典が分かる。特集＋目次の型は維持。ログイン後回し。細目はリファインで削る。develop 上。 |

## 本番URL

https://ai-company-news-potal-site.vercel.app

## 後回し

- ログイン
- コメント

## シゲッティ向けの見方

このファイルがバックログの正。チャットと食い違うときはここを更新してから話す。
