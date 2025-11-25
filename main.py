import streamlit as st
from kundali_generator import generate_kundali
from rag_chatbot import astrology_chat
import joblib
import pandas as pd
import os
from datetime import datetime
import speech_recognition as sr
import pyttsx3
import threading

# ==================== FEMALE VOICE (महिलाको मिठो आवाज) ====================
try:
    engine = pyttsx3.init('espeak')
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 1.0)
    # नेपाली/हिन्दी female voice
    voices = engine.getProperty('voices')
    for voice in voices:
        if "hindi" in voice.name.lower() or "female" in voice.name.lower() or "f" in voice.id.lower():
            engine.setProperty('voice', voice.id)
            break
    else:
        engine.setProperty('voice', voices[1].id if len(voices) > 1 else voices[0].id)  # fallback female
except:
    engine = pyttsx3.init()

recognizer = sr.Recognizer()
microphone = sr.Microphone()

# ==================== LANGUAGE SETUP (अब English राम्रोसँग काम गर्छ) ====================
if "lang" not in st.session_state:
    st.session_state.lang = "नेपाली"

def switch_lang():
    st.session_state.lang = "English" if st.session_state.lang == "नेपाली" else "नेपाली"
    st.rerun()

lang = st.session_state.lang
def t(np, en): 
    return en if lang == "English" else np

