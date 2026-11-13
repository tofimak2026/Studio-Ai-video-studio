import asyncio
import base64
import io
import os
import urllib.parse
import edge_tts
from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips
import numpy as np
from PIL import Image, ImageFilter, ImageOps
import requests
import streamlit as st

st.set_page_config(page_title="Ago Italy AI Studio", page_icon="🚀", layout="wide")

# --- نظام الحماية بكلمة مرور خاصة ---
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


def prepare_image(uploaded_file, max_dim=1200):
  img = Image.open(uploaded_file)
  img = ImageOps.exif_transpose(img)
  img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
  return img


def get_direct_download_link(file_bytes, filename, mime_type, button_text):
  b64 = base64.b64encode(file_bytes).decode()
  return (
      f'<a href="data:{mime_type};base64,{b64}" download="{filename}"'
      ' style="display:inline-block; padding:10px 20px; background-color:#28a745;'
      " color:white; text-decoration:none; border-radius:6px; font-weight:bold;"
      f' margin-top:5px;">{button_text}</a>'
  )


tab1, tab2, tab3, tab4 = st.tabs([
    "📸 1. تجهيز صور المتجر",
    "✨ 2. توليد صور وخلفيات",
    "🎙️ 3. تعليق صوتي سريع",
    "🎬 4. صانع الفيديو الإعلاني",
])

# =========================================================
# القسم 1: تجهيز صور المتجر (مقاس مربع مثالي لـ Shopify)
# =========================================================
with tab1:
  st.header("تحسين جودة ومقاسات صور المنتجات لمتجر Shopify")
  uploaded_files = st.file_uploader(
      "اختر صور المنتجات:",
      type=["png", "jpg", "jpeg", "webp"],
      accept_multiple_files=True,
      key="tab1_uploader",
  )
  if uploaded_files and st.button("✨ تجهيز الصور الآن"):
    results = []
    for idx, file in enumerate(uploaded_files):
      img = prepare_image(file, max_dim=1200).convert("RGB")
      square_bg = Image.new("RGB", (1200, 1200), (255, 255, 255))
      paste_x = (1200 - img.width) // 2
      paste_y = (1200 - img.height) // 2
      square_bg.paste(img, (paste_x, paste_y))
      buf = io.BytesIO()
      square_bg.save(buf, format="JPEG", quality=95)
      base_name = os.path.splitext(file.name)[0]
      results.append(
          {"name": f"shopify_{base_name}.jpg", "bytes": buf.getvalue()}
      )
    st.session_state.clean_images = results

  if "clean_images" in st.session_state and st.session_state.clean_images:
    cols = st.columns(2)
    for idx, item in enumerate(st.session_state.clean_images):
      with cols[idx % 2]:
        st.image(item["bytes"], caption=item["name"], use_container_width=True)
        st.markdown(
            get_direct_download_link(
                item["bytes"],
                item["name"],
                "image/jpeg",
                "⬇️ تحميل الصورة لـ Shopify",
            ),
            unsafe_allow_html=True,
        )

