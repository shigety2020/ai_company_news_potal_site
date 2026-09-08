# Sprint 6 レビュー — 2026-09-08

**ゴール**: 毎朝自動で今日の号を載せる（人手pushなし）
**インクリメント**: 初回自動で `data/2026-09-08.json` → `/api/daily?date=2026-09-08`（特集1＋目次20）

## Preview

https://ai-shain-daily-git-feat-white-edit-64e9fa-shigety2020s-projects.vercel.app/?date=2026-09-08

特集: 「AIエージェント、試したのに立ち消える会社の共通点」（@TAKA_ENX / 作り方）
Commit: `efb82b14132868026f7243c1eb643701df3e63ce`
残高: 約 $4.49

## 検証（セルフチェック）

- ナオ: 特集・画面3/3/3・JSON20・ナビOK。空号そのまま
- ユイ: 号あり／空号画素通し。レイアウト触ってない
- カナ: 回帰通し。空号は `featured: null`＋空目次
- レン: 自動収集→APIまで確認。契約そのまま

## 受け入れ

PB#6 Done。リク受け入れ。Sprint 6 ゴール達成。
