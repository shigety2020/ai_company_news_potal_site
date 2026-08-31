import { headers } from "next/headers";

export const dynamic = "force-dynamic";

type Category = "作り方" | "ツール" | "事例";

type DailyItem = {
  time: string;
  headline: string;
  summary: string;
  handle: string;
  category: Category;
  url: string;
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

function emptyDaily(date: string): DailyResponse {
  return { date, featured: null, items: [] };
}

function itemKey(item: DailyItem): string {
  return `${item.url}::${item.headline}`;
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

function Photo({ src }: { src?: string | null }) {
  if (src) {
    return (
      <div className="photo">
        {/* Seed has no images; keep a plain <img> if a URL appears later. */}
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src={src} alt="" />
      </div>
    );
  }
  return <div className="photo" aria-hidden="true" />;
}

function Featured({ item }: { item: DailyItem | null }) {
  return (
    <section className="featured" aria-label="本日の特集">
      <Photo src={item?.image} />
      {item ? (
        <a className="featured-body story" href={item.url} target="_blank" rel="noreferrer">
          <div className="kicker-row">
            <span className="kicker">{item.category}</span>
            <time className="time" dateTime={item.time}>
              {item.time}
            </time>
          </div>
          <h2 className="featured-headline">{item.headline}</h2>
          <p className="summary">{item.summary}</p>
          <p className="via">via @{item.handle}</p>
        </a>
      ) : (
        <div className="featured-body is-empty" aria-hidden="true" />
      )}
    </section>
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

  return (
    <div className="page">
      <div className="page-inner">
        <header className="masthead">
          <h1 className="logo">AI社員デイリー</h1>
          <p className="issue-date">{formatIssueDate(data.date)}</p>
        </header>
        <ul className="cats" aria-label="カテゴリ">
          {CATEGORIES.map((cat) => (
            <li key={cat}>{cat}</li>
          ))}
        </ul>
        <main>
          <Featured item={featured} />
          <ol className="index">
            {items.map((item, i) => (
              <li className="index-item" key={itemKey(item)}>
                <span className="index-num">{String(i + 1).padStart(2, "0")}</span>
                <a className="story" href={item.url} target="_blank" rel="noreferrer">
                  <div className="kicker-row">
                    <time className="time" dateTime={item.time}>
                      {item.time}
                    </time>
                    <span className="kicker">{item.category}</span>
                  </div>
                  <h2 className="item-headline">{item.headline}</h2>
                  <p className="item-summary">{item.summary}</p>
                  <p className="via">via @{item.handle}</p>
                </a>
              </li>
            ))}
          </ol>
        </main>
        <footer className="quote">
          役割を決めて、手順にして、任せる。
          <small>AI社員デイリー</small>
        </footer>
      </div>
    </div>
  );
}
