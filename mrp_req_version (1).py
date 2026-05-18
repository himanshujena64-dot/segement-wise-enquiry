"""
SAP MRP ENGINE — Professional Sidebar Navigation Layout (Fixed)
No black gaps — uses Streamlit's native sidebar styled as a custom nav panel.
"""

import io
import re
from collections import defaultdict

import numpy as np
import pandas as pd
import streamlit as st
from scipy.optimize import linprog

st.set_page_config(
    page_title="SAP MRP Engine",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════
# GLOBAL CSS
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Apply font globally ──────────────────────────────────── */
html, body, [class*="css"], .stApp {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

/* ── Remove all default Streamlit chrome ──────────────────── */
#MainMenu, footer, header { visibility: hidden !important; }
.block-container { padding: 1rem 2rem 2rem 2rem !important; max-width: 100% !important; }

/* ══════════════════════════════════════════════════════════
   SIDEBAR — transform into dark nav panel
══════════════════════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: #0d1b2a !important;
    min-width: 230px !important;
    max-width: 230px !important;
    padding: 0 !important;
}
[data-testid="stSidebar"] > div:first-child {
    background: #0d1b2a !important;
    padding: 0 !important;
}
[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
    background: #0d1b2a !important;
    padding: 0 !important;
    overflow-x: hidden !important;
}

/* Hide sidebar collapse arrow */
[data-testid="collapsedControl"] { display: none !important; }

/* ── Sidebar buttons → nav items ──────────────────────────── */
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: none !important;
    border-radius: 8px !important;
    color: rgba(255,255,255,0.5) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    text-align: left !important;
    padding: 9px 14px !important;
    margin: 1px 8px !important;
    width: calc(100% - 16px) !important;
    transition: background 0.15s, color 0.15s !important;
    box-shadow: none !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.07) !important;
    color: rgba(255,255,255,0.9) !important;
    box-shadow: none !important;
}
[data-testid="stSidebar"] .stButton > button:focus {
    box-shadow: none !important;
    outline: none !important;
}

/* ── Active nav item ──────────────────────────────────────── */
[data-testid="stSidebar"] .stButton > button[data-active="true"],
[data-testid="stSidebar"] .nav-active button {
    background: #1a6ef7 !important;
    color: #ffffff !important;
}

/* ── Sidebar dividers ─────────────────────────────────────── */
[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.07) !important;
    margin: 8px 0 !important;
}

/* ── Sidebar markdown text ────────────────────────────────── */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span {
    color: rgba(255,255,255,0.35) !important;
    font-size: 11px !important;
}

/* ══════════════════════════════════════════════════════════
   MAIN CONTENT AREA
══════════════════════════════════════════════════════════ */
.stApp {
    background: #f0f2f5 !important;
}
.main .block-container {
    background: #f0f2f5 !important;
}

