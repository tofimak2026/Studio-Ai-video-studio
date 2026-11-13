
import asyncio
import io
import os
import urllib.parse
import edge_tts
from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips
import numpy as np
from PIL import Image, ImageFilter
from rembg import remove
import requests
import streamlit as st

st.set_page_config(page_title="Ago Italy AI Studio", page_icon="🚀", layout="wide")

st.title("🚀 استوديو الذكاء الاصطناعي المتكامل - Ago Italy")
st.markdown(
    "تجهيز صور المنتجات، الديكورات الفاخرة، التعليق الصوتي، وصناعة"
    " الفيديوهات الإعلانية."
)

tab1, tab2, tab3, tab4 = st.tabs([
    "📸 1. مسح الخلفية",
    "✨ 2. ديكور فاخر للمنتج",
    "🎙️ 3. تعليق صوتي سريع",
    "🎬 4. صانع الفيديو الإعلاني",
])

with tab1:
  st.header("تجهيز صور المنتجات لمتجر Shopify (خلفية بيضاء)")
  uploaded_files = st.file_uploader(
      "ارفع صور أي منتج هنا (يمكنك رفع عدة صور دفعة واحدة):",
      type=["png", "jpg", "jpeg", "webp"],
      accept_multiple_files=True,
      key="tab1_uploader",
  )

  if uploaded_files and st.button("✨ مسح الخلفية الآن"):
    cols = st.columns(2)
    for idx, file in enumerate(uploaded_files):
      with st.spinner(f"جاري معالجة {file.name}..."):
        cutout_bytes = remove(file.read())
        img = Image.open(io.BytesIO(cutout_bytes)).convert("RGBA")
        white_bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
        final_img = Image.alpha_composite(white_bg, img).convert("RGB")

        buf = io.BytesIO()
        final_img.save(buf, format="JPEG", quality=95)

        with cols[idx % 2]:
          st.image(final_img, caption=file.name, use_container_width=True)
          st.download_button(
              label=f"⬇️ تحميل الصورة ({file.name})",
              data=buf.getvalue(),
              file_name=f"clean_{os.path.splitext(file.name)[0]}.jpg",
              mime="image/jpeg",
              key=f"dl_clean_{idx}",
          )

with tab2:
  st.header("دمج منتجك الحقيقي في خلفية فاخرة بالذكاء الاصطناعي")
  product_file = st.file_uploader(
      "ارفع صورة المنتج الواضحة:",
      type=["png", "jpg", "jpeg", "webp"],
      key="tab2_uploader",
  )

  scene_presets = {
      "طاولة رخامية فاخرة مع إضاءة شمس ناعمة": (
          "luxury white marble table, soft warm sunlight shadows, minimalist"
          " aesthetic background, high resolution product photography"
      ),
      "طاولة خشبية دافئة في غرفة معيشة عصرية": (
          "warm oak wooden table in a modern cozy Italian living room, soft"
          " blurred background, natural daylight"
      ),
      "مقهى إيطالي أنيق في ميلانو": (
          "chic outdoor cafe table in Milan Italy, blurred background, golden"
          " hour sunlight, editorial fashion photography"
      ),
      "منصة عرض استوديو احترافية (Podium)": (
          "minimalist beige stone podium studio background, soft dramatic"
          " lighting, commercial photography"
      ),
      "وصف مخصص (اكتب المكان الذي تريده بالأسفل)": "custom",
  }

  selected_scene = st.selectbox(
      "اختر المكان المناسب لمنتجك:", list(scene_presets.keys())
  )
  if scene_presets[selected_scene] == "custom":
    scene_prompt = st.text_input(
        "اكتب وصف الخلفية بالإنجليزية (مثال: luxury wooden table near a"
        " window):",
        "luxury marble table with soft lighting",
    )
  else:
    scene_prompt = scene_presets[selected_scene]

  if product_file and st.button("🎨 توليد المشهد ودمج المنتج"):
    with st.spinner("جاري قص المنتج وتوليد الخلفية الفاخرة..."):
      cutout_bytes = remove(product_file.read())
      prod_img = Image.open(io.BytesIO(cutout_bytes)).convert("RGBA")

      bbox = prod_img.getbbox()
      if bbox:
        prod_img = prod_img.crop(bbox)

      encoded_prompt = urllib.parse.quote(scene_prompt)
      bg_url = f"https://pollinations.ai{encoded_prompt}?width=1024&height=1024&nologo=true"
      response = requests.get(bg_url, timeout=30)

      if response.status_code == 200:
        bg_img = (
            Image.open(io.BytesIO(response.content))
            .convert("RGBA")
            .resize((1024, 1024))
        )

        max_size = 620
        prod_img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

        pos_x = (1024 - prod_img.width) // 2
        pos_y = (1024 - prod_img.height) // 2 + 40

        shadow = Image.new("RGBA", prod_img.size, (0, 0, 0, 90))
        shadow_mask = prod_img.split()[3]
        shadow.putalpha(shadow_mask)
        shadow = shadow.filter(ImageFilter.GaussianBlur(15))

        bg_img.paste(shadow, (pos_x + 10, pos_y + 20), shadow)
        bg_img.paste(prod_img, (pos_x, pos_y), prod_img)

        final_scene = bg_img.convert("RGB")
        st.image(
            final_scene,
            caption="النتيجة النهائية جاهزة للإعلان!",
            use_container_width=True,
        )

        buf = io.BytesIO()
        final_scene.save(buf, format="JPEG", quality=95)
        st.download_button(
            label="⬇️ تحميل الصورة الاحترافية",
            data=buf.getvalue(),
            file_name="ago_italy_luxury_scene.jpg",
            mime="image/jpeg",
        )
      else:
        st.error("حدث ضغط على خادم توليد الخلفيات، يرجى المحاولة مرة أخرى.")

