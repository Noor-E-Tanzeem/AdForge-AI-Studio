import streamlit as st
from moviepy.editor import ImageClip, VideoFileClip, CompositeVideoClip, TextClip, AudioFileClip, concatenate_videoclips
from gtts import gTTS
import tempfile
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import base64
import time
import random
import os

# ---------------- CONFIG ----------------
st.set_page_config(page_title="AdForge AI Studio", page_icon="🤖", layout="wide")

# ---------------- ENHANCED CSS ----------------
st.markdown("""
<style>
    .main { background-color: #0e1117; color: white; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #ff4b4b; color: white; }
    .card { background-color: #1e2130; padding: 20px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #3e4259; }
    .section-title { font-size: 24px; font-weight: bold; color: #ff4b4b; margin-bottom: 15px; }
    .feature-list { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }
    .feature-item { background: #262730; padding: 15px; border-radius: 8px; text-align: center; }
    .profile-icon { position: absolute; top: 10px; right: 10px; width: 50px; height: 50px; border-radius: 50%; border: 2px solid #ff4b4b; }
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION DEFAULTS ----------------
defaults = {
    "profile_created": False, "user_name": "", "user_email": "", "user_brand": "", "user_gender": "",
    "slogan": "", "script": "", "audio": None, "human_img": None, "product_img": None,
    "review_rating": 5, "review_text": "", "video_resolution": "720p", "voice_style": "Female", 
    "script_style": "Corporate", "bgm_enabled": False, "bgm_url": "", "ad_format": "Video Ad", 
    "language": "English", "generated_ads": []
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ---------------- UTILS ----------------
def load_image(url):
    response = requests.get(url)
    return Image.open(BytesIO(response.content))

def generate_with_llama(prompt):
    if "slogan" in prompt.lower():
        slogans = ["Unleash Energy. Unstoppable You.", "Power Your Passion.", "Elevate Every Moment.", "Ignite Your Potential."]
        return random.choice(slogans)
    elif "script" in prompt.lower():
        style = st.session_state.script_style
        scripts = {
            "Funny": "RedBull gives wings… and laughs! Fly through your day with energy and fun.",
            "Dramatic": "RedBull empowers you to conquer the impossible. Every sip, a surge of power.",
            "Corporate": "Introducing RedBull — the energy that keeps you moving. Fuel ambition."
        }
        return scripts.get(style, "Your brand. Your power. Your moment.")
    return "AI-generated content here."

def generate_voiceover(text):
    lang_map = {"English": "en", "Spanish": "es", "French": "fr"}
    lang = lang_map.get(st.session_state.language, "en")
    tts = gTTS(text=text, lang=lang)
    temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_audio.name)
    return temp_audio.name

# ---------------- PROFILE CREATION ----------------
if not st.session_state.profile_created:
    st.markdown('<h1 style="text-align: center;">🤖 AdForge AI Studio</h1>', unsafe_allow_html=True)
    with st.container():
        st.markdown('### 👤 Create Your Profile')
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Name", placeholder="Enter your full name")
            email = st.text_input("Email", placeholder="your.email@example.com")
            gender = st.selectbox("Gender", ["Female", "Male"])
        with col2:
            brand = st.text_input("Company / Brand Name", placeholder="e.g., RedBull")
            avatar = st.file_uploader("Upload Avatar (Optional)", type=["png","jpg","jpeg"])
        
        if st.button("✅ Create Profile"):
            if not name or not email or not brand:
                st.error("Please fill all required fields.")
            else:
                st.session_state.profile_created = True
                st.session_state.user_name = name
                st.session_state.user_brand = brand
                if avatar:
                    st.session_state.avatar_data = avatar.read()
                st.rerun()
    st.stop()

# ---------------- SIDEBAR ----------------
st.sidebar.markdown(f"👋 Hello, {st.session_state.user_name}!")
menu = st.sidebar.radio("📌 Navigation", ["Home", "Ad Studio", "Analytics"])

# ---------------- HOME ----------------
if menu == "Home":
    st.title("AdForge AI Studio")
    st.markdown('<div class="card"><div class="section-title">🚀 About AdForge</div>'
                'Auto-generate professional ad creatives using advanced AI. From scripts to videos.</div>', unsafe_allow_html=True)
    
    if st.button("Go to Ad Studio"):
        # Note: In Streamlit, we change state and rerun
        st.session_state.active_tab = "Ad Studio" 
        # For simplicity in this demo, just use the sidebar to navigate

# ---------------- AD STUDIO ----------------
elif menu == "Ad Studio":
    st.title("🎬 Ad Studio")
    tabs = st.tabs(["📝 Script & Slogan", "🖼️ Assets", "🎥 Generation"])
    
    with tabs[0]:
        product = st.text_input("Product / Topic", placeholder="e.g., RedBull Energy Drink")
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.script_style = st.selectbox("Script Style", ["Corporate", "Funny", "Dramatic"])
        with col2:
            st.session_state.language = st.selectbox("Language", ["English", "Spanish", "French"])
            
        if st.button("✨ Generate Slogan + Script (AI)"):
            if not product:
                st.error("Enter a product.")
            else:
                with st.spinner("Generating..."):
                    st.session_state.slogan = generate_with_llama(f"slogan for {product}")
                    st.session_state.script = generate_with_llama(f"script for {product}")
                    st.success("Content Generated!")
                    st.write(f"**Slogan:** {st.session_state.slogan}")
                    st.write(f"**Script:** {st.session_state.script}")
