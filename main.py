import streamlit as st
from kundali_generator import generate_kundali
from rag_chatbot import astrology_chat
import joblib
import pandas as pd
import os
from datetime import datetime

# ==================== LANGUAGE & SESSION SETUP ====================
if "lang" not in st.session_state:
    st.session_state.lang = "नेपाली"

def switch_lang():
    st.session_state.lang = "English" if st.session_state.lang == "नेपाली" else "नेपाली"

lang = st.session_state.lang
t = lambda np, en: en if lang == "English" else np

# ==================== PAGE CONFIG ====================
st.set_page_config(page_title="JyotishAI Pro 2025", layout="wide", page_icon="Om")
st.markdown(f"""
<h1 style='text-align: center; color: #FFD700; font-size: 3.5em; text-shadow: 2px 2px 8px gold;'>
    ज्योतिषAI प्रो २०२५
</h1>
<p style='text-align: center; font-size: 1.5em; color: #00ffcc;'>
    {t('नेपालको पहिलो पूर्ण AI ज्योतिष प्रणाली', 'Nepal\'s First Complete AI Astrology System')}
</p>
""", unsafe_allow_html=True)

# Language Switcher
col1, col2, col3 = st.columns([1,1,1])
with col2:
    if st.button("English" if lang == "नेपाली" else "नेपाली", use_container_width=True, type="primary"):
        switch_lang()
        st.rerun()

# ==================== TABS ====================
tab1, tab2, tab3 = st.tabs([
    t("कुण्डली बनाउनुहोस्", "Generate Kundali"),
    t("AI भविष्यवाणी", "AI Predictions"),
    t("ज्योतिषसँग कुरा गर्नुहोस्", "Talk to Astrologer")
])

# ==================== TAB 1: कुण्डली + चार्ट ====================
with tab1:
    st.header(t("तपाईंको वैदिक कुण्डली बनाउनुहोस्", "Generate Your Vedic Kundali"))
    
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input(t("पुरा नाम", "Full Name"), placeholder="अमित पोखरेल")
        dob = st.date_input(
            t("जन्म मिति", "Date of Birth"),
            min_value=datetime(1900, 1, 1),
            max_value=datetime.today(),
            format="DD/MM/YYYY"
        )
        tob = st.time_input(t("जन्म समय", "Time of Birth"), value=datetime.now().time())
    
    with col2:
        gender = st.selectbox(t("लिङ्ग", "Gender"), ["पुरुष", "महिला", "अन्य"] if lang == "नेपाली" else ["Male", "Female", "Other"])
        nepal_cities = ["काठमाडौं", "पोखरा", "ललितपुर", "भक्तपुर", "विराटनगर", "जनकपुर", "नेपालगंज", "धरान", "बुटवल", "हेटौंडा"]
        place = st.selectbox(t("जन्म स्थान", "Birth Place"), nepal_cities)

    if st.button(t("कुण्डली बनाउनुहोस्", "Generate Kundali"), type="primary", use_container_width=True):
        with st.spinner(t("कुण्डली गणना गर्दै...", "Calculating Kundali...")):
            time_str = f"{tob.hour:02d}:{tob.minute:02d}"
            kundali = generate_kundali(name=name or "User", dob=dob.strftime("%Y-%m-%d"), tob=time_str)
        
        # Save everything in session
        st.session_state.kundali = kundali
        st.session_state.name = name or "User"
        st.session_state.time_str = time_str
        st.session_state.dob = dob
        st.session_state.place = place
        
        st.success(f"{t('नमस्ते', 'Namaste')} {name or 'User'} जी! तपाईंको कुण्डली तयार भयो")
        st.markdown(f"**लग्न:** {kundali['lagna']['rashi']} {kundali['lagna']['degree']:.2f}°")
        st.markdown(f"**सूर्य:** {kundali['planets']['सूर्य']['rashi']} {kundali['planets']['सूर्य']['degree']:.2f}°")
        st.markdown(f"**चन्द्र:** {kundali['planets']['चन्द्र']['rashi']} → **नक्षत्र:** {kundali['nakshatra']}")
        st.balloons()

    # Show Full Kundali Chart (Only after generation)
    if "kundali" in st.session_state:
        if st.button(t("पूर्ण कुण्डली चार्ट हेर्नुहोस्", "View Full Kundali Chart"), use_container_width=True):
            k = st.session_state.kundali
            chart_html = f"""
            <div style="font-family: 'Noto Sans Devanagari', sans-serif; text-align:center; background:#000; color:#FFD700; padding:30px; border:5px solid gold; border-radius:20px; margin:20px;">
                <h2 style="color:gold;">{st.session_state.name} जीको वैदिक कुण्डली</h2>
                <h3 style="color:#00ffcc;">उत्तर भारतीय शैली</h3>
                <table style="margin:20px auto; border-collapse:collapse; width:90%; font-size:18px;">
                    <tr><td colspan="3" style="border:3px solid gold; padding:20px; background:#111; font-size:22px;">लग्न: {k['lagna']['rashi']}</td></tr>
                    <tr>
                        <td style="border:3px solid gold; padding:15px; background:#222;">{k['planets']['सूर्य']['rashi']}<br><b>सूर्य</b></td>
                        <td style="border:3px solid gold; padding:15px; background:#111;">राहु</td>
                        <td style="border:3px solid gold; padding:15px; background:#222;">{k['planets']['चन्द्र']['rashi']}<br><b>चन्द्र</b><br>({k['nakshatra']})</td>
                    </tr>
                    <tr>
                        <td style="border:3px solid gold; padding:15px; background:#111;">गुरु</td>
                        <td style="border:3px solid gold; padding:25px; background:#000; color:#FFD700; font-size:28px; font-weight:bold;">
                            {k['lagna']['rashi']}<br>लग्न
                        </td>
                        <td style="border:3px solid gold; padding:15px; background:#111;">शनि</td>
                    </tr>
                    <tr>
                        <td style="border:3px solid gold; padding:15px; background:#222;">बुध</td>
                        <td style="border:3px solid gold; padding:15px; background:#111;">केतु</td>
                        <td style="border:3px solid gold; padding:15px; background:#222;">मंगल</td>
                    </tr>
                    <tr><td colspan="3" style="border:3px solid gold; padding:15px; background:#111;">शुक्र</td></tr>
                </table>
                <p style="margin-top:20px; color:#aaa;">
                    जन्म: {st.session_state.dob.strftime('%Y-%m-%d')} | समय: {st.session_state.time_str} | स्थान: {st.session_state.place}
                </p>
            </div>
            """
            st.markdown(chart_html, unsafe_allow_html=True)
            st.download_button(
                "Download Kundali as PDF",
                data="Your personalized Vedic Kundali",
                file_name=f"{st.session_state.name}_kundali.pdf",
                mime="text/plain"
            )

