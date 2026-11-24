"""キー無しのテスト: python3 -m unittest scripts/daily/test_collect.py"""
import datetime as dt, glob, io, json, os, sys, unittest, urllib.error, urllib.parse
sys.path.insert(0, os.path.dirname(__file__))
import collect as C


def cand(src, n, handle=None, cat="事例", thumb=None):
    u = {"x": f"https://x.com/h{n}/status/{n}", "youtube": f"https://www.youtube.com/watch?v=v{n}", "web": f"https://example.com/{n}"}[src]
    return {"source": src, "url": u, "handle": handle or f"{src}{n}", "category": cat, "headline": f"h{n}", "summary": "s",
            "published": dt.datetime(2026, 10, 20, 8, n % 60, tzinfo=C.JST), "thumbnail": thumb}


class T(unittest.TestCase):
    def test_existing_data_valid(self):
        files = sorted(glob.glob(os.path.join(C.DATA, "2*.json")))
        for f in files:
            d = json.load(open(f, encoding="utf8"))
            if not d.get("items") or d["date"] < "2026-10-05":
                continue  # 空の号と、今の決まり（だぶりなし・1アカウント1件・サムネ式）より前の号は対象外
            e = [x for x in C.validate(d, C.seen_urls(exclude_date=d["date"])) if not x.startswith("items ")]
            self.assertEqual(e, [], f)

    def test_yt_relative(self):
        now = dt.datetime(2026, 10, 23, 7, 0, tzinfo=C.JST)
        self.assertEqual(C.yt_relative("3日前", now), dt.datetime(2026, 10, 20, tzinfo=C.JST))
        self.assertEqual(C.yt_relative("2 時間前", now), dt.datetime(2026, 10, 23, 5, 0, tzinfo=C.JST))
        self.assertEqual(C.yt_relative("ストリーム配信: 1 週間前", now).date(), dt.date(2026, 10, 16))
        self.assertIsNone(C.yt_relative("", now))

    def test_yt_feed(self):
        C._FEEDS["UCx"] = "<entry><yt:videoId>abc</yt:videoId><published>2026-10-20T09:00:00+00:00</published></entry>"
        self.assertEqual(C.yt_feed_published("UCx", "abc").astimezone(C.JST).hour, 18)
        self.assertIsNone(C.yt_feed_published("UCx", "zzz"))

    def test_fallback(self):
        u = "https://x.com/DeNAAIshain/status/2112409727141634365"
        self.assertEqual(C.fallback_thumb(u), "/thumb-fallback/0.jpg")

    def test_select_normal(self):
        cs = [cand("web", 0)] + [cand("x", i) for i in range(1, 15)] + [cand("youtube", i) for i in range(20, 30)] + [cand("web", i) for i in range(30, 40)]
        cs.append(cand("x", 99, handle="x1"))  # 同じアカウント
        cs.append(cand("x", 98, thumb="https://pbs.twimg.com/card_img/1/a.jpg"))
        f, items = C.select(cs, no_x=False)
        d = C.build_issue(dt.date(2026, 10, 22), f, items, False)
        self.assertEqual(C.validate(d, set()), [])
        from collections import Counter
        self.assertEqual(Counter(i["source"] for i in items), {"x": 9, "youtube": 6, "web": 5})
        self.assertNotIn("collection", d)

    def test_select_no_x(self):
        cs = [cand("youtube", i) for i in range(20, 32)] + [cand("web", i) for i in range(30, 45)] + [cand("x", 1)]
        f, items = C.select(cs, no_x=True)
        d = C.build_issue(dt.date(2026, 10, 22), f, items, True)
        self.assertEqual(C.validate(d, set()), [])
        self.assertEqual(d["collection"], "no-x")
        self.assertFalse(any(i["source"] == "x" for i in items))

    def test_overlap_and_window(self):
        cs = [cand("web", 0)] + [cand("x", i) for i in range(1, 15)] + [cand("youtube", i) for i in range(20, 30)] + [cand("web", i) for i in range(30, 40)]
        f, items = C.select(cs, no_x=False)
        d = C.build_issue(dt.date(2026, 10, 22), f, items, False)
        self.assertTrue(C.validate(d, {items[0]["url"]}))
        self.assertTrue(C.validate(d, set(), {items[0]["url"]: dt.date(2026, 6, 1)}, dt.date(2026, 10, 22)))

    def test_single_web_stays_in_items(self):
        cs = [cand("web", 0)] + [cand("x", i) for i in range(1, 15)] + [cand("youtube", i) for i in range(20, 30)]
        f, items = C.select(cs, no_x=False)
        d = C.build_issue(dt.date(2026, 10, 22), f, items, False)
        self.assertEqual(C.validate(d, set()), [])
        self.assertNotEqual(f["source"], "web")
        self.assertEqual(sum(1 for i in items if i["source"] == "web"), 1)

    def test_two_webs_featured_web_and_one_in_items(self):
        cs = [cand("web", 0), cand("web", 30)] + [cand("x", i) for i in range(1, 15)] + [cand("youtube", i) for i in range(20, 30)]
        f, items = C.select(cs, no_x=False)
        self.assertEqual(f["source"], "web")
        self.assertEqual(sum(1 for i in items if i["source"] == "web"), 1)

    def test_only_web_featured_web(self):
        f, items = C.select([cand("web", 0)], no_x=True)
        self.assertEqual(f["source"], "web")

    def test_web_queries_and_limit(self):
        src = open(C.__file__, encoding="utf8").read()
        self.assertIn("h)))[:20]", src)
        self.assertTrue(all("導入" in q or "業務" in q for q in C.WEB_QUERIES))


