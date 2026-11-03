import { listIssueDates, readIssue } from "./store";

export type IssueSummary = {
  date: string;
  featuredHeadline: string | null;
  itemCount: number;
};

/** data/ にある号の一覧（新しい順）。today より先の日付は除く。 */
export async function listIssueSummaries(today: string): Promise<IssueSummary[]> {
  const dates = (await listIssueDates()).filter((d) => d <= today).reverse();
  const out: IssueSummary[] = [];
  for (const date of dates) {
    const issue = await readIssue(date);
    if (!issue) continue;
    const f = issue.featured as { headline?: unknown } | null;
    out.push({
      date,
      featuredHeadline: typeof f?.headline === "string" ? f.headline : null,
      itemCount: Array.isArray(issue.items) ? issue.items.length : 0,
    });
  }
  return out;
}
