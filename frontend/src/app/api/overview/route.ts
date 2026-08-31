import { bannerPayload, withDataset } from "@/lib/api-route";
import { demoAvailable, loadOverview, loadQuality } from "@/lib/dataset";

export const dynamic = "force-dynamic";

export async function GET() {
  return withDataset(async (mode) => {
    const data = { ...loadOverview(mode) } as Record<string, unknown>;
    data.banner = await bannerPayload();
    data.demo_available = demoAvailable();
    data.quality = loadQuality(mode);
    return data;
  });
}
