import streamlit as st
import tempfile
import requests
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import base64
import random 

# ---------- SAFE MOVIEPY IMPORT ----------
try:
    from moviepy.editor import (
    ImageClip,
    VideoFileClip,
    CompositeVideoClip,
    ColorClip,
    concatenate_videoclips,
    AudioFileClip
)
    
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
.section-title { font-size: 28px; font-weight: 800; color: #4da6ff; }
.feature-box { background:#1e2230; border-radius:14px; padding:20px; }
.small-text { color: #dddddd; font-size: 16px; line-height: 1.6; }
.footer-nav { position: fixed; bottom: 0; width: 100%; background: #171a23; padding: 12px; text-align: center; color: #aaaaaa; font-size: 14px; border-top: 1px solid #2b2f3a;}
.center { text-align: center; }
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
    "brand_color": "#4da6ff"
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ---------------- UTILS ----------------

# ---------------- UTILS ----------------

def load_image(url):
    response = requests.get(url)
    return Image.open(BytesIO(response.content))


def generate_with_llama(prompt):
    GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
    if not GROQ_API_KEY:
        return fallback_copy(prompt)

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    system_prompt = (
        "You are an expert advertising copywriter. "
        "Generate creative, product-specific, non-generic ad content."
    )

    if "slogan" in prompt.lower():
        user_prompt = f"{prompt}\nGenerate ONE catchy slogan (max 10 words)."
    elif "script" in prompt.lower():
        user_prompt = f"{prompt}\nGenerate a 6–7 line cinematic voiceover script."
    else:
        user_prompt = prompt

    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.9,
        "max_tokens": 350
    }

    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=20
        )
        data = r.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception:
        return fallback_copy(prompt)


def fallback_copy(prompt):
    product = prompt.replace("slogan for", "").replace("script for", "").strip()

    if "slogan" in prompt.lower():
        return f"{product.capitalize()} that’s ready when you are."

    return (
        f"This is not just {product}.\n"
        f"Designed for real-life moments.\n"
        f"Built to perform when it matters.\n"
        f"Strong. Simple. Reliable.\n"
        f"Wherever life takes you.\n"
        f"Stay confident.\n"
        f"Choose reliability."
    )


def generate_voiceover(text):
    tts = gTTS(text=text, lang="en")
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(tmp.name)
    return tmp.name


def generate_billboard(product, slogan, brand_color, cta, product_img=None):
    bg = Image.new("RGB", (1280, 720), (20, 20, 40))
    draw = ImageDraw.Draw(bg)

    try:
        font_title = ImageFont.truetype("DejaVuSans-Bold.ttf", 64)
        font_slogan = ImageFont.truetype("DejaVuSans-Bold.ttf", 44)
        font_cta = ImageFont.truetype("DejaVuSans-Bold.ttf", 40)
    except:
        font_title = font_slogan = font_cta = ImageFont.load_default()

    draw.text((40, 40), product.upper(), fill="white", font=font_title)
    draw.text((40, 160), slogan, fill="yellow", font=font_slogan)

    draw.rectangle([900, 560, 1220, 650], fill=(255, 80, 80))
    draw.text((940, 585), cta, fill="white", font=font_cta)

    if product_img:
        prod = Image.open(product_img).resize((260, 260))
        bg.paste(prod, (40, 400))

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    bg.save(tmp.name)
    return tmp.name


def make_text_image(text, size=(1100, 200)):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 64)
    except:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]

    draw.text(
        ((size[0] - w) // 2, (size[1] - h) // 2),
        text,
        font=font,
        fill=(255, 215, 0, 255)
    )

    return img


def generate_product_ad_video(product_img_path, audio_path, slogan):
    audio = AudioFileClip(audio_path)
    total_duration = audio.duration

    # ---- split time across scenes ----
    t1 = 2
    t2 = 3
    t3 = 3
    t4 = max(2, total_duration - (t1 + t2 + t3))

    # ================= SCENE 1 — HOOK =================
    scene1_bg = ColorClip((1280, 720), color=(10, 10, 20)).set_duration(t1)

    hook_text = make_text_image("MADE FOR REAL LIFE")
    tmp_hook = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    hook_text.save(tmp_hook.name)

    hook_clip = (
        ImageClip(tmp_hook.name)
        .set_position("center")
        .set_duration(t1)
    )

    scene1 = CompositeVideoClip([scene1_bg, hook_clip])

   # ================= SCENE 2 — PRODUCT REVEAL =================

# --- Resize product safely with PIL ---
img = Image.open(product_img_path).convert("RGBA")
w, h = img.size
new_h = 360
new_w = int((new_h / h) * w)
img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

tmp_prod = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
img.save(tmp_prod.name)

# --- Background ---
scene2_bg = ColorClip(
    size=(1280, 720),
    color=(20, 20, 40)
).set_duration(t2)

# --- Product motion (cinematic) ---
product_clip = ImageClip(tmp_prod.name)
product_clip = product_clip.set_position(
    lambda t: (
        400 + int(120 * (t / t2) ** 2),   # ease-in motion
        220 + int(6 * (-1) ** int(t * 2)) # subtle float
    )
)
product_clip = product_clip.resize(
    lambda t: 1.0 + 0.03 * (t / t2)
)
product_clip = product_clip.set_duration(t2)

# --- Slogan text (PIL-rendered, safe) ---
slogan_img = make_text_image(slogan.upper())
tmp_slogan = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
slogan_img.save(tmp_slogan.name)

slogan_clip = ImageClip(tmp_slogan.name)
slogan_clip = slogan_clip.set_position(
    lambda t: ("center", int(120 - 40 * min(t, 1)))
)
slogan_clip = slogan_clip.fadein(0.6)
slogan_clip = slogan_clip.set_duration(t2)

# --- Dark overlay for depth ---
overlay = ColorClip(
    size=(1280, 720),
    color=(0, 0, 0)
).set_opacity(0.25).set_duration(t2)

# --- Final Scene 2 composition ---
scene2 = CompositeVideoClip([
    scene2_bg,
    overlay,
    product_clip,
    slogan_clip
])
    # ================= SCENE 3 — VALUE =================
    scene3_bg = ColorClip((1280, 720), color=(30, 30, 50)).set_duration(t3)

    value_text = make_text_image("SIMPLE. STRONG. RELIABLE.")
    tmp_value = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    value_text.save(tmp_value.name)

    value_clip = (
        ImageClip(tmp_value.name)
        .set_position("center")
        .set_duration(t3)
    )

    scene3 = CompositeVideoClip([scene3_bg, value_clip])

    # ================= SCENE 4 — CTA =================
    scene4_bg = ColorClip((1280, 720), color=(0, 0, 0)).set_duration(t4)

    cta_text = make_text_image("EXPERIENCE IT TODAY")
    tmp_cta = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    cta_text.save(tmp_cta.name)

    cta_clip = (
        ImageClip(tmp_cta.name)
        .set_position("center")
        .set_duration(t4)
    )

    scene4 = CompositeVideoClip([scene4_bg, cta_clip])

    # ================= FINAL VIDEO =================
    final_video = concatenate_videoclips(
        [scene1, scene2, scene3, scene4],
        method="compose"
    ).set_audio(audio)

    tmp_video = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    final_video.write_videofile(
        tmp_video.name,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        verbose=False,
        logger=None
    )

    return tmp_video.name
# ---------------- PROFILE CREATION ----------------
if not st.session_state.profile_created:

    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.markdown("""
    <div class="center">
        <img src="https://i.postimg.cc/3rz01J48/Screenshot_2026_01_23_021409.png" width="100">
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title center">👤 Create Your Profile</div>', unsafe_allow_html=True)

    name = st.text_input("Name")
    email = st.text_input("Email")
    brand = st.text_input("Brand Name")
    gender = st.selectbox("Gender", ["Male","Female"])

    if st.button("Start Creating Ads 🚀"):
        if not name or not email or not brand:
            st.error("Please fill all fields.")
        else:
            st.session_state.profile_created = True
            st.session_state.user_name = name
            st.session_state.user_email = email
            st.session_state.user_brand = brand
            st.session_state.user_gender = gender
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ---------------- PROFILE ICON ----------------
if st.session_state.user_gender == "Male":
    profile_icon = "https://i.postimg.cc/5tTtnXH0/Screenshot_2026_01_23_010056.png"
else:
    profile_icon = "https://i.postimg.cc/PrVnmBvh/Screenshot_2026_01_23_010324.png"

st.markdown(f"""
<div class="profile-icon">
    <img src="{profile_icon}" width="60">
</div>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
st.sidebar.markdown(f"👋 Hello, {st.session_state.user_name}")
menu = st.sidebar.radio("📌 Navigation", ["Home","Ad Studio","Billboard","Settings","License"])

# ---------------- HOME ----------------
if menu == "Home":

    st.markdown('<div class="main-title">AdForge AI Studio</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Create cinematic ads in seconds using AI</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🚀 Features")
    st.markdown("""
    • 🎬 AI Video Ads  
    • 🖼 Smart Billboard Generator  
    • 🎙 Voiceover AI  
    • ✍ Script Generator  
    • 🎨 Brand Styling  
    • 📊 Audience Targeting  
    • ⚡ Hackathon-ready UX  
    """)
    st.markdown("### 🔧 How It Works")
    st.markdown("""
    1️⃣ Enter your product  
    2️⃣ Generate slogan + script  
    3️⃣ Upload images  
    4️⃣ Generate poster or video  
    5️⃣ Download and share  
    """)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- AD STUDIO ----------------
elif menu == "Ad Studio":

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🎬 Ad Studio</div>', unsafe_allow_html=True)

    # -------- INPUTS --------
    product = st.text_input("Product / Topic")

    st.session_state.audience = st.selectbox(
        "Audience", ["General", "Youth", "Corporate", "Luxury"]
    )

    st.session_state.tone = st.selectbox(
        "Ad Tone", ["Corporate", "Funny", "Dramatic", "Luxury"]
    )

    st.session_state.cta = st.selectbox(
        "Call-To-Action", ["Buy Now", "Shop Today", "Learn More", "Download App"]
    )

    st.session_state.brand_color = st.color_picker(
        "Brand Color", st.session_state.brand_color
    )

    # -------- AI COPY --------
    if st.button("✨ Generate Slogan + Script"):
        if not product:
            st.error("Enter a product name.")
        else:
            st.session_state.slogan = generate_with_llama(f"slogan for {product}")
            st.session_state.script = generate_with_llama(f"script for {product}")
            st.success("AI content generated!")

    st.text_input("AI Slogan", value=st.session_state.slogan)
    script = st.text_area("AI Script", value=st.session_state.script, height=150)

    # -------- PRODUCT IMAGE --------
    st.markdown("### 🥤 Upload Product Image")
    prod = st.file_uploader("Product Image", type=["png", "jpg", "jpeg"])
    if prod:
        tmp_prod = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        tmp_prod.write(prod.read())
        st.session_state.product_img = tmp_prod.name
        st.image(st.session_state.product_img, width=200)

    # -------- VOICEOVER --------
    if st.button("🔊 Generate Voiceover"):
        if not script:
            st.error("Generate script first.")
        else:
            st.session_state.audio = generate_voiceover(script)
            st.audio(st.session_state.audio)
            st.success("Voiceover ready!")

    # -------- FINAL AD VIDEO --------
    if st.button("🎥 Generate AI Video"):
        if not st.session_state.audio or not st.session_state.product_img:
            st.error("Upload product image and generate voiceover first.")
        else:
            with st.spinner("Creating cinematic advertisement..."):
                video_path = generate_product_ad_video(
                    st.session_state.product_img,
                    st.session_state.audio,
                    st.session_state.slogan
                )

            if video_path:
                st.video(video_path)
                st.success("🎬 Advertisement video generated successfully!")

    st.markdown("</div>", unsafe_allow_html=True)
# ---------------- BILLBOARD ----------------
elif menu == "Billboard":

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🖼 Billboard Generator</div>', unsafe_allow_html=True)

    if st.button("🎨 Generate Decorative Billboard"):
        if not st.session_state.slogan:
            st.error("Generate slogan first.")
        else:
            img = generate_billboard(
                st.session_state.user_brand or "Product",
                st.session_state.slogan,
                st.session_state.brand_color,
                st.session_state.cta,
                st.session_state.product_img
            )

            st.session_state.billboard_img = img
            st.image(img, use_column_width=True)
            st.success("Billboard generated!")

    if st.session_state.billboard_img:
        with open(st.session_state.billboard_img, "rb") as f:
            st.download_button(
                "⬇ Download Billboard",
                f,
                file_name="adforge_billboard.png"
            )

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- SETTINGS ----------------
elif menu == "Settings":

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">⚙ Settings</div>', unsafe_allow_html=True)

    st.markdown("• Video resolution (coming soon)")
    st.markdown("• Background music (coming soon)")
    st.markdown("• Voice accents (coming soon)")
    st.markdown("• Ad history (coming soon)")

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- LICENSE ----------------
elif menu == "License":

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📜 License & Info</div>', unsafe_allow_html=True)

    st.markdown(f"""
    AdForge AI Studio – Hackathon Edition  
    User: {st.session_state.user_name}  
    Email: {st.session_state.user_email}  
    Brand: {st.session_state.user_brand}  
    """)

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- FOOTER ----------------
st.markdown('<div class="footer-nav">🚀 AdForge AI Studio — Hackathon Build</div>', unsafe_allow_html=True)
