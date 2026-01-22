import streamlit as st
from moviepy.editor import ImageClip, VideoFileClip, CompositeVideoClip, TextClip
from gtts import gTTS
import tempfile
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import base64
import os

st.set_page_config(page_title="AdForge AI Studio", page_icon="🤖", layout="wide")

st.markdown("""
<style>
body { background-color: #0e0f14; }
.main-title { font-size: 42px; font-weight: 800; color: #ffffff; }
.sub-title { font-size: 20px; color: #cfcfcf; }
.card { background: #171a23; border-radius: 18px; padding: 28px; color: #ffffff; box-shadow: 0 8px 25px rgba(0,0,0,0.4);}
.section-title { font-size: 26px; font-weight: 700; color: #4da6ff; }
.small-text { color: #dddddd; font-size: 16px; line-height: 1.6; }
.footer-nav { position: fixed; bottom: 0; width: 100%; background: #171a23; padding: 12px; text-align: center; color: #aaaaaa; font-size: 14px; border-top: 1px solid #2b2f3a;}
</style>
""", unsafe_allow_html=True)

defaults = {
    "profile_created": False,
    "user_name": "",
    "user_email": "",
    "user_brand": "",
    "slogan": "",
    "script": "",
    "audio": None,
    "human_img_path": None,
    "product_img_path": None,
    "review_rating": 5,
    "review_text": "",
    "video_resolution": "720p",
    "voice_style": "Female",
    "script_style": "Corporate",
    "product_name": ""
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

def load_image(url):
    response = requests.get(url)
    return Image.open(BytesIO(response.content))

def generate_with_llama(prompt):
    if "slogan" in prompt.lower():
        return "⚡ Unleash Energy. Unstoppable You."
    elif "script" in prompt.lower():
        style = st.session_state.script_style
        if style == "Funny":
            return "😂 Boost your day with laughter and energy!"
        elif style == "Dramatic":
            return "🔥 Power that drives greatness."
        return "Introducing power that keeps you moving forward."
    return "Your brand. Your power. Your moment."

def generate_voiceover(text):
    tts = gTTS(text=text, lang="en")
    temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_audio.name)
    return temp_audio.name

def save_uploaded_file(uploaded_file):
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    temp.write(uploaded_file.read())
    return temp.name

def generate_billboard(product, slogan, human_img_path=None, product_img_path=None):
    bg = Image.new("RGB", (1280, 720), (30, 20, 60))
    draw = ImageDraw.Draw(bg)

    try:
        font_title = ImageFont.truetype("DejaVuSans-Bold.ttf", 70)
        font_slogan = ImageFont.truetype("DejaVuSans.ttf", 42)
    except:
        font_title = ImageFont.load_default()
        font_slogan = ImageFont.load_default()

    draw.text((50, 40), product.upper(), fill=(255, 215, 0), font=font_title)
    draw.text((50, 150), slogan, fill=(200, 200, 255), font=font_slogan)

    if human_img_path:
        human = Image.open(human_img_path).convert("RGB").resize((360, 500))
        bg.paste(human, (860, 160))

    if product_img_path:
        prod = Image.open(product_img_path).convert("RGB").resize((300, 300))
        bg.paste(prod, (60, 350))

    draw.text((60, 660), "✨ AdForge AI Studio", fill=(180, 180, 220), font=font_slogan)

    temp_img = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    bg.save(temp_img.name)
    return temp_img.name

