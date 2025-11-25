# ========================================
# JYOTISHAI v3.0 – FINAL FYP 2025
# Offline • Nepali + English • Voice + Video + Real-Time Chat
# ========================================
import streamlit as st
import ollama
import re
import random
import speech_recognition as sr
from gtts import gTTS
import os
import tempfile
import cv2
import av
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration

# ========================================
# 1. MUST BE FIRST: PAGE CONFIG
# ========================================
st.set_page_config(page_title="JyotishAI", layout="wide", page_icon="Om")

# ========================================
# 2. UI HEADER
# ========================================
st.markdown("<h1 style='text-align: center; color: #FFD700;'>JyotishAI – Real-Time Vedic AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #CCCCCC;'>Nepal's First Offline AI Astrologer | Nov 13, 2025</p>", unsafe_allow_html=True)

# Language Selector
lang = st.sidebar.selectbox("Language / भाषा", ["English", "नेपाली"])

# ========================================
# 3. MOCK KUNDALI (Deterministic)
# ========================================
def get_kundali(birth_date):
    signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
    nepali = ['मेष', 'वृष', 'मिथुन', 'कर्कट', 'सिंह', 'कन्या', 'तुला', 'वृश्चिक', 'धनु', 'मकर', 'कुम्भ', 'मीन']
    random.seed(sum(ord(c) for c in birth_date))
    idx = random.randint(0, 11)
    return {
        'lagna': signs[idx], 'sun': signs[(idx+1)%12], 'moon': signs[(idx+2)%12],
        'nepali': {'lagna': nepali[idx], 'sun': nepali[(idx+1)%12], 'moon': nepali[(idx+2)%12]}
    }

# ========================================
# 4. EXTRACT DATE & QUESTION
# ========================================
def extract_input(text):
    date_match = re.search(r'\d{4}-\d{2}-\d{2}', text)
    birth_date = date_match.group() if date_match else None
    q_map = {
        'career': 'Career?', 'करियर': 'Career?', 'job': 'Career?',
        'marriage': 'Marriage?', 'विवाह': 'Marriage?', 'बिहे': 'Marriage?',
        'health': 'Health?', 'स्वास्थ्य': 'Health?',
        'future': 'Future?', 'भविष्य': 'Future?'
    }
    text_lower = text.lower()
    question = next((q_map[w] for w in text_lower.split() if w in q_map), None)
    return birth_date, question

# ========================================
# 5. OLLAMA ASTROLOGY PREDICTION
# ========================================
def predict_astrology(kundali, question):
    prompt = f"""
    You are JyotishAI. Lagna={kundali['lagna']}, Sun={kundali['sun']}, Moon={kundali['moon']}.
    Question: {question}
    Answer in **{lang} only**. 3 sentences. End with a Vedic remedy.
    """
    try:
        res = ollama.chat(model='llama3.2:1b', messages=[{'role': 'user', 'content': prompt}])
        return res['message']['content']
    except:
        return "Try again." if lang == "English" else "पछि प्रयास गर्नुहोस्।"

# ========================================
# 6. GENERAL CHAT (Fallback)
# ========================================
def general_chat(prompt):
    prompt_text = f"Reply in **{lang} only**, short and natural: {prompt}"
    try:
        res = ollama.chat(model='llama3.2:1b', messages=[{'role': 'user', 'content': prompt_text}])
        return res['message']['content']
    except:
        return "I'm here!" if lang == "English" else "म यहाँ छु!"

# ========================================
# 7. VOICE INPUT ENG / NEPAL
# ========================================
def recognize_speech():
    r = sr.Recognizer()
    try:
        mic_list = sr.Microphone.list_microphone_names()
        if not mic_list:
            st.warning("No mic found. Use text.")
            return ""
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=0.5)
            st.info("Listening... (5 sec)")
            audio = r.listen(source, timeout=5, phrase_time_limit=5)
        try:
            text = r.recognize_google(audio, language="ne-NP")
            st.success(f"You: {text}")
            return text
        except:
            try:
                text = r.recognize_google(audio, language="en-IN")
                st.success(f"You: {text}")
                return text
            except:
                st.warning("Could not understand.")
                return ""
    except sr.WaitTimeoutError:
        st.warning("No speech. Type.")
        return ""
    except Exception as e:
        st.error(f"Mic error: {e}")
        return ""

