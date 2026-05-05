import { Slide } from "../Slide";
import { SectionLabel } from "../ui/SectionLabel";
import { FEATURE_SETS } from "../../lib/data";

export function FeaturesSlide() {
  return (
    <Slide index={3}>
      <div className="flex flex-col gap-10">
        <div className="flex flex-col gap-3">
          <SectionLabel>Feature Engineering</SectionLabel>
          <h2 className="font-display font-light text-5xl tracking-tight text-obsidian leading-tight">
            From 7 to 28 features
          </h2>
          <p className="text-base font-body text-gravel max-w-2xl leading-relaxed">
            Feature Set B extends the baseline with continuous CCI values,
            macroeconomic indicators, and derived interaction features.
          </p>
        </div>

        <div className="grid grid-cols-2 gap-6">
          {/* Feature Set A */}
          <div className="rounded-2xl bg-white p-6 shadow-card flex flex-col gap-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-slate" />
                <span className="text-sm font-body font-medium text-obsidian">
                  {FEATURE_SETS.A.name}
                </span>
              </div>
              <span className="rounded-full bg-powder px-3 py-0.5 text-xs font-body text-gravel">
                {FEATURE_SETS.A.label}
              </span>
            </div>
            <div className="font-display font-light text-4xl text-obsidian tracking-tight">
              {FEATURE_SETS.A.count}{" "}
              <span className="text-lg text-gravel">features</span>
            </div>
            <div className="flex flex-col gap-1.5">
              {FEATURE_SETS.A.features.map((f) => (
                <span key={f} className="text-xs font-mono text-gravel">
                  {f}
                </span>
              ))}
            </div>
            <div className="mt-auto pt-4 border-t border-chalk flex gap-6 text-center">
              <div className="flex flex-col">
                <span className="text-lg font-display font-light text-obsidian">
                  {(FEATURE_SETS.A.r2 * 100).toFixed(2)}%
                </span>
                <span className="text-xs font-body text-gravel">R²</span>
              </div>
              <div className="flex flex-col">
                <span className="text-lg font-display font-light text-obsidian">
                  {FEATURE_SETS.A.mape}%
                </span>
                <span className="text-xs font-body text-gravel">MAPE</span>
              </div>
            </div>
          </div>

          {/* Feature Set B */}
          <div className="rounded-2xl bg-obsidian p-6 shadow-card flex flex-col gap-4 text-eggshell">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-eggshell" />
                <span className="text-sm font-body font-medium text-eggshell">
                  {FEATURE_SETS.B.name}
                </span>
              </div>
              <span className="rounded-full bg-white/10 px-3 py-0.5 text-xs font-body text-eggshell">
                {FEATURE_SETS.B.label}
              </span>
            </div>
            <div className="font-display font-light text-4xl text-eggshell tracking-tight">
              {FEATURE_SETS.B.count}{" "}
              <span className="text-lg text-eggshell/60">features</span>
            </div>
            <div className="flex flex-col gap-2">
              {[
                { group: "Base", desc: "7 project attributes", color: "text-eggshell/50" },
                { group: "CCI", desc: "+4 continuous cost indices", color: "text-eggshell/70" },
                { group: "Macro", desc: "+11 economic indicators", color: "text-eggshell/70" },
                { group: "Derived", desc: "+6 interaction features", color: "text-eggshell/70" },
              ].map((g) => (
                <div key={g.group} className="flex items-center gap-3">
                  <span className="text-xs font-mono text-eggshell/80 w-14">
                    {g.group}
                  </span>
                  <span className={`text-xs font-body ${g.color}`}>
                    {g.desc}
                  </span>
                </div>
              ))}
            </div>
            <div className="mt-auto pt-4 border-t border-white/20 flex gap-6 text-center">
              <div className="flex flex-col">
                <span className="text-lg font-display font-light text-eggshell">
                  {(FEATURE_SETS.B.r2 * 100).toFixed(2)}%
                </span>
                <span className="text-xs font-body text-eggshell/60">R²</span>
              </div>
              <div className="flex flex-col">
                <span className="text-lg font-display font-light text-eggshell">
                  {FEATURE_SETS.B.mape}%
                </span>
                <span className="text-xs font-body text-eggshell/60">
                  MAPE
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Slide>
  );
}