def generate_animated_human(human_img_path, audio_path):
    API_KEY = st.secrets["did_api_key"]
    url = "https://api.d-id.com/talks"

    with open(human_img_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("utf-8")
    with open(audio_path, "rb") as f:
        audio_b64 = base64.b64encode(f.read()).decode("utf-8")

    payload = {
        "source_image": img_b64,
        "driver_audio": audio_b64,
        "config": {"fluent": True, "expression": "neutral"}
    }

    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    resp = requests.post(url, json=payload, headers=headers).json()

    if "result_url" in resp:
        data = requests.get(resp["result_url"]).content
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        tmp.write(data)
        return tmp.name

    st.error(f"D-ID API Error: {resp}")
    return None

def add_product_overlay(talking_video_path, product_img_path, slogan):
    video_clip = VideoFileClip(talking_video_path)

    product_clip = ImageClip(product_img_path)\
        .set_duration(video_clip.duration)\
        .resize(height=200)\
        .set_position(("right", "bottom"))

    text_clip = TextClip(slogan, fontsize=50, color='white')\
        .set_duration(video_clip.duration)\
        .set_position(("left", "top"))

    final = CompositeVideoClip([video_clip, product_clip, text_clip])

    tmp_final = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    final.write_videofile(tmp_final.name, fps=24)
    return tmp_final.name

# ---------------- PROFILE ----------------
if not st.session_state.profile_created:
    banner = load_image("https://i.postimg.cc/CLnTFRX1/Screenshot-2026-01-22-232250.png")
    st.image(banner, width=220)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">👤 Create Your Profile</div>', unsafe_allow_html=True)

    name = st.text_input("Name")
    email = st.text_input("Email")
    brand = st.text_input("Company / Brand Name")

    if st.button("✅ Create Profile"):
        if not name or not email or not brand:
            st.error("Please fill all fields.")
        else:
            st.session_state.profile_created = True
            st.session_state.user_name = name
            st.session_state.user_email = email
            st.session_state.user_brand = brand
            st.success(f"Welcome, {name}! You can now create ads.")

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ---------------- SIDEBAR ----------------
st.sidebar.markdown(f"👋 Hello, {st.session_state.user_name}!")
st.sidebar.markdown("---")
menu = st.sidebar.radio("📌 Navigation", ["Home", "Ad Studio", "Settings", "License"])

# ---------------- HOME ----------------
if menu == "Home":
    banner = load_image("https://i.postimg.cc/CLnTFRX1/Screenshot-2026-01-22-232250.png")
    st.image(banner, width=180)

    st.markdown('<div class="main-title">AdForge AI Studio</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Turn your ideas into cinematic AI ads.</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🚀 Features</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class='small-text'>
    • AI slogan & script generator  
    • Talking-head video ads  
    • Billboard ad creator  
    • Voiceovers  
    • Product overlays  
    • Hackathon-ready UI  
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- AD STUDIO ----------------
elif menu == "Ad Studio":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🎬 Ad Studio</div>', unsafe_allow_html=True)

    product = st.text_input("Product / Topic")
    st.session_state.product_name = product

    if st.button("✨ Generate Slogan + Script"):
        if not product:
            st.error("Enter a product.")
        else:
            st.session_state.slogan = generate_with_llama(f"slogan for {product}")
            st.session_state.script = generate_with_llama(f"script for {product}")
            st.success("AI slogan and script generated!")

    st.text_input("AI Slogan", value=st.session_state.slogan or "")
    script = st.text_area("AI Script", value=st.session_state.script or "", height=120)

    human = st.file_uploader("Human Image", type=["png", "jpg", "jpeg"])
    if human:
        st.session_state.human_img_path = save_uploaded_file(human)

    prod = st.file_uploader("Product Image", type=["png", "jpg", "jpeg"])
    if prod:
        st.session_state.product_img_path = save_uploaded_file(prod)

    if st.button("🖼 Generate Billboard"):
        billboard = generate_billboard(
            st.session_state.product_name,
            st.session_state.slogan,
            st.session_state.human_img_path,
            st.session_state.product_img_path
        )
        st.image(billboard)
        st.success("Billboard created!")

    if st.button("🔊 Generate Voiceover"):
        if not script:
            st.error("Generate script first.")
        else:
            st.session_state.audio = generate_voiceover(script)
            st.audio(st.session_state.audio)
            st.success("Voiceover ready!")

    if st.button("🎥 Generate Animated AI Video"):
        if not st.session_state.audio or not st.session_state.human_img_path:
            st.error("Missing required inputs.")
        else:
            talking_video = generate_animated_human(
                st.session_state.human_img_path,
                st.session_state.audio
            )
            if talking_video:
                final_video = add_product_overlay(
                    talking_video,
                    st.session_state.product_img_path,
                    st.session_state.slogan
                )
                st.video(final_video)
                st.success("Animated AI ad generated!")

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- SETTINGS ----------------
elif menu == "Settings":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">⚙ Settings</div>', unsafe_allow_html=True)
    st.session_state.video_resolution = st.selectbox("Video Resolution", ["480p", "720p", "1080p"])
    st.session_state.voice_style = st.selectbox("Voice Style", ["Female", "Male"])
    st.session_state.script_style = st.selectbox("Script Style", ["Corporate", "Funny", "Dramatic"])
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- LICENSE ----------------
elif menu == "License":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📜 License & Info</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class='small-text'>
    AdForge AI Studio – Community Edition © 2026  
    User: {st.session_state.user_name}  
    Email: {st.session_state.user_email}  
    Brand: {st.session_state.user_brand}
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="footer-nav">🏠 Home | 🎬 Studio | ⚙ Settings | 📜 License</div>', unsafe_allow_html=True)
