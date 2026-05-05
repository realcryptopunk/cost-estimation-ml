export function FeatureBar({
  label,
  value,
  maxValue,
}: {
  label: string;
  value: number;
  maxValue: number;
}) {
  const pct = (value / maxValue) * 100;

  return (
    <div className="flex items-center gap-4">
      <span className="w-32 text-right text-sm font-body font-medium text-obsidian shrink-0">
        {label}
      </span>
      <div className="flex-1 h-7 bg-powder rounded-full overflow-hidden">
        <div
          className="h-full bg-obsidian rounded-full transition-all duration-700 ease-out"
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="w-16 text-right text-xs font-mono text-gravel shrink-0">
        {value.toFixed(1)}%
      </span>
    </div>
  );
}
