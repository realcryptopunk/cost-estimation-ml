import { Slide } from "../Slide";
import { SectionLabel } from "../ui/SectionLabel";
import { FeatureBar } from "../ui/FeatureBar";
import { FigureCard } from "../ui/FigureCard";
import { SHAP_TOP } from "../../lib/data";

export function ShapSlide() {
  const maxVal = SHAP_TOP[0].importance;

  return (
    <Slide index={8}>
      <div className="flex flex-col gap-8">
        <div className="flex flex-col gap-3">
          <SectionLabel>Explainability</SectionLabel>
          <h2 className="font-display font-light text-5xl tracking-tight text-obsidian leading-tight">
            What drives the predictions?
          </h2>
        </div>

        <div className="grid grid-cols-2 gap-6">
          <div className="flex flex-col gap-6">
            <div className="rounded-2xl bg-white p-6 shadow-card">
              <p className="text-xs font-mono text-slate mb-4 uppercase tracking-wider">
                Global Feature Importance (Mean |SHAP|)
              </p>
              <div className="flex flex-col gap-3">
                {SHAP_TOP.map((f) => (
                  <FeatureBar
                    key={f.feature}
                    label={f.label}
                    value={f.importance}
                    maxValue={maxVal}
                  />
                ))}
              </div>
            </div>

            <p className="text-sm font-body text-gravel leading-relaxed">
              Project type dominates (39.1%), confirming that building category
              is the strongest cost driver. CCI-derived features
              (cci_deviation, weighted_cci, labor_cci) collectively account for
              21.6% of importance.
            </p>
          </div>

          <FigureCard
            src="/figures/shap_beeswarm_global.png"
            alt="SHAP beeswarm plot showing feature value impact on model output"
            caption="SHAP beeswarm plot — each dot is a prediction"
          />
        </div>
      </div>
    </Slide>
  );
}
