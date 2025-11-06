# JyotishAI – Vedic Astrology Chatbot (FYP 2025)

![JyotishAI](assets/logo.png)

**Real-time, local, Nepali/English Vedic astrology advisor**  
Powered by **Ollama Llama3.2:1b** + **Streamlit**

---

## Features

- **Auto kundali** from birth date (`2004-06-11`)
- **Smart extraction** of Lagna, Sun, Moon
- **Natural chat** in **English / नेपाली**
- **Ollama-powered predictions** (100% offline)
- **Remedy included** in every response
- **No OpenAI, No Internet**

---

## How to Run

```bash
# 1. Clone
git clone https://github.com/amyths04/jyotishai.git
cd jyotishai

# 2. Setup
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Run Ollama (in another terminal)
ollama run llama3.2:1b

# 4. Launch
streamlit run chatbot.py