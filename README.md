# ⚡ The Anti-Generic Engine

**An autonomous multi-agent AI debate loop that forces language models to stop acting like boring startups.** 

Built for the **Inkloom Hackathon** (in partnership with WeCodeCoders), this application tackles the problem of generic, cliché AI generations. It utilizes a dual-agent architecture (Generator vs. Critic) to ensure that the output is highly original, distinct, and ready for market launch.

---

## 🚀 The Problem & Solution
**The Problem:** Startup founders often waste hours generating brand identities using standard, single-prompt AI tools. These LLMs inherently gravitate towards the mean, producing overused "-ify" suffixes, "connecting the world" taglines, and generic value propositions.
**The Solution:** The Anti-Generic Engine features an autonomous "Debate Terminal." Instead of accepting the first output, a ruthless AI Critic scans the Strategist's draft for clichés. If generic buzzwords are found, the Critic rejects the draft and forces a revision loop until the originality score passes a strict threshold.

## ✨ Key Features
*   **🤖 Multi-Agent Architecture:** Features two distinct AI personas (Brand Strategist and Anti-Generic Critic) conversing in a live debate loop.
*   **🔍 Built-in Cliche Detection:** Evaluator agent explicitly scans against a blacklist of startup buzzwords and generic concepts.
*   **📦 Structured JSON Output:** Leverages `Pydantic` to force the Gemini model to output strict, reliable JSON schemas for the final Brand Kit.
*   **💎 Glassmorphism UI:** A premium, dark-themed user interface built entirely with Streamlit and custom CSS.

## 🛠️ Tech Stack
*   **Frontend:** Streamlit
*   **Backend Logic:** Python
*   **AI Model:** Google Gemini API (`gemini-3.8-flash`)
*   **Data Validation:** Pydantic

---

## 🧠 AI Workflow Architecture

1.  **User Input:** The user provides a raw product idea.
2.  **Agent 1 (Generator):** Drafts a complete `BrandIdentity` using a Pydantic schema.
3.  **Agent 2 (Critic):** Evaluates the draft against an originality rubric and outputs a `CritiqueResult`.
4.  **Debate Loop:** If `is_cliche` is true, the Critic's harsh feedback is appended to the Generator's context, and the loop repeats (up to 3 times).
5.  **Final Export:** Once approved, the pristine JSON Brand Kit is provided as a downloadable file.

---

## 💻 Local Installation

To run this project on your local machine:

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/HimanshiGarg27/anti-generic-brand-engine.git](https://github.com/HimanshiGarg27/anti-generic-brand-engine.git)
   cd anti-generic-brand-engine
2. Install dependencies
    pip install -r requirements.txt
3. Run the streamlit application
    streamlit run app.py
   Note: You will need a valid Google Gemini API Key to run the engine. You can enter this securely via the app's sidebar UI.
   🌐 Deployment
This application is fully compatible with Streamlit Community Cloud.
When
deploying, ensure you configure the Gemini API key in the Streamlit Advanced Settings -> Secrets:
GEMINI_API_KEY = " "
👨‍💻 Author
Himanshi Garg
Aspiring AI / ML Engineer & Full Stack Developer
GitHub: @HimanshiGarg27
📄 License
This project is licensed under the MIT License - see the LICENSE file for details.
    
