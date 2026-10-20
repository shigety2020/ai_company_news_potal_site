"use client";

import { useRef, useState, type FormEvent, type KeyboardEvent, type ReactNode } from "react";

type FieldName = "type" | "name" | "email" | "message";
type Values = Record<FieldName, string>;
type Errors = Partial<Record<FieldName, string>>;
type Status = "idle" | "sending" | "sent";
type Notice = { title: string; body: string } | null;

const TYPES = [
  { value: "listing", label: "掲載依頼", desc: "AI社員・デジタル社員の記事や事例を載せてほしいとき" },
  { value: "removal", label: "削除依頼", desc: "載っている記事を消してほしいとき" },
  { value: "service", label: "わたしのデジタル社員構築サービス", desc: "自分専用のデジタル社員づくりを相談したいとき" },
] as const;

const ORDER: FieldName[] = ["type", "name", "email", "message"];
const LABELS: Record<FieldName, string> = {
  type: "お問い合わせの種類",
  name: "お名前",
  email: "メールアドレス",
  message: "内容",
};
const MESSAGES: Record<FieldName, string> = {
  type: "お問い合わせの種類を選んでください",
  name: "お名前を入力してください",
  email: "メールアドレスの形が正しくありません（例：hanako@example.com）",
  message: "内容を入力してください",
};
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function validate(v: Values): Errors {
  const e: Errors = {};
  if (!TYPES.some((t) => t.value === v.type)) e.type = MESSAGES.type;
  if (!v.name.trim()) e.name = MESSAGES.name;
  if (!v.email.trim()) e.email = "メールアドレスを入力してください";
  else if (!EMAIL_RE.test(v.email.trim())) e.email = MESSAGES.email;
  if (!v.message.trim()) e.message = MESSAGES.message;
  return e;
}

function fieldId(f: FieldName): string {
  return f === "type" ? "type-listing" : `contact-${f}`;
}

function ErrorText({ field, text }: { field: FieldName; text?: string }) {
  if (!text) return null;
  return (
    <p className="field-error" id={`err-${field}`}>
      <span className="field-error-icon" aria-hidden="true">!</span>
      {text}
    </p>
  );
}

function Field({
  field,
  label,
  hint,
  error,
  children,
}: {
  field: FieldName;
  label: string;
  hint?: string;
  error?: string;
  children: ReactNode;
}) {
  return (
    <div className={`field${error ? " is-invalid" : ""}`}>
      <label className="field-label" htmlFor={fieldId(field)}>
        {label}
        <span className="required">必須</span>
      </label>
      {children}
      {hint && (
        <p className="field-hint" id={`hint-${field}`}>
          {hint}
        </p>
      )}
      <ErrorText field={field} text={error} />
    </div>
  );
}

function RadioCard({
  value,
  label,
  desc,
  checked,
  invalid,
  onSelect,
  onKeyDown,
}: {
  value: string;
  label: string;
  desc: string;
  checked: boolean;
  invalid: boolean;
  onSelect: (v: string) => void;
  onKeyDown: (e: KeyboardEvent<HTMLInputElement>) => void;
}) {
  return (
    <label className={`radio-card${checked ? " is-checked" : ""}${invalid ? " is-invalid" : ""}`}>
      <input
        className="radio-card-input"
        type="radio"
        name="type"
        id={`type-${value}`}
        value={value}
        checked={checked}
        onChange={() => onSelect(value)}
        onKeyDown={onKeyDown}
        aria-describedby={`desc-${value}`}
      />
      <span className="radio-card-dot" aria-hidden="true" />
      <span className="radio-card-text">
        <span className="radio-card-label">{label}</span>
        <span className="radio-card-desc" id={`desc-${value}`}>
          {desc}
        </span>
      </span>
    </label>
  );
}

