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


if __name__ == "__main__":
    unittest.main()
