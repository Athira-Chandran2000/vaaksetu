"""
VaakSetu — FastAPI Backend
Main application with WebSocket endpoints for real-time call processing
and REST endpoints for agent actions.
"""

import os
import json
import uuid
import logging
import asyncio
from datetime import datetime
from typing import Dict, Optional
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from models import (
    CallSession, CallStatus, EscalationReason,
    Language, KannadaDialect, VerificationStatus,
    ProcessTextRequest, ProcessTextResponse,
    VerifyRequest, AgentCorrectionRequest, AgentTakeoverRequest,
)
from ai_pipeline import run_pipeline, classify_verification_response, generate_restatement
from sentiment import classify_sentiment
from mock_integrations import (
    get_crm_trends, generate_crm_call_logs, enrich_context,
    get_seva_sindhu_services, get_bbmp_grievances, get_bbmp_trending,
    get_bwssb_status, get_bwssb_outages,
    search_bhoomi, search_ration_card, search_pension,
)

# ─── Logging Setup ──────────────────────────────────────────────────────────

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vaaksetu")

# ─── In-Memory State ────────────────────────────────────────────────────────

sessions: Dict[str, CallSession] = {}
feedback_store: list = []  # Stores corrections/confirmations for learning
connected_agents: Dict[str, WebSocket] = {}

# ─── App Lifecycle ──────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 VaakSetu backend starting...")
    logger.info(f"   Groq API key    : {'Yes ✅' if os.getenv('GROQ_API_KEY') else 'No ⚠️  — set GROQ_API_KEY'}")
    logger.info(f"   Sarvam AI (ASR) : {'Yes ✅' if os.getenv('SARVAM_API_KEY') else 'No ⚠️  — set SARVAM_API_KEY (audio will be demo-only)'}")
    yield
    logger.info("🛑 VaakSetu backend shutting down.")


# ─── FastAPI App ─────────────────────────────────────────────────────────────

