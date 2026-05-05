// Pre-extracted constants from thesis JSON results

export const ABLATION = {
  base: { r2: 0.9663, rmse: 6.28, mape: 2.96, features: 7, label: "Base" },
  plusCCI: {
    r2: 0.9748,
    rmse: 5.43,
    mape: 2.61,
    features: 11,
    label: "+CCI",
  },
  plusMacro: {
    r2: 0.9738,
    rmse: 5.54,
    mape: 2.66,
    features: 22,
    label: "+Macro",
  },
  fullB: {
    r2: 0.9743,
    rmse: 5.49,
    mape: 2.63,
    features: 28,
    label: "+Derived (Full B)",
  },
} as const;

export const MODELS = [
  { name: "CatBoost", r2: 0.9743, rmse: 5.49, mape: 2.63, rank: 1 },
  { name: "MLP", r2: 0.9723, rmse: 5.70, mape: 2.73, rank: 2 },
  { name: "LightGBM", r2: 0.9708, rmse: 5.84, mape: 2.82, rank: 3 },
  { name: "XGBoost", r2: 0.9675, rmse: 6.17, mape: 2.95, rank: 4 },
  { name: "Random Forest", r2: 0.9657, rmse: 6.34, mape: 3.02, rank: 5 },
] as const;

export const SHAP_TOP = [
  { feature: "project_type", importance: 39.12, label: "Project Type" },
  { feature: "cci_deviation", importance: 9.46, label: "CCI Deviation" },
  { feature: "area_sqft", importance: 7.58, label: "Area (sqft)" },
  { feature: "weighted_cci", importance: 6.71, label: "Weighted CCI" },
  { feature: "log_area", importance: 6.10, label: "Log Area" },
  { feature: "labor_cci", importance: 5.40, label: "Labor CCI" },
  { feature: "mat_cci", importance: 2.68, label: "Material CCI" },
  { feature: "region", importance: 2.17, label: "Region" },
] as const;

export const SIGNIFICANCE = [
  {
    modelA: "CatBoost",
    modelB: "XGBoost",
    meanDiff: 0.0068,
    correctedP: 0.0012,
    cohensD: 5.32,
    ciLower: 0.0058,
    ciUpper: 0.008,
  },
  {
    modelA: "CatBoost",
    modelB: "LightGBM",
    meanDiff: 0.0035,
    correctedP: 0.0046,
    cohensD: 3.69,
    ciLower: 0.0028,
    ciUpper: 0.0042,
  },
  {
    modelA: "CatBoost",
    modelB: "Random Forest",
    meanDiff: 0.0086,
    correctedP: 0.0001,
    cohensD: 9.93,
    ciLower: 0.0079,
    ciUpper: 0.0093,
  },
  {
    modelA: "CatBoost",
    modelB: "MLP",
    meanDiff: 0.002,
    correctedP: 0.1775,
    cohensD: 1.06,
    ciLower: 0.0003,
    ciUpper: 0.0032,
  },
] as const;

export const REGIONS = [
  { name: "Midwest", r2: 0.9739, mape: 2.58 },
  { name: "Northeast", r2: 0.9720, mape: 2.71 },
  { name: "Southeast", r2: 0.9735, mape: 2.65 },
  { name: "Southwest", r2: 0.9744, mape: 2.55 },
  { name: "West", r2: 0.9661, mape: 2.89 },
] as const;

export const FEATURE_SETS = {
  A: {
    name: "Feature Set A",
    count: 7,
    label: "Baseline",
    r2: 0.9663,
    rmse: 6.28,
    mape: 2.96,
    features: [
      "project_type",
      "area_sqft",
      "year",
      "region",
      "state",
      "formwork_rate",
      "concrete_rate",
    ],
  },
  B: {
    name: "Feature Set B",
    count: 28,
    label: "Regional-Aware",
    r2: 0.9748,
    rmse: 5.43,
    mape: 2.61,
    features: [
      "Base (7)",
      "+weighted_cci, labor_cci, mat_cci, equip_cci",
      "+ppi_lumber, ppi_steel_mill, ppi_cement, ...",
      "+cci_deviation, cci_labor_premium, log_area, ...",
    ],
  },
} as const;
