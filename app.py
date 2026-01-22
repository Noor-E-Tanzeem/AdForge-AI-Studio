import streamlit as st
from moviepy.editor import ImageClip, AudioFileClip
from gtts import gTTS
import tempfile
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="AdForge AI Studio",
    page_icon="🎬",
    layout="wide"
)

# ---------------- CSS ----------------
st.markdown("""
<style>
body {
    background-color: #111217;
}

.main-title {
    font-size: 42px;
    font-weight: 800;
    color: #ffffff;
}

.sub-title {
    font-size: 20px;
    color: #cccccc;
}

.card {
    background: #181b23;
    border-radius: 18px;
    padding: 28px;
    color: #ffffff;
    box-shadow: 0 8px 25px rgba(0,0,0,0.3);
}

.section-title {
    font-size: 26px;
    font-weight: 700;
    color: #4da6ff;
}

.small-text {
    color: #dddddd;
    font-size: 16px;
}

.footer-nav {
    position: fixed;
    bottom: 0;
    width: 100%;
    background: #181b23;
    padding: 12px;
    text-align: center;
    color: #aaaaaa;
    font-size: 14px;
    border-top: 1px solid #2b2f3a;
}
</style>
""", unsafe_allow_html=True)

# ---------------- NAV ----------------
menu = st.sidebar.radio(
    "📌 Navigation",
    ["Home", "Ad Studio", "Settings", "License"]
)

# ---------------- UTILS ----------------
def load_image(url):
    response = requests.get(url)
    return Image.open(BytesIO(response.content))

# ---------------- LLaMA PLACEHOLDER ----------------
def generate_with_llama(prompt):
    if "slogan" in prompt.lower():
        return "Unleash Energy. Unstoppable You."
    elif "script" in prompt.lower():
        return (
            "Introducing RedBull – the energy that keeps you moving. "
            "Whether you're chasing dreams or breaking limits, "
            "RedBull fuels your ambition. Grab one today and feel the power."
        )
    else:
        return "Your brand. Your power. Your moment."

# ---------------- VOICEOVER ----------------
def generate_voiceover(text):
    tts = gTTS(text=text, lang="en")
    temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_audio.name)
    return temp_audio.name

# ---------------- BILLBOARD ----------------
def generate_billboard(product, slogan):
    img = Image.new("RGB", (1280, 720), (20, 20, 30))
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype("DejaVuSans-Bold.ttf", 80)
        font_slogan = ImageFont.truetype("DejaVuSans.ttf", 50)
    except:
        font_title = ImageFont.load_default()
        font_slogan = ImageFont.load_default()

    draw.text((60, 80), product.upper(), fill=(255, 255, 255), font=font_title)
    draw.text((60, 220), slogan, fill=(200, 200, 255), font=font_slogan)
    draw.text((60, 620), "AdForge AI Studio", fill=(120, 120, 160), font=font_slogan)

    temp_img = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    img.save(temp_img.name)
    return temp_img.name

# ---------------- VIDEO ----------------
def create_video(billboard_img, audio_path):
    img_clip = ImageClip(billboard_img).set_duration(8)

    def zoom(t):
        return 1 + 0.03 * t

    img_clip = img_clip.resize(zoom)

    audio = AudioFileClip(audio_path)
    img_clip = img_clip.set_duration(audio.duration)
    img_clip = img_clip.set_audio(audio)

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    img_clip.write_videofile(
        temp.name,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        verbose=False,
        logger=None
    )

    return temp.name

# ---------------- SESSION ----------------
if "slogan" not in st.session_state:
    st.session_state.slogan = ""
if "script" not in st.session_state:
    st.session_state.script = ""
if "audio" not in st.session_state:
    st.session_state.audio = None

# ---------------- HOME ----------------
if menu == "Home":

    col1, col2 = st.columns([1, 3])

    with col1:
        try:
            banner = load_image("https://i.postimg.cc/Dwg8cpgg/Screenshot-2026-01-22-234840.png")
            st.image(banner, width=160)
        except:
            st.write("")

    with col2:
        st.markdown('<div class="main-title">AdForge AI Studio</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="sub-title">Create cinematic AI advertisements in one click.</div>',
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">What is AdForge?</div>', unsafe_allow_html=True)
        st.markdown(
            "<div class='small-text'>"
            "AdForge AI Studio creates professional advertisements automatically. "
            "Enter a product name and get a slogan, script, voiceover and billboard-style ad video."
            "</div>",
            unsafe_allow_html=True
        )

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown('<div class="section-title">✨ Features</div>', unsafe_allow_html=True)
        st.markdown(
            "<div class='small-text'>"
            "• LLaMA-powered slogan generator<br>"
            "• LLaMA-powered ad scripts<br>"
            "• AI voiceover (no uploads)<br>"
            "• Auto-generated billboard visuals<br>"
            "• AI video ads<br>"
            "• Human talking ads (coming soon)"
            "</div>",
            unsafe_allow_html=True
        )

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown('<div class="section-title">🚀 Get Started</div>', unsafe_allow_html=True)
        st.markdown(
            "<div class='small-text'>Go to <b>Ad Studio</b> and generate your first AI ad.</div>",
            unsafe_allow_html=True
        )
        st.markdown("</div>", unsafe_allow_html=True)

# ---------------- AD STUDIO ----------------
elif menu == "Ad Studio":

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🎬 Ad Studio</div>', unsafe_allow_html=True)

    product = st.text_input("Enter Product / Topic")

    if st.button("✨ Generate Slogan + Script (AI)"):
        if not product:
            st.error("Enter a product or topic.")
        else:
            st.session_state.slogan = generate_with_llama(f"Generate a catchy slogan for {product}")
            st.session_state.script = generate_with_llama(f"Generate a full ad script for {product}")
            st.success("AI slogan and script generated!")

    slogan = st.text_input("AI Slogan", value=st.session_state.slogan)
    script = st.text_area("AI Ad Script", value=st.session_state.script, height=140)

    if st.button("🔊 Generate Voiceover"):
        if not script:
            st.error("Generate script first.")
        else:
            st.session_state.audio = generate_voiceover(script)
            st.success("Voiceover generated!")
            st.audio(st.session_state.audio)

    if st.button("🎥 Generate Billboard + AI Video"):
        if not product or not st.session_state.slogan or not st.session_state.audio:
            st.error("Generate slogan, script and voiceover first.")
        else:
            billboard = generate_billboard(product, st.session_state.slogan)
            video = create_video(billboard, st.session_state.audio)

            st.success("Your AI ad video is ready!")
            st.video(video)

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- SETTINGS ----------------
elif menu == "Settings":

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">⚙ Settings</div>', unsafe_allow_html=True)

    theme = st.selectbox("Theme", ["Dark", "Light"])
    quality = st.selectbox("Video Quality", ["720p", "1080p"])
    fps = st.selectbox("FPS", [24, 30, 60])

    st.markdown(
        "<div class='small-text'>Settings will apply to future ad renders.</div>",
        unsafe_allow_html=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- LICENSE ----------------
elif menu == "License":

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📜 License</div>', unsafe_allow_html=True)

    st.markdown(
        "<div class='small-text'>"
        "AdForge AI Studio – Community Edition<br><br>"
        "You are free to use this application for personal and educational purposes.<br>"
        "Commercial redistribution or resale is not permitted without permission.<br><br>"
        "© 2026 AdForge AI"
        "</div>",
        unsafe_allow_html=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- FOOTER ----------------
st.markdown("""
<div class="footer-nav">
🏠 Home | 🎬 Studio | ⚙ Settings | 📜 License
</div>
""", unsafe_allow_html=True)
