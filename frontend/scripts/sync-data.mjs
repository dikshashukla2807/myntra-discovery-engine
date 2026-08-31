import { cpSync, existsSync, mkdirSync, rmSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const frontendRoot = join(dirname(fileURLToPath(import.meta.url)), "..");
const dest = join(frontendRoot, "dataset");
const src = join(frontendRoot, "..", "data");
const srcOverview = join(src, "processed", "overview.json");
const destOverview = join(dest, "processed", "overview.json");

if (!existsSync(srcOverview)) {
  if (existsSync(destOverview)) {
    console.log("dataset already present at", dest);
    process.exit(0);
  }
  console.warn("No processed dataset at", srcOverview);
  process.exit(0);
}

rmSync(dest, { recursive: true, force: true });
mkdirSync(join(dest, "processed"), { recursive: true });
cpSync(join(src, "processed"), join(dest, "processed"), { recursive: true });
if (existsSync(join(src, "processed_demo"))) {
  cpSync(join(src, "processed_demo"), join(dest, "processed_demo"), { recursive: true });
}
console.log("synced discovery dataset ->", dest);