# =========================================================
# القسم 2: توليد صور وخلفيات فاخرة (مع إمكانية رفع صورة منتج)
# =========================================================
with tab2:
  st.header("توليد صور إعلانية ودمج منتجك في ديكور فاخر")
  ref_product = st.file_uploader(
      "ارفع صورة منتجك لدمجها في المشهد (اختياري):",
      type=["png", "jpg", "jpeg", "webp"],
      key="tab2_uploader",
  )

  scene_presets = {
      "طاولة رخامية فاخرة مع إضاءة شمس": (
          "luxury white marble table, soft warm sunlight shadows, minimalist"
          " aesthetic product photography background"
      ),
      "طاولة خشبية في غرفة معيشة إيطالية": (
          "warm oak wooden table in a modern cozy Italian living room, soft"
          " blurred background, natural daylight"
      ),
      "مقهى إيطالي أنيق في ميلانو": (
          "chic outdoor cafe table in Milan Italy, blurred background, golden"
          " hour sunlight, luxury editorial photography"
      ),
      "منصة عرض استوديو احترافية": (
          "minimalist beige stone podium studio background, soft dramatic"
          " lighting, commercial photography"
      ),
      "وصف مخصص (اكتب بالأسفل)": "custom",
  }

  selected_scene = st.selectbox(
      "اختر نوع الخلفية أو الصورة:", list(scene_presets.keys())
  )
  if scene_presets[selected_scene] == "custom":
    scene_prompt = st.text_input(
        "اكتب وصف الصورة المطلوبة بالإنجليزية:",
        "luxury leather handbag on a marble table in Milan, high quality",
    )
  else:
    scene_prompt = scene_presets[selected_scene]

  if st.button("🎨 توليد الصورة الآن"):
    with st.spinner("جاري رسم الصورة بالذكاء الاصطناعي..."):
      encoded_prompt = urllib.parse.quote(scene_prompt)
      bg_url = f"https://pollinations.ai{encoded_prompt}?width=1024&height=1024&nologo=true"
      response = requests.get(bg_url, timeout=30)

      if response.status_code == 200:
        bg_img = (
            Image.open(io.BytesIO(response.content))
            .convert("RGBA")
            .resize((1024, 1024))
        )

        # إذا قام المستخدم برفع صورة منتج، ندمجها في منتصف المشهد بإطار أنيق
        if ref_product:
          prod_img = prepare_image(ref_product, max_dim=550).convert("RGBA")
          pos_x = (1024 - prod_img.width) // 2
          pos_y = (1024 - prod_img.height) // 2
          bg_img.paste(prod_img, (pos_x, pos_y), prod_img)

        final_out = bg_img.convert("RGB")
        buf = io.BytesIO()
        final_out.save(buf, format="JPEG", quality=95)
        st.session_state.luxury_scene = buf.getvalue()
      else:
        st.error("يرجى المحاولة مرة أخرى.")

  if "luxury_scene" in st.session_state:
    st.image(
        st.session_state.luxury_scene,
        caption="الصورة المولدة",
        use_container_width=True,
    )
    st.markdown(
        get_direct_download_link(
            st.session_state.luxury_scene,
            "ago_italy_ai_photo.jpg",
            "image/jpeg",
            "⬇️ تحميل الصورة مباشرة",
        ),
        unsafe_allow_html=True,
    )

# =========================================================
# القسم 3: التعليق الصوتي السريع (إيطالي، عربي، إنجليزي)
# =========================================================
with tab3:
  st.header("توليد التعليق الصوتي الفوري للإعلانات")
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
  selected_voice_label = st.selectbox(
      "اختر اللغة والصوت:", list(voices.keys())
  )
  selected_voice = voices[selected_voice_label]
  script_text = st.text_area(
      "اكتب نص الإعلان:",
      value=(
          "Scopri la nuova collezione Ago Italy! Spedizione veloce e pagamento"
          " alla consegna."
      ),
      height=120,
      key="tts_script",
  )

  async def create_tts(text, voice, out_path):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(out_path)

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
    st.markdown(
        get_direct_download_link(
            st.session_state.generated_audio,
            "ago_italy_audio.mp3",
            "audio/mpeg",
            "⬇️ تحميل الملف الصوتي (MP3)",
        ),
        unsafe_allow_html=True,
    )

# =========================================================
# القسم 4: صانع الفيديو الإعلاني
# =========================================================
with tab4:
  st.header("صناعة فيديو إعلاني جاهز لفيسبوك وتيك توك")
  video_images = st.file_uploader(
      "اختر صور المنتج بالترتيب:",
      type=["png", "jpg", "jpeg"],
      accept_multiple_files=True,
      key="tab4_uploader",
  )
  video_audio = st.file_uploader(
      "ارفع ملف الصوت (اختياري):", type=["mp3", "wav"], key="tab4_audio"
  )
  aspect_ratio = st.radio(
      "اختر مقاس الفيديو:", ["📱 عمودي 9:16 (TikTok / Reels)", "💻 عرضي 16:9"]
  )
  target_w, target_h = (720, 1280) if "9:16" in aspect_ratio else (1280, 720)

  if video_images and st.button("🎬 صناعة الفيديو الإعلاني الآن"):
    with st.spinner("جاري مونتاج الفيديو..."):
      clips = []
      audio_clip = None
      total_duration = len(video_images) * 3.0

      if video_audio:
        ext = os.path.splitext(video_audio.name)[1]
        temp_aud_name = f"temp_audio{ext}"
        with open(temp_aud_name, "wb") as f:
          f.write(video_audio.read())
        audio_clip = AudioFileClip(temp_aud_name)
        total_duration = audio_clip.duration

      duration_per_img = total_duration / len(video_images)

      for idx, img_file in enumerate(video_images):
        pil_img = prepare_image(img_file).convert("RGB")
        bg = pil_img.resize((target_w, target_h)).filter(
