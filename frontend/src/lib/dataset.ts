import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { cookies } from "next/headers";

export const MODE_COOKIE = "myntra_dataset_mode";

export type DatasetMode = "public" | "demo";

type Json = Record<string, unknown>;

type Cache = {
  root?: string;
  json: Record<string, unknown>;
  jsonl: Record<string, Json[]>;
};

const g = globalThis as typeof globalThis & { __myntraDataset?: Cache };
function cache(): Cache {
  if (!g.__myntraDataset) g.__myntraDataset = { json: {}, jsonl: {} };
  return g.__myntraDataset;
}

function findDataRoot(): string {
  const hit = cache();
  const root = join(process.cwd(), "dataset");
  if (existsSync(join(root, "processed", "overview.json"))) {
    hit.root = root;
    return root;
  }
  throw new Error("Processed dataset not found. Public-source files live in data/processed/.");
}

export function processedDir(mode: DatasetMode): string {
  const root = findDataRoot();
  const dir =
    mode === "demo"
      ? join(root, "processed_demo")
      : join(root, "processed");
  if (!existsSync(join(dir, "overview.json"))) {
    throw new Error(mode === "demo" ? "Demo dataset has not been generated yet." : "Processed dataset not found.");
  }
  return dir;
}

export function demoAvailable(): boolean {
  try {
    return existsSync(join(process.cwd(), "dataset", "processed_demo", "overview.json"));
  } catch {
    return false;
  }
}

export async function currentMode(): Promise<DatasetMode> {
  const jar = await cookies();
  return jar.get(MODE_COOKIE)?.value === "demo" ? "demo" : "public";
}

export function datasetBanner(mode: DatasetMode): { mode: string; label: string; detail: string } {
  if (mode === "demo") {
    return {
      mode: "demo",
      label: "DEMO / SAMPLE DATA",
      detail:
        "These observations are labeled sample data. They are not real user research and must not be presented as public-source findings.",
    };
  }
  return {
    mode: "public",
    label: "Public-source dataset",
    detail:
      "Public user-generated content collected from source platforms. Not independently verified as genuine.",
  };
}

function readJsonFile<T>(path: string, fallback: T): T {
  const hit = cache();
  if (path in hit.json) return hit.json[path] as T;
  if (!existsSync(path)) {
    hit.json[path] = fallback;
    return fallback;
  }
  const parsed = JSON.parse(readFileSync(path, "utf8")) as T;
  hit.json[path] = parsed;
  return parsed;
}

function readJsonl(path: string): Json[] {
  const hit = cache();
  if (path in hit.jsonl) return hit.jsonl[path];
  if (!existsSync(path)) {
    hit.jsonl[path] = [];
    return [];
  }
  const rows: Json[] = [];
  for (const line of readFileSync(path, "utf8").split("\n")) {
    const trimmed = line.trim();
    if (!trimmed) continue;
    rows.push(JSON.parse(trimmed) as Json);
  }
  hit.jsonl[path] = rows;
  return rows;
}

export function loadOverview(mode: DatasetMode): Json {
  return readJsonFile(join(processedDir(mode), "overview.json"), {});
}

export function loadQuality(mode: DatasetMode): Json {
  return readJsonFile(join(processedDir(mode), "quality_report.json"), {});
}

export function loadPipeline(mode: DatasetMode): Json {
  return readJsonFile(join(processedDir(mode), "pipeline_status.json"), {});
}

export function loadThemes(mode: DatasetMode): Json[] {
  return readJsonFile(join(processedDir(mode), "themes.json"), []);
}

export function loadOpportunities(mode: DatasetMode): Json[] {
  return readJsonFile(join(processedDir(mode), "opportunities.json"), []);
}

export function loadHypotheses(mode: DatasetMode): Json[] {
  return readJsonFile(join(processedDir(mode), "hypotheses.json"), []);
}

export function loadHypothesisComparison(mode: DatasetMode): Json[] {
  return readJsonFile(join(processedDir(mode), "hypothesis_comparison.json"), []);
}

export function loadRelevant(mode: DatasetMode): Json[] {
  return readJsonl(join(processedDir(mode), "relevant_observations.jsonl"));
}

