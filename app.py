import os
import requests
import streamlit as st
import xai_sdk
from gradio_client import client, handle_file

st.set_page_config(page_title="استوديو توليد الفيديو", page_icon="🎬", layout="centered")

# --- نظام الحماية بكلمة مرور خاصة ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 استوديو خاص")
    st.write("الرجاء إدخال كلمة المرور السرية للدخول:")
    password_input = st.text_input("كلمة المرور:", type="password")
    
    if st.button("دخول", type="primary"):
        if "APP_PASSWORD" in st.secrets and password_input == st.secrets["APP_PASSWORD"]:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ كلمة المرور غير صحيحة!")
    st.stop()
# ------------------------------------

st.title("🎬 استوديو توليد الفيديو الخاص بي")
st.write("مدعوم بمحرك Grok Imagine من شركة xAI")

if "XAI_API_KEY" in st.secrets:
    os.environ["XAI_API_KEY"] = st.secrets["XAI_API_KEY"]
else:
    st.error("⚠️ يرجى إضافة مفتاح XAI_API_KEY في إعدادات Secrets الخاصة بالموقع أولاً.")
    st.stop()

prompt = st.text_area(
    "اكتب وصف الفيديو الذي تتخيله (يفضل باللغة الإنجليزية لنتائج أدق):",
    placeholder="مثال: A cinematic drone shot flying over snowy mountains at sunset, 4k resolution",
    height=120
)

col1, col2 = st.columns(2)
with col1:
    duration = st.selectbox("مدة الفيديو (بالثواني):", [5, 10], index=0)
with col2:
    aspect_ratio = st.selectbox("أبعاد الفيديو:", ["16:9 (يوتيوب / عرضي)", "9:16 (تيك توك / طولي)", "1:1 (مربع)"])

ratio_code = aspect_ratio.split(" ")[0]

if st.button("✨ اصنع الفيديو الآن", type="primary", use_container_width=True):
    if not prompt.strip():
        st.warning("الرجاء كتابة وصف للفيديو أولاً!")
    else:
        with st.spinner("⏳ جاري صناعة الفيديو بواسطة الذكاء الاصطناعي... قد يستغرق الأمر من 30 إلى 60 ثانية"):
            try:
                client = xai_sdk.Client()
                response = client.video.generate(
                    prompt=prompt,
                    model="grok-imagine-video",
                    duration=duration,
                    aspect_ratio=ratio_code,
                    resolution="720p"
                )
                
                video_url = response.url
                st.success("🎉 تم صنع الفيديو بنجاح!")
                
                st.video(video_url)
                
                video_bytes = requests.get(video_url).content
                st.download_button(
                    label="⬇️ حفظ الفيديو في التابلت",
                    data=video_bytes,
                    file_name="my_ai_video.mp4",
                    mime="video/mp4",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"حدث خطأ أثناء التوليد: {e}")
import streamlit as st
import requests

st.divider()
st.header("🗣️ التحدث بصوتي المستنسخ")

# ضع هنا مفتاح API الخاص بك ومعرف صوتك المستنسخ من ElevenLabs
ELEVENLABS_API_KEY = "ضع_مفتاح_API_هنا"
VOICE_ID = "ضع_معرف_صوتك_هنا"

cloned_text = st.text_area("اكتب النص ليتم قراءته بصوتك الشخصي:", height=100)

if st.button("توليد بصوتي المستنسخ 🎙️"):
    if cloned_text.strip():
        with st.spinner("جاري التوليد بصوتك..."):
            url = f"https://elevenlabs.io{VOICE_ID}"
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": ELEVENLABS_API_KEY
            }
            data = {
                "text": cloned_text,
                "model_id": "eleven_multilingual_v2", # يدعم الإنجليزية والإيطالية والعربية بصوتك
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.8
                }
            }
            
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                with open("my_cloned_voice.mp3", "wb") as f:
                    f.write(response.content)
                st.success("تم التوليد بصوتك بنجاح!")
                st.audio("my_cloned_voice.mp3", format="audio/mp3")
                with open("my_cloned_voice.mp3", "rb") as file:
                    st.download_button("📥 تحميل الصوت المستنسخ", file, "my_voice.mp3", "audio/mp3")
            else:
                st.error("حدث خطأ في الاتصال، تأكد من مفتاح API والرصيد.")
    else:
        st.warning("يرجى كتابة النص أولاً.")

import streamlit as st
from gradio_client import Client, handle_file

st.divider()
st.header("🎙️ استنساخ صوتي مجاني (بدون حدود)")

# رفع عينة من صوتك (10 إلى 15 ثانية بصيغة wav أو mp3)
ref_audio = st.file_uploader("ارفع مقطعاً قصيراً بصوتك (10 ثوانٍ):", type=["mp3", "wav"])
ref_text = st.text_input("اكتب الكلام الموجود في المقطع الصوتي الذي رفعته (اختياري):")
target_text = st.text_area("اكتب النص الجديد الذي تريد أن ينطقه بصوتك:", height=100)

if st.button("استنساخ الصوت وتوليده مجاناً 🚀"):
    if ref_audio is not None and target_text.strip():
        with st.spinner("جاري استنساخ صوتك عبر السحابة المجانية..."):
            try:
                # حفظ الملف المرفوع مؤقتاً
                with open("temp_ref.wav", "wb") as f:
                    f.write(ref_audio.getbuffer())
                
                # الاتصال بنموذج F5-TTS المجاني على Hugging Face
                client = Client("mrfakename/E2-F5-TTS")
                result = client.predict(
                    ref_audio_input=handle_file("temp_ref.wav"),
                    ref_text_input=ref_text,
                    gen_text_input=target_text,
                    remove_silence=True,
                    api_name="/basic_tts"
                )
                
                # النتيجة تعود كمسار للملف الصوتي
                audio_output = result[0] if isinstance(result, (list, tuple)) else result
                
                st.success("تم استنساخ صوتك بنجاح ومجاناً!")
                st.audio(audio_output)
                
                with open(audio_output, "rb") as file:
                    st.download_button("📥 تحميل الصوت المستنسخ", file, "cloned_voice.wav", "audio/wav")
                    
            except Exception as e:
                st.error(f"السيرفر المجاني مزدحم حالياً، حاول مرة أخرى بعد قليل. التفاصيل: {e}")
    else:
        st.warning("يرجى رفع ملف صوتي وكتابة النص المطلوب.")
