import pandas as pd
import streamlit as st

from data import STAGES, find_contact, parse_date
from ui import add_person_dialog, empty_state, page_head


def render():
    page_head("People", "Everyone you’re asking for support. Edit a cell to update it; changes save instantly.")
    contacts = st.session_state.contacts

    if not contacts:
        empty_state("🤝", "No one on your list yet", "Add the people you can ask: family, friends, shops, schools.")
        st.write("")
        if st.button("➕ Add your first person", type="primary"):
            add_person_dialog()
        return

    counts = {s: sum(1 for c in contacts if c["status"] == s) for s in STAGES}
    labels = ["All · " + str(len(contacts))] + [f"{s} · {counts[s]}" for s in STAGES]
    top1, top2 = st.columns([4, 1], vertical_alignment="bottom")
    with top1:
        pick = st.pills("Stage", labels, default=labels[0], selection_mode="single", label_visibility="collapsed")
    with top2:
        if st.button("➕ Add person", width="stretch", type="primary"):
            add_person_dialog()
    search = st.text_input("Search", placeholder="🔍 Search by name, organization or notes", label_visibility="collapsed")

    stage = None if pick in (None, labels[0]) else STAGES[labels.index(pick) - 1]
    shown = [c for c in contacts
             if (stage is None or c["status"] == stage)
             and (not search or search.lower() in " ".join(str(c.get(k, "")) for k in ("name", "organization", "notes", "contact_type")).lower())]

    if not shown:
        st.info("No one matches this filter.")
        return

    df = pd.DataFrame([{
        "id": c["id"], "Name": c["name"], "Stage": c["status"],
        "Follow up on": parse_date(c.get("next_followup")), "Phone": c.get("contact", ""),
        "Type": c.get("contact_type", ""), "Notes": c.get("notes", ""),
    } for c in shown])

    edited = st.data_editor(
        df, hide_index=True, width="stretch", num_rows="fixed", key=f"people_{stage}_{search}",
        column_order=["Name", "Stage", "Follow up on", "Phone", "Notes"],
        column_config={
            "Name": st.column_config.TextColumn(required=True, width="medium"),
            "Stage": st.column_config.SelectboxColumn(options=STAGES, required=True, width="small"),
            "Follow up on": st.column_config.DateColumn(format="DD MMM", width="small"),
            "Phone": st.column_config.TextColumn(width="small"),
            "Notes": st.column_config.TextColumn(width="large"),
        },
        disabled=["id", "Type"],
    )

    for _, row in edited.iterrows():
        c = find_contact(row["id"])
        if not c:
            continue
        c["name"] = (row["Name"] or c["name"]).strip() or c["name"]
        c["status"] = row["Stage"] or c["status"]
        d = row["Follow up on"]
        c["next_followup"] = str(d) if pd.notna(d) and d else c.get("next_followup", "")
        c["contact"] = row["Phone"] or ""
        c["notes"] = row["Notes"] or ""

    with st.expander("Remove people"):
        gone = st.multiselect("Select people to remove", [c["id"] for c in contacts],
                              format_func=lambda i: find_contact(i)["name"], label_visibility="collapsed")
        if gone and st.button(f"Remove {len(gone)} selected", type="primary"):
            st.session_state.contacts = [c for c in contacts if c["id"] not in gone]
            st.rerun()
