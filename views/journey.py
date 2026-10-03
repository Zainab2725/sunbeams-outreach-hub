import streamlit as st

from data import MILESTONES, current_week
from services.gemini import generate_text, is_configured
from services.reports import build_impact_report
from ui import html, page_head


def _weekly():
    week = current_week()
    strip = "".join(
        f'<div class="{"done" if i < week else "now" if i == week else ""}">{"✓" if i < week else "Week " + str(i) if i == week else i}</div>'
        for i in range(1, 7))
    html(f'<div class="wk">{strip}</div>')
    if not st.session_state.campaign.get("start"):
        week = st.slider("Which week are you in?", 1, 6, st.session_state.manual_week)
        st.session_state.manual_week = week
        st.caption("Set a start date in Project and this will update automatically.")

    for w in range(1, 7):
        items = MILESTONES[w]
        done = sum(bool(st.session_state.checks.get(f"w{w}_{i}")) for i in range(len(items)))
        state = "Current" if w == week else "Done" if w < week else "Upcoming"
        with st.expander(f"Week {w} · {done}/{len(items)} · {state}", expanded=(w == week)):
            for i, item in enumerate(items):
                key = f"w{w}_{i}"
                st.session_state.checks[key] = st.checkbox(item, value=bool(st.session_state.checks.get(key)), key=f"chk_{key}")


def _report():
    ss = st.session_state
    r = ss.reflections
    st.markdown("Fill in the three boxes below. Everything else in your report is filled in for you from what you recorded.")
    r["learnings"] = st.text_area("What did you learn?", r["learnings"], height=100, placeholder="e.g. People respond better to personal messages than group posts.")
    r["challenges"] = st.text_area("What was hard, and how did you handle it?", r["challenges"], height=100)
    r["evidence"] = st.text_area("Evidence you’re keeping", r["evidence"], height=80, placeholder="e.g. WhatsApp screenshots, donation receipts, photos of supplies")

    if is_configured() and st.button("✨ Write a short summary with Gemini"):
        facts = build_impact_report(ss.campaign, ss.contacts, ss.donations, current_week(), r)
        with st.spinner("Writing…"):
            out = generate_text("Write a factual, first-person summary paragraph (max 120 words) for this intern's impact report. "
                                "Only use facts below.\n\n" + facts, ss.language)
        if not out.startswith(("Gemini error", "Gemini is not")):
            r["narrative"] = out
    if r["narrative"]:
        r["narrative"] = st.text_area("Summary (edit freely)", r["narrative"], height=140)

    report = build_impact_report(ss.campaign, ss.contacts, ss.donations, current_week(), r)
    st.divider()
    st.markdown("### Your report")
    st.markdown(report)
    c1, c2, _ = st.columns([1, 1, 2])
    c1.download_button("⬇ Download report", report, "sunbeams_impact_report.md", "text/markdown", type="primary", width="stretch")
    c2.download_button("⬇ As text", report, "sunbeams_impact_report.txt", "text/plain", width="stretch")


def render():
    page_head("Journey", "Your six-week plan and your final impact report, built as you go.")
    t1, t2 = st.tabs(["📅 Weekly plan", "📄 Impact report"])
    with t1:
        _weekly()
    with t2:
        _report()
