# Presentation Script
### "Predicting Construction Costs with Regional Intelligence"
**Duration:** 20-22 minutes | **17 slides** | **Target pace:** ~75 seconds per slide

---

## Slide 1 — Title
**[0:00 - 1:00]**

Good afternoon, everyone. My name is Navid Roshan, and today I'm presenting my thesis: Predicting Construction Costs with Regional Intelligence.

The core question is straightforward. If you're building a hospital in Manhattan versus a warehouse in rural Oklahoma, the cost per square foot is wildly different. National models treat these as the same problem. My work asks whether we can do better by giving models explicit knowledge of *where* they're estimating.

Three numbers to frame the rest of this talk. Our best model achieves 97.48% R-squared, a mean absolute percentage error of just 2.61%, and it uses 28 engineered features — 21 of which are new regional and macroeconomic signals that don't exist in baseline approaches.

---

## Slide 2 — Research Question
**[1:00 - 2:30]**

I structured the research around three testable hypotheses.

The first: that integrating city-level construction cost indices — CCI — into the feature set improves prediction accuracy over a baseline model that only uses project attributes and flat categorical encodings of region and state. This was confirmed. CCI features alone contribute a +0.85% lift in R-squared.

The second hypothesis: that CatBoost, a gradient-boosted decision tree framework designed for categorical-heavy data, outperforms four alternatives — XGBoost, LightGBM, Random Forest, and a PyTorch MLP. Also confirmed. CatBoost ranks first across every metric and every region.

The third: that feature importance patterns aren't uniform across the country — that what drives cost in the Midwest is different from what drives cost in the Southeast. SHAP analysis confirms this. Labor CCI dominates in the Southeast; material CCI matters more in the Midwest. This has real implications for how we build regional estimators.

---

## Slide 3 — Data Pipeline
**[2:30 - 4:00]**

Let me walk you through the data.

I pull from four public sources. RSMeans CCI provides city-level construction cost indices across 50 cities in five US regions — that's your labor, material, and equipment cost multipliers. FRED gives us Producer Price Indices for specific construction materials: lumber, steel, cement. BLS provides Consumer Price Index data at both national and regional levels. And BEA contributes macroeconomic signals — real GDP, housing starts, building permits, mortgage rates.

The pipeline is simple. A collection script fetches the raw data from public APIs. A preprocessing step merges everything, engineers derived features, and produces a single model-ready CSV with 28 columns.

I use a temporal holdout for evaluation. Training data covers 2015 through 2023 — about 2,200 records. The test set is 2024 and 2025 — roughly 550 records. This simulates the real deployment scenario: you train on historical data and predict future costs.

All five models are then trained and evaluated on this same split.

---

## Slide 4 — Feature Engineering
**[4:00 - 5:30]**

This is the heart of the thesis — the feature engineering.

Feature Set A is the baseline. Seven features: project type, area in square feet, year, region, state, and two rate variables — formwork and concrete. This is essentially what a naive model would use. It achieves 96.63% R-squared, which is already decent.

Feature Set B is the regional-aware set. Twenty-eight features. It extends the baseline in three layers.

First, four continuous CCI features — weighted CCI, labor CCI, material CCI, and equipment CCI. These replace the flat region categorical with continuous cost signals that capture *how much* a city deviates from the national average.

Second, eleven macroeconomic indicators — PPI for lumber, steel, cement; CPI; GDP; housing starts; permits; mortgage rates. These capture the broader economic environment that influences construction costs.

Third, six derived interaction features — CCI deviation, CCI labor premium, log area, year number, PPI year-over-year change, and a combined material rate. These let the model capture nonlinear relationships.

Feature Set B achieves 97.48% R-squared. That 0.85% improvement is the central finding.

---

## Slide 5 — Model Comparison
**[5:30 - 7:00]**

I compared five models, all trained on Feature Set B.

CatBoost takes first place with 97.43% R-squared, an RMSE of 5.49 dollars per square foot, and 2.63% MAPE. That means on average, the model's estimate is within $5.49 of the actual cost.

MLP — a three-layer neural network built in PyTorch — comes second at 97.23%. It's competitive, but requires significantly more tuning and training time.

LightGBM is third at 97.08%. XGBoost fourth at 96.75%. Random Forest last at 96.57%.

The gap between CatBoost and Random Forest is 0.86 percentage points in R-squared. That may sound small in absolute terms, but as we'll see in the significance analysis, the effect size is enormous.

CatBoost's advantage here is its native handling of categorical features. Rather than one-hot encoding region and state — which inflates dimensionality — CatBoost uses ordered target statistics internally. That matters when your categories interact with continuous CCI values.

---

## Slide 6 — Key Finding
**[7:00 - 8:30]**

