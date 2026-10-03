"""State, persistence and small business-logic helpers for the Outreach Hub."""
import json
import uuid
from datetime import date, datetime, timedelta

import streamlit as st

STAGES = ["To contact", "Contacted", "Interested", "Committed", "Donated", "Closed"]
ACTIVE = ["To contact", "Contacted", "Interested", "Committed"]

# Old versions of the app used these labels
LEGACY_STATUS = {
    "Not Contacted": "To contact",
    "Contacted": "Contacted",
    "Interested": "Interested",
    "Follow-up Needed": "Contacted",
    "Committed": "Committed",
    "Donated": "Donated",
    "Not Interested": "Closed",
    "No Response": "Closed",
}

CONTACT_TYPES = [
    "Family", "Friend", "Personal network", "Small business",
    "Organization", "School/community contact", "Other",
]
PROJECT_TYPES = [
    "Stationery / Book Drive", "First Aid / Sports Kit Drive",
    "Sponsor a Child", "Water Filter", "Other",
]
METHODS = ["Bank transfer", "JazzCash", "Easypaisa", "PayPal", "GlobalGiving", "Zelle", "Cash", "Other"]

MILESTONES = {
    1: ["Define project and target", "Identify your audience", "Add your first 10 people", "Send first messages"],
    2: ["Take first significant action", "Record every conversation", "Keep evidence (screenshots, receipts)"],
    3: ["Review progress against target", "Adjust strategy", "Reach out to new people"],
    4: ["Core fundraising push", "Follow up with everyone interested", "Verify received donations"],
    5: ["Wrap up the project", "Thank every donor", "Collect impact information"],
    6: ["Write final impact summary", "Prepare final presentation", "Back up all your records"],
}

BLANK_CAMPAIGN = {
    "intern_name": "", "project_name": "", "project_type": PROJECT_TYPES[0],
    "target_audience": "", "target": 0.0, "students_impacted": 0,
    "description": "", "why": "", "start": "", "end": "",
}
BLANK_REFLECTIONS = {"learnings": "", "challenges": "", "evidence": "", "narrative": ""}


# ---------------------------------------------------------------- state

def init_state():
    ss = st.session_state
    ss.setdefault("campaign", dict(BLANK_CAMPAIGN))
    ss.setdefault("contacts", [])
    ss.setdefault("donations", [])
    ss.setdefault("checks", {})
    ss.setdefault("reflections", dict(BLANK_REFLECTIONS))
    ss.setdefault("language", "English")
    ss.setdefault("manual_week", 1)
    ss.setdefault("page", "Home")


def new_id():
    return uuid.uuid4().hex[:10]


def parse_date(value):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value)[:10])
    except (ValueError, TypeError):
        return None


def money(value):
    try:
        return f"Rs. {float(value or 0):,.0f}"
    except (TypeError, ValueError):
        return "Rs. 0"


# ---------------------------------------------------------------- numbers

def raised():
    return sum(float(d.get("amount") or 0) for d in st.session_state.donations)


def target():
    return float(st.session_state.campaign.get("target") or 0)


def progress():
    t = target()
    return min(raised() / t, 1.0) if t else 0.0


def has_campaign():
    return bool(st.session_state.campaign.get("project_name"))


def stage_counts():
    counts = {s: 0 for s in STAGES}
    for c in st.session_state.contacts:
        counts[c.get("status", "To contact")] = counts.get(c.get("status", "To contact"), 0) + 1
    return counts


