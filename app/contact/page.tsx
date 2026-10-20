import type { Metadata } from "next";
import ContactForm from "./ContactForm";

export const metadata: Metadata = {
  title: "お問い合わせ｜みんなのデジタル社員",
  description: "記事の掲載・削除のご依頼や、デジタル社員づくりのご相談はこちらから。",
};

export default function ContactPage() {
  return (
    <div className="page">
      <div className="page-inner">
        <header className="masthead">
          <div className="masthead-brand">
            <div className="masthead-title-row">
              <a className="logo-lockup" href="/">
                <span className="logo-mark" aria-hidden="true">み</span>
                <span className="logo">みんなのデジタル社員</span>
              </a>
              <p className="vol">VOL.001</p>
            </div>
            <p className="disclaimer">※実在の人間の求人情報ではありません</p>
          </div>
          <span aria-hidden="true" />
          <p className="tagline">AI社員の話題を、毎朝まとめて</p>
        </header>
        <nav className="breadcrumb" aria-label="パンくずリスト">
          <ol>
            <li>
              <a href="/">今日</a>
            </li>
            <li aria-current="page">お問い合わせ</li>
          </ol>
        </nav>
        <main className="contact">
          <p className="kicker">CONTACT</p>
          <h1 className="contact-title">お問い合わせ</h1>
          <ContactForm />
        </main>
      </div>
    </div>
  );
}
