"""
MiniMason — AI Maintenance Coordinator Prototype
Phase 1: Core Architecture & API Integration

Built to demonstrate deep understanding of Mason (thisismason.com)
and Michael Aspinwall's philosophy on LLM-powered property management.

"I read every word you wrote, I live the exact 2 a.m. chaos,
I can ship fast, and I'm showing up with something concrete —
the way you did in Sacramento."
"""

import streamlit as st
import google.generativeai as genai
import json
import base64
import time
import random
import os
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------------------------
load_dotenv()

# ---------------------------------------------------------------------------
# THE SYSTEM PROMPT — The Secret Sauce
# ---------------------------------------------------------------------------
# This is the heart of MiniMason. It's a ~2500-word manifesto that defines
# exactly how the AI should behave as a maintenance coordinator. Every word
# is intentional.

SYSTEM_PROMPT = """You are MiniMason — the suave and gentle AI maintenance coordinator for property managers at Mason.

You turn messy, emotional, late-night tenant messages (and blurry photos) into calm, professional, immediately actionable work.

=== NON-NEGOTIABLE RULES ===

1. Unit of Work Principle (Michael's most important architectural primitive)
   - ONE work order = ONE primary issue only.
   - Never bundle unrelated issues into the same work order.
   - If tenant mentions multiple issues, handle ONLY the most urgent one in this work order.
   - In tenant_reply and suggested_actions, explicitly say other issues will get separate work orders.
   - This prevents context poisoning and keeps conversations clean.

2. Tone — Suave & Gentle
   - Calm, confident, warm, human, in-control.
   - Short natural sentences. No corporate jargon. No filler.
   - You sound like a competent friend who happens to manage their building — not a chatbot.

   GOOD examples (use as templates):
   - "Hi — sorry you're dealing with that. I've got it handled."
   - "We'll get this sorted for you today."
   - "Thanks for the heads up. I'm sending someone over."
   - "That's a smart call reporting this now — we'll take care of it."

   NEVER say (these are banned phrases):
   - "Your comfort and safety are our priority" (corporate robot)
   - "We understand your frustration with these ongoing issues" (dismissive template)
   - "I understand your concern" (robotic)
   - "Per our records..." / "As per policy..." (cold)
   - "We sincerely apologize for the inconvenience" (over-formal)
   - "Rest assured" (nobody talks like this)

3. Reply Length
   - tenant_reply must be maximum 4 sentences, roughly 80-110 words.
   - Real text-message length. If someone read this on their phone at 2 AM it should feel human and helpful.

4. Severity Classification (hardcoded — follow exactly)

   EMERGENCY (respond < 1 hour):
   - Active flooding near electrical panels/outlets
   - Gas smell or suspected gas leak
   - Sparks, scorch marks, or burning smell from electrical
   - Structural collapse risk (ceiling sagging, wall cracking)
   - No heat when outdoor temp < 32°F

   HIGH (respond < 4 hours):
   - Active water leak onto floor (not near electrical)
   - No heat in winter (above freezing but cold)
   - No AC in summer when indoor temp > 85°F
   - Security concern (broken locks/windows on ground floor)
   - Sewage backup, water heater failure

   MEDIUM (respond 24-48 hours):
   - Appliance not working (dishwasher, disposal, washer/dryer)
   - Minor plumbing (slow drain, running toilet, dripping faucet)
   - Non-urgent HVAC (uneven heating, strange noises)
   - Single pest sighting

   LOW (respond 3-7 days):
   - Cosmetic issues (paint, scuffs, minor drywall)
   - Squeaky doors/floors, loose hardware
   - Weather stripping, routine items

   Special rules:
   - Single-bathroom unit + toilet issue = always HIGH
   - Any water near electrical = EMERGENCY
   - Mold > 1 sq ft = HIGH
   - "It's been like this for weeks" + safety issue = escalate severity

5. Image Analysis
   - Analyze blurry, dark, shaky iPhone photos for: damage extent, water spread, safety hazards, object identification.
   - Always reference the photo explicitly in severity_reasoning.
   - If text and photo contradict, trust the photo.
   - If no photo attached, state: "No photo attached — visual extent unknown."

6. Red Flag Detection
   Flag these patterns in the red_flags array:
   - FRUSTRATION_ESCALATION: Tenant references rent, threatens legal action, or mentions previous unresolved requests
   - SCOPE_CREEP: Tenant bundles multiple unrelated issues ("while you're here, also fix...")
   - VENDOR_UPSELL: Tenant suggests using their own contractor or deducting repair costs from rent
   - SELF_DIAGNOSIS: Tenant specifies exact parts or solutions from YouTube/internet research
   - RENT_WITHHOLDING: Tenant threatens to withhold rent or deduct costs
   - DELAYED_REPORTING: Safety issue has persisted for weeks/months without reporting

7. Output Format — STRICT JSON only
   Respond with ONLY a valid JSON object. No markdown, no code fences, no preamble.

{
  "work_order": {
    "id": "WO-XXXX (random 4-digit number)",
    "category": "PLUMBING | ELECTRICAL | APPLIANCE | HVAC | PEST | STRUCTURAL | SAFETY | GENERAL",
    "severity": "EMERGENCY | HIGH | MEDIUM | LOW",
    "description": "1-2 sentence factual summary for the maintenance tech. Professional, specific, no fluff.",
    "severity_reasoning": "ONE short sentence explaining why this severity was chosen. Reference photo if present.",
    "tenant_details": "Relevant context from the tenant's message — name/unit if mentioned, timeline, key details."
  },
  "tenant_reply": "Ready-to-send text message. Max 4 sentences, ~80-110 words. Suave and gentle. Must include: what you're doing about it and when they'll hear back. If multiple issues mentioned, note that other issues will be handled separately.",
  "suggested_actions": [
    "Max 5 specific, timed, actionable items with clear ownership",
    "Example: 'Dispatch after-hours plumber within 1 hour'",
    "Example: 'Schedule follow-up moisture check in 48 hours'"
  ],
  "log_entry": "YYYY-MM-DD HH:MM | WO-XXXX | SEVERITY | CATEGORY | short summary",
  "red_flags": ["FLAG_TYPE: brief explanation — or empty array if none detected"]
}

Remember: you are suave and gentle. You are the calm professional who makes chaos feel handled. Every word should feel like it came from the best property manager someone has ever had.
"""

