"use client";

import { useEffect, useState } from "react";
import Image from "next/image";
import { useRouter } from "next/navigation";
import CarCard from "@/components/CarCard";
import EmptyState from "@/components/EmptyState";
import type { RecommendResponse } from "@/lib/types";

type PageState =
  | { kind: "loading" }
  | { kind: "ready"; data: RecommendResponse }
  | { kind: "missing" };

function loadResults(): PageState {
  const raw = sessionStorage.getItem("carparkho_results");
  if (!raw) return { kind: "missing" };
  try {
    return { kind: "ready", data: JSON.parse(raw) };
  } catch {
    return { kind: "missing" };
  }
}

export default function ResultsPage() {
  const router = useRouter();
  // Start with "loading" during SSR; populate from sessionStorage once mounted on client.
  const [state, setState] = useState<PageState>({ kind: "loading" });

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setState(loadResults());
  }, []);

  const handleStartOver = () => {
    sessionStorage.removeItem("carparkho_results");
    router.push("/");
  };

  if (state.kind === "loading") {
    return (
      <main className="min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center gap-3 text-secondary">
          <svg className="w-6 h-6 animate-spin text-coral" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
          </svg>
          <span className="text-sm">Loading…</span>
        </div>
      </main>
    );
  }

  if (state.kind === "missing") {
    return (
      <main className="min-h-screen flex flex-col items-center justify-center px-5">
        <div className="text-center">
          <p className="text-secondary text-sm mb-4">No results found. Please take the quiz first.</p>
          <button
            type="button"
            onClick={() => router.push("/quiz")}
            className="px-6 py-3 bg-coral text-white text-sm font-bold rounded-[8px]"
          >
            Take the quiz
          </button>
        </div>
      </main>
    );
  }

  const { data } = state;

  return (
    <main className="min-h-screen bg-[#F7F8FA]">
      {/* Header */}
      <header className="px-5 pt-5 pb-4 bg-white border-b border-border sticky top-0 z-10">
        <div className="w-full max-w-sm mx-auto flex items-center justify-between">
          <div>
            <div className="flex items-center gap-1.5 mb-0.5">
              <Image src="/logo.png" alt="Car Parkho" width={20} height={20} className="rounded-md" />
              <span className="text-coral text-xs font-bold tracking-widest uppercase">Car Parkho</span>
            </div>
            <h1 className="text-charcoal text-lg font-bold leading-tight">Your shortlist</h1>
          </div>
          <button
            type="button"
            onClick={handleStartOver}
            className="text-secondary text-sm font-semibold hover:text-charcoal transition-colors flex items-center gap-1"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 16 16">
              <path d="M2 8a6 6 0 1 1 1.5 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
              <path d="M2 12V8h4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
            Start over
          </button>
        </div>
      </header>

      <div className="px-5 py-5">
        <div className="w-full max-w-sm mx-auto flex flex-col gap-4">
          {/* Banner for <3 results */}
          {data.banner && (
            <div className="bg-orange-50 border border-coral/20 rounded-[8px] px-4 py-3 flex items-start gap-3">
              <svg className="w-4 h-4 text-coral flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 16 16">
                <path d="M8 1.5a6.5 6.5 0 100 13 6.5 6.5 0 000-13zM8 5v4m0 2.5h.01" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" />
              </svg>
              <p className="text-sm text-charcoal">{data.banner}</p>
            </div>
          )}

          {/* Zero results */}
          {data.results.length === 0 ? (
            <EmptyState blocker={data.blocker} onStartOver={handleStartOver} />
          ) : (
            <>
              <p className="text-secondary text-sm">
                {data.total_matched > 3
                  ? `${data.total_matched} cars matched — showing the top 3 for you.`
                  : `${data.results.length} car${data.results.length > 1 ? "s" : ""} matched your preferences.`}
              </p>
              {data.results.map((car, i) => (
                <CarCard key={car.id} car={car} rank={i + 1} />
              ))}
            </>
          )}

          {/* Retake CTA at bottom */}
          {data.results.length > 0 && (
            <button
              type="button"
              onClick={handleStartOver}
              className="w-full py-3 border border-border text-secondary text-sm font-semibold rounded-[8px] hover:bg-white transition-colors mt-2"
            >
              Adjust preferences →
            </button>
          )}
        </div>
      </div>
    </main>
  );
}
