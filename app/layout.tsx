import type { ReactNode } from "react";
import type { Metadata } from "next";
import { Analytics } from "@vercel/analytics/next";
import "./globals.css";

const NOTO_CSS =
  "https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap";

// next/font の Noto CSS（約 68 KB、@font-face 249）はレンダーブロックして LCP を止める。
// ウェイトは CSS で使っている 400 と 700 のみ。変数とフォールバック指標は next/font と同じにする。
// CSS 自体は media=print → onload で all にし、描画はブロックしない。
const FONT_VARS =
  'html{--font-sans:"Noto Sans JP", "Noto Sans JP Fallback"}' +
  "@font-face{font-family:Noto Sans JP Fallback;src:local(Arial);ascent-override:110.73%;descent-override:27.49%;line-gap-override:0.0%;size-adjust:104.76%}" +
  '@media (min-width: 1024px){html{--font-serif:"Shippori Mincho",serif}}';

const LOAD_NOTO =
  "(function(){var l=document.createElement('link');l.rel='stylesheet';l.href='" +
  NOTO_CSS +
  "';l.media='print';l.onload=function(){l.media='all'};document.head.appendChild(l);})();";

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
    <html lang="ja">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <script dangerouslySetInnerHTML={{ __html: LOAD_NOTO }} />
        <noscript>
          <link rel="stylesheet" href={NOTO_CSS} />
        </noscript>
        {/* 明朝は PC 幅だけ。Google Fonts CSS を media で読み、リポに woff2 を足さない。 */}
        <link
          rel="stylesheet"
          href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@600;700&display=swap"
          media="(min-width: 1024px)"
        />
        <style dangerouslySetInnerHTML={{ __html: FONT_VARS }} />
      </head>
      <body>
        {children}
        <Analytics />
      </body>
    </html>
  );
}
