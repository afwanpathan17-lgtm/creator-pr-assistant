import streamlit as st
from moviepy.editor import VideoFileClip
from groq import Groq
import base64
from io import BytesIO
from PIL import Image

# --- THE UI/UX HERO SECTION ---
# This MUST be the first Streamlit command to unlock widescreen!
st.set_page_config(page_title="Creator PR Assistant", page_icon="🛡️", layout="wide")

# --- CONFIGURATION ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

trending_controversies = {
    "SmartPin": "High PR Risk: Major unpatched privacy vulnerability discovered 24 hours ago.",
    "OpenArt AI": "Medium PR Risk: Facing a class-action lawsuit for copyright infringement."
}

st.title("🛡️ AI Creator PR & Safety Assistant")
st.markdown("Upload your short-form content for an enterprise-grade policy, safety, and controversy scan.")
st.markdown("---")

# --- SIDEBAR CONTROL PANEL ---
with st.sidebar:
    st.header("⚙️ Control Panel")
    st.info("Upload your video below to begin the deep scan. Max length: 60 seconds.")
    
    uploaded_file = st.file_uploader("Drop Video Here", type=["mp4", "mov"])
    run_button = st.button("🚀 Run Full Scan", use_container_width=True)

# --- THE MAIN SCAN ENGINE ---
if run_button:
    if uploaded_file is None:
        st.sidebar.error("⚠️ Please upload a video first!")
        st.stop()
        
    with open("temp_video.mp4", "wb") as f:
        f.write(uploaded_file.getbuffer())            
        
        # --- THE 60-SECOND GUARDRAIL ---
        video = VideoFileClip("temp_video.mp4")
        
        if video.duration > 60:
            st.error("⚠️ Video is too long! To ensure lightning-fast analysis, please upload a clip under 1 minute.")
            st.stop() 
        
# --- THE VISUAL SLICER (5 FRAMES) ---
        st.info("Slicing video into 5 keyframes for a deep scan...")
        base64_frames = []
        
        timestamps = [video.duration * (i/6) for i in range(1, 6)]
        
        for t in timestamps:
            frame = video.get_frame(t)
            img = Image.fromarray(frame)
            img.thumbnail((512, 512)) 
            
            buffer = BytesIO()
            img.save(buffer, format="JPEG")
            base64_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
            base64_frames.append(base64_str)
            
        # --- THE VISION API CALL (LLAMA 4 SCOUT) ---
        st.info("Scanning all keyframes for visual policy violations...")
        try:
            vision_content = [
                {
                    "type": "text",
                    "text": """You are a strict YouTube Policy Reviewer. I am providing 5 sequential keyframes from a short-form video. Review the timeline for visual policy violations (Nudity, Violence, Offensive gestures, Slurs, Brand risks).

OUTPUT FORMAT:
You MUST respond using a strict Markdown table. Do not include any intro or outro paragraphs.
| Frame Sequence | Visual Element Detected | Risk Level (🟢 Low, 🟡 Med, 🔴 High) | Policy Explanation |
| :--- | :--- | :--- | :--- |
"""
                }
            ]
            
            for b64_img in base64_frames:
                vision_content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}
                })
                
            vision_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": vision_content}],
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                temperature=0.1,
            )
        except Exception as e:
            st.error(f"API Error: {e}")
            st.stop()            
        # --- AUDIO EXTRACTION & TRANSCRIPTION ---
        st.info("Extracting audio and transcribing with Whisper...")
        video.audio.write_audiofile("temp_audio.mp3", logger=None)
        
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
            
        st.info("Analyzing transcript against policies and PR risks...")
       radar_prompt = f"
        You are a strict YouTube Policy Reviewer AND a high-level PR Manager.
        Analyze the transcript against baseline rules (Profanity, Violence). 
        Cross-reference any brands mentioned with this database: {trending_controversies}"
        
        OUTPUT FORMAT:
        Do not write introductory or concluding paragraphs. Output a professional audit using this exact Markdown structure for every issue found:
        
        * ⏱️ **[Timestamp]** - 🎙️ **Quote:** "[Insert transcript quote]"
        * 🚨 **Risk Level:** [🟢 Low, 🟡 Med, or 🔴 High]
        * 🛡️ **Action Required:** [Your PR advice]
        ---
        """
        
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": radar_prompt},
                {"role": "user", "content": f"Here is the transcript:\n\n{full_transcript}"}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.1, 
        )
        
        # --- THE ENTERPRISE UI/UX DASHBOARD ---
        st.markdown("---")
        st.header("📊 Final Moderation Audit")
        
        # Create two side-by-side columns
        col1, col2 = st.columns(2)
        
        with col1:
            st.success("✅ Visual Scan Complete")
            st.subheader("👁️ Visual Report")
            with st.expander("View Detailed Visual Findings", expanded=True):
                st.write(vision_completion.choices[0].message.content)
                
        with col2:
            st.success("✅ Audio Scan Complete")
            st.subheader("🔊 Audio & PR Report")
            with st.expander("View Detailed Audio Findings", expanded=True):
                st.write(chat_completion.choices[0].message.content)