app = FastAPI(
    title="VaakSetu API",
    description="AI-Assisted Voice Understanding for the Karnataka 1092 Helpline",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── REST Endpoints ─────────────────────────────────────────────────────────

# The root "/" will be handled by the serve_frontend catch-all at the end of the file.


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


# ─── Process Text Input ─────────────────────────────────────────────────────

@app.post("/api/process-text", response_model=ProcessTextResponse)
async def process_text(request: ProcessTextRequest):
    """
    Process citizen text input through the full VaakSetu pipeline.
    This is the primary endpoint for the demo — simulates ASR from text.
    """
    session_id = request.session_id or str(uuid.uuid4())

    # Create or get session
    if session_id not in sessions:
        sessions[session_id] = CallSession(session_id=session_id)

    session = sessions[session_id]
    session.language = request.language
    session.dialect = request.dialect
    session.transcript_history.append(request.text)

    # Run the full pipeline
    try:
        result = run_pipeline(
            text=request.text,
            language=request.language,
            dialect=request.dialect,
        )
    except RuntimeError as e:
        # Groq key not set — return a mock result for demo
        logger.warning(f"Pipeline error (likely no API key): {e}")
        return _generate_mock_pipeline_response(session_id, request.text, request.language)

    # Update session
    session.language = result.get("active_language", session.language)
    session.asr_result = result["asr_result"]
    session.interpretation = result["interpretation"]
    session.sentiment = result["sentiment"]
    session.verification = result["verification"]
    session.suggested_solution = result["interpretation"].suggested_solution

    if result["should_escalate"]:
        session.status = CallStatus.ESCALATED
        session.escalation_reason = EscalationReason.HIGH_DISTRESS
        session.escalation_notes = result["escalation_reason"] or ""

    # Broadcast to connected agent dashboards
    await broadcast_to_agents({
        "type": "call_update",
        "session_id": session_id,
        "data": _session_to_dict(session),
    })

    return ProcessTextResponse(
        session_id=session_id,
        status=session.status,
        asr_result=result["asr_result"],
        interpretation=result["interpretation"],
        sentiment=result["sentiment"],
        verification=result["verification"],
        enrichment_data=_sanitize_enrichment(result["enrichment_data"]),
        should_escalate=result["should_escalate"],
        escalation_reason=result["escalation_reason"],
    )


# ─── Process Audio Upload ───────────────────────────────────────────────────

@app.post("/api/process-audio")
async def process_audio(
    audio: UploadFile = File(...),
    session_id: Optional[str] = None,
    language: str = "kannada",
    dialect: str = "standard",
):
    """Process audio file through the full VaakSetu pipeline using Sarvam AI ASR."""
    sid = session_id or str(uuid.uuid4())

    if sid not in sessions:
        sessions[sid] = CallSession(session_id=sid)

    session = sessions[sid]
    audio_bytes = await audio.read()
    filename = audio.filename or ""

    try:
        result = run_pipeline(
            text="",
            language=Language(language),
            dialect=KannadaDialect(dialect),
            audio_bytes=audio_bytes,
            audio_filename=filename,
        )
    except RuntimeError as e:
        logger.warning(f"Pipeline error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    session.language = result.get("active_language", session.language)
    session.asr_result = result["asr_result"]
    session.interpretation = result["interpretation"]
    session.sentiment = result["sentiment"]
    session.verification = result["verification"]
    session.suggested_solution = result["interpretation"].suggested_solution

    if result["should_escalate"]:
        session.status = CallStatus.ESCALATED

    await broadcast_to_agents({
        "type": "call_update",
        "session_id": sid,
        "data": _session_to_dict(session),
    })

    return {
        "session_id": sid,
        "status": session.status.value,
        "asr_result": result["asr_result"].model_dump(),
        "interpretation": result["interpretation"].model_dump(),
        "sentiment": result["sentiment"].model_dump(),
        "verification": result["verification"].model_dump(),
        "enrichment_data": _sanitize_enrichment(result["enrichment_data"]),
        "should_escalate": result["should_escalate"],
        "escalation_reason": result["escalation_reason"],
    }


# ─── Verification Loop ──────────────────────────────────────────────────────

@app.post("/api/verify")
async def verify_response(request: VerifyRequest):
    """Process the citizen's response to the verification restatement."""
    session = sessions.get(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Classify the response
    status = classify_verification_response(request.citizen_response)
    session.verification_attempts += 1

    if session.verification:
        session.verification.status = status
        session.verification.citizen_response = request.citizen_response
        session.verification.attempt_number = session.verification_attempts

    # Update session status based on verification result
    action = ""
    if status == VerificationStatus.CONFIRMED:
        session.status = CallStatus.VERIFIED
        action = "proceed"
    elif status == VerificationStatus.INCORRECT:
        if session.verification_attempts >= 2:
            session.status = CallStatus.ESCALATED
            session.escalation_reason = EscalationReason.VERIFICATION_FAILED
            action = "escalate"
        else:
            action = "retry"
    elif status == VerificationStatus.PARTIAL:
        action = "retry_with_correction"
    elif status == VerificationStatus.UNCERTAIN:
        if session.verification_attempts >= 2:
            session.status = CallStatus.ESCALATED
            session.escalation_reason = EscalationReason.MULTIPLE_RETRIES
            action = "escalate"
        else:
            action = "retry"

    response_data = {
        "session_id": request.session_id,
        "status": session.status.value,
        "verification_status": status.value,
        "attempt_number": session.verification_attempts,
        "action": action,
        "suggested_solution": session.suggested_solution,
    }

    if status == VerificationStatus.CONFIRMED:
        # Store as positive training example
        feedback_store.append({
            "type": "confirmed",
            "session_id": request.session_id,
            "transcript": session.transcript_history,
            "interpretation": session.interpretation.model_dump() if session.interpretation else None,
            "timestamp": datetime.utcnow().isoformat(),
        })
    elif status == VerificationStatus.INCORRECT and action == "retry":
        # Generate new restatement with open prompt
        if session.interpretation:
            new_restatement = generate_restatement(session.interpretation, session.language)
            response_data["new_restatement"] = new_restatement
    elif status == VerificationStatus.PARTIAL:
        response_data["citizen_correction"] = request.citizen_response

    await broadcast_to_agents({
        "type": "verification_update",
        "session_id": request.session_id,
        "data": response_data,
    })

    return response_data


# ─── Agent Actions ───────────────────────────────────────────────────────────

@app.post("/api/agent/correction")
async def agent_correction(request: AgentCorrectionRequest):
    """Agent corrects an AI interpretation — highest quality training signal."""
    session = sessions.get(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.agent_correction = request.corrected_interpretation
    session.agent_notes = request.agent_notes

    # Store as high-priority training example
    feedback_store.append({
        "type": "agent_correction",
        "priority": "high",
        "session_id": request.session_id,
        "original_interpretation": session.interpretation.model_dump() if session.interpretation else None,
        "corrected_interpretation": request.corrected_interpretation,
        "agent_notes": request.agent_notes,
        "transcript": session.transcript_history,
        "timestamp": datetime.utcnow().isoformat(),
    })

    logger.info(f"Agent correction stored for session {request.session_id}")

    return {
        "status": "correction_saved",
        "session_id": request.session_id,
        "feedback_count": len(feedback_store),
    }


@app.post("/api/agent/takeover")
async def agent_takeover(request: AgentTakeoverRequest):
    """Agent manually takes over the call."""
    session = sessions.get(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.status = CallStatus.TAKEOVER
    session.escalation_reason = EscalationReason.AGENT_TAKEOVER
    session.escalation_notes = request.reason

    await broadcast_to_agents({
        "type": "takeover",
        "session_id": request.session_id,
        "reason": request.reason,
        "context": _session_to_dict(session),
    })

    return {
        "status": "takeover_activated",
        "session_id": request.session_id,
        "context": _session_to_dict(session),
    }


# ─── Data Endpoints ─────────────────────────────────────────────────────────

@app.get("/api/crm-trends")
async def crm_trends():
    """Get real-time CRM trend data for the dashboard."""
    return get_crm_trends()


@app.get("/api/crm-logs")
async def crm_logs(count: int = 30):
    """Get simulated 1092 CRM call logs."""
    return generate_crm_call_logs(count)


@app.get("/api/sessions")
async def list_sessions():
    """List all active call sessions."""
    return {
        "active_sessions": len(sessions),
        "sessions": [_session_to_dict(s) for s in sessions.values()],
    }


@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """Get a specific session's full state."""
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return _session_to_dict(session)


@app.get("/api/feedback-store")
async def get_feedback_store():
    """Get all stored feedback (for continuous learning demo)."""
    return {
        "total_entries": len(feedback_store),
        "entries": feedback_store[-50:],  # Last 50
    }


@app.get("/api/real-time-data")
async def get_real_time_data():
    """Get all real-time government data feeds for the dashboard panel."""
    return {
        "seva_sindhu": get_seva_sindhu_services(),
        "bbmp_trending": get_bbmp_trending(),
        "bbmp_grievances": get_bbmp_grievances(),
        "bwssb_status": get_bwssb_status(),
        "bwssb_outages": get_bwssb_outages(),
        "bhoomi_sample": search_bhoomi(),
        "ration_card_sample": search_ration_card(),
        "pension_sample": search_pension(),
        "crm_trends": get_crm_trends(),
    }


# ─── WebSocket: Agent Dashboard ─────────────────────────────────────────────

@app.websocket("/ws/agent/{agent_id}")
async def agent_websocket(websocket: WebSocket, agent_id: str):
    """WebSocket endpoint for real-time agent dashboard updates."""
    await websocket.accept()
    connected_agents[agent_id] = websocket
    logger.info(f"Agent {agent_id} connected via WebSocket")

    # Send initial state
    await websocket.send_json({
        "type": "initial_state",
        "active_sessions": [_session_to_dict(s) for s in sessions.values()],
        "crm_trends": get_crm_trends(),
    })

    try:
        while True:
            # Keep connection alive and listen for agent messages
            data = await websocket.receive_text()
            msg = json.loads(data)

            if msg.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
            elif msg.get("type") == "request_trends":
                await websocket.send_json({
                    "type": "crm_trends",
                    "data": get_crm_trends(),
                })

    except WebSocketDisconnect:
        logger.info(f"Agent {agent_id} disconnected")
        connected_agents.pop(agent_id, None)
    except Exception as e:
        logger.error(f"WebSocket error for agent {agent_id}: {e}")
        connected_agents.pop(agent_id, None)


# ─── WebSocket: Call Simulation ──────────────────────────────────────────────

@app.websocket("/ws/call/{session_id}")
async def call_websocket(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time call simulation and processing."""
    await websocket.accept()
    logger.info(f"Call WebSocket connected for session {session_id}")

    if session_id not in sessions:
        sessions[session_id] = CallSession(session_id=session_id)

    session = sessions[session_id]

    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)

            if msg.get("type") == "text_input":
                # Process text through pipeline
                text = msg.get("text", "")
                language = Language(msg.get("language", "kannada"))
                dialect = KannadaDialect(msg.get("dialect", "standard"))

                session.transcript_history.append(text)

                try:
                    result = run_pipeline(text=text, language=language, dialect=dialect)
                except RuntimeError:
                    result = _generate_mock_result(text, language)

                session.language = result.get("active_language", session.language)
                session.asr_result = result["asr_result"]
                session.interpretation = result["interpretation"]
                session.sentiment = result["sentiment"]
                session.verification = result["verification"]
                session.suggested_solution = result["interpretation"].suggested_solution

                await websocket.send_json({
                    "type": "pipeline_result",
                    "data": {
                        "asr_result": result["asr_result"].model_dump(),
                        "interpretation": result["interpretation"].model_dump(),
                        "sentiment": result["sentiment"].model_dump(),
                        "verification": result["verification"].model_dump(),
                        "enrichment_data": _sanitize_enrichment(result["enrichment_data"]),
                        "should_escalate": result["should_escalate"],
                        "escalation_reason": result["escalation_reason"],
                    },
                })

                await broadcast_to_agents({
                    "type": "call_update",
                    "session_id": session_id,
                    "data": _session_to_dict(session),
                })

            elif msg.get("type") == "verification_response":
                citizen_response = msg.get("response", "")
                status = classify_verification_response(citizen_response)
                session.verification_attempts += 1

                await websocket.send_json({
                    "type": "verification_result",
                    "status": status.value,
                    "attempt": session.verification_attempts,
                })

    except WebSocketDisconnect:
        logger.info(f"Call WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"Call WebSocket error: {e}")


# ─── Helpers ─────────────────────────────────────────────────────────────────

async def broadcast_to_agents(message: dict):
    """Broadcast a message to all connected agent dashboards."""
    disconnected = []
    for agent_id, ws in connected_agents.items():
        try:
            await ws.send_json(message)
        except Exception:
            disconnected.append(agent_id)
    for aid in disconnected:
        connected_agents.pop(aid, None)


def _session_to_dict(session: CallSession) -> dict:
    """Convert a session to a JSON-serializable dict."""
    return {
        "session_id": session.session_id,
        "started_at": session.started_at.isoformat(),
        "status": session.status.value,
        "language": session.language.value,
        "dialect": session.dialect.value,
        "asr_result": session.asr_result.model_dump() if session.asr_result else None,
        "interpretation": session.interpretation.model_dump() if session.interpretation else None,
        "sentiment": session.sentiment.model_dump() if session.sentiment else None,
        "verification": session.verification.model_dump() if session.verification else None,
        "escalation_reason": session.escalation_reason.value if session.escalation_reason else None,
        "escalation_notes": session.escalation_notes,
        "agent_correction": session.agent_correction,
        "agent_notes": session.agent_notes,
        "transcript_history": session.transcript_history,
        "verification_attempts": session.verification_attempts,
        "suggested_solution": session.suggested_solution,
    }


def _sanitize_enrichment(data: dict) -> dict:
    """Sanitize enrichment data for JSON serialization — keep only summaries."""
    safe = {}
    for key, val in data.items():
        if key == "crm_trends":
            # Summarise top categories only
            cats = val.get("top_categories", []) if isinstance(val, dict) else []
            safe["crm_trends"] = {
                "total_calls_today": val.get("total_calls_today", 0) if isinstance(val, dict) else 0,
                "top_categories": cats[:5],
            }
        elif key == "alerts":
            safe["alerts"] = val
        elif isinstance(val, list):
            safe[key] = val[:3]  # Limit to 3 items per source
        else:
            safe[key] = val
    return safe


def _generate_mock_pipeline_response(session_id: str, text: str, language: Language) -> ProcessTextResponse:
    """Generate a mock pipeline response when Groq API is not available."""
    from models import ASRResult, InterpretationCard, SentimentResult, VerificationResult, ExtractedEntities

    sentiment = classify_sentiment(text, language.value)

    return ProcessTextResponse(
        session_id=session_id,
        status=CallStatus.ACTIVE,
        asr_result=ASRResult(
            transcript=text,
            language_detected=language,
            confidence=0.92,
        ),
        interpretation=InterpretationCard(
            core_issue=f"Citizen reported: {text[:100]}",
            native_core_issue=text if language != Language.ENGLISH else None,
            detected_language=language,
            category="General Inquiry",
            intent="complaint",
            entities=ExtractedEntities(),
            confidence=0.75,
            raw_interpretation=(
                f"[Demo mode — set GROQ_API_KEY for real AI analysis] "
                f"Citizen input: {text}"
            ),
            suggested_solution=(
                "ನಮ್ಮ ತಂಡವು ಇದನ್ನು ತಕ್ಷಣ ಗಮನಿಸುತ್ತದೆ. ದಯವಿಟ್ಟು ನಿಮ್ಮ ಉಲ್ಲೇಖ ಸಂಖ್ಯೆಯನ್ನು ಸಿದ್ಧವಾಗಿಡಿ." if language == Language.KANNADA else
                "हमारी टीम तुरंत इस पर गौर करेगी। कृपया अपना संदर्भ नंबर तैयार रखें।" if language == Language.HINDI else
                "Our team will look into this immediately. Please keep your reference number ready."
            ),
        ),
        sentiment=sentiment,
        verification=VerificationResult(
            status=VerificationStatus.PENDING,
            restatement_text=f"You said: {text[:80]}... Is that correct?",
            restatement_language=language,
        ),
        enrichment_data=_sanitize_enrichment(enrich_context(text)),
        should_escalate=sentiment.urgency_flag,
        escalation_reason="High distress detected" if sentiment.urgency_flag else None,
    )


def _generate_mock_result(text: str, language: Language) -> dict:
    """Generate mock pipeline result dict when API is unavailable."""
    from models import ASRResult, InterpretationCard, SentimentResult, VerificationResult, ExtractedEntities

    sentiment = classify_sentiment(text, language.value)

    return {
        "asr_result": ASRResult(transcript=text, language_detected=language, confidence=0.90),
        "interpretation": InterpretationCard(
            core_issue=f"Citizen reported: {text[:100]}",
            native_core_issue=text if language != Language.ENGLISH else None,
            detected_language=language,
            category="General Inquiry",
            intent="complaint",
            entities=ExtractedEntities(),
            confidence=0.70,
            raw_interpretation=f"[Mock] {text}",
            suggested_solution=(
                "ನಮ್ಮ ತಂಡವು ಇದನ್ನು ತಕ್ಷಣ ಗಮನಿಸುತ್ತದೆ. ದಯವಿಟ್ಟು ನಿಮ್ಮ ಉಲ್ಲೇಖ ಸಂಖ್ಯೆಯನ್ನು ಸಿದ್ಧವಾಗಿಡಿ." if language == Language.KANNADA else
                "हमारी टीम तुरंत इस पर गौर करेगी। कृपया अपना संदर्भ नंबर तैयार रखें।" if language == Language.HINDI else
                "Our team will look into this immediately. Please keep your reference number ready."
            ),
        ),
        "sentiment": sentiment,
        "verification": VerificationResult(
            status=VerificationStatus.PENDING,
            restatement_text=f"You said: {text[:80]}... Is that correct?",
            restatement_language=language,
        ),
        "enrichment_data": enrich_context(text),
        "should_escalate": sentiment.urgency_flag,
        "escalation_reason": "High distress" if sentiment.urgency_flag else None,
    }


# ─── Serve Frontend ──────────────────────────────────────────────────────────

# Mount the static files directory (built React app)
# Note: In production, the 'frontend/dist' folder should exist
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")

if os.path.exists(frontend_path):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_path, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # Serve index.html for any route not handled by the API (SPA support)
        if full_path.startswith("api/") or full_path.startswith("ws/"):
            raise HTTPException(status_code=404, detail="API route not found")
        
        index_file = os.path.join(frontend_path, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {"error": "Frontend build not found. Run 'npm run build' in frontend directory."}
else:
    logger.warning(f"Frontend build directory not found at {frontend_path}. API only mode.")


# ─── Run ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
