# rag_chatbot.py - SUPER INTELLIGENT NEPALI ASTROLOGY BOT
import ollama
import chromadb
from chromadb.utils import embedding_functions
import os
from PyPDF2 import PdfReader

# Load Knowledge Base
def load_knowledge():
    if os.path.exists("knowledge/vedic_astrology_knowledge_full.pdf"):
        reader = PdfReader("knowledge/vedic_astrology_knowledge_full.pdf")
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
    else:
        text = open("knowledge/vedic_astrology_knowledge_full.txt", "r", encoding="utf-8").read()
    return text

knowledge_base = load_knowledge()

# ChromaDB Setup
client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_or_create_collection("jyotish_knowledge")

if collection.count() == 0:
    chunks = [knowledge_base[i:i+1000] for i in range(0, len(knowledge_base), 1000)]
    for i, chunk in enumerate(chunks):
        collection.add(ids=[f"chunk_{i}"], documents=[chunk])
    print("ज्ञानको भण्डार लोड भयो!")

def retrieve_context(query):
    results = collection.query(query_texts=[query], n_results=4)
    return "\n".join(results['documents'][0])

# SUPER INTELLIGENT ASTROLOGY CHAT
def astrology_chat(user_question, kundali=None):
    question = user_question.strip().lower()

    # Friendly Greetings
    if any(g in question for g in ["hi", "hello", "namaste", "नमस्ते", "नमस्कार"]):
        return "नमस्ते जी! म तपाईंको व्यक्तिगत ज्योतिषAI हुँ। तपाईंको कुण्डली बनिसक्यो! के सोध्न चाहनुहुन्छ? विवाह, करियर, स्वास्थ्य, पैसा, उपाय?"

    # Block Non-Astrology
    blocked = ["python", "java", "code", "linux", "who made you", "कसले बनायो", "owner", "grok", "elon"]
    if any(word in question for word in blocked):
        return "माफ गर्नुहोस् जी, म केवल ज्योतिष सम्बन्धी कुरा गर्छु। तपाईंको कुण्डली, ग्रह, दशा, योग, उपाय बारे सोध्नुहोस्।"

    # Kundali Info
    kinfo = ""
    if kundali:
        kinfo = f"""
        प्रयोगकर्ताको कुण्डली:
        - नाम: {kundali.get('name', 'User')}
        - लग्न: {kundali['lagna']['rashi']}
        - सूर्य: {kundali['planets']['सूर्य']['rashi']}
        - चन्द्र: {kundali['planets']['चन्द्र']['rashi']} (नक्षत्र: {kundali['nakshatra']})
        """

    context = retrieve_context(user_question)

    prompt = f"""
    तपाईं नेपालका प्रसिद्ध ज्योतिष पण्डित हुनुहुन्छ। नेपालीमा बोल्नुहोस्। हाँसिलो, सम्मानजनक र स्पष्ट जवाफ दिनुहोस्।
    {kinfo}
    
    ज्ञान:
    {context}
    
    प्रश्न: {user_question}
    
    जवाफ छोटो, मिठो, उपायसहित र नेपालीमा दिनुहोस्।
    यदि विवाह बारे सोधे भने: कहिले हुन्छ, कस्तो जोडी मिल्छ, उपाय के गर्ने भन्नुहोस्।
    """

    try:
        response = ollama.chat(model="llama3.2:1b", messages=[
            {"role": "system", "content": "तपाईं ज्योतिषका गुरु हुनुहुन्छ। केवल ज्योतिषको कुरा गर्नुहोस्।"},
            {"role": "user", "content": prompt}
        ])
        return response['message']['content']
    except:
        return "क्षमा गर्नुहोस्, अहिले सेवा उपलब्ध छैन। फेरि प्रयास गर्नुहोस्।"
