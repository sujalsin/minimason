# 🏠 MiniMason — AI Maintenance Coordinator

**A working prototype that turns messy tenant maintenance requests into structured, actionable work orders — powered by Gemini 2.5 Flash.**

Built to demonstrate deep understanding of [Mason](https://thisismason.com) and Michael Aspinwall's philosophy from *"LLM Communications in the Wild"*.

---

## ✨ What It Does

Drop in a panicked 2 AM tenant message (+ optional blurry iPhone photo) and MiniMason returns:

- **📋 Structured Work Order** — severity-classified, categorized, with one-sentence reasoning
- **💬 Tenant Reply** — suave & gentle, SMS-ready, max 4 sentences
- **⚡ Suggested Actions** — specific, timed, with clear ownership
- **🚩 Red Flag Detection** — frustration escalation, scope creep, vendor upsell, self-diagnosis, rent withholding
- **📝 Log Entry** — timestamped, structured, copy-ready

### Core Principles

| Principle | Implementation |
|-----------|---------------|
| **Unit of Work** | One work order = one issue. Bundled requests are separated automatically. |
| **Suave & Gentle** | No corporate jargon. No "Your comfort and safety are our priority." Real human tone. |
| **Context Poisoning Defense** | Emotional language, threats, and rent references don't inflate severity. |
| **Photo-First Assessment** | When text and photo contradict, the photo wins. |

---

## 🚀 Quick Start

```bash
# Clone and setup
git clone https://github.com/sujalsin/minimason.git
cd minimason

# Virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure API key (get free key at https://aistudio.google.com/apikey)
cp .env.example .env
# Edit .env → add your GEMINI_API_KEY

# Run
streamlit run app.py
```

Opens at `http://localhost:8501`.

---

## 🧪 Demo Scenarios

10 built-in scenarios covering the full spectrum of real maintenance chaos:

| # | Scenario | Tests |
|---|----------|-------|
| 1 | 🚽 Clogged Toilet Overflow (2 AM) | Panic, urgency, single-bathroom rule |
| 2 | ⚡ Sparking Electrical Outlet | EMERGENCY classification, safety |
| 3 | ❄️ No Heat in Winter | HVAC + children + oven safety concern |
| 4 | 💧 Ceiling Water Stain | Ambiguous severity, early reporting |
| 5 | 🔧 Garbage Disposal + Self-Diagnosis | SELF_DIAGNOSIS red flag |
| 6 | 🌡️ AC Not Cooling | Rent frustration + SCOPE_CREEP |
| 7 | 🐭 Rodent Sighting | FRUSTRATION_ESCALATION |
| 8 | 🔒 Broken Window Lock | Ground-floor security |
| 9 | 🟤 Bathroom Mold | DELAYED_REPORTING + health concern |
| 10 | 😤 Rent Frustration + Bundled Requests | Maximum red flags, Unit-of-Work test |

### Testing with Photos

Upload any JPEG/PNG via the drag-and-drop uploader. Use the prompts in [`image_prompts.md`](image_prompts.md) to generate realistic tenant photos with any AI image generator.

---

## 📁 Project Structure

```
minimason/
├── app.py               # Streamlit app — system prompt, Gemini integration, UI
├── requirements.txt     # streamlit, google-generativeai, python-dotenv, Pillow
├── .env.example         # API key template
├── .streamlit/
│   └── config.toml      # Theme + deployment config
├── image_prompts.md     # 8 prompts for generating test tenant photos
├── loom_script.md       # 2-3 min demo video talking points
├── cold_email.md        # Outreach email template
└── README.md
```

---

## 🛠️ Technical Details

| Component | Details |
|-----------|---------|
| **Model** | Gemini 2.5 Flash (fallback: 2.0 → 1.5) |
| **System Prompt** | ~800 words — Unit-of-Work, severity table, tone rules, red flag patterns |
| **Temperature** | 0.7 |
| **Output** | Strict JSON with `response_mime_type: "application/json"` |
| **Post-Processing** | Reply length enforcement, unit-of-work violation detection, severity_reasoning truncation |
| **UI** | Glassmorphism cards, animated header, copy-to-clipboard with toast, collapsible red flags |

---

## 💡 Philosophy

> *"Another major benefit to texting them right when they submit the issue is that it greatly reduces back and forth because they are clearly free/thinking about it right then."*
> — Michael Aspinwall

> *"Everything great came from showing up in person, sitting with real operators, and building together in the room."*
> — Michael Aspinwall, "Being There"

This prototype is built to prove: **"I read every word you wrote, I live the exact 2 AM chaos, and I'm showing up with something concrete."**
