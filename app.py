import streamlit as st
import tempfile, base64, requests, numpy as np
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
from groq import Groq
from moviepy.editor import ImageClip, TextClip, CompositeVideoClip, AudioFileClip

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="AdForge AI Studio",
    page_icon="🎬",
    layout="wide"
)

# -------------------------------------------------
# INIT LLaMA (Groq)
# -------------------------------------------------
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# -------------------------------------------------
# MULTI-AGENT SYSTEM
# -------------------------------------------------
def agentic_campaign(product, audience, tone, cta):
    prompt = f"""
You are an AGENTIC AI SYSTEM trained in multi-agent collaboration.

AGENT 1 – Brand Strategist:
Define brand personality for "{product}"

AGENT 2 – Audience Analyst:
Adapt messaging for audience "{audience}"

AGENT 3 – Copywriter:
Write a CINEMATIC AD SCRIPT of 8–10 SHORT LINES
• Emotional
• Marketing-grade
• No repetition
• End with CTA "{cta}"

AGENT 4 – Slogan Architect:
Create ONE bold billboard slogan (max 8 words)

Few-shot example:
Product: Electric Bike
Script:
1. Silence isn’t empty — it’s powerful.
2. The city moves when you do.
3. Zero fuel. Pure freedom.
4. Acceleration that thrills.
5. Control in every curve.
6. Designed for tomorrow.
7. Ride smarter. Ride cleaner.
8. The future is electric.

Return STRICT JSON:
{{"slogan":"...", "script":"line1\\nline2\\n..."}}
"""

    res = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role":"user","content":prompt}],
        temperature=0.85
    )

    return eval(res.choices[0].message.content)

# -------------------------------------------------
# VOICE AGENT
# -------------------------------------------------
def voice_agent(text):
    tts = gTTS(text)
    f = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(f.name)
    return f.name

# -------------------------------------------------
# BILLBOARD VISUAL AGENT
# -------------------------------------------------
def billboard_agent(product, slogan, cta):
    img = Image.new("RGB",(1280,720),(12,14,30))
    d = ImageDraw.Draw(img)

    try:
        big = ImageFont.truetype("DejaVuSans-Bold.ttf",80)
        mid = ImageFont.truetype("DejaVuSans-Bold.ttf",55)
        btn = ImageFont.truetype("DejaVuSans-Bold.ttf",45)
    except:
        big = mid = btn = ImageFont.load_default()

    # Neon Header
    d.rectangle([0,0,1280,120],fill=(255,60,100))
    d.text((40,25),product.upper(),font=big,fill="white")

    # Glow slogan
    d.text((80,260),slogan,font=mid,fill=(0,255,220))

    # Decorative lights
    for x in range(0,1280,70):
        d.ellipse([x,650,x+20,670],fill=(255,255,100))

    # CTA Button
    d.rounded_rectangle([500,560,780,640],radius=35,fill=(0,200,120))
    d.text((560,580),cta,font=btn,fill="black")

    f = tempfile.NamedTemporaryFile(delete=False,suffix=".png")
    img.save(f.name)
    return f.name

# -------------------------------------------------
# VIDEO DIRECTOR AGENT
# -------------------------------------------------
def video_agent(image_path, audio_path, slogan):
    base = ImageClip(image_path).set_duration(8)

    text = TextClip(
        slogan,
        fontsize=60,
        color="white",
        method="caption",
        size=(900,None)
    ).set_position(("center",480)).set_duration(8)

    audio = AudioFileClip(audio_path)
    final = CompositeVideoClip([base,text]).set_audio(audio)

    out = tempfile.NamedTemporaryFile(delete=False,suffix=".mp4")
    final.write_videofile(out.name,fps=24,codec="libx264",audio_codec="aac")
    return out.name

# -------------------------------------------------
# UI – REAL APP FEEL
# -------------------------------------------------
st.title("🎬 AdForge AI Studio")
st.markdown("**Agentic AI-powered Advertisement Creation Platform**")

st.sidebar.header("📌 Campaign Settings")
product = st.sidebar.text_input("Product / Brand")
audience = st.sidebar.selectbox("Target Audience",["General","Youth","Corporate","Luxury"])
tone = st.sidebar.selectbox("Tone",["Emotional","Corporate","Luxury","Dramatic"])
cta = st.sidebar.selectbox("Call To Action",["Buy Now","Experience It","Upgrade Today"])

st.markdown("""
### 🔍 What this app does
• Uses **multi-agent LLaMA architecture**  
• Generates **long-form cinematic scripts**  
• Designs **decorative billboards**  
• Produces **AI voiceover**  
• Renders a **real advertisement video**  

_No paid video APIs. No shortcuts._
""")

if st.button("🚀 Generate Full AI Advertisement"):
    if not product:
        st.error("Product name required")
    else:
        with st.spinner("Multi-agent system collaborating..."):
            data = agentic_campaign(product,audience,tone,cta)

        st.subheader("🎯 AI Slogan")
        st.success(data["slogan"])

        st.subheader("📝 Cinematic Script (8–10 lines)")
        st.text(data["script"])

        audio = voice_agent(data["script"])
        st.audio(audio)

        billboard = billboard_agent(product,data["slogan"],cta)
        st.image(billboard,use_column_width=True)

        video = video_agent(billboard,audio,data["slogan"])
        st.subheader("🎥 AI Advertisement Video")
        st.video(video)

st.markdown("---")
st.caption("Built with Agenting AI • Hackathon Edition • AdForge AI Studio")
