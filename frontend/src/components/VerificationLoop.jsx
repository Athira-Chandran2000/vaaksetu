import React from 'react';
import './VerificationLoop.css';

/**
 * VerificationLoop — Displays the verification restatement and citizen response status.
 * Shows the current state of the verified understanding loop.
 */

const STATUS_CONFIG = {
  pending:   { icon: '⏳', label: 'Awaiting Verification', color: 'var(--color-warning)', className: 'status-pending' },
  confirmed: { icon: '✅', label: 'Verified by Citizen', color: 'var(--color-success)', className: 'status-confirmed' },
  incorrect: { icon: '❌', label: 'Citizen Rejected', color: 'var(--color-danger)', className: 'status-incorrect' },
  partial:   { icon: '🔄', label: 'Partial Correction', color: 'var(--color-info)', className: 'status-partial' },
  uncertain: { icon: '❓', label: 'Uncertain Response', color: 'var(--color-warning)', className: 'status-uncertain' },
  skipped:   { icon: '⏭️', label: 'Skipped (High Urgency)', color: 'var(--color-danger)', className: 'status-skipped' },
  escalated: { icon: '🔺', label: 'Escalated to Agent', color: 'var(--color-danger)', className: 'status-escalated' },
};

export default function VerificationLoop({ verification, onVerify }) {
  if (!verification) return null;

  const status = STATUS_CONFIG[verification.status] || STATUS_CONFIG.pending;

  return (
    <div className={`verification-loop glass-card animate-fade-in ${status.className}`}>
      <div className="verify-header">
        <h3 className="verify-title">🔄 Verification Loop</h3>
        <div className="verify-status-badge" style={{ borderColor: status.color }}>
          <span>{status.icon}</span>
          <span>{status.label}</span>
        </div>
      </div>

      {/* Restatement */}
      {verification.restatement_text && (
        <div className="restatement-box">
          <div className="restatement-label">
            <span>🗣️</span>
            <span>AI Restatement ({verification.restatement_language})</span>
          </div>
          <p className="restatement-text">
            "{verification.restatement_text}"
          </p>
        </div>
      )}

      {/* Attempt Counter */}
      <div className="verify-meta">
        <span className="attempt-counter">
          Attempt {verification.attempt_number || 0} / {verification.max_attempts || 2}
        </span>
        {verification.attempt_number >= (verification.max_attempts || 2) && 
         verification.status !== 'confirmed' && (
          <span className="max-attempts-warning animate-pulse">
            ⚠️ Max attempts reached — escalation triggered
          </span>
        )}
      </div>

      {/* Citizen Response (if any) */}
      {verification.citizen_response && (
        <div className="citizen-response">
          <span className="response-label">Citizen responded:</span>
          <p className="response-text">"{verification.citizen_response}"</p>
        </div>
      )}

      {/* Verification Input (for demo) */}
      {verification.status === 'pending' && onVerify && (
        <div className="verify-actions">
          <div className="verify-input-row">
            <input
              type="text"
              className="input verify-input"
              placeholder="Type citizen's response (e.g., 'houdu', 'illa', 'yes but...')"
              id="verification-response-input"
              onKeyDown={(e) => {
                if (e.key === 'Enter' && e.target.value.trim()) {
                  onVerify(e.target.value.trim());
                  e.target.value = '';
                }
              }}
            />
            <button
              className="btn btn-primary btn-sm"
              onClick={() => {
                const input = document.getElementById('verification-response-input');
                if (input?.value.trim()) {
                  onVerify(input.value.trim());
                  input.value = '';
                }
              }}
            >
              Verify
            </button>
          </div>
          <div className="quick-responses">
            <button className="btn btn-ghost btn-sm" onClick={() => onVerify('houdu')}>✅ Houdu (Yes)</button>
            <button className="btn btn-ghost btn-sm" onClick={() => onVerify('illa')}>❌ Illa (No)</button>
            <button className="btn btn-ghost btn-sm" onClick={() => onVerify('houdu, aadre...')}>🔄 Partial</button>
          </div>
        </div>
      )}

      {/* Progress Steps */}
      <div className="verify-steps">
        <div className={`step ${verification.status !== 'pending' ? 'completed' : 'active'}`}>
          <div className="step-dot" />
          <span>Listen</span>
        </div>
        <div className="step-connector" />
        <div className={`step ${verification.restatement_text ? 'completed' : ''}`}>
          <div className="step-dot" />
          <span>Restate</span>
        </div>
        <div className="step-connector" />
        <div className={`step ${verification.status === 'confirmed' ? 'completed' : verification.citizen_response ? 'active' : ''}`}>
          <div className="step-dot" />
          <span>Confirm</span>
        </div>
        <div className="step-connector" />
        <div className={`step ${verification.status === 'confirmed' ? 'completed' : verification.status === 'escalated' ? 'escalated' : ''}`}>
          <div className="step-dot" />
          <span>Proceed</span>
        </div>
      </div>
    </div>
  );
}
