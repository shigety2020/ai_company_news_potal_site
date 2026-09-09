import { NextRequest, NextResponse } from "next/server";
import { jpeg0 } from "../../../lib/masthead-empty/jpeg-0";
import { jpeg1 } from "../../../lib/masthead-empty/jpeg-1";
import { jpeg2 } from "../../../lib/masthead-empty/jpeg-2";
import { jpeg3 } from "../../../lib/masthead-empty/jpeg-3";
import { jpeg4 } from "../../../lib/masthead-empty/jpeg-4";
import { jpeg5 } from "../../../lib/masthead-empty/jpeg-5";
import { jpeg6 } from "../../../lib/masthead-empty/jpeg-6";

const MAP: Record<string, string> = {
  "0.jpg": jpeg0,
  "1.jpg": jpeg1,
  "2.jpg": jpeg2,
  "3.jpg": jpeg3,
  "4.jpg": jpeg4,
  "5.jpg": jpeg5,
  "6.jpg": jpeg6,
};

export const runtime = "nodejs";

export async function GET(
  _req: NextRequest,
  ctx: { params: Promise<{ file: string }> | { file: string } },
) {
  const params = await Promise.resolve(ctx.params);
  const b64 = MAP[params.file];
  if (!b64) {
    return new NextResponse("Not Found", { status: 404 });
  }
  const buf = Buffer.from(b64, "base64");
  return new NextResponse(buf, {
    status: 200,
    headers: {
      "Content-Type": "image/jpeg",
      "Cache-Control": "public, max-age=86400",
    },
  });
}
