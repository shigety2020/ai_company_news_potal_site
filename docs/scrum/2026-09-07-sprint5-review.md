# Sprint 5 レビュー — 2026-09-07

**ゴール**: 日次収集を日付キーの号に乗せる
**インクリメント**: `data/2026-09-07.json`（特集1＋目次20）を `/api/daily?date=2026-09-07` に載せた。

## Preview

https://ai-shain-daily-git-feat-white-edit-64e9fa-shigety2020s-projects.vercel.app/?date=2026-09-07

## 検証

- ナオ: 差し替え確認。画面3/3/3、`?date=` とキャップ外していない
- ユイ: 画素通し。号あり／空号ともOK。レイアウト触ってない
- カナ: 回帰通し。JSON20、空号は `featured: null`＋空目次
- レン: 収集→APIまでロック。契約そのまま

## 受け入れ

PB#5 Done。リク受け入れ。Sprint 5 ゴール達成。
