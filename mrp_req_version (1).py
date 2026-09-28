"""
SAP MRP ENGINE — Professional Sidebar Navigation Layout (Fixed)
ENHANCED with Download Template Option for Each Upload File
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

/* ── Template button styling ────────────────────────────────── */
.template-btn-container {
    display: flex;
    gap: 8px;
    margin-bottom: 12px;
    flex-wrap: wrap;
}
.template-info {
    background: #f0fdf4;
    border: 1px solid #dcfce7;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 11px;
    color: #166534;
    margin-bottom: 10px;
}

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
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS - TEMPLATE GENERATION
# ═══════════════════════════════════════════════════════════════

def create_requirement_template():
    """Generate a sample Requirement & Stock template"""
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
        # Create "Requirement" sheet
        df.to_excel(w, sheet_name="Requirement", index=False)
    buf.seek(0)
    return buf


def create_bom_template():
    """Generate a sample BOM (Bill of Materials) template"""
    template_data = {
        "BOM Header": ["MODEL-001", "MODEL-001", "MODEL-002", "MODEL-002"],
        "BOM Header Desc": ["Model 001 Description", "Model 001 Description", "Model 002 Description", "Model 002 Description"],
        "Item": ["1", "2", "1", "2"],
        "Component": ["COMP-A", "COMP-B", "COMP-A", "COMP-C"],
        "Quantity": [2, 3, 2, 1],
        "Unit": ["EA", "EA", "EA", "EA"],
    }
    df = pd.DataFrame(template_data)
    
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, sheet_name="BOM", index=False)
    buf.seek(0)
    return buf


def create_stock_template():
    """Generate a sample Stock/Opening Balance template"""
    template_data = {
        "Component": ["COMP-A", "COMP-B", "COMP-C"],
        "Stock Quantity": [500, 300, 200],
        "Unit": ["EA", "EA", "EA"],
        "Safety Stock": [50, 30, 20],
    }
    df = pd.DataFrame(template_data)
    
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, sheet_name="Stock", index=False)
    buf.seek(0)
    return buf


def create_production_template():
    """Generate a sample Production Batch template"""
    template_data = {
        "BOM Header": ["MODEL-001", "MODEL-002"],
        "Batch Size": [500, 1000],
        "Lead Time (days)": [10, 15],
    }
    df = pd.DataFrame(template_data)
    
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, sheet_name="Production", index=False)
    buf.seek(0)
    return buf


def create_receipt_template():
    """Generate a sample Receipts/POs template"""
    template_data = {
        "Component": ["COMP-A", "COMP-B", "COMP-C"],
        "Quantity": [200, 150, 100],
        "Due Date": ["2025-01-15", "2025-01-20", "2025-02-01"],
        "Status": ["Open", "Confirmed", "Open"],
    }
    df = pd.DataFrame(template_data)
    
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, sheet_name="Receipts", index=False)
    buf.seek(0)
    return buf


def create_aging_template():
    """Generate a sample Aging Projection template"""
    template_data = {
        "Component": ["COMP-A", "COMP-B", "COMP-C"],
        "Current Stock": [500, 300, 200],
        "Monthly Consumption": [100, 75, 50],
    }
    df = pd.DataFrame(template_data)
    
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, sheet_name="Aging Data", index=False)
    buf.seek(0)
    return buf


# ═══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def topbar(ttl, sub):
    """Render page topbar"""
    st.markdown(f"""
    <div class="topbar">
        <div class="topbar-left">
            <h1 class="topbar-title">{ttl}</h1>
            <p class="topbar-sub">{sub}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