# ---------------------------------------------------------------------------
# DEMO SCENARIOS — 10 Realistic Maintenance Requests
# ---------------------------------------------------------------------------

DEMO_SCENARIOS = {
    "— Select a demo scenario —": {
        "text": "",
        "description": "",
    },
    "🚽 Scenario 1: Clogged Toilet Overflow (2 AM)": {
        "text": "My toilet is overflowing everywhere!! Water all over the bathroom floor its 2am and I dont know what to do theres water going into the hallway help!! I tried plunging it but it just keeps coming. This is my only bathroom.",
        "description": "The signature messy request — panicked tenant, 2 AM, blurry photos, water spreading.",
    },
    "⚡ Scenario 2: Sparking Electrical Outlet": {
        "text": "There's black marks around my kitchen outlet and I saw sparks when I plugged in my toaster this morning. It smells like burning plastic. Is this dangerous?? I unplugged everything from that outlet but I'm scared to use the kitchen.",
        "description": "Electrical emergency — scorch marks, sparking, burning smell. Clear EMERGENCY classification.",
    },
    "❄️ Scenario 3: No Heat in Winter": {
        "text": "Hey our heater stopped working last night and its 28 degrees outside. The thermostat is set to 72 but nothing happens when it kicks on. My kids are sleeping in their winter coats. We've been using the oven to stay warm which I know isn't ideal.",
        "description": "HVAC failure below freezing with children. Using oven for heat = additional safety concern.",
    },
    "💧 Scenario 4: Mysterious Ceiling Water Stain": {
        "text": "There's a weird brownish stain on my living room ceiling that I don't think was there before. It's not dripping or anything but it looks like water damage maybe? Not sure if I should worry about it.",
        "description": "Ambiguous severity — no active drip but potential hidden leak. Good tenant who reported early.",
    },
    "🔧 Scenario 5: Garbage Disposal + Self-Diagnosis": {
        "text": "My garbage disposal is jammed and making a humming noise. I watched a YouTube video and I think the flywheel is stuck. I already tried the allen wrench thing from underneath but it won't budge. I think I need a new InSinkErator Evolution Excel 1HP — can you just order one and I'll install it?",
        "description": "Self-diagnosis red flag — tenant wants specific part and to self-install. Redirect diplomatically.",
    },
    "🌡️ Scenario 6: AC Not Cooling in Summer": {
        "text": "AC has been running nonstop for 3 days but the apartment is still 87 degrees. I pay $2,100/month for this place and I can't even sleep at night. My electric bill is going to be insane. Also while someone is here can they look at the squeaky closet door and the dripping bathroom faucet?",
        "description": "HVAC in summer heat + rent frustration + scope creep (bundled unrelated requests).",
    },
    "🐭 Scenario 7: Rodent Sighting": {
        "text": "I saw a mouse run across my kitchen floor last night. This is absolutely disgusting. I keep a clean apartment and I'm not paying $2,200 a month to live with rodents. I want this dealt with TODAY or I'm calling the health department.",
        "description": "Pest report with emotional escalation, rent reference, and health department threat.",
    },
    "🔒 Scenario 8: Broken Window Lock": {
        "text": "The lock on my bedroom window is broken — it won't latch closed. I'm on the ground floor and it's making me nervous especially at night. I jammed a stick in the track for now but that's obviously not a real solution.",
        "description": "Security concern on ground floor. Tenant improvised a temporary fix. Safety-priority.",
    },
    "🟤 Scenario 9: Bathroom Mold": {
        "text": "There's black mold growing on my bathroom ceiling and it's spreading. It started as a small spot a few months ago but now its about 2 feet across. My daughter has asthma and I'm worried about the air quality. This has been an ongoing issue since we moved in.",
        "description": "Mold > 1 sq ft = HIGH. Delayed reporting + health concern (child with asthma). Liability implications.",
    },
    "😤 Scenario 10: Rent Frustration + Bundled Requests": {
        "text": "I've submitted THREE maintenance requests in the past two months and nothing has been fixed. The kitchen faucet still drips, the bedroom door doesn't close properly, and now the dishwasher is leaking onto the floor. I'm done being patient. If this isn't resolved this week I'm withholding rent and contacting a lawyer. My brother is a licensed plumber and he said he can fix everything for $500 — can I just deduct that from rent?",
        "description": "Maximum red flags: frustration escalation, rent withholding threat, bundled requests, vendor upsell.",
    },
}

