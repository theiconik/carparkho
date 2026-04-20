"use client";

interface Option {
  id: string;
  label: string;
}

interface MultiSelectProps {
  options: Option[];
  value: string[];
  onChange: (value: string[]) => void;
  maxSelections?: number;
}

export default function MultiSelect({ options, value, onChange, maxSelections }: MultiSelectProps) {
  const toggle = (id: string) => {
    if (value.includes(id)) {
      onChange(value.filter((v) => v !== id));
    } else {
      if (maxSelections && value.length >= maxSelections) return;
      onChange([...value, id]);
    }
  };

  return (
    <div className="flex flex-col gap-3">
      {options.map((option) => {
        const isActive = value.includes(option.id);
        const isDisabled = !isActive && maxSelections !== undefined && value.length >= maxSelections;

        return (
          <button
            key={option.id}
            type="button"
            onClick={() => toggle(option.id)}
            disabled={isDisabled}
            className={`flex items-center gap-3 w-full text-left px-4 py-3.5 rounded-[8px] border transition-all cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed ${
              isActive
                ? "border-coral bg-orange-50"
                : "border-border bg-surface hover:border-secondary"
            }`}
          >
            {/* Checkbox indicator */}
            <span
              className={`flex-shrink-0 w-5 h-5 rounded-[4px] border-2 flex items-center justify-center transition-colors ${
                isActive ? "border-coral bg-coral" : "border-border"
              }`}
            >
              {isActive && (
                <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 12 12">
                  <path d="M2 6l3 3 5-5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              )}
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
