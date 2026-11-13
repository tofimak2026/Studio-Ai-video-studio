import asyncio
import io
import os
import urllib.parse
import edge_tts
from moviepy.editor import AudioFileClip, ImageClip, VideoFileClip, concatenate_videoclips
import numpy as np
from PIL import Image, ImageFilter, ImageOps
from rembg import new_session, remove
import requests
import streamlit as st

st.set_page_config(page_title="Ago Italy AI Studio", page_icon="🚀", layout="wide")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 استوديو خاص - Ago Italy")
    password_input = st.text_input("كلمة المرور:", type="password")
    if st.button("دخول", type="primary"):
        secret_pass = st.secrets.get("APP_PASSWORD", "ago2026")
        if password_input == secret_pass or password_input == "ago2026":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ كلمة المرور غير صحيحة!")
    st.stop()

st.title("🚀 استوديو الذكاء الاصطناعي المتكامل - Ago Italy")

@st.cache_resource
def get_bg_session():
    return new_session("u2netp")

def prepare_image(uploaded_file, max_dim=1200):
    img = Image.open(uploaded_file)
    img = ImageOps.exif_transpose(img)
    img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
    return img

async def create_tts(text, voice, out_path):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(out_path)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📸 1. تجهيز صور المتجر",
    "✨ 2. دمج الحقائب في ديكور فاخر",
    "🎙️ 3. تعليق صوتي سريع",
    "🎬 4. فيديو إعلاني للمتجر",
    "🧹 5. صانع Shorts للتنظيف",
])

with tab1:
    st.header("تحسين جودة ومقاسات صور المنتجات لمتجر Shopify")
    uploaded_files = st.file_uploader("اختر صور المنتجات:", type=["png", "jpg", "jpeg", "webp"], accept_multiple_files=True, key="tab1_uploader")
    remove_bg_tab1 = st.checkbox("إزالة الخلفية وتفريغ المنتج على خلفية بيضاء نقية", value=True)
    if uploaded_files and st.button("✨ تجهيز الصور الآن"):
        with st.spinner("جاري معالجة الصور وتفريغ الخلفية..."):
            session = get_bg_session() if remove_bg_tab1 else None
            results = []
            for idx, file in enumerate(uploaded_files):
                img = prepare_image(file, max_dim=1100).convert("RGBA")
                if remove_bg_tab1:
                    img = remove(img, session=session)
                square_bg = Image.new("RGBA", (1200, 1200), (255, 255, 255, 255))
                paste_x = (1200 - img.width) // 2
                paste_y = (1200 - img.height) // 2
                square_bg.paste(img, (paste_x, paste_y), img)
                final_sq = square_bg.convert("RGB")
                buf = io.BytesIO()
                final_sq.save(buf, format="JPEG", quality=95)
                clean_name = f"shopify_bag_{idx+1}.jpg"
                results.append({"name": clean_name, "bytes": buf.getvalue()})
            st.session_state.clean_images = results
    if "clean_images" in st.session_state and st.session_state.clean_images:
        cols = st.columns(2)
        for idx, item in enumerate(st.session_state.clean_images):
            with cols[idx % 2]:
                st.image(item["bytes"], caption=item["name"], use_container_width=True)
                st.download_button(
                    label=f"⬇️ تحميل {item['name']}",
                    data=item["bytes"],
                    file_name=item["name"],
                    mime="image/jpeg",
                    key=f"dl_tab1_{idx}"
                )

with tab2:
    st.header("تفريغ الحقيبة تلقائياً ودمجها في ديكور فاخر")
    ref_product = st.file_uploader("ارفع صورة الحقيبة (سيتم قص الخلفية تلقائياً):", type=["png", "jpg", "jpeg", "webp"], key="tab2_uploader")
    scene_presets = {
        "طاولة رخامية فاخرة مع إضاءة شمس": "luxury white marble table top surface, soft warm sunlight shadows, minimalist aesthetic product photography background",
        "طاولة خشبية في غرفة معيشة إيطالية": "warm oak wooden table top in a modern cozy Italian living room, soft blurred background, natural daylight",
        "مقهى إيطالي أنيق في ميلانو": "chic outdoor cafe table surface in Milan Italy, blurred background, golden hour sunlight, luxury editorial photography",
        "منصة عرض استوديو احترافية": "minimalist beige stone podium studio background, soft dramatic lighting, commercial photography",
        "وصف مخصص (اكتب بالأسفل)": "custom",
    }
    selected_scene = st.selectbox("اختر نوع الخلفية أو الديكور:", list(scene_presets.keys()))
    if scene_presets[selected_scene] == "custom":
        scene_prompt = st.text_input("اكتب وصف الخلفية بالإنجليزية:", "luxury marble pedestal with soft warm lighting, product display")
    else:
        scene_prompt = scene_presets[selected_scene]
    if st.button("🎨 توليد المشهد ودمج الحقيبة"):
        with st.spinner("جاري قص الحقيبة وتوليد الديكور بالذكاء الاصطناعي..."):
            encoded_prompt = urllib.parse.quote(scene_prompt)
            base_api = "https://pollinations.ai"
            bg_url = f"{base_api}{encoded_prompt}?width=1024&height=1024&nologo=true"
            try:
                response = requests.get(bg_url, timeout=45)
                if response.status_code == 200:
                    bg_img = Image.open(io.BytesIO(response.content)).convert("RGBA").resize((1024, 1024))
                    if ref_product:
                        session = get_bg_session()
                        prod_img = prepare_image(ref_product, max_dim=650).convert("RGBA")
                        prod_no_bg = remove(prod_img, session=session)
                        pos_x = (1024 - prod_no_bg.width) // 2
                        pos_y = int((1024 - prod_no_bg.height) * 0.58)
                        bg_img.paste(prod_no_bg, (pos_x, pos_y), prod_no_bg)
                    final_out = bg_img.convert("RGB")
                    buf = io.BytesIO()
                    final_out.save(buf, format="JPEG", quality=95)
                    st.session_state.luxury_scene = buf.getvalue()
                else:
                    st.error("خادم الصور مشغول حالياً، اضغط توليد مرة أخرى.")
            except Exception as e:
                st.error("حدث خطأ في الاتصال بخادم الصور، حاول مرة أخرى.")
    if "luxury_scene" in st.session_state:
        st.image(st.session_state.luxury_scene, caption="الصورة النهائية الجاهزة", use_container_width=True)
        st.download_button(
            label="⬇️ تحميل الصورة الفاخرة",
            data=st.session_state.luxury_scene,
            file_name="ago_italy_luxury.jpg",
            mime="image/jpeg",
            key="dl_tab2"
        )

