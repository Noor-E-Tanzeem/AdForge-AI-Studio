import streamlit as st
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip, TextClip
from gtts import gTTS
import tempfile
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import base64
import os

# ---------------- CONFIG ----------------
st.set_page_config(page_title="AdForge AI Studio", page_icon="🤖", layout="wide")

# ---------------- CSS ----------------
st.markdown("""
<style>
body { background-color: #0e0f14; }
.main-title { font-size: 42px; font-weight: 800; color: #ffffff; }
.sub-title { font-size: 20px; color: #cfcfcf; }
.card { background: #171a23; border-radius: 18px; padding: 28px; color: #ffffff; box-shadow: 0 8px 25px rgba(0,0,0,0.4); margin-bottom:20px;}
.section-title { font-size: 26px; font-weight: 700; color: #4da6ff; margin-bottom:12px;}
.small-text { color: #dddddd; font-size: 16px; line-height: 1.6; }
.footer-nav { position: fixed; bottom: 0; width: 100%; background: #171a23; padding: 12px; text-align: center; color: #aaaaaa; font-size: 14px; border-top: 1px solid #2b2f3a;}
.profile-top {position: fixed; top: 10px; right: 20px; width: 80px; text-align:center; z-index:999;}
.profile-top img {border-radius:50%; width:80px; height:80px;}
.share-buttons a {margin-right: 8px; text-decoration:none; color:white; background-color:#4da6ff; padding:6px 12px; border-radius:8px;}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE DEFAULTS ----------------
defaults = {
    "profile_created": False, "user_name": "", "user_email": "", "user_brand": "", "user_gender": "Male",
    "slogan": "", "script": "", "audio": None, "human_img": None, "product_img": None,
    "review_rating": 5, "review_text": "", "video_resolution": "720p", "voice_style": "Female",
    "script_style": "Corporate", "ads_history": []
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ---------------- UTILS ----------------
def load_image(url):
    response = requests.get(url)
    return Image.open(BytesIO(response.content))

def generate_with_llama(prompt):
    # simple AI mock function
    if "slogan" in prompt.lower():
        return "Unleash Energy. Unstoppable You."
    elif "script" in prompt.lower():
        style = st.session_state.script_style
        if style=="Funny": return "RedBull gives wings… and laughs! Fly through your day with energy and fun."
        elif style=="Dramatic": return "RedBull empowers you to conquer the impossible. Every sip, a surge of power."
        return "Introducing RedBull — the energy that keeps you moving. Chase dreams, break limits, fuel ambition."
    return "Your brand. Your power. Your moment."

def generate_voiceover(text):
    lang = "en-us" if st.session_state.voice_style=="Male" else "en"
    tts = gTTS(text=text, lang=lang)
    temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_audio.name)
    return temp_audio.name

def generate_animated_human(human_img_path, audio_path):
    # MOCK function: returns placeholder video for testing
    # Replace with your D-ID API call if available
    temp_vid = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    clip = ImageClip(human_img_path).set_duration(5)
    clip.write_videofile(temp_vid.name, fps=24, codec="libx264", audio=False, ffmpeg_params=["-pix_fmt","yuv420p"])
    return temp_vid.name

def add_product_overlay(talking_video_path, product_img_path, slogan):
    video_clip = VideoFileClip(talking_video_path)
    product_clip = ImageClip(product_img_path).set_duration(video_clip.duration).resize(height=150).set_position(("right","bottom"))
    text_clip = TextClip(slogan, fontsize=30, color='white', font="Arial-Bold").set_duration(video_clip.duration).set_position(("left","top"))
    final = CompositeVideoClip([video_clip, product_clip, text_clip])
    tmp_final = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    final.write_videofile(tmp_final.name, fps=24, codec="libx264", audio_codec="aac", ffmpeg_params=["-pix_fmt","yuv420p"])
    return tmp_final.name

# ---------------- PROFILE CREATION ----------------
if not st.session_state.profile_created:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">👤 Create Your Profile</div>', unsafe_allow_html=True)
    name = st.text_input("Name")
    email = st.text_input("Email")
    brand = st.text_input("Company / Brand Name")
    gender = st.radio("Gender", ["Male","Female"], index=0)
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

# ---------------- PROFILE PICTURE TOP-RIGHT ----------------
profile_url = "https://i.postimg.cc/5tTtnXH0/Screenshot-2026-01-23-010056.png" if st.session_state.user_gender=="Male" else "https://i.postimg.cc/PrVnmBvh/Screenshot-2026-01-23-010324.png"
st.markdown(f'<div class="profile-top"><img src="{profile_url}"></div>', unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
st.sidebar.markdown(f"👋 Hello, {st.session_state.user_name}!")
menu = st.sidebar.radio("📌 Navigation", ["Home","Ad Studio","My Ads","Profile","Settings","License"])

# ---------------- HOME ----------------
if menu=="Home":
    st.image("https://i.postimg.cc/CLnTFRX1/Screenshot-2026-01-22-232250.png", use_column_width=True)
    st.markdown('<div class="main-title">AdForge AI Studio</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Turn your ideas into cinematic AI ads.</div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🚀 Features</div>', unsafe_allow_html=True)
    st.markdown("""
    <ul class='small-text'>
    <li>Generate AI slogans & scripts for any product.</li>
    <li>Create voiceovers with Male/Female options.</li>
    <li>Animated AI spokesperson video with your uploaded human image.</li>
    <li>Overlay product images and slogans on video automatically.</li>
    <li>Share your ads to Instagram, WhatsApp, Telegram, LinkedIn directly.</li>
    <li>Keep track of all your generated ads and reviews in "My Ads".</li>
    </ul>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- AD STUDIO ----------------
elif menu=="Ad Studio":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🎬 Ad Studio</div>', unsafe_allow_html=True)
    product = st.text_input("Product / Topic")
    if st.button("✨ Generate Slogan + Script (AI)"):
        if not product: st.error("Enter a product.")
        else:
            st.session_state.slogan = generate_with_llama(f"slogan for {product}")
            st.session_state.script = generate_with_llama(f"script for {product}")
            st.success("AI slogan & script generated!")

    st.text_input("AI Slogan", value=st.session_state.slogan or "")
    script = st.text_area("AI Script", value=st.session_state.script or "", height=120)

    human = st.file_uploader("Human Image", type=["png","jpg","jpeg"])
    if human: st.session_state.human_img = human

    prod = st.file_uploader("Product Image", type=["png","jpg","jpeg"])
    if prod: st.session_state.product_img = prod

    if st.button("🔊 Generate Voiceover"):
        if not script: st.error("Generate script first.")
        else:
            st.session_state.audio = generate_voiceover(script)
            st.audio(st.session_state.audio)
            st.success("Voiceover ready!")

    if st.button("🎥 Generate Animated AI Video"):
        if not product or not st.session_state.audio or not st.session_state.human_img:
            st.error("Missing required inputs.")
        else:
            talking_video = generate_animated_human(st.session_state.human_img.name, st.session_state.audio)
            final_video = add_product_overlay(talking_video, st.session_state.product_img.name, st.session_state.slogan)
            st.video(final_video)
            st.success("Animated AI ad generated!")

            # save ad to history
            st.session_state.ads_history.append({
                "product":product,
                "slogan":st.session_state.slogan,
                "video":final_video
            })

            st.markdown("""
            <div class="share-buttons">
                <a href="https://www.instagram.com" target="_blank">Instagram</a>
                <a href="https://web.whatsapp.com/" target="_blank">WhatsApp</a>
                <a href="https://telegram.org/" target="_blank">Telegram</a>
                <a href="https://www.linkedin.com/" target="_blank">LinkedIn</a>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- MY ADS ----------------
elif menu=="My Ads":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📂 My Ads</div>', unsafe_allow_html=True)
    if not st.session_state.ads_history:
        st.info("No ads generated yet.")
    for idx, ad in enumerate(st.session_state.ads_history[::-1],1):
        st.markdown(f"### Ad {idx}: {ad['product']}")
        st.markdown(f"**Slogan:** {ad['slogan']}")
        st.video(ad['video'])
        rating = st.slider(f"Rate this Ad {idx}", min_value=1, max_value=5, value=5, key=f"rate_{idx}")
        review = st.text_area(f"Review {idx}", key=f"rev_{idx}")
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- PROFILE ----------------
elif menu=="Profile":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">👤 Edit Profile</div>', unsafe_allow_html=True)
    st.session_state.user_name = st.text_input("Name", st.session_state.user_name)
    st.session_state.user_email = st.text_input("Email", st.session_state.user_email)
    st.session_state.user_brand = st.text_input("Brand", st.session_state.user_brand)
    st.session_state.user_gender = st.radio("Gender", ["Male","Female"], index=0 if st.session_state.user_gender=="Male" else 1)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- SETTINGS ----------------
elif menu=="Settings":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">⚙ Settings</div>', unsafe_allow_html=True)
    st.selectbox("Video Resolution", ["480p","720p","1080p"], index=["480p","720p","1080p"].index(st.session_state.video_resolution))
    st.selectbox("Voice Style", ["Female","Male"], index=["Female","Male"].index(st.session_state.voice_style))
    st.selectbox("Script Style", ["Corporate","Funny","Dramatic"], index=["Corporate","Funny","Dramatic"].index(st.session_state.script_style))
    st.checkbox("Add Background Music", value=False)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- LICENSE ----------------
elif menu=="License":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📜 License & Info</div>', unsafe_allow_html=True)
    st.markdown(f"<div class='small-text'>AdForge AI Studio – Community Edition © 2026<br>User: {st.session_state.user_name}<br>Email: {st.session_state.user_email}<br>Brand: {st.session_state.user_brand}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- FOOTER ----------------
st.markdown('<div class="footer-nav">🏠 Home | 🎬 Studio | 📂 My Ads | 👤 Profile | ⚙ Settings | 📜 License</div>', unsafe_allow_html=True)
