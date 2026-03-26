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
        
        # --- THE VISUAL SLICER (THE FILMSTRIP HACK) ---
        st.info("Slicing video into a 5-frame filmstrip for visual analysis...")
        
        timestamps = [video.duration * (i/6) for i in range(1, 6)]
        frames = []
        
        for t in timestamps:
            frame = video.get_frame(t)
            img = Image.fromarray(frame)
            img.thumbnail((200, 200)) # Shrink even more to respect the 1120px width limit
            frames.append(img)
            
        # Stitch all 5 images side-by-side into ONE single image
        total_width = sum(img.size[0] for img in frames)
        max_height = max(img.size[1] for img in frames)
        filmstrip = Image.new('RGB', (total_width, max_height))
        
        x_offset = 0
        for img in frames:
            filmstrip.paste(img, (x_offset, 0))
            x_offset += img.size[0]
            
        # Translate the single filmstrip into base64
        buffer = BytesIO()
        filmstrip.save(buffer, format="JPEG")
        base64_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
        
        st.success("Successfully created the Filmstrip!")
        # -------------------------
        
        # --- THE VISION AI SCANNER ---
        st.info("Scanning filmstrip for visual policy violations...")
        
        vision_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "You are a strict YouTube Policy Reviewer. I am providing a single 'filmstrip' image containing 5 sequential frames from a short-form video. Review the sequence for any visual policy violations including: 1) Nudity, 2) Graphic violence, 3) Offensive gestures, 4) Slurs or restricted brand names written on screen. Provide a clear, structured report."
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_str}"}
                        }
                    ]
                }
            ],
            model="llama-3.2-11b-vision-preview",
            temperature=0.1,
        )
        
        st.success("Visual Scan Complete!")
        st.subheader("👁️ Visual Moderation Report")
        st.write(vision_completion.choices[0].message.content)
        st.markdown("---")
        # -----------------------------
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