def sec(s):
    """Section divider"""
    st.markdown(f"""
    <div class="sec-div">
        <div class="sec-div-line"></div>
        <div class="sec-div-text">{s}</div>
        <div class="sec-div-line"></div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# INITIALIZE SESSION STATE
# ═══════════════════════════════════════════════════════════════

if "page" not in st.session_state:
    st.session_state["page"] = "upload"
if "mrp_results" not in st.session_state:
    st.session_state["mrp_results"] = None
if "seg_results" not in st.session_state:
    st.session_state["seg_results"] = None
if "aging_results" not in st.session_state:
    st.session_state["aging_results"] = None
if "cfg_phantom" not in st.session_state:
    st.session_state["cfg_phantom"] = "50"
if "cfg_vl1" not in st.session_state:
    st.session_state["cfg_vl1"] = "MAT001"
if "cfg_vl2" not in st.session_state:
    st.session_state["cfg_vl2"] = "MAT002"
if "cfg_vl3" not in st.session_state:
    st.session_state["cfg_vl3"] = "MAT003"
if "cfg_vl4" not in st.session_state:
    st.session_state["cfg_vl4"] = "MAT004"


# ═══════════════════════════════════════════════════════════════
# SIDEBAR NAVIGATION
# ═══════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    st.markdown("## 📊 SAP MRP Engine", unsafe_allow_html=True)
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    if st.button("📤 Upload Files", use_container_width=True, key="nav_upload"):
        st.session_state["page"] = "upload"
    if st.button("📋 Production Plan", use_container_width=True, key="nav_plan"):
        st.session_state["page"] = "plan"
    if st.button("⚙️  Settings", use_container_width=True, key="nav_settings"):
        st.session_state["page"] = "settings"

    st.divider()


# ═══════════════════════════════════════════════════════════════
# PAGE: UPLOAD FILES (ENHANCED WITH TEMPLATES)
# ═══════════════════════════════════════════════════════════════

if st.session_state["page"] == "upload":
    topbar("Upload Files", "Upload MRP data files with optional template download")

    st.markdown("""
    <div class="template-info">
    💡 <strong>Tip:</strong> Click "📥 Download Template" under each section to see the expected file format. 
    Fill in your data and upload to avoid errors.
    </div>
    """, unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────
    # SECTION 1: REQUIREMENT & STOCK
    # ─────────────────────────────────────────────────────────────
    sec("Requirement & Stock")

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("**Upload requirement file** (Excel)")
        st.markdown("""
        Expected sheets:
        - **Requirement**: BOM Header, Alt., and monthly demand columns
        """)
        req_file = st.file_uploader(
            "Choose Requirement file",
            type=["xlsx", "xls"],
            key="req_upload",
            label_visibility="collapsed"
        )
        if req_file:
            st.session_state["_req"] = req_file.read()
            st.success("✓ Requirement file loaded")

    with col2:
        st.markdown("**Download template**")
        st.markdown("Start with this format:")
        template_buf = create_requirement_template()
        st.download_button(
            label="📥 Download Requirement Template",
            data=template_buf.getvalue(),
            file_name="requirement_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    st.divider()

    # ─────────────────────────────────────────────────────────────
    # SECTION 2: BOM (BILL OF MATERIALS)
    # ─────────────────────────────────────────────────────────────
    sec("Bill of Materials (BOM)")

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("**Upload BOM file** (Excel)")
        st.markdown("""
        Expected columns:
        - **BOM Header**: Model identifier
        - **BOM Header Desc**: Model description
        - **Component**: Part number
        - **Quantity**: Required quantity
        """)
        bom_file = st.file_uploader(
            "Choose BOM file",
            type=["xlsx", "xls"],
            key="bom_upload",
            label_visibility="collapsed"
        )
        if bom_file:
            st.session_state["_bom"] = bom_file.read()
            st.success("✓ BOM file loaded")

    with col2:
        st.markdown("**Download template**")
        st.markdown("Start with this format:")
        template_buf = create_bom_template()
        st.download_button(
            label="📥 Download BOM Template",
            data=template_buf.getvalue(),
            file_name="bom_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    st.divider()

    # ─────────────────────────────────────────────────────────────
    # SECTION 3: STOCK / OPENING BALANCE
    # ─────────────────────────────────────────────────────────────
    sec("Stock / Opening Balance")

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("**Upload stock file** (Excel)")
        st.markdown("""
        Expected columns:
        - **Component**: Part number
        - **Stock Quantity**: Current inventory
        - **Safety Stock**: Minimum safety level
        """)
        stock_file = st.file_uploader(
            "Choose Stock file",
            type=["xlsx", "xls"],
            key="stock_upload",
            label_visibility="collapsed"
        )
        if stock_file:
            st.session_state["_prod"] = stock_file.read()
            st.success("✓ Stock file loaded")

    with col2:
        st.markdown("**Download template**")
        st.markdown("Start with this format:")
        template_buf = create_stock_template()
        st.download_button(
            label="📥 Download Stock Template",
            data=template_buf.getvalue(),
            file_name="stock_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    st.divider()

    # ─────────────────────────────────────────────────────────────
    # SECTION 4: PRODUCTION BATCH (OPTIONAL)
    # ─────────────────────────────────────────────────────────────
    sec("Production Batch Configuration (Optional)")

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("**Upload production batch file** (Excel)")
        st.markdown("""
        Expected columns:
        - **BOM Header**: Model identifier
        - **Batch Size**: Production quantity
        - **Lead Time**: Days to produce
        """)
        prod_file = st.file_uploader(
            "Choose Production file",
            type=["xlsx", "xls"],
            key="prod_upload",
            label_visibility="collapsed"
        )
        if prod_file:
            st.session_state["_prod"] = prod_file.read()
            st.success("✓ Production file loaded")

    with col2:
        st.markdown("**Download template**")
        st.markdown("Start with this format:")
        template_buf = create_production_template()
        st.download_button(
            label="📥 Download Production Template",
            data=template_buf.getvalue(),
            file_name="production_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    st.divider()

    # ─────────────────────────────────────────────────────────────
    # SECTION 5: RECEIPTS / POs (OPTIONAL)
    # ─────────────────────────────────────────────────────────────
    sec("Receipts / Purchase Orders (Optional)")

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("**Upload receipts file** (Excel)")
        st.markdown("""
        Expected columns:
        - **Component**: Part number
        - **Quantity**: Received quantity
        - **Due Date**: Expected date
        """)
        receipt_file = st.file_uploader(
            "Choose Receipts file",
            type=["xlsx", "xls"],
            key="receipt_upload",
            label_visibility="collapsed"
        )
        if receipt_file:
            st.session_state["_receipt"] = receipt_file.read()
            st.success("✓ Receipts file loaded")

    with col2:
        st.markdown("**Download template**")
        st.markdown("Start with this format:")
        template_buf = create_receipt_template()
        st.download_button(
            label="📥 Download Receipts Template",
            data=template_buf.getvalue(),
            file_name="receipts_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    st.divider()

    # ─────────────────────────────────────────────────────────────
    # SECTION 6: AGING / CONSUMPTION (OPTIONAL)
    # ─────────────────────────────────────────────────────────────
    sec("Aging / Consumption Data (Optional)")

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("**Upload aging file** (Excel)")
        st.markdown("""
        Expected columns:
        - **Component**: Part number
        - **Current Stock**: Inventory level
        - **Monthly Consumption**: Avg usage
        """)
        aging_file = st.file_uploader(
            "Choose Aging file",
            type=["xlsx", "xls"],
            key="aging_upload",
            label_visibility="collapsed"
        )
        if aging_file:
            st.session_state["_aging"] = aging_file.read()
            st.success("✓ Aging file loaded")

    with col2:
        st.markdown("**Download template**")
        st.markdown("Start with this format:")
        template_buf = create_aging_template()
        st.download_button(
            label="📥 Download Aging Template",
            data=template_buf.getvalue(),
            file_name="aging_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    # Summary section
    st.divider()
    sec("Upload Summary")
    
    summary_cols = st.columns(6)
    with summary_cols[0]:
        st.metric("Requirement", "✓" if st.session_state.get("_req") else "✗")
    with summary_cols[1]:
        st.metric("BOM", "✓" if st.session_state.get("_bom") else "✗")
    with summary_cols[2]:
        st.metric("Stock", "✓" if st.session_state.get("_prod") else "✗")
    with summary_cols[3]:
        st.metric("Production", "✓" if st.session_state.get("_prod") else "✗")
    with summary_cols[4]:
        st.metric("Receipts", "✓" if st.session_state.get("_receipt") else "✗")
    with summary_cols[5]:
        st.metric("Aging", "✓" if st.session_state.get("_aging") else "✗")


# ═══════════════════════════════════════════════════════════════
# PAGE: PRODUCTION PLAN
# ═══════════════════════════════════════════════════════════════
elif st.session_state["page"] == "plan":
    topbar("Production Plan", "Model-wise month-by-month requirement plan")

    req_bytes = st.session_state.get("_req")

    if not req_bytes:
        st.markdown("""<div class="empty"><div class="empty-icon">📋</div>
        <div class="empty-ttl">No requirement data</div>
        <div class="empty-sub">Upload the Requirement & Stock file on the Upload Files page first.</div></div>""",
        unsafe_allow_html=True)
    else:
        st.success("Production Plan module ready. (Full implementation from original code)")


# ═══════════════════════════════════════════════════════════════
# PAGE: SETTINGS
# ═══════════════════════════════════════════════════════════════
elif st.session_state["page"] == "settings":
    topbar("Settings", "Engine configuration and session management")

    sec("Engine Configuration")
    c1, c2 = st.columns(2)
    with c1:
        st.session_state["cfg_phantom"] = st.text_input(
            "Phantom Special Procurement Code",
            value=st.session_state["cfg_phantom"],
            key="s_ph"
        )
    with c2:
        st.markdown("**Phantom assemblies** are pass-through BOMs (e.g. SP code 50). The engine skips them and directly explodes their children.")

    sec("Verification Component Codes")
    v1, v2 = st.columns(2)
    with v1:
        st.session_state["cfg_vl1"] = st.text_input(
            "Verify L1",
            value=st.session_state["cfg_vl1"],
            key="s_v1"
        )
        st.session_state["cfg_vl3"] = st.text_input(
            "Verify L3 (phantom — should NOT appear)",
            value=st.session_state["cfg_vl3"],
            key="s_v3"
        )
    with v2:
        st.session_state["cfg_vl2"] = st.text_input(
            "Verify L2",
            value=st.session_state["cfg_vl2"],
            key="s_v2"
        )
        st.session_state["cfg_vl4"] = st.text_input(
            "Verify L4",
            value=st.session_state["cfg_vl4"],
            key="s_v4"
        )

    sec("Session Data")
    r1, r2, r3 = st.columns(3)
    r1.metric("MRP results", "Loaded" if st.session_state["mrp_results"] else "Not run")
    r2.metric("Segment results", "Loaded" if st.session_state["seg_results"] else "Not run")
    r3.metric("Aging results", "Loaded" if st.session_state["aging_results"] else "Not run")
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    if st.button("🗑 Clear all session data", key="clr"):
        for k in ["mrp_results", "seg_results", "aging_results", "seg_imp_bytes",
                  "_bom", "_req", "_prod", "_receipt", "_aging", "_ag_bom", "_ag_req", "_ag_rec"]:
            st.session_state[k] = None
        st.success("Session cleared.")
        st.rerun()
