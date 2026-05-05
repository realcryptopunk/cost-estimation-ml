"use client";

import { useEffect, useRef, useState } from "react";

function AnimatedNumber({
  value,
  decimals = 2,
  suffix = "",
  prefix = "",
  active,
}: {
  value: number;
  decimals?: number;
  suffix?: string;
  prefix?: string;
  active: boolean;
}) {
  const [display, setDisplay] = useState(0);
  const animating = useRef(false);

  useEffect(() => {
    if (!active || animating.current) return;
    animating.current = true;

    const duration = 1200;
    const start = performance.now();

    function tick(now: number) {
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setDisplay(value * eased);
      if (progress < 1) requestAnimationFrame(tick);
    }

    requestAnimationFrame(tick);
  }, [active, value]);

  return (
    <span>
      {prefix}
      {display.toFixed(decimals)}
      {suffix}
    </span>
  );
}

export function StatCard({
  value,
  label,
  suffix = "",
  prefix = "",
  decimals = 2,
  delta,
  active = true,
}: {
  value: number;
  label: string;
  suffix?: string;
  prefix?: string;
  decimals?: number;
  delta?: string;
  active?: boolean;
}) {
  return (
    <div className="flex flex-col items-center gap-2 rounded-2xl bg-white p-6 shadow-card">
      <span className="font-display font-light text-5xl tracking-tight text-obsidian leading-none">
        <AnimatedNumber
          value={value}
          decimals={decimals}
          suffix={suffix}
          prefix={prefix}
          active={active}
        />
      </span>
      <span className="text-sm font-body font-normal text-gravel">{label}</span>
      {delta && (
        <span className="inline-flex items-center rounded-full bg-powder px-3 py-0.5 text-xs font-body font-medium text-gravel">
          {delta}
        </span>
      )}
    </div>
  );
}