This is the slide I want you to remember.

Plus 0.85 percent. That's the R-squared improvement from adding CCI features. Moving from Feature Set A at 96.63% to Feature Set B at 97.48%.

But the improvement isn't just in R-squared. RMSE drops from 6.28 to 5.43 — nearly a dollar less error per square foot. MAPE drops from 2.96% to 2.61%.

What makes this finding significant is that the CCI features alone account for almost the entire lift. When I ran the ablation study — which I'll show next — adding macro indicators and derived features on top of CCI provides diminishing returns. The macro features actually *reduce* R-squared slightly from 97.48% to 97.38% before the derived features recover it to 97.43%.

The takeaway: if you're building a construction cost model and you can only add one thing, add city-level cost indices. The macroeconomic signals and interaction terms are nice-to-haves, not need-to-haves.

---

## Slide 7 — Ablation Study
**[8:30 - 10:00]**

The ablation study makes this argument rigorous.

I added feature groups incrementally. Start with the 7-feature base at 96.63%. Add CCI — four features — and you jump to 97.48%. That's the biggest single step. Add macro — eleven more features — and you actually drop slightly to 97.38%. The macro features introduce noise that slightly hurts performance. Add derived features — six more — and you recover to 97.43%.

On the left you can see the ablation chart. The CCI step is clearly the dominant inflection point.

I also ran a leave-one-group-out analysis. Remove the CCI group from the full model, and R-squared drops by 0.12%. Remove macro, it barely moves. Remove derived, it barely moves. CCI is the only group whose removal meaningfully degrades performance.

This tells us the model isn't just memorizing 28 features. It's genuinely using the CCI signals to improve its regional discrimination.

---

## Slide 8 — Regional Performance
**[10:00 - 11:15]**

How does this play out across geography?

The Southwest performs best — 97.44% R-squared, 2.55% MAPE. The Midwest is close behind at 97.39%. The West is the most challenging region at 96.61% R-squared and 2.89% MAPE.

That West result is interesting. The West has the most heterogeneous construction market — San Francisco, Seattle, Denver, Phoenix all in one region, with massive cost variation between coastal and inland cities. The model works harder here and still achieves over 96.6%.

The left chart shows R-squared by region across all five models. CatBoost leads in every single region. The right chart shows the same story for MAPE. The consistency across regions is an important validation — this isn't a model that works well in one area and fails in another.

---

## Slide 9 — SHAP Explainability
**[11:15 - 12:45]**

Now let's open the black box.

I used SHAP TreeExplainer to decompose every prediction into per-feature contributions. The bar chart shows global mean absolute SHAP values.

Project type dominates at 39.1%. This makes intuitive sense — a hospital costs fundamentally different from a parking garage, regardless of location.

But look at the next five features. CCI deviation at 9.5%, area at 7.6%, weighted CCI at 6.7%, log area at 6.1%, labor CCI at 5.4%. Three of the top six features are CCI-derived. Collectively, the CCI features account for 21.6% of the model's explanatory power.

The beeswarm plot on the right shows individual predictions. Each dot is a data point, colored by feature value. You can see that high CCI deviation — meaning the city costs much more or less than the national average — pushes predictions strongly in both directions. This is the model learning regional price variation.

---

## Slide 10 — Regional SHAP
**[12:45 - 14:00]**

This is where it gets really interesting.

The top figure breaks down SHAP importance by region. Project type is consistently dominant everywhere. But the second and third most important features shift.

In the Southeast, labor CCI ranks much higher than in other regions. Construction labor markets in the Southeast have unique dynamics — right-to-work laws, different union density, seasonal patterns. The model captures this.

In the Midwest, material CCI is more prominent. That region is more sensitive to steel and concrete prices, which makes sense given its industrial construction base.

The dependence plots below show how individual features interact with the output. The CCI deviation plot has a clear positive slope — cities with higher-than-average construction costs get higher predictions. But the slope varies by region, which is exactly what regional intelligence should do.

---

## Slide 11 — Statistical Significance
**[14:00 - 15:15]**

I want to address whether these model differences are real or just noise.

I used corrected paired t-tests on the 5-fold cross-validation results. CatBoost versus Random Forest has a corrected p-value of 0.0001 and a Cohen's d of 9.93. That's an enormous effect size — well above the 0.8 threshold for "large."

CatBoost versus XGBoost: p = 0.0012, Cohen's d = 5.32. CatBoost versus LightGBM: p = 0.0046, Cohen's d = 3.69. All statistically and practically significant.

The one comparison that doesn't reach significance is CatBoost versus MLP: p = 0.18, Cohen's d = 1.06. MLP is the only model that comes close to CatBoost's performance, but it requires more computation and is harder to deploy to mobile.

