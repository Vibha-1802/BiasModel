import React, { useState } from 'react';
import { ChevronDown, ChevronUp, BookOpen } from 'lucide-react';
import { formatKey } from '../utils/formatters';

export default function TaxonomyCatalog({ taxonomy }) {
  const [expandedSection, setExpandedSection] = useState(null);

  if (!taxonomy) return null;

  const {
    detection_metrics_catalog,
    mitigation_algorithms_catalog,
  } = taxonomy;

  const sections = [
    {
      id: 'detection',
      title: 'Detection Metrics Catalog',
      icon: '📊',
      description: 'All available fairness metrics for bias detection',
      items: detection_metrics_catalog || {},
    },
    {
      id: 'mitigation',
      title: 'Mitigation Algorithms Catalog',
      icon: '🔧',
      description: 'All available algorithms organized by stage',
      items: mitigation_algorithms_catalog || {},
      isNested: true,
    },
  ];

  return (
    <div className="glass-card mb-8">
      <div className="flex items-center gap-3 mb-6">
        <BookOpen size={24} style={{ color: 'var(--accent-blue)' }} />
        <div>
          <h2 className="text-xl font-bold">Fairness & Mitigation Catalog</h2>
          <p className="text-sm text-secondary">Complete reference of detection metrics and mitigation strategies</p>
        </div>
      </div>

      <div className="flex flex-col gap-4">
        {sections.map((section) => (
          <div key={section.id}>
            {/* Section Header */}
            <div
              onClick={() => setExpandedSection(expandedSection === section.id ? null : section.id)}
              style={{
                padding: '16px 20px',
                background: 'rgba(255,255,255,0.02)',
                border: '1px solid var(--border-glass)',
                borderRadius: '12px',
                cursor: 'pointer',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                transition: 'all 0.2s',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'rgba(255,255,255,0.05)';
                e.currentTarget.style.borderColor = 'rgba(255,255,255,0.2)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'rgba(255,255,255,0.02)';
                e.currentTarget.style.borderColor = 'var(--border-glass)';
              }}
            >
              <div className="flex items-center gap-3 flex-1">
                <span style={{ fontSize: '20px' }}>{section.icon}</span>
                <div>
                  <h3 className="font-bold text-lg">{section.title}</h3>
                  <p className="text-sm text-secondary">{section.description}</p>
                </div>
              </div>
              {expandedSection === section.id ? (
                <ChevronUp size={20} style={{ color: 'var(--text-secondary)' }} />
              ) : (
                <ChevronDown size={20} style={{ color: 'var(--text-secondary)' }} />
              )}
            </div>

            {/* Expanded Content */}
            {expandedSection === section.id && (
              <div style={{ marginTop: '12px', paddingLeft: '12px' }}>
                {section.isNested ? (
                  // Mitigation Algorithms (nested by stage)
                  <div className="flex flex-col gap-4">
                    {Object.entries(section.items).map(([stage, algorithms]) => (
                      <div key={stage}>
                        <h4
                          style={{
                            fontSize: '13px',
                            fontWeight: 700,
                            color: 'var(--text-secondary)',
                            textTransform: 'uppercase',
                            letterSpacing: '0.05em',
                            marginBottom: '10px',
                            paddingBottom: '8px',
                            borderBottom: '1px solid var(--border-glass)',
                          }}
                        >
                          {formatKey(stage)}
                        </h4>
                        <div className="grid grid-cols-1 gap-3">
                          {Object.entries(algorithms).map(([algoKey, algoData]) => (
                            <div
                              key={algoKey}
                              className="glass-panel"
                              style={{
                                padding: '16px',
                                background: 'rgba(255,255,255,0.02)',
                                border: algoData.supported_now ? '1px solid var(--accent-green)40' : '1px solid var(--border-glass)',
                                borderLeft: algoData.supported_now ? '3px solid var(--accent-green)' : '3px solid var(--border-glass)',
                              }}
                            >
                              <div className="flex justify-between items-start mb-2">
                                <h5 className="font-bold text-sm">{formatKey(algoKey)}</h5>
                                {algoData.supported_now && (
                                  <span
                                    style={{
                                      background: 'rgba(16, 185, 129, 0.1)',
                                      color: 'var(--accent-green)',
                                      padding: '4px 10px',
                                      borderRadius: '6px',
                                      fontSize: '10px',
                                      fontWeight: 600,
                                      textTransform: 'uppercase',
                                    }}
                                  >
                                    ✓ Active
                                  </span>
                                )}
                              </div>
                              <p className="text-xs text-secondary">{algoData.description}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  // Detection Metrics (flat list)
                  <div className="grid grid-cols-1 gap-3">
                    {Object.entries(section.items).map(([metricKey, metricData]) => (
                      <div
                        key={metricKey}
                        className="glass-panel"
                        style={{
                          padding: '16px',
                          background: 'rgba(255,255,255,0.02)',
                          border: metricData.supported_now ? '1px solid var(--accent-green)40' : '1px solid var(--border-glass)',
                          borderLeft: metricData.supported_now ? '3px solid var(--accent-green)' : '3px solid var(--border-glass)',
                        }}
                      >
                        <div className="flex justify-between items-start mb-2">
                          <h5 className="font-bold text-sm">{formatKey(metricKey)}</h5>
                          {metricData.supported_now && (
                            <span
                              style={{
                                background: 'rgba(16, 185, 129, 0.1)',
                                color: 'var(--accent-green)',
                                padding: '4px 10px',
                                borderRadius: '6px',
                                fontSize: '10px',
                                fontWeight: 600,
                                textTransform: 'uppercase',
                              }}
                            >
                              ✓ Active
                            </span>
                          )}
                        </div>
                        <p className="text-xs text-secondary">{metricData.description}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Legend */}
      <div
        style={{
          marginTop: '24px',
          padding: '12px 16px',
          background: 'rgba(255,255,255,0.02)',
          borderRadius: '8px',
          borderLeft: '3px solid var(--text-secondary)',
        }}
      >
        <p className="text-xs text-secondary">
          <span style={{ fontWeight: 600 }}>✓ Active:</span> Currently supported and can be used in bias detection/mitigation.
          <br />
          <span style={{ fontWeight: 600 }}>Inactive:</span> Not yet implemented but planned for future versions.
        </p>
      </div>
    </div>
  );
}
