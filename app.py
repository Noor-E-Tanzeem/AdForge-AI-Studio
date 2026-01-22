import streamlit as st
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
from rembg import remove
from moviepy.editor import (
    ImageClip,
    AudioFileClip,
    concatenate_videoclips,
    TextClip,
    CompositeVideoClip,
    VideoFileClip
)
import tempfile
import os
import re

# ---------------------------
# Streamlit Page Config
# ---------------------------
st.set_page_config(page_title="🎬 AdForge AI Studio", layout="wide", initial_sidebar_state="expanded")

# ---------------------------
# CSS Styles for Neon Headings, Background, etc.
# ---------------------------
st.markdown("""
<style>
body {
    background-image: url('https://i.ibb.co/7bQjGZs/background-energy.jpg');
    background-size: cover;
    background-repeat: no-repeat;
    background-attachment: fixed;
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
st.sidebar.markdown('<p style="color:#00FFFF;font-weight:bold;font-size:20px;">💡 Tips:</p>', unsafe_allow_html=True)
st.sidebar.markdown("Upload product images, optional stock video, and enter script. Generate dynamic AI ad videos! ✨")

# ---------------------------
# Header & Banner
# ---------------------------
st.markdown('<h1 class="neon-header">🎬 AdForge AI Studio</h1>', unsafe_allow_html=True)
st.image("https://i.ibb.co/4pDNDk1/energy-drink-banner.png", width=600)
st.markdown('<p class="emoji-title">Generate ads with animated text, voiceover & dynamic slides 🌟</p>', unsafe_allow_html=True)

# ---------------------------
# Utility Functions
# ---------------------------
def clean_script(script):
    """Remove brackets/stage directions for TTS"""
    cleaned = re.sub(r"\[.*?\]", "", script)
    cleaned = "\n".join([line.strip() for line in cleaned.splitlines() if line.strip() != ""])
    return cleaned

def generate_voiceover(script_text):
    cleaned_text = clean_script(script_text)
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
    """Animated ad video with TTS + moving image + optional stock video"""
    clips = []

    # Animated text clips
    script_lines = clean_script(script).splitlines()
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

    # Concatenate all clips
    video = concatenate_videoclips(clips, method="compose")

    # Overlay audio
    audio_clip = AudioFileClip(audio_path)
    audio_clip = audio_clip.set_duration(video.duration)
    video = video.set_audio(audio_clip)

    # Write final video
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    temp_file.close()
    video.write_videofile(temp_file.name, fps=24, codec='libx264', audio_codec='aac', verbose=False, logger=None)

    return temp_file.name

# ---------------------------
# Streamlit Sections
# ---------------------------

# 1️⃣ Script Input
st.markdown('<p class="section-title">1️⃣ Script Generator ✍️</p>', unsafe_allow_html=True)
script = st.text_area("Paste or type your ad script here", height=150)

# 2️⃣ Product Image
st.markdown('<p class="section-title">2️⃣ Product Image Editor 🖼️</p>', unsafe_allow_html=True)
uploaded_image = st.file_uploader("Upload product image (PNG/JPG)", type=["png","jpg","jpeg"])
text_overlay = st.text_input("Text overlay on product image", value="ElectriFy: Power Your Potential")

if uploaded_image and st.button("Edit Product Image"):
    edited_image_path = edit_image(uploaded_image, text_overlay)
    st.session_state.edited_image_path = edited_image_path
    st.image(edited_image_path, caption="Edited Product Image")

# 3️⃣ Optional Stock Video
st.markdown('<p class="section-title">3️⃣ Optional Stock Video 🎥</p>', unsafe_allow_html=True)
stock_video = st.file_uploader("Upload short stock video (MP4)", type=["mp4"])

# 4️⃣ Voiceover Generation
st.markdown('<p class="section-title">4️⃣ Background Music + Voiceover 🎙️</p>', unsafe_allow_html=True)
music_file = st.file_uploader("Optional: Upload background music (MP3)", type=["mp3"])

if script:
    if st.button("Generate Voiceover"):
        audio_path = generate_voiceover(script)
        st.session_state.audio_path = audio_path
        st.audio(audio_path)
        with open(audio_path, "rb") as f:
            st.download_button("Download Voiceover MP3", f, file_name="voiceover.mp3")

# 5️⃣ Generate Animated Ad Video
st.markdown('<p class="section-title">5️⃣ Create Animated Ad Video 🎬</p>', unsafe_allow_html=True)
duration_per_slide = st.slider("Duration per text/image slide (seconds)", 2, 10, 5)

if st.button("Create Animated Ad Video"):
    if "edited_image_path" in st.session_state and "audio_path" in st.session_state:
        video_path = create_ad_video(
            script,
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
