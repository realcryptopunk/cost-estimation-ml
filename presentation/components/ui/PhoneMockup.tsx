export function PhoneMockup({
  children,
  label,
}: {
  children: React.ReactNode;
  label?: string;
}) {
  return (
    <div className="flex flex-col items-center gap-3">
      <div className="relative w-[280px] h-[580px] rounded-[40px] bg-obsidian p-[10px] shadow-[0_20px_60px_rgba(0,0,0,0.3)]">
        {/* Dynamic Island */}
        <div className="absolute top-[14px] left-1/2 -translate-x-1/2 w-[90px] h-[26px] bg-obsidian rounded-full z-20" />

        {/* Screen */}
        <div className="relative w-full h-full rounded-[30px] bg-eggshell overflow-hidden">
          {/* Status bar */}
          <div className="flex items-center justify-between px-6 pt-[44px] pb-2 text-[10px] font-body font-medium text-obsidian">
            <span>9:41</span>
            <div className="flex items-center gap-1">
              <svg width="14" height="10" viewBox="0 0 14 10" fill="currentColor">
                <rect x="0" y="6" width="2.5" height="4" rx="0.5" />
                <rect x="3.5" y="4" width="2.5" height="6" rx="0.5" />
                <rect x="7" y="2" width="2.5" height="8" rx="0.5" />
                <rect x="10.5" y="0" width="2.5" height="10" rx="0.5" />
              </svg>
              <svg width="20" height="10" viewBox="0 0 20 10" fill="currentColor">
                <rect x="0" y="0" width="18" height="10" rx="2" stroke="currentColor" strokeWidth="1" fill="none" />
                <rect x="2" y="2" width="12" height="6" rx="1" />
                <rect x="18.5" y="3" width="1.5" height="4" rx="0.5" />
              </svg>
            </div>
          </div>

          {/* App content */}
          <div className="px-4 pb-4 h-[calc(100%-60px)] overflow-hidden">
            {children}
          </div>

          {/* Home indicator */}
          <div className="absolute bottom-2 left-1/2 -translate-x-1/2 w-[100px] h-[4px] rounded-full bg-obsidian/20" />
        </div>
      </div>

      {label && (
        <span className="text-sm font-body font-medium text-gravel">
          {label}
        </span>
      )}
    </div>
  );
}
