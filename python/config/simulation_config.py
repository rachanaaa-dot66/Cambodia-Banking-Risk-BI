# =============================================================================
# simulation_config.py
# Cambodia Banking Risk & Business Intelligence Platform
# Central configuration — all simulation parameters sourced from:
#   05_Simulation_Logic.md  &  06_Data_Generation_Roadmap.md
# =============================================================================

import os
from datetime import date

# ---------------------------------------------------------------------------
# Simulation Period  (doc 05 §2)
# ---------------------------------------------------------------------------
SIM_START_DATE = date(2024, 1, 1)
SIM_END_DATE   = date(2025, 12, 31)
SIM_MONTHS     = 24   # Jan-2024 → Dec-2025

# ---------------------------------------------------------------------------
# Economic Phase Calendar  (doc 05 §2)
# ---------------------------------------------------------------------------
ECONOMIC_PHASES = {
    2024: "Agricultural Stress Event",
    2025: "Tourism Slowdown Event",
}

# ---------------------------------------------------------------------------
# Branch Network  (doc 06 §4)
# ---------------------------------------------------------------------------
BRANCH_TARGET = 20

BRANCHES = [
    # (branch_name, province, city, branch_type)
    ("Phnom Penh Central",    "Phnom Penh",       "Phnom Penh",    "Urban"),
    ("Phnom Penh South",      "Phnom Penh",       "Phnom Penh",    "Urban"),
    ("Phnom Penh North",      "Phnom Penh",       "Phnom Penh",    "Urban"),
    ("Siem Reap Main",        "Siem Reap",        "Siem Reap",     "Urban"),
    ("Siem Reap Angkor",      "Siem Reap",        "Siem Reap",     "Urban"),
    ("Battambang Central",    "Battambang",       "Battambang",    "Urban"),
    ("Battambang Rural",      "Battambang",       "Bavel",         "Rural"),
    ("Kampong Cham Main",     "Kampong Cham",     "Kampong Cham",  "Urban"),
    ("Kampong Cham East",     "Kampong Cham",     "Cheung Prey",   "Rural"),
    ("Kandal Branch",         "Kandal",           "Ta Khmau",      "Urban"),
    ("Kandal Rural",          "Kandal",           "Koh Thom",      "Rural"),
    ("Takeo Branch",          "Takeo",            "Takeo",         "Urban"),
    ("Takeo South",           "Takeo",            "Kirivong",      "Rural"),
    ("Banteay Meanchey Main", "Banteay Meanchey", "Sisophon",      "Urban"),
    ("Banteay Meanchey Rural","Banteay Meanchey", "Mongkol Borei", "Rural"),
    ("Prey Veng Branch",      "Prey Veng",        "Prey Veng",     "Urban"),
    ("Prey Veng Rural",       "Prey Veng",        "Peam Ro",       "Rural"),
    ("Phnom Penh East",       "Phnom Penh",       "Phnom Penh",    "Urban"),
    ("Kampong Speu Branch",   "Kampong Speu",     "Chbar Mon",     "Urban"),
    ("Koh Kong Branch",       "Koh Kong",         "Koh Kong",      "Rural"),
]

# ---------------------------------------------------------------------------
# Customer Volume  (doc 05 §3)
# ---------------------------------------------------------------------------
CUSTOMER_TARGET = 5_000

# Age distribution  (doc 05 §3)
AGE_DISTRIBUTION = {
    (18, 24): 0.15,
    (25, 34): 0.30,
    (35, 44): 0.25,
    (45, 54): 0.15,
    (55, 65): 0.15,
}

# Gender distribution  (doc 05 §3)
GENDER_DISTRIBUTION = {"Male": 0.50, "Female": 0.50}

# Occupation distribution  (doc 05 §3)
OCCUPATION_DISTRIBUTION = {
    "Farmer":             0.25,
    "Private Employee":   0.25,
    "SME Owner":          0.20,
    "Factory Worker":     0.10,
    "Government Officer": 0.10,
    "Freelancer":         0.05,
    "Student":            0.05,
}

