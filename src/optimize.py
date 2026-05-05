"""
Hyperparameter optimization with Optuna.

Runs Bayesian optimization for each model type using region-stratified
5-fold CV R² as the objective. Saves best params per model.
"""

import json
import numpy as np
import pandas as pd
import optuna
from pathlib import Path
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import r2_score

from models import FEATURES_B, CATEGORICALS, TARGET, get_available_features, create_model

optuna.logging.set_verbosity(optuna.logging.WARNING)

DATA_PATH = Path(__file__).parent.parent / "data" / "processed" / "model_ready.csv"
RESULTS_DIR = Path(__file__).parent.parent / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def cv_score(model_name, df_train, features, cat_features, params):
    """Quick 5-fold CV returning mean R²."""
    avail = get_available_features(df_train, features)
    avail_cats = [c for c in cat_features if c in avail]
    X = df_train[avail]
    y = df_train[TARGET].values
    regions = df_train["region"].values

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scores = []

    for train_idx, val_idx in skf.split(X, regions):
        model = create_model(model_name, avail, avail_cats, params)
        model.fit(X.iloc[train_idx], y[train_idx], X.iloc[val_idx], y[val_idx])
        preds = model.predict(X.iloc[val_idx])
        scores.append(r2_score(y[val_idx], preds))

    return np.mean(scores)


# ── Search spaces ─────────────────────────────────────────────────────────────

def catboost_objective(trial, df_train, features, cat_features):
    params = {
        "iterations": trial.suggest_int("iterations", 500, 2000),
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.1, log=True),
        "depth": trial.suggest_int("depth", 4, 10),
        "l2_leaf_reg": trial.suggest_float("l2_leaf_reg", 1, 10),
        "min_data_in_leaf": trial.suggest_int("min_data_in_leaf", 1, 50),
    }
    return cv_score("CatBoost", df_train, features, cat_features, params)


def xgboost_objective(trial, df_train, features, cat_features):
    params = {
        "n_estimators": trial.suggest_int("n_estimators", 500, 2000),
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.1, log=True),
        "max_depth": trial.suggest_int("max_depth", 4, 10),
        "reg_lambda": trial.suggest_float("reg_lambda", 0.1, 10, log=True),
        "reg_alpha": trial.suggest_float("reg_alpha", 0.001, 10, log=True),
        "subsample": trial.suggest_float("subsample", 0.6, 1.0),
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
    }
    return cv_score("XGBoost", df_train, features, cat_features, params)


def lightgbm_objective(trial, df_train, features, cat_features):
    params = {
        "n_estimators": trial.suggest_int("n_estimators", 500, 2000),
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.1, log=True),
        "max_depth": trial.suggest_int("max_depth", 4, 10),
        "reg_lambda": trial.suggest_float("reg_lambda", 0.1, 10, log=True),
        "num_leaves": trial.suggest_int("num_leaves", 31, 255),
        "min_child_samples": trial.suggest_int("min_child_samples", 5, 50),
        "subsample": trial.suggest_float("subsample", 0.6, 1.0),
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
    }
    return cv_score("LightGBM", df_train, features, cat_features, params)


def rf_objective(trial, df_train, features, cat_features):
    params = {
        "n_estimators": trial.suggest_int("n_estimators", 200, 1000),
        "max_depth": trial.suggest_int("max_depth", 10, 40),
        "min_samples_split": trial.suggest_int("min_samples_split", 2, 20),
        "min_samples_leaf": trial.suggest_int("min_samples_leaf", 1, 20),
        "max_features": trial.suggest_float("max_features", 0.3, 1.0),
    }
    return cv_score("RandomForest", df_train, features, cat_features, params)


def mlp_objective(trial, df_train, features, cat_features):
    layers = trial.suggest_categorical("layers", ["128,64,32", "256,128,64", "128,64", "256,128"])
    params = {
        "hidden_layer_sizes": tuple(int(x) for x in layers.split(",")),
        "learning_rate_init": trial.suggest_float("learning_rate_init", 1e-4, 1e-2, log=True),
        "batch_size": trial.suggest_categorical("batch_size", [32, 64, 128]),
        "max_iter": 500,
        "early_stopping": True,
        "n_iter_no_change": 15,
    }
    return cv_score("MLP", df_train, features, cat_features, params)


OBJECTIVES = {
    "CatBoost": catboost_objective,
    "XGBoost": xgboost_objective,
    "LightGBM": lightgbm_objective,
    "RandomForest": rf_objective,
    "MLP": mlp_objective,
}


def optimize_all(model_names=None, n_trials=50, features=None, cat_features=None):
    """Run Optuna optimization for each model. Returns dict of best params."""
    if model_names is None:
        model_names = list(OBJECTIVES.keys())
    if features is None:
        features = FEATURES_B
    if cat_features is None:
        cat_features = CATEGORICALS

    df = pd.read_csv(DATA_PATH)
    # Use only training years for optimization
    df_train = df[~df["year"].isin([2024, 2025])].reset_index(drop=True)
    print(f"Optimizing on {len(df_train)} training rows\n")

    best_params = {}

    for name in model_names:
        if name not in OBJECTIVES:
            print(f"  Skipping {name} (no search space defined)")
            continue

        print(f"Optimizing {name} ({n_trials} trials)...", end=" ", flush=True)
        obj_func = OBJECTIVES[name]

        study = optuna.create_study(direction="maximize",
                                    sampler=optuna.samplers.TPESampler(seed=42))
        study.optimize(
            lambda trial: obj_func(trial, df_train, features, cat_features),
            n_trials=n_trials, show_progress_bar=False,
        )

        best_params[name] = study.best_params
        print(f"R²={study.best_value:.4f}")
        print(f"  Best: {study.best_params}")

    # Save
    out_path = RESULTS_DIR / "optuna_best_params.json"
    with open(out_path, "w") as f:
        json.dump(best_params, f, indent=2)
    print(f"\nSaved best params: {out_path}")

    return best_params


if __name__ == "__main__":
    print("=" * 60)
    print("HYPERPARAMETER OPTIMIZATION (Optuna)")
    print("=" * 60)
    best = optimize_all(n_trials=50)
