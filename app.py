import streamlit as st
import requests
from groq import Groq
from PIL import Image, ImageDraw, ImageFont
from rembg import remove
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
import tempfile
import os

# Access secrets with error handling to prevent crashes if not set in Streamlit Cloud
try:
    GROQ_API_KEY = st.secrets["groq_api_key"]
    ELEVENLABS_API_KEY = st.secrets["elevenlabs_api_key"]
    ELEVENLABS_VOICE_ID = st.secrets["elevenlabs_voice_id"]
except KeyError as e:
    st.error(f"Missing secret: {e}. Please add 'groq_api_key', 'elevenlabs_api_key', and 'elevenlabs_voice_id' in Streamlit Cloud settings under Secrets.")
    st.stop()

# Add this for testing (remove after fixing)
st.write("Secrets check:", "groq_api_key" in st.secrets, "elevenlabs_api_key" in st.secrets, "elevenlabs_voice_id" in st.secrets)

# Initialize Groq client for script generation
groq_client = Groq(api_key=GROQ_API_KEY)

# Function to generate ad script using Groq API
def generate_script(topic):
    prompt = f"Write a short, engaging 30-second ad script for {topic}. Keep it under 100 words."
    response = groq_client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150
    )
    return response.choices[0].message.content.strip()

# Function to generate voiceover MP3 using Eleven Labs API directly (no SDK)
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
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            temp_file.write(response.content)
            return temp_file.name
    else:
        raise Exception(f"Eleven Labs API error: {response.status_code} - {response.text}")

# Function to edit image: background removal, text overlay, resize
def edit_image(image_file, text_overlay, resize_width=800, resize_height=600):
    image = Image.open(image_file)
    image_no_bg = remove(image)  # Background removal
    image_resized = image_no_bg.resize((resize_width, resize_height))  # Resize
    draw = ImageDraw.Draw(image_resized)
    font = ImageFont.load_default()
    draw.text((50, 50), text_overlay, fill="white", font=font)  # Text overlay
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
        image_resized.save(temp_file.name)
        return temp_file.name

# Function to create simple slideshow video
def create_slideshow_video(image_path, audio_path, duration=10):
    image_clip = ImageClip(image_path).set_duration(duration)
    audio_clip = AudioFileClip(audio_path).set_duration(duration)
    video_clip = image_clip.set_audio(audio_clip)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
        video_clip.write_videofile(temp_file.name, fps=24, codec="libx264", audio_codec="aac")
        return temp_file.name

# Streamlit UI for the app
st.title("Ad Video Generator")
st.write("Generate scripts, voiceovers, edit images, and create slideshow videos for your hackathon project!")

# Step 1: Script Generator
topic = st.text_input("Enter ad topic (e.g., 'a new energy drink')")
if st.button("Generate Script"):
    if topic:
        script = generate_script(topic)
        st.session_state.script = script
        st.success("Script generated!")
        st.text_area("Generated Script", script, height=100)
    else:
        st.error("Please enter a topic.")

# Step 2: Voiceover MP3
if "script" in st.session_state and st.button("Generate Voiceover MP3"):
    try:
        audio_path = generate_voiceover(st.session_state.script, ELEVENLABS_VOICE_ID)
        st.session_state.audio_path = audio_path
        st.success("Voiceover generated!")
        st.audio(audio_path, format="audio/mp3")
        with open(audio_path, "rb") as file:
            st.download_button("Download MP3", file, file_name="voiceover.mp3")
    except Exception as e:
        st.error(f"Error generating voiceover: {e}")

# Step 3: Billboard PNG with Smart Photoshop (Background removal, Text overlay, Resize)
uploaded_image = st.file_uploader("Upload an image for billboard (PNG/JPG)", type=["png", "jpg", "jpeg"])
text_overlay = st.text_input("Text to overlay on image")
resize_width = st.number_input("Resize Width", value=800, min_value=100)
resize_height = st.number_input("Resize Height", value=600, min_value=100)

if uploaded_image and st.button("Edit Image"):
    edited_image_path = edit_image(uploaded_image, text_overlay, resize_width, resize_height)
    st.session_state.edited_image_path = edited_image_path
    st.success("Image edited!")
    st.image(edited_image_path, caption="Edited Billboard")
    with open(edited_image_path, "rb") as file:
        st.download_button("Download PNG", file, file_name="billboard.png")

# Step 4: Simple Slideshow Video
if "audio_path" in st.session_state and "edited_image_path" in st.session_state and st.button("Create Slideshow Video"):
    video_path = create_slideshow_video(st.session_state.edited_image_path, st.session_state.audio_path)
    st.success("Video created!")
    st.video(video_path)
    with open(video_path, "rb") as file:
        st.download_button("Download MP4", file, file_name="slideshow.mp4")

# Cleanup temporary files to avoid storage issues
for key in ["audio_path", "edited_image_path"]:
    if key in st.session_state and os.path.exists(st.session_state[key]):
        os.unlink(st.session_state[key])
