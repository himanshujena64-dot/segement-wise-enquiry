"""
SAP MRP ENGINE — Professional Sidebar Navigation Layout
========================================================
Nav pages: Home · Upload Files · Run MRP · Segment Capacity · Aging · Settings
"""

import io
import re
from collections import defaultdict

import numpy as np
import pandas as pd
import streamlit as st
from scipy.optimize import linprog

# ═══════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="SAP MRP Engine",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ═══════════════════════════════════════════════════════════════
# GLOBAL CSS — full layout takeover
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Reset Streamlit chrome ──────────────────────────────── */
[data-testid="stSidebar"],
[data-testid="collapsedControl"],
#MainMenu, footer, header { display: none !important; }

html, body { overflow: hidden; }

.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

[data-testid="stAppViewContainer"] {
    padding: 0 !important;
}

/* ── App shell ────────────────────────────────────────────── */
.app-shell {
    display: flex;
    height: 100vh;
    width: 100vw;
    font-family: 'Plus Jakarta Sans', sans-serif;
    background: #f0f2f5;
    overflow: hidden;
}

/* ── Left nav ─────────────────────────────────────────────── */
.nav-panel {
    width: 240px;
    min-width: 240px;
    background: #0d1b2a;
    display: flex;
    flex-direction: column;
    padding: 0;
    overflow: hidden;
    position: relative;
}

.nav-logo {
    padding: 20px 20px 16px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    display: flex;
    align-items: center;
    gap: 10px;
}

.nav-logo-icon {
    width: 34px;
    height: 34px;
    background: #1a6ef7;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    flex-shrink: 0;
}

.nav-logo-text {
    font-size: 13px;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: 0.04em;
    line-height: 1.2;
}

.nav-logo-sub {
    font-size: 10px;
    color: rgba(255,255,255,0.35);
    font-weight: 400;
    letter-spacing: 0.06em;
}

.nav-section-label {
    font-size: 10px;
    font-weight: 600;
    color: rgba(255,255,255,0.25);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 18px 20px 6px;
}

.nav-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 9px 16px;
    margin: 1px 8px;
    border-radius: 8px;
    cursor: pointer;
    transition: background 0.15s;
    font-size: 13px;
    font-weight: 500;
    color: rgba(255,255,255,0.55);
    text-decoration: none;
    border: none;
    background: none;
    width: calc(100% - 16px);
    text-align: left;
}

.nav-item:hover {
    background: rgba(255,255,255,0.06);
    color: rgba(255,255,255,0.85);
}

.nav-item.active {
    background: #1a6ef7;
    color: #ffffff;
}

.nav-item .nav-icon {
    width: 18px;
    height: 18px;
    opacity: 0.7;
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
}

.nav-item.active .nav-icon { opacity: 1; }

.nav-badge {
    margin-left: auto;
    background: rgba(255,255,255,0.12);
    color: rgba(255,255,255,0.6);
    font-size: 10px;
    font-weight: 600;
    padding: 2px 7px;
    border-radius: 10px;
}

.nav-badge.done {
    background: rgba(34,197,94,0.2);
    color: #4ade80;
}

.nav-badge.ready {
    background: rgba(251,191,36,0.2);
    color: #fbbf24;
}

.nav-footer {
    margin-top: auto;
    padding: 16px 20px;
    border-top: 1px solid rgba(255,255,255,0.06);
}

.nav-footer-help {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    color: rgba(255,255,255,0.35);
}

.nav-footer-help span { font-size: 10px; color: rgba(255,255,255,0.2); }

/* ── Main content ─────────────────────────────────────────── */
.main-content {
    flex: 1;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    min-width: 0;
}

.topbar {
    background: #ffffff;
    border-bottom: 1px solid #e5e7eb;
    padding: 0 32px;
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-shrink: 0;
    position: sticky;
    top: 0;
    z-index: 10;
}

.topbar-title {
    font-size: 17px;
    font-weight: 700;
    color: #111827;
    letter-spacing: -0.01em;
}

.topbar-subtitle {
    font-size: 12px;
    color: #9ca3af;
    font-weight: 400;
    margin-top: 1px;
}

.topbar-right {
    display: flex;
    align-items: center;
    gap: 12px;
}

.status-chip {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 11px;
    font-weight: 600;
    padding: 4px 10px;
    border-radius: 20px;
    letter-spacing: 0.02em;
}

.status-chip.idle {
    background: #f3f4f6;
    color: #6b7280;
}

.status-chip.done {
    background: #dcfce7;
    color: #15803d;
}

.status-chip.pending {
    background: #fef3c7;
    color: #b45309;
}

.status-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: currentColor;
}

.page-content {
    padding: 32px;
    flex: 1;
}

/* ── Upload cards ─────────────────────────────────────────── */
.upload-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    margin-bottom: 28px;
}

.upload-card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 20px;
    transition: border-color 0.2s, box-shadow 0.2s;
}

.upload-card:hover {
    border-color: #93c5fd;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.06);
}

.upload-card-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    margin-bottom: 12px;
}

.upload-card-icon {
    width: 36px;
    height: 36px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 17px;
    flex-shrink: 0;
}

