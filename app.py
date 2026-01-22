import streamlit as st
from moviepy.editor import ImageClip, TextClip, AudioFileClip, CompositeVideoClip, ColorClip
from gtts import gTTS
import tempfile
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO
import time
import random
import os

# ---------------- CONFIG & CSS ----------------
st.set_page_config(page_title="AdForge AI Studio", page_icon="🤖", layout="wide")

st.markdown("""
<style>
    .profile-icon {
        position: fixed;
        top: 15px;
        right: 25px;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        border: 3px solid #00f2fe;
        z-index: 9999;
        object-fit: cover;
        box-shadow: 0 0 15px rgba(0,242,254,0.6);
    }
    .login-logo {
        display: block;
        margin: 0 auto 30px auto;
        width: 280px;
    }
    .card {
        background: rgba(255, 255, 255, 0.05);
        padding: 25px;
        border-radius: 15px;
        margin-bottom: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .section-title { font-size: 26px; font-weight: bold; color: #00f2fe; }
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION DEFAULTS ----------------
if "profile_created" not in st.session_state:
    st.session_state.update({
        "profile_created": False, "user_name": "", "user_brand": "", "user_gender": "Female",
        "slogan": "", "script": "", "avatar_url": "", "product_img": None, "credits": 500
    })

# ---------------- GROQ LLAMA API ----------------
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
    except:
        return "AI Logic Offline. Check Secrets."

# ---------------- AD RENDERING ENGINES ----------------

def render_motion_ad(product_img_data, script, slogan):
    """Creates a high-energy ad with product zoom, voiceover, CC, and moving emojis."""
    # 1. Voiceover
    tts = gTTS(script, lang='en')
    v_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(v_tmp.name)
    audio = AudioFileClip(v_tmp.name)
    duration = audio.duration

    # 2. Product Image with Zoom Effect
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as f:
        f.write(product_img_data.getbuffer())
        p_path = f.name
    
    bg_color = ColorClip(size=(1280, 720), color=(10, 10, 20)).set_duration(duration)
    prod_clip = ImageClip(p_path).set_duration(duration).resize(height=400).set_position('center')
    prod_clip = prod_clip.resize(lambda t: 1 + 0.05*t) # Slow zoom

    # 3. Floating Emojis Logic
    emojis = ["🔥", "🚀", "✨", "💎", "💯"]
    emoji_clips = []
    for _ in range(8):
        e_txt = TextClip(random.choice(emojis), fontsize=50, color='white').set_duration(duration)
        # Random floating movement
        start_pos = (random.randint(0, 1200), random.randint(0, 700))
        end_pos = (start_pos[0] + random.randint(-100, 100), start_pos[1] - 300)
        e_txt = e_txt.set_position(lambda t, sp=start_pos, ep=end_pos: (sp[0], sp[1] - (t*50)))
        emoji_clips.append(e_txt)

    # 4. Captions (Closed Captions)
    words = script.split()
    w_dur = duration / len(words)
    cc_clips = []
    for i, w in enumerate(words):
        cc = TextClip(w.upper(), fontsize=70, color='cyan', font='Arial-Bold', stroke_color='black', stroke_width=2)
        cc = cc.set_start(i*w_dur).set_duration(w_dur).set_position(('center', 600))
        cc_clips.append(cc)

    # 5. Slogan Overlay
    slogan_txt = TextClip(slogan, fontsize=40, color='white', bg_color='purple').set_duration(duration).set_position(('center', 50))

    final = CompositeVideoClip([bg_color, prod_clip, slogan_txt] + emoji_clips + cc_clips).set_audio(audio)
    out_p = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
    final.write_videofile(out_p, fps=24, codec="libx264")
    return out_p

def generate_decorated_billboard(brand, slogan, product_img_data):
    """Creates a professional, highly decorated billboard."""
    canvas = Image.new("RGB", (1920, 1080), (15, 15, 25))
    draw = ImageDraw.Draw(canvas)
    
    # Add Abstract Decorations (Rectangles/Lines)
    for i in range(0, 1920, 200):
        draw.line([(i, 0), (i+100, 1080)], fill=(30, 30, 60), width=2)
    
    # Product Image
    prod = Image.open(product_img_data).convert("RGBA").resize((700, 700))
    canvas.paste(prod, (1100, 190), prod)
    
    # Text Decoration
    draw.text((100, 300), brand.upper(), fill=(0, 242, 254))
    draw.text((100, 450), slogan, fill=(255, 255, 255))
    draw.rectangle([90, 420, 800, 430], fill=(0, 242, 254)) # Decorative line
    
    out = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    canvas.save(out.name)
    return out.name

# ---------------- LOGIN SCREEN ----------------
if not st.session_state.profile_created:
    st.markdown('<img src="https://i.postimg.cc/3rz01J48/Screenshot_2026_01_23_021409.png" class="login-logo">', unsafe_allow_html=True)
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Operator Name")
            brand = st.text_input("Brand Name")
        with c2:
            gender = st.selectbox("Gender", ["Female", "Male"])
            
        if st.button("🚀 ACCESS STUDIO"):
            if name and brand:
                st.session_state.user_name = name
                st.session_state.user_brand = brand
                st.session_state.user_gender = gender
                st.session_state.avatar_url = "https://i.postimg.cc/PrVnmBvh/Screenshot-2026-01-23-010324.png" if gender == "Female" else "https://i.postimg.cc/5tTtnXH0/Screenshot_2026_01_23_010056.png"
                st.session_state.profile_created = True
                st.rerun()
    st.stop()

# ---------------- UI LAYOUT ----------------
st.markdown(f'<img src="{st.session_state.avatar_url}" class="profile-icon">', unsafe_allow_html=True)

st.sidebar.title(f"Logged: {st.session_state.user_name}")
menu = st.sidebar.radio("Navigation", ["Home", "AI Ad Studio"])

if menu == "Home":
    st.title(f"Welcome to {st.session_state.user_brand} Lab")
    st.image("https://i.postimg.cc/CLnTFRX1/Screenshot-2026-01-22-232250.png", width=200)
    st.markdown('<div class="card"><h3>Professional AI Ad Creation</h3>Generate high-energy video ads with moving emojis and decorated billboards instantly.</div>', unsafe_allow_html=True)

elif menu == "AI Ad Studio":
    st.title("🎬 Creative Engine")
    t1, t2, t3 = st.tabs(["[1] Llama Script", "[2] Assets", "[3] Final Render"])
    
    with t1:
        prod_name = st.text_input("Product Name")
        if st.button("✨ Write Script"):
            st.session_state.slogan = call_groq_llama(f"5 word catchy slogan for {prod_name}")
            st.session_state.script = call_groq_llama(f"20 word energy ad script for {prod_name}")
            st.success("Llama 3 has generated your copy!")
            st.write(f"**Slogan:** {st.session_state.slogan}")
            st.write(f"**Script:** {st.session_state.script}")

    with t2:
        st.session_state.product_img = st.file_uploader("Upload Product Photo", type=['png', 'jpg'])
        if st.session_state.product_img:
            st.image(st.session_state.product_img, width=300)

    with t3:
        if st.session_state.product_img and st.session_state.script:
            c1, c2 = st.columns(2)
            with c1:
                if st.button("📹 Render Motion Video"):
                    path = render_motion_ad(st.session_state.product_img, st.session_state.script, st.session_state.slogan)
                    st.video(path)
            with c2:
                if st.button("🖼️ Generate Decorated Billboard"):
                    b_path = generate_decorated_billboard(st.session_state.user_brand, st.session_state.slogan, st.session_state.product_img)
                    st.image(b_path)
        else:
            st.warning("Upload product photo and generate script first!")
