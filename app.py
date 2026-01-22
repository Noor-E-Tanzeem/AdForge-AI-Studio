<think>
First, the user wants to enhance the Home page with more features and info, making it more like a real app. Add sections like features, testimonials, stats, etc., to make it innovative and hackathon-level winner worthy.


## Enhancing Home Page  
- The goal is to make the Home page more feature-rich and app-like, aligning with user expectations for innovation.  
- Consider adding sections like features, testimonials, and stats to boost engagement and hackathon-level quality.
</think>```python
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
.profile-icon { position: fixed; top: 10px; right: 10px; width: 50px; height: 50px; border-radius: 50%; border: 2px solid #4da6ff; }
.feature-list { display: flex; flex-wrap: wrap; gap: 20px; }
.feature-item { flex: 1 1 300px; background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px; text-align: center; }
.testimonial { background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; margin: 10px 0; }
.stats { display: flex; justify-content: space-around; margin: 20px 0; }
.stat-item { text-align: center; }
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION DEFAULTS ----------------
defaults = {
    "profile_created": False, "user_name": "", "user_email": "", "user_brand": "", "user_gender": "",
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

def generate_animated_human(human_img_path, audio_path, script):
    # Enhanced: Simulate lip-sync by adding subtitles from script, making it look synced
    progress_bar = st.progress(0)
    for i in range(100):
        time.sleep(0.05)
        progress_bar.progress(i + 1)
    progress_bar.empty()
    
    # Create video with image, audio, and subtitles for realism
    img_clip = ImageClip(human_img_path).set_duration(AudioFileClip(audio_path).duration)
    audio_clip = AudioFileClip(audio_path)
    # Split script into words for subtitle effect
    words = script.split()
    subtitle_clips = []
    duration_per_word = audio_clip.duration / len(words) if words else audio_clip.duration
    for i, word in enumerate(words):
        start_time = i * duration_per_word
        end_time = (i + 1) * duration_per_word
        txt_clip = TextClip(word, fontsize=40, color='white', bg_color='black').set_position(('center', 'bottom')).set_start(start_time).set_end(end_time)
        subtitle_clips.append(txt_clip)
    video_clip = CompositeVideoClip([img_clip] + subtitle_clips).set_audio(audio_clip)
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
    # Add logo at top center
    st.markdown('<div style="text-align: center;"><img src="https://i.postimg.cc/3rz01J48/Screenshot_2026_01_23_021409.png" width="200"></div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">👤 Create Your Profile</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Name", placeholder="Enter your full name")
        email = st.text_input("Email", placeholder="your.email@example.com")
        gender = st.selectbox("Gender", ["Female", "Male"])
    with col2:
        brand = st.text_input("Company / Brand Name", placeholder="e.g., RedBull")
        avatar = st.file_uploader("Upload Avatar (Optional)", type=["png","jpg","jpeg"])
    if st.button("✅ Create Profile", key="create_profile"):
        if not name or not email or not brand or not gender:
            st.error("Please fill all required fields.")
        else:
            st.session_state.profile_created = True
            st.session_state.user_name = name
            st.session_state.user_email = email
            st.session_state.user_brand = brand
            st.session_state.user_gender = gender
            if avatar:
                st.session_state.avatar = avatar
            else:
                # Set default avatar based on gender
                if gender == "Female":
                    st.session_state.avatar_url = "https://i.postimg.cc/PrVnmBvh/Screenshot-2026-01-23-010324.png"
                else:
                    st.session_state.avatar_url = "https://i.postimg.cc/5tTtnXH0/Screenshot_2026_01_23_010056.png"
            st.success(f"Welcome, {name}! Let's forge some epic ads! 🚀")
            st.balloons()
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ---------------- PROFILE ICON AT TOP RIGHT ----------------
if st.session_state.profile_created:
    if "avatar" in st.session_state:
        st.markdown(f'<img src="data:image/png;base64,{base64.b64encode(open(st.session_state.avatar.name, "rb").read()).decode()}" class="profile-icon">', unsafe_allow_html=True)
    elif "avatar_url" in st.session_state:
        st.markdown(f'<img src="{st.session_state.avatar_url}" class="profile-icon">', unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
st.sidebar.markdown(f"👋 Hello, {st.session_state.user_name}!")
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
    
    # Enhanced Home with more features and info
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🚀 About AdForge</div>', unsafe_allow_html=True)
    st.markdown("<div class='small-text'>AdForge AI Studio is the ultimate tool for creators, marketers, and businesses. Auto-generate professional ad creatives using advanced AI. From scripts to videos, we've got you covered with multi-language support, voiceovers, and seamless integrations.</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">✨ Key Features</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="feature-list">
        <div class="feature-item">
            <h4>🤖 AI-Powered Scripts</h4>
            <p>Generate engaging slogans and scripts in multiple styles and languages.</p>
        </div>
        <div class="feature-item">
            <h4>🎥 Realistic Video Ads</h4>
            <p>Create animated videos with lip-sync simulation and overlays.</p>
        </div>
        <div class="feature-item">
            <h4>🎵 Custom Voiceovers & BGM</h4>
            <p>Add professional voiceovers and background music to your ads.</p>
        </div>
        <div class="feature-item">
            <h4>📊 Analytics Dashboard</h4>
            <p>Track your ad performance and user feedback in real-time.</p>
        </div>
        <div class="feature-item">
            <h4>🌍 Multi-Format Support</h4>
            <p>Generate videos, billboards, and social posts effortlessly.</p>
        </div>
        <div class="feature-item">
            <h4>🔒 Secure & Private</h4>
            <p>Your data is protected with enterprise-level security.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📈 Stats & Impact</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="stats">
        <div class="stat-item">
            <h2>10K+</h2>
            <p>Ads Generated</p>
        </div>
        <div class="stat-item">
            <h2>500+</h2>
            <p>Happy Users</p>
        </div>
        <div class="stat-item">
            <h2>95%</h2>
            <p>Satisfaction Rate</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">💬 What Users Say</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="testimonial">
        <p>"AdForge revolutionized our ad creation process. The AI videos are stunning!" - Jane Doe, Marketing Lead</p>
    </div>
    <div class="testimonial">
        <p>"Easy to use and incredibly innovative. A must-have for any brand." - John Smith, Entrepreneur</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🚀 Get Started</div>', unsafe_allow_html=True)
    st.markdown("<div class='small-text'>Ready to create your first AI ad? Head over to the Ad Studio and unleash your creativity!</div>", unsafe_allow_html=True)
    if st.button("Go to Ad Studio", key="go_to_studio"):
        st.session_state.menu = "Ad Studio"
        st.experimental_rerun()
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
                    st.session_state.slogan = generate_with_llama(f"slogan for {product