def current_week():
    start = parse_date(st.session_state.campaign.get("start"))
    if start:
        return max(1, min(6, (date.today() - start).days // 7 + 1))
    return st.session_state.manual_week


def days_left():
    end = parse_date(st.session_state.campaign.get("end"))
    if not end:
        return None
    return (end - date.today()).days


def due_followups():
    """People who need action today or are overdue, most overdue first."""
    today = date.today()
    out = []
    for c in st.session_state.contacts:
        if c.get("status") not in ACTIVE:
            continue
        due = parse_date(c.get("next_followup"))
        if due and due <= today:
            out.append((due, c))
    out.sort(key=lambda x: x[0])
    return [c for _, c in out]


def find_contact(contact_id):
    for c in st.session_state.contacts:
        if c.get("id") == contact_id:
            return c
    return None


# ---------------------------------------------------------------- mutations

def add_contact(name, contact_type="Friend", phone="", organization="", status="To contact",
                followup=None, notes=""):
    st.session_state.contacts.append({
        "id": new_id(), "name": name.strip(), "contact_type": contact_type,
        "contact": phone.strip(), "organization": organization.strip(),
        "status": status, "last_contacted": "",
        "next_followup": str(followup or date.today()), "notes": notes.strip(),
    })
    return st.session_state.contacts[-1]["id"]


def add_donation(contact_id, donor, amount, when, method, purpose="", reference="", verified=False):
    st.session_state.donations.append({
        "id": new_id(), "contact_id": contact_id, "donor": donor.strip(),
        "amount": float(amount), "date": str(when), "method": method,
        "purpose": purpose.strip(), "reference": reference.strip(), "verified": bool(verified),
    })
    c = find_contact(contact_id)
    if c:
        c["status"] = "Donated"
        c["last_contacted"] = str(date.today())


def mark_contacted(contact_id, days=3):
    c = find_contact(contact_id)
    if not c:
        return
    if c["status"] == "To contact":
        c["status"] = "Contacted"
    c["last_contacted"] = str(date.today())
    c["next_followup"] = str(date.today() + timedelta(days=days))


def snooze(contact_id, days=2):
    c = find_contact(contact_id)
    if c:
        c["next_followup"] = str(date.today() + timedelta(days=days))


# ---------------------------------------------------------------- backup

def snapshot():
    ss = st.session_state
    return {
        "app": "sunbeams-outreach-hub", "version": 2, "saved": datetime.now().isoformat(timespec="seconds"),
        "campaign": ss.campaign, "contacts": ss.contacts, "donations": ss.donations,
        "checks": ss.checks, "reflections": ss.reflections,
        "manual_week": ss.manual_week, "language": ss.language,
    }


def snapshot_json():
    return json.dumps(snapshot(), indent=2, ensure_ascii=False)


def restore(raw):
    """Load a backup (also understands backups from the old version). Returns an error string or None."""
    try:
        data = json.loads(raw)
        if not isinstance(data, dict) or "campaign" not in data:
            return "This does not look like a Sunbeams Outreach Hub backup."
        contacts = []
        for c in data.get("contacts", []):
            c = dict(c)
            c.setdefault("id", new_id())
            c["status"] = LEGACY_STATUS.get(c.get("status"), c.get("status") if c.get("status") in STAGES else "To contact")
            c.setdefault("next_followup", str(date.today()))
            contacts.append(c)
        by_name = {c["name"].strip().lower(): c["id"] for c in contacts}
        donations = []
        for d in data.get("donations", []):
            d = dict(d)
            d.setdefault("id", new_id())
            d.setdefault("contact_id", by_name.get(str(d.get("donor", "")).strip().lower()))
            donations.append(d)
        ss = st.session_state
        ss.campaign = {**BLANK_CAMPAIGN, **data["campaign"]}
        ss.contacts, ss.donations = contacts, donations
        ss.checks = data.get("checks", {})
        ss.reflections = {**BLANK_REFLECTIONS, **data.get("reflections", {})}
        ss.manual_week = int(data.get("manual_week", data.get("week", 1)) or 1)
        ss.language = data.get("language", "English")
        return None
    except Exception as exc:  # noqa: BLE001
        return f"Could not read that file: {exc}"


def load_demo():
    ss = st.session_state
    today = date.today()
    ss.campaign = {
        **BLANK_CAMPAIGN, "intern_name": "Sample Intern", "project_name": "Stationery Drive for 50 Students",
        "project_type": PROJECT_TYPES[0], "target_audience": "Family, friends and local businesses",
        "target": 50000.0, "students_impacted": 50,
        "description": "Collect funds to buy notebooks, pens and geometry boxes for 50 children.",
        "why": "Many students start the school year without basic supplies.",
        "start": str(today - timedelta(days=9)), "end": str(today + timedelta(days=33)),
    }
    ss.contacts, ss.donations = [], []
    rows = [
        ("Ayesha Khan", "Family", "03001234567", "Donated", 0), ("Bilal Ahmed", "Friend", "03211234567", "Committed", -1),
        ("Sara Malik", "Friend", "03331234567", "Interested", -2), ("Crescent Traders", "Small business", "", "Contacted", 0),
        ("Usman Ali", "Personal network", "03451234567", "Donated", 2), ("Hina Raza", "Family", "03121234567", "To contact", 0),
        ("Dr. Farooq", "School/community contact", "", "Closed", 5),
    ]
    ids = {}
    for name, typ, phone, status, offset in rows:
        ids[name] = add_contact(name, typ, phone, status=status, followup=today + timedelta(days=offset))
    add_donation(ids["Ayesha Khan"], "Ayesha Khan", 15000, today - timedelta(days=3), "JazzCash", verified=True)
    add_donation(ids["Usman Ali"], "Usman Ali", 5000, today - timedelta(days=1), "Bank transfer")
    ss.checks = {"w1_0": True, "w1_1": True, "w1_2": True}
    ss.reflections = dict(BLANK_REFLECTIONS)
