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

    # -------- Scene timing --------
    t1 = 2
    t2 = 3
    t3 = 3
    t4 = max(2, total_duration - (t1 + t2 + t3))

    # ================= SCENE 1 — HOOK =================
    scene1_bg = ColorClip(
        size=(1280, 720),
        color=(10, 10, 20)
    ).set_duration(t1)

    hook_img = make_text_image("MADE FOR REAL LIFE")
    tmp_hook = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    hook_img.save(tmp_hook.name)

    hook_clip = (
        ImageClip(tmp_hook.name)
        .set_position("center")
        .set_duration(t1)
        .fadein(0.6)
    )

    scene1 = CompositeVideoClip([scene1_bg, hook_clip])

    # ================= SCENE 2 — PRODUCT REVEAL =================
    img = Image.open(product_img_path).convert("RGBA")
    w, h = img.size
    new_h = 360
    new_w = int((new_h / h) * w)
    img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

    tmp_prod = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    img.save(tmp_prod.name)

    scene2_bg = ColorClip(
        size=(1280, 720),
        color=(20, 20, 40)
    ).set_duration(t2)

    product_clip = (
        ImageClip(tmp_prod.name)
        .set_position(lambda t: (
            400 + int(140 * (t / t2)),   # slide-in
            220 + int(6 * (-1) ** int(t * 2))  # subtle float
        ))
        .set_duration(t2)
    )

    slogan_img = make_text_image(slogan.upper())
    tmp_slogan = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    slogan_img.save(tmp_slogan.name)

    slogan_clip = (
        ImageClip(tmp_slogan.name)
        .set_position(lambda t: ("center", int(130 - 40 * min(t, 1))))
        .set_duration(t2)
        .fadein(0.6)
    )

    overlay = ColorClip(
        size=(1280, 720),
        color=(0, 0, 0)
    ).set_opacity(0.25).set_duration(t2)

    scene2 = CompositeVideoClip([
        scene2_bg,
        overlay,
        product_clip,
        slogan_clip
    ])

    # ================= SCENE 3 — VALUE =================
    scene3_bg = ColorClip(
        size=(1280, 720),
        color=(30, 30, 50)
    ).set_duration(t3)

    value_img = make_text_image("SIMPLE. STRONG. RELIABLE.")
    tmp_value = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    value_img.save(tmp_value.name)

    value_clip = (
        ImageClip(tmp_value.name)
        .set_position("center")
        .set_duration(t3)
        .fadein(0.6)
    )

    scene3 = CompositeVideoClip([scene3_bg, value_clip])

    # ================= SCENE 4 — CTA =================
    scene4_bg = ColorClip(
        size=(1280, 720),
        color=(0, 0, 0)
    ).set_duration(t4)

    cta_img = make_text_image("EXPERIENCE IT TODAY")
    tmp_cta = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    cta_img.save(tmp_cta.name)

    cta_clip = (
        ImageClip(tmp_cta.name)
        .set_position("center")
        .set_duration(t4)
        .fadein(0.6)
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
    st.markdown('<div class="section-title">⚙️ Settings</div>', unsafe_allow_html=True)

    # -------- ACCOUNT --------
    st.markdown("### 👤 Account")
    st.text_input("Name", value=st.session_state.user_name, disabled=True)
    st.text_input("Email", value=st.session_state.user_email, disabled=True)
    st.text_input("Brand", value=st.session_state.user_brand, disabled=True)

    st.divider()

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
