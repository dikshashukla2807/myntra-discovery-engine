"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { BookOpen, FolderSearch, LayoutDashboard, Puzzle } from "lucide-react";
import { cn } from "@/lib/cn";

const NAV = [
  { href: "/", label: "Overview", icon: LayoutDashboard },
  { href: "/evidence", label: "Evidence Explorer", icon: FolderSearch },
  { href: "/opportunities", label: "Opportunity Landscape", icon: Puzzle },
  { href: "/research", label: "Research Handoff", icon: BookOpen },
];

export function Shell({ children }: { children: React.ReactNode }) {
  const path = usePathname();
  return (
    <div className="min-h-screen bg-[#f6f3ee] text-zinc-900">
      <aside className="fixed inset-y-0 left-0 hidden w-64 flex-col border-r border-zinc-800 bg-[#1c1412] text-zinc-100 md:flex">
        <div className="border-b border-white/10 px-5 py-5">
          <p className="text-[11px] uppercase tracking-[0.18em] text-rose-300">NextLeap · Growth</p>
          <h1 className="mt-1 font-semibold leading-tight">Myntra Discovery Engine</h1>
          <p className="mt-2 text-xs text-zinc-400">
            Business metric → public evidence → candidate opportunities → interview questions.
          </p>
        </div>
        <nav className="flex-1 space-y-0.5 overflow-y-auto px-3 py-4">
          {NAV.map((item) => {
            const active =
              item.href === "/"
                ? path === "/"
                : path === item.href || path.startsWith(`${item.href}/`);
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-2 rounded-md px-3 py-2 text-sm",
                  active ? "bg-white/10 text-white" : "text-zinc-300 hover:bg-white/5 hover:text-white",
                )}
              >
                <Icon size={16} />
                {item.label}
              </Link>
            );
          })}
        </nav>
        <p className="px-5 py-4 text-[11px] leading-relaxed text-zinc-500">
          Stops at opportunity + evidence + research gap. Does not recommend a feature.
        </p>
      </aside>
      <div className="md:pl-64">
        <header className="sticky top-0 z-20 border-b border-zinc-200 bg-[#f6f3ee]/90 px-4 py-3 backdrop-blur md:hidden">
          <p className="text-sm font-semibold">Myntra Discovery Engine</p>
          <nav className="mt-2 flex flex-wrap gap-3 text-xs">
            {NAV.map((item) => (
              <Link key={item.href} href={item.href} className="text-rose-800">
                {item.label}
              </Link>
            ))}
          </nav>
        </header>
        <main className="mx-auto max-w-7xl px-4 py-6 md:px-8 md:py-8">{children}</main>
      </div>
    </div>
  );
}

export function DatasetBanner({ banner }: { banner?: { mode: string; label: string; detail: string } }) {
  if (!banner) return null;
  const tone =
    banner.mode === "demo"
      ? "border-amber-300 bg-amber-50 text-amber-950"
      : "border-emerald-300 bg-emerald-50 text-emerald-950";
  return (
    <div className={cn("mb-6 rounded-lg border px-4 py-3 text-sm", tone)}>
      <p className="font-semibold">{banner.label}</p>
      <p className="mt-1 text-[13px] opacity-90">{banner.detail}</p>
    </div>
  );
}

export function PageHeader({
  eyebrow,
  title,
  description,
}: {
  eyebrow?: string;
  title: string;
  description?: string;
}) {
  return (
    <div className="mb-6">
      {eyebrow ? (
        <p className="text-xs font-medium uppercase tracking-[0.16em] text-rose-800">{eyebrow}</p>
      ) : null}
      <h2 className="mt-1 text-2xl font-semibold tracking-tight">{title}</h2>
      {description ? <p className="mt-2 max-w-3xl text-sm leading-6 text-zinc-600">{description}</p> : null}
    </div>
  );
}
