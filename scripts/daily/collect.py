#!/usr/bin/env python3
"""PB1: 毎朝の号を自動で作る（依存なし・Python 3.10+ 標準ライブラリだけ）。

使い方:
  python3 scripts/daily/collect.py               # 今日(JST)の data/YYYY-MM-DD.json を作る
  python3 scripts/daily/collect.py --date 2026-10-22 --dry-run   # 書き込まない
  python3 scripts/daily/collect.py --validate data/2026-10-20.json  # 既存ファイルを検証だけ

環境変数:
  X_BEARER_TOKEN   X API v2 の Bearer Token（無ければ X なしで 20 件・"collection":"no-x"）
  OPENAI_API_KEY   OpenAI API キー（判定・見出し・要約に使う。必須）
  OPENAI_MODEL     既定 gpt-4o-mini
"""
import argparse, datetime as dt, glob, html, json, os, re, sys, urllib.parse, urllib.request
from collections import Counter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA = os.path.join(ROOT, "data")
JST = dt.timezone(dt.timedelta(hours=9))
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124 Safari/537.36"
CATS = ["事例", "ツール", "作り方"]
SRCS = ["x", "youtube", "web"]
TARGET = {"x": 9, "youtube": 6, "web": 5}
TOTAL = 20
WINDOW_DAYS = 90  # 公開3か月以内
X_QUERIES = [  # 1回の収集で3回まで・max_results<=20・次ページなし
    '"AI社員" -is:retweet lang:ja',
    '("AIエージェント" OR "デジタル社員") 業務 -is:retweet lang:ja',
    '"AI秘書" -is:retweet lang:ja',
]
YT_QUERIES = ["AI社員", "AIエージェント 業務", "AI秘書 作り方"]
WEB_QUERIES = ["AI社員", "AIエージェント 業務", "デジタル社員"]
ITEM_KEYS = ["time", "headline", "summary", "handle", "category", "url", "source", "thumbnail"]
FEATURED_KEYS = ["time", "headline", "summary", "handle", "category", "url", "source"]


def log(*a):
    print(*a, file=sys.stderr, flush=True)


def fallback_thumb(url):
    return f"/thumb-fallback/{sum(ord(c) for c in url) % 6}.jpg"


def http(url, headers=None, data=None, timeout=30):
    h = {"User-Agent": UA, "Accept-Language": "ja-JP,ja;q=0.9"}
    if "youtube.com" in url:
        h["Cookie"] = "SOCS=CAI; CONSENT=YES+cb"  # 同意画面（EU/データセンター向け）を飛ばす
    h.update(headers or {})
    req = urllib.request.Request(url, headers=h, data=data)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf8", "ignore")


def hhmm(t):
    """datetime -> JST の HH:MM。取れないときは今は既存どおり 00:00。"""
    return t.astimezone(JST).strftime("%H:%M") if t else "00:00"


# ---------------- 既存の号（だぶり確認用） ----------------
def seen_urls(exclude_date=None):
    s = set()
    for f in glob.glob(os.path.join(DATA, "2*.json")):
        if exclude_date and os.path.basename(f) == f"{exclude_date}.json":
            continue
        d = json.load(open(f, encoding="utf8"))
        s |= {i["url"] for i in d.get("items", [])}
        if d.get("featured"):
            s.add(d["featured"]["url"])
    return s


# ---------------- X ----------------
def collect_x(token, since):
    out = []
    for q in X_QUERIES[:3]:
        p = {"query": q, "max_results": "20", "start_time": since.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
             "tweet.fields": "created_at,author_id,attachments,public_metrics", "expansions": "author_id,attachments.media_keys",
             "user.fields": "username,name", "media.fields": "url,preview_image_url,type"}
        url = "https://api.twitter.com/2/tweets/search/recent?" + urllib.parse.urlencode(p)
        try:
            d = json.loads(http(url, {"Authorization": f"Bearer {token}"}))
        except Exception as e:
            log("X search failed:", q, e)
            if getattr(e, "code", None) in (401, 402, 403, 429):
                raise
            continue
        users = {u["id"]: u for u in d.get("includes", {}).get("users", [])}
        media = {m["media_key"]: m for m in d.get("includes", {}).get("media", [])}
        for t in d.get("data", []):  # next_token は使わない
            u = users.get(t["author_id"], {})
            name = u.get("username", "")
            thumb = None
            for k in t.get("attachments", {}).get("media_keys", []):
                m = media.get(k, {})
                thumb = m.get("url") or m.get("preview_image_url")
                if thumb:
                    break
            out.append({"source": "x", "url": f"https://x.com/{name}/status/{t['id']}", "handle": name,
                        "published": dt.datetime.fromisoformat(t["created_at"].replace("Z", "+00:00")),
                        "title": "", "text": t.get("text", ""), "thumbnail": thumb})
    return out


