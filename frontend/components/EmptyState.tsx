interface EmptyStateProps {
  blocker: string | null;
  onStartOver: () => void;
}

export default function EmptyState({ blocker, onStartOver }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center text-center px-6 py-12 gap-6">
      <div className="w-16 h-16 rounded-full bg-orange-50 flex items-center justify-center">
        <svg className="w-8 h-8 text-coral" fill="none" viewBox="0 0 24 24">
          <path
            d="M12 9v4m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </div>
      <div>
        <h2 className="text-charcoal text-xl font-bold mb-2">No cars matched</h2>
        <p className="text-secondary text-sm leading-relaxed max-w-xs mx-auto">
          {blocker && blocker !== "no_cars_found"
            ? `No cars match all your requirements. The most common blocker was your ${blocker}.`
            : "No cars matched all your requirements. Try adjusting your preferences."}
        </p>
      </div>
      <button
        type="button"
        onClick={onStartOver}
        className="px-6 py-3 bg-coral text-white text-sm font-bold rounded-[8px] hover:bg-orange-600 transition-colors"
      >
        Start over
      </button>
    </div>
  );
}
