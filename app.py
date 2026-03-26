import streamlit as st
from moviepy.editor import VideoFileClip
from groq import Groq

# --- CONFIGURATION (THE SECRETS SAFE) ---
# The app will now look for the key inside Streamlit's secure server settings!
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Our live "database"
trending_controversies = {
    "SmartPin": "High PR Risk: Major unpatched privacy vulnerability discovered 24 hours ago.",
    "OpenArt AI": "Medium PR Risk: Facing a class-action lawsuit for copyright infringement."
}

# --- THE APP INTERFACE ---
st.title("🛡️ Creator PR & Policy Assistant")
st.write("Upload a draft video to scan for YouTube policy violations and real-world PR risks.")

uploaded_file = st.file_uploader("Choose an MP4 video", type=["mp4"])

if uploaded_file is not None:
    if uploaded_file is not None:
    if st.button("Run Full Scan"):
        
        with open("temp_video.mp4", "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        # --- THE NEW 60-SECOND GUARDRAIL ---
        video = VideoFileClip("temp_video.mp4")
        
        if video.duration > 60:
            st.error("⚠️ Video is too long! To ensure lightning-fast analysis and protect against the 60-second Shorts copyright rule, please upload a clip under 1 minute.")
            st.stop() # This command instantly stops the rest of the code from running!
        # -----------------------------------
            
        st.info("Extracting audio...")
        
        video.audio.write_audiofile("temp_audio.mp3", logger=None)
        
        st.info("Transcribing video incredibly fast with Groq...")
        
        with open("temp_audio.mp3", "rb") as audio_file:
            transcription = client.audio.translations.create(
                model="whisper-large-v3", 
                file=audio_file,
                response_format="verbose_json"
            )
            
        full_transcript = ""
        for segment in transcription.segments:
            start_time = round(segment['start'], 2)
            full_transcript += f"[{start_time}s]: {segment['text']}\n"
            
        st.info("Analyzing transcript against policies and trending controversies...")
        
        radar_prompt = f"""
        You are a strict YouTube Policy Reviewer AND a high-level PR Manager.
        Analyze the transcript against baseline rules (Profanity, Violence). 
        Also cross-reference any brands with this database: {trending_controversies}
        Format your output clearly with timestamps, the Risk Level, and Suggested Actions.
        """
        
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": radar_prompt},
                {"role": "user", "content": f"Here is the transcript:\n\n{full_transcript}"}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.1, 
        )
        
        st.success("Scan Complete!")
        st.subheader("Risk & Controversy Report")
        st.write(chat_completion.choices[0].message.content)
