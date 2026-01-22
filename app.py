import streamlit as st
from moviepy.editor import ImageClip, VideoFileClip, CompositeVideoClip, TextClip
from gtts import gTTS
import tempfile
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import base64

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
.main-title { font-size: 42px; font-weight: 800; color: #ffffff; }
.sub-title { font-size: 20px; color: #cfcfcf; }
.card { background: #171a23; border-radius: 18px; padding: 28px; color: #ffffff; box-shadow: 0 8px 25px rgba(0,0,0,0.4);}
.section-title { font-size: 26px; font-weight: 700; color: #4da6ff; }
.small-text { color: #dddddd; font-size: 16px; line-height: 1.6; }
.footer-nav { position: fixed; bottom: 0; width: 100%; background: #171a23; padding: 12px; text-align: center; color: #aaaaaa; font-size: 14px; border-top: 1px solid #2b2f3a;}
</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
st.sidebar.image(
    "https://i.postimg.cc/Dwg8cpgg/Screenshot-2026-01-22-234840.png",
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

def generate_voiceover(text):
    tts = gTTS(text=text, lang="en")
    temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_audio.name)
    return temp_audio.name

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

# ---------------- D-ID API ----------------
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
    response = requests.post(url, json=payload, headers=headers)
    result = response.json()
    if "result_url" in result:
        video_url = result["result_url"]
        video_data = requests.get(video_url).content
        temp_video = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        temp_video.write(video_data)
        return temp_video.name
    else:
        st.error(f"D-ID API Error: {result}")
        return None

def add_product_overlay(talking_video_path, product_img_path, slogan):
    video_clip = VideoFileClip(talking_video_path)
    product_clip = ImageClip(product_img_path).set_duration(video_clip.duration).resize(height=200).set_position(("right","bottom"))
    text_clip = TextClip(slogan, fontsize=50, color='white').set_duration(video_clip.duration).set_position(("left","top"))
    final = CompositeVideoClip([video_clip, product_clip, text_clip])
    temp_final = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    final.write_videofile(temp_final.name, fps=24)
    return temp_final.name

# ---------------- SESSION ----------------
for k in ["profile_created","user_name","user_email","user_brand","slogan","script","audio","human_img","product_img","review_rating","review_text"]:
    if k not in st.session_state:
        st.session_state[k] = None

# ---------------- PROFILE CREATION ----------------
if not st.session_state.profile_created:
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

# ---------------- HOME ----------------
if menu == "Home":
    col1, col2 = st.columns([1, 4])
    with col1:
        small_banner = load_image("https://i.postimg.cc/CLnTFRX1/Screenshot-2026-01-22-232250.png")
        st.image(small_banner, width=170)
    with col2:
        st.markdown(f'<div class="main-title">AdForge AI Studio</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="sub-title">Welcome, {st.session_state.user_name}! Turn ideas into cinematic AI ads.</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🚀 About</div>', unsafe_allow_html=True)
        st.markdown("<div class='small-text'>AdForge AI Studio auto-creates professional ad creatives using AI. Upload a human image, product image, and generate scripts, voiceovers, and videos.</div>", unsafe_allow_html=True)
        st.markdown('<div class="section-title">✨ Features</div>', unsafe_allow_html=True)
        st.markdown("<div class='small-text'>• AI slogan & script generation<br>• AI voiceover<br>• Billboard generator<br>• Animated talking human<br>• Product placement<br>• AI video generation</div>", unsafe_allow_html=True)
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

    st.markdown("### 🧑 Upload Human Image (for animated ad)")
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

    if st.button("🎥 Generate Animated AI Video"):
        if not product or not st.session_state.audio or not st.session_state.human_img:
            st.error("Missing product, voiceover, or human image.")
        else:
            talking_video = generate_animated_human(st.session_state.human_img.name, st.session_state.audio)
            if talking_video:
                final_video = add_product_overlay(talking_video, st.session_state.product_img.name, st.session_state.slogan)
                st.video(final_video)
                st.success("Animated AI ad video generated!")

                # ---------------- REVIEW / RATING ----------------
                st.markdown("### ⭐ Rate Your Experience")
                rating = st.slider("Rate the App", min_value=1, max_value=5, value=5)
                review = st.text_area("Your Feedback")
                if st.button("Submit Review"):
                    st.session_state.review_rating = rating
                    st.session_state.review_text = review
                    st.success("Thank you for your feedback! 🌟")

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- SETTINGS ----------------
elif menu == "Settings":
    st.markdown('<div class="card"><div class="section-title">⚙ Settings</div><div class="small-text">Video quality & AI model options coming soon.</div></div>', unsafe_allow_html=True)

# ---------------- LICENSE ----------------
elif menu == "License":
    st.markdown('<div class="card"><div class="section-title">📜 License</div><div class="small-text">AdForge AI Studio – Community Edition © 2026</div></div>', unsafe_allow_html=True)

# ---------------- FOOTER ----------------
st.markdown('<div class="footer-nav">🏠 Home | 🎬 Studio | ⚙ Settings | 📜 License</div>', unsafe_allow_html=True)
