import type { ReactNode } from "react";
import type { Metadata } from "next";
import { Noto_Sans_JP } from "next/font/google";
import { Analytics } from "@vercel/analytics/next";
import "./globals.css";

const sans = Noto_Sans_JP({
  subsets: ["latin"],
  weight: ["400", "700"],
  display: "swap",
  variable: "--font-sans",
  adjustFontFallback: false,
  preload: false,
});

export const metadata: Metadata = {
  title: "みんなのデジタル社員｜AI秘書・AI社員の事例とツール",
  description: "AI社員の話題を、毎朝まとめて",
  openGraph: {
    title: "みんなのデジタル社員｜AI秘書・AI社員の事例とツール",
    siteName: "みんなのデジタル社員",
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
    <html lang="ja" className={sans.variable}>
      <head>
        {/* 明朝は PC 幅だけ。Google Fonts CSS を media で読み、リポに woff2 を足さない。 */}
        <link
          rel="stylesheet"
          href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@600;700&display=swap"
          media="(min-width: 1024px)"
        />
        <style
          dangerouslySetInnerHTML={{
            __html: '@media (min-width: 1024px){html{--font-serif:"Shippori Mincho",serif}}',
          }}
        />
      </head>
      <body>
        {children}
        <Analytics />
      </body>
    </html>
  );
}
