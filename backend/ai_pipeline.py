"""
VaakSetu — AI Pipeline (v2.1)
─────────────────────────────
ASR   : Sarvam AI (Saaras v3) — FREE tier, built for Indic languages (Kannada/Hindi/English)
NLU   : Groq Cloud (Llama 3.3 70B) — Ultra-low latency, multilingual
Verify: Keyword-based classifier — zero API cost

Pipeline: Audio/Text → Sarvam ASR → Groq Interpretation → Groq Restatement → Verify
"""

import os
import json
import logging
from typing import Optional

import httpx                                        # async-friendly HTTP client
from groq import Groq
from models import (
    ASRResult, InterpretationCard, ExtractedEntities,
    VerificationResult, VerificationStatus,
    Language, KannadaDialect,
)
from mock_integrations import enrich_context

logger = logging.getLogger("vaaksetu.pipeline")

# ─── Sarvam AI ASR constants ──────────────────────────────────────────────────
#
# Get your free API key from: https://www.sarvam.ai/apis
# Set it in backend/.env as:  SARVAM_API_KEY=your_key_here
#
# Model : Saaras v3  — best quality for Kannada, Hindi, English
# Docs  : https://docs.sarvam.ai/api-reference-docs/endpoints/speech-to-text
#
SARVAM_ASR_URL    = "https://api.sarvam.ai/speech-to-text"
SARVAM_ASR_MODEL  = "saaras:v3"   # saaras:v1 also available

# Language code map (BCP-47 tags that Sarvam accepts)
LANG_CODE: dict[Language, str] = {
    Language.KANNADA: "kn-IN",
    Language.HINDI:   "hi-IN",
    Language.ENGLISH: "en-IN",
}

# Mime types for multipart upload
AUDIO_MIME: dict[str, str] = {
    "wav":  "audio/wav",
    "mp3":  "audio/mpeg",
    "webm": "audio/webm",
    "ogg":  "audio/ogg",
    "flac": "audio/flac",
    "m4a":  "audio/mp4",
}


# ─── Groq client ─────────────────────────────────────────────────────────────

_groq_client: Optional[Groq] = None
GROQ_MODEL = "llama-3.3-70b-versatile" # "llama3-70b-8192" or "mixtral-8x7b-32768"


def get_groq_client() -> Groq:
    """Lazy-init Groq client from GROQ_API_KEY env var."""
    global _groq_client
    if _groq_client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY is not set. "
                "Get a FREE key from https://console.groq.com/ and add it to backend/.env"
            )
        _groq_client = Groq(api_key=api_key)
    return _groq_client


# ─── Sarvam AI ASR ────────────────────────────────────────────────────────────

