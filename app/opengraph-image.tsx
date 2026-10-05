import { ImageResponse } from "next/og";

export const alt = "みんなのデジタル社員";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

const SITE = "みんなのデジタル社員";
const NOTE = "※実在の人間の求人情報ではありません";

const FONT_BOLD =
  "https://cdn.jsdelivr.net/fontsource/fonts/noto-sans-jp@5.2.5/japanese-700-normal.ttf";
const FONT_REGULAR =
  "https://cdn.jsdelivr.net/fontsource/fonts/noto-sans-jp@5.2.5/japanese-400-normal.ttf";

export default async function OpenGraphImage() {
  const [fontRegular, fontBold] = await Promise.all([
    fetch(FONT_REGULAR).then((r) => {
      if (!r.ok) throw new Error(`font regular ${r.status}`);
      return r.arrayBuffer();
    }),
    fetch(FONT_BOLD).then((r) => {
      if (!r.ok) throw new Error(`font bold ${r.status}`);
      return r.arrayBuffer();
    }),
  ]);

  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          background: "#FFFFFF",
          padding: "72px 80px",
          fontFamily: '"Noto Sans JP"',
        }}
      >
        <div
          style={{
            position: "absolute",
            left: 0,
            top: 0,
            bottom: 0,
            width: 16,
            background: "#D01808",
          }}
        />
        <div style={{ display: "flex", alignItems: "center", gap: 28 }}>
          <div
            style={{
              width: 96,
              height: 96,
              borderRadius: 20,
              background: "#D01808",
              color: "#FFFFFF",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: 56,
              fontWeight: 700,
              lineHeight: 1,
            }}
          >
            み
          </div>
          <div
            style={{
              fontSize: 64,
              fontWeight: 700,
              color: "#111111",
              letterSpacing: "0.02em",
              lineHeight: 1.2,
            }}
          >
            {SITE}
          </div>
        </div>
        <div
          style={{
            marginTop: 28,
            marginLeft: 124,
            fontSize: 32,
            fontWeight: 400,
            color: "#767676",
            letterSpacing: "0.02em",
            lineHeight: 1.4,
          }}
        >
          {NOTE}
        </div>
      </div>
    ),
    {
      ...size,
      fonts: [
        { name: "Noto Sans JP", data: fontRegular, style: "normal", weight: 400 },
        { name: "Noto Sans JP", data: fontBold, style: "normal", weight: 700 },
      ],
    },
  );
}
