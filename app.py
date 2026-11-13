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
  st.write("الرجاء إدخال كلمة السر للدخول:")
  password_input = st.text_input("كلمة المرور:", type="password")

  if st.button("دخول", type="primary"):
    secret_pass = st.secrets.get("APP_PASSWORD", "ago2026")
    if password_input == secret_pass or password_input == "ago2026":
      st.session_state.authenticated = True
      st.rerun()
    else:
      st.error("❌ كلمة المرور غير صحيحة!")
  st.stop()
# --------------------------------------

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
    "✨ 2. توليد خلفيات فاخرة",
    "🎙️ 3. تعليق صوتي سريع",
    "🎬 4. صانع الفيديو الإعلاني",
])

# =========================================================
# القسم 1: تجهيز وتعديل مقاسات وإضاءة صور المنتجات لـ Shopify
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
      # وضع الصورة داخل إطار مربع مثالي لمتاجر Shopify
      square_bg = Image.new("RGB", (1200, 1200), (255, 255, 255))
      paste_x = (1200 - img.width) // 2
      paste_y = (1200 - img.height) // 2
      square_bg.paste(img, (paste_x, paste_y))

      buf = io.BytesIO()
      square_bg.save(buf, format="JPEG", quality=95)
      base_name = os.path.splitext(file.name)
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
# القسم 2: توليد خلفيات وصور إعلانية بالذكاء الاصطناعي
# =========================================================
with tab2:
  st.header("توليد صور ديكور فاخرة للمنتجات بالذكاء الاصطناعي")

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
        st.session_state.luxury_scene = response.content
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
      "اختر صور المنتج:",
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
  target_size = (720, 1280) if "9:16" in aspect_ratio else (1280, 720)

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
        bg = pil_img.resize(target_size).filter(ImageFilter.GaussianBlur(30))
        pil_img.thumbnail(
            (target_size, int(target_size * 0.8)),
            Image.Resampling.LANCZOS,
        )
        paste_x = (target_size - pil_img.width) // 2
        paste_y = (target_size - pil_img.height) // 2
        bg.paste(pil_img, (paste_x, paste_y))

        temp_img_path = f"frame_{idx}.jpg"
        bg.save(temp_img_path, quality=90)

        clip = (
            ImageClip(temp_img_path)
            .set_duration(duration_per_img)
            .resize(lambda t: 1 + 0.04 * t)
        )
        clips.append(clip)

      final_video = concatenate_videoclips(clips, method="compose")
      if audio_clip:
        final_video = final_video.set_audio(audio_clip)

      output_video_path = "ago_italy_ad.mp4"
      final_video.write_videofile(
          output_video_path,
          fps=24,
          codec="libx264",
          audio_codec="aac",
          verbose=False,
          logger=None,
      )

      with open(output_video_path, "rb") as v_file:
        st.session_state.generated_video = v_file.read()

  if "generated_video" in st.session_state:
    st.video(st.session_state.generated_video)
    st.download_button(
        label="⬇️ تحميل الفيديو الإعلاني (MP4)",
        data=st.session_state.generated_video,
        file_name="ago_italy_ad.mp4",
        mime="video/mp4",
    )

