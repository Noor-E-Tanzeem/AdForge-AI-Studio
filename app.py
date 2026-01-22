import streamlit as st
import requests
from groq import Groq
from PIL import Image, ImageDraw, ImageFont
from rembg import remove
from moviepy.editor import ImageClip, AudioFileClip
import tempfile
import os

# ---------------------------
# Secrets Handling
# ---------------------------
try:
    GROQ_API_KEY = st.secrets["groq_api_key"]
    ELEVENLABS_API_KEY = st.secrets["elevenlabs_api_key"]
    ELEVENLABS_VOICE_ID = st.secrets["elevenlabs_voice_id"]
except KeyError as e:
    st.error(
        "Missing secrets! Please add:\n"
        "- groq_api_key\n"
        "- elevenlabs_api_key\n"
        "- elevenlabs_voice_id\n"
        "in Streamlit Cloud → Settings → Secrets"
    )
    st.stop()

# ---------------------------
# Initialize Groq Client Safely
# ---------------------------
try:
    groq_client = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    st.error(f"Groq initialization failed: {e}")
    st.stop()

# ---------------------------
# Functions
# ---------------------------

def generate_script(topic):
    prompt = f"Write a short, engaging 30-second ad script for {topic}. Keep it under 100 words."
    try:
        response = groq_client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise Exception(f"Groq API error: {e}")


def generate_voiceover(text, voice_id):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        temp_file.write(response.content)
        temp_file.close()
        return temp_file.name
    else:
        raise Exception(f"ElevenLabs API error: {response.status_code} - {response.text}")


def edit_image(image_file, text_overlay, resize_width=800, resize_height=600):
    try:
        image = Image.open(image_file).convert("RGBA")
        image_no_bg = remove(image)
        image_resized = image_no_bg.resize((resize_width, resize_height))

        draw = ImageDraw.Draw(image_resized)
        font = ImageFont.load_default()

        draw.text((30, 30), text_overlay, fill="white", font=font)

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        image_resized.save(temp_file.name)
        temp_file.close()

        return temp_file.name

    except Exception as e:
        raise Exception(f"Image processing error: {e}")


def create_slideshow_video(image_path, audio_path, duration=10):
    try:
        image_clip = ImageClip(image_path).set_duration(duration)
        audio_clip = AudioFileClip(audio_path).set_duration(duration)
        video_clip = image_clip.set_audio(audio_clip)

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        temp_file.close()

        video_clip.write_videofile(
            temp_file.name,
            fps=24,
            codec="libx264",
            audio_codec="aac",
            verbose=False,
            logger=None
        )

        return temp_file.name

    except Exception as e:
        raise Exception(f"Video creation error: {e}")


# ---------------------------
# Streamlit UI
# ---------------------------

st.set_page_config(page_title="AdForge AI Studio", layout="centered")
st.title("🎬 AdForge AI Studio")
st.write("Generate scripts, voiceovers, smart billboards, and slideshow ads.")

# Step 1: Script Generator
st.header("1️⃣ Script Generator")
topic = st.text_input("Enter ad topic (e.g., 'a new energy drink')")

if st.button("Generate Script"):
    if topic:
        with st.spinner("Generating script..."):
            try:
                script = generate_script(topic)
                st.session_state.script = script
                st.success("Script generated!")
                st.text_area("Generated Script", script, height=120)
            except Exception as e:
                st.error(str(e))
    else:
        st.error("Please enter a topic.")

# Step 2: Voiceover MP3
st.header("2️⃣ Voiceover Generator")

if "script" in st.session_state:
    if st.button("Generate Voiceover MP3"):
        with st.spinner("Generating voiceover..."):
            try:
                audio_path = generate_voiceover(st.session_state.script, ELEVENLABS_VOICE_ID)
                st.session_state.audio_path = audio_path
                st.success("Voiceover generated!")
                st.audio(audio_path, format="audio/mp3")

                with open(audio_path, "rb") as file:
                    st.download_button("Download MP3", file, file_name="voiceover.mp3")

            except Exception as e:
                st.error(str(e))

# Step 3: Billboard PNG with Smart Photoshop
st.header("3️⃣ Smart Billboard Editor")

uploaded_image = st.file_uploader("Upload an image (PNG/JPG)", type=["png", "jpg", "jpeg"])
text_overlay = st.text_input("Text to overlay on image")
resize_width = st.number_input("Resize Width", value=800, min_value=100)
resize_height = st.number_input("Resize Height", value=600, min_value=100)

if uploaded_image and st.button("Edit Image"):
    with st.spinner("Editing image..."):
        try:
            edited_image_path = edit_image(uploaded_image, text_overlay, resize_width, resize_height)
            st.session_state.edited_image_path = edited_image_path
            st.success("Image edited!")
            st.image(edited_image_path, caption="Edited Billboard")

            with open(edited_image_path, "rb") as file:
                st.download_button("Download PNG", file, file_name="billboard.png")

        except Exception as e:
            st.error(str(e))

# Step 4: Simple Slideshow Video
st.header("4️⃣ Slideshow Video")

if "audio_path" in st.session_state and "edited_image_path" in st.session_state:
    if st.button("Create Slideshow Video"):
        with st.spinner("Creating video..."):
            try:
                video_path = create_slideshow_video(
                    st.session_state.edited_image_path,
                    st.session_state.audio_path
                )
                st.success("Video created!")
                st.video(video_path)

                with open(video_path, "rb") as file:
                    st.download_button("Download MP4", file, file_name="slideshow.mp4")

            except Exception as e:
                st.error(str(e))

# ---------------------------
# Cleanup Temp Files
# ---------------------------

def cleanup_file(key):
    if key in st.session_state:
        try:
            path = st.session_state[key]
            if os.path.exists(path):
                os.unlink(path)
        except:
            pass
        del st.session_state[key]

if st.button("🧹 Clear Generated Files"):
    cleanup_file("audio_path")
    cleanup_file("edited_image_path")
    st.success("Temporary files cleared!")
