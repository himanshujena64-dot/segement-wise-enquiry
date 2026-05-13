"""
MRP Config Dashboard — Streamlit App
Run with: streamlit run mrp_streamlit_app.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import io
from datetime import datetime

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MRP Config",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Global ── */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #0E1120;
    color: #F0F0F8;
}
[data-testid="stSidebar"] {
    background-color: #111422;
    border-right: 1px solid #2A2D42;
}
[data-testid="stSidebar"] * { color: #F0F0F8 !important; }

/* Hide default streamlit branding */
#MainMenu, footer, header { visibility: hidden; }

/* Metric cards */
[data-testid="metric-container"] {
    background: #1A1D2E;
    border: 1px solid #2A2D42;
    border-radius: 12px;
    padding: 16px !important;
}
[data-testid="stMetricValue"] { color: #A89CF5 !important; font-size: 26px !important; }
[data-testid="stMetricLabel"] { color: #7A7E9A !important; }

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #7C6EF5, #22C997) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    padding: 10px 24px !important;
    font-size: 14px !important;
    letter-spacing: 0.5px !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

/* File uploader */
[data-testid="stFileUploader"] {
    background: #1A1D2E !important;
    border: 1.5px dashed #2A2D42 !important;
    border-radius: 12px !important;
}

/* Dataframe */
[data-testid="stDataFrame"] { background: #1A1D2E !important; }
.dataframe { background: #1A1D2E !important; color: #D0D4F0 !important; }

/* Tabs */
[data-baseweb="tab-list"] { background: #1A1D2E !important; border-radius: 10px; }
[data-baseweb="tab"] { color: #7A7E9A !important; }
[aria-selected="true"] { color: #A89CF5 !important; }

/* Divider */
hr { border-color: #2A2D42 !important; }

/* Select box */
[data-baseweb="select"] { background: #1A1D2E !important; }

/* Expander */
[data-testid="stExpander"] {
    background: #1A1D2E !important;
    border: 1px solid #2A2D42 !important;
    border-radius: 12px !important;
}

/* Progress bar */
[data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, #7C6EF5, #22C997) !important;
}

/* Text input */
[data-testid="stTextInput"] input, [data-testid="stNumberInput"] input {
    background: #2A2D42 !important;
    border: 1px solid #3A3D52 !important;
    color: #F0F0F8 !important;
    border-radius: 8px !important;
}

/* Status badge helper */
.badge-ok    { background:#22C99720; color:#22C997; border:1px solid #22C99744;
               padding:3px 10px; border-radius:20px; font-size:11px; font-weight:700; }
.badge-low   { background:#F5C84220; color:#F5C842; border:1px solid #F5C84244;
               padding:3px 10px; border-radius:20px; font-size:11px; font-weight:700; }
.badge-crit  { background:#F55A5A20; color:#F55A5A; border:1px solid #F55A5A44;
               padding:3px 10px; border-radius:20px; font-size:11px; font-weight:700; }
.badge-req   { background:#F55A5A18; color:#F55A5A; border:1px solid #F55A5A33;
               padding:3px 7px; border-radius:20px; font-size:10px; font-weight:700; }
.badge-opt   { background:#7A7E9A18; color:#7A7E9A; border:1px solid #7A7E9A33;
               padding:3px 7px; border-radius:20px; font-size:10px; font-weight:700; }

/* Section header cards */
.section-card {
    background: #1A1D2E;
    border: 1.5px solid #2A2D42;
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 16px;
}

/* Sidebar section label */
.sidebar-section-label {
    font-size: 10px; font-weight: 700; letter-spacing: 1.5px;
    color: #4A4E6A; padding: 14px 0 4px;
}
</style>
""", unsafe_allow_html=True)

