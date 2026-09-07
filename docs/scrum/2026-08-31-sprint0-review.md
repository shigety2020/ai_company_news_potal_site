# Sprint 0 レビュー — 2026-08-31

**ゴール**: 真っ白編集誌面の骨格を Ready で見る
**インクリメント**: `feat/white-editorial-skeleton` のプレビュー（特集大きめ＋目次、カテゴリ3列）

## 見たもの

- Ready: `ai-shain-daily-git-feat-white-edit-64e9fa-shigety2020s-projects.vercel.app`
- 特集ブロックから time/via を外して画素通過（1440 / 390）
- データはモック。契約は `GET /api/daily` → `{ date, featured, items[] }`

## 受け入れ

Sprint 0 Done。モック誌面を受け入れ。

## 次

Sprint 1 = 同じJSON／画面に実Xを乗せる。
