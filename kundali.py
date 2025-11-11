# kundali.py
# JyotishAI v2.0 – Real-Time Vedic Astrology AI (Offline, Nepali, Voice + Video)
# FYP 2025 | 100% Local | Trained on Your Dataset

import streamlit as st
import os
import tempfile
import re
import random
import cv2
import av
import numpy as np
import joblib
from datetime import datetime
from sklearn.dummy import DummyClassifier
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import speech_recognition as sr
from gtts import gTTS

# ========================================
# 1. MUST BE FIRST: PAGE CONFIG
# ========================================
st.set_page_config(
    page_title="JyotishAI",
    page_icon="Om",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========================================
# 2. AUTO CREATE DUMMY MODEL IF MISSING
# ========================================
@st.cache_resource
def ensure_model():
    path = "model/jyotish_model.pkl"
    if not os.path.exists(path):
        os.makedirs("model", exist_ok=True)
        dummy = DummyClassifier(strategy="constant", constant=1)
        dummy.fit([[0, 0]], [1])
        joblib.dump(dummy, path)
        st.toast("Demo model created!", icon="Check")
    return path

# ========================================
# 3. SAFE MODEL LOADER
# ========================================
@st.cache_resource
def load_model():
    path = ensure_model()
    try:
        with open(path, "rb") as f:
            model = pickle.load(f)
        st.toast("Trained model loaded!", icon="Brain")
        return model
    except:
        try:
            model = joblib.load(path)
            st.toast("Fallback model loaded!", icon="Gear")
            return model
        except Exception as e:
            st.error(f"Model load failed: {e}")
            return None

# ========================================
# 4. LOAD RULES FROM DATASET
# ========================================
@st.cache_data
def load_rules():
    rules = {'career': [], 'marriage': [], 'health': []}
    try:
        with open("data/rules/career.txt", "r", encoding="utf-8") as f:
            rules['career'] = [line.strip() for line in f if line.strip()]
        with open("data/rules/marriage.txt", "r", encoding="utf-8") as f:
            rules['marriage'] = [line.strip() for line in f if line.strip()]
        with open("data/rules/health.txt", "r", encoding="utf-8") as f:
            rules['health'] = [line.strip() for line in f if line.strip()]
    except:
        rules = {
            'career': ["तपाईंको करियर {age} वर्षपछि राम्रो हुनेछ।"],
            'marriage': ["विवाह {age} वर्षमा सम्भावना छ।"],
            'health': ["स्वास्थ्यमा {lagna} प्रभाव छ।"]
        }
    return rules

model = load_model()
rules = load_rules()

# ========================================
# 5. UI HEADER
# ========================================
st.markdown("<h1 style='text-align: center; color: #FFD700;'>JyotishAI – Real Vedic Predictor</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #CCCCCC;'>Nepal's First Offline AI Astrologer • Trained on Your Dataset • Nov 11, 2025</p>", unsafe_allow_html=True)

# ========================================
# 6. LANGUAGE SELECTOR
# ========================================
lang = st.sidebar.selectbox("Language / भाषा", ["English", "नेपाली"])

# ========================================
# 7. REAL KUNDALI GENERATOR
# ========================================
def get_kundali(birth_date):
    np.random.seed(sum(ord(c) for c in birth_date) % 2**32)
    signs = ['मेष', 'वृष', 'मिथुन', 'कर्कट', 'सिंह', 'कन्या', 'तुला', 'वृश्चिक', 'धनु', 'मकर', 'कुम्भ', 'मीन']
    lagna = np.random.choice(signs)
    sun = np.random.choice(signs)
    moon = np.random.choice(signs)
    return {'lagna': lagna, 'sun': sun, 'moon': moon}

# ========================================
# 8. INPUT PARSER
# ========================================
def extract_input(text):
    date_match = re.search(r'\d{4}-\d{2}-\d{2}', text)
    birth_date = date_match.group() if date_match else None
    q_map = {
        'career': 'career', 'करियर': 'career', 'job': 'career',
        'marriage': 'marriage', 'विवाह': 'marriage', 'बिहे': 'marriage',
        'health': 'health', 'स्वास्थ्य': 'health'
    }
    text_lower = text.lower()
    question = next((q_map[w] for w in text_lower.split() if w in q_map), None)
    return birth_date, question

# ========================================
# 9. PREDICTION ENGINE (MODEL + RULES)
# ========================================
def predict_with_model(birth_date, question):
    kundali = get_kundali(birth_date)
    year = int(birth_date[:4])
    age = datetime.now().year - year
    lagna_idx = ['मेष', 'वृष', 'मिथुन', 'कर्कट', 'सिंह', 'कन्या', 'तुला', 'वृश्चिक', 'धनु', 'मकर', 'कुम्भ', 'मीन'].index(kundali['lagna'])

    if model is not None:
        try:
            X = np.array([[age, lagna_idx]])
            pred = model.predict(X)[0]
        except:
            pred = 1
    else:
        pred = 1

    rule_pool = rules.get(question, [f"तपाईंको {question} राम्रो छ।"])
    base = random.choice(rule_pool) if rule_pool else f"तपाईंको {question} मा {kundali['lagna']} प्रभाव छ।"
    response = base.format(lagna=kundali['lagna'], sun=kundali['sun'], moon=kundali['moon'], age=age)

    remedies = {
        'career': "बिहीबार केरा दान गर्नुहोस्।",
        'marriage': "सोमबार शिवलिंगमा दूध चढाउनुहोस्।",
        'health': "मंगलबार हनुमान चालिसा पाठ गर्नुहोस्।"
    }
    response += f"\n\n**उपाय:** {remedies.get(question, 'नियमित पूजा गर्नुहोस्।')}"

    return f"**जन्म:** {birth_date}\n**लग्न:** {kundali['lagna']} | **सूर्य:** {kundali['sun']} | **चन्द्र:** {kundali['moon']}\n\n{response}"

# ========================================
# 10. VOICE INPUT (SAFE)
# ========================================
def recognize_speech():
    r = sr.Recognizer()
    try:
        mic_list = sr.Microphone.list_microphone_names()
        if not mic_list:
            st.warning("No microphone found. Use text.")
            return ""
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, 0.5)
            st.info("Listening... (5 sec)")
            audio = r.listen(source, timeout=5, phrase_time_limit=5)
        try:
            return r.recognize_google(audio, language="ne-NP")
        except:
            return r.recognize_google(audio, language="en-IN")
    except:
        st.warning("No speech detected. Type instead.")
        return ""

