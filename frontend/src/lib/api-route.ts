import { NextResponse } from "next/server";
import { currentMode, datasetBanner, demoAvailable } from "@/lib/dataset";

export const dynamic = "force-dynamic";

export async function withDataset<T>(fn: (mode: "public" | "demo") => T | Promise<T>) {
  try {
    const mode = await currentMode();
    const data = await fn(mode);
    return NextResponse.json(data);
  } catch (err) {
    const message = err instanceof Error ? err.message : "Internal Server Error";
    const status = /not found/i.test(message) ? 404 : /not been generated/i.test(message) ? 400 : 500;
    return NextResponse.json({ error: message }, { status });
  }
}

export async function bannerPayload() {
  const mode = await currentMode();
  return { ...datasetBanner(mode), demo_available: demoAvailable() };
}
