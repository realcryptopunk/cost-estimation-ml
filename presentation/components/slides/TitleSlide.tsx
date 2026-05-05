"use client";

import { Slide } from "../Slide";
import { StatCard } from "../ui/StatCard";
import { useSlide } from "../SlideProvider";

export function TitleSlide() {
  const { current } = useSlide();

  return (
    <Slide index={0}>
      <div className="flex flex-col items-center text-center gap-10 py-8">
        <h1 className="font-display font-light text-6xl tracking-tight leading-tight text-obsidian max-w-4xl">
          Predicting Construction Costs with Regional Intelligence
        </h1>

        <p className="text-lg font-body font-normal text-gravel max-w-2xl leading-relaxed">
          A multi-model ML approach using city-level cost indices and
          macroeconomic signals to improve regional accuracy in US construction
          cost estimation
        </p>

        <div className="flex items-center gap-3 text-sm font-body text-slate">
          <span>Navid Roshan</span>
          <span className="w-1 h-1 rounded-full bg-chalk" />
          <span>CS/ML Thesis</span>
          <span className="w-1 h-1 rounded-full bg-chalk" />
          <span>2025</span>
        </div>

        <div className="grid grid-cols-3 gap-6 mt-4 w-full max-w-2xl">
          <StatCard
            value={97.48}
            label="R-squared"
            suffix="%"
            active={current === 0}
          />
          <StatCard
            value={2.61}
            label="MAPE"
            suffix="%"
            active={current === 0}
          />
          <StatCard
            value={28}
            label="Features"
            decimals={0}
            active={current === 0}
          />
        </div>
      </div>
    </Slide>
  );
}
