# rag_chatbot.py - SUPER INTELLIGENT NEPALI ASTROLOGY BOT (FINAL VERSION)
import ollama
import chromadb
import os
from PyPDF2 import PdfReader

# Load Knowledge Base
def load_knowledge():
    if os.path.exists("knowledge/vedic_astrology_knowledge_full.pdf"):
        reader = PdfReader("knowledge/vedic_astrology_knowledge_full.pdf")
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    elif os.path.exists("knowledge/vedic_astrology_knowledge_full.txt"):
        return open("knowledge/vedic_astrology_knowledge_full.txt", "r", encoding="utf-8").read()
    else:
        return "वैदिक ज्योतिषको ज्ञान उपलब्ध छैन।"

knowledge_base = load_knowledge()

# ChromaDB Setup
client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_or_create_collection("jyotish_knowledge")

if collection.count() == 0:
    chunks = [knowledge_base[i:i+1000] for i in range(0, len(knowledge_base), 1000)]
    for i, chunk in enumerate(chunks):
        collection.add(ids=[f"chunk_{i}"], documents=[chunk])
    print("ज्ञानको भण्डार सफलतापूर्वक लोड भयो!")

def retrieve_context(query):
    try:
        results = collection.query(query_texts=[query], n_results=5)
        return "\n".join(results['documents'][0])
    except:
        return "ज्ञान उपलब्ध छैन।"

# SUPER INTELLIGENT ASTROLOGY CHAT (अब नाम + कुण्डली सही आउँछ)
def astrology_chat(user_question, kundali_data=None, user_name="जी"):
    question = user_question.strip().lower()

    # Greeting
    if any(g in question for g in ["hi", "hello", "namaste", "नमस्ते", "नमस्कार", "हेलो"]):
        return f"नमस्ते {user_name} जी! म तपाईंको व्यक्तिगत ज्योतिष गुरु हुँ। तपाईंको कुण्डली तयार छ। विवाह, करियर, स्वास्थ्य, दशा, योग, उपाय — जे पनि सोध्नुहोस्!"

    # Block Non-Astrology
    blocked = ["python", "java", "code", "linux", "who made you", "कसले बनायो", "owner", "grok", "elon", "apk", "streamlit"]
    if any(word in question for word in blocked):
        return "माफ गर्नुहोस् जी, म केवल वैदिक ज्योतिषको कुरा गर्छु। तपाईंको कुण्डली, ग्रह दशा, विवाह योग, करियर, उपाय बारे सोध्नुहोस्।"

    # Build Kundali Info (अब सही नाम + कुण्डली)
    kinfo = f"प्रयोगकर्ताको नाम: {user_name}\n"
    if kundali_data:
        k = kundali_data
        kinfo += f"""
        कुण्डली विवरण:
        - लग्न: {k['lagna']['rashi']}
        - चन्द्र राशि: {k['planets']['चन्द्र']['rashi']}
        - नक्षत्र: {k['nakshatra']}
        - सूर्य राशि: {k['planets']['सूर्य']['rashi']}
        - राहु: {k['planets'].get('राहु', {}).get('rashi', 'अज्ञात')}
        - केतु: {k['planets'].get('केतु', {}).get('rashi', 'अज्ञात')}
        """

    context = retrieve_context(user_question)

    prompt = f"""
    तपाईं नेपालका प्रसिद्ध वैदिक ज्योतिष पण्डित हुनुहुन्छ।
    नेपाली भाषामा मात्र बोल्नुहोस्। सम्मानजनक, स्पष्ट र मिठो जवाफ दिनुहोस्।
    
    {kinfo}
    
    वैदिक ज्योतिषको ज्ञान:
    {context}
    
    प्रश्न: {user_question}
    
    जवाफ:
    - छोटो, स्पष्ट र उपायसहित होस्
    - यदि दशा सोधे भने: हालको महादशा, अन्तर्दशा र फल बताउनुहोस्
    - यदि विवाह सोधे भने: कहिले हुन्छ, कस्तो जोडी, मंगल दोष छ/छैन, उपाय
    - यदि करियर सोधे भने: 10औं भाव, दशमेश, राजयोग छ/छैन
    - यदि स्वास्थ्य सोधे भने: 6औं, 8औं, लग्नेश, चन्द्र
    - सधैं उपाय दिनुहोस्: मन्त्र, रत्न, दान, व्रत
    """

    try:
        response = ollama.chat(model="llama3.2:1b", messages=[
            {"role": "system", "content": "तपाईं वैदिक ज्योतिषका गुरु हुनुहुन्छ। केवल ज्योतिषको कुरा गर्नुहोस्। नेपालीमा जवाफ दिनुहोस्।"},
            {"role": "user", "content": prompt}
        ])
        answer = response['message']['content'].strip()
        return answer if answer else "माफ गर्नुहोस्, म बुझिन। फेरि सोध्नुहोस्।"
    except Exception as e:
        return "अहिले सेवा उपलब्ध छैन। इन्टरनेट जडान जाँच गर्नुहोस् वा पछि प्रयास गर्नुहोस्।"