# ========================================
# 8. VOICE OUTPUT and CLEANUP
# ========================================
def speak_text(text):
    clean = re.sub(r'\*\*|\*|_|\n', ' ', text).strip()
    clean = clean.split("उपाय:|Remedy:")[0] if "उपाय:" in clean or "Remedy:" in clean else clean
    try:
        lang_code = "en" if lang == "English" else "hi"
        tts = gTTS(clean, lang=lang_code, slow=False)
        f = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(f.name)
        return f.name
    except:
        return None

# ========================================
# 9. VIDEO CALL + FACE DETECTION
# ========================================
def video_frame_callback(frame):
    img = frame.to_ndarray(format="bgr24")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4)
    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
    return av.VideoFrame.from_ndarray(img, format="bgr24")

# Video Call Button
if st.button("Start Video Call", key="start_video"):
    st.session_state.in_video_call = True

if st.session_state.get("in_video_call", False):
    st.subheader("Video Consultation")
    ctx = webrtc_streamer(
        key="video_call",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=RTCConfiguration({"iceServers": [
            {"urls": "stun:stun.l.google.com:19302"}
        ]}),
        video_frame_callback=video_frame_callback,
        media_stream_constraints={"video": True, "audio": True},
        async_processing=True
    )
    if ctx.state.playing:
        st.success("Camera & Mic ON! Speak your question.")
        if st.button("End Call", key="end_call"):
            st.session_state.in_video_call = False
            st.rerun()
    else:
        st.warning("Connecting... Allow camera & mic.")

# ========================================
# 10. TEXT & VOICE CHAT
# ========================================
st.subheader("Text & Voice Chat")

if "messages" not in st.session_state:
    welcome = (
        "Namaste! Ask anything — text, voice, or video call!" 
        if lang == "English" else 
        "नमस्ते! टेक्स्ट, आवाज वा भिडियोमा सोध्नुहोस्!"
    )
    st.session_state.messages = [{"role": "assistant", "content": welcome}]

# Display chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input
col1, col2 = st.columns([4, 1])
with col1:
    prompt = st.chat_input("Type: `2004-06-11, career?` or say 'hi'")
with col2:
    if st.button("Speak", key="voice"):
        with st.spinner("Listening..."):
            prompt = recognize_speech()

# Process Input
if prompt:
    prompt = prompt.strip()
    if not prompt:
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    birth_date, question = extract_input(prompt)

    with st.chat_message("assistant"):
        if birth_date and question:
            with st.spinner("Predicting..." if lang == "English" else "गणना गर्दै..."):
                kundali = get_kundali(birth_date)
                pred = predict_astrology(kundali, question)
                l = kundali['nepali'] if lang == "नेपाली" else kundali
                response = f"**Date:** {birth_date}\n**Lagna:** {l['lagna']} | **Sun:** {l['sun']} | **Moon:** {l['moon']}\n\n{pred}"
        else:
            response = general_chat(prompt)

        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

        # Speak Response
        audio_file = speak_text(response)
        if audio_file:
            st.audio(audio_file, format="audio/mp3")
            os.unlink(audio_file)

# ========================================
# 11. SIDEBAR
# ========================================
with st.sidebar:
    st.header("JyotishAI v3.0")
    st.info(
        f"**Language:** {lang}\n"
        "**Model:** Llama3.2:1b (Offline)\n"
        "**Features:**\n"
        "• Voice In/Out\n"
        "• Video Call + Face Detect\n"
        "• Real-Time Chat\n"
        "• General + Astrology"
    )
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()