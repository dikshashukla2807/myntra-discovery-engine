import { bannerPayload, withDataset } from "@/lib/api-route";

export const dynamic = "force-dynamic";

export async function GET() {
  return withDataset(async () => ({
    ok: true,
    time: new Date().toISOString(),
    ...(await bannerPayload()),
    banner: await bannerPayload(),
  }));
}
