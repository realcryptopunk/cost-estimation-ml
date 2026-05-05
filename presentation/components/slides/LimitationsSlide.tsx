import { Slide } from "../Slide";
import { SectionLabel } from "../ui/SectionLabel";

const limitations = [
  {
    title: "Simulated CCI Data",
    desc: "RSMeans construction cost indices are commercially licensed and paywalled. This study uses synthetically generated CCI data calibrated from published city cost ratios.",
    mitigation:
      "Synthetic data preserves relative cost relationships between cities and regions. The pipeline accepts real CCI tables as a drop-in replacement — no model or architecture changes required.",
  },
  {
    title: "Sample Size",
    desc: "The dataset contains ~2,750 project records across 50 cities. This is modest compared to production-scale construction databases with hundreds of thousands of records.",
    mitigation:
      "Region-stratified 5-fold CV and temporal holdout testing mitigate overfitting risk. All five models converge to similar performance, suggesting the signal is real, not an artifact of small data.",
  },
  {
    title: "Domain Shift on Real Data",
    desc: "A validation experiment on real USA Spending federal procurement data (8,464 records) yielded R\u00B2 near zero — the model trained on synthetic data did not generalize to real-world federal projects.",
    mitigation:
      "This is an honest and expected result. Federal procurement pricing follows different cost structures than commercial construction. It validates the need for domain-specific training data.",
  },
  {
    title: "Statistical Power",
    desc: "With 5 CV folds, Wilcoxon signed-rank tests have a minimum achievable p-value of 0.0625, limiting the ability to claim significance at conventional thresholds.",
    mitigation:
      "Corrected paired t-tests (Nadeau & Bengio, 2003) and large Cohen\u2019s d effect sizes (up to 9.93) provide converging evidence of practically meaningful differences.",
  },
];

export function LimitationsSlide() {
  return (
    <Slide index={11}>
      <div className="flex flex-col gap-6">
        <div className="flex flex-col gap-2">
          <SectionLabel>Limitations &amp; Disclosure</SectionLabel>
          <h2 className="font-display font-light text-5xl tracking-tight text-obsidian leading-tight">
            What this study does not claim
          </h2>
          <p className="text-base font-body text-gravel max-w-3xl leading-relaxed">
            Transparency about data provenance and methodological constraints
            is essential to interpreting the results correctly.
          </p>
        </div>

        <div className="flex flex-col gap-3">
          {limitations.map((l) => (
            <div
              key={l.title}
              className="rounded-2xl bg-white shadow-card overflow-hidden"
            >
              <div className="flex">
                {/* Left: limitation */}
                <div className="flex-1 p-5 border-r border-chalk">
                  <div className="flex items-center gap-2 mb-2">
                    <div className="w-2 h-2 rounded-full bg-obsidian shrink-0" />
                    <span className="text-sm font-body font-medium text-obsidian">
                      {l.title}
                    </span>
                  </div>
                  <p className="text-xs font-body text-gravel leading-relaxed">
                    {l.desc}
                  </p>
                </div>

                {/* Right: mitigation */}
                <div className="flex-1 p-5 bg-powder/40">
                  <span className="text-[10px] font-mono text-slate uppercase tracking-wider">
                    Mitigation
                  </span>
                  <p className="text-xs font-body text-obsidian leading-relaxed mt-1.5">
                    {l.mitigation}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="rounded-2xl bg-obsidian p-5">
          <p className="text-sm font-body text-eggshell leading-relaxed">
            <span className="text-eggshell/50 font-mono text-xs uppercase tracking-wider mr-2">
              Key takeaway
            </span>
            The contribution of this work is the{" "}
            <span className="font-medium text-eggshell">methodology</span>, not
            the specific model weights. The finding that CCI features improve
            regional prediction accuracy is robust to the synthetic data
            constraint — retraining on licensed RSMeans data would preserve
            the architecture and likely improve absolute performance.
          </p>
        </div>
      </div>
    </Slide>
  );
}