/* ── Page topbar ──────────────────────────────────────────── */
.topbar {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 16px 24px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.topbar-left {}
.topbar-title {
    font-size: 20px;
    font-weight: 700;
    color: #111827;
    letter-spacing: -0.02em;
    margin: 0 0 2px 0;
}
.topbar-sub {
    font-size: 12px;
    color: #9ca3af;
    margin: 0;
}
.topbar-chips { display: flex; gap: 8px; align-items: center; }
.chip {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 11px;
    font-weight: 600;
    padding: 4px 10px;
    border-radius: 20px;
    white-space: nowrap;
}
.chip.idle { background:#f3f4f6; color:#6b7280; }
.chip.done { background:#dcfce7; color:#15803d; }
.chip-dot { width:6px; height:6px; border-radius:50%; background:currentColor; }

/* ── Upload cards ─────────────────────────────────────────── */
.ucard {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 18px 20px 14px;
    height: 100%;
    transition: border-color 0.2s, box-shadow 0.2s;
}
.ucard:hover { border-color: #93c5fd; box-shadow: 0 0 0 3px rgba(59,130,246,0.06); }
.ucard-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:12px; }
.ucard-title-row { display:flex; align-items:center; gap:12px; }
.ucard-icon {
    width:38px; height:38px; border-radius:9px;
    display:flex; align-items:center; justify-content:center; font-size:18px; flex-shrink:0;
}
.ucard-icon.purple { background:#ede9fe; }
.ucard-icon.green  { background:#dcfce7; }
.ucard-icon.orange { background:#ffedd5; }
.ucard-icon.blue   { background:#dbeafe; }
.ucard-title { font-size:14px; font-weight:700; color:#111827; margin:0 0 2px 0; }
.ucard-desc  { font-size:12px; color:#6b7280; margin:0; }
.badge-req  { font-size:10px; font-weight:700; background:#fee2e2; color:#dc2626; padding:3px 9px; border-radius:10px; }
.badge-opt  { font-size:10px; font-weight:700; background:#f0fdf4; color:#16a34a; padding:3px 9px; border-radius:10px; }
.accepted   { font-size:11px; color:#9ca3af; margin-top:6px; font-family:'JetBrains Mono',monospace; }

/* ── Section dividers ─────────────────────────────────────── */
.sec-div {
    display:flex; align-items:center; gap:10px;
    margin: 24px 0 14px;
}
.sec-div-line { flex:1; height:1px; background:#e5e7eb; }
.sec-div-text { font-size:11px; font-weight:700; color:#9ca3af; letter-spacing:0.1em; text-transform:uppercase; white-space:nowrap; }

/* ── Content cards ────────────────────────────────────────── */
.ccard {
    background:#fff; border:1px solid #e5e7eb; border-radius:12px; padding:20px 24px; margin-bottom:14px;
}

/* ── Run bar ──────────────────────────────────────────────── */
.run-bar {
    background:#fff; border:1px solid #e5e7eb; border-radius:12px;
    padding:18px 22px; display:flex; align-items:center; justify-content:space-between;
    margin-top:14px;
}
.run-bar-text { font-size:14px; font-weight:600; color:#111827; }
.run-bar-sub  { font-size:12px; color:#6b7280; margin-top:2px; }

/* ── Empty state ──────────────────────────────────────────── */
.empty {
    text-align:center; padding:56px 32px;
    background:#fff; border:1.5px dashed #d1d5db; border-radius:14px; margin-top:8px;
}
.empty-icon { font-size:38px; margin-bottom:12px; opacity:0.35; }
.empty-ttl  { font-size:15px; font-weight:600; color:#374151; margin-bottom:6px; }
.empty-sub  { font-size:13px; color:#9ca3af; max-width:320px; margin:0 auto; line-height:1.6; }

/* ── Home step cards ──────────────────────────────────────── */
.step-grid { display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-bottom:24px; }
.step-card {
    background:#fff; border-radius:12px; padding:18px 20px;
    border: 1px solid #e5e7eb;
}
.step-card.done { border-color: #86efac; }

/* ── Metric tiles ─────────────────────────────────────────── */
[data-testid="stMetric"] {
    background:#ffffff !important;
    border:1px solid #e5e7eb !important;
    border-radius:10px !important;
    padding:14px 18px !important;
}
[data-testid="stMetricLabel"] > div {
    font-family:'Plus Jakarta Sans',sans-serif !important;
    font-size:11px !important; font-weight:600 !important;
    color:#9ca3af !important; text-transform:uppercase !important; letter-spacing:0.06em !important;
}
[data-testid="stMetricValue"] > div {
    font-family:'JetBrains Mono',monospace !important;
    font-size:20px !important; font-weight:700 !important; color:#111827 !important;
}

/* ── Buttons ──────────────────────────────────────────────── */
.stButton > button[kind="primary"] {
    background:#1a6ef7 !important; color:#fff !important; border:none !important;
    border-radius:8px !important; font-family:'Plus Jakarta Sans',sans-serif !important;
    font-size:13px !important; font-weight:600 !important; letter-spacing:0.02em !important;
    padding:0.55rem 1.5rem !important; transition:background 0.15s !important;
}
.stButton > button[kind="primary"]:hover { background:#1558d6 !important; }

.stButton > button:not([kind="primary"]):not([data-testid="StyledFullScreenButton"]) {
    background:transparent !important; border:1px solid #e5e7eb !important;
    border-radius:8px !important; font-family:'Plus Jakarta Sans',sans-serif !important;
    font-size:13px !important; font-weight:500 !important; color:#374151 !important;
}
.stButton > button:not([kind="primary"]):hover { background:#f9fafb !important; }

/* ── File uploader ────────────────────────────────────────── */
[data-testid="stFileUploader"] {
    border:1.5px dashed #e5e7eb !important; border-radius:8px !important; background:#fafafa !important;
}
[data-testid="stFileUploader"]:hover { border-color:#93c5fd !important; background:#eff6ff !important; }

/* ── Dataframes ───────────────────────────────────────────── */
[data-testid="stDataFrame"] { border:1px solid #e5e7eb !important; border-radius:10px !important; }

/* ── Download button ──────────────────────────────────────── */
.stDownloadButton > button {
    background:#eff6ff !important; border:1px solid #bfdbfe !important;
    border-radius:8px !important; color:#1d4ed8 !important;
    font-family:'Plus Jakarta Sans',sans-serif !important; font-size:13px !important; font-weight:600 !important;
}
.stDownloadButton > button:hover { background:#dbeafe !important; }

/* ── Alerts / info ────────────────────────────────────────── */
[data-testid="stAlert"] { border-radius:8px !important; font-size:13px !important; }
[data-testid="stStatusContainer"] { border-radius:8px !important; font-size:13px !important; }
[data-testid="stExpander"] { border:1px solid #e5e7eb !important; border-radius:10px !important; }
[data-testid="stCaptionContainer"] p { font-size:11px !important; color:#9ca3af !important; }

/* ── Inputs ───────────────────────────────────────────────── */
[data-testid="stTextInput"] input {
    font-family:'JetBrains Mono',monospace !important; font-size:13px !important; border-radius:7px !important;
}
[data-testid="stSelectbox"] > div > div { border-radius:7px !important; font-size:13px !important; }

/* ── Typography ───────────────────────────────────────────── */
h2 { font-size:15px !important; font-weight:700 !important; color:#111827 !important; }
h3 { font-size:14px !important; font-weight:600 !important; color:#374151 !important; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════
for k, v in {
    "page": "home", "mrp_results": None, "seg_results": None,
    "aging_results": None, "seg_imp_bytes": None,
    "cfg_phantom": "50", "cfg_vl1": "0010748460",
    "cfg_vl2": "0010748458", "cfg_vl3": "0010748814", "cfg_vl4": "0010300601DEL",
    "_bom": None, "_req": None, "_prod": None, "_receipt": None,
    "_aging": None, "_ag_bom": None, "_ag_req": None, "_ag_rec": None,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

PHANTOM   = st.session_state["cfg_phantom"]
VERIFY_L1 = st.session_state["cfg_vl1"]
VERIFY_L2 = st.session_state["cfg_vl2"]
VERIFY_L3 = st.session_state["cfg_vl3"]
VERIFY_L4 = st.session_state["cfg_vl4"]


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════
def go(page):
    st.session_state["page"] = page
    st.rerun()

def sec(text):
    st.markdown(f'<div class="sec-div"><div class="sec-div-line"></div>'
                f'<div class="sec-div-text">{text}</div>'
                f'<div class="sec-div-line"></div></div>', unsafe_allow_html=True)

def topbar(title, sub=""):
    mrp_done  = st.session_state["mrp_results"]  is not None
    seg_done  = st.session_state["seg_results"]  is not None
    ag_done   = st.session_state["aging_results"] is not None
    chips = ""
    if mrp_done:  chips += '<span class="chip done"><span class="chip-dot"></span>MRP done</span>'
    if seg_done:  chips += '<span class="chip done"><span class="chip-dot"></span>Segment done</span>'
    if ag_done:   chips += '<span class="chip done"><span class="chip-dot"></span>Aging done</span>'
    if not mrp_done: chips += '<span class="chip idle"><span class="chip-dot"></span>Awaiting run</span>'
    st.markdown(f"""
    <div class="topbar">
      <div class="topbar-left">
        <p class="topbar-title">{title}</p>
        <p class="topbar-sub">{sub}</p>
      </div>
      <div class="topbar-chips">{chips}</div>
    </div>""", unsafe_allow_html=True)


MONTH_ABBR = {"jan":1,"feb":2,"mar":3,"apr":4,"may":5,"jun":6,
              "jul":7,"aug":8,"sep":9,"oct":10,"nov":11,"dec":12}

def parse_col_to_date(col, default_year=2026):
    if isinstance(col, pd.Timestamp): return col.replace(day=1), col.strftime("%d-%b-%y")
    if hasattr(col,"year") and hasattr(col,"month"):
        ts=pd.Timestamp(col); return ts.replace(day=1), ts.strftime("%d-%b-%y")
    if pd.isna(col): return None, None
    s=str(col).strip()
    if not s: return None, None
    m=re.match(r'^(\d{1,2})[/\-]([A-Za-z]{3})(?:[/\-](\d{2,4}))?$',s)
    if m:
        day_s,mon_s,yr_s=m.group(1),m.group(2).lower(),m.group(3)
        mon_num=MONTH_ABBR.get(mon_s)
        if mon_num and 1<=int(day_s)<=31:
            yr=int(yr_s)+(2000 if yr_s and len(yr_s)==2 else 0) if yr_s else default_year
            try: ts=pd.Timestamp(year=yr,month=mon_num,day=int(day_s)); return ts,s
            except: pass
    m=re.match(r'^([A-Za-z]{3})[-\'\s_](\d{2,4})$',s)
    if m:
        mon_s,yr_s=m.group(1).lower(),m.group(2); mon_num=MONTH_ABBR.get(mon_s)
        if mon_num:
            yr=int(yr_s)+(2000 if len(yr_s)==2 else 0)
            return pd.Timestamp(year=yr,month=mon_num,day=1),s
    try: ts=pd.to_datetime(s,dayfirst=True,errors="raise"); return ts,s
    except: pass
    return None, None

def infer_year(parsed): years=[p["ts"].year for p in parsed if p["ts"] is not None]; return max(set(years),key=years.count) if years else 2026

def parse_all_month_cols(cols, skip):
    cands=[c for c in cols if c not in skip]
    parsed=[]
    for col in cands:
        ts,lbl=parse_col_to_date(col)
        if ts is not None: parsed.append({"orig":col,"ts":ts,"label":lbl})
    ref=infer_year(parsed)
    if ref!=2026:
        parsed=[]
        for col in cands:
            ts,lbl=parse_col_to_date(col,default_year=ref)
            if ts is not None: parsed.append({"orig":col,"ts":ts,"label":lbl})
    parsed.sort(key=lambda x:x["ts"])
    seen,unique=[],[]
    for p in parsed:
        if p["ts"] not in seen: seen.append(p["ts"]); unique.append(p)
    return unique

def standardize_req_header(v):
    if pd.isna(v): return ""
    s=str(v).strip()
    return {"alt.":"Alt","alternative":"Alt","bom header":"BOM Header"}.get(s.lower(),s)

def detect_req_header_row(file_obj,sheet_name="Requirement",scan_rows=20):
    raw=pd.read_excel(file_obj,sheet_name=sheet_name,header=None,nrows=scan_rows)
    best_row,best_score=0,-1
    for i in range(len(raw)):
        cleaned=[standardize_req_header(x) for x in raw.iloc[i].tolist()]
        score=(10 if "BOM Header" in cleaned else 0)+(5 if "Alt" in cleaned else 0)+sum(1 for x in cleaned if parse_col_to_date(x)[0] is not None)
        if score>best_score: best_score,best_row=score,i
    if best_score<10: raise ValueError("Could not detect header row.")
    return best_row

def safe_series(df,col):
    r=df[col]; return r.iloc[:,0] if isinstance(r,pd.DataFrame) else r

def is_phantom(val): return str(val).strip()==PHANTOM
def empty_prod(): return pd.DataFrame(columns=["Component","Confirmed_Qty","Open_Production_Qty"])

def load_receipt_qty(f):
    if f is None: return pd.Series(dtype=float)
    try:
        df=pd.read_excel(f); df.columns=df.columns.str.strip()
        mat_kw=["material","component","part number","part","mat"]
        qty_kw=["gr qty","gr quantity","receipt qty","receipt quantity","received qty","quantity","qty"]
        mc=next((c for c in df.columns if any(k in c.lower() for k in mat_kw)),df.columns[0])
        qc=next((c for c in df.columns if any(k in c.lower() for k in qty_kw) and c!=mc),None)
        if qc is None: return pd.Series(dtype=float)
        df[mc]=df[mc].astype(str).str.strip()
        df[qc]=pd.to_numeric(df[qc].astype(str).str.replace(",","",regex=False).str.strip(),errors="coerce").fillna(0)
        return df.groupby(mc)[qc].sum()
    except: return pd.Series(dtype=float)


# ═══════════════════════════════════════════════════════════════
# MRP ENGINE
# ═══════════════════════════════════════════════════════════════
def run_mrp_engine(bom_bytes, req_bytes, prod_bytes, receipt_bytes):
    logs=[]; log=lambda m: logs.append(m)
    status=st.status("Running MRP engine ...",expanded=True)

    with status: st.write("► Building BOM ...")
    bom=pd.read_excel(io.BytesIO(bom_bytes)); bom.columns=bom.columns.str.strip()
    if "Alt." in bom.columns: bom=bom.rename(columns={"Alt.":"Alt"})
    bom["Level"]=pd.to_numeric(bom["Level"],errors="coerce").fillna(0).astype(int)
    bom=bom.reset_index(drop=True)
    parents,stack=[],{}
    for i in range(len(bom)):
        lvl=bom.loc[i,"Level"]; parent=bom.loc[i,"BOM Header"] if lvl==1 else stack.get(lvl-1)
        stack={k:v for k,v in stack.items() if k<=lvl}; stack[lvl]=bom.loc[i,"Component"]; parents.append(parent)
    bom["Parent"]=parents
    drop_cols=["Plant","Usage","Quantity","Unit","BOM L/T","BOM code","Item","Mat. Group","Mat. Group Desc.","Pur. Group","Pur. Group Desc.","MRP Controller","MRP Controller Desc."]
    bom=bom.drop(columns=[c for c in drop_cols if c in bom.columns],errors="ignore")
    for old,new in [("Component description","Component descriptio"),("BOM header description","BOM header descripti")]:
        if old in bom.columns: bom=bom.rename(columns={old:new})
    keep=["BOM Header","BOM header descripti","Alt","Level","Path","Parent","Component","Component descriptio","Required Qty","Base unit","Procurement type","Special procurement"]
    missing=[c for c in ["BOM Header","Level","Component","Required Qty"] if c not in bom.columns]
    if missing: st.error(f"Missing BOM columns: {missing}"); return None
    bom=bom[[c for c in keep if c in bom.columns]].copy()
    for col,default in [("Alt","0"),("Special procurement",""),("Procurement type",""),("Component descriptio","")]:
        if col not in bom.columns: bom[col]=default
    bom["Component"]=bom["Component"].astype(str).str.strip()
    bom["BOM Header"]=bom["BOM Header"].astype(str).str.strip()
    bom["Special procurement"]=bom["Special procurement"].astype(str).str.strip()
    bom["Procurement type"]=bom["Procurement type"].astype(str).str.strip()
    bom["Component descriptio"]=bom["Component descriptio"].astype(str).str.strip()
    bom["Required Qty"]=pd.to_numeric(bom["Required Qty"],errors="coerce").fillna(0)
    bom["Alt"]=pd.to_numeric(bom["Alt"],errors="coerce").fillna(0).astype(int).astype(str)

    with status: st.write("► Loading Req & Stock ...")
    req_f=io.BytesIO(req_bytes)
    hrrow=detect_req_header_row(req_f,sheet_name="Requirement"); req_f.seek(0)
    req=pd.read_excel(req_f,sheet_name="Requirement",header=None)
    req.columns=[standardize_req_header(x) for x in req.iloc[hrrow].tolist()]
    req=req.iloc[hrrow+1:].reset_index(drop=True)
    req=req.loc[:,[str(c).strip()!="" for c in req.columns]]
    req=req.loc[:,~pd.Index(req.columns).duplicated(keep="first")]
    if "BOM Header" not in req.columns: st.error("BOM Header column missing in Req file."); return None
    req["BOM Header"]=req["BOM Header"].astype(str).str.strip()
    req["Alt"]=pd.to_numeric(req.get("Alt",pd.Series(["0"]*len(req))),errors="coerce").fillna(0).astype(int).astype(str)
    parsed=parse_all_month_cols(req.columns.tolist(),{"BOM Header","Alt"})
    if not parsed: st.error("No month columns found."); return None
    rename_map={p["orig"]:p["label"] for p in parsed if p["orig"]!=p["label"]}
    if rename_map: req=req.rename(columns=rename_map)
    months=[p["label"] for p in parsed]; MONTH_ORDER={m:i for i,m in enumerate(months)}
    for m in months:
        col_data=safe_series(req,m)
        req[m]=pd.to_numeric(col_data.astype(str).str.replace(",","",regex=False).str.strip(),errors="coerce").fillna(0)
    req_f.seek(0)
    stock_raw=pd.read_excel(req_f,sheet_name="Stock",usecols=[0,1],header=0,names=["Component","Stock_Qty"])
    stock_raw=stock_raw.dropna(subset=["Component"]).copy()
    stock_raw["Component"]=stock_raw["Component"].astype(str).str.strip()
    stock_raw["Stock_Qty"]=pd.to_numeric(stock_raw["Stock_Qty"].astype(str).str.replace(",","",regex=False).str.strip(),errors="coerce").fillna(0)
    stock=stock_raw.groupby("Component")["Stock_Qty"].sum()
    receipt_qty=load_receipt_qty(io.BytesIO(receipt_bytes) if receipt_bytes else None)
    if not receipt_qty.empty:
        for comp,qty in receipt_qty.items(): stock[comp]=float(stock.get(comp,0))+float(qty)
    req_long=req.melt(id_vars=["BOM Header","Alt"],value_vars=months,var_name="Month",value_name="FG_Demand")
    req_long=req_long[req_long["FG_Demand"]>0].copy()

    with status: st.write("► Loading Production Orders ...")
    prod_summary=empty_prod()
    if prod_bytes:
        try:
            coois=pd.read_excel(io.BytesIO(prod_bytes)); coois.columns=coois.columns.str.strip()
            sc=next((c for c in coois.columns if "status" in c.lower()),None)
            mc=next((c for c in coois.columns if "material" in c.lower() and "description" not in c.lower()),None)
            oc=next((c for c in coois.columns if "order" in c.lower() and ("qty" in c.lower() or "quantity" in c.lower())),None)
            dc=next((c for c in coois.columns if "deliver" in c.lower() or ("quantity" in c.lower() and "gr" in c.lower())),None)
            cc=next((c for c in coois.columns if "confirm" in c.lower() and "quantity" in c.lower()),None)
            if all([sc,mc,oc,dc,cc]):
                coois=coois[~coois[sc].astype(str).str.contains("TECO",case=False,na=False)].copy()
                for col in [mc,oc,dc,cc]: coois[col]=(coois[col].astype(str).str.strip() if col==mc else pd.to_numeric(coois[col],errors="coerce").fillna(0))
                coois["Open_Qty"]=(coois[oc]-coois[dc]).clip(lower=0)
                prod_summary=(coois.groupby(mc,as_index=False).agg(Confirmed_Qty=(cc,"sum"),Open_Production_Qty=("Open_Qty","sum")).rename(columns={mc:"Component"}))
                prod_summary["Component"]=prod_summary["Component"].astype(str).str.strip()
        except Exception as e: log(f"Prod error: {e}")

    def get_sfrac(rows,comp_col,gross_col):
        agg=rows.groupby([comp_col,"Month","Month_Order"],as_index=False)[gross_col].sum(); sfrac={}
        for comp,grp in agg.groupby(comp_col):
            avail=float(stock.get(comp,0))
            for _,row in grp.sort_values("Month_Order").iterrows():
                g=float(row[gross_col]); sfrac[(comp,row["Month"])]=max(0.0,g-avail)/g if g>0 else 0.0; avail=max(0.0,avail-g)
        return sfrac

    def make_report(agg_df,comp_col):
        BASE=["Component","Description","Month","Gross_Requirement","Stock_Used","Shortage","Stock_Remaining"]
        if agg_df.empty: return pd.DataFrame(columns=BASE)
        results=[]
        for comp,grp in agg_df.groupby(comp_col):
            avail=float(stock.get(comp,0)); desc=grp["Desc"].iloc[0]
            for _,row in grp.sort_values("Month_Order").iterrows():
                gr=float(row["Gross"]); consumed=min(avail,gr); shortage=max(0.0,gr-avail); avail=max(0.0,avail-gr)
                results.append({"Component":comp,"Description":desc,"Month":row["Month"],"Gross_Requirement":gr,"Stock_Used":consumed,"Shortage":shortage,"Stock_Remaining":avail})
        return pd.DataFrame(results,columns=BASE)

    def applysfrac(df,gc,pc,sfrac,comp_col):
        return df.apply(lambda r:r[gc] if is_phantom(r[pc]) else r[gc]*sfrac.get((r[comp_col],r["Month"]),1.0),axis=1)

    with status: st.write("► Exploding L1–L4 ...")
    bl1=(bom[bom["Level"]==1][["BOM Header","Alt","Component","Component descriptio","Required Qty","Special procurement"]].copy()
         .rename(columns={"Component":"L1_Comp","Component descriptio":"L1_Desc","Required Qty":"L1_Qty","Special procurement":"L1_Ph"}))
    l1=req_long.merge(bl1,on=["BOM Header","Alt"],how="inner")
    l1["L1_Gross"]=l1["FG_Demand"]*l1["L1_Qty"]; l1["Month_Order"]=l1["Month"].map(MONTH_ORDER)
    l1n=l1[~l1["L1_Ph"].apply(is_phantom)].copy(); l1sf=get_sfrac(l1n,"L1_Comp","L1_Gross")
    l1["L1_Eff"]=applysfrac(l1,"L1_Gross","L1_Ph",l1sf,"L1_Comp")
    l1a=(l1n.groupby(["L1_Comp","L1_Desc","Month","Month_Order"],as_index=False)["L1_Gross"].sum().rename(columns={"L1_Comp":"Component","L1_Desc":"Desc","L1_Gross":"Gross"}))
    r1=make_report(l1a,"Component")

    bl2=(bom[bom["Level"]==2][["BOM Header","Alt","Parent","Component","Component descriptio","Required Qty","Special procurement"]].copy()
         .rename(columns={"Parent":"L1_Comp","Component":"L2_Comp","Component descriptio":"L2_Desc","Required Qty":"L2_Qty","Special procurement":"L2_Ph"}))
    l2=l1.merge(bl2,on=["BOM Header","Alt","L1_Comp"],how="inner")
    l2["L2_Gross"]=l2["L1_Eff"]*l2["L2_Qty"]
    l2n=l2[~l2["L2_Ph"].apply(is_phantom)].copy(); l2sf=get_sfrac(l2n,"L2_Comp","L2_Gross")
    l2["L2_Eff"]=applysfrac(l2,"L2_Gross","L2_Ph",l2sf,"L2_Comp")
    l2a=(l2n.groupby(["L2_Comp","L2_Desc","Month","Month_Order"],as_index=False)["L2_Gross"].sum().rename(columns={"L2_Comp":"Component","L2_Desc":"Desc","L2_Gross":"Gross"}))
    r2=make_report(l2a,"Component")

    bl3=(bom[bom["Level"]==3][["BOM Header","Alt","Parent","Component","Component descriptio","Required Qty","Special procurement"]].copy()
         .rename(columns={"Parent":"L2_Comp","Component":"L3_Comp","Component descriptio":"L3_Desc","Required Qty":"L3_Qty","Special procurement":"L3_Ph"}))
    l3=l2.merge(bl3,on=["BOM Header","Alt","L2_Comp"],how="inner")
    l3["L3_Gross"]=l3.apply(lambda r:r["L2_Eff"] if is_phantom(r["L3_Ph"]) else r["L2_Eff"]*r["L3_Qty"],axis=1)
    l3n=l3[~l3["L3_Ph"].apply(is_phantom)].copy(); l3sf=get_sfrac(l3n,"L3_Comp","L3_Gross")
    l3["L3_Eff"]=applysfrac(l3,"L3_Gross","L3_Ph",l3sf,"L3_Comp")
    l3a=(l3n.groupby(["L3_Comp","L3_Desc","Month","Month_Order"],as_index=False)["L3_Gross"].sum().rename(columns={"L3_Comp":"Component","L3_Desc":"Desc","L3_Gross":"Gross"}))
    r3=make_report(l3a,"Component")

    bl4=(bom[bom["Level"]==4][["BOM Header","Alt","Parent","Component","Component descriptio","Required Qty","Special procurement"]].copy()
         .rename(columns={"Parent":"L3_Comp","Component":"L4_Comp","Component descriptio":"L4_Desc","Required Qty":"L4_Qty","Special procurement":"L4_Ph"}))
    l4=l3.merge(bl4,on=["BOM Header","Alt","L3_Comp"],how="inner")
    l4["L4_Gross"]=l4["L3_Eff"]*l4["L4_Qty"]
    l4a=(l4.groupby(["L4_Comp","L4_Desc","Month","Month_Order"],as_index=False)["L4_Gross"].sum().rename(columns={"L4_Comp":"Component","L4_Desc":"Desc","L4_Gross":"Gross"}))
    r4=make_report(l4a,"Component")

    with status: st.write("► Building pivot output ...")
    status.update(label="MRP complete ✅",state="complete",expanded=False)

    final=pd.concat([r1,r2,r3,r4],ignore_index=True)
    all_comps=final[["Component","Description"]].drop_duplicates(subset="Component").copy()
    pg=(final.pivot_table(index=["Component","Description"],columns="Month",values="Gross_Requirement",aggfunc="sum",fill_value=0).reset_index())
    pivot=all_comps.merge(pg,on=["Component","Description"],how="left").fillna(0)
    mcols=[m for m in months if m in pivot.columns]
    if mcols: pivot[mcols]=pivot[mcols].cumsum(axis=1)
    bm=bom[["Component","Procurement type","Special procurement"]].drop_duplicates(subset="Component")
    sd=stock.reset_index().rename(columns={"Stock_Qty":"Stock"})
    pivot=pivot.merge(bm,on="Component",how="left").merge(sd,on="Component",how="left").merge(prod_summary,on="Component",how="left")
    for c,d in [("Procurement type",""),("Special procurement",""),("Stock",0),("Confirmed_Qty",0),("Open_Production_Qty",0)]:
        pivot[c]=pivot[c].fillna(d)
    for m in mcols: pivot[m]=pivot["Stock"]-pivot[m]
    if not receipt_qty.empty:
        rq=receipt_qty.reset_index(); rq.columns=["Component","Receipt_Qty"]
        pivot=pivot.merge(rq,on="Component",how="left"); pivot["Receipt_Qty"]=pivot["Receipt_Qty"].fillna(0)
        extra=["Receipt_Qty"]
    else: extra=[]
    pivot=pivot.rename(columns={"Description":"Component descri"})
    fc=["Component","Component descri","Procurement type","Special procurement","Confirmed_Qty","Open_Production_Qty","Stock"]+extra+mcols
    for c in fc:
        if c not in pivot.columns: pivot[c]=0 if c in mcols+["Confirmed_Qty","Open_Production_Qty","Stock","Receipt_Qty"] else ""
    pivot=pivot[fc].sort_values("Component").reset_index(drop=True)

    with st.expander("Run log"):
        for l in logs: st.text(l)

    return dict(bom=bom,req=req,months=months,stock=stock,prod_summary=prod_summary,
                result_l1=r1,result_l2=r2,result_l3=r3,result_l4=r4,
                raw_l1=l1a,raw_l2=l2a,raw_l3=l3a,raw_l4=l4a,
                receipt_qty=receipt_qty,pivot=pivot,month_cols=mcols)


# ═══════════════════════════════════════════════════════════════
# SEGMENT CAPACITY ENGINE
# ═══════════════════════════════════════════════════════════════
def load_seg_imp(f):
    xl=pd.ExcelFile(f); sheets=xl.sheet_names
    imp_sh=next((s for s in sheets if "import" in s.lower()),sheets[0])
    imp=pd.read_excel(f,sheet_name=imp_sh,header=0); imp.columns=[str(c).strip() for c in imp.columns]
    cc=imp.columns[0]; imp[cc]=imp[cc].astype(str).str.strip()
    rm_col=next((c for c in imp.columns if "rm" in c.lower() or "group" in c.lower()),None)
    rm_map={}
    if rm_col: imp[rm_col]=imp[rm_col].astype(str).str.strip(); rm_map=dict(zip(imp[cc],imp[rm_col]))
    import_parts=sorted(imp[cc].dropna().unique())
    seg_sh=next((s for s in sheets if "seg" in s.lower()),sheets[min(1,len(sheets)-1)])
    seg=pd.read_excel(f,sheet_name=seg_sh,header=0); seg.columns=[str(c).strip() for c in seg.columns]
    cm={seg.columns[0]:"Segment",seg.columns[1]:"FG_Code",seg.columns[2]:"IDU"}
    if len(seg.columns)>=4: cm[seg.columns[3]]="Compatible_ODU"
    seg=seg.rename(columns=cm)
    if "Compatible_ODU" not in seg.columns: seg["Compatible_ODU"]=""
    for c in ("Segment","FG_Code","IDU","Compatible_ODU"): seg[c]=seg[c].astype(str).str.strip()
    seg=seg[seg["Segment"].notna()&(seg["Segment"]!="")&(seg["Segment"]!="nan")&
            seg["FG_Code"].notna()&(seg["FG_Code"]!="")&(seg["FG_Code"]!="nan")&
            seg["IDU"].notna()&(seg["IDU"]!="")&(seg["IDU"]!="nan")].copy().reset_index(drop=True)
    return import_parts,seg,rm_map

def explode_seg(hdr,bom,tset):
    alts=sorted(bom[bom["BOM Header"]==hdr]["Alt"].unique())
    if not alts: return {}
    sub=bom[(bom["BOM Header"]==hdr)&(bom["Alt"]==alts[0])]
    cmap=defaultdict(list)
    for _,r in sub.iterrows(): cmap[r["Parent"]].append(r)
    res={}
    def dfs(node,acc,d=0):
        if d>12: return
        for r in cmap.get(node,[]):
            comp=r["Component"]; qty=float(r["Required Qty"]); sp=r["Special procurement"]
            eff=acc*(1.0 if sp==PHANTOM else qty)
            if comp in tset: res[comp]=res.get(comp,0)+eff
            dfs(comp,eff,d+1)
    dfs(hdr,1.0); return res

def run_segment(bom,stock,seg_bytes,active_rm=None):
    f=io.BytesIO(seg_bytes)
    status=st.status("Running Segment Capacity ...",expanded=True)
    with status: st.write("► Loading data ...")
    import_parts,seg_df,rm_map=load_seg_imp(f)
    all_rm=sorted(set(rm_map.values())) if rm_map else []
    if active_rm is None: active_rm=all_rm
    if rm_map and active_rm: import_parts=[p for p in import_parts if rm_map.get(p,"Unknown") in active_rm]
    tset=set(import_parts); bhdrs=set(bom["BOM Header"].unique())
    dc="BOM header descripti" if "BOM header descripti" in bom.columns else None
    dmap=(bom[["BOM Header",dc]].drop_duplicates("BOM Header").set_index("BOM Header")[dc].to_dict()) if dc else {}
    with status: st.write("► Exploding BOMs ...")
    idu_r={}; odu_r={}; nib=[]
    for idu in seg_df["IDU"].unique():
        if idu in bhdrs: idu_r[idu]=explode_seg(idu,bom,tset)
        else: nib.append(f"IDU {idu}")
    for odu in seg_df["Compatible_ODU"].unique():
        if not odu or odu=="nan": continue
        if odu in bhdrs: odu_r[odu]=explode_seg(odu,bom,tset)
        else: nib.append(f"ODU {odu}")
    if nib: st.warning(f"Not in BOM: {', '.join(sorted(set(nib)))}")
    with status: st.write("► LP optimisation ...")
    fg_list=[]; fgseg={}; fgidu={}; fgodu={}; fgcomb={}; skipped=[]
    for _,row in seg_df.iterrows():
        fg=row["FG_Code"]; seg=row["Segment"]; idu=row["IDU"]; odu=row["Compatible_ODU"]
        if not odu or odu=="nan": skipped.append(f"{fg}: no ODU"); continue
        ir=idu_r.get(idu,{}); or_=odu_r.get(odu,{})
        if not ir and not or_: skipped.append(f"{fg}: no import parts"); continue
        ap=set(ir)|set(or_); comb={p:ir.get(p,0)+or_.get(p,0) for p in ap if ir.get(p,0)+or_.get(p,0)>0}
        fg_list.append(fg); fgseg[fg]=seg; fgidu[fg]=idu; fgodu[fg]=odu; fgcomb[fg]=comb
    if not fg_list: st.error("No valid FG codes."); return None
    n=len(fg_list); cp=[]; AR=[]; br=[]
    for p in import_parts:
        rv=[fgcomb[fg].get(p,0) for fg in fg_list]
        if any(v>0 for v in rv): cp.append(p); AR.append(rv); br.append(float(stock.get(p,0)))
    A=np.array(AR,dtype=float); b=np.array(br,dtype=float)
    res=linprog(-np.ones(n),A_ub=A,b_ub=b,bounds=[(0,None)]*n,method="highs")
    if res.status not in (0,1): st.error(f"LP failed: {res.message}"); return None
    ai=np.floor(res.x).astype(int); total=int(ai.sum())
    fg_res=[]
    for fg,qty in zip(fg_list,ai):
        cq=fgcomb[fg]; lp="—"; lr=float("inf")
        for p,req in cq.items():
            if req>0:
                r=float(stock.get(p,0))/req
                if r<lr: lr,lp=r,p
        fg_res.append({"Segment":fgseg[fg],"FG_Code":fg,"FG_Desc":dmap.get(fg,""),"IDU":fgidu[fg],
                       "IDU_Desc":dmap.get(fgidu[fg],""),"Compatible_ODU":fgodu[fg],
                       "ODU_Desc":dmap.get(fgodu[fg],""),"Max_Sets":int(qty),"Limiting_Part":lp,
                       "Limiting_Stock":int(stock.get(lp,0)) if lp!="—" else 0,"combined_req":cq})
    st_tot=defaultdict(int); st_fg=defaultdict(list)
    for f2 in fg_res: st_tot[f2["Segment"]]+=f2["Max_Sets"]; st_fg[f2["Segment"]].append(f2)
    sdata={}
    for seg,fgs2 in st_fg.items():
        ap=set(p for f2 in fgs2 for p in f2["combined_req"])
        sdata[seg]={"combined_req":{p:max(f2["combined_req"].get(p,0) for f2 in fgs2) for p in ap},
                    "idu_count":len({f2["IDU"] for f2 in fgs2}),"odu_count":len({f2["Compatible_ODU"] for f2 in fgs2})}
    segs=list(sdata.keys()); sai=np.array([st_tot[s] for s in segs],dtype=int)
    pu={}
    for p,rv,av in zip(cp,AR,br):
        used=sum(rv[j]*ai[j] for j in range(n))
        pu[p]={"stock":av,"used":used,"remain":max(0,av-used),"pct":round(100*used/av,1) if av>0 else 0}
    with status: st.write("► Done.")
    status.update(label="Segment Capacity ✅",state="complete",expanded=False)
    return dict(segs=segs,alloc_int=sai,total_sets=total,segments_data=sdata,fg_results=fg_res,
                import_parts=import_parts,constrained_parts=cp,part_usage=pu,stock=stock,
                skipped_segs=skipped,rm_map=rm_map,active_rm_groups=active_rm)


# ═══════════════════════════════════════════════════════════════
# AGING ENGINE
# ═══════════════════════════════════════════════════════════════
AGING_BUCKETS   = ["0-15 Qty","16-30 Qty","31-60 Qty","61-90 Qty",
                   "91-120 Qty","121-150 Qty","151-180 Qty","181-360 Qty","Over361 Qty"]
AGING_VAL_BKTS  = ["0-15 Value","16-30 Value","31-60 Value","61-90 Value",
                   "91-120 Value","121-150 Value","151-180 Value","181-360 Value","Over361 Value"]

def load_aging(f):
    """
    Load aging file, consolidate storage-location rows → one row per material.
    Keeps both qty AND value buckets for accurate value computation.
    """
    df = pd.read_excel(f)
    df.columns = [str(c).strip() for c in df.columns]

    # Normalise key column names
    rename = {}
    for c in df.columns:
        cl = c.lower().replace(" ", "")
        if cl == "material":
            rename[c] = "Material"
        elif "description" in cl and "material" in cl:
            rename[c] = "Material Description"
        elif cl == "materialtype":
            rename[c] = "Material Type"
        elif "movingaverage" in cl or cl == "map":
            rename[c] = "MAP"
    df = df.rename(columns=rename)

    # Ensure all qty and value bucket columns exist and are numeric
    for col in AGING_BUCKETS + AGING_VAL_BKTS:
        if col not in df.columns:
            df[col] = 0.0
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    if "MAP" in df.columns:
        df["MAP"] = pd.to_numeric(df["MAP"], errors="coerce").fillna(0)

    # Group by Material (consolidate storage locations → one row per component)
    agg = {c: "sum" for c in AGING_BUCKETS + AGING_VAL_BKTS}
    if "Material Description" in df.columns: agg["Material Description"] = "first"
    if "MAP"                  in df.columns: agg["MAP"]                  = "first"
    if "Material Type"        in df.columns: agg["Material Type"]        = "first"

    return df.groupby("Material", as_index=False).agg(agg)


def compute_bom_consumption(bom_bytes, req_bytes, phantom_code="50"):
    """
    Standalone BOM explosion to get GROSS component requirement per month.
    Returns: dict  {material_code: {month_label: gross_qty}}
    Uses the same alt-BOM-aware explosion as the main MRP engine,
    but skips stock netting — pure gross consumption only.
    """
    import io, re

    MONTH_ABBR_L = {"jan":1,"feb":2,"mar":3,"apr":4,"may":5,"jun":6,
                    "jul":7,"aug":8,"sep":9,"oct":10,"nov":11,"dec":12}

    def _parse_col(col, default_year=2026):
        if isinstance(col, pd.Timestamp): return col.replace(day=1), col.strftime("%b-%y")
        if hasattr(col, "year"):
            ts = pd.Timestamp(col); return ts.replace(day=1), ts.strftime("%b-%y")
        if pd.isna(col): return None, None
        s = str(col).strip()
        m = re.match(r'^([A-Za-z]{3})[-\'\s_](\d{2,4})$', s)
        if m:
            mon_s, yr_s = m.group(1).lower(), m.group(2)
            mn = MONTH_ABBR_L.get(mon_s)
            if mn:
                yr = int(yr_s) + (2000 if len(yr_s) == 2 else 0)
                return pd.Timestamp(year=yr, month=mn, day=1), s
        try:
            ts = pd.to_datetime(s, dayfirst=True, errors="raise")
            return ts.replace(day=1), ts.strftime("%b-%y")
        except:
            return None, None

    def _std(v):
        if pd.isna(v): return ""
        s = str(v).strip()
        return {"alt.": "Alt", "alternative": "Alt", "bom header": "BOM Header"}.get(s.lower(), s)

    def _detect_hrow(f_bytes, sheet="Requirement", scan=20):
        raw = pd.read_excel(io.BytesIO(f_bytes), sheet_name=sheet, header=None, nrows=scan)
        best_r, best_s = 0, -1
        for i in range(len(raw)):
            cleaned = [_std(x) for x in raw.iloc[i].tolist()]
            score = (10 if "BOM Header" in cleaned else 0) + (5 if "Alt" in cleaned else 0) \
                  + sum(1 for x in cleaned if _parse_col(x)[0] is not None)
            if score > best_s: best_s, best_r = score, i
        if best_s < 10:
            raise ValueError("Could not detect header row in Requirement sheet.")
        return best_r

    # ── BOM ──────────────────────────────────────────────────────
    bom = pd.read_excel(io.BytesIO(bom_bytes))
    bom.columns = bom.columns.str.strip()
    if "Alt." in bom.columns: bom = bom.rename(columns={"Alt.": "Alt"})
    bom["Level"] = pd.to_numeric(bom["Level"], errors="coerce").fillna(0).astype(int)
    bom["Component"]      = bom["Component"].astype(str).str.strip()
    bom["BOM Header"]     = bom["BOM Header"].astype(str).str.strip()
    bom["Special procurement"] = bom.get("Special procurement", pd.Series([""] * len(bom))).astype(str).str.strip()
    bom["Required Qty"]   = pd.to_numeric(bom["Required Qty"], errors="coerce").fillna(0)
    bom["Alt"]            = pd.to_numeric(bom.get("Alt", pd.Series([0]*len(bom))), errors="coerce").fillna(0).astype(int).astype(str)

    # Build Parent column
    parents, stack = [], {}
    for i in range(len(bom)):
        lvl = bom.loc[i, "Level"]
        parent = bom.loc[i, "BOM Header"] if lvl == 1 else stack.get(lvl - 1)
        stack = {k: v for k, v in stack.items() if k <= lvl}
        stack[lvl] = bom.loc[i, "Component"]
        parents.append(parent)
    bom["Parent"] = parents

    # ── Requirement ───────────────────────────────────────────────
    hrrow = _detect_hrow(req_bytes)
    req   = pd.read_excel(io.BytesIO(req_bytes), sheet_name="Requirement", header=None)
    req.columns = [_std(x) for x in req.iloc[hrrow].tolist()]
    req   = req.iloc[hrrow + 1:].reset_index(drop=True)
    req   = req.loc[:, [str(c).strip() != "" for c in req.columns]]
    req   = req.loc[:, ~pd.Index(req.columns).duplicated(keep="first")]
    req["BOM Header"] = req["BOM Header"].astype(str).str.strip()
    req["Alt"]        = pd.to_numeric(req.get("Alt", pd.Series(["0"] * len(req))),
                                      errors="coerce").fillna(0).astype(int).astype(str)

    # Parse month columns
    skip = {"BOM Header", "Alt"}
    cands = [c for c in req.columns if c not in skip]
    parsed = []
    for col in cands:
        ts, lbl = _parse_col(col)
        if ts is not None:
            parsed.append({"orig": col, "ts": ts, "label": lbl})
    parsed.sort(key=lambda x: x["ts"])
    # deduplicate
    seen, unique = [], []
    for p in parsed:
        if p["ts"] not in seen: seen.append(p["ts"]); unique.append(p)
    parsed = unique

    rename_map = {p["orig"]: p["label"] for p in parsed if p["orig"] != p["label"]}
    if rename_map: req = req.rename(columns=rename_map)
    months = [p["label"] for p in parsed]
    MONTH_ORDER = {m: i for i, m in enumerate(months)}

    for m in months:
        col_data = req[m]
        if isinstance(col_data, pd.DataFrame): col_data = col_data.iloc[:, 0]
        req[m] = pd.to_numeric(col_data.astype(str).str.replace(",", "", regex=False).str.strip(),
                               errors="coerce").fillna(0)

    req_long = req.melt(id_vars=["BOM Header", "Alt"], value_vars=months,
                        var_name="Month", value_name="FG_Demand")
    req_long = req_long[req_long["FG_Demand"] > 0].copy()
    req_long["Month_Order"] = req_long["Month"].map(MONTH_ORDER)

    def _is_ph(val): return str(val).strip() == phantom_code

    # ── BOM explosion helpers ─────────────────────────────────────
    def _explode(bom_level, join_cols, parent_col, child_comp_col, child_qty_col,
                 child_ph_col, child_desc_col, demand_col, prev_df):
        bl = (bom[bom["Level"] == bom_level]
              [[*join_cols, "Parent", "Component", "Component descriptio",
                "Required Qty", "Special procurement"]].copy()
              .rename(columns={"Parent": parent_col, "Component": child_comp_col,
                               "Component descriptio": child_desc_col,
                               "Required Qty": child_qty_col,
                               "Special procurement": child_ph_col}))
        merged = prev_df.merge(bl, on=list(join_cols), how="inner")
        merged[demand_col] = merged[demand_col.replace("_Gross","_Eff") if bom_level > 1 else "FG_Demand"] \
                             * merged[child_qty_col]
        # Phantom pass-through: if phantom, set gross = parent effective qty
        if bom_level > 1:
            eff_src = demand_col.replace("_Gross", "_Eff")
            merged.loc[merged[child_ph_col].apply(_is_ph), demand_col] = \
                merged.loc[merged[child_ph_col].apply(_is_ph), eff_src]

        # Compute effective (stock-free — just gross for non-phantoms)
        eff_col = demand_col.replace("_Gross", "_Eff")
        merged[eff_col] = merged[demand_col]  # no stock netting for aging consumption

        # Aggregate non-phantom results
        non_ph = merged[~merged[child_ph_col].apply(_is_ph)].copy()
        agg = (non_ph.groupby([child_comp_col, child_desc_col, "Month", "Month_Order"],
                               as_index=False)[demand_col].sum()
               .rename(columns={child_comp_col: "Component", child_desc_col: "Desc",
                                demand_col: "Gross"}))
        return merged, agg

    # L1
    l1, a1 = _explode(1, ["BOM Header", "Alt"], None, "L1_Comp", "L1_Qty",
                      "L1_Ph", "L1_Desc", "L1_Gross", req_long)
    # Fix: L1 parent col doesn't exist in join, use BOM Header directly
    bl1 = (bom[bom["Level"] == 1]
           [["BOM Header", "Alt", "Component", "Component descriptio",
             "Required Qty", "Special procurement"]].copy()
           .rename(columns={"Component": "L1_Comp", "Component descriptio": "L1_Desc",
                            "Required Qty": "L1_Qty", "Special procurement": "L1_Ph"}))
    l1 = req_long.merge(bl1, on=["BOM Header", "Alt"], how="inner")
    l1["L1_Gross"] = l1["FG_Demand"] * l1["L1_Qty"]
    l1["L1_Eff"]   = l1["L1_Gross"]
    a1 = (l1[~l1["L1_Ph"].apply(_is_ph)]
          .groupby(["L1_Comp", "L1_Desc", "Month", "Month_Order"], as_index=False)["L1_Gross"]
          .sum().rename(columns={"L1_Comp": "Component", "L1_Desc": "Desc", "L1_Gross": "Gross"}))

    # L2
    bl2 = (bom[bom["Level"] == 2]
           [["BOM Header", "Alt", "Parent", "Component", "Component descriptio",
             "Required Qty", "Special procurement"]].copy()
           .rename(columns={"Parent": "L1_Comp", "Component": "L2_Comp",
                            "Component descriptio": "L2_Desc",
                            "Required Qty": "L2_Qty", "Special procurement": "L2_Ph"}))
    l2 = l1.merge(bl2, on=["BOM Header", "Alt", "L1_Comp"], how="inner")
    l2["L2_Gross"] = l2["L1_Eff"] * l2["L2_Qty"]
    l2["L2_Eff"]   = l2["L2_Gross"]
    a2 = (l2[~l2["L2_Ph"].apply(_is_ph)]
          .groupby(["L2_Comp", "L2_Desc", "Month", "Month_Order"], as_index=False)["L2_Gross"]
          .sum().rename(columns={"L2_Comp": "Component", "L2_Desc": "Desc", "L2_Gross": "Gross"}))

    # L3
    bl3 = (bom[bom["Level"] == 3]
           [["BOM Header", "Alt", "Parent", "Component", "Component descriptio",
             "Required Qty", "Special procurement"]].copy()
           .rename(columns={"Parent": "L2_Comp", "Component": "L3_Comp",
                            "Component descriptio": "L3_Desc",
                            "Required Qty": "L3_Qty", "Special procurement": "L3_Ph"}))
    l3 = l2.merge(bl3, on=["BOM Header", "Alt", "L2_Comp"], how="inner")
    l3["L3_Gross"] = l3.apply(
        lambda r: r["L2_Eff"] if _is_ph(r["L3_Ph"]) else r["L2_Eff"] * r["L3_Qty"], axis=1)
    l3["L3_Eff"] = l3["L3_Gross"]
    a3 = (l3[~l3["L3_Ph"].apply(_is_ph)]
          .groupby(["L3_Comp", "L3_Desc", "Month", "Month_Order"], as_index=False)["L3_Gross"]
          .sum().rename(columns={"L3_Comp": "Component", "L3_Desc": "Desc", "L3_Gross": "Gross"}))

    # L4
    bl4 = (bom[bom["Level"] == 4]
           [["BOM Header", "Alt", "Parent", "Component", "Component descriptio",
             "Required Qty", "Special procurement"]].copy()
           .rename(columns={"Parent": "L3_Comp", "Component": "L4_Comp",
                            "Component descriptio": "L4_Desc",
                            "Required Qty": "L4_Qty", "Special procurement": "L4_Ph"}))
    l4 = l3.merge(bl4, on=["BOM Header", "Alt", "L3_Comp"], how="inner")
    l4["L4_Gross"] = l4["L3_Eff"] * l4["L4_Qty"]
    a4 = (l4.groupby(["L4_Comp", "L4_Desc", "Month", "Month_Order"], as_index=False)["L4_Gross"]
          .sum().rename(columns={"L4_Comp": "Component", "L4_Desc": "Desc", "L4_Gross": "Gross"}))

    # Combine all levels and sum gross per component per month
    all_levels = pd.concat([a1, a2, a3, a4], ignore_index=True)
    combined   = (all_levels.groupby(["Component", "Month"], as_index=False)["Gross"].sum())

    # Build consumption dict  {material: {month_label: gross_qty}}
    cons = {}
    for _, row in combined.iterrows():
        mat = str(row["Component"]).strip()
        mon = str(row["Month"]).strip()
        qty = float(row["Gross"])
        if qty > 0:
            if mat not in cons: cons[mat] = {}
            cons[mat][mon] = cons[mat].get(mon, 0) + qty

    return cons, months


def load_receipts(f):
    """
    Load month-wise receipt file.
    Format: Component | May-26 | Jun-26 | Jul-26 | Aug-26 ...
    Returns: dict {material: {month_label: receipt_qty}}
    """
    df = pd.read_excel(f)
    df.columns = [str(c).strip() for c in df.columns]

    # First column = Component/Material
    mat_col = df.columns[0]
    month_cols = df.columns[1:]

    receipts = {}
    for _, row in df.iterrows():
        mat = str(row[mat_col]).strip()
        if not mat or mat.lower() in ("nan", "none", ""): continue
        for col in month_cols:
            qty = pd.to_numeric(row[col], errors="coerce")
            if pd.isna(qty) or qty <= 0: continue
            # Normalise column label to Mon-YY
            try:
                ts = pd.Timestamp(col).replace(day=1)
                lbl = ts.strftime("%b-%y")
            except:
                try:
                    ts = pd.to_datetime(str(col), dayfirst=True).replace(day=1)
                    lbl = ts.strftime("%b-%y")
                except:
                    lbl = str(col).strip()
            if mat not in receipts: receipts[mat] = {}
            receipts[mat][lbl] = receipts[mat].get(lbl, 0) + float(qty)
    return receipts


def project_aging(aging_df, base_date, prod_cons, months_list, receipts=None):
    """
    Aging Opening Inventory Projection
    ────────────────────────────────────────────────────────────────
    Snapshot date = base_date (e.g. May-01-2026).
    Aging buckets represent stock age AS OF the snapshot date.

    Bucket index in AGING_BUCKETS:
      0: 0-15 d   1: 16-30 d   2: 31-60 d   3: 61-90 d
      4: 91-120d  5: 121-150d  6: 151-180d  7: 181-360d  8: Over361d

    Opening Aging on snapshot month (off=0):
      Pool  = buckets[4:]   → already ≥ 90 days
      Less  = nothing (baseline)
      Plus  = nothing

    Jun-1 opening (off=1, snapshot=May-1):
      Pool  = buckets[3:]   → 61-90 day stock will be 91-120 days by Jun-1
      Less  = May consumption (months BEFORE Jun)
      Plus  = May receipts not consumed

    Jul-1 opening (off=2):
      Pool  = buckets[2:]   → 31-60 day stock will be 91+ by Jul-1
      Less  = May + Jun cumulative consumption
      Plus  = May + Jun cumulative receipts not consumed

    Aug-1 opening (off=3):
      Pool  = ALL buckets   → even 0-15 day stock will be 90+ by Aug-1
      Less  = May + Jun + Jul cumulative consumption
      Plus  = May + Jun + Jul cumulative receipts not consumed

    Sep-1+ opening (off≥3):
      Pool  = ALL buckets   (same as Aug — all buckets exhausted)
      Less  = all prior months cumulative consumption
      Plus  = all prior months cumulative receipts not consumed

    KEY RULES:
    • Consumption deducted = all months BEFORE this opening (off months back)
      i.e. for off=1 (Jun opening) deduct only May (1 month before)
    • Receipts added = same prior months as consumption
      Receipt qty valued at MAP. Only net-positive receipts (receipt > consumption
      for that material) contribute to aging.
    • Aging Value:
        off=0 → actual SAP value columns (sum of 91-120 Value + …)
        off>0 → Aging_Qty × MAP
    ────────────────────────────────────────────────────────────────
    """
    if receipts is None:
        receipts = {}

    base_ts = pd.Timestamp(base_date)

    def _month_offset(label):
        try:    ts = pd.to_datetime(label, format="%b-%y")
        except:
            try: ts = pd.to_datetime(label).replace(day=1)
            except: return 0
        return (ts.year - base_ts.year) * 12 + (ts.month - base_ts.month)

    offsets = [max(0, _month_offset(m)) for m in months_list]

    # Bucket index where aging pool starts for a given month-offset
    # off=0 → idx 4 (91-120+)
    # off=1 → idx 3 (61-90+)
    # off=2 → idx 2 (31-60+)
    # off≥3 → idx 0 (ALL — even 0-15 day stock will be 90+ days old)
    def _aging_start_idx(off): return max(0, 4 - off) if off < 4 else 0

    records = []
    for _, row in aging_df.iterrows():
        mat   = str(row["Material"]).strip()
        desc  = str(row.get("Material Description", ""))
        mtype = str(row.get("Material Type", ""))
        mapx  = float(row.get("MAP", 0) or 0)

        bkts_q = [float(row.get(b, 0) or 0) for b in AGING_BUCKETS]
        bkts_v = [float(row.get(b, 0) or 0) for b in AGING_VAL_BKTS]

        mcons  = prod_cons.get(mat, {})
        mrec   = receipts.get(mat, {})

        # Build cumulative consumption and receipts month by month
        # We track cumulatives up to (but NOT including) the current opening month
        # i.e. for off=1 (Jun opening) → deduct only months[0] (May)
        cum_cons = 0.0
        cum_rec  = 0.0

        for mi, ml in enumerate(months_list):
            off = offsets[mi]
            si  = _aging_start_idx(off)

            # ── For off=0 (snapshot/current month): no prior months to deduct ──
            # ── For off>0: deduct all months BEFORE this one (index 0..mi-1) ──
            # We accumulate as we iterate, so cum_cons/cum_rec at start of this
            # iteration already holds sum of months[0..mi-1]. Correct!

            aging_pool_qty = sum(bkts_q[si:])
            aging_pool_val = sum(bkts_v[si:])

            # Newly crossing 90-day threshold this opening
            newly_aging = bkts_q[si] if (off > 0 and si < len(bkts_q)) else 0.0

            # Net receipts (only receipts exceeding consumption matter for aging)
            net_receipt = max(0.0, cum_rec - cum_cons)

            # Net aging qty
            # = pool qty - cumulative consumption + net receipts (uncollected)
            aging_qty = max(0.0, aging_pool_qty - cum_cons + net_receipt)

            # Aging value
            if off == 0:
                val_rate = (aging_pool_val / aging_pool_qty) if aging_pool_qty > 0 else mapx
                aging_val = round(aging_qty * val_rate, 2)
            else:
                aging_val = round(aging_qty * mapx, 2) if mapx > 0 else 0.0

            turning_next = bkts_q[si - 1] if si > 0 else 0.0

            records.append({
                "Material":                   mat,
                "Description":                desc,
                "Material Type":              mtype,
                "Opening Month":              ml,
                "Aging Pool Qty":             round(aging_pool_qty, 2),
                "Newly Aging This Month":     round(newly_aging, 2),
                "Month BOM Consumption":      round(float(mcons.get(ml, 0)), 2),
                "Cumulative BOM Consumption": round(cum_cons, 2),
                "Month Receipt Qty":          round(float(mrec.get(ml, 0)), 2),
                "Cumulative Receipt Qty":     round(cum_rec, 2),
                "Net Receipt (unused)":       round(net_receipt, 2),
                "Aging Qty (>=91d)":          round(aging_qty, 2),
                "Aging Value (Rs)":           aging_val,
                "Turning Aging Next Month":   round(turning_next, 2),
            })

            # NOW accumulate this month's consumption and receipts
            # so next iteration has correct prior-month totals
            cum_cons += float(mcons.get(ml, 0))
            cum_rec  += float(mrec.get(ml, 0))

    return pd.DataFrame(records)


# ═══════════════════════════════════════════════════════════════
# COMPONENT SEARCH (used inside MRP page)
# ═══════════════════════════════════════════════════════════════
def show_search(bom,req_df,months,stock,prod_summary):
    sec("Component Search & BOM Ancestry")
    sc,_=st.columns([2,3])
    with sc:
        comp=st.text_input("Component code",placeholder="e.g. 0010748458",label_visibility="collapsed",key="cs").strip()
    if not comp: return
    r=st.session_state.get("mrp_results",{})
    found_in={}
    for lbl in ["result_l1","result_l2","result_l3","result_l4"]:
        df=r.get(lbl)
        if df is not None and not df.empty and comp in df["Component"].values:
            found_in[lbl]=df[df["Component"]==comp].copy()
    bom_in=bom[bom["Component"]==comp]
    if bom_in.empty and not found_in: st.warning(f"`{comp}` not found."); return
    desc=bom_in["Component descriptio"].iloc[0] if not bom_in.empty else "—"
    ptype=bom_in["Procurement type"].iloc[0] if not bom_in.empty else "—"
    sp=bom_in["Special procurement"].iloc[0] if not bom_in.empty else "—"
    stk=float(stock.get(comp,0))
    pr=prod_summary[prod_summary["Component"]==comp]
    cq=float(pr["Confirmed_Qty"].iloc[0]) if not pr.empty else 0
    oq=float(pr["Open_Production_Qty"].iloc[0]) if not pr.empty else 0
    ph=" · 🔶 PHANTOM" if str(sp).strip()==PHANTOM else ""
    st.markdown(f"**`{comp}`** — {desc}{ph}")
    c1,c2,c3,c4,c5=st.columns(5)
    c1.metric("Stock",f"{stk:,.3f}"); c2.metric("Confirmed",f"{cq:,.0f}")
    c3.metric("Open prod",f"{oq:,.0f}"); c4.metric("Proc type",ptype); c5.metric("Sp proc",sp if sp not in ("","nan") else "—")
    if found_in:
        all_rows=pd.concat(found_in.values(),ignore_index=True)
        mo={m:i for i,m in enumerate(months)}
        monthly=(all_rows.groupby("Month",as_index=False)
                 .agg(Gross_Requirement=("Gross_Requirement","sum"),Stock_Used=("Stock_Used","sum"),
                      Shortage=("Shortage","sum"),Stock_Remaining=("Stock_Remaining","last")))
        monthly["_o"]=monthly["Month"].map(mo); monthly=monthly.sort_values("_o").drop(columns="_o")
        monthly["Cumul"]=monthly["Gross_Requirement"].cumsum(); monthly["Net"]=stk-monthly["Cumul"]
        def hl(row):
            if row["Net"]<0: return ["background-color:#fff0f0"]*len(row)
            elif row["Net"]>0: return ["background-color:#f0fdf4"]*len(row)
            return [""]*len(row)
        st.dataframe(monthly[["Month","Gross_Requirement","Stock_Used","Stock_Remaining","Net"]].style.apply(hl,axis=1)
                     .format({c:"{:,.2f}" for c in ["Gross_Requirement","Stock_Used","Stock_Remaining","Net"]}),
                     use_container_width=True,hide_index=True)
        s1,s2,s3,s4=st.columns(4); fn=monthly["Net"].iloc[-1]
        s1.metric("Total gross",f"{monthly['Gross_Requirement'].sum():,.2f}")
        s2.metric("Opening stock",f"{stk:,.2f}")
        s3.metric("Final net",f"{fn:,.2f}",delta="surplus" if fn>=0 else "shortage",delta_color="normal" if fn>=0 else "inverse")
        s4.metric("Months short",f"{(monthly['Net']<0).sum()} / {len(monthly)}")
    else: st.info("In BOM but not in MRP results (phantom or no demand).")


# ═══════════════════════════════════════════════════════════════
# SIDEBAR NAV
# ═══════════════════════════════════════════════════════════════
with st.sidebar:
    # Logo
    st.markdown("""
    <div style="padding:20px 16px 16px;border-bottom:1px solid rgba(255,255,255,0.08);margin:-16px -16px 8px -16px;">
      <div style="display:flex;align-items:center;gap:10px;">
        <div style="width:32px;height:32px;background:#1a6ef7;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0;">⚙</div>
        <div>
          <div style="font-size:13px;font-weight:700;color:#fff;font-family:'Plus Jakarta Sans',sans-serif;letter-spacing:0.03em;">MRP CONFIG</div>
          <div style="font-size:10px;color:rgba(255,255,255,0.3);font-family:'Plus Jakarta Sans',sans-serif;">SAP MRP Engine</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Nav items
    page = st.session_state["page"]
    mrp_done  = st.session_state["mrp_results"] is not None
    seg_done  = st.session_state["seg_results"] is not None
    ag_done   = st.session_state["aging_results"] is not None

    nav_items = [
        ("🏠", "Home",                    "home",    None),
        ("📂", "Upload Files",            "upload",  None),
        ("⚙️",  "Run MRP",               "mrp",     "✓" if mrp_done else None),
        ("🏭",  "Segment Wise Available", "segment", "✓" if seg_done else None),
        ("📦",  "Aging Projection",       "aging",   "✓" if ag_done else None),
        ("⚙",  "Settings",               "settings",None),
    ]

    for icon, label, pg, badge in nav_items:
        is_active = (page == pg)
        # Use HTML for active styling since we can't use data attributes easily
        if is_active:
            st.markdown(f"""
            <div style="background:#1a6ef7;border-radius:8px;margin:1px 0;padding:9px 14px;
                        display:flex;align-items:center;gap:8px;cursor:pointer;">
              <span style="font-size:14px;">{icon}</span>
              <span style="font-size:13px;font-weight:600;color:#fff;font-family:'Plus Jakarta Sans',sans-serif;flex:1;">{label}</span>
              {"<span style='font-size:10px;background:rgba(255,255,255,0.2);color:#fff;padding:2px 6px;border-radius:8px;font-weight:600;'>"+badge+"</span>" if badge else ""}
            </div>""", unsafe_allow_html=True)
        else:
            if st.button(f"{icon}  {label}", key=f"nav_{pg}", use_container_width=True):
                go(pg)

    # Footer
    st.markdown("""
    <div style="position:fixed;bottom:0;left:0;width:230px;padding:14px 16px;
                border-top:1px solid rgba(255,255,255,0.07);background:#0d1b2a;">
      <div style="font-size:12px;color:rgba(255,255,255,0.3);font-family:'Plus Jakarta Sans',sans-serif;">
        Need help?<br>
        <span style="font-size:11px;color:rgba(255,255,255,0.18);">Contact support</span>
      </div>
    </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# PAGE: HOME
# ═══════════════════════════════════════════════════════════════
if st.session_state["page"] == "home":
    topbar("Dashboard", "SAP MRP Engine — workflow overview")

    mrp_done  = st.session_state["mrp_results"] is not None
    seg_done  = st.session_state["seg_results"] is not None
    ag_done   = st.session_state["aging_results"] is not None

    steps = [
        ("📂","Upload Files",      "Upload BOM, Req & Stock and optional files",    True,     "upload"),
        ("⚙️","Run MRP",           "Execute L1–L4 BOM explosion & NET propagation", mrp_done, "mrp"),
        ("🏭","Segment Wise Available","LP-optimised import-part constrained capacity", seg_done, "segment"),
        ("📦","Aging Projection",  "Material aging forecast with consumption offset", ag_done,  "aging"),
    ]

    c1, c2 = st.columns(2)
    for i, (icon, title, desc, done, pk) in enumerate(steps):
        with (c1 if i%2==0 else c2):
            border = "#86efac" if done else "#e5e7eb"
            badge = ('<span style="font-size:10px;font-weight:700;background:#dcfce7;color:#15803d;padding:3px 9px;border-radius:10px;">✓ DONE</span>'
                     if done else
                     '<span style="font-size:10px;font-weight:600;background:#f3f4f6;color:#9ca3af;padding:3px 9px;border-radius:10px;">PENDING</span>')
            st.markdown(f"""
            <div style="background:#fff;border:1px solid {border};border-radius:12px;padding:18px 20px;margin-bottom:12px;">
              <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;">
                <span style="font-size:24px;">{icon}</span>{badge}
              </div>
              <div style="font-size:14px;font-weight:700;color:#111827;margin-bottom:4px;">{title}</div>
              <div style="font-size:12px;color:#6b7280;">{desc}</div>
            </div>""", unsafe_allow_html=True)

    if mrp_done:
        sec("MRP Quick Stats")
        r = st.session_state["mrp_results"]
        col1,col2,col3,col4 = st.columns(4)
        total_comps = sum(df["Component"].nunique() for df in [r["result_l1"],r["result_l2"],r["result_l3"],r["result_l4"]] if not df.empty)
        total_short = sum(df[df["Shortage"]>0]["Component"].nunique() for df in [r["result_l1"],r["result_l2"],r["result_l3"],r["result_l4"]] if not df.empty)
        col1.metric("Total components", f"{total_comps:,}")
        col2.metric("With shortage",    f"{total_short:,}")
        col3.metric("Planning months",  f"{len(r['months'])}")
        col4.metric("Stock records",    f"{len(r['stock']):,}")

    if seg_done:
        sec("Segment Quick Stats")
        r = st.session_state["seg_results"]
        s1,s2,s3,s4=st.columns(4)
        s1.metric("Total sets",        f"{r['total_sets']:,}")
        s2.metric("FGs producing",     f"{sum(1 for f in r['fg_results'] if f['Max_Sets']>0)} / {len(r['fg_results'])}")
        s3.metric("Active segments",   f"{(r['alloc_int']>0).sum()} / {len(r['segs'])}")
        s4.metric("Constrained parts", f"{len(r['constrained_parts'])}")


# ═══════════════════════════════════════════════════════════════
# PAGE: UPLOAD FILES
# ═══════════════════════════════════════════════════════════════
elif st.session_state["page"] == "upload":
    topbar("Upload Configuration & Data Files", "Upload all required files to run the MRP process")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""<div class="ucard"><div class="ucard-header"><div class="ucard-title-row">
        <div class="ucard-icon purple">📋</div><div><p class="ucard-title">BOM File</p>
        <p class="ucard-desc">Upload your BOM file (.XLSX, .XLS)</p></div></div>
        <span class="badge-req">Required</span></div></div>""", unsafe_allow_html=True)
        bf = st.file_uploader("BOM", type=["xlsx","xls"], key="bom_u", label_visibility="collapsed")
        if bf: st.session_state["_bom"]=bf.read()
        st.markdown('<p class="accepted">Accepted: .XLSX, .XLS</p>', unsafe_allow_html=True)

    with c2:
        st.markdown("""<div class="ucard"><div class="ucard-header"><div class="ucard-title-row">
        <div class="ucard-icon green">📊</div><div><p class="ucard-title">Req. &amp; Stock File</p>
        <p class="ucard-desc">Upload your requirement &amp; stock file</p></div></div>
        <span class="badge-req">Required</span></div></div>""", unsafe_allow_html=True)
        rf = st.file_uploader("Req", type=["xlsx","xls"], key="req_u", label_visibility="collapsed")
        if rf: st.session_state["_req"]=rf.read()
        st.markdown('<p class="accepted">Accepted: .XLSX, .XLS</p>', unsafe_allow_html=True)

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    with c3:
        st.markdown("""<div class="ucard"><div class="ucard-header"><div class="ucard-title-row">
        <div class="ucard-icon orange">📦</div><div><p class="ucard-title">Production Orders</p>
        <p class="ucard-desc">Upload your production orders file</p></div></div>
        <span class="badge-opt">Optional</span></div></div>""", unsafe_allow_html=True)
        pf = st.file_uploader("Prod", type=["xlsx","xls"], key="prod_u", label_visibility="collapsed")
        if pf: st.session_state["_prod"]=pf.read()
        st.markdown('<p class="accepted">Accepted: .XLSX, .XLS</p>', unsafe_allow_html=True)

    with c4:
        st.markdown("""<div class="ucard"><div class="ucard-header"><div class="ucard-title-row">
        <div class="ucard-icon blue">📥</div><div><p class="ucard-title">Receipt Quantities</p>
        <p class="ucard-desc">Upload your receipt quantities file</p></div></div>
        <span class="badge-opt">Optional</span></div></div>""", unsafe_allow_html=True)
        rrf = st.file_uploader("Receipt", type=["xlsx","xls"], key="receipt_u", label_visibility="collapsed")
        if rrf: st.session_state["_receipt"]=rrf.read()
        st.markdown('<p class="accepted">Accepted: .XLSX, .XLS</p>', unsafe_allow_html=True)

    st.markdown("""<div class="run-bar">
      <div><div class="run-bar-text">Ready to process?</div>
      <div class="run-bar-sub">All required files uploaded · Click Run MRP to proceed</div></div>
    </div>""", unsafe_allow_html=True)
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    rb, _ = st.columns([1,4])
    with rb:
        if st.button("Run MRP  ▶", type="primary", use_container_width=True): go("mrp")


# ═══════════════════════════════════════════════════════════════
# PAGE: RUN MRP
# ═══════════════════════════════════════════════════════════════
elif st.session_state["page"] == "mrp":
    topbar("Run MRP", "Execute Material Requirements Planning — L1 to L4 BOM explosion")

    bom_b = st.session_state.get("_bom"); req_b = st.session_state.get("_req")
    prod_b = st.session_state.get("_prod"); receipt_b = st.session_state.get("_receipt")

    if not bom_b or not req_b:
        sec("File Input")
        st.info("Upload files on the **Upload Files** page, or upload directly below.")
        a,b2 = st.columns(2)
        with a:
            f=st.file_uploader("BOM File *",type=["xlsx","xls"],key="bom_m")
            if f: bom_b=f.read(); st.session_state["_bom"]=bom_b
        with b2:
            f=st.file_uploader("Req & Stock *",type=["xlsx","xls"],key="req_m")
            if f: req_b=f.read(); st.session_state["_req"]=req_b
        c,d=st.columns(2)
        with c:
            f=st.file_uploader("Production Orders",type=["xlsx","xls"],key="prod_m")
            if f: prod_b=f.read(); st.session_state["_prod"]=prod_b
        with d:
            f=st.file_uploader("Receipt Quantities",type=["xlsx","xls"],key="rec_m")
            if f: receipt_b=f.read(); st.session_state["_receipt"]=receipt_b

    sec("Engine Configuration")
    g1,g2,g3,g4,g5=st.columns(5)
    with g1: st.session_state["cfg_phantom"]=st.text_input("Phantom code",value=st.session_state["cfg_phantom"],key="ph"); PHANTOM=st.session_state["cfg_phantom"]
    with g2: st.session_state["cfg_vl1"]=st.text_input("Verify L1",value=st.session_state["cfg_vl1"],key="vl1"); VERIFY_L1=st.session_state["cfg_vl1"]
    with g3: st.session_state["cfg_vl2"]=st.text_input("Verify L2",value=st.session_state["cfg_vl2"],key="vl2"); VERIFY_L2=st.session_state["cfg_vl2"]
    with g4: st.session_state["cfg_vl3"]=st.text_input("Verify L3",value=st.session_state["cfg_vl3"],key="vl3"); VERIFY_L3=st.session_state["cfg_vl3"]
    with g5: st.session_state["cfg_vl4"]=st.text_input("Verify L4",value=st.session_state["cfg_vl4"],key="vl4"); VERIFY_L4=st.session_state["cfg_vl4"]

    rb,_=st.columns([1,4])
    with rb:
        run_btn=st.button("▶ Execute MRP",type="primary",use_container_width=True,key="exec_mrp")
    if run_btn:
        if not bom_b or not req_b: st.warning("Upload BOM and Req & Stock files first.")
        else:
            try:
                results=run_mrp_engine(bom_b,req_b,prod_b,receipt_b)
                if results: st.session_state["mrp_results"]=results; st.success("MRP completed.")
            except Exception as e: st.exception(e)

    r=st.session_state.get("mrp_results")
    if r is None:
        st.markdown("""<div class="empty"><div class="empty-icon">⚙️</div>
        <div class="empty-ttl">Ready to run</div>
        <div class="empty-sub">Upload files, configure codes above, then click Execute MRP.</div></div>""",
        unsafe_allow_html=True)
    else:
        sec("MRP Summary")
        c1,c2,c3,c4=st.columns(4)
        for col_ui,lbl,df in zip([c1,c2,c3,c4],["L1","L2","L3","L4"],[r["result_l1"],r["result_l2"],r["result_l3"],r["result_l4"]]):
            short=df[df["Shortage"]>0]["Component"].nunique() if not df.empty else 0
            with col_ui:
                st.metric(f"L{lbl[-1]} components",df["Component"].nunique() if not df.empty else 0)
                st.metric("With shortage",short)

        sec("Verification")
        t1,t2,t3,t4=st.tabs(["L1","L2","L3 (phantom)","L4"])
        def sv(tab,rdf,tgt,lbl):
            with tab:
                st.markdown(f"**{lbl} — `{tgt}`**")
                if rdf is None or rdf.empty: st.warning("No rows."); return
                t=rdf[rdf["Component"]==tgt]
                if t.empty: st.info("Not found — phantom or no demand."); return
                st.caption(f"Description: {t['Description'].iloc[0]} | Stock: {r['stock'].get(tgt,0):,.3f}")
                st.dataframe(t[["Month","Gross_Requirement","Stock_Used","Shortage","Stock_Remaining"]].reset_index(drop=True),use_container_width=True)
        sv(t1,r["result_l1"],VERIFY_L1,"LEVEL 1")
        sv(t2,r["result_l2"],VERIFY_L2,"LEVEL 2")
        with t3:
            if (not r["result_l3"].empty) and (VERIFY_L3 in r["result_l3"]["Component"].values):
                st.error(f"ERROR: {VERIFY_L3} found — phantom logic broken!")
            else: st.success(f"✅ {VERIFY_L3} correctly SKIPPED (phantom confirmed).")
        sv(t4,r["result_l4"],VERIFY_L4,"LEVEL 4")

        sec("Net Position Output")
        pivot=r.get("pivot")
        if pivot is not None:
            st.dataframe(pivot.head(300),use_container_width=True)
            st.caption(f"{len(pivot):,} rows · {len(r['month_cols'])} months · positive=surplus · negative=shortage")
            buf=io.BytesIO(); pivot.to_excel(buf,index=False,engine="openpyxl"); buf.seek(0)
            st.download_button("⬇ Download mrp_final.xlsx",data=buf,file_name="mrp_final.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                               use_container_width=True,type="primary")
        show_search(r["bom"],r["req"],r["months"],r["stock"],r["prod_summary"])


# ═══════════════════════════════════════════════════════════════
# PAGE: SEGMENT WISE AVAILABLE
# ═══════════════════════════════════════════════════════════════
elif st.session_state["page"] == "segment":
    topbar("Segment Wise Material Available", "LP-optimised IDU + ODU capacity constrained by import parts")

    mrp_r=st.session_state.get("mrp_results")
    if mrp_r is None:
        st.markdown("""<div class="empty"><div class="empty-icon">🏭</div>
        <div class="empty-ttl">Run MRP first</div>
        <div class="empty-sub">Segment Capacity uses the same BOM and Stock data from the MRP run.</div></div>""",
        unsafe_allow_html=True)
    else:
        sec("Segment & Import Part File")
        sc,_=st.columns([2,3])
        with sc:
            sf=st.file_uploader("Segment & Import Part (.xlsx)",type=["xlsx","xls"],key="seg_f",
                                 help="Sheet 1: Import Part List | Sheet 2: Segment (IDU/ODU codes)")
        rb,_=st.columns([1,4])
        with rb:
            run_seg=st.button("▶ Run Segment Capacity",type="primary",use_container_width=True,key="run_seg")
        if run_seg:
            if sf is None: st.warning("Upload Segment & Import Part file first.")
            else:
                try:
                    seg_bytes=sf.read(); st.session_state["seg_imp_bytes"]=seg_bytes
                    res=run_segment(mrp_r["bom"],mrp_r["stock"],seg_bytes)
                    if res: st.session_state["seg_results"]=res
                except Exception as e: st.exception(e)

        r=st.session_state.get("seg_results")
        if r is None:
            if not run_seg:
                st.markdown("""<div class="empty"><div class="empty-icon">🏭</div>
                <div class="empty-ttl">No results yet</div>
                <div class="empty-sub">Upload the Segment & Import Part file and click Run Segment Capacity.</div></div>""",
                unsafe_allow_html=True)
        else:
            sec("Overview")
            m1,m2,m3,m4=st.columns(4)
            m1.metric("Total FG sets",f"{r['total_sets']:,}")
            m2.metric("FGs producing",f"{sum(1 for f in r['fg_results'] if f['Max_Sets']>0)} / {len(r['fg_results'])}")
            m3.metric("Active segments",f"{(r['alloc_int']>0).sum()} / {len(r['segs'])}")
            m4.metric("Constrained parts",f"{len(r['constrained_parts'])}")

            rm_map=r.get("rm_map",{}); all_rm=sorted(set(rm_map.values())) if rm_map else []; ag=r.get("active_rm_groups",[])
            if all_rm:
                sec("RM Group Filter")
                rmc=st.columns(min(len(all_rm),6)); sg=[]
                for i,grp in enumerate(all_rm):
                    with rmc[i%len(rmc)]:
                        if st.checkbox(grp,value=(grp in ag),key=f"rm_{grp}"): sg.append(grp)
                ab,_=st.columns([1,4])
                with ab:
                    if st.button("↻ Apply filter",key="arm",type="primary"):
                        sb=st.session_state.get("seg_imp_bytes")
                        if sb:
                            with st.spinner("Recalculating ..."):
                                nr=run_segment(mrp_r["bom"],mrp_r["stock"],sb,active_rm=sg)
                                if nr: st.session_state["seg_results"]=nr; st.rerun()

            if r.get("skipped_segs"):
                with st.expander(f"⚠ {len(r['skipped_segs'])} FGs skipped"):
                    for s in r["skipped_segs"]: st.text(f"  · {s}")

            sec("Sets producible per FG code")
            fg_res=r.get("fg_results",[])
            if fg_res:
                fgdf=pd.DataFrame([{"Segment":f["Segment"],"FG Code":f["FG_Code"],"FG Description":f.get("FG_Desc",""),
                                     "IDU":f["IDU"],"IDU Desc":f.get("IDU_Desc",""),"Compatible ODU":f["Compatible_ODU"],
                                     "ODU Desc":f.get("ODU_Desc",""),"Max Sets":f["Max_Sets"],
                                     "Limiting Part":f["Limiting_Part"],"Limiting Stock":f["Limiting_Stock"]}
                                    for f in fg_res]).sort_values(["Segment","Max Sets"],ascending=[True,False])
                def hf(row): return ["background-color:#f0fdf4"]*len(row) if row["Max Sets"]>0 else ["background-color:#fffbeb"]*len(row)
                st.dataframe(fgdf.style.apply(hf,axis=1).format({"Max Sets":"{:,}","Limiting Stock":"{:,}"}),use_container_width=True,hide_index=True)

            sec("Segment rollup")
            srows=[]
            for s,qty in zip(r["segs"],r["alloc_int"]):
                sd=r["segments_data"][s]; fgs=[f for f in fg_res if f["Segment"]==s]
                srows.append({"Segment":s,"Total Sets":int(qty),"FG codes":len(fgs),"FGs producing":sum(1 for f in fgs if f["Max_Sets"]>0),"Unique IDUs":sd["idu_count"],"Unique ODUs":sd["odu_count"]})
            sdf=pd.DataFrame(srows).sort_values("Total Sets",ascending=False)
            def hs(row): return ["background-color:#f0fdf4"]*len(row) if row["Total Sets"]>0 else ["background-color:#f9fafb"]*len(row)
            st.dataframe(sdf.style.apply(hs,axis=1).format({"Total Sets":"{:,}"}),use_container_width=True,hide_index=True)

            sec("FG detail — import part breakdown")
            opts=sorted([f["FG_Code"] for f in fg_res],key=lambda fg:-next(f["Max_Sets"] for f in fg_res if f["FG_Code"]==fg))
            sfg=st.selectbox("Select FG code",options=opts,key="sfg")
            if sfg:
                fgr=next(f for f in fg_res if f["FG_Code"]==sfg); sets=fgr["Max_Sets"]
                st.markdown(f"**{sfg}** — {fgr.get('FG_Desc','')} · Segment: `{fgr['Segment']}` · IDU: `{fgr['IDU']}` · ODU: `{fgr['Compatible_ODU']}` · **Max sets: {sets:,}**")
                irows=[]
                for p,req in sorted(fgr["combined_req"].items(),key=lambda x:-x[1]):
                    avail=float(r["stock"].get(p,0)); ms=int(avail/req) if req>0 else 0
                    irows.append({"Import Part":p,"RM Group":rm_map.get(p,"—"),"Qty per set":round(req,4),"Stock available":int(avail),"Max sets (alone)":ms,"Binding?":"🔴 YES" if ms==sets and sets>0 else ""})
                idf=pd.DataFrame(irows)
                def hi(row): return ["background-color:#fff0f0"]*len(row) if row["Binding?"]=="🔴 YES" else [""]*len(row)
                st.dataframe(idf.style.apply(hi,axis=1).format({"Qty per set":"{:.4f}","Stock available":"{:,}","Max sets (alone)":"{:,}"}),use_container_width=True,hide_index=True)

            sec("Import part stock utilisation")
            purows=[]
            for p in r["import_parts"]:
                pu=r["part_usage"].get(p,{})
                purows.append({"Import Part":p,"RM Group":rm_map.get(p,"—"),"Stock":int(r["stock"].get(p,0)),"Used":int(pu.get("used",0)),"Remaining":int(pu.get("remain",r["stock"].get(p,0))),"Utilisation%":pu.get("pct",0)})
            pudf=pd.DataFrame(purows).sort_values("Utilisation%",ascending=False)
            def hu(row):
                p=row["Utilisation%"]
                if p>=90: return ["background-color:#fff0f0"]*len(row)
                elif p>=50: return ["background-color:#fffbeb"]*len(row)
                elif p>0: return ["background-color:#f0fdf4"]*len(row)
                return [""]*len(row)
            ta,tc=st.tabs(["All import parts","Constrained only"])
            with ta: st.dataframe(pudf.style.apply(hu,axis=1).format({"Stock":"{:,}","Used":"{:,}","Remaining":"{:,}","Utilisation%":"{:.1f}"}),use_container_width=True,hide_index=True)
            with tc: st.dataframe(pudf[pudf["Import Part"].isin(r["constrained_parts"])].style.apply(hu,axis=1).format({"Stock":"{:,}","Used":"{:,}","Remaining":"{:,}","Utilisation%":"{:.1f}"}),use_container_width=True,hide_index=True)

            buf=io.BytesIO()
            with pd.ExcelWriter(buf,engine="openpyxl") as w:
                if fg_res: fgdf.to_excel(w,sheet_name="FG Sets",index=False)
                sdf.to_excel(w,sheet_name="Segment Rollup",index=False)
                pudf.to_excel(w,sheet_name="Import Part Utilisation",index=False)
            buf.seek(0)
            st.download_button("⬇ Download Segment Capacity (.xlsx)",data=buf,file_name="segment_capacity.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",use_container_width=True,type="primary")


# ═══════════════════════════════════════════════════════════════
# PAGE: AGING PROJECTION
# ═══════════════════════════════════════════════════════════════
elif st.session_state["page"] == "aging":
    topbar("Aging Opening Inventory Forecast", "Month-wise aging opening stock — BOM consumption + receipt adjusted")

    sec("Input Files")
    fc1, fc2 = st.columns(2)
    with fc1:
        af = st.file_uploader("Aging Material Details (.xlsx) *Required*",
                              type=["xlsx","xls"], key="ag_f")
        if af:
            st.session_state["_aging"] = af.read()
    with fc2:
        bom_ag_f = st.file_uploader("BOM File (.xlsx) — leave blank to use MRP session BOM",
                                    type=["xlsx","xls"], key="ag_bom_f")
        if bom_ag_f:
            st.session_state["_ag_bom"] = bom_ag_f.read()
        if not st.session_state.get("_ag_bom") and st.session_state.get("_bom"):
            st.caption("✓ Will use BOM already loaded in MRP session")

    fc3, fc4 = st.columns(2)
    with fc3:
        req_ag_f = st.file_uploader("Requirement File (.xlsx) — leave blank to use MRP session Req",
                                    type=["xlsx","xls"], key="ag_req_f")
        if req_ag_f:
            st.session_state["_ag_req"] = req_ag_f.read()
        if not st.session_state.get("_ag_req") and st.session_state.get("_req"):
            st.caption("✓ Will use Req & Stock already loaded in MRP session")
    with fc4:
        rec_ag_f = st.file_uploader("Receipt File (.xlsx) — Optional",
                                    type=["xlsx","xls"], key="ag_rec_f")
        if rec_ag_f:
            st.session_state["_ag_rec"] = rec_ag_f.read()
            st.caption("✓ Receipt file loaded")

    fc5, fc6 = st.columns(2)
    with fc5:
        st.markdown("**Aging snapshot date**")
        st.caption("Date the aging file was extracted from SAP (e.g. May-01 if it is May opening)")
        abd = st.date_input("Snapshot date", value=pd.Timestamp("2026-05-01"),
                            key="ag_dt", label_visibility="collapsed")
    with fc6:
        st.markdown(" ")

    rb, _ = st.columns([1,4])
    with rb:
        run_ag = st.button("▶ Run Aging Projection", type="primary",
                           use_container_width=True, key="run_ag")

    if run_ag:
        ag_bytes  = st.session_state.get("_aging")
        bom_bytes = st.session_state.get("_ag_bom") or st.session_state.get("_bom")
        req_bytes = st.session_state.get("_ag_req") or st.session_state.get("_req")
        rec_bytes = st.session_state.get("_ag_rec")

        missing = []
        if not ag_bytes:  missing.append("Aging Material Details")
        if not bom_bytes: missing.append("BOM File")
        if not req_bytes: missing.append("Requirement File")
        if missing:
            st.warning(f"Please upload: {', '.join(missing)}")
        else:
            try:
                status_ag = st.status("Running Aging Projection ...", expanded=True)
                with status_ag:
                    # Step 1 — consolidate aging
                    st.write("► Step 1 — Consolidating aging file (storage location → material) ...")
                    agdf = load_aging(io.BytesIO(ag_bytes))
                    n_mats    = len(agdf)
                    n_aging90 = int((agdf[["91-120 Qty","121-150 Qty","151-180 Qty",
                                           "181-360 Qty","Over361 Qty"]].sum(axis=1) > 0).sum())
                    st.write(f"   → {n_mats:,} unique materials · {n_aging90:,} with current 90+ day aging")

                    # Step 2 — BOM explosion
                    st.write("► Step 2 — Exploding BOM (L1–L4) to get gross component consumption ...")
                    prod_cons, months_from_req = compute_bom_consumption(
                        bom_bytes, req_bytes,
                        phantom_code=str(st.session_state.get("cfg_phantom","50")).strip())
                    st.write(f"   → {len(prod_cons):,} components with BOM consumption · "
                             f"{len(months_from_req)} months: {', '.join(months_from_req)}")

                    # Step 3 — Receipts (optional)
                    receipts = {}
                    if rec_bytes:
                        st.write("► Step 3 — Loading receipt file ...")
                        receipts = load_receipts(io.BytesIO(rec_bytes))
                        st.write(f"   → {len(receipts):,} components with receipt data")
                    else:
                        st.write("► Step 3 — No receipt file provided (skipping)")

                    # Step 4 — Project aging
                    st.write("► Step 4 — Projecting aging opening inventory month-by-month ...")
                    proj = project_aging(agdf, base_date=abd,
                                         prod_cons=prod_cons,
                                         months_list=months_from_req,
                                         receipts=receipts)

                    st.session_state["aging_results"] = {
                        "proj": proj, "months": months_from_req, "base_date": abd,
                        "n_mats": n_mats, "n_aging90": n_aging90,
                        "prod_cons": prod_cons, "receipts": receipts,
                    }
                status_ag.update(label="Aging Projection complete ✅", state="complete", expanded=False)
            except Exception as e:
                st.exception(e)

    ag = st.session_state.get("aging_results")
    if ag is None:
        if not run_ag:
            st.markdown("""<div class="empty"><div class="empty-icon">📦</div>
            <div class="empty-ttl">No aging data yet</div>
            <div class="empty-sub">Upload Aging file + BOM + Requirement (Receipt optional), then click Run Aging Projection.</div></div>""",
            unsafe_allow_html=True)
    else:
        proj     = ag["proj"]; ml = ag["months"]; bd = ag["base_date"]
        prod_cons = ag.get("prod_cons", {}); receipts = ag.get("receipts", {})
        mo = [m for m in ml if m in proj["Opening Month"].unique()]
        lm = mo[-1] if mo else ""; fm = mo[0] if mo else ""
        fd  = proj[proj["Opening Month"] == lm]
        ffd = proj[proj["Opening Month"] == fm]

        # ── Logic explainer ────────────────────────────────────
        with st.expander("ℹ How the aging opening forecast is calculated"):
            def _pool_desc(off):
                if off == 0: return "91-120 + 121-150 + 151-180 + 181-360 + Over361 day stock"
                if off == 1: return "61-90 + 91+ day stock"
                if off == 2: return "31-60 + 61-90 + 91+ day stock"
                return "ALL buckets (0-15 + 16-30 + 31-60 + 61-90 + 91+ day stock)"
            def _cons_desc(idx, mo_list):
                prior = mo_list[:idx]
                if not prior: return "— (baseline, no prior months)"
                return "Cumulative " + "+".join(prior) + " BOM consumption"
            rows_md = ""
            for i, m in enumerate(mo):
                pool = _pool_desc(i)
                cons = _cons_desc(i, mo)
                rows_md += "| **" + m + "** opening | " + pool + " | " + cons + " |\n"
            st.markdown(f"""
**Snapshot date:** {bd} — date the aging file was extracted from SAP.

| Opening Month | Aging Pool (stock age on snapshot) | Less |
|---|---|---|
{rows_md}
**Value:** Snapshot month uses actual SAP value columns. Forecast months use `Aging Qty × MAP`.  
**Receipts:** Receipt qty × MAP added for prior months (only net-positive = receipt > consumption).  
**Consumption:** Pure gross BOM explosion — no stock netting.
""")

        # ── Overview metrics ───────────────────────────────────
        sec("Overview")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric(f"Opening Aging Value ({fm})",
                  f"Rs {ffd['Aging Value (Rs)'].sum():,.0f}",
                  help="Current 90+ day aging — actual SAP values")
        c2.metric(f"Projected Opening Aging ({lm})",
                  f"Rs {fd['Aging Value (Rs)'].sum():,.0f}",
                  delta=f"Rs {fd['Aging Value (Rs)'].sum() - ffd['Aging Value (Rs)'].sum():,.0f}",
                  delta_color="inverse")
        c3.metric(f"Materials with aging ({lm})",
                  f"{(fd['Aging Value (Rs)'] > 0).sum():,}")
        c4.metric("With receipt adjustment",
                  f"{len(receipts):,} components" if receipts else "No receipt file")

        # ── Monthly summary table ──────────────────────────────
        sec("Opening aging by month")
        msumm = (proj.groupby("Opening Month", sort=False)
                 .agg(
                     Aging_Val   =("Aging Value (Rs)",          "sum"),
                     Mat_Aging   =("Material", lambda x: (proj.loc[x.index,"Aging Value (Rs)"]>0).sum()),
                     Newly_Aging =("Newly Aging This Month",    "sum"),
                     Month_Cons  =("Month BOM Consumption",     "sum"),
                     Cum_Cons    =("Cumulative BOM Consumption","sum"),
                     Month_Rec   =("Month Receipt Qty",         "sum"),
                     Cum_Rec     =("Cumulative Receipt Qty",    "sum"),
                     Net_Rec     =("Net Receipt (unused)",      "sum"),
                 )
                 .reindex(mo).reset_index())
        msumm.columns = ["Opening Month","Aging Value (Rs)","Materials with Aging",
                         "Newly Aging Qty","Month BOM Consumption","Cumulative BOM Consumption",
                         "Month Receipt Qty","Cumulative Receipt Qty","Net Unused Receipt Qty"]
        def hv(row):
            v = row["Aging Value (Rs)"]
            if v > 10_000_000: return ["background-color:#fff0f0"] * len(row)
            if v > 1_000_000:  return ["background-color:#fffbeb"] * len(row)
            if v > 0:          return ["background-color:#f0fdf4"] * len(row)
            return [""] * len(row)
        fmt_s = {
            "Aging Value (Rs)":           "Rs {:,.0f}",
            "Newly Aging Qty":            "{:,.0f}",
            "Month BOM Consumption":      "{:,.0f}",
            "Cumulative BOM Consumption": "{:,.0f}",
            "Month Receipt Qty":          "{:,.0f}",
            "Cumulative Receipt Qty":     "{:,.0f}",
            "Net Unused Receipt Qty":     "{:,.0f}",
        }
        st.dataframe(msumm.style.apply(hv, axis=1).format(fmt_s),
                     use_container_width=True, hide_index=True)

        # ── Material × month pivot (aging value) ───────────────
        sec("Aging value — material × opening month")
        piv = (proj.pivot_table(index=["Material","Description"], columns="Opening Month",
                                values="Aging Value (Rs)", aggfunc="sum")
               .reindex(columns=mo, fill_value=0).reset_index())
        arows = piv[piv[mo].max(axis=1) > 0].sort_values(lm, ascending=False)
        st.caption(f"{len(arows):,} materials with aging value")
        st.dataframe(
            arows.style.format({m: "Rs {:,.0f}" for m in mo})
                       .background_gradient(subset=mo, cmap="YlOrRd"),
            use_container_width=True, hide_index=True)

        # ── Material detail for selected opening month ─────────
        sec("Material detail — select opening month")
        sm = st.selectbox("Opening as of:", mo, index=0, key="ag_sel")
        mdf = (proj[proj["Opening Month"] == sm]
               .query("`Aging Value (Rs)` > 0")
               .sort_values("Aging Value (Rs)", ascending=False).copy())
        st.caption(f"{len(mdf):,} materials · Total: Rs {mdf['Aging Value (Rs)'].sum():,.0f}")
        shc = ["Material","Description","Material Type",
               "Aging Pool Qty","Newly Aging This Month",
               "Cumulative BOM Consumption","Cumulative Receipt Qty","Net Receipt (unused)",
               "Aging Qty (>=91d)","Aging Value (Rs)","Turning Aging Next Month"]
        shc = [c for c in shc if c in mdf.columns]
        def hr2(row):
            v = row["Aging Value (Rs)"]
            if v > 500_000: return ["background-color:#fff0f0"] * len(row)
            if v > 100_000: return ["background-color:#fffbeb"] * len(row)
            return [""] * len(row)
        fmt2 = {c: "{:,.0f}" for c in shc if c != "Material" and c != "Description" and c != "Material Type"}
        fmt2["Aging Value (Rs)"] = "Rs {:,.0f}"
        st.dataframe(
            mdf[shc].style.apply(hr2, axis=1).format({k:v for k,v in fmt2.items() if k in shc}),
            use_container_width=True, hide_index=True)

        # ── Receipts drill-down (if loaded) ───────────────────
        if receipts:
            sec("Receipt adjustment drill-down")
            rec_rows = []
            for mat, mdict in receipts.items():
                row_d = {"Component": mat}
                total = 0.0
                for m in mo:
                    row_d[m] = float(mdict.get(m, 0))
                    total += row_d[m]
                row_d["Total Receipt"] = total
                rec_rows.append(row_d)
            rec_df = (pd.DataFrame(rec_rows)
                      .sort_values("Total Receipt", ascending=False)
                      .reset_index(drop=True))
            aging_mats = set(proj["Material"].unique())
            rec_ag = rec_df[rec_df["Component"].isin(aging_mats)].copy()
            st.caption(f"{len(rec_ag):,} components with receipt data also present in aging file")
            if not rec_ag.empty:
                st.dataframe(rec_ag.style.format({m: "{:,.0f}" for m in mo + ["Total Receipt"]}),
                             use_container_width=True, hide_index=True)

        # ── Download ───────────────────────────────────────────
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as w:
            msumm.to_excel(w, sheet_name="Monthly Summary",    index=False)
            arows.to_excel(w, sheet_name="Aging Value Pivot",  index=False)
            proj.to_excel( w, sheet_name="Full Detail",        index=False)
            if prod_cons:
                cons_rows = []
                for mat, mdict in prod_cons.items():
                    row_d = {"Component": mat}
                    for m in mo: row_d[m] = float(mdict.get(m, 0))
                    cons_rows.append(row_d)
                pd.DataFrame(cons_rows).to_excel(w, sheet_name="BOM Consumption", index=False)
            if receipts:
                rec_df.to_excel(w, sheet_name="Receipts", index=False)
        buf.seek(0)
        st.download_button(
            "⬇ Download Aging Projection (.xlsx)", data=buf,
            file_name="aging_projection.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True, type="primary")


# ═══════════════════════════════════════════════════════════════
# PAGE: SETTINGS
# ═══════════════════════════════════════════════════════════════
elif st.session_state["page"] == "settings":
    topbar("Settings", "Engine configuration and session management")

    sec("Engine Configuration")
    c1,c2=st.columns(2)
    with c1: st.session_state["cfg_phantom"]=st.text_input("Phantom Special Procurement Code",value=st.session_state["cfg_phantom"],key="s_ph")
    with c2: st.markdown("**Phantom assemblies** are pass-through BOMs (e.g. SP code 50). The engine skips them and directly explodes their children.")

    sec("Verification Component Codes")
    v1,v2=st.columns(2)
    with v1:
        st.session_state["cfg_vl1"]=st.text_input("Verify L1",value=st.session_state["cfg_vl1"],key="s_v1")
        st.session_state["cfg_vl3"]=st.text_input("Verify L3 (phantom — should NOT appear)",value=st.session_state["cfg_vl3"],key="s_v3")
    with v2:
        st.session_state["cfg_vl2"]=st.text_input("Verify L2",value=st.session_state["cfg_vl2"],key="s_v2")
        st.session_state["cfg_vl4"]=st.text_input("Verify L4",value=st.session_state["cfg_vl4"],key="s_v4")

    sec("Session Data")
    r1,r2,r3=st.columns(3)
    r1.metric("MRP results",    "Loaded" if st.session_state["mrp_results"] else "Not run")
    r2.metric("Segment results","Loaded" if st.session_state["seg_results"] else "Not run")
    r3.metric("Aging results",  "Loaded" if st.session_state["aging_results"] else "Not run")
    st.markdown("<div style='height:8px'></div>",unsafe_allow_html=True)
    if st.button("🗑 Clear all session data",key="clr"):
        for k in ["mrp_results","seg_results","aging_results","seg_imp_bytes",
                  "_bom","_req","_prod","_receipt","_aging","_ag_bom","_ag_req","_ag_rec"]:
            st.session_state[k]=None
        st.success("Session cleared."); st.rerun()
