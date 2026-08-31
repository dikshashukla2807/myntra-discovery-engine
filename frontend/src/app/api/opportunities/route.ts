import { withDataset } from "@/lib/api-route";
import { loadOpportunities } from "@/lib/dataset";

export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  const sort = new URL(request.url).searchParams.get("sort") || "rank";
  return withDataset((mode) => {
    const rows = [...loadOpportunities(mode)];
    const key = sort.replace(/^-/, "");
    const allowed = new Set([
      "rank",
      "frequency",
      "purchase_association",
      "evidence_strength",
      "composite_score",
      "frequency_percentage",
    ]);
    if (!allowed.has(key)) return rows;
    const reverse = sort.startsWith("-") || key !== "rank";
    rows.sort((a, b) => {
      const av = Number(a[key] ?? 0);
      const bv = Number(b[key] ?? 0);
      return reverse ? bv - av : av - bv;
    });
    return rows;
  });
}
