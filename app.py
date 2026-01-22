# app.py
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip
import tempfile
import os

st.set_page_config(page_title="AdForge AI Studio", page_icon="🤖", layout="wide")

# --- Session State Setup ---
if "profile" not in st.session_state:
    st.session_state.profile = {
        "name": "Noor E Tanzeem",
        "email": "noor@example.com",
        "gender": "Male",
        "bio": "Creative Ad Maker",
        "image_url": "https://i.postimg.cc/3rz01J48/Screenshot-2026-01-23-021409.png"
    }

if "ads" not in st.session_state:
    st.session_state.ads = []

if "reviews" not in st.session_state:
    st.session_state.reviews = []

# --- Sidebar / Profile ---
with st.sidebar:
    st.image(st.session_state.profile["image_url"], width=150)
    st.write(f"**{st.session_state.profile['name']}**")
    st.write(st.session_state.profile["email"])
    st.write(st.session_state.profile["gender"])
    st.write(st.session_state.profile["bio"])
    st.markdown("---")
    st.write("### Share your Ad Studio")
    st.markdown(
        """
        [Instagram](https://instagram.com) | 
        [WhatsApp](https://web.whatsapp.com/) | 
        [Twitter](https://twitter.com)
        """
    )

# --- Tabs ---
tabs = st.tabs(["Home", "Create Ad", "Profile", "Reviews"])

# --- HOME ---
with tabs[0]:
    st.markdown("## Welcome to AdForge AI Studio 🤖")
    st.image("https://i.postimg.cc/3rz01J48/Screenshot-2026-01-23-021409.png", width=300)
    st.markdown("""
    Create professional product ads in minutes.
    Features:
    - Product image to video with captions
    - Animated emoji text
    - Voiceover narration
    - Share to social media
    """)
    st.markdown("---")
    st.write("Your previous ads:")
    for idx, ad in enumerate(st.session_state.ads):
        st.write(f"**Ad {idx+1}:** {ad['product']} - {ad['slogan']}")

# --- CREATE AD ---
with tabs[1]:
    st.subheader("🛒 Product / Topic")
    product_name = st.text_input("Enter Product Name / Topic")
    st.subheader("💡 Slogan / Caption")
    slogan_text = st.text_area("Enter your slogan (max 7 lines)", height=120)

    product_img_file = st.file_uploader("Upload Product Image", type=["png", "jpg", "jpeg"])

    generate_btn = st.button("Generate Video 🎬")

    if generate_btn:
        if not product_name or not slogan_text or not product_img_file:
            st.error("Please fill all inputs and upload a product image.")
        else:
            # --- Save product image temporarily ---
            product_img = Image.open(product_img_file).convert("RGBA")
            temp_img_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            product_img.save(temp_img_file.name)

            # --- Generate audio using gTTS ---
            tts = gTTS(text=slogan_text, lang="en")
            temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            tts.save(temp_audio_file.name)

            # --- Create animated text over image ---
            frames = []
            for i in range(30):  # 3 seconds, 10 fps
                frame = product_img.copy()
                draw = ImageDraw.Draw(frame)
                font = ImageFont.load_default()
                text_y = 10 + i*2
                draw.text((10, text_y), slogan_text + " 🚀🎉", font=font, fill="white")
                frames.append(frame)

            # --- Create MoviePy video ---
            clips = [ImageClip(frame).set_duration(0.1) for frame in frames]
            video_clip = CompositeVideoClip(clips)

            audio_clip = AudioFileClip(temp_audio_file.name)
            video_clip = video_clip.set_audio(audio_clip)
            temp_final = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            video_clip.write_videofile(temp_final.name, fps=10, codec="libx264", audio_codec="aac")

            # --- Save ad info ---
            st.session_state.ads.append({
                "product": product_name,
                "slogan": slogan_text,
                "video_path": temp_final.name
            })

            st.success("🎉 Video Generated!")
            st.video(temp_final.name)

# --- PROFILE EDIT ---
with tabs[2]:
    st.subheader("Edit Profile")
    st.session_state.profile["name"] = st.text_input("Name", st.session_state.profile["name"])
    st.session_state.profile["email"] = st.text_input("Email", st.session_state.profile["email"])
    st.session_state.profile["gender"] = st.selectbox("Gender", ["Male", "Female", "Other"], index=0)
    st.session_state.profile["bio"] = st.text_area("Bio", st.session_state.profile["bio"])
    st.session_state.profile["image_url"] = st.text_input("Profile Image URL", st.session_state.profile["image_url"])
    st.button("Save Profile")

# --- REVIEWS ---
with tabs[3]:
    st.subheader("Ratings & Reviews ⭐")
    rating = st.slider("Your Rating", 1, 5, 5)
    review_text = st.text_area("Write a review")
    if st.button("Submit Review"):
        st.session_state.reviews.append({"rating": rating, "review": review_text})
        st.success("Review submitted!")
    st.write("### All Reviews")
    for rev in st.session_state.reviews:
        st.write(f"⭐ {rev['rating']} - {rev['review']}")
