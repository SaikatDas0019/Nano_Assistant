import streamlit as st
import google.generativeai as genai
import re
from gtts import gTTS
import io
import os
from dotenv import load_dotenv

# .env ফাইল থেকে এনভায়রনমেন্ট ভেরিয়েবল লোড করা
load_dotenv()

# ==========================================
# ১. Streamlit পেজ সেটআপ
# ==========================================
st.set_page_config(page_title="Robot Brain Test", page_icon="🤖", layout="centered")
st.title("🤖 Robot Brain Test")
st.write("আপনার ফোনের কীবোর্ডের মাইক ব্যবহার করে কথা বলুন!")

# ==========================================
# ২. API Key সিকিউরিটি (.env থেকে নেওয়া)
# ==========================================
# .env ফাইল থেকে API key পড়া হচ্ছে
api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    # API কনফিগারেশন
    genai.configure(api_key=api_key)
    
    system_instruction = """
    You are a friendly, intelligent robot companion. 
    ALWAYS start your response with an emotion tag enclosed in square brackets. 
    Valid tags are: [Happy], [Sad], [Thinking], [Excited], [Neutral].
    Example format: "[Happy] Hello there! How can I help you today?"
    Keep your answers brief and conversational.
    """
    
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=system_instruction
    )

    # ==========================================
    # ৩. কোর ফাংশনসমূহ
    # ==========================================
    def get_ai_response(user_input):
        try:
            response = model.generate_content(user_input)
            return response.text.strip()
        except Exception as e:
            return "[Sad] I am having trouble connecting to my brain."

    def parse_response(raw_text):
        match = re.match(r'\[(.*?)\](.*)', raw_text, re.DOTALL)
        if match:
            return match.group(1).strip(), match.group(2).strip()
        return "Neutral", raw_text

    def get_emotion_emoji(emotion):
        """ওয়েবসাইটের স্ক্রিনের জন্য ইমোজি"""
        faces = {
            "Happy": "😊",
            "Sad": "😢",
            "Thinking": "🤔",
            "Excited": "🤩",
            "Neutral": "😐"
        }
        return faces.get(emotion, "😐")

    # ==========================================
    # ৪. ইউজার ইন্টারফেস (UI) এবং লজিক
    # ==========================================
    user_input = st.text_input("আপনার মেসেজ দিন (বা কীবোর্ডের মাইক আইকনে চাপুন):")
    
    if st.button("Send") and user_input:
        with st.spinner("রোবট ভাবছে... 🤔"):
            
            # AI থেকে উত্তর আনা
            raw_response = get_ai_response(user_input)
            
            # ইমোশন এবং টেক্সট আলাদা করা
            emotion, spoken_text = parse_response(raw_response)
            
            # স্ক্রিনে বড় করে ইমোজি দেখানো
            st.markdown(f"<h1 style='text-align: center; font-size: 100px;'>{get_emotion_emoji(emotion)}</h1>", unsafe_allow_html=True)
            
            # রোবট কী বলছে তা টেক্সট আকারে দেখানো
            st.success(f"**Robot:** {spoken_text}")
            
            # Text-to-Speech (gTTS) - অডিও তৈরি করে ব্রাউজারে প্লে করা
            tts = gTTS(text=spoken_text, lang='en')
            audio_bytes = io.BytesIO()
            tts.write_to_fp(audio_bytes)
            audio_bytes.seek(0)
            
            # অডিও প্লেয়ার
            st.audio(audio_bytes, format="audio/mp3", autoplay=True)

else:
    st.error("⚠️ .env ফাইলে API Key পাওয়া যায়নি! দয়া করে প্রজেক্ট ফোল্ডারে একটি .env ফাইল তৈরি করে আপনার GEMINI_API_KEY যুক্ত করুন।")