with tab3:
    st.header("توليد التعليق الصوتي الفوري للإعلانات والفيديوهات")
    voices = {
        "🇮🇹 إيطالي - أنثى (Elsa)": "it-IT-ElsaNeural",
        "🇮🇹 إيطالي - أنثى (Isabella)": "it-IT-IsabellaNeural",
        "🇮🇹 إيطالي - رجل (Diego)": "it-IT-DiegoNeural",
        "🇸🇦 عربي خليجي - أنثى (Zariyah)": "ar-SA-ZariyahNeural",
        "🇸🇦 عربي خليجي - رجل (Hamed)": "ar-SA-HamedNeural",
        "🇦🇪 عربي إماراتي - أنثى (Fatima)": "ar-AE-FatimaNeural",
        "🇪🇬 عربي عام - أنثى (Salma)": "ar-EG-SalmaNeural",
        "🇬🇧 إنجليزي - أنثى (Sonia)": "en-GB-SoniaNeural",
        "🇺🇸 إنجليزي - أنثى (Jenny)": "en-US-JennyNeural",
        "🇺🇸 إنجليزي - رجل (Christopher)": "en-US-ChristopherNeural",
    }
    selected_voice_label = st.selectbox("اختر اللغة والصوت:", list(voices.keys()))
    selected_voice = voices[selected_voice_label]
    script_text = st.text_area("اكتب النص:", value="Scopri la nuova collezione Ago Italy! Spedizione veloce e pagamento alla consegna.", height=120, key="tts_script")
    if st.button("🎙️ توليد الصوت الآن"):
        if script_text.strip():
            with st.spinner("جاري تسجيل الصوت..."):
                audio_filename = "generated_voice.mp3"
                asyncio.run(create_tts(script_text, selected_voice, audio_filename))
                with open(audio_filename, "rb") as f:
                    st.session_state.generated_audio = f.read()
        else:
            st.warning("يرجى كتابة النص أولاً.")
    if "generated_audio" in st.session_state:
        st.audio(st.session_state.generated_audio, format="audio/mp3")
        st.download_button(
            label="⬇️ تحميل الملف الصوتي (MP3)",
            data=st.session_state.generated_audio,
            file_name="ago_italy_audio.mp3",
            mime="audio/mpeg",
            key="dl_tab3"
        )

with tab4:
    st.header("صناعة فيديو إعلاني جاهز لفيسبوك وتيك توك")
    video_images = st.file_uploader("اختر صور المنتج بالترتيب:", type=["png", "jpg", "jpeg"], accept_multiple_files=True, key="tab4_uploader")
    video_audio = st.file_uploader("ارفع ملف الصوت (اختياري):", type=["mp3", "wav"], key="tab4_audio")
    aspect_ratio = st.radio("اختر مقاس الفيديو:", ["📱 عمودي 9:16 (TikTok / Reels)", "💻 عرضي 16:9"])
    target_w, target_h = (720, 1280) if "9:16" in aspect_ratio else (1280, 720)
    if video_images and st.button("🎬 صناعة الفيديو الإعلاني الآن"):
        with st.spinner("جاري مونتاج الفيديو..."):
            clips = []
            audio_clip = None
            total_duration = len(video_images) * 3.0
            if video_audio:
                ext = os.path.splitext(video_audio.name)
                temp_aud_name = f"temp_audio{ext}"
                with open(temp_aud_name, "wb") as f:
                    f.write(video_audio.read())
                audio_clip = AudioFileClip(temp_aud_name)
                total_duration = audio_clip.duration
            duration_per_img = total_duration / len(video_images)
            for idx, img_file in enumerate(video_images):
                pil_img = prepare_image(img_file).convert("RGB")
                bg = pil_img.resize((target_w, target_h))
                bg = bg.filter(ImageFilter.GaussianBlur(30))
                new_w = int(target_w * 0.9)
                new_h = int(target_h * 0.8)
                pil_img.thumbnail((new_w, new_h))
