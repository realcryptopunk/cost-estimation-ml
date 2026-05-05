"""
Unified model factory for multi-model comparison.

Provides a consistent train/predict interface across CatBoost, XGBoost,
LightGBM, Random Forest, and a PyTorch MLP. Handles categorical encoding
differences transparently.
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor
from catboost import CatBoostRegressor, Pool
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from sklearn.neural_network import MLPRegressor as _SklearnMLP

# ── Feature / categorical definitions (shared across all experiments) ─────────

FEATURES_A = [
    "area_sqft", "formwork_rate", "concrete_rate",
    "project_type", "region", "state", "year",
]

FEATURES_B = [
    "area_sqft", "formwork_rate", "concrete_rate",
    "project_type", "region", "state", "year",
    # CCI continuous
    "mat_cci", "labor_cci", "equip_cci", "weighted_cci",
    # Derived
    "cci_labor_premium", "cci_deviation", "combined_material_rate",
    "log_area", "year_num",
    # Macro
    "ppi_construction_materials", "ppi_cement", "ppi_steel_mill", "ppi_lumber",
    "real_gdp", "cpi_all_urban", "unemployment_rate",
    "mortgage_30yr", "building_permits", "housing_starts",
    "ppi_yoy_change",
    # Regional CPI
    "regional_cpi",
]

CATEGORICALS = ["project_type", "region", "state"]
TARGET = "cost_per_sqft"

# Ablation feature groups
FEATURE_GROUPS = {
    "base": ["area_sqft", "formwork_rate", "concrete_rate",
             "project_type", "region", "state", "year"],
    "cci": ["mat_cci", "labor_cci", "equip_cci", "weighted_cci"],
    "macro": ["ppi_construction_materials", "ppi_cement", "ppi_steel_mill",
              "ppi_lumber", "real_gdp", "cpi_all_urban", "unemployment_rate",
              "mortgage_30yr", "building_permits", "housing_starts",
              "regional_cpi"],
    "derived": ["cci_labor_premium", "cci_deviation", "combined_material_rate",
                "log_area", "year_num", "ppi_yoy_change"],
}


def get_available_features(df, feature_list):
    """Filter to features that exist in the dataframe."""
    return [f for f in feature_list if f in df.columns]


# ── Preprocessing helpers ─────────────────────────────────────────────────────

class TabularPreprocessor:
    """Handles one-hot encoding + scaling for models that need it (RF, MLP, XGBoost)."""

    def __init__(self, cat_cols, num_cols):
        self.cat_cols = cat_cols
        self.num_cols = num_cols
        self.ohe = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
        self.scaler = StandardScaler()
        self._fitted = False

    def fit_transform(self, X):
        X_cat = self.ohe.fit_transform(X[self.cat_cols]) if self.cat_cols else np.empty((len(X), 0))
        X_num = self.scaler.fit_transform(X[self.num_cols]) if self.num_cols else np.empty((len(X), 0))
        self._fitted = True
        return np.hstack([X_num, X_cat]).astype(np.float32)

    def transform(self, X):
        X_cat = self.ohe.transform(X[self.cat_cols]) if self.cat_cols else np.empty((len(X), 0))
        X_num = self.scaler.transform(X[self.num_cols]) if self.num_cols else np.empty((len(X), 0))
        return np.hstack([X_num, X_cat]).astype(np.float32)

    @property
    def n_features(self):
        n = len(self.num_cols)
        if self.cat_cols and self._fitted:
            n += sum(len(c) for c in self.ohe.categories_)
        return n


# ── Model wrappers ────────────────────────────────────────────────────────────

class ModelWrapper:
    """Base interface: fit(X_df, y, X_val_df, y_val) and predict(X_df)."""
    name = "base"
    needs_preprocessing = False

    def fit(self, X_train, y_train, X_val=None, y_val=None):
        raise NotImplementedError

    def predict(self, X):
        raise NotImplementedError

    def get_raw_model(self):
        raise NotImplementedError


class CatBoostModel(ModelWrapper):
    name = "CatBoost"
    needs_preprocessing = False

    def __init__(self, features, cat_features, params=None):
        self.features = features
        self.cat_features = cat_features
        self.cat_indices = [features.index(c) for c in cat_features if c in features]
        defaults = dict(iterations=1000, learning_rate=0.05, depth=8,
                        l2_leaf_reg=3, verbose=0, early_stopping_rounds=50)
        if params:
            defaults.update(params)
        self.params = defaults
        self.model = None

    def fit(self, X_train, y_train, X_val=None, y_val=None):
        X_tr = X_train[self.features].copy()
        for c in self.cat_features:
            if c in X_tr.columns:
                X_tr[c] = X_tr[c].astype(str)

        self.model = CatBoostRegressor(**self.params, random_seed=42, cat_features=self.cat_indices)
        train_pool = Pool(X_tr, y_train, cat_features=self.cat_indices)

        if X_val is not None:
            X_v = X_val[self.features].copy()
            for c in self.cat_features:
                if c in X_v.columns:
                    X_v[c] = X_v[c].astype(str)
            val_pool = Pool(X_v, y_val, cat_features=self.cat_indices)
            self.model.fit(train_pool, eval_set=val_pool)
        else:
            self.model.fit(train_pool)
        return self

    def predict(self, X):
        X_p = X[self.features].copy()
        for c in self.cat_features:
            if c in X_p.columns:
                X_p[c] = X_p[c].astype(str)
        return self.model.predict(X_p)

    def get_raw_model(self):
        return self.model


class XGBoostModel(ModelWrapper):
    name = "XGBoost"
    needs_preprocessing = True

    def __init__(self, features, cat_features, params=None):
        self.features = features
        self.cat_features = [c for c in cat_features if c in features]
        self.num_features = [f for f in features if f not in cat_features]
        self.preprocessor = TabularPreprocessor(self.cat_features, self.num_features)
        defaults = dict(n_estimators=1000, learning_rate=0.05, max_depth=8,
                        reg_lambda=3, verbosity=0)
        if params:
            defaults.update(params)
        self.params = defaults
        self.model = None

    def fit(self, X_train, y_train, X_val=None, y_val=None):
        X_tr = self.preprocessor.fit_transform(X_train[self.features])
        params = dict(self.params)
        fit_params = {"verbose": False}
        if X_val is not None:
            X_v = self.preprocessor.transform(X_val[self.features])
            fit_params["eval_set"] = [(X_v, y_val)]
            params["early_stopping_rounds"] = 50
        self.model = XGBRegressor(**params, random_state=42)
        self.model.fit(X_tr, y_train, **fit_params)
        return self

    def predict(self, X):
        X_p = self.preprocessor.transform(X[self.features])
        return self.model.predict(X_p)

    def get_raw_model(self):
        return self.model


class LightGBMModel(ModelWrapper):
    name = "LightGBM"
    needs_preprocessing = False

    def __init__(self, features, cat_features, params=None):
        self.features = features
        self.cat_features = [c for c in cat_features if c in features]
        defaults = dict(n_estimators=1000, learning_rate=0.05, max_depth=8,
                        reg_lambda=3, verbose=-1)
        if params:
            defaults.update(params)
        self.params = defaults
        self.model = None

    def fit(self, X_train, y_train, X_val=None, y_val=None):
        X_tr = X_train[self.features].copy()
        for c in self.cat_features:
            X_tr[c] = X_tr[c].astype("category")

        self.model = LGBMRegressor(**self.params, random_state=42)
        cat_feature_arg = self.cat_features if self.cat_features else "auto"

        fit_params = {"categorical_feature": cat_feature_arg}
        if X_val is not None:
            X_v = X_val[self.features].copy()
            for c in self.cat_features:
                X_v[c] = X_v[c].astype("category")
            fit_params["eval_set"] = [(X_v, y_val)]
            import lightgbm
            fit_params["callbacks"] = [
                lightgbm.early_stopping(50, verbose=False),
                lightgbm.log_evaluation(0),
            ]

        self.model.fit(X_tr, y_train, **fit_params)

        return self

    def predict(self, X):
        X_p = X[self.features].copy()
        for c in self.cat_features:
            X_p[c] = X_p[c].astype("category")
        return self.model.predict(X_p)

    def get_raw_model(self):
        return self.model


class RandomForestModel(ModelWrapper):
    name = "RandomForest"
    needs_preprocessing = True

    def __init__(self, features, cat_features, params=None):
        self.features = features
        self.cat_features = [c for c in cat_features if c in features]
        self.num_features = [f for f in features if f not in cat_features]
        self.preprocessor = TabularPreprocessor(self.cat_features, self.num_features)
        defaults = dict(n_estimators=500, max_depth=20, min_samples_leaf=5, n_jobs=-1)
        if params:
            defaults.update(params)
        self.params = defaults
        self.model = None

    def fit(self, X_train, y_train, X_val=None, y_val=None):
        X_tr = self.preprocessor.fit_transform(X_train[self.features])
        self.model = RandomForestRegressor(**self.params, random_state=42)
        self.model.fit(X_tr, y_train)
        return self

    def predict(self, X):
        X_p = self.preprocessor.transform(X[self.features])
        return self.model.predict(X_p)

    def get_raw_model(self):
        return self.model


# ── MLP (sklearn) ─────────────────────────────────────────────────────────────

class MLPModel(ModelWrapper):
    name = "MLP"
    needs_preprocessing = True

    def __init__(self, features, cat_features, params=None):
        self.features = features
        self.cat_features = [c for c in cat_features if c in features]
        self.num_features = [f for f in features if f not in cat_features]
        self.preprocessor = TabularPreprocessor(self.cat_features, self.num_features)
        defaults = dict(
            hidden_layer_sizes=(128, 64, 32),
            max_iter=500,
            learning_rate_init=1e-3,
            early_stopping=True,
            validation_fraction=0.15,
            n_iter_no_change=15,
            batch_size=64,
        )
        if params:
            defaults.update(params)
        self.params = defaults
        self.model = None

    def fit(self, X_train, y_train, X_val=None, y_val=None):
        X_tr = self.preprocessor.fit_transform(X_train[self.features])
        self.model = _SklearnMLP(**self.params, random_state=42)
        self.model.fit(X_tr, y_train)
        return self

    def predict(self, X):
        X_p = self.preprocessor.transform(X[self.features])
        return self.model.predict(X_p)

    def get_raw_model(self):
        return self.model


# ── Factory ───────────────────────────────────────────────────────────────────

MODEL_REGISTRY = {
    "catboost": CatBoostModel,
    "xgboost": XGBoostModel,
    "lightgbm": LightGBMModel,
    "randomforest": RandomForestModel,
    "mlp": MLPModel,
}


def create_model(name, features, cat_features, params=None):
    """Create a model wrapper by name."""
    key = name.lower().replace(" ", "").replace("_", "")
    if key not in MODEL_REGISTRY:
        raise ValueError(f"Unknown model: {name}. Available: {list(MODEL_REGISTRY.keys())}")
    avail_cats = [c for c in cat_features if c in features]
    return MODEL_REGISTRY[key](features, avail_cats, params)