class RefetchPublishDate(unittest.TestCase):
    """公開日なしの YouTube を、絞り込む前にもう一度取り直す（通信なし）。"""

    def setUp(self):
        C._FEEDS.clear()
        C._PLAYER_CALLS[0] = 0

    def test_yt_video_id(self):
        self.assertEqual(C.yt_video_id("https://www.youtube.com/watch?v=IMolcog2r68"), "IMolcog2r68")
        self.assertIsNone(C.yt_video_id("https://example.com/x"))

    def test_refetch_uses_watch_when_time_present(self):
        pub = dt.datetime(2026, 11, 10, 9, 15, tzinfo=C.JST)
        def fake_published(vid, timeout=30):
            self.assertEqual(vid, "abc123")
            self.assertEqual(timeout, C.YT_REFETCH_TIMEOUT)
            return pub, "desc"
        def fail_feed(*_a, **_k):
            self.fail("watch で時刻が取れたときは feed を呼ばない")
        orig_p, orig_f = C.yt_published, C.yt_feed_published
        C.yt_published, C.yt_feed_published = fake_published, fail_feed
        try:
            self.assertEqual(C.yt_refetch_published("abc123", "UCx"), pub)
        finally:
            C.yt_published, C.yt_feed_published = orig_p, orig_f

    def test_refetch_falls_back_to_feed_when_watch_is_date_only(self):
        date_only = dt.datetime(2026, 11, 10, 0, 0, tzinfo=C.JST)
        feed_pub = dt.datetime(2026, 11, 10, 9, 0, tzinfo=dt.timezone.utc)
        def fake_published(vid, timeout=30):
            return date_only, ""
        def fake_feed(channel_id, vid, timeout=30, refresh=False):
            self.assertTrue(refresh)
            self.assertEqual(timeout, C.YT_REFETCH_TIMEOUT)
            self.assertEqual((channel_id, vid), ("UCx", "abc123"))
            return feed_pub
        orig_p, orig_f = C.yt_published, C.yt_feed_published
        C.yt_published, C.yt_feed_published = fake_published, fake_feed
        try:
            self.assertEqual(C.yt_refetch_published("abc123", "UCx"), feed_pub)
        finally:
            C.yt_published, C.yt_feed_published = orig_p, orig_f

    def test_refetch_returns_none_when_both_fail(self):
        def fake_published(vid, timeout=30):
            return None, ""
        def fake_feed(channel_id, vid, timeout=30, refresh=False):
            return None
        orig_p, orig_f = C.yt_published, C.yt_feed_published
        C.yt_published, C.yt_feed_published = fake_published, fake_feed
        try:
            self.assertIsNone(C.yt_refetch_published("abc123", "UCx"))
        finally:
            C.yt_published, C.yt_feed_published = orig_p, orig_f

    def test_refetch_discards_date_only_without_feed(self):
        date_only = dt.datetime(2026, 11, 10, 0, 0, tzinfo=C.JST)
        def fake_published(vid, timeout=30):
            return date_only, ""
        def fake_feed(channel_id, vid, timeout=30, refresh=False):
            return None
        orig_p, orig_f = C.yt_published, C.yt_feed_published
        C.yt_published, C.yt_feed_published = fake_published, fake_feed
        try:
            self.assertIsNone(C.yt_refetch_published("abc123", "UCx"))
        finally:
            C.yt_published, C.yt_feed_published = orig_p, orig_f

    def test_refill_fills_missing_only_and_skips_existing(self):
        recovered_pub = dt.datetime(2026, 11, 10, 8, 30, tzinfo=C.JST)
        already = dt.datetime(2026, 11, 9, 12, 0, tzinfo=C.JST)
        cands = [
            {"source": "youtube", "url": "https://www.youtube.com/watch?v=miss1", "published": None, "channel_id": "UCa"},
            {"source": "youtube", "url": "https://www.youtube.com/watch?v=has1", "published": already, "channel_id": "UCb"},
            {"source": "web", "url": "https://example.com/1", "published": None},
        ]
        called = []
        def fake_refetch(vid, channel_id=None, timeout=8, refresh_feed=True):
            called.append((vid, channel_id, timeout, refresh_feed))
            return recovered_pub
        orig = C.yt_refetch_published
        C.yt_refetch_published = fake_refetch
        try:
            n = C.refill_youtube_dates(cands)
        finally:
            C.yt_refetch_published = orig
        self.assertEqual(n, 1)
        self.assertEqual(cands[0]["published"], recovered_pub)
        self.assertEqual(cands[1]["published"], already)
        self.assertIsNone(cands[2]["published"])
        self.assertEqual(called, [("miss1", "UCa", C.YT_REFETCH_TIMEOUT, True)])

    def test_refill_still_none_when_retry_fails(self):
        cands = [{"source": "youtube", "url": "https://www.youtube.com/watch?v=miss1", "published": None, "channel_id": "UCa"}]
        orig = C.yt_refetch_published
        C.yt_refetch_published = lambda *a, **k: None
        try:
            self.assertEqual(C.refill_youtube_dates(cands), 0)
        finally:
            C.yt_refetch_published = orig
        self.assertIsNone(cands[0]["published"])

    def test_refill_refreshes_feed_once_per_channel(self):
        called = []
        def fake_refetch(vid, channel_id=None, timeout=8, refresh_feed=True):
            called.append((vid, channel_id, refresh_feed))
            return None
        cands = [
            {"source": "youtube", "url": "https://www.youtube.com/watch?v=a1", "published": None, "channel_id": "UCz"},
            {"source": "youtube", "url": "https://www.youtube.com/watch?v=a2", "published": None, "channel_id": "UCz"},
        ]
        orig = C.yt_refetch_published
        C.yt_refetch_published = fake_refetch
        try:
            C.refill_youtube_dates(cands)
        finally:
            C.yt_refetch_published = orig
        self.assertEqual(called, [("a1", "UCz", True), ("a2", "UCz", False)])

    def test_refetch_passes_short_timeout_to_http(self):
        seen = []
        def fake_http(url, headers=None, data=None, timeout=30):
            seen.append((url, timeout))
            raise TimeoutError("no network in tests")
        orig = C.http
        C.http = fake_http
        try:
            self.assertIsNone(C.yt_refetch_published("abc123", "UCx", timeout=8))
        finally:
            C.http = orig
        self.assertEqual(len(seen), 3)
        self.assertIn("watch?v=abc123", seen[0][0])
        self.assertEqual(seen[0][1], 8)
        self.assertIn("youtubei/v1/player", seen[1][0])
        self.assertEqual(seen[1][1], 8)
        self.assertIn("channel_id=UCx", seen[2][0])
        self.assertEqual(seen[2][1], 8)

    def test_yt_published_uses_player_when_watch_has_no_date(self):
        pub = "2026-11-10T09:15:00+09:00"
        def fake_http(url, headers=None, data=None, timeout=30):
            if "watch?v=" in url:
                return "<html><title>no dates</title></html>"
            if "youtubei/v1/player" in url:
                self.assertEqual(timeout, 8)
                self.assertEqual((headers or {}).get("Content-Type"), "application/json")
                body = json.loads(data.decode())
                self.assertEqual(body["videoId"], "abc123")
                return json.dumps({
                    "microformat": {"playerMicroformatRenderer": {"publishDate": pub}},
                    "videoDetails": {"shortDescription": "hello"},
                })
            self.fail(url)
        orig = C.http
        C.http = fake_http
        try:
            t, desc = C.yt_published("abc123", timeout=8)
        finally:
            C.http = orig
        self.assertEqual(t, dt.datetime.fromisoformat(pub))
        self.assertEqual(desc, "hello")

    def test_yt_published_skips_player_when_watch_has_time(self):
        def fake_http(url, headers=None, data=None, timeout=30):
            if "watch?v=" in url:
                return '"publishDate":"2026-11-10T09:15:00+09:00"<meta name="description" content="d">'
            self.fail("watch で時刻が取れたときは player を呼ばない")
        orig = C.http
        C.http = fake_http
        try:
            t, desc = C.yt_published("abc123")
        finally:
            C.http = orig
        self.assertEqual(t, dt.datetime.fromisoformat("2026-11-10T09:15:00+09:00"))
        self.assertEqual(desc, "d")

    def test_yt_published_uses_player_when_watch_is_date_only(self):
        def fake_http(url, headers=None, data=None, timeout=30):
            if "watch?v=" in url:
                return '"publishDate":"2026-11-10"'
            if "youtubei/v1/player" in url:
                return json.dumps({"microformat": {"playerMicroformatRenderer": {"publishDate": "2026-11-10T09:15:00+09:00"}}})
            self.fail(url)
        orig = C.http
        C.http = fake_http
        try:
            t, _desc = C.yt_published("abc123")
        finally:
            C.http = orig
        self.assertEqual(t, dt.datetime.fromisoformat("2026-11-10T09:15:00+09:00"))

    def test_refetch_uses_player_before_feed_when_watch_fails(self):
        pub = dt.datetime(2026, 11, 10, 9, 15, tzinfo=C.JST)
        def fake_http(url, headers=None, data=None, timeout=30):
            if "watch?v=" in url:
                return "<html></html>"
            if "youtubei/v1/player" in url:
                return json.dumps({"microformat": {"playerMicroformatRenderer": {"publishDate": pub.isoformat()}}})
            self.fail("player で時刻が取れたときは feed を呼ばない")
        orig = C.http
        C.http = fake_http
        try:
            self.assertEqual(C.yt_refetch_published("abc123", "UCx"), pub)
        finally:
            C.http = orig

    def test_player_timeout_is_capped_at_8(self):
        seen = []
        def fake_http(url, headers=None, data=None, timeout=30):
            seen.append(timeout)
            return "{}"
        orig = C.http
        C.http = fake_http
        try:
            C.yt_player_published("abc", timeout=30)
        finally:
            C.http = orig
        self.assertEqual(seen, [8])

    def test_player_stops_after_max_calls(self):
        calls = []
        def fake_http(url, headers=None, data=None, timeout=30):
            calls.append(url)
            raise TimeoutError("slow")
        orig = C.http
        C.http = fake_http
        try:
            for i in range(C.YT_PLAYER_MAX_CALLS + 10):
                self.assertEqual(C.yt_player_published(f"v{i}"), (None, ""))
        finally:
            C.http = orig
        self.assertEqual(len(calls), C.YT_PLAYER_MAX_CALLS)

    def test_player_unexpected_json_shape_does_not_raise(self):
        bodies = ["[]", '"x"', '{"microformat": []}', '{"microformat": {"playerMicroformatRenderer": {"publishDate": 5}}}', "not json"]
        orig = C.http
        try:
            for b in bodies:
                C.http = lambda url, headers=None, data=None, timeout=30, b=b: b
                self.assertEqual(C.yt_player_published("abc"), (None, ""))
        finally:
            C.http = orig

    def test_window_filter_untouched(self):

        src = open(C.__file__, encoding="utf8").read()
        self.assertIn("refill_youtube_dates(raw, seen=seen)", src)
        self.assertNotIn("refill_youtube_dates(out)", src)
        self.assertIn("cut = today - dt.timedelta(days=WINDOW_DAYS)", src)
        self.assertIn("if not (cut <= p <= today):", src)
        # 絞り込みは seen → no_date → 00:00 → 窓 → 判定のまま
        i_seen = src.index('if c["url"] in seen or not c["published"]:')
        i_midnight = src.index('if hhmm(c["published"]) == "00:00":')
        i_window = src.index("if not (cut <= p <= today):")
        i_classify = src.index("j = classify(c, key, model)")
        self.assertLess(i_seen, i_midnight)
        self.assertLess(i_midnight, i_window)
        self.assertLess(i_window, i_classify)

    def test_refill_skips_seen_url(self):
        recovered_pub = dt.datetime(2026, 11, 10, 8, 30, tzinfo=C.JST)
        cands = [
            {"source": "youtube", "url": "https://www.youtube.com/watch?v=seen1", "published": None, "channel_id": "UCa"},
            {"source": "youtube", "url": "https://www.youtube.com/watch?v=miss1", "published": None, "channel_id": "UCb"},
        ]
        called = []
        def fake_refetch(vid, channel_id=None, timeout=8, refresh_feed=True):
            called.append(vid)
            return recovered_pub
        orig = C.yt_refetch_published
        C.yt_refetch_published = fake_refetch
        try:
            n = C.refill_youtube_dates(cands, seen={"https://www.youtube.com/watch?v=seen1"})
        finally:
            C.yt_refetch_published = orig
        self.assertEqual(n, 1)
        self.assertIsNone(cands[0]["published"])
        self.assertEqual(cands[1]["published"], recovered_pub)
        self.assertEqual(called, ["miss1"])

    def test_refill_continues_after_one_raises(self):
        recovered_pub = dt.datetime(2026, 11, 10, 8, 30, tzinfo=C.JST)
        cands = [
            {"source": "youtube", "url": "https://www.youtube.com/watch?v=boom", "published": None, "channel_id": "UCa"},
            {"source": "youtube", "url": "https://www.youtube.com/watch?v=ok1", "published": None, "channel_id": "UCb"},
        ]
        def fake_refetch(vid, channel_id=None, timeout=8, refresh_feed=True):
            if vid == "boom":
                raise RuntimeError("boom")
            return recovered_pub
        orig = C.yt_refetch_published
        C.yt_refetch_published = fake_refetch
        try:
            n = C.refill_youtube_dates(cands)
        finally:
            C.yt_refetch_published = orig
        self.assertEqual(n, 1)
        self.assertIsNone(cands[0]["published"])
        self.assertEqual(cands[1]["published"], recovered_pub)

    def test_refill_failure_log_includes_exception_type(self):
        cands = [{"source": "youtube", "url": "https://www.youtube.com/watch?v=boom", "published": None, "channel_id": "UCa"}]
        def fake_refetch(*_a, **_k):
            raise TimeoutError("boom")
        orig = C.yt_refetch_published
        buf = io.StringIO()
        C.yt_refetch_published = fake_refetch
        orig_err = sys.stderr
        try:
            sys.stderr = buf
            C.refill_youtube_dates(cands)
        finally:
            sys.stderr = orig_err
            C.yt_refetch_published = orig
        logged = buf.getvalue()
        self.assertIn("YouTube date refetch failed:", logged)
        self.assertIn("TimeoutError", logged)
        self.assertIn("boom", logged)


