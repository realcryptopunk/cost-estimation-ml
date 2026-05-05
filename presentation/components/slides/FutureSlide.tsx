import { Slide } from "../Slide";
import { SectionLabel } from "../ui/SectionLabel";

const steps = [
  {
    n: "1",
    title: "Scan",
    desc: "LiDAR 3D scan, up to 5 photos, or manual dimensions. Works on every iPhone.",
  },
  {
    n: "2",
    title: "Describe",
    desc: "Type or dictate what you\u2019re building. Real-time voice transcription for the job site.",
  },
  {
    n: "3",
    title: "Estimate",
    desc: "Claude AI generates a build list across 17 trade categories, priced with your state\u2019s CCI.",
  },
  {
    n: "4",
    title: "Share",
    desc: "Export a branded PDF estimate or numbered invoice. Send via text, email, or AirDrop.",
  },
];

const features = [
  { title: "17 Trade Categories", desc: "Demolition to Equipment Rental" },
  { title: "50-State CCI Pricing", desc: "BLS Construction Cost Indices" },
  { title: "Voice Input", desc: "Dictate on the job site" },
  { title: "Smart Upsell Suggestions", desc: "3-5 upgrades per estimate" },
  { title: "Before & After Viz", desc: "AI-generated finish preview" },
  { title: "Invoice Conversion", desc: "Estimate to invoice in one tap" },
];

export function FutureSlide() {
  return (
    <Slide index={12}>
      <div className="flex flex-col gap-8">
        <div className="flex flex-col gap-2">
          <SectionLabel>What&apos;s Next</SectionLabel>
          <h2 className="font-display font-light text-5xl tracking-tight text-obsidian leading-tight">
            BuildScan
          </h2>
          <p className="text-base font-body text-gravel max-w-3xl leading-relaxed">
            AI-powered construction cost estimation for contractors. Point your
            phone, describe the job, and get a professional proposal you can
            share with clients — complete with regional pricing, itemized build
            lists, and upgrade recommendations.
          </p>
        </div>

        {/* 4-step flow */}
        <div className="grid grid-cols-4 gap-3">
          {steps.map((s, i) => (
            <div
              key={s.title}
              className="flex flex-col gap-3 rounded-2xl bg-white p-5 shadow-card relative"
            >
              <span className="font-display font-light text-3xl text-obsidian">
                {s.n}
              </span>
              <div className="flex flex-col gap-1">
                <span className="text-sm font-body font-medium text-obsidian">
                  {s.title}
                </span>
                <span className="text-xs font-body text-gravel leading-snug">
                  {s.desc}
                </span>
              </div>
              {i < steps.length - 1 && (
                <div className="absolute right-0 top-1/2 -translate-y-1/2 translate-x-1/2 z-10">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#b1b0b0" strokeWidth="2">
                    <path d="M9 18l6-6-6-6" />
                  </svg>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Feature grid */}
        <div className="grid grid-cols-3 gap-3">
          {features.map((f) => (
            <div
              key={f.title}
              className="flex items-center gap-3 rounded-xl bg-white px-4 py-3 shadow-card"
            >
              <div className="w-1.5 h-1.5 rounded-full bg-obsidian shrink-0" />
              <div className="flex flex-col">
                <span className="text-xs font-body font-medium text-obsidian">
                  {f.title}
                </span>
                <span className="text-[10px] font-body text-gravel">
                  {f.desc}
                </span>
              </div>
            </div>
          ))}
        </div>

        {/* Thesis connection */}
        <div className="rounded-2xl bg-obsidian p-5 shadow-card">
          <p className="text-sm font-body text-eggshell leading-relaxed">
            <span className="text-eggshell/50 font-mono text-xs uppercase tracking-wider">
              Thesis → Product{" "}
            </span>
            The +0.85% R² lift from CCI features validates the core engine.
            BuildScan applies BLS Construction Cost Indices across all 50 states
            so every line item reflects your local market.
          </p>
        </div>
      </div>
    </Slide>
  );
}