def transcribe_audio_sarvam(
    audio_bytes: bytes,
    language: Language = Language.KANNADA,
    audio_format: str = "wav",
) -> ASRResult:
    """
    Transcribe audio using the Sarvam AI (Saaras v3) speech-to-text API.

    Supported audio formats: wav, mp3, webm, ogg, flac, m4a
    Supports Kannada (kn-IN), Hindi (hi-IN), English (en-IN) and other Indic languages.

    Set SARVAM_API_KEY in backend/.env  — free tier, no ID proof needed.
    Falls back gracefully to demo mode if key is not set.
    """
    import time

    api_key  = os.getenv("SARVAM_API_KEY", "").strip()
    lang_bcp = LANG_CODE.get(language, "kn-IN")

    # ── No credentials → demo mode ────────────────────────────────────────────
    if not api_key:
        logger.warning(
            "SARVAM_API_KEY not set. Running in text-only demo mode. "
            "Get a free key from https://www.sarvam.ai/apis and add it to backend/.env"
        )
        return ASRResult(
            transcript=(
                "[Audio received — Sarvam ASR not configured. "
                "Add SARVAM_API_KEY to backend/.env]"
            ),
            language_detected=language,
            dialect_detected=KannadaDialect.STANDARD,
            confidence=0.0,
            duration_seconds=0.0,
            segments=[],
        )

    # ── Build multipart request ───────────────────────────────────────────────
    mime_type  = AUDIO_MIME.get(audio_format, "audio/wav")
    filename   = f"audio.{audio_format}"

    headers = {
        "api-subscription-key": api_key,
    }
    files = {
        "file": (filename, audio_bytes, mime_type),
    }
    data = {
        "model":     SARVAM_ASR_MODEL,
        "language_code": "unknown",  # Saaras v3 supports auto-detection
        "with_timestamps": "false",
    }

    # ── Call Sarvam API ───────────────────────────────────────────────────────
    try:
        t0 = time.time()
        with httpx.Client(timeout=40) as client:
            resp = client.post(
                SARVAM_ASR_URL,
                headers=headers,
                files=files,
                data=data,
            )

        if resp.status_code != 200:
            logger.error(f"Sarvam ASR error {resp.status_code}: {resp.text[:300]}")
            raise RuntimeError(f"Sarvam AI returned HTTP {resp.status_code}: {resp.text[:200]}")

        duration = round(time.time() - t0, 2)
        result   = resp.json()

        # Sarvam returns: { "transcript": "...", "language_code": "...", "language_probability": ... }
        transcript = result.get("transcript", "").strip()
        detected_bcp = result.get("language_code", lang_bcp)
        
        # Map BCP-47 back to Language enum
        inv_lang_code = {v: k for k, v in LANG_CODE.items()}
        asr_detected_lang = inv_lang_code.get(detected_bcp, language)
        
        logger.info(f"Sarvam ASR [Detected: {detected_bcp}]: '{transcript}' ({duration}s)")
        
        return ASRResult(
            transcript=transcript,
            language_detected=asr_detected_lang,
            dialect_detected=KannadaDialect.STANDARD,
            confidence=result.get("language_probability", 0.90),
            duration_seconds=duration,
            segments=[],
        )

    except (KeyError, IndexError) as e:
        logger.error(f"Unexpected Sarvam response structure: {e}\n{resp.text[:400]}")
        raise RuntimeError(f"Sarvam response parsing failed: {e}")

    except httpx.TimeoutException:
        raise RuntimeError("Sarvam ASR timed out (>40s). Try a shorter audio clip.")

    except Exception as e:
        logger.error(f"Sarvam ASR failed: {e}")
        raise RuntimeError(f"Sarvam ASR failed: {e}")


def detect_audio_format(audio_bytes: bytes, filename: str = "") -> str:
    """
    Detect audio format from magic bytes or filename extension.
    Returns a Bhashini-compatible format string.
    """
    if filename:
        ext = filename.rsplit(".", 1)[-1].lower()
        fmt_map = {"wav": "wav", "mp3": "mp3", "webm": "webm",
                   "ogg": "ogg", "flac": "flac", "m4a": "wav"}
        if ext in fmt_map:
            return fmt_map[ext]

    # Magic bytes detection
    if audio_bytes[:4] == b"RIFF":
        return "wav"
    if audio_bytes[:3] == b"ID3" or audio_bytes[:2] == b"\xff\xfb":
        return "mp3"
    if audio_bytes[:4] == b"\x1aE\xdf\xa3":
        return "webm"
    if audio_bytes[:4] == b"OggS":
        return "ogg"
    if audio_bytes[:4] == b"fLaC":
        return "flac"

    return "wav"   # safe default


# ─── Text passthrough ASR ─────────────────────────────────────────────────────

def transcribe_text_as_asr(
    text: str,
    language: Language = Language.KANNADA,
    dialect: KannadaDialect = KannadaDialect.STANDARD,
) -> ASRResult:
    """Create an ASR result from direct text input (for the text-based demo path)."""
    return ASRResult(
        transcript=text,
        language_detected=language,
        dialect_detected=dialect,
        confidence=0.95,
        duration_seconds=0.0,
        segments=[],
    )


# ─── Groq: Semantic Interpretation ───────────────────────────────────────────

