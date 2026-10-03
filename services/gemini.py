import os

import streamlit as st


def _api_key():
    try:
        key = st.secrets.get("GEMINI_API_KEY")
    except Exception:  # no secrets file locally
        key = None
    return key or os.getenv("GEMINI_API_KEY")


def is_configured():
    return bool(_api_key())


def generate_text(prompt: str, language: str = "English") -> str:
    key = _api_key()
    if not key:
        return "Gemini is not configured yet. Add GEMINI_API_KEY to Streamlit Secrets."
    try:
        from google import genai
        client = genai.Client(api_key=key)
        lang = ("Respond in natural English." if language == "English"
                else "Respond in natural Roman Urdu using Latin letters only.")
        system = (
            "You are the Sunbeams Outreach Hub assistant. Help an internship participant with fundraising outreach.\n"
            f"{lang}\n"
            "Do not invent official Sunbeams donation channels, account numbers, policies, rules, facts, or payment details.\n"
            "Keep suggestions practical, respectful, and non-pushy."
        )
        response = client.models.generate_content(model="gemini-2.5-flash", contents=system + "\n\n" + prompt)
        return response.text or "Gemini returned an empty answer. Please try again."
    except Exception as exc:  # noqa: BLE001
        return f"Gemini error: {exc}"
