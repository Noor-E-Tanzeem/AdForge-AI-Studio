import streamlit as st
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
from rembg import remove
from moviepy.editor import (
    ImageClip,
    AudioFileClip,
    concatenate_videoclips,
    TextClip
)
import tempfile
import random
import re

st.set_page_config(page_title="🎬 AdForge AI Studio", layout="wide")

# ---------------- CSS ----------------
st.markdown("""
<style>
body { background-color: #EBDCFB; }
.neon-header {
    font-size: 42px;
    font-weight: 900;
    color: #7B2CFF;
    text-shadow: 0px 0px 10px #C08BFF;
}
.section-title {
    font-size: 26px;
    font-weight: 700;
    color: #FF6EC7;
}
.card {
    background: white;
    border-radius: 18px;
    padding: 20px;
    box-shadow: 0 0 15px rgba(0,0,0,0.15);
}
</style>
""", unsafe_allow_html=True)

# ---------------- Sidebar ----------------
page = st.sidebar.radio("Navigation", ["🏠 Home", "🎬 Ad Studio", "⚙️ Settings"])

st.sidebar.image(
    "https://i.postimg.cc/Dwg8cpgg/Screenshot-2026-01-22-234840.png",
    width=100,
    caption="Inspiration"
)

# ---------------- Session Defaults ----------------
if "tone" not in st.session_state:
    st.session_state.tone = "Energetic"
if "voice_speed" not in st.session_state:
    st.session_state.voice_speed = 1.0
if "billboard_mode" not in st.session_state:
    st.session_state.billboard_mode = True
if "neon_theme" not in st.session_state:
    st.session_state.neon_theme = True

# ---------------- Utilities ----------------
def generate_slogan(topic):
    slogans = [
        f"{topic} – Feel the Power!",
        f"{topic} – Fuel Your Dreams!",
        f"Life gets better with {topic}",
        f"{topic} – Made to Move You",
        f"{topic} – The Energy You Deserve"
    ]
    return random.choice(slogans)

def generate_script(topic, slogan, tone):
    base = f"""
Meet the future of energy — {topic}.
When your day slows down…
and your ambition speeds up…
you need more than a drink.

You need {topic}.

{slogan}

Crafted for champions.
Designed for dreamers.
Powered for winners.

Grab your {topic} today.
And feel unstoppable.
"""
    if tone == "Luxury":
        base = base.replace("energy", "excellence").replace("champions", "icons")
    if tone == "Calm":
        base = base.replace("unstoppable", "balanced")
    return base.strip()

def generate_voice(script_text, speed):
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts = gTTS(text=script_text, lang='en', slow=(speed < 1))
    tts.save(temp.name)
    return temp.name

def billboard_image(product_img, slogan):
    product = Image.open(product_img).convert("RGBA")
    product = remove(product)
    product = product.resize((400, 400))

    board = Image.new("RGBA", (900, 600), (40, 40, 40, 255))
    draw = ImageDraw.Draw(board)
    draw.rectangle([20,20,880,580], outline="white", width=6)

    board.paste(product, (250, 120), product)

    try:
        font = ImageFont.truetype("arial.ttf", 45)
    except:
        font = ImageFont.load_default()

    draw.text((100, 30), slogan, fill="white", font=font)

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    board.save(temp.name)
    return temp.name

def create_video(script, billboard_img, audio_path):
    clips = []

    for line in script.split("\n"):
        if line.strip():
            txt = TextClip(line.strip(), fontsize=52, color='white', size=(1280,720))
            txt = txt.set_duration(3).set_position("center")
            clips.append(txt)

    img_clip = ImageClip(billboard_img).set_duration(6).resize(height=720)
    clips.append(img_clip)

    video = concatenate_videoclips(clips, method="compose")
    audio = AudioFileClip(audio_path)
    video = video.set_audio(audio)

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    video.write_videofile(temp.name, fps=24, codec="libx264", audio_codec="aac", verbose=False, logger=None)
    return temp.name

# ---------------- HOME ----------------
if page == "🏠 Home":
    st.markdown('<h1 class="neon-header">🎬 AdForge AI Studio</h1>', unsafe_allow_html=True)

    banner_url = "https://i.postimg.cc/CLnTFRX1/Screenshot-2026-01-22-232250.png"
    st.image(banner_url, width=600)

    st.markdown("""
    <div class="card">
    <h2>What is AdForge?</h2>
    AdForge AI Studio helps you create stunning TV & Billboard ads in minutes.

    <h3>✨ Features</h3>
    • AI slogan & script  
    • AI voiceover  
    • Billboard-style ads  
    • Human + product visuals  
    • Animated ad videos  

    <h3>🚀 Get Started</h3>
    Go to Ad Studio and create your first ad!
    </div>
    """, unsafe_allow_html=True)

# ---------------- SETTINGS ----------------
if page == "⚙️ Settings":
    st.markdown('<h1 class="neon-header">⚙️ Settings</h1>', unsafe_allow_html=True)

    st.session_state.tone = st.selectbox("Ad Tone", ["Energetic", "Calm", "Luxury"])
    st.session_state.voice_speed = st.slider("Voice Speed", 0.5, 1.5, 1.0)
    st.session_state.billboard_mode = st.toggle("Enable Billboard Mode", True)
    st.session_state.neon_theme = st.toggle("Neon Theme", True)

    st.success("Settings saved!")

# ---------------- AD STUDIO ----------------
if page == "🎬 Ad Studio":
    st.markdown('<h1 class="neon-header">🎬 Ad Studio</h1>', unsafe_allow_html=True)

    topic = st.text_input("Enter Product / Topic")

    if topic and st.button("Generate Slogan + Script"):
        st.session_state.slogan = generate_slogan(topic)
        st.session_state.script = generate_script(
            topic,
            st.session_state.slogan,
            st.session_state.tone
        )
        st.success("Generated!")
        st.text_area("Slogan", st.session_state.slogan, height=70)
        st.text_area("Script", st.session_state.script, height=200)

    product_img = st.file_uploader("Upload Product Image", type=["png","jpg","jpeg"])

    if product_img and st.session_state.billboard_mode:
        billboard = billboard_image(product_img, st.session_state.slogan)
        st.image(billboard, caption="Billboard Preview")

    if st.session_state.script and product_img and st.button("Generate AI Voiceover"):
        st.session_state.audio = generate_voice(
            st.session_state.script,
            st.session_state.voice_speed
        )
        st.audio(st.session_state.audio)

    if st.button("Create Ad Video"):
        if product_img and st.session_state.audio:
            billboard = billboard_image(product_img, st.session_state.slogan)
            video = create_video(
                st.session_state.script,
                billboard,
                st.session_state.audio
            )
            st.video(video)
        else:
            st.error("Upload product image & generate voiceover first.")