INTERPRETATION_SYSTEM_PROMPT = """\
You are VaakSetu, an AI assistant for the Karnataka 1092 government helpline.
Interpret citizen complaints/queries and produce a structured JSON interpretation.

Respond with VALID JSON ONLY — no markdown, no extra text. Schema:
{
  "core_issue": "One-sentence summary of the citizen's main issue in English",
  "native_core_issue": "One-sentence summary of the citizen's main issue in their Spoken Language (Kannada script for Kannada, Devanagari for Hindi)",
  "detected_language": "The primary language the citizen is speaking in (one of: kannada | hindi | english)",
  "category": "One of: Water Supply | Ration Card | Land Records | Road/Infrastructure | Pension | Garbage | Seva Sindhu | Street Light | Tree/Horticulture | BBMP Tax | Noise/Pollution | Other",
  "intent": "One of: complaint | status_inquiry | new_application | correction | emergency_report | information_request",
  "entities": {
    "location": "Location mentioned or null",
    "department": "Relevant government department or null",
    "service_name": "Specific service name or null",
    "person_name": "Person name mentioned or null",
    "id_number": "Any ID/reference number mentioned or null",
    "event_description": "Brief event description or null",
    "date_mentioned": "Any date or timeframe mentioned or null"
  },
  "raw_interpretation": "Detailed interpretation in English with nuance and implied meaning"
}

Karnataka context:
- Services: Seva Sindhu (online portal), BBMP (Bengaluru civic body), BWSSB (water supply),
  Bhoomi (land records), Aadhaar linkage, Fair Price Shops (FPS), RTC (land title)
- Code-switching is common between Kannada, Hindi, English
- Kannada expressions: "update aagilla" (not updated), "barilla" (didn't come),
  "kelsa aagilla" (work not done), "samaSye ide" (there's a problem)
- Hindi in Karnataka: "kaam nahi hua" (work not done), "paani nahi aa raha" (no water)
- Govt terms: tahsildar, taluk, gram panchayat, BPL/APL, anganwadi, ASHA worker
- You natively understand Kannada (Kannada script + romanised), Hindi, and English.\
"""


def interpret_transcript(
    transcript: str,
    language: Language = Language.KANNADA,
    dialect: KannadaDialect = KannadaDialect.STANDARD,
    enrichment_context: Optional[dict] = None,
) -> InterpretationCard:
    """Use Groq (Llama 3) to produce a structured interpretation."""
    client = get_groq_client()

    user_prompt = (
        f"Citizen speech (language: {language.value}, dialect: {dialect.value}):\n"
        f'"{transcript}"\n'
    )

    if enrichment_context:
        alerts = enrichment_context.get("alerts", [])
        if alerts:
            user_prompt += "\nActive government system alerts:\n"
            for alert in alerts:
                user_prompt += f"  • {alert}\n"

        crm = enrichment_context.get("crm_trends", {})
        top_cats = crm.get("top_categories", [])[:3]
        if top_cats:
            user_prompt += "\nTop trending issues on 1092 helpline today:\n"
            for tc in top_cats:
                user_prompt += f"  • {tc['category']}: {tc['count']} calls (trend: {tc['trend']})\n"

    user_prompt += "\nProduce the JSON interpretation:"

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": INTERPRETATION_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            max_tokens=1000,
            response_format={"type": "json_object"},
        )

        result = json.loads(response.choices[0].message.content.strip())

        ed = result.get("entities", {})
        entities = ExtractedEntities(
            location=ed.get("location"),
            department=ed.get("department"),
            service_name=ed.get("service_name"),
            person_name=ed.get("person_name"),
            id_number=ed.get("id_number"),
            event_description=ed.get("event_description"),
            date_mentioned=ed.get("date_mentioned"),
        )

        enrichment_labels = []
        if enrichment_context:
            label_map = {
                "seva_sindhu": "Seva Sindhu service data loaded",
                "bbmp":        "BBMP trending issues loaded",
                "bwssb":       "BWSSB water status loaded",
                "bhoomi":      "Bhoomi land records loaded",
                "ration_card": "Ration card database loaded",
                "pension":     "Pension portal data loaded",
            }
            for key, label in label_map.items():
                if enrichment_context.get(key):
                    enrichment_labels.append(label)

        detected_lang_str = result.get("detected_language", language.value).lower()
        try:
            detected_lang = Language(detected_lang_str)
        except ValueError:
            detected_lang = language

        return InterpretationCard(
            core_issue=result.get("core_issue", "Unable to determine"),
            native_core_issue=result.get("native_core_issue"),
            detected_language=detected_lang,
            category=result.get("category", "Other"),
            intent=result.get("intent", "unknown"),
            entities=entities,
            enrichment_context=enrichment_labels,
            confidence=0.85,
            raw_interpretation=result.get("raw_interpretation", ""),
            suggested_solution=generate_solution(result, detected_lang, enrichment_context),
        )

    except Exception as e:
        logger.error(f"Groq interpretation failed: {e}")
        return InterpretationCard(
            core_issue=f"Interpretation error: {str(e)[:120]}",
            category="Error",
            intent="unknown",
            confidence=0.0,
            raw_interpretation=str(e),
        )


# ─── Groq: Solution Generation ───────────────────────────────────────────────

