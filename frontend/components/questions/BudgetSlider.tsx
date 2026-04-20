"use client";

import { useCallback, useRef } from "react";
import type { BudgetAnswers } from "@/lib/types";

interface BudgetSliderProps {
  value: BudgetAnswers;
  onChange: (value: BudgetAnswers) => void;
  min?: number;
  max?: number;
  step?: number;
}

const MIN = 3_00_000;   // 3L — below cheapest car (Alto 800 ₹3.85L)
const MAX = 35_00_000;  // 35L — above most expensive car (Fortuner ₹32L)
const STEP = 50_000;

const LAKH = 1_00_000;
const CRORE = 1_00_00_000;

function formatINR(amount: number): string {
  if (amount >= CRORE) {
    return `₹${(amount / CRORE).toFixed(2).replace(/\.?0+$/, "")}Cr`;
  }
  if (amount >= LAKH) {
    return `₹${(amount / LAKH).toFixed(1).replace(/\.0$/, "")}L`;
  }
  return `₹${(amount / 1000).toFixed(0)}K`;
}

export default function BudgetSlider({
  value,
  onChange,
  min = MIN,
  max = MAX,
  step = STEP,
}: BudgetSliderProps) {
  const trackRef = useRef<HTMLDivElement>(null);
  const draggingRef = useRef<"comfortable" | "stretch" | null>(null);

  const clamp = useCallback(
    (v: number) => Math.max(min, Math.min(max, Math.round(v / step) * step)),
    [min, max, step]
  );

  const getClickPct = useCallback((clientX: number) => {
    const track = trackRef.current;
    if (!track) return 0;
    const rect = track.getBoundingClientRect();
    return Math.max(0, Math.min(1, (clientX - rect.left) / rect.width));
  }, []);

  const handlePointerDown = useCallback(
    (e: React.PointerEvent<HTMLDivElement>) => {
      const pct = getClickPct(e.clientX);
      const clickedValue = min + pct * (max - min);

      const distToComfortable = Math.abs(clickedValue - value.comfortable);
      const distToStretch = Math.abs(clickedValue - value.stretch);

      draggingRef.current =
        distToComfortable <= distToStretch ? "comfortable" : "stretch";
      e.currentTarget.setPointerCapture(e.pointerId);
    },
    [getClickPct, min, max, value.comfortable, value.stretch]
  );

  const handlePointerMove = useCallback(
    (e: React.PointerEvent<HTMLDivElement>) => {
      if (!draggingRef.current) return;
      const pct = getClickPct(e.clientX);
      const raw = min + pct * (max - min);

      if (draggingRef.current === "comfortable") {
        const newComfortable = clamp(Math.min(raw, value.stretch - step));
        onChange({ ...value, comfortable: newComfortable });
      } else {
        const newStretch = clamp(Math.max(raw, value.comfortable + step));
        onChange({ ...value, stretch: newStretch });
      }
    },
    [getClickPct, min, max, clamp, value, onChange, step]
  );

  const handlePointerUp = useCallback(() => {
    draggingRef.current = null;
  }, []);

  const comfortablePct = ((value.comfortable - min) / (max - min)) * 100;
  const stretchPct = ((value.stretch - min) / (max - min)) * 100;

  return (
    <div className="flex flex-col gap-6">
      {/* Price type toggle */}
      <div className="flex gap-2 p-1 bg-white rounded-[8px] border border-border w-fit">
        {(["on_road", "ex_showroom"] as const).map((type) => (
          <button
            key={type}
            type="button"
            onClick={() => onChange({ ...value, price_type: type })}
            className={`px-4 py-1.5 rounded-[6px] text-sm font-semibold transition-all ${
              value.price_type === type
                ? "bg-charcoal text-white"
                : "text-secondary hover:text-charcoal"
            }`}
          >
            {type === "on_road" ? "On-Road" : "Ex-Showroom"}
          </button>
        ))}
      </div>

      {/* Budget display */}
      <div className="flex justify-between text-sm">
        <div>
          <p className="text-secondary font-medium mb-0.5">Comfortable at</p>
          <p className="text-charcoal text-xl font-bold">{formatINR(value.comfortable)}</p>
        </div>
        <div className="text-right">
          <p className="text-secondary font-medium mb-0.5">Stretch to</p>
          <p className="text-coral text-xl font-bold">{formatINR(value.stretch)}</p>
        </div>
      </div>

      {/* Dual slider track */}
      <div
        ref={trackRef}
        className="relative py-4 cursor-pointer select-none touch-none"
        onPointerDown={handlePointerDown}
        onPointerMove={handlePointerMove}
        onPointerUp={handlePointerUp}
        onPointerLeave={handlePointerUp}
        role="group"
        aria-label="Budget range"
      >
        <div className="relative h-2 rounded-full bg-border">
          {/* Active range fill */}
          <div
            className="absolute h-full rounded-full bg-coral"
            style={{ left: `${comfortablePct}%`, width: `${stretchPct - comfortablePct}%` }}
          />
        </div>

        {/* Comfortable thumb */}
        <div
          className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-5 h-5 rounded-full bg-white border-2 border-charcoal shadow-sm pointer-events-none"
          style={{ left: `${comfortablePct}%` }}
          aria-label={`Comfortable budget: ${formatINR(value.comfortable)}`}
        />

        {/* Stretch thumb */}
        <div
          className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-5 h-5 rounded-full bg-coral border-2 border-coral shadow-sm pointer-events-none"
          style={{ left: `${stretchPct}%` }}
          aria-label={`Stretch budget: ${formatINR(value.stretch)}`}
        />
      </div>

      <div className="flex justify-between text-xs text-secondary">
        <span>{formatINR(min)}</span>
        <span>{formatINR(max)}</span>
      </div>
    </div>
  );
}
