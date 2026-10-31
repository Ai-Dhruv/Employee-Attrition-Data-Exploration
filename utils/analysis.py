"""
analysis.py
-----------
All attrition calculations. Every function works on whatever DataFrame it is given
(full dataset OR filtered dataset), so KPIs, charts and insights stay in sync.
"""

import pandas as pd


def calculate_attrition_rate(attrition_series):
    """Attrition rate in % = share of 'Yes' values (same formula as the notebook)."""
    if len(attrition_series) == 0:
        return 0.0
    return round((attrition_series == "Yes").mean() * 100, 2)


def calculate_kpis(df):
    """Numbers for the four KPI cards."""
    total = len(df)
    left = int((df["Attrition"] == "Yes").sum())
    return {
        "total": total,
        "active": total - left,
        "left": left,
        "rate": calculate_attrition_rate(df["Attrition"]),
    }


def filter_data(df, departments, genders, age_groups, job_roles, overtime):
    """Keep only rows that match ALL selected sidebar filters."""
    mask = (
        df["Department"].isin(departments)
        & df["Gender"].isin(genders)
        & df["AgeGroup"].isin(age_groups)
        & df["JobRole"].isin(job_roles)
        & df["OverTime"].isin(overtime)
    )
    return df[mask]


def attrition_by_group(df, column):
    """Attrition table for any column.
    Returns columns: <column>, Total, Left (Attrition Yes), Stayed (Attrition No), Rate (%).
    Groups with zero employees are dropped.
    """
    if df.empty:
        return pd.DataFrame(columns=[column, "Total", "Left", "Stayed", "Rate"])

    table = (
        df.groupby(column, observed=True)["Attrition"]
        .agg(Total="size", Left=lambda s: int((s == "Yes").sum()))
        .reset_index()
    )
    table["Stayed"] = table["Total"] - table["Left"]
    table["Rate"] = (table["Left"] / table["Total"] * 100).round(2)
    return table


def average_income_by_attrition(df):
    """Average monthly income for 'No' (stayed) and 'Yes' (left)."""
    return df.groupby("Attrition")["MonthlyIncome"].mean().round(2).reindex(["No", "Yes"])


# ---------------------------------------------------------------- insights

def _highest_group_insight(icon, title, table, column, subject):
    """Sentence about the group with the highest attrition rate."""
    top = table.loc[table["Rate"].idxmax()]
    if len(table) == 1:
        text = (f"Only the {subject} '{top[column]}' is in the current selection: "
                f"{top['Rate']:.2f}% attrition ({top['Left']:,} of {top['Total']:,} employees).")
    else:
        text = (f"'{top[column]}' has the highest attrition rate among {subject}s at "
                f"{top['Rate']:.2f}% ({top['Left']:,} of {top['Total']:,} employees).")
    return {"icon": icon, "title": title, "text": text}


def _overtime_insight(table):
    """Sentence comparing the overtime groups."""
    if len(table) == 1:
        row = table.iloc[0]
        return {"icon": "⏱️", "title": "Overtime",
                "text": f"Only employees with OverTime = {row['OverTime']} are in the selection "
                        f"({row['Rate']:.2f}% attrition)."}

    top = table.loc[table["Rate"].idxmax()]
    low = table.loc[table["Rate"].idxmin()]
    if top["Rate"] == low["Rate"]:
        text = f"Both overtime groups have the same attrition rate ({top['Rate']:.2f}%)."
    else:
        name = {"Yes": "who work overtime", "No": "who do not work overtime"}
        text = (f"Employees {name[top['OverTime']]} have a higher attrition rate "
                f"({top['Rate']:.2f}%) than employees {name[low['OverTime']]} ({low['Rate']:.2f}%).")
    return {"icon": "⏱️", "title": "Overtime", "text": text}


def _income_insight(df):
    """Sentence comparing average monthly income of leavers and stayers."""
    avg = average_income_by_attrition(df)
    if avg.isnull().any():
        text = "An income comparison needs both employees who stayed and who left in the selection."
    else:
        stayed, left = avg["No"], avg["Yes"]
        diff = (left - stayed) / stayed * 100
        direction = "lower" if diff < 0 else "higher"
        text = (f"Employees who left earned {left:,.2f} per month on average, versus {stayed:,.2f} "
                f"for those who stayed ({abs(diff):.1f}% {direction}).")
    return {"icon": "💰", "title": "Monthly income", "text": text}


def generate_insights(df):
    """Build the Key Insights list from the CURRENT (filtered) data.
    Returns an empty list when there is no data."""
    if df.empty:
        return []

    kpis = calculate_kpis(df)
    return [
        {"icon": "📊", "title": "Overall attrition",
         "text": f"{kpis['rate']:.2f}% of employees in this selection left "
                 f"({kpis['left']:,} of {kpis['total']:,})."},
        _highest_group_insight("🏢", "Department", attrition_by_group(df, "Department"),
                               "Department", "department"),
        _highest_group_insight("🎂", "Age group", attrition_by_group(df, "AgeGroup"),
                               "AgeGroup", "age group"),
        _overtime_insight(attrition_by_group(df, "OverTime")),
        _highest_group_insight("😊", "Job satisfaction",
                               attrition_by_group(df, "JobSatisfactionLevel"),
                               "JobSatisfactionLevel", "job satisfaction level"),
        _income_insight(df),
    ]
