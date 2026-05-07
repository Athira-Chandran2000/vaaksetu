"""
VaakSetu — Pydantic Data Models
All core data structures for the AI pipeline, call sessions, and agent interface.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime
from enum import Enum
import uuid


# ─── Enums ───────────────────────────────────────────────────────────────────

class Language(str, Enum):
    KANNADA = "kannada"
    HINDI = "hindi"
    ENGLISH = "english"
    KANNADA_HINDI = "kannada-hindi"
    KANNADA_ENGLISH = "kannada-english"


class KannadaDialect(str, Enum):
    STANDARD = "standard"
    DHARWAD = "dharwad"
    MYSURU = "mysuru"
    MANGALURU = "mangaluru"
    HAVYAKA = "havyaka"
    NORTH_KARNATAKA = "north-karnataka"
    UNKNOWN = "unknown"


class SentimentCategory(str, Enum):
    DISTRESS = "distress"
    ANGER = "anger"
    FEAR = "fear"
    CONFUSION = "confusion"
    URGENCY = "urgency"
    CALM = "calm"
    NEUTRAL = "neutral"


class VerificationStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    INCORRECT = "incorrect"
    PARTIAL = "partial"
    UNCERTAIN = "uncertain"
    SKIPPED = "skipped"
    ESCALATED = "escalated"


class CallStatus(str, Enum):
    ACTIVE = "active"
    VERIFIED = "verified"
    ESCALATED = "escalated"
    COMPLETED = "completed"
    TAKEOVER = "takeover"


class EscalationReason(str, Enum):
    VERIFICATION_FAILED = "verification_failed"
    HIGH_DISTRESS = "high_distress"
    LOW_ASR_CONFIDENCE = "low_asr_confidence"
    AGENT_TAKEOVER = "agent_takeover"
    MULTIPLE_RETRIES = "multiple_retries"


# ─── ASR Result ──────────────────────────────────────────────────────────────

class ASRResult(BaseModel):
    transcript: str
    language_detected: Language = Language.KANNADA
    dialect_detected: KannadaDialect = KannadaDialect.STANDARD
    confidence: float = Field(ge=0.0, le=1.0, default=0.85)
    duration_seconds: float = 0.0
    segments: List[dict] = Field(default_factory=list)


# ─── Sentiment Result ────────────────────────────────────────────────────────

class SentimentResult(BaseModel):
    category: SentimentCategory = SentimentCategory.NEUTRAL
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    urgency_flag: bool = False
    acoustic_sentiment: Optional[SentimentCategory] = None
    lexical_sentiment: Optional[SentimentCategory] = None
    display_label: str = "Citizen appears calm"


# ─── Extracted Entities ──────────────────────────────────────────────────────

class ExtractedEntities(BaseModel):
    location: Optional[str] = None
    department: Optional[str] = None
    service_name: Optional[str] = None
    person_name: Optional[str] = None
    id_number: Optional[str] = None
    event_description: Optional[str] = None
    date_mentioned: Optional[str] = None


# ─── Interpretation Card ─────────────────────────────────────────────────────

class InterpretationCard(BaseModel):
    core_issue: str = ""
    native_core_issue: Optional[str] = None  # Issue in citizen's spoken language
    detected_language: Optional[Language] = None
    category: str = ""
    intent: str = ""
    entities: ExtractedEntities = Field(default_factory=ExtractedEntities)
    enrichment_context: List[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    raw_interpretation: str = ""
    suggested_solution: Optional[str] = None


# ─── Verification Loop ──────────────────────────────────────────────────────

class VerificationResult(BaseModel):
    status: VerificationStatus = VerificationStatus.PENDING
    restatement_text: str = ""
    restatement_language: Language = Language.KANNADA
    citizen_response: str = ""
    attempt_number: int = 0
    max_attempts: int = 2


# ─── Call Session ────────────────────────────────────────────────────────────

class CallSession(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    started_at: datetime = Field(default_factory=datetime.utcnow)
    status: CallStatus = CallStatus.ACTIVE
    language: Language = Language.KANNADA
    dialect: KannadaDialect = KannadaDialect.STANDARD

    # Pipeline outputs
    asr_result: Optional[ASRResult] = None
    interpretation: Optional[InterpretationCard] = None
    sentiment: Optional[SentimentResult] = None
    verification: Optional[VerificationResult] = None

    # Escalation
    escalation_reason: Optional[EscalationReason] = None
    escalation_notes: str = ""
    suggested_solution: Optional[str] = None

    # Agent actions
    agent_correction: Optional[str] = None
    agent_notes: str = ""

    # Metadata
    transcript_history: List[str] = Field(default_factory=list)
    verification_attempts: int = 0


# ─── API Request / Response Models ──────────────────────────────────────────

class ProcessTextRequest(BaseModel):
    text: str
    language: Language = Language.KANNADA
    dialect: KannadaDialect = KannadaDialect.STANDARD
    session_id: Optional[str] = None


class ProcessTextResponse(BaseModel):
    session_id: str
    status: CallStatus = CallStatus.ACTIVE
    asr_result: ASRResult
    interpretation: InterpretationCard
    sentiment: SentimentResult
    verification: VerificationResult
    enrichment_data: dict = Field(default_factory=dict)
    should_escalate: bool = False
    escalation_reason: Optional[str] = None


class VerifyRequest(BaseModel):
    session_id: str
    citizen_response: str


class AgentCorrectionRequest(BaseModel):
    session_id: str
    corrected_interpretation: str
    agent_notes: str = ""


class AgentTakeoverRequest(BaseModel):
    session_id: str
    reason: str = ""


class CRMTrendItem(BaseModel):
    category: str
    count: int
    trend: Literal["up", "down", "stable"]
    last_hour: int = 0


class DashboardState(BaseModel):
    active_calls: int = 0
    calls_today: int = 0
    avg_resolution_time: str = "4m 32s"
    escalation_rate: float = 0.12
    top_issues: List[CRMTrendItem] = Field(default_factory=list)
    recent_sessions: List[dict] = Field(default_factory=list)
