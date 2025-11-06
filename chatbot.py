import streamlit as st
import ollama
import re
import random
import speech_recognition as sr
from gtts import gTTS
import os
import tempfile

# === CONFIG ===
st.set_page_config(page_title="JyotishAI", layout="wide")
st.markdown("<h1 style='text-align: center; color: #FFD700;'>JyotishAI – Auto Vedic Predictor</h1>", unsafe_allow_html=True)
st.markdown("**Say or type: `2004-06-11, career?`**")

# Language
lang = st.sidebar.selectbox("Language / भाषा", ["English", "नेपाली"])

# === MOCK KUNDALI ===
def get_kundali(birth_date):
    signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
    nepali = ['मेष', 'वृष', 'मिथुन', 'कर्कट', 'सिंह', 'कन्या', 'तुला', 'वृश्चिक', 'धनु', 'मकर', 'कुम्भ', 'मीन']
    random.seed(sum(ord(c) for c in birth_date))
    idx = random.randint(0, 11)
    return {
        'lagna': signs[idx], 'sun': signs[(idx+1)%12], 'moon': signs[(idx+2)%12],
        'nepali': {'lagna': nepali[idx], 'sun': nepali[(idx+1)%12], 'moon': nepali[(idx+2)%12]}
    }

# === OLLAMA PREDICTION ===
def predict_with_ollama(kundali, question):
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

# === VOICE INPUT ===
def recognize_speech():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening... Speak now!")
        audio = r.listen(source, timeout=6)
    try:
        text = r.recognize_google(audio, language="ne-NP")
        st.success(f"Recognized: {text}")
        return text
    except:
        try:
            text = r.recognize_google(audio, language="en-IN")
            st.success(f"Recognized: {text}")
            return text
        except:
            st.error("Could not understand.")
            return ""

# === VOICE OUTPUT (Always speak) ===
def speak_text(text, lang_code="ne"):
    try:
        tts = gTTS(text=text, lang=lang_code, slow=False)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts.save(fp.name)
            return fp.name
    except:
        return None

# === CHAT INIT WITH FULL HISTORY ===
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": 
         "Namaste! Say your **birth date + question** (e.g., `2004-06-11, career?`)." 
         if lang == "English" else 
         "नमस्ते! **जन्म मिति + प्रश्न** भन्नुहोस् (उदाहरण: `२००४-०६-११, करियर?`)।"}
    ]

# === DISPLAY FULL CHAT HISTORY ===
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# === INPUT ROW ===
col1, col2 = st.columns([4, 1])
with col1:
    prompt = st.chat_input("Type or press microphone to speak...")
with col2:
    if st.button("microphone", key="voice"):
        prompt = recognize_speech()

# === PROCESS INPUT ===
if prompt:
    prompt = prompt.strip()
    if not prompt:
        st.stop()

    # Avoid duplicate response
    last_msg = st.session_state.messages[-1]["content"] if st.session_state.messages else ""
    if prompt.lower() in ["namaste", "नमस्ते", "hi", "hello"] and "नमस्ते" in last_msg:
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    birth_date, question = extract_input(prompt)

    with st.chat_message("assistant"):
        if birth_date and question:
            with st.spinner("Predicting..." if lang == "English" else "गणना गर्दै..."):
                kundali = get_kundali(birth_date)
                pred = predict_with_ollama(kundali, question)
                l = kundali['nepali'] if lang == "नेपाली" else kundali
                response = f"**Date:** {birth_date}\n**Lagna:** {l['lagna']} | **Sun:** {l['sun']} | **Moon:** {l['moon']}\n\n{pred}"
        else:
            # === NATURAL & VARIED REPLIES ===
            greetings = [
                ("नमस्ते", "नमस्ते! तपाईंको जन्म मिति र प्रश्न भन्नुहोस्।"),
                ("namaste", "Namaste! Share your birth date and question."),
                ("hi", "Namaste! Ready for prediction?"),
                ("hello", "Hi! Say birth date + question."),
                ("how are you", "I'm great! Your turn.")
            ]
            text_lower = prompt.lower().strip()
            response = next((nep for eng, nep in greetings if eng in text_lower), None)
            if not response:
                response = (
                    "Please say **birth date + question** (e.g., `2004-06-11, career?`)." 
                    if lang == "English" else 
                    "**जन्म मिति + प्रश्न** भन्नुहोस् (उदाहरण: `२००४-०६-११, करियर?`)।"
                )
        
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

        # === ALWAYS SPEAK RESPONSE ===
        voice_text = re.sub(r'\*\*.*?\*\*', '', response).strip()
        voice_text = voice_text.split("उपाय:")[0] if "उपाय:" in voice_text else voice_text
        audio_file = speak_text(voice_text, lang_code="ne" if lang == "नेपाली" else "en")
        if audio_file:
            st.audio(audio_file, format="audio/mp3")
            os.unlink(audio_file)

# === SIDEBAR ===
with st.sidebar:
    st.header("JyotishAI")
    st.info(f"**Language:** {lang}\n\nmicrophone Voice In & Out\n\nFull Chat History\n\nNo Repetition\n\nOllama Llama3.2:1b")
    if st.button("Clear Chat"):
        st.session_state.messages = [
            {"role": "assistant", "content": "New chat started! नयाँ च्याट सुरु भयो।"}
        ]
        st.rerun()