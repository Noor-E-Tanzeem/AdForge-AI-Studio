# app.py
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip
import tempfile
import os

st.set_page_config(page_title="AdForge AI Studio", page_icon="🤖", layout="wide")

# ---------------- SESSION STATE -----------------
if "profile_set" not in st.session_state:
    st.session_state.profile_set = False

if "profile" not in st.session_state:
    st.session_state.profile = {
        "name": "",
        "email": "",
        "gender": "",
        "bio": "",
        "image_url": ""
    }

if "ads" not in st.session_state:
    st.session_state.ads = []

if "reviews" not in st.session_state:
    st.session_state.reviews = []

# ---------------- PROFILE CREDENTIALS -----------------
if not st.session_state.profile_set:
    st.title("Welcome to AdForge AI Studio 🤖")
    st.subheader("Enter your profile details to continue")

    st.session_state.profile["name"] = st.text_input("Full Name")
    st.session_state.profile["email"] = st.text_input("Email Address")
    st.session_state.profile["gender"] = st.selectbox("Gender", ["Male", "Female", "Other"])
    st.session_state.profile["bio"] = st.text_area("Bio / About You", max_chars=150)
    st.session_state.profile["image_url"] = st.text_input("Profile Image URL", "https://i.postimg.cc/3rz01J48/Screenshot-2026-01-23-021409.png")

    if st.button("Save & Continue"):
        if st.session_state.profile["name"] and st.session_state.profile["email"]:
            st.session_state.profile_set = True
            st.experimental_rerun()
        else:
            st.error("Please fill at least Name and Email to continue.")

# ---------------- MAIN APP -----------------
else:
    # Sidebar with profile info
    with st.sidebar:
        st.image(st.session_state.profile["image_url"], width=150)
        st.write(f"**{st.session_state.profile['name']}**")
        st.write(st.session_state.profile["email"])
        st.write(st.session_state.profile["gender"])
        st.write(st.session_state.profile["bio"])
        st.markdown("---")
        st.write("### Share your Ad Studio")
        st.markdown(
            "[Instagram](https://instagram.com) | [WhatsApp](https://web.whatsapp.com/) | [Twitter](https://twitter.com)"
        )

    # Tabs
    tabs = st.tabs(["Home", "Create Ad", "Profile", "Reviews"])

    # ---------------- HOME -----------------
    with tabs[0]:
        st.header("Welcome to AdForge AI Studio 🤖")
        st.markdown(
            """
            Create professional product ads in minutes.
            
            **Features:**
            - Product image to video with animated captions
            - Voiceover narration using your slogan
            - Emoji animations
            - Download & share videos
            """
        )
        st.markdown("---")
        st.write("Your Previous Ads:")
        for idx, ad in enumerate(st.session_state.ads):
            st.write(f"**Ad {idx+1}:** {ad['product']} - {ad['slogan']}")
            st.video(ad['video_path'])

    # ---------------- CREATE AD -----------------
    with tabs[1]:
        st.header("🛒 Create Your Ad")
        product_name = st.text_input("Product / Topic")
        slogan_text = st.text_area("Slogan / Caption (max 7 lines)", height=120)
        product_img_file = st.file_uploader("Upload Product Image", type=["png", "jpg", "jpeg"])
        generate_btn = st.button("Generate Video 🎬")

        if generate_btn:
            if not product_name or not slogan_text or not product_img_file:
                st.error("Fill all fields and upload product image!")
            else:
                # Save product image
                product_img = Image.open(product_img_file).convert("RGBA")
                temp_img_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                product_img.save(temp_img_file.name)

                # Voiceover using gTTS
                tts = gTTS(text=slogan_text, lang="en")
                temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                tts.save(temp_audio_file.name)

                # Animated text frames
                frames = []
                for i in range(30):  # 3 seconds, 10 fps
                    frame = product_img.copy()
                    draw = ImageDraw.Draw(frame)
                    font = ImageFont.load_default()
                    text_y = 10 + i*2
                    draw.text((10, text_y), slogan_text + " 🚀🎉", font=font, fill="white")
                    frames.append(frame)

                # MoviePy video
                clips = [ImageClip(frame).set_duration(0.1) for frame in frames]
                video_clip = CompositeVideoClip(clips)
                audio_clip = AudioFileClip(temp_audio_file.name)
                video_clip = video_clip.set_audio(audio_clip)

                temp_final = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
                video_clip.write_videofile(temp_final.name, fps=10, codec="libx264", audio_codec="aac")

                # Save ad info
                st.session_state.ads.append({
                    "product": product_name,
                    "slogan": slogan_text,
                    "video_path": temp_final.name
                })

                st.success("🎉 Video Generated!")
                st.video(temp_final.name)

    # ---------------- PROFILE -----------------
    with tabs[2]:
        st.header("Edit Profile")
        st.session_state.profile["name"] = st.text_input("Name", st.session_state.profile["name"])
        st.session_state.profile["email"] = st.text_input("Email", st.session_state.profile["email"])
        st.session_state.profile["gender"] = st.selectbox("Gender", ["Male", "Female", "Other"], index=0)
        st.session_state.profile["bio"] = st.text_area("Bio", st.session_state.profile["bio"])
        st.session_state.profile["image_url"] = st.text_input("Profile Image URL", st.session_state.profile["image_url"])
        st.button("Save Profile")

    # ---------------- REVIEWS -----------------
    with tabs[3]:
        st.header("Ratings & Reviews ⭐")
        rating = st.slider("Your Rating", 1, 5, 5)
        review_text = st.text_area("Write a review")
        if st.button("Submit Review"):
            st.session_state.reviews.append({"rating": rating, "review": review_text})
            st.success("Review submitted!")
        st.write("### All Reviews")
        for rev in st.session_state.reviews:
            st.write(f"⭐ {rev['rating']} - {rev['review']}")
