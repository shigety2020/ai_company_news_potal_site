import { NextRequest, NextResponse } from "next/server";
import { DATE_RE, emptyIssue, findAdjacentDates, jstDate, readIssue } from "@/lib/daily";

export async function GET(req: NextRequest) {
  const today = jstDate();
  const date = req.nextUrl.searchParams.get("date") ?? today;

  if (!DATE_RE.test(date)) {
    return NextResponse.json({ error: "invalid date" }, { status: 400 });
  }

  const issue = (await readIssue(date)) ?? emptyIssue(date);
  const { prevDate, nextDate } = await findAdjacentDates(date, today);
  return NextResponse.json({ ...issue, prevDate, nextDate });
}