with tab3:
  st.header("توليد التعليق الصوتي الفوري للإعلانات (بدون انتظار)")

  voices = {
      "🇮🇹 إيطالي - أنثى أنيقة (Elsa - للموضة والحقائب)": "it-IT-ElsaNeural",
      "🇮🇹 إيطالي - أنثى حيوية (Isabella - للمنتجات المنزلية)": (
          "it-IT-IsabellaNeural"
      ),
      "🇮🇹 إيطالي - رجل فخم (Diego)": "it-IT-DiegoNeural",
      "🇸🇦 عربي خليجي/سعودي - أنثى (Zariyah)": "ar-SA-ZariyahNeural",
      "🇸🇦 عربي خليجي/سعودي - رجل (Hamed)": "ar-SA-HamedNeural",
      "🇦🇪 عربي إماراتي - أنثى (Fatima)": "ar-AE-FatimaNeural",
      "🇪🇬 عربي عام - أنثى (Salma)": "ar-EG-SalmaNeural",
      "🇬🇧 إنجليزي بريطاني - أنثى (Sonia - لأوروبا)": "en-GB-SoniaNeural",
      "🇺🇸 إنجليزي أمريكي - أنثى (Jenny)": "en-US-JennyNeural",
      "🇺🇸 إنجليزي أمريكي - رجل (Christopher)": "en-US-ChristopherNeural",
  }

  selected_voice_label = st.selectbox(
      "اختر اللغة والصوت:", list(voices.keys())
  )
  selected_voice = voices[selected_voice_label]

  script_text = st.text_area(
      "اكتب نص الإعلان هنا بنفس لغة الصوت الذي اخترته:",
      value=(
          "Scopri la nuova collezione Ago Italy! Qualità garantita, spedizione"
          " veloce e pagamento alla consegna."
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
          audio_bytes = f.read()
        st.audio(audio_bytes, format="audio/mp3")
        st.download_button(
            label="⬇️ تحميل الملف الصوتي (MP3)",
            data=audio_bytes,
            file_name="ago_italy_audio.mp3",
            mime="audio/mpeg",
        )
    else:
      st.warning("يرجى كتابة النص أولاً.")

with tab4:
  st.header("صناعة فيديو إعلاني جاهز لفيسبوك وتيك توك")
  st.markdown("ارفع من صورتين إلى 5 صور لمنتجك، وسيقوم التطبيق بتحريكها وتركيب الصوت عليها تلقائياً.")

  video_images = st.file_uploader(
      "ارفع صور المنتج بالترتيب:",
      type=["png", "jpg", "jpeg"],
      accept_multiple_files=True,
      key="tab4_uploader",
  )
  video_audio = st.file_uploader(
      "ارفع ملف الصوت (MP3 أو WAV) الذي ولدته في القسم السابق (اختياري):",
      type=["mp3", "wav"],
      key="tab4_audio",
  )

  aspect_ratio = st.radio(
      "اختر مقاس الفيديو:",
      [
          "📱 عمودي 9:16 (TikTok / Reels / Facebook Ads)",
          "💻 عرضي 16:9 (YouTube / الموقع)",
      ],
  )
  target_size = (720, 1280) if "9:16" in aspect_ratio else (1280, 720)

  if video_images and st.button("🎬 صناعة الفيديو الإعلاني الآن"):
    with st.spinner("جاري مونتاج الفيديو وإضافة الحركة والصوت..."):
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
        pil_img = Image.open(img_file).convert("RGB")
        bg = pil_img.resize(target_size).filter(ImageFilter.GaussianBlur(30))
        pil_img.thumbnail(
            (target_size[0], int(target_size[1] * 0.8)),
            Image.Resampling.LANCZOS,
        )
        paste_x = (target_size[0] - pil_img.width) // 2
        paste_y = (target_size[1] - pil_img.height) // 2
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
        video_bytes = v_file.read()
        st.video(video_bytes)
        st.download_button(
            label="⬇️ تحميل الفيديو الإعلاني الجاهز (MP4)",
            data=video_bytes,
            file_name="ago_italy_ad.mp4",
          )