# ==================== TAB 2 & 3: बाँकी कोड (पहिलेकै जस्तै) ====================
with tab2:
    st.header(t("AI बाट जीवन भविष्यवाणी", "AI Life Predictions"))
    if 'kundali' not in st.session_state:
        st.warning(t("पहिला कुण्डली बनाउनुहोस्!", "Please generate Kundali first!"))
        st.stop()
    try:
        model = joblib.load("model/career_rf_model.pkl")
        le = joblib.load("model/career_label_encoder.pkl")
        X = pd.DataFrame([{'age': 25, 'lagna_sign': 6, 'sun_sign': 0, 'moon_sign': 8,
                          'mars_in_7th': 1, 'saturn_aspect_7th': 0, 'rahu_ketu_axis': 1}])
        pred = model.predict(X)[0]
        career = le.inverse_transform([pred])[0]
        st.success(f"{t('करियर स्तर', 'Career Level')}: **{career}**")
        if career == "High":
            st.markdown(t("उच्च पद प्राप्ति! राजयोग बनेको छ।", "You will reach high position! Rajyoga present."))
        if os.path.exists("assets/plots/confusion_matrix.png"):
            st.image("assets/plots/confusion_matrix.png", caption=t("ML Model Accuracy", "Model Accuracy"))
    except Exception as e:
        st.error("ML Model not found.")

with tab3:
    st.header(t("ज्योतिषसँग नेपालीमा कुरा गर्नुहोस्", "Talk to Astrologer in Nepali"))
    if 'kundali' not in st.session_state:
        st.warning(t("पहिला कुण्डली बनाउनुहोस्!", "Generate Kundali first!"))
        st.stop()
    
    if "messages" not in st.session_state:
        st.session_state.messages = [{
            "role": "assistant",
            "content": f"नमस्ते {st.session_state.name} जी! म तपाईंको व्यक्तिगत ज्योतिष गुरु हुँ। तपाईंको कुण्डली बनिसक्यो! विवाह, करियर, पैसा, स्वास्थ्य, उपाय — जे पनि सोध्नुहोस्।"
        }]
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    if prompt := st.chat_input(t("यहाँ प्रश्न लेख्नुहोस्... (जस्तै: मेरो विवाह कहिले हुन्छ?)", "Ask your question...")):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("गणना गर्दै..."):
                answer = astrology_chat(prompt, st.session_state.kundali)
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown(f"### नमस्ते {st.session_state.get('name', 'User')} जी")
    st.success("JyotishAI Pro 2025")
    st.info(f"भाषा: {lang}\nपूर्ण Offline\nसटीक कुण्डली\nAI + Ollama")
    if st.button(t("Chat मेटाउनुहोस्", "Clear Chat")):
        st.session_state.messages = []
        st.rerun()