# Marital status
MARITAL_STATUS_DISTRIBUTION = {
    "Married": 0.55,
    "Single":  0.35,
    "Divorced":0.07,
    "Widowed": 0.03,
}

# ---------------------------------------------------------------------------
# Province weights for customer assignment
# ---------------------------------------------------------------------------
PROVINCE_WEIGHTS = {
    "Phnom Penh":       0.30,
    "Siem Reap":        0.15,
    "Battambang":       0.12,
    "Kampong Cham":     0.10,
    "Kandal":           0.10,
    "Takeo":            0.08,
    "Banteay Meanchey": 0.08,
    "Prey Veng":        0.07,
}

# ---------------------------------------------------------------------------
# Income ranges by occupation  (doc 05 §5)
# ---------------------------------------------------------------------------
INCOME_RANGES = {
    "Farmer":             (150,  800),
    "Factory Worker":     (200,  600),
    "Private Employee":   (300, 1500),
    "Government Officer": (350, 1200),
    "SME Owner":          (500, 5000),
    "Freelancer":         (250, 3000),
    "Student":            (0,    300),
}

INCOME_AVERAGES = {
    "Farmer":             450,
    "Factory Worker":     400,
    "Private Employee":   850,
    "Government Officer": 700,
    "SME Owner":          1500,
    "Freelancer":         900,
    "Student":            100,
}

# ---------------------------------------------------------------------------
# Account product probabilities  (doc 05 §6 / doc 06 §6)
# ---------------------------------------------------------------------------
ACCOUNT_PRODUCTS = {
    "Savings": {
        "base_prob": 0.95,
        "all_occupations": True,
    },
    "Fixed Deposit": {
        "income_threshold": 800,   # USD/month
        "age_threshold": 35,
        "base_prob": 0.30,
    },
    "Payroll": {
        "eligible_occupations": ["Government Officer", "Private Employee", "Factory Worker"],
        "base_prob": 0.70,
    },
    "Business": {
        "eligible_occupations": ["SME Owner"],
        "base_prob": 0.80,
    },
}

# ---------------------------------------------------------------------------
# Loan assignment  (doc 05 §7, §8)
# ---------------------------------------------------------------------------
LOAN_ELIGIBILITY = {
    "min_age":           21,
    "min_credit_score":  450,
    "max_dti":           0.60,
    "loan_penetration":  0.60,   # ~60 % of customers get at least one loan
}

LOAN_TYPES = {
    "Personal Loan":     {"eligible_occupations": ["Private Employee", "Government Officer", "Factory Worker", "Freelancer"],
                          "rate_range": (12.0, 18.0), "term_range": (12, 60)},
    "Agriculture Loan":  {"eligible_occupations": ["Farmer"],
                          "rate_range": (9.0, 14.0),  "term_range": (12, 48)},
    "SME Loan":          {"eligible_occupations": ["SME Owner"],
                          "rate_range": (10.0, 16.0), "term_range": (24, 84)},
    "Housing Loan":      {"min_age": 30, "min_income": 400,
                          "rate_range": (8.0, 12.0),  "term_range": (60, 240)},
    "Vehicle Loan":      {"income_range": (300, 2000),
                          "rate_range": (10.0, 15.0), "term_range": (24, 60)},
}

# Loan-to-income multipliers  (doc 05 §8)
LOAN_INCOME_MULTIPLIERS = {
    "Personal Loan":    (6,  18),
    "Agriculture Loan": (4,  15),
    "SME Loan":         (12, 36),
    "Housing Loan":     (20, 60),
    "Vehicle Loan":     (6,  20),
}

# ---------------------------------------------------------------------------
# Credit score ranges by occupation  (doc 05 §9)
# ---------------------------------------------------------------------------
CREDIT_SCORE_RANGES = {
    "SME Owner":          (600, 850),
    "Government Officer": (650, 800),
    "Private Employee":   (600, 750),
    "Factory Worker":     (550, 700),
    "Freelancer":         (550, 720),
    "Farmer":             (550, 700),
    "Student":            (450, 650),
}