export function loadExtractions(mode: DatasetMode): Record<string, Json> {
  const rows = readJsonl(join(processedDir(mode), "extractions.jsonl"));
  const map: Record<string, Json> = {};
  for (const row of rows) {
    const id = String(row.observation_id || "");
    if (id) map[id] = row;
  }
  return map;
}

export function loadHypothesisClassifications(mode: DatasetMode): Record<string, Json> {
  const rows = readJsonl(join(processedDir(mode), "hypothesis_classifications.jsonl"));
  const map: Record<string, Json> = {};
  for (const row of rows) {
    const id = String(row.observation_id || "");
    if (id) map[id] = row;
  }
  return map;
}

export function loadClusters(mode: DatasetMode): Record<string, number> {
  const rows = readJsonFile<Json[]>(join(processedDir(mode), "clusters.json"), []);
  const map: Record<string, number> = {};
  for (const row of rows) {
    if (typeof row.observation_id === "string" && typeof row.cluster_id === "number") {
      map[row.observation_id] = row.cluster_id;
    }
  }
  return map;
}

export function packEvidence(
  ids: string[] | undefined,
  observations: Record<string, Json>,
  extractions: Record<string, Json>,
  limit: number,
): Array<{ observation: Json; extraction?: Json }> {
  const out: Array<{ observation: Json; extraction?: Json }> = [];
  for (const id of (ids || []).slice(0, limit)) {
    const obs = observations[id];
    if (!obs) continue;
    out.push({ observation: obs, extraction: extractions[id] });
  }
  return out;
}

const BASE_QUESTIONS = [
  "Tell me about the last fashion product you wanted to buy but didn't.",
  "Walk me through how that product ended up saved, wishlisted, or sitting in your bag.",
  "What made you save it in the first place?",
  "What happened between saving it and deciding whether to buy?",
  "What information were you still looking for?",
  "Where did you go to find that information, if anywhere?",
  "Did you look anywhere outside Myntra? If yes, what were you trying to learn?",
  "If you compared it with something else, how did you compare?",
  "What did you eventually do, and what made that the decision?",
  "Tell me about a time you did buy something you had saved. What was different?",
  "When you hesitate, what usually makes you wait versus drop it altogether?",
  "Who, if anyone, do you involve before you buy clothes online?",
];

export function interviewPlan(opportunity: Json, segment: string | null): Json {
  const segs = (opportunity.user_segment as string[] | undefined) || [];
  return {
    opportunity_id: opportunity.opportunity_id,
    selected_opportunity: opportunity.title,
    target_segment: segment || segs[0] || "Insufficient evidence.",
    what_we_know: opportunity.what_we_know || opportunity.description || "Insufficient evidence.",
    what_we_dont_know:
      opportunity.research_gap || "Whether this pattern actually prevents 30-day wishlist conversion.",
    research_hypothesis:
      "If this barrier is a true decision blocker for high-intent / high-wishlist users, we should hear it unprompted in stories of products they wanted but did not buy. This remains a hypothesis until interviews.",
    research_objective:
      "Understand what actually happens between expressing interest (save/wishlist) and buying or not buying, for this opportunity area — without validating a solution.",
    interview_questions: BASE_QUESTIONS,
    research_objectives: [
      "What actually happened between saving/wishlisting and deciding not to buy?",
      "Was this barrier the main reason, or one of several?",
      "Who else was involved, and what information was still missing?",
      "When in the 30 days after saving did the decision stall?",
    ],
    ready_for_primary_research: true,
    end_state: "READY FOR PRIMARY RESEARCH",
    why_primary_research:
      "Public UGC can show that a pattern exists and whether it is observed alongside postponement or non-purchase. It cannot prove the final user problem, severity, or whether fixing it would change 30-day wishlist conversion. That takes 5–6 interviews.",
    notes: [
      "Ask for the last real episode, not hypotheticals.",
      "Follow the story: trigger → save → wait → research → decide.",
      "Do not pitch a feature. The engine stops at opportunity + evidence + research gap.",
      "End state: ready for primary research — not a final solution.",
    ],
  };
}
