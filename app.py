import streamlit as st
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
from rembg import remove
from moviepy.editor import (
    ImageClip,
    AudioFileClip,
    concatenate_videoclips,
    TextClip,
    VideoFileClip
)
import tempfile
import os
import re
import random

# ---------------------------
# Page Config
# ---------------------------
st.set_page_config(page_title="🎬 AdForge AI Studio", layout="wide", initial_sidebar_state="expanded")

# ---------------------------
# CSS Styles
# ---------------------------
st.markdown("""
<style>
body {
    background-color: #FFDEE9; /* Light Pink */
}
.neon-header {
    font-size: 40px;
    font-weight: 800;
    color: #00F2FF;
    text-shadow: 0px 0px 10px #00E5FF, 0px 0px 20px #00AAFF;
}
.emoji-title {
    font-size: 28px;
    font-weight: bold;
    color: #FF33CC;
}
.section-title {
    font-size: 24px;
    font-weight: 700;
    color: #FFAA33;
    text-shadow: 0px 0px 6px #FFDD55;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# Sidebar Decorations
# ---------------------------
st.sidebar.image("https://i.ibb.co/Y3rY3kF/butterfly.png", width=120, caption="🦋 Inspiration")
st.sidebar.markdown('<p style="color:#FF33CC;font-weight:bold;font-size:20px;">💡 Tips:</p>', unsafe_allow_html=True)
st.sidebar.markdown("Enter a product/topic, get a catchy slogan automatically, then create dynamic ads with voiceover & slides! ✨")

# ---------------------------
# Header & Banner
# ---------------------------
st.markdown('<h1 class="neon-header">🎬 AdForge AI Studio</h1>', unsafe_allow_html=True)

# Uploaded decorative banner
banner_image = Image.open("/mnt/data/8b652796-3a13-41fd-94d3-547a6acef6f1.png")
st.image(banner_image, caption="💥 Iconic TV Ad Inspiration 💥", use_column_width=True)

st.markdown('<p class="emoji-title">Automatically generate catchy slogans & dynamic ad videos 🌟</p>', unsafe_allow_html=True)

# ---------------------------
# Utility Functions
# ---------------------------
def generate_slogan(topic):
    """Automatically suggest a catchy slogan based on topic"""
    templates = [
        f"{topic} – Power Your Potential!",
        f"{topic} – Energize Your Day, Every Day!",
        f"Boost Your Life with {topic}!",
        f"{topic} – The Ultimate College Companion!",
        f"{topic} – Fuel Your Ambitions!"
    ]
    return random.choice(templates)

def clean_text(text):
    """Remove brackets/stage directions for TTS"""
    cleaned = re.sub(r"\[.*?\]", "", text)
    cleaned = "\n".join([line.strip() for line in cleaned.splitlines() if line.strip() != ""])
    return cleaned

def generate_voiceover(script_text):
    cleaned_text = clean_text(script_text)
    temp_voice = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts = gTTS(text=cleaned_text, lang='en')
    tts.save(temp_voice.name)
    temp_voice.close()
    return temp_voice.name

def edit_image(image_file, text_overlay, resize_width=800, resize_height=600):
    image = Image.open(image_file).convert("RGBA")
    image_no_bg = remove(image)
    image_resized = image_no_bg.resize((resize_width, resize_height))
    draw = ImageDraw.Draw(image_resized)
    font = ImageFont.load_default()
    draw.text((30, 30), text_overlay, fill="white", font=font)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    image_resized.save(temp_file.name)
    temp_file.close()
    return temp_file.name

def create_ad_video(script, image_path, audio_path, stock_video_path=None, duration_per_slide=5):
    clips = []
    script_lines = clean_text(script).splitlines()

    # Animated text slides
    for line in script_lines:
        txt_clip = TextClip(line, fontsize=50, color='white', font='Arial-Bold', size=(1280,720))
        txt_clip = txt_clip.set_duration(duration_per_slide).set_position('center')
        clips.append(txt_clip)

    # Product image slide
    img_clip = ImageClip(image_path).set_duration(duration_per_slide)
    img_clip = img_clip.resize(width=800).set_position(('center','bottom'))
    clips.append(img_clip)

    # Optional stock video
    if stock_video_path:
        stock_clip = VideoFileClip(stock_video_path)
        stock_clip = stock_clip.subclip(0, min(stock_clip.duration, duration_per_slide*len(clips)))
        stock_clip = stock_clip.resize(height=720)
        clips.insert(0, stock_clip)

    video = concatenate_videoclips(clips, method="compose")

    # Overlay audio
    audio_clip = AudioFileClip(audio_path)
    audio_clip = audio_clip.set_duration(video.duration)
    video = video.set_audio(audio_clip)

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    temp_file.close()
    video.write_videofile(temp_file.name, fps=24, codec='libx264', audio_codec='aac', verbose=False, logger=None)
    return temp_file.name

# ---------------------------
# 1️⃣ Topic Input & Slogan
# ---------------------------
st.markdown('<p class="section-title">1️⃣ Topic & Catchy Slogan ✍️</p>', unsafe_allow_html=True)
topic_input = st.text_input("Enter your product/topic (e.g., 'Energy Drink for College Students')")

if topic_input and st.button("Generate Catchy Slogan"):
    slogan = generate_slogan(topic_input)
    st.session_state.slogan = slogan
    st.success("✅ Catchy slogan generated!")
    st.text_area("Generated Slogan", slogan, height=100)

# ---------------------------
# 2️⃣ Product Image Editor
# ---------------------------
st.markdown('<p class="section-title">2️⃣ Product Image Editor 🖼️</p>', unsafe_allow_html=True)
uploaded_image = st.file_uploader("Upload product image (PNG/JPG)", type=["png","jpg","jpeg"])
text_overlay = st.text_input("Text overlay on product image", value=st.session_state.slogan if "slogan" in st.session_state else "")

if uploaded_image and st.button("Edit Product Image"):
    edited_image_path = edit_image(uploaded_image, text_overlay)
    st.session_state.edited_image_path = edited_image_path
    st.image(edited_image_path, caption="Edited Product Image")

# ---------------------------
# 3️⃣ Optional Stock Video
# ---------------------------
st.markdown('<p class="section-title">3️⃣ Optional Stock Video 🎥</p>', unsafe_allow_html=True)
stock_video = st.file_uploader("Upload short stock video (MP4)", type=["mp4"])

# ---------------------------
# 4️⃣ Voiceover Generation
# ---------------------------
st.markdown('<p class="section-title">4️⃣ Voiceover 🎙️</p>', unsafe_allow_html=True)
music_file = st.file_uploader("Optional: Upload background music (MP3)", type=["mp3"])

if "slogan" in st.session_state and st.button("Generate Voiceover"):
    audio_path = generate_voiceover(st.session_state.slogan)
    st.session_state.audio_path = audio_path
    st.audio(audio_path)
    with open(audio_path, "rb") as f:
        st.download_button("Download Voiceover MP3", f, file_name="voiceover.mp3")

# ---------------------------
# 5️⃣ Create Animated Ad Video
# ---------------------------
st.markdown('<p class="section-title">5️⃣ Create Animated Ad Video 🎬</p>', unsafe_allow_html=True)
duration_per_slide = st.slider("Duration per text/image slide (seconds)", 2, 10, 5)

if st.button("Create Animated Ad Video"):
    if "edited_image_path" in st.session_state and "audio_path" in st.session_state:
        video_path = create_ad_video(
            st.session_state.slogan,
            st.session_state.edited_image_path,
            st.session_state.audio_path,
            stock_video_path=stock_video.name if stock_video else None,
            duration_per_slide=duration_per_slide
        )
        st.session_state.video_path = video_path
        st.video(video_path)
        with open(video_path, "rb") as f:
            st.download_button("Download Video MP4", f, file_name="ad_video.mp4")
    else:
        st.error("Please upload a product image and generate voiceover first.")
