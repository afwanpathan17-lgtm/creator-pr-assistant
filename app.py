import streamlit as st
from moviepy.editor import VideoFileClip
from groq import Groq
import base64
from io import BytesIO
from PIL import Image
from duckduckgo_search import DDGS
import re

# --- THE UI/UX HERO SECTION ---
st.set_page_config(page_title="Creator PR Assistant", page_icon="🛡️", layout="wide")

# --- CONFIGURATION ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

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
                    "text": """You are a strict YouTube Policy Reviewer. I am providing 5 sequential keyframes from a video. Review the timeline for visual policy violations (Nudity, Violence, Offensive gestures, Slurs, Brand risks).

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
            st.error(f"Visual API Error: {e}")
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
            
        # --- THE AGENTIC SEARCH PIPELINE ---
        st.info("🧠 AI is extracting brands to search the live web...")
        
        # Step 1: Ask Llama to find the brands
        entity_prompt = "Extract a comma-separated list of the main brands, companies, or public figures mentioned in this transcript. Return ONLY the comma-separated list. If none are found, return 'None'."
        entity_completion = client.chat.completions.create(
            messages=[{"role": "system", "content": entity_prompt}, {"role": "user", "content": full_transcript}],
            model="llama-3.1-8b-instant",
            temperature=0.1,
        )
        entities_str = entity_completion.choices[0].message.content.strip()
        
        # Step 2: Run the Live Web Search
        live_news_context = "No recent controversies found."
        if entities_str.lower() != "none":
            st.info(f"🌐 Searching live internet for news on: {entities_str}...")
            live_news_context = ""
            entities = [e.strip() for e in entities_str.split(",")]
            
            for entity in entities:
                try:
                    # We search DDG for the top 3 news articles about the brand
                    results = DDGS().text(f"{entity} controversy news PR", max_results=3)
                    live_news_context += f"\nLive News for {entity}:\n"
                    for r in results:
                        live_news_context += f"- {r['title']}: {r['body']}\n"
                except Exception as e:
                    pass # If the search glitches, silently skip
                    
# Step 3: The Final PR Radar
        st.info("✍️ Writing final PR report and calculating compliance score...")
        radar_prompt = f"""
        You are a strict YouTube Policy Reviewer AND a high-level PR Manager.
        
        CRITICAL RULEBOOK: You MUST grade the transcript strictly against these official guidelines:
        {youtube_rules}
        
        CRITICAL CONTEXT: Cross-reference the transcript with this LIVE BREAKING NEWS pulled from the internet:
        {live_news_context}
        
        OUTPUT FORMAT:
        You MUST start your response with exactly this line:
        SCORE: [Calculate a compliance score from 0 to 100. 100 is perfectly safe, 0 is total violation]
        
        Then, leave a blank line, and output a professional audit using this exact Markdown structure for every issue found:
        
        * ⏱️ **[Timestamp]** - 🎙️ **Quote:** "[Insert transcript quote]"
        * 🚨 **Risk Level:** [🟢 Low, 🟡 Med, or 🔴 High]
        * 📖 **Policy Rule Broken:** [Cite the exact rule from the rulebook, or write 'None']
        * 🌐 **Live Web Context:** [Mention if the live news confirms this is a bad time to post, or write 'None']
        * 🛡️ **Action Required:** [Your PR advice]
        ---
        """
        
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": radar_prompt},
                    {"role": "user", "content": f"Here is the transcript:\n\n{full_transcript}"}
                ],
                model="llama-3.1-8b-instant",
                temperature=0.1, 
            )
        except Exception as e:
            st.error(f"Audio API Error: {e}")
            st.stop()
            
        # --- PARSE THE SCORE OUT OF THE AI'S TEXT ---
        raw_audio_report = chat_completion.choices[0].message.content
        match = re.search(r"SCORE:\s*(\d+)", raw_audio_report)
        compliance_score = int(match.group(1)) if match else 100 # Grabs the number, defaults to 100 if it fails
        audio_report_clean = re.sub(r"SCORE:\s*\d+", "", raw_audio_report).strip() # Removes the score from the text
        
        # --- THE ENTERPRISE UI/UX DASHBOARD ---
        st.markdown("---")
        st.header("📊 Final Moderation Audit")
        
        # 1. The Compliance Score UI
        score_color = "🟢" if compliance_score >= 80 else "🟡" if compliance_score >= 50 else "🔴"
        st.metric(label="Overall Compliance Score", value=f"{score_color} {compliance_score}%")
        st.progress(compliance_score / 100.0)
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 2. The Side-by-Side Reports
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
                st.write(audio_report_clean)
                
        # 3. The Export Button
        st.markdown("---")
        final_report_text = f"🛡️ FINAL PR & SAFETY AUDIT\n\nCOMPLIANCE SCORE: {compliance_score}%\n\n=== VISUAL REPORT ===\n{vision_completion.choices[0].message.content}\n\n=== AUDIO & PR REPORT ===\n{audio_report_clean}"
        
        st.download_button(
            label="📥 Download Official Audit Report",
            data=final_report_text,
            file_name="pr_safety_audit.txt",
            mime="text/plain",
            use_container_width=True
        )
