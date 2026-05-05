import { Slide } from "../Slide";
import { SectionLabel } from "../ui/SectionLabel";
import { FigureCard } from "../ui/FigureCard";
import { REGIONS } from "../../lib/data";

export function RegionalSlide() {
  return (
    <Slide index={7}>
      <div className="flex flex-col gap-8">
        <div className="flex flex-col gap-3">
          <SectionLabel>Regional Performance</SectionLabel>
          <h2 className="font-display font-light text-5xl tracking-tight text-obsidian leading-tight">
            How does the model perform across US regions?
          </h2>
        </div>

        <div className="grid grid-cols-2 gap-5">
          <FigureCard
            src="/figures/regional_r2_comparison.png"
            alt="R² comparison across 5 US regions for all models"
            caption="R² by region"
          />
          <FigureCard
            src="/figures/regional_mape_comparison.png"
            alt="MAPE comparison across 5 US regions for all models"
            caption="MAPE by region"
          />
        </div>

        <div className="flex gap-3 justify-center">
          {REGIONS.map((r) => (
            <div
              key={r.name}
              className="flex flex-col items-center gap-1 rounded-full bg-white px-5 py-3 shadow-card"
            >
              <span className="text-sm font-body font-medium text-obsidian">
                {r.name}
              </span>
              <span className="text-xs font-mono text-gravel">
                R² {(r.r2 * 100).toFixed(2)}%
              </span>
            </div>
          ))}
        </div>
      </div>
    </Slide>
  );
}
