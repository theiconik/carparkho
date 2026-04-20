"use client";

interface Option {
  id: string;
  label: string;
}

interface SingleSelectProps {
  options: Option[];
  value: string;
  onChange: (value: string) => void;
}

export default function SingleSelect({ options, value, onChange }: SingleSelectProps) {
  return (
    <div className="flex flex-col gap-3">
      {options.map((option) => {
        const isActive = value === option.id;
        return (
          <button
            key={option.id}
            type="button"
            onClick={() => onChange(option.id)}
            className={`flex items-center gap-3 w-full text-left px-4 py-3.5 rounded-[8px] border transition-all cursor-pointer ${
              isActive
                ? "border-coral bg-orange-50"
                : "border-border bg-surface hover:border-secondary"
            }`}
          >
            {/* Radio indicator */}
            <span
              className={`flex-shrink-0 w-5 h-5 rounded-full border-2 flex items-center justify-center transition-colors ${
                isActive ? "border-coral" : "border-border"
              }`}
            >
              {isActive && <span className="w-2.5 h-2.5 rounded-full bg-coral" />}
            </span>
            <span
              className={`text-sm font-semibold transition-colors ${
                isActive ? "text-coral" : "text-secondary"
              }`}
            >
              {option.label}
            </span>
          </button>
        );
      })}
    </div>
  );
}
