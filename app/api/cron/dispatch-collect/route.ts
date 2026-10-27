// PB1: Vercel Cron（毎日 6:00 JST 台）から呼ばれ、GitHub Actions の daily-collect を workflow_dispatch で起こす
export const dynamic = "force-dynamic";

const DISPATCH_URL =
  "https://api.github.com/repos/shigety2020/ai_company_news_potal_site/actions/workflows/daily-collect.yml/dispatches";

export async function GET(request: Request) {
  const cronSecret = process.env.CRON_SECRET;
  const token = process.env.GH_DISPATCH_TOKEN;
  if (!cronSecret || !token) {
    return Response.json(
      { ok: false, status: 500, error: "必要な環境変数（CRON_SECRET / GH_DISPATCH_TOKEN）が未設定です" },
      { status: 500 }
    );
  }
  if (request.headers.get("authorization") !== `Bearer ${cronSecret}`) {
    return Response.json({ ok: false, status: 401, error: "unauthorized" }, { status: 401 });
  }
  try {
    const res = await fetch(DISPATCH_URL, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        Accept: "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json",
      },
      // dry_run の既定値は true なので、本番の号を作るため明示的に false を渡す
      body: JSON.stringify({ ref: "main", inputs: { dry_run: "false" } }),
      cache: "no-store",
    });
    const ok = res.status === 204;
    return Response.json({ ok, status: res.status }, { status: ok ? 200 : 502 });
  } catch {
    return Response.json({ ok: false, status: 502, error: "GitHub への接続に失敗しました" }, { status: 502 });
  }
}