.upload-card-icon.purple { background: #ede9fe; }
.upload-card-icon.green  { background: #dcfce7; }
.upload-card-icon.orange { background: #ffedd5; }
.upload-card-icon.blue   { background: #dbeafe; }

.upload-card-meta { margin-left: 12px; flex: 1; }

.upload-card-title {
    font-size: 14px;
    font-weight: 600;
    color: #111827;
    margin: 0 0 2px 0;
}

.upload-card-desc {
    font-size: 12px;
    color: #6b7280;
    margin: 0;
}

.badge-required {
    font-size: 10px;
    font-weight: 600;
    background: #fee2e2;
    color: #dc2626;
    padding: 3px 8px;
    border-radius: 10px;
    white-space: nowrap;
}

.badge-optional {
    font-size: 10px;
    font-weight: 600;
    background: #f0fdf4;
    color: #16a34a;
    padding: 3px 8px;
    border-radius: 10px;
    white-space: nowrap;
}

.accepted-text {
    font-size: 11px;
    color: #9ca3af;
    margin-top: 8px;
    font-family: 'JetBrains Mono', monospace;
}

/* ── Run button area ──────────────────────────────────────── */
.run-area {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 20px 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
}

.run-area-text {
    font-size: 14px;
    font-weight: 600;
    color: #111827;
}

.run-area-sub {
    font-size: 12px;
    color: #6b7280;
    margin-top: 2px;
}

/* ── Summary / metric cards ───────────────────────────────── */
.metric-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-bottom: 24px;
}

.metric-card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    padding: 16px 18px;
}

.metric-label {
    font-size: 11px;
    font-weight: 600;
    color: #9ca3af;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-bottom: 6px;
}

.metric-value {
    font-size: 22px;
    font-weight: 700;
    color: #111827;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: -0.02em;
}

.metric-delta {
    font-size: 11px;
    margin-top: 4px;
    font-weight: 500;
}

.metric-delta.good { color: #16a34a; }
.metric-delta.bad  { color: #dc2626; }

/* ── Section headers ──────────────────────────────────────── */
.section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 28px 0 14px;
}

.section-header-line {
    flex: 1;
    height: 1px;
    background: #e5e7eb;
}

.section-header-text {
    font-size: 11px;
    font-weight: 700;
    color: #9ca3af;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    white-space: nowrap;
}

/* ── Content cards ────────────────────────────────────────── */
.content-card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 16px;
}

/* ── Empty state ──────────────────────────────────────────── */
.empty-state {
    text-align: center;
    padding: 64px 32px;
    background: #ffffff;
    border: 1.5px dashed #d1d5db;
    border-radius: 14px;
    margin-top: 24px;
}

.empty-icon {
    font-size: 40px;
    margin-bottom: 14px;
    opacity: 0.4;
}

.empty-title {
    font-size: 15px;
    font-weight: 600;
    color: #374151;
    margin-bottom: 6px;
}

.empty-sub {
    font-size: 13px;
    color: #9ca3af;
    max-width: 340px;
    margin: 0 auto;
    line-height: 1.6;
}

/* ── Streamlit component overrides ───────────────────────── */
[data-testid="stFileUploader"] {
    border: 1.5px dashed #e5e7eb !important;
    border-radius: 8px !important;
    background: #fafafa !important;
}

[data-testid="stFileUploader"]:hover {
    border-color: #93c5fd !important;
    background: #eff6ff !important;
}

.stButton > button[kind="primary"] {
    background: #1a6ef7 !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    letter-spacing: 0.02em !important;
    padding: 0.55rem 1.5rem !important;
    transition: background 0.15s, transform 0.1s !important;
}
.stButton > button[kind="primary"]:hover {
    background: #1558d6 !important;
    transform: translateY(-1px) !important;
}

.stButton > button:not([kind="primary"]) {
    background: transparent !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 8px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    color: #374151 !important;
}
.stButton > button:not([kind="primary"]):hover {
    background: #f9fafb !important;
    border-color: #d1d5db !important;
}

[data-testid="stMetric"] {
    background: #ffffff !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 10px !important;
    padding: 14px 18px !important;
}
[data-testid="stMetricLabel"] > div {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    color: #9ca3af !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
}
[data-testid="stMetricValue"] > div {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 20px !important;
    font-weight: 700 !important;
    color: #111827 !important;
}

[data-testid="stDataFrame"] {
    border: 1px solid #e5e7eb !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}

[data-testid="stAlert"] {
    border-radius: 8px !important;
    font-size: 13px !important;
}

[data-testid="stStatusContainer"] {
    border-radius: 8px !important;
    font-size: 13px !important;
}

.stDownloadButton > button {
    background: #eff6ff !important;
    border: 1px solid #bfdbfe !important;
    border-radius: 8px !important;
    color: #1d4ed8 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 13px !important;
    font-weight: 600 !important;
}
.stDownloadButton > button:hover {
    background: #dbeafe !important;
}

[data-testid="stTextInput"] input {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 13px !important;
    border-radius: 7px !important;
}

[data-testid="stSelectbox"] > div > div {
    border-radius: 7px !important;
    font-size: 13px !important;
}

[data-testid="stExpander"] {
    border: 1px solid #e5e7eb !important;
    border-radius: 10px !important;
}

details summary {
    font-size: 13px !important;
    font-weight: 500 !important;
    color: #374151 !important;
}

.stTabs [data-testid="stMarkdownContainer"] p { font-size: 13px !important; }

[data-testid="stCaptionContainer"] p {
    font-size: 11px !important;
    color: #9ca3af !important;
}

h2 { font-size: 15px !important; font-weight: 700 !important; color: #111827 !important; }
h3 { font-size: 14px !important; font-weight: 600 !important; color: #374151 !important; }

/* Checkbox override */
[data-testid="stCheckbox"] label {
    font-size: 13px !important;
    font-weight: 500 !important;
    color: #374151 !important;
}

/* Date input */
[data-testid="stDateInput"] input {
    font-size: 13px !important;
    border-radius: 7px !important;
}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# SESSION STATE INIT
# ═══════════════════════════════════════════════════════════════
defaults = {
    "page":          "home",
    "mrp_results":   None,
    "seg_results":   None,
    "aging_results": None,
    "seg_imp_bytes": None,
    # config
    "cfg_phantom":  "50",
    "cfg_vl1":      "0010748460",
    "cfg_vl2":      "0010748458",
    "cfg_vl3":      "0010748814",
    "cfg_vl4":      "0010300601DEL",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

PHANTOM   = st.session_state["cfg_phantom"]
VERIFY_L1 = st.session_state["cfg_vl1"]
VERIFY_L2 = st.session_state["cfg_vl2"]
VERIFY_L3 = st.session_state["cfg_vl3"]
VERIFY_L4 = st.session_state["cfg_vl4"]


# ═══════════════════════════════════════════════════════════════
# NAV STATE HELPERS
# ═══════════════════════════════════════════════════════════════
def go(page):
    st.session_state["page"] = page
    st.rerun()

def nav_btn(label, icon, page_key, badge=None, badge_type=""):
    active = st.session_state["page"] == page_key
    badge_html = ""
    if badge:
        badge_html = f'<span class="nav-badge {badge_type}">{badge}</span>'
    active_cls = "active" if active else ""
    clicked = st.button(
        f"{icon}  {label}",
        key=f"nav_{page_key}",
        use_container_width=True,
    )
    if clicked:
        go(page_key)


def section_header(text):
    st.markdown(f"""
    <div class="section-header">
        <div class="section-header-line"></div>
        <div class="section-header-text">{text}</div>
        <div class="section-header-line"></div>
    </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# TOPBAR STATUS CHIPS
# ═══════════════════════════════════════════════════════════════
def topbar(title, subtitle=""):
    mrp_done  = st.session_state["mrp_results"]  is not None
    seg_done  = st.session_state["seg_results"]  is not None
    aging_done = st.session_state["aging_results"] is not None

    chips = ""
    if mrp_done:
        chips += '<span class="status-chip done"><span class="status-dot"></span>MRP done</span>'
    if seg_done:
        chips += '<span class="status-chip done"><span class="status-dot"></span>Segment done</span>'
    if aging_done:
        chips += '<span class="status-chip done"><span class="status-dot"></span>Aging done</span>'
    if not mrp_done:
        chips += '<span class="status-chip idle"><span class="status-dot"></span>Awaiting files</span>'

    st.markdown(f"""
    <div class="topbar">
        <div>
            <div class="topbar-title">{title}</div>
            <div class="topbar-subtitle">{subtitle}</div>
        </div>
        <div class="topbar-right">{chips}</div>
    </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# SHARED HELPERS
# ═══════════════════════════════════════════════════════════════
MONTH_ABBR = {
    "jan":1,"feb":2,"mar":3,"apr":4,"may":5,"jun":6,
    "jul":7,"aug":8,"sep":9,"oct":10,"nov":11,"dec":12
}

def parse_col_to_date(col, default_year=2026):
    if isinstance(col, pd.Timestamp):
        return col.replace(day=1), col.strftime("%d-%b-%y")
    if hasattr(col, "year") and hasattr(col, "month"):
        ts = pd.Timestamp(col)
        return ts.replace(day=1), ts.strftime("%d-%b-%y")
    if pd.isna(col): return None, None
    s = str(col).strip()
    if not s: return None, None
    m = re.match(r'^(\d{1,2})[/\-]([A-Za-z]{3})(?:[/\-](\d{2,4}))?$', s)
    if m:
        day_s, mon_s, yr_s = m.group(1), m.group(2).lower(), m.group(3)
        mon_num = MONTH_ABBR.get(mon_s)
        if mon_num and 1 <= int(day_s) <= 31:
            yr = int(yr_s)+(2000 if yr_s and len(yr_s)==2 else 0) if yr_s else default_year
            try:
                ts = pd.Timestamp(year=yr, month=mon_num, day=int(day_s))
                return ts, s
            except: pass
    m = re.match(r'^([A-Za-z]{3})[-\'\s_](\d{2,4})$', s)
    if m:
        mon_s, yr_s = m.group(1).lower(), m.group(2)
        mon_num = MONTH_ABBR.get(mon_s)
        if mon_num:
            yr = int(yr_s)+(2000 if len(yr_s)==2 else 0)
            ts = pd.Timestamp(year=yr, month=mon_num, day=1)
            return ts, s
    try:
        ts = pd.to_datetime(s, dayfirst=True, errors="raise")
        return ts, s
    except: pass
    return None, None

def infer_year_from_parsed(parsed_list):
    years = [p["ts"].year for p in parsed_list if p["ts"] is not None]
    return max(set(years), key=years.count) if years else 2026

def parse_all_month_cols(req_cols, non_month_set):
    candidates = [c for c in req_cols if c not in non_month_set]
    parsed = []
    for col in candidates:
        ts, label = parse_col_to_date(col)
        if ts is not None:
            parsed.append({"orig": col, "ts": ts, "label": label})
    ref_year = infer_year_from_parsed(parsed)
    if ref_year != 2026:
        parsed = []
        for col in candidates:
            ts, label = parse_col_to_date(col, default_year=ref_year)
            if ts is not None:
                parsed.append({"orig": col, "ts": ts, "label": label})
    parsed.sort(key=lambda x: x["ts"])
    seen_ts, unique = set(), []
    for p in parsed:
        if p["ts"] not in seen_ts:
            seen_ts.add(p["ts"])
            unique.append(p)
    return unique

def standardize_req_header(v):
    if pd.isna(v): return ""
    s = str(v).strip()
    return {"alt.":"Alt","alternative":"Alt","bom header":"BOM Header"}.get(s.lower(), s)

def detect_requirement_header_row(file_obj, sheet_name="Requirement", scan_rows=20):
    raw = pd.read_excel(file_obj, sheet_name=sheet_name, header=None, nrows=scan_rows)
    best_row, best_score = 0, -1
    for i in range(len(raw)):
        cleaned = [standardize_req_header(x) for x in raw.iloc[i].tolist()]
        score = (10 if "BOM Header" in cleaned else 0) + \
                (5  if "Alt" in cleaned else 0) + \
                sum(1 for x in cleaned if parse_col_to_date(x)[0] is not None)
        if score > best_score:
            best_score, best_row = score, i
    if best_score < 10:
        raise ValueError("Could not detect Requirement header row.")
    return best_row

def safe_series(df_or_series, col):
    result = df_or_series[col]
    return result.iloc[:, 0] if isinstance(result, pd.DataFrame) else result

def is_phantom(val):
    return str(val).strip() == PHANTOM

def empty_prod_summary():
    return pd.DataFrame(columns=["Component","Confirmed_Qty","Open_Production_Qty"])

def load_receipt_qty(receipt_file):
    if receipt_file is None:
        return pd.Series(dtype=float)
    try:
        df = pd.read_excel(receipt_file)
        df.columns = df.columns.str.strip()
        mat_kw = ["material","component","part number","part","mat"]
        qty_kw = ["gr qty","gr quantity","receipt qty","receipt quantity","received qty","quantity","qty"]
        mat_col = next((c for c in df.columns if any(k in c.lower() for k in mat_kw)), df.columns[0])
        qty_col = next((c for c in df.columns if any(k in c.lower() for k in qty_kw) and c != mat_col), None)
        if qty_col is None:
            st.warning("Receipt file: quantity column not detected — skipped.")
            return pd.Series(dtype=float)
        df[mat_col] = df[mat_col].astype(str).str.strip()
        df[qty_col] = pd.to_numeric(df[qty_col].astype(str).str.replace(",","",regex=False).str.strip(), errors="coerce").fillna(0)
        result = df.groupby(mat_col)[qty_col].sum()
        st.success(f"✓ Receipt file: {len(result):,} components loaded.")
        return result
    except Exception as e:
        st.warning(f"Receipt file error ({e}) — skipped.")
        return pd.Series(dtype=float)


# ═══════════════════════════════════════════════════════════════
# SEARCH + TREE
# ═══════════════════════════════════════════════════════════════
def get_ancestry_paths(component, bom):
    comp_rows = bom[bom["Component"] == component][
        ["BOM Header","Alt","Level","Parent","Component","Required Qty","Component descriptio","Special procurement"]
    ].drop_duplicates()
    paths = []
    for _, row in comp_rows.iterrows():
        path_comps = [row["Component"]]
        path_descs = [row["Component descriptio"]]
        path_qtys  = [float(row["Required Qty"])]
        path_sp    = [str(row["Special procurement"]).strip()]
        current, fg, alt = row["Parent"], row["BOM Header"], row["Alt"]
        for _ in range(4):
            if current == fg: break
            pr_rows = bom[(bom["BOM Header"]==fg)&(bom["Alt"]==alt)&(bom["Component"]==current)]
            if pr_rows.empty: break
            pr = pr_rows.iloc[0]
            path_comps.insert(0, pr["Component"]); path_descs.insert(0, pr["Component descriptio"])
            path_qtys.insert(0, float(pr["Required Qty"])); path_sp.insert(0, str(pr["Special procurement"]).strip())
            current = pr["Parent"]
        paths.append({"fg":fg,"alt":str(alt),"level":int(row["Level"]),"path_comps":path_comps,
                      "path_descs":path_descs,"path_qtys":path_qtys,"path_sp":path_sp})
    return paths

def build_dot_tree(component, paths, req_df, months, stock, prod_summary):
    fg_demand = {}
    for p in paths:
        rows = req_df[(req_df["BOM Header"]==p["fg"])&(req_df["Alt"]==p["alt"])]
        fg_demand[(p["fg"],p["alt"])] = float(rows[months].sum(numeric_only=True).sum()) if not rows.empty else 0
    result_dfs = st.session_state.get("mrp_results", {})
    gross_map, shortage_map = {}, {}
    for key in ["result_l1","result_l2","result_l3","result_l4"]:
        df = result_dfs.get(key)
        if df is None or df.empty: continue
        agg = df.groupby("Component")[["Gross_Requirement","Shortage"]].sum()
        for comp, row in agg.iterrows():
            gross_map[comp] = gross_map.get(comp,0)+row["Gross_Requirement"]
            shortage_map[comp] = shortage_map.get(comp,0)+row["Shortage"]
    def trunc(s, n=20): return (str(s)[:n]+"…") if len(str(s))>n else str(s)
    node_attrs, edges, seen_edges = {}, [], set()
    for path in paths:
        fg, alt = path["fg"], path["alt"]
        fg_id = f"FG_{fg}_A{alt}".replace("-","_").replace(".","_")
        node_attrs[fg_id] = (f'label="FG: {fg}\\nAlt: {alt}\\nDemand: {fg_demand.get((fg,alt),0):,.0f}"'
                             f' shape=box style="filled,rounded" fillcolor="#0d1b2a" fontcolor="#e2e8f0" fontsize=11')
        prev_id = fg_id
        for comp, desc, qty, sp in zip(path["path_comps"],path["path_descs"],path["path_qtys"],path["path_sp"]):
            is_tgt = (comp == component); is_ph = (sp == PHANTOM)
            nid = f"N_{comp}_FG_{fg}_A{alt}".replace("-","_").replace(".","_").replace("+","p")
            gross = gross_map.get(comp,0); shortage = shortage_map.get(comp,0); stk = float(stock.get(comp,0))
            if is_tgt:
                prod_row = prod_summary[prod_summary["Component"]==comp]
                conf  = float(prod_row["Confirmed_Qty"].iloc[0]) if not prod_row.empty else 0
                oprod = float(prod_row["Open_Production_Qty"].iloc[0]) if not prod_row.empty else 0
                label = (f"{trunc(comp)}\\n{trunc(desc)}\\nStock: {stk:,.0f} | Conf: {conf:,.0f}\\n"
                         f"Open: {oprod:,.0f} | Short: {shortage:,.0f}")
                node_attrs[nid] = (f'label="{label}" shape=box style="filled,rounded"'
                                   f' fillcolor="#166534" fontcolor="#dcfce7" fontsize=11 penwidth=2.5')
            elif is_ph:
                label = f"PHANTOM\\n{trunc(comp)}\\n{trunc(desc)}\\n×{qty:g}"
                node_attrs[nid] = (f'label="{label}" shape=box style="filled,dashed"'
                                   f' fillcolor="#78350f" fontcolor="#fef3c7" fontsize=10')
            else:
                label = (f"{trunc(comp)}\\n{trunc(desc)}\\nQty: {qty:g} | Stk: {stk:,.0f}\\n"
                         f"Short: {shortage:,.0f}")
                node_attrs[nid] = (f'label="{label}" shape=box style="filled,rounded"'
                                   f' fillcolor="#f8fafc" fontcolor="#1e293b" fontsize=10')
            ek = (prev_id, nid)
            if ek not in seen_edges:
                edges.append((prev_id, nid, f"×{qty:g}"))
                seen_edges.add(ek)
            prev_id = nid
    lines = ['digraph MRP { rankdir=TB;',
             '  node [fontname="Plus Jakarta Sans"];',
             '  edge [fontname="Plus Jakarta Sans" fontsize=10];',
             '  graph [splines=ortho nodesep=0.6 ranksep=0.9 bgcolor=transparent];']
    for nid, attrs in node_attrs.items():
        lines.append(f'  "{nid}" [{attrs}];')
    for src, dst, lbl in edges:
        lines.append(f'  "{src}" -> "{dst}" [label="{lbl}" color="#94a3b8"];')
    lines.append("}")
    return "\n".join(lines)

def show_search_section(bom, req_df, months, stock, prod_summary):
    section_header("Component Search & BOM Ancestry")
    st.caption("Search any component code to view demand breakdown, shortage analysis, and BOM ancestry tree.")
    sc, _ = st.columns([2, 3])
    with sc:
        comp = st.text_input("Component code", placeholder="e.g. 0010748458", label_visibility="collapsed", key="comp_search").strip()
    if not comp: return
    r = st.session_state.get("mrp_results", {})
    found_in = {}
    for lbl in ["result_l1","result_l2","result_l3","result_l4"]:
        df = r.get(lbl)
        if df is not None and not df.empty and comp in df["Component"].values:
            found_in[lbl] = df[df["Component"]==comp].copy()
    bom_in = bom[bom["Component"]==comp]
    if bom_in.empty and not found_in:
        st.warning(f"`{comp}` not found in BOM or MRP results.")
        return
    desc  = bom_in["Component descriptio"].iloc[0] if not bom_in.empty else "—"
    ptype = bom_in["Procurement type"].iloc[0]     if not bom_in.empty else "—"
    sp    = bom_in["Special procurement"].iloc[0]  if not bom_in.empty else "—"
    stk   = float(stock.get(comp, 0))
    prod_row = prod_summary[prod_summary["Component"]==comp]
    conf_qty = float(prod_row["Confirmed_Qty"].iloc[0]) if not prod_row.empty else 0
    open_qty = float(prod_row["Open_Production_Qty"].iloc[0]) if not prod_row.empty else 0
    ph_badge = " · 🔶 PHANTOM" if str(sp).strip()==PHANTOM else ""
    st.markdown(f"**`{comp}`** — {desc}{ph_badge}")
    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Stock on hand", f"{stk:,.3f}")
    c2.metric("Confirmed prod", f"{conf_qty:,.0f}")
    c3.metric("Open prod qty",  f"{open_qty:,.0f}")
    c4.metric("Proc. type",     ptype)
    c5.metric("Sp. proc.",      sp if sp not in ("","nan") else "—")
    if found_in:
        all_rows = pd.concat(found_in.values(), ignore_index=True)
        mo = {m:i for i,m in enumerate(months)}
        monthly = (all_rows.groupby("Month",as_index=False)
                   .agg(Gross_Requirement=("Gross_Requirement","sum"),Stock_Used=("Stock_Used","sum"),
                        Shortage=("Shortage","sum"),Stock_Remaining=("Stock_Remaining","last")))
        monthly["_ord"] = monthly["Month"].map(mo)
        monthly = monthly.sort_values("_ord").drop(columns="_ord")
        monthly["Cumul_Gross"]  = monthly["Gross_Requirement"].cumsum()
        monthly["Net_Position"] = stk - monthly["Cumul_Gross"]
        def hl(row):
            if row["Net_Position"] < 0: return ["background-color:#fff0f0"]*len(row)
            elif row["Net_Position"] > 0: return ["background-color:#f0fdf4"]*len(row)
            return [""]*len(row)
        st.dataframe(
            monthly[["Month","Gross_Requirement","Stock_Used","Stock_Remaining","Net_Position"]]
            .style.apply(hl,axis=1).format({c:"{:,.2f}" for c in ["Gross_Requirement","Stock_Used","Stock_Remaining","Net_Position"]}),
            use_container_width=True, hide_index=True)
        s1,s2,s3,s4 = st.columns(4)
        final_net = monthly["Net_Position"].iloc[-1]
        s1.metric("Total gross req",   f"{monthly['Gross_Requirement'].sum():,.2f}")
        s2.metric("Opening stock",     f"{stk:,.2f}")
        s3.metric("Final net position",f"{final_net:,.2f}",
                  delta="surplus" if final_net>=0 else "shortage",
                  delta_color="normal" if final_net>=0 else "inverse")
        s4.metric("Months in shortage",f"{(monthly['Net_Position']<0).sum()} / {len(monthly)}")
    else:
        st.info("Component found in BOM but not in MRP results (phantom or no demand).")
    paths = get_ancestry_paths(comp, bom)
    if not paths:
        st.info("No ancestry paths found."); return
    desc_map = {}
    if "BOM header descripti" in bom.columns:
        desc_map = (bom[["BOM Header","BOM header descripti"]].drop_duplicates("BOM Header")
                    .set_index("BOM Header")["BOM header descripti"].to_dict())
    fg_rows = []
    for p in paths:
        rows = req_df[(req_df["BOM Header"]==p["fg"])&(req_df["Alt"]==p["alt"])]
        total = rows[months].sum(numeric_only=True).sum() if not rows.empty else 0
        mv = {m: float(rows[m].sum()) if not rows.empty else 0 for m in months}
        fg_rows.append({"FG code":p["fg"],"Description":desc_map.get(p["fg"],"—"),"Alt":p["alt"],
                        "BOM level":p["level"],"Total demand":f"{total:,.0f}",
                        **{m:f"{mv[m]:,.0f}" for m in months}})
    st.dataframe(pd.DataFrame(fg_rows).drop_duplicates(subset=["FG code","Alt"]),
                 use_container_width=True, hide_index=True)
    MAX_PATHS = 12
    display_paths = paths[:MAX_PATHS]
    if len(paths) > MAX_PATHS:
        st.caption(f"⚠ Showing {MAX_PATHS} of {len(paths)} ancestry paths.")
    dot = build_dot_tree(comp, display_paths, req_df, months, stock, prod_summary)
    try:
        st.graphviz_chart(dot, use_container_width=True)
    except Exception as e:
        st.error(f"Tree render error: {e}")


# ═══════════════════════════════════════════════════════════════
# MRP ENGINE
# ═══════════════════════════════════════════════════════════════
def run_mrp(bom_file, req_file, prod_file, receipt_file):
    logs = []
    log  = lambda msg: logs.append(msg)
    status = st.status("Running MRP engine ...", expanded=True)

    with status: st.write("► Building clean BOM ...")
    bom = pd.read_excel(bom_file)
    bom.columns = bom.columns.str.strip()
    if "Alt." in bom.columns: bom = bom.rename(columns={"Alt.":"Alt"})
    bom["Level"] = pd.to_numeric(bom["Level"],errors="coerce").fillna(0).astype(int)
    bom = bom.reset_index(drop=True)
    parents, stack = [], {}
    for i in range(len(bom)):
        lvl = bom.loc[i,"Level"]
        parent = bom.loc[i,"BOM Header"] if lvl==1 else stack.get(lvl-1)
        stack = {k:v for k,v in stack.items() if k<=lvl}
        stack[lvl] = bom.loc[i,"Component"]
        parents.append(parent)
    bom["Parent"] = parents
    drop_cols = ["Plant","Usage","Quantity","Unit","BOM L/T","BOM code","Item",
                 "Mat. Group","Mat. Group Desc.","Pur. Group","Pur. Group Desc.","MRP Controller","MRP Controller Desc."]
    bom = bom.drop(columns=[c for c in drop_cols if c in bom.columns],errors="ignore")
    for old,new in [("Component description","Component descriptio"),("BOM header description","BOM header descripti")]:
        if old in bom.columns: bom = bom.rename(columns={old:new})
    keep = ["BOM Header","BOM header descripti","Alt","Level","Path","Parent","Component","Component descriptio",
            "Required Qty","Base unit","Procurement type","Special procurement"]
    missing_bom = [c for c in ["BOM Header","Level","Component","Required Qty"] if c not in bom.columns]
    if missing_bom: st.error(f"Missing BOM columns: {missing_bom}"); return None
    bom = bom[[c for c in keep if c in bom.columns]].copy()
    for col,default in [("Alt","0"),("Special procurement",""),("Procurement type",""),("Component descriptio","")]:
        if col not in bom.columns: bom[col] = default
    bom["Component"]            = bom["Component"].astype(str).str.strip()
    bom["BOM Header"]           = bom["BOM Header"].astype(str).str.strip()
    bom["Special procurement"]  = bom["Special procurement"].astype(str).str.strip()
    bom["Procurement type"]     = bom["Procurement type"].astype(str).str.strip()
    bom["Component descriptio"] = bom["Component descriptio"].astype(str).str.strip()
    bom["Required Qty"]         = pd.to_numeric(bom["Required Qty"],errors="coerce").fillna(0)
    bom["Alt"] = pd.to_numeric(bom["Alt"],errors="coerce").fillna(0).astype(int).astype(str)
    log(f"BOM rows: {len(bom):,} | Unique headers: {bom['BOM Header'].nunique()}")

    with status: st.write("► Loading Requirement and Stock ...")
    req_header_row = detect_requirement_header_row(req_file, sheet_name="Requirement")
    req_file.seek(0)
    req = pd.read_excel(req_file, sheet_name="Requirement", header=None)
    raw_headers = req.iloc[req_header_row].tolist()
    req.columns = [standardize_req_header(x) for x in raw_headers]
    req = req.iloc[req_header_row+1:].reset_index(drop=True)
    req = req.loc[:,[str(c).strip()!="" for c in req.columns]]
    req = req.loc[:,~pd.Index(req.columns).duplicated(keep="first")]
    missing_req = [c for c in ["BOM Header","Alt"] if c not in req.columns]
    if missing_req: st.error(f"Missing Req columns: {missing_req}"); return None
    req["BOM Header"] = req["BOM Header"].astype(str).str.strip()
    req["Alt"] = pd.to_numeric(req["Alt"],errors="coerce").fillna(0).astype(int).astype(str)
    parsed = parse_all_month_cols(req.columns.tolist(),{"BOM Header","Alt"})
    if not parsed: st.error("No date/month columns detected."); return None
    rename_map = {p["orig"]:p["label"] for p in parsed if p["orig"]!=p["label"]}
    if rename_map: req = req.rename(columns=rename_map)
    months      = [p["label"] for p in parsed]
    MONTH_ORDER = {m:i for i,m in enumerate(months)}
    for m in months:
        col_data = safe_series(req, m)
        req[m] = pd.to_numeric(col_data.astype(str).str.replace(",","",regex=False).str.strip(),errors="coerce").fillna(0)
    log(f"Months ({len(months)}): {months}")
    req_file.seek(0)
    stock_raw = pd.read_excel(req_file,sheet_name="Stock",usecols=[0,1],header=0,names=["Component","Stock_Qty"])
    stock_raw = stock_raw.dropna(subset=["Component"]).copy()
    stock_raw["Component"] = stock_raw["Component"].astype(str).str.strip()
    stock_raw["Stock_Qty"] = pd.to_numeric(stock_raw["Stock_Qty"].astype(str).str.replace(",","",regex=False).str.strip(),errors="coerce").fillna(0)
    stock = stock_raw.groupby("Component")["Stock_Qty"].sum()
    receipt_qty = load_receipt_qty(receipt_file)
    receipt_added = 0
    if not receipt_qty.empty:
        for comp, qty in receipt_qty.items():
            stock[comp] = float(stock.get(comp,0)) + float(qty)
            receipt_added += 1
        log(f"Receipt: {receipt_added} components updated")
    req_long = req.melt(id_vars=["BOM Header","Alt"],value_vars=months,var_name="Month",value_name="FG_Demand")
    req_long = req_long[req_long["FG_Demand"]>0].copy()

    with status: st.write("► Loading Production Orders ...")
    prod_summary = empty_prod_summary()
    if prod_file is not None:
        try:
            coois = pd.read_excel(prod_file)
            coois.columns = coois.columns.str.strip()
            if not coois.empty:
                status_col = next((c for c in coois.columns if "status" in c.lower()),None)
                mat_col    = next((c for c in coois.columns if "material" in c.lower() and "description" not in c.lower()),None)
                ord_col    = next((c for c in coois.columns if "order" in c.lower() and ("qty" in c.lower() or "quantity" in c.lower())),None)
                del_col    = next((c for c in coois.columns if "deliver" in c.lower() or ("quantity" in c.lower() and "gr" in c.lower())),None)
                conf_col   = next((c for c in coois.columns if "confirm" in c.lower() and "quantity" in c.lower()),None)
                if all([status_col,mat_col,ord_col,del_col,conf_col]):
                    coois = coois[~coois[status_col].astype(str).str.contains("TECO",case=False,na=False)].copy()
                    coois[mat_col]  = coois[mat_col].astype(str).str.strip()
                    coois[ord_col]  = pd.to_numeric(coois[ord_col],errors="coerce").fillna(0)
                    coois[del_col]  = pd.to_numeric(coois[del_col],errors="coerce").fillna(0)
                    coois[conf_col] = pd.to_numeric(coois[conf_col],errors="coerce").fillna(0)
                    coois["Open_Qty"] = (coois[ord_col]-coois[del_col]).clip(lower=0)
                    prod_summary = (coois.groupby(mat_col,as_index=False)
                                    .agg(Confirmed_Qty=(conf_col,"sum"),Open_Production_Qty=("Open_Qty","sum"))
                                    .rename(columns={mat_col:"Component"}))
                    prod_summary["Component"] = prod_summary["Component"].astype(str).str.strip()
                    log(f"Prod orders (non-TECO): {len(coois):,}")
        except Exception as e:
            log(f"Prod order error ({e})")

    def get_sfrac(rows, comp_col, gross_col):
        agg = rows.groupby([comp_col,"Month","Month_Order"],as_index=False)[gross_col].sum()
        sfrac = {}
        for comp, grp in agg.groupby(comp_col):
            avail = float(stock.get(comp,0))
            for _, row in grp.sort_values("Month_Order").iterrows():
                g = float(row[gross_col])
                sfrac[(comp,row["Month"])] = max(0.0,g-avail)/g if g>0 else 0.0
                avail = max(0.0, avail-g)
        return sfrac

    def make_report(gross_agg_df, comp_col):
        BASE = ["Component","Description","Month","Gross_Requirement","Stock_Used","Shortage","Stock_Remaining"]
        if gross_agg_df.empty: return pd.DataFrame(columns=BASE)
        results = []
        for comp, grp in gross_agg_df.groupby(comp_col):
            avail = float(stock.get(comp,0)); desc = grp["Desc"].iloc[0]
            for _, row in grp.sort_values("Month_Order").iterrows():
                gr = float(row["Gross"]); consumed = min(avail,gr); shortage = max(0.0,gr-avail); avail = max(0.0,avail-gr)
                results.append({"Component":comp,"Description":desc,"Month":row["Month"],"Gross_Requirement":gr,
                                 "Stock_Used":consumed,"Shortage":shortage,"Stock_Remaining":avail})
        return pd.DataFrame(results,columns=BASE)

    def apply_sfrac(df, gross_col, ph_col, sfrac_dict, comp_col):
        return df.apply(lambda r: r[gross_col] if is_phantom(r[ph_col]) else r[gross_col]*sfrac_dict.get((r[comp_col],r["Month"]),1.0),axis=1)

    with status: st.write("► Running L1–L4 explosion ...")

    bom_l1 = (bom[bom["Level"]==1][["BOM Header","Alt","Component","Component descriptio","Required Qty","Special procurement"]].copy()
              .rename(columns={"Component":"L1_Comp","Component descriptio":"L1_Desc","Required Qty":"L1_Qty","Special procurement":"L1_Ph"}))
    l1 = req_long.merge(bom_l1,on=["BOM Header","Alt"],how="inner")
    l1["L1_Gross"] = l1["FG_Demand"]*l1["L1_Qty"]
    l1["Month_Order"] = l1["Month"].map(MONTH_ORDER)
    l1_norm = l1[~l1["L1_Ph"].apply(is_phantom)].copy()
    l1_sfrac = get_sfrac(l1_norm,"L1_Comp","L1_Gross")
    l1["L1_Eff"] = apply_sfrac(l1,"L1_Gross","L1_Ph",l1_sfrac,"L1_Comp")
    l1_agg = (l1_norm.groupby(["L1_Comp","L1_Desc","Month","Month_Order"],as_index=False)["L1_Gross"].sum()
              .rename(columns={"L1_Comp":"Component","L1_Desc":"Desc","L1_Gross":"Gross"}))
    result_l1 = make_report(l1_agg,"Component")

    bom_l2 = (bom[bom["Level"]==2][["BOM Header","Alt","Parent","Component","Component descriptio","Required Qty","Special procurement"]].copy()
              .rename(columns={"Parent":"L1_Comp","Component":"L2_Comp","Component descriptio":"L2_Desc","Required Qty":"L2_Qty","Special procurement":"L2_Ph"}))
    l2 = l1.merge(bom_l2,on=["BOM Header","Alt","L1_Comp"],how="inner")
    l2["L2_Gross"] = l2["L1_Eff"]*l2["L2_Qty"]
    l2_norm = l2[~l2["L2_Ph"].apply(is_phantom)].copy()
    l2_sfrac = get_sfrac(l2_norm,"L2_Comp","L2_Gross")
    l2["L2_Eff"] = apply_sfrac(l2,"L2_Gross","L2_Ph",l2_sfrac,"L2_Comp")
    l2_agg = (l2_norm.groupby(["L2_Comp","L2_Desc","Month","Month_Order"],as_index=False)["L2_Gross"].sum()
              .rename(columns={"L2_Comp":"Component","L2_Desc":"Desc","L2_Gross":"Gross"}))
    result_l2 = make_report(l2_agg,"Component")

    bom_l3 = (bom[bom["Level"]==3][["BOM Header","Alt","Parent","Component","Component descriptio","Required Qty","Special procurement"]].copy()
              .rename(columns={"Parent":"L2_Comp","Component":"L3_Comp","Component descriptio":"L3_Desc","Required Qty":"L3_Qty","Special procurement":"L3_Ph"}))
    l3 = l2.merge(bom_l3,on=["BOM Header","Alt","L2_Comp"],how="inner")
    l3["L3_Gross"] = l3.apply(lambda r: r["L2_Eff"] if is_phantom(r["L3_Ph"]) else r["L2_Eff"]*r["L3_Qty"],axis=1)
    l3_norm = l3[~l3["L3_Ph"].apply(is_phantom)].copy()
    l3_sfrac = get_sfrac(l3_norm,"L3_Comp","L3_Gross")
    l3["L3_Eff"] = apply_sfrac(l3,"L3_Gross","L3_Ph",l3_sfrac,"L3_Comp")
    l3_agg = (l3_norm.groupby(["L3_Comp","L3_Desc","Month","Month_Order"],as_index=False)["L3_Gross"].sum()
              .rename(columns={"L3_Comp":"Component","L3_Desc":"Desc","L3_Gross":"Gross"}))
    result_l3 = make_report(l3_agg,"Component")

    bom_l4 = (bom[bom["Level"]==4][["BOM Header","Alt","Parent","Component","Component descriptio","Required Qty","Special procurement"]].copy()
              .rename(columns={"Parent":"L3_Comp","Component":"L4_Comp","Component descriptio":"L4_Desc","Required Qty":"L4_Qty","Special procurement":"L4_Ph"}))
    l4 = l3.merge(bom_l4,on=["BOM Header","Alt","L3_Comp"],how="inner")
    l4["L4_Gross"] = l4["L3_Eff"]*l4["L4_Qty"]
    l4_agg = (l4.groupby(["L4_Comp","L4_Desc","Month","Month_Order"],as_index=False)["L4_Gross"].sum()
              .rename(columns={"L4_Comp":"Component","L4_Desc":"Desc","L4_Gross":"Gross"}))
    result_l4 = make_report(l4_agg,"Component")

    with status: st.write("► Building output ...")
    status.update(label="MRP complete ✅", state="complete", expanded=False)

    final_output = pd.concat([result_l1,result_l2,result_l3,result_l4],ignore_index=True)
    all_comps = final_output[["Component","Description"]].drop_duplicates(subset="Component").copy()
    pivot_gross = (final_output.pivot_table(index=["Component","Description"],columns="Month",
                  values="Gross_Requirement",aggfunc="sum",fill_value=0).reset_index())
    pivot = all_comps.merge(pivot_gross,on=["Component","Description"],how="left").fillna(0)
    month_cols = [m for m in months if m in pivot.columns]
    if month_cols: pivot[month_cols] = pivot[month_cols].cumsum(axis=1)
    bom_master = bom[["Component","Procurement type","Special procurement"]].drop_duplicates(subset="Component")
    stock_df   = stock.reset_index().rename(columns={"Stock_Qty":"Stock"})
    pivot = (pivot.merge(bom_master,on="Component",how="left")
                  .merge(stock_df,on="Component",how="left")
                  .merge(prod_summary,on="Component",how="left"))
    pivot["Procurement type"]    = pivot["Procurement type"].fillna("")
    pivot["Special procurement"] = pivot["Special procurement"].fillna("")
    pivot["Stock"]               = pivot["Stock"].fillna(0)
    pivot["Confirmed_Qty"]       = pivot["Confirmed_Qty"].fillna(0)
    pivot["Open_Production_Qty"] = pivot["Open_Production_Qty"].fillna(0)
    for m in month_cols: pivot[m] = pivot["Stock"] - pivot[m]
    if not receipt_qty.empty:
        rq_df = receipt_qty.reset_index(); rq_df.columns = ["Component","Receipt_Qty"]
        pivot = pivot.merge(rq_df,on="Component",how="left")
        pivot["Receipt_Qty"] = pivot["Receipt_Qty"].fillna(0)
        extra_cols = ["Receipt_Qty"]
    else:
        extra_cols = []
    pivot = pivot.rename(columns={"Description":"Component descri"})
    final_cols = (["Component","Component descri","Procurement type","Special procurement",
                   "Confirmed_Qty","Open_Production_Qty","Stock"]+extra_cols+month_cols)
    for c in final_cols:
        if c not in pivot.columns: pivot[c] = 0 if c in month_cols+["Confirmed_Qty","Open_Production_Qty","Stock","Receipt_Qty"] else ""
    pivot = pivot[final_cols].sort_values("Component").reset_index(drop=True)

    with st.expander("Run log"):
        for line in logs: st.text(line)

    return dict(bom=bom,req=req,months=months,stock=stock,prod_summary=prod_summary,
                result_l1=result_l1,result_l2=result_l2,result_l3=result_l3,result_l4=result_l4,
                raw_l1=l1_agg,raw_l2=l2_agg,raw_l3=l3_agg,raw_l4=l4_agg,
                receipt_qty=receipt_qty,pivot=pivot,month_cols=month_cols)


# ═══════════════════════════════════════════════════════════════
# SEGMENT CAPACITY
# ═══════════════════════════════════════════════════════════════
def load_segment_import(seg_imp_file):
    xl = pd.ExcelFile(seg_imp_file); sheets = xl.sheet_names
    imp_sheet = next((s for s in sheets if "import" in s.lower()),sheets[0])
    imp_df = pd.read_excel(seg_imp_file,sheet_name=imp_sheet,header=0)
    imp_df.columns = [str(c).strip() for c in imp_df.columns]
    comp_col = imp_df.columns[0]
    imp_df[comp_col] = imp_df[comp_col].astype(str).str.strip()
    rm_col = next((c for c in imp_df.columns if "rm" in c.lower() or "group" in c.lower()),None)
    if rm_col:
        imp_df[rm_col] = imp_df[rm_col].astype(str).str.strip()
        rm_map = dict(zip(imp_df[comp_col],imp_df[rm_col]))
    else: rm_map = {}
    import_parts = sorted(imp_df[comp_col].dropna().unique())
    seg_sheet = next((s for s in sheets if "seg" in s.lower()),sheets[min(1,len(sheets)-1)])
    seg_df = pd.read_excel(seg_imp_file,sheet_name=seg_sheet,header=0)
    seg_df.columns = [str(c).strip() for c in seg_df.columns]
    col_map = {seg_df.columns[0]:"Segment",seg_df.columns[1]:"FG_Code",seg_df.columns[2]:"IDU"}
    if len(seg_df.columns)>=4: col_map[seg_df.columns[3]]="Compatible_ODU"
    seg_df = seg_df.rename(columns=col_map)
    if "Compatible_ODU" not in seg_df.columns: seg_df["Compatible_ODU"]=""
    for c in ("Segment","FG_Code","IDU","Compatible_ODU"):
        seg_df[c] = seg_df[c].astype(str).str.strip()
    seg_df = seg_df[
        seg_df["Segment"].notna()&(seg_df["Segment"]!="")&(seg_df["Segment"]!="nan")&
        seg_df["FG_Code"].notna()&(seg_df["FG_Code"]!="")&(seg_df["FG_Code"]!="nan")&
        seg_df["IDU"].notna()&(seg_df["IDU"]!="")&(seg_df["IDU"]!="nan")
    ].copy().reset_index(drop=True)
    return import_parts,seg_df,rm_map

def explode_bom_for_seg(bom_header,bom_df,target_set,phantom=None):
    if phantom is None: phantom = PHANTOM
    alts = sorted(bom_df[bom_df["BOM Header"]==bom_header]["Alt"].unique())
    if not alts: return {}
    alt = alts[0]
    sub = bom_df[(bom_df["BOM Header"]==bom_header)&(bom_df["Alt"]==alt)]
    children_map = defaultdict(list)
    for _,r in sub.iterrows(): children_map[r["Parent"]].append(r)
    result = {}
    def dfs(node,accum,depth=0):
        if depth>12: return
        for r in children_map.get(node,[]):
            comp=r["Component"]; qty=float(r["Required Qty"]); sp=r["Special procurement"]
            eff=accum*(1.0 if sp==phantom else qty)
            if comp in target_set: result[comp]=result.get(comp,0)+eff
            dfs(comp,eff,depth+1)
    dfs(bom_header,1.0)
    return result

def run_segment_capacity(bom,stock,seg_imp_file,active_rm_groups=None):
    status = st.status("Running Segment Capacity ...",expanded=True)
    with status: st.write("► Loading data ...")
    import_parts,seg_df,rm_map = load_segment_import(seg_imp_file)
    all_rm_groups = sorted(set(rm_map.values())) if rm_map else []
    if active_rm_groups is None: active_rm_groups = all_rm_groups
    if rm_map and active_rm_groups:
        import_parts = [p for p in import_parts if rm_map.get(p,"Unknown") in active_rm_groups]
    target_set = set(import_parts); bom_headers = set(bom["BOM Header"].unique())
    desc_col = "BOM header descripti" if "BOM header descripti" in bom.columns else None
    desc_map = (bom[["BOM Header",desc_col]].drop_duplicates("BOM Header").set_index("BOM Header")[desc_col].to_dict()) if desc_col else {}
    with status: st.write("► Exploding IDU / ODU BOMs ...")
    idu_reqs={}; not_in_bom=[]
    for idu in seg_df["IDU"].unique():
        if idu in bom_headers: idu_reqs[idu]=explode_bom_for_seg(idu,bom,target_set)
        else: not_in_bom.append(f"IDU {idu}")
    odu_reqs={}
    for odu in seg_df["Compatible_ODU"].unique():
        if not odu or odu=="nan": continue
        if odu in bom_headers: odu_reqs[odu]=explode_bom_for_seg(odu,bom,target_set)
        else: not_in_bom.append(f"ODU {odu}")
    if not_in_bom: st.warning(f"Not in BOM: {', '.join(sorted(set(not_in_bom)))}")
    with status: st.write("► Building LP ...")
    fg_list=[]; fg_segment={}; fg_idu={}; fg_odu={}; fg_combined={}; skipped_segs=[]
    for _,row in seg_df.iterrows():
        fg=row["FG_Code"]; seg=row["Segment"]; idu=row["IDU"]; odu=row["Compatible_ODU"]
        if not odu or odu=="nan": skipped_segs.append(f"{fg}: no ODU"); continue
        idu_req=idu_reqs.get(idu,{}); odu_req=odu_reqs.get(odu,{})
        if not idu_req and not odu_req: skipped_segs.append(f"{fg}: no import parts"); continue
        all_parts=set(idu_req)|set(odu_req)
        combined={p:idu_req.get(p,0)+odu_req.get(p,0) for p in all_parts if idu_req.get(p,0)+odu_req.get(p,0)>0}
        fg_list.append(fg); fg_segment[fg]=seg; fg_idu[fg]=idu; fg_odu[fg]=odu; fg_combined[fg]=combined
    if not fg_list: st.error("No FG codes with valid BOM data."); return None
    with status: st.write(f"► LP: {len(fg_list)} FG codes ...")
    n_fg=len(fg_list); constrained_parts=[]; A_rows=[]; b_rows=[]
    for p in import_parts:
        row_vec=[fg_combined[fg].get(p,0) for fg in fg_list]
        if any(v>0 for v in row_vec):
            constrained_parts.append(p); A_rows.append(row_vec); b_rows.append(float(stock.get(p,0)))
    A=np.array(A_rows,dtype=float); b=np.array(b_rows,dtype=float); c=-np.ones(n_fg)
    res=linprog(c,A_ub=A,b_ub=b,bounds=[(0,None)]*n_fg,method="highs")
    if res.status not in (0,1): st.error(f"LP failed: {res.message}"); return None
    alloc_int=np.floor(res.x).astype(int); total_sets=int(alloc_int.sum())
    fg_results=[]
    for fg,qty in zip(fg_list,alloc_int):
        creq=fg_combined[fg]; lim_part="—"; lim_ratio=float("inf")
        for p,req in creq.items():
            if req>0:
                ratio=float(stock.get(p,0))/req
                if ratio<lim_ratio: lim_ratio,lim_part=ratio,p
        fg_results.append({"Segment":fg_segment[fg],"FG_Code":fg,"FG_Desc":desc_map.get(fg,""),
                            "IDU":fg_idu[fg],"IDU_Desc":desc_map.get(fg_idu[fg],""),
                            "Compatible_ODU":fg_odu[fg],"ODU_Desc":desc_map.get(fg_odu[fg],""),
                            "Max_Sets":int(qty),"Limiting_Part":lim_part,
                            "Limiting_Stock":int(stock.get(lim_part,0)) if lim_part!="—" else 0,
                            "combined_req":creq})
    seg_totals=defaultdict(int); seg_fg_map=defaultdict(list)
    for fgr in fg_results:
        seg_totals[fgr["Segment"]]+=fgr["Max_Sets"]; seg_fg_map[fgr["Segment"]].append(fgr)
    segments_data={}
    for seg,fgrs in seg_fg_map.items():
        idu_codes=list({f["IDU"] for f in fgrs}); odu_codes=list({f["Compatible_ODU"] for f in fgrs})
        all_parts=set(p for f in fgrs for p in f["combined_req"])
        combined={p:max(f["combined_req"].get(p,0) for f in fgrs) for p in all_parts}
        segments_data[seg]={"combined_req":combined,"idu_codes":idu_codes,"odu_codes":odu_codes,
                            "idu_count":len(idu_codes),"odu_count":len(odu_codes)}
    segs=list(segments_data.keys()); seg_alloc_arr=np.array([seg_totals[s] for s in segs],dtype=int)
    part_usage={}
    for p,row_vec,avail in zip(constrained_parts,A_rows,b_rows):
        used=sum(row_vec[j]*alloc_int[j] for j in range(n_fg))
        part_usage[p]={"stock":avail,"used":used,"remain":max(0,avail-used),
                       "pct":round(100*used/avail,1) if avail>0 else 0}
    with status: st.write("► Done.")
    status.update(label="Segment Capacity complete ✅",state="complete",expanded=False)
    return dict(segs=segs,alloc_int=seg_alloc_arr,total_sets=total_sets,segments_data=segments_data,
                fg_results=fg_results,import_parts=import_parts,constrained_parts=constrained_parts,
                part_usage=part_usage,stock=stock,skipped_segs=skipped_segs,rm_map=rm_map,
                active_rm_groups=active_rm_groups)


# ═══════════════════════════════════════════════════════════════
# AGING ENGINE
# ═══════════════════════════════════════════════════════════════
AGING_BUCKETS = ["0-15 Qty","16-30 Qty","31-60 Qty","61-90 Qty",
                 "91-120 Qty","121-150 Qty","151-180 Qty","181-360 Qty","Over361 Qty"]
AGING_VAL_BUCKETS = ["0-15 Value","16-30 Value","31-60 Value","61-90 Value",
                     "91-120 Value","121-150 Value","151-180 Value","181-360 Value","Over361 Value"]

def load_aging_data(aging_file):
    df=pd.read_excel(aging_file); df.columns=[str(c).strip() for c in df.columns]
    rename={}
    for c in df.columns:
        cl=c.lower().replace(" ","")
        if cl=="material": rename[c]="Material"
        elif "description" in cl: rename[c]="Material Description"
        elif cl=="materialtype": rename[c]="Material Type"
        elif "movingaverage" in cl or cl=="map": rename[c]="MAP"
    df=df.rename(columns=rename)
    for col in AGING_BUCKETS+AGING_VAL_BUCKETS:
        if col not in df.columns: df[col]=0.0
        df[col]=pd.to_numeric(df[col],errors="coerce").fillna(0)
    agg_cols={c:"sum" for c in AGING_BUCKETS+AGING_VAL_BUCKETS}
    if "Material Description" in df.columns: agg_cols["Material Description"]="first"
    if "MAP" in df.columns: agg_cols["MAP"]="first"
    if "Material Type" in df.columns: agg_cols["Material Type"]="first"
    return df.groupby("Material",as_index=False).agg(agg_cols)

def project_aging(aging_df,base_date,production_consumption,months_list):
    base_ts=pd.Timestamp(base_date)
    def month_offset(label):
        try: ts=pd.to_datetime(label,format="%b-%y")
        except:
            try: ts=pd.to_datetime(label); ts=ts.replace(day=1)
            except: return 0
        return (ts.year-base_ts.year)*12+(ts.month-base_ts.month)
    month_offsets=[max(0,month_offset(m)) for m in months_list]
    def aging_start_idx(offset): return max(0,4-offset)
    records=[]
    for _,row in aging_df.iterrows():
        mat=str(row["Material"]).strip(); desc=str(row.get("Material Description",""))
        mat_type=str(row.get("Material Type","")); map_px=float(row.get("MAP",0) or 0)
        buckets=[float(row.get(b,0) or 0) for b in AGING_BUCKETS]
        mat_cons=production_consumption.get(mat,{}); cum_consumption=0.0
        for m_idx,month_label in enumerate(months_list):
            offset=month_offsets[m_idx]; cum_consumption+=float(mat_cons.get(month_label,0))
            start_idx=aging_start_idx(offset); aging_pool=sum(buckets[start_idx:])
            fresh_pool=sum(buckets[:start_idx]); aging_consumed=max(0.0,cum_consumption-fresh_pool)
            aging_qty=max(0.0,aging_pool-aging_consumed); aging_val=round(aging_qty*map_px,2) if map_px>0 else 0.0
            turning_next=buckets[start_idx-1] if start_idx>0 else 0.0
            records.append({"Material":mat,"Description":desc,"Material Type":mat_type,"Month":month_label,
                            "Aging Pool Qty":round(aging_pool,2),"Cumulative Consumption":round(cum_consumption,2),
                            "Aging Qty (>=91d)":round(aging_qty,2),"Aging Value (Rs)":aging_val,
                            "Turning Aging Next Month":round(turning_next,2)})
    return pd.DataFrame(records)


# ═══════════════════════════════════════════════════════════════
# PAGE RENDERERS
# ═══════════════════════════════════════════════════════════════

def page_home():
    topbar("Dashboard", "SAP MRP Engine overview")
    st.markdown('<div class="page-content">', unsafe_allow_html=True)

    mrp_done  = st.session_state["mrp_results"] is not None
    seg_done  = st.session_state["seg_results"] is not None
    aging_done = st.session_state["aging_results"] is not None

    # Quick status grid
    steps = [
        ("📂", "Upload Files",       "Upload BOM, Req & Stock and optional files",    True,     "upload"),
        ("⚙️",  "Run MRP",            "Execute L1–L4 BOM explosion",                   mrp_done, "mrp"),
        ("🏭",  "Segment Capacity",   "LP-optimised import-part constrained capacity",  seg_done, "segment"),
        ("📦",  "Aging Projection",   "Material aging forecast with consumption offset",aging_done,"aging"),
    ]

    st.markdown('<div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:28px">', unsafe_allow_html=True)
    for icon, title, desc, done, page_key in steps:
        border = "#1a6ef7" if done else "#e5e7eb"
        badge_html = '<span style="font-size:10px;font-weight:700;background:#dcfce7;color:#15803d;padding:3px 9px;border-radius:10px;">DONE</span>' if done else '<span style="font-size:10px;font-weight:600;background:#f3f4f6;color:#9ca3af;padding:3px 9px;border-radius:10px;">PENDING</span>'
        st.markdown(f"""
        <div style="background:#fff;border:1px solid {border};border-radius:12px;padding:18px 20px;cursor:pointer;transition:box-shadow 0.15s;" onclick="">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">
                <div style="font-size:22px;">{icon}</div>
                {badge_html}
            </div>
            <div style="font-size:14px;font-weight:700;color:#111827;margin-bottom:4px;">{title}</div>
            <div style="font-size:12px;color:#6b7280;">{desc}</div>
        </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if mrp_done:
        r = st.session_state["mrp_results"]
        section_header("MRP Quick Stats")
        c1,c2,c3,c4 = st.columns(4)
        total_comps = sum(df["Component"].nunique() for df in [r["result_l1"],r["result_l2"],r["result_l3"],r["result_l4"]] if not df.empty)
        total_short = sum(df[df["Shortage"]>0]["Component"].nunique() for df in [r["result_l1"],r["result_l2"],r["result_l3"],r["result_l4"]] if not df.empty)
        c1.metric("Total components", f"{total_comps:,}")
        c2.metric("With shortage",    f"{total_short:,}")
        c3.metric("Planning months",  f"{len(r['months'])}")
        c4.metric("Stock records",    f"{len(r['stock']):,}")

    if seg_done:
        r = st.session_state["seg_results"]
        section_header("Segment Quick Stats")
        s1,s2,s3,s4 = st.columns(4)
        s1.metric("Total sets producible",  f"{r['total_sets']:,}")
        s2.metric("FG codes with output",   f"{sum(1 for f in r['fg_results'] if f['Max_Sets']>0)} / {len(r['fg_results'])}")
        s3.metric("Segments active",        f"{(r['alloc_int']>0).sum()} / {len(r['segs'])}")
        s4.metric("Constrained parts",      f"{len(r['constrained_parts'])}")

    st.markdown("</div>", unsafe_allow_html=True)


def page_upload():
    topbar("Upload Configuration & Data Files", "Upload all required files to run the MRP process")
    st.markdown('<div class="page-content">', unsafe_allow_html=True)

    st.markdown("""
    <div class="upload-grid">
        <div class="upload-card">
            <div class="upload-card-header">
                <div style="display:flex;align-items:center;gap:12px;">
                    <div class="upload-card-icon purple">📋</div>
                    <div class="upload-card-meta">
                        <p class="upload-card-title">BOM File</p>
                        <p class="upload-card-desc">Upload your BOM file (.XLSX, .XLS)</p>
                    </div>
                </div>
                <span class="badge-required">Required</span>
            </div>
        </div>
        <div class="upload-card">
            <div class="upload-card-header">
                <div style="display:flex;align-items:center;gap:12px;">
                    <div class="upload-card-icon green">📊</div>
                    <div class="upload-card-meta">
                        <p class="upload-card-title">Req. &amp; Stock File</p>
                        <p class="upload-card-desc">Upload your requirement &amp; stock file</p>
                    </div>
                </div>
                <span class="badge-required">Required</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        bom_file = st.file_uploader("BOM File", type=["xlsx","xls"], key="bom_up", label_visibility="collapsed")
        st.markdown('<p class="accepted-text">Accepted: .XLSX, .XLS</p>', unsafe_allow_html=True)
    with col2:
        req_file = st.file_uploader("Req & Stock", type=["xlsx","xls"], key="req_up", label_visibility="collapsed")
        st.markdown('<p class="accepted-text">Accepted: .XLSX, .XLS</p>', unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="upload-grid">
        <div class="upload-card">
            <div class="upload-card-header">
                <div style="display:flex;align-items:center;gap:12px;">
                    <div class="upload-card-icon orange">📦</div>
                    <div class="upload-card-meta">
                        <p class="upload-card-title">Production Orders</p>
                        <p class="upload-card-desc">Upload your production orders file</p>
                    </div>
                </div>
                <span class="badge-optional">Optional</span>
            </div>
        </div>
        <div class="upload-card">
            <div class="upload-card-header">
                <div style="display:flex;align-items:center;gap:12px;">
                    <div class="upload-card-icon blue">📥</div>
                    <div class="upload-card-meta">
                        <p class="upload-card-title">Receipt Quantities</p>
                        <p class="upload-card-desc">Upload your receipt quantities file</p>
                    </div>
                </div>
                <span class="badge-optional">Optional</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col3, col4 = st.columns(2)
    with col3:
        prod_file = st.file_uploader("Production Orders", type=["xlsx","xls"], key="prod_up", label_visibility="collapsed")
        st.markdown('<p class="accepted-text">Accepted: .XLSX, .XLS</p>', unsafe_allow_html=True)
    with col4:
        receipt_file = st.file_uploader("Receipt Quantities", type=["xlsx","xls"], key="receipt_up", label_visibility="collapsed")
        st.markdown('<p class="accepted-text">Accepted: .XLSX, .XLS</p>', unsafe_allow_html=True)

    # Store uploads in session state
    if bom_file:     st.session_state["_bom_file_data"]     = bom_file.read(); bom_file.seek(0)
    if req_file:     st.session_state["_req_file_data"]     = req_file.read(); req_file.seek(0)
    if prod_file:    st.session_state["_prod_file_data"]    = prod_file.read(); prod_file.seek(0)
    if receipt_file: st.session_state["_receipt_file_data"] = receipt_file.read(); receipt_file.seek(0)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    all_ready = bom_file is not None or st.session_state.get("_bom_file_data")
    req_ready = req_file is not None or st.session_state.get("_req_file_data")

    st.markdown(f"""
    <div class="run-area">
        <div>
            <div class="run-area-text">Ready to process</div>
            <div class="run-area-sub">All required files uploaded · Click Run MRP to proceed</div>
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    c_btn, _ = st.columns([1, 4])
    with c_btn:
        if st.button("Run MRP  ▶", type="primary", use_container_width=True, key="upload_run_btn"):
            go("mrp")

    st.markdown("</div>", unsafe_allow_html=True)


def page_mrp():
    topbar("Run MRP", "Execute Material Requirements Planning — L1 to L4 BOM explosion")
    st.markdown('<div class="page-content">', unsafe_allow_html=True)

    # File re-use from upload page or direct upload
    bom_bytes     = st.session_state.get("_bom_file_data")
    req_bytes     = st.session_state.get("_req_file_data")
    prod_bytes    = st.session_state.get("_prod_file_data")
    receipt_bytes = st.session_state.get("_receipt_file_data")

    has_files = bom_bytes and req_bytes
    if not has_files:
        section_header("File Input")
        st.info("Upload files on the **Upload Files** page, or upload directly here.")
        c1, c2 = st.columns(2)
        with c1:
            bf = st.file_uploader("BOM File *", type=["xlsx","xls"], key="bom_mrp")
            if bf: bom_bytes = bf.read(); st.session_state["_bom_file_data"] = bom_bytes
        with c2:
            rf = st.file_uploader("Req & Stock File *", type=["xlsx","xls"], key="req_mrp")
            if rf: req_bytes = rf.read(); st.session_state["_req_file_data"] = req_bytes
        c3, c4 = st.columns(2)
        with c3:
            pf = st.file_uploader("Production Orders", type=["xlsx","xls"], key="prod_mrp")
            if pf: prod_bytes = pf.read(); st.session_state["_prod_file_data"] = prod_bytes
        with c4:
            rrf = st.file_uploader("Receipt Quantities", type=["xlsx","xls"], key="receipt_mrp")
            if rrf: receipt_bytes = rrf.read(); st.session_state["_receipt_file_data"] = receipt_bytes

    section_header("Engine Configuration")
    cfg1,cfg2,cfg3,cfg4,cfg5 = st.columns(5)
    with cfg1: st.session_state["cfg_phantom"] = st.text_input("Phantom code",    value=st.session_state["cfg_phantom"], key="ph_in")
    with cfg2: st.session_state["cfg_vl1"]     = st.text_input("Verify L1",       value=st.session_state["cfg_vl1"],     key="vl1_in")
    with cfg3: st.session_state["cfg_vl2"]     = st.text_input("Verify L2",       value=st.session_state["cfg_vl2"],     key="vl2_in")
    with cfg4: st.session_state["cfg_vl3"]     = st.text_input("Verify L3",       value=st.session_state["cfg_vl3"],     key="vl3_in")
    with cfg5: st.session_state["cfg_vl4"]     = st.text_input("Verify L4",       value=st.session_state["cfg_vl4"],     key="vl4_in")

    PHANTOM   = st.session_state["cfg_phantom"]
    VERIFY_L1 = st.session_state["cfg_vl1"]
    VERIFY_L2 = st.session_state["cfg_vl2"]
    VERIFY_L3 = st.session_state["cfg_vl3"]
    VERIFY_L4 = st.session_state["cfg_vl4"]

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    run_col, _ = st.columns([1, 4])
    with run_col:
        run_btn = st.button("▶  Execute MRP", type="primary", use_container_width=True, key="run_mrp_btn")

    if run_btn:
        if not bom_bytes or not req_bytes:
            st.warning("Please upload BOM and Req & Stock files first.")
        else:
            try:
                bom_f     = io.BytesIO(bom_bytes)
                req_f     = io.BytesIO(req_bytes)
                prod_f    = io.BytesIO(prod_bytes)    if prod_bytes    else None
                receipt_f = io.BytesIO(receipt_bytes) if receipt_bytes else None
                results = run_mrp(bom_f, req_f, prod_f, receipt_f)
                if results is not None:
                    st.session_state["mrp_results"] = results
                    st.success("MRP completed successfully.")
            except Exception as e:
                st.exception(e)

    r = st.session_state.get("mrp_results")
    if r is None:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">⚙️</div>
            <div class="empty-title">Ready to run</div>
            <div class="empty-sub">Ensure files are uploaded, configure verification codes above, then click Execute MRP.</div>
        </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        return

    # ── Results ────────────────────────────────────────────────
    section_header("Summary")
    c1,c2,c3,c4 = st.columns(4)
    for col_ui,lbl,df in zip([c1,c2,c3,c4],["L1","L2","L3","L4"],[r["result_l1"],r["result_l2"],r["result_l3"],r["result_l4"]]):
        short = df[df["Shortage"]>0]["Component"].nunique() if not df.empty else 0
        with col_ui:
            st.metric(f"L{lbl[-1]} components", df["Component"].nunique() if not df.empty else 0)
            st.metric("With shortage", short)

    section_header("Verification")
    tab1,tab2,tab3,tab4 = st.tabs(["L1","L2","L3 (phantom)","L4"])
    def show_verify(tab,result_df,target,level_label):
        with tab:
            st.markdown(f"**{level_label} — `{target}`**")
            if result_df is None or result_df.empty: st.warning("No rows at this level."); return
            t = result_df[result_df["Component"]==target]
            if t.empty: st.info("Not found — phantom or no demand."); return
            st.caption(f"Description: {t['Description'].iloc[0]} | Opening Stock: {r['stock'].get(target,0):,.3f}")
            st.dataframe(t[["Month","Gross_Requirement","Stock_Used","Shortage","Stock_Remaining"]].reset_index(drop=True),use_container_width=True)
    show_verify(tab1,r["result_l1"],VERIFY_L1,"LEVEL 1")
    show_verify(tab2,r["result_l2"],VERIFY_L2,"LEVEL 2")
    with tab3:
        ph_found = (not r["result_l3"].empty) and (VERIFY_L3 in r["result_l3"]["Component"].values)
        if ph_found: st.error(f"ERROR: {VERIFY_L3} found — phantom logic broken!")
        else: st.success(f"✅ {VERIFY_L3} correctly SKIPPED (phantom pass-through confirmed).")
    show_verify(tab4,r["result_l4"],VERIFY_L4,"LEVEL 4")

    section_header("Net Position Output")
    pivot = r.get("pivot")
    if pivot is not None:
        st.dataframe(pivot.head(300), use_container_width=True)
        st.caption(f"{len(pivot):,} rows · {len(r['month_cols'])} month columns · positive = surplus · negative = shortage")
        buf = io.BytesIO(); pivot.to_excel(buf,index=False,engine="openpyxl"); buf.seek(0)
        st.download_button("⬇  Download mrp_final.xlsx", data=buf, file_name="mrp_final.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                           use_container_width=True, type="primary")

    # Search
    show_search_section(bom=r["bom"],req_df=r["req"],months=r["months"],
                        stock=r["stock"],prod_summary=r["prod_summary"])

    st.markdown("</div>", unsafe_allow_html=True)


def page_segment():
    topbar("Segment Wise Material Available", "LP-optimised IDU + ODU production capacity constrained by import parts")
    st.markdown('<div class="page-content">', unsafe_allow_html=True)

    mrp_r = st.session_state.get("mrp_results")
    if mrp_r is None:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">🏭</div>
            <div class="empty-title">MRP not yet run</div>
            <div class="empty-sub">Run MRP first — Segment Capacity uses the same BOM and Stock data.</div>
        </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        return

    section_header("Segment & Import Part File")
    seg_col, _ = st.columns([2, 3])
    with seg_col:
        seg_imp_file = st.file_uploader("Segment & Import Part (.xlsx)",
                                         type=["xlsx","xls"],key="seg_up",
                                         help="Sheet 1: Import Part List | Sheet 2: Segment (IDU / ODU codes)")

    run_col, _ = st.columns([1, 4])
    with run_col:
        run_seg = st.button("▶  Run Segment Capacity", type="primary", use_container_width=True, key="run_seg_btn")

    if run_seg:
        if seg_imp_file is None:
            st.warning("Please upload the Segment & Import Part file.")
        else:
            try:
                seg_result = run_segment_capacity(mrp_r["bom"],mrp_r["stock"],seg_imp_file)
                if seg_result is not None:
                    st.session_state["seg_results"] = seg_result
                    seg_imp_file.seek(0)
                    st.session_state["seg_imp_bytes"] = seg_imp_file.read()
            except Exception as e:
                st.exception(e)

    r = st.session_state.get("seg_results")
    if r is None:
        if not run_seg:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-icon">🏭</div>
                <div class="empty-title">No results yet</div>
                <div class="empty-sub">Upload the Segment & Import Part file and click Run Segment Capacity.</div>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        return

    # Metrics
    section_header("Overview")
    m1,m2,m3,m4 = st.columns(4)
    m1.metric("Total FG sets", f"{r['total_sets']:,}")
    m2.metric("FGs producing", f"{sum(1 for f in r['fg_results'] if f['Max_Sets']>0)} / {len(r['fg_results'])}")
    m3.metric("Active segments", f"{(r['alloc_int']>0).sum()} / {len(r['segs'])}")
    m4.metric("Constrained parts", f"{len(r['constrained_parts'])}")

    # RM filter
    rm_map = r.get("rm_map",{})
    all_rm_groups = sorted(set(rm_map.values())) if rm_map else []
    active_groups = r.get("active_rm_groups",[])
    if all_rm_groups:
        section_header("RM Group Filter")
        rm_cols = st.columns(min(len(all_rm_groups),6))
        sel_grps = []
        for i,grp in enumerate(all_rm_groups):
            with rm_cols[i%len(rm_cols)]:
                if st.checkbox(grp,value=(grp in active_groups),key=f"rm_{grp}"):
                    sel_grps.append(grp)
        apply_col, _ = st.columns([1,4])
        with apply_col:
            if st.button("↻ Apply filter", key="apply_rm", type="primary"):
                _seg_bytes = st.session_state.get("seg_imp_bytes")
                if _seg_bytes:
                    with st.spinner("Recalculating ..."):
                        new_r = run_segment_capacity(mrp_r["bom"],mrp_r["stock"],io.BytesIO(_seg_bytes),active_rm_groups=sel_grps)
                        if new_r: st.session_state["seg_results"] = new_r; st.rerun()
                else: st.warning("Re-upload Segment file first.")

    if r.get("skipped_segs"):
        with st.expander(f"⚠ {len(r['skipped_segs'])} FGs skipped"):
            for s in r["skipped_segs"]: st.text(f"  · {s}")

    # FG table
    section_header("Sets producible per FG code")
    fg_results = r.get("fg_results",[])
    if fg_results:
        fg_df = pd.DataFrame([{
            "Segment":f["Segment"],"FG Code":f["FG_Code"],"FG Description":f.get("FG_Desc",""),
            "IDU":f["IDU"],"IDU Desc":f.get("IDU_Desc",""),"Compatible ODU":f["Compatible_ODU"],
            "ODU Desc":f.get("ODU_Desc",""),"Max Sets":f["Max_Sets"],
            "Limiting Part":f["Limiting_Part"],"Limiting Stock":f["Limiting_Stock"],
        } for f in fg_results]).sort_values(["Segment","Max Sets"],ascending=[True,False])
        def hl_fg(row):
            if row["Max Sets"]>0: return ["background-color:#f0fdf4"]*len(row)
            return ["background-color:#fffbeb"]*len(row)
        st.dataframe(fg_df.style.apply(hl_fg,axis=1).format({"Max Sets":"{:,}","Limiting Stock":"{:,}"}),
                     use_container_width=True,hide_index=True)

    # Segment rollup
    section_header("Segment rollup")
    seg_rows=[]
    for s,qty in zip(r["segs"],r["alloc_int"]):
        sd=r["segments_data"][s]; fgs=[f for f in fg_results if f["Segment"]==s]
        seg_rows.append({"Segment":s,"Total Sets":int(qty),"FG codes":len(fgs),
                          "FGs producing":sum(1 for f in fgs if f["Max_Sets"]>0),
                          "Unique IDUs":sd["idu_count"],"Unique ODUs":sd["odu_count"]})
    seg_df_d = pd.DataFrame(seg_rows).sort_values("Total Sets",ascending=False)
    def hl_seg(row):
        if row["Total Sets"]>0: return ["background-color:#f0fdf4"]*len(row)
        return ["background-color:#f9fafb"]*len(row)
    st.dataframe(seg_df_d.style.apply(hl_seg,axis=1).format({"Total Sets":"{:,}"}),
                 use_container_width=True,hide_index=True)

    # FG detail
    section_header("FG detail — import part breakdown")
    fg_opts = sorted([f["FG_Code"] for f in fg_results],key=lambda fg:-next(f["Max_Sets"] for f in fg_results if f["FG_Code"]==fg))
    sel_fg = st.selectbox("Select FG code",options=fg_opts,key="fg_det")
    if sel_fg:
        fgr=next(f for f in fg_results if f["FG_Code"]==sel_fg); sets=fgr["Max_Sets"]
        st.markdown(f"**{sel_fg}** — {fgr.get('FG_Desc','')} · Segment: `{fgr['Segment']}` · IDU: `{fgr['IDU']}` · ODU: `{fgr['Compatible_ODU']}` · **Max sets: {sets:,}**")
        imp_rows=[]
        for p,req in sorted(fgr["combined_req"].items(),key=lambda x:-x[1]):
            avail=float(r["stock"].get(p,0)); max_s=int(avail/req) if req>0 else 0
            imp_rows.append({"Import Part":p,"RM Group":rm_map.get(p,"—"),"Qty per set":round(req,4),
                              "Stock available":int(avail),"Max sets (alone)":max_s,
                              "Binding?":"🔴 YES" if max_s==sets and sets>0 else ""})
        imp_df=pd.DataFrame(imp_rows)
        def hl_imp(row): return (["background-color:#fff0f0"]*len(row) if row["Binding?"]=="🔴 YES" else [""]*len(row))
        st.dataframe(imp_df.style.apply(hl_imp,axis=1).format({"Qty per set":"{:.4f}","Stock available":"{:,}","Max sets (alone)":"{:,}"}),
                     use_container_width=True,hide_index=True)

    # Utilisation
    section_header("Import part stock utilisation")
    pu_rows=[]
    for p in r["import_parts"]:
        pu=r["part_usage"].get(p,{})
        pu_rows.append({"Import Part":p,"RM Group":rm_map.get(p,"—"),"Stock":int(r["stock"].get(p,0)),
                         "Used":int(pu.get("used",0)),"Remaining":int(pu.get("remain",r["stock"].get(p,0))),"Utilisation%":pu.get("pct",0)})
    pu_df=pd.DataFrame(pu_rows).sort_values("Utilisation%",ascending=False)
    def hl_util(row):
        pct=row["Utilisation%"]
        if pct>=90: return ["background-color:#fff0f0"]*len(row)
        elif pct>=50: return ["background-color:#fffbeb"]*len(row)
        elif pct>0: return ["background-color:#f0fdf4"]*len(row)
        return [""]*len(row)
    tab_all,tab_con = st.tabs(["All import parts","Constrained only"])
    with tab_all:
        st.dataframe(pu_df.style.apply(hl_util,axis=1).format({"Stock":"{:,}","Used":"{:,}","Remaining":"{:,}","Utilisation%":"{:.1f}"}),
                     use_container_width=True,hide_index=True)
    with tab_con:
        st.dataframe(pu_df[pu_df["Import Part"].isin(r["constrained_parts"])].style.apply(hl_util,axis=1)
                     .format({"Stock":"{:,}","Used":"{:,}","Remaining":"{:,}","Utilisation%":"{:.1f}"}),
                     use_container_width=True,hide_index=True)

    # Download
    st.divider()
    buf=io.BytesIO()
    with pd.ExcelWriter(buf,engine="openpyxl") as writer:
        if fg_results: fg_df.to_excel(writer,sheet_name="FG Sets",index=False)
        seg_df_d.to_excel(writer,sheet_name="Segment Rollup",index=False)
        pu_df.to_excel(writer,sheet_name="Import Part Utilisation",index=False)
    buf.seek(0)
    st.download_button("⬇  Download Segment Capacity (.xlsx)",data=buf,file_name="segment_production_capacity.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                       use_container_width=True,type="primary")

    st.markdown("</div>", unsafe_allow_html=True)


def page_aging():
    topbar("Aging Material Projection", "Forecast aging stock with cumulative production consumption offset")
    st.markdown('<div class="page-content">', unsafe_allow_html=True)

    section_header("Aging Data File")
    a_col1, a_col2 = st.columns([2,1])
    with a_col1:
        aging_file = st.file_uploader("Aging Material Details (.xlsx)", type=["xlsx","xls"], key="aging_up",
                                       help="Buckets: 0-15, 16-30, 31-60, 61-90, 91-120, 121-150, 151-180, 181-360, Over361")
    with a_col2:
        st.markdown("**Aging snapshot date**")
        aging_base_date = st.date_input("As-on date", value=pd.Timestamp("2026-05-01"), key="aging_dt", label_visibility="collapsed")

    run_col, _ = st.columns([1,4])
    with run_col:
        run_aging = st.button("▶  Run Aging Projection", type="primary", use_container_width=True, key="run_aging_btn")

    if run_aging:
        if aging_file is None:
            st.warning("Please upload the Aging Material Details file.")
        else:
            try:
                with st.spinner("Running aging projection ..."):
                    aging_df = load_aging_data(aging_file)
                    mrp_r = st.session_state.get("mrp_results")
                    prod_cons = {}
                    if mrp_r is not None:
                        all_raw=[]
                        for key in ["raw_l1","raw_l2","raw_l3","raw_l4"]:
                            df=mrp_r.get(key)
                            if df is not None and not df.empty:
                                gc=next((c for c in df.columns if c.lower() in ("gross","gross_requirement")),None)
                                if "Component" in df.columns and "Month" in df.columns and gc:
                                    tmp=df[["Component","Month",gc]].copy(); tmp.columns=["Component","Month","Gross"]; all_raw.append(tmp)
                        if all_raw:
                            cdf=pd.concat(all_raw,ignore_index=True).groupby(["Component","Month"],as_index=False)["Gross"].sum()
                            for _,row2 in cdf.iterrows():
                                mat=str(row2["Component"]).strip(); mon=str(row2["Month"]).strip(); qty=float(row2["Gross"])
                                if qty>0:
                                    if mat not in prod_cons: prod_cons[mat]={}
                                    prod_cons[mat][mon]=prod_cons[mat].get(mon,0)+qty
                            st.info(f"BOM consumption loaded: {len(prod_cons):,} components.")
                        else: st.warning("Raw gross data not found. Run MRP first for consumption-adjusted projections.")
                    raw_months=mrp_r.get("months",[]) if mrp_r else []
                    if not raw_months:
                        base=pd.Timestamp(aging_base_date)
                        raw_months=[(base+pd.DateOffset(months=i)) for i in range(6)]
                    def to_lbl(m):
                        try: return pd.to_datetime(m,dayfirst=True).strftime("%b-%y")
                        except: return str(m)
                    months_list=[to_lbl(m) for m in raw_months]
                    if prod_cons:
                        new_pc={}
                        for mat,monthly in prod_cons.items():
                            new_pc[mat]={}
                            for rm,qty in monthly.items():
                                cm=to_lbl(rm); new_pc[mat][cm]=new_pc[mat].get(cm,0)+qty
                        prod_cons=new_pc
                    proj=project_aging(aging_df,base_date=aging_base_date,production_consumption=prod_cons,months_list=months_list)
                    st.session_state["aging_results"]={"proj":proj,"months":months_list,"base_date":aging_base_date}
            except Exception as e:
                st.exception(e)

    ag = st.session_state.get("aging_results")
    if ag is None:
        if not run_aging:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-icon">📦</div>
                <div class="empty-title">No aging data yet</div>
                <div class="empty-sub">Upload the aging file and click Run Aging Projection.<br>Optionally run MRP first for consumption-adjusted forecasts.</div>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        return

    aging_proj_df=ag["proj"]; months_list=ag["months"]; base_date=ag["base_date"]
    months_ordered=[m for m in months_list if m in aging_proj_df["Month"].unique()]
    last_month=months_ordered[-1] if months_ordered else ""; first_month=months_ordered[0] if months_ordered else ""
    final_df=aging_proj_df[aging_proj_df["Month"]==last_month]
    first_df=aging_proj_df[aging_proj_df["Month"]==first_month]

    section_header("Overview")
    c1,c2,c3,c4=st.columns(4)
    c1.metric(f"Aging Value — {first_month}",f"Rs {first_df['Aging Value (Rs)'].sum():,.0f}")
    c2.metric(f"Aging Value — {last_month}", f"Rs {final_df['Aging Value (Rs)'].sum():,.0f}",
              delta=f"Rs {final_df['Aging Value (Rs)'].sum()-first_df['Aging Value (Rs)'].sum():,.0f}",
              delta_color="inverse")
    c3.metric(f"Materials aging — {last_month}",f"{(final_df['Aging Value (Rs)']>0).sum():,}")
    c4.metric("Materials tracked",f"{aging_proj_df['Material'].nunique():,}")

    section_header("Aging value by month-end")
    msumm=(aging_proj_df.groupby("Month",sort=False)
           .agg(Aging_Val=("Aging Value (Rs)","sum"),
                Mat_Aging=("Material",lambda x:(aging_proj_df.loc[x.index,"Aging Value (Rs)"]>0).sum()),
                Turning_Next=("Turning Aging Next Month","sum"))
           .reindex(months_ordered).reset_index())
    msumm.columns=["Month","Aging Value (Rs)","Materials with Aging Value","Qty Turning Aging Next Month"]
    def hl_val(row):
        v=row["Aging Value (Rs)"]
        if v>10_000_000: return ["background-color:#fff0f0"]*len(row)
        if v>1_000_000: return ["background-color:#fffbeb"]*len(row)
        if v>0: return ["background-color:#f0fdf4"]*len(row)
        return [""]*len(row)
    st.dataframe(msumm.style.apply(hl_val,axis=1).format({"Aging Value (Rs)":"Rs {:,.0f}","Qty Turning Aging Next Month":"{:,.0f}"}),
                 use_container_width=True,hide_index=True)

    section_header("Aging value — material × month")
    piv=(aging_proj_df.pivot_table(index=["Material","Description"],columns="Month",values="Aging Value (Rs)",aggfunc="sum")
         .reindex(columns=months_ordered,fill_value=0).reset_index())
    aging_rows=piv[piv[months_ordered].max(axis=1)>0].sort_values(last_month,ascending=False)
    st.caption(f"{len(aging_rows):,} materials have aging value in at least one month")
    st.dataframe(aging_rows.style.format({m:"Rs {:,.0f}" for m in months_ordered}).background_gradient(subset=months_ordered,cmap="YlOrRd"),
                 use_container_width=True,hide_index=True)

    section_header("Material detail — select month")
    sel_month=st.selectbox("View aging as of:",months_ordered,index=len(months_ordered)-1,key="ag_sel")
    mdf=(aging_proj_df[aging_proj_df["Month"]==sel_month].query("`Aging Value (Rs)` > 0")
         .sort_values("Aging Value (Rs)",ascending=False).copy())
    st.caption(f"{len(mdf):,} materials · Total: Rs {mdf['Aging Value (Rs)'].sum():,.0f}")
    show_c=["Material","Description","Material Type","Aging Pool Qty","Cumulative Consumption","Aging Qty (>=91d)","Aging Value (Rs)"]
    def hl_row(row):
        v=row["Aging Value (Rs)"]
        if v>500_000: return ["background-color:#fff0f0"]*len(row)
        if v>100_000: return ["background-color:#fffbeb"]*len(row)
        return [""]*len(row)
    st.dataframe(mdf[show_c].style.apply(hl_row,axis=1).format({"Aging Pool Qty":"{:,.0f}","Cumulative Consumption":"{:,.0f}","Aging Qty (>=91d)":"{:,.0f}","Aging Value (Rs)":"Rs {:,.0f}"}),
                 use_container_width=True,hide_index=True)

    st.divider()
    buf=io.BytesIO()
    with pd.ExcelWriter(buf,engine="openpyxl") as writer:
        msumm.to_excel(writer,sheet_name="Monthly Summary",index=False)
        aging_rows.to_excel(writer,sheet_name="Aging Value Pivot",index=False)
        aging_proj_df.to_excel(writer,sheet_name="Full Detail",index=False)
    buf.seek(0)
    st.download_button("⬇  Download Aging Projection (.xlsx)",data=buf,file_name="aging_material_projection.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                       use_container_width=True,type="primary")

    st.markdown("</div>", unsafe_allow_html=True)


def page_settings():
    topbar("Settings", "Engine configuration and verification codes")
    st.markdown('<div class="page-content">', unsafe_allow_html=True)

    section_header("Engine Configuration")
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1:
        st.session_state["cfg_phantom"] = st.text_input(
            "Phantom Special Procurement Code",
            value=st.session_state["cfg_phantom"],
            key="s_phantom",
            help="BOM items with this special procurement key are treated as phantom assemblies — their children are exploded but the phantom itself is skipped.")
    with c2:
        st.markdown("**What is a phantom?**")
        st.caption("Phantom assemblies (e.g. SP code 50) are pass-through BOMs used for grouping. The engine skips them and directly explodes their children.")
    st.markdown("</div>", unsafe_allow_html=True)

    section_header("Verification Component Codes")
    st.caption("These codes are used to verify the MRP explosion results after each run. Set them to known components in your BOM.")
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    v1,v2 = st.columns(2)
    with v1:
        st.session_state["cfg_vl1"] = st.text_input("Verify L1 component", value=st.session_state["cfg_vl1"], key="s_vl1")
        st.session_state["cfg_vl3"] = st.text_input("Verify L3 (phantom — should NOT appear)", value=st.session_state["cfg_vl3"], key="s_vl3")
    with v2:
        st.session_state["cfg_vl2"] = st.text_input("Verify L2 component", value=st.session_state["cfg_vl2"], key="s_vl2")
        st.session_state["cfg_vl4"] = st.text_input("Verify L4 component", value=st.session_state["cfg_vl4"], key="s_vl4")
    st.markdown("</div>", unsafe_allow_html=True)

    section_header("Session Data")
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    mrp_done  = st.session_state["mrp_results"] is not None
    seg_done  = st.session_state["seg_results"] is not None
    aging_done= st.session_state["aging_results"] is not None
    r1,r2,r3 = st.columns(3)
    r1.metric("MRP results",     "Loaded" if mrp_done  else "Not run")
    r2.metric("Segment results", "Loaded" if seg_done  else "Not run")
    r3.metric("Aging results",   "Loaded" if aging_done else "Not run")
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    if st.button("🗑  Clear all session data", key="clear_session"):
        for k in ["mrp_results","seg_results","aging_results","seg_imp_bytes",
                  "_bom_file_data","_req_file_data","_prod_file_data","_receipt_file_data"]:
            st.session_state[k] = None
        st.success("Session data cleared.")
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# LAYOUT: LEFT NAV + MAIN
# ═══════════════════════════════════════════════════════════════
mrp_done  = st.session_state["mrp_results"] is not None
seg_done  = st.session_state["seg_results"] is not None
aging_done= st.session_state["aging_results"] is not None

left, right = st.columns([240, 1000], gap="small")

# ── Left nav ──────────────────────────────────────────────────
with left:
    st.markdown("""
    <style>
    /* Expand first column to be nav panel */
    [data-testid="stHorizontalBlock"] > div:first-child {
        background: #0d1b2a !important;
        min-height: 100vh !important;
        padding: 0 !important;
        border-right: none !important;
    }
    [data-testid="stHorizontalBlock"] > div:first-child > div {
        background: #0d1b2a !important;
    }
    /* Nav buttons */
    [data-testid="stHorizontalBlock"] > div:first-child .stButton > button {
        background: transparent !important;
        border: none !important;
        border-radius: 8px !important;
        color: rgba(255,255,255,0.55) !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        text-align: left !important;
        padding: 9px 12px !important;
        margin: 1px 0 !important;
        transition: background 0.15s, color 0.15s !important;
    }
    [data-testid="stHorizontalBlock"] > div:first-child .stButton > button:hover {
        background: rgba(255,255,255,0.07) !important;
        color: rgba(255,255,255,0.9) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    page = st.session_state["page"]

    st.markdown("""
    <div style="padding:20px 16px 14px;border-bottom:1px solid rgba(255,255,255,0.07);margin-bottom:8px;">
        <div style="display:flex;align-items:center;gap:10px;">
            <div style="width:32px;height:32px;background:#1a6ef7;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:15px;">⚙</div>
            <div>
                <div style="font-size:13px;font-weight:700;color:#fff;font-family:'Plus Jakarta Sans',sans-serif;letter-spacing:0.03em;">MRP CONFIG</div>
                <div style="font-size:10px;color:rgba(255,255,255,0.3);font-family:'Plus Jakarta Sans',sans-serif;">SAP MRP Engine</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Nav items
    nav_items = [
        ("🏠", "Home",                       "home"),
        ("📂", "Upload Files",               "upload"),
        ("⚙️",  "Run MRP",                   "mrp"),
        ("🏭",  "Segment Wise Available",    "segment"),
        ("📦",  "Aging Projection",          "aging"),
        ("⚙",  "Settings",                  "settings"),
    ]

    for icon, label, page_key in nav_items:
        is_active = (page == page_key)
        # Visual active indicator via CSS on active buttons
        if is_active:
            st.markdown(f"""
            <style>
            [data-testid="stHorizontalBlock"] > div:first-child button[kind="secondary"]:nth-of-type(1),
            div[data-testid="element-container"]:has(button[key="nav_{page_key}"]) button {{
                background: #1a6ef7 !important;
                color: #ffffff !important;
            }}
            </style>""", unsafe_allow_html=True)
        btn = st.button(
            f"{icon}  {label}",
            key=f"nav_{page_key}",
            use_container_width=True,
        )
        if btn:
            st.session_state["page"] = page_key
            st.rerun()

    st.markdown("""
    <div style="position:absolute;bottom:0;left:0;right:0;padding:16px;border-top:1px solid rgba(255,255,255,0.06);">
        <div style="font-size:12px;color:rgba(255,255,255,0.3);font-family:'Plus Jakarta Sans',sans-serif;">
            Need help?<br><span style="color:rgba(255,255,255,0.18);font-size:11px;">Contact support</span>
        </div>
    </div>""", unsafe_allow_html=True)


# ── Right content ──────────────────────────────────────────────
with right:
    # Override right column background
    st.markdown("""
    <style>
    [data-testid="stHorizontalBlock"] > div:last-child {
        background: #f0f2f5 !important;
        padding: 0 !important;
        overflow-y: auto !important;
    }
    [data-testid="stHorizontalBlock"] > div:last-child > div {
        background: #f0f2f5 !important;
    }
    </style>""", unsafe_allow_html=True)

    current_page = st.session_state["page"]
    if   current_page == "home":     page_home()
    elif current_page == "upload":   page_upload()
    elif current_page == "mrp":      page_mrp()
    elif current_page == "segment":  page_segment()
    elif current_page == "aging":    page_aging()
    elif current_page == "settings": page_settings()
    else:                            page_home()
