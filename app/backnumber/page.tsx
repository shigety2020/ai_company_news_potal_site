import { jstDate, listIssueSummaries } from "../../lib/daily";

export const dynamic = "force-dynamic";

const MONTH_RE = /^\d{4}-\d{2}$/;
const PAGE_SIZE = 10;
const WD = ["日", "月", "火", "水", "木", "金", "土"];

function wdOf(iso: string): number {
  const [y, m, d] = iso.split("-").map(Number);
  return new Date(Date.UTC(y, m - 1, d, 12)).getUTCDay();
}

function label(iso: string): string {
  const [, m, d] = iso.split("-").map(Number);
  return `${m}/${d}（${WD[wdOf(iso)]}）`;
}

function shiftMonth(ym: string, delta: number): string {
  const [y, m] = ym.split("-").map(Number);
  const dt = new Date(Date.UTC(y, m - 1 + delta, 1));
  return `${dt.getUTCFullYear()}-${String(dt.getUTCMonth() + 1).padStart(2, "0")}`;
}

export default async function BackNumber({
  searchParams,
}: {
  searchParams: Promise<{ month?: string; limit?: string }>;
}) {
  const { month: monthParam, limit: limitParam } = await searchParams;
  const today = jstDate();
  // Days with 0 items are treated as "no issue" (not listed, not clickable).
  const issues = (await listIssueSummaries(today)).filter((i) => i.itemCount > 0);
  const latest = issues[0]?.date ?? null;
  const has = new Map(issues.map((i) => [i.date, i]));

  const month = monthParam && MONTH_RE.test(monthParam) ? monthParam : (latest ?? today).slice(0, 7);
  const [y, m] = month.split("-").map(Number);
  const daysInMonth = new Date(Date.UTC(y, m, 0)).getUTCDate();
  const lead = (wdOf(`${month}-01`) + 6) % 7; // Monday start
  const prevMonth = shiftMonth(month, -1);
  const nextMonth = shiftMonth(month, 1);
  const canNext = nextMonth <= today.slice(0, 7);

  const limit = Math.max(PAGE_SIZE, Number(limitParam) || PAGE_SIZE);
  const shown = issues.slice(0, limit);

  return (
    <div className="page">
      <div className="page-inner">
        <header className="masthead">
          <div className="logo-lockup">
            <span className="logo-mark" aria-hidden="true">み</span>
            <a className="logo" href="/">みんなのデジタル社員</a>
          </div>
        </header>
        <main className="bn">
          <h1 className="bn-title">過去の号を探す</h1>
          <p className="bn-lead">日付を選ぶと、その日の号が開きます。号は毎朝 7:30 までに出ます。</p>
          <div className="bn-grid">
            <section className="bn-sec" aria-labelledby="bn-cal">
              <h2 id="bn-cal" className="bn-sec-title">① カレンダーで選ぶ</h2>
              <div className="cal-head">
                <a className="cal-nav" href={`/backnumber?month=${prevMonth}`} aria-label="前の月">‹</a>
                <p className="cal-month" aria-live="polite">{y}年{m}月</p>
                {canNext ? (
                  <a className="cal-nav" href={`/backnumber?month=${nextMonth}`} aria-label="次の月">›</a>
                ) : (
                  <span className="cal-nav off" aria-hidden="true">›</span>
                )}
              </div>
              <div className="cal" role="grid" aria-label={`${y}年${m}月`}>
                {["月", "火", "水", "木", "金", "土", "日"].map((w) => (
                  <span key={w} className="cal-wd" role="columnheader">{w}</span>
                ))}
                {Array.from({ length: lead }, (_, i) => <span key={`l${i}`} className="cal-blank" />)}
                {Array.from({ length: daysInMonth }, (_, i) => {
                  const d = i + 1;
                  const iso = `${month}-${String(d).padStart(2, "0")}`;
                  if (has.has(iso)) {
                    return (
                      <a key={iso} role="gridcell" className={iso === latest ? "cal-day on latest" : "cal-day on"}
                        href={`/?date=${iso}`} aria-label={`${m}月${d}日の号`}>{d}</a>
                    );
                  }
                  return (
                    <span key={iso} role="gridcell" className={iso > today ? "cal-day future" : "cal-day none"}
                      aria-label={`${m}月${d}日 号なし`}>{d}</span>
                  );
                })}
              </div>
            </section>
            <section className="bn-sec" aria-labelledby="bn-list">
              <h2 id="bn-list" className="bn-sec-title">② 一覧で選ぶ（新しい順）</h2>
              <ul className="bn-list">
                {shown.map((i) => (
                  <li key={i.date}>
                    <a className="bn-row" href={`/?date=${i.date}`}>
                      <span className="bn-date">{label(i.date)}</span>
                      <span className="bn-meta">{i.date === latest ? "最新号・" : ""}{i.itemCount}件</span>
                      <span className="bn-open">開く →</span>
                    </a>
                  </li>
                ))}
              </ul>
              {issues.length > shown.length && (
                <a className="btn bn-more" href={`/backnumber?limit=${limit + PAGE_SIZE}${monthParam ? `&month=${month}` : ""}`}>
                  もっと前の号を見る
                </a>
              )}
            </section>
          </div>
        </main>
      </div>
    </div>
  );
}