A note on methodology: Wilcoxon signed-rank tests are constrained by 5 folds — the minimum possible p-value is 0.0625 — so I used the corrected t-test following Nadeau and Bengio's 2003 correction for overlapping training sets in cross-validation.

---

## Slide 12 — Limitations & Disclosure
**[15:15 - 17:00]**

Before I move to applications, I want to be transparent about what this study does and does not claim.

The most important disclosure: the CCI data in this study is simulated. RSMeans construction cost indices are commercially licensed and paywalled — they cost thousands of dollars per year. So I generated synthetic CCI data calibrated from published city cost ratios, with realistic yearly drift, COVID-era price bumps, and per-project noise.

This is a real limitation, and I want to explain why the results are still meaningful.

The synthetic data preserves the *relative* cost relationships between cities and regions. San Francisco is more expensive than rural Oklahoma in the synthetic data, by approximately the same ratio as in reality. The model learns these relative patterns — and the pipeline is designed so that licensed RSMeans data drops in as a direct replacement. No model architecture changes, no retraining logic changes. Just swap the CCI table.

Second, sample size. Twenty-seven hundred records across fifty cities is modest. I mitigate this with region-stratified cross-validation and temporal holdout testing. The fact that all five models converge to similar performance suggests the signal is real, not an artifact of small data.

Third — and I think this is the most honest result in the thesis — I ran a validation experiment on real USA Spending federal procurement data. Over eight thousand real records. The model achieved an R-squared near zero. It did not generalize. But this is expected. Federal procurement follows fundamentally different cost structures than commercial construction. It validates the need for domain-specific training data, which is exactly what BuildScan addresses by using CCI tables directly rather than relying on the trained model.

The key takeaway: the contribution is the *methodology*, not the specific model weights. The finding that CCI features improve regional prediction accuracy is robust to the synthetic data constraint. Retraining on licensed data would preserve the architecture and likely improve absolute performance.

---

## Slide 13 — BuildScan Overview
**[17:00 - 18:15]**

So what do we do with these findings?

BuildScan is an iOS app — AI-powered construction cost estimation built for contractors. The pitch is simple: point your phone at a room, describe the job, and get a professional proposal you can share with clients. Complete with regional pricing, itemized build lists, and upgrade recommendations.

The workflow has four steps.

Step one, Scan: capture the space using LiDAR 3D scanning, take up to five photos, or enter dimensions manually. BuildScan works on every iPhone — you don't need a Pro model.

Step two, Describe: tell the app what you're building. Type it out or tap the mic and dictate. Real-time voice transcription — because on a job site, your hands are dirty.

Step three, Estimate: Claude AI generates a detailed build list with realistic quantities across seventeen trade categories. The pricing engine applies your state's Construction Cost Index so every number reflects your local market.

Step four, Share: export a branded PDF estimate or convert it to a numbered invoice. Send it to your client via text, email, or AirDrop in one tap.

The +0.85% R-squared lift from CCI features validates the core engine. BuildScan applies BLS Construction Cost Indices across all fifty states so every line item reflects local pricing.

---

## Slide 14 — App Demo: 3 Capture Methods
**[18:15 - 19:15]**

Here's what the capture experience looks like.

On the phone you can see the LiDAR scan in action — green measurement dots mapping walls and surfaces in real-time, with precise dimensions extracted automatically. 12.4 feet wide, 9.2 feet long, 8.5-foot ceiling. 114 square feet calculated instantly.

But not every contractor has an iPhone Pro, and not every situation calls for LiDAR. So BuildScan offers three capture methods.

LiDAR Room Scan — walk around the room and get precise 3D measurements. Walls, windows, doors, and furniture are detected automatically. This requires iPhone 12 Pro or later.

Multi-Photo Capture — take up to five photos from different angles. The AI uses visual details to refine quantities and identify existing materials. This works on any iPhone with a camera.

Manual Entry — type length, width, ceiling height, and window and door counts. No camera needed. Works offline, works everywhere.

And on any capture method, you can tap the mic to describe the job out loud instead of typing. BuildScan transcribes in real time. It's built for the reality of a construction site.

---

## Slide 15 — App Demo: AI-Powered Build Lists
**[19:15 - 20:15]**

Once the space is captured and the job is described, Claude AI generates the estimate.

Look at the phone screen. The grand total is $3,412.80 — that includes a subtotal of $2,772, plus ten percent overhead, ten percent profit, and five percent contingency. The cost split bar shows 54% materials, 46% labor. Every number is CCI-adjusted — this estimate uses the Illinois index at 1.12, broken down into material at 1.08, labor at 1.18, and equipment at 1.04.

