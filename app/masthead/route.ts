import { NextResponse } from "next/server";
import { a } from "./jpeg-a";
import { b } from "./jpeg-b";
import { c } from "./jpeg-c";
import { d } from "./jpeg-d";

const JPEG_BASE64 = a + b + c + d;

export function GET() {
  const body = Buffer.from(JPEG_BASE64, "base64");
  return new NextResponse(body, {
    headers: {
      "Content-Type": "image/jpeg",
      "Cache-Control": "public, max-age=31536000, immutable",
    },
  });
}
