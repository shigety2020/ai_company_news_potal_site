import type { ReactNode } from "react";
import type { Metadata } from "next";
import { Noto_Sans_JP, Shippori_Mincho } from "next/font/google";
import "./globals.css";

const sans = Noto_Sans_JP({
  subsets: ["latin"],
  weight: ["400", "500", "700"],
  display: "swap",
  variable: "--font-sans",
  adjustFontFallback: false,
});

const serif = Shippori_Mincho({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  display: "swap",
  variable: "--font-serif",
  adjustFontFallback: false,
});

export const metadata: Metadata = {
  title: "AI社員デイリー",
  description:
    "AI社員の作り方・ツール・事例を、毎日ひとつの特集と見出し一覧で。",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="ja" className={`${sans.variable} ${serif.variable}`}>
      <body>{children}</body>
    </html>
  );
}
