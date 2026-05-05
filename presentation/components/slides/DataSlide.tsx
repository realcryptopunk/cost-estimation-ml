import { Slide } from "../Slide";
import { SectionLabel } from "../ui/SectionLabel";

function PipelineNode({
  label,
  sub,
  accent = false,
}: {
  label: string;
  sub: string;
  accent?: boolean;
}) {
  return (
    <div
      className={`flex flex-col items-center gap-1 rounded-2xl px-5 py-3 text-center shadow-card ${
        accent
          ? "bg-obsidian text-eggshell"
          : "bg-white text-obsidian"
      }`}
    >
      <span className={`text-xs font-body font-medium ${accent ? "text-eggshell" : "text-obsidian"}`}>
        {label}
      </span>
      <span className={`text-[10px] font-mono ${accent ? "text-eggshell/60" : "text-slate"}`}>
        {sub}
      </span>
    </div>
  );
}

function Arrow({ vertical = false }: { vertical?: boolean }) {
  if (vertical) {
    return (
      <div className="flex justify-center py-1">
        <svg width="12" height="20" viewBox="0 0 12 20" fill="none">
          <path d="M6 0L6 16M6 16L1 11M6 16L11 11" stroke="#b1b0b0" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </div>
    );
  }
  return (
    <div className="flex items-center px-1">
      <svg width="24" height="12" viewBox="0 0 24 12" fill="none">
        <path d="M0 6H20M20 6L15 1M20 6L15 11" stroke="#b1b0b0" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    </div>
  );
}

export function DataSlide() {
  return (
    <Slide index={2}>
      <div className="flex flex-col gap-8">
        <div className="flex flex-col gap-3">
          <SectionLabel>Data</SectionLabel>
          <h2 className="font-display font-light text-5xl tracking-tight text-obsidian leading-tight">
            Four data sources, one pipeline
          </h2>
        </div>

        {/* Visual pipeline */}
        <div className="rounded-2xl bg-white p-8 shadow-card">
          {/* Row 1: Data Sources */}
          <div className="flex items-center justify-center gap-2 mb-2">
            <PipelineNode label="RSMeans CCI" sub="50 cities x 5 regions" />
            <PipelineNode label="FRED PPI" sub="lumber, steel, cement" />
            <PipelineNode label="BLS CPI" sub="national + regional" />
            <PipelineNode label="BEA GDP" sub="housing, permits" />
          </div>

          {/* Converging arrows */}
          <div className="flex justify-center py-2">
            <svg width="400" height="30" viewBox="0 0 400 30" fill="none">
              <path d="M60 0 L200 26" stroke="#b1b0b0" strokeWidth="1.5" strokeLinecap="round" />
              <path d="M150 0 L200 26" stroke="#b1b0b0" strokeWidth="1.5" strokeLinecap="round" />
              <path d="M250 0 L200 26" stroke="#b1b0b0" strokeWidth="1.5" strokeLinecap="round" />
              <path d="M340 0 L200 26" stroke="#b1b0b0" strokeWidth="1.5" strokeLinecap="round" />
              <circle cx="200" cy="28" r="2" fill="#b1b0b0" />
            </svg>
          </div>

          {/* Row 2: Processing */}
          <div className="flex items-center justify-center gap-2">
            <PipelineNode label="data_collection.py" sub="fetch APIs" />
            <Arrow />
            <PipelineNode label="preprocessing.py" sub="merge + engineer" accent />
            <Arrow />
            <PipelineNode label="model_ready.csv" sub="28 features" />
          </div>

          {/* Split arrow */}
          <div className="flex justify-center py-2">
            <svg width="300" height="30" viewBox="0 0 300 30" fill="none">
              <path d="M150 0 L150 10" stroke="#b1b0b0" strokeWidth="1.5" strokeLinecap="round" />
              <path d="M150 10 L80 26" stroke="#b1b0b0" strokeWidth="1.5" strokeLinecap="round" />
              <path d="M150 10 L220 26" stroke="#b1b0b0" strokeWidth="1.5" strokeLinecap="round" />
              <circle cx="80" cy="28" r="2" fill="#b1b0b0" />
              <circle cx="220" cy="28" r="2" fill="#b1b0b0" />
            </svg>
          </div>

          {/* Row 3: Train/Test split */}
          <div className="flex items-center justify-center gap-12">
            <PipelineNode label="Training Set" sub="2015 - 2023 | ~2,200 records" accent />
            <PipelineNode label="Test Set" sub="2024 - 2025 | ~550 records" />
          </div>

          {/* Arrow down */}
          <Arrow vertical />

          {/* Row 4: Models */}
          <div className="flex items-center justify-center gap-2">
            {["CatBoost", "XGBoost", "LightGBM", "RF", "MLP"].map((m) => (
              <div
                key={m}
                className={`rounded-full px-3 py-1.5 text-[10px] font-mono ${
                  m === "CatBoost"
                    ? "bg-obsidian text-eggshell"
                    : "bg-powder text-obsidian border border-chalk"
                }`}
              >
                {m}
              </div>
            ))}
          </div>
        </div>

        {/* Stats row */}
        <div className="grid grid-cols-4 gap-3">
          {[
            { n: "2,750", l: "Projects", sub: "synthetic + real" },
            { n: "50", l: "Cities", sub: "across US" },
            { n: "5", l: "Regions", sub: "MW, NE, SE, SW, W" },
            { n: "10yr", l: "Span", sub: "2015 - 2025" },
          ].map((s) => (
            <div
              key={s.l}
              className="flex flex-col items-center gap-1 rounded-2xl bg-white p-4 shadow-card"
            >
              <span className="font-display font-light text-3xl text-obsidian tracking-tight">
                {s.n}
              </span>
              <span className="text-sm font-body font-medium text-obsidian">{s.l}</span>
              <span className="text-xs font-body text-slate">{s.sub}</span>
            </div>
          ))}
        </div>
      </div>
    </Slide>
  );
}
