import streamlit as st
from moviepy.editor import ImageClip, AudioFileClip
import tempfile
import requests
from PIL import Image
from io import BytesIO

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="AdForge AI Studio",
    page_icon="🎬",
    layout="wide"
)

BG_URL = "https://i.postimg.cc/DZKyGtJB/Screenshot-2026-01-23-000724.png"

# ---------------- CSS ----------------
st.markdown(f"""
<style>
[data-testid="stAppViewContainer"] {{
    background-image: url("{BG_URL}");
    background-size: cover;
    background-attachment: fixed;
}}

.main-title {{
    font-size: 48px;
    font-weight: 800;
    color: #ffffff;
    text-shadow: 0 0 15px #ff00ff;
}}

.sub-title {{
    font-size: 20px;
    color: #f0f0f0;
}}

.glass-box {{
    background: rgba(0,0,0,0.65);
    border-radius: 20px;
    padding: 30px;
    color: #ffffff;
}}

.section-title {{
    font-size: 28px;
    font-weight: 700;
    color: #00ffff;
}}

.footer-nav {{
    position: fixed;
    bottom: 0;
    width: 100%;
    background: rgba(0,0,0,0.85);
    padding: 12px;
    text-align: center;
    color: white;
}}

.small-text {{
    color: #dddddd;
    font-size: 16px;
}}
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

# ---------------- VIDEO FIX ----------------
def create_video(script, billboard_img, audio_path):
    img_clip = ImageClip(billboard_img).set_duration(8)

    def zoom(t):
        return 1 + 0.04 * t

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
if "script" not in st.session_state:
    st.session_state.script = ""
if "audio" not in st.session_state:
    st.session_state.audio = None

# ---------------- HOME ----------------
if menu == "Home":
    col1, col2 = st.columns([1, 3])

    with col1:
        banner = load_image("https://i.postimg.cc/ZK6Z9tFJ/ai-banner.png")
        st.image(banner, width=180)

    with col2:
        st.markdown('<div class="main-title">AdForge AI Studio</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-title">Turn ideas into cinematic TV & Billboard ads in minutes 🚀</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="glass-box">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">What is AdForge?</div>', unsafe_allow_html=True)
        st.markdown(
            "<div class='small-text'>AdForge AI Studio lets you generate high-impact TV and billboard-style ads using AI. "
            "Create scripts, voiceovers, visuals, and videos in just a few clicks.</div>",
            unsafe_allow_html=True
        )

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown('<div class="section-title">✨ Features</div>', unsafe_allow_html=True)
        st.markdown(
            "<div class='small-text'>"
            "• AI Slogan & Script Generator<br>"
            "• AI Voiceovers<br>"
            "• Billboard-Style Visuals<br>"
            "• Human + Product Ads<br>"
            "• Animated Ad Videos<br>"
            "• Cloud-Friendly Video Rendering"
            "</div>",
            unsafe_allow_html=True
        )

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown('<div class="section-title">🚀 Get Started</div>', unsafe_allow_html=True)
        st.markdown(
            "<div class='small-text'>Go to <b>Ad Studio</b> and create your first ad!</div>",
            unsafe_allow_html=True
        )
        st.markdown("</div>", unsafe_allow_html=True)

# ---------------- AD STUDIO ----------------
elif menu == "Ad Studio":
    st.markdown('<div class="glass-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🎬 Ad Studio</div>', unsafe_allow_html=True)

    st.session_state.script = st.text_area("Enter Ad Script", height=120)

    billboard_url = st.text_input("Billboard Image URL")
    audio_file = st.file_uploader("Upload Voiceover Audio (.mp3/.wav)", type=["mp3", "wav"])

    if audio_file:
        temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        temp_audio.write(audio_file.read())
        st.session_state.audio = temp_audio.name

    if st.button("🎥 Create AI Video"):
        if not billboard_url or not st.session_state.audio:
            st.error("Please provide a billboard image URL and voiceover audio.")
        else:
            billboard_img = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            img = load_image(billboard_url)
            img.save(billboard_img.name)

            video = create_video(st.session_state.script, billboard_img.name, st.session_state.audio)
            st.success("Your ad video is ready!")
            st.video(video)

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- SETTINGS ----------------
elif menu == "Settings":
    st.markdown('<div class="glass-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">⚙ Settings</div>', unsafe_allow_html=True)

    theme = st.selectbox("Theme", ["Neon Dark", "Minimal Light", "Cyber Purple"])
    quality = st.selectbox("Video Quality", ["720p", "1080p"])
    fps = st.selectbox("FPS", [24, 30, 60])

    st.markdown(
        "<div class='small-text'>Settings will apply to future ad renders.</div>",
        unsafe_allow_html=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- LICENSE ----------------
elif menu == "License":
    st.markdown('<div class="glass-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📜 License</div>', unsafe_allow_html=True)

    st.markdown(
        "<div class='small-text'>"
        "AdForge AI Studio – Community Edition<br><br>"
        "You are free to use this application for personal and educational projects.<br>"
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

