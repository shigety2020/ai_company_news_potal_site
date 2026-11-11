"""キー無しのテスト: python3 -m unittest scripts/daily/test_collect.py"""
import datetime as dt, glob, json, os, sys, unittest
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
        self.assertEqual(len(seen), 2)
        self.assertIn("watch?v=abc123", seen[0][0])
        self.assertEqual(seen[0][1], 8)
        self.assertIn("channel_id=UCx", seen[1][0])
        self.assertEqual(seen[1][1], 8)

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


if __name__ == "__main__":
    unittest.main()
