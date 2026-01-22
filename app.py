import streamlit as st
from moviepy.editor import ImageClip, TextClip, AudioFileClip, CompositeVideoClip
from gtts import gTTS
import tempfile
import requests
from PIL import Image
import base64
import time
import random
import os

# ---------------- GROQ API INTEGRATION ----------------
def call_llama_groq(system_prompt, user_prompt):
    """Real Groq API Call for Llama 3"""
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "llama3-70b-8192",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7
        }
        response = requests.post(url, headers=headers, json=data)
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"Error: Please ensure GROQ_API_KEY is set in Secrets. {str(e)}"

# ---------------- CONFIG & THEME ----------------
st.set_page_config(page_title="AdForge AI Studio | Pro", page_icon="🚀", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Inter:wght@300;400;600&display=swap');
    :root { --primary: #00f2fe; --secondary: #4facfe; --bg: #050505; }
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: var(--bg); color: white; }
    h1, h2, h3 { font-family: 'Orbitron', sans-serif; letter-spacing: 2px; color: var(--primary); }
    .stApp { background: radial-gradient(circle at 50% 0%, #1a1b3a 0%, #050505 100%); }
    .profile-section { position: fixed; top: 15px; right: 25px; z-index: 1000; display: flex; align-items: center; gap: 12px; background: rgba(255,255,255,0.05); padding: 5px 15px; border-radius: 50px; border: 1px solid var(--primary); }
    .profile-icon { width: 40px; height: 40px; border-radius: 50%; border: 2px solid var(--primary); object-fit: cover; }
    .glass-card { background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 20px; padding: 30px; margin-bottom: 25px; }
    .login-logo { display: block; margin: 0 auto 20px auto; width: 120px; filter: drop-shadow(0 0 10px var(--primary)); }
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "profile_created" not in st.session_state:
    st.session_state.update({
        "profile_created": False, "user_name": "", "user_brand": "", "user_gender": "Female",
        "slogan": "", "script": "", "avatar_url": "", "human_img": None, "credits": 500
    })

# ---------------- LOGIN SCREEN ----------------
if not st.session_state.profile_created:
    st.markdown('<div style="height: 10vh;"></div>', unsafe_allow_html=True)
    st.markdown(f'<img src="https://i.postimg.cc/3rz01J48/Screenshot_2026_01_23_021409.png" class="login-logo">', unsafe_allow_html=True)
    
    with st.container():
        cols = st.columns([1, 2, 1])
        with cols[1]:
            st.markdown("<h2 style='text-align: center;'>NEURAL LOGIN</h2>", unsafe_allow_html=True)
            u_name = st.text_input("Operator Name")
            u_brand = st.text_input("Brand Identifier (e.g. Nike, Tesla)")
            u_gender = st.radio("Identity Profile", ["Female", "Male"], horizontal=True)
            
            if st.button("INITIALIZE STUDIO"):
                if u_name and u_brand:
                    st.session_state.user_name = u_name
                    st.session_state.user_brand = u_brand
                    st.session_state.user_gender = u_gender
                    st.session_state.avatar_url = "https://i.postimg.cc/PrVnmBvh/Screenshot-2026-01-23-010324.png" if u_gender == "Female" else "https://i.postimg.cc/5tTtnXH0/Screenshot_2026_01_23_010056.png"
                    st.session_state.profile_created = True
                    st.rerun()
    st.stop()

# ---------------- TOP NAV ----------------
st.markdown(f"""<div class="profile-section"><b>{st.session_state.user_name}</b><img src="{st.session_state.avatar_url}" class="profile-icon"></div>""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown(f"### {st.session_state.user_brand} Studio")
    st.write(f"Credits: {st.session_state.credits} ⚡")
    menu = st.radio("Navigation", ["Dashboard", "AI Generator", "Asset Library"])
    if st.button("Sign Out"):
        st.session_state.profile_created = False
        st.rerun()

# ---------------- DASHBOARD ----------------
if menu == "Dashboard":
    st.title("🎛️ Command Center")
    c1, c2, c3 = st.columns(3)
    c1.metric("API Status", "Groq-Llama 3 Active")
    c2.metric("GPU Load", "12%")
    c3.metric("Render Engine", "V2.5 Cinematic")
    
    st.markdown('<div class="glass-card"><h3>Market Insights</h3><p>Your brand <b>{}</b> is currently trending in "Minimalist Tech" aesthetics. Llama suggests using a <b>Dramatic</b> tone for high conversion.</p></div>'.format(st.session_state.user_brand), unsafe_allow_html=True)

# ---------------- GENERATOR ----------------
elif menu == "AI Generator":
    st.title("🎬 AI Ad Forge")
    
    tab1, tab2, tab3 = st.tabs(["Step 1: AI Writing", "Step 2: Visuals", "Step 3: Render"])
    
    with tab1:
        product = st.text_input("What is the product?")
        tone = st.select_slider("Ad Tone", ["Funny", "Professional", "Dramatic", "Aggressive"])
        
        if st.button("✨ Generate Script (Llama 3)"):
            with st.spinner("Llama 3 is thinking via Groq..."):
                sys_msg = f"You are a master ad copywriter. Write for the brand {st.session_state.user_brand}."
                slogan_p = f"Write a 5 word powerful slogan for {product} with a {tone} tone."
                script_p = f"Write a 30-word high-energy ad script for {product}. Tone: {tone}. Start with a hook."
                
                st.session_state.slogan = call_llama_groq(sys_msg, slogan_p)
                st.session_state.script = call_llama_groq(sys_msg, script_p)
            
            st.subheader(f"Slogan: {st.session_state.slogan}")
            st.write(f"**Script:** {st.session_state.script}")

    with tab2:
        st.markdown("### Upload Assets")
        colA, colB = st.columns(2)
        with colA:
            h_img = st.file_uploader("Spokesperson Image", type=['png', 'jpg'])
            if h_img: st.session_state.human_img = h_img
        with colB:
            st.file_uploader("Product Overlay (Optional)", type=['png', 'jpg'])

    with tab3:
        if st.session_state.human_img and st.session_state.script:
            if st.button("🚀 RENDER FINAL VIDEO"):
                with st.status("Neural Synthesis in progress...") as s:
                    # 1. Voice
                    s.write("Generating Voiceover...")
                    tts = gTTS(st.session_state.script, lang='en')
                    v_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                    tts.save(v_tmp.name)
                    
                    # 2. Process Video
                    s.write("Applying Cinematic Motion & Lip-Sync...")
                    # Save image
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as f:
                        f.write(st.session_state.human_img.getbuffer())
                        img_p = f.name
                    
                    audio = AudioFileClip(v_tmp.name)
                    # Zoom Effect
                    clip = ImageClip(img_p).set_duration(audio.duration).resize(lambda t: 1 + 0.03*t).set_position('center')
                    
                    # Add Script Overlay
                    txt = TextClip(st.session_state.slogan.upper(), fontsize=50, color='white', font='Arial-Bold', bg_color='black').set_duration(audio.duration).set_position(('center', 100))
                    
                    final = CompositeVideoClip([clip, txt]).set_audio(audio)
                    out_p = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
                    final.write_videofile(out_p, fps=24, codec="libx264")
                    
                    st.session_state.credits -= 50
                    s.update(label="Ad Forged Successfully!", state="complete")
                    
                st.video(out_p)
                st.download_button("Download Ad", open(out_p, "rb"), file_name="adforge_pro.mp4")
        else:
            st.warning("Please complete Step 1 (Script) and Step 2 (Image) first!")
