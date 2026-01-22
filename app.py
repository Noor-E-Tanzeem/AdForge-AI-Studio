import streamlit as st
from moviepy.editor import ImageClip, VideoFileClip, CompositeVideoClip, TextClip, AudioFileClip, concatenate_videoclips
from gtts import gTTS
import tempfile
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import base64
import time
import random

# ---------------- CONFIG ----------------
st.set_page_config(page_title="AdForge AI Studio", page_icon="🤖", layout="wide")

# ---------------- ENHANCED CSS ----------------
st.markdown("""
<style>
body { background: linear-gradient(135deg, #0e0f14, #1a1d29); font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
.main-title { font-size: 48px; font-weight: 900; color: #ffffff; text-shadow: 0 0 20px #4da6ff; animation: glow 2s ease-in-out infinite alternate; }
@keyframes glow { from { text-shadow: 0 0 20px #4da6ff; } to { text-shadow: 0 0 30px #ff6b6b; } }
.sub-title { font-size: 22px; color: #cfcfcf; margin-bottom: 20px; }
.card { background: linear-gradient(145deg, #171a23, #2b2f3a); border-radius: 20px; padding: 30px; color: #ffffff; box-shadow: 0 10px 40px rgba(0,0,0,0.5); border: 1px solid #4da6ff; transition: transform 0.3s; }
.card:hover { transform: translateY(-5px); }
.section-title { font-size: 28px; font-weight: 700; color: #4da6ff; margin-bottom: 15px; }
.small-text { color: #dddddd; font-size: 16px; line-height: 1.6; }
.footer-nav { position: fixed; bottom: 0; width: 100%; background: #171a23; padding: 15px; text-align: center; color: #aaaaaa; font-size: 14px; border-top: 2px solid #4da6ff; }
.progress-bar { width: 100%; height: 10px; background: #333; border-radius: 5px; overflow: hidden; }
.progress-fill { height: 100%; background: linear-gradient(90deg, #4da6ff, #ff6b6b); transition: width 0.5s; }
.btn-primary { background: linear-gradient(45deg, #4da6ff, #6c5ce7); border: none; color: white; padding: 12px 24px; border-radius: 10px; font-weight: bold; cursor: pointer; transition: all 0.3s; }
.btn-primary:hover { transform: scale(1.05); box-shadow: 0 5px 15px rgba(77, 166, 255, 0.4); }
.tab-content { padding: 20px; background: rgba(255,255,255,0.05); border-radius: 15px; margin-top: 10px; }
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION DEFAULTS ----------------
defaults = {
    "profile_created": False, "user_name": "", "user_email": "", "user_brand": "",
    "slogan": "", "script": "", "audio": None, "human_img": None, "product_img": None,
    "review_rating": 5, "review_text": "", "video_resolution": "720p", "voice_style": "Female", "script_style": "Corporate",
    "bgm_enabled": False, "bgm_url": "", "ad_format": "Video Ad", "language": "English", "generated_ads": []
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ---------------- UTILS ----------------
def load_image(url):
    response = requests.get(url)
    return Image.open(BytesIO(response.content))

def generate_with_llama(prompt):
    # Simulate AI generation with more variety
    if "slogan" in prompt.lower():
        slogans = ["Unleash Energy. Unstoppable You.", "Power Your Passion.", "Elevate Every Moment.", "Ignite Your Potential."]
        return random.choice(slogans)
    elif "script" in prompt.lower():
        style = st.session_state.script_style
        scripts = {
            "Funny": "RedBull gives wings… and laughs! Fly through your day with energy and fun. Don't just sip, giggle!",
            "Dramatic": "RedBull empowers you to conquer the impossible. Every sip, a surge of power. Rise above the ordinary!",
            "Corporate": "Introducing RedBull — the energy that keeps you moving. Chase dreams, break limits, fuel ambition."
        }
        return scripts.get(style, "Your brand. Your power. Your moment.")
    return "AI-generated content here."

def generate_voiceover(text):
    lang_map = {"English": "en", "Spanish": "es", "French": "fr"}
    lang = lang_map.get(st.session_state.language, "en")
    if st.session_state.voice_style == "Male":
        lang += "-us" if lang == "en" else ""
    tts = gTTS(text=text, lang=lang)
    temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_audio.name)
    return temp_audio.name

def generate_billboard(product, slogan, human_img=None, product_img=None):
    bg = Image.new("RGB", (1280, 720), (20, 20, 30))
    draw = ImageDraw.Draw(bg)
    try:
        font_title = ImageFont.truetype("DejaVuSans-Bold.ttf", 70)
        font_slogan = ImageFont.truetype("DejaVuSans.ttf", 42)
    except:
        font_title = ImageFont.load_default()
        font_slogan = ImageFont.load_default()
    draw.text((60, 60), product.upper(), fill=(255,255,255), font=font_title)
    draw.text((60, 160), slogan, fill=(200,200,255), font=font_slogan)

    if human_img:
        human = Image.open(human_img).convert("RGB").resize((360,500))
        bg.paste(human, (860,170))

    if product_img:
        prod = Image.open(product_img).convert("RGB").resize((280,280))
        bg.paste(prod, (60,380))

    draw.text((60, 660), "AdForge AI Studio", fill=(140,140,180), font=font_slogan)
    temp_img = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    bg.save(temp_img.name)
    return temp_img.name

def generate_animated_human(human_img_path, audio_path):
    # Simulate D-ID API with progress
    progress_bar = st.progress(0)
    for i in range(100):
        time.sleep(0.05)
        progress_bar.progress(i + 1)
    progress_bar.empty()
    
    # Placeholder: In real app, use actual API
    # For demo, create a simple video clip
    img_clip = ImageClip(human_img_path).set_duration(5)
    audio_clip = AudioFileClip(audio_path)
    video_clip = img_clip.set_audio(audio_clip)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    video_clip.write_videofile(tmp.name, fps=24, verbose=False, logger=None)
    return tmp.name

def add_product_overlay(talking_video_path, product_img_path, slogan):
    video_clip = VideoFileClip(talking_video_path)
    product_clip = ImageClip(product_img_path).set_duration(video_clip.duration).resize(height=200).set_position(("right","bottom"))
    text_clip = TextClip(slogan, fontsize=50, color='white', bg_color='black').set_duration(video_clip.duration).set_position(("left","top"))
    final = CompositeVideoClip([video_clip, product_clip, text_clip])
    tmp_final = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    final.write_videofile(tmp_final.name, fps=24, verbose=False, logger=None)
    return tmp_final.name

def add_bgm(video_path, bgm_url):
    video_clip = VideoFileClip(video_path)
    bgm_clip = AudioFileClip(bgm_url).subclip(0, video_clip.duration)
    video_clip = video_clip.set_audio(bgm_clip)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    video_clip.write_videofile(tmp.name, fps=24, verbose=False, logger=None)
    return tmp.name

# ---------------- PROFILE CREATION ----------------
if not st.session_state.profile_created:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">👤 Create Your Profile</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Name", placeholder="Enter your full name")
        email = st.text_input("Email", placeholder="your.email@example.com")
    with col2:
        brand = st.text_input("Company / Brand Name", placeholder="e.g., RedBull")
        avatar = st.file_uploader("Upload Avatar (Optional)", type=["png","jpg","jpeg"])
    if st.button("✅ Create Profile", key="create_profile"):
        if not name or not email or not brand:
            st.error("Please fill all required fields.")
        else:
            st.session_state.profile_created = True
            st.session_state.user_name = name
            st.session_state.user_email = email
            st.session_state.user_brand = brand
            if avatar:
                st.session_state.avatar = avatar
            st.success(f"Welcome, {name}! Let's forge some epic ads! 🚀")
            st.balloons()
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ---------------- SIDEBAR ----------------
st.sidebar.markdown(f"👋 Hello, {st.session_state.user_name}!")
if "avatar" in st.session_state:
    st.sidebar.image(st.session_state.avatar, width=100)
st.sidebar.markdown("---")
menu = st.sidebar.radio("📌 Navigation", ["Home", "Ad Studio", "Analytics", "Settings", "License"])

# ---------------- HOME ----------------
if menu == "Home":
    col1, col2 = st.columns([1, 4])
    with col1:
        small_banner = load_image("https://i.postimg.cc/CLnTFRX1/Screenshot-2026-01-22-232250.png")
        st.image(small_banner, width=170)
    with col2:
        st.markdown('<div class="main-title">AdForge AI Studio</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-title">Turn your ideas into cinematic AI ads with cutting-edge innovation.</div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🚀 About</div>', unsafe_allow_html=True)
    st.markdown("<div class='small-text'>AdForge AI Studio auto-generates professional ad creatives using AI. Upload images, generate scripts, voiceovers, and videos. Now with multi-language support, BGM, and analytics!</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- AD STUDIO ----------------
elif menu == "Ad Studio":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🎬 Ad Studio</div>', unsafe_allow_html=True)
    
    tabs = st.tabs(["📝 Script & Slogan", "🖼️ Assets", "🎥 Generation", "📤 Export"])
    
    with tabs[0]:
        st.markdown("### Generate AI Content")
        product = st.text_input("Product / Topic", placeholder="e.g., RedBull Energy Drink")
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.script_style = st.selectbox("Script Style", ["Corporate", "Funny", "Dramatic"])
        with col2:
            st.session_state.language = st.selectbox("Language", ["English", "Spanish", "French"])
        if st.button("✨ Generate Slogan + Script (AI)", key="gen_slogan_script"):
            if not product:
                st.error("Enter a product.")
            else:
                with st.spinner("Generating..."):
                    st.session_state.slogan = generate_with_llama(f"slogan for {product}")
                    st.session_state.script = generate_with_llama(f"script for {product}")
                st.success("AI slogan and script generated! 🎉")
        st.text_input("AI Slogan", value=st.session_state.slogan or "", key="slogan_input")
        script = st.text_area("AI Script", value=st.session_state.script or "", height=120, key="script_input")
    
    with tabs[1]:
        st.markdown("### Upload Assets")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🧑 Human Image")
            human = st.file_uploader("Upload Human Image", type=["png", "jpg", "jpeg"], key="human_uploader")
            if human:
                st.session_state.human_img = human
                st.image(human, width=200)
        with col2:
            st.markdown("### 🥤 Product Image")
            prod = st.file_uploader("Upload Product Image", type=["png", "jpg", "jpeg"], key="product_uploader")
            if prod:
                st.session_state.product_img = prod
                st.image(prod, width=200)
    
    with tabs[2]:
        st.markdown("### Generate Ad")
        st.session_state.ad_format = st.selectbox("Ad Format", ["Video Ad", "Billboard", "Social Post"])
        if st.button("🔊 Generate Voiceover", key="gen_voice"):
            if not script:
                st.error("Generate script first.")
            else:
                with st.spinner("Generating voiceover..."):
                    st.session_state.audio = generate_voiceover(script)
                st.audio(st.session_state.audio)
                st.success("Voiceover ready! 🎤")
        
        if st.button("🎥 Generate Ad", key="gen_ad"):
            if not product or not st.session_state.audio or not st.session_state.human_img:
                st.error("Missing required inputs.")
            else:
                with st.spinner("Creating animated AI video..."):
                    talking_video = generate_animated_human(st.session_state.human_img.name, st.session_state.audio)
                    if talking_video:
                        final_video = add_product_overlay(talking_video, st.session_state.product_img.name, st.session_state.slogan)
                        if st.session_state.bgm_enabled and st.session_state.bgm_url:
                            final_video = add_bgm(final_video, st.session_state.bgm_url)
                        st.session_state.generated_ads.append(final_video)
                        st.video(final_video)
                        st.success("Animated AI ad generated! 🌟")
        
        # Review Section
        st.markdown("### ⭐ Rate Your Experience")
        rating = st.slider("Rate the App", min_value=1, max_value=5, value=5, key="rating_slider")
        review = st.text_area("Feedback", key="review_text")
        if st.button("Submit Review", key="submit_review"):
            st.session_state.review_rating = rating
            st.session_state.review_text = review
            st.success("Thanks for your feedback! 🌟")
    
    with tabs[3]:
        st.markdown("### Export & Share")
        if st.session_state.generated_ads:
            st.download_button("Download Latest Ad", data=open(st.session_state.generated_ads[-1], "rb"), file_name="adforge_ad.mp4", mime="video/mp4")
            st.text("Share Link: https://adforge.ai/share/" + str(random.randint(1000,9999)))  # Placeholder
        else:
            st.info("Generate an ad first!")
    
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- ANALYTICS ----------------
elif menu == "Analytics":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📊 Analytics Dashboard</div>', unsafe_allow_html=True)
    st.markdown(f"<div class='small-text'>Total Ads Generated: {len(st.session_state.generated_ads)}<br>Average Rating: {st.session_state.review_rating}/5<br>Latest Feedback: {st.session_state.review_text or 'None'}</div>", unsafe_allow_html=True)
    # Placeholder for charts
    st.bar_chart({"Ads": len(st.session_state.generated_ads), "Ratings": st.session_state.review_rating})
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- SETTINGS ----------------
elif menu == "Settings":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">⚙ Settings</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.video_resolution = st.selectbox("Video Resolution", ["480p", "720p", "1080p"], index=1)
        st.session_state.voice_style = st.selectbox("Voice Style", ["Female", "Male"], index=0)
    with col2:
        st.session_state.bgm_enabled = st.checkbox("Add Background Music", value=st.session_state.bgm_enabled)
        if st.session_state.bgm_enabled:
            st.session_state.bgm_url = st.text_input("BGM URL", value=st.session_state.bgm_url, placeholder="https://example.com/bgm.mp3")
    st.markdown("<div class='small-text'>Settings will be applied to generated ads.</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- LICENSE ----------------
elif menu == "License":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📜 License & Info</div>', unsafe_allow_html=True)
    st.markdown(f"<div class='small-text'>AdForge AI Studio – Community Edition © 2026<br>User: {st.session_state.user_name}<br>Email: {st.session_state.user_email}<br>Brand: {st.session_state.user_brand}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- FOOTER ----------------
st.markdown('<div class="footer-nav">🏠 Home | 🎬 Studio | 📊 Analytics | ⚙ Settings | 📜 License</div>', unsafe_allow_html=True)
