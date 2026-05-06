import React, { useState, useCallback } from 'react';
import CallInterface from './CallInterface';
import InterpretationCard from './InterpretationCard';
import SentimentBadge from './SentimentBadge';
import VerificationLoop from './VerificationLoop';
import SolutionCard from './SolutionCard';
import RealTimeDataPanel from './RealTimeDataPanel';
import CRMTrends from './CRMTrends';
import './AgentDashboard.css';

/**
 * AgentDashboard — Main agent workspace showing the complete VaakSetu pipeline.
 */

const API_BASE = '/api';

export default function AgentDashboard() {
  // Pipeline state
  const [pipelineResult, setPipelineResult] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState(null);
  const [transcriptHistory, setTranscriptHistory] = useState([]);

  // Agent actions
  const [correctionText, setCorrectionText] = useState('');
  const [correctionNotes, setCorrectionNotes] = useState('');
  const [showCorrectionForm, setShowCorrectionForm] = useState(false);

  // CRM trends
  const [crmTrends, setCrmTrends] = useState(null);
  const [feedbackLog, setFeedbackLog] = useState([]);

  // ─── Process Text ──────────────────────────────────────────────────

  const handleSubmitText = useCallback(async (text, language, dialect) => {
    setIsProcessing(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/process-text`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, language, dialect }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();
      setPipelineResult(data);
      setTranscriptHistory(prev => [...prev, { text, language, timestamp: new Date().toISOString() }]);

      // Auto-fetch CRM trends
      fetchCRMTrends();

    } catch (err) {
      setError(err.message);
      console.error('Pipeline error:', err);
    } finally {
      setIsProcessing(false);
    }
  }, []);

  // ─── Process Audio ─────────────────────────────────────────────────

  const handleSubmitAudio = useCallback(async (audioBlob, language, dialect) => {
    setIsProcessing(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.webm');
      formData.append('language', language);
      formData.append('dialect', dialect);

      const response = await fetch(`${API_BASE}/process-audio`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();
      setPipelineResult(data);
      setTranscriptHistory(prev => [...prev, {
        text: data.asr_result?.transcript || '[Audio]',
        language,
        timestamp: new Date().toISOString(),
        source: 'audio',
      }]);

      fetchCRMTrends();

    } catch (err) {
      setError(err.message);
    } finally {
      setIsProcessing(false);
    }
  }, []);

  // ─── Verification ──────────────────────────────────────────────────

  const handleVerify = useCallback(async (citizenResponse) => {
    if (!pipelineResult?.session_id) return;

    try {
      const response = await fetch(`${API_BASE}/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: pipelineResult.session_id,
          citizen_response: citizenResponse,
        }),
      });

      const data = await response.json();

      setPipelineResult(prev => ({
        ...prev,
        status: data.status,
        verification: {
          ...prev.verification,
          status: data.verification_status,
          citizen_response: citizenResponse,
          attempt_number: data.attempt_number,
        },
        interpretation: {
          ...prev.interpretation,
          suggested_solution: data.suggested_solution || prev.interpretation?.suggested_solution
        }
      }));

      setFeedbackLog(prev => [...prev, {
        type: 'verification',
        status: data.verification_status,
        response: citizenResponse,
        timestamp: new Date().toISOString(),
      }]);

    } catch (err) {
      setError(err.message);
    }
  }, [pipelineResult]);

  // ─── Agent Correction ──────────────────────────────────────────────

  const handleCorrection = useCallback(async () => {
    if (!pipelineResult?.session_id || !correctionText.trim()) return;

    try {
      const response = await fetch(`${API_BASE}/agent/correction`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: pipelineResult.session_id,
          corrected_interpretation: correctionText,
          agent_notes: correctionNotes,
        }),
      });

      const data = await response.json();

      setFeedbackLog(prev => [...prev, {
        type: 'correction',
        correction: correctionText,
        timestamp: new Date().toISOString(),
      }]);

      setShowCorrectionForm(false);
      setCorrectionText('');
      setCorrectionNotes('');
      alert('✅ Correction saved to feedback store for retraining!');

    } catch (err) {
      setError(err.message);
    }
  }, [pipelineResult, correctionText, correctionNotes]);

  // ─── Agent Takeover ────────────────────────────────────────────────

  const handleTakeover = useCallback(async () => {
    if (!pipelineResult?.session_id) return;

    try {
      const response = await fetch(`${API_BASE}/agent/takeover`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: pipelineResult.session_id,
          reason: 'Agent manual takeover',
        }),
      });

      const data = await response.json();

      setPipelineResult(prev => ({
        ...prev,
        should_escalate: true,
        escalation_reason: 'Agent took over the call manually',
      }));

      setFeedbackLog(prev => [...prev, {
        type: 'takeover',
        timestamp: new Date().toISOString(),
      }]);

    } catch (err) {
      setError(err.message);
    }
  }, [pipelineResult]);

  // ─── CRM Trends ───────────────────────────────────────────────────

  const fetchCRMTrends = async () => {
    try {
      const response = await fetch(`${API_BASE}/crm-trends`);
      const data = await response.json();
      setCrmTrends(data);
    } catch (err) {
      console.error('CRM trends fetch failed:', err);
    }
  };

  return (
    <div className="agent-dashboard">
      {/* Top Bar */}
      <header className="dashboard-topbar">
        <div className="topbar-left">
          <h1 className="topbar-title">
            <span className="topbar-logo">🌉</span>
            VaakSetu
          </h1>
          <span className="topbar-subtitle">1092 AI Agent Dashboard</span>
        </div>
        <div className="topbar-right">
          {pipelineResult?.session_id && (
            <span className="session-id badge badge-accent">
              Session: {pipelineResult.session_id.slice(0, 8)}...
            </span>
          )}
          <button
            className="btn btn-danger btn-sm takeover-btn"
            onClick={handleTakeover}
            disabled={!pipelineResult?.session_id}
            id="takeover-btn"
          >
            🖐️ Human Takeover
          </button>
        </div>
      </header>

      {/* Error Banner */}
      {error && (
        <div className="error-banner animate-slide-up">
          <span>⚠️ {error}</span>
          <button className="btn btn-ghost btn-sm" onClick={() => setError(null)}>Dismiss</button>
        </div>
      )}

      {/* Escalation Banner */}
      {pipelineResult?.should_escalate && (
        <div className="escalation-banner animate-slide-up">
          <span className="escalation-icon">🔺</span>
          <span className="escalation-text">
            <strong>ESCALATION TRIGGERED</strong> — {pipelineResult.escalation_reason}
          </span>
        </div>
      )}

      {/* Main Grid */}
      <div className="dashboard-grid">
        {/* Left Column: Call Simulator */}
        <div className="dashboard-col dashboard-col-left">
          <CallInterface
            onSubmitText={handleSubmitText}
            onSubmitAudio={handleSubmitAudio}
            isProcessing={isProcessing}
          />

          {/* Transcript History */}
          {transcriptHistory.length > 0 && (
            <div className="transcript-history glass-card">
              <h4 className="transcript-title">📜 Transcript History</h4>
              <div className="transcript-list">
                {transcriptHistory.map((entry, i) => (
                  <div key={i} className="transcript-entry animate-fade-in">
                    <span className="transcript-lang badge badge-accent">{entry.language}</span>
                    <p className="transcript-text">{entry.text}</p>
                    <span className="transcript-time">
                      {new Date(entry.timestamp).toLocaleTimeString()}
                      {entry.source === 'audio' && ' 🎙️'}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Center Column: Pipeline Results */}
        <div className="dashboard-col dashboard-col-center">
          {pipelineResult ? (
            <>
              <InterpretationCard
                interpretation={pipelineResult.interpretation}
                asrResult={pipelineResult.asr_result}
              />

              <SentimentBadge sentiment={pipelineResult.sentiment} />

              <VerificationLoop
                verification={pipelineResult.verification}
                onVerify={handleVerify}
              />
              
              <SolutionCard 
                solution={pipelineResult.interpretation?.suggested_solution}
                sessionStatus={pipelineResult.status}
              />

              {/* Agent Correction */}
              <div className="agent-actions glass-card">
                <h4 className="actions-title">✏️ Agent Actions</h4>
                {!showCorrectionForm ? (
                  <div className="action-buttons">
                    <button
                      className="btn btn-ghost"
                      onClick={() => setShowCorrectionForm(true)}
                      id="correct-btn"
                    >
                      ✏️ Correct Interpretation
                    </button>
                    <button className="btn btn-success btn-sm" id="confirm-btn"
                      onClick={() => {
                        setFeedbackLog(prev => [...prev, { type: 'confirmed', timestamp: new Date().toISOString() }]);
                        alert('✅ Interpretation confirmed! Stored as positive training example.');
                      }}
                    >
                      ✅ Confirm Correct
                    </button>
                  </div>
                ) : (
                  <div className="correction-form animate-fade-in">
                    <textarea
                      className="textarea"
                      value={correctionText}
                      onChange={(e) => setCorrectionText(e.target.value)}
                      placeholder="Enter the correct interpretation..."
                      rows={3}
                      id="correction-text"
                    />
                    <input
                      type="text"
                      className="input"
                      value={correctionNotes}
                      onChange={(e) => setCorrectionNotes(e.target.value)}
                      placeholder="Agent notes (optional)"
                      id="correction-notes"
                    />
                    <div className="correction-actions">
                      <button className="btn btn-primary btn-sm" onClick={handleCorrection} id="save-correction-btn">
                        💾 Save Correction
                      </button>
                      <button className="btn btn-ghost btn-sm" onClick={() => setShowCorrectionForm(false)}>
                        Cancel
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </>
          ) : (
            <div className="empty-state glass-card">
              <div className="empty-icon">🌉</div>
              <h3>VaakSetu Ready</h3>
              <p>Submit a citizen query from the call simulator to see the AI pipeline in action.</p>
              <p className="empty-hint">Select a quick test scenario or type your own message.</p>
            </div>
          )}
        </div>

        {/* Right Column: Data Feeds & Trends */}
        <div className="dashboard-col dashboard-col-right">
          <RealTimeDataPanel enrichmentData={pipelineResult?.enrichment_data} />

          {crmTrends && <CRMTrends trends={crmTrends} />}

          {/* Feedback Log */}
          {feedbackLog.length > 0 && (
            <div className="feedback-log glass-card">
              <h4 className="feedback-title">🔄 Learning Store</h4>
              <div className="feedback-list">
                {feedbackLog.slice(-10).reverse().map((entry, i) => (
                  <div key={i} className="feedback-entry">
                    <span className={`badge ${
                      entry.type === 'confirmed' ? 'badge-success' :
                      entry.type === 'correction' ? 'badge-warning' :
                      entry.type === 'takeover' ? 'badge-danger' :
                      'badge-info'
                    }`}>
                      {entry.type}
                    </span>
                    <span className="feedback-time">
                      {new Date(entry.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                ))}
              </div>
              <div className="feedback-stats">
                <span className="feedback-stat">
                  Total: {feedbackLog.length} signals
                </span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
