"""
VaakSetu — Sentiment and Urgency Classifier
Dual-channel sentiment analysis: lexical (keyword + pattern) and acoustic (simulated).
Produces a fused sentiment result with urgency flag and human-readable display label.
"""

import re
from models import SentimentCategory, SentimentResult


# ─── Lexical Keyword Banks ──────────────────────────────────────────────────

# Kannada emotional keywords (transliterated)
KANNADA_DISTRESS = [
    "sahaya", "help", "dayavittu", "please", "kashta", "tumba kashta",
    "bejaar", "novu", "aglta", "crying", "yenmaadu", "gottilla",
    "bayaagide", "preoccupied", "tension", "problem aagide",
]

KANNADA_ANGER = [
    "swaami", "yeno maadtira", "kelsa aagilla", "bekku", "ashtu dina",
    "yaaradru keli", "nimage gottagalla", "yenu use illa", "waste",
    "kerage keli", "swalpa keliri", "kopa bandide",
]

KANNADA_URGENCY = [
    "turant", "bega", "emergency", "immediately", "urgent",
    "life threatening", "ambulance", "hospital", "accident",
    "fire", "beele bittide", "praana", "saavu",
]

KANNADA_CONFUSION = [
    "gottilla", "artha aagilla", "yenu maadodu", "confuse",
    "yelli hogodu", "yaarige kelbeku", "namge tiliyadu",
    "form yelli", "application yelli", "where", "how to",
]

KANNADA_FEAR = [
    "bhaya", "bayaagide", "scared", "threatening",
    "danger", "risk", "worried", "tensionalli",
]

KANNADA_CALM = [
    "dhanyavaada", "thanks", "okay", "sari", "houdu",
    "good", "fine", "nanage ondu vishaya", "kelbekittu",
]

# Hindi emotional keywords
HINDI_DISTRESS = [
    "madad", "kripaya", "sahayata", "taklif", "bahut mushkil",
    "pareshaan", "ro raha", "kya karu", "samajh nahi",
]

HINDI_ANGER = [
    "kya kar rahe", "kaam nahi", "kitne din", "koi sunata nahi",
    "bekaar", "gussa", "complaint", "action lo",
]

HINDI_URGENCY = [
    "turant", "jaldi", "emergency", "ambulance", "abhi",
    "zindagi ka sawaal", "bahut zaruri", "fauran",
]

# English emotional keywords
ENGLISH_DISTRESS = [
    "help", "please", "suffering", "desperate", "no one listens",
    "don't know what to do", "struggling", "crying",
]

ENGLISH_ANGER = [
    "useless", "nothing done", "how many days", "waste of time",
    "incompetent", "fed up", "ridiculous", "pathetic",
]

ENGLISH_URGENCY = [
    "urgent", "emergency", "immediately", "life threatening",
    "right now", "asap", "critical", "ambulance",
]


# ─── Scoring Engine ─────────────────────────────────────────────────────────

def _score_keywords(text: str, keyword_lists: dict) -> dict:
    """Score text against multiple keyword lists. Returns {category: score}."""
    text_lower = text.lower()
    scores = {}
    for category, keywords in keyword_lists.items():
        count = 0
        for kw in keywords:
            if kw.lower() in text_lower:
                count += 1
        if count > 0:
            scores[category] = min(count / max(len(keywords) * 0.3, 1), 1.0)
    return scores


def _detect_exclamation_intensity(text: str) -> float:
    """Detect emotional intensity from punctuation and capitalization."""
    excl_count = text.count("!")
    caps_words = len(re.findall(r"\b[A-Z]{2,}\b", text))
    repeat_chars = len(re.findall(r"(.)\1{2,}", text))  # e.g., "pleeease", "nooo"
    intensity = min((excl_count * 0.15 + caps_words * 0.1 + repeat_chars * 0.1), 1.0)
    return intensity


def _detect_repetition_stress(text: str) -> float:
    """Detect stress from word repetition (e.g., 'please please please')."""
    words = text.lower().split()
    if len(words) < 2:
        return 0.0
    repeated = 0
    for i in range(1, len(words)):
        if words[i] == words[i - 1]:
            repeated += 1
    return min(repeated * 0.2, 0.6)


# ─── Main Classifier ────────────────────────────────────────────────────────

