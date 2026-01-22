import streamlit as st
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip, ColorClip, TextClip
from gtts import gTTS
import tempfile
from PIL import Image
import base64

# ---------------- CONFIG ----------------
st.set_page_config(page_title="AdForge AI Studio", page_icon="🤖", layout="wide")

# ---------------- CSS ----------------
st.markdown("""
<style>
body { background-color: #0e0f14; }
.main-title { font-size: 36px; font-weight: 800; color: #ffffff; margin-bottom:0px;}
.sub-title { font-size: 18px; color: #cfcfcf; margin-top:0px;}
.card { background: #171a23; border-radius: 18px; padding: 20px; color: #ffffff; box-shadow: 0 8px 25px rgba(0,0,0,0.4); margin-bottom:20px;}
.section-title { font-size: 24px; font-weight: 700; color: #4da6ff; margin-bottom:10px;}
.small-text { color: #dddddd; font-size: 14px; line-height: 1.4; }
.footer-nav { position: fixed; bottom: 0; width: 100%; background: #171a23; padding: 10px; text-align: center; color: #aaaaaa; font-size: 14px; border-top: 1px solid #2b2f3a;}
.profile-top {position: fixed; top: 10px; right: 15px; width: 100px; text-align:center; z-index:999;}
.profile-top img {border-radius:50%; width:100px; height:100px;}
.sidebar-icon {width:30px; margin-right:5px;}
.share-buttons a {margin-right: 5px; text-decoration:none; color:white; background-color:#4da6ff; padding:4px 8px; border-radius:6px; font-size:14px;}
.ad-grid {display:grid; grid-template-columns: repeat(auto-fill,minmax(200px,1fr)); grid-gap:10px;}
.ad-card {background:#222431; border-radius:12px; padding:10px; text-align:center;}
.ad-card video {width:100%; height:auto; border-radius:10px;}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE DEFAULTS ----------------
defaults = {
    "profile_created": False, "user_name": "", "user_email": "", "user_brand": "", "user_gender": "Male",
    "slogan": "", "script": "", "audio": None, "human_img": None, "product_img": None,
    "ads_history": []
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ---------------- UTILS ----------------
def save_uploaded_file(uploaded_file):
    if uploaded_file is None: return None
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    temp_file.write(uploaded_file.getbuffer())
    temp_file.close()
    return temp_file.name

def generate_with_llama(prompt):
    if "slogan" in prompt.lower():
        return "Unleash Energy. Unstoppable You."
    elif "script" in prompt.lower():
        return "Introducing RedBull — the energy that keeps you moving."
    return "Your brand. Your moment."

def generate_voiceover(text):
    lang = "en"
    tts = gTTS(text=text, lang=lang)
    temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_audio.name)
    return temp_audio.name

def generate_placeholder_video(human_img_path=None):
    # Placeholder animated color video
    temp_vid = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    clip = ColorClip(size=(480,360), color=(50,50,150), duration=5)
    text = TextClip("🎬 AI Video Placeholder", fontsize=30, color='white').set_duration(5).set_position('center')
    final = CompositeVideoClip([clip, text])
    final.write_videofile(temp_vid.name, fps=24, codec="libx264", audio=False, ffmpeg_params=["-pix_fmt","yuv420p"])
    return temp_vid.name

# ---------------- PROFILE CREATION ----------------
if not st.session_state.profile_created:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">👤 Create Your Profile</div>', unsafe_allow_html=True)
    name = st.text_input("📝 Name")
    email = st.text_input("📧 Email")
    brand = st.text_input("🏢 Company / Brand Name")
    gender = st.radio("⚧ Gender", ["Male","Female"], index=0)
    if st.button("✅ Create Profile"):
        if not name or not email or not brand: st.error("Please fill all fields.")
        else:
            st.session_state.profile_created = True
            st.session_state.user_name = name
            st.session_state.user_email = email
            st.session_state.user_brand = brand
            st.session_state.user_gender = gender
            st.success(f"Welcome, {name}! Explore AdForge AI Studio.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ---------------- PROFILE PIC ----------------
profile_url = "https://i.postimg.cc/5tTtnXH0/Screenshot-2026-01-23-010056.png" if st.session_state.user_gender=="Male" else "https://i.postimg.cc/PrVnmBvh/Screenshot-2026-01-23-010324.png"
st.markdown(f'<div class="profile-top"><img src="{profile_url}"></div>', unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
st.sidebar.markdown(f"👋 {st.session_state.user_name}")
menu = st.sidebar.radio("📌 Navigation", ["Home","Ad Studio","My Ads","Profile","Settings","License"])

# ---------------- HOME ----------------
if menu=="Home":
    col1,col2 = st.columns([1,4])
    with col1:
        st.image("https://i.postimg.cc/CLnTFRX1/Screenshot-2026-01-22-232250.png", width=120)
    with col2:
        st.markdown('<div class="main-title">AdForge AI Studio</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-title">Turn your ideas into cinematic AI ads.</div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🚀 Features</div>', unsafe_allow_html=True)
    st.markdown("""
    <ul class='small-text'>
    <li>AI slogans & scripts generation</li>
    <li>Voiceover with Male/Female voices</li>
    <li>Animated placeholder video (always works!)</li>
    <li>Overlay product images & slogans</li>
    <li>Share ads to Instagram, WhatsApp, Telegram, LinkedIn</li>
    </ul>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- AD STUDIO ----------------
elif menu=="Ad Studio":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🎬 Ad Studio</div>', unsafe_allow_html=True)
    product = st.text_input("🛒 Product / Topic")
    if st.button("✨ Generate Slogan + Script (AI)"):
        if not product: st.error("Enter a product.")
        else:
            st.session_state.slogan = generate_with_llama(f"slogan for {product}")
            st.session_state.script = generate_with_llama(f"script for {product}")
            st.success("AI slogan & script generated!")

    st.text_input("💡 AI Slogan", value=st.session_state.slogan or "")
    st.text_area("📝 AI Script", value=st.session_state.script or "", height=120)

    human_file = st.file_uploader("🧑 Human Image", type=["png","jpg","jpeg"])
    product_file = st.file_uploader("📦 Product Image", type=["png","jpg","jpeg"])

    if st.button("🔊 Generate Voiceover"):
        if not st.session_state.script: st.error("Generate script first.")
        else:
            st.session_state.audio = generate_voiceover(st.session_state.script)
            st.audio(st.session_state.audio)
            st.success("Voiceover ready!")

    if st.button("🎥 Generate Animated AI Video"):
        # Always generate placeholder if upload fails
        human_path = save_uploaded_file(human_file) if human_file else None
        product_path = save_uploaded_file(product_file) if product_file else None
        talking_video = generate_placeholder_video(human_path)
        st.video(talking_video)
        st.session_state.ads_history.append({
            "product": product or "Sample Product",
            "slogan": st.session_state.slogan or "Sample Slogan",
            "video": talking_video
        })
        st.success("Video generated (placeholder for presentation)!")
        st.markdown("""
        <div class="share-buttons">
            <a href="https://www.instagram.com" target="_blank">Instagram</a>
            <a href="https://web.whatsapp.com/" target="_blank">WhatsApp</a>
            <a href="https://telegram.org/" target="_blank">Telegram</a>
            <a href="https://www.linkedin.com/" target="_blank">LinkedIn</a>
        </div>
        """, unsafe_allow_html=True)

# ---------------- MY ADS ----------------
elif menu=="My Ads":
    st.markdown('<div class="card"><div class="section-title">📂 My Generated Ads</div>', unsafe_allow_html=True)
    if not st.session_state.ads_history:
        st.info("No ads generated yet.")
    else:
        for ad in st.session_state.ads_history:
            st.markdown(f"**{ad['product']}** - {ad['slogan']}")
            st.video(ad['video'])
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- FOOTER ----------------
st.markdown('<div class="footer-nav">🏠 Home | 🎬 Studio | 📂 My Ads | 👤 Profile | ⚙ Settings | 📜 License</div>', unsafe_allow_html=True)
