"""
data_loader.py
--------------
Loads the IBM HR Analytics CSV and performs basic validation.
The original data is never changed - helper columns are added to a COPY.
"""

from pathlib import Path

import pandas as pd

# Project root = the folder that contains app.py (one level above /utils)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "WA_Fn-UseC_-HR-Employee-Attrition.csv"

# Columns the dashboard needs. If any are missing we show a clear error.
REQUIRED_COLUMNS = [
    "Age", "Attrition", "Department", "Gender", "JobRole", "OverTime",
    "JobSatisfaction", "MonthlyIncome", "EducationField", "EmployeeNumber",
]

# Same age groups as your Google Colab notebook
AGE_BINS = [17, 25, 35, 45, 55, 65]
AGE_LABELS = ["18-25", "26-35", "36-45", "46-55", "56-65"]

JOB_SATISFACTION_LABELS = {1: "1 - Low", 2: "2 - Medium", 3: "3 - High", 4: "4 - Very High"}


def load_raw_data(file_path=DATA_FILE):
    """Read the CSV exactly as it is and check that the needed columns exist."""
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(
            f"Dataset not found at: {file_path}\n"
            "Please place 'WA_Fn-UseC_-HR-Employee-Attrition.csv' inside the 'data' folder."
        )

    df = pd.read_csv(file_path)

    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_columns:
        raise ValueError(f"The CSV is missing required columns: {', '.join(missing_columns)}")

    return df


def add_derived_columns(df):
    """Return a copy of the data with two helper columns (originals untouched):
    - AgeGroup             (same as in your notebook)
    - JobSatisfactionLevel (1-4 converted to readable labels)
    """
    result = df.copy()
    result["AgeGroup"] = pd.cut(result["Age"], bins=AGE_BINS, labels=AGE_LABELS)
    result["JobSatisfactionLevel"] = pd.Categorical(
        result["JobSatisfaction"].map(JOB_SATISFACTION_LABELS),
        categories=list(JOB_SATISFACTION_LABELS.values()),
        ordered=True,
    )
    return result


def get_data_quality(df):
    """Data quality numbers from your notebook: shape, missing values, duplicates."""
    return {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "missing": int(df.isnull().sum().sum()),
        "duplicates": int(df.duplicated().sum()),
    }