# ── Session state init ────────────────────────────────────────────────────────
defaults = {
    "page": "📊 Dashboard",
    "bom_file": None,
    "req_file": None,
    "prod_file": None,
    "receipt_file": None,
    "mrp_status": "idle",        # idle | running | done
    "mrp_output": None,
    "lead_time_buffer": 5,
    "safety_stock_pct": 10,
    "planning_horizon": 12,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # Logo
    st.markdown("""
    <div style="display:flex;align-items:center;gap:12px;padding:8px 0 18px">
      <div style="width:38px;height:38px;border-radius:10px;
                  background:linear-gradient(135deg,#7C6EF5,#22C997);
                  display:flex;align-items:center;justify-content:center;
                  font-size:18px;font-weight:800;color:#fff">M</div>
      <div>
        <div style="font-weight:800;font-size:13px;letter-spacing:1.5px">MRP CONFIG</div>
        <div style="font-size:10px;color:#4A4E6A">v2.4.1</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Upload progress
    uploaded_count = sum([
        st.session_state.bom_file is not None,
        st.session_state.req_file is not None,
        st.session_state.prod_file is not None,
        st.session_state.receipt_file is not None,
    ])
    req_done = sum([
        st.session_state.bom_file is not None,
        st.session_state.req_file is not None,
    ])

    st.markdown(f"""
    <div style="background:#1A1D2E;border:1px solid #2A2D42;border-radius:10px;padding:12px 14px;margin-bottom:14px">
      <div style="display:flex;justify-content:space-between;margin-bottom:6px">
        <span style="color:#7A7E9A;font-size:11px">Files uploaded</span>
        <span style="color:#22C997;font-size:11px;font-weight:700">{uploaded_count}/4</span>
      </div>
      <div style="background:#2A2D42;border-radius:999px;height:4px;overflow:hidden">
        <div style="width:{int(uploaded_count/4*100)}%;height:4px;
                    background:linear-gradient(90deg,#7C6EF5,#22C997);border-radius:999px"></div>
      </div>
      <div style="margin-top:6px;color:#4A4E6A;font-size:10px">{req_done}/2 required files ready</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Navigation
    PAGES = {
        "⊞ Dashboard": "📊 Dashboard",
        "⬆ Upload Files": "⬆ Upload Files",
        "▶ Run MRP": "▶ Run MRP",
        "── ANALYSIS ──": None,
        "⏱ Inventory Aging": "⏱ Inventory Aging",
        "📊 Stock Analysis": "📊 Stock Analysis",
        "📄 Reports": "📄 Reports",
        "── CONFIGURATION ──": None,
        "≡ Summary": "≡ Summary",
        "⚙ Settings": "⚙ Settings",
    }

    for label, page_key in PAGES.items():
        if page_key is None:
            st.markdown(f'<div class="sidebar-section-label">{label.replace("──","").strip()}</div>',
                        unsafe_allow_html=True)
        else:
            badge = ""
            if label == "⬆ Upload Files" and uploaded_count > 0:
                badge = f" ({uploaded_count})"
            if label == "⏱ Inventory Aging":
                badge = " ⚠"
            if st.button(f"{label}{badge}", key=f"nav_{page_key}", use_container_width=True):
                st.session_state.page = page_key

    st.divider()

    # MRP status badge
    status_color = {"idle": "#7A7E9A", "running": "#F5C842", "done": "#22C997"}[st.session_state.mrp_status]
    status_label = {"idle": "● Idle", "running": "⟳ Processing…", "done": "✓ MRP Complete"}[st.session_state.mrp_status]
    st.markdown(f"""
    <div style="background:#1A1D2E;border:1px solid {status_color}44;border-radius:8px;
                padding:8px 12px;text-align:center;color:{status_color};font-size:12px;font-weight:600">
      {status_label}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-top:20px;padding-top:14px;border-top:1px solid #2A2D42">
      <div style="color:#4A4E6A;font-size:11px">Need help?</div>
      <a href="#" style="color:#7C6EF5;font-size:12px;text-decoration:none">Contact support →</a>
    </div>
    """, unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def status_badge(s):
    cls = {"ok": "badge-ok", "low": "badge-low", "critical": "badge-crit"}.get(s, "badge-opt")
    lbl = {"ok": "OK", "low": "LOW", "critical": "CRITICAL"}.get(s, s.upper())
    return f'<span class="{cls}">{lbl}</span>'


def card(title, value, color="#A89CF5", sub=""):
    return f"""
    <div style="background:#1A1D2E;border:1.5px solid {color}33;border-radius:14px;padding:18px 16px">
      <div style="color:#7A7E9A;font-size:12px">{title}</div>
      <div style="color:{color};font-size:26px;font-weight:800;margin:8px 0 2px">{value}</div>
      <div style="color:#4A4E6A;font-size:12px">{sub}</div>
    </div>"""


def read_excel(uploaded):
    if uploaded is None:
        return None
    try:
        return pd.read_excel(uploaded)
    except Exception:
        try:
            uploaded.seek(0)
            return pd.read_csv(uploaded)
        except Exception:
            return None


# ── Sample data ───────────────────────────────────────────────────────────────
AGING_DATA = pd.DataFrame([
    {"Bucket": "0–30 days",  "Items": 1240, "Value (₹L)": 42.3, "Pct": 58, "Color": "#22C997"},
    {"Bucket": "31–60 days", "Items": 580,  "Value (₹L)": 18.7, "Pct": 27, "Color": "#F5C842"},
    {"Bucket": "61–90 days", "Items": 210,  "Value (₹L)": 7.1,  "Pct": 12, "Color": "#F5893A"},
    {"Bucket": "90+ days",   "Items": 90,   "Value (₹L)": 3.2,  "Pct": 5,  "Color": "#F55A5A"},
])

STOCK_DATA = pd.DataFrame([
    {"Part No.": "SHAFT-7700A", "Description": "Drive Shaft Assembly", "Stock": 340, "Required": 280, "Aging": "0-30",  "Status": "ok"},
    {"Part No.": "BRKT-1200",   "Description": "Mounting Bracket",      "Stock": 12,  "Required": 95,  "Aging": "61-90", "Status": "critical"},
    {"Part No.": "VALVE-09X",   "Description": "Pneumatic Valve",       "Stock": 0,   "Required": 44,  "Aging": "90+",   "Status": "critical"},
    {"Part No.": "CABLE-55M",   "Description": "Control Cable 5m",      "Stock": 210, "Required": 190, "Aging": "0-30",  "Status": "ok"},
    {"Part No.": "SEAL-R44",    "Description": "Rotary Seal Kit",       "Stock": 5,   "Required": 60,  "Aging": "61-90", "Status": "low"},
    {"Part No.": "MOTOR-3PH",   "Description": "3-Phase Motor 5HP",     "Stock": 8,   "Required": 20,  "Aging": "31-60", "Status": "low"},
    {"Part No.": "PUMP-HYD22",  "Description": "Hydraulic Pump Unit",   "Stock": 0,   "Required": 12,  "Aging": "90+",   "Status": "critical"},
])

# ── PLOTLY theme helper ───────────────────────────────────────────────────────
PLOT_BG = "#1A1D2E"
PAPER_BG = "#0E1120"
FONT_COLOR = "#A0A4C4"
GRID_COLOR = "#2A2D42"


def dark_layout(fig, title=""):
    fig.update_layout(
        title=dict(text=title, font=dict(color="#F0F0F8", size=14)),
        plot_bgcolor=PLOT_BG,
        paper_bgcolor=PAPER_BG,
        font=dict(color=FONT_COLOR, size=12),
        margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(bgcolor=PLOT_BG, bordercolor=GRID_COLOR, borderwidth=1),
        xaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR),
        yaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR),
    )
    return fig


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "📊 Dashboard":
    st.markdown("## 📊 Dashboard")
    st.markdown('<p style="color:#7A7E9A;font-size:13px;margin-top:-12px">Overview of your MRP process</p>',
                unsafe_allow_html=True)
    st.divider()

    # KPI row
    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(card("Files Uploaded", f"{uploaded_count}/4", "#7C6EF5", "total data files"), unsafe_allow_html=True)
    k2.markdown(card("Required Files", f"{req_done}/2", "#22C997", "BOM + Req & Stock"), unsafe_allow_html=True)
    k3.markdown(card("MRP Status",
                     {"idle": "Pending", "running": "Running", "done": "Done"}[st.session_state.mrp_status],
                     {"idle": "#F5C842", "running": "#F5893A", "done": "#22C997"}[st.session_state.mrp_status],
                     "last run"), unsafe_allow_html=True)
    k4.markdown(card("Critical Items", "3", "#F55A5A", "need attention"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts row
    col_left, col_right = st.columns([1, 1], gap="medium")

    with col_left:
        st.markdown("#### Aging Distribution")
        fig_pie = go.Figure(go.Pie(
            labels=AGING_DATA["Bucket"],
            values=AGING_DATA["Items"],
            marker=dict(colors=AGING_DATA["Color"].tolist(), line=dict(color=PLOT_BG, width=2)),
            hole=0.55,
            textinfo="label+percent",
            textfont=dict(color="#F0F0F8", size=11),
        ))
        dark_layout(fig_pie)
        fig_pie.update_layout(showlegend=False, height=280, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_right:
        st.markdown("#### Stock vs Requirement")
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            name="Stock", x=STOCK_DATA["Part No."], y=STOCK_DATA["Stock"],
            marker_color="#7C6EF5CC", marker_line_width=0,
        ))
        fig_bar.add_trace(go.Bar(
            name="Required", x=STOCK_DATA["Part No."], y=STOCK_DATA["Required"],
            marker_color="#22C99766", marker_line_width=0,
        ))
        dark_layout(fig_bar)
        fig_bar.update_layout(barmode="group", height=280, xaxis_tickangle=-30,
                               legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_bar, use_container_width=True)

    # Quick actions
    st.markdown("#### Quick Actions")
    qa1, qa2, qa3, _ = st.columns([1, 1, 1, 3])
    if qa1.button("⬆ Upload Files"):
        st.session_state.page = "⬆ Upload Files"
        st.rerun()
    if qa2.button("⏱ View Aging"):
        st.session_state.page = "⏱ Inventory Aging"
        st.rerun()
    if qa3.button("📊 Stock Analysis"):
        st.session_state.page = "📊 Stock Analysis"
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: UPLOAD FILES
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "⬆ Upload Files":
    st.markdown("## ⬆ Upload Configuration & Data Files")
    st.markdown('<p style="color:#7A7E9A;font-size:13px;margin-top:-12px">Upload all required files to run the MRP process</p>',
                unsafe_allow_html=True)
    st.divider()

    col1, col2 = st.columns(2, gap="medium")

    with col1:
        st.markdown("""
        <div class="section-card" style="border-color:#7C6EF566">
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px">
            <div style="display:flex;align-items:center;gap:10px">
              <span style="font-size:22px">📐</span>
              <span style="font-weight:700;font-size:14px">BOM File</span>
            </div>
            <span class="badge-req">REQUIRED</span>
          </div>
        </div>""", unsafe_allow_html=True)
        bom = st.file_uploader("BOM File", type=["xlsx", "xls"],
                               key="bom_uploader", label_visibility="collapsed")
        if bom:
            st.session_state.bom_file = bom
            st.success(f"✓  {bom.name}  ({bom.size/1024:.1f} KB)")
        elif st.session_state.bom_file:
            st.success(f"✓  {st.session_state.bom_file.name}")

    with col2:
        st.markdown("""
        <div class="section-card" style="border-color:#22C99766">
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px">
            <div style="display:flex;align-items:center;gap:10px">
              <span style="font-size:22px">📦</span>
              <span style="font-weight:700;font-size:14px">Req. & Stock File</span>
            </div>
            <span class="badge-req">REQUIRED</span>
          </div>
        </div>""", unsafe_allow_html=True)
        req = st.file_uploader("Req & Stock", type=["xlsx", "xls"],
                               key="req_uploader", label_visibility="collapsed")
        if req:
            st.session_state.req_file = req
            st.success(f"✓  {req.name}  ({req.size/1024:.1f} KB)")
        elif st.session_state.req_file:
            st.success(f"✓  {st.session_state.req_file.name}")

    st.markdown("<br>", unsafe_allow_html=True)
    col3, col4 = st.columns(2, gap="medium")

    with col3:
        st.markdown("""
        <div class="section-card" style="border-color:#F5893A44">
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px">
            <div style="display:flex;align-items:center;gap:10px">
              <span style="font-size:22px">🏭</span>
              <span style="font-weight:700;font-size:14px">Production Orders</span>
            </div>
            <span class="badge-opt">OPTIONAL</span>
          </div>
        </div>""", unsafe_allow_html=True)
        prod = st.file_uploader("Production Orders", type=["xlsx", "xls"],
                                key="prod_uploader", label_visibility="collapsed")
        if prod:
            st.session_state.prod_file = prod
            st.success(f"✓  {prod.name}  ({prod.size/1024:.1f} KB)")
        elif st.session_state.prod_file:
            st.success(f"✓  {st.session_state.prod_file.name}")

    with col4:
        st.markdown("""
        <div class="section-card" style="border-color:#3A9EF544">
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px">
            <div style="display:flex;align-items:center;gap:10px">
              <span style="font-size:22px">🧾</span>
              <span style="font-weight:700;font-size:14px">Receipt Quantities</span>
            </div>
            <span class="badge-opt">OPTIONAL</span>
          </div>
        </div>""", unsafe_allow_html=True)
        receipt = st.file_uploader("Receipt Quantities", type=["xlsx", "xls"],
                                   key="receipt_uploader", label_visibility="collapsed")
        if receipt:
            st.session_state.receipt_file = receipt
            st.success(f"✓  {receipt.name}  ({receipt.size/1024:.1f} KB)")
        elif st.session_state.receipt_file:
            st.success(f"✓  {st.session_state.receipt_file.name}")

    st.divider()

    # Run MRP button
    can_run = (st.session_state.bom_file is not None and
               st.session_state.req_file is not None)

    run_col, msg_col = st.columns([1, 3])
    with run_col:
        run_clicked = st.button("▶ Run MRP", disabled=not can_run)
    with msg_col:
        if not can_run:
            st.markdown('<p style="color:#7A7E9A;margin-top:12px">Upload BOM and Req. & Stock files to continue</p>',
                        unsafe_allow_html=True)

    if run_clicked and can_run:
        with st.spinner("Running MRP engine…"):
            import time
            time.sleep(2)
        st.session_state.mrp_status = "done"
        st.success("✓ MRP completed successfully! Navigate to Summary to view results.")


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: RUN MRP
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "▶ Run MRP":
    st.markdown("## ▶ Run MRP")
    st.markdown('<p style="color:#7A7E9A;font-size:13px;margin-top:-12px">Execute the Material Requirements Planning engine</p>',
                unsafe_allow_html=True)
    st.divider()

    st.markdown("#### File Readiness Check")
    checks = [
        ("📐 BOM File", st.session_state.bom_file, True),
        ("📦 Req. & Stock File", st.session_state.req_file, True),
        ("🏭 Production Orders", st.session_state.prod_file, False),
        ("🧾 Receipt Quantities", st.session_state.receipt_file, False),
    ]
    for label, fobj, required in checks:
        r1, r2, r3 = st.columns([3, 1, 1])
        r1.markdown(f'<span style="color:#D0D4F0">{label}</span>', unsafe_allow_html=True)
        r2.markdown(
            f'<span class="badge-req">{"REQUIRED" if required else "OPTIONAL"}</span>',
            unsafe_allow_html=True)
        if fobj:
            r3.markdown('<span class="badge-ok">✓ READY</span>', unsafe_allow_html=True)
        elif required:
            r3.markdown('<span class="badge-crit">✗ MISSING</span>', unsafe_allow_html=True)
        else:
            r3.markdown('<span style="color:#4A4E6A;font-size:12px">— Not provided</span>',
                        unsafe_allow_html=True)

    st.divider()

    st.markdown("#### MRP Engine Parameters")
    p1, p2, p3 = st.columns(3)
    with p1:
        lb = st.number_input("Lead Time Buffer (days)", min_value=0, max_value=30,
                             value=st.session_state.lead_time_buffer)
    with p2:
        ss = st.number_input("Safety Stock %", min_value=0, max_value=50,
                             value=st.session_state.safety_stock_pct)
    with p3:
        ph = st.number_input("Planning Horizon (weeks)", min_value=1, max_value=52,
                             value=st.session_state.planning_horizon)

    st.session_state.lead_time_buffer = lb
    st.session_state.safety_stock_pct = ss
    st.session_state.planning_horizon = ph

    st.markdown("<br>", unsafe_allow_html=True)
    can_run = st.session_state.bom_file and st.session_state.req_file
    if st.button("▶ Run MRP Now", disabled=not can_run):
        with st.spinner("Running MRP engine…"):
            import time
            time.sleep(2)
        st.session_state.mrp_status = "done"
        st.success("✓ MRP completed! View results in Summary.")


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: INVENTORY AGING
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "⏱ Inventory Aging":
    st.markdown("## ⏱ Inventory Aging")
    st.markdown('<p style="color:#7A7E9A;font-size:13px;margin-top:-12px">Stock age distribution across all warehouses</p>',
                unsafe_allow_html=True)
    st.divider()

    # Metric cards
    ag_cols = st.columns(4)
    colors = ["#22C997", "#F5C842", "#F5893A", "#F55A5A"]
    for i, (_, row) in enumerate(AGING_DATA.iterrows()):
        ag_cols[i].markdown(
            card(row["Bucket"], str(row["Items"]), colors[i], f"₹{row['Value (₹L)']}L  ·  {row['Pct']}% of stock"),
            unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts
    ch1, ch2 = st.columns([1, 1], gap="medium")

    with ch1:
        st.markdown("#### Aging Donut")
        fig_donut = go.Figure(go.Pie(
            labels=AGING_DATA["Bucket"],
            values=AGING_DATA["Items"],
            marker=dict(colors=colors, line=dict(color=PLOT_BG, width=3)),
            hole=0.6,
            textinfo="label+percent",
            textfont=dict(color="#F0F0F8", size=11),
        ))
        dark_layout(fig_donut)
        fig_donut.update_layout(showlegend=False, height=320, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig_donut, use_container_width=True)

    with ch2:
        st.markdown("#### Aging Bar Chart")
        fig_hbar = go.Figure(go.Bar(
            x=AGING_DATA["Items"],
            y=AGING_DATA["Bucket"],
            orientation="h",
            marker=dict(color=colors, line_width=0),
            text=AGING_DATA["Items"].astype(str) + " items",
            textposition="inside",
            textfont=dict(color="#fff", size=11),
        ))
        dark_layout(fig_hbar)
        fig_hbar.update_layout(height=320, xaxis_title="Items", showlegend=False)
        st.plotly_chart(fig_hbar, use_container_width=True)

    # Value trend (synthetic)
    st.markdown("#### Stock Value by Aging Bucket (₹ Lakhs)")
    fig_value = go.Figure(go.Bar(
        x=AGING_DATA["Bucket"],
        y=AGING_DATA["Value (₹L)"],
        marker=dict(color=colors, line_width=0),
        text=AGING_DATA["Value (₹L)"].apply(lambda v: f"₹{v}L"),
        textposition="outside",
        textfont=dict(color="#F0F0F8"),
    ))
    dark_layout(fig_value)
    fig_value.update_layout(height=280, yaxis_title="₹ Lakhs")
    st.plotly_chart(fig_value, use_container_width=True)

    # Critical items table
    st.markdown("#### Critical Aging Items")
    display = STOCK_DATA.copy()
    display["Gap"] = display["Stock"] - display["Required"]

    def color_status(val):
        c = {"ok": "color: #22C997", "low": "color: #F5C842", "critical": "color: #F55A5A"}.get(val, "")
        return c

    def color_gap(val):
        return "color: #22C997" if val >= 0 else ("color: #F5C842" if val > -20 else "color: #F55A5A")

    styled = (display.style
              .applymap(color_status, subset=["Status"])
              .applymap(color_gap, subset=["Gap"])
              .set_properties(**{"background-color": "#1A1D2E", "color": "#D0D4F0", "border-color": "#2A2D42"})
              .format({"Gap": lambda v: f"+{v}" if v >= 0 else str(v)}))
    st.dataframe(styled, use_container_width=True, hide_index=True)

    # Download
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        AGING_DATA.drop(columns=["Color"]).to_excel(writer, sheet_name="Aging Summary", index=False)
        display.to_excel(writer, sheet_name="Critical Items", index=False)
    st.download_button("⬇ Download Aging Report (.xlsx)", buf.getvalue(),
                       file_name=f"aging_report_{datetime.today().strftime('%Y%m%d')}.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: STOCK ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "📊 Stock Analysis":
    st.markdown("## 📊 Stock Analysis")
    st.markdown('<p style="color:#7A7E9A;font-size:13px;margin-top:-12px">Current inventory levels vs requirements</p>',
                unsafe_allow_html=True)
    st.divider()

    s1, s2, s3 = st.columns(3)
    s1.markdown(card("Total SKUs", "2,340", "#7C6EF5", "active items"), unsafe_allow_html=True)
    s2.markdown(card("Stock Value", "₹71.3L", "#22C997", "current holding"), unsafe_allow_html=True)
    s3.markdown(card("Shortage Items", "48", "#F55A5A", "need replenishment"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Filter
    fc1, fc2 = st.columns([2, 1])
    with fc1:
        status_filter = st.multiselect("Filter by Status", ["ok", "low", "critical"],
                                       default=["ok", "low", "critical"])
    with fc2:
        aging_filter = st.multiselect("Filter by Aging", ["0-30", "31-60", "61-90", "90+"],
                                      default=["0-30", "31-60", "61-90", "90+"])

    df_filtered = STOCK_DATA[
        (STOCK_DATA["Status"].isin(status_filter)) &
        (STOCK_DATA["Aging"].isin(aging_filter))
    ].copy()
    df_filtered["Gap"] = df_filtered["Stock"] - df_filtered["Required"]

    # Grouped bar chart
    fig_stock = go.Figure()
    fig_stock.add_trace(go.Bar(name="Stock", x=df_filtered["Part No."], y=df_filtered["Stock"],
                               marker_color="#7C6EF5CC", marker_line_width=0))
    fig_stock.add_trace(go.Bar(name="Required", x=df_filtered["Part No."], y=df_filtered["Required"],
                               marker_color="#22C99766", marker_line_width=0))
    dark_layout(fig_stock, "Stock vs Requirement by Part")
    fig_stock.update_layout(barmode="group", height=320, xaxis_tickangle=-30)
    st.plotly_chart(fig_stock, use_container_width=True)

    # Gap chart
    gap_colors = ["#22C997" if g >= 0 else ("#F5C842" if g > -20 else "#F55A5A")
                  for g in df_filtered["Gap"]]
    fig_gap = go.Figure(go.Bar(
        x=df_filtered["Part No."], y=df_filtered["Gap"],
        marker=dict(color=gap_colors, line_width=0),
        text=df_filtered["Gap"].apply(lambda v: f"+{v}" if v >= 0 else str(v)),
        textposition="outside", textfont=dict(color="#F0F0F8"),
    ))
    dark_layout(fig_gap, "Stock Gap (Stock − Required)")
    fig_gap.add_hline(y=0, line_color="#4A4E6A", line_dash="dot")
    fig_gap.update_layout(height=260)
    st.plotly_chart(fig_gap, use_container_width=True)

    # Table
    st.markdown("#### Detailed Stock Table")

    def highlight_gap(val):
        return "color: #22C997" if val >= 0 else ("color: #F5C842" if val > -20 else "color: #F55A5A")

    def highlight_status(val):
        return {"ok": "color: #22C997", "low": "color: #F5C842", "critical": "color: #F55A5A"}.get(val, "")

    styled = (df_filtered.style
              .applymap(highlight_gap, subset=["Gap"])
              .applymap(highlight_status, subset=["Status"])
              .set_properties(**{"background-color": "#1A1D2E", "color": "#D0D4F0", "border-color": "#2A2D42"})
              .format({"Gap": lambda v: f"+{v}" if v >= 0 else str(v)}))
    st.dataframe(styled, use_container_width=True, hide_index=True)

    # Download
    buf = io.BytesIO()
    df_filtered.to_excel(buf, index=False, engine="openpyxl")
    st.download_button("⬇ Download Stock Analysis (.xlsx)", buf.getvalue(),
                       file_name=f"stock_analysis_{datetime.today().strftime('%Y%m%d')}.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: REPORTS
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "📄 Reports":
    st.markdown("## 📄 Reports")
    st.markdown('<p style="color:#7A7E9A;font-size:13px;margin-top:-12px">Generate and download MRP reports</p>',
                unsafe_allow_html=True)
    st.divider()

    REPORTS = [
        ("MRP Output Report", "Full procurement & production plan from last MRP run", "📋"),
        ("Shortage Report", "Items below safety stock or with zero inventory", "⚠️"),
        ("Aging Summary", "Stock aging buckets with value breakdown", "⏱"),
        ("Stock Valuation", "Current inventory valued at standard cost", "💰"),
    ]

    for icon, title, desc in [(r[2], r[0], r[1]) for r in REPORTS]:
        with st.expander(f"{icon}  {title}"):
            st.markdown(f'<span style="color:#7A7E9A;font-size:13px">{desc}</span>',
                        unsafe_allow_html=True)
            if title == "Aging Summary":
                buf = io.BytesIO()
                with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                    AGING_DATA.drop(columns=["Color"]).to_excel(writer, sheet_name="Aging", index=False)
                st.download_button(f"⬇ Download {title}", buf.getvalue(),
                                   file_name=f"{title.lower().replace(' ','_')}.xlsx",
                                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                   key=f"dl_{title}")
            elif title == "Shortage Report":
                shortage = STOCK_DATA[STOCK_DATA["Status"].isin(["low", "critical"])].copy()
                shortage["Gap"] = shortage["Stock"] - shortage["Required"]
                buf = io.BytesIO()
                shortage.to_excel(buf, index=False, engine="openpyxl")
                st.download_button(f"⬇ Download {title}", buf.getvalue(),
                                   file_name=f"{title.lower().replace(' ','_')}.xlsx",
                                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                   key=f"dl_{title}")
            else:
                st.info("Run MRP engine to generate this report.")


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "≡ Summary":
    st.markdown("## ≡ Summary")
    st.markdown('<p style="color:#7A7E9A;font-size:13px;margin-top:-12px">MRP run summary and key outputs</p>',
                unsafe_allow_html=True)
    st.divider()

    if st.session_state.mrp_status != "done":
        st.markdown("""
        <div class="section-card" style="text-align:center;padding:48px">
          <div style="font-size:40px;margin-bottom:12px">🏭</div>
          <div style="color:#7A7E9A;font-size:15px">Run the MRP engine to view summary results.</div>
        </div>""", unsafe_allow_html=True)
    else:
        m1, m2, m3, m4 = st.columns(4)
        m1.markdown(card("Items Processed", "2,340", "#7C6EF5"), unsafe_allow_html=True)
        m2.markdown(card("POs Suggested", "148", "#22C997"), unsafe_allow_html=True)
        m3.markdown(card("Shortage Items", "48", "#F55A5A"), unsafe_allow_html=True)
        m4.markdown(card("Surplus Items", "312", "#3A9EF5"), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### MRP Output Preview")
        sample_output = pd.DataFrame([
            {"Part No.": "BRKT-1200", "Action": "Purchase", "Qty": 83, "Due Date": "2026-05-25", "Priority": "High"},
            {"Part No.": "VALVE-09X", "Action": "Purchase", "Qty": 44, "Due Date": "2026-05-20", "Priority": "Critical"},
            {"Part No.": "SEAL-R44",  "Action": "Purchase", "Qty": 55, "Due Date": "2026-06-01", "Priority": "Medium"},
            {"Part No.": "MOTOR-3PH", "Action": "Purchase", "Qty": 12, "Due Date": "2026-05-28", "Priority": "High"},
            {"Part No.": "PUMP-HYD22","Action": "Purchase", "Qty": 12, "Due Date": "2026-05-18", "Priority": "Critical"},
        ])
        st.dataframe(sample_output, use_container_width=True, hide_index=True)

        buf = io.BytesIO()
        sample_output.to_excel(buf, index=False, engine="openpyxl")
        st.download_button("⬇ Download MRP Output (.xlsx)", buf.getvalue(),
                           file_name=f"mrp_output_{datetime.today().strftime('%Y%m%d')}.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: SETTINGS
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "⚙ Settings":
    st.markdown("## ⚙ Settings")
    st.markdown('<p style="color:#7A7E9A;font-size:13px;margin-top:-12px">Configure MRP engine parameters</p>',
                unsafe_allow_html=True)
    st.divider()

    with st.form("settings_form"):
        st.markdown("#### Planning Parameters")
        sc1, sc2, sc3 = st.columns(3)
        lt = sc1.number_input("Lead Time Buffer (days)", 0, 30, st.session_state.lead_time_buffer)
        ss = sc2.number_input("Safety Stock %", 0, 50, st.session_state.safety_stock_pct)
        ph = sc3.number_input("Planning Horizon (weeks)", 1, 52, st.session_state.planning_horizon)

        st.markdown("#### Output Options")
        oc1, oc2 = st.columns(2)
        oc1.checkbox("Include production orders in plan", value=True)
        oc2.checkbox("Include receipt quantities in plan", value=True)
        oc1.checkbox("Generate shortage alerts", value=True)
        oc2.checkbox("Auto-export results to Excel", value=False)

        st.markdown("#### Notifications")
        nc1, nc2 = st.columns(2)
        nc1.text_input("Alert Email", placeholder="ops@company.com")
        nc2.selectbox("Alert Threshold", ["Any shortage", "Critical only", "None"])

        submitted = st.form_submit_button("💾 Save Settings")
        if submitted:
            st.session_state.lead_time_buffer = lt
            st.session_state.safety_stock_pct = ss
            st.session_state.planning_horizon = ph
            st.success("✓ Settings saved successfully.")
