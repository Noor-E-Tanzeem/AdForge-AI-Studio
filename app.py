import streamlit as st
import tempfile
import requests
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO
import base64
import random
import time

# ---------- CINEMATIC RENDERING ENGINE ----------
def create_luxury_billboard(brand, slogan, product_img_path):
    # Base Canvas: Deep Midnight Gradient
    canvas = Image.new("RGB", (1280, 720), (5, 5, 15))
    draw = ImageDraw.Draw(canvas)
    
    # 🎨 AGENTIC DESIGN: Layer 1 - Geometric Depth
    for i in range(0, 1280, 40):
        draw.line([(i, 0), (i - 200, 720)], fill=(15, 20, 45), width=1)
    
    # Layer 2: Glowing Brand Accent
    draw.rectangle([1250, 0, 1280, 720], fill="#4da6ff")
    
    # Layer 3: Product Integration with Soft Glow
    if product_img_path:
        prod = Image.open(product_img_path).convert("RGBA")
        prod.thumbnail((550, 550))
        # Create a glow effect
        glow = Image.new("RGBA", (600, 600), (77, 166, 255, 30))
        canvas.paste(glow, (650, 60), glow)
        canvas.paste(prod, (680, 100), prod)

    # Layer 4: Typography Agent
    # We use high-contrast white and brand-color text
    draw.text((60, 100), brand.upper(), fill="#4da6ff")
    draw.text((60, 140), "PREMIUM SELECTION", fill=(100, 100, 120))
    
    # Split slogan into lines if too long
    words = slogan.split()
    line1 = " ".join(words[:len(words)//2])
    line2 = " ".join(words[len(words)//2:])
    draw.text((60, 250), line1, fill="white")
    draw.text((60, 320), line2, fill="white")

    # Layer 5: Interactive CTA
    draw.rounded_rectangle([60, 550, 350, 630], radius=15, fill="#ff4b4b")
    draw.text((120, 575), "ORDER NOW", fill="white")

    temp_path = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name
    canvas.save(temp_path)
    return temp_path

# ---------------- CONFIG & CSS ----------------
st.set_page_config(page_title="AdForge AI Studio", page_icon="🚀", layout="wide")

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #0e0f14; }
    
    /* FIX: Full Visibility Profile Icon */
    .profile-container {
        position: fixed;
        top: 20px;
        right: 40px;
        z-index: 1000;
        text-align: center;
    }
    .profile-img {
        width: 70px;
        height: 70px;
        border-radius: 50%;
        border: 3px solid #4da6ff;
        object-fit: cover;
        background: #171a23;
    }

    .hero-banner {
        width: 100%;
        border-radius: 20px;
        margin-bottom: 30px;
        border: 1px solid #2b2f3a;
    }
    .card {
        background: #171a23;
        padding: 30px;
        border-radius: 20px;
        border: 1px solid #2b2f3a;
        margin-bottom: 20px;
    }
    .stButton>button {
        background: linear-gradient(90deg, #4da6ff, #0072ff);
        color: white; border: none; border-radius: 10px; width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "profile_created" not in st.session_state:
    st.session_state.update({
        "profile_created": False, "user_name": "", "user_brand": "", "user_gender": "Male",
        "slogan": "", "script": "", "avatar_url": "", "product_img": None
    })

# ---------------- LOGIN LOGIC ----------------
if not st.session_state.profile_created:
    st.image("https://i.postimg.cc/3rz01J48/Screenshot_2026_01_23_021409.png", width=200)
    with st.container():
        st.markdown('<div class="card"><h2>🚀 Initialize AdForge OS</h2>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        name = col1.text_input("Operator Name")
        brand = col2.text_input("Brand Identity")
        gender = col1.selectbox("Avatar System", ["Male", "Female"])
        if st.button("BOOT SYSTEM"):
            if name and brand:
                st.session_state.update({
                    "user_name": name, "user_brand": brand, "user_gender": gender,
                    "profile_created": True,
                    "avatar_url": "https://i.postimg.cc/5tTtnXH0/Screenshot_2026_01_23_010056.png" if gender == "Male" else "https://i.postimg.cc/PrVnmBvh/Screenshot-2026-01-23-010324.png"
                })
                st.rerun()
    st.stop()

# ---------------- HEADER & NAV ----------------
st.markdown(f'<div class="profile-container"><img src="{st.session_state.avatar_url}" class="profile-img"><br><small>{st.session_state.user_name}</small></div>', unsafe_allow_html=True)

menu = st.sidebar.radio("Navigation", ["Home", "Ad Studio", "Marketplace"])

# ---------------- HOME TAB (RESTORED BANNER) ----------------
if menu == "Home":
    st.image("https://i.postimg.cc/CLnTFRX1/Screenshot-2026-01-22-232250.png", use_column_width=True, caption="AdForge Enterprise v2.0")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="card">
            <h3>🤖 Multi-Agent AI Core</h3>
            <p>Our Llama 3 backbone uses <b>Agentic Workflows</b>:</p>
            <ul>
                <li><b>Creative Director Agent:</b> Tone & Market Analysis</li>
                <li><b>Copywriting Agent:</b> 10-Line Script Mastery</li>
                <li><b>Visual Agent:</b> Billboard Composition</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="card">
            <h3>✨ Key Features</h3>
            <ul>
                <li>Few-Shot Response Engineering</li>
                <li>Dynamic Motion Ad Rendering</li>
                <li>Real-time Groq LPU Processing</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# ---------------- AD STUDIO ----------------
elif menu == "Ad Studio":
    st.title("🎬 Multi-Agent Creative Studio")
    
    with st.expander("🛠️ Agent Configuration", expanded=True):
        prod = st.text_input("Target Product")
        tone = st.select_slider("Creative Tone", ["Funny", "Professional", "Dramatic"])

    if st.button("🧠 Invoke Agents"):
        with st.status("Agents are collaborating...") as status:
            # Multi-agent simulation
            st.write("Agent 1 (Strategist): Analyzing market fit...")
            time.sleep(1)
            st.write("Agent 2 (Writer): Applying few-shot concepts...")
            
            # REAL API CALL with Error Handling
            try:
                api_key = st.secrets["groq_api_key"]
                resp = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={
                        "model": "llama3-70b-8192",
                        "messages": [{"role": "system", "content": "You are a professional ad agency. Provide a 5-word slogan and a 10-line high-energy ad script with emojis."},
                                     {"role": "user", "content": f"Create an ad for {prod} with a {tone} tone."}]
                    }
                ).json()
                
                content = resp['choices'][0]['message']['content']
                # Splitting logic
                st.session_state.slogan = " ".join(content.split()[:5]) + "..."
                st.session_state.script = content
                status.update(label="Creative Ready!", state="complete")
            except:
                st.session_state.slogan = f"Experience the Power of {prod} Today."
                st.session_state.script = f"🚀 Unleash your potential with {prod}.\n" * 8
                status.update(label="Manual Fallback Active", state="error")

    st.text_input("Final Slogan", value=st.session_state.slogan)
    st.text_area("Multi-Line Script", value=st.session_state.script, height=250)

    # BILLBOARD GENERATION
    st.divider()
    st.subheader("🖼️ Premium Billboard Generation")
    u_prod = st.file_uploader("Upload Product Master Image")
    if u_prod:
        st.session_state.product_img = u_prod
        if st.button("🎨 Render Luxury Billboard"):
            path = create_luxury_billboard(st.session_state.user_brand, st.session_state.slogan, u_prod)
            st.image(path, use_column_width=True)
            with open(path, "rb") as f:
                st.download_button("Download 4K Billboard", f, "billboard.png")
