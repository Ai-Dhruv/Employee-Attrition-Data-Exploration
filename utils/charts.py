"""
charts.py
---------
All Matplotlib / Seaborn charts, styled for the dark navy dashboard theme.
Every function returns a figure, or None when there is no data to draw.
"""

import textwrap

import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Patch

# ---- Theme colours (match assets/style.css) ----
CARD_BG = "#131A36"
TEXT = "#E6E9F5"
MUTED = "#9AA3C7"
GRID = "#2A3262"
STAYED = "#38BDF8"     # sky blue
LEFT = "#A855F7"       # purple
BAR = "#4F6BED"        # royal blue
HIGHLIGHT = "#A855F7"  # highest bar

STATUS_LABELS = {"No": "Stayed", "Yes": "Left"}


def _wrap(label, width=14):
    """Break long labels (e.g. 'Research & Development') over two lines."""
    return textwrap.fill(str(label), width)


def _base_figure(title, height=3.8, horizontal=False, width=6.4):
    """Create a figure with the dashboard look (dark card, light text, soft grid)."""
    fig, ax = plt.subplots(figsize=(width, height))
    fig.patch.set_facecolor(CARD_BG)
    ax.set_facecolor(CARD_BG)
    ax.set_title(title, color=TEXT, fontsize=13, fontweight="bold", loc="left", pad=14)
    ax.tick_params(colors=MUTED, labelsize=9)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GRID)
    ax.grid(axis="x" if horizontal else "y", color=GRID, linewidth=0.6, alpha=0.7)
    ax.set_axisbelow(True)
    return fig, ax


def _add_overall_line(ax, overall_rate, horizontal):
    """Dashed reference line showing the overall attrition rate."""
    label = f"Overall {overall_rate:.2f}%"
    if horizontal:
        ax.axvline(overall_rate, color=MUTED, linestyle="--", linewidth=1, label=label)
    else:
        ax.axhline(overall_rate, color=MUTED, linestyle="--", linewidth=1, label=label)
    ax.legend(frameon=False, labelcolor=MUTED, fontsize=8, loc="upper right")


# ------------------------------------------------------------ overview

def attrition_donut(kpis):
    """Donut chart: percentage of employees who stayed vs left."""
    if kpis["total"] == 0:
        return None

    fig, ax = plt.subplots(figsize=(6.4, 3.8))
    fig.patch.set_facecolor(CARD_BG)
    ax.pie([kpis["active"], kpis["left"]], colors=[STAYED, LEFT], startangle=90,
           counterclock=False, wedgeprops={"width": 0.38, "edgecolor": CARD_BG, "linewidth": 3})
    ax.text(0, 0.07, f"{kpis['rate']:.2f}%", ha="center", va="center",
            color=TEXT, fontsize=22, fontweight="bold")
    ax.text(0, -0.2, "attrition rate", ha="center", va="center", color=MUTED, fontsize=9)

    stayed_pct = 100 - kpis["rate"]
    ax.legend(
        handles=[Patch(color=STAYED, label=f"Stayed  {stayed_pct:.2f}%"),
                 Patch(color=LEFT, label=f"Left  {kpis['rate']:.2f}%")],
        frameon=False, labelcolor=TEXT, fontsize=9, loc="center left", bbox_to_anchor=(1.0, 0.5))
    fig.text(0.03, 0.93, "Attrition Distribution (%)", color=TEXT, fontsize=13, fontweight="bold")
    return fig


def stayed_vs_left_bar(kpis):
    """Bar chart: number of employees who stayed vs left."""
    if kpis["total"] == 0:
        return None

    fig, ax = _base_figure("Employees Who Stayed vs Left")
    bars = ax.bar(["Stayed", "Left"], [kpis["active"], kpis["left"]], color=[STAYED, LEFT], width=0.5)
    ax.bar_label(bars, fmt="{:,.0f}", color=TEXT, fontsize=10, padding=3)
    ax.set_ylabel("Number of Employees", color=MUTED, fontsize=9)
    ax.set_ylim(0, max(kpis["active"], kpis["left"]) * 1.15)
    return fig


# -------------------------------------------------------- generic charts

