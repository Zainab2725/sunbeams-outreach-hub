from urllib.parse import quote

import streamlit as st

from data import find_contact, mark_contacted, money, raised, stage_counts, target
from services import messages
from services.gemini import generate_text, is_configured
from ui import page_head, whatsapp_number


def _context():
    c = st.session_state.campaign
    counts = stage_counts()
    return (f"Campaign: {c.get('project_name') or 'not set'} ({c.get('project_type')})\n"
            f"Target: {money(target())}. Raised: {money(raised())}. Donors: {len(st.session_state.donations)}.\n"
            f"People: {len(st.session_state.contacts)} (" + ", ".join(f"{k}: {v}" for k, v in counts.items() if v) + ").\n"
            f"Audience: {c.get('target_audience') or 'not set'}.")


def _draft_tab(lang):
    contacts = st.session_state.contacts
    ids = [None] + [c["id"] for c in contacts]
    names = {None: "Someone general"} | {c["id"]: c["name"] for c in contacts}
    c1, c2 = st.columns(2)
    who = c1.selectbox("Who is it for?", ids, format_func=lambda i: names[i], key="coach_person")
    person = find_contact(who) if who else None
    default_kind = {"Donated": "Thank you", "To contact": "First ask"}.get(person["status"] if person else "", "Follow-up")
    kind = c2.selectbox("What kind of message?", messages.KINDS, index=messages.KINDS.index(default_kind),
                        key=f"kind_{who}")

    use_ai = is_configured()
    label = "✨ Write with Gemini" if use_ai else "Write message"
    if st.button(label, type="primary"):
        project = st.session_state.campaign.get("project_name", "")
        base = messages.template(kind, person["name"] if person else "", project, target(), lang)
        text = base
        if use_ai:
            prompt = (f"Rewrite this {kind.lower()} message so it sounds warm, personal and short (under 70 words), keeping its meaning. "
                      f"Recipient: {names[who]}"
                      + (f" ({person.get('contact_type')}). Notes about them: {person.get('notes') or 'none'}" if person else "")
                      + f"\nDo not add payment details.\n\n{base}\n\nReturn only the message.")
            with st.spinner("Writing…"):
                out = generate_text(prompt, lang)
            text = base if out.startswith(("Gemini error", "Gemini is not")) else out
            if text is base:
                st.warning("Gemini was unavailable, so here is the built-in version.")
        st.session_state.draft_text = text

    if st.session_state.get("draft_text"):
        text = st.text_area("Your message (edit freely)", key="draft_text", height=170)
        b1, b2, _ = st.columns([1.3, 1.3, 2])
        num = whatsapp_number(person.get("contact")) if person else ""
        if person and num:
            b1.link_button("Open WhatsApp", f"https://wa.me/{num}?text={quote(text)}", width="stretch")
        else:
            b1.link_button("Open WhatsApp", f"https://wa.me/?text={quote(text)}", width="stretch")
        if person:
            b2.button("Mark as sent", width="stretch", help="Sets status to Contacted and reminds you in 3 days",
                      on_click=mark_contacted, args=(person["id"],))
        st.caption("Tip: tap the copy icon on the box below to paste anywhere else.")
        st.code(text, language=None, wrap_lines=True)
    if not use_ai:
        st.caption("Messages use built-in templates. Add GEMINI_API_KEY in Streamlit Secrets for personalised AI wording.")


def _advice_tab(lang):
    if not is_configured():
        st.info("The AI coach needs a Gemini API key. Add `GEMINI_API_KEY` in Streamlit Secrets (see README). "
                "Message drafting still works without it.")
        return
    quick = {"Plan my next 3 actions": "Plan my next three outreach actions based on my current campaign.",
             "Improve my donor strategy": "Review my campaign position and suggest practical ways to improve donor outreach.",
             "Plan this week": "Create a focused action plan for this week.",
             "Handle “no response”": "Give me tips for people who haven’t replied to my messages."}
    cols = st.columns(len(quick))
    for col, (label, text) in zip(cols, quick.items()):
        if col.button(label, width="stretch"):
            st.session_state.advice_q = text
    q = st.text_area("Ask anything about your campaign", key="advice_q", height=100,
                     placeholder="e.g. Maine 8 logon ko contact kiya, 2 interested hain. Ab kya karun?")
    if st.button("Get advice", type="primary"):
        if not q.strip():
            st.warning("Type a question or pick a quick option above.")
        else:
            with st.spinner("Thinking…"):
                st.session_state.advice_out = generate_text(_context() + "\n\nRequest:\n" + q, lang)
    if st.session_state.get("advice_out"):
        st.markdown(st.session_state.advice_out)


def render():
    page_head("Assistant", "Draft messages in seconds and get coaching on what to do next.")
    st.session_state.language = st.radio("Language", ["English", "Roman Urdu"], horizontal=True,
                                         index=["English", "Roman Urdu"].index(st.session_state.language),
                                         label_visibility="collapsed")
    lang = st.session_state.language
    t1, t2 = st.tabs(["✉️ Write a message", "💡 Ask for advice"])
    with t1:
        _draft_tab(lang)
    with t2:
        _advice_tab(lang)
