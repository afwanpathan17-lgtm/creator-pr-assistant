
# 🛡️ TrustScout.ai
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io)
[![Groq API](https://img.shields.io/badge/Powered%20by-Groq-orange)](https://groq.com)

**Enterprise-Grade Multimodal AI Content Moderation & PR Auditing**

Manual content moderation is a bottleneck, often taking human reviewers up to 15 minutes to fully audit a 60-second video for visual risks, audio violations, and real-time PR context. **TrustScout.ai automates this entire workflow in seconds.** By leveraging state-of-the-art vision models, audio transcription, and a Retrieval-Augmented Generation (RAG) pipeline connected to the live internet, this agentic tool generates strict, policy-compliant PR and safety audits.
<img width="1717" height="871" alt="Initiating" src="https://github.com/user-attachments/assets/18aaecc6-1f9e-4d9d-8cbb-883b280250a2" />


---

## 📊 The Impact & Results

TrustScout.ai doesn't just generate text; it provides actionable, enterprise-ready compliance data. 

<img width="1762" height="867" alt="Results" src="https://github.com/user-attachments/assets/64601f00-2df7-4b0d-ad52-5f6cdd4db97f" />


### Key Deliverables:
1. **Dynamic Compliance Scoring:** A calculated, color-coded metric (0-100%) grading the overall safety of the content.
2. **Frame-by-Frame Visual Audit:** Slices video into keyframes and scans for brand risks, gestures, and visual policy violations.
3. **Agentic PR Context:** Extracts brands mentioned in the audio, searches the live internet for breaking controversies, and warns you *before* you post.
4. **PDF Export:** Generates a clean, downloadable `PR_Safety_Audit.pdf` for compliance record-keeping.

<img width="991" height="801" alt="PDF REPORT" src="https://github.com/user-attachments/assets/946864d4-dc49-47b2-b5e1-8e313079df2b" />


---

## 🚀 The Agentic Architecture

TrustScout.ai utilizes a multi-step, multimodal pipeline to cross-reference video content against live data and strict text rulebooks.

```mermaid
graph TD;
    A[Upload Video] --> B(MoviePy Extraction);
    B -->|Visual Slices| C[Llama 4 Scout Vision Scan];
    B -->|Audio Track| D[Whisper Large v3 Transcription];
    D --> E[Llama 3.1 Entity Extraction];
    E -->|Search Brands| F{DuckDuckGo Live Web Search};
    C --> G[RAG Policy Engine];
    D --> G;
    F --> G;
    G -->|Enforce youtube_rules.txt| H[Final Compliance Report & PDF];
```

---
## 🛠️ Tech Stack & Capabilities

| Layer | Technology | Function |
| :--- | :--- | :--- |
| **Frontend/UI** | `Streamlit` | Enterprise dashboard and interactive data frames. |
| **Inference Engine** | `Groq API` | Lightning-fast LPU processing for near-instant results. |
| **Vision Model** | `Llama-4-Scout-17b` | Zero-shot visual policy detection on sequential frames. |
| **Audio Model** | `Whisper-large-v3` | High-fidelity audio transcription with precise timestamping. |
| **Live Data** | `duckduckgo-search` | Automated background pipeline for real-time PR controversy checks. |
| **Export Engine**| `fpdf2` & `RegEx` | Parses LLM output to generate formatted PDF compliance reports. |

---

## 💻 Run It Locally

**1. Clone the repository:**
```bash
https://github.com/Afwan-Insights/trustscout-ai.git
```

**2. Install dependencies:**
```bash
pip install -r requirements.txt
```

**3. Configure Credentials:**
Create a `.streamlit/secrets.toml` file in the root directory and add your Groq API key:
```toml
GROQ_API_KEY = "your_api_key_here"
```

**4. Run the application:**
```bash
streamlit run app.py
```

---
