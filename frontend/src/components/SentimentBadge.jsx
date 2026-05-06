import React from 'react';
import './SentimentBadge.css';

/**
 * SentimentBadge — Displays the citizen's emotional state as a visual badge.
 * Shows category, confidence, and urgency flag.
 */

const SENTIMENT_CONFIG = {
  distress:  { icon: '⚠️', color: 'var(--sentiment-distress)', label: 'Distressed', className: 'sentiment-distress' },
  anger:     { icon: '🔴', color: 'var(--sentiment-anger)', label: 'Angry', className: 'sentiment-anger' },
  fear:      { icon: '😰', color: 'var(--sentiment-fear)', label: 'Fearful', className: 'sentiment-fear' },
  confusion: { icon: '🤔', color: 'var(--sentiment-confused)', label: 'Confused', className: 'sentiment-confused' },
  urgency:   { icon: '🚨', color: 'var(--sentiment-urgency)', label: 'URGENT', className: 'sentiment-urgency' },
  calm:      { icon: '🟢', color: 'var(--sentiment-calm)', label: 'Calm', className: 'sentiment-calm' },
  neutral:   { icon: '⚪', color: 'var(--sentiment-neutral)', label: 'Neutral', className: 'sentiment-neutral' },
};

export default function SentimentBadge({ sentiment }) {
  if (!sentiment) return null;

  const config = SENTIMENT_CONFIG[sentiment.category] || SENTIMENT_CONFIG.neutral;
  const confidencePercent = Math.round((sentiment.confidence || 0) * 100);

  return (
    <div className={`sentiment-badge ${config.className} ${sentiment.urgency_flag ? 'urgent' : ''}`}>
      <div className="sentiment-badge-header">
        <span className="sentiment-icon">{config.icon}</span>
        <span className="sentiment-label">{sentiment.display_label || config.label}</span>
      </div>
      
      <div className="sentiment-details">
        <div className="sentiment-confidence">
          <div className="confidence-bar-track">
            <div 
              className="confidence-bar-fill"
              style={{ 
                width: `${confidencePercent}%`,
                backgroundColor: config.color 
              }}
            />
          </div>
          <span className="confidence-value">{confidencePercent}%</span>
        </div>

        {sentiment.urgency_flag && (
          <div className="urgency-alert animate-pulse">
            🚨 URGENT — Immediate attention required
          </div>
        )}

        <div className="sentiment-channels">
          {sentiment.lexical_sentiment && (
            <span className="channel-tag">
              📝 Lexical: {sentiment.lexical_sentiment}
            </span>
          )}
          {sentiment.acoustic_sentiment && (
            <span className="channel-tag">
              🎙️ Acoustic: {sentiment.acoustic_sentiment}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
