import { Slide } from "../Slide";
import { SectionLabel } from "../ui/SectionLabel";
import { AppScreenshot } from "../ui/AppScreenshot";

export function AppReportSlide() {
  return (
    <Slide index={15}>
      <div className="flex items-center gap-16">
        <div className="flex-1 flex flex-col gap-5">
          <SectionLabel>App Demo</SectionLabel>
          <h2 className="font-display font-light text-5xl tracking-tight text-obsidian leading-tight">
            Share &amp; invoice
          </h2>
          <p className="text-base font-body text-gravel leading-relaxed">
            Every estimate includes a full cost breakdown with CCI-adjusted
            regional pricing. Export a branded PDF or convert to a numbered
            invoice — send to your client in one tap.
          </p>

          <div className="grid grid-cols-2 gap-3">
            <div className="rounded-xl bg-white p-4 shadow-card">
              <span className="text-sm font-body font-medium text-obsidian">Estimate PDF</span>
              <p className="text-xs font-body text-gravel mt-1">
                Room measurements, line items by trade category, material/labor
                breakdown, CCI annotation, and grand total with overhead, profit,
                and contingency.
              </p>
            </div>
            <div className="rounded-xl bg-white p-4 shadow-card">
              <span className="text-sm font-body font-medium text-obsidian">Invoice PDF</span>
              <p className="text-xs font-body text-gravel mt-1">
                Invoice number, issue/due dates, FROM/BILL TO layout, line items,
                payment terms (Net 15/30/45/60), and totals. Ready to send.
              </p>
            </div>
            <div className="rounded-xl bg-white p-4 shadow-card">
              <span className="text-sm font-body font-medium text-obsidian">Before &amp; After</span>
              <p className="text-xs font-body text-gravel mt-1">
                Tap &ldquo;Visualize Result&rdquo; to see an AI-generated
                description of the finished space with key changes and estimated
                timeframe.
              </p>
            </div>
            <div className="rounded-xl bg-white p-4 shadow-card">
              <span className="text-sm font-body font-medium text-obsidian">Project Portfolio</span>
              <p className="text-xs font-body text-gravel mt-1">
                Save unlimited estimates. Home screen shows total value, average
                estimate, cost split bars, and CCI badges for every project.
              </p>
            </div>
          </div>

          <div className="flex gap-3">
            {[
              { n: "5", l: "Project types" },
              { n: "17", l: "Trade categories" },
              { n: "50", l: "State CCIs" },
            ].map((s) => (
              <div key={s.l} className="flex flex-col items-center gap-1 rounded-xl bg-white px-5 py-3 shadow-card">
                <span className="font-display font-light text-xl text-obsidian">{s.n}</span>
                <span className="text-[10px] font-body text-gravel">{s.l}</span>
              </div>
            ))}
          </div>
        </div>

        <AppScreenshot
          src="/figures/app_estimate.png"
          alt="BuildScan cost estimate screen showing $12,860 total with materials and labor breakdown"
          label="Cost Estimate"
        />
      </div>
    </Slide>
  );
}
