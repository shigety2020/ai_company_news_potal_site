import { NextResponse } from "next/server";
import { jstDate, listIssueSummaries } from "@/lib/daily";

export async function GET() {
  const issues = await listIssueSummaries(jstDate());
  return NextResponse.json({ issues });
}
