# Sprint 4 レビュー — 2026-09-07

**ゴール**: 日付で号を送る（前日／翌日）
**インクリメント**: issue-nav＋空号コピー。契約・レイアウト不変。

## Preview

https://ai-shain-daily-git-feat-white-edit-64e9fa-shigety2020s-projects.vercel.app/?date=2026-09-05

Commit: `55a2ccf0fd69a1b3e40ce53d3e5b337a8e4f6e81`

## 検証

- ナオ: 号あり `?date=2026-09-04` 特集＋画面3/3/3。空号 `?date=2026-09-05` マストヘッド残し「今日の特集はありません」。前日／翌日あり。
- ユイ: 画素通し。レイアウト触ってない。
- カナ: 回帰通し。空号は `featured: null`＋空目次。号ありは JSON20のまま。
- レン: API `?date=` で号あり／空号、契約そのまま。

## 受け入れ

PB#4 Done。リク受け入れ。Sprint 4 ゴール達成。
