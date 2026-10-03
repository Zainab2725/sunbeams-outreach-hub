import streamlit as st

from data import (ACTIVE, STAGES, current_week, days_left, due_followups, find_contact, has_campaign, load_demo, mark_contacted,
                  money, progress, raised, snooze, stage_counts, target)
from ui import add_person_dialog, badge, donation_dialog, due_badge, empty_state, esc, go, html, stat, whatsapp_number


def _hero():
    c = st.session_state.campaign
    pct = progress() * 100
    left = days_left()
    meta = f"Week {current_week()} of 6" + (f" · {left} days left" if left is not None and left >= 0 else "")
    html(f"""
    <div class="hero">
      <div class="hero-top"><div><div class="eyebrow">{esc(meta)}</div><h1>{esc(c['project_name'])}</h1></div>
      <div class="hero-pct">{pct:.0f}%</div></div>
      <div class="bar"><div style="width:{pct:.1f}%"></div></div>
      <div class="hero-nums"><span><b>{money(raised())}</b> raised of {money(target())}</span>
      <span>{money(max(target() - raised(), 0))} to go</span></div>
    </div>""")


def _next_step(due):
    contacts = st.session_state.contacts
    counts = stage_counts()
    if not contacts:
        return "Add the first 10 people you can ask", "Start with family and friends. People who already know you are the easiest first conversations."
    if due:
        n = len(due)
        return f"Follow up with {n} {'person' if n == 1 else 'people'} today", "Tap “Message” below. A short, friendly nudge works best."
    waiting = [c for c in contacts if c["status"] == "Committed"]
    if waiting:
        return f"Help {waiting[0]['name']} complete their donation", "They said yes. Make it easy: share the details and confirm once received."
    todo = [c for c in contacts if c["status"] == "To contact"]
    if todo:
        return f"Reach out to {todo[0]['name']}", "Send your first message from the Assistant tab."
    donors, goal_left = counts["Donated"], max(target() - raised(), 0)
    if goal_left and donors:
        avg = raised() / donors
        return f"You need about {int(goal_left / avg) + 1} more donors", f"At an average gift of {money(avg)}, add more people to your list to get there."
    return "Add more people to your list", "More conversations lead to more donors."


def _today(due):
    st.markdown("### Today")
    if not due:
        html('<div class="hint"><b>You’re all caught up 🎉</b><br>Nobody needs a follow-up right now. Add more people or check People for the full list.</div>')
        return
    for c in due[:5]:
        with st.container(border=True):
            left, right = st.columns([3, 2], vertical_alignment="center")
            with left:
                sub = c.get("organization") or c.get("contact_type", "")
                html(f'<div class="person"><div><div class="nm">{esc(c["name"])}</div>'
                     f'<div class="sub">{esc(sub)}</div></div></div>')
                html(f'{badge(c["status"])} {due_badge(c)}')
            with right:
                b1, b2 = st.columns(2)
                b1.button("Message", key=f"h_msg_{c['id']}", width="stretch", type="primary",
                          on_click=go, args=("Assistant",), kwargs={"coach_person": c["id"]})
                b2.button("Done", key=f"h_done_{c['id']}", width="stretch",
                          help="Mark as contacted and remind me in 3 days", on_click=mark_contacted, args=(c["id"],))
                st.button("Snooze 2 days", key=f"h_snz_{c['id']}", width="stretch", type="tertiary",
                          on_click=snooze, args=(c["id"],))
    if len(due) > 5:
        st.caption(f"+ {len(due) - 5} more in People")


def _pipeline():
    st.markdown("### Pipeline")
    counts = stage_counts()
    biggest = max(counts.values()) or 1
    rows = "".join(
        f'<div class="pipe-row s-{s.lower().replace(" ", "-")}"><span>{s}</span>'
        f'<div class="t"><div style="width:{counts[s] / biggest * 100:.0f}%"></div></div><span class="c">{counts[s]}</span></div>'
        for s in STAGES)
    html(f'<div class="pipe">{rows}</div>')
    st.button("Open People", key="home_people", on_click=go, args=("People",), type="tertiary")


def render():
    if not has_campaign():
        empty_state("☀️", "Let’s set up your campaign",
                    "Give your project a name and a target. It takes a minute, and everything else builds on it.")
        st.write("")
        with st.form("quick_setup"):
            name = st.text_input("Project name", placeholder="e.g. Stationery Drive for 50 Students")
            c1, c2 = st.columns(2)
            goal = c1.number_input("Fundraising target (Rs.)", min_value=0.0, step=1000.0, value=50000.0)
            kids = c2.number_input("Students you expect to help", min_value=0, step=5, value=0)
            if st.form_submit_button("Start campaign", type="primary", width="stretch"):
                if not name.strip():
                    st.error("Please give your project a name.")
                else:
                    st.session_state.campaign.update(project_name=name.strip(), target=goal, students_impacted=kids)
                    st.rerun()
        st.button("Or explore with sample data", on_click=load_demo, type="tertiary")
        return

    _hero()

    due = due_followups()
    contacts = st.session_state.contacts
    donors = len(st.session_state.donations)
    a, b, c, d = st.columns(4)
    with a: stat("People on list", len(contacts))
    with b: stat("Donors", donors, "good" if donors else "")
    with c: stat("Need follow-up", len(due), "warn" if due else "")
    with d: stat("Students to help", st.session_state.campaign.get("students_impacted", 0))
    st.write("")

    title, why = _next_step(due)
    html(f'<div class="hint"><b>Next best step: {esc(title)}</b><br>{esc(why)}</div>')
    st.write("")

    q1, q2, _ = st.columns([1, 1, 2])
    if q1.button("➕ Add person", width="stretch", type="primary"):
        add_person_dialog()
    if q2.button("💚 Record donation", width="stretch"):
        donation_dialog()
    st.write("")

    left, right = st.columns([1.6, 1], gap="large")
    with left:
        _today(due)
    with right:
        _pipeline()