SOLUTION_SYSTEM_PROMPT = """\
You are VaakSetu, an AI assistant for the Karnataka 1092 helpline.
Based on the confirmed interpretation of a citizen's issue, provide a concise, helpful solution or next step.

Context Guidelines:
- If it's a complaint, explain how to track it or what the timeline is.
- If it's an inquiry, provide the specific info requested.
- Use a polite, supportive tone.
- Reference relevant government services (Seva Sindhu, BBMP, etc.) if applicable.
- Keep it under 3 sentences.

MANDATORY Language Rules:
- Detect the language of the citizen's query and respond ONLY in that same language.
- Kannada input → Respond in Kannada script (ಕನ್ನಡ)
- Hindi input   → Respond in Devanagari script (हिंदी)
- English input → Respond in English
- Do NOT mix languages unless the citizen used a mix.
"""

def generate_solution(
    interpretation_dict: dict,
    language: Language = Language.KANNADA,
    enrichment_context: Optional[dict] = None
) -> str:
    """Generate a suggested solution/advice for the citizen using Groq."""
    client = get_groq_client()

    prompt = (
        f"Core Issue (EN): {interpretation_dict.get('core_issue')}\n"
        f"Core Issue (Native): {interpretation_dict.get('native_core_issue')}\n"
        f"Category  : {interpretation_dict.get('category')}\n"
        f"Intent    : {interpretation_dict.get('intent')}\n"
        f"Entities  : {json.dumps(interpretation_dict.get('entities', {}))}\n"
        f"Target Language : {language.value}\n"
    )

    if enrichment_context:
        prompt += f"\nRelevant Data: {json.dumps(enrichment_context.get('crm_trends', {}))}\n"

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": SOLUTION_SYSTEM_PROMPT},
                {"role": "user", "content": f"Generate a solution in {language.value} for this citizen issue:\n{prompt}"}
            ],
            temperature=0.4,
            max_tokens=300,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Solution generation failed: {e}")
        return "Our team will look into this immediately. Please keep your reference number ready."


# ─── Groq: Verification Restatement ──────────────────────────────────────────

RESTATEMENT_SYSTEM_PROMPT = """\
You are VaakSetu, an AI assistant for the Karnataka 1092 helpline.

Generate ONE short, natural verification question summarising what the citizen said.
Use the target language with simple, colloquial phrasing suited for a phone helpline.

Language rules:
• Kannada  → Use Kannada script (ಕನ್ನಡ) — e.g. "ನೀವು ರೇಷನ್ ಕಾರ್ಡ್ ಅಪ್ಡೇಟ್ ಬಗ್ಗೆ ಮಾತನಾಡುತ್ತಿದ್ದೀರಾ?"
• Hindi    → Use Devanagari script — e.g. "क्या आप राशन कार्ड अपडेट के बारे में बात कर रहे हैं?"
• English  → Simple plain English — e.g. "Are you calling about a ration card update?"

Respond with ONLY the restatement question — nothing else.\
"""


def generate_restatement(
    interpretation: InterpretationCard,
    language: Language = Language.KANNADA,
) -> str:
    """Generate a natural-language verification restatement via Groq."""
    client = get_groq_client()

    prompt = (
        f"Core issue (EN): {interpretation.core_issue}\n"
        f"Core issue (Native): {interpretation.native_core_issue}\n"
        f"Category    : {interpretation.category}\n"
        f"Intent      : {interpretation.intent}\n"
        f"Target lang : {language.value}\n\n"
        "Generate the verification question:"
    )

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": RESTATEMENT_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=200,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Restatement generation failed: {e}")
        return f"Did you say: {interpretation.core_issue}?"


# ─── Verification Classifier (keyword-based, zero cost) ──────────────────────

VERIFICATION_KEYWORDS = {
    "confirmed": [
        # English
        "yes", "correct", "right", "exactly", "that's right", "that is correct", "yep", "yeah",
        # Kannada (romanised + script)
        "houdu", "howdu", "houdhu", "sari", "adhe", "ade", "ha", "haa",
        "ಹೌದು", "ಸರಿ",
        # Hindi
        "haan", "han", "ji haan", "bilkul", "theek hai",
        "हाँ", "हां", "जी हाँ", "बिल्कुल",
    ],
    "denied": [
        # English
        "no", "wrong", "incorrect", "that's not", "not right", "nope",
        # Kannada
        "illa", "alla", "beda", "thappu",
        "ಇಲ್ಲ", "ಅಲ್ಲ",
        # Hindi
        "nahin", "nahi", "galat", "naa",
        "नहीं", "नहीं", "गलत",
    ],
    "partial": [
        # English
        "but", "however", "not exactly", "kind of", "sort of", "partially", "also",
        # Kannada
        "aadre", "aaadre", "mattu", "aadhare",
        "ಆದರೆ", "ಮತ್ತು",
        # Hindi
        "lekin", "par", "magar", "aur bhi",
        "लेकिन", "पर", "मगर",
    ],
}


