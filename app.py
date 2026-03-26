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
        
       # --- THE VISUAL SLICER (MULTI-FRAME UPGRADE) ---
        st.info("Slicing video into multiple keyframes for a deep scan...")
        base64_frames = []
        
        # Calculates 5 evenly spaced timestamps
        timestamps = [video.duration * (i/11) for i in range(1, 11)]
        
        for t in timestamps:
            frame = video.get_frame(t)
            img = Image.fromarray(frame)
            
            # Keep them compressed to 512x512 so we don't break the 4MB payload limit!
            img.thumbnail((512, 512)) 
            
            buffer = BytesIO()
            img.save(buffer, format="JPEG")
            base64_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
            base64_frames.append(base64_str)
            
        st.success(f"Successfully captured {len(base64_frames)} keyframes!")
        
        # --- THE VISION API CALL ---
        st.info("Scanning all keyframes for visual policy violations...")
        
        try:
            # 1. Start with our text instructions
            vision_content = [
                {
                    "type": "text",
                    "text": "You are a strict YouTube Policy Reviewer. I am providing multiple sequential keyframes from a short-form video. Review them as a timeline for any visual policy violations including: 1) Nudity, 2) Graphic violence, 3) Offensive gestures, 4) Slurs or restricted brand names written on screen. Provide a clear, structured report."
                }
            ]
            
            # 2. Attach all of our base64 images to the exact same message
            for b64_img in base64_frames:
                vision_content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}
                })
                
            # 3. Send the massive package to Llama 4 Scout
            vision_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": vision_content
                    }
                ],
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                temperature=0.1,
            )
            
            st.success("Visual Scan Complete!")
            st.subheader("👁️ Visual Moderation Report")
            st.write(vision_completion.choices[0].message.content)
            st.markdown("---")
            
        except Exception as e:
            st.error(f"API Error: {e}")
            st.stop()
        # -----------------------------
        # -----------------------------        # -----------------------------
        # Adds a nice visual dividing line
        # -----------------------------
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
