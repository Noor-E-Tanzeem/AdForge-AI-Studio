import streamlit as st
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip, TextClip, ColorClip, AudioFileClip
from gtts import gTTS
import tempfile
from PIL import Image
import os

# ---------------- CONFIG ----------------
st.set_page_config(page_title="AdForge AI Studio", page_icon="🤖", layout="wide")

# ---------------- CSS ----------------
st.markdown("""
<style>
body { background-color: #0e0f14; }
.main-title { font-size: 38px; font-weight: 800; color: #ffffff; margin-bottom:0px;}
.sub-title { font-size: 18px; color: #cfcfcf; margin-top:0px;}
.card { background: #171a23; border-radius: 18px; padding: 20px; color: #ffffff; box-shadow: 0 8px 25px rgba(0,0,0,0.4); margin-bottom:20px;}
.section-title { font-size: 24px; font-weight: 700; color: #4da6ff; margin-bottom:10px;}
.small-text { color: #dddddd; font-size: 14px; line-height: 1.4; }
.footer-nav { position: fixed; bottom: 0; width: 100%; background: #171a23; padding: 10px; text-align: center; color: #aaaaaa; font-size: 14px; border-top: 1px solid #2b2f3a;}
.profile-top {position: fixed; top: 10px; right: 20px; width: 120px; text-align:center; z-index:999;}
.profile-top img {border-radius:50%; width:120px; height:120px;}
.share-buttons a {margin-right: 5px; text-decoration:none; color:white; background-color:#4da6ff; padding:4px 8px; border-radius:6px; font-size:14px;}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
defaults = {
    "profile_created": False,
    "user_name": "",
    "user_email": "",
    "user_brand": "",
    "user_gender": "Male",
    "ads_history": [],
    "slogan": "",
    "text_overlay": "",
    "audio": None
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

def generate_voiceover(text):
    tts = gTTS(text=text, lang='en')
    temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_audio.name)
    return temp_audio.name

def generate_product_video(product_img_path, text_overlay, audio_path=None):
    # Placeholder background if no image
    if product_img_path:
        clip = ImageClip(product_img_path).set_duration(8).resize(height=360)
    else:
        clip = ColorClip(size=(480,360), color=(50,50,150)).set_duration(8)

    # Moving text with emojis (scroll up)
    txt_clip = TextClip(text_overlay or "Your Product Here 🚀🎉", fontsize=28, color="white", method="caption", size=(480,None))
    txt_clip = txt_clip.set_position(lambda t: ('center', 360 - 50*t)).set_duration(8)

    clips = [clip, txt_clip]

    # Add audio if exists
    if audio_path and os.path.exists(audio_path):
        audio_clip = AudioFileClip(audio_path).subclip(0,8)
        final = CompositeVideoClip(clips).set_audio(audio_clip)
    else:
        final = CompositeVideoClip(clips)

    temp_vid = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    final.write_videofile(temp_vid.name, fps=24, codec="libx264", audio_codec="aac", ffmpeg_params=["-pix_fmt","yuv420p"])
    return temp_vid.name

# ---------------- PROFILE CREATION ----------------
if not st.session_state.profile_created:
    st.markdown('<div class="card" style="text-align:center;">', unsafe_allow_html=True)
    st.image("https://i.postimg.cc/3rz01J48/Screenshot-2026-01-23-021409.png", width=150)
    st.markdown('<div class="section-title">👤 Create Your Profile</div>', unsafe_allow_html=True)
    name = st.text_input("📝 Name")
    email = st.text_input("📧 Email")
    brand = st.text_input("🏢 Company / Brand Name")
    gender = st.radio("⚧ Gender", ["Male","Female"], index=0)
    if st.button("✅ Create Profile"):
        if not name or not email or not brand:
            st.error("Please fill all fields.")
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
        st.markdown('<div class="sub-title">Create amazing animated product ads effortlessly.</div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🚀 Features</div>', unsafe_allow_html=True)
    st.markdown("""
    <ul class='small-text'>
    <li>Upload product images</li>
    <li>Add animated captions & emojis</li>
    <li>Generate voiceover for your text</li>
    <li>View past ads & ratings</li>
    <li>Edit profile anytime</li>
    <li>Download & share your ads</li>
    </ul>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- AD STUDIO ----------------
elif menu=="Ad Studio":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🎬 Ad Studio</div>', unsafe_allow_html=True)
    
    product_name = st.text_input("🛒 Product / Topic")
    slogan = st.text_input("💡 Slogan / Caption", value=st.session_state.get("slogan", ""))
    text_overlay = st.text_area("📝 Video Text / Emojis", height=120, value=st.session_state.get("text_overlay",""))
    product_file = st.file_uploader("📦 Product Image", type=["png","jpg","jpeg"])

    # ---- Generate Slogan + Text ----
    if st.button("✨ Generate Slogan + Text (AI)"):
        if not product_name:
            st.error("Enter a product name first!")
        else:
            st.session_state.slogan = f"{product_name} — Boost Your Day!"
            st.session_state.text_overlay = f"Try {product_name} today! 💪⚡🎉"
            st.success("Slogan and text generated!")
            slogan = st.session_state.slogan
            text_overlay = st.session_state.text_overlay

    # ---- Generate Voiceover ----
    if st.button("🔊 Generate Voiceover"):
        if not text_overlay:
            st.error("Enter text for voiceover.")
        else:
            st.session_state.audio = generate_voiceover(text_overlay)
            st.audio(st.session_state.audio)
            st.success("Voiceover ready!")

    # ---- Generate Animated Product Video ----
    if st.button("🎥 Generate Animated Product Video"):
        product_path = save_uploaded_file(product_file) if product_file else None
        video_path = generate_product_video(product_path, text_overlay or "Your Product Here 🚀🎉", getattr(st.session_state,"audio",None))
        st.video(video_path)
        st.session_state.ads_history.append({
            "product": product_name or "Sample Product",
            "slogan": slogan or "Sample Slogan",
            "text": text_overlay or "Your Text",
            "video": video_path,
            "rating": None,
            "review": None
        })
        st.success("Animated product video generated!")
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
    st.markdown('<div class="card"><div class="section-title">📂 My Generated Ads</div>', unsafe_allow_html=True)
    if not st.session_state.ads_history:
        st.info("No ads generated yet.")
    else:
        for idx, ad in enumerate(st.session_state.ads_history,1):
            st.markdown(f"**{idx}. {ad['product']}** - {ad['slogan']}")
            st.video(ad['video'])
            st.markdown(f"**Text Overlay:** {ad['text']}")
            # Rating
            rating = st.slider(f"⭐ Rate Ad {idx}", 1,5,value=ad.get("rating") or 5, key=f"rate_{idx}")
            review = st.text_area(f"💬 Review Ad {idx}", value=ad.get("review") or "", key=f"rev_{idx}")
            ad["rating"] = rating
            ad["review"] = review
            # Download button
            with open(ad["video"], "rb") as f:
                st.download_button(f"⬇ Download Ad {idx}", f, file_name=f"{ad['product']}.mp4")
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- PROFILE ----------------
elif menu=="Profile":
    st.markdown('<div class="card"><div class="section-title">👤 Edit Profile</div>', unsafe_allow_html=True)
    name = st.text_input("📝 Name", value=st.session_state.user_name)
    email = st.text_input("📧 Email", value=st.session_state.user_email)
    brand = st.text_input("🏢 Company / Brand Name", value=st.session_state.user_brand)
    gender = st.radio("⚧ Gender", ["Male","Female"], index=0 if st.session_state.user_gender=="Male" else 1)
    if st.button("💾 Save Profile"):
        st.session_state.user_name = name
        st.session_state.user_email = email
        st.session_state.user_brand = brand
        st.session_state.user_gender = gender
        st.success("Profile updated successfully!")
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- SETTINGS ----------------
elif menu=="Settings":
    st.markdown('<div class="card"><div class="section-title">⚙ Settings</div>', unsafe_allow_html=True)
    st.markdown("All app settings are currently auto-handled. Future updates will include BGM, fonts, video resolution.")
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- LICENSE ----------------
elif menu=="License":
    st.markdown('<div class="card"><div class="section-title">📜 License & Info</div>', unsafe_allow_html=True)
    st.markdown(f"<div class='small-text'>AdForge AI Studio – Hackathon Edition © 2026<br>User: {st.session_state.user_name}<br>Email: {st.session_state.user_email}<br>Brand: {st.session_state.user_brand}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- FOOTER ----------------
st.markdown('<div class="footer-nav">🏠 Home | 🎬 Studio | 📂 My Ads | 👤 Profile | ⚙ Settings | 📜 License</div>', unsafe_allow_html=True)
