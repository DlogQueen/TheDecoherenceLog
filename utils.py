import streamlit as st
import time
import random
import re
import socket
import base64
import os

@st.cache_data
def get_img_as_base64(file_path):
    if not os.path.exists(file_path): return ""
    with open(file_path, "rb") as f: data = f.read()
    return base64.b64encode(data).decode()

def load_css(file_name="style.css"):
    with open(file_name) as f: css = f.read()
    # Global background: background 4 PNG (login + all pages except profiles)
    bg_b64 = get_img_as_base64("backgroud 4.png") or get_img_as_base64("background3.jpg")
    css += """
    /* CYBERPUNK 2026 OVERRIDE */
    .stApp {
        background-attachment: fixed;
        background-size: cover;
    }
    """
    if bg_b64:
        css += f"""
        .stApp {{
            background-image: url("data:image/png;base64,{bg_b64}");
        }}
        """
    else:
        css += """
        .stApp {
            background-image: radial-gradient(circle at center, #0d0d1a 0%, #111 50%, #000 100%);
        }
        """
    # Neon buttons & inputs
    css += """
    div.stButton > button {
        background: linear-gradient(45deg, #00f2ff22, #00f2ff11);
        border: 1px solid #00f2ff;
        color: #00f2ff;
        text-shadow: 0 0 5px #00f2ff;
        transition: all .2s ease;
    }
    div.stButton > button:hover {
        background: #00f2ff;
        color: #000;
        box-shadow: 0 0 15px #00f2ff, 0 0 30px #00f2ff88;
        transform: scale(1.02);
    }
    /* Glass cards */
    .glass-card {
        background: rgba(0,0,0,0.45);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(0,242,255,0.4);
        border-radius: 8px;
        box-shadow: 0 0 20px rgba(0,242,255,0.15);
    }
    /* Toggles */
    .stCheckbox > label > div {
        background: #00f2ff22;
        border: 1px solid #00f2ff;
    }
    /* Inputs glow */
    input {
        caret-color: #00f2ff;
        border: 1px solid #00f2ff44;
    }
    input:focus {
        border-color: #00f2ff;
        box-shadow: 0 0 10px #00f2ff;
    }
    /* CRACKING BUTTONS */
    div.stButton > button,
    a.st-emotion-cache-1wivap2 {   /* Streamlit link buttons */
        position: relative;
        overflow: hidden;
        background: linear-gradient(45deg, #00f2ff22, #00f2ff11);
        border: 1px solid #00f2ff;
        color: #00f2ff;
        text-shadow: 0 0 5px #00f2ff;
        transition: all .2s ease;
    }
    div.stButton > button:hover,
    a.st-emotion-cache-1wivap2:hover {
        background: #00f2ff;
        color: #000;
        box-shadow: 0 0 15px #00f2ff, 0 0 30px #00f2ff88;
        transform: scale(1.02);
    }
    /* CRT flicker + crack on click */
    div.stButton > button:active,
    a.st-emotion-cache-1wivap2:active {
        animation: crack .15s forwards;
    }
    @keyframes crack {
        0%   { transform: scale(1);   filter: brightness(1); }
        25%  { transform: scale(1.02) rotate(.5deg); filter: brightness(1.3); }
        50%  { transform: scale(.98) rotate(-.5deg); filter: brightness(.7); }
        100% { transform: scale(1);   filter: brightness(1); }
    }
    /* Sidebar link buttons inherit crack style */
    section[data-testid="stSidebar"] a {
        text-decoration: none;
    }
    """
    st.markdown(f'<style>{css}/*cache-buster=5*/</style>', unsafe_allow_html=True)

def render_void_intro():
    st.markdown("""
    <div class="void-warning">
        <div class="void-text">
            ⚠️ REALITY DECOHERENCE DETECTED ⚠️<br>
            <span style="font-size: 0.5em; color: #00f2ff;">PROCEED AT YOUR OWN RISK</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_glitch_header(text, subtext=""):
    st.markdown(f"""<div style="text-align: center; margin-bottom: 40px;">
<h1 class="glitch-text" style="font-size: 3em; margin: 0;">{text}</h1>
<p class="neon-cyan" style="font-size: 1.2em; letter-spacing: 2px;">{subtext}</p>
</div>""", unsafe_allow_html=True)

def render_glass_card(content):
    st.markdown(f"""<div class="glass-card">{content}</div>""", unsafe_allow_html=True)

def render_resonance_meter(protons, electrons, neutrals=0):
    pass # Simplified for new version

def render_entanglement_alert(matched_users):
    users_str = ", ".join(str(u) for u in matched_users) if isinstance(matched_users, list) else "UNKNOWN"
    st.markdown(f"""<div style="position: fixed; top: 15%; left: 5%; right: 5%; background: rgba(0,0,0,0.95); border: 2px solid #ff0000; z-index: 9999; padding: 40px; text-align: center; box-shadow: 0 0 50px #ff0000; animation: glitch 0.5s infinite;">
<h1 class="warning-red" style="font-size: 3em;">⚠ QUANTUM ENTANGLEMENT DETECTED ⚠</h1>
<p style="color: #FFF; font-size: 1.5em;">SYNC ESTABLISHED WITH: {users_str}</p>
</div>""", unsafe_allow_html=True)

def render_terminal_boot():
    placeholder = st.empty()
    return placeholder

def get_logo_html(size=40):
    logo_b64 = get_img_as_base64("logo1.png")   # deco logo
    if logo_b64:
        return f'<img src="data:image/png;base64,{logo_b64}" width="{size}" style="filter: drop-shadow(0 0 8px #00f2ff);">'
    return "🧬"

def render_atoms(post_id):
    return None

class ObserverAI:
    def __init__(self):
        self.knowledge_base = {
            r"superposition": "A system in multiple states at once.",
            r"entangle": "Particles connected across distance.",
            r"decoherence": "Breakdown of consensus reality.",
            r"hello": "Greetings, Observer.",
            r"help": "I can explain quantum concepts."
        }
    def get_response(self, user_msg):
        msg = user_msg.lower()
        time.sleep(0.3)
        for pattern, response in self.knowledge_base.items():
            if re.search(pattern, msg): return f"🔍 **ANALYSIS:** {response}"
        return "🤖 **SYSTEM:** Query not recognized."

observer_ai = ObserverAI()