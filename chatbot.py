import streamlit as st
import ollama
import re
import random
import av
import cv2
import numpy as np
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
from aiortc.contrib.media import MediaPlayer

# === CONFIG ===
st.set_page_config(page_title="JyotishAI", layout="wide")
st.markdown("<h1 style='text-align: center; color: #FFD700;'>JyotishAI – Video Astrology Chat</h1>", unsafe_allow_html=True)

# Language
lang = st.sidebar.selectbox("Language / भाषा", ["English", "नेपाली"])

# === VIDEO CALL ===
def video_callback(frame):
    img = frame.to_ndarray(format="bgr24")
    # Simple face detection
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml').detectMultiScale(gray, 1.1, 4)
    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
    return av.VideoFrame.from_ndarray(img, format="bgr24")

# === VIDEO CALL BUTTON ===
if st.button("Start Video Call", key="start_video"):
    st.session_state.in_video_call = True  # ← Fixed key

if 'in_video_call' in st.session_state and st.session_state.in_video_call:
    st.subheader("Video Consultation")
    ctx = webrtc_streamer(
        key="video-call",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=RTCConfiguration({
            "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
        }),
        video_frame_callback=video_callback,
        media_stream_constraints={"video": True, "audio": True}
    )
    
    if ctx.state.playing:
        st.info("Speak your question — I can see and hear you!")
        if st.button("End Call", key="end_call"):
            st.session_state.in_video_call = False
            st.rerun()

# === TEXT CHAT ===
st.subheader("💬 Text Chat")
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Namaste! Choose video or text chat." if lang == "English" else "नमस्ते! भिडियो वा टेक्स्ट च्याट छान्नुहोस्।"}
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Your message..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Simple prediction (add your logic)
        pred = f"In {lang}, your prediction is ready. Video call for personalized reading!"
        st.markdown(pred)
        st.session_state.messages.append({"role": "assistant", "content": pred})

# === SIDEBAR ===
with st.sidebar:
    st.header("JyotishAI")
    st.info("🎥 Video Call + AI Vision\n💬 Text Chat\n🗣️ Voice Input\nनेपाली + English")
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()