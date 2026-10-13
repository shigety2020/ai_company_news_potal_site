import { readdir, readFile } from "node:fs/promises";
import path from "node:path";
import { DATE_RE } from "./date";

export type DailyIssue = {
  date: string;
  featured: unknown;
  items: unknown[];
  [key: string]: unknown;
};

const DATA_DIR = path.join(process.cwd(), "data");

export function emptyIssue(date: string): DailyIssue {
  return { date, featured: null, items: [] };
}

/** Raw issue JSON for a date, or null when the file is missing or unreadable. */
export async function readIssue(date: string): Promise<DailyIssue | null> {
  try {
    const raw = await readFile(path.join(DATA_DIR, `${date}.json`), "utf8");
    return JSON.parse(raw) as DailyIssue;
  } catch {
    return null;
  }
}

export function hasContent(issue: DailyIssue | null): boolean {
  if (!issue) return false;
  return (Array.isArray(issue.items) && issue.items.length > 0) || Boolean(issue.featured);
}

/** All YYYY-MM-DD dates that have a data file, ascending. */
export async function listIssueDates(): Promise<string[]> {
  try {
    const names = await readdir(DATA_DIR);
    return names
      .filter((n) => n.endsWith(".json"))
      .map((n) => n.slice(0, -5))
      .filter((d) => DATE_RE.test(d))
      .sort();
  } catch {
    return [];
  }
}
