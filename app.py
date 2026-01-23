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
def generate_billboard(product, slogan, brand_color, cta, human_img=None, product_img=None):
    """
    Multimodal Billboard Generator
    Uses real-world billboard images (search-based) + AI overlay
    """

    # ---- STEP 1: SEARCH REAL BILLBOARD IMAGE ----
    search_query = f"{product} advertising billboard"
    bing_url = f"https://www.bing.com/images/search?q={search_query}&form=HDRSC2"

    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        html = requests.get(bing_url, headers=headers).text

        # crude but effective image scrape
        img_urls = []
        for line in html.split('"'):
            if line.startswith("https") and ("jpg" in line or "png" in line):
                img_urls.append(line)

        if not img_urls:
            raise Exception("No images found")

        img_url = random.choice(img_urls[:10])
        response = requests.get(img_url, headers=headers, timeout=10)
        bg = Image.open(BytesIO(response.content)).convert("RGB").resize((1280, 720))

    except Exception:
        # fallback background
        bg = Image.new("RGB", (1280, 720), (20, 20, 40))

    draw = ImageDraw.Draw(bg)

    # ---- STEP 2: LOAD FONTS ----
    try:
        font_title = ImageFont.truetype("DejaVuSans-Bold.ttf", 64)
        font_slogan = ImageFont.truetype("DejaVuSans-Bold.ttf", 46)
        font_cta = ImageFont.truetype("DejaVuSans-Bold.ttf", 42)
    except:
        font_title = font_slogan = font_cta = ImageFont.load_default()

    # ---- STEP 3: DECORATIVE OVERLAY ----
    overlay = Image.new("RGBA", bg.size, (0, 0, 0, 120))
    bg = Image.alpha_composite(bg.convert("RGBA"), overlay)

    draw = ImageDraw.Draw(bg)

    # ---- STEP 4: BRAND TEXT ----
    draw.text((40, 40), product.upper(), fill=(255,255,255), font=font_title)
    draw.text((40, 130), slogan, fill=(255, 215, 0), font=font_slogan)

    # ---- STEP 5: CTA BUTTON ----
    draw.rounded_rectangle([900, 560, 1220, 650], radius=35, fill=(255,80,80))
    w, h = draw.textsize(cta, font=font_cta)
    draw.text((1060 - w//2, 585), cta, fill=(255,255,255), font=font_cta)

    # ---- STEP 6: OPTIONAL PRODUCT IMAGE ----
    if product_img:
        prod = Image.open(product_img).convert("RGBA").resize((260,260))
        bg.paste(prod, (40, 420), prod)

    # ---- SAVE ----
    temp_img = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    bg.convert("RGB").save(temp_img.name)
    return temp_img.name

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
