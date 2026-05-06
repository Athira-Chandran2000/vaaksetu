import React from 'react';
import './InterpretationCard.css';

/**
 * InterpretationCard — Displays the AI's structured interpretation of the citizen's speech.
 * Shows core issue, category, intent, entities, and enrichment context.
 */

export default function InterpretationCard({ interpretation, asrResult }) {
  if (!interpretation) return null;

  const confidencePercent = Math.round((interpretation.confidence || 0) * 100);
  const entities = interpretation.entities || {};

  // Collect non-null entities
  const entityEntries = Object.entries(entities).filter(([, val]) => val);

  return (
    <div className="interpretation-card glass-card animate-slide-up">
      <div className="interp-header">
        <div className="interp-title-row">
          <h3 className="interp-title">🧠 AI Interpretation</h3>
          <div className="interp-confidence">
            <div className={`confidence-dot ${confidencePercent > 70 ? 'high' : confidencePercent > 40 ? 'medium' : 'low'}`} />
            <span>{confidencePercent}% confident</span>
          </div>
        </div>
        <div className="interp-badges">
          <span className="badge badge-accent">{interpretation.category || 'Unknown'}</span>
          <span className="badge badge-info">{interpretation.intent || 'unknown'}</span>
        </div>
      </div>

      <div className="interp-body">
        {/* Core Issue */}
        <div className="interp-section">
          <h4 className="interp-section-label">Core Issue</h4>
          <p className="interp-core-issue">{interpretation.core_issue}</p>
          {interpretation.native_core_issue && (
            <p className="interp-native-issue">{interpretation.native_core_issue}</p>
          )}
        </div>

        {/* Detailed Interpretation */}
        {interpretation.raw_interpretation && (
          <div className="interp-section">
            <h4 className="interp-section-label">Detailed Interpretation</h4>
            <p className="interp-detail">{interpretation.raw_interpretation}</p>
          </div>
        )}

        {/* Entities */}
        {entityEntries.length > 0 && (
          <div className="interp-section">
            <h4 className="interp-section-label">Extracted Entities</h4>
            <div className="entity-grid">
              {entityEntries.map(([key, value]) => (
                <div key={key} className="entity-item">
                  <span className="entity-key">{key.replace(/_/g, ' ')}</span>
                  <span className="entity-value">{value}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Enrichment Context */}
        {interpretation.enrichment_context?.length > 0 && (
          <div className="interp-section">
            <h4 className="interp-section-label">Real-Time Data Sources</h4>
            <div className="enrichment-list">
              {interpretation.enrichment_context.map((ctx, i) => (
                <span key={i} className="enrichment-tag">
                  <span className="enrichment-dot" />
                  {ctx}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* ASR Details */}
        {asrResult && (
          <div className="interp-section asr-section">
            <h4 className="interp-section-label">ASR Details</h4>
            <div className="asr-meta">
              <span className="asr-tag">
                🗣️ {asrResult.language_detected} ({asrResult.dialect_detected})
              </span>
              <span className="asr-tag">
                📊 ASR Conf: {Math.round((asrResult.confidence || 0) * 100)}%
              </span>
              {asrResult.duration_seconds > 0 && (
                <span className="asr-tag">
                  ⏱️ {asrResult.duration_seconds}s
                </span>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
