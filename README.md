# JyotishAI – Real-Time Vedic Astrology Chatbot (JyotishAI in 2025)

![JyotishAI](assets/logo.png)

**Nepal’s first offline, voice + video-enabled Vedic astrology AI**  
**100% Local • No Internet • Nepali/English**

---

## Features

| Feature | Description |
|-------|-----------|
| **Real-Time Chat** | Type or speak → Instant reply |
| **Voice Input** | Speak in **Nepali/English** |
| **Voice Output** | AI **speaks in Nepali** |
| **Video Call** | Face-to-face consultation + face detection |
| **Auto Kundali** | From birth date (`2004-06-11`) |
| **Smart Prediction** | Lagna, Sun, Moon + Vedic remedy |
| **General Chat** | Ask anything (not just astrology) |
| **Full History** | All chats saved |

---

## Demo

> **You:** `2004-06-11, career?`  
> **JyotishAI:**  
> **Lagna:** सिंह | **Sun:** मिथुन | **Moon:** मेष  
> तपाईंको करियर २०२७ पछि उचाइमा पुग्नेछ...  
> **उपाय:** बिहीबार केरा दान गर्नुहोस्।

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