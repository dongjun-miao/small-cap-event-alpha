"""Build public figures from the canonical method and saved aggregate tables."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "results" / "tables"
FIGURES = ROOT / "figures"

COLORS = {
    "navy": "#17324D",
    "blue": "#3B82B4",
    "teal": "#2A9D8F",
    "orange": "#F4A261",
    "red": "#C95B4B",
    "gray": "#697681",
    "light": "#EDF2F5",
}


def save(fig: plt.Figure, name: str) -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        FIGURES / name,
        dpi=220,
        bbox_inches="tight",
        facecolor="white",
        metadata={"Author": "Dongjun Miao", "Title": name},
    )
    plt.close(fig)


def event_schematic() -> None:
    fig, ax = plt.subplots(figsize=(13, 4.2))
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 4.2)
    ax.axis("off")

    boxes = [
        (0.3, 1.45, 3.2, 1.45, COLORS["light"], COLORS["navy"],
         "Pre-event state: t−20 … t−1",
         "Lagged volume means and ADV20\nNo event-day liquidity leakage"),
        (4.0, 1.45, 2.25, 1.45, "#FFF3D6", COLORS["orange"],
         "Event session t",
         "Volume ≥ 1.8× previous\nClose position ≥ 0.6"),
        (6.75, 1.45, 2.0, 1.45, "#E5F4F1", COLORS["teal"],
         "Entry: open t+1",
         "First implementable price\nafter signal formation"),
        (9.25, 1.45, 3.25, 1.45, "#E7EEF6", COLORS["blue"],
         "Exit: close t+h",
         "h = 5, 10, or 20 sessions\nExact session offset required"),
    ]
    for x, y, width, height, fill, edge, title, body in boxes:
        box = FancyBboxPatch(
            (x, y),
            width,
            height,
            boxstyle="round,pad=0.04,rounding_size=0.08",
            linewidth=1.5,
            edgecolor=edge,
            facecolor=fill,
        )
        ax.add_patch(box)
        ax.text(
            x + width / 2,
            y + 1.03,
            title,
            ha="center",
            va="center",
            fontsize=11,
            fontweight="bold",
            color=COLORS["navy"],
        )
        ax.text(
            x + width / 2,
            y + 0.48,
            body,
            ha="center",
            va="center",
            fontsize=9.3,
            color="#34424D",
            linespacing=1.35,
        )

    for start, end in ((3.5, 4.0), (6.25, 6.75), (8.75, 9.25)):
        ax.add_patch(
            FancyArrowPatch(
                (start, 2.18),
                (end, 2.18),
                arrowstyle="-|>",
                mutation_scale=14,
                linewidth=1.3,
                color=COLORS["gray"],
            )
        )

    ax.text(
        5.12,
        3.25,
        "Signal observable only after the close of t",
        ha="center",
        fontsize=10,
        fontweight="bold",
        color=COLORS["red"],
    )
    ax.plot([5.12, 5.12], [3.08, 2.92], color=COLORS["red"], linewidth=1.2)
    ax.text(
        0.3,
        0.55,
        "Daily small-cap filter: market-cap percentile ≤ 1/3 "
        "in the supplied eligible cross-section",
        ha="left",
        fontsize=10,
        color=COLORS["navy"],
    )
    ax.text(
        0.3,
        0.20,
        "Return label is a price return, not a dividend- or "
        "delisting-adjusted total return.",
        ha="left",
        fontsize=9,
        color=COLORS["gray"],
    )
    ax.set_title(
        "Canonical Event Formation and Execution Timing",
        loc="left",
        fontsize=15,
        fontweight="bold",
        color=COLORS["navy"],
        pad=10,
    )
    save(fig, "event_definition_schematic.png")


def robustness_figure() -> None:
    data = pd.read_csv(TABLES / "a_small_subperiod_summary.csv")
    labels = data["period"].str.replace("-", "–", regex=False)
    x = np.arange(len(data))
    width = 0.24

    fig, ax = plt.subplots(figsize=(11.4, 5.8))
    series = [
        ("mean_20d", "Raw mean", COLORS["blue"]),
        ("median_20d", "Median", COLORS["gray"]),
        ("winsor_1pct_mean_20d", "1% winsorized mean", COLORS["teal"]),
    ]
    for offset, (column, name, color) in zip((-width, 0, width), series):
        ax.bar(
            x + offset,
            100 * data[column],
            width,
            label=name,
            color=color,
            edgecolor="white",
            linewidth=0.5,
        )

    ax.axhline(0, color="#27333B", linewidth=0.9)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("20-session next-open-to-close return (%)")
    fig.suptitle(
        "Raw Means Are Positive, but Robust Summaries Reveal Strong Right Skew",
        x=0.075,
        y=0.98,
        ha="left",
        fontsize=14,
        fontweight="bold",
        color=COLORS["navy"],
    )
    fig.text(
        0.075,
        0.90,
        "Saved aggregate evidence; medians are non-positive in every subperiod",
        fontsize=9.5,
        color=COLORS["gray"],
    )
    ax.legend(frameon=False, ncol=3, loc="upper left", bbox_to_anchor=(0, 0.96))
    ax.grid(axis="y", color="#D7DEE3", linewidth=0.7, alpha=0.8)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_axisbelow(True)
    ax.text(
        1,
        -0.19,
        "Source: results/tables/a_small_subperiod_summary.csv",
        transform=ax.transAxes,
        ha="right",
        fontsize=8,
        color=COLORS["gray"],
    )
    fig.subplots_adjust(top=0.82, bottom=0.18)
    save(fig, "event_return_robustness.png")


def capacity_figure() -> None:
    data = pd.read_csv(TABLES / "a_small_capacity_summary.csv")
    periods = list(dict.fromkeys(data["period"]))
    palette = plt.cm.viridis(np.linspace(0.12, 0.88, len(periods)))
    money = FuncFormatter(
        lambda value, _: f"USD {value / 1000:,.0f}k"
        if value < 1_000_000
        else f"USD {value / 1_000_000:,.1f}m"
    )

    fig, axes = plt.subplots(1, 2, figsize=(12, 5.3), sharey=True)
    for ax, universe, title in zip(
        axes,
        ("all_events", "adv70_events"),
        ("All signal events", "Top 30% by pre-event ADV"),
    ):
        subset = data.loc[data["universe"] == universe]
        for period, color in zip(periods, palette):
            line = subset.loc[subset["period"] == period].sort_values(
                "participation_rate"
            )
            ax.plot(
                100 * line["participation_rate"],
                line["median_cohort_capacity_usd"],
                marker="o",
                linewidth=2,
                markersize=5,
                label=period.replace("-", "–"),
                color=color,
            )
        ax.set_title(title, fontsize=11.5, fontweight="bold", color=COLORS["navy"])
        ax.set_xlabel("ADV participation at entry (%)")
        ax.set_xticks([0.5, 1.0, 2.0])
        ax.set_yscale("log")
        ax.yaxis.set_major_formatter(money)
        ax.grid(True, which="both", color="#D7DEE3", linewidth=0.7, alpha=0.75)
        ax.spines[["top", "right"]].set_visible(False)

    axes[0].set_ylabel("Median equal-weight cohort capacity (USD, log scale)")
    axes[1].legend(frameon=False, fontsize=8.5, loc="upper left")
    fig.suptitle(
        "Liquidity Filtering Improves a Narrow Entry-Cohort Capacity Diagnostic",
        x=0.07,
        ha="left",
        fontsize=14,
        fontweight="bold",
        color=COLORS["navy"],
    )
    fig.text(
        0.07,
        0.91,
        "Not portfolio AUM: exits, impact, overlap, and capital reuse are not simulated",
        fontsize=9.5,
        color=COLORS["gray"],
    )
    fig.text(
        0.98,
        0.01,
        "Source: results/tables/a_small_capacity_summary.csv",
        ha="right",
        fontsize=8,
        color=COLORS["gray"],
    )
    fig.subplots_adjust(top=0.80, bottom=0.16, wspace=0.12)
    save(fig, "liquidity_capacity_sensitivity.png")


def main() -> None:
    event_schematic()
    robustness_figure()
    capacity_figure()
    print(f"Wrote three figures to {FIGURES}")


if __name__ == "__main__":
    main()
