import React, { useState } from 'react';
import { ChevronDown, ChevronUp, CheckCircle, XCircle, TrendingDown, TrendingUp } from 'lucide-react';
import { formatKey } from '../utils/formatters';

export default function DetailedBiasMatrix({ biasMatrix }) {
  const [expandedAttribute, setExpandedAttribute] = useState(null);

  if (!biasMatrix || biasMatrix.length === 0) return null;

  const metricKeys = [
    'statistical_parity_difference',
    'disparate_impact_ratio',
    'equalized_odds_difference',
  ];

  const getMetricThreshold = (metricKey) => {
    switch (metricKey) {
      case 'statistical_parity_difference':
        return 0.1; // Typically, |difference| <= 0.1 is good
      case 'disparate_impact_ratio':
        return 0.8; // 80% rule: ratio >= 0.8
      case 'equalized_odds_difference':
        return 0.1;
      default:
        return 0.1;
    }
  };

  const formatMetricValue = (value) => {
    if (value === null || value === undefined) return 'N/A';
    return Number(value).toFixed(4);
  };

  const getImprovementIcon = (before, after) => {
    if (before === null || after === null) return null;
    const improved = Math.abs(after) < Math.abs(before);
    return improved ? (
      <TrendingDown size={14} style={{ color: 'var(--accent-green)' }} />
    ) : (
      <TrendingUp size={14} style={{ color: 'var(--accent-red)' }} />
    );
  };

  return (
    <div className="glass-card mb-8">
      <h2 className="text-xl font-bold mb-6">Detailed Bias Metrics by Attribute</h2>
      <p className="text-secondary mb-6">Expand each attribute to see detailed metric values, pass/fail status, and improvement trends.</p>

      <div className="flex flex-col gap-3">
        {biasMatrix.map((item, idx) => (
          <div key={idx} className="glass-panel" style={{ padding: '0', overflow: 'hidden' }}>
            {/* Header - Click to Expand */}
            <div
              onClick={() => setExpandedAttribute(expandedAttribute === idx ? null : idx)}
              style={{
                padding: '16px 20px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                cursor: 'pointer',
                background: 'rgba(255,255,255,0.02)',
                transition: 'background 0.2s',
              }}
              onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.05)'}
              onMouseLeave={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.02)'}
            >
              <div className="flex items-center gap-3 flex-1">
                <h3 className="font-bold text-lg">{formatKey(item.attribute)}</h3>
                
                {/* Quick Status Summary */}
                <div className="flex gap-2">
                  {metricKeys.map((metricKey) => {
                    const passedBefore = item[`${metricKey}_passed_before`];
                    const passedAfter = item[`${metricKey}_passed_after`];
                    
                    if (passedBefore === null || passedBefore === undefined) return null;
                    
                    return (
                      <div key={metricKey} style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                        {passedBefore ? (
                          <CheckCircle size={16} style={{ color: 'var(--accent-green)' }} />
                        ) : (
                          <XCircle size={16} style={{ color: 'var(--accent-red)' }} />
                        )}
                        {passedAfter !== null && passedAfter !== undefined && (
                          <span style={{ color: 'var(--text-secondary)', fontSize: '12px' }}>→</span>
                        )}
                        {passedAfter !== null && passedAfter !== undefined && (
                          passedAfter ? (
                            <CheckCircle size={16} style={{ color: 'var(--accent-green)' }} />
                          ) : (
                            <XCircle size={16} style={{ color: 'var(--accent-red)' }} />
                          )
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <span style={{ color: 'var(--text-secondary)', fontSize: '12px', fontWeight: 500 }}>
                  {expandedAttribute === idx ? 'Hide' : 'Show'} Details
                </span>
                {expandedAttribute === idx ? (
                  <ChevronUp size={20} style={{ color: 'var(--text-secondary)' }} />
                ) : (
                  <ChevronDown size={20} style={{ color: 'var(--text-secondary)' }} />
                )}
              </div>
            </div>

            {/* Expanded Content */}
            {expandedAttribute === idx && (
              <div style={{ padding: '20px', borderTop: '1px solid var(--border-glass)' }}>
                <div className="grid grid-cols-1 gap-6">
                  {metricKeys.map((metricKey) => {
                    const valueBefore = item[`${metricKey}_before`];
                    const valueAfter = item[`${metricKey}_after`];
                    const passedBefore = item[`${metricKey}_passed_before`];
                    const passedAfter = item[`${metricKey}_passed_after`];
                    const delta = item[`${metricKey}_delta`];

                    if (valueBefore === null && valueBefore === undefined) return null;

                    const threshold = getMetricThreshold(metricKey);
                    const goalValue = metricKey === 'disparate_impact_ratio' ? 1 : 0;

                    return (
                      <div
                        key={metricKey}
                        style={{
                          padding: '16px',
                          background: 'rgba(255,255,255,0.02)',
                          borderRadius: '8px',
                          borderLeft: `3px solid ${passedAfter ? 'var(--accent-green)' : 'var(--accent-red)'}`,
                        }}
                      >
                        <div className="flex justify-between items-start mb-3">
                          <div>
                            <h4 className="font-bold mb-1">{formatKey(metricKey)}</h4>
                            <p className="text-xs text-secondary">
                              Goal: {goalValue === 0 ? 'Close to 0' : 'Close to 1'} (threshold: ±{threshold.toFixed(2)})
                            </p>
                          </div>
                          <div className="flex gap-2">
                            {passedBefore ? (
                              <div style={{ display: 'flex', alignItems: 'center', gap: '4px', background: 'rgba(16, 185, 129, 0.1)', padding: '4px 8px', borderRadius: '4px' }}>
                                <CheckCircle size={14} style={{ color: 'var(--accent-green)' }} />
                                <span style={{ fontSize: '11px', color: 'var(--accent-green)', fontWeight: 600 }}>PASS</span>
                              </div>
                            ) : (
                              <div style={{ display: 'flex', alignItems: 'center', gap: '4px', background: 'rgba(239, 68, 68, 0.1)', padding: '4px 8px', borderRadius: '4px' }}>
                                <XCircle size={14} style={{ color: 'var(--accent-red)' }} />
                                <span style={{ fontSize: '11px', color: 'var(--accent-red)', fontWeight: 600 }}>FAIL</span>
                              </div>
                            )}
                          </div>
                        </div>

                        <div className="grid grid-cols-3 gap-4 mt-3">
                          <div style={{ background: 'rgba(100, 116, 139, 0.2)', padding: '12px', borderRadius: '6px' }}>
                            <p className="text-xs text-secondary uppercase font-bold mb-1">Before Mitigation</p>
                            <p className="text-lg font-bold">{formatMetricValue(valueBefore)}</p>
                          </div>

                          <div style={{ background: 'rgba(59, 130, 246, 0.2)', padding: '12px', borderRadius: '6px' }}>
                            <p className="text-xs text-secondary uppercase font-bold mb-1">After Mitigation</p>
                            <div className="flex items-end justify-between">
                              <p className="text-lg font-bold">{formatMetricValue(valueAfter)}</p>
                              {valueAfter !== null && (
                                getImprovementIcon(valueBefore, valueAfter)
                              )}
                            </div>
                          </div>

                          <div style={{ background: 'rgba(139, 92, 246, 0.2)', padding: '12px', borderRadius: '6px' }}>
                            <p className="text-xs text-secondary uppercase font-bold mb-1">Change (Δ)</p>
                            <p className="text-lg font-bold">{formatMetricValue(delta)}</p>
                          </div>
                        </div>

                        {valueAfter !== null && valueAfter !== undefined && passedAfter !== null && passedAfter !== undefined && (
                          <div style={{ marginTop: '12px', padding: '8px 12px', background: passedAfter ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)', borderRadius: '4px' }}>
                            <p className="text-xs font-medium" style={{ color: passedAfter ? 'var(--accent-green)' : 'var(--accent-red)' }}>
                              {passedAfter ? '✓ This metric now passes fairness threshold' : '✗ This metric still fails fairness threshold'}
                            </p>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
