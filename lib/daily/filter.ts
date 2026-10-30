import type { DailyIssue } from "./store";

/** 号データに入っているカテゴリ値（data/*.json の items[].category）。 */
export const CATEGORIES = ["事例", "ツール", "作り方"] as const;
export type Category = (typeof CATEGORIES)[number];

export function isCategory(v: string): v is Category {
  return (CATEGORIES as readonly string[]).includes(v);
}

/** 目次（items）だけを category で絞る。特集（featured）はそのまま残す。 */
export function filterByCategory(issue: DailyIssue, category: Category): DailyIssue {
  const items = Array.isArray(issue.items)
    ? issue.items.filter((it) => (it as { category?: unknown })?.category === category)
    : [];
  return { ...issue, items };
}
