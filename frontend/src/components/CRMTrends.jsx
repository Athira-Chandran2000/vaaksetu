import React, { useState, useEffect } from 'react';
import './CRMTrends.css';

/**
 * CRMTrends — Displays real-time 1092 CRM call trend data.
 * Shows hourly volume, top categories, district distribution, and sentiment.
 */

export default function CRMTrends({ trends }) {
  const [activeTab, setActiveTab] = useState('categories');

  if (!trends) return null;

  const topCategories = trends.top_categories || [];
  const districtHeatmap = trends.district_heatmap || [];
  const sentimentDist = trends.sentiment_distribution || {};
  const hourlyVolume = trends.hourly_volume || [];

  // Find max for bar scaling
  const maxCatCount = Math.max(...topCategories.map(c => c.count), 1);
  const maxDistCount = Math.max(...districtHeatmap.map(d => d.calls), 1);
  const maxHourly = Math.max(...hourlyVolume.map(h => h.calls), 1);

  return (
    <div className="crm-trends glass-card">
      <div className="crm-header">
        <h3 className="crm-title">📈 1092 CRM Live Trends</h3>
        <div className="crm-summary">
          <div className="crm-kpi">
            <span className="kpi-value">{trends.total_calls_today}</span>
            <span className="kpi-label">Calls Today</span>
          </div>
          <div className="crm-kpi">
            <span className="kpi-value">{trends.active_calls}</span>
            <span className="kpi-label">Active Now</span>
          </div>
          <div className="crm-kpi">
            <span className="kpi-value">{Math.round((trends.ai_assist_rate || 0) * 100)}%</span>
            <span className="kpi-label">AI Assisted</span>
          </div>
          <div className="crm-kpi">
            <span className="kpi-value">{Math.round((trends.escalation_rate || 0) * 100)}%</span>
            <span className="kpi-label">Escalation</span>
          </div>
        </div>
      </div>

      <div className="crm-tabs">
        {['categories', 'districts', 'hourly', 'sentiment'].map(tab => (
          <button
            key={tab}
            className={`crm-tab ${activeTab === tab ? 'active' : ''}`}
            onClick={() => setActiveTab(tab)}
          >
            {tab === 'categories' ? '📋 Categories' : 
             tab === 'districts' ? '📍 Districts' : 
             tab === 'hourly' ? '⏰ Hourly' : '😊 Sentiment'}
          </button>
        ))}
      </div>

      <div className="crm-tab-content">
        {activeTab === 'categories' && (
          <div className="chart-bars animate-fade-in">
            {topCategories.map((cat, i) => (
              <div key={i} className="bar-row" style={{ animationDelay: `${i * 0.05}s` }}>
                <div className="bar-label">
                  <span className="bar-name">{cat.category}</span>
                  <span className="bar-meta">
                    <span className="bar-count">{cat.count}</span>
                    <span className={`bar-trend trend-${cat.trend}`}>
                      {cat.trend === 'up' ? '↑' : cat.trend === 'down' ? '↓' : '→'}
                    </span>
                    {cat.last_hour > 0 && (
                      <span className="bar-last-hour">+{cat.last_hour}/hr</span>
                    )}
                  </span>
                </div>
                <div className="bar-track">
                  <div
                    className="bar-fill"
                    style={{ width: `${(cat.count / maxCatCount) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'districts' && (
          <div className="chart-bars animate-fade-in">
            {districtHeatmap.map((d, i) => (
              <div key={i} className="bar-row" style={{ animationDelay: `${i * 0.05}s` }}>
                <div className="bar-label">
                  <span className="bar-name">{d.district}</span>
                  <span className="bar-count">{d.calls}</span>
                </div>
                <div className="bar-track">
                  <div
                    className="bar-fill bar-fill-cyan"
                    style={{ width: `${(d.calls / maxDistCount) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'hourly' && (
          <div className="hourly-chart animate-fade-in">
            <div className="hourly-bars">
              {hourlyVolume.map((h, i) => (
                <div key={i} className="hourly-col" title={`${h.hour}: ${h.calls} calls`}>
                  <div
                    className="hourly-bar"
                    style={{ height: `${(h.calls / maxHourly) * 100}%` }}
                  />
                  {i % 4 === 0 && <span className="hourly-label">{h.hour}</span>}
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'sentiment' && (
          <div className="sentiment-dist animate-fade-in">
            {Object.entries(sentimentDist).map(([key, val], i) => (
              <div key={key} className="sentiment-row">
                <span className="sentiment-name">{key}</span>
                <div className="sentiment-bar-track">
                  <div
                    className={`sentiment-bar-fill sentiment-fill-${key}`}
                    style={{ width: `${val * 100}%` }}
                  />
                </div>
                <span className="sentiment-pct">{Math.round(val * 100)}%</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
