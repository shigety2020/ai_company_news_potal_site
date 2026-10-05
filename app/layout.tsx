import type { ReactNode } from "react";
import type { Metadata } from "next";
import { Noto_Sans_JP, Shippori_Mincho } from "next/font/google";
import { Analytics } from "@vercel/analytics/next";
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
  title: "みんなのデジタル社員",
  description: "AI社員の話題を、毎朝まとめて",
  openGraph: {
    title: "みんなのデジタル社員",
    description: "AI社員の話題を、毎朝まとめて",
    images: [{ url: "/og.png", width: 1200, height: 630, alt: "みんなのデジタル社員" }],
  },
  twitter: {
    card: "summary_large_image",
    title: "みんなのデジタル社員",
    description: "AI社員の話題を、毎朝まとめて",
    images: ["/og.png"],
  },
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="ja" className={`${sans.variable} ${serif.variable}`}>
      <body>
        {children}
        <Analytics />
      </body>
    </html>
  );
}
