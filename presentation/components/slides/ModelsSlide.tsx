import { Slide } from "../Slide";
import { SectionLabel } from "../ui/SectionLabel";
import { MetricTable } from "../ui/MetricTable";
import { MODELS } from "../../lib/data";

export function ModelsSlide() {
  const headers = ["Model", "R²", "RMSE", "MAPE", "Rank"];
  const rows = MODELS.map((m) => [
    m.name,
    (m.r2 * 100).toFixed(2) + "%",
    m.rmse.toFixed(2),
    m.mape.toFixed(2) + "%",
    "#" + m.rank,
  ]);

  return (
    <Slide index={4}>
      <div className="flex flex-col gap-10">
        <div className="flex flex-col gap-3">
          <SectionLabel>Model Comparison</SectionLabel>
          <h2 className="font-display font-light text-5xl tracking-tight text-obsidian leading-tight">
            Five models, one winner
          </h2>
          <p className="text-base font-body text-gravel max-w-2xl leading-relaxed">
            All models trained with Feature Set B (28 features). Evaluated via
            5-fold region-stratified cross-validation on training data
            (2015-2023).
          </p>
        </div>

        <MetricTable headers={headers} rows={rows} highlightRow={0} />

        <div className="flex items-center gap-3 text-sm font-body text-gravel">
          <span className="w-3 h-3 rounded-sm bg-obsidian" />
          <span>CatBoost achieves highest R² and lowest MAPE across all metrics</span>
        </div>
      </div>
    </Slide>
  );
}
