import { Slide } from "../Slide";
import { SectionLabel } from "../ui/SectionLabel";
import { AppScreenshot } from "../ui/AppScreenshot";

export function AppScanSlide() {
  return (
    <Slide index={13}>
      <div className="flex items-center gap-16">
        <div className="flex-1 flex flex-col gap-6">
          <SectionLabel>App Demo</SectionLabel>
          <h2 className="font-display font-light text-5xl tracking-tight text-obsidian leading-tight">
            3 ways to capture
          </h2>
          <p className="text-base font-body text-gravel leading-relaxed">
            BuildScan works on every iPhone. Choose the capture method that fits
            the situation.
          </p>

          <div className="flex flex-col gap-4">
            {[
              {
                title: "LiDAR Room Scan",
                desc: "Walk around the room and get precise 3D measurements. Walls, windows, doors, and furniture detected automatically.",
                detail: "iPhone 12 Pro and later",
              },
              {
                title: "Multi-Photo Capture",
                desc: "Take up to 5 photos from different angles. The AI uses visual details to refine quantities and identify existing materials.",
                detail: "Any iPhone",
              },
              {
                title: "Manual Entry",
                desc: "Type length, width, ceiling height, and window/door counts. Works offline, works everywhere.",
                detail: "No camera needed",
              },
            ].map((f) => (
              <div key={f.title} className="rounded-xl bg-white p-4 shadow-card">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-body font-medium text-obsidian">{f.title}</span>
                  <span className="text-[10px] font-mono text-slate">{f.detail}</span>
                </div>
                <p className="text-xs font-body text-gravel leading-snug">{f.desc}</p>
              </div>
            ))}
          </div>

          <div className="rounded-xl bg-powder px-4 py-3 flex items-center gap-3">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#777169" strokeWidth="2">
              <path d="M12 1a3 3 0 00-3 3v8a3 3 0 006 0V4a3 3 0 00-3-3z" />
              <path d="M19 10v2a7 7 0 01-14 0v-2M12 19v4M8 23h8" />
            </svg>
            <div>
              <span className="text-xs font-body font-medium text-obsidian">Voice Input</span>
              <span className="text-xs font-body text-gravel ml-1">
                — Tap the mic and describe the job out loud. Built for dirty hands on a job site.
              </span>
            </div>
          </div>
        </div>

        <AppScreenshot
          src="/figures/app_scan.png"
          alt="BuildScan LiDAR room scanning interface showing 3D room capture"
          label="LiDAR Scan"
        />
      </div>
    </Slide>
  );
}
