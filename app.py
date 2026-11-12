import os
import requests
import streamlit as st
import xai_sdk

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
