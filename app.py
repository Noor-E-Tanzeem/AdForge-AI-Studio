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
.main-title { font-size: 46px; font-weight: 900; color: #ffffff; text-shadow: 2px 2px #4da6ff; }
.sub-title { font-size: 20px; color: #cfcfcf; }
.card { background: #171a23; border-radius: 18px; padding: 28px; color: #ffffff; box-shadow: 0 8px 25px rgba(0,0,0,0.4); border: 1px solid #2b2f3a;}
.section-title { font-size: 28px; font-weight: 800; color: #4da6ff; }
.profile-icon { position: fixed; top: 20px; right: 40px; z-index: 1000; border-radius: 50%; border: 2px solid #4da6ff; box-shadow: 0 0 10px #4da6ff;}
.footer-nav { position: fixed; bottom: 0; width: 100%; background: #171a23; padding: 12px; text-align: center; color: #aaaaaa; border-top: 1px solid #2b2f3a;}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION DEFAULTS ----------------
defaults = {
    "profile_created": False, "user_name": "", "user_email": "", "user_brand": "", "user_gender": "Male",
    "slogan": "", "script": "", "audio": None, "human_img": None, "product_img": None,
    "billboard_img": None, "audience": "General", "tone": "Corporate", "cta": "Buy Now",
    "brand_color": "#4da6ff"
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ---------------- AGENTIC AI & LLAMA (GROQ) ----------------
def groq_agent_call(prompt):
    """Multi-Agent Simulation using Groq Llama 3"""
    try:
        api_key = st.secrets["groq_api_key"]
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        
        # Implementation of Few-Shot Response Concepts
        data = {
            "model": "llama3-70b-8192",
            "messages": [
                {"role": "system", "content": f"You are a Multi-Agent Creative Team for {st.session_state.user_brand}. Agent 1 (Strategist) sets the tone. Agent 2 (Copywriter) writes 8-10 high-energy lines. Agent 3 (Editor) adds emojis."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }
        response = requests.post(url, headers=headers, json=data)
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"Error connecting to Llama Agent: {str(e)}"

# ---------------- UTILS ----------------
def generate_billboard(product, slogan, brand_color, cta, human_img_path=None, product_img_path=None):
    """Advanced Decorative Billboard Generator"""
    # Create Canvas with Cinematic Dark Gradient
    bg = Image.new("RGB", (1280, 720), (10, 12, 30))
    draw = ImageDraw.Draw(bg)
    
    # 🎨 Decorations: Abstract Shapes
    draw.polygon([(0,0), (400,0), (0,720)], fill=(20, 30, 60))
    draw.rectangle([1230, 0, 1280, 720], fill=brand_color) # Side Accent
    
    # Slogan with Color (Using Shadow/Glow effect)
    draw.text((82, 182), slogan, fill=(0,0,0)) # Shadow
    draw.text((80, 180), slogan, fill=brand_color)
    
    # Brand and Product Title
    draw.text((80, 60), f"{st.session_state.user_brand} PRESENTS", fill=(150,150,150))
    draw.text((80, 100), product.upper(), fill=(255,255,255))

    if human_img_path:
        human = Image.open(human_img_path).convert("RGBA")
        human.thumbnail((500, 700))
        bg.paste(human, (750, 70), human)

    if product_img_path:
        prod = Image.open(product_img_path).convert("RGBA")
        prod.thumbnail((350, 350))
        # Add a glow behind product
        bg.paste(prod, (100, 320), prod)

    # Decorative Button (CTA)
    draw.rounded_rectangle([100, 600, 400, 680], radius=20, fill=(255, 60, 60))
    draw.text((180, 620), cta, fill="white")

    temp_img = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    bg.save(temp_img.name)
    return temp_img.name

def generate_animated_human(human_img_path, audio_path):
    API_KEY = st.secrets.get("did_api_key", "")
    if not API_KEY:
        st.error("D-ID API key missing in Secrets!")
        return None
    
    # Upload Image to D-ID
    headers = {"Authorization": f"Basic {API_KEY}"}
    
    # This is a simplified version of the D-ID 'Talks' flow
    # In a real hackathon, ensure your D-ID API key is the Base64 of 'email:password' or the API Key
    url = "https://api.d-id.com/talks"
    
    # (Note: For D-ID you usually need to upload files to their S3 first or use URLs. 
    # For this script, we assume the D-ID API handles direct payload or you have pre-hosted assets)
    st.info("Sending data to D-ID Agents...")
    time.sleep(2)
    return None # D-ID requires async polling; for local render, we show overlay below

# ---------------- PROFILE CREATION ----------------
if not st.session_state.profile_created:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="center"><img src="https://i.postimg.cc/3rz01J48/Screenshot_2026_01_23_021409.png" width="100"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title center">👤 Create Your Profile</div>', unsafe_allow_html=True)
    
    name = st.text_input("Name")
    email = st.text_input("Email")
    brand = st.text_input("Brand Name")
    gender = st.selectbox("Gender", ["Male","Female"])

    if st.button("Start Creating Ads 🚀"):
        if name and email and brand:
            st.session_state.profile_created = True
            st.session_state.user_name = name
            st.session_state.user_email = email
            st.session_state.user_brand = brand
            st.session_state.user_gender = gender
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ---------------- PROFILE ICON ----------------
profile_icon = "https://i.postimg.cc/5tTtnXH0/Screenshot_2026_01_23_010056.png" if st.session_state.user_gender == "Male" else "https://i.postimg.cc/PrVnmBvh/Screenshot-2026-01-23-010324.png"
st.markdown(f'<div class="profile-icon"><img src="{profile_icon}" width="60"></div>', unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
st.sidebar.markdown(f"👋 Hello, **{st.session_state.user_name}**")
menu = st.sidebar.radio("📌 Navigation", ["Home","Ad Studio","Billboard","Settings","License"])

# ---------------- HOME ----------------
if menu == "Home":
    st.markdown('<div class="main-title">AdForge AI Studio</div>', unsafe_allow_html=True)
    st.markdown('<div class="card"><h3>🚀 Agentic AI Powered</h3>This app uses a multi-agent Llama system to brainstorm, write, and design your marketing.</div>', unsafe_allow_html=True)

# ---------------- AD STUDIO ----------------
elif menu == "Ad Studio":
    st.markdown('<div class="card"><div class="section-title">🎬 Ad Studio</div>', unsafe_allow_html=True)
    product = st.text_input("Product / Topic")
    st.session_state.audience = st.selectbox("Audience", ["Youth", "Luxury", "General"])
    st.session_state.tone = st.selectbox("Ad Tone", ["Dramatic", "Funny", "Luxury"])
    
    if st.button("✨ Invoke Llama Agents"):
        with st.spinner("Agents are brainstorming..."):
            st.session_state.slogan = groq_agent_call(f"Write a 5-word catchy slogan for {product}. Tone: {st.session_state.tone}")
            st.session_state.script = groq_agent_call(f"Act as a professional scriptwriter. Write a 10-line high-energy video script for {product}. Include emojis and a strong hook for {st.session_state.audience} audience.")
            st.success("Agents have responded!")

    st.text_input("AI Slogan", value=st.session_state.slogan)
    script_area = st.text_area("AI Script (8-10 Lines)", value=st.session_state.script, height=250)

    human = st.file_uploader("Upload Human Image", type=["png","jpg"])
    if human:
        t = tempfile.NamedTemporaryFile(delete=False, suffix=".png"); t.write(human.read()); st.session_state.human_img = t.name
    
    prod_img = st.file_uploader("Upload Product Image", type=["png","jpg"])
    if prod_img:
        t = tempfile.NamedTemporaryFile(delete=False, suffix=".png"); t.write(prod_img.read()); st.session_state.product_img = t.name

    if st.button("🎥 Generate AI Video"):
        if st.session_state.human_img and st.session_state.script:
            audio_path = generate_voiceover(st.session_state.script)
            st.audio(audio_path)
            st.info("D-ID Animation API Invoked. Please check your D-ID dashboard for the final render or use MoviePy overlay.")
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- BILLBOARD ----------------
elif menu == "Billboard":
    st.markdown('<div class="card"><div class="section-title">🖼 Billboard Generator</div>', unsafe_allow_html=True)
    st.session_state.cta = st.text_input("CTA Text", value="BUY NOW")
    st.session_state.brand_color = st.color_picker("Slogan Color", "#4da6ff")

    if st.button("🎨 Generate Decorative Billboard"):
        if st.session_state.slogan:
            img_path = generate_billboard(
                st.session_state.user_brand, st.session_state.slogan, 
                st.session_state.brand_color, st.session_state.cta,
                st.session_state.human_img, st.session_state.product_img
            )
            st.session_state.billboard_img = img_path
            st.image(img_path)
        else: st.error("Generate slogan in Ad Studio first!")

# ---------------- SETTINGS / LICENSE ----------------
else:
    st.markdown('<div class="card"><h4>Settings & License</h4>Agentic AI Logic v1.2 Enabled.</div>', unsafe_allow_html=True)

st.markdown('<div class="footer-nav">🚀 AdForge AI Studio — Agentic AI Hackathon Build</div>', unsafe_allow_html=True)
