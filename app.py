import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import cv2
import tempfile
from gtts import gTTS
from pydub import AudioSegment
import os

st.set_page_config(page_title="AdForge AI Studio", page_icon="🤖", layout="wide")

# ---------------- CSS ----------------
st.markdown("""
<style>
body {background-color:#0e0f14; color:white;}
.card {background:#171a23; padding:15px; border-radius:15px; margin-bottom:15px;}
.section-title {font-size:24px; font-weight:bold; color:#4da6ff; margin-bottom:10px;}
.profile-top {position:fixed; top:10px; right:20px; text-align:center; z-index:999;}
.profile-top img {border-radius:50%; width:120px; height:120px;}
.share-buttons a {margin-right:5px; text-decoration:none; color:white; background:#4da6ff; padding:5px 10px; border-radius:6px;}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION ----------------
for key in ["name","email","profile_img","ads_history","audio_path"]:
    if key not in st.session_state:
        st.session_state[key] = "" if key!="ads_history" else []

# ---------------- PROFILE ----------------
st.markdown('<div class="profile-top">', unsafe_allow_html=True)
profile_img = st.file_uploader("Upload Profile Image", type=["png","jpg","jpeg"], key="profile_img_uploader")
if profile_img:
    st.session_state.profile_img = profile_img
    st.image(profile_img, width=120)
st.markdown('</div>', unsafe_allow_html=True)

st.title("AdForge AI Studio 🛒")
st.markdown("Create professional animated ads in seconds!")

# ---------------- INPUTS ----------------
with st.expander("Enter Product Details"):
    product_name = st.text_input("🛒 Product / Topic")
    slogan_text = st.text_area("💡 Slogan / Caption (7–8 lines max)")
    voice_lang = st.selectbox("🎤 Voice Language", ["en","hi","es"], index=0)
    submit_btn = st.button("Generate Ad Video")

# ---------------- VIDEO GENERATOR ----------------
def generate_product_video(product_name, slogan_text, voice_lang="en"):

    # ---------------- AUDIO ----------------
    tts = gTTS(text=slogan_text, lang=voice_lang)
    temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_audio.name)
    audio = AudioSegment.from_file(temp_audio.name)
    
    # ---------------- VIDEO ----------------
    width, height = 640, 360
    fps = 24
    duration_sec = max(len(audio)/1000.0, 6)  # min 6 sec
    n_frames = int(fps*duration_sec)
    font = ImageFont.truetype("arial.ttf", 28)

    temp_video = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    video_out = cv2.VideoWriter(temp_video.name, fourcc, fps, (width,height))

    # Preprocess multiline text
    lines = slogan_text.split("\n")
    line_height = 35

    for i in range(n_frames):
        img = Image.new("RGB",(width,height),(20,20,30))
        draw = ImageDraw.Draw(img)
        
        # Scroll effect
        offset = int((i/n_frames)*height)
        for idx, line in enumerate(lines):
            y = height - offset + idx*line_height
            draw.text((20,y), line + " 🚀🎉", font=font, fill=(255,255,255))
        
        frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        video_out.write(frame)

    video_out.release()

    # ---------------- ADD AUDIO ----------------
    # Using pydub to match audio length
    silent = AudioSegment.silent(duration=duration_sec*1000 - len(audio))
    final_audio = audio + silent
    temp_audio_final = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    final_audio.export(temp_audio_final.name, format="mp3")

    # Combine video+audio using ffmpeg
    final_output = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    os.system(f'ffmpeg -y -i "{temp_video.name}" -i "{temp_audio_final.name}" -c:v copy -c:a aac "{final_output.name}"')

    return final_output.name

# ---------------- GENERATE ----------------
if submit_btn:
    if not product_name or not slogan_text:
        st.error("Enter both product name and slogan!")
    else:
        st.info("Generating video... This may take ~15 seconds")
        video_path = generate_product_video(product_name, slogan_text, voice_lang)
        st.video(video_path)

        # Add to session ads history
        st.session_state.ads_history.append({"product":product_name, "video":video_path})

# ---------------- ADS HISTORY ----------------
if st.session_state.ads_history:
    st.markdown("### 📝 Your Generated Ads")
    for ad in st.session_state.ads_history[::-1]:
        st.markdown(f"**Product:** {ad['product']}")
        st.video(ad["video"])

# ---------------- SHARE ----------------
st.markdown("""
<div class='share-buttons'>
<a href='https://instagram.com' target='_blank'>Instagram</a>
<a href='https://wa.me' target='_blank'>WhatsApp</a>
<a href='https://facebook.com' target='_blank'>Facebook</a>
</div>
""", unsafe_allow_html=True)
