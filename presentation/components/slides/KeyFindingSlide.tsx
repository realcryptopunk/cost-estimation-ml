"use client";

import { Slide } from "../Slide";
import { SectionLabel } from "../ui/SectionLabel";
import { useSlide } from "../SlideProvider";
import { StatCard } from "../ui/StatCard";
import { FEATURE_SETS } from "../../lib/data";

export function KeyFindingSlide() {
  const { current } = useSlide();

  return (
    <Slide index={5}>
      <div className="flex flex-col items-center text-center gap-10">
        <SectionLabel>Key Finding</SectionLabel>

        <div className="flex flex-col items-center gap-2">
          <span className="font-display font-light text-8xl tracking-tight text-obsidian">
            +0.85%
          </span>
          <span className="text-xl font-body text-gravel">
            R² improvement from CCI features
          </span>
        </div>

        <div className="grid grid-cols-2 gap-6 w-full max-w-2xl">
          <div className="rounded-2xl bg-white p-6 shadow-card flex flex-col items-center gap-3">
            <span className="text-xs font-body font-medium text-gravel uppercase tracking-wider">
              Feature Set A
            </span>
            <StatCard
              value={FEATURE_SETS.A.r2 * 100}
              label="R-squared"
              suffix="%"
              active={current === 5}
            />
            <div className="flex gap-4 text-center">
              <div className="flex flex-col">
                <span className="text-sm font-mono text-obsidian">
                  {FEATURE_SETS.A.rmse}
                </span>
                <span className="text-xs text-gravel">RMSE</span>
              </div>
              <div className="flex flex-col">
                <span className="text-sm font-mono text-obsidian">
                  {FEATURE_SETS.A.mape}%
                </span>
                <span className="text-xs text-gravel">MAPE</span>
              </div>
            </div>
          </div>

          <div className="rounded-2xl bg-obsidian p-6 shadow-card flex flex-col items-center gap-3">
            <span className="text-xs font-body font-medium text-eggshell/60 uppercase tracking-wider">
              Feature Set B
            </span>
            <div className="flex flex-col items-center gap-2 rounded-2xl p-4">
              <span className="font-display font-light text-5xl tracking-tight text-eggshell leading-none">
                {(FEATURE_SETS.B.r2 * 100).toFixed(2)}%
              </span>
              <span className="text-sm font-body font-normal text-eggshell/60">
                R-squared
              </span>
            </div>
            <div className="flex gap-4 text-center">
              <div className="flex flex-col">
                <span className="text-sm font-mono text-eggshell">
                  {FEATURE_SETS.B.rmse}
                </span>
                <span className="text-xs text-eggshell/60">RMSE</span>
              </div>
              <div className="flex flex-col">
                <span className="text-sm font-mono text-eggshell">
                  {FEATURE_SETS.B.mape}%
                </span>
                <span className="text-xs text-eggshell/60">MAPE</span>
              </div>
            </div>
          </div>
        </div>

        <p className="text-sm font-body text-gravel max-w-lg">
          CCI features alone provide +0.85% R² lift. Adding macro indicators
          and derived features yields diminishing returns, confirming that
          city-level cost indices are the primary value driver.
        </p>
      </div>
    </Slide>
  );
}