class YtQueryRotation(unittest.TestCase):
    """号の日付から YouTube 検索語を決める（通信なし）。"""

    def test_same_date_same_queries(self):
        d = dt.date(2026, 11, 11)
        self.assertEqual(C.yt_queries_for_date(d), C.yt_queries_for_date(d))
        self.assertEqual(C.yt_queries_for_date(d), C.yt_queries_for_date(dt.date(2026, 11, 11)))

    def test_different_dates_change_queries(self):
        a = C.yt_queries_for_date(dt.date(2026, 11, 11))
        b = C.yt_queries_for_date(dt.date(2026, 11, 12))
        self.assertNotEqual(a, b)

    def test_base_queries_always_included(self):
        for d in (dt.date(2026, 11, 11), dt.date(2026, 11, 12), dt.date(2026, 12, 1), dt.date(2027, 1, 1)):
            q = C.yt_queries_for_date(d)
            for base in C.YT_BASE_QUERIES:
                self.assertIn(base, q, d)

    def test_query_count_within_limit(self):
        self.assertLessEqual(C.YT_QUERY_LIMIT, 3 + 1)  # 現行3に対し +1 まで
        self.assertEqual(C.YT_QUERY_LIMIT, 4)
        for i in range(40):
            d = dt.date(2026, 11, 11) + dt.timedelta(days=i)
            q = C.yt_queries_for_date(d)
            self.assertLessEqual(len(q), C.YT_QUERY_LIMIT, d)
            self.assertEqual(len(q), len(set(q)), d)
            self.assertGreaterEqual(len(q), len(C.YT_BASE_QUERIES), d)

    def test_collect_uses_date_queries(self):
        src = open(C.__file__, encoding="utf8").read()
        self.assertIn("collect_youtube(today)", src)
        self.assertIn("yt_queries_for_date(", src)
        self.assertNotIn("YT_QUERIES =", src)
        self.assertNotIn("for q in YT_QUERIES", src)


