import { readFileSync, writeFileSync, mkdirSync, copyFileSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const brand = join(root, "scripts", "brand-assets");

function readB64(b64Name) {
  const single = join(brand, b64Name);
  if (existsSync(single)) {
    return readFileSync(single, "utf8").replace(/\s+/g, "");
  }
  // Concatenate .part1 + .part2 if present (for large assets pushed via MCP)
  const p1 = join(brand, b64Name + ".part1");
  const p2 = join(brand, b64Name + ".part2");
  if (existsSync(p1) && existsSync(p2)) {
    return (readFileSync(p1, "utf8") + readFileSync(p2, "utf8")).replace(/\s+/g, "");
  }
  throw new Error("missing brand asset: " + b64Name);
}

function writeFromB64(relOut, b64Name) {
  const out = join(root, relOut);
  mkdirSync(dirname(out), { recursive: true });
  const buf = Buffer.from(readB64(b64Name), "base64");
  writeFileSync(out, buf);
  console.log("wrote", relOut, buf.length, "bytes");
}

writeFromB64("public/og.png", "og.png.b64");
writeFromB64("public/favicon.ico", "favicon.ico.b64");
writeFromB64("app/favicon.ico", "favicon.ico.b64");
writeFromB64("app/apple-icon.png", "apple-icon.png.b64");
writeFromB64("public/apple-icon.png", "apple-icon.png.b64");
writeFromB64("public/icon-16.png", "icon-16.png.b64");
writeFromB64("public/icon-32.png", "icon-32.png.b64");
writeFromB64("app/icon.png", "icon-32.png.b64");

copyFileSync(join(root, "app/icon.svg"), join(root, "public/icon.svg"));
console.log("wrote public/icon.svg");