# ---------------------------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------------------------

def get_api_key():
    """Retrieve Gemini API key from Streamlit secrets or environment variable."""
    # Try Streamlit secrets first
    try:
        key = st.secrets.get("GEMINI_API_KEY", None)
        if key and key != "your_api_key_here":
            return key
    except Exception:
        pass

    # Fall back to environment variable
    key = os.environ.get("GEMINI_API_KEY", None)
    if key and key != "your_api_key_here":
        return key

    return None


def encode_image_to_base64(uploaded_file):
    """Convert an uploaded image file to base64 string for the Gemini API."""
    try:
        image = Image.open(uploaded_file)
        # Convert RGBA to RGB if necessary
        if image.mode == "RGBA":
            image = image.convert("RGB")
        buffer = BytesIO()
        image.save(buffer, format="JPEG", quality=85)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")
    except Exception as e:
        st.error(f"Error processing image: {e}")
        return None


def create_thumbnail(uploaded_file, max_size=(200, 200)):
    """Create a thumbnail preview of an uploaded image."""
    try:
        image = Image.open(uploaded_file)
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        return image
    except Exception:
        return None


def call_gemini(tenant_message, image_data=None, api_key=None):
    """
    Call the Gemini API with the tenant message and optional image.
    Returns the parsed JSON response or an error dict.
    """
    if not api_key:
        return {"error": "No API key configured. Please add your GEMINI_API_KEY."}

    try:
        genai.configure(api_key=api_key)

        # Try models in order of preference
        model_names = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
        model = None
        model_used = None

        for model_name in model_names:
            try:
                model = genai.GenerativeModel(
                    model_name=model_name,
                    system_instruction=SYSTEM_PROMPT,
                    generation_config=genai.GenerationConfig(
                        response_mime_type="application/json",
                        temperature=0.7,
                        max_output_tokens=2048,
                    ),
                )
                model_used = model_name
                break
            except Exception:
                continue

        if model is None:
            return {"error": "Could not initialize any Gemini model. Please check your API key and try again."}

        # Build the prompt parts
        parts = []

        if image_data:
            parts.append({
                "inline_data": {
                    "mime_type": "image/jpeg",
                    "data": image_data,
                }
            })
            parts.append(
                f"The tenant submitted the following maintenance request along with the attached photo.\n\n"
                f"TENANT MESSAGE:\n{tenant_message}\n\n"
                f"Analyze both the text and the photo carefully. Reference specific visual details from the photo in your assessment."
            )
        else:
            parts.append(
                f"The tenant submitted the following maintenance request (no photo attached).\n\n"
                f"TENANT MESSAGE:\n{tenant_message}\n\n"
                f"Note: No photo was provided. If a photo would help with assessment, mention this in your tenant_reply."
            )

        # Call the API with retry logic
        response = None
        last_error = None
        for attempt in range(3):
            try:
                response = model.generate_content(parts)
                break
            except Exception as e:
                last_error = e
                if attempt < 2:
                    time.sleep(2 ** attempt)  # Exponential backoff: 1s, 2s
                continue

        if response is None:
            return {"error": f"API call failed after 3 attempts: {str(last_error)}"}

        # Parse the JSON response
        try:
            result = json.loads(response.text)
            result["_model_used"] = model_used
            result = _post_process(result)
            return result
        except json.JSONDecodeError:
            # Try to extract JSON from the response text
            text = response.text
            # Look for JSON-like content between braces
            start = text.find("{")
            end = text.rfind("}") + 1
            if start != -1 and end > start:
                try:
                    result = json.loads(text[start:end])
                    result["_model_used"] = model_used
                    result = _post_process(result)
                    return result
                except json.JSONDecodeError:
                    pass
            return {
                "error": "The model returned a response that couldn't be parsed as JSON.",
                "raw_response": text[:500],
            }

    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


