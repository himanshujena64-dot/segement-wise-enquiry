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
    color: rgba(255,255,255,0.88) !important;
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
[data-testid="stSidebar"] .stButton > button p {
    color: rgba(255,255,255,0.88) !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.10) !important;
    color: #ffffff !important;
    box-shadow: none !important;
}
[data-testid="stSidebar"] .stButton > button:hover p {
    color: #ffffff !important;
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

/* ── Template info box (NEW) ──────────────────────────────– */
.template-info {
    background: #f0fdf4;
    border: 1px solid #dcfce7;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 12px;
    color: #166534;
    margin-bottom: 16px;
    line-height: 1.5;
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
    "_aging": None, "_ag_bom": None, "_ag_req": None, "_ag_rec": None, "plan_open": False,
    "_imp_po": None, "imp_results": None, "_sup_master": None,
    "authenticated": False, "_login_error": "",
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ═══════════════════════════════════════════════════════════════
# SAVED UPLOADS — keep uploaded files on disk so they survive app restarts / redeploys during trials
# ═══════════════════════════════════════════════════════════════
import os, hashlib, datetime as _dt
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".saved_uploads")
PERSIST_KEYS = {"_bom":"BOM", "_req":"Req & Stock", "_prod":"Production Orders", "_receipt":"Receipts",
                "seg_imp_bytes":"Segment & Import Part", "_imp_po":"Import PO",
                "_aging":"Aging", "_ag_bom":"Aging BOM", "_ag_req":"Aging Req", "_ag_rec":"Aging Receipts",
                "_sup_master":"Supplier Master"}

def _saved_path(k): return os.path.join(UPLOAD_DIR, k.strip("_") + ".bin")

def restore_saved_uploads():
    """Once per browser session: load any saved file the session doesn't already have."""
    if st.session_state.get("_uploads_restored"): return
    st.session_state["_uploads_restored"] = True; got = []
    for k, lbl in PERSIST_KEYS.items():
        p = _saved_path(k)
        if st.session_state.get(k) is None and os.path.exists(p):
            try:
                with open(p, "rb") as fh: st.session_state[k] = fh.read()
                got.append(lbl)
            except OSError: pass
    st.session_state["_restored_list"] = got

def sync_saved_uploads():
    """Write new / changed uploads to disk; delete the saved copy when a file is cleared."""
    try: os.makedirs(UPLOAD_DIR, exist_ok=True)
    except OSError: return
    hashes = st.session_state.setdefault("_saved_hashes", {})
    for k in PERSIST_KEYS:
        v = st.session_state.get(k); p = _saved_path(k)
        try:
            if isinstance(v, (bytes, bytearray)) and v:
                h = hashlib.md5(v).hexdigest()
                if hashes.get(k) != h:
                    with open(p, "wb") as fh: fh.write(v)
                    hashes[k] = h
            elif v is None and os.path.exists(p):
                os.remove(p); hashes.pop(k, None)
        except OSError: pass

def saved_uploads_info():
    out = []
    for k, lbl in PERSIST_KEYS.items():
        p = _saved_path(k)
        if os.path.exists(p):
            out.append({"File": lbl, "Size (KB)": round(os.path.getsize(p)/1024, 1),
                        "Saved at": _dt.datetime.fromtimestamp(os.path.getmtime(p)).strftime("%d-%b-%y %H:%M")})
    return out

restore_saved_uploads()

# ═══════════════════════════════════════════════════════════════
# LOGIN GATE
# ═══════════════════════════════════════════════════════════════
_VALID_USER = "admin"
_VALID_PASS = "admin@2040"

if not st.session_state["authenticated"]:
    st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none !important; }
    .login-wrap {
        max-width: 420px; margin: 80px auto 0;
        background: #ffffff; border: 1px solid #e5e7eb;
        border-radius: 16px; padding: 40px 36px 36px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.07);
    }
    .login-logo {
        width: 48px; height: 48px; background: #1a6ef7;
        border-radius: 12px; display: flex; align-items: center;
        justify-content: center; font-size: 24px; margin: 0 auto 20px;
    }
    .login-title {
        font-size: 22px; font-weight: 700; color: #111827;
        text-align: center; margin-bottom: 4px;
    }
    .login-sub { font-size: 13px; color: #9ca3af; text-align: center; margin-bottom: 28px; }
    .login-err {
        background: #fff0f0; border: 1px solid #fecaca;
        border-radius: 8px; padding: 10px 14px;
        color: #dc2626; font-size: 13px; font-weight: 500;
        margin-bottom: 14px; text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

    _col_l, _col_c, _col_r = st.columns([1, 2, 1])
    with _col_c:
        st.markdown("""
        <div class="login-wrap">
          <div class="login-logo">⚙</div>
          <div class="login-title">SAP MRP Engine</div>
          <div class="login-sub">Sign in to continue</div>
        </div>
        """, unsafe_allow_html=True)
        if st.session_state["_login_error"]:
            st.markdown(f'<div class="login-err">❌ {st.session_state["_login_error"]}</div>',
                        unsafe_allow_html=True)
        _uid = st.text_input("User ID", placeholder="Enter user ID", key="_li_uid")
        _pwd = st.text_input("Password", placeholder="Enter password",
                             type="password", key="_li_pwd")
        _btn = st.button("Sign In", type="primary", use_container_width=True)
        if _btn:
            if _uid.strip() == _VALID_USER and _pwd == _VALID_PASS:
                st.session_state["authenticated"] = True
                st.session_state["_login_error"] = ""
                st.rerun()
            else:
                st.session_state["_login_error"] = "Invalid user ID or password."
                st.rerun()
    st.stop()  # block the rest of the app until authenticated

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
    sync_saved_uploads()
    st.rerun()

def sec(text):
    st.markdown(f'<div class="sec-div"><div class="sec-div-line"></div>'
                f'<div class="sec-div-text">{text}</div>'
                f'<div class="sec-div-line"></div></div>', unsafe_allow_html=True)

def _restored_banner():
    got=st.session_state.pop("_restored_list",None)
    if got: st.toast(f"Restored saved uploads: {', '.join(got)}. Run MRP again to refresh results.", icon="📂")

def topbar(title, sub=""):
    _restored_banner()
    mrp_done  = st.session_state["mrp_results"]  is not None
    seg_done  = st.session_state["seg_results"]  is not None
    ag_done   = st.session_state["aging_results"] is not None
    chips = ""
    if mrp_done:  chips += '<span class="chip done"><span class="chip-dot"></span>MRP done</span>'
    if seg_done:  chips += '<span class="chip done"><span class="chip-dot"></span>Segment done</span>'
    if ag_done:   chips += '<span class="chip done"><span class="chip-dot"></span>Aging done</span>'
    if st.session_state["imp_results"] is not None: chips += '<span class="chip done"><span class="chip-dot"></span>Import done</span>'
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

def resolve_sheet(src, wanted):
    """Return the real sheet name in `src` matching `wanted` ignoring case/extra spaces.
    Falls back to `wanted` unchanged (so behaviour is identical when names already match)."""
    try:
        if isinstance(src, (bytes, bytearray)): bio = io.BytesIO(src)
        else:
            pos = src.tell() if hasattr(src, "tell") else None
            bio = src
        names = pd.ExcelFile(bio).sheet_names
        if not isinstance(src, (bytes, bytearray)) and pos is not None: src.seek(pos)
        key = str(wanted).strip().lower()
        for n in names:
            if str(n).strip().lower() == key: return n
    except Exception:
        try:
            if not isinstance(src, (bytes, bytearray)) and pos is not None: src.seek(pos)
        except Exception: pass
    return wanted

def detect_req_header_row(file_obj,sheet_name="Requirement",scan_rows=20):
    sheet_name=resolve_sheet(file_obj,sheet_name)
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
# FLEXIBLE COLUMN NAME DETECTION (NEW - HANDLES VARIATIONS)
# ═══════════════════════════════════════════════════════════════

def normalize_column_name(col_name):
    """Convert any column name to standard format"""
    s = str(col_name).strip().lower()
    
    # BOM Header variations
    if any(x in s for x in ["bom", "model", "header", "product"]):
        if any(x in s for x in ["header", "desc", "description", "name"]):
            return "BOM Header Desc"
        return "BOM Header"
    
    # Alternative variations
    if any(x in s for x in ["alt", "variant", "version"]):
        return "Alt"
    
    # Level variations
    if "level" in s or "lvl" in s:
        return "Level"
    
    # Parent variations
    if "parent" in s or "assembly" in s:
        return "Parent"
    
    # Component variations
    if "component" in s or "part" in s or "material" in s or "mat" in s or "part number" in s or "partnum" in s:
        if any(x in s for x in ["desc", "description", "name"]):
            return "Component descriptio"
        return "Component"
    
    # Quantity variations
    if any(x in s for x in ["qty", "quantity", "required", "req"]):
        if "base" in s or "unit" in s:
            return "Base unit"
        return "Required Qty"
    
    # Procurement variations
    if any(x in s for x in ["procurement", "special", "sp code", "type"]):
        if "special" in s or "sp" in s:
            return "Special procurement"
        return "Procurement type"
    
    # Stock variations
    if any(x in s for x in ["stock", "inventory", "qty on hand", "opening"]):
        return "Stock"
    
    # Path variations
    if "path" in s:
        return "Path"
    
    # Return original if no match
    return col_name

def auto_map_columns(df, required_cols):
    """
    Automatically map user's column names to standard names
    
    Parameters:
    df: DataFrame with user's columns
    required_cols: List of required standard column names
    
    Returns:
    df with renamed columns, mapping dict
    """
    # Create mapping from current columns to standard names
    mapping = {}
    matched = set()
    
    # Pass 0: columns that already have the exact standard name always keep it
    for col in df.columns:
        if col in required_cols and col not in matched:
            mapping[col] = col
            matched.add(col)
    
    # First pass: exact matches
    for col in df.columns:
        if col in mapping: continue
        normalized = normalize_column_name(col)
        if normalized in required_cols and normalized not in matched:
            mapping[col] = normalized
            matched.add(normalized)
    
    # Second pass: fuzzy matching for unmapped required columns
    for req_col in required_cols:
        if req_col not in matched:
            # Try to find best match by similar keywords
            for col in df.columns:
                if col not in mapping:
                    norm = normalize_column_name(col)
                    # If normalized name contains same keywords as required
                    if req_col.lower() in norm.lower() or norm.lower() in req_col.lower():
                        mapping[col] = req_col
                        matched.add(req_col)
                        break
    
    # Apply mapping
    df_mapped = df.rename(columns=mapping)
    
    return df_mapped, mapping

def verify_bom_columns(df):
    """
    Verify and auto-fix BOM DataFrame
    Handles flexible column names
    """
    required = ["BOM Header", "Level", "Component", "Required Qty"]
    
    # Auto-map columns
    df, mapping = auto_map_columns(df, required)
    
    # Check for missing required columns
    missing = [c for c in required if c not in df.columns]
    if missing:
        return None, f"Missing columns: {', '.join(missing)}"
    
    # Auto-rename/create optional columns that might be named differently
    optional_mappings = {
        "BOM Header Desc": ["BOM Header Desc", "BOM Header Description", "Model Description", "Description"],
        "Alt": ["Alt", "Alt.", "Alternative", "Variant", "Version"],
        "Component descriptio": ["Component descriptio", "Component Description", "Component Desc", "Part Description"],
        "Special procurement": ["Special procurement", "SP Code", "Procurement Type", "Type"],
        "Base unit": ["Base unit", "Unit", "UOM"],
        "Parent": ["Parent", "Parent Component", "Assembly"],
        "Path": ["Path", "Component Path"],
        "Procurement type": ["Procurement type", "Procurement Type"]
    }
    
    # Try to map optional columns
    for standard_name, variants in optional_mappings.items():
        if standard_name not in df.columns:
            for col in df.columns:
                if col in required: continue
                norm = normalize_column_name(col)
                if norm == standard_name and col != standard_name:
                    df = df.rename(columns={col: standard_name})
                    break
    
    return df, None

def verify_requirement_columns(df):
    """
    Verify and auto-fix Requirement DataFrame
    Handles flexible column names
    """
    required = ["BOM Header"]
    
    # Auto-map columns
    df, mapping = auto_map_columns(df, required)
    
    if "BOM Header" not in df.columns:
        return None, "BOM Header column not found"
    
    # Try to find Alt column
    if "Alt" not in df.columns:
        for col in df.columns:
            if normalize_column_name(col) == "Alt":
                df = df.rename(columns={col: "Alt"})
                break
    
    # Ensure Alt exists
    if "Alt" not in df.columns:
        df.insert(1, "Alt", "A")  # Default to "A"
    
    return df, None

def verify_stock_columns(df):
    """
    Verify and auto-fix Stock DataFrame
    Handles flexible column names
    """
    required = ["Component", "Stock"]
    
    # Auto-map columns
    df, mapping = auto_map_columns(df, required)
    
    missing = [c for c in required if c not in df.columns]
    if missing:
        return None, f"Missing columns: {', '.join(missing)}"
    
    return df, None


# ═══════════════════════════════════════════════════════════════
# TEMPLATE GENERATION FUNCTIONS (NEW - FOR DOWNLOAD FEATURE)
# ═══════════════════════════════════════════════════════════════

def create_requirement_template():
    """Generate sample Requirement & Stock template"""
    template_data = {
        "BOM Header": ["MODEL-001", "MODEL-002", "MODEL-003"],
        "Alt.": ["A", "B", "A"],
        "2025-01": [100, 150, 200],
        "2025-02": [120, 160, 210],
        "2025-03": [110, 155, 205],
        "2025-04": [130, 170, 220],
    }
    df = pd.DataFrame(template_data)
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, sheet_name="Requirement", index=False)
    buf.seek(0)
    return buf

def create_bom_template():
    """Generate sample BOM template"""
    template_data = {
        "BOM Header": ["MODEL-001", "MODEL-001", "MODEL-002", "MODEL-002"],
        "BOM Header Desc": ["Model 001", "Model 001", "Model 002", "Model 002"],
        "Level": [1, 1, 1, 1],
        "Parent": ["", "", "", ""],
        "Component": ["COMP-A", "COMP-B", "COMP-A", "COMP-C"],
        "Component descriptio": ["Component A", "Component B", "Component A", "Component C"],
        "Required Qty": [2, 3, 2, 1],
        "Special procurement": ["", "", "", ""],
    }
    df = pd.DataFrame(template_data)
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, sheet_name="BOM", index=False)
    buf.seek(0)
    return buf

def create_stock_template():
    """Generate sample Stock template"""
    template_data = {
        "Component": ["COMP-A", "COMP-B", "COMP-C"],
        "Stock": [500, 300, 200],
    }
    df = pd.DataFrame(template_data)
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, sheet_name="Stock", index=False)
    buf.seek(0)
    return buf

def create_consumption_template():
    """Generate sample Consumption template"""
    template_data = {
        "Component": ["COMP-A", "COMP-B", "COMP-C"],
        "May-26": [100, 75, 50],
        "Jun-26": [110, 80, 55],
        "Jul-26": [120, 85, 60],
    }
    df = pd.DataFrame(template_data)
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, sheet_name="Consumption", index=False)
    buf.seek(0)
    return buf

def create_segments_template():
    """Generate sample Segments template"""
    template_data = {
        "Component": ["COMP-A", "COMP-B", "COMP-C"],
        "Segment": ["A", "B", "A"],
    }
    df = pd.DataFrame(template_data)
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, sheet_name="Segments", index=False)
    buf.seek(0)
    return buf

def create_receipts_template():
    """Generate sample Receipts template"""
    template_data = {
        "Component": ["COMP-A", "COMP-B", "COMP-C"],
        "May-26": [200, 150, 100],
        "Jun-26": [150, 120, 80],
        "Jul-26": [180, 140, 90],
    }
    df = pd.DataFrame(template_data)
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, sheet_name="Receipts", index=False)
    buf.seek(0)
    return buf


