import type { CarResult } from "@/lib/types";

interface CarCardProps {
  car: CarResult;
  rank: number;
}

const FUEL_LABELS: Record<string, string> = {
  petrol: "Petrol",
  diesel: "Diesel",
  electric: "Electric",
  hybrid: "Hybrid",
  mild_hybrid: "Mild Hybrid",
  strong_hybrid: "Strong Hybrid",
  cng: "CNG",
};

const TX_LABELS: Record<string, string> = {
  manual: "Manual",
  automatic: "Automatic",
  amt: "AMT",
  cvt: "CVT",
  dct: "DCT",
  torque_converter: "Torque Converter",
};

export default function CarCard({ car, rank }: CarCardProps) {
  const { key_specs } = car;

  return (
    <div className="bg-white rounded-[8px] border border-border overflow-hidden">
      {/* Rank badge + name header */}
      <div className="px-5 pt-5 pb-4">
        <div className="flex items-start justify-between gap-3 mb-3">
          <div>
            <span className="inline-block text-xs font-bold text-coral bg-orange-50 border border-coral/20 px-2.5 py-0.5 rounded-full mb-2">
              #{rank} Pick
            </span>
            <h2 className="text-charcoal text-lg font-bold leading-tight">
              {car.make} {car.model}
            </h2>
            <p className="text-secondary text-sm mt-0.5">{car.variant}</p>
          </div>
          <div className="text-right flex-shrink-0">
            <p className="text-charcoal text-xl font-bold">
              ₹{(car.on_road_price / 100_000).toFixed(1)}L
            </p>
            <p className="text-secondary text-xs mt-0.5">On-road, Bengaluru</p>
          </div>
        </div>

        {/* Explanation */}
        <p className="text-secondary text-sm leading-relaxed">{car.explanation}</p>
      </div>

      {/* Key specs */}
      <div className="border-t border-border px-5 py-3 grid grid-cols-3 gap-3">
        <Spec label="Seating" value={`${key_specs.seating_capacity} seats`} />
        <Spec label="Fuel" value={FUEL_LABELS[key_specs.fuel_type] ?? key_specs.fuel_type} />
        <Spec label="Gearbox" value={TX_LABELS[key_specs.transmission_type] ?? key_specs.transmission_type} />
        <Spec label="Safety" value={`${key_specs.safety_rating}★`} />
        <Spec label="Mileage" value={`${key_specs.mileage_kmpl} kmpl`} />
        <Spec label="Type" value={key_specs.body_type.replace(/_/g, " ")} />
      </div>

      {/* CTA */}
      <div className="border-t border-border px-5 py-3">
        <a
          href={car.detail_page_url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center justify-center gap-2 w-full py-2.5 rounded-[8px] border border-border text-charcoal text-sm font-semibold hover:bg-gray-50 transition-colors"
        >
          View full details
          <svg className="w-4 h-4" fill="none" viewBox="0 0 16 16">
            <path d="M6 3l5 5-5 5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </a>
      </div>
    </div>
  );
}

function Spec({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-secondary text-xs mb-0.5">{label}</p>
      <p className="text-charcoal text-sm font-semibold capitalize">{value}</p>
    </div>
  );
}
