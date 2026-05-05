import { Slide } from "../Slide";
import { SectionLabel } from "../ui/SectionLabel";
import Image from "next/image";

export function ShapRegionalSlide() {
  return (
    <Slide index={9} compact>
      <div className="flex flex-col gap-4">
        <div className="flex items-end justify-between">
          <div className="flex flex-col gap-1">
            <SectionLabel>Regional Explainability</SectionLabel>
            <h2 className="font-display font-light text-4xl tracking-tight text-obsidian leading-tight">
              Feature importance varies by geography
            </h2>
          </div>
          <p className="text-sm font-body text-gravel max-w-sm text-right leading-snug">
            Labor CCI is disproportionately important in the Southeast, while
            material CCI matters more in the Midwest.
          </p>
        </div>

        {/* Full-width regional summary — the main figure */}
        <div className="rounded-2xl bg-white p-3 shadow-card">
          <Image
            src="/figures/shap_regional_summary.png"
            alt="Regional SHAP importance breakdown across 5 US regions"
            width={1400}
            height={600}
            className="w-full h-auto"
            priority
          />
        </div>

        {/* Dependence plots below, narrower but still wide */}
        <div className="rounded-2xl bg-white p-3 shadow-card">
          <Image
            src="/figures/shap_dependence_top4.png"
            alt="SHAP dependence plots for the top 4 features"
            width={1400}
            height={400}
            className="w-full h-auto"
            priority
          />
          <p className="mt-1 text-center text-xs font-body text-gravel">
            Dependence plots — project_type, cci_deviation, area_sqft, weighted_cci
          </p>
        </div>
      </div>
    </Slide>
  );
}
