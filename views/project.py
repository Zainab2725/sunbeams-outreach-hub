from datetime import date, timedelta

import streamlit as st

from data import PROJECT_TYPES, load_demo, parse_date, restore, snapshot_json
from ui import page_head


def render():
    page_head("Project", "Your campaign details and your data backup.")
    c = st.session_state.campaign

    with st.form("project_form", border=True):
        st.markdown("### Campaign details")
        a, b = st.columns(2)
        intern = a.text_input("Your name", c.get("intern_name", ""))
        name = b.text_input("Project name *", c.get("project_name", ""))
        a, b = st.columns(2)
        ptype = a.selectbox("Project type", PROJECT_TYPES, index=PROJECT_TYPES.index(c["project_type"]) if c.get("project_type") in PROJECT_TYPES else 0)
        audience = b.text_input("Target audience", c.get("target_audience", ""))
        a, b = st.columns(2)
        goal = a.number_input("Fundraising target (Rs.)", min_value=0.0, step=1000.0, value=float(c.get("target") or 0))
        kids = b.number_input("Students you expect to help", min_value=0, step=5, value=int(c.get("students_impacted") or 0))
        a, b = st.columns(2)
        start = a.date_input("Start date", value=parse_date(c.get("start")) or date.today())
        end = b.date_input("End date", value=parse_date(c.get("end")) or date.today() + timedelta(weeks=6))
        desc = st.text_area("What is the project?", c.get("description", ""), height=90)
        why = st.text_area("Why does it matter?", c.get("why", ""), height=90)
        if st.form_submit_button("Save", type="primary", width="stretch"):
            if not name.strip():
                st.error("Project name is required.")
            elif end < start:
                st.error("End date must be after the start date.")
            else:
                st.session_state.campaign = {
                    "intern_name": intern, "project_name": name.strip(), "project_type": ptype,
                    "target_audience": audience, "target": goal, "students_impacted": kids,
                    "start": str(start), "end": str(end), "description": desc, "why": why}
                st.toast("Saved ✓")
                st.rerun()

    st.markdown("### Backup")
    st.warning("Your data lives in this browser session. **Download a backup regularly**: if you close the tab or the app restarts, "
               "unsaved data is lost.")
    d1, d2 = st.columns(2)
    d1.download_button("⬇ Download backup", snapshot_json(), f"sunbeams-backup-{date.today()}.json", "application/json",
                       type="primary", width="stretch")
    up = d2.file_uploader("Restore from backup", type="json", label_visibility="collapsed")
    if up is not None and st.session_state.get("restored_name") != up.file_id:
        err = restore(up.getvalue().decode("utf-8", "ignore"))
        if err:
            st.error(err)
        else:
            st.session_state.restored_name = up.file_id
            st.toast("Backup restored ✓")
            st.rerun()

    with st.expander("More"):
        st.button("Load sample data", on_click=load_demo)
        if st.checkbox("I understand this deletes everything"):
            if st.button("Erase all data", type="primary"):
                for k in ("campaign", "contacts", "donations", "checks", "reflections", "draft_text", "advice_out", "restored_name"):
                    st.session_state.pop(k, None)
                st.rerun()