class YtDataApi(unittest.TestCase):
    """YouTube Data API v3（search.list -> videos.list）。通信はモック。"""

    def setUp(self):
        self.orig_http, self.orig_scrape = C.http, C.collect_youtube_scrape
        self.calls, self.scraped = [], []
        self.err = io.StringIO()
        self.orig_stderr = sys.stderr
        sys.stderr = self.err

        def scrape(queries):
            self.scraped.append(list(queries))
            return []
        C.collect_youtube_scrape = scrape

    def tearDown(self):
        C.http, C.collect_youtube_scrape = self.orig_http, self.orig_scrape
        sys.stderr = self.orig_stderr

    def fake_ok(self, url, headers=None, data=None, timeout=30):
        self.calls.append(url)
        q = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
        if "/youtube/v3/search?" in url:
            n = len([c for c in self.calls if "/search?" in c])
            items = [{"id": {"kind": "youtube#video", "videoId": f"v{n}{i}"},
                      "snippet": {"title": "t &amp; x", "channelTitle": f"ch{n}{i}", "channelId": f"UC{n}{i}"}} for i in range(3)]
            return json.dumps({"items": items})
        if "/youtube/v3/videos?" in url:
            ids = q["id"][0].split(",")
            return json.dumps({"items": [{"id": v, "snippet": {
                "publishedAt": "2026-11-20T03:04:05Z", "title": "T & x", "description": "desc " + v,
                "channelTitle": "ch " + v, "channelId": "UC" + v,
                "thumbnails": {"default": {"url": "d.jpg"}, "high": {"url": f"https://i.ytimg.com/vi/{v}/hqdefault.jpg"}}}} for v in ids]})
        raise AssertionError(url)

    def test_search_then_videos_gives_dates(self):
        C.http = self.fake_ok
        out = C.collect_youtube(dt.date(2026, 11, 24), key="K")
        qs = C.yt_queries_for_date(dt.date(2026, 11, 24))
        searches = [c for c in self.calls if "/search?" in c]
        videos = [c for c in self.calls if "/videos?" in c]
        self.assertEqual(len(searches), len(qs))
        self.assertEqual(len(videos), 1)
        p = urllib.parse.parse_qs(urllib.parse.urlparse(searches[0]).query)
        self.assertEqual(p["part"], ["snippet"]); self.assertEqual(p["type"], ["video"])
        self.assertEqual(p["regionCode"], ["JP"]); self.assertEqual(p["relevanceLanguage"], ["ja"])
        self.assertEqual(p["q"], [qs[0]])
        self.assertEqual(p["publishedAfter"], ["2026-08-25T15:00:00Z"])  # 90日前の 0:00 JST
        self.assertEqual(len(out), 3 * len(qs))
        self.assertTrue(all(c["published"] for c in out))
        c = out[0]
        self.assertEqual(set(c), {"source", "url", "handle", "published", "title", "text", "thumbnail", "channel_id"})
        self.assertEqual(c["source"], "youtube")
        self.assertEqual(C.hhmm(c["published"]), "12:04")
        self.assertEqual(c["url"], "https://www.youtube.com/watch?v=v10")
        self.assertEqual(c["thumbnail"], "https://i.ytimg.com/vi/v10/hqdefault.jpg")
        self.assertEqual(c["title"], "T & x")
        self.assertEqual(self.scraped, [])
        self.assertEqual(C.YT_STATS["units"], len(qs) * 100 + 1)
        log = self.err.getvalue()
        self.assertIn(f"YouTube API: searches {len(qs)} items {len(out)} with date {len(out)} units {len(qs) * 100 + 1}", log)
        self.assertNotIn("K", [w for w in log.split()])  # キーはログに出ない
        self.assertNotIn("key=K", log)

    def _http_error(self, code, reason):
        body = json.dumps({"error": {"code": code, "errors": [{"reason": reason}]}}).encode()
        def f(url, headers=None, data=None, timeout=30):
            self.calls.append(url)
            raise urllib.error.HTTPError("https://www.googleapis.com/youtube/v3/x", code, "err", {}, io.BytesIO(body))
        return f

    def test_quota_exceeded_logs_reason_and_falls_back(self):
        C.http = self._http_error(403, "quotaExceeded")
        out = C.collect_youtube(dt.date(2026, 11, 24), key="K")
        self.assertEqual(out, [])
        self.assertEqual(len(self.scraped), 1)
        log = self.err.getvalue()
        self.assertIn("HTTP 403 reason=quotaExceeded", log)
        self.assertIn("旧経路", log)
        self.assertEqual(C.YT_STATS["mode"], "scrape")
        self.assertIn("quotaExceeded", C.YT_STATS["reason"])
        self.assertEqual(len(self.calls), 1)  # 失敗したら API はそれ以上呼ばない

    def test_key_invalid_400(self):
        C.http = self._http_error(400, "keyInvalid")
        C.collect_youtube(dt.date(2026, 11, 24), key="K")
        self.assertIn("HTTP 400 reason=keyInvalid", self.err.getvalue())
        self.assertEqual(len(self.scraped), 1)

    def test_no_key_uses_old_path(self):
        C.http = lambda *a, **k: self.fail("API を呼ばない")
        old = os.environ.pop("YOUTUBE_API_KEY", None)
        try:
            C.collect_youtube(dt.date(2026, 11, 24))
        finally:
            if old is not None:
                os.environ["YOUTUBE_API_KEY"] = old
        self.assertEqual(len(self.scraped), 1)
        self.assertIn("YOUTUBE_API_KEY なし", self.err.getvalue())
        self.assertEqual(C.YT_STATS["reason"], "YOUTUBE_API_KEY なし")

    def test_unit_limit_guard(self):
        C.http = self.fake_ok
        qs = ["a", "b", "c", "d"]
        out = C.collect_youtube_api(qs, "K", dt.date(2026, 11, 24), limit=250)
        self.assertEqual(len([c for c in self.calls if "/search?" in c]), 2)  # 2*100 + videos 1 <= 250、3回目は止める
        self.assertEqual(len([c for c in self.calls if "/videos?" in c]), 1)
        self.assertLessEqual(C.YT_STATS["units"], 250)
        self.assertEqual(C.YT_STATS["error"], "unit_limit")
        self.assertEqual(len(out), 6)

    def test_unit_budget_numbers(self):
        n = C.YT_QUERY_LIMIT
        per_run = C.yt_api_cost(n, n * C.YT_API_MAX_RESULTS)
        self.assertEqual(per_run, n * 100 + 2)  # 4語なら 402
        self.assertLessEqual(per_run, C.YT_API_RUN_LIMIT)
        self.assertLessEqual(C.YT_API_RUN_LIMIT * 10, C.YT_API_DAILY_BUDGET)  # 1日10回動いても 5,000 以下
        self.assertLessEqual(C.YT_API_DAILY_BUDGET, 10000 // 2)


if __name__ == "__main__":
    unittest.main()
