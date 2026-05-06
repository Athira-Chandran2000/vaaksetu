import React from 'react';
import './SolutionCard.css';

/**
 * SolutionCard — Displays the AI-generated solution or suggested response
 * after the citizen has verified the interpretation.
 */

export default function SolutionCard({ solution, sessionStatus }) {
  if (!solution || sessionStatus !== 'verified') return null;

  return (
    <div className="solution-card glass-card animate-slide-up">
      <div className="solution-header">
        <div className="solution-title-row">
          <h3 className="solution-title">💡 Suggested Solution</h3>
          <span className="badge badge-success">Verified & Ready</span>
        </div>
      </div>
      <div className="solution-body">
        <div className="solution-content">
          <div className="solution-icon">✨</div>
          <p className="solution-text">{solution}</p>
        </div>
        <div className="solution-footer">
          <button className="btn btn-primary btn-sm" onClick={() => alert('Solution sent to citizen!')}>
            📤 Send to Citizen
          </button>
          <button className="btn btn-ghost btn-sm" onClick={() => alert('Solution copied to clipboard!')}>
            📋 Copy
          </button>
        </div>
      </div>
    </div>
  );
}
