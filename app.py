"""
Employee Attrition Analytics Dashboard
Run with:  streamlit run app.py
"""

import html
import io
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from utils import analysis, charts, data_loader

# This must be the first Streamlit command in the script.
st.set_page_config(page_title="Employee Attrition Analytics", page_icon="📊", layout="wide")

CSS_FILE = Path(__file__).resolve().parent / "assets" / "style.css"

PAGES = ["📊 Dashboard", "🔎 Data Explorer", "🗂️ Dataset Overview"]

# Sidebar filters: session-state key -> (label shown, dataframe column)
FILTERS = {
    "filter_department": ("Department", "Department"),
    "filter_gender": ("Gender", "Gender"),
    "filter_age_group": ("Age Group", "AgeGroup"),
    "filter_job_role": ("Job Role", "JobRole"),
    "filter_overtime": ("OverTime", "OverTime"),
}

# Columns hidden in the Data Explorer (identifiers / constant technical columns)
HIDDEN_COLUMNS = ["EmployeeNumber", "EmployeeCount", "Over18", "StandardHours", "JobSatisfactionLevel"]


# ======================================================================
# Setup helpers
# ======================================================================

def apply_custom_css():
    """Inject assets/style.css into the page."""
    if CSS_FILE.exists():
        st.markdown(f"<style>{CSS_FILE.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


@st.cache_data(show_spinner="Loading dataset...")
def load_dataset():
    """Load the CSV once and keep it in cache. Returns (original data, data + helper columns)."""
    raw_df = data_loader.load_raw_data()
    return raw_df, data_loader.add_derived_columns(raw_df)


def get_filter_options(df):
    """All possible values for each sidebar filter."""
    options = {}
    for key, (_, column) in FILTERS.items():
        if column == "AgeGroup":
            options[key] = list(data_loader.AGE_LABELS)  # keep natural order
        else:
            options[key] = sorted(df[column].dropna().unique().tolist())
    return options


def reset_filters(options):
    """Button callback: select every option again."""
    for key, values in options.items():
        st.session_state[key] = list(values)


# ======================================================================
# Sidebar
# ======================================================================

def render_sidebar(df):
    """Draw the sidebar and return (selected page, filtered dataframe)."""
    options = get_filter_options(df)

    with st.sidebar:
        st.markdown(
            '<div class="brand"><div class="brand-logo">📊</div><div>'
            '<div class="brand-name">Attrition Analytics</div>'
            '<div class="brand-tag">HR INSIGHTS DASHBOARD</div></div></div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div class="sidebar-label">Navigation</div>', unsafe_allow_html=True)
        page = st.radio("Navigation", PAGES, label_visibility="collapsed")

        st.markdown('<div class="sidebar-label">Filters</div>', unsafe_allow_html=True)
        for key, (label, _) in FILTERS.items():
            if key not in st.session_state:          # first run: everything selected
                st.session_state[key] = list(options[key])
            st.multiselect(label, options[key], key=key)

        st.button("↺  Reset filters", on_click=reset_filters, args=(options,), width="stretch")

    filtered_df = analysis.filter_data(
        df,
        st.session_state["filter_department"],
        st.session_state["filter_gender"],
        st.session_state["filter_age_group"],
        st.session_state["filter_job_role"],
        st.session_state["filter_overtime"],
    )
    return page, filtered_df


# ======================================================================
# Reusable UI pieces
# ======================================================================

def render_header():
    today = datetime.now().strftime("%A, %d %B %Y")
    st.markdown(
        '<div class="hero"><div>'
        '<h1 class="hero-title">Employee Attrition Analytics</h1>'
        '<p class="hero-sub">Understand workforce trends, identify attrition patterns, '
        'and support better HR decisions.</p></div>'
        f'<div class="date-pill">📅 {today}</div></div>',
        unsafe_allow_html=True,
    )


def kpi_card(icon, label, value, note, color):
    return (f'<div class="kpi-card {color}"><div class="kpi-icon">{icon}</div><div>'
            f'<div class="kpi-label">{label}</div><div class="kpi-value">{value}</div>'
            f'<div class="kpi-note">{note}</div></div></div>')


def render_cards(cards):
    st.markdown('<div class="kpi-grid">' + "".join(cards) + "</div>", unsafe_allow_html=True)


def section_header(title, subtitle, badge=None):
    """Section title with an optional 'Core EDA' / 'Additional' badge."""
    badge_html = ""
    if badge == "core":
        badge_html = '<span class="badge core">Core EDA</span>'
    elif badge == "extra":
        badge_html = '<span class="badge extra">Additional analysis</span>'
    st.markdown(
        f'<div class="section-head"><span class="section-title">{title}</span>{badge_html}</div>'
        f'<p class="section-sub">{subtitle}</p>',
        unsafe_allow_html=True,
    )


def show_chart(fig, empty_message="No data available for the selected filters."):
    """Display a Matplotlib figure inside a card (or a friendly message if there is no data)."""
    with st.container(border=True):
        if fig is None:
            st.info(empty_message)
        else:
            st.pyplot(fig)
            plt.close(fig)  # free memory


def show_table(table, column, label):
    """Small table (Yes / No / Rate) so numbers can be compared with the notebook."""
    view = table.rename(columns={column: label, "Left": "Attrition Yes",
                                 "Stayed": "Attrition No", "Rate": "Attrition Rate (%)"})
    st.dataframe(view[[label, "Attrition Yes", "Attrition No", "Attrition Rate (%)"]],
                 hide_index=True, width="stretch")


# ======================================================================
# Page 1: Dashboard
# ======================================================================

def render_kpis(df, full_df):
    kpis = analysis.calculate_kpis(df)
    overall = analysis.calculate_attrition_rate(full_df["Attrition"])
    active_share = 100 - kpis["rate"] if kpis["total"] else 0
    render_cards([
        kpi_card("👥", "Total Employees", f"{kpis['total']:,}",
                 f"of {len(full_df):,} in dataset", "blue"),
        kpi_card("✅", "Active Employees", f"{kpis['active']:,}",
                 f"{active_share:.2f}% of selection", "sky"),
        kpi_card("🚪", "Attrition Count", f"{kpis['left']:,}",
                 "employees who left", "purple"),
        kpi_card("📉", "Attrition Rate", f"{kpis['rate']:.2f}%",
                 f"dataset overall: {overall:.2f}%", "pink"),
    ])
    return kpis


def render_insights(df):
    insights = analysis.generate_insights(df)
    if not insights:
        return
    section_header("Key Insights", "Generated automatically from the current selection.")
    cards = "".join(
        f'<div class="insight-card"><div class="insight-title">{item["icon"]} {html.escape(item["title"])}</div>'
        f'<div class="insight-text">{html.escape(item["text"])}</div></div>'
        for item in insights
    )
    st.markdown(f'<div class="insight-grid">{cards}</div>'
                '<p class="note">These are observed patterns in the data. They show association, '
                'not proof that one factor causes attrition.</p>', unsafe_allow_html=True)


def render_dashboard(df, full_df):
    render_header()
    kpis = render_kpis(df, full_df)

    if df.empty:
        st.warning("No employees match the selected filters. Choose at least one option in every "
                   "filter, or click **Reset filters** in the sidebar.")
        return

    overall_rate = kpis["rate"]
    render_insights(df)

    # ---- D. Attrition overview ----
    section_header("Attrition Overview", "How many employees stayed and how many left.", "core")
    col1, col2 = st.columns(2)
    with col1:
        show_chart(charts.attrition_donut(kpis))
    with col2:
        show_chart(charts.stayed_vs_left_bar(kpis))

    # ---- E. Department ----
    dept = analysis.attrition_by_group(df, "Department")
    section_header("Department Analysis", "Attrition count, comparison and rate by department.", "core")
    col1, col2 = st.columns(2)
    with col1:
        show_chart(charts.grouped_count_bar(df, dept, "Department", "Attrition Count by Department"))
    with col2:
        show_chart(charts.rate_bar(dept, "Department", "Attrition Rate by Department", overall_rate))
    with st.expander("View department table"):
        show_table(dept, "Department", "Department")

    # ---- F. Overtime ----
    overtime = analysis.attrition_by_group(df, "OverTime")
    section_header("Overtime Analysis", "Do employees who work overtime leave more often?", "core")
    col1, col2 = st.columns(2)
    with col1:
        show_chart(charts.grouped_count_bar(df, overtime, "OverTime", "Overtime vs Attrition Count"))
    with col2:
        show_chart(charts.rate_bar(overtime, "OverTime", "Overtime vs Attrition Rate", overall_rate))
    with st.expander("View overtime table"):
        show_table(overtime, "OverTime", "OverTime")

    # ---- G. Job satisfaction ----
    satisfaction = analysis.attrition_by_group(df, "JobSatisfactionLevel")
    section_header("Job Satisfaction Analysis", "Satisfaction levels: 1 = Low, 2 = Medium, 3 = High, 4 = Very High.", "core")
    col1, col2 = st.columns(2)
    with col1:
        show_chart(charts.grouped_count_bar(df, satisfaction, "JobSatisfactionLevel", "Employees by Job Satisfaction"))
    with col2:
        show_chart(charts.rate_bar(satisfaction, "JobSatisfactionLevel", "Attrition Rate by Job Satisfaction", overall_rate))
    with st.expander("View job satisfaction table"):
        show_table(satisfaction, "JobSatisfactionLevel", "Job Satisfaction")

    # ---- H. Age ----
    age = analysis.attrition_by_group(df, "AgeGroup")
    section_header("Age Analysis", "Employee distribution and attrition rate by age group.", "core")
    col1, col2 = st.columns(2)
    with col1:
        show_chart(charts.count_bar(age, "AgeGroup", "Employees by Age Group"))
    with col2:
        show_chart(charts.rate_bar(age, "AgeGroup", "Attrition Rate by Age Group", overall_rate))
    with st.expander("View age group table"):
        show_table(age, "AgeGroup", "Age Group")

    # ---- I. Income ----
    section_header("Income Analysis", "Average monthly income of employees who stayed vs left.", "core")
    col1, col2 = st.columns(2)
    with col1:
        show_chart(charts.income_bar(analysis.average_income_by_attrition(df)))
    with col2:
        show_chart(charts.income_box(df))

    # ---- J. Additional analysis ----
    section_header("Additional Analysis", "Extra views beyond the six core analyses in the notebook.", "extra")
    gender = analysis.attrition_by_group(df, "Gender")
    education = analysis.attrition_by_group(df, "EducationField")
    role = analysis.attrition_by_group(df, "JobRole")
    col1, col2 = st.columns(2)
    with col1:
        show_chart(charts.rate_bar(gender, "Gender", "Attrition Rate by Gender", overall_rate))
    with col2:
        show_chart(charts.rate_bar(education, "EducationField", "Attrition Rate by Education Field",
                                   overall_rate, horizontal=True))
    show_chart(charts.rate_bar(role, "JobRole", "Attrition Rate by Job Role", overall_rate,
                                  horizontal=True, width=12.8))


# ======================================================================
# Page 2: Data Explorer
# ======================================================================

def search_records(df, query):
    """Keep rows where any text column contains the search text (case-insensitive)."""
    text_columns = [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c])]
    mask = pd.Series(False, index=df.index)
    for column in text_columns:
        mask |= df[column].astype(str).str.contains(query, case=False, na=False, regex=False)
    return df[mask]