# ═══════════════════════════════════════════════════════════════
# MRP ENGINE
# ═══════════════════════════════════════════════════════════════
def run_mrp_engine(bom_bytes, req_bytes, prod_bytes, receipt_bytes):
    logs=[]; log=lambda m: logs.append(m)
    status=st.status("Running MRP engine ...",expanded=True)

    with status: st.write("► Building BOM ...")
    bom=pd.read_excel(io.BytesIO(bom_bytes)); bom.columns=bom.columns.str.strip()
    
    # NEW: Use flexible column detection
    bom, bom_error = verify_bom_columns(bom)
    if bom_error:
        st.error(f"BOM Error: {bom_error}"); 
        return None
    
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
    for old,new in [("Component description","Component descriptio"),("BOM header description","BOM header descripti"),
                    ("BOM Header Desc","BOM header descripti")]:
        if old in bom.columns: bom=bom.rename(columns={old:new})
    keep=["BOM Header","BOM header descripti","Alt","Level","Path","Parent","Component","Component descriptio","Required Qty","Base unit","Procurement type","Special procurement"]
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
    req_f.seek(0); _req_sh=resolve_sheet(req_f,"Requirement"); req_f.seek(0)
    req=pd.read_excel(req_f,sheet_name=_req_sh,header=None)
    req.columns=[standardize_req_header(x) for x in req.iloc[hrrow].tolist()]
    req=req.iloc[hrrow+1:].reset_index(drop=True)
    req=req.loc[:,[str(c).strip()!="" for c in req.columns]]
    req=req.loc[:,~pd.Index(req.columns).duplicated(keep="first")]
    
    # NEW: Use flexible column detection for requirement
    req, req_error = verify_requirement_columns(req)
    if req_error:
        st.error(f"Requirement Error: {req_error}"); 
        return None
    
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
    req_f.seek(0); _stk_sh=resolve_sheet(req_f,"Stock"); req_f.seek(0)
    stock_raw=pd.read_excel(req_f,sheet_name=_stk_sh,usecols=[0,1],header=0,names=["Component","Stock_Qty"])
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
def _interchange_col(cols):
    """Column naming interchangeable-part groups (same hardware, only EPROM / firmware differs)."""
    return next((c for c in cols if "interchang" in str(c).lower() or "common group" in str(c).lower()),None)

def _interchange_map(df,part_col,ig_col):
    """{part code: group name} for rows with a group; blank group = part stands alone."""
    if not ig_col: return {}
    g=df[[part_col,ig_col]].copy(); g[ig_col]=g[ig_col].fillna("").astype(str).str.strip()
    g=g[(g[ig_col]!="")&(g[ig_col].str.lower()!="nan")]
    return {str(p).strip():"⇄ "+v for p,v in zip(g[part_col],g[ig_col])}

def load_interchange_map(seg_bytes):
    """Interchange groups from the Segment & Import Part file's import-part sheet (empty if none)."""
    if not seg_bytes: return {}
    try: return load_seg_imp(io.BytesIO(seg_bytes))[3]
    except Exception: return {}

def pool_interchange(stock, ig_map, parts=None):
    """Pooled stock per group (sum of member codes) + {group: [members]}. Non-grouped parts keep their own stock."""
    members=defaultdict(list)
    for p,g in ig_map.items():
        if parts is None or p in parts: members[g].append(p)
    pooled=stock.copy().astype(float)
    for g,mem in members.items(): pooled[g]=float(sum(float(stock.get(m,0)) for m in mem))
    return pooled,{g:sorted(m) for g,m in members.items()}

def load_seg_imp(f):
    xl=pd.ExcelFile(f); sheets=xl.sheet_names
    imp_sh=next((s for s in sheets if "import" in s.lower()),sheets[0])
    imp=pd.read_excel(f,sheet_name=imp_sh,header=0,dtype=str); imp.columns=[str(c).strip() for c in imp.columns]
    cc=imp.columns[0]; imp=imp[imp[cc].notna()].copy(); imp[cc]=imp[cc].astype(str).str.strip()
    imp=imp[(imp[cc]!="")&(imp[cc].str.lower()!="nan")]
    ig_col=_interchange_col(imp.columns)
    rm_col=next((c for c in imp.columns if c!=ig_col and ("rm" in c.lower() or "group" in c.lower() or "category" in c.lower())),None)
    rm_map={}
    if rm_col: imp[rm_col]=imp[rm_col].fillna("").astype(str).str.strip(); rm_map=dict(zip(imp[cc],imp[rm_col]))
    ig_map=_interchange_map(imp,cc,ig_col)
    import_parts=sorted(imp[cc].unique())
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
    return import_parts,seg,rm_map,ig_map

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
    import_parts,seg_df,rm_map,ig_map=load_seg_imp(f)
    kn=set(bom["Component"].astype(str))
    _al=align_part_codes(pd.DataFrame({"Part":import_parts}),kn)["Part"].tolist()
    ren=dict(zip(import_parts,_al)); import_parts=sorted(set(_al))
    rm_map={ren.get(p,p):v for p,v in rm_map.items()}; ig_map={ren.get(p,p):v for p,v in ig_map.items()}
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
    fg_list=[]; fgseg={}; fgidu={}; fgodu={}; fgcomb={}; fgside={}; skipped=[]
    for _,row in seg_df.iterrows():
        fg=row["FG_Code"]; seg=row["Segment"]; idu=row["IDU"]; odu=row["Compatible_ODU"]
        if not odu or odu=="nan": skipped.append(f"{fg}: no ODU"); continue
        ir=idu_r.get(idu,{}); or_=odu_r.get(odu,{})
        if not ir and not or_: skipped.append(f"{fg}: no import parts"); continue
        ap=set(ir)|set(or_); comb={p:ir.get(p,0)+or_.get(p,0) for p in ap if ir.get(p,0)+or_.get(p,0)>0}
        fg_list.append(fg); fgseg[fg]=seg; fgidu[fg]=idu; fgodu[fg]=odu; fgcomb[fg]=comb; fgside[fg]=(dict(ir),dict(or_))
    if not fg_list: st.error("No valid FG codes."); return None
    # Interchangeable parts: pool member codes into one group row (qty per set and stock both summed)
    ig_act={p:g for p,g in ig_map.items() if p in tset}
    stock,group_members=pool_interchange(stock,ig_act,tset)
    if ig_act:
        for fg in fg_list:
            pc=defaultdict(float)
            for p,q in fgcomb[fg].items(): pc[ig_act.get(p,p)]+=q
            fgcomb[fg]=dict(pc)
        for g,mem in group_members.items(): rm_map[g]=rm_map.get(mem[0],"—")
        import_parts=sorted({ig_act.get(p,p) for p in import_parts})
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
                       "Limiting_Stock":int(stock.get(lp,0)) if lp!="—" else 0,"combined_req":cq,
                       "IDU_req":fgside[fg][0],"ODU_req":fgside[fg][1]})
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
                skipped_segs=skipped,rm_map=rm_map,active_rm_groups=active_rm,
                group_members=group_members,part_group=ig_act)


WEEKS=["WK01","WK02","WK03","WK04"]

