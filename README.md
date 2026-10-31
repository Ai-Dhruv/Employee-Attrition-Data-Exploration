# Employee Attrition Analytics Dashboard

An interactive HR analytics dashboard built with **Python, Streamlit, Pandas, Matplotlib and Seaborn**.
It turns the Exploratory Data Analysis (EDA) from my Google Colab notebook into a professional web dashboard.

## Project Overview
The dashboard analyses the IBM HR Analytics Employee Attrition dataset and shows how attrition
varies by department, age group, overtime, job satisfaction, monthly income and more.
Every KPI, chart and insight is calculated from the real CSV and updates with the sidebar filters.

## Problem Statement
Organisations lose employees every year, and replacing them is costly. HR teams need a clear view of
*where* and *among whom* attrition is highest so they can investigate and plan retention actions.

## Project Objectives
- Measure overall employee attrition.
- Compare attrition across departments, age groups, overtime groups and job satisfaction levels.
- Compare the monthly income of employees who stayed and who left.
- Present the findings in an interactive, easy-to-read dashboard with automatic insights.

## Dataset Description
- Source: IBM HR Analytics Employee Attrition & Performance dataset
- File: `data/WA_Fn-UseC_-HR-Employee-Attrition.csv`
- 1,470 employee records, 35 columns, no missing values, no duplicate rows
- Target column: `Attrition` (`Yes` = left, `No` = stayed)

## Technology Stack
Python 3.11 | Streamlit | HTML + CSS (custom theme) | Pandas | NumPy | Matplotlib | Seaborn | VS Code

## Main Features
- Sidebar navigation and 5 working filters (Department, Gender, Age Group, Job Role, OverTime) with a Reset button
- Four KPI cards: Total, Active, Attrition Count, Attrition Rate
- Automatic **Key Insights** (no hard-coded conclusions, handles empty selections)
- Six core analyses from the notebook + additional Gender / Job Role / Education Field analysis
- Data Explorer: clean table, text search, CSV download
- Dataset Overview: shape, `info()`, `describe()`, missing values, duplicates

## EDA Findings (unfiltered dataset)
| Analysis | Result |
|---|---|
| Overall attrition | 237 of 1,470 employees left (16.12%) |
| Department | Sales highest at 20.63%; HR 19.05%; R&D 13.84% |
| Overtime | Yes 30.53% vs No 10.44% |
| Job satisfaction | Level 1: 22.84%, 2: 16.43%, 3: 16.52%, 4: 11.33% |
| Monthly income | Stayed 6,832.74 vs Left 4,787.09 (average) |
| Age group | 18-25 highest at 35.77%; 36-45 lowest at 9.19% |

These are observed associations and do not prove causation.

## Project Structure
```
Employee-Attrition-Dashboard/
├── app.py                  # Streamlit app and page layout
├── requirements.txt
├── README.md
├── .streamlit/config.toml  # Dark theme colours
├── data/
│   └── WA_Fn-UseC_-HR-Employee-Attrition.csv
├── assets/
│   └── style.css           # Custom styling
├── notebooks/
│   └── employee_Attrition.ipynb   # Original Google Colab EDA
└── utils/
    ├── __init__.py
    ├── data_loader.py      # Load + validate the CSV
    ├── analysis.py         # KPIs, attrition tables, filters, insights
    └── charts.py           # Matplotlib / Seaborn charts
```

## Installation (Windows PowerShell)
```powershell
cd path\to\Employee-Attrition-Dashboard
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
If activation is blocked, run once: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

## Execution
1. Put `WA_Fn-UseC_-HR-Employee-Attrition.csv` inside the `data` folder.
2. Run:
```powershell
streamlit run app.py
```
3. The dashboard opens at http://localhost:8501

## Future Scope
- Predictive attrition model (e.g. logistic regression / random forest)
- Correlation heatmap and more filters (tenure, salary band)
- Export dashboard summary as PDF
- Deploy on Streamlit Community Cloud
