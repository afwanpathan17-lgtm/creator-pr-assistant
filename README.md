# 🛡️ TrustScout.ai
**Enterprise-Grade Multimodal AI Content Moderation & PR Auditing**

TrustScout.ai is an automated, agentic workflow designed to replace manual content review bottlenecks. It ingests short-form video content and utilizes state-of-the-art vision models, audio transcription, Retrieval-Augmented Generation (RAG), and live web searching to generate strict, policy-compliant PR and safety audits.

---

## 🚀 The Architecture
This application moves beyond basic LLM text generation by employing a multi-step, multimodal pipeline:

1. **Multimodal Extraction:** - Uses `moviepy` to slice video into sequential visual keyframes and extract isolated audio tracks.
2. **Vision-Language Processing:** - Feeds keyframes into Meta's **Llama 4 Scout** to scan for visual policy violations (e.g., brand risks, offensive imagery) using strict, formatted Markdown constraints.
3. **Audio Transcription:** - Utilizes **Whisper Large v3** to convert audio payloads into highly accurate, timestamped transcripts.
4. **Agentic Live Web Search:** - An LLM entity-extraction layer identifies public figures or brands in the transcript, silently triggers a `duckduckgo-search` query, and pulls breaking internet news to assess real-time PR risks.
5. **RAG Policy Enforcement:** - Ingests a local `youtube_rules.txt` file as "Ground Truth" to strictly enforce current platform policies without hallucination.
6. **Enterprise Export:** - Uses RegEx parsing to calculate a mathematical Compliance Score and utilizes `fpdf2` to generate a formatted, downloadable PDF audit report.

---

## 🛠️ Tech Stack
* **Frontend UI:** Streamlit
* **AI Inference Engine:** Groq API
* **Vision Model:** `meta-llama/llama-4-scout-17b-16e-instruct`
* **Audio Model:** `whisper-large-v3`
* **Text/Agentic Model:** `llama-3.1-8b-instant`
* **Data Processing:** Python, MoviePy, PIL (Pillow), RegEx
* **PDF Generation:** FPDF2
* **Live Search Tool:** DuckDuckGo Search API

---

## 📸 Dashboard Interface
*(Note: Add a screenshot of your Streamlit Dashboard here!)*

* **Real-time Compliance Gauge:** Dynamic scoring based on aggregate transcript and visual analysis.
* **Side-by-Side Reporting:** Expandable data frames for isolated audio and visual analysis.
* **One-Click Export:** Seamless PDF report generation for compliance record keeping.

---

## 💻 Run It Locally

**1. Clone the repository:**
```bash
git clone [https://github.com/yourusername/trustscout-ai.git](https://github.com/yourusername/trustscout-ai.git)
cd trustscout-ai
