import { NextRequest, NextResponse } from "next/server";
import {
  CATEGORIES,
  DATE_RE,
  emptyIssue,
  filterByCategory,
  findAdjacentDates,
  isCategory,
  jstDate,
  readIssue,
} from "@/lib/daily";

export async function GET(req: NextRequest) {
  const today = jstDate();
  const date = req.nextUrl.searchParams.get("date") ?? today;
  const category = req.nextUrl.searchParams.get("category");

  if (!DATE_RE.test(date)) {
    return NextResponse.json({ error: "invalid date" }, { status: 400 });
  }
  if (category !== null && !isCategory(category)) {
    return NextResponse.json(
      { error: "invalid category", categories: CATEGORIES },
      { status: 400 },
    );
  }

  let issue = (await readIssue(date)) ?? emptyIssue(date);
  if (category !== null) issue = filterByCategory(issue, category);
  const { prevDate, nextDate } = await findAdjacentDates(date, today);
  return NextResponse.json({ ...issue, prevDate, nextDate, ...(category !== null ? { category } : {}) });
}
