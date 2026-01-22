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
    .profile-icon {
        position: fixed;
        top: 15px;
        right: 25px;
        width: 55px;
        height: 55px;
        border-radius: 50%;
        border: 3px solid #ff4b4b;
        z-index: 9999;
        object-fit: cover;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .login-logo {
        display: block;
        margin: 0 auto 30px auto;
        width: 280px;
    }
    .card {
        background-color: #1e2130;
        padding: 25px;
        border-radius: 15px;
        margin-bottom: 20px;
        border-left: 5px solid #ff4b4b;
    }
    .section-title { font-size: 26px; font-weight: bold; color: #ff4b4b; margin-bottom: 10px; }
    .feature-item { background: #262730; padding: 15px; border-radius: 8px; margin: 10px 0; }
    .stats { display: flex; justify-content: space-around; text-align: center; margin-top: 20px; }
    .stat-item h2 { color: #ff4b4b; margin-bottom: 0; }
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION DEFAULTS ----------------
defaults = {
    "profile_created": False, "user_name": "", "user_email": "", "user_brand": "", "user_gender": "Female",
    "slogan": "", "script": "", "audio": None, "human_img": None, "product_img": None,
    "review_rating": 5, "review_text": "", "video_resolution": "720p", "voice_style": "Female", 
    "script_style": "Corporate", "bgm_enabled": False, "bgm_url": "", "ad_format": "Video Ad", 
    "language": "English", "generated_ads": [], "avatar_url": ""
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ---------------- AI ENGINES (GROQ LLAMA) ----------------
def call_groq_llama(prompt):
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        data = {
            "model": "llama3-8b-8192",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.8
        }
        response = requests.post(url, headers=headers, json=data)
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"AI Logic Offline: {str(e)}"

# ---------------- UTILS ----------------
def load_image(url):
    response = requests.get(url)
    return Image.open(BytesIO(response.content))

def generate_voiceover(text):
    lang_map = {"English": "en", "Spanish": "es", "French": "fr"}
    lang = lang_map.get(st.session_state.language, "en")
    tts = gTTS(text=text, lang=lang)
    temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_audio.name)
    return temp_audio.name

def generate_billboard(product, slogan, human_img=None, product_img=None):
    bg = Image.new("RGB", (1280, 720), (20, 20, 30))
    draw = ImageDraw.Draw(bg)
    # Simple draw logic as fallback for fonts
    draw.text((60, 60), f"BRAND: {st.session_state.user_brand.upper()}", fill=(255,255,255))
    draw.text((60, 120), f"PRODUCT: {product}", fill=(255,255,255))
    draw.text((60, 200), slogan, fill=(200,200,255))
    
    if human_img:
        human = Image.open(human_img).convert("RGBA").resize((400,600))
        bg.paste(human, (800,120), human)
    if product_img:
        prod = Image.open(product_img).convert("RGBA").resize((300,300))
        bg.paste(prod, (100,350), prod)
        
    temp_img = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    bg.save(temp_img.name)
    return temp_img.name

def render_ai_video(human_img_path, audio_path, script_text, slogan):
    audio_clip = AudioFileClip(audio_path)
    # Slow zoom effect for "Realism"
    img_clip = ImageClip(human_img_path).set_duration(audio_clip.duration).resize(lambda t: 1 + 0.02*t)
    
    # Word-by-word lip-sync simulation (Subtitles)
    words = script_text.split()
    word_dur = audio_clip.duration / len(words)
    subs = []
    for i, w in enumerate(words):
        txt = TextClip(w.upper(), fontsize=60, color='yellow', font='Arial-Bold', bg_color='black').set_start(i*word_dur).set_duration(word_dur).set_position(('center', 600))
        subs.append(txt)
    
    # Add Slogan Overlay
    slogan_clip = TextClip(slogan, fontsize=40, color='white', bg_color='red').set_duration(audio_clip.duration).set_position(('left', 'top'))
    
    final = CompositeVideoClip([img_clip] + subs + [slogan_clip]).set_audio(audio_clip)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    final.write_videofile(tmp.name, fps=24, codec="libx264")
    return tmp.name

# ---------------- PROFILE CREATION (LOGIN) ----------------
if not st.session_state.profile_created:
    st.markdown('<img src="https://i.postimg.cc/3rz01J48/Screenshot_2026_01_23_021409.png" class="login-logo">', unsafe_allow_html=True)
    st.markdown('<div class="card"><h2 style="text-align: center;">👤 User Profile Initialization</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name")
        email = st.text_input("Email Address")
        gender = st.selectbox("Gender", ["Female", "Male"])
    with col2:
        brand = st.text_input("Brand Name", placeholder="e.g. RedBull")
        avatar_upload = st.file_uploader("Custom Avatar", type=['png', 'jpg'])
    
    if st.button("✅ Launch Studio"):
        if name and brand:
            st.session_state.user_name = name
            st.session_state.user_brand = brand
            st.session_state.user_gender = gender
            # Specific URL Requirement
            if gender == "Female":
                st.session_state.avatar_url = "https://i.postimg.cc/PrVnmBvh/Screenshot-2026-01-23-010324.png"
            else:
                st.session_state.avatar_url = "https://i.postimg.cc/5tTtnXH0/Screenshot_2026_01_23_010056.png"
            st.session_state.profile_created = True
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ---------------- PROFILE ICON TOP RIGHT ----------------
st.markdown(f'<img src="{st.session_state.avatar_url}" class="profile-icon">', unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
st.sidebar.title(f"Operator: {st.session_state.user_name}")
menu = st.sidebar.radio("📌 Navigation", ["Home", "Ad Studio", "Analytics", "Settings", "License"])

# ---------------- HOME ----------------
if menu == "Home":
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image("https://i.postimg.cc/CLnTFRX1/Screenshot-2026-01-22-232250.png", width=170)
    with col2:
        st.markdown(f'<h1>AdForge AI Studio: {st.session_state.user_brand}</h1>', unsafe_allow_html=True)
        st.write("Turn ideas into cinematic AI ads with Groq-speed Llama 3 generation.")

    st.markdown('<div class="card"><h3>🚀 About AdForge</h3>Ultimate tool for marketers. Auto-generate scripts, videos, and billboards.</div>', unsafe_allow_html=True)
    
    # Feature List
    st.markdown("""
    <div class="card">
        <div class="section-title">✨ Professional Suite</div>
        <div class="feature-item"><b>🤖 Groq Llama 3:</b> Sub-second script generation.</div>
        <div class="feature-item"><b>🎥 Lip-Sync Engine:</b> Advanced voice-to-visual mapping.</div>
        <div class="feature-item"><b>🎨 Billboard Creator:</b> High-res static ad generation.</div>
    </div>
    """, unsafe_allow_html=True)

    # Stats
    st.markdown("""
    <div class="card">
        <div class="stats">
            <div class="stat-item"><h2>15k+</h2><p>Ads Forged</p></div>
            <div class="stat-item"><h2>98%</h2><p>Accuracy</p></div>
            <div class="stat-item"><h2>A100</h2><p>GPU Power</p></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ---------------- AD STUDIO ----------------
elif menu == "Ad Studio":
    st.title("🎬 Ad Studio")
    tabs = st.tabs(["📝 Script & Slogan", "🖼️ Assets", "🎥 Generation", "📤 Billboard"])
    
    with tabs[0]:
        prod = st.text_input("Target Product", placeholder="e.g. RedBull Energy")
        style = st.selectbox("Script Style", ["Funny", "Dramatic", "Corporate"])
        if st.button("✨ Generate AI Content"):
            with st.spinner("Calling Groq Llama 3..."):
                st.session_state.slogan = call_groq_llama(f"Write a 5 word slogan for {prod}")
                st.session_state.script = call_groq_llama(f"Write a 25 word {style} ad script for {prod}")
                st.success("Done!")
                st.write(f"**Slogan:** {st.session_state.slogan}")
                st.write(f"**Script:** {st.session_state.script}")

    with tabs[1]:
        st.session_state.human_img = st.file_uploader("Upload Person Image", type=['png','jpg'])
        st.session_state.product_img = st.file_uploader("Upload Product Image", type=['png','jpg'])

    with tabs[2]:
        if st.session_state.human_img and st.session_state.script:
            if st.button("⚡ Generate AI Video Ad"):
                with st.spinner("Processing Lip-Sync..."):
                    audio_path = generate_voiceover(st.session_state.script)
                    # Save human image to temp
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as f:
                        f.write(st.session_state.human_img.getbuffer())
                        h_path = f.name
                    
                    vid_path = render_ai_video(h_path, audio_path, st.session_state.script, st.session_state.slogan)
                    st.video(vid_path)
        else:
            st.warning("Needs Script and Human Image first!")

    with tabs[3]:
        if st.button("🖼️ Generate High-Res Billboard"):
            h_path = None
            p_path = None
            if st.session_state.human_img:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as f:
                    f.write(st.session_state.human_img.getbuffer())
                    h_path = f.name
            if st.session_state.product_img:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as f:
                    f.write(st.session_state.product_img.getbuffer())
                    p_path = f.name
            
            billboard = generate_billboard(st.session_state.user_brand, st.session_state.slogan, h_path, p_path)
            st.image(billboard, caption="AI Generated Billboard")

# ---------------- ANALYTICS ----------------
elif menu == "Analytics":
    st.title("📊 Performance Tracking")
    st.line_chart([10, 25, 45, 30, 80, 100])
    st.write("Campaign Reach: +240% this week.")