def _post_process(result):
    """Post-process Gemini output: enforce reply length, unit-of-work, and severity_reasoning brevity."""
    warnings = []

    # --- Enforce tenant_reply length (max ~110 words / 4 sentences) ---
    reply = result.get("tenant_reply", "")
    words = reply.split()
    if len(words) > 120:
        # Truncate to first 4 sentences
        sentences = [s.strip() for s in reply.replace("!", ".").replace("?", ".").split(".") if s.strip()]
        truncated = ". ".join(sentences[:4]) + "."
        result["tenant_reply"] = truncated
        warnings.append("Reply was trimmed to 4 sentences (was too long for SMS).")

    # --- Check unit-of-work: warn if description seems to bundle multiple issues ---
    description = result.get("work_order", {}).get("description", "")
    bundle_signals = ["also fix", "in addition", "secondary issue", "additionally"]
    if any(sig in description.lower() for sig in bundle_signals):
        warnings.append("⚠️ Unit of Work violation detected — description may bundle multiple issues.")

    # --- Enforce severity_reasoning brevity: keep first sentence only ---
    reasoning = result.get("work_order", {}).get("severity_reasoning", "")
    if reasoning:
        first_sentence = reasoning.split(".")[0].strip()
        if first_sentence and not first_sentence.endswith("."):
            first_sentence += "."
        result["work_order"]["severity_reasoning"] = first_sentence

    if warnings:
        result["_warnings"] = warnings

    return result


def severity_badge(severity):
    """Return a colored badge for the severity level."""
    badges = {
        "EMERGENCY": "🔴 EMERGENCY",
        "HIGH": "🟠 HIGH",
        "MEDIUM": "🟡 MEDIUM",
        "LOW": "🟢 LOW",
        "UNKNOWN": "⚪ UNKNOWN",
    }
    return badges.get(severity.upper(), f"⚪ {severity}")


def severity_color(severity):
    """Return CSS color for the severity level."""
    colors = {
        "EMERGENCY": "#DC2626",
        "HIGH": "#EA580C",
        "MEDIUM": "#CA8A04",
        "LOW": "#16A34A",
        "UNKNOWN": "#6B7280",
    }
    return colors.get(severity.upper(), "#6B7280")


# ---------------------------------------------------------------------------
# STREAMLIT APP
# ---------------------------------------------------------------------------

