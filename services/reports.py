from datetime import date


def build_impact_report(campaign, contacts, donations, week, reflections=None):
    reflections = reflections or {}
    raised = sum(float(d.get("amount") or 0) for d in donations)
    target = float(campaign.get("target") or 0)
    pct = (raised / target * 100) if target else 0
    verified = sum(1 for d in donations if d.get("verified"))
    reached = [c for c in contacts if c.get("status") != "To contact"]
    interested = [c for c in contacts if c.get("status") in ("Interested", "Committed", "Donated")]

    L = [
        f"# Individual Impact Summary: {campaign.get('project_name') or 'Untitled project'}", "",
        f"Prepared by: {campaign.get('intern_name') or '-'}  |  Date: {date.today():%d %b %Y}  |  Internship week {week} of 6", "",
        "## At a glance",
        f"- Project type: {campaign.get('project_type', '-')}",
        f"- Target audience: {campaign.get('target_audience') or '-'}",
        f"- Fundraising target: Rs. {target:,.0f}",
        f"- Amount raised: Rs. {raised:,.0f} ({pct:.1f}% of target)",
        f"- Donors: {len(donations)} ({verified} verified)",
        f"- People approached: {len(reached)} of {len(contacts)} on my list",
        f"- Showed interest or donated: {len(interested)}",
        f"- Expected students supported: {campaign.get('students_impacted', 0)}", "",
        "## About the project", campaign.get("description") or "_Add a project description in the Project tab._", "",
        "## Why it matters", campaign.get("why") or "_Add why this project matters in the Project tab._", "",
    ]
    if reflections.get("narrative"):
        L += ["## Summary", reflections["narrative"], ""]
    L += ["## Outreach activity"]
    L += [f"- {c['name']}: {c.get('status', '')}" + (f". {c['notes']}" if c.get("notes") else "") for c in contacts] or ["- No outreach recorded."]
    L += ["", "## Donations"]
    L += [f"- {d.get('date', '')}: {d.get('donor', '')}, Rs. {float(d.get('amount') or 0):,.0f} via {d.get('method', '')}"
          + (" (verified)" if d.get("verified") else " (not yet verified)") for d in donations] or ["- No donations recorded."]
    L += ["", "## Key learnings", reflections.get("learnings") or "_Write your learnings in the Journey tab._",
          "", "## Challenges and how I handled them", reflections.get("challenges") or "_Write your challenges in the Journey tab._",
          "", "## Evidence", reflections.get("evidence") or "_List your evidence (screenshots, receipts, photos) in the Journey tab._"]
    return "\n".join(L)
