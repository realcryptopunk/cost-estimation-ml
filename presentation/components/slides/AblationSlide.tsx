import { Slide } from "../Slide";
import { SectionLabel } from "../ui/SectionLabel";
import { FigureCard } from "../ui/FigureCard";
import { ABLATION } from "../../lib/data";

const steps = [
  ABLATION.base,
  ABLATION.plusCCI,
  ABLATION.plusMacro,
  ABLATION.fullB,
];

export function AblationSlide() {
  return (
    <Slide index={6}>
      <div className="flex flex-col gap-8">
        <div className="flex flex-col gap-3">
          <SectionLabel>Ablation Study</SectionLabel>
          <h2 className="font-display font-light text-5xl tracking-tight text-obsidian leading-tight">
            Which features matter most?
          </h2>
        </div>

        <div className="grid grid-cols-2 gap-6">
          <FigureCard
            src="/figures/ablation_study.png"
            alt="Ablation study showing incremental R² gains from each feature group"
            caption="Incremental R² improvement by feature group"
          />

          <div className="flex flex-col gap-3">
            {steps.map((step, i) => {
              const isTop = step.label === "+CCI";
              return (
                <div
                  key={step.label}
                  className={`rounded-2xl p-4 flex items-center gap-4 ${
                    isTop
                      ? "bg-obsidian text-eggshell shadow-card"
                      : "bg-white shadow-card"
                  }`}
                >
                  <div className="flex flex-col items-center shrink-0 w-14">
                    <span
                      className={`font-display font-light text-2xl tracking-tight ${isTop ? "text-eggshell" : "text-obsidian"}`}
                    >
                      {step.features}
                    </span>
                    <span
                      className={`text-xs font-body ${isTop ? "text-eggshell/60" : "text-gravel"}`}
                    >
                      feat
                    </span>
                  </div>

                  <div className="flex-1">
                    <span
                      className={`text-sm font-body font-medium ${isTop ? "text-eggshell" : "text-obsidian"}`}
                    >
                      {step.label}
                    </span>
                    <div className="flex gap-4 mt-1">
                      <span
                        className={`text-xs font-mono ${isTop ? "text-eggshell/70" : "text-gravel"}`}
                      >
                        R² {(step.r2 * 100).toFixed(2)}%
                      </span>
                      <span
                        className={`text-xs font-mono ${isTop ? "text-eggshell/70" : "text-gravel"}`}
                      >
                        MAPE {step.mape}%
                      </span>
                    </div>
                  </div>

                  {i > 0 && (
                    <span
                      className={`text-xs font-mono ${isTop ? "text-eggshell/80" : "text-gravel"}`}
                    >
                      {((step.r2 - ABLATION.base.r2) * 100).toFixed(2) + "%"}
                    </span>
                  )}
                </div>
              );
            })}

            <p className="text-sm font-body text-gravel mt-2 leading-relaxed">
              CCI features provide the dominant lift (+0.85%). Macro indicators
              add marginal noise, and derived features recover slightly.
            </p>
          </div>
        </div>
      </div>
    </Slide>
  );
}