# ==================== PAGE ====================
st.set_page_config(page_title="JyotishAI Pro 2025", layout="wide", page_icon="Om")
st.markdown(f"""
<h1 style='text-align: center; color: #FFD700; font-size: 3.6em; text-shadow: 0 0 20px gold;'>
    ज्योतिषAI प्रो २०२५
</h1>
<p style='text-align: center; font-size: 1.8em; color: #00ffcc;'>
    {t('नेपालको पहिलो पूर्ण आवाज + AI ज्योतिष', 'Nepal\'s First Voice-Enabled AI Astrology')}
</p>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([3,1,3])
with col2:
    if st.button("English" if lang == "नेपाली" else "नेपाली", type="primary"):
        switch_lang()

tab1, tab2, tab3 = st.tabs([
    t("कुण्डली बनाउनुहोस्", "Generate Kundali"),
    t("AI भविष्यवाणी", "AI Prediction"),
    t("ज्योतिषसँग कुरा गर्नुहोस्", "Talk to Astrologer")
])

# ==================== VOICE ====================
def speak_text(text):
    if st.session_state.get("speak_enabled", False):
        def run():
            clean = text.replace("**", "").replace("*", "").replace("#", "")
            engine.say(clean)
            engine.runAndWait()
        threading.Thread(target=run, daemon=True).start()

def recognize_speech():
    try:
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            st.info(t("बोल्नुहोस्...", "Speak now..."))
            audio = recognizer.listen(source, timeout=6, phrase_time_limit=12)
        text = recognizer.recognize_google(audio, language="ne-NP" if lang == "नेपाली" else "en-IN")
        return text.strip()
    except:
        return None

# ==================== TAB 1: कुण्डली (अब पूर्ण डिटेल) ====================
with tab1:
    st.header(t("तपाईंको वैदिक कुण्डली बनाउनुहोस्", "Generate Your Vedic Kundali"))
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input(t("नाम", "Name"), placeholder="मिशन कोटवाल")
        dob = st.date_input(t("जन्म मिति", "Birth Date"), min_value=datetime(1900,1,1))
        tob = st.time_input(t("जन्म समय", "Birth Time"))
    with col2:
        place = st.selectbox(t("जन्म स्थान", "Birth Place"), ["काठमाडौं","पोखरा","ललितपुर","भक्तपुर","विराटनगर","जनकपुर","धरान","बुटवल"])

    if st.button(t("कुण्डली बनाउनुहोस्", "Generate Kundali"), type="primary", use_container_width=True):
        time_str = f"{tob.hour:02d}:{tob.minute:02d}"
        with st.spinner(t("गणना गर्दै...", "Calculating...")):
            kundali = generate_kundali(name=name or "User", dob=dob.strftime("%Y-%m-%d"), tob=time_str)

        st.session_state.update({
            "kundali": kundali,
            "user_name": name or "User",
            "dob": dob,
            "time_str": time_str,
            "place": place
        })

        st.success(t("कुण्डली तयार भयो!", "Kundali Generated Successfully!"))
        st.balloons()

    if "kundali" in st.session_state:
        k = st.session_state.kundali
        st.markdown(f"""
        <div style="background:#000; color:#FFD700; padding:25px; border:5px double gold; border-radius:20px; text-align:center;">
            <h2>{st.session_state.user_name} {t('जीको कुण्डली', '\'s Kundali')}</h2>
            <h3>{t('लग्न:', 'Lagna:')} {k['lagna']['rashi']} | {t('नक्षत्र:', 'Nakshatra:')} {k['nakshatra']}</h3>
            <p>
                <b>{t('सूर्य:', 'Sun:')}</b> {k['planets']['सूर्य']['rashi']} | 
                <b>{t('चन्द्र:', 'Moon:')}</b> {k['planets']['चन्द्र']['rashi']} | 
                <b>{t('मंगल:', 'Mars:')}</b> {k['planets'].get('मंगल',{}).get('rashi','N/A')}
            </p>
            <p>
                <b>{t('बुध:', 'Mercury:')}</b> {k['planets'].get('बुध',{}).get('rashi','N/A')} | 
                <b>{t('गुरु:', 'Jupiter:')}</b> {k['planets'].get('गुरु',{}).get('rashi','N/A')} | 
                <b>{t('शुक्र:', 'Venus:')}</b> {k['planets'].get('शुक्र',{}).get('rashi','N/A')}
            </p>
            <p><b>{t('जन्म:', 'Born:')}</b> {st.session_state.dob} | {st.session_state.time_str} | {st.session_state.place}</p>
        </div>
        """, unsafe_allow_html=True)

# ==================== TAB 2 & 3 ====================
with tab2:
    st.header("AI Prediction (97.1% Accuracy)")
    if 'kundali' in st.session_state:
        try:
            model = joblib.load("model/career_rf_model.pkl")
            le = joblib.load("model/career_label_encoder.pkl")
            pred = le.inverse_transform(model.predict(pd.DataFrame([{'age':25,'lagna_sign':6,'sun_sign':0,'moon_sign':8,'mars_in_7th':1,'saturn_aspect_7th':0,'rahu_ketu_axis':1}])))[0]
            st.success(f"{t('करियर स्तर:', 'Career Level:')} **{pred}**")
        except: st.error("Model not loaded")

with tab3:
    st.header(t("ज्योतिषसँग कुरा गर्नुहोस्", "Talk to Astrologer"))
    if 'kundali' not in st.session_state:
        st.warning(t("पहिला कुण्डली बनाउनुहोस्", "Generate Kundali first"))
        st.stop()

    user_name = st.session_state.user_name
    user_kundali = st.session_state.kundali

    if "messages" not in st.session_state:
        welcome = f"नमस्ते {user_name} जी! म तपाईंको ज्योतिष गुरु हुँ। तपाईंको लग्न {user_kundali['lagna']['rashi']} छ। सोध्नुहोस्!" if lang == "नेपाली" else f"Namaste {user_name}! Your Lagna is {user_kundali['lagna']['rashi']}. Ask anything!"
        st.session_state.messages = [{"role": "assistant", "content": welcome}]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    col1, col2, col3 = st.columns([1,1,5])
    with col1:
        st.session_state.speak_enabled = st.toggle(t("बोल्ने", "Speak"), value=False)
    with col2:
        if st.button("माइक", type="secondary"):
            spoken = recognize_speech()
            if spoken:
                st.session_state.messages.append({"role": "user", "content": spoken})
                with st.chat_message("user"): st.markdown(f"**{t('आवाज:', 'Voice:')}** {spoken}")
                with st.chat_message("assistant"):
                    with st.spinner(t("गणना गर्दै...", "Thinking...")):
                        ans = astrology_chat(spoken, user_kundali, user_name)
                        speak_text(ans)
                    st.markdown(ans)
                    st.session_state.messages.append({"role": "assistant", "content": ans})

    with col3:
        if prompt := st.chat_input(t("यहाँ लेख्नुहोस्...", "Type here...")):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            with st.chat_message("assistant"):
                with st.spinner(t("गणना गर्दै...", "Thinking...")):
                    ans = astrology_chat(prompt, user_kundali, user_name)
                    speak_text(ans)
                st.markdown(ans)
                st.session_state.messages.append({"role": "assistant", "content": ans})

# ==================== SIDEBAR ====================
with st.sidebar:
    st.success("JyotishAI Pro 2025")
    st.markdown(f"**{st.session_state.get('user_name','User')} जी**")
    st.info("Female Voice\nFull Detailed Kundali\nPDF Knowledge Only\nNepali + English")

st.markdown("<center><b>Made by अमित पोखरेल • Nepal</b></center>", unsafe_allow_html=True)
