import streamlit as st
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
from rembg import remove
from moviepy.editor import (
    ImageClip,
    AudioFileClip,
    concatenate_videoclips,
    TextClip,
    CompositeVideoClip
)
import tempfile
import os
import re
import random

st.set_page_config(page_title="🎬 AdForge AI Studio", layout="wide")

# ---------------- CSS ----------------
st.markdown("""
<style>
body { background-color: #FFDEE9; }
.neon-header {
    font-size: 40px;
    font-weight: 800;
    color: #00F2FF;
    text-shadow: 0px 0px 10px #00E5FF, 0px 0px 20px #00AAFF;
}
.emoji-title { font-size: 28px; font-weight: bold; color: #FF33CC; }
.section-title {
    font-size: 24px; font-weight: 700;
    color: #FFAA33; text-shadow: 0px 0px 6px #FFDD55;
}
</style>
""", unsafe_allow_html=True)

# ---------------- Sidebar ----------------
st.sidebar.image(
    "https://i.postimg.cc/Dwg8cpgg/Screenshot-2026-01-22-234840.png",
    width=120,
    caption="🦋 Inspiration"
)
st.sidebar.markdown("💡 **Tips:**")
st.sidebar.markdown("Enter a product, generate slogan + script, then create an ad!")

# ---------------- Header ----------------
st.markdown('<h1 class="neon-header">🎬 AdForge AI Studio</h1>', unsafe_allow_html=True)

banner_url = "https://i.postimg.cc/CLnTFRX1/Screenshot-2026-01-22-232250.png"
st.image(banner_url, use_column_width=True)

st.markdown('<p class="emoji-title">AI-Powered TV Advertisement Generator ✨</p>', unsafe_allow_html=True)

# ---------------- Utilities ----------------
def generate_slogan(topic):
    slogans = [
        f"{topic} – Power Your Potential!",
        f"{topic} – Fuel Your Ambition!",
        f"Boost Your Life with {topic}!",
        f"{topic} – The Energy You Deserve!",
        f"{topic} – Feel the Rush!"
    ]
    return random.choice(slogans)

def generate_ad_script(topic, slogan):
    script = f"""
Meet the future of energy — {topic}!

When your day feels slow,
when your dreams feel big,
you need more than a drink…

You need {topic}.

{slogan}

Packed with powerful energy,
crafted for unstoppable ambition,
and made for champions like you.

Grab your {topic} today…
and feel the power within!

{topic}. Fuel your future.
"""
    return script.strip()

def clean_text(text):
    cleaned = re.sub(r"\[.*?\]", "", text)
    return " ".join(cleaned.split())

def generate_voiceover(script_text):
    temp_voice = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts = gTTS(text=script_text, lang='en', slow=False)
    tts.save(temp_voice.name)
    return temp_voice.name

def combine_human_product(human_img, product_img):
    human = Image.open(human_img).convert("RGBA")
    product = Image.open(product_img).convert("RGBA")
    product = remove(product)

    human = human.resize((800, 800))
    product = product.resize((300, 300))

    canvas = Image.new("RGBA", (800, 800), (255, 255, 255, 0))
    canvas.paste(human, (0, 0))
    canvas.paste(product, (450, 450), product)

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    canvas.save(temp.name)
    return temp.name

def create_ad_video(script, combined_img_path, audio_path):
    clips = []

    for line in script.split("\n"):
        if line.strip():
            txt = TextClip(line.strip(), fontsize=50, color='white', size=(1280,720))
            txt = txt.set_duration(3).set_position('center')
            clips.append(txt)

    img_clip = ImageClip(combined_img_path).set_duration(8).resize(height=720)
    clips.append(img_clip)

    video = concatenate_videoclips(clips, method="compose")

    audio = AudioFileClip(audio_path)
    video = video.set_audio(audio)

    temp_video = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    video.write_videofile(temp_video.name, fps=24, codec='libx264', audio_codec='aac', verbose=False, logger=None)

    return temp_video.name

# ---------------- Session ----------------
if "slogan" not in st.session_state:
    st.session_state.slogan = ""
if "script" not in st.session_state:
    st.session_state.script = ""
if "audio" not in st.session_state:
    st.session_state.audio = ""
if "video" not in st.session_state:
    st.session_state.video = ""

# ---------------- Step 1 ----------------
st.markdown('<p class="section-title">1️⃣ Topic Input</p>', unsafe_allow_html=True)
topic = st.text_input("Enter product/topic (e.g., Red Bull for College Students)")

if topic and st.button("Generate Slogan + Script"):
    st.session_state.slogan = generate_slogan(topic)
    st.session_state.script = generate_ad_script(topic, st.session_state.slogan)

    st.success("Slogan & Script Generated!")
    st.text_area("Slogan", st.session_state.slogan, height=80)
    st.text_area("Advertisement Script", st.session_state.script, height=220)

# ---------------- Step 2 ----------------
st.markdown('<p class="section-title">2️⃣ Upload Human + Product Images</p>', unsafe_allow_html=True)
human_img = st.file_uploader("Upload human face image", type=["png","jpg","jpeg"])
product_img = st.file_uploader("Upload product image (e.g., Red Bull)", type=["png","jpg","jpeg"])

# ---------------- Step 3 ----------------
st.markdown('<p class="section-title">3️⃣ Generate Voiceover</p>', unsafe_allow_html=True)

if st.session_state.script and st.button("Generate AI Voiceover"):
    st.session_state.audio = generate_voiceover(st.session_state.script)
    st.audio(st.session_state.audio)

# ---------------- Step 4 ----------------
st.markdown('<p class="section-title">4️⃣ Create Animated Ad Video</p>', unsafe_allow_html=True)

if st.button("Create Video"):
    if human_img and product_img and st.session_state.audio:
        combined_img = combine_human_product(human_img, product_img)
        st.session_state.video = create_ad_video(
            st.session_state.script,
            combined_img,
            st.session_state.audio
        )
        st.video(st.session_state.video)
    else:
        st.error("Upload human image, product image & generate voiceover first.")
