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

/**
 * 号数（VOL）。/backnumber と同じ「today までで中身のある号」を古い順に並べたときの 1 始まりの位置。
 * 中身のない日は、その日までに出た号の数（最低 1）を返す。
 */
export async function issueOrdinal(date: string, today: string): Promise<number> {
  const dates = (await listIssueDates()).filter((d) => d <= today && d <= date);
  let n = 0;
  for (const d of dates) {
    const issue = await readIssue(d);
    if (issue && Array.isArray(issue.items) && issue.items.length > 0) n += 1;
  }
  return Math.max(1, n);
}
