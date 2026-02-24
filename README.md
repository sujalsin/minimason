# 🏠 MiniMason — AI Maintenance Coordinator

**A focused prototype demonstrating deep understanding of [Mason](https://thisismason.com) and Michael Aspinwall's philosophy on LLM-powered property management.**

MiniMason processes tenant maintenance requests (text + photos) through Gemini AI to produce structured work orders, ready-to-send tenant replies, suggested actions, and red flag detection — all with the "suave and gentle" tone that real property management demands.

---

## 🚀 Quick Start (< 5 minutes)

### Prerequisites
- Python 3.10+
- A Gemini API key (free at [Google AI Studio](https://aistudio.google.com/apikey))

### Setup

```bash
# 1. Navigate to the project
cd mason

# 2. Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure your API key (choose ONE method)

# Method A: Environment variable (recommended for local dev)
cp .env.example .env
# Edit .env and replace 'your_api_key_here' with your real key

# Method B: Streamlit secrets
mkdir -p .streamlit
echo 'GEMINI_API_KEY = "your_real_key_here"' > .streamlit/secrets.toml

# 5. Run the app
streamlit run app.py
```

The app will open at `http://localhost:8501`.

---

## 🧪 Testing the API Integration

1. **Select a demo scenario** from the dropdown (e.g., "Clogged Toilet Overflow")
2. Click **"Process Maintenance Request"**
3. Verify the output includes:
   - ✅ Work Order with severity badge
   - ✅ Tenant Reply in "suave and gentle" tone
   - ✅ Specific, timed suggested actions
   - ✅ Red flags (if applicable)
   - ✅ Monospace log entry

### Testing Image Upload
1. Upload any JPEG/PNG image
2. Enter a maintenance complaint
3. Verify the model references visual details from the image in its assessment

---

## 📁 Project Structure

```
mason/
├── app.py              # Main Streamlit application (Phase 1)
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template
├── .env                # Your actual API key (git-ignored)
├── image_prompts.md    # Prompts for generating test photos
└── README.md           # This file
```

---

## 🗺️ Phase Roadmap

| Phase | Status | Description |
|-------|--------|-------------|
| **Phase 1** | ✅ Complete | Core architecture, Gemini integration, system prompt, demo scenarios |
| **Phase 2** | 🔲 Planned | UI/UX polish, animations, mobile optimization |
| **Phase 3** | 🔲 Planned | Deployment, Loom demo, outreach |

---

## 💡 Core Philosophy

> *"Another major benefit to texting them right when they submit the issue is that it greatly reduces back and forth because they are clearly free/thinking about it right then."*
> — Michael Aspinwall

> *"Everything great came from showing up in person, sitting with real operators, and building together in the room."*
> — Michael Aspinwall, "Being There"

This prototype is built to prove: **"I read every word you wrote, I live the exact 2 AM chaos, I can ship fast, and I'm showing up with something concrete."**