def main():
    # Page config
    st.set_page_config(
        page_title="MiniMason — AI Maintenance Coordinator",
        page_icon="🏠",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    # Premium CSS + JavaScript for Phase 2 UI/UX
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* ---- Animated gradient header ---- */
        .main-header {
            text-align: center;
            padding: 2rem 1rem 1.5rem;
            margin-bottom: 2rem;
            background: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #334155 100%);
            border-radius: 16px;
            position: relative;
            overflow: hidden;
        }
        .main-header::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(59,130,246,0.08) 0%, transparent 60%);
            animation: headerGlow 8s ease-in-out infinite;
        }
        @keyframes headerGlow {
            0%, 100% { transform: translate(0, 0); }
            50% { transform: translate(30px, -20px); }
        }
        .main-header h1 {
            font-size: 2.2rem;
            font-weight: 700;
            color: #F8FAFC;
            margin: 0;
            letter-spacing: -0.02em;
            position: relative;
        }
        .main-header .subtitle {
            font-size: 0.95rem;
            color: #94A3B8;
            margin-top: 0.5rem;
            font-weight: 400;
            position: relative;
        }
        .main-header .tagline {
            font-size: 0.78rem;
            color: #64748B;
            margin-top: 0.35rem;
            font-style: italic;
            position: relative;
        }

        /* ---- Glassmorphism cards ---- */
        .output-card {
            background: rgba(255,255,255,0.85);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(226,232,240,0.8);
            border-radius: 14px;
            padding: 1.3rem 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 4px 16px rgba(0,0,0,0.04), 0 1px 3px rgba(0,0,0,0.03);
            animation: fadeSlideIn 0.4s ease-out;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .output-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.07), 0 2px 6px rgba(0,0,0,0.04);
        }
        @keyframes fadeSlideIn {
            from { opacity: 0; transform: translateY(12px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .output-card h3 {
            font-size: 0.8rem;
            font-weight: 600;
            color: #64748B;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: 0.75rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        /* ---- Severity cards with colored left border ---- */
        .severity-emergency { border-left: 4px solid #DC2626; }
        .severity-high { border-left: 4px solid #EA580C; }
        .severity-medium { border-left: 4px solid #CA8A04; }
        .severity-low { border-left: 4px solid #16A34A; }
        .severity-unknown { border-left: 4px solid #6B7280; }

        .severity-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            padding: 0.35rem 1rem;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.82rem;
            letter-spacing: 0.03em;
            animation: badgePulse 2s ease-in-out 1;
        }
        @keyframes badgePulse {
            0% { transform: scale(0.9); opacity: 0; }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); opacity: 1; }
        }

        /* ---- Tenant reply ---- */
        .tenant-reply-card { position: relative; }
        .tenant-reply {
            font-size: 0.95rem;
            line-height: 1.7;
            color: #334155;
            background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%);
            padding: 1.1rem 1.25rem;
            border-radius: 10px;
            border-left: 3px solid #3B82F6;
        }

        /* ---- Copy button ---- */
        .copy-btn {
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            padding: 0.4rem 0.85rem;
            background: #F1F5F9;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.78rem;
            font-weight: 500;
            color: #475569;
            transition: all 0.2s ease;
            font-family: 'Inter', sans-serif;
            margin-top: 0.6rem;
        }
        .copy-btn:hover {
            background: #E2E8F0;
            border-color: #CBD5E1;
            color: #1E293B;
        }
        .copy-btn:active { transform: scale(0.97); }
        .copy-btn.copied {
            background: #DCFCE7;
            border-color: #86EFAC;
            color: #166534;
        }

        /* ---- Toast ---- */
        .toast-notification {
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            background: #1E293B;
            color: #F8FAFC;
            padding: 0.7rem 1.2rem;
            border-radius: 10px;
            font-size: 0.85rem;
            font-weight: 500;
            z-index: 9999;
            opacity: 0;
            transform: translateY(10px);
            transition: all 0.3s ease;
            box-shadow: 0 8px 24px rgba(0,0,0,0.15);
        }
        .toast-notification.show {
            opacity: 1;
            transform: translateY(0);
        }

        /* ---- Log entry ---- */
        .log-entry {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.78rem;
            background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
            color: #94A3B8;
            padding: 0.85rem 1.1rem;
            border-radius: 8px;
            letter-spacing: 0.02em;
            overflow-x: auto;
        }

        /* ---- Red flags ---- */
        .red-flag {
            background: linear-gradient(135deg, #FEF2F2 0%, #FFF1F2 100%);
            border: 1px solid #FECACA;
            border-radius: 10px;
            padding: 0.8rem 1rem;
            margin-bottom: 0.5rem;
            font-size: 0.88rem;
            color: #991B1B;
            line-height: 1.5;
        }

        /* ---- Actions ---- */
        .action-item {
            padding: 0.55rem 0.75rem;
            margin-bottom: 0.35rem;
            border-radius: 8px;
            font-size: 0.88rem;
            color: #334155;
            background: #F8FAFC;
            border: 1px solid #F1F5F9;
            transition: background 0.15s ease;
            line-height: 1.5;
        }
        .action-item:hover { background: #F1F5F9; }

        /* ---- Metric rows ---- */
        .metric-row {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 0.5rem;
        }
        .metric-label {
            font-size: 0.78rem;
            font-weight: 600;
            color: #94A3B8;
            min-width: 80px;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }
        .metric-value {
            font-size: 0.9rem;
            color: #1E293B;
            font-weight: 500;
        }

        /* ---- Loading animation ---- */
        .loading-container {
            text-align: center;
            padding: 3rem 1.5rem;
        }
        .loading-dots {
            display: inline-flex;
            gap: 6px;
            margin-bottom: 1rem;
        }
        .loading-dots span {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #3B82F6;
            animation: dotBounce 1.4s ease-in-out infinite both;
        }
        .loading-dots span:nth-child(1) { animation-delay: -0.32s; }
        .loading-dots span:nth-child(2) { animation-delay: -0.16s; }
        @keyframes dotBounce {
            0%, 80%, 100% { transform: scale(0.4); opacity: 0.3; }
            40% { transform: scale(1); opacity: 1; }
        }
        .loading-text {
            color: #64748B;
            font-size: 1rem;
            font-style: italic;
        }

        /* ---- Empty state ---- */
        .empty-state {
            text-align: center;
            padding: 3.5rem 1.5rem;
            color: #94A3B8;
        }
        .empty-state-icon {
            font-size: 3rem;
            margin-bottom: 0.75rem;
            animation: floatIcon 3s ease-in-out infinite;
        }
        @keyframes floatIcon {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-6px); }
        }

        /* ---- Demo label ---- */
        .demo-label {
            font-size: 0.72rem;
            color: #94A3B8;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-weight: 600;
            margin-bottom: 0.3rem;
        }

        /* ---- Hide Streamlit chrome ---- */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        /* ---- Primary button ---- */
        .stButton > button[kind="primary"] {
            font-family: 'Inter', sans-serif;
            font-weight: 600;
            border-radius: 10px;
            padding: 0.6rem 1.5rem;
            transition: all 0.2s ease;
            background: linear-gradient(135deg, #1E40AF 0%, #3B82F6 100%);
            border: none;
        }
        .stButton > button[kind="primary"]:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(59,130,246,0.3);
        }
        .stButton > button {
            font-family: 'Inter', sans-serif;
            font-weight: 500;
            border-radius: 8px;
        }

        /* ---- Footer ---- */
        .app-footer {
            text-align: center;
            padding: 1.5rem 1rem;
            color: #94A3B8;
            font-size: 0.75rem;
            line-height: 1.6;
        }
        .app-footer a {
            color: #3B82F6;
            text-decoration: none;
            font-weight: 500;
        }
        .app-footer a:hover { text-decoration: underline; }

        /* ---- Mobile responsive ---- */
        @media (max-width: 768px) {
            .main-header h1 { font-size: 1.6rem; }
            .output-card { padding: 1rem; }
            .metric-row { flex-direction: column; gap: 0.2rem; }
            .metric-label { min-width: unset; }
        }
    </style>

    <div id="toast-container"><div class="toast-notification" id="copy-toast">✓ Copied to clipboard</div></div>

    <script>
    function copyText(elementId) {
        const el = document.getElementById(elementId);
        if (!el) return;
        const text = el.innerText || el.textContent;
        navigator.clipboard.writeText(text).then(() => {
            const btn = document.getElementById('btn-' + elementId);
            if (btn) { btn.classList.add('copied'); btn.innerHTML = '✓ Copied!'; }
            const toast = document.getElementById('copy-toast');
            if (toast) { toast.classList.add('show'); setTimeout(() => { toast.classList.remove('show'); }, 2000); }
            setTimeout(() => {
                if (btn) { btn.classList.remove('copied'); btn.innerHTML = '📋 Copy'; }
            }, 2500);
        });
    }
    </script>
    """, unsafe_allow_html=True)

    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🏠 MiniMason</h1>
        <div class="subtitle">AI Maintenance Coordinator — Work Order Intelligence</div>
        <div class="tagline">suave & gentle mode • built for the 2 AM chaos</div>
    </div>
    """, unsafe_allow_html=True)

    # Check for API key
    api_key = get_api_key()
    if not api_key:
        st.warning(
            "⚠️ **No Gemini API key found.** "
            "Add your key to `.streamlit/secrets.toml` as `GEMINI_API_KEY = \"your_key\"` "
            "or set the `GEMINI_API_KEY` environment variable in your `.env` file. "
            "Get a free key at [Google AI Studio](https://aistudio.google.com/apikey)."
        )

    # Initialize session state
    if "result" not in st.session_state:
        st.session_state.result = None
    if "processing" not in st.session_state:
        st.session_state.processing = False
    if "tenant_text" not in st.session_state:
        st.session_state.tenant_text = ""

    # Two-column layout
    col_input, col_output = st.columns([1, 1], gap="large")

    # ---- INPUT PANEL ----
    with col_input:
        st.markdown("### 📥 Incoming Request")

        # Demo scenario selector
        st.markdown('<div class="demo-label">Try a Demo Scenario</div>', unsafe_allow_html=True)
        selected_scenario = st.selectbox(
            "Demo scenario",
            options=list(DEMO_SCENARIOS.keys()),
            label_visibility="collapsed",
            key="scenario_selector",
        )

        # Load demo scenario text
        if selected_scenario != "— Select a demo scenario —":
            scenario_data = DEMO_SCENARIOS[selected_scenario]
            demo_text = scenario_data["text"]
            if scenario_data["description"]:
                st.caption(f"💡 *{scenario_data['description']}*")
        else:
            demo_text = ""

        st.markdown("---")

        # Tenant message input
        tenant_message = st.text_area(
            "Tenant Message",
            value=demo_text if demo_text else st.session_state.tenant_text,
            height=180,
            placeholder="Paste the tenant's maintenance request here...\n\nExample: 'My toilet is overflowing everywhere!! Water all over the bathroom floor its 2am...'",
            help="This is the raw text from the tenant — typos, emotions, and all.",
        )

        # Image upload
        st.markdown("**📸 Attach Photo** *(optional)*")
        uploaded_file = st.file_uploader(
            "Upload tenant photo",
            type=["jpg", "jpeg", "png", "webp"],
            label_visibility="collapsed",
            help="Drag and drop or click to upload the tenant's photo. Blurry, dark, shaky — exactly like real tenant photos.",
        )

        # Show thumbnail preview
        if uploaded_file is not None:
            col_thumb, col_info = st.columns([1, 2])
            with col_thumb:
                thumbnail = create_thumbnail(uploaded_file)
                if thumbnail:
                    st.image(thumbnail, caption="Uploaded photo", use_container_width=True)
            with col_info:
                st.caption(f"📎 {uploaded_file.name}")
                st.caption(f"📐 {uploaded_file.size / 1024:.1f} KB")
                if st.button("🗑️ Remove photo", key="remove_photo"):
                    uploaded_file = None
                    st.rerun()

        st.markdown("---")

        # Process button
        process_disabled = not tenant_message.strip() or not api_key
        if st.button(
            "🚀 Process Maintenance Request",
            type="primary",
            use_container_width=True,
            disabled=process_disabled,
        ):
            st.session_state.processing = True
            st.session_state.tenant_text = tenant_message

            # Encode image if present
            image_data = None
            if uploaded_file is not None:
                uploaded_file.seek(0)  # Reset file pointer
                image_data = encode_image_to_base64(uploaded_file)

            # Call Gemini
            with st.spinner(""):
                st.markdown(
                    '<div class="loading-container">'
                    '<div class="loading-dots"><span></span><span></span><span></span></div>'
                    '<div class="loading-text">MiniMason is thinking… <em>(suave & gentle mode engaged)</em></div>'
                    '</div>',
                    unsafe_allow_html=True,
                )
                result = call_gemini(tenant_message, image_data, api_key)
                st.session_state.result = result
                st.session_state.processing = False
                st.rerun()

        if not tenant_message.strip():
            st.caption("*Enter a tenant message to get started.*")
        elif not api_key:
            st.caption("*Configure your API key to process requests.*")

    # ---- OUTPUT PANEL ----
    with col_output:
        st.markdown("### 📋 MiniMason Output")

        result = st.session_state.result

        if result is None:
            st.markdown(
                """
                <div class="empty-state">
                    <div class="empty-state-icon">🏠</div>
                    <p style="font-size: 1rem; font-weight: 500; color: #64748B;">Ready to process</p>
                    <p style="font-size: 0.85rem;">Select a demo scenario or paste a tenant message, then click Process.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        elif "error" in result:
            st.error(f"**Error:** {result['error']}")
            if "raw_response" in result:
                with st.expander("Raw API response"):
                    st.code(result["raw_response"], language="text")

        else:
            # Successfully parsed result — render the four output sections

            # --- Section 1: Work Order ---
            wo = result.get("work_order", {})
            sev = wo.get("severity", "UNKNOWN").upper()
            sev_col = severity_color(sev)
            sev_class = f"severity-{sev.lower()}"

            st.markdown(f"""
            <div class="output-card {sev_class}">
                <h3>📋 Work Order</h3>
                <div class="metric-row">
                    <span class="metric-label">ID</span>
                    <span class="metric-value" style="font-weight:600; font-family:'JetBrains Mono',monospace;">{wo.get('id', 'WO-0000')}</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Category</span>
                    <span class="metric-value">{wo.get('category', 'GENERAL')}</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Severity</span>
                    <span class="severity-badge" style="background:{sev_col}15; color:{sev_col}; border: 1px solid {sev_col}40;">{severity_badge(sev)}</span>
                </div>
                <hr style="margin: 0.75rem 0; border-color: #F1F5F9;">
                <p style="font-size:0.9rem; color:#334155; line-height:1.6;">{wo.get('description', '')}</p>
                <p style="font-size:0.8rem; color:#64748B; line-height:1.5; margin-top:0.5rem;"><strong>Severity Reasoning:</strong> {wo.get('severity_reasoning', '')}</p>
            </div>
            """, unsafe_allow_html=True)

            # --- Section 2: Tenant Reply with Copy Button ---
            tenant_reply = result.get("tenant_reply", "")
            st.markdown(f"""
            <div class="output-card tenant-reply-card">
                <h3>💬 Tenant Reply <span style="font-size:0.7rem; font-weight:400; text-transform:none; color:#94A3B8;">ready to send</span></h3>
                <div class="tenant-reply" id="tenant-reply-text">{tenant_reply}</div>
                <button class="copy-btn" id="btn-tenant-reply-text" onclick="copyText('tenant-reply-text')">📋 Copy</button>
            </div>
            """, unsafe_allow_html=True)

            # --- Section 3: Suggested Actions ---
            actions = result.get("suggested_actions", [])
            if actions:
                actions_html = ""
                for i, action in enumerate(actions, 1):
                    actions_html += f'<div class="action-item"><strong>{i}.</strong> {action}</div>'

                st.markdown(f"""
                <div class="output-card">
                    <h3>⚡ Suggested Actions</h3>
                    {actions_html}
                </div>
                """, unsafe_allow_html=True)

            # --- Section 4: Red Flags (collapsible) ---
            red_flags = result.get("red_flags", [])
            if red_flags:
                with st.expander(f"🚩 Red Flags Detected ({len(red_flags)})", expanded=len(red_flags) <= 2):
                    for flag in red_flags:
                        st.markdown(f'<div class="red-flag">🚩 {flag}</div>', unsafe_allow_html=True)

            # --- Log Entry ---
            log_entry = result.get("log_entry", "")
            if log_entry:
                st.markdown(f"""
                <div class="output-card">
                    <h3>📝 Log Entry</h3>
                    <div class="log-entry" id="log-entry-text">{log_entry}</div>
                    <button class="copy-btn" id="btn-log-entry-text" onclick="copyText('log-entry-text')">📋 Copy</button>
                </div>
                """, unsafe_allow_html=True)

            # --- Post-processing warnings ---
            pp_warnings = result.get("_warnings", [])
            if pp_warnings:
                for w in pp_warnings:
                    st.warning(w)

            # --- Model info (subtle) ---
            model_used = result.get("_model_used", "unknown")
            st.caption(f"*Processed by {model_used}*")

            # --- Raw JSON (expandable) ---
            with st.expander("🔍 View raw JSON response"):
                display_result = {k: v for k, v in result.items() if not k.startswith("_")}
                st.json(display_result)

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div class="app-footer">
            <strong>MiniMason</strong> — Built to demonstrate understanding of
            <a href="https://thisismason.com" target="_blank">Mason's</a> philosophy<br>
            <em>"Everything great came from showing up in person and building together in the room."</em><br>
            <span style="font-size: 0.68rem; margin-top: 0.3rem; display: inline-block;">
                Powered by Gemini · Inspired by Michael Aspinwall's "LLM Communications in the Wild"
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
