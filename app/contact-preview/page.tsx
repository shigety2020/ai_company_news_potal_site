import type { Metadata } from "next";
import ContactForm from "../components/contact/ContactForm";

// PB4 確認用の仮ページ。確認が終わったら消す。
export const metadata: Metadata = {
  title: "問い合わせフォーム（仮ページ・確認用）",
  robots: { index: false, follow: false },
};

export default function ContactPreviewPage() {
  return (
    <main style={{ maxWidth: 720, margin: "0 auto", padding: "24px 16px" }}>
      <p role="note" style={{ padding: "8px 12px", border: "1px dashed #999", fontSize: 14 }}>
        これは確認用の仮ページです（PB4）。/api/contact はまだ無いので、送信すると「送信できませんでした」になります。
      </p>
      <ContactForm />
    </main>
  );
}