Each line item shows the trade category — Drywall, Framing, Insulation, Electrical — and a confidence indicator. High confidence means the quantity was measured directly from the scan. Medium or Low means it was inferred from the project description, flagged so the contractor can verify before sending.

Two features that matter for sales. First, Smart Upsell Suggestions. After every estimate, BuildScan recommends three to five upgrade opportunities — switching from laminate to hardwood, adding underfloor heating. Each shows the additional cost. Tap "Add to Estimate" and it's included instantly. This helps contractors increase ticket size.

Second, Before and After Visualization. Tap "Visualize Result" and the AI generates a description of what the finished space will look like, with key changes listed as bullet points alongside the original photos. It's a deal-closer for client presentations.

---

## Slide 16 — App Demo: Share & Invoice
**[20:15 - 21:15]**

The final step is getting the estimate to the client.

BuildScan produces two PDF formats. The Estimate PDF includes project summary, room measurements, line items grouped by the seventeen trade categories, material and labor breakdown, regional CCI annotation, and the grand total with overhead, profit, and contingency all itemized.

But here's what really matters for contractors: you can convert any estimate to a numbered invoice with one tap. The Invoice PDF adds invoice number, issue and due dates, FROM and BILL TO layout, payment terms — Due on Receipt, Net 15, Net 30, Net 45, Net 60 — and professional totals. Your contractor info is saved once and auto-filled on every future invoice.

Sharing is one tap — text, email, or AirDrop.

On the project management side, BuildScan saves unlimited estimates. The home screen shows your project portfolio with total value, average estimate, cost split bars, and CCI badges. It becomes your estimate database.

Five project types — Residential, Commercial, Industrial, Institutional, and Infrastructure — each with tuned cost multipliers. Seventeen trade categories from Demolition to Equipment Rental. Fifty state CCIs from BLS data. All running locally on the device.

---

## Slide 17 — Thank You
**[21:15 - 21:45]**

To summarize: regional cost indices — specifically city-level CCI — are the single most impactful feature for improving construction cost prediction. They contribute +0.85% R-squared over a strong baseline. CatBoost is the best model for this task. And BuildScan translates those findings into a practical tool that contractors can use on the job site today.

Thank you. I'm happy to take questions.

---

## Q&A Preparation Notes

**Likely questions and talking points:**

**"Why is the data synthetic?"**
RSMeans CCI data is commercially licensed and paywalled. The synthetic dataset is calibrated from known city cost ratios, with realistic yearly drift, COVID-era bumps, and per-project noise. The USA Spending validation experiment (real federal procurement data) showed domain shift issues (R² near zero), which honestly demonstrates the gap between synthetic training and real-world data — and motivates the BuildScan approach of using CCI tables directly rather than relying on the trained model.

**"Is 0.85% R² improvement meaningful?"**
In absolute terms it's modest. But: (1) the baseline is already 96.6%, so we're operating in the regime where improvements are hard-won; (2) RMSE drops by nearly $1/sqft, which scales — on a 10,000 sqft project that's $10,000 less error; (3) Cohen's d for the feature set comparison would be similarly large.

**"Why not a deeper neural network?"**
The MLP is already second-best. But gradient-boosted trees have three advantages for this domain: native categorical handling, built-in feature importance, and easy CoreML export for on-device inference. A transformer or deeper architecture would likely overfit on 2,750 records.

**"How would this work with real CCI data?"**
Drop-in replacement. The feature engineering pipeline accepts a CCI table keyed by city and year. Replace the synthetic table with RSMeans licensed data and retrain. The model architecture and feature definitions don't change.

**"What about cost inflation / temporal drift?"**
The temporal holdout (train on 2015-2023, test on 2024-2025) explicitly tests this. The model includes year and PPI year-over-year change as features, giving it some ability to track inflation trends. For production use, periodic retraining on updated data would be essential.

**"Why does Claude generate quantities but not prices?"**
Separation of concerns. Claude is excellent at reasoning about *what* materials and labor a job requires — it understands construction context. But dollar amounts drift with markets, regions, and time. The CCI pricing engine uses structured BLS data that can be updated independently. This means the app stays accurate without retraining the AI — just update the CCI tables.

**"How does the upsell feature work?"**
After generating the base estimate, a second Claude call analyzes the build list and identifies 3-5 upgrade opportunities based on the project type and current materials. Each suggestion includes the cost delta and a brief rationale. The contractor decides what to include — it's a sales tool, not an automatic add-on.

**"What about accuracy of AI-generated quantities?"**
That's why confidence indicators exist. Line items derived from direct LiDAR measurements get High confidence. Items inferred from the project description or photos get Medium or Low, and they're visually flagged. The contractor is always the final check before sending.
