import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse
import random
import zipfile
from io import BytesIO

st.set_page_config(
    page_title="TGM Website-to-Promo Asset Generator",
    page_icon="🌐",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Mobile-friendly CSS
st.markdown("""
    <style>
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 720px;
    }
    .stButton > button {
        min-height: 46px;
        font-size: 16px !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
    }
    textarea, input, select {
        font-size: 16px !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🌐 Website-to-Promo Asset Studio")
st.caption("Website URL + Short Description daalein → Voiceover Script aur 5-10 Images tayar payein!")

# 1. User Inputs
st.subheader("1️⃣ Reference Details Dalein")

ref_url = st.text_input(
    "Reference Website URL:",
    placeholder="https://example.com"
)

short_desc = st.text_area(
    "Business / Offer Short Description:",
    placeholder="Jaise: Hum Delhi NCR mein ₹999 mein professional business websites banate hain, WhatsApp integration aur fast delivery ke sath.",
    height=100
)

col1, col2 = st.columns(2)
with col1:
    num_images = st.slider("Kitni Images Chahiye?", min_value=5, max_value=10, value=6)
with col2:
    script_lang = st.selectbox(
        "Voiceover Script Language:",
        ["Hinglish (Best for Reels/Ads)", "Pure Hindi", "English"]
    )

image_aspect = st.selectbox(
    "Image Size / Orientation:",
    ["Vertical / Reels (1080x1920)", "Square / Post (1080x1080)", "Landscape (1920x1080)"]
)

generate_assets_btn = st.button("✨ Generate Script & Images", type="primary", use_container_width=True)

# Helper function to scrape website info safely
def extract_website_context(url):
    context = {"title": "", "meta_desc": "", "headings": []}
    if not url.strip():
        return context
    if not url.startswith("http"):
        url = "https://" + url.strip()
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            if soup.title and soup.title.string:
                context["title"] = soup.title.string.strip()
            meta = soup.find("meta", attrs={"name": "description"})
            if meta and meta.get("content"):
                context["meta_desc"] = meta["content"].strip()
            for tag in soup.find_all(["h1", "h2"])[:6]:
                txt = tag.get_text(" ", strip=True)
                if txt and len(txt) > 3:
                    context["headings"].append(txt)
    except Exception:
        pass
    return context

# Helper function to generate voiceover script
def build_voiceover_script(web_info, desc, lang, scene_count):
    brand_hint = web_info["title"].split("|")[0].split("-")[0].strip() if web_info["title"] else "hamare business"
    services_hint = ", ".join(web_info["headings"][:2]) if web_info["headings"] else ""
    core_offer = desc.strip() if desc.strip() else web_info["meta_desc"]

    if lang == "Hinglish (Best for Reels/Ads)":
        script = (
            f"Kya aap apne business ko next level par le jaana chahte hain? "
            f"Miliye {brand_hint} se! {core_offer} "
            f"{('Humari khaas services hain: ' + services_hint + '. ') if services_hint else ''}"
            f"Aaj hi humse judiye aur apne business ko tezi se grow kijiye. Abhi contact karein!"
        )
    elif lang == "Pure Hindi":
        script = (
            f"Kya aap apne vyapaar ko nayi oonchaiyon par le jaana chahte hain? "
            f"{brand_hint} aapke liye laaya hai behtareen suvidha. {core_offer} "
            f"Behtareen quality aur bharosemand seva ke liye aaj hi sampark karein!"
        )
    else:
        script = (
            f"Looking to take your business to the next level? "
            f"Discover {brand_hint}. {core_offer} "
            f"{('Key highlights include ' + services_hint + '. ') if services_hint else ''}"
            f"Get started today and grow faster with trusted results. Contact us now!"
        )
    return script

# Helper function to build visual scene prompts based on topic
def build_scene_prompts(web_info, desc, count):
    topic_text = f"{web_info['title']} {desc} {' '.join(web_info['headings'])}".strip()
    if not topic_text:
        topic_text = "modern business growth and digital success"

    base_scenes = [
        f"A small business owner looking worried about low customer walk-ins in a shop, cinematic natural lighting, realistic photo, related to {topic_text[:60]}",
        f"Modern professional workspace showcasing {topic_text[:70]}, clean bright aesthetic, commercial photography, 8k",
        f"Close-up of a smartphone and sleek laptop displaying a modern digital service for {topic_text[:60]}, crisp UI, photorealistic",
        f"Happy Indian business owner smiling while checking orders and messages on smartphone, bright modern store, DSLR photo",
        f"Team of professionals collaborating on a digital project in a modern office, warm lighting, high resolution",
        f"Customer happily interacting with a service provider, trustworthy commercial photography, sharp focus",
        f"Digital growth analytics and upward business success visual on a clean tablet screen, modern aesthetic",
        f"Clean promotional banner style workspace with coffee cup, notebook, and laptop showing {topic_text[:50]}, bright daylight",
        f"Satisfied client shaking hands with a business consultant in a modern Delhi NCR office, natural candid photo",
        f"Modern storefront with digital QR code and happy customers entering, vibrant realistic street photography"
    ]
    return base_scenes[:count]

if generate_assets_btn:
    if not ref_url.strip() and not short_desc.strip():
        st.warning("Kripya kam se kam Reference Website URL ya Short Description zaroor dalein!")
    else:
        status = st.empty()
        status.info("🔍 Website aur description ko analyze kiya ja raha hai...")

        web_data = extract_website_context(ref_url)
        
        if web_data["title"]:
            st.success(f"✅ Website Detected: **{web_data['title'][:65]}**")

        # 1. Generate Voiceover Text Prompt
        st.markdown("---")
        st.subheader("🎙️ Ready Voiceover Script (Audio Prompt)")
        st.caption("Is script ko copy karke apne **TGM Promo Video Studio** ke voiceover box mein paste karein:")

        final_script = build_voiceover_script(web_data, short_desc, script_lang, num_images)
        st.text_area("Copy Voiceover Text:", value=final_script, height=130)

        # 2. Generate Images (Instant URLs + Downloadable ZIP)
        st.markdown("---")
        st.subheader(f"🖼️ Generated {num_images} Visual Scenes")
        st.caption("Har image ke neeche uska prompt aur download option diya gaya hai:")

        if "1080x1920" in image_aspect:
            w, h = 720, 1280
        elif "1080x1080" in image_aspect:
            w, h = 1024, 1024
        else:
            w, h = 1280, 720

        scene_prompts = build_scene_prompts(web_data, short_desc, num_images)
        zip_buffer = BytesIO()
        downloaded_count = 0

        status.info(f"🎨 {num_images} images tayar ki ja rahi hain (Isme 10-15 seconds lag sakte hain)...")

        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            for idx, prompt in enumerate(scene_prompts):
                seed = random.randint(100, 99999) + idx
                encoded_p = urllib.parse.quote(prompt + ", photorealistic, high quality, no watermark")
                img_url = f"https://image.pollinations.ai/prompt/{encoded_p}?width={w}&height={h}&seed={seed}&nologo=true"

                st.markdown(f"**Slide #{idx + 1}**")
                st.image(img_url, use_container_width=True)
                
                with st.expander(f"📝 Slide #{idx + 1} Image Prompt Dekhein"):
                    st.code(prompt, language="text")

                # Try fetching image bytes for single ZIP download
                try:
                    img_resp = requests.get(img_url, timeout=25)
                    if img_resp.status_code == 200 and len(img_resp.content) > 1000:
                        zip_file.writestr(f"slide_{idx+1:02d}.jpg", img_resp.content)
                        downloaded_count += 1
                except Exception:
                    pass

                st.divider()

        status.empty()

        if downloaded_count > 0:
            st.download_button(
                label=f"📦 Download All {downloaded_count} Images as ZIP",
                data=zip_buffer.getvalue(),
                file_name="promo_video_images.zip",
                mime="application/zip",
                type="primary",
                use_container_width=True
            )