# ---------------------------------------------------------------------------
# Risk categories  (doc 05 §10)
# ---------------------------------------------------------------------------
RISK_CATEGORIES = [
    (750, 850, "Very Low Risk"),
    (650, 749, "Low Risk"),
    (550, 649, "Medium Risk"),
    (450, 549, "High Risk"),
    (300, 449, "Very High Risk"),
]

def get_risk_category(score: int) -> str:
    for low, high, cat in RISK_CATEGORIES:
        if low <= score <= high:
            return cat
    return "Very High Risk"

# ---------------------------------------------------------------------------
# Credit score migration  (doc 05 §13)
# ---------------------------------------------------------------------------
SCORE_DELTA = {
    "on_time":  (1,   5),
    "late":     (-15, -5),
    "missed":   (-30, -15),
    "default":  (-100, -50),
}

SCORE_MIN = 300
SCORE_MAX = 850

# ---------------------------------------------------------------------------
# Payment behaviour probabilities  (doc 05 §12)
# Adjusted per risk category
# ---------------------------------------------------------------------------
PAYMENT_PROBS = {
    "Very Low Risk":  {"on_time": 0.97, "late": 0.025, "missed": 0.005},
    "Low Risk":       {"on_time": 0.93, "late": 0.055, "missed": 0.015},
    "Medium Risk":    {"on_time": 0.82, "late": 0.13,  "missed": 0.05},
    "High Risk":      {"on_time": 0.65, "late": 0.24,  "missed": 0.11},
    "Very High Risk": {"on_time": 0.45, "late": 0.32,  "missed": 0.23},
}

# Days past due for each outcome
DPD_RANGES = {
    "on_time": (0,  0),
    "late":    (1,  89),
    "missed":  (30, 180),
}

# ---------------------------------------------------------------------------
# Economic events  (doc 05 §16)
# ---------------------------------------------------------------------------
ECONOMIC_EVENTS = [
    {
        "event_id":          1,
        "event_name":        "Agricultural Stress 2024",
        "start_date":        date(2024, 3, 1),
        "end_date":          date(2024, 12, 31),
        "affected_province": "Battambang,Takeo,Prey Veng",
        "affected_sector":   "Farmer",
        "severity":          "High",
        "income_shock":      -0.25,   # 25 % income reduction
        "delinquency_boost": 0.15,    # +15 pp extra missed prob
        "score_penalty":     -20,     # extra score drag per month
    },
    {
        "event_id":          2,
        "event_name":        "Tourism Slowdown 2025",
        "start_date":        date(2025, 1, 1),
        "end_date":          date(2025, 12, 31),
        "affected_province": "Siem Reap",
        "affected_sector":   "SME Owner",
        "severity":          "Medium",
        "income_shock":      -0.20,
        "delinquency_boost": 0.10,
        "score_penalty":     -15,
    },
]

# ---------------------------------------------------------------------------
# Transaction frequency (transactions / month)  (doc 05 §11)
# ---------------------------------------------------------------------------
TXN_FREQ = {
    "SME Owner":          (8, 20),
    "Private Employee":   (5, 12),
    "Government Officer": (4, 10),
    "Factory Worker":     (3, 8),
    "Freelancer":         (4, 10),
    "Farmer":             (2, 6),
    "Student":            (2, 6),
}

TXN_TYPE_WEIGHTS = {
    "Deposit":        0.30,
    "Withdrawal":     0.35,
    "Transfer":       0.20,
    "Loan Payment":   0.10,
    "Interest Credit":0.05,
}

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_RAW      = os.path.join(BASE_DIR, "..", "data", "raw")
DATA_PROCESSED= os.path.join(BASE_DIR, "..", "data", "processed")
DATA_WAREHOUSE= os.path.join(BASE_DIR, "..", "data", "warehouse")

# ---------------------------------------------------------------------------
# Random seed for reproducibility  (doc 05 §19)
# ---------------------------------------------------------------------------
RANDOM_SEED = 42
