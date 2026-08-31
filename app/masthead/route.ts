import { NextResponse } from "next/server";

const JPEG_BASE64 = "FULL_JPEG_FROM_WORKSPACE_MASTHEAD_ROUTE";

export function GET() {
  const body = Buffer.from(JPEG_BASE64, "base64");
  return new NextResponse(body, {
    headers: {
      "Content-Type": "image/jpeg",
      "Cache-Control": "public, max-age=31536000, immutable",
    },
  });
}
