import React, { useState, useEffect } from 'react';
import './RealTimeDataPanel.css';

/**
 * RealTimeDataPanel — Shows live government API data feeds enriching the AI pipeline.
 */

export default function RealTimeDataPanel({ enrichmentData }) {
  const [expanded, setExpanded] = useState(null);

  const sections = [
    {
      key: 'alerts',
      title: '🚨 Active Alerts',
      icon: '🚨',
      data: enrichmentData?.alerts || [],
      render: (items) => (
        <div className="alert-list">
          {items.map((alert, i) => (
            <div key={i} className="alert-item animate-fade-in" style={{ animationDelay: `${i * 0.1}s` }}>
              {alert}
            </div>
          ))}
        </div>
      ),
    },
    {
      key: 'crm_trends',
      title: '📊 CRM Trends',
      icon: '📊',
      data: enrichmentData?.crm_trends,
      render: (data) => data ? (
        <div className="crm-mini">
          <div className="crm-stat">
            <span className="crm-stat-value">{data.total_calls_today || 0}</span>
            <span className="crm-stat-label">Calls Today</span>
          </div>
          {data.top_categories?.slice(0, 3).map((cat, i) => (
            <div key={i} className="crm-cat-row">
              <span className="crm-cat-name">{cat.category}</span>
              <span className="crm-cat-count">{cat.count}</span>
              <span className={`crm-cat-trend trend-${cat.trend}`}>
                {cat.trend === 'up' ? '↑' : cat.trend === 'down' ? '↓' : '→'}
              </span>
            </div>
          ))}
        </div>
      ) : null,
    },
    {
      key: 'seva_sindhu',
      title: '🏛️ Seva Sindhu',
      icon: '🏛️',
      data: enrichmentData?.seva_sindhu || [],
      render: (items) => (
        <div className="data-list">
          {items.map((s, i) => (
            <div key={i} className="data-list-item">
              <span className="data-name">{s.service_name}</span>
              <span className={`badge ${s.status === 'active' ? 'badge-success' : 'badge-warning'}`}>
                {s.status}
              </span>
            </div>
          ))}
        </div>
      ),
    },
    {
      key: 'bwssb',
      title: '🚰 BWSSB Water',
      icon: '🚰',
      data: enrichmentData?.bwssb || [],
      render: (items) => (
        <div className="data-list">
          {items.map((s, i) => (
            <div key={i} className="data-list-item">
              <span className="data-name">{s.area}</span>
              <span className={`badge ${s.outage_active ? 'badge-danger' : 'badge-success'}`}>
                {s.water_supply_status}
              </span>
            </div>
          ))}
        </div>
      ),
    },
    {
      key: 'bbmp',
      title: '🏗️ BBMP Trending',
      icon: '🏗️',
      data: enrichmentData?.bbmp || [],
      render: (items) => (
        <div className="data-list">
          {items.map((g, i) => (
            <div key={i} className="data-list-item">
              <span className="data-name">{g.category}</span>
              <span className="data-count">{g.count}</span>
              <span className={`crm-cat-trend trend-${g.trend}`}>
                {g.trend === 'up' ? '↑' : g.trend === 'down' ? '↓' : '→'}
              </span>
            </div>
          ))}
        </div>
      ),
    },
    {
      key: 'ration_card',
      title: '🪪 Ration Card',
      icon: '🪪',
      data: enrichmentData?.ration_card || [],
      render: (items) => (
        <div className="data-list">
          {items.map((r, i) => (
            <div key={i} className="data-list-item">
              <span className="data-name">{r.holder_name} ({r.card_type})</span>
              <span className={`badge ${r.status === 'active' ? 'badge-success' : 'badge-danger'}`}>
                {r.status}
              </span>
            </div>
          ))}
        </div>
      ),
    },
    {
      key: 'pension',
      title: '💰 Pension',
      icon: '💰',
      data: enrichmentData?.pension || [],
      render: (items) => (
        <div className="data-list">
          {items.map((p, i) => (
            <div key={i} className="data-list-item">
              <span className="data-name">{p.beneficiary_name}</span>
              <span className={`badge ${p.status === 'active' ? 'badge-success' : 'badge-warning'}`}>
                {p.status}
              </span>
            </div>
          ))}
        </div>
      ),
    },
    {
      key: 'bhoomi',
      title: '🌾 Bhoomi Land',
      icon: '🌾',
      data: enrichmentData?.bhoomi || [],
      render: (items) => (
        <div className="data-list">
          {items.map((b, i) => (
            <div key={i} className="data-list-item">
              <span className="data-name">Survey #{b.survey_number} — {b.village}</span>
              <span className={`badge ${b.mutation_status === 'completed' ? 'badge-success' : b.mutation_status === 'disputed' ? 'badge-danger' : 'badge-warning'}`}>
                {b.mutation_status}
              </span>
            </div>
          ))}
        </div>
      ),
    },
  ];

  // Filter to only show sections with data
  const activeSections = sections.filter(s => {
    if (Array.isArray(s.data)) return s.data.length > 0;
    return s.data != null;
  });

  if (activeSections.length === 0) {
    return (
      <div className="rtd-panel glass-card">
        <h3 className="rtd-title">📡 Real-Time Data Feeds</h3>
        <p className="rtd-empty">No enrichment data available. Submit a citizen query to see live data feeds.</p>
      </div>
    );
  }

  return (
    <div className="rtd-panel glass-card">
      <div className="rtd-header">
        <h3 className="rtd-title">📡 Real-Time Data Feeds</h3>
        <span className="rtd-status">
          <span className="status-dot active" />
          <span>{activeSections.length} sources active</span>
        </span>
      </div>

      <div className="rtd-sections">
        {activeSections.map((section) => (
          <div
            key={section.key}
            className={`rtd-section ${expanded === section.key ? 'expanded' : ''}`}
          >
            <button
              className="rtd-section-header"
              onClick={() => setExpanded(expanded === section.key ? null : section.key)}
            >
              <span className="rtd-section-title">{section.title}</span>
              <span className="rtd-section-count">
                {Array.isArray(section.data) ? section.data.length : ''}
              </span>
              <span className="rtd-expand-icon">{expanded === section.key ? '▾' : '▸'}</span>
            </button>
            {expanded === section.key && (
              <div className="rtd-section-body animate-fade-in">
                {section.render(section.data)}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