def classify_verification_response(response_text: str) -> VerificationStatus:
    """Classify citizen's yes/no/partial response — pure keyword matching, zero API cost."""
    text_lower = response_text.lower().strip()

    if not text_lower:
        return VerificationStatus.UNCERTAIN

    has_confirm = any(kw in text_lower for kw in VERIFICATION_KEYWORDS["confirmed"])
    has_deny    = any(kw in text_lower for kw in VERIFICATION_KEYWORDS["denied"])
    has_partial = any(kw in text_lower for kw in VERIFICATION_KEYWORDS["partial"])

    if has_confirm and has_partial:
        return VerificationStatus.PARTIAL
    if has_confirm and not has_deny:
        return VerificationStatus.CONFIRMED
    if has_deny:
        return VerificationStatus.INCORRECT
    if has_partial:
        return VerificationStatus.PARTIAL

    return VerificationStatus.UNCERTAIN


# ─── Full Pipeline Orchestrator ───────────────────────────────────────────────

def run_pipeline(
    text: str,
    language: Language = Language.KANNADA,
    dialect: KannadaDialect = KannadaDialect.STANDARD,
    audio_bytes: Optional[bytes] = None,
    audio_filename: str = "",
) -> dict:
    """
    Run the complete VaakSetu pipeline.

    Text path  → text passthrough ASR → Groq NLU → Groq restatement
    Audio path → Sarvam AI ASR        → Groq NLU → Groq restatement
    """

    # ── Step 1: ASR ────────────────────────────────────────────────────────────
    if audio_bytes:
        fmt = detect_audio_format(audio_bytes, audio_filename)
        asr_result = transcribe_audio_sarvam(audio_bytes, language, fmt)
        # Prioritise language detected by ASR for the rest of the pipeline
        language = asr_result.language_detected
    else:
        asr_result = transcribe_text_as_asr(text, language, dialect)

    transcript = asr_result.transcript

    # ── Step 2: Context enrichment (mock govt APIs) ───────────────────────────
    enrichment = enrich_context(transcript)

    # ── Step 3: Semantic interpretation (Groq) ───────────────────────────────
    interpretation = interpret_transcript(
        transcript=transcript,
        language=language,
        dialect=dialect,
        enrichment_context=enrichment,
    )

    # Use detected language for subsequent steps
    active_language = interpretation.detected_language or language
    if active_language != language:
        logger.info(f"Language switch detected: {language} -> {active_language}")

    # ── Step 4: Sentiment (local rule-based, zero cost) ───────────────────────
    from sentiment import classify_sentiment
    sentiment = classify_sentiment(text=transcript, language=active_language.value)

    # ── Step 5: Escalation logic ──────────────────────────────────────────────
    should_escalate = False
    escalation_reason = None

    if sentiment.urgency_flag and sentiment.confidence > 0.7:
        should_escalate = True
        escalation_reason = (
            "High distress/urgency detected — escalating to human agent immediately"
        )
    elif asr_result.confidence > 0.0 and asr_result.confidence < 0.4:
        # confidence == 0.0 → Bhashini not configured (demo mode) — don't penalise
        should_escalate = True
        escalation_reason = "Low ASR confidence — escalating for manual review"

    # ── Step 6: Verification restatement (Groq) ──────────────────────────────
    verification = VerificationResult(
        status=VerificationStatus.SKIPPED if should_escalate else VerificationStatus.PENDING,
        restatement_text="",
        restatement_language=active_language,
        attempt_number=0,
    )

    if not should_escalate:
        verification.restatement_text = generate_restatement(interpretation, active_language)

    return {
        "asr_result":       asr_result,
        "interpretation":   interpretation,
        "sentiment":        sentiment,
        "verification":     verification,
        "enrichment_data":  enrichment,
        "should_escalate":  should_escalate,
        "escalation_reason": escalation_reason,
        "active_language":  active_language,
    }
