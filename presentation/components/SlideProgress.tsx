"use client";

import { useSlide } from "./SlideProvider";

export function SlideProgress() {
  const { current, total, next, prev } = useSlide();
  const progress = ((current + 1) / total) * 100;

  return (
    <>
      {/* Progress bar */}
      <div className="fixed bottom-0 left-0 right-0 h-0.5 bg-chalk z-50">
        <div
          className="h-full bg-obsidian transition-all duration-400 ease-out"
          style={{ width: `${progress}%` }}
        />
      </div>

      {/* Slide counter + nav */}
      <div className="fixed bottom-5 right-8 flex items-center gap-4 z-50">
        <button
          onClick={prev}
          className="w-8 h-8 flex items-center justify-center rounded-full border border-chalk text-gravel hover:text-obsidian hover:border-obsidian transition-colors"
          aria-label="Previous slide"
        >
          <svg
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
          >
            <path d="M15 18l-6-6 6-6" />
          </svg>
        </button>
        <span className="text-sm font-body text-gravel tabular-nums">
          {current + 1} / {total}
        </span>
        <button
          onClick={next}
          className="w-8 h-8 flex items-center justify-center rounded-full border border-chalk text-gravel hover:text-obsidian hover:border-obsidian transition-colors"
          aria-label="Next slide"
        >
          <svg
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
          >
            <path d="M9 18l6-6-6-6" />
          </svg>
        </button>
      </div>
    </>
  );
}