def render_explorer(df):
    render_header()
    section_header("Employee Data Explorer",
                   "Browse, search and download employee records. Sidebar filters apply here too.")

    visible = df.drop(columns=HIDDEN_COLUMNS, errors="ignore")
    query = st.text_input("Search records", placeholder="Try: Sales, Laboratory Technician, Male, Yes ...")
    if query.strip():
        visible = search_records(visible, query.strip())

    st.caption(f"Showing {len(visible):,} of {len(df):,} employees (identifier and constant columns are hidden).")
    if visible.empty:
        st.warning("No records match your filters and search. Try changing them.")
        return

    st.dataframe(visible, hide_index=True, width="stretch", height=520)
    st.download_button("⬇  Download as CSV", data=visible.to_csv(index=False).encode("utf-8"),
                       file_name="filtered_employee_attrition.csv", mime="text/csv")


# ======================================================================
# Page 3: Dataset Overview (the first part of the notebook)
# ======================================================================

def render_dataset_overview(raw_df):
    render_header()
    section_header("Dataset Overview", "Original, unfiltered dataset - same checks as in the notebook.", "core")

    quality = data_loader.get_data_quality(raw_df)
    render_cards([
        kpi_card("🧾", "Rows", f"{quality['rows']:,}", "employee records", "blue"),
        kpi_card("🏷️", "Columns", f"{quality['columns']}", "original columns", "sky"),
        kpi_card("❓", "Missing Values", f"{quality['missing']}", "across all columns", "purple"),
        kpi_card("🧬", "Duplicate Rows", f"{quality['duplicates']}", "exact duplicates", "pink"),
    ])

    counts = raw_df["Attrition"].value_counts()
    percent = (raw_df["Attrition"].value_counts(normalize=True) * 100).round(2)
    st.markdown("**Overall attrition**")
    st.dataframe(pd.DataFrame({"Employees": counts, "Percentage (%)": percent}), width="stretch")

    tab_head, tab_info, tab_describe, tab_columns = st.tabs(
        ["First rows", "df.info()", "df.describe()", "Column names"])
    with tab_head:
        st.dataframe(raw_df.head(10), hide_index=True, width="stretch")
    with tab_info:
        buffer = io.StringIO()
        raw_df.info(buf=buffer)
        st.code(buffer.getvalue())
    with tab_describe:
        st.dataframe(raw_df.describe().T, width="stretch")
    with tab_columns:
        st.dataframe(pd.DataFrame({"Column": raw_df.columns, "Type": raw_df.dtypes.astype(str).values}),
                     hide_index=True, width="stretch")


# ======================================================================
# Main
# ======================================================================

def main():
    apply_custom_css()

    try:
        raw_df, df = load_dataset()
    except FileNotFoundError as error:
        st.error("Dataset file not found")
        st.code(str(error))
        st.stop()
    except ValueError as error:
        st.error("The dataset file is not in the expected format")
        st.code(str(error))
        st.stop()

    page, filtered_df = render_sidebar(df)

    if page == PAGES[0]:
        render_dashboard(filtered_df, df)
    elif page == PAGES[1]:
        render_explorer(filtered_df)
    else:
        render_dataset_overview(raw_df)


main()
