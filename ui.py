"""Shared UI helpers and dialogs."""
import html as _html
from datetime import date

import streamlit as st

from data import (CONTACT_TYPES, METHODS, STAGES, add_contact, add_donation, find_contact, money, parse_date)

PAGES = ["Home", "People", "Donations", "Assistant", "Journey", "Project"]


def esc(value):
    return _html.escape(str(value if value is not None else ""))


def html(markup):
    """Render HTML safely: strip indentation so markdown never turns it into a code block."""
    st.markdown("\n".join(line.strip() for line in markup.strip().splitlines()), unsafe_allow_html=True)


def go(page, **state):
    """Button callback: change page (and optionally set other session values)."""
    for k, v in state.items():
        st.session_state[k] = v
    st.session_state.page = page


def page_head(title, subtitle):
    html(f'<div class="pagehead"><h2>{esc(title)}</h2><p>{esc(subtitle)}</p></div>')


def stat(label, value, tone=""):
    html(f'<div class="stat {tone}"><div class="n">{esc(value)}</div><div class="l">{esc(label)}</div></div>')


def badge(status):
    return f'<span class="badge s-{status.lower().replace(" ", "-")}">{esc(status)}</span>'


def due_badge(contact):
    d = parse_date(contact.get("next_followup"))
    if not d:
        return ""
    delta = (date.today() - d).days
    if delta > 0:
        return f'<span class="badge late">{delta} day{"s" if delta != 1 else ""} overdue</span>'
    if delta == 0:
        return '<span class="badge today">Due today</span>'
    return ""


def empty_state(icon, title, text):
    html(f'<div class="empty"><div class="big">{icon}</div><h3>{esc(title)}</h3><p>{esc(text)}</p></div>')


def whatsapp_number(raw):
    digits = "".join(ch for ch in str(raw or "") if ch.isdigit())
    if len(digits) == 11 and digits.startswith("0"):   # Pakistani local format 03xx...
        digits = "92" + digits[1:]
    return digits if 10 <= len(digits) <= 15 else ""


# ---------------------------------------------------------------- dialogs

@st.dialog("Add a person")
def add_person_dialog():
    with st.form("add_person", clear_on_submit=True, border=False):
        name = st.text_input("Name *", placeholder="e.g. Ayesha Khan")
        c1, c2 = st.columns(2)
        ctype = c1.selectbox("Who are they?", CONTACT_TYPES)
        phone = c2.text_input("Phone (WhatsApp)", placeholder="03xx xxxxxxx")
        org = st.text_input("Organization (optional)")
        c3, c4 = st.columns(2)
        status = c3.selectbox("Where are you with them?", STAGES[:4])
        when = c4.date_input("Reach out / follow up on", value=date.today())
        notes = st.text_area("Notes", height=80, placeholder="What could they support? Anything to remember?")
        if st.form_submit_button("Add person", type="primary", width="stretch"):
            if not name.strip():
                st.error("Please enter a name.")
            else:
                add_contact(name, ctype, phone, org, status, when, notes)
                st.toast(f"Added {name.strip()}")
                st.rerun()


@st.dialog("Record a donation")
def donation_dialog(contact_id=None):
    contacts = st.session_state.contacts
    options = [c["id"] for c in contacts] + ["__new__"]
    labels = {c["id"]: c["name"] for c in contacts}
    labels["__new__"] = "➕ Someone new"
    default = options.index(contact_id) if contact_id in options else (len(options) - 1 if not contacts else 0)

    who = st.selectbox("Donor", options, index=default, format_func=lambda x: labels[x])
    with st.form("record_donation", clear_on_submit=True, border=False):
        new_name = st.text_input("Donor name *") if who == "__new__" else ""
        c1, c2 = st.columns(2)
        amount = c1.number_input("Amount (Rs.) *", min_value=0.0, step=500.0)
        when = c2.date_input("Date received", value=date.today())
        c3, c4 = st.columns(2)
        method = c3.selectbox("Method", METHODS)
        reference = c4.text_input("Reference / receipt no.")
        purpose = st.text_input("Purpose (optional)")
        verified = st.checkbox("I have verified this donation was received")
        if st.form_submit_button("Save donation", type="primary", width="stretch"):
            name = new_name if who == "__new__" else labels[who]
            if not name.strip():
                st.error("Please enter the donor's name.")
            elif amount <= 0:
                st.error("Amount must be more than zero.")
            else:
                cid = who
                if who == "__new__":
                    cid = add_contact(name, "Other", status="Donated")
                add_donation(cid, name, amount, when, method, purpose, reference, verified)
                st.toast(f"Recorded {money(amount)} from {name.strip()} 🎉")
                st.rerun()
