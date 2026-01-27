import streamlit as st
import tempfile
import requests
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import base64
import random 
import tempfile
import os
import textwrap

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

st.markdown("""
<style>
/* Sidebar base */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0e0f14, #12141c);
}

/* Profile card */
.sidebar-profile {
    text-align: center;
    padding: 18px 12px;
    margin-bottom: 12px;
    border-bottom: 1px solid #2b2f3a;
    animation: fadeIn 0.6s ease-in-out;
}

.sidebar-profile img {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    object-fit: cover;
    border: 3px solid #4da6ff;
    box-shadow: 0 8px 20px rgba(0,0,0,0.6);
}

.sidebar-name {
    margin-top: 10px;
    font-weight: 700;
    font-size: 16px;
    color: #ffffff;
}

.sidebar-brand {
    font-size: 12px;
    color: #9aa4b2;
}

/* Badge */
.badge {
    display: inline-block;
    margin-top: 6px;
    padding: 4px 10px;
    font-size: 11px;
    font-weight: 700;
    border-radius: 999px;
    background: linear-gradient(135deg, #4da6ff, #6f7cff);
    color: white;
}

/* Animation */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(-6px); }
    to { opacity: 1; transform: translateY(0); }
}
</style>
""", unsafe_allow_html=True)
# ---------------- SESSION DEFAULTS ----------------
defaults = {
    # ---- PROFILE ----
    "profile_created": False,
    "user_name": "",
    "user_email": "",
    "user_brand": "",
    "user_gender": "Male",

    # ---- AI CONTENT ----
    "slogan": "",
    "script": "",

    # ---- MEDIA ----
    "audio": None,
    "human_img": None,
    "product_img": None,
    "billboard_img": None,

    # ---- AD SETTINGS ----
    "audience": "General",
    "tone": "Corporate",
    "cta": "Buy Now",
    "brand_color": "#4da6ff",

    # ---- FEEDBACK SYSTEM ----
    "rating": 0,
    "review": "",
    "feedback_submitted": False
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value
# ---------------- PROFILE CREATION GATE ----------------
if not st.session_state.profile_created:

    st.markdown(
        """
        <div style="
            max-width:420px;
            margin:80px auto;
            background:#171a23;
            padding:32px;
            border-radius:18px;
            box-shadow:0 10px 30px rgba(0,0,0,0.6);
        ">
            <h2 style="text-align:center; margin-bottom:6px;">
                👤 Create Your Profile
            </h2>
            <p style="text-align:center; color:#cfcfcf; margin-bottom:24px;">
                Set up your identity to start creating ads
            </p>
        """,
        unsafe_allow_html=True
    )

    name = st.text_input("Your Name")
    email = st.text_input("Email Address")
    brand = st.text_input("Brand / Company Name")
    gender = st.selectbox("Gender", ["Male", "Female"])

    if st.button("🚀 Enter AdForge"):
        if not name or not email or not brand:
            st.error("Please fill all fields.")
        else:
            st.session_state.user_name = name
            st.session_state.user_email = email
            st.session_state.user_brand = brand
            st.session_state.user_gender = gender
            st.session_state.profile_created = True
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    st.stop()


# ---------------- UTILS ----------------
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
        try:
            prod = Image.open(product_img).resize((260, 260))
            bg.paste(prod, (40, 400))
        except:
            pass

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    bg.save(tmp.name)
    return tmp.name
def generate_with_llama(content_type, product, audience, tone):
    GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")

    if not GROQ_API_KEY:
        st.error("Missing GROQ API key")
        st.stop()

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    system_prompt = """
    You are an elite advertising creative director.
    Every output must be unique.
    Avoid generic phrases.
    """

    if content_type == "slogan":
        user_prompt = f"""
        Product: {product}
        Audience: {audience}
        Tone: {tone}

        Generate ONE punchy slogan.
        Max 10 words.
        """
        max_tokens = 80
    else:
        user_prompt = f"""
        Product: {product}
        Audience: {audience}
        Tone: {tone}

        Write a cinematic ad script.
        7–9 short lines.
        No brackets, no stage directions.
        """
        max_tokens = 300

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 1.2,
        "max_tokens": max_tokens
    }

    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=30
    )

    data = r.json()

    if "choices" not in data:
        raise RuntimeError(data)

    return data["choices"][0]["message"]["content"].strip()
import re
from moviepy.audio.fx.all import volumex, audio_loop
from moviepy.editor import CompositeAudioClip

