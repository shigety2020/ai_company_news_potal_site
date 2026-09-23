import { headers } from "next/headers";

export const dynamic = "force-dynamic";

type Category = "作り方" | "ツール" | "事例";

type Source = "x" | "youtube" | "web";

type DailyItem = {
  time: string;
  headline: string;
  summary: string;
  handle: string;
  category: Category;
  url: string;
  source?: Source;
  sourceLabel?: string;
  /** TOC thumbnail URL (develop). Empty/legacy single fallback → URL-hash /thumb-fallback/0..5.jpg. */
  thumbnail?: string | null;
  image?: string | null;
};

type DailyResponse = {
  date: string;
  featured: DailyItem | null;
  items: DailyItem[];
};

const DATE_RE = /^\d{4}-\d{2}-\d{2}$/;
const CATEGORIES: Category[] = ["作り方", "ツール", "事例"];

function jstDate(d = new Date()): string {
  return new Intl.DateTimeFormat("en-CA", {
    timeZone: "Asia/Tokyo",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(d);
}

function formatIssueDate(iso: string): string {
  const [y, m, d] = iso.split("-");
  return `${y}.${m}.${d}`;
}

/** Shift YYYY-MM-DD by delta days in calendar (UTC noon to avoid TZ edge). */
function shiftDate(iso: string, delta: number): string {
  const [y, m, d] = iso.split("-").map(Number);
  const dt = new Date(Date.UTC(y, m - 1, d + delta, 12, 0, 0));
  const yy = dt.getUTCFullYear();
  const mm = String(dt.getUTCMonth() + 1).padStart(2, "0");
  const dd = String(dt.getUTCDate()).padStart(2, "0");
  return `${yy}-${mm}-${dd}`;
}

/** Weekday index Sun=0 … Sat=6. */
function weekdaySun0(iso: string): number {
  const [y, m, d] = iso.split("-").map(Number);
  return new Date(Date.UTC(y, m - 1, d, 12, 0, 0)).getUTCDay();
}

/** Featured-issue masthead rotates by weekday. */
function featuredMastheadSrc(iso: string): string {
  return `/masthead/${weekdaySun0(iso)}.jpg`;
}

/** Empty-issue masthead is a single fixed photo. */
function emptyMastheadSrc(): string {
  return "/masthead-empty.jpg";
}

function emptyDaily(date: string): DailyResponse {
  return { date, featured: null, items: [] };
}

function itemKey(item: DailyItem): string {
  return `${item.url}::${item.headline}`;
}


/** Prefer one of each source (x/youtube/web), then fill to 3 in API order. */
function pickThreePreferSources(items: DailyItem[]): DailyItem[] {
  const picked: DailyItem[] = [];
  const used = new Set<string>();
  const prefer: Source[] = ["x", "youtube", "web"];
  for (const s of prefer) {
    if (picked.length >= 3) break;
    const hit = items.find((item) => {
      if (used.has(itemKey(item))) return false;
      const src: Source =
        item.source === "youtube" || item.source === "web" || item.source === "x"
          ? item.source
          : "x";
      return src === s;
    });
    if (hit) {
      picked.push(hit);
      used.add(itemKey(hit));
    }
  }
  for (const item of items) {
    if (picked.length >= 3) break;
    const k = itemKey(item);
    if (used.has(k)) continue;
    picked.push(item);
    used.add(k);
  }
  return picked;
}


async function getBaseUrl(): Promise<string> {
  try {
    const h = await headers();
    const host = h.get("x-forwarded-host") ?? h.get("host");
    if (host) {
      const proto =
        h.get("x-forwarded-proto") ??
        (host.includes("localhost") || host.startsWith("127.") ? "http" : "https");
      return `${proto}://${host}`;
    }
  } catch {
    /* no request context (e.g. build) */
  }
  if (process.env.VERCEL_URL) return `https://${process.env.VERCEL_URL}`;
  return "http://localhost:3000";
}

async function getDaily(date: string): Promise<DailyResponse> {
  try {
    const base = await getBaseUrl();
    const res = await fetch(`${base}/api/daily?date=${date}`, { cache: "no-store" });
    if (!res.ok) return emptyDaily(date);
    const data = (await res.json()) as DailyResponse;
    return {
      date: data.date ?? date,
      featured: data.featured ?? null,
      items: Array.isArray(data.items) ? data.items : [],
    };
  } catch {
    return emptyDaily(date);
  }
}

function Photo({ src }: { src: string }) {
  return (
    <div className="photo">
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={src} alt="窓辺のデスクにノートとコーヒー" />
    </div>
  );
}

function Featured({ item, date }: { item: DailyItem | null; date: string }) {
  const photoSrc = item ? featuredMastheadSrc(date) : emptyMastheadSrc();
  return (
    <section className="featured" aria-label="本日の特集">
      <Photo src={photoSrc} />
      {item ? (
        <a className="featured-body story" href={item.url} target="_blank" rel="noreferrer">
          <p className="kicker">今日の特集 01</p>
          <h2 className="featured-headline">{item.headline}</h2>
          <p className="summary">{item.summary}</p>
          <p className="read-more">続きを読む →</p>
        </a>
      ) : (
        <div className="featured-body">
          <p className="kicker">今日の特集 01</p>
          <h2 className="featured-headline">今日の特集はありません</h2>
        </div>
      )}
    </section>
  );
}


/** TOC source line. Missing source treated as x (main-compatible). */
function formatVia(item: DailyItem): string {
  const source: Source =
    item.source === "youtube" || item.source === "web" || item.source === "x"
      ? item.source
      : "x";
  const label =
    item.sourceLabel?.trim() ||
    (source === "youtube" ? "YouTube" : source === "web" ? "Web" : "X");
  const raw = (item.handle ?? "").trim();
  if (!raw) return `via ${label}`;
  const name = source === "x" ? (raw.startsWith("@") ? raw : `@${raw}`) : raw;
  return `via ${label} · ${name}`;
}

const THUMB_FALLBACK_COUNT = 6;

/** Stable positive hash for URL → fixed fallback index. */
function stableHash(s: string): number {
  let h = 0;
  for (let i = 0; i < s.length; i++) {
    h = (Math.imul(h, 31) + s.charCodeAt(i)) >>> 0;
  }
  return h;
}

function thumbFallbackForUrl(url: string): string {
  return `/thumb-fallback/${stableHash(url || "") % THUMB_FALLBACK_COUNT}.jpg`;
}

/** Prefer acquired thumbnail; empty or legacy `/thumb-fallback.jpg` → URL-hash 0..5. */
function resolveThumb(item: DailyItem): string {
  const t = (item.thumbnail ?? "").trim();
  if (t && t !== "/thumb-fallback.jpg") return t;
  return thumbFallbackForUrl(item.url);
}

function IndexStory({ item }: { item: DailyItem }) {
  const thumb = resolveThumb(item);
  return (
    <a className="story" href={item.url} target="_blank" rel="noreferrer">
      <div className="kicker-row">
        <time className="time" dateTime={item.time}>
          {item.time}
        </time>
        <span className="kicker">{item.category}</span>
      </div>
      <div className="item-row">
        <div className="item-thumb" aria-hidden="true">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={thumb} alt="" />
        </div>
        <div className="item-copy">
          <h2 className="item-headline">{item.headline}</h2>
          <p className="item-summary">{item.summary}</p>
          <p className="via">{formatVia(item)}</p>
        </div>
      </div>
    </a>
  );
}

export default async function Home({
  searchParams,
}: {
  searchParams: Promise<{ date?: string }>;
}) {
  const { date: dateParam } = await searchParams;
  const date = dateParam && DATE_RE.test(dateParam) ? dateParam : jstDate();
  const data = await getDaily(date);
  const featured = data.featured;
  const featuredKey = featured ? itemKey(featured) : null;
  const items = data.items.filter((item) => itemKey(item) !== featuredKey);
  // Screen shows max 3 per category; prefer one of each source when present.
  const sections = CATEGORIES.map((cat) => ({
    cat,
    items: pickThreePreferSources(items.filter((item) => item.category === cat)),
  })).filter((section) => section.items.length > 0);
  const prevDate = shiftDate(data.date, -1);
  const nextDate = shiftDate(data.date, 1);
  const indexNumbers = new Map<string, number>();
  let indexSeq = 0;
  for (const section of sections) {
    for (const item of section.items) {
      indexSeq += 1;
      indexNumbers.set(itemKey(item), indexSeq);
    }
  }

  return (
    <div className="page">
      <div className="page-inner">
        <header className="masthead">
          <div className="masthead-brand">
            <h1 className="logo">AI社員デイリー</h1>
            <p className="vol">VOL.001</p>
          </div>
          <p className="issue-date"><span className="issue-vol-sp">VOL.001 | </span>{formatIssueDate(data.date)}</p>
          <p className="tagline">Xから集めた、AI社員の作り方</p>
        </header>
        <nav className="issue-nav" aria-label="号の日付">
          <a className="issue-nav-link" href={`/?date=${prevDate}`}>
            ← 前日
          </a>
          <span className="issue-nav-current">{formatIssueDate(data.date)}</span>
          <a className="issue-nav-link" href={`/?date=${nextDate}`}>
            翌日 →
          </a>
        </nav>
        <main>
          <Featured item={featured} date={data.date} />
          <div className="index index-sp">
            <h2 className="index-heading">INDEX</h2>
            {sections.map(({ cat, items: catItems }) => (
              <section className="index-sp-cat" key={cat} aria-label={cat}>
                <h3 className="index-sp-cat-title">{cat}</h3>
                <ol className="index-sp-list">
                  {catItems.map((item) => (
                    <li className="index-item" key={itemKey(item)}>
                      <span className="index-num">
                        {String(indexNumbers.get(itemKey(item)) ?? 0).padStart(2, "0")}
                      </span>
                      <IndexStory item={item} />
                    </li>
                  ))}
                </ol>
              </section>
            ))}
          </div>
          <div className="index index-pc">
            {sections.map(({ cat, items: catItems }) => (
              <section className="index-col" key={cat} aria-label={cat}>
                <h2 className="index-col-title">{cat}</h2>
                <ul className="index-col-list">
                  {catItems.map((item) => (
                    <li className="index-item" key={itemKey(item)}>
                      <IndexStory item={item} />
                    </li>
                  ))}
                </ul>
              </section>
            ))}
          </div>
        </main>
      </div>
    </div>
  );
}
