"""
Evaluate — Compare Model A vs Model B and generate visualizations.

Produces:
  - Comparison bar chart (R² by region)
  - Residual analysis
  - Model comparison table
"""

import json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

MODEL_DIR = Path(__file__).parent.parent / "models"
FIG_DIR = Path(__file__).parent.parent / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)


def load_results():
    """Load both model results."""
    with open(MODEL_DIR / "model_a_baseline_results.json") as f:
        a = json.load(f)
    with open(MODEL_DIR / "model_b_regional_results.json") as f:
        b = json.load(f)
    return a, b


def plot_regional_r2(a, b):
    """Bar chart comparing R² by region."""
    print("\n📊 Generating regional R² comparison chart...")
    
    regions = sorted(a["region_metrics"].keys())
    r2_a = [a["region_metrics"][r]["r2"] for r in regions]
    r2_b = [b["region_metrics"][r]["r2"] for r in regions]
    
    x = np.arange(len(regions))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(12, 6))
    bars_a = ax.bar(x - width/2, r2_a, width, label="Model A (Baseline)", color="#ff6b6b", alpha=0.85)
    bars_b = ax.bar(x + width/2, r2_b, width, label="Model B (Regional-Aware)", color="#00d2ff", alpha=0.85)
    
    ax.set_xlabel("Region", fontsize=12)
    ax.set_ylabel("R² Score", fontsize=12)
    ax.set_title("R² by Region: National Baseline vs Regional-Aware Model", fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(regions, fontsize=11)
    ax.legend(fontsize=11)
    ax.set_ylim(0, 1.05)
    ax.grid(axis="y", alpha=0.3)
    
    # Add value labels
    for bar in bars_a:
        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.01,
                f'{bar.get_height():.3f}', ha='center', va='bottom', fontsize=8)
    for bar in bars_b:
        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.01,
                f'{bar.get_height():.3f}', ha='center', va='bottom', fontsize=8)
    
    plt.tight_layout()
    out = FIG_DIR / "regional_r2_comparison.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✅ Saved: {out}")


def plot_delta_r2(a, b):
    """Horizontal bar chart showing ΔR² (improvement)."""
    print("\n📊 Generating ΔR² improvement chart...")
    
    regions = sorted(a["region_metrics"].keys())
    deltas = [b["region_metrics"][r]["r2"] - a["region_metrics"][r]["r2"] for r in regions]
    
    colors = ["#00c853" if d > 0 else "#ff6b6b" for d in deltas]
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(regions, deltas, color=colors, alpha=0.85)
    ax.set_xlabel("ΔR² (Model B − Model A)", fontsize=12)
    ax.set_title("Regional R² Improvement from CCI + Macro Integration", fontsize=14)
    ax.axvline(x=0, color="white", linewidth=0.8)
    ax.grid(axis="x", alpha=0.3)
    
    for i, (r, d) in enumerate(zip(regions, deltas)):
        ax.text(d + 0.001 * (1 if d > 0 else -1), i, f"{d:+.4f}", 
                va="center", ha="left" if d > 0 else "right", fontsize=10)
    
    plt.tight_layout()
    out = FIG_DIR / "delta_r2_improvement.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✅ Saved: {out}")


def plot_mape_comparison(a, b):
    """MAPE comparison by region."""
    print("\n📊 Generating MAPE comparison chart...")
    
    regions = sorted(a["region_metrics"].keys())
    mape_a = [a["region_metrics"][r]["mape"] for r in regions]
    mape_b = [b["region_metrics"][r]["mape"] for r in regions]
    
    x = np.arange(len(regions))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(x - width/2, mape_a, width, label="Model A (Baseline)", color="#ff6b6b", alpha=0.85)
    ax.bar(x + width/2, mape_b, width, label="Model B (Regional-Aware)", color="#00d2ff", alpha=0.85)
    
    ax.set_xlabel("Region", fontsize=12)
    ax.set_ylabel("MAPE (%)", fontsize=12)
    ax.set_title("MAPE by Region: Lower is Better", fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(regions, fontsize=11)
    ax.legend(fontsize=11)
    ax.grid(axis="y", alpha=0.3)
    
    plt.tight_layout()
    out = FIG_DIR / "regional_mape_comparison.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✅ Saved: {out}")


def print_summary_table(a, b):
    """Print a formatted comparison table."""
    print("\n" + "=" * 70)
    print("📋 FULL COMPARISON TABLE")
    print("=" * 70)
    
    print(f"\n{'':15s} {'Model A':>20s} {'Model B':>20s} {'Δ':>12s}")
    print(f"{'─'*67}")
    
    # Overall
    for metric in ["r2", "rmse", "mape"]:
        va = a["avg_metrics"][metric]
        vb = b["avg_metrics"][metric]
        delta = vb - va
        unit = "%" if metric == "mape" else ""
        print(f"{'Overall '+metric.upper():15s} {va:>19.4f}{unit} {vb:>19.4f}{unit} {delta:>+11.4f}{unit}")
    
    print(f"\n{'─'*67}")
    print(f"{'Region':15s} {'R²(A)':>8s} {'R²(B)':>8s} {'ΔR²':>8s} {'MAPE(A)':>8s} {'MAPE(B)':>8s} {'ΔMAPE':>8s}")
    print(f"{'─'*67}")
    
    for region in sorted(a["region_metrics"].keys()):
        ra = a["region_metrics"][region]
        rb = b["region_metrics"][region]
        print(f"{region:15s} {ra['r2']:>8.4f} {rb['r2']:>8.4f} {rb['r2']-ra['r2']:>+8.4f} "
              f"{ra['mape']:>7.2f}% {rb['mape']:>7.2f}% {rb['mape']-ra['mape']:>+7.2f}%")
    
    print(f"\n  Features — Model A: {a['n_features']}, Model B: {b['n_features']}")
    

if __name__ == "__main__":
    print("=" * 60)
    print("Regional Construction Cost Estimation — Evaluation")
    print("=" * 60)
    
    a, b = load_results()
    
    plot_regional_r2(a, b)
    plot_delta_r2(a, b)
    plot_mape_comparison(a, b)
    print_summary_table(a, b)
    
    print("\n" + "=" * 60)
    print("✅ Evaluation complete!")
    print(f"   Figures saved to: {FIG_DIR}")
    print("   Next: python src/explain.py")
    print("=" * 60)
