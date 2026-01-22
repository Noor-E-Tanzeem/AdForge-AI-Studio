import streamlit as st
from moviepy.editor import ImageClip, TextClip, AudioFileClip, CompositeVideoClip
from gtts import gTTS
import tempfile
import requests
from PIL import Image
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
    .profile-icon {
        position: fixed;
        top: 10px;
        right: 20px;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        border: 2px solid #ff4b4b;
        z-index: 1000;
        object-fit: cover;
    }
    .login-logo {
        display: block;
        margin: 0 auto 20px auto;
        width: 250px;
    }
    .card {
        background-color: #1e2130;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .section-title { font-size: 24px; font-weight: bold; color: #ff4b4b; }
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION DEFAULTS ----------------
if "profile_created" not in st.session_state:
    st.session_state.update({
        "profile_created": False, "user_name": "", "user_brand": "", "user_gender": "Female",
        "slogan": "", "script": "", "avatar_url": "", "human_img": None, "product_img": None,
        "language": "English", "script_style": "Corporate"
    })

# ---------------- GROQ LLAMA INTEGRATION ----------------
def call_groq_llama(prompt):
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        data = {
            "model": "llama3-8b-8192",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }
        response = requests.post(url, headers=headers, json=data)
        return response.json()['choices'][0]['message']['content']
    except:
        return "AI generation failed. Please check your Secret Key."

# ---------------- PROFILE CREATION ----------------
if not st.session_state.profile_created:
    # Login Logo at Top Center
    st.markdown('<img src="https://i.postimg.cc/3rz01J48/Screenshot_2026_01_23_021409.png" class="login-logo">', unsafe_allow_html=True)
    st.markdown('<h2 style="text-align: center;">👤 Create Your Profile</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Name", placeholder="Enter your full name")
        brand = st.text_input("Company / Brand Name", placeholder="e.g., RedBull")
    with col2:
        gender = st.selectbox("Gender", ["Female", "Male"])
        email = st.text_input("Email", placeholder="your.email@example.com")

    if st.button("✅ Create Profile"):
        if name and brand:
            st.session_state.user_name = name
            st.session_state.user_brand = brand
            st.session_state.user_gender = gender
            # Gender based URL logic
            if gender == "Female":
                st.session_state.avatar_url = "https://i.postimg.cc/PrVnmBvh/Screenshot-2026-01-23-010324.png"
            else:
                st.session_state.avatar_url = "https://i.postimg.cc/5tTtnXH0/Screenshot_2026_01_23_010056.png"
            st.session_state.profile_created = True
            st.rerun()
        else:
            st.error("Fill in the details!")
    st.stop()

# ---------------- PROFILE ICON AT TOP RIGHT ----------------
st.markdown(f'<img src="{st.session_state.avatar_url}" class="profile-icon">', unsafe_allow_html=True)

# ---------------- SIDEBAR & NAV ----------------
st.sidebar.markdown(f"👋 Hello, {st.session_state.user_name}!")
menu = st.sidebar.radio("📌 Navigation", ["Home", "Ad Studio"])

# ---------------- HOME ----------------
if menu == "Home":
    st.title("AdForge AI Studio")
    
    st.markdown('<div class="card"><div class="section-title">🚀 About AdForge</div>'
                'The ultimate tool for creators. Auto-generate professional ad creatives using Groq-powered Llama 3. '
                'From scripts to lip-synced videos, we’ve got you covered.</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="card"><div class="section-title">✨ Key Features</div>'
                '<ul><li>🤖 <b>Llama 3 Powered:</b> Instant high-conversion copywriting.</li>'
                '<li>🎥 <b>Lip-Sync Simulation:</b> Voiceover synced with human images.</li>'
                '<li>🌍 <b>Multi-Language:</b> Reach global markets easily.</li></ul></div>', unsafe_allow_html=True)
    
    if st.button("Go to Ad Studio"):
        st.info("Select 'Ad Studio' from the sidebar to start.")

# ---------------- AD STUDIO ----------------
elif menu == "Ad Studio":
    st.title("🎬 Ad Studio")
    t1, t2, t3 = st.tabs(["📝 Scripting", "🖼️ Assets", "🎥 Generation"])
    
    with t1:
        product = st.text_input("Product Name")
        style = st.selectbox("Style", ["Funny", "Corporate", "Dramatic"])
        if st.button("✨ Generate with Llama"):
            prompt = f"Write a 30-word {style} ad script for {product}. Brand name: {st.session_state.user_brand}."
            st.session_state.script = call_groq_llama(prompt)
            st.session_state.slogan = call_groq_llama(f"Write a 5 word slogan for {product}")
            st.success("Generated!")
            st.write(f"**Slogan:** {st.session_state.slogan}")
            st.write(f"**Script:** {st.session_state.script}")

    with t2:
        st.session_state.human_img = st.file_uploader("Upload Human Face Image", type=['png', 'jpg'])
        st.session_state.product_img = st.file_uploader("Upload Product Image", type=['png', 'jpg'])

    with t3:
        if st.session_state.human_img and st.session_state.script:
            if st.button("🚀 Final Video Render"):
                with st.spinner("Simulating Lip-Sync & Rendering..."):
                    # 1. Voice
                    tts = gTTS(st.session_state.script)
                    v_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                    tts.save(v_tmp.name)
                    audio = AudioFileClip(v_tmp.name)
                    
                    # 2. Save Image
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as f:
                        f.write(st.session_state.human_img.getbuffer())
                        img_path = f.name
                    
                    # 3. Video Logic (Syncing image to voice)
                    img_clip = ImageClip(img_path).set_duration(audio.duration)
                    
                    # Subtitle logic to simulate "talking"
                    words = st.session_state.script.split()
                    w_dur = audio.duration / len(words)
                    subs = []
                    for i, w in enumerate(words):
                        t = TextClip(w.upper(), fontsize=50, color='yellow', font='Arial-Bold', bg_color='black')
                        t = t.set_start(i * w_dur).set_duration(w_dur).set_position(('center', 500))
                        subs.append(t)
                    
                    final = CompositeVideoClip([img_clip] + subs).set_audio(audio)
                    out_p = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
                    final.write_videofile(out_p, fps=24, codec="libx264")
                    
                    st.video(out_p)
        else:
            st.warning("Please upload a human image and generate a script first!")
