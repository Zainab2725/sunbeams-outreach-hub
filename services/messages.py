"""Ready-made outreach messages so the app is useful even without an AI key."""

KINDS = ["First ask", "Follow-up", "Gentle reminder", "Thank you"]

_EN = {
    "First ask": (
        "Assalam o Alaikum {name}! I hope you're well. I'm working on a project with Sunbeams: {project}"
        "{goal}. I'd really value your support, even a small contribution helps. "
        "If you're interested, I'll share the details. No pressure at all, and thank you for reading!"
    ),
    "Follow-up": (
        "Hi {name}, hope you're doing well. Just following up on my message about {project}. "
        "Please let me know if you have any questions or if I can share more details. Thank you!"
    ),
    "Gentle reminder": (
        "Hi {name}! A gentle reminder about {project}. If it's still something you'd like to support, "
        "I'm happy to help with the next step. If not, no worries at all. Thank you for your time!"
    ),
    "Thank you": (
        "Dear {name}, thank you so much for your support towards {project}. "
        "Your contribution makes a real difference for the children we're helping. "
        "I'll keep you updated on the impact. JazakAllah!"
    ),
}

_UR = {
    "First ask": (
        "Assalam o Alaikum {name}! Umeed hai aap khairiyat se hon gay. Main Sunbeams ke saath ek project par kaam "
        "kar raha/rahi hoon: {project}{goal}. Aap ka chhota sa support bhi bohat maayne rakhta hai. "
        "Agar aap interested hon to main tafseelat share kar doon? Koi pressure nahi, aur parhne ka shukriya!"
    ),
    "Follow-up": (
        "Salam {name}, umeed hai sab khairiyat hai. Main {project} ke baare mein apne pichle message ka follow-up "
        "kar raha/rahi tha/thi. Agar koi sawal ho ya mazeed tafseelat chahiye hon to bata dein. Shukriya!"
    ),
    "Gentle reminder": (
        "Salam {name}! {project} ke baare mein ek chhoti si yaad-dehani. Agar aap ab bhi support karna chahte hon to "
        "main agle step mein madad kar doon ga/gi. Warna koi baat nahi. Waqt dene ka shukriya!"
    ),
    "Thank you": (
        "Mohtaram {name}, {project} ke liye aap ke support ka bohat shukriya. Aap ka hissa un bachon ke liye "
        "waqai farq laata hai jin ki hum madad kar rahe hain. Main aap ko impact ke baare mein update karta/karti rahoon ga/gi. JazakAllah!"
    ),
}


def template(kind, name, project, goal_amount=0, language="English"):
    goal = ""
    if goal_amount:
        goal = f" (we're aiming to raise Rs. {goal_amount:,.0f})" if language == "English" else f" (hamara maqsad Rs. {goal_amount:,.0f} jama karna hai)"
    text = (_EN if language == "English" else _UR)[kind]
    return text.format(name=name or "there", project=project or "our fundraising project", goal=goal)