# ---------------- YouTube（検索ページを読む：yts.py 相当） ----------------
def _walk(o, key):
    if isinstance(o, dict):
        if key in o:
            yield o[key]
        for v in o.values():
            yield from _walk(v, key)
    elif isinstance(o, list):
        for v in o:
            yield from _walk(v, key)


def yt_published(vid):
    try:
        h = http(f"https://www.youtube.com/watch?v={vid}&hl=ja&gl=JP")
    except Exception as e:
        log("YouTube watch failed:", vid, e)
        return None, ""
    m = re.search(r'"(?:publishDate|uploadDate)":"([^"]+)"', h)
    desc = re.search(r'<meta name="description" content="([^"]*)"', h)
    t = None
    if m:
        s = m.group(1)
        try:
            t = dt.datetime.fromisoformat(s) if "T" in s else None
            if t is None:
                t = dt.datetime.fromisoformat(s[:10]).replace(tzinfo=JST)  # 時刻なし -> 00:00（既存どおり）
                t = t.replace(hour=0, minute=0)
                return t, html.unescape(desc.group(1)) if desc else ""
        except ValueError:
            t = None
    return t, html.unescape(desc.group(1)) if desc else ""


_FEEDS = {}


def yt_feed_published(channel_id, vid):
    """チャンネルの RSS から公開日時を取る（watch ページが読めないときの代わり）。"""
    if not channel_id:
        return None
    if channel_id not in _FEEDS:
        try:
            _FEEDS[channel_id] = http(f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}")
        except Exception as e:
            log("YouTube feed failed:", channel_id, e)
            _FEEDS[channel_id] = ""
    m = re.search(r"<yt:videoId>" + re.escape(vid) + r"</yt:videoId>.*?<published>([^<]+)</published>", _FEEDS[channel_id], re.S)
    if not m:
        return None
    try:
        return dt.datetime.fromisoformat(m.group(1))
    except ValueError:
        return None


def yt_relative(text, now=None):
    """検索結果の「3日前」「2 weeks ago」などから公開日時のめやすを出す（ほかで取れないときだけ）。"""
    now = now or dt.datetime.now(JST)
    m = re.search(r"(\d+)\s*(分|時間|日|週間|か月|ヶ月|年|minute|hour|day|week|month|year)", text or "")
    if not m:
        return None
    n, u = int(m.group(1)), m.group(2)
    if u in ("分", "minute"):
        return now - dt.timedelta(minutes=n)
    if u in ("時間", "hour"):
        return now - dt.timedelta(hours=n)
    days = {"日": 1, "day": 1, "週間": 7, "week": 7, "か月": 30, "ヶ月": 30, "month": 30, "年": 365, "year": 365}[u] * n
    d = (now - dt.timedelta(days=days)).date()
    return dt.datetime(d.year, d.month, d.day, tzinfo=JST)  # 時刻なし -> 00:00（既存どおり）


