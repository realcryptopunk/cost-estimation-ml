import { Slide } from "../Slide";
import { SectionLabel } from "../ui/SectionLabel";

const hypotheses = [
  {
    id: "H1",
    text: "Integrating CCI features improves prediction accuracy over a national baseline model",
    result: "Confirmed",
    detail: "+0.85% R\u00B2 improvement",
  },
  {
    id: "H2",
    text: "CatBoost outperforms alternative models on regional construction data",
    result: "Confirmed",
    detail: "Highest R\u00B2 across all regions",
  },
  {
    id: "H3",
    text: "Feature importance patterns vary meaningfully across US regions",
    result: "Confirmed",
    detail: "SHAP reveals regional variation",
  },
];

export function ProblemSlide() {
  return (
    <Slide index={1}>
      <div className="flex flex-col gap-10">
        <div className="flex flex-col gap-3">
          <SectionLabel>Research Question</SectionLabel>
          <h2 className="font-display font-light text-5xl tracking-tight text-obsidian leading-tight">
            Can regional cost indices improve construction cost prediction?
          </h2>
          <p className="text-base font-body text-gravel max-w-2xl mt-2 leading-relaxed">
            US construction costs vary dramatically by geography. National
            models ignore city-level labor, material, and equipment cost
            differentials.
          </p>
        </div>

        <div className="grid grid-cols-3 gap-5">
          {hypotheses.map((h) => (
            <div
              key={h.id}
              className="flex flex-col gap-3 rounded-2xl bg-white p-6 shadow-card"
            >
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs text-slate">{h.id}</span>
                <span className="inline-flex items-center rounded-full bg-obsidian text-eggshell px-2.5 py-0.5 text-xs font-body font-medium">
                  {h.result}
                </span>
              </div>
              <p className="text-sm font-body font-medium text-obsidian leading-snug">
                {h.text}
              </p>
              <p className="text-xs font-body text-gravel">{h.detail}</p>
            </div>
          ))}
        </div>
      </div>
    </Slide>
  );
}
