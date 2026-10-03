import streamlit as st

from data import init_state
from styles import inject_css
from ui import PAGES, html
from views import assistant, donations, home, journey, people, project

st.set_page_config(page_title="Sunbeams Outreach Hub", page_icon="☀️", layout="centered", initial_sidebar_state="collapsed")
inject_css()
init_state()

html("""<div class="brandbar"><div class="logo">☀️</div>
<div><div class="brandname">Sunbeams Outreach Hub</div><div class="brandsub">100 for 100 · Track 1</div></div></div>""")

ICONS = {"Home": "🏠 Home", "People": "👥 People", "Donations": "💚 Donations",
         "Assistant": "✨ Assistant", "Journey": "🗺 Journey", "Project": "⚙️ Project"}
st.segmented_control("Navigate", PAGES, key="page", format_func=ICONS.get, label_visibility="collapsed")
page = st.session_state.page if st.session_state.page in PAGES else "Home"  # control can be un-selected

{"Home": home, "People": people, "Donations": donations,
 "Assistant": assistant, "Journey": journey, "Project": project}[page].render()
