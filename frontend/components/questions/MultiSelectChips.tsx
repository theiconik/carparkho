"use client";

interface Option {
  id: string;
  label: string;
}

interface MultiSelectChipsProps {
  options: Option[];
  value: string[];
  onChange: (value: string[]) => void;
}

export default function MultiSelectChips({ options, value, onChange }: MultiSelectChipsProps) {
  const toggle = (id: string) => {
    if (value.includes(id)) {
      onChange(value.filter((v) => v !== id));
    } else {
      onChange([...value, id]);
    }
  };

  return (
    <div className="flex flex-wrap gap-2.5">
      {options.map((option) => {
        const isActive = value.includes(option.id);
        return (
          <button
            key={option.id}
            type="button"
            onClick={() => toggle(option.id)}
            className={`px-4 py-2 rounded-full border text-sm font-semibold transition-all cursor-pointer ${
              isActive
                ? "bg-coral border-coral text-white"
                : "bg-surface border-border text-secondary hover:border-secondary"
            }`}
          >
            {option.label}
          </button>
        );
      })}
    </div>
  );
}
