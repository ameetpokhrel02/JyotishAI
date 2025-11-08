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

# === CONFIG ===
st.set_page_config(page_title="JyotishAI", layout="wide")
st.markdown("<h1 style='text-align: center; color: #FFD700;'>JyotishAI – Real-Time Vedic AI</h1>", unsafe_allow_html=True)
st.markdown("**Say or type: `2004-06-11, career?` or start video call!**")

# Language
lang = st.sidebar.selectbox("Language / भाषा", ["English", "नेपाली"])

# === MOCK KUNDALI  ===
def get_kundali(birth_date):
    signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
    nepali = ['मेष', 'वृष', 'मिथुन', 'कर्कट', 'सिंह', 'कन्या', 'तुला', 'वृश्चिक', 'धनु', 'मकर', 'कुम्भ', 'मीन']
    random.seed(sum(ord(c) for c in birth_date))
    idx = random.randint(0, 11)
    return {
        'lagna': signs[idx], 'sun': signs[(idx+1)%12], 'moon': signs[(idx+2)%12],
        'nepali': {'lagna': nepali[idx], 'sun': nepali[(idx+1)%12], 'moon': nepali[(idx+2)%12]}
    }

# === EXTRACT DATE & QUESTION ===
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

# === OLLAMA ASTROLOGY PREDICTION ===
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

# === GENERAL CHAT ===
def general_chat(prompt):
    prompt_text = f"Reply in **{lang} only**, short and natural: {prompt}"
    try:
        res = ollama.chat(model='llama3.2:1b', messages=[{'role': 'user', 'content': prompt_text}])
        return res['message']['content']
    except:
        return "I'm here!" if lang == "English" else "म यहाँ छु!"

# === VOICE INPUT ===
def recognize_speech():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening... Speak now!")
        audio = r.listen(source, timeout=6)
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
            st.error("Could not understand.")
            return ""

# === VOICE OUTPUT (Nepali via Hindi TTS) ===
def speak_text(text, lang_code="hi"):
    try:
        tts = gTTS(text=text, lang=lang_code, slow=False)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts.save(fp.name)
            return fp.name
    except:
        return None

# === VIDEO CALL FACE DETECTION ===
def video_frame_callback(frame):
    img = frame.to_ndarray(format="bgr24")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4)
    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
    return av.VideoFrame.from_ndarray(img, format="bgr24")

# === VIDEO CALL SECTION  jyotishai===
if st.button("Start Video Call", key="start_video"):
    st.session_state.in_video_call = True

if st.session_state.get("in_video_call", False):
    st.subheader("Video Consultation")
    ctx = webrtc_streamer(
        key="jyotishai-video",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=RTCConfiguration({
            "iceServers": [
                {"urls": "stun:stun.l.google.com:19302"},
                {"urls": "turn:openrelay.metered.ca:80", "username": "openrelayproject", "credential": "openrelayproject"},
                {"urls": "turn:openrelay.metered.ca:443", "username": "openrelayproject", "credential": "openrelayproject"}
            ]
        }),
        video_frame_callback=video_frame_callback,
        media_stream_constraints={"video": True, "audio": True},
        async_processing=True
    )
    if ctx.state.playing:
        st.success("Camera ON! Speak your question.")
        if st.button("End Call", key="end_call"):
            st.session_state.in_video_call = False
            st.rerun()
    else:
        st.warning("Connecting... Allow camera & mic.")

# === TEXT CHAT SECTION ===
st.subheader("Text & Voice Chat")
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": 
         "Namaste! Ask anything — text, voice, or video call!" 
         if lang == "English" else 
         "नमस्ते! टेक्स्ट, आवाज वा भिडियोमा सोध्नुहोस्!"}
    ]

# Display chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input
col1, col2 = st.columns([4, 1])
with col1:
    prompt = st.chat_input("Type your message...")
with col2:
    if st.button("Speak", key="voice"):
        prompt = recognize_speech()

# Process
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

        # Speak response
        voice_text = re.sub(r'\*\*.*?\*\*', '', response).strip()
        voice_text = voice_text.split("उपाय:")[0] if "उपाय:" in voice_text else voice_text
        audio_file = speak_text(voice_text, "hi")
        if audio_file:
            st.audio(audio_file, format="audio/mp3")
            os.unlink(audio_file)

# === SIDEBAR ===
with st.sidebar:
    st.header("JyotishAI")
    st.info(f"**Language:** {lang}\n\nVideo Call + Face Detect\nVoice In & Out\nReal-Time Chat\nLocal Ollama Llama3.2")
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()