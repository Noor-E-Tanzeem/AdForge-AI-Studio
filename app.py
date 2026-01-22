import streamlit as st
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip
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

# ---------------- ASSET URLS (YOURS) ----------------
BANNER_URL = "https://i.postimg.cc/CLnTFRX1/Screenshot-2026-01-22-232250.png"
SIDE_IMAGE_URL = "https://i.postimg.cc/Dwg8cpgg/Screenshot-2026-01-22-234840.png"

# ---------------- CSS ----------------
st.markdown("""
<style>
body { background-color: #111217; }

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
menu = st.sidebar.radio("📌 Navigation", ["Home", "Ad Studio", "Settings", "License"])

# ---------------- UTILS ----------------
def load_image(url):
    response = requests.get(url)
    return Image.open(BytesIO(response.content)).convert("RGBA")

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

# ---------------- VIDEO (BILLBOARD + HUMAN + PRODUCT) ----------------
def create_ad_video(billboard_img, human_img, product_img, audio_path):
    billboard = ImageClip(billboard_img).set_duration(8)
    human = ImageClip(human_img).resize(height=480).set_position(("left", "bottom")).set_duration(8)
    product = ImageClip(product_img).resize(height=420).set_position(("right", "bottom")).set_duration(8)

    audio = AudioFileClip(audio_path)
    duration = audio.duration

    billboard = billboard.set_duration(duration)
    human = human.set_duration(duration)
    product = product.set_duration(duration)

    composite = CompositeVideoClip([billboard, human, product])
    composite = composite.set_audio(audio)

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    composite.write_videofile(
        temp.name,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        verbose=False,
        logger=None
    )

    return temp.name

# ---------------- SESSION ----------------
for k in ["slogan", "script", "audio"]:
    if k not in st.session_state:
        st.session_state[k] = None

# ---------------- HOME ----------------
if menu == "Home":

    col1, col2 = st.columns([1, 3])

    with col1:
        banner = load_image(SIDE_IMAGE_URL)
        st.image(banner, width=180)

    with col2:
        st.markdown('<div class="main-title">AdForge AI Studio</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-title">Turn products into cinematic AI ads.</div>', unsafe_allow_html=True)

    st.image(BANNER_URL, use_column_width=True)

    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">What is AdForge?</div>', unsafe_allow_html=True)
        st.markdown(
            "<div class='small-text'>"
            "AdForge AI Studio creates advertisements automatically using AI. "
            "Just enter a product and get a slogan, script, voiceover, and a billboard-style video ad."
            "</div>",
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

    slogan = st.text_input("AI Slogan", value=st.session_state.slogan or "")
    script = st.text_area("AI Ad Script", value=st.session_state.script or "", height=140)

    if st.button("🔊 Generate Voiceover"):
        if not script:
            st.error("Generate script first.")
        else:
            st.session_state.audio = generate_voiceover(script)
            st.success("Voiceover generated!")
            st.audio(st.session_state.audio)

    st.markdown("### 🧍 Human Image")
    human_image = st.file_uploader("Upload human image (PNG/JPG)", type=["png", "jpg", "jpeg"])

    st.markdown("### 🥤 Product Image")
    product_image = st.file_uploader("Upload product image (PNG/JPG)", type=["png", "jpg", "jpeg"])

    if st.button("🎥 Generate AI Ad Video"):
        if not (product and st.session_state.slogan and st.session_state.audio and human_image and product_image):
            st.error("Complete all steps: slogan, script, voiceover, human image, product image.")
        else:
            billboard = generate_billboard(product, st.session_state.slogan)

            human_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            Image.open(human_image).save(human_temp.name)

            product_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            Image.open(product_image).save(product_temp.name)

            video = create_ad_video(billboard, human_temp.name, product_temp.name, st.session_state.audio)

            st.success("Your AI ad video is ready!")
            st.video(video)

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- SETTINGS ----------------
elif menu == "Settings":

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">⚙ Settings</div>', unsafe_allow_html=True)

    st.selectbox("Theme", ["Dark", "Light"])
    st.selectbox("Video Quality", ["720p", "1080p"])
    st.selectbox("FPS", [24, 30, 60])

    st.markdown("<div class='small-text'>Settings will apply to future ad renders.</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- LICENSE ----------------
elif menu == "License":

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📜 License</div>', unsafe_allow_html=True)

    st.markdown(
        "<div class='small-text'>"
        "AdForge AI Studio – Community Edition<br><br>"
        "Free for personal and educational use.<br>"
        "Commercial use requires permission.<br><br>"
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
