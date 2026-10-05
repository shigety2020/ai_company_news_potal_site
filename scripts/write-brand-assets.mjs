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
  let out = "";
  for (let i = 1; i <= 16; i++) {
    const p = join(brand, `${b64Name}.part${i}`);
    if (!existsSync(p)) break;
    out += readFileSync(p, "utf8");
  }
  if (!out) throw new Error("missing brand asset: " + b64Name);
  return out.replace(/\s+/g, "");
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