export default function ContactForm() {
  const [values, setValues] = useState<Values>({ type: "", name: "", email: "", message: "" });
  const [website, setWebsite] = useState("");
  const [errors, setErrors] = useState<Errors>({});
  const [summaryError, setSummaryError] = useState<string | null>(null);
  const [notice, setNotice] = useState<Notice>(null);
  const [status, setStatus] = useState<Status>("idle");
  const summaryRef = useRef<HTMLDivElement>(null);
  const noticeRef = useRef<HTMLDivElement>(null);
  const sentRef = useRef<HTMLDivElement>(null);

  const set = (f: FieldName, v: string) => setValues((prev) => ({ ...prev, [f]: v }));

  const showErrors = (e: Errors, general: string | null = null) => {
    setErrors(e);
    setSummaryError(general);
    setNotice(null);
    requestAnimationFrame(() => summaryRef.current?.focus());
  };

  const showNotice = (n: Notice) => {
    setErrors({});
    setSummaryError(null);
    setNotice(n);
    requestAnimationFrame(() => noticeRef.current?.focus());
  };

  const onRadioKey = (e: KeyboardEvent<HTMLInputElement>) => {
    // ブラウザ標準の矢印キー移動に加え、未選択からでも確実に動くようにする
    const keys = ["ArrowDown", "ArrowRight", "ArrowUp", "ArrowLeft"];
    if (!keys.includes(e.key)) return;
    e.preventDefault();
    const idx = TYPES.findIndex((t) => t.value === e.currentTarget.value);
    const step = e.key === "ArrowDown" || e.key === "ArrowRight" ? 1 : -1;
    const next = TYPES[(idx + step + TYPES.length) % TYPES.length];
    set("type", next.value);
    document.getElementById(`type-${next.value}`)?.focus();
  };

  async function onSubmit(ev: FormEvent<HTMLFormElement>) {
    ev.preventDefault();
    if (status === "sending") return;
    const e = validate(values);
    if (Object.keys(e).length > 0) {
      showErrors(e);
      return;
    }
    setStatus("sending");
    try {
      const res = await fetch("/api/contact", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          type: values.type,
          name: values.name.trim(),
          email: values.email.trim(),
          message: values.message,
          website,
        }),
      });
      if (res.ok) {
        setStatus("sent");
        requestAnimationFrame(() => sentRef.current?.focus());
        return;
      }
      setStatus("idle");
      if (res.status === 400) {
        const data = (await res.json().catch(() => null)) as
          | { error?: string; fields?: Partial<Record<string, string>> }
          | null;
        const fe: Errors = {};
        for (const f of ORDER) {
          const msg = data?.fields?.[f];
          if (msg) fe[f] = typeof msg === "string" && msg ? msg : MESSAGES[f];
        }
        const general = Object.keys(fe).length === 0 ? data?.error ?? "入力を確かめてください" : null;
        showErrors(fe, general);
        return;
      }
      if (res.status === 429) {
        showNotice({
          title: "送信が多すぎます。しばらくしてからお試しください",
          body: "入力した内容はそのまま残っています。",
        });
        return;
      }
      throw new Error(`HTTP ${res.status}`);
    } catch {
      setStatus("idle");
      showNotice({
        title: "送信できませんでした",
        body: "通信がうまくいきませんでした。電波のよい所で、もう一度「送信する」を押してください。入力した内容はそのまま残っています。",
      });
    }
  }

  if (status === "sent") {
    return (
      <div className="contact-sent" role="status" tabIndex={-1} ref={sentRef}>
        <h2 className="contact-sent-title">送信しました</h2>
        <p className="contact-lead">
          お問い合わせありがとうございます。お返事は、入力いただいたメールアドレスにお送りします。
        </p>
        <a className="contact-button" href="/">
          今日の号へ戻る
        </a>
      </div>
    );
  }

  const errorFields = ORDER.filter((f) => errors[f]);
  const hasSummary = errorFields.length > 0 || !!summaryError;
  const describedBy = (f: FieldName, hint = false) =>
    [hint ? `hint-${f}` : "", errors[f] ? `err-${f}` : ""].filter(Boolean).join(" ") || undefined;

  return (
    <>
      <p className="contact-lead">
        記事の掲載・削除のご依頼や、デジタル社員づくりのご相談はこちらから。お返事はメールでお送りします。
      </p>
      {hasSummary && (
        <div className="contact-alert" role="alert" tabIndex={-1} ref={summaryRef}>
          <p className="contact-alert-title">
            入力を確かめてください{errorFields.length > 0 ? `（${errorFields.length}か所）` : ""}
          </p>
          {summaryError && <p className="contact-alert-body">{summaryError}</p>}
          {errorFields.length > 0 && (
            <ul className="contact-alert-list">
              {errorFields.map((f) => (
                <li key={f}>
                  <a
                    href={`#${fieldId(f)}`}
                    onClick={(e) => {
                      e.preventDefault();
                      const target =
                        f === "type"
                          ? document.getElementById(`type-${values.type || "listing"}`)
                          : document.getElementById(fieldId(f));
                      target?.focus();
                    }}
                  >
                    {errors[f]}
                  </a>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
      {notice && (
        <div className="contact-alert" role="alert" tabIndex={-1} ref={noticeRef}>
          <p className="contact-alert-title">{notice.title}</p>
          <p className="contact-alert-body">{notice.body}</p>
        </div>
      )}
      <form className="contact-form" noValidate onSubmit={onSubmit}>
        <fieldset
          className={`field${errors.type ? " is-invalid" : ""}`}
          aria-invalid={errors.type ? true : undefined}
          aria-describedby={errors.type ? "err-type" : undefined}
        >
          <legend className="field-label">
            {LABELS.type}
            <span className="required">必須</span>
          </legend>
          <div className="radio-cards">
            {TYPES.map((t) => (
              <RadioCard
                key={t.value}
                value={t.value}
                label={t.label}
                desc={t.desc}
                checked={values.type === t.value}
                invalid={!!errors.type}
                onSelect={(v) => set("type", v)}
                onKeyDown={onRadioKey}
              />
            ))}
          </div>
          <ErrorText field="type" text={errors.type} />
        </fieldset>

        <Field field="name" label={LABELS.name} error={errors.name}>
          <input
            className="input"
            id="contact-name"
            name="name"
            type="text"
            autoComplete="name"
            placeholder="例：山田 花子"
            value={values.name}
            onChange={(e) => set("name", e.target.value)}
            aria-required="true"
            aria-invalid={errors.name ? true : undefined}
            aria-describedby={describedBy("name")}
          />
        </Field>

        <Field field="email" label={LABELS.email} hint="お返事はこのアドレスにお送りします。" error={errors.email}>
          <input
            className="input"
            id="contact-email"
            name="email"
            type="email"
            inputMode="email"
            autoComplete="email"
            placeholder="例：hanako@example.com"
            value={values.email}
            onChange={(e) => set("email", e.target.value)}
            aria-required="true"
            aria-invalid={errors.email ? true : undefined}
            aria-describedby={describedBy("email", true)}
          />
        </Field>

        <Field field="message" label={LABELS.message} error={errors.message}>
          <textarea
            className="input textarea"
            id="contact-message"
            name="message"
            placeholder="掲載依頼・削除依頼のときは、記事の URL も書いてください。"
            value={values.message}
            onChange={(e) => set("message", e.target.value)}
            aria-required="true"
            aria-invalid={errors.message ? true : undefined}
            aria-describedby={describedBy("message")}
          />
        </Field>

        <div className="honeypot" aria-hidden="true">
          <label htmlFor="contact-website">website</label>
          <input
            id="contact-website"
            name="website"
            type="text"
            tabIndex={-1}
            autoComplete="off"
            value={website}
            onChange={(e) => setWebsite(e.target.value)}
          />
        </div>

        <p className="contact-privacy">いただいた内容は、お返事のためだけに使います。</p>
        <button className="contact-button" type="submit" disabled={status === "sending"}>
          {status === "sending" ? "送信しています…" : "送信する"}
        </button>
      </form>
    </>
  );
}