def clean_script_for_voice(text):
    text = re.sub(r"\(.*?\)", "", text)
    text = re.sub(r"\[.*?\]", "", text)
    text = re.sub(r"\*.*?\*", "", text)
    return text.strip()

def generate_voiceover(text):
    clean_text = clean_script_for_voice(text)
    tts = gTTS(text=clean_text, lang="en")
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(tmp.name)
    return tmp.name
 

def make_text_image(
    text,
    size=(1000, 160),
    max_font_size=64,
    min_font_size=28
):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    for font_size in range(max_font_size, min_font_size, -2):
        try:
            font = ImageFont.truetype("DejaVuSans-Bold.ttf", font_size)
        except:
            font = ImageFont.load_default()

        wrapped = textwrap.fill(text, width=22)
        bbox = draw.multiline_textbbox((0, 0), wrapped, font=font, spacing=6)

        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

        if text_w <= size[0] - 40 and text_h <= size[1] - 20:
            draw.multiline_text(
                ((size[0] - text_w)//2, (size[1] - text_h)//2),
                wrapped,
                font=font,
                fill=(255, 215, 0, 255),
                align="center",
                spacing=6
            )
            return img

    draw.text((20, size[1]//2), text[:30], fill="yellow")
    return img

def generate_product_ad_video(product_img_path, voice_path, slogan, tone):
    # ---------- LOAD VOICE ----------
    voice = AudioFileClip(voice_path)
    voice = volumex(voice, 1.3)

    # ---------- OPTIONAL BGM ----------
    try:
        bgm = AudioFileClip("assets/bgm/default.mp3")
        bgm = audio_loop(bgm, duration=voice.duration)
        bgm = volumex(bgm, 0.25)
        final_audio = CompositeAudioClip([bgm, voice])
    except:
        final_audio = voice

    total_duration = final_audio.duration

    # ---------- BACKGROUND ----------
    bg = ColorClip((1280, 720), color=(10, 10, 20)).set_duration(total_duration)

    overlay = (
        ColorClip((1280, 720), color=(0, 0, 0))
        .set_opacity(0.25)
        .set_duration(total_duration)
    )

    top_bar = (
        ColorClip((1280, 80), color=(0, 0, 0))
        .set_position(("center", "top"))
        .set_duration(total_duration)
    )

    bottom_bar = (
        ColorClip((1280, 80), color=(0, 0, 0))
        .set_position(("center", "bottom"))
        .set_duration(total_duration)
    )

    # ---------- PRODUCT IMAGE ----------
    img = Image.open(product_img_path).convert("RGBA")
    img = img.resize((520, 520))

    tmp_img = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    img.save(tmp_img.name)

# ---------- PRODUCT CLIP ----------
   product_clip = (
        ImageClip(tmp_img.name)
        .set_duration(total_duration)
        .set_position(lambda t: (
            "center",
            360 - int(8 * t)   # cinematic vertical drift
        ))
        .fadein(0.8)
        .fadeout(0.8)
    )
    # ---------- TEXT ----------
    lines = [
        l.strip()
        for l in clean_script_for_voice(st.session_state.script).split("\n")
        if l.strip()
    ]

    per_line = max(1.6, voice.duration / max(len(lines), 1))
    text_clips = []
    t = 0

    for i, line in enumerate(lines):
        size = (1000, 220) if i == 0 else (900, 160)

        txt_img = make_text_image(line.upper(), size=size)
        tmp_txt = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        txt_img.save(tmp_txt.name)

        clip = (
            ImageClip(tmp_txt.name)
            .set_start(t)
            .set_duration(per_line)
            .set_position(("center", 500))
            .fadein(0.4)
            .fadeout(0.4)
        )

        text_clips.append(clip)
        t += per_line
    # ---------- FINAL VIDEO ----------
    final_video = CompositeVideoClip(
        [bg, product_clip, overlay, top_bar, bottom_bar] + text_clips
    ).set_audio(final_audio)

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
# ---------------- PROFILE ICON ----------------
if st.session_state.user_gender == "Male":
    profile_icon = "https://i.postimg.cc/5tTtnXH0/Screenshot_2026_01_23_010056.png"
else:
    profile_icon = "https://i.postimg.cc/PrVnmBvh/Screenshot_2026_01_23_010324.png"


# ---------------- SIDEBAR ----------------
st.sidebar.markdown(
    f"""
    <div class="sidebar-profile">
        <img src="{profile_icon}">
        <div class="sidebar-name">
            {st.session_state.user_name}
        </div>
        <div class="sidebar-brand">
            {st.session_state.user_brand}
        </div>
        <div class="badge">
            🚀 Hackathon
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ---- DROPDOWN MENU ----
profile_action = st.sidebar.selectbox(
    "Account",
    ["— Select —", "⚙ Settings", "🚪 Logout"],
    label_visibility="collapsed"
)

if profile_action == "🚪 Logout":
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.rerun()

menu = st.sidebar.radio(
    "📌 Navigation",
    ["Home", "Ad Studio", "Billboard", "Settings", "License"]
)
# ---------------- HOME ----------------
if menu == "Home":

    # ===== HERO SECTION =====
    col1, col2 = st.columns([1.2, 1])

    with col1:
        st.markdown("""
        <div style="margin-top:20px;">
            <h1 style="font-size:50px; font-weight:900; margin-bottom:12px;">
                AdForge AI Studio
            </h1>

            <p style="font-size:19px; color:#cfcfcf; max-width:520px;">
                Create cinematic AI advertisements, smart billboards, and
                motion promo videos in seconds — no editing skills required.
            </p>

            <div style="margin-top:18px; opacity:0.85; font-size:15px;">
                🚀 Hackathon Build &nbsp; • &nbsp;
                ⚡ AI-Powered &nbsp; • &nbsp;
                🎯 Creator-Focused
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.image(
            "https://i.postimg.cc/CLnTFRX1/Screenshot_2026_01_22_232250.png",
            width=320
        )

    st.markdown("<br><br>", unsafe_allow_html=True)

    # ===== FEATURES =====
    st.markdown("## 🚀 Key Features")

    f1, f2, f3 = st.columns(3)

    with f1:
        st.markdown("""
        🎬 **AI Video Ads**  
        Motion scenes, transitions & voiceover
        """)

    with f2:
        st.markdown("""
        🖼 **Smart Billboard Generator**  
        Posters with brand colors & CTA
        """)

    with f3:
        st.markdown("""
        🎙 **Script & Voice AI**  
        Cinematic ad copy + narration
        """)

    st.markdown("<br>", unsafe_allow_html=True)

    f4, f5, f6 = st.columns(3)

    with f4:
        st.markdown("""
        🎨 **Brand Styling**  
        Themes, tone & call-to-action
        """)

    with f5:
        st.markdown("""
        📊 **Audience Targeting**  
        Youth, corporate, luxury, general
        """)

    with f6:
        st.markdown("""
        ⚡ **Hackathon-Ready UX**  
        Fast, clean, production-style UI
        """)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # ===== HOW IT WORKS =====
    st.markdown("## 🛠 How It Works")

    st.markdown("""
    **1️⃣ Enter your product or idea**  
    **2️⃣ Generate AI slogan & script**  
    **3️⃣ Upload product image**  
    **4️⃣ Create AI video or billboard**  
    **5️⃣ Download, review & share**
    """)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # ===== SAMPLE OUTPUT PREVIEW =====
    st.markdown("## 🔥 What You Can Create")

    p1, p2 = st.columns(2)

    with p1:
        st.image(
            "https://i.postimg.cc/k5PbY3Q4/Screenshot_2026_01_24_031122.png",
            width=340,
            caption="AI-Generated Billboard"
        )

    with p2:
        st.image(
            "https://i.postimg.cc/c1k8y87G/Screenshot_2026_01_24_031153.png",
            width=340,
            caption="AI Video Advertisement"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <div style="opacity:0.65; font-size:14px;">
        AdForge AI Studio — Built for Hackathons & Real-World AI Demos
    </div>
    """, unsafe_allow_html=True)
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
            with st.spinner("Generating AI content..."):
                st.session_state.slogan = generate_with_llama(
                    "slogan",
                    product,
                    st.session_state.audience,
                    st.session_state.tone
                )

                st.session_state.script = generate_with_llama(
                    "script",
                    product,
                    st.session_state.audience,
                    st.session_state.tone
                )

            st.success("AI slogan & script generated!")

    # -------- SHOW GENERATED TEXT --------
    st.text_input(
        "AI Slogan",
        value=st.session_state.slogan
    )

    st.text_area(
        "AI Script",
        value=st.session_state.script,
        height=280
    )

    # -------- VOICEOVER --------
    if st.button("🔊 Generate Voiceover"):
        if not st.session_state.script:
            st.error("Generate script first.")
        else:
            with st.spinner("Generating voiceover..."):
                st.session_state.audio = generate_voiceover(
                    st.session_state.script
                )

            st.audio(st.session_state.audio)
            st.success("Voiceover generated!")

    # -------- PRODUCT IMAGE --------
    st.markdown("### 🥤 Upload Product Image")

    prod = st.file_uploader(
        "Product Image",
        type=["png", "jpg", "jpeg"]
    )

    if prod is not None:
        tmp_prod = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        tmp_prod.write(prod.read())
        tmp_prod.close()

        st.session_state.product_img = tmp_prod.name
        st.image(st.session_state.product_img, width=200)

    # -------- AI VIDEO GENERATION --------
    st.markdown("### 🎬 Generate AI Video")

    if st.button("🎥 Generate AI Video"):
        if not st.session_state.audio:
            st.error("Generate voiceover first.")
        elif not st.session_state.product_img:
            st.error("Upload product image first.")
        else:
            with st.spinner("Creating cinematic AI video..."):
                video_path = generate_product_ad_video(
    st.session_state.product_img,
    st.session_state.audio,
    st.session_state.slogan,
    st.session_state.tone
)

            st.video(video_path)
            st.success("🎉 AI video generated successfully!")

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
    st.markdown('<div class="section-title">⚙️ Settings</div>', unsafe_allow_html=True)

    # -------- ACCOUNT --------
    st.markdown("### 👤 Account")
    st.text_input("Name", value=st.session_state.user_name, disabled=True)
    st.text_input("Email", value=st.session_state.user_email, disabled=True)
    st.text_input("Brand", value=st.session_state.user_brand, disabled=True)

    st.divider()
# ---------------- LICENSE ----------------
elif menu == "License":

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📜 License & Usage</div>', unsafe_allow_html=True)

    st.markdown("""
    ### 🔐 Application License

    **AdForge AI Studio** is a hackathon prototype built for **educational and demonstration purposes**.

    ### 🤖 AI Models
    - Uses **LLaMA model** via **Groq API**
    - Model is accessed through API calls
    - No model training or fine-tuning is done locally

    ### 📦 Libraries Used
    - Streamlit (UI framework)
    - MoviePy (video generation)
    - PIL (image processing)
    - gTTS (text-to-speech)

    All libraries are open-source and used according to their licenses.

    ### 🎵 Media Usage
    - Background music is **royalty-free**
    - Used only for demo purposes

    ### ⚠ Disclaimer
    - Generated content is AI-based
    - Not intended for commercial or legal use
    - This is a prototype, not a deployed product

    ---
    © 2026 AdForge AI Studio – Hackathon Build
    """)

    st.markdown('</div>', unsafe_allow_html=True)
    # -------- PREFERENCES --------
    st.markdown("### 🎨 Preferences")

    theme = st.selectbox(
        "App Theme",
        ["Dark (Default)", "Light (Coming Soon)"],
        disabled=True
    )

    default_tone = st.selectbox(
        "Default Ad Tone",
        ["Corporate", "Funny", "Dramatic", "Luxury"],
        index=["Corporate", "Funny", "Dramatic", "Luxury"].index(st.session_state.tone)
    )

    default_cta = st.selectbox(
        "Default Call-To-Action",
        ["Buy Now", "Shop Today", "Learn More", "Download App"],
        index=["Buy Now", "Shop Today", "Learn More", "Download App"].index(st.session_state.cta)
    )

    if st.button("💾 Save Preferences"):
        st.session_state.tone = default_tone
        st.session_state.cta = default_cta
        st.success("Preferences saved!")

    st.divider()

    # -------- FEEDBACK --------
    st.markdown("### ⭐ Rate AdForge AI")

    if not st.session_state.feedback_submitted:
        rating = st.slider("Your Rating", 1, 5, st.session_state.rating)
        review = st.text_area(
            "Your Feedback",
            placeholder="What did you like? What can be better?"
        )

        if st.button("Submit Feedback"):
            st.session_state.rating = rating
            st.session_state.review = review
            st.session_state.feedback_submitted = True
            st.success("Thanks for your feedback! 🙌")

    else:
        st.success("✅ Feedback already submitted")
        st.markdown(f"**Rating:** ⭐ {st.session_state.rating}/5")
        st.markdown(f"**Review:** {st.session_state.review or '—'}")

    st.divider()

    # -------- DANGER ZONE --------
    st.markdown("### ⚠️ Danger Zone")

    if st.button("🚪 Log Out"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
