import { withDataset } from "@/lib/api-route";
import {
  loadClusters,
  loadExtractions,
  loadHypothesisClassifications,
  loadRelevant,
  loadThemes,
} from "@/lib/dataset";

export const dynamic = "force-dynamic";

type StanceMap = Record<string, { stance?: string }>;

export async function GET(request: Request) {
  const params = new URL(request.url).searchParams;
  const source = params.get("source") || "";
  const q = (params.get("q") || "").toLowerCase();
  const userIntent = params.get("user_intent") || "";
  const purchaseOutcome = params.get("purchase_outcome") || "";
  const barrier = params.get("barrier") || "";
  const theme = (params.get("theme") || "").toLowerCase();
  const hypothesis = (params.get("hypothesis") || "").toUpperCase();
  const stance = params.get("stance") || "";
  const limit = Math.min(100, Math.max(1, Number(params.get("limit") || 25)));
  const offset = Math.max(0, Number(params.get("offset") || 0));

  return withDataset((mode) => {
    const rows = loadRelevant(mode);
    const ext = loadExtractions(mode);
    const clusters = loadClusters(mode);
    const themes = loadThemes(mode);
    const clusterToTheme = Object.fromEntries(themes.map((t) => [String(t.cluster_id), t]));
    const classified = loadHypothesisClassifications(mode);
    const filtered = [];
    for (const obs of rows) {
      const oid = String(obs.observation_id || "");
      const e = ext[oid] || {};
      if (source && obs.source !== source) continue;
      if (userIntent && e.user_intent !== userIntent) continue;
      if (purchaseOutcome && e.purchase_outcome !== purchaseOutcome) continue;
      if (barrier && !((e.barriers as string[] | undefined) || []).includes(barrier)) continue;
      const themeObj = clusterToTheme[String(clusters[oid])];
      if (theme) {
        if (!themeObj) continue;
        const blob = `${themeObj.theme_id || ""} ${themeObj.theme_name || ""}`.toLowerCase();
        if (!blob.includes(theme)) continue;
      }
      const stances = ((classified[oid] || {}).stances as StanceMap) || {};
      if (hypothesis) {
        const current = (stances[hypothesis] || {}).stance;
        if (stance) {
          if (current !== stance) continue;
        } else if (!["supporting", "counter", "unclear"].includes(current || "")) {
          continue;
        }
      } else if (stance && !Object.values(stances).some((v) => v.stance === stance)) {
        continue;
      }
      if (q) {
        const text = `${obs.text_original || ""} ${obs.title || ""}`.toLowerCase();
        if (!text.includes(q)) continue;
      }
      filtered.push({ observation: obs, extraction: e, theme: themeObj, hypothesis_stances: stances });
    }
    return { total: filtered.length, offset, limit, results: filtered.slice(offset, offset + limit) };
  });
}
