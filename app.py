import streamlit as st
import tempfile
import requests
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO
import base64
import random
import os

# ---------- SAFE MOVIEPY IMPORT ----------
try:
    from moviepy.editor import ImageClip, VideoFileClip, CompositeVideoClip, TextClip
    MOVIEPY_OK = True
except Exception:
    MOVIEPY_OK = False

# ---------------- CONFIG ----------------
st.set_page_config(page_title="AdForge AI Studio", page_icon="🤖", layout="wide")

# ---------------- CSS ----------------
st.markdown("""
<style>
body { background-color: #0e0f14; }
.main-title { font-size: 46px; font-weight: 900; color: #ffffff; }
.sub-title { font-size: 20px; color: #cfcfcf; }
.card { background: #171a23; border-radius: 18px; padding: 28px; color: #ffffff; box-shadow: 0 8px 25px rgba(0,0,0,0.4);}
.section-title { font-size: 28px; font-weight: 800; color: #ff77aa; }
.profile-icon { position: absolute; top: 20px; right: 20px; }
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION DEFAULTS ----------------
defaults = {
    "profile_created": False,
    "user_name": "",
    "user_email": "",
    "user_brand": "",
    "user_gender": "Male",
    "slogan": "",
    "script": "",
    "audio": None,
    "human_img": None,
    "product_img": None,
    "billboard_img": None,
    "audience": "General",
    "tone": "Corporate",
    "cta": "Buy Now",
    "brand_color": "#ff77aa"
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ---------------- GROQ (LLAMA-3) ----------------
GROQ_API_KEY = st.secrets.get("groq_api_key", "")

def groq_llama(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-70b-8192",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.9
    }
    r = requests.post(url, json=payload, headers=headers)
    return r.json()["choices"][0]["message"]["content"]

# ---------------- MULTI-AGENT PIPELINE ----------------
def slogan_agent(product, tone, audience):
    fewshot = """
Example:
Product: Energy Drink
Tone: Youth
Audience: Students
Slogan: "Fuel Your Hustle. Own the Day."

Now generate a new slogan:
"""
    prompt = f"""{fewshot}
Product: {product}
Tone: {tone}
Audience: {audience}
Slogan:"""
    return groq_llama(prompt).strip()

def script_agent(product, slogan, tone, audience):
    fewshot = """
Example Script:
Meet VoltX, the energy drink built for unstoppable ambition.
Feel the surge from your first sip.
Stay focused during late nights.
Power your workouts.
Crush deadlines.
Fuel creativity.
Beat fatigue.
Rise stronger every day.
VoltX — your energy, your edge.

Now generate a similar 8–10 line script:
"""
    prompt = f"""{fewshot}
Product: {product}
Slogan: {slogan}
Tone: {tone}
Audience: {audience}
Script:"""
    return groq_llama(prompt).strip()

def creative_agent(product, slogan):
    styles = ["neon futuristic", "luxury gold", "youth graffiti", "corporate minimal"]
    return random.choice(styles)

# ---------------- VOICE ----------------
def generate_voiceover(text):
    tts = gTTS(text=text, lang="en")
    temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_audio.name)
    return temp_audio.name

# ---------------- DECORATIVE BILLBOARD ----------------
def generate_billboard(product, slogan, brand_color, cta, human_img=None, product_img=None):
    bg = Image.new("RGB", (1400, 800), brand_color)
    draw = ImageDraw.Draw(bg)

    overlay = Image.new("RGB", (1400, 800), (0,0,0))
    overlay = overlay.filter(ImageFilter.GaussianBlur(120))
    bg = Image.blend(bg, overlay, 0.35)

    try:
        font_title = ImageFont.truetype("DejaVuSans-Bold.ttf", 90)
        font_slogan = ImageFont.truetype("DejaVuSans-Bold.ttf", 56)
        font_cta = ImageFont.truetype("DejaVuSans-Bold.ttf", 52)
    except:
        font_title = ImageFont.load_default()
        font_slogan = ImageFont.load_default()
        font_cta = ImageFont.load_default()

    draw.rounded_rectangle([50,50,1350,200], radius=40, fill=(20,20,40))
    draw.text((80,90), product.upper(), fill=(255,255,255), font=font_title)

    draw.rounded_rectangle([50,240,1350,360], radius=40, fill=(255,255,255))
    draw.text((80,270), slogan, fill=(0,0,0), font=font_slogan)

    if product_img:
        prod = Image.open(product_img).convert("RGBA").resize((350,350))
        bg.paste(prod, (80,400), prod)

    if human_img:
        human = Image.open(human_img).convert("RGBA").resize((300,450))
        bg.paste(human, (1000,330), human)

    draw.rounded_rectangle([500,650,900,740], radius=50, fill=(255,80,120))
    w,h = draw.textsize(cta, font=font_cta)
    draw.text((700-w//2, 670), cta, fill=(255,255,255), font=font_cta)

    temp_img = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    bg.save(temp_img.name)
    return temp_img.name

# ---------------- D-ID ----------------
def generate_animated_human(human_img_path, audio_path):
    API_KEY = st.secrets.get("did_api_key", "")
    if not API_KEY:
        return None

    url = "https://api.d-id.com/talks"
    with open(human_img_path,"rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    with open(audio_path,"rb") as f:
        audio_b64 = base64.b64encode(f.read()).decode()

    payload = {"source_image": img_b64, "driver_audio": audio_b64}
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type":"application/json"}

    r = requests.post(url, json=payload, headers=headers).json()

    if "result_url" in r:
        data = requests.get(r["result_url"]).content
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        tmp.write(data)
        return tmp.name
    return None

# ---------------- PROFILE ----------------
if not st.session_state.profile_created:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title center">👤 Create Your Profile</div>', unsafe_allow_html=True)
    name = st.text_input("Name")
    email = st.text_input("Email")
    brand = st.text_input("Brand Name")
    gender = st.selectbox("Gender", ["Male","Female"])
    if st.button("Start 🚀"):
        if name and email and brand:
            st.session_state.profile_created = True
            st.session_state.user_name = name
            st.session_state.user_email = email
            st.session_state.user_brand = brand
            st.session_state.user_gender = gender
            st.experimental_rerun()
        else:
            st.error("Fill all fields")
    st.stop()

# ---------------- SIDEBAR ----------------
st.sidebar.markdown(f"👋 Hello, {st.session_state.user_name}")
menu = st.sidebar.radio("📌 Navigation", ["Ad Studio","Billboard"])

# ---------------- AD STUDIO ----------------
if menu == "Ad Studio":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🎬 Ad Studio</div>', unsafe_allow_html=True)

    product = st.text_input("Product / Topic")
    st.session_state.audience = st.selectbox("Audience", ["General","Youth","Corporate","Luxury"])
    st.session_state.tone = st.selectbox("Ad Tone", ["Corporate","Funny","Dramatic","Luxury"])
    st.session_state.cta = st.selectbox("Call-To-Action", ["Buy Now","Shop Today","Learn More"])
    st.session_state.brand_color = st.color_picker("Brand Color", st.session_state.brand_color)

    if st.button("✨ Generate AI Content"):
        slogan = slogan_agent(product, st.session_state.tone, st.session_state.audience)
        script = script_agent(product, slogan, st.session_state.tone, st.session_state.audience)
        st.session_state.slogan = slogan
        st.session_state.script = script

    st.text_input("AI Slogan", value=st.session_state.slogan)
    script = st.text_area("AI Script (8–10 lines)", value=st.session_state.script, height=220)

    human = st.file_uploader("Human Image", type=["png","jpg"])
    if human:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        tmp.write(human.read())
        st.session_state.human_img = tmp.name

    prod = st.file_uploader("Product Image", type=["png","jpg"])
    if prod:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        tmp.write(prod.read())
        st.session_state.product_img = tmp.name

    if st.button("🔊 Generate Voice"):
        st.session_state.audio = generate_voiceover(script)
        st.audio(st.session_state.audio)

    if st.button("🎥 Generate AI Video"):
        video = generate_animated_human(st.session_state.human_img, st.session_state.audio)
        if video:
            st.video(video)

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- BILLBOARD ----------------
elif menu == "Billboard":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🖼 Decorative Billboard</div>', unsafe_allow_html=True)

    if st.button("🎨 Generate Billboard"):
        img = generate_billboard(
            st.session_state.user_brand,
            st.session_state.slogan,
            st.session_state.brand_color,
            st.session_state.cta,
            st.session_state.human_img,
            st.session_state.product_img
        )
        st.session_state.billboard_img = img
        st.image(img, use_column_width=True)

    if st.session_state.billboard_img:
        with open(st.session_state.billboard_img, "rb") as f:
            st.download_button("⬇ Download Billboard", f, "billboard.png")

    st.markdown("</div>", unsafe_allow_html=True)