def rate_bar(table, column, title, overall_rate=None, horizontal=False, width=6.4):
    """Attrition rate (%) per group. The highest bar is highlighted in purple."""
    if table.empty:
        return None

    labels = [str(v) if horizontal else _wrap(v) for v in table[column]]
    values = table["Rate"].tolist()
    top = max(values)
    colors = [HIGHLIGHT if v == top else BAR for v in values]
    limit = max(top, overall_rate or 0) * 1.2 + 1

    height = max(3.8, 0.42 * len(labels) + 1.4) if horizontal else 3.8
    fig, ax = _base_figure(title, height=height, horizontal=horizontal, width=width)

    if horizontal:
        bars = ax.barh(labels, values, color=colors, height=0.65)
        ax.invert_yaxis()
        ax.set_xlim(0, limit)
        ax.set_xlabel("Attrition Rate (%)", color=MUTED, fontsize=9)
    else:
        bars = ax.bar(labels, values, color=colors, width=0.6)
        ax.set_ylim(0, limit)
        ax.set_ylabel("Attrition Rate (%)", color=MUTED, fontsize=9)
    ax.bar_label(bars, fmt="%.2f%%", color=TEXT, fontsize=9, padding=3)

    if overall_rate is not None:
        _add_overall_line(ax, overall_rate, horizontal)
    return fig


def count_bar(table, column, title):
    """Number of employees in each group (used for the age-group distribution)."""
    if table.empty:
        return None

    fig, ax = _base_figure(title)
    bars = ax.bar([_wrap(v) for v in table[column]], table["Total"], color=BAR, width=0.6)
    ax.bar_label(bars, fmt="{:,.0f}", color=TEXT, fontsize=9, padding=3)
    ax.set_ylabel("Number of Employees", color=MUTED, fontsize=9)
    ax.set_ylim(0, table["Total"].max() * 1.15)
    return fig


def grouped_count_bar(df, table, column, title):
    """Side-by-side bars: employees who stayed (No) vs left (Yes) in each group."""
    if df.empty or table.empty:
        return None

    counts = df.groupby([column, "Attrition"], observed=True).size().reset_index(name="Employees")
    counts[column] = counts[column].astype(str).map(_wrap)
    order = [_wrap(v) for v in table[column]]

    fig, ax = _base_figure(title)
    sns.barplot(data=counts, x=column, y="Employees", hue="Attrition", order=order,
                hue_order=["No", "Yes"], palette={"No": STAYED, "Yes": LEFT}, ax=ax)
    for container in ax.containers:
        ax.bar_label(container, fmt="{:,.0f}", color=TEXT, fontsize=8, padding=2)
    ax.set_xlabel("")
    ax.set_ylim(0, counts["Employees"].max() * 1.25)  # headroom so the legend never covers a label
    ax.set_ylabel("Number of Employees", color=MUTED, fontsize=9)
    ax.legend(handles=[Patch(color=STAYED, label="Stayed (No)"), Patch(color=LEFT, label="Left (Yes)")],
              frameon=False, labelcolor=TEXT, fontsize=8, loc="upper right")
    return fig


# ----------------------------------------------------------------- income

def income_bar(average_income):
    """Average monthly income: employees who stayed vs left."""
    available = average_income.dropna()
    if available.empty:
        return None

    labels = [STATUS_LABELS[key] for key in available.index]
    colors = [STAYED if key == "No" else LEFT for key in available.index]

    fig, ax = _base_figure("Average Monthly Income")
    bars = ax.bar(labels, available.values, color=colors, width=0.5)
    ax.bar_label(bars, fmt="{:,.2f}", color=TEXT, fontsize=10, padding=3)
    ax.set_ylabel("Average Monthly Income", color=MUTED, fontsize=9)
    ax.set_ylim(0, available.max() * 1.15)
    return fig


def income_box(df):
    """Box plot showing how monthly income is spread for each group."""
    if df.empty:
        return None

    plot_data = df.assign(Status=df["Attrition"].map(STATUS_LABELS))
    order = [name for name in ("Stayed", "Left") if name in set(plot_data["Status"])]

    fig, ax = _base_figure("Monthly Income Distribution")
    sns.boxplot(data=plot_data, x="Status", y="MonthlyIncome", order=order, hue="Status",
                palette={"Stayed": STAYED, "Left": LEFT}, width=0.45, linecolor=MUTED,
                linewidth=1.2, legend=False, ax=ax)
    ax.set_xlabel("")
    ax.set_ylabel("Monthly Income", color=MUTED, fontsize=9)
    return fig