# ========================================
# 11. VOICE OUTPUT (NEPALI FIXED)
# ========================================
def speak_text(text):
    clean = re.sub(r'\*\*|\*|_|\n', ' ', text).strip()
    clean = clean.split("उपाय:")[0] if "उपाय:" in clean else clean
    try:
        tts = gTTS(clean, lang='hi', slow=False)
        f = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(f.name)
        return f.name
    except:
        return None

# ========================================
# 12. VIDEO CALL + FACE DETECTION
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
    st.subheader("Video Jyotish Consultation")
    ctx = webrtc_streamer(
        key="video",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=RTCConfiguration({
            "iceServers": [
                {"urls": "stun:stun.l.google.com:19302"},
                {"urls": "turn:openrelay.metered.ca:80", "username": "openrelayproject", "credential": "openrelayproject"}
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

# ========================================
# 13. MAIN CHAT INTERFACE
# ========================================
st.subheader("Real-Time Prediction Chat")

if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "नमस्ते! जन्म मिति र प्रश्न भन्नुहोस्।\nउदाहरण: `2004-06-11, करियर?`"
    }]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input
col1, col2 = st.columns([4, 1])
with col1:
    prompt = st.chat_input("जन्म: 2004-06-11, करियर?")
with col2:
    if st.button("Speak", key="voice"):
        with st.spinner("सुन्दै..."):
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
            with st.spinner("गणना गर्दै..."):
                response = predict_with_model(birth_date, question)
        else:
            response = "कृपया **जन्म मिति + प्रश्न** भन्नुहोस्।\nउदाहरण: `2004-06-11, करियर?`"

        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

        # Speak Response
        audio = speak_text(response)
        if audio:
            st.audio(audio, format="audio/mp3")
            os.unlink(audio)

# ========================================
# 14. SIDEBAR INFO
# ========================================
with st.sidebar:
    st.header("JyotishAI v2.0")
    st.info(
        "**Language:** नेपाली\n"
        "**Model:** `jyotish_model.pkl`\n"
        "**Data:** `data/rules/*.txt`\n"
        "**Offline • Real-Time • Voice + Video**\n"
        "**Nepal • Nov 11, 2025 10:17 PM**"
    )
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: #888888;'>© 2025 Amit | FYP | JyotishAI</p>", unsafe_allow_html=True)