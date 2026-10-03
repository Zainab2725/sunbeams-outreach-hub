# Sunbeams Outreach Hub

A Streamlit app for running a Sunbeams 100 for 100 Track 1 fundraising project. It's built around one daily question: **who do I talk to today?**

## What's inside (6 sections)

| Section | What it does |
|---|---|
| **Home** | Campaign progress, today's follow-ups (Message / Done / Snooze), the next best step, pipeline |
| **People** | Your supporter list. Filter by stage, search, and edit any cell in place |
| **Donations** | Record gifts, tick them as verified, download CSV |
| **Assistant** | Write First ask / Follow-up / Reminder / Thank-you messages in English or Roman Urdu, open in WhatsApp. AI coaching with Gemini (optional) |
| **Journey** | Auto-tracked six-week plan with checklists, plus a ready-made impact report |
| **Project** | Campaign details, **backup / restore**, sample data |

Works without an AI key (built-in message templates). Add one for personalised wording.

## Important

- This app does **not** process payments. It only records fundraising activity.
- Data lives in the browser session. **Use Project → Download backup regularly** and restore it from the same page.
- Gemini is told never to invent Sunbeams donation details. Add official channels from the handbook before sharing widely.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

Push to GitHub, create the app, and (optionally) add to Secrets:

```toml
GEMINI_API_KEY = "your-api-key"
```

## Structure

```
app.py          navigation + page routing
data.py         state, business logic, backup/restore
ui.py           shared components and dialogs
styles.py       theme / CSS
views/          home, people, donations, assistant, journey, project
services/       gemini.py, messages.py, reports.py
```
