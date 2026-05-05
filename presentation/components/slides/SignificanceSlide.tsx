import { Slide } from "../Slide";
import { SectionLabel } from "../ui/SectionLabel";
import { MetricTable } from "../ui/MetricTable";
import { SIGNIFICANCE } from "../../lib/data";

export function SignificanceSlide() {
  const headers = [
    "Comparison",
    "Mean R² Diff",
    "p-value",
    "Cohen's d",
    "95% CI",
  ];
  const rows = SIGNIFICANCE.map((s) => [
    `${s.modelA} vs ${s.modelB}`,
    "+" + (s.meanDiff * 100).toFixed(2) + "%",
    s.correctedP < 0.01 ? s.correctedP.toFixed(4) : s.correctedP.toFixed(4),
    s.cohensD.toFixed(2),
    `[${(s.ciLower * 100).toFixed(2)}, ${(s.ciUpper * 100).toFixed(2)}]`,
  ]);

  return (
    <Slide index={10}>
      <div className="flex flex-col gap-8">
        <div className="flex flex-col gap-3">
          <SectionLabel>Statistical Rigor</SectionLabel>
          <h2 className="font-display font-light text-5xl tracking-tight text-obsidian leading-tight">
            Are the differences significant?
          </h2>
        </div>

        <MetricTable headers={headers} rows={rows} />

        <div className="grid grid-cols-2 gap-5">
          <div className="rounded-2xl bg-white p-5 shadow-card">
            <p className="text-sm font-body font-medium text-obsidian mb-2">
              Practical significance
            </p>
            <p className="text-sm font-body text-gravel leading-relaxed">
              Cohen&apos;s d values of 5.3+ indicate large effect sizes.
              CatBoost vs Random Forest (d=9.93) shows the strongest practical
              difference.
            </p>
          </div>
          <div className="rounded-2xl bg-white p-5 shadow-card">
            <p className="text-sm font-body font-medium text-obsidian mb-2">
              Limited power
            </p>
            <p className="text-sm font-body text-gravel leading-relaxed">
              Wilcoxon tests are constrained by 5 folds (minimum p=0.0625).
              Corrected t-tests provide additional evidence with p&lt;0.005 for
              3 of 4 comparisons.
            </p>
          </div>
        </div>
      </div>
    </Slide>
  );
}
