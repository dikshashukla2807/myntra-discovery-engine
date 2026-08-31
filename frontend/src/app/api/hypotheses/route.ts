import { withDataset } from "@/lib/api-route";
import { datasetBanner, loadHypotheses, loadHypothesisComparison } from "@/lib/dataset";

export const dynamic = "force-dynamic";

export async function GET() {
  return withDataset((mode) => {
    const rows = loadHypotheses(mode);
    const comparison =
      loadHypothesisComparison(mode).length > 0
        ? loadHypothesisComparison(mode)
        : rows.map((r) => ({
            hypothesis_id: r.hypothesis_id,
            hypothesis_name: r.hypothesis_name,
            evidence: r.evidence_label,
            support: r.support_count,
            counter_evidence: r.counter_count,
            purchase_association: r.purchase_association,
            confidence: r.confidence,
            priority: r.priority,
            status: r.status,
          }));
    return {
      hypotheses: rows,
      comparison,
      summary: {
        tested: rows.length,
        supported: rows.filter((r) => r.status === "supported").length,
        weakly_supported: rows.filter((r) => r.status === "weakly_supported").length,
        contradicted: rows.filter((r) => r.status === "contradicted").length,
        insufficient_evidence: rows.filter((r) => r.status === "insufficient_evidence").length,
      },
      banner: datasetBanner(mode),
    };
  });
}
