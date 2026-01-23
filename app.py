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
        ImageClip, VideoFileClip, CompositeVideoClip,
        TextClip, ColorClip, concatenate_videoclips
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
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=20
        )

        data = response.json()
        if "choices" not in data:
            return fallback_copy(prompt)

        return data["choices"][0]["message"]["content"].strip()

    except Exception:
        return fallback_copy(prompt)
        def fallback_copy(prompt):
    if "slogan" in prompt.lower():
        product = prompt.replace("slogan for", "").strip()
        return f"{product.capitalize()} that’s ready when you are."

    if "script" in prompt.lower():
        product = prompt.replace("script for", "").strip()
        return (
            f"This is not just {product}.\n"
            f"It’s designed for real-life moments.\n"
            f"Built to perform when it matters.\n"
            f"Simple, strong, and dependable.\n"
            f"Wherever you go, stay confident.\n"
            f"Prepared for the unexpected.\n"
            f"Choose reliability."
        )

    return "Smart. Simple. Reliable."
def generate_voiceover(text):
    tts = gTTS(text=text, lang="en")
    temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_audio.name)
    return temp_audio.name

def generate_billboard(product, slogan, brand_color, cta, human_img=None, product_img=None):
    """
    Multimodal Billboard Generator
    Uses real-world billboard images (search-based) + AI overlay
    """

    # ---- STEP 1: SEARCH REAL BILLBOARD IMAGE ----
    search_query = f"{product} advertising billboard"
    bing_url = f"https://www.bing.com/images/search?q={search_query}&form=HDRSC2"

    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        html = requests.get(bing_url, headers=headers).text

        # crude but effective image scrape
        img_urls = []
        for line in html.split('"'):
            if line.startswith("https") and ("jpg" in line or "png" in line):
                img_urls.append(line)

        if not img_urls:
            raise Exception("No images found")

        img_url = random.choice(img_urls[:10])
        response = requests.get(img_url, headers=headers, timeout=10)
        bg = Image.open(BytesIO(response.content)).convert("RGB").resize((1280, 720))

    except Exception:
        # fallback background
        bg = Image.new("RGB", (1280, 720), (20, 20, 40))

    draw = ImageDraw.Draw(bg)

    # ---- STEP 2: LOAD FONTS ----
    try:
        font_title = ImageFont.truetype("DejaVuSans-Bold.ttf", 64)
        font_slogan = ImageFont.truetype("DejaVuSans-Bold.ttf", 46)
        font_cta = ImageFont.truetype("DejaVuSans-Bold.ttf", 42)
    except:
        font_title = font_slogan = font_cta = ImageFont.load_default()

    # ---- STEP 3: DECORATIVE OVERLAY ----
    overlay = Image.new("RGBA", bg.size, (0, 0, 0, 120))
    bg = Image.alpha_composite(bg.convert("RGBA"), overlay)

    draw = ImageDraw.Draw(bg)

    # ---- STEP 4: BRAND TEXT ----
    draw.text((40, 40), product.upper(), fill=(255,255,255), font=font_title)
    draw.text((40, 130), slogan, fill=(255, 215, 0), font=font_slogan)

    # ---- STEP 5: CTA BUTTON ----
    draw.rounded_rectangle([900, 560, 1220, 650], radius=35, fill=(255,80,80))
    w, h = draw.textsize(cta, font=font_cta)
    draw.text((1060 - w//2, 585), cta, fill=(255,255,255), font=font_cta)

    # ---- STEP 6: OPTIONAL PRODUCT IMAGE ----
    if product_img:
        prod = Image.open(product_img).convert("RGBA").resize((260,260))
        bg.paste(prod, (40, 420), prod)

    # ---- SAVE ----
    temp_img = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    bg.convert("RGB").save(temp_img.name)
    return temp_img.name

def generate_animated_human(human_img_path, audio_path):
    API_KEY = st.secrets.get("did_api_key", "")
    if not API_KEY:
        st.warning("D-ID API key missing. Video disabled.")
        return None

    url = "https://api.d-id.com/talks"

    with open(human_img_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("utf-8")
    with open(audio_path, "rb") as f:
        audio_b64 = base64.b64encode(f.read()).decode("utf-8")

    payload = {"source_image": img_b64, "driver_audio": audio_b64}
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type":"application/json"}

    resp = requests.post(url, json=payload, headers=headers).json()

    if "result_url" in resp:
        data = requests.get(resp["result_url"]).content
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        tmp.write(data)
        return tmp.name

    return None

def add_product_overlay(talking_video_path, product_img_path, slogan):
    if not MOVIEPY_OK:
        st.warning("MoviePy missing. Video disabled.")
        return None

    from moviepy.editor import (
        VideoFileClip, ImageClip, TextClip,
        CompositeVideoClip, ColorClip, concatenate_videoclips
    )

    # ---------- LOAD TALKING VIDEO ----------
    talk_clip = VideoFileClip(talking_video_path)

    W, H = talk_clip.size

    clips = []

    # ==============================
    # 🎬 SCENE 1 — HOOK (INTRO)
    # ==============================
    bg_intro = ColorClip(size=(W, H), color=(10, 10, 30)).set_duration(3)

    text_intro = TextClip(
        slogan,
        fontsize=70,
        color='white',
        font='DejaVu-Sans-Bold',
        method='caption',
        size=(W-200, None)
    ).set_position('center').set_duration(3)

    intro_scene = CompositeVideoClip([bg_intro, text_intro])
    clips.append(intro_scene)

    # ==============================
    # 🎬 SCENE 2 — MAIN AD (TALKING HUMAN)
    # ==============================
    talk = talk_clip.resize(width=W)

    layers = [talk]

    # Product floating overlay
    if product_img_path:
        product_clip = (
            ImageClip(product_img_path)
            .set_duration(talk.duration)
            .resize(height=220)
            .set_position(("right", "bottom"))
        )
        layers.append(product_clip)

    # Branding slogan overlay
    slogan_clip = (
        TextClip(
            slogan,
            fontsize=42,
            color='yellow',
            font='DejaVu-Sans-Bold',
            method='caption',
            size=(W-100, None)
        )
        .set_position(("center", 30))
        .set_duration(talk.duration)
    )

    layers.append(slogan_clip)

    main_scene = CompositeVideoClip(layers)
    clips.append(main_scene)

    # ==============================
    # 🎬 SCENE 3 — CTA ENDING
    # ==============================
    bg_outro = ColorClip(size=(W, H), color=(30, 0, 0)).set_duration(3)

    end_text = TextClip(
        "Experience the Future.\nAct Now.",
        fontsize=60,
        color='white',
        font='DejaVu-Sans-Bold',
        method='caption',
        size=(W-200, None)
    ).set_position('center').set_duration(3)

    outro_layers = [bg_outro, end_text]

    if product_img_path:
        prod_big = (
            ImageClip(product_img_path)
            .set_duration(3)
            .resize(height=320)
            .set_position(("center", "bottom"))
        )
        outro_layers.append(prod_big)

    outro_scene = CompositeVideoClip(outro_layers)
    clips.append(outro_scene)

    # ==============================
    # 🎬 FINAL COMPOSITION
    # ==============================
    final_video = concatenate_videoclips(clips, method="compose")

    tmp_final = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    final_video.write_videofile(
        tmp_final.name,
        fps=24,
        codec="libx264",
        audio_codec="aac"
    )

    return tmp_final.name

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

    product = st.text_input("Product / Topic")
    st.session_state.audience = st.selectbox("Audience", ["General","Youth","Corporate","Luxury"])
    st.session_state.tone = st.selectbox("Ad Tone", ["Corporate","Funny","Dramatic","Luxury"])
    st.session_state.cta = st.selectbox("Call-To-Action", ["Buy Now","Shop Today","Learn More","Download App"])
    st.session_state.brand_color = st.color_picker("Brand Color", st.session_state.brand_color)

    if st.button("✨ Generate Slogan + Script"):
        if not product:
            st.error("Enter a product.")
        else:
            st.session_state.slogan = generate_with_llama(f"slogan for {product}")
            st.session_state.script = generate_with_llama(f"script for {product}")
            st.success("AI content generated!")

    st.text_input("AI Slogan", value=st.session_state.slogan or "")
    script = st.text_area("AI Script", value=st.session_state.script or "", height=120)

    st.markdown("### 🧑 Upload Human Image")
    human = st.file_uploader("Human Image", type=["png","jpg","jpeg"])
    if human:
        tmp_human = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        tmp_human.write(human.read())
        st.session_state.human_img = tmp_human.name

    st.markdown("### 🥤 Upload Product Image")
    prod = st.file_uploader("Product Image", type=["png","jpg","jpeg"])
    if prod:
        tmp_prod = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        tmp_prod.write(prod.read())
        st.session_state.product_img = tmp_prod.name

    if st.button("🔊 Generate Voiceover"):
        if not script:
            st.error("Generate script first.")
        else:
            st.session_state.audio = generate_voiceover(script)
            st.audio(st.session_state.audio)
            st.success("Voiceover ready!")

    if st.button("🎥 Generate AI Video"):
        if not st.session_state.audio or not st.session_state.human_img:
            st.error("Upload human image + generate voice.")
        else:
            talking_video = generate_animated_human(st.session_state.human_img, st.session_state.audio)
            if talking_video:
                final_video = add_product_overlay(talking_video, st.session_state.product_img, st.session_state.slogan)
                if final_video:
                    st.video(final_video)
                    st.success("AI Video Generated!")

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
                st.session_state.human_img,
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
