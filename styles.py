import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

:root {
  --ink:#241f2b; --muted:#6f6879; --line:#e8e3ee; --card:#ffffff; --bg:#f7f5fa;
  --brand:#6b46a8; --brand-d:#54348c; --brand-l:#efe9f8; --sun:#f4a62a; --sun-l:#fff4de;
  --good:#1f8a5b; --good-l:#e3f5ec; --warn:#b4570a; --warn-l:#fff0df; --bad:#b3261e; --bad-l:#fdeceb;
}
html, body, [class*="css"], .stApp { font-family:'Plus Jakarta Sans', system-ui, -apple-system, 'Segoe UI', sans-serif; }
.stApp { background:var(--bg); color:var(--ink); }

/* chrome */
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stSidebar"],
[data-testid="collapsedControl"], [data-testid="stSidebarCollapsedControl"] { display:none !important; }
header[data-testid="stHeader"] { background:transparent; height:0; }
.block-container { max-width:1080px; padding:1.2rem 1.2rem 5rem; }
h1,h2,h3 { letter-spacing:-.01em; color:var(--ink); }
h3 { font-size:1.05rem !important; font-weight:700 !important; margin:.2rem 0 .4rem !important; }

/* brand bar */
.brandbar { display:flex; align-items:center; gap:.7rem; margin-bottom:.2rem; }
.logo { width:38px; height:38px; border-radius:12px; background:linear-gradient(135deg,var(--sun),#ff7a45);
  display:grid; place-items:center; font-size:20px; box-shadow:0 4px 12px rgba(244,166,42,.35); }
.brandname { font-weight:800; font-size:1.05rem; line-height:1.1; }
.brandsub { color:var(--muted); font-size:.74rem; font-weight:500; }

/* nav (segmented control) */
.st-key-page, .st-key-page [data-testid="stButtonGroup"] { width:100% !important; }
.st-key-page { margin:.5rem 0 1.1rem; }
.st-key-page [data-testid="stButtonGroup"] { display:flex; background:var(--card); border:1px solid var(--line); border-radius:14px; padding:4px; gap:2px; box-sizing:border-box; }
.st-key-page button { flex:1 1 0; min-width:0; border-radius:10px !important; font-weight:600; padding:.55rem .3rem; border:0 !important; white-space:nowrap; justify-content:center; }
.st-key-page [data-testid="stButtonGroup"] > div:not([data-testid]) { flex:1 1 100% !important; width:100% !important; min-width:100% !important; max-width:none !important; display:flex; gap:2px; }
.st-key-page button p { overflow:visible !important; text-overflow:clip !important; }
.st-key-page button[aria-checked="true"], .st-key-page button[kind="segmented_controlActive"] { background:var(--brand) !important; color:#fff !important; }
.st-key-page button[aria-checked="true"] *, .st-key-page button[kind="segmented_controlActive"] * { color:#fff !important; }

/* page title */
.pagehead h2 { margin:0; font-size:1.55rem; font-weight:800; }
.pagehead p { margin:.15rem 0 1rem; color:var(--muted); font-size:.93rem; }

/* hero */
.hero { background:linear-gradient(135deg,#5b3896 0%,#7d52c0 100%); color:#fff; border-radius:22px; padding:1.4rem 1.5rem 1.3rem;
  box-shadow:0 10px 30px rgba(91,56,150,.25); margin-bottom:1rem; }
.hero .eyebrow { font-size:.72rem; font-weight:700; letter-spacing:.09em; text-transform:uppercase; opacity:.8; }
.hero h1 { color:#fff; font-size:1.55rem; font-weight:800; margin:.15rem 0 0; padding:0; line-height:1.2; }
.hero-top { display:flex; justify-content:space-between; align-items:flex-start; gap:1rem; }
.hero-pct { font-size:2.5rem; font-weight:800; line-height:1; color:var(--sun); }
.bar { height:12px; background:rgba(255,255,255,.22); border-radius:99px; overflow:hidden; margin:1rem 0 .7rem; }
.bar > div { height:100%; background:linear-gradient(90deg,var(--sun),#ffd27a); border-radius:99px; min-width:6px; }
.hero-nums { display:flex; justify-content:space-between; flex-wrap:wrap; gap:.3rem; font-size:.92rem; opacity:.95; }
.hero-nums b { font-size:1.15rem; }

/* cards & stats */
.stat { background:var(--card); border:1px solid var(--line); border-radius:16px; padding:.85rem 1rem; }
.stat .n { font-size:1.55rem; font-weight:800; line-height:1.15; }
.stat .l { color:var(--muted); font-size:.78rem; font-weight:600; }
.stat.warn .n { color:var(--warn); } .stat.good .n { color:var(--good); }
[data-testid="stVerticalBlockBorderWrapper"] { background:var(--card); border-radius:16px; }
.hint { background:var(--sun-l); border:1px solid #f6dca6; border-radius:14px; padding:.8rem 1rem; font-size:.92rem; }
.hint b { color:#8a5a00; }
.empty { text-align:center; padding:2rem 1rem; border:2px dashed var(--line); border-radius:18px; background:var(--card); }
.empty .big { font-size:2rem; } .empty h3 { margin-top:.4rem !important; }
.empty p { color:var(--muted); max-width:460px; margin:.2rem auto 0; }

/* people rows */
.person { display:flex; justify-content:space-between; align-items:center; gap:.6rem; }
.person .nm { font-weight:700; } .person .sub { color:var(--muted); font-size:.82rem; }
.badge { display:inline-block; font-size:.72rem; font-weight:700; padding:.15rem .6rem; border-radius:99px; background:var(--brand-l); color:var(--brand-d); white-space:nowrap; }
.badge.s-donated { background:var(--good-l); color:var(--good); }
.badge.s-committed, .badge.s-interested { background:var(--sun-l); color:#8a5a00; }
.badge.s-closed { background:#eee; color:#666; }
.badge.late { background:var(--bad-l); color:var(--bad); }
.badge.today { background:var(--warn-l); color:var(--warn); }

/* pipeline */
.pipe { display:flex; flex-direction:column; gap:.45rem; }
.pipe-row { display:grid; grid-template-columns:92px 1fr 26px; align-items:center; gap:.6rem; font-size:.84rem; }
.pipe-row .t { height:9px; background:var(--brand-l); border-radius:9px; overflow:hidden; }
.pipe-row .t > div { height:100%; background:var(--brand); border-radius:9px; }
.pipe-row.s-donated .t > div { background:var(--good); }
.pipe-row .c { text-align:right; font-weight:700; }

/* journey */
.wk { display:flex; gap:.4rem; margin:.2rem 0 1rem; }
.wk div { flex:1; text-align:center; padding:.5rem 0; border-radius:12px; background:var(--card); border:1px solid var(--line); font-weight:700; font-size:.82rem; color:var(--muted); }
.wk div.done { background:var(--good-l); color:var(--good); border-color:transparent; }
.wk div.now { background:var(--brand); color:#fff; border-color:transparent; }

/* controls */
.stButton > button, .stDownloadButton > button, .stLinkButton > a { border-radius:12px; font-weight:600; border:1px solid var(--line); }
.stButton > button[kind="primary"], .stDownloadButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] { background:var(--brand); border-color:var(--brand); color:#fff; }
.stButton > button[kind="primary"]:hover, .stFormSubmitButton > button[kind="primary"]:hover { background:var(--brand-d); border-color:var(--brand-d); }
.stTextInput input, .stTextArea textarea, .stNumberInput input, .stDateInput input, [data-baseweb="select"] > div { border-radius:12px !important; }
[data-testid="stDataFrame"], [data-testid="stDataEditor"] { border:1px solid var(--line); border-radius:14px; overflow:hidden; }
[data-testid="stTabs"] button { font-weight:600; }
.reply { white-space:pre-wrap; background:var(--card); border:1px solid var(--line); border-radius:14px; padding:1rem 1.1rem; }

@media (max-width:640px) {
  .st-key-page button, .st-key-page button * { font-size:.6rem !important; letter-spacing:-.02em; }
  .st-key-page button { padding:.5rem 0 !important; overflow:visible !important; }
  div[data-testid="stHorizontalBlock"]:has(.stat) { flex-wrap:wrap; gap:.6rem; }
  div[data-testid="stHorizontalBlock"]:has(.stat) > div { min-width:calc(50% - .4rem) !important; flex:1 1 calc(50% - .4rem) !important; }
  .block-container { padding:.8rem .7rem 4rem; }
  .hero h1 { font-size:1.25rem; } .hero-pct { font-size:2rem; }
  [data-testid="stSegmentedControl"] button, [data-testid="stButtonGroup"] button { font-size:.72rem; padding:.5rem .15rem; }
  .pagehead h2 { font-size:1.3rem; }
}
</style>
"""


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)
