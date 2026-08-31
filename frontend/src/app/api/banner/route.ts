import { NextResponse } from "next/server";
import { bannerPayload } from "@/lib/api-route";

export const dynamic = "force-dynamic";

export async function GET() {
  return NextResponse.json(await bannerPayload());
}
