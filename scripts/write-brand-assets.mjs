import { readFileSync, writeFileSync, mkdirSync, copyFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const brand = join(root, "scripts", "brand-assets");

function writeFromB64(relOut, b64Name) {
  const out = join(root, relOut);
  mkdirSync(dirname(out), { recursive: true });
  const buf = Buffer.from(readFileSync(join(brand, b64Name), "utf8"), "base64");
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

// icon.svg is committed as text under app/; mirror to public
copyFileSync(join(root, "app/icon.svg"), join(root, "public/icon.svg"));
console.log("wrote public/icon.svg");
