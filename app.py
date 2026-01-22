import streamlit as st
from groq import Groq
from PIL import Image, ImageDraw, ImageFont
from rembg import remove
from moviepy.editor import ImageClip, AudioFileClip
import requests
import os

# ---------- CONFIG ----------
st.set_page_config(page_title="AdForge AI Studio", layout="wide")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.title("🎬 AdForge AI Studio")
st.caption("One-click Ads, Billboards, Voiceovers & Smart Photoshop")

# ---------- INPUTS ----------
product_name = st.text_input("Product Name")
description = st.text_area("Product Description")
audience = st.text_input("Target Audience")
tone = st.selectbox("Tone", ["Funny", "Premium", "Emotional", "Bold", "Energetic"])
platform = st.selectbox("Platform", ["Instagram", "YouTube", "Billboard", "TV"])
duration = st.selectbox("Ad Duration", ["15 seconds", "30 seconds"])

uploaded_image = st.file_uploader("Upload Product Image (Optional)", type=["png", "jpg", "jpeg"])

# ---------- FUNCTIONS ----------

def generate_script():
    prompt = f"""
    Create a {duration} ad for:
    Product: {product_name}
    Description: {description}
    Target Audience: {audience}
    Tone: {tone}
    Platform: {platform}

    Output:
    1. Ad Script
    2. Voiceover Text
    3. Headline
    4. Tagline
    5. Call to Action
    """

    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


def remove_bg(image_bytes):
    return remove(image_bytes)


def create_billboard(text):
    img = Image.new("RGB", (1024, 576), color=(20, 20, 20))
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", 48)
    except:
        font = ImageFont.load_default()

    draw.text((50, 200), text[:80], fill="white", font=font)
    path = "billboard.png"
    img.save(path)
    return path


def generate_voiceover(text):
    url = "https://api.elevenlabs.io/v1/text-to-speech/" + st.secrets["ELEVENLABS_VOICE_ID"]
    headers = {
        "xi-api-key": st.secrets["ELEVENLABS_API_KEY"],
        "Content-Type": "application/json"
    }
    data = {
        "text": text,
        "voice_settings": {"stability": 0.4, "similarity_boost": 0.8}
    }

    r = requests.post(url, json=data, headers=headers)

    if r.status_code == 200:
        with open("voiceover.mp3", "wb") as f:
            f.write(r.content)
        return "voiceover.mp3"
    else:
        return None


def create_video(image_path, audio_path):
    clip = ImageClip(image_path).set_duration(10)

    if audio_path:
        audio = AudioFileClip(audio_path)
        clip = clip.set_audio(audio)

    output = "ad_video.mp4"
    clip.write_videofile(output, fps=24)
    return output


# ---------- MAIN ----------
if st.button("Generate Ad Studio Output"):

    if not product_name or not description or not audience:
        st.warning("Please fill all required fields.")
    else:
        with st.spinner("Generating AI Ad Content..."):

            ad_text = generate_script()
            st.subheader("📜 Ad Script & Content")
            st.write(ad_text)

            # Extract voiceover fallback
            voiceover_text = ad_text[:800]

            # Voiceover
            audio_file = generate_voiceover(voiceover_text)

            if audio_file:
                st.subheader("🔊 AI Voiceover")
                st.audio(audio_file)

            # Billboard
            billboard_path = create_billboard(product_name + " - " + tone)
            st.subheader("🖼️ Billboard Preview")
            st.image(billboard_path)

            # Smart Photoshop
            if uploaded_image:
                st.subheader("🧠 Smart Photoshop")

                input_bytes = uploaded_image.read()
                no_bg = remove_bg(input_bytes)

                with open("product_no_bg.png", "wb") as f:
                    f.write(no_bg)

                st.image("product_no_bg.png", caption="Background Removed")

            # Video
            if audio_file:
                video_file = create_video(billboard_path, audio_file)
                st.subheader("🎥 Auto Ad Video")
                st.video(video_file)

        st.success("AdForge AI Studio Output Ready!")
