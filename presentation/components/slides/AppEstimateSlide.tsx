import { Slide } from "../Slide";
import { SectionLabel } from "../ui/SectionLabel";
import { AppScreenshot } from "../ui/AppScreenshot";

export function AppEstimateSlide() {
  return (
    <Slide index={14}>
      <div className="flex items-center gap-16">
        <AppScreenshot
          src="/figures/app_describe.png"
          alt="BuildScan project description screen with project type selector and voice input"
          label="Describe Your Project"
        />

        <div className="flex-1 flex flex-col gap-5">
          <SectionLabel>App Demo</SectionLabel>
          <h2 className="font-display font-light text-5xl tracking-tight text-obsidian leading-tight">
            AI-powered build lists
          </h2>
          <p className="text-base font-body text-gravel leading-relaxed">
            Select a project type, describe what you&apos;re building, and Claude AI
            generates an itemized build list with realistic quantities, waste
            factors, and specifications. No templates — every estimate is custom
            to the job.
          </p>

          <div className="grid grid-cols-2 gap-3">
            <div className="rounded-xl bg-white p-4 shadow-card">
              <span className="text-sm font-body font-medium text-obsidian">5 Project Types</span>
              <p className="text-xs font-body text-gravel mt-1">
                Residential, Commercial, Industrial, Institutional, and
                Infrastructure — each with tuned cost multipliers.
              </p>
            </div>
            <div className="rounded-xl bg-white p-4 shadow-card">
              <span className="text-sm font-body font-medium text-obsidian">17 Trade Categories</span>
              <p className="text-xs font-body text-gravel mt-1">
                Demolition, Framing, Drywall, Electrical, Plumbing, HVAC,
                Flooring, Paint, Tile, Insulation, Fixtures, and more.
              </p>
            </div>
            <div className="rounded-xl bg-white p-4 shadow-card">
              <span className="text-sm font-body font-medium text-obsidian">Smart Upsell Suggestions</span>
              <p className="text-xs font-body text-gravel mt-1">
                3-5 upgrade opportunities per estimate — hardwood over laminate,
                underfloor heating — with instant &ldquo;Add to Estimate.&rdquo;
              </p>
            </div>
            <div className="rounded-xl bg-white p-4 shadow-card">
              <span className="text-sm font-body font-medium text-obsidian">Confidence Indicators</span>
              <p className="text-xs font-body text-gravel mt-1">
                Every line item carries High, Medium, or Low confidence so you
                know which quantities are measured vs. estimated.
              </p>
            </div>
          </div>

          <div className="rounded-xl bg-obsidian px-4 py-3">
            <div className="flex items-center gap-3">
              <span className="text-xs font-mono text-eggshell/50 uppercase tracking-wider shrink-0">
                Pricing
              </span>
              <span className="text-xs font-body text-eggshell/80">
                Subtotal + 10% Overhead + 10% Profit + 5% Contingency = Grand Total
              </span>
            </div>
          </div>
        </div>
      </div>
    </Slide>
  );
}
