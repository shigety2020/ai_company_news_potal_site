import { hasContent, listIssueDates, readIssue } from "./store";

/**
 * Nearest dates before/after `date` that have an issue with content.
 * Empty issues are skipped; dates later than `today` (Asia/Tokyo) are never returned.
 */
export async function findAdjacentDates(
  date: string,
  today: string,
): Promise<{ prevDate: string | null; nextDate: string | null }> {
  const dates = (await listIssueDates()).filter((d) => d <= today);

  let prevDate: string | null = null;
  for (const d of dates.filter((d) => d < date).reverse()) {
    if (hasContent(await readIssue(d))) { prevDate = d; break; }
  }
  let nextDate: string | null = null;
  for (const d of dates.filter((d) => d > date)) {
    if (hasContent(await readIssue(d))) { nextDate = d; break; }
  }
  return { prevDate, nextDate };
}
