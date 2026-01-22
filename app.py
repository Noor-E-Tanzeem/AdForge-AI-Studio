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
    page_icon="🤖",
    layout="wide"
)

# ---------------- CSS ----------------
st.markdown("""
<style>
body { background-color: #0e0f14; }

.main-title {
    font-size: 42px; font-weight: 800; color: #ffffff;
}

.sub-title {
    font-size: 20px; color: #cfcfcf;
}

.card {
    background: #171a23; border-radius: 18px;
    padding: 28px; color: #ffffff;
    box-shadow: 0 8px 25px rgba(0,0,0,0.4);
}

.section-title {
    font-size: 26px; font-weight: 700; color: #4da6ff;
}

.small-text {
    color: #dddddd; font-size: 16px; line-height: 1.6;
}

.footer-nav {
    position: fixed; bottom: 0; width: 100%;
    background: #171a23; padding: 12px;
    text-align: center; color: #aaaaaa;
    font-size: 14px; border-top: 1px solid #2b2f3a;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
st.sidebar.image(
    "https://i.postimg.cc/CLnTFRX1/Screenshot-2026-01-22-232250.png",
    width=180,
    caption="AdForge AI"
)

menu = st.sidebar.radio(
    "📌 Navigation",
    ["Home", "Ad Studio", "Settings", "License"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("🎯 *Create cinematic AI advertisements.*")

# ---------------- UTILS ----------------
def load_image(url):
    response = requests.get(url)
    return Image.open(BytesIO(response.content))

# ---------------- AI (LLaMA PLACEHOLDER) ----------------
def generate_with_llama(prompt):
    if "slogan" in prompt.lower():
        return "Unleash Energy. Unstoppable You."
    elif "script" in prompt.lower():
        return (
            "Introducing RedBull — the energy that keeps you moving. "
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
def generate_billboard(product, slogan, human_img=None, product_img=None):
    bg = Image.new("RGB", (1280, 720), (20, 20, 30))
    draw = ImageDraw.Draw(bg)

    try:
        font_title = ImageFont.truetype("DejaVuSans-Bold.ttf", 70)
        font_slogan = ImageFont.truetype("DejaVuSans.ttf", 42)
    except:
        font_title = ImageFont.load_default()
        font_slogan = ImageFont.load_default()

    draw.text((60, 60), product.upper(), fill=(255,255,255), font=font_title)
    draw.text((60, 160), slogan, fill=(200,200,255), font=font_slogan)

    if human_img:
        human = Image.open(human_img).convert("RGBA").resize((360, 500))
        bg.paste(human, (860, 170), human)

    if product_img:
        prod = Image.open(product_img).convert("RGBA").resize((280, 280))
        bg.paste(prod, (60, 380), prod)

    draw.text((60, 660), "AdForge AI Studio", fill=(140,140,180), font=font_slogan)

    temp_img = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    bg.save(temp_img.name)
    return temp_img.name

# ---------------- VIDEO ----------------
def create_video(billboard_img, audio_path):
    img_clip = ImageClip(billboard_img)

    def zoom(t): return 1 + 0.03 * t
    img_clip = img_clip.resize(zoom)

    audio = AudioFileClip(audio_path)
    img_clip = img_clip.set_duration(audio.duration)
    img_clip = img_clip.set_audio(audio)

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    img_clip.write_videofile(
        temp.name, fps=24,
        codec="libx264", audio_codec="aac",
        verbose=False, logger=None
    )
    return temp.name

# ---------------- SESSION ----------------
for k in ["slogan","script","audio","human_img","product_img"]:
    if k not in st.session_state:
        st.session_state[k] = None

# ---------------- HOME ----------------
if menu == "Home":

    col1, col2 = st.columns([1, 4])

    with col1:
        small_banner = load_image(
            "https://i.postimg.cc/Dwg8cpgg/Screenshot-2026-01-22-234840.png"
        )
        st.image(small_banner, width=160)

    with col2:
        st.markdown('<div class="main-title">AdForge AI Studio</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="sub-title">Create cinematic AI advertisements with talking humans.</div>',
            unsafe_allow_html=True
        )

    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)

        st.markdown('<div class="section-title">🚀 About</div>', unsafe_allow_html=True)
        st.markdown(
            "<div class='small-text'>"
            "AdForge AI Studio is a next-gen advertising tool that auto-creates "
            "professional ads using AI. Just enter your product, upload a human face "
            "and a product image — and let AI handle the rest."
            "</div>", unsafe_allow_html=True
        )

        st.markdown('<div class="section-title">✨ Features</div>', unsafe_allow_html=True)
        st.markdown(
            "<div class='small-text'>"
            "• AI slogan & script generation<br>"
            "• AI voiceover<br>"
            "• Billboard generator<br>"
            "• Human talking ad mode<br>"
            "• Product placement<br>"
            "• AI video generation"
            "</div>", unsafe_allow_html=True
        )

        st.markdown("</div>", unsafe_allow_html=True)

# ---------------- AD STUDIO ----------------
elif menu == "Ad Studio":

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🎬 Ad Studio</div>', unsafe_allow_html=True)

    product = st.text_input("Enter Product / Topic")

    if st.button("✨ Generate Slogan + Script (AI)"):
        if not product:
            st.error("Enter a product.")
        else:
            st.session_state.slogan = generate_with_llama(f"Generate slogan for {product}")
            st.session_state.script = generate_with_llama(f"Generate script for {product}")
            st.success("AI slogan and script generated!")

    st.text_input("AI Slogan", value=st.session_state.slogan or "")
    script = st.text_area("AI Script", value=st.session_state.script or "", height=120)

    st.markdown("### 🧑 Upload Human Face (for talking ad)")
    human = st.file_uploader("Human Image", type=["png","jpg","jpeg"])
    if human:
        st.session_state.human_img = human

    st.markdown("### 🥤 Upload Product Image")
    prod = st.file_uploader("Product Image", type=["png","jpg","jpeg"])
    if prod:
        st.session_state.product_img = prod

    if st.button("🔊 Generate Voiceover"):
        if not script:
            st.error("Generate script first.")
        else:
            st.session_state.audio = generate_voiceover(script)
            st.audio(st.session_state.audio)
            st.success("Voiceover ready!")

    if st.button("🎥 Generate Billboard + AI Video"):
        if not product or not st.session_state.audio:
            st.error("Missing product or voiceover.")
        else:
            billboard = generate_billboard(
                product,
                st.session_state.slogan,
                st.session_state.human_img,
                st.session_state.product_img
            )

            video = create_video(billboard, st.session_state.audio)
            st.video(video)
            st.success("AI ad video generated!")

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- SETTINGS ----------------
elif menu == "Settings":
    st.markdown(
        '<div class="card">'
        '<div class="section-title">⚙ Settings</div>'
        "<div class='small-text'>Video quality & AI model options coming soon.</div>"
        "</div>",
        unsafe_allow_html=True
    )

# ---------------- LICENSE ----------------
elif menu == "License":
    st.markdown(
        '<div class="card">'
        '<div class="section-title">📜 License</div>'
        "<div class='small-text'>AdForge AI Studio – Community Edition © 2026</div>"
        "</div>",
        unsafe_allow_html=True
    )

# ---------------- FOOTER ----------------
st.markdown("""
<div class="footer-nav">
🏠 Home | 🎬 Studio | ⚙ Settings | 📜 License
</div>
""", unsafe_allow_html=True)