def collect_youtube():
    out, seen = [], set()
    for q in YT_QUERIES:
        h = ""
        for _ in range(2):  # ytInitialData が無い応答（ボット確認など）はもう1回だけ
            try:
                h = http("https://www.youtube.com/results?search_query=" + urllib.parse.quote(q) + "&sp=CAI%3D&hl=ja&gl=JP")
            except Exception as e:
                log("YouTube search failed:", q, e)
            if "ytInitialData" in h:
                break
        try:
            log("YT search", q, "bytes", len(h), "consent" if "consent." in h[:5000] else "", "has_data", "ytInitialData" in h)
            d = json.loads(re.search(r"var ytInitialData = (\{.*?\});</script>", h).group(1))
        except Exception as e:
            log("YouTube search failed:", q, e)
            continue
        vr = list(_walk(d, "videoRenderer"))
        log("YT renderers", q, len(vr), "lockups", len(list(_walk(d, "lockupViewModel"))))
        for v in vr[:15]:
            vid = v.get("videoId")
            if not vid or vid in seen:
                continue
            seen.add(vid)
            ch = (v.get("ownerText", {}).get("runs") or [{}])[0].get("text", "")
            title = "".join(r.get("text", "") for r in v.get("title", {}).get("runs", []))
            pub, desc = yt_published(vid)
            if not desc:
                desc = "".join(r.get("text", "") for r in (v.get("detailedMetadataSnippets") or [{}])[0].get("snippetText", {}).get("runs", []))
            if pub is None:
                cid = (v.get("ownerText", {}).get("runs") or [{}])[0].get("navigationEndpoint", {}).get("browseEndpoint", {}).get("browseId", "")
                pub = yt_feed_published(cid, vid)
            if pub is None:
                pub = yt_relative(v.get("publishedTimeText", {}).get("simpleText", ""))
            out.append({"source": "youtube", "url": f"https://www.youtube.com/watch?v={vid}", "handle": ch, "published": pub,
                        "title": title, "text": desc[:800], "thumbnail": f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"})
    log("YouTube candidates:", len(out), "with date:", sum(1 for c in out if c["published"]))
    return out


# ---------------- Web（PR TIMES の検索ページ + note の検索） ----------------
def og(url):
    try:
        h = http(url)
    except Exception:
        return None, None, "", None
    def meta(p):
        m = re.search(r'<meta[^>]+(?:property|name)=["\']' + p + r'["\'][^>]*content=["\']([^"\']*)', h) or \
            re.search(r'<meta[^>]+content=["\']([^"\']*)["\'][^>]*(?:property|name)=["\']' + p + '["\']', h)
        return html.unescape(m.group(1)) if m else None
    pub = None
    m = re.search(r'"datePublished":"([^"]+)"', h)
    if m:
        try:
            pub = dt.datetime.fromisoformat(m.group(1).replace(" ", "T"))
            pub = pub if pub.tzinfo else pub.replace(tzinfo=JST)  # PR TIMES は JST
        except ValueError:
            pub = None
    return meta("og:title"), meta("og:image"), meta("og:description") or meta("description") or "", pub


def collect_web():
    out, seen = [], set()
    for q in WEB_QUERIES:
        try:
            h = http("https://prtimes.jp/main/action.php?" + urllib.parse.urlencode({"run": "html", "page": "searchkey", "search_word": q}))
        except Exception as e:
            log("PR TIMES search failed:", q, e)
            h = ""
        for path in list(dict.fromkeys(re.findall(r'/main/html/rd/p/\d+\.\d+\.html', h)))[:10]:
            url = "https://prtimes.jp" + path
            if url in seen:
                continue
            seen.add(url)
            title, img, desc, pub = og(url)
            if not title:
                continue
            out.append({"source": "web", "url": url, "handle": "PR TIMES", "published": pub, "title": title,
                        "text": desc[:800], "thumbnail": img})
        try:
            d = json.loads(http("https://note.com/api/v3/searches?" + urllib.parse.urlencode({"context": "note", "q": q, "size": 10, "sort": "new"})))
            notes = d["data"]["notes"]["contents"]
        except Exception as e:
            log("note search failed:", q, e)
            notes = []
        for n in notes:
            u = n.get("user", {})
            url = f"https://note.com/{u.get('urlname')}/n/{n.get('key')}"
            if url in seen or not n.get("publish_at"):
                continue
            seen.add(url)
            out.append({"source": "web", "url": url, "handle": u.get("nickname") or u.get("urlname"),
                        "published": dt.datetime.fromisoformat(n["publish_at"]), "title": n.get("name", ""),
                        "text": (n.get("description") or n.get("body") or "")[:800], "thumbnail": n.get("eyecatch")})
    return out


# ---------------- OpenAI 判定 ----------------
PROMPT = """あなたは「AI社員」ニュースまとめサイトの編集者です。次の投稿・動画・記事について JSON で答えてください。
- is_ai_employee: 会社の仕事をAIに任せる「AI社員・AIエージェントを業務で働かせる」話なら true（一般的なAIニュースや宣伝だけは false）
- category: "事例"（導入・運用の実例や調査）/"ツール"（製品・サービス・発表）/"作り方"（作り方・手順・使い方）のどれか
- headline: 日本語の見出し 60字以内。何が起きたかを具体的に、煽らない
- summary: 日本語の要約 1〜2文・120字以内。本文に無いことは書かない
返す形: {"is_ai_employee": bool, "category": str, "headline": str, "summary": str}"""


def classify(c, key, model):
    body = json.dumps({"model": model, "response_format": {"type": "json_object"}, "temperature": 0.2,
                       "messages": [{"role": "system", "content": PROMPT},
                                    {"role": "user", "content": json.dumps({"source": c["source"], "author": c["handle"], "title": c["title"],
                                                                            "text": c["text"][:1500], "url": c["url"]}, ensure_ascii=False)}]}).encode()
    r = json.loads(http("https://api.openai.com/v1/chat/completions",
                        {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}, data=body, timeout=60))
    j = json.loads(r["choices"][0]["message"]["content"])
    if j.get("category") not in CATS or not j.get("headline") or not j.get("summary"):
        return None
    return j


# ---------------- 選ぶ・組み立てる ----------------
def thumb_ok(t):
    return bool(t) and "pbs.twimg.com/card_img" not in t


def to_item(c):
    return {"time": hhmm(c["published"]), "headline": c["headline"], "summary": c["summary"], "handle": c["handle"],
            "category": c["category"], "url": c["url"], "source": c["source"],
            "thumbnail": c["thumbnail"] if thumb_ok(c.get("thumbnail")) else fallback_thumb(c["url"])}


def select(cands, no_x):
    """cands は判定済み（is_ai_employee=True）・新しい順。featured 1件 + items 20件を選ぶ。"""
    used_handles, used_urls = set(), set()
    pick = {s: [] for s in SRCS}
    target = dict(TARGET)
    if no_x:
        target = {"x": 0, "youtube": 0, "web": 0}
    def ok(c):
        if c["url"] in used_urls:
            return False
        if c["source"] in ("x", "youtube") and (c["source"], c["handle"]) in used_handles:
            return False
        return True
    def take(c):
        used_urls.add(c["url"]); used_handles.add((c["source"], c["handle"])); pick[c["source"]].append(c)
    featured = next((c for c in cands if c["source"] == "web"), None) or (cands[0] if cands else None)
    if featured:
        used_urls.add(featured["url"])
    for s in SRCS:  # まず目安どおり
        for c in cands:
            if len(pick[s]) >= target[s]:
                break
            if c["source"] == s and ok(c):
                take(c)
    for c in cands:  # 足りない分はほかの出どころで埋める
        if sum(map(len, pick.values())) >= TOTAL:
            break
        if (no_x and c["source"] == "x") or not ok(c):
            continue
        take(c)
    chosen = [c for s in SRCS for c in pick[s]]
    by_cat = {k: [c for c in chosen if c["category"] == k] for k in CATS}
    items = []
    for k in CATS:  # build.py と同じ並べ方：列の中で x→youtube→web を順に
        q = {s: [to_item(c) for c in by_cat[k] if c["source"] == s] for s in SRCS}
        while any(q.values()):
            for s in SRCS:
                if q[s]:
                    items.append(q[s].pop(0))
    f = None
    if featured:
        f = {k: v for k, v in to_item(featured).items() if k in FEATURED_KEYS}
    return f, items


def build_issue(date, featured, items, no_x):
    d = {"date": date.isoformat(), "featured": featured, "items": items}
    if no_x:
        d["collection"] = "no-x"
    return d


# ---------------- 検証（既存の決まり） ----------------
def validate(d, seen, pub=None, today=None):
    """問題の一覧を返す（空なら OK）。pub は url->公開日(date) の辞書（あれば3か月を確かめる）。"""
    errs = []
    keys = list(d)
    if keys[:3] != ["date", "featured", "items"] or any(k not in ("date", "featured", "items", "collection") for k in keys):
        errs.append(f"top keys {keys}")
    if d.get("collection") not in (None, "no-x"):
        errs.append("collection must be no-x")
    items = d.get("items", [])
    if len(items) != TOTAL:
        errs.append(f"items {len(items)} != {TOTAL}")
    if d.get("featured") is not None and list(d["featured"]) != FEATURED_KEYS:
        errs.append(f"featured keys {list(d['featured'])}")
    for i in items:
        if list(i) != ITEM_KEYS:
            errs.append(f"item keys {list(i)} {i.get('url')}")
        if i.get("category") not in CATS or i.get("source") not in SRCS:
            errs.append(f"bad category/source {i.get('url')}")
        if not re.fullmatch(r"\d\d:\d\d", i.get("time", "")):
            errs.append(f"bad time {i.get('url')}")
        t = i.get("thumbnail", "")
        if not t or "card_img" in t:
            errs.append(f"bad thumbnail {i.get('url')}")
        if t.startswith("/thumb-fallback/") and t != fallback_thumb(i["url"]):
            errs.append(f"fallback formula {i['url']}")
    urls = [i.get("url") for i in items] + ([d["featured"]["url"]] if d.get("featured") else [])
    if len(set(urls)) != len(urls):
        errs.append("duplicate url in issue")
    if set(urls) & seen:
        errs.append(f"overlap with previous issues {sorted(set(urls) & seen)}")
    hc = Counter((i.get("source"), i.get("handle")) for i in items if i.get("source") in ("x", "youtube"))
    errs += [f"same account twice {k}" for k, n in hc.items() if n > 1]
    if d.get("collection") == "no-x" and any(i["source"] == "x" for i in items):
        errs.append("no-x issue has x items")
    if pub and today:
        cut = today - dt.timedelta(days=WINDOW_DAYS)
        errs += [f"out of 3 months {u} {p}" for u, p in pub.items() if u in urls and not (cut <= p <= today)]
    return errs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--validate", nargs="+")
    a = ap.parse_args()
    if a.validate:
        bad = 0
        for f in a.validate:
            d = json.load(open(f, encoding="utf8"))
            e = validate(d, seen_urls(exclude_date=d["date"]))
            print(("OK  " if not e else "NG  ") + f, *e[:5], sep="\n    " if e else "")
            bad += bool(e)
        sys.exit(1 if bad else 0)

    today = dt.date.fromisoformat(a.date) if a.date else dt.datetime.now(JST).date()
    out = os.path.join(DATA, f"{today}.json")
    if os.path.exists(out):
        log("already exists:", out); return
    key, model = os.environ.get("OPENAI_API_KEY"), os.environ.get("OPENAI_MODEL") or "gpt-4o-mini"
    if not key:
        sys.exit("OPENAI_API_KEY がありません")
    now = dt.datetime.now(JST)
    since = now - dt.timedelta(days=3)
    seen = seen_urls()
    no_x = False
    raw = []
    token = os.environ.get("X_BEARER_TOKEN")
    if token:
        try:
            raw += collect_x(token, since)
        except Exception as e:
            log("X unavailable -> no-x:", e); no_x = True
        if not any(c["source"] == "x" for c in raw):
            no_x = True
    else:
        no_x = True
    raw += collect_youtube() + collect_web()
    cut = today - dt.timedelta(days=WINDOW_DAYS)
    cands, pub = [], {}
    for c in raw:
        if c["url"] in seen or not c["published"]:
            continue
        p = c["published"].astimezone(JST).date()
        if not (cut <= p <= today):
            continue
        try:
            j = classify(c, key, model)
        except Exception as e:
            log("classify failed:", c["url"], e); continue
        if not j or not j.get("is_ai_employee"):
            continue
        c.update(category=j["category"], headline=j["headline"].strip(), summary=j["summary"].strip())
        cands.append(c); pub[c["url"]] = p
    cands.sort(key=lambda c: c["published"], reverse=True)
    featured, items = select(cands, no_x)
    d = build_issue(today, featured, items, no_x)
    errs = validate(d, seen, pub, today)
    log("sources", Counter(i["source"] for i in items), "categories", Counter(i["category"] for i in items), "no_x", no_x)
    if errs:
        log("validation failed:", *errs, sep="\n  "); sys.exit(1)
    if a.dry_run:
        print(json.dumps(d, ensure_ascii=False, indent=2)); return
    with open(out, "w", encoding="utf8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2); f.write("\n")
    print(out)


if __name__ == "__main__":
    main()
