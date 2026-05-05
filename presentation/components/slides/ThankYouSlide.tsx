import { Slide } from "../Slide";

export function ThankYouSlide() {
  return (
    <Slide index={16}>
      <div className="flex flex-col items-center text-center gap-10 py-16">
        <h2 className="font-display font-light text-7xl tracking-tight text-obsidian">
          Thank You
        </h2>

        <div className="flex flex-col items-center gap-2">
          <span className="text-lg font-body font-medium text-obsidian">
            Navid Roshan
          </span>
          <span className="text-sm font-body text-gravel">
            CS/ML Thesis | 2025
          </span>
        </div>

        <div className="flex items-center gap-4 mt-4">
          <a
            href="#"
            className="inline-flex items-center justify-center rounded-full bg-white px-6 py-2.5 text-sm font-body font-medium text-obsidian border border-chalk shadow-button hover:opacity-80 transition-opacity"
          >
            View Repository
          </a>
        </div>

        <p className="text-sm font-body text-slate mt-8">
          Use arrow keys or spacebar to navigate
        </p>
      </div>
    </Slide>
  );
}