def _week_of_month(ts):
    """Day 1-7 → WK01, 8-14 → WK02, 15-21 → WK03, 22-31 → WK04."""
    return WEEKS[min(3,(ts.day-1)//7)]

def _month_starts(months):
    parsed=[parse_col_to_date(m)[0] for m in months]
    yr=infer_year([{"ts":t} for t in parsed if t is not None])
    out=[]
    for m in months:
        t,_=parse_col_to_date(m,default_year=yr)
        out.append(pd.Timestamp(t).normalize().replace(day=1) if t is not None else pd.NaT)
    return out

def import_arrivals_by_week(po_df, months):
    """{(part, month, week): qty}. ETA before first month → first month WK01; after last month → dropped."""
    mts=_month_starts(months); arr=defaultdict(float)
    if po_df is None or po_df.empty or any(pd.isna(t) for t in mts): return arr
    horizon_end=mts[-1]+pd.offsets.MonthEnd(0)
    for _,r in po_df.iterrows():
        eta=r["ETA"]
        if pd.isna(eta) or eta>horizon_end: continue
        if eta<mts[0]: m,w=months[0],WEEKS[0]
        else:
            i=max(j for j,t in enumerate(mts) if eta>=t); m,w=months[i],_week_of_month(eta)
        arr[(str(r["Part"]).strip(),m,w)]+=float(r["PO_Qty"])
    return arr

def segment_monthwise(seg_r, mrp_r, basis="max", po_df=None):
    """Month-wise set rollover per FG with weekly import arrivals converted into sets.
    Opening(first month) = sets from stock; Opening(next) = previous Balance.
    Arrival sets per week = extra sets the LP can make once that week's import parts land (never taking back earlier sets).
    Balance = max(0, Opening + Arrivals − Req); Shortfall = max(0, Req − Opening − Arrivals).
    basis="max": LP maximises total sets; basis="req": each FG capped at its total horizon requirement."""
    months=list(mrp_r["months"]); req=mrp_r["req"].copy()
    req["BOM Header"]=req["BOM Header"].astype(str).str.strip()
    mcols=[m for m in months if m in req.columns]
    req_by_hdr=req.groupby("BOM Header")[mcols].sum() if mcols else pd.DataFrame()
    hdrs=set(req_by_hdr.index); fg_res=seg_r["fg_results"]
    if not fg_res or not mcols: return pd.DataFrame(),mcols

    # Requirement per FG: match on FG code, else IDU code (ODU is shared across sets, so not used)
    fg_req={}; fg_src={}; fg_alt={}
    req["_tot"]=req[mcols].sum(axis=1)
    bom=mrp_r["bom"]
    def _alts(code):
        a=req[(req["BOM Header"]==code)&(req["_tot"]>0)]["Alt"].astype(str).unique().tolist() or \
          req[req["BOM Header"]==code]["Alt"].astype(str).unique().tolist()
        return ", ".join(sorted(a,key=lambda x:(len(x),x)))
    for f in fg_res:
        for lbl,code in [("FG",f["FG_Code"]),("IDU",f["IDU"])]:
            if code in hdrs:
                fg_req[f["FG_Code"]]={m:float(req_by_hdr.at[code,m]) for m in mcols}; fg_src[f["FG_Code"]]=lbl
                fg_alt[f["FG_Code"]]=_alts(code); break
        else:
            fg_req[f["FG_Code"]]={m:0.0 for m in mcols}; fg_src[f["FG_Code"]]="Not in Req"
            ba=sorted(bom[bom["BOM Header"]==f["IDU"]]["Alt"].astype(str).unique().tolist())
            fg_alt[f["FG_Code"]]=ba[0] if ba else ""  # alt used by the segment BOM explosion

    fgs=[f["FG_Code"] for f in fg_res]; stock=seg_r["stock"]
    parts=sorted({p for f in fg_res for p in f["combined_req"]})
    A=np.array([[f["combined_req"].get(p,0) for f in fg_res] for p in parts],dtype=float)
    ub=[sum(fg_req[fg].values()) if basis=="req" else None for fg in fgs]
    po_al=align_part_codes(po_df,_mrp_known_codes(mrp_r))
    if po_al is not None and seg_r.get("part_group"):
        po_al=po_al.copy(); po_al["Part"]=po_al["Part"].map(lambda p:seg_r["part_group"].get(p,p))
    arr=import_arrivals_by_week(po_al,mcols)

    nf,nm=len(fgs),len(mcols)
    def solve(b,lb):
        if not parts: return np.array(lb,dtype=float)
        if basis!="req":
            res=linprog(-np.ones(nf),A_ub=A,b_ub=b,bounds=list(zip(lb,ub)),method="highs")
            return res.x if res.status in (0,1) else np.array(lb,dtype=float)
        # Aligned: one variable per (FG, month) capped at that month's requirement; earlier months weigh more,
        # so material covers every model's near-term demand before anyone's later months.
        Ax=np.repeat(A,nm,axis=1)                              # column f*nm+k uses FG f's qty per set
        L=np.zeros((nf,nf*nm))
        for f in range(nf): L[f,f*nm:(f+1)*nm]=-1.0           # keep sets already counted: Σ_k x[f,k] ≥ lb[f]
        w=np.tile([1.0+0.01*(nm-k) for k in range(nm)],nf)
        bnd=[(0,fg_req[fgs[f]][mcols[k]]) for f in range(nf) for k in range(nm)]
        res=linprog(-w,A_ub=np.vstack([Ax,L]),b_ub=np.concatenate([b,-np.asarray(lb,dtype=float)]),bounds=bnd,method="highs")
        return res.x.reshape(nf,nm).sum(axis=1) if res.status in (0,1) else np.array(lb,dtype=float)

    # Capacity timeline: stock only, then stock + cumulative arrivals after each week
    supply=np.array([float(stock.get(p,0)) for p in parts],dtype=float)
    x=solve(supply,[0.0]*len(fgs)); prev=np.floor(x+1e-9)
    opening0=dict(zip(fgs,prev.astype(int).tolist())); inc={}
    for m in mcols:
        for w in WEEKS:
            add=np.array([arr.get((p,m,w),0.0) for p in parts],dtype=float)
            if add.any():
                supply=supply+add; x=solve(supply,list(prev)); cur=np.maximum(np.floor(x+1e-9),prev)
            else: cur=prev
            for fg,d in zip(fgs,cur-prev): inc[(fg,m,w)]=float(d)
            prev=cur

    rows=[]
    for f in fg_res:
        fg=f["FG_Code"]; avail=float(opening0[fg])
        for m in mcols:
            wk={w:inc[(fg,m,w)] for w in WEEKS}; tot_arr=sum(wk.values())
            rq=fg_req[fg][m]; have=avail+tot_arr
            bal=max(0.0,have-rq); sf=max(0.0,rq-have)
            rows.append({"Segment":f["Segment"],"FG Code":fg,"FG Description":f.get("FG_Desc","") or f.get("IDU_Desc",""),
                         "Alt BOM":fg_alt[fg],"Req matched on":fg_src[fg],"Month":m,"Sets Available":avail,"Requirement":rq,
                         **{w:wk[w] for w in WEEKS},"Arrival Sets":tot_arr,
                         "Balance c/f":bal,"Net Shortfall":sf})
            avail=bal
    out=pd.DataFrame(rows)
    # Alt per BOM header: alt(s) with demand in the Requirement sheet, else the alt used by the segment explosion
    hdr_alt={}
    for f in fg_res:
        for code in (f["IDU"],f["Compatible_ODU"]):
            if code in hdr_alt or not code: continue
            a=_alts(code) if code in hdrs else ""
            if not a:
                ba=sorted(bom[bom["BOM Header"]==code]["Alt"].astype(str).unique().tolist()); a=ba[0] if ba else ""
            hdr_alt[code]=a
    out.attrs["ctx"]=dict(fg_req=fg_req,arr={"|".join(k):v for k,v in arr.items()},hdr_alt=hdr_alt)
    return out,mcols

def component_monthwise(seg_r, mw, mcols, desc_map=None, sup_map=None):
    """Component-level ledger in pieces: one row per FG × BOM header (IDU/ODU) × import component.
    Req = FG req × qty per set. Stock (pooled per interchange group) and PO arrivals are shared by all rows using
    that component and consumed in table order: Available = what is left when the row is reached, Balance is handed
    to the next row using the same component, and the last balance carries into next month."""
    ctx=mw.attrs.get("ctx",{}); fg_req=ctx.get("fg_req",{}); arr=ctx.get("arr",{}); hdr_alt=ctx.get("hdr_alt",{})
    pg=seg_r.get("part_group",{}); stock=seg_r["stock"]
    meta=mw.drop_duplicates("FG Code").set_index("FG Code")
    order=meta.sort_values("Segment",kind="stable").index.tolist()
    lines=[]
    for f in seg_r["fg_results"]:
        if f["FG_Code"] not in meta.index: continue
        sides=[("IDU",f["IDU"],f.get("IDU_req")),("ODU",f["Compatible_ODU"],f.get("ODU_req"))]
        if sides[0][2] is None: sides=[("IDU+ODU",f"{f['IDU']} + {f['Compatible_ODU']}",f["combined_req"])]
        for side,hdr,rq in sides:
            for p,q in sorted((rq or {}).items()):
                if q>0: lines.append((f["FG_Code"],side,hdr,p,pg.get(p,p),q,hdr_alt.get(hdr,"")))
    lines.sort(key=lambda x:order.index(x[0]) if x[0] in order else 1e9)
    left={}; firsts=defaultdict(set); rows=[]
    for k in {l[4] for l in lines}: left[k]=float(stock.get(k,0))
    for m in mcols:
        seen=set()
        for fg,side,hdr,p,key,q,alt in lines:
            av=left[key]
            wk={w:(float(arr.get(f"{key}|{m}|{w}",0.0)) if key not in seen else 0.0) for w in WEEKS}; seen.add(key)
            rq=float(fg_req.get(fg,{}).get(m,0.0))*q; tot=sum(wk.values())
            bal=max(0.0,av+tot-rq); sf=max(0.0,rq-av-tot); left[key]=bal
            mt=meta.loc[fg]
            rows.append({"Segment":mt["Segment"],"Alt BOM":alt,"FG Description":mt["FG Description"],"FG Code":fg,
                         "Category":side,"IDU / ODU":hdr,"Component":p,
                         "Description":(desc_map or {}).get(p,""),"Supplier":(sup_map or {}).get(p,""),
                         "Key":key,"Qty / set":q,"Month":m,
                         "Sets Available":av,"Requirement":rq,**wk,"Arrival Sets":tot,"Balance c/f":bal,"Net Shortfall":sf})
    return pd.DataFrame(rows)

MODEL_KEYS={"Segment":"Segment","FG Code":"FG Code","Category":"Category","IDU / ODU":"IDU / ODU",
            "Alt BOM":"Alt BOM","Component":"Component","Description":"Description","Supplier":"Supplier",
            "Qty / set":"Qty / set","Unit":"Unit"}

def model_with_components(mw, cmw):
    """Long table for the Model + components view: per FG its import component rows in pieces
    (which part is short, per BOM header). FG set totals are in the Model-wise (sets) tab."""
    num=["Sets Available","Requirement"]+WEEKS+["Arrival Sets","Balance c/f","Net Shortfall"]
    parts=[]
    comp=cmw.copy() if not cmw.empty else pd.DataFrame(columns=list(MODEL_KEYS)+["Month"]+num)
    if not comp.empty:
        comp["Qty / set"]=comp["Qty / set"].map(lambda v:f"{v:g}"); comp["Unit"]="Pcs"
    for fg in mw["FG Code"].drop_duplicates():
        parts.append(comp[comp["FG Code"]==fg])
    out=pd.concat(parts,ignore_index=True)
    return out[list(MODEL_KEYS)+["Month"]+num]

def component_shortage(cmw, mcols, arr, seg_r):
    """One row per import component (or ⇄ interchange group), all FGs together, in pieces; plus where it is used
    and the week-wise arrivals."""
    if cmw.empty: return pd.DataFrame(),pd.DataFrame()
    num=["Sets Available","Requirement"]+WEEKS+["Arrival Sets","Balance c/f","Net Shortfall"]
    members=seg_r.get("group_members",{}); rows=[]; info=[]
    pm=pretty_months(mcols)
    for key,g in cmw.groupby("Key",sort=False):
        codes=", ".join(members.get(key,[])) or key
        hdrs=", ".join(sorted(g["IDU / ODU"].astype(str).unique()))
        fgs=", ".join(sorted(g["FG Code"].unique()))
        for m in mcols:
            gm=g[g["Month"]==m]
            if gm.empty: continue
            rows.append({"Component":key,"Codes":codes,"Used in BOM headers":hdrs,"FG codes":fgs,"Month":m,
                         "Sets Available":gm["Sets Available"].iloc[0],"Requirement":gm["Requirement"].sum(),
                         **{w:gm[w].sum() for w in WEEKS},"Arrival Sets":gm["Arrival Sets"].sum(),
                         "Balance c/f":gm["Balance c/f"].iloc[-1],"Net Shortfall":gm["Net Shortfall"].sum()})
        sched=[(m,w,arr.get(f"{key}|{m}|{w}",0.0)) for m in mcols for w in WEEKS]
        sf=[m for m in mcols if g[g["Month"]==m]["Net Shortfall"].sum()>0]
        info.append({"Component":key,"Codes":codes,"Used in BOM headers":hdrs,"FG codes":fgs,
                     "Total shortfall":g["Net Shortfall"].sum(),"First short month":pm[sf[0]] if sf else "—",
                     "Arrivals (week-wise)":"; ".join(f"{pm[m]} {w}: {q:,.0f}" for m,w,q in sched if q>0) or "No PO in horizon"})
    long=pd.DataFrame(rows)
    order=pd.DataFrame(info).sort_values("Total shortfall",ascending=False,kind="stable")
    long["_o"]=long["Component"].map({k:i for i,k in enumerate(order["Component"])})
    long=long.sort_values(["_o"],kind="stable").drop(columns="_o")
    return long,order.reset_index(drop=True)

def pretty_months(months):
    """Display labels: 'Sep-26' (or '26-Sep-26' when two columns fall in the same month)."""
    ts=_month_starts(months); full={}
    for m in months:
        t,_=parse_col_to_date(m); full[m]=pd.Timestamp(t) if t is not None else None
    if any(v is None for v in full.values()): return {m:str(m) for m in months}
    lab={m:full[m].strftime("%b-%y") for m in months}
    if len(set(lab.values()))<len(months): lab={m:full[m].strftime("%d-%b-%y") for m in months}
    return lab

MW_METRICS=["Available","Req"]+WEEKS+["Balance","Shortfall","Remarks"]

def _mw_remark(av,rq,arrivals,sf):
    if rq==0 and av==0 and arrivals==0: return ""
    if sf>0:
        if av+arrivals==0: return "No material"
        return f"Short {sf:,.0f}"
    if arrivals>0 and av<rq: return "Covered by arrival"
    return "OK"

def monthwise_grouped(long_df,keys,mcols,keep_order=False,total=True):
    """Rows = keys (e.g. Segment); for each month the MW_METRICS block, like the planning sheet."""
    agg=["Sets Available","Requirement"]+WEEKS+["Arrival Sets","Balance c/f","Net Shortfall"]
    g=long_df.groupby(keys+["Month"],as_index=False,sort=False)[agg].sum()
    base=long_df[keys].drop_duplicates().reset_index(drop=True)
    tot_req=long_df.groupby(keys,sort=False)["Requirement"].sum().rename("_r").reset_index()
    base=base.merge(tot_req,on=keys)
    if not keep_order: base=base.sort_values("_r",ascending=False,kind="stable")
    base=base.drop(columns="_r").reset_index(drop=True)
    cols={}
    for m in mcols:
        gm=base.merge(g[g["Month"]==m],on=keys,how="left").fillna(0)
        cols[(m,"Available")]=gm["Sets Available"].values; cols[(m,"Req")]=gm["Requirement"].values
        for w in WEEKS: cols[(m,w)]=gm[w].values
        cols[(m,"Balance")]=gm["Balance c/f"].values; cols[(m,"Shortfall")]=gm["Net Shortfall"].values
        cols[(m,"Remarks")]=[_mw_remark(a,r,x,s) for a,r,x,s in zip(gm["Sets Available"],gm["Requirement"],gm["Arrival Sets"],gm["Net Shortfall"])]
    out=pd.DataFrame(cols); out.columns=pd.MultiIndex.from_tuples(out.columns)
    left=base.copy(); left.columns=pd.MultiIndex.from_tuples([("",k) for k in keys])
    out=pd.concat([left,out],axis=1)
    if not total: return out
    # TOTAL row: Available = opening, Balance = closing, flows summed per month block
    tr={("",k):"" for k in keys}; tr[("",keys[0])]="TOTAL"
    for m in mcols:
        for mt in MW_METRICS:
            if mt=="Remarks": continue
            tr[(m,mt)]=float(out[(m,mt)].sum())
        tr[(m,"Remarks")]=_mw_remark(tr[(m,"Available")],tr[(m,"Req")],sum(tr[(m,w)] for w in WEEKS),tr[(m,"Shortfall")])
    return pd.concat([out,pd.DataFrame([tr],columns=out.columns)],ignore_index=True)

KEY_COL_WIDTH={"Segment":140,"Model":150,"FG Code":165,"Category":78,"IDU / ODU":100,"Alt BOM":76,"Component":135,
               "Qty / set":66,"Unit":48,"Description":190,"Supplier":150,"Codes":160,"Used in BOM headers":150,"FG codes":170}

def grouped_table_html(df,key_labels,freeze=(),weeks=True):
    """Two-row header HTML table: month blocks with 'Arrival Week' spanning WK01-WK04.
    freeze: key columns that stay pinned on the left while scrolling sideways through the months."""
    import html as _h
    keys=[c for c in df.columns if c[0]==""]; months=list(dict.fromkeys(c[0] for c in df.columns if c[0]!=""))
    labels=[key_labels.get(k[1],k[1]) for k in keys]
    widths=[KEY_COL_WIDTH.get(l,110) for l in labels]
    fz=[i for i,l in enumerate(labels) if l in freeze]
    lefts={i:sum(widths[j] for j in fz if j<i) for i in fz}
    def kst(i,bg,z):
        w=widths[i]; base=f"min-width:{w}px;max-width:{w}px;width:{w}px;box-sizing:border-box;overflow:hidden;text-overflow:ellipsis;"
        if i not in lefts: return base
        edge="box-shadow:inset -2px 0 0 #94a3b8;" if i==fz[-1] else ""
        return base+f"position:sticky;left:{lefts[i]}px;z-index:{z};background:{bg};{edge}"
    th_base="border:1px solid #d1d5db;padding:4px 8px;background:#f3f4f6;font-weight:700;text-align:center;white-space:nowrap;"
    th=f'style="{th_base}"'
    thm='style="border:1px solid #d1d5db;padding:4px 8px;background:#e0ecff;font-weight:700;text-align:center;"'
    h0="<tr>"+"".join(f'<th style="{th_base}{kst(i,"#f3f4f6",4)}" rowspan="3" title="{_h.escape(l)}">{_h.escape(l)}</th>' for i,l in enumerate(labels))
    pm=pretty_months(months)
    mets=MW_METRICS if weeks else [x for x in MW_METRICS if x not in WEEKS]
    h0+="".join(f'<th {thm} colspan="{len(mets)}">{_h.escape(pm[m])}</th>' for m in months)+"</tr>"
    h1="<tr>"; h2="<tr>"
    for m in months:
        if not weeks:
            h1+="".join(f'<th {th} rowspan="2">{x}</th>' for x in mets); continue
        h1+=f'<th {th} rowspan="2">Available</th><th {th} rowspan="2">Req</th><th {th} colspan="4">Arrival Week</th>'
        h1+=f'<th {th} rowspan="2">Balance</th><th {th} rowspan="2">Shortfall</th><th {th} rowspan="2">Remarks</th>'
        h2+="".join(f"<th {th}>{w}</th>" for w in WEEKS)
    h1+="</tr>"; h2+="</tr>"
    body=""
    for i,row in df.iterrows():
        is_tot=str(row[keys[0]])=="TOTAL"
        is_set=("","Unit") in df.columns and row[("","Unit")]=="Sets"
        tr_style=' style="background:#f9fafb;font-weight:700;"' if is_tot else (' style="background:#eef4ff;font-weight:700;border-top:2px solid #93c5fd;"' if is_set else "")
        rbg="#f9fafb" if is_tot else ("#eef4ff" if is_set else "#ffffff")
        _kv=lambda v:f"{v:g}" if isinstance(v,float) else str(v)
        cells="".join(f'<td style="border:1px solid #e5e7eb;padding:4px 8px;white-space:nowrap;{kst(i,rbg,2)}" title="{_h.escape(_kv(row[k]))}">{_h.escape(_kv(row[k]))}</td>'
                      for i,k in enumerate(keys))
        for m in months:
            for mt in mets:
                v=row[(m,mt)]; st_="border:1px solid #e5e7eb;padding:4px 8px;text-align:right;"
                if mt=="Remarks":
                    col="#dc2626" if str(v).startswith(("Short","No ")) else "#15803d" if v else "#6b7280"
                    cells+=f'<td style="{st_}text-align:left;color:{col};white-space:nowrap;">{_h.escape(str(v))}</td>'; continue
                v=float(v)
                if mt=="Shortfall" and v>0: st_+="color:#dc2626;font-weight:700;background:#fef2f2;"
                elif mt=="Balance": st_+="background:#f0fdf4;"
                elif mt in WEEKS and v>0: st_+="color:#1d4ed8;background:#eff6ff;"
                txt="" if (mt in WEEKS and v==0) else f"{v:,.0f}"
                cells+=f'<td style="{st_}">{txt}</td>'
        body+=f"<tr{tr_style}>{cells}</tr>"
    return ('<div style="overflow-x:auto;max-height:560px;border:1px solid #e5e7eb;border-radius:8px;margin-bottom:8px;">'
            '<table style="border-collapse:collapse;font-size:12px;font-family:\'Plus Jakarta Sans\',sans-serif;background:#fff;">'
            f"<thead>{h0}{h1}{h2}</thead><tbody>{body}</tbody></table></div>")

def show_grouped_table(df,key_labels,freeze=(),weeks=True):
    """Render the grouped table inside its own frame so every Streamlit version shows it exactly as built
    (merged month headers, colours, pinned columns, sideways scroll) — st.markdown may strip the styling."""
    html=grouped_table_html(df,key_labels,freeze=freeze,weeks=weeks)   # every cell value is html-escaped
    h=min(600,3*30+len(df)*29+30)
    page=('<html><head><style>body{margin:0;font-family:"Plus Jakarta Sans","Segoe UI",Arial,sans-serif;}'
          'div::-webkit-scrollbar{height:10px;width:10px}div::-webkit-scrollbar-thumb{background:#cbd5e1;border-radius:5px}'
          '</style></head><body>'+html.replace("max-height:560px","max-height:590px")+'</body></html>')
    if hasattr(st,"iframe"): st.iframe(page,height=h)            # newer Streamlit
    else:
        import streamlit.components.v1 as components               # older Streamlit
        components.html(page,height=h,scrolling=False)

def grouped_to_excel(w,df,sheet,key_labels,weeks=True):
    """Write the grouped table with merged month / 'Arrival Week' headers (weeks=False leaves out WK01-WK04)."""
    from openpyxl.styles import Alignment,Font,PatternFill,Border,Side
    ws=w.book.create_sheet(sheet)
    keys=[c for c in df.columns if c[0]==""]; months=list(dict.fromkeys(c[0] for c in df.columns if c[0]!=""))
    bold=Font(bold=True); ctr=Alignment(horizontal="center",vertical="center",wrap_text=True)
    fill=PatternFill("solid",fgColor="E0ECFF"); thin=Side(style="thin",color="BFBFBF"); bd=Border(thin,thin,thin,thin)
    c=1
    for k in keys:
        ws.cell(1,c,key_labels.get(k[1],k[1])); ws.merge_cells(start_row=1,start_column=c,end_row=3,end_column=c); c+=1
    mets=MW_METRICS if weeks else [x for x in MW_METRICS if x not in WEEKS]
    for m in months:
        ws.cell(1,c,pretty_months(months)[m]); ws.merge_cells(start_row=1,start_column=c,end_row=1,end_column=c+len(mets)-1)
        if not weeks:
            for off,lbl in enumerate(mets):
                ws.cell(2,c+off,lbl); ws.merge_cells(start_row=2,start_column=c+off,end_row=3,end_column=c+off)
            c+=len(mets); continue
        for off,lbl in enumerate(["Available","Req"]):
            ws.cell(2,c+off,lbl); ws.merge_cells(start_row=2,start_column=c+off,end_row=3,end_column=c+off)
        ws.cell(2,c+2,"Arrival Week"); ws.merge_cells(start_row=2,start_column=c+2,end_row=2,end_column=c+5)
        for i,wk in enumerate(WEEKS): ws.cell(3,c+2+i,wk)
        for off,lbl in enumerate(["Balance","Shortfall","Remarks"]):
            ws.cell(2,c+6+off,lbl); ws.merge_cells(start_row=2,start_column=c+6+off,end_row=3,end_column=c+6+off)
        c+=len(MW_METRICS)
    ncol=c-1
    for r_ in range(1,4):
        for cc in range(1,ncol+1):
            cell=ws.cell(r_,cc); cell.font=bold; cell.alignment=ctr; cell.border=bd
            if r_==1 and cc>len(keys): cell.fill=fill
    for i,(_,row) in enumerate(df.iterrows(),start=4):
        vals=[row[k] for k in keys]+[row[(m,mt)] for m in months for mt in mets]
        for j,v in enumerate(vals,start=1):
            is_wk=weeks and j>len(keys) and mets[(j-len(keys)-1)%len(mets)] in WEEKS
            cell=ws.cell(i,j,(None if isinstance(v,float) and v==0 and is_wk else v))
            cell.border=bd
            if isinstance(v,float): cell.number_format="#,##0"
            if str(row[keys[0]])=="TOTAL": cell.font=bold
    ws.freeze_panes=ws.cell(4,len(keys)+1)


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
        sheet = resolve_sheet(f_bytes, sheet)
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
    req   = pd.read_excel(io.BytesIO(req_bytes), sheet_name=resolve_sheet(req_bytes, "Requirement"), header=None)
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
# IMPORT MATERIAL SHORTAGE & COVERAGE ENGINE
# ═══════════════════════════════════════════════════════════════
IMP_PO_ALIASES = {
    "Part":        ["import part","part","part no","part number","material","material code","material no",
                    "component","component code","item","item code"],
    "Description": ["description","material description","part description","component description","desc"],
    "PO_No":       ["po","po no","po number","purchase order","purchase order no","po num"],
    "Supplier":    ["supplier","vendor","vendor name","supplier name"],
    "PO_Qty":      ["po qty","po quantity","open po qty","open qty","pending qty","balance qty","qty","quantity"],
    "ETD":         ["etd","etd date","dispatch date","ship date","shipment date"],
    "ETA":         ["eta","eta date","arrival date","expected arrival","expected arrival date"],
    "IGroup":      ["interchange group","interchangeable group","interchange","common group"],
}

def _imp_norm(c): return re.sub(r"[^a-z0-9]+"," ",str(c).lower()).strip()

def map_import_po_columns(df):
    """Map user's PO-file headers onto Part / Description / PO_No / Supplier / PO_Qty / ETD / ETA."""
    cols={c:_imp_norm(c) for c in df.columns}; mapping={}; used=set()
    # Pass 1: exact alias match
    for tgt,aliases in IMP_PO_ALIASES.items():
        c=next((c for c,n in cols.items() if c not in used and n in aliases),None)
        if c is not None: mapping[c]=tgt; used.add(c)
    # Pass 2: keyword containment for anything still missing
    kw={"ETA":lambda n:"eta" in n.split() or "arrival" in n,
        "ETD":lambda n:"etd" in n.split() or "dispatch" in n,
        "PO_Qty":lambda n:("qty" in n or "quantity" in n),
        "Description":lambda n:"desc" in n,
        "Part":lambda n:("part" in n or "material" in n or "component" in n) and "desc" not in n,
        "PO_No":lambda n:n.startswith("po") and "qty" not in n and "date" not in n,
        "Supplier":lambda n:"vendor" in n or "supplier" in n}
    for tgt,fn in kw.items():
        if tgt in mapping.values(): continue
        c=next((c for c,n in cols.items() if c not in used and fn(n)),None)
        if c is not None: mapping[c]=tgt; used.add(c)
    df=df.rename(columns=mapping)
    missing=[c for c in ["Part","PO_Qty"] if c not in df.columns]
    if "ETA" not in df.columns and "ETD" not in df.columns: missing.append("ETA or ETD")
    return df,missing

def load_import_po(po_bytes, transit_days=30):
    xl=pd.ExcelFile(io.BytesIO(po_bytes))
    sh=next((s for s in xl.sheet_names if "po" in s.lower() or "import" in s.lower()),xl.sheet_names[0])
    df=pd.read_excel(io.BytesIO(po_bytes),sheet_name=sh); df.columns=[str(c).strip() for c in df.columns]
    txt=pd.read_excel(io.BytesIO(po_bytes),sheet_name=sh,dtype=str)  # same sheet as text, keeps leading zeros
    df=df.dropna(how="all")
    df,missing=map_import_po_columns(df)
    if missing: return None,f"Could not find column(s): {', '.join(missing)}. Found: {', '.join(map(str,df.columns))}"
    for c in ["Part","PO_No"]:
        if c in df.columns: df[c]=txt.iloc[:,list(df.columns).index(c)].loc[df.index]
    for c,d in [("Description",""),("PO_No",""),("Supplier",""),("ETD",pd.NaT),("ETA",pd.NaT),("IGroup","")]:
        if c not in df.columns: df[c]=d
    df["Part"]=df["Part"].astype(str).str.strip()
    df=df[(df["Part"]!="")&(df["Part"].str.lower()!="nan")].copy()
    for c in ["Description","PO_No","Supplier","IGroup"]:
        df[c]=df[c].fillna("").astype(str).str.strip().replace("nan","")
    df["PO_Qty"]=pd.to_numeric(df["PO_Qty"].astype(str).str.replace(",","",regex=False).str.strip(),errors="coerce").fillna(0)
    for c in ["ETD","ETA"]: df[c]=pd.to_datetime(df[c],errors="coerce",dayfirst=True,format="mixed")
    # Missing ETA → ETD + transit days
    df["ETA_Estimated"]=df["ETA"].isna()&df["ETD"].notna()
    df.loc[df["ETA_Estimated"],"ETA"]=df.loc[df["ETA_Estimated"],"ETD"]+pd.Timedelta(days=int(transit_days))
    return df.reset_index(drop=True),None

def create_seg_imp_template():
    """Segment & Import Part template. 'Interchange Group': same name = same hardware (only EPROM / firmware differs),
    stock is pooled across those codes; blank = code stands alone. 'Category' drives the RM Group filter."""
    from openpyxl import Workbook
    from openpyxl.styles import Font,PatternFill,Alignment,Border,Side
    def F(size=10,**k): return Font(name="Arial",size=size,**k)
    groups=[  # (group, fill colour, category, [(code, desc)])
     ("DISP-G1","92D050","PCB-Display",[("0011801045ANP","Display pcb"),("0011801045NP","display panel")]),
     ("","FCE4D6","PCB-IDU",[("0011800613Z","IDU PCB-70R")]),
     ("IDU-G1","A6A6A6","PCB-IDU",[("0011800613X","INDOOR PCB"),("0011800613WD","INDOOR PCB-18K/19K"),("0011800613Y","INDOOR PCB"),
        ("0011800613XA","INDOOR PCB"),("0011800613WE","IDU PCB- Hot & Cool"),("0011800613XNP","Indoor PCB"),("0011800613YNP","Indoor PCB"),
        ("0011800613WA","INDOOR PCB"),("0011800613WM","IDU PCB"),("0011800613ZM","IDU PCB")]),
     ("","FFFFFF","PCB-IDU",[("0011800323AZDEL","PCB"),("0011800491CDEL","IDU computer board")]),
     ("ODU-G1","1F6B2A","PCB-ODU",[("0011801843WFNP","ODU Comoputer Board"),("0011801843WFNPA","Outdoor PCB"),("0011801843WFNPB","ODU PCB"),
        ("0011801843BFNPB","Outdoor PCB"),("0011801843BFNP","ODU Computer Board"),("0011801843BFNPA","ODU Computer Board")]),
     ("ODU-G2","F2CEEF","PCB-ODU",[("0011801843JNP","Outdoor PCB"),("0011801843JNPA","Outdoor PCB")]),
     ("ODU-G3","17405F","PCB-ODU",[("0011801490MANPB","ODU PCB"),("0011801490MANPG","Outdoor PCB"),("0011801490QNP","ODU PCB"),
        ("0011801490MANPH","Outdoor PCB"),("0011801490QNPB","Outdoor PCB"),("0011801490QNPA","ODU Computer Board")]),
     ("","FFFFFF","PCB-ODU",[("0011801118CSB","Outdoor PCB")]),
     ("ODU-G4","FFFF00","PCB-ODU",[("0011801843WNPE","Outdoor PCB"),("0011801843BNPA","ODU Computer Board"),("0011801843WNPA","Outdoor PCB"),
        ("0011801843WNPD","Outdoor PCB"),("0011801843WNP","ODU PCB"),("0011801843BNPB","ODU Computer Board"),("0011801843BNPC","ODU Computer Board"),
        ("0011801843WNPG","Outdoor PCB"),("0011801843WNPC","Outdoor PCB"),("0011801843WNPH","ODU PCB"),("0011801843WNPB","ODU PCB"),
        ("0011801843WNPCA","ODU PCB"),("0011801843WNPEA","ODU PCB"),("0011801843WNPJ","ODU PCB"),("0011801843WNPK","ODU PCB")]),
     ("","FFFFFF","PCB-TOWER",[("0011800698BGNP","INDOOR PCB")]),
    ]
    thin=Side(style="thin",color="BFBFBF"); bd=Border(thin,thin,thin,thin)
    wb=Workbook(); ws=wb.active; ws.title="Import Part"
    hdr=["Part Code","Desc.","Category","Interchange Group"]; ws.append(hdr)
    for g,colr,cat,items in groups:
        dark=colr in ("1F6B2A","17405F")
        for code,desc in items:
            ws.append([code,desc,cat,g]); r=ws.max_row
            for c in range(1,5):
                cell=ws.cell(r,c); cell.border=bd; cell.font=F(color="FFFFFF" if dark and c<=2 else "0000FF" if c==4 else "000000")
                cell.number_format="@"
                if c<=2 and colr!="FFFFFF": cell.fill=PatternFill("solid",fgColor=colr)
                if c==4: cell.fill=PatternFill("solid",fgColor="FFF2CC")
    for c in range(1,5):
        cell=ws.cell(1,c); cell.font=F(bold=True,color="FFFFFF"); cell.fill=PatternFill("solid",fgColor="1F4E78")
        cell.border=bd; cell.alignment=Alignment(horizontal="center")
    for col,w in zip("ABCD",[20,26,14,18]): ws.column_dimensions[col].width=w
    ws.freeze_panes="A2"
    sg=wb.create_sheet("Segment"); sg.append(["Segment","FG Code","IDU","ODU"])
    for row in [("1 ton 3 Star","FG-1T3S-01","IDU-CODE-1","ODU-CODE-1"),("1.5 ton 5 Star","FG-15T5S-01","IDU-CODE-2","ODU-CODE-2")]:
        sg.append(list(row))
    for c in range(1,5):
        cell=sg.cell(1,c); cell.font=F(bold=True,color="FFFFFF"); cell.fill=PatternFill("solid",fgColor="1F4E78")
        sg.column_dimensions["ABCD"[c-1]].width=18
    ins=wb.create_sheet("Instructions")
    for i,(t,b_) in enumerate([("Segment & Import Part file",True),("",False),("Sheet 'Import Part'",True),
        ("Part Code - import part code as in BOM / Stock (text, leading zeros kept).",False),
        ("Category - used as the RM Group filter on the Segment page (e.g. PCB-IDU, PCB-ODU, PCB-Display).",False),
        ("Interchange Group - codes with the SAME group name are the same hardware (only EPROM / firmware differs):",False),
        ("   their stock and PO arrivals are pooled when calculating sets and shortage. Leave blank if the code cannot be swapped.",False),
        ("Colours are only for reading - the app uses the group name, not the colour.",False),("",False),("Sheet 'Segment'",True),
        ("Segment name, FG (set) code, IDU BOM header, ODU BOM header - replace the 2 example rows.",False)],1):
        ins.cell(i,1,t).font=F(size=12 if i==1 else 10,bold=b_)
    ins.column_dimensions["A"].width=115
    buf=io.BytesIO(); wb.save(buf); buf.seek(0); return buf

def load_supplier_master(sup_bytes, known_codes=()):
    """Part-wise supplier master: first column (or 'Part/Material/Component') = part code, 'Supplier'/'Vendor' column
    = supplier (several suppliers for one part are joined). Returns ({part: supplier}, error)."""
    try:
        df=pd.read_excel(io.BytesIO(sup_bytes),dtype=str); df.columns=[str(c).strip() for c in df.columns]
    except Exception as e: return {},f"Could not read Supplier Master: {e}"
    if df.empty or len(df.columns)<2: return {},"Supplier Master needs a part code column and a supplier column."
    n=lambda c:c.lower()
    pc=next((c for c in df.columns if any(k in n(c) for k in ["part","material","component","item"]) and "desc" not in n(c)),df.columns[0])
    sc=next((c for c in df.columns if c!=pc and any(k in n(c) for k in ["supplier","vendor"]) and "code" not in n(c)),None) \
       or next((c for c in df.columns if c!=pc and any(k in n(c) for k in ["supplier","vendor"])),None) \
       or next(c for c in df.columns if c!=pc)
    d=df[[pc,sc]].dropna(); d[pc]=d[pc].astype(str).str.strip(); d[sc]=d[sc].astype(str).str.strip()
    d=d[(d[pc]!="")&(d[sc]!="")&(d[sc].str.lower()!="nan")]
    if known_codes: d[pc]=align_part_codes(d.rename(columns={pc:"Part"}),set(known_codes))["Part"].values
    return {p:", ".join(dict.fromkeys(g[sc])) for p,g in d.groupby(pc,sort=False)},None

def create_supplier_master_template():
    df=pd.DataFrame({"Part Code":["0011800613Z","0011801843WNP","0010205068HNP"],
                     "Description":["IDU PCB-70R","ODU PCB","Compressor"],
                     "Supplier":["Supplier A","Supplier B","Supplier C"]})
    buf=io.BytesIO()
    with pd.ExcelWriter(buf,engine="openpyxl") as w:
        df.to_excel(w,sheet_name="Supplier Master",index=False)
        for c in w.sheets["Supplier Master"]["A"]: c.number_format="@"
    buf.seek(0); return buf

def create_import_po_template():
    """Import PO template: one row per PO line; red headers required; grey columns show the ETA month / week."""
    from datetime import date
    from openpyxl import Workbook
    from openpyxl.styles import Font,PatternFill,Alignment,Border,Side
    from openpyxl.worksheet.datavalidation import DataValidation
    from openpyxl.workbook.properties import CalcProperties
    def F(size=10,**k): return Font(name="Arial",size=size,**k)
    wb=Workbook(); ws=wb.active; ws.title="Import PO"
    hdr=["Import Part","Description","PO No","Supplier","PO Qty","ETD","ETA","Arrival Month (auto)","Arrival Week (auto)"]
    ws.append(hdr)
    # Example rows: Oct–Dec, every arrival week used (Part, Desc, PO No, Supplier, Qty, ETD, ETA)
    C=("0010748458","Compressor Rotary 1.5T","Supplier A"); P=("0010300601","Inverter PCB Assy","Supplier B")
    M=("0010748814","BLDC Fan Motor","Supplier C")
    ex=[(C,"4500012345",1200,(9,1),(10,6)), (P,"4500012410",1500,(9,5),(10,10)), (M,"4500012433",600,(9,14),(10,17)),
        (C,"4500012399",800,(9,20),(10,24)), (P,"4500012455",1000,(10,2),(11,4)), (M,"4500012470",700,(10,8),(11,12)),
        (C,"4500012488",1500,(10,15),(11,19)), (P,"4500012502",900,(10,22),(11,27)), (M,"4500012519",500,(11,1),(12,3)),
        (C,"4500012530",1000,(11,6),(12,9)), (P,"4500012547",1200,(11,13),(12,16)), (M,"4500012560",400,(11,24),None)]
    rows=[(i[0],i[1],po,i[2],q,date(2026,*etd),date(2026,*eta) if eta else None) for i,po,q,etd,eta in ex]
    thin=Side(style="thin",color="BFBFBF"); bd=Border(thin,thin,thin,thin)
    grey=PatternFill("solid",fgColor="F2F2F2"); N=200
    for r in range(2,N+2):
        vals=rows[r-2] if r-2<len(rows) else (None,)*7
        for c,v in enumerate(vals,1):
            cell=ws.cell(r,c,v); cell.font=F(color="0000FF"); cell.border=bd
            if c in (1,3): cell.number_format="@"
            if c in (6,7): cell.number_format="dd-mmm-yy"
            if c==5: cell.number_format="#,##0"
        ws.cell(r,8,f'=IF(G{r}="","",TEXT(G{r},"mmm-yy"))')
        ws.cell(r,9,f'=IF(G{r}="","","WK0"&MIN(4,INT((DAY(G{r})-1)/7)+1))')
        for c in (8,9):
            cell=ws.cell(r,c); cell.font=F(); cell.fill=grey; cell.border=bd; cell.alignment=Alignment(horizontal="center")
    for c in range(1,len(hdr)+1):
        cell=ws.cell(1,c); cell.font=F(bold=True,color="FFFFFF"); cell.border=bd
        cell.fill=PatternFill("solid",fgColor="C00000" if c in (1,5,6,7) else "1F4E78")  # red = required
        cell.alignment=Alignment(horizontal="center",vertical="center",wrap_text=True)
    for col,w in zip("ABCDEFGHI",[16,28,14,16,10,12,12,14,14]): ws.column_dimensions[col].width=w
    ws.row_dimensions[1].height=30; ws.freeze_panes="A2"
    dv=DataValidation(type="date",operator="greaterThan",formula1="DATE(2020,1,1)",allow_blank=True,
                      error="Enter a date, e.g. 06-Oct-26",errorTitle="Date needed")
    ws.add_data_validation(dv); dv.add(f"F2:G{N+1}")
    dq=DataValidation(type="decimal",operator="greaterThanOrEqual",formula1="0",allow_blank=True,error="PO Qty must be a number >= 0")
    ws.add_data_validation(dq); dq.add(f"E2:E{N+1}")
    ins=wb.create_sheet("Instructions")
    lines=[("How to fill the Import PO template",True),("",False),
     ("One row per PO line (the same part can have many rows / POs).",False),
     ("Red headers are required: Import Part, PO Qty, and ETA (or ETD if ETA not known yet).",False),
     ("Blue text = your inputs. Replace the example rows (Oct-Dec, all 4 weeks) with your data.",False),
     ("Grey columns (Arrival Month / Week) are formulas for your reference only - the app works them out itself.",False),
     ("",False),("Columns",True),
     ("Import Part - material code as in BOM / Stock (column is text, so leading zeros are kept).",False),
     ("Description / PO No / Supplier - optional, shown in reports.",False),
     ("PO Qty - open quantity still to arrive (do not include already-received qty).",False),
     ("ETD - dispatch date from supplier.",False),
     ("ETA - arrival date at plant. If blank, the app uses ETD + Transit days (default 30) - see last example row.",False),
     ("",False),("Arrival Week rule (week of the ETA month)",True),
     ("Day 1-7 = WK01 | Day 8-14 = WK02 | Day 15-21 = WK03 | Day 22-31 = WK04",False),
     ("ETA before the first MRP month = counted in first month WK01. ETA after the last MRP month = ignored.",False),
     ("",False),("Where to upload",True),
     ("Import Shortage page, or Segment Wise page > 'Import PO file for Arrival Weeks'. Same file works for both.",False)]
    for i,(t,b_) in enumerate(lines,1): ins.cell(i,1,t).font=F(size=12 if i==1 else 10,bold=b_)
    ins.column_dimensions["A"].width=110
    wb.calculation=CalcProperties(fullCalcOnLoad=True)
    buf=io.BytesIO(); wb.save(buf); buf.seek(0); return buf

def align_part_codes(po_df, known_codes):
    """Match PO part codes to MRP/BOM codes even if one side lost leading zeros (e.g. 0010748458 vs 10748458)."""
    if po_df is None or po_df.empty: return po_df
    known=[str(k).strip() for k in known_codes]; ks=set(known)
    by_stripped={}
    for k in known: by_stripped.setdefault(k.lstrip("0") or "0",k)
    po_df=po_df.copy()
    po_df["Part"]=[p if p in ks else by_stripped.get(p.lstrip("0") or "0",p) for p in po_df["Part"].astype(str)]
    return po_df

def _mrp_known_codes(mrp_r):
    return set(mrp_r["bom"]["Component"].astype(str))|set(mrp_r["bom"]["BOM Header"].astype(str))|set(map(str,mrp_r["stock"].index))

def run_import_coverage(mrp_r, po_df, group_map=None):
    """Month-wise projection per import part: Stock + PO arrivals (by ETA bucket) − MRP gross requirement.
    group_map {part: group}: interchangeable codes are pooled — requirement, stock and POs summed per group."""
    months=list(mrp_r["months"])
    parsed=[parse_col_to_date(m)[0] for m in months]
    yr=infer_year([{"ts":t} for t in parsed])
    mts=[]
    for m in months:
        t,_=parse_col_to_date(m,default_year=yr); mts.append(pd.Timestamp(t).normalize() if t is not None else pd.NaT)
    if not months or any(pd.isna(t) for t in mts): return None,"Could not read MRP month columns as dates."
    horizon_end=mts[-1]+pd.offsets.MonthEnd(0)

    # Requirement per component per month (all BOM levels, as in the MRP pivot)
    req=pd.concat([mrp_r[k][["Component","Month","Gross_Requirement"]] for k in
                   ["result_l1","result_l2","result_l3","result_l4"] if not mrp_r[k].empty],ignore_index=True) \
          if any(not mrp_r[k].empty for k in ["result_l1","result_l2","result_l3","result_l4"]) \
          else pd.DataFrame(columns=["Component","Month","Gross_Requirement"])
    req_map=req.groupby(["Component","Month"])["Gross_Requirement"].sum().to_dict()
    desc_map={}
    for k in ["result_l1","result_l2","result_l3","result_l4"]:
        d=mrp_r[k]
        if not d.empty: desc_map.update(dict(zip(d["Component"],d["Description"])))
    stock=mrp_r["stock"]

    # Bucket each PO into an MRP month by ETA
    known=_mrp_known_codes(mrp_r)
    po=align_part_codes(po_df,known)
    members={}
    if group_map:
        gk=list(group_map); gk_al=align_part_codes(pd.DataFrame({"Part":gk}),known)["Part"].tolist()
        gmap={a:group_map[k] for k,a in zip(gk,gk_al)}
        stock,members=pool_interchange(stock,gmap)
        req_map2=defaultdict(float)
        for (c,m),v in req_map.items(): req_map2[(gmap.get(c,c),m)]+=v
        req_map=dict(req_map2)
        for g,mem in members.items():
            desc_map[g]=f"Interchangeable ({len(mem)} codes)"
        po=po.copy(); po["Part"]=po["Part"].map(lambda p:gmap.get(p,p))
    def bucket(eta):
        if pd.isna(eta): return "Unscheduled"
        if eta>horizon_end: return "Beyond horizon"
        idx=0
        for i,t in enumerate(mts):
            if eta>=t: idx=i
        return months[idx]
    po["Arrival_Month"]=po["ETA"].apply(bucket)
    po["ETA_Past_Due"]=po["ETA"].notna()&(po["ETA"]<mts[0])

    parts=list(dict.fromkeys(po["Part"].tolist()))
    summary=[]; proj=[]; po_status=[]
    for p in parts:
        pp=po[po["Part"]==p]
        desc=(desc_map.get(p,"") if p in members else "") or next((d for d in pp["Description"] if d),"") or desc_map.get(p,"")
        stk=float(stock.get(p,0))
        arr={m:float(pp.loc[pp["Arrival_Month"]==m,"PO_Qty"].sum()) for m in months}
        beyond=float(pp.loc[pp["Arrival_Month"]=="Beyond horizon","PO_Qty"].sum())
        unsched=float(pp.loc[pp["Arrival_Month"]=="Unscheduled","PO_Qty"].sum())
        bal=stk; bal_noPO=stk; first_short=None; first_short_noPO=None; max_short=0.0; tot_req=0.0
        cov_m=0; cov_noPO=0; still_cov=True; still_cov_noPO=True
        for m in months:
            rq=float(req_map.get((p,m),0)); tot_req+=rq
            opening=bal; bal=bal+arr[m]-rq; bal_noPO=bal_noPO-rq
            short=max(0.0,-bal)
            if bal<0 and first_short is None: first_short=m
            if bal_noPO<0 and first_short_noPO is None: first_short_noPO=m
            if bal<0: still_cov=False
            if bal_noPO<0: still_cov_noPO=False
            if still_cov: cov_m+=1
            if still_cov_noPO: cov_noPO+=1
            max_short=max(max_short,short)
            proj.append({"Import Part":p,"Description":desc,"Month":m,"Opening":opening,"PO Arrival":arr[m],
                         "Requirement":rq,"Closing":bal,"Shortage":short})
        tot_po=float(pp["PO_Qty"].sum())
        in_h=tot_po-beyond-unsched
        if tot_req==0: status="⚪ No demand"
        elif first_short is None: status="🟢 Covered"
        elif stk+in_h>=tot_req: status="🟠 Short – expedite PO"
        elif stk+tot_po>=tot_req: status="🟠 Short – PO beyond horizon"
        else: status="🔴 Short – new PO needed"
        nxt=pp[pp["ETA"].notna()&(pp["ETA"]>=pd.Timestamp.today().normalize())]["ETA"].min()
        summary.append({"Import Part":p,"Description":desc,"Interchangeable codes":", ".join(members.get(p,[])),"Stock":stk,"Total Requirement":tot_req,
                        "Open PO Qty":tot_po,"PO in horizon":in_h,"Closing Balance":bal,
                        "Max Shortage":max_short,"Additional PO Needed":max(0.0,-bal),
                        "First Shortage Month":first_short or "—",
                        "Covered till":(months[cov_m-1] if cov_m>0 else "Not covered") if first_short else "Full horizon",
                        "Coverage (months)":cov_m,"Coverage w/o PO (months)":cov_noPO,
                        "Stock-only shortage from":first_short_noPO or "—",
                        "Next ETA":nxt.strftime("%d-%b-%y") if pd.notna(nxt) else "—",
                        "Status":status})

        # PO-level need-by check (FIFO by ETA): when is each PO needed vs when does it land
        running={m:0.0 for m in months}; mi={m:i for i,m in enumerate(months)}
        for idx,row in pp.sort_values("ETA",na_position="last").iterrows():
            b=stk; need=None
            for m in months:
                b=b+running[m]-float(req_map.get((p,m),0))
                if b<0: need=m; break
            am=row["Arrival_Month"]
            if need is None: st_="✅ Not needed in horizon" if tot_req>0 else "⚪ No demand"
            elif am in mi and mi[am]<=mi[need]: st_="✅ On time"
            else: st_="⏰ Late – expedite"
            if am in running: running[am]+=float(row["PO_Qty"])
            po_status.append({"Import Part":p,"Description":desc,"PO No":row["PO_No"],"Supplier":row["Supplier"],
                              "PO Qty":float(row["PO_Qty"]),
                              "ETD":row["ETD"].strftime("%d-%b-%y") if pd.notna(row["ETD"]) else "—",
                              "ETA":(row["ETA"].strftime("%d-%b-%y")+(" (est.)" if row["ETA_Estimated"] else "")) if pd.notna(row["ETA"]) else "—",
                              "Arrival Month":am,"Needed by":need or "—","PO Status":st_})

    summ=pd.DataFrame(summary)
    proj_df=pd.DataFrame(proj)
    closing=proj_df.pivot_table(index=["Import Part","Description"],columns="Month",values="Closing",aggfunc="sum").reset_index() \
            if not proj_df.empty else pd.DataFrame()
    if not closing.empty: closing=closing[["Import Part","Description"]+[m for m in months if m in closing.columns]]
    not_in_mrp=[p for p in parts if not any(req_map.get((p,m),0) for m in months) and p not in stock.index]
    return dict(summary=summ,projection=proj_df,closing=closing,po_status=pd.DataFrame(po_status),
                months=months,not_in_mrp=not_in_mrp,
                unscheduled=int((po["Arrival_Month"]=="Unscheduled").sum()),
                past_due=int(po["ETA_Past_Due"].sum())),None


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

    # Main workflow nav items
    workflow_items = [
        ("🏠", "Home",                    "home",    None),
        ("📂", "Upload Files",            "upload",  None),
        ("⚙️",  "Run MRP",               "mrp",     "✓" if mrp_done else None),
        ("🏭",  "Segment Wise Available", "segment", "✓" if seg_done else None),
        ("📦",  "Aging Projection",       "aging",   "✓" if ag_done else None),
        ("🚢",  "Import Shortage",        "import",  "✓" if st.session_state["imp_results"] is not None else None),
    ]
    # Tools / views nav items
    tools_items = [
        ("📋",  "Production Plan",        "plan",    None),
        ("⚙",   "Settings",              "settings",None),
    ]

    def _nav_btn(icon, label, pg, badge):
        is_active = (page == pg)
        if is_active:
            st.markdown(f"""
            <div style="background:#1a6ef7;border-radius:8px;margin:1px 0;padding:9px 14px;
                        display:flex;align-items:center;gap:8px;">
              <span style="font-size:14px;">{icon}</span>
              <span style="font-size:13px;font-weight:600;color:#fff;font-family:'Plus Jakarta Sans',sans-serif;flex:1;">{label}</span>
              {"<span style='font-size:10px;background:rgba(255,255,255,0.2);color:#fff;padding:2px 6px;border-radius:8px;font-weight:600;'>"+badge+"</span>" if badge else ""}
            </div>""", unsafe_allow_html=True)
        else:
            if st.button(f"{icon}  {label}", key=f"nav_{pg}", use_container_width=True):
                go(pg)

    for icon, label, pg, badge in workflow_items:
        _nav_btn(icon, label, pg, badge)

    # Divider before tools
    st.markdown("""<div style="border-top:1px solid rgba(255,255,255,0.08);margin:8px 8px 6px 8px;"></div>
    <div style="font-size:10px;color:rgba(255,255,255,0.3);font-family:'Plus Jakarta Sans',sans-serif;
                padding:0 14px 4px;letter-spacing:0.08em;text-transform:uppercase;">Views</div>""",
    unsafe_allow_html=True)

    for icon, label, pg, badge in tools_items:
        _nav_btn(icon, label, pg, badge)

    # Footer with logout
    st.markdown("""
    <div style="position:fixed;bottom:48px;left:0;width:230px;padding:10px 16px 4px;
                background:#0d1b2a;">
      <div style="font-size:11px;color:rgba(255,255,255,0.3);font-family:'Plus Jakarta Sans',sans-serif;">
        Logged in as <span style="color:rgba(255,255,255,0.55);font-weight:600;">admin</span>
      </div>
    </div>""", unsafe_allow_html=True)
    if st.button("🔒  Sign Out", key="nav_logout", use_container_width=True):
        st.session_state["authenticated"] = False
        st.rerun()


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
        ("🚢","Import Shortage",   "Import part shortage & coverage from PO Qty, ETD, ETA", st.session_state["imp_results"] is not None, "import"),
        ("📋","Production Plan",   "Month-wise model requirement plan with descriptions", True, "plan"),
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

    # NEW: Add template download tip
    st.markdown("""
    <div class="template-info">
    💡 <strong>Tip:</strong> Click the template download buttons below to see the exact file 
    format required. This shows column names and sample data to help you prepare your files correctly.
    </div>
    """, unsafe_allow_html=True)

    def _file_status(key, label):
        """Show green tick if file already in session, grey hint if not."""
        if st.session_state.get(key):
            st.markdown(
                f'''<div style="display:flex;align-items:center;gap:6px;margin:4px 0 6px;
                            padding:6px 10px;background:#f0fdf4;border-radius:6px;
                            border:1px solid #bbf7d0;">
                  <span style="color:#16a34a;font-size:14px;">✓</span>
                  <span style="color:#15803d;font-size:12px;font-weight:600;">{label} loaded — retained in session.
                  Re-upload to replace.</span>
                </div>''', unsafe_allow_html=True)
        else:
            st.markdown(
                '<p style="color:#9ca3af;font-size:11px;margin:2px 0 6px;">Accepted: .XLSX, .XLS</p>',
                unsafe_allow_html=True)

    # Show overall status badges in topbar area
    _bom_ok = bool(st.session_state.get("_bom"))
    _req_ok = bool(st.session_state.get("_req"))
    status_html = ""
    if _bom_ok: status_html += '<span style="background:#dcfce7;color:#15803d;font-size:11px;font-weight:700;padding:3px 10px;border-radius:10px;margin-right:6px;">● BOM done</span>'
    if _req_ok: status_html += '<span style="background:#dcfce7;color:#15803d;font-size:11px;font-weight:700;padding:3px 10px;border-radius:10px;margin-right:6px;">● Req done</span>'
    if status_html:
        st.markdown(f'<div style="margin-bottom:12px;">{status_html}</div>', unsafe_allow_html=True)

    c1, c1b = st.columns([1, 1])
    with c1:
        st.markdown("""<div class="ucard"><div class="ucard-header"><div class="ucard-title-row">
        <div class="ucard-icon purple">📋</div><div><p class="ucard-title">BOM File</p>
        <p class="ucard-desc">Upload your BOM file (.XLSX, .XLS)</p></div></div>
        <span class="badge-req">Required</span></div></div>""", unsafe_allow_html=True)
        bf = st.file_uploader("BOM", type=["xlsx","xls"], key="bom_u", label_visibility="collapsed")
        if bf: st.session_state["_bom"] = bf.read()
        _file_status("_bom", "BOM file")
    
    with c1b:
        st.markdown("<p style='font-size:12px;color:#6b7280;margin-bottom:8px;'><strong>BOM Template</strong></p>", unsafe_allow_html=True)
        template_buf = create_bom_template()
        st.download_button(
            "📥 Download Template",
            data=template_buf.getvalue(),
            file_name="bom_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key="dl_bom"
        )
        st.markdown("<p style='font-size:10px;color:#9ca3af;margin-top:4px;'>Shows exact columns and sample data</p>", unsafe_allow_html=True)

    c2, c2b = st.columns([1, 1])
    with c2:
        st.markdown("""<div class="ucard"><div class="ucard-header"><div class="ucard-title-row">
        <div class="ucard-icon green">📊</div><div><p class="ucard-title">Req. &amp; Stock File</p>
        <p class="ucard-desc">Upload your requirement &amp; stock file</p></div></div>
        <span class="badge-req">Required</span></div></div>""", unsafe_allow_html=True)
        rf = st.file_uploader("Req", type=["xlsx","xls"], key="req_u", label_visibility="collapsed")
        if rf: st.session_state["_req"] = rf.read()
        _file_status("_req", "Req & Stock file")
    
    with c2b:
        st.markdown("<p style='font-size:12px;color:#6b7280;margin-bottom:8px;'><strong>Requirement Template</strong></p>", unsafe_allow_html=True)
        template_buf = create_requirement_template()
        st.download_button(
            "📥 Download Template",
            data=template_buf.getvalue(),
            file_name="requirement_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key="dl_req"
        )
        st.markdown("<p style='font-size:10px;color:#9ca3af;margin-top:4px;'>Shows exact columns and sample data</p>", unsafe_allow_html=True)

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    c3, c3b = st.columns([1, 1])
    with c3:
        st.markdown("""<div class="ucard"><div class="ucard-header"><div class="ucard-title-row">
        <div class="ucard-icon orange">📦</div><div><p class="ucard-title">Production Orders</p>
        <p class="ucard-desc">Upload your production orders file</p></div></div>
        <span class="badge-opt">Optional</span></div></div>""", unsafe_allow_html=True)
        pf = st.file_uploader("Prod", type=["xlsx","xls"], key="prod_u", label_visibility="collapsed")
        if pf: st.session_state["_prod"] = pf.read()
        _file_status("_prod", "Production Orders file")

    with c3b:
        st.markdown("<p style='font-size:12px;color:#6b7280;margin-bottom:8px;'><strong>Consumption Template</strong></p>", unsafe_allow_html=True)
        template_buf = create_consumption_template()
        st.download_button(
            "📥 Download Template",
            data=template_buf.getvalue(),
            file_name="consumption_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key="dl_cons"
        )
        st.markdown("<p style='font-size:10px;color:#9ca3af;margin-top:4px;'>Optional: For consumption analysis</p>", unsafe_allow_html=True)

    c4, c4b = st.columns([1, 1])
    with c4:
        st.markdown("""<div class="ucard"><div class="ucard-header"><div class="ucard-title-row">
        <div class="ucard-icon blue">📥</div><div><p class="ucard-title">Receipt Quantities</p>
        <p class="ucard-desc">Upload your receipt quantities file</p></div></div>
        <span class="badge-opt">Optional</span></div></div>""", unsafe_allow_html=True)
        rrf = st.file_uploader("Receipt", type=["xlsx","xls"], key="receipt_u", label_visibility="collapsed")
        if rrf: st.session_state["_receipt"] = rrf.read()
        _file_status("_receipt", "Receipt Quantities file")

    with c4b:
        st.markdown("<p style='font-size:12px;color:#6b7280;margin-bottom:8px;'><strong>Receipts Template</strong></p>", unsafe_allow_html=True)
        template_buf = create_receipts_template()
        st.download_button(
            "📥 Download Template",
            data=template_buf.getvalue(),
            file_name="receipts_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key="dl_receipt"
        )
        st.markdown("<p style='font-size:10px;color:#9ca3af;margin-top:4px;'>Optional: For purchase order tracking</p>", unsafe_allow_html=True)

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    ready = _bom_ok and _req_ok
    bar_sub = "All required files loaded · Click Run MRP to proceed" if ready else "Upload BOM and Req & Stock files to continue"
    st.markdown(f'''<div class="run-bar">
      <div><div class="run-bar-text">{"Ready to process! ✓" if ready else "Waiting for required files..."}</div>
      <div class="run-bar-sub">{bar_sub}</div></div>
    </div>''', unsafe_allow_html=True)
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    rb, _ = st.columns([1,4])
    with rb:
        if st.button("Run MRP  ▶", type="primary", use_container_width=True, disabled=not ready): go("mrp")


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
                                 help="Sheet 1: Import Part List (Part Code, Desc., Category, Interchange Group) | Sheet 2: Segment (IDU/ODU codes)")
            st.download_button("📥 Segment & Import Part template (with Interchange Group)",data=create_seg_imp_template().getvalue(),
                               file_name="segment_import_part_template.xlsx",key="dl_seg_imp",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        rb,_=st.columns([1,4])
        with rb:
            run_seg=st.button("▶ Run Segment Capacity",type="primary",use_container_width=True,key="run_seg")
        if sf is not None: st.session_state["seg_imp_bytes"]=sf.getvalue()
        elif st.session_state.get("seg_imp_bytes"): st.caption("✓ Segment & Import Part file retained from earlier upload. Re-upload to replace.")
        if run_seg:
            if not st.session_state.get("seg_imp_bytes"): st.warning("Upload Segment & Import Part file first.")
            else:
                try:
                    seg_bytes=st.session_state["seg_imp_bytes"]
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
            rm_map=r.get("rm_map",{}); all_rm=sorted(set(rm_map.values())) if rm_map else []; ag=r.get("active_rm_groups",[])

            # ── RM Group Filter — shown FIRST so it drives the metrics below ──
            if all_rm:
                st.markdown("""
                <style>
                .rm-filter-card {
                    background:#ffffff; border:1px solid #e5e7eb; border-radius:12px;
                    padding:18px 22px 14px; margin-bottom:18px;
                }
                .rm-filter-title {
                    font-size:11px; font-weight:700; color:#6b7280;
                    letter-spacing:0.1em; text-transform:uppercase; margin-bottom:14px;
                    display:flex; align-items:center; gap:8px;
                }
                .rm-filter-title::after {
                    content:""; flex:1; height:1px; background:#e5e7eb;
                }
                .rm-hint {
                    font-size:11px; color:#9ca3af; margin-top:10px;
                }
                /* Tighten checkbox rows inside the filter card */
                .rm-filter-card [data-testid="stCheckbox"] {
                    background:#f9fafb; border:1px solid #e5e7eb; border-radius:8px;
                    padding:6px 10px; margin-bottom:4px;
                }
                .rm-filter-card [data-testid="stCheckbox"]:has(input:checked) {
                    background:#eff6ff; border-color:#bfdbfe;
                }
                </style>
                """, unsafe_allow_html=True)

                st.markdown('<div class="rm-filter-card">', unsafe_allow_html=True)
                st.markdown('<div class="rm-filter-title">RM Group Filter</div>', unsafe_allow_html=True)

                # Quick-action buttons: Select All / Clear All
                qa1, qa2, qa_spacer = st.columns([1, 1, 6])
                with qa1:
                    select_all = st.button("✓ Select All", key="rm_all", use_container_width=True)
                with qa2:
                    clear_all  = st.button("✗ Clear All",  key="rm_none", use_container_width=True)

                if select_all:
                    for grp in all_rm: st.session_state[f"rm_{grp}"] = True
                if clear_all:
                    for grp in all_rm: st.session_state[f"rm_{grp}"] = False

                # Checkboxes in a clean 4-column grid
                sg = []
                cols_per_row = 4
                rm_rows = [all_rm[i:i+cols_per_row] for i in range(0, len(all_rm), cols_per_row)]
                for rm_row in rm_rows:
                    row_cols = st.columns(cols_per_row)
                    for ci, grp in enumerate(rm_row):
                        with row_cols[ci]:
                            checked = st.checkbox(grp, value=st.session_state.get(f"rm_{grp}", grp in ag), key=f"rm_{grp}")
                            if checked: sg.append(grp)
                    # Fill empty cells in last row
                    for ci in range(len(rm_row), cols_per_row):
                        row_cols[ci].empty()

                st.markdown('<div class="rm-hint">💡 Toggle groups to include / exclude their parts as constraints. Click <b>Apply Filter</b> to recalculate capacity.</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

                # Apply button — triggers recalculation which refreshes the metrics below
                ab, _ = st.columns([1.4, 5])
                with ab:
                    if st.button("↻  Apply Filter", key="arm", type="primary", use_container_width=True):
                        sb = st.session_state.get("seg_imp_bytes")
                        if sb:
                            with st.spinner("Recalculating capacity …"):
                                nr = run_segment(mrp_r["bom"], mrp_r["stock"], sb, active_rm=sg)
                                if nr: st.session_state["seg_results"] = nr; st.rerun()

            # ── Overview metrics — reflect the latest (possibly filtered) results ──
            st.markdown("""
            <div style="font-size:11px;font-weight:700;color:#6b7280;letter-spacing:0.1em;
                        text-transform:uppercase;display:flex;align-items:center;gap:8px;margin:4px 0 10px;">
              OVERVIEW
              <span style="flex:1;height:1px;background:#e5e7eb;display:block;"></span>
            </div>""", unsafe_allow_html=True)
            m1,m2,m3,m4=st.columns(4)
            m1.metric("Total FG sets",f"{r['total_sets']:,}")
            m2.metric("FGs producing",f"{sum(1 for f in r['fg_results'] if f['Max_Sets']>0)} / {len(r['fg_results'])}")
            m3.metric("Active segments",f"{(r['alloc_int']>0).sum()} / {len(r['segs'])}")
            m4.metric("Constrained parts",f"{len(r['constrained_parts'])}")

            if r.get("group_members"):
                with st.expander(f"⇄ {len(r['group_members'])} interchangeable part group(s) pooled — same hardware, stock shared across codes"):
                    st.dataframe(pd.DataFrame([{"Group":g,"Codes":len(m),"Pooled stock":int(r["stock"].get(g,0)),"Member codes":", ".join(m)}
                                               for g,m in r["group_members"].items()]),use_container_width=True,hide_index=True)
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

            sec("Month-wise sets vs requirement")
            if fg_res:
                st.session_state["_seg_mw_export"]=None
                bcol,pcol=st.columns([2,2])
                with bcol:
                    basis=st.radio("Opening sets basis",["Max Sets (as above)","Aligned to requirement"],horizontal=True,key="seg_mw_basis",
                                   help="Max Sets: LP maximum total sets (may give sets to FGs with no demand). "
                                        "Aligned: LP re-run with each FG capped at its total requirement, so material goes to FGs that have demand.")
                with pcol:
                    pof=st.file_uploader("Import PO file for Arrival Weeks (optional — same file as Import Shortage page)",
                                         type=["xlsx","xls"],key="seg_po_u")
                    if pof: st.session_state["_imp_po"]=pof.read()
                    if st.session_state.get("_imp_po") and not pof: st.caption("✓ Using Import PO file already in session.")
                    st.download_button("📥 Import PO template (week-wise ETA / ETD)",data=create_import_po_template().getvalue(),
                                       file_name="import_po_weekly_template.xlsx",key="dl_seg_po",
                                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                    smf=st.file_uploader("Supplier Master — part-wise supplier (optional)",type=["xlsx","xls"],key="seg_sup_u",
                                         help="Columns: Part Code, Supplier (Description optional). Fills the Supplier column in Model + components.")
                    if smf: st.session_state["_sup_master"]=smf.getvalue()
                    elif st.session_state.get("_sup_master"): st.caption("✓ Using Supplier Master already in session.")
                    st.download_button("📥 Supplier Master template",data=create_supplier_master_template().getvalue(),
                                       file_name="supplier_master_template.xlsx",key="dl_seg_sup",
                                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                po_df=None
                if st.session_state.get("_imp_po"):
                    po_df,po_err=load_import_po(st.session_state["_imp_po"],st.session_state.get("imp_transit",30))
                    if po_err: st.warning(f"Import PO file: {po_err}"); po_df=None
                _bs="req" if basis.startswith("Aligned") else "max"
                mw,mw_months=segment_monthwise(r,mrp_r,_bs,None)          # sets: stock only (no PO arrivals)
                mw_arr,_=segment_monthwise(r,mrp_r,_bs,po_df)             # component view: with weekly PO arrivals
                if mw.empty or not mw_months:
                    st.info("No month-wise requirement found in the MRP Requirement sheet.")
                else:
                    t_req=mw["Requirement"].sum(); t_sf=mw["Net Shortfall"].sum()
                    t_open=mw[mw["Month"]==mw_months[0]]["Sets Available"].sum()
                    q1,q2,q3,q4,q5=st.columns(5)
                    q1.metric(f"Sets available ({mw_months[0]})",f"{t_open:,.0f}")
                    q2.metric("Extra sets possible from PO arrivals",f"{mw_arr['Arrival Sets'].sum():,.0f}")
                    q3.metric("Total requirement",f"{t_req:,.0f}")
                    q4.metric("Total net shortfall",f"{t_sf:,.0f}")
                    q5.metric("FGs with shortfall",f"{mw[mw['Net Shortfall']>0]['FG Code'].nunique()} / {mw['FG Code'].nunique()}")
                    nmc=(mw.drop_duplicates("FG Code")["Req matched on"]=="Not in Req").sum()
                    if nmc: st.caption(f"⚠ {nmc} FG code(s) not found in the Requirement sheet (by FG or IDU code) — treated as zero requirement.")
                    if po_df is None: st.caption("ℹ Upload the Import PO file to fill the Arrival Week columns in Model + components.")
                    st.caption("Segment-wise / Model-wise (sets): from stock only · Available = balance carried from previous month · "
                               "Balance = Available − Req (min 0) · Shortfall = Req − Available (min 0). "
                               "PO arrivals by week (ETA day 1-7 WK01, 8-14 WK02, 15-21 WK03, 22+ WK04) are shown per component in Model + components.")

                    seg_keys={"Segment":"Segment"}
                    fg_keys=MODEL_KEYS
                    cs_keys={"Component":"Component","Codes":"Codes","Used in BOM headers":"Used in BOM headers","FG codes":"FG codes"}
                    seg_g=monthwise_grouped(mw,["Segment"],mw_months)
                    fgo_keys={"Segment":"Segment","Alt BOM":"Alt BOM","FG Description":"Model","FG Code":"FG Code"}
                    fgo_g=monthwise_grouped(mw,list(fgo_keys),mw_months)
                    fgo_g=pd.concat([fgo_g.iloc[:-1].sort_values(("","Segment"),kind="stable"),fgo_g.iloc[-1:]],ignore_index=True)
                    _bom=mrp_r["bom"]
                    desc_map=dict(zip(_bom["Component"].astype(str),_bom["Component descriptio"].astype(str).replace("nan",""))) \
                             if "Component descriptio" in _bom.columns else {}
                    sup_map={}
                    if po_df is not None and "Supplier" in po_df.columns:     # fallback: supplier on the PO lines
                        _p=align_part_codes(po_df,_mrp_known_codes(mrp_r)); _p=_p[_p["Supplier"].astype(str).str.strip()!=""]
                        sup_map={k:", ".join(dict.fromkeys(g["Supplier"].astype(str).str.strip())) for k,g in _p.groupby("Part")}
                    if st.session_state.get("_sup_master"):                      # Supplier Master wins
                        _sm,_se=load_supplier_master(st.session_state["_sup_master"],_mrp_known_codes(mrp_r))
                        if _se: st.warning(_se)
                        sup_map.update(_sm)
                    cmw=component_monthwise(r,mw_arr,mw_months,desc_map,sup_map)
                    mdl=model_with_components(mw_arr,cmw)
                    fg_g=monthwise_grouped(mdl,list(fg_keys),mw_months,keep_order=True,total=False)
                    cs_long,cs_info=component_shortage(cmw,mw_months,mw_arr.attrs.get("ctx",{}).get("arr",{}),r)
                    cs_g=monthwise_grouped(cs_long,list(cs_keys),mw_months,keep_order=True,total=False) if not cs_long.empty else pd.DataFrame()
                    _xb=io.BytesIO()
                    with pd.ExcelWriter(_xb,engine="openpyxl") as _w:
                        grouped_to_excel(_w,seg_g,"Segment-wise",seg_keys,weeks=False)
                        grouped_to_excel(_w,fgo_g,"Model-wise (sets)",fgo_keys,weeks=False)
                        if not fg_g.empty: grouped_to_excel(_w,fg_g,"Model + components",fg_keys)
                        if "Sheet" in _w.book.sheetnames and len(_w.book.sheetnames)>1: del _w.book["Sheet"]
                    _xb.seek(0)
                    st.download_button("⬇ Download month-wise tables (.xlsx)",data=_xb,file_name="segment_monthwise.xlsx",
                                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                       type="primary",key="dl_seg_mw")
                    sw1,sw5,sw2,sw4,sw3=st.tabs(["Segment-wise (sets)","Model-wise (sets)","Model + components (drill-down)",
                                                 "Component shortage & arrivals","Single FG / segment view"])
                    with sw1:
                        show_grouped_table(seg_g,seg_keys,freeze=("Segment",),weeks=False)
                    with sw5:
                        only_fgo=st.checkbox("Show only models with shortfall",key="seg_fgo_sf")
                        fgv=fgo_g
                        if only_fgo:
                            sfc=[c for c in fgo_g.columns if c[1]=="Shortfall"]
                            body=fgo_g.iloc[:-1]; fgv=pd.concat([body[body[sfc].sum(axis=1)>0],fgo_g.iloc[-1:]],ignore_index=True)
                        show_grouped_table(fgv,fgo_keys,freeze=("FG Code",),weeks=False)
                    with sw2:
                        st.caption("Each import component per BOM header (IDU / ODU) in pieces (complete sets per FG are in the Model-wise (sets) tab): "
                                   "Req = FG req × Qty/set; stock and PO arrivals of a component "
                                   "(or its ⇄ interchange group) are shared by all FGs using it, in table order.")
                        o1,o2=st.columns(2)
                        with o1: only_fg=st.checkbox("Only FGs with a set shortfall",key="seg_mw_sf")
                        with o2: comp_mode=st.radio("Component rows",["All","Short only"],horizontal=True,key="seg_mw_comp")
                        fv=fg_g
                        sfc=[c for c in fg_g.columns if c[1]=="Shortfall"]
                        keep=pd.Series(comp_mode=="All",index=fv.index) | (fv[sfc].sum(axis=1)>0)
                        if only_fg:
                            short_fg=set(mw[mw["Net Shortfall"]>0]["FG Code"])
                            keep=keep & fv[("","FG Code")].isin(short_fg)
                        if not keep.any(): st.success("No component rows to show with these filters.")
                        else: show_grouped_table(fv[keep],fg_keys,freeze=("FG Code","Component"))
                    with sw4:
                        if cs_g.empty: st.info("No import components found for these FGs.")
                        else:
                            st.caption("All FGs together, in pieces · Arrival Week = PO qty landing that week · sorted by total shortfall")
                            st.dataframe(cs_info.style.apply(lambda c:["color:#dc2626;font-weight:600" if v>0 else "" for v in c],subset=["Total shortfall"])
                                         .format({"Total shortfall":"{:,.0f}"}),use_container_width=True,hide_index=True)
                            only_cs=st.checkbox("Only components with shortfall",value=True,key="seg_cs_sf")
                            cv=cs_g
                            if only_cs:
                                sfc2=[c for c in cs_g.columns if c[1]=="Shortfall"]; cv=cs_g[cs_g[sfc2].sum(axis=1)>0]
                            if cv.empty: st.success("No import component is short in the horizon.")
                            else: show_grouped_table(cv,cs_keys,freeze=("Component",))
                    with sw3:
                        v1,v2=st.columns(2)
                        with v1: vseg=st.selectbox("Segment",["All"]+sorted(mw["Segment"].unique()),key="seg_mw_seg")
                        sub=mw if vseg=="All" else mw[mw["Segment"]==vseg]
                        with v2: vfg=st.selectbox("FG code",["All"]+sorted(sub["FG Code"].unique()),key="seg_mw_fg")
                        if vfg!="All": sub=sub[sub["FG Code"]==vfg]
                        cc=["Sets Available","Requirement","Balance c/f","Net Shortfall"]
                        one=sub.groupby("Month",as_index=False,sort=False)[cc].sum()
                        st.dataframe(one.style.apply(lambda c:["color:#dc2626;font-weight:600" if v>0 else "" for v in c],subset=["Net Shortfall"])
                                     .format({c:"{:,.0f}" for c in cc}),use_container_width=True,hide_index=True)
                        st.line_chart(one.set_index("Month")[["Sets Available","Requirement"]],use_container_width=True,height=240)
                    st.session_state["_seg_mw_export"]=(seg_g,fg_g,mw,seg_keys,fg_keys,cs_g,cs_keys,cs_info,fgo_g,fgo_keys)

            sec("FG detail — import part breakdown")
            opts=sorted([f["FG_Code"] for f in fg_res],key=lambda fg:-next(f["Max_Sets"] for f in fg_res if f["FG_Code"]==fg))
            sfg=st.selectbox("Select FG code",options=opts,key="sfg")
            if sfg:
                fgr=next(f for f in fg_res if f["FG_Code"]==sfg); sets=fgr["Max_Sets"]
                st.markdown(f"**{sfg}** — {fgr.get('FG_Desc','')} · Segment: `{fgr['Segment']}` · IDU: `{fgr['IDU']}` · ODU: `{fgr['Compatible_ODU']}` · **Max sets: {sets:,}**")
                irows=[]
                for p,req in sorted(fgr["combined_req"].items(),key=lambda x:-x[1]):
                    avail=float(r["stock"].get(p,0)); ms=int(avail/req) if req>0 else 0
                    irows.append({"Import Part":p,"Interchangeable codes":", ".join(r.get("group_members",{}).get(p,[])),"RM Group":rm_map.get(p,"—"),"Qty per set":round(req,4),"Stock available":int(avail),"Max sets (alone)":ms,"Binding?":"🔴 YES" if ms==sets and sets>0 else ""})
                idf=pd.DataFrame(irows)
                if not idf.empty and not idf["Interchangeable codes"].astype(bool).any(): idf=idf.drop(columns="Interchangeable codes")
                def hi(row): return ["background-color:#fff0f0"]*len(row) if row["Binding?"]=="🔴 YES" else [""]*len(row)
                st.dataframe(idf.style.apply(hi,axis=1).format({"Qty per set":"{:.4f}","Stock available":"{:,}","Max sets (alone)":"{:,}"}),use_container_width=True,hide_index=True)

            sec("Import part stock utilisation")
            purows=[]
            for p in r["import_parts"]:
                pu=r["part_usage"].get(p,{})
                purows.append({"Import Part":p,"Interchangeable codes":", ".join(r.get("group_members",{}).get(p,[])),"RM Group":rm_map.get(p,"—"),"Stock":int(r["stock"].get(p,0)),"Used":int(pu.get("used",0)),"Remaining":int(pu.get("remain",r["stock"].get(p,0))),"Utilisation%":pu.get("pct",0)})
            pudf=pd.DataFrame(purows).sort_values("Utilisation%",ascending=False)
            if not pudf.empty and not pudf["Interchangeable codes"].astype(bool).any(): pudf=pudf.drop(columns="Interchangeable codes")
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
                _mwx=st.session_state.get("_seg_mw_export")
                if fg_res and _mwx:
                    grouped_to_excel(w,_mwx[0],"Monthwise Segment",_mwx[3],weeks=False)
                    grouped_to_excel(w,_mwx[8],"Monthwise Model (sets)",_mwx[9],weeks=False)
                    if not _mwx[1].empty: grouped_to_excel(w,_mwx[1],"Monthwise Model+Comp",_mwx[4])
                    if not _mwx[5].empty:
                        _mwx[7].to_excel(w,sheet_name="Component Shortage",index=False)
                        grouped_to_excel(w,_mwx[5],"Component Monthwise",_mwx[6])
                    _mwx[2].to_excel(w,sheet_name="Monthwise Detail",index=False)
            buf.seek(0)
            st.download_button("⬇ Download Segment Capacity (.xlsx)",data=buf,file_name="segment_capacity.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",use_container_width=True,type="primary")


# ═══════════════════════════════════════════════════════════════
# PAGE: AGING PROJECTION
# ═══════════════════════════════════════════════════════════════
elif st.session_state["page"] == "aging":
    topbar("Aging Opening Inventory Forecast", "Month-wise aging opening stock — BOM consumption + receipt adjusted")

    sec("Input Files")

    # ── BOM and Req auto-carry from MRP session — no re-upload needed ──
    _bom_ready = bool(st.session_state.get("_bom"))
    _req_ready = bool(st.session_state.get("_req"))

    fc1, fc2 = st.columns(2)
    with fc1:
        af = st.file_uploader("Aging Material Details (.xlsx) *Required*",
                              type=["xlsx","xls"], key="ag_f")
        if af:
            st.session_state["_aging"] = af.read()

    with fc2:
        rec_ag_f = st.file_uploader("Receipt File (.xlsx) — Optional",
                                    type=["xlsx","xls"], key="ag_rec_f")
        if rec_ag_f:
            st.session_state["_ag_rec"] = rec_ag_f.read()

    # Show BOM / Req status — auto-used from MRP session, override only if needed
    fc3, fc4 = st.columns(2)
    with fc3:
        if _bom_ready:
            st.success("✓ BOM file — carried from MRP session (no re-upload needed)")
            bom_override = st.file_uploader("Upload different BOM (optional override)",
                                            type=["xlsx","xls"], key="ag_bom_f")
            if bom_override:
                st.session_state["_ag_bom"] = bom_override.read()
                st.caption("Using overridden BOM for aging")
        else:
            bom_ag_f = st.file_uploader("BOM File (.xlsx) *Required*",
                                        type=["xlsx","xls"], key="ag_bom_f")
            if bom_ag_f:
                st.session_state["_ag_bom"] = bom_ag_f.read()

    with fc4:
        if _req_ready:
            st.success("✓ Requirement file — carried from MRP session (no re-upload needed)")
            req_override = st.file_uploader("Upload different Requirement (optional override)",
                                            type=["xlsx","xls"], key="ag_req_f")
            if req_override:
                st.session_state["_ag_req"] = req_override.read()
                st.caption("Using overridden Requirement for aging")
        else:
            req_ag_f = st.file_uploader("Requirement File (.xlsx) *Required*",
                                        type=["xlsx","xls"], key="ag_req_f")
            if req_ag_f:
                st.session_state["_ag_req"] = req_ag_f.read()

    fc5, _ = st.columns([1, 3])
    with fc5:
        st.markdown("**Aging snapshot date**")
        st.caption("Date the aging file was extracted from SAP (e.g. May-01 for May opening)")
        abd = st.date_input("Snapshot date", value=pd.Timestamp("2026-05-01"),
                            key="ag_dt", label_visibility="collapsed")

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
        # Ensure month columns are numeric before styling
        for _mc in mo:
            piv[_mc] = pd.to_numeric(piv[_mc], errors="coerce").fillna(0)
        arows = piv[piv[mo].max(axis=1) > 0].sort_values(lm, ascending=False).reset_index(drop=True)
        st.caption(f"{len(arows):,} materials with aging value")

        # Manual heat-map colouring (no matplotlib needed)
        def _heatmap_row(row):
            styles = []
            for col in row.index:
                if col not in mo:
                    styles.append("")
                    continue
                v = row[col]
                if v <= 0:
                    styles.append("")
                else:
                    # Red intensity scaled 0-100 within each row's max
                    row_max = max(row[mo].max(), 1)
                    pct = min(v / row_max, 1.0)
                    # YlOrRd approximation: low=yellow, high=red
                    r = int(255)
                    g = int(255 * (1 - pct * 0.85))
                    b = int(max(0, 180 * (1 - pct * 2)))
                    styles.append(f"background-color:rgb({r},{g},{b});color:{'#111' if pct < 0.6 else '#fff'}")
            return styles

        styled = (arows.style
                  .format({m: "Rs {:,.0f}" for m in mo})
                  .apply(_heatmap_row, axis=1))
        st.dataframe(styled, use_container_width=True, hide_index=True)

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
# PAGE: PRODUCTION PLAN
# ═══════════════════════════════════════════════════════════════
elif st.session_state["page"] == "plan":
    topbar("Production Plan", "Model-wise month-by-month requirement plan")

    req_bytes = st.session_state.get("_req")
    bom_bytes = st.session_state.get("_bom")

    if not req_bytes:
        st.markdown("""<div class="empty"><div class="empty-icon">📋</div>
        <div class="empty-ttl">No requirement data</div>
        <div class="empty-sub">Upload the Requirement & Stock file on the Upload Files page first.</div></div>""",
        unsafe_allow_html=True)
    else:
        # ── Load & parse requirement sheet ────────────────────
        import io as _io
        raw = pd.read_excel(_io.BytesIO(req_bytes), sheet_name=resolve_sheet(req_bytes, "Requirement"), header=None)
        raw.columns = [str(c).strip() for c in raw.iloc[0].tolist()]
        raw = raw.iloc[1:].reset_index(drop=True)

        # Parse month columns
        month_cols = []
        month_labels = {}
        for col in raw.columns:
            try:
                ts = pd.Timestamp(col)
                if pd.notna(ts) and ts.year > 2000:
                    lbl = ts.strftime("%b-%y")
                    month_cols.append(col)
                    month_labels[col] = lbl
            except Exception:
                pass

        # Rename month columns to labels
        raw = raw.rename(columns=month_labels)
        months_lbl = list(month_labels.values())

        # Clean up
        raw["BOM Header"] = raw["BOM Header"].astype(str).str.strip()
        alt_col = "Alt." if "Alt." in raw.columns else "Alt"
        raw[alt_col] = raw[alt_col].astype(str).str.strip()
        for m in months_lbl:
            raw[m] = pd.to_numeric(raw[m], errors="coerce").fillna(0)

        # ── Get model descriptions from BOM ───────────────────
        if bom_bytes:
            bom_df = pd.read_excel(_io.BytesIO(bom_bytes))
            bom_df.columns = bom_df.columns.str.strip()
            desc_col = next((c for c in bom_df.columns if "header desc" in c.lower()), None)
            if desc_col:
                model_desc = (bom_df[["BOM Header", desc_col]]
                              .drop_duplicates("BOM Header")
                              .rename(columns={desc_col: "Model Description"}))
                model_desc["BOM Header"] = model_desc["BOM Header"].astype(str).str.strip()
                raw = raw.merge(model_desc, on="BOM Header", how="left")
            else:
                raw["Model Description"] = ""
        else:
            raw["Model Description"] = ""

        raw["Model Description"] = raw["Model Description"].fillna("")

        # ── Filters ────────────────────────────────────────────
        sec("Filters")
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            all_models = sorted(raw["BOM Header"].unique().tolist())
            sel_models = st.multiselect("Filter by Model", all_models,
                                        placeholder="All models", key="plan_models")
        with fc2:
            all_alts = sorted(raw[alt_col].unique().tolist())
            sel_alts = st.multiselect("Filter by Alt BOM", all_alts,
                                      placeholder="All alts", key="plan_alts")
        with fc3:
            search_desc = st.text_input("Search description", placeholder="e.g. HSI18", key="plan_search")

        # Apply filters
        plan_df = raw.copy()
        if sel_models:
            plan_df = plan_df[plan_df["BOM Header"].isin(sel_models)]
        if sel_alts:
            plan_df = plan_df[plan_df[alt_col].isin(sel_alts)]
        if search_desc:
            plan_df = plan_df[plan_df["Model Description"].str.contains(search_desc, case=False, na=False)]

        # ── Summary metrics ────────────────────────────────────
        sec("Plan Summary")
        mc = st.columns(len(months_lbl) + 1)
        mc[0].metric("Total Models", f"{len(plan_df):,}")
        for i, m in enumerate(months_lbl):
            mc[i+1].metric(m, f"{int(plan_df[m].sum()):,}")

        # ── Main plan table ────────────────────────────────────
        sec("Month-wise Requirement Plan")

        disp_cols = ["BOM Header", "Model Description", alt_col] + months_lbl + ["Total"]
        plan_df["Total"] = plan_df[months_lbl].sum(axis=1)
        plan_df = plan_df.sort_values("Total", ascending=False).reset_index(drop=True)

        # Show only rows with any demand
        show_zero = st.checkbox("Include models with zero demand", value=False, key="plan_zero")
        if not show_zero:
            plan_df = plan_df[plan_df["Total"] > 0]

        st.caption(f"{len(plan_df):,} models shown")

        # Style: highlight high-demand rows
        def _plan_row_style(row):
            total = row.get("Total", 0)
            if total > 5000:  return ["background-color:#fff0f0"] * len(row)
            if total > 1000:  return ["background-color:#fffbeb"] * len(row)
            if total > 0:     return ["background-color:#f0fdf4"] * len(row)
            return [""] * len(row)

        fmt = {m: "{:,.0f}" for m in months_lbl}
        fmt["Total"] = "{:,.0f}"

        avail_cols = [c for c in disp_cols if c in plan_df.columns]
        st.dataframe(
            plan_df[avail_cols].style
                .apply(_plan_row_style, axis=1)
                .format({k: v for k, v in fmt.items() if k in avail_cols}),
            use_container_width=True, hide_index=True, height=520)

        # ── Month-wise bar chart (total across all models) ─────
        sec("Total Requirement by Month")
        month_totals = {m: int(plan_df[m].sum()) for m in months_lbl}
        chart_data = pd.DataFrame({
            "Month": list(month_totals.keys()),
            "Requirement": list(month_totals.values())
        })
        st.bar_chart(chart_data.set_index("Month"), use_container_width=True, height=280)

        # ── Download ───────────────────────────────────────────
        buf = _io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as w:
            plan_df[avail_cols].to_excel(w, sheet_name="Production Plan", index=False)
            # Also a pivot: month as columns, model as rows
            plan_df[avail_cols].to_excel(w, sheet_name="Plan (All Models)", index=False)
        buf.seek(0)
        st.download_button(
            "⬇ Download Production Plan (.xlsx)", data=buf,
            file_name="production_plan.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True, type="primary")


# ═══════════════════════════════════════════════════════════════
# PAGE: IMPORT SHORTAGE & COVERAGE
# ═══════════════════════════════════════════════════════════════
elif st.session_state["page"] == "import":
    topbar("Import Material Shortage & Coverage", "Stock + open import POs (by ETA) vs MRP requirement, month-wise")

    mrp_r=st.session_state.get("mrp_results")
    if mrp_r is None:
        st.markdown("""<div class="empty"><div class="empty-icon">🚢</div>
        <div class="empty-ttl">Run MRP first</div>
        <div class="empty-sub">Import coverage uses the month-wise requirement and stock from the MRP run.</div></div>""",
        unsafe_allow_html=True)
    else:
        sec("Import PO File")
        u1,u2,u3=st.columns([2,1,1])
        with u1:
            pf=st.file_uploader("Import parts with PO Qty, ETD, ETA (.xlsx)",type=["xlsx","xls"],key="imp_po_u",
                                help="One row per PO line. Columns: Import Part, Description (opt), PO No (opt), Supplier (opt), PO Qty, ETD, ETA")
            if pf: st.session_state["_imp_po"]=pf.read()
            if st.session_state.get("_imp_po") and not pf:
                st.caption("✓ Import PO file retained in session. Re-upload to replace.")
        with u2:
            transit=st.number_input("Transit days (if ETA blank)",min_value=0,max_value=180,value=30,step=1,key="imp_transit",
                                    help="When ETA is empty, ETA = ETD + these days")
        with u3:
            st.markdown("<p style='font-size:12px;color:#6b7280;margin-bottom:8px;'><strong>Import PO Template</strong></p>",unsafe_allow_html=True)
            st.download_button("📥 Download Template",data=create_import_po_template().getvalue(),
                               file_name="import_po_template.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                               use_container_width=True,key="dl_imp_po")
        use_ig=st.checkbox("⇄ Pool interchangeable parts (same hardware, only EPROM / firmware differs)",value=True,key="imp_use_ig",
                           help="Groups come from the 'Interchange Group' column of the Segment & Import Part file (Segment page) "
                                "and/or an 'Interchange Group' column in this PO file. Stock, POs and requirement are summed per group.")
        rb,_=st.columns([1,4])
        with rb:
            run_imp=st.button("▶ Calculate Coverage",type="primary",use_container_width=True,key="run_imp")
        if run_imp:
            if not st.session_state.get("_imp_po"): st.warning("Upload the Import PO file first.")
            else:
                try:
                    po_df,err=load_import_po(st.session_state["_imp_po"],transit)
                    if err: st.error(err)
                    else:
                        gmap=load_interchange_map(st.session_state.get("seg_imp_bytes")) if use_ig else {}
                        if use_ig:
                            gmap.update({p:"⇄ "+g for p,g in zip(po_df["Part"],po_df["IGroup"]) if g})
                        res,err=run_import_coverage(mrp_r,po_df,gmap or None)
                        if err: st.error(err)
                        else: st.session_state["imp_results"]=res; st.success("Import coverage calculated.")
                except Exception as e: st.exception(e)

        r=st.session_state.get("imp_results")
        if r is None:
            st.markdown("""<div class="empty"><div class="empty-icon">🚢</div>
            <div class="empty-ttl">No coverage calculated yet</div>
            <div class="empty-sub">Upload the import part / PO file (PO Qty, ETD, ETA) and click Calculate Coverage.</div></div>""",
            unsafe_allow_html=True)
        else:
            summ=r["summary"]; months=r["months"]
            short=summ[summ["Max Shortage"]>0]
            sec("Summary")
            k1,k2,k3,k4,k5=st.columns(5)
            k1.metric("Import parts",f"{len(summ):,}")
            k2.metric("Parts short",f"{len(short):,}")
            k3.metric("Need new PO",f"{(summ['Status'].str.contains('new PO')).sum():,}")
            k4.metric("Need expedite",f"{(summ['Status'].str.contains('expedite|beyond')).sum():,}")
            k5.metric("Fully covered",f"{(summ['Status'].str.contains('Covered')).sum():,}")
            if r["past_due"]: st.warning(f"{r['past_due']} PO line(s) have ETA before the first MRP month — counted as arriving in {months[0]}.")
            if r["unscheduled"]: st.warning(f"{r['unscheduled']} PO line(s) have no ETA/ETD — excluded from the projection.")
            if r["not_in_mrp"]: st.info(f"{len(r['not_in_mrp'])} part(s) not found in MRP requirement or stock: {', '.join(r['not_in_mrp'][:20])}{' …' if len(r['not_in_mrp'])>20 else ''}")

            def _status_style(row):
                s=str(row.get("Status",row.get("PO Status","")))
                bg="#fef2f2" if "🔴" in s else "#fff7ed" if ("🟠" in s or "⏰" in s) else "#f0fdf4" if ("🟢" in s or "✅" in s) else ""
                return [f"background-color:{bg}" if bg else ""]*len(row)
            num_fmt={c:"{:,.0f}" for c in ["Stock","Total Requirement","Open PO Qty","PO in horizon","Closing Balance",
                                          "Max Shortage","Additional PO Needed","PO Qty"]}

            t1,t2,t3,t4=st.tabs(["🔴 Shortage list","📋 Coverage list","📅 Month-wise balance","🚢 PO status"])
            with t1:
                if short.empty: st.success("No import part goes short within the MRP horizon. 🎉")
                else:
                    cols=["Import Part","Description","Interchangeable codes","Stock","Total Requirement","Open PO Qty","First Shortage Month",
                          "Max Shortage","Additional PO Needed","Next ETA","Status"]
                    cols=[c for c in cols if c!="Interchangeable codes" or short[c].astype(bool).any()]
                    sdf=short.sort_values(["First Shortage Month","Max Shortage"],
                                          key=lambda s:s.map({m:i for i,m in enumerate(months)}) if s.name=="First Shortage Month" else -s)[cols]
                    st.dataframe(sdf.style.apply(_status_style,axis=1).format({k:v for k,v in num_fmt.items() if k in cols}),
                                 use_container_width=True,hide_index=True)
            with t2:
                sf_opt=st.multiselect("Filter status",sorted(summ["Status"].unique()),key="imp_st_f")
                q=st.text_input("Search part",key="imp_q",placeholder="Part code or description").strip().lower()
                cdf=summ.copy()
                if sf_opt: cdf=cdf[cdf["Status"].isin(sf_opt)]
                if q: cdf=cdf[cdf["Import Part"].str.lower().str.contains(q,regex=False)|cdf["Description"].str.lower().str.contains(q,regex=False)]
                cols=["Import Part","Description","Interchangeable codes","Stock","Total Requirement","Open PO Qty","PO in horizon","Closing Balance",
                      "Coverage w/o PO (months)","Coverage (months)","Covered till","First Shortage Month","Next ETA","Status"]
                cols=[c for c in cols if c!="Interchangeable codes" or cdf[c].astype(bool).any()]
                st.dataframe(cdf[cols].style.apply(_status_style,axis=1).format({k:v for k,v in num_fmt.items() if k in cols}),
                             use_container_width=True,hide_index=True)
                st.caption(f"Coverage (months) counts consecutive MRP months from {months[0]} with no shortage, using stock + PO arrivals by ETA.")
            with t3:
                cl=r["closing"]
                if not cl.empty:
                    def _neg_red(v):
                        return "color:#dc2626;font-weight:600;background-color:#fef2f2" if isinstance(v,(int,float)) and v<0 else ""
                    mc=[m for m in months if m in cl.columns]
                    st.dataframe(cl.style.apply(lambda c:[_neg_red(v) for v in c],subset=mc).format({m:"{:,.0f}" for m in mc}),
                                 use_container_width=True,hide_index=True)
                    st.caption("Closing balance per month = Stock + cumulative PO arrivals − cumulative requirement · negative = shortage")
                sec("Part drill-down")
                sel=st.selectbox("Import part",summ["Import Part"].tolist(),key="imp_sel")
                if sel:
                    pj=r["projection"]; pj=pj[pj["Import Part"]==sel][["Month","Opening","PO Arrival","Requirement","Closing","Shortage"]]
                    st.dataframe(pj.style.apply(lambda c:[_neg_red(v) for v in c],subset=["Closing"]).format({c:"{:,.0f}" for c in ["Opening","PO Arrival","Requirement","Closing","Shortage"]}),
                                 use_container_width=True,hide_index=True)
                    st.bar_chart(pj.set_index("Month")[["Closing"]],use_container_width=True,height=240)
                    pos=r["po_status"]; pos=pos[pos["Import Part"]==sel]
                    if not pos.empty: st.dataframe(pos.drop(columns=["Import Part","Description"]),use_container_width=True,hide_index=True)
            with t4:
                pos=r["po_status"]
                only_late=st.checkbox("Show only late POs",key="imp_late")
                if only_late: pos=pos[pos["PO Status"].str.contains("Late")]
                st.dataframe(pos.rename(columns={"PO Status":"Status"}).style.apply(_status_style,axis=1)
                             .format({"PO Qty":"{:,.0f}"}),use_container_width=True,hide_index=True)
                st.caption("Needed by = first month the part goes short using stock + earlier-ETA POs only. Late = PO lands after that month.")

            buf=io.BytesIO()
            with pd.ExcelWriter(buf,engine="openpyxl") as w:
                summ[summ["Max Shortage"]>0].to_excel(w,sheet_name="Shortage List",index=False)
                summ.to_excel(w,sheet_name="Coverage List",index=False)
                r["closing"].to_excel(w,sheet_name="Month-wise Balance",index=False)
                r["projection"].to_excel(w,sheet_name="Projection Detail",index=False)
                r["po_status"].to_excel(w,sheet_name="PO Status",index=False)
            buf.seek(0)
            st.download_button("⬇ Download import_coverage.xlsx",data=buf,file_name="import_coverage.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                               use_container_width=True,type="primary")


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
    sec("Saved uploads (kept on the server between sessions)")
    _si=saved_uploads_info()
    if _si: st.dataframe(pd.DataFrame(_si),use_container_width=True,hide_index=True)
    else: st.caption("No saved uploads yet.")
    st.caption("Uploaded files are saved next to the app and reloaded automatically after a refresh, restart or new deploy. "
               "'Clear all session data' below also deletes these saved copies.")
    if st.button("🗑 Clear all session data",key="clr"):
        for k in ["mrp_results","seg_results","aging_results","seg_imp_bytes",
                  "_bom","_req","_prod","_receipt","_aging","_ag_bom","_ag_req","_ag_rec",
                  "_imp_po","imp_results","_sup_master"]:
            st.session_state[k]=None
        sync_saved_uploads()
        st.success("Session cleared."); st.rerun()


# Keep uploads on disk (runs at the end of every page render)
sync_saved_uploads()
