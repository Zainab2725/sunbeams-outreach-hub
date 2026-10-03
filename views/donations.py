import pandas as pd
import streamlit as st

from data import METHODS, money, parse_date, progress, raised, target
from ui import donation_dialog, empty_state, html, page_head, stat


def render():
    page_head("Donations", "Every rupee raised, in one place. Mark each one verified once you’ve confirmed it arrived.")
    donations = st.session_state.donations
    total, goal = raised(), target()

    a, b, c, d = st.columns(4)
    with a: stat("Raised", money(total), "good" if total else "")
    with b: stat("Target", money(goal))
    with c: stat("Remaining", money(max(goal - total, 0)))
    with d: stat("Average gift", money(total / len(donations)) if donations else "–")
    st.write("")
    if goal:
        st.progress(progress(), text=f"{progress() * 100:.0f}% of target")

    if st.button("💚 Record donation", type="primary"):
        donation_dialog()

    if not donations:
        st.write("")
        empty_state("💚", "No donations yet", "When someone donates, record it here and it updates your progress everywhere.")
        return

    unverified = [d for d in donations if not d.get("verified")]
    if unverified:
        html(f'<div class="hint"><b>{len(unverified)} donation{"s" if len(unverified) != 1 else ""} not verified yet.</b> '
             'Tick “Verified” once you’ve confirmed it was received. You’ll need this for your report.</div>')
        st.write("")

    df = pd.DataFrame([{
        "id": d["id"], "Date": parse_date(d.get("date")), "Donor": d.get("donor", ""), "Amount": float(d.get("amount") or 0),
        "Method": d.get("method", ""), "Reference": d.get("reference", ""), "Verified": bool(d.get("verified")),
    } for d in sorted(donations, key=lambda x: str(x.get("date", "")), reverse=True)])

    edited = st.data_editor(
        df, hide_index=True, width="stretch", num_rows="fixed", key="donations_table",
        column_order=["Date", "Donor", "Amount", "Method", "Reference", "Verified"],
        column_config={
            "Date": st.column_config.DateColumn(format="DD MMM YYYY"),
            "Amount": st.column_config.NumberColumn(format="Rs. %d", min_value=1),
            "Method": st.column_config.SelectboxColumn(options=METHODS),
            "Verified": st.column_config.CheckboxColumn(),
        },
    )
    by_id = {d["id"]: d for d in donations}
    for _, row in edited.iterrows():
        d = by_id.get(row["id"])
        if d:
            d["verified"] = bool(row["Verified"])
            d["amount"] = float(row["Amount"] or d["amount"])
            d["donor"] = row["Donor"] or d["donor"]
            d["method"] = row["Method"] or d["method"]
            d["reference"] = row["Reference"] or ""
            if pd.notna(row["Date"]) and row["Date"]:
                d["date"] = str(row["Date"])

    col1, col2 = st.columns([1, 3])
    col1.download_button("⬇ Download CSV", df.drop(columns="id").to_csv(index=False), "donations.csv", "text/csv")
    with st.expander("Remove a donation"):
        gone = st.multiselect("Select donations to remove", [d["id"] for d in donations], label_visibility="collapsed",
                              format_func=lambda i: f"{by_id[i]['donor']} · {money(by_id[i]['amount'])} · {by_id[i]['date']}")
        if gone and st.button(f"Remove {len(gone)} selected", type="primary"):
            st.session_state.donations = [d for d in donations if d["id"] not in gone]
            st.rerun()