def classify_sentiment(
    text: str,
    language: str = "kannada",
    simulate_acoustic: bool = True,
) -> SentimentResult:
    """
    Classify sentiment from transcribed text.
    
    Args:
        text: Transcribed citizen speech
        language: Detected language
        simulate_acoustic: Whether to simulate acoustic channel
    
    Returns:
        SentimentResult with category, confidence, urgency flag, and display label
    """

    # Build keyword bank based on language
    keyword_banks = {}

    if language in ("kannada", "kannada-hindi", "kannada-english"):
        keyword_banks.update({
            SentimentCategory.DISTRESS: KANNADA_DISTRESS,
            SentimentCategory.ANGER: KANNADA_ANGER,
            SentimentCategory.URGENCY: KANNADA_URGENCY,
            SentimentCategory.CONFUSION: KANNADA_CONFUSION,
            SentimentCategory.FEAR: KANNADA_FEAR,
            SentimentCategory.CALM: KANNADA_CALM,
        })

    if language in ("hindi", "kannada-hindi"):
        keyword_banks.update({
            SentimentCategory.DISTRESS: keyword_banks.get(SentimentCategory.DISTRESS, []) + HINDI_DISTRESS,
            SentimentCategory.ANGER: keyword_banks.get(SentimentCategory.ANGER, []) + HINDI_ANGER,
            SentimentCategory.URGENCY: keyword_banks.get(SentimentCategory.URGENCY, []) + HINDI_URGENCY,
        })

    if language in ("english", "kannada-english"):
        keyword_banks.update({
            SentimentCategory.DISTRESS: keyword_banks.get(SentimentCategory.DISTRESS, []) + ENGLISH_DISTRESS,
            SentimentCategory.ANGER: keyword_banks.get(SentimentCategory.ANGER, []) + ENGLISH_ANGER,
            SentimentCategory.URGENCY: keyword_banks.get(SentimentCategory.URGENCY, []) + ENGLISH_URGENCY,
        })

    # Score each category
    scores = _score_keywords(text, keyword_banks)

    # Add intensity modifiers
    intensity = _detect_exclamation_intensity(text)
    repetition = _detect_repetition_stress(text)

    # Boost top scores with intensity
    for cat in scores:
        if cat in (SentimentCategory.DISTRESS, SentimentCategory.ANGER, SentimentCategory.URGENCY):
            scores[cat] = min(scores[cat] + intensity * 0.3 + repetition * 0.2, 1.0)

    # Determine lexical sentiment
    if scores:
        lexical_category = max(scores, key=scores.get)
        lexical_confidence = scores[lexical_category]
    else:
        lexical_category = SentimentCategory.NEUTRAL
        lexical_confidence = 0.5

    # Simulate acoustic channel
    acoustic_category = None
    if simulate_acoustic:
        # In production, this would come from Wav2Vec2 on raw audio
        # We simulate by slightly varying the lexical result
        acoustic_category = lexical_category
        if intensity > 0.4:
            acoustic_category = SentimentCategory.DISTRESS

    # Fuse channels
    final_category = lexical_category
    final_confidence = lexical_confidence

    if acoustic_category and acoustic_category != lexical_category:
        # If acoustic detects higher distress, escalate
        distress_priority = [
            SentimentCategory.URGENCY, SentimentCategory.DISTRESS,
            SentimentCategory.FEAR, SentimentCategory.ANGER,
        ]
        if acoustic_category in distress_priority:
            a_idx = distress_priority.index(acoustic_category) if acoustic_category in distress_priority else 99
            l_idx = distress_priority.index(lexical_category) if lexical_category in distress_priority else 99
            if a_idx < l_idx:
                final_category = acoustic_category
                final_confidence = max(final_confidence, 0.7)

    # Determine urgency flag
    urgency_flag = final_category in (SentimentCategory.URGENCY, SentimentCategory.DISTRESS) and final_confidence > 0.5
    if SentimentCategory.URGENCY in scores and scores[SentimentCategory.URGENCY] > 0.3:
        urgency_flag = True

    # Generate display label
    display_labels = {
        SentimentCategory.DISTRESS: "⚠️ Citizen appears distressed",
        SentimentCategory.ANGER: "🔴 Citizen sounds angry",
        SentimentCategory.FEAR: "😰 Citizen appears fearful",
        SentimentCategory.CONFUSION: "🤔 Citizen sounds confused",
        SentimentCategory.URGENCY: "🚨 URGENT — Citizen reports emergency",
        SentimentCategory.CALM: "🟢 Citizen appears calm",
        SentimentCategory.NEUTRAL: "⚪ Neutral tone detected",
    }

    return SentimentResult(
        category=final_category,
        confidence=round(final_confidence, 3),
        urgency_flag=urgency_flag,
        acoustic_sentiment=acoustic_category,
        lexical_sentiment=lexical_category,
        display_label=display_labels.get(final_category, "⚪ Neutral tone detected"),
    )
