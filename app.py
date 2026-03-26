import streamlit as st
from moviepy.editor import VideoFileClip
from groq import Groq
import base64
from io import BytesIO
from PIL import Image

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
    if st.button("Run Full Scan"):
        
        with open("temp_video.mp4", "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        # --- THE NEW 60-SECOND GUARDRAIL ---
        video = VideoFileClip("temp_video.mp4")
        
        if video.duration > 60:
            st.error("⚠️ Video is too long! To ensure lightning-fast analysis and protect against the 60-second Shorts copyright rule, please upload a clip under 1 minute.")
            st.stop() 
        # -----------------------------------
         # --- THE VISUAL SLICER ---
     st.info("Slicing video into 5 keyframes for visual analysis...")
     base64_frames = []

     # Calculate 5 evenly spaced timestamps (e.g., 20%, 40%, 60%, 80%, 100% of the video)
     timestamps = [video.duration * (i/5) for i in range(1, 6)]

     for t in timestamps:
         # 1. Grab the image at this exact second
         frame = video.get_frame(t)
         # 2. Convert it into a workable image file
         img = Image.fromarray(frame)
         # 3. Save it to a temporary digital buffer
         buffer = BytesIO()
         img.save(buffer, format="JPEG")
         # 4. Translate it into base64 text
         base64_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
         base64_frames.append(base64_str)

     st.success("Successfully captured and translated 5 keyframes!")
     # -------------------------   
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
