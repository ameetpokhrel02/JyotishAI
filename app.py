import streamlit as st
import pandas as pd
import joblib
import os

# === CONFIG ===
st.set_page_config(page_title="JyotishAI", layout="centered")
st.title("JyotishAI – Your Vedic Astrology Predictor")

# Load model
@st.cache_resource
def load_model():
    return joblib.load('model/jyotish_model.pkl')

model = load_model()

# Load sample data for dropdowns
df = pd.read_csv('data/clean/clean_kundali.csv')

# === SIDEBAR ===
st.sidebar.header("Enter Birth Details")
lagna = st.sidebar.selectbox("Lagna (Ascendant)", sorted(df['lagna'].unique()))
sun = st.sidebar.selectbox("Sun Sign", sorted(df['sun'].unique()))
moon = st.sidebar.selectbox("Moon Sign", sorted(df['moon'].unique()))
question = st.sidebar.selectbox("Your Question", [
    "Career?", "Marriage?", "Health?", "Studies?", "Wealth?",
    "Love Life?", "Job?", "Business?", "Future?", "Family?"
])

# === PREDICTION ===
if st.sidebar.button("Get Prediction"):
    user_input = f"{lagna} {sun} {moon} {question}"
    pred = model.predict([user_input])[0]
    
    st.success("Prediction Ready!")
    st.markdown(f"**Input:** {user_input}")
    st.markdown(f"### {pred}")
    
    # Show similar real cases
    matches = df[
        (df['lagna'] == lagna) |
        (df['sun'] == sun) |
        (df['moon'] == moon) |
        (df['question'] == question)
    ]
    if not matches.empty:
        st.info(f"Found {len(matches)} similar real kundalis")
        st.dataframe(matches[['birth_date','place','question','prediction']].head(3))

# === FOOTER ===
st.markdown("---")
st.markdown("**JyotishAI** – AI-Powered Vedic Insights | FYP 2025")
