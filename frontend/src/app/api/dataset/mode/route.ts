import { NextResponse } from "next/server";
import { cookies } from "next/headers";
import { MODE_COOKIE, demoAvailable, datasetBanner } from "@/lib/dataset";

export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  const body = (await request.json().catch(() => ({}))) as { mode?: string };
  const mode = body.mode === "demo" ? "demo" : "public";
  if (mode === "demo" && !demoAvailable()) {
    return NextResponse.json({ error: "Demo dataset has not been generated yet." }, { status: 400 });
  }
  const jar = await cookies();
  jar.set(MODE_COOKIE, mode, {
    path: "/",
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
  });
  return NextResponse.json({ ...datasetBanner(mode), demo_available: demoAvailable() });
}
