"""
streamlit_app.py
================
Dustin - Galgotias University AI Chatbot
Fixed: Raw HTML visibility bug, Super Large DUSTIN Title, No Extra Subtitles
"""

import streamlit as st
import sys, os, re, base64

sys.path.insert(0, os.path.dirname(__file__))
from chatbot import get_response

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dustin – Galgotias University",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Load Logo as Base64 ──────────────────────────────────────────────────────
def get_logo_base64():
    logo_paths = [
        os.path.join(os.path.dirname(__file__), 'static', 'galgotias_logo.png'),
        'static/galgotias_logo.png',
    ]
    for path in logo_paths:
        if os.path.exists(path):
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode()
    return None

logo_b64 = get_logo_base64()

logo_html = f'<div style="text-align:center; margin-top:-25px; margin-bottom:30px;"><img src="data:image/png;base64,{logo_b64}" style="height:180px; display:inline-block;" /></div>'
# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

  html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
  }

  #MainMenu, footer { visibility: hidden; }

  /* ── Bot message ── */
  .bot-msg {
    background: #ffffff;
    color: #1a1a1a;
    padding: 18px 22px;
    border-radius: 18px 18px 18px 4px;
    margin: 10px 0;
    margin-right: 12%;
    border: 1.5px solid #e0e0e0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    font-size: 1.05rem;
    line-height: 1.85;
  }

  /* ── User message ── */
  .user-msg {
    background: linear-gradient(135deg, #a52a2a, #c0392b);
    color: white;
    padding: 16px 22px;
    border-radius: 18px 18px 4px 18px;
    margin: 10px 0;
    margin-left: 12%;
    box-shadow: 0 3px 14px rgba(165, 42, 42, 0.35);
    font-size: 1.05rem;
    line-height: 1.7;
  }

  /* ── Labels ── */
  .msg-label {
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.6px;
    text-transform: uppercase;
    color: #666;
    margin-bottom: 3px;
    display: flex;
    align-items: center;
    gap: 5px;
  }
  .msg-label.user-label { justify-content: flex-end; color: #a52a2a; }

  /* ── Numbered list inside bot msg ── */
  .bot-msg ol {
    padding-left: 22px;
    margin: 8px 0;
  }
  .bot-msg ol li {
    font-size: 1.05rem;
    margin-bottom: 6px;
    line-height: 1.8;
  }

  /* ── Status badge ── */
  .status-badge {
    display: inline-block;
    background: #dcfce7;
    color: #166534;
    padding: 5px 14px;
    border-radius: 999px;
    font-size: 0.82rem;
    font-weight: 600;
    margin-top: 8px;
  }

  /* ── Input box bigger ── */
  .stTextInput input {
    font-size: 1.05rem !important;
    padding: 14px 16px !important;
    border-radius: 12px !important;
  }

  /* ── Send button ── */
  .stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #a52a2a, #c0392b) !important;
    border: none !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    border-radius: 12px !important;
    height: 52px !important;
  }
</style>
""", unsafe_allow_html=True)

# ─── Format bot response (bold + numbered list) ───────────────────────────────
def format_bot_message(text: str) -> str:
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    lines = text.split('\n')
    result = []
    in_list = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith('•') or stripped.startswith('-'):
            if not in_list:
                result.append('<ol>')
                in_list = True
            item = re.sub(r'^[•\-]\s*', '', stripped)
            result.append(f'<li>{item}</li>')
        else:
            if in_list:
                result.append('</ol>')
                in_list = False
            if stripped:
                result.append(f'{line}<br/>')
            else:
                result.append('<br/>')

    if in_list:
        result.append('</ol>')

    return ''.join(result)

# ─── Welcome message (numbered list) ─────────────────────────────────────────
WELCOME_TEXT = (
    "Hello! 👋 Welcome to <strong>Galgotias University!</strong><br/><br/>"
    "I'm <strong>Dustin</strong>, your AI assistant. I can help you with:<br/><br/>"
    "<ol>"
    "<li>🎓 Admissions &amp; Eligibility</li>"
    "<li>📚 Courses &amp; Programs</li>"
    "<li>💰 Fees &amp; Scholarships</li>"
    "<li>🏠 Hostel Facilities</li>"
    "<li>🏢 Placement Statistics</li>"
    "<li>📅 Exam Schedule</li>"
    "<li>👨‍🏫 Faculty Information</li>"
    "<li>📞 Contact Details</li>"
    "</ol><br/>"
    "What would you like to know?"
)

# ─── Session State Init ───────────────────────────────────────────────────────
if 'messages' not in st.session_state:
    st.session_state.messages = [{'role': 'bot', 'content': WELCOME_TEXT, 'preformatted': True}]

if 'last_input' not in st.session_state:
    st.session_state.last_input = ''

# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    sidebar_logo = f'<div style="text-align:center; padding:10px 0;"><img src="data:image/png;base64,{logo_b64}" style="height:75px; display:inline-block;" /></div>' if logo_b64 else '<div style="font-size:2.5rem; text-align:center;">🎓</div>'
    
    st.markdown(f"{sidebar_logo}<div style='text-align:center;'><h2 style='color:#a52a2a; font-weight:800; margin:6px 0 2px; font-size:1.2rem;'>Galgotias University</h2><p style='color:#666; font-size:0.82rem; margin:0;'>Greater Noida, Uttar Pradesh</p><div class='status-badge'>🟢 Dustin Online</div></div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 💬 Quick Questions")
    st.caption("Click any question to ask instantly:")

    quick_questions = [
        ("🎓", "What is the admission process?"),
        ("📚", "What courses are available?"),
        ("💰", "What are BCA fees?"),
        ("🏠", "Is hostel available?"),
        ("🏢", "Tell me about placement packages"),
        ("📅", "When will exams start?"),
        ("👨‍💼", "Who is the HOD of Computer Science?"),
        ("📞", "How can I contact the college?"),
        ("🏅", "What scholarships are available?"),
        ("🚌", "Is there a transport facility?"),
    ]

    for emoji, question in quick_questions:
        if st.button(f"{emoji} {question}", key=f"sidebar_{question}", use_container_width=True):
            st.session_state.messages.append({'role': 'user', 'content': question})
            result = get_response(question)
            st.session_state.messages.append({'role': 'bot', 'content': result['response']})
            st.rerun()

    st.markdown("---")
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = [{'role': 'bot', 'content': WELCOME_TEXT, 'preformatted': True}]
        st.session_state.last_input = ''
        st.rerun()

    st.markdown("---")
    st.markdown("""
    <div style='text-align:center; font-size:0.78rem; color:#999;'>
        Powered by Python + NLTK<br/>
        <strong>Dustin v1.0</strong>
    </div>
    """, unsafe_allow_html=True)

# ─── Centered Top Header Layout (Strictly Only Massive DUSTIN - Fixed Code Visibility Bug) ───
st.markdown(f"{logo_html}<div style='text-align:center; background:linear-gradient(135deg, #7b1c1c 0%, #a52a2a 50%, #c0392b 100%); padding:25px 40px; border-radius:24px; box-shadow:0 6px 25px rgba(123, 28, 28, 0.25); margin-top:-30px; margin-bottom:30px;'><h1 style='font-size:5.5rem; font-weight:900; margin:0; letter-spacing:4px; background:linear-gradient(45deg, #FFD700 30%, #FFA500 100%); -webkit-background-clip:text; -webkit-text-fill-color:transparent; text-shadow:3px 3px 6px rgba(0,0,0,0.35); line-height:1.1;'>DUSTIN</h1></div>", unsafe_allow_html=True)

# ─── Chat Messages ────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    if msg['role'] == 'user':
        st.markdown(f"<div class='msg-label user-label'>You</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='user-msg'>{msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='msg-label'>🤖 Dustin</div>", unsafe_allow_html=True)
        content = msg['content'] if msg.get('preformatted') else format_bot_message(msg['content'])
        st.markdown(f"<div class='bot-msg'>{content}</div>", unsafe_allow_html=True)

# ─── Input Area ───────────────────────────────────────────────────────────────
st.markdown("<br/>", unsafe_allow_html=True)
col1, col2 = st.columns([5, 1])

with col1:
    user_input = st.text_input(
        label="msg",
        placeholder="Type your question... (e.g. What are BCA fees?)",
        label_visibility="collapsed",
        key="user_input_field"
    )
with col2:
    send_clicked = st.button("Send 📤", type="primary", use_container_width=True)

# ─── Process Input ────────────────────────────────────────────────────────────
if send_clicked and user_input.strip() and user_input.strip() != st.session_state.last_input:
    current_input = user_input.strip()
    st.session_state.last_input = current_input

    st.session_state.messages.append({'role': 'user', 'content': current_input})

    with st.spinner("Dustin is thinking..."):
        result = get_response(current_input)

    st.session_state.messages.append({'role': 'bot', 'content': result['response']})
    st.rerun()

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align:center; color:#aaa; font-size:0.82rem; padding:8px 0;'>
    © 2026 Galgotias University, Greater Noida &nbsp;|&nbsp;
    Dustin – AI Chatbot built with Python, NLTK &amp; Streamlit
</div>
""", unsafe_allow_html=True)