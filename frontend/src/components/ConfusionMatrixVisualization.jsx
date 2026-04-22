import React from 'react';
import { formatKey } from '../utils/formatters';

export default function ConfusionMatrixVisualization({ performanceMatrix }) {
  if (!performanceMatrix || performanceMatrix.length === 0) return null;

  const ConfusionMatrix = ({ matrix, label }) => {
    if (!matrix || matrix.length !== 2) return null;

    const [[tn, fp], [fn, tp]] = matrix;
    const total = tn + fp + fn + tp;
    const accuracy = total > 0 ? ((tn + tp) / total * 100).toFixed(2) : 0;
    const precision = tp + fp > 0 ? (tp / (tp + fp) * 100).toFixed(2) : 0;
    const recall = tp + fn > 0 ? (tp / (tp + fn) * 100).toFixed(2) : 0;
    const f1 = precision > 0 && recall > 0 ? (2 * (precision * recall) / (precision + recall)).toFixed(2) : 0;

    return (
      <div style={{ marginBottom: '24px' }}>
        <h4 className="font-bold text-sm mb-4">{label}</h4>
        
        {/* Confusion Matrix Grid */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: '60px 100px 100px',
          gap: '8px',
          marginBottom: '16px',
          alignItems: 'center',
        }}>
          {/* Headers */}
          <div />
          <div style={{ textAlign: 'center', fontWeight: 600, fontSize: '12px', color: 'var(--text-secondary)' }}>Pred: 0</div>
          <div style={{ textAlign: 'center', fontWeight: 600, fontSize: '12px', color: 'var(--text-secondary)' }}>Pred: 1</div>

          {/* True Negatives and False Positives */}
          <div style={{ fontWeight: 600, fontSize: '12px', color: 'var(--text-secondary)' }}>Actual: 0</div>
          <div style={{
            background: 'rgba(16, 185, 129, 0.2)',
            border: '1px solid rgba(16, 185, 129, 0.5)',
            borderRadius: '6px',
            padding: '12px',
            textAlign: 'center',
            minHeight: '50px',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
          }}>
            <div style={{ fontSize: '18px', fontWeight: 'bold', color: 'var(--accent-green)' }}>{tn}</div>
            <div style={{ fontSize: '10px', color: 'var(--text-secondary)' }}>TN</div>
          </div>
          <div style={{
            background: 'rgba(239, 68, 68, 0.2)',
            border: '1px solid rgba(239, 68, 68, 0.5)',
            borderRadius: '6px',
            padding: '12px',
            textAlign: 'center',
            minHeight: '50px',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
          }}>
            <div style={{ fontSize: '18px', fontWeight: 'bold', color: 'var(--accent-red)' }}>{fp}</div>
            <div style={{ fontSize: '10px', color: 'var(--text-secondary)' }}>FP</div>
          </div>

          {/* False Negatives and True Positives */}
          <div style={{ fontWeight: 600, fontSize: '12px', color: 'var(--text-secondary)' }}>Actual: 1</div>
          <div style={{
            background: 'rgba(239, 68, 68, 0.2)',
            border: '1px solid rgba(239, 68, 68, 0.5)',
            borderRadius: '6px',
            padding: '12px',
            textAlign: 'center',
            minHeight: '50px',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
          }}>
            <div style={{ fontSize: '18px', fontWeight: 'bold', color: 'var(--accent-red)' }}>{fn}</div>
            <div style={{ fontSize: '10px', color: 'var(--text-secondary)' }}>FN</div>
          </div>
          <div style={{
            background: 'rgba(16, 185, 129, 0.2)',
            border: '1px solid rgba(16, 185, 129, 0.5)',
            borderRadius: '6px',
            padding: '12px',
            textAlign: 'center',
            minHeight: '50px',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
          }}>
            <div style={{ fontSize: '18px', fontWeight: 'bold', color: 'var(--accent-green)' }}>{tp}</div>
            <div style={{ fontSize: '10px', color: 'var(--text-secondary)' }}>TP</div>
          </div>
        </div>

        {/* Metrics */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(4, 1fr)',
          gap: '8px',
        }}>
          <div style={{
            background: 'rgba(59, 130, 246, 0.1)',
            padding: '10px',
            borderRadius: '6px',
            textAlign: 'center',
          }}>
            <p style={{ fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '4px' }}>Accuracy</p>
            <p style={{ fontSize: '14px', fontWeight: 'bold', color: 'var(--accent-blue)' }}>{accuracy}%</p>
          </div>
          <div style={{
            background: 'rgba(139, 92, 246, 0.1)',
            padding: '10px',
            borderRadius: '6px',
            textAlign: 'center',
          }}>
            <p style={{ fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '4px' }}>Precision</p>
            <p style={{ fontSize: '14px', fontWeight: 'bold', color: 'var(--accent-purple)' }}>{precision}%</p>
          </div>
          <div style={{
            background: 'rgba(16, 185, 129, 0.1)',
            padding: '10px',
            borderRadius: '6px',
            textAlign: 'center',
          }}>
            <p style={{ fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '4px' }}>Recall</p>
            <p style={{ fontSize: '14px', fontWeight: 'bold', color: 'var(--accent-green)' }}>{recall}%</p>
          </div>
          <div style={{
            background: 'rgba(236, 72, 153, 0.1)',
            padding: '10px',
            borderRadius: '6px',
            textAlign: 'center',
          }}>
            <p style={{ fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '4px' }}>F1-Score</p>
            <p style={{ fontSize: '14px', fontWeight: 'bold', color: '#ec4899' }}>{f1}</p>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="glass-card mb-8">
      <h2 className="text-xl font-bold mb-6">Confusion Matrices & Performance Details</h2>
      <p className="text-secondary mb-8">Before and after mitigation performance comparison</p>

      <div className="grid grid-cols-1 gap-8">
        {performanceMatrix.map((item) => (
          <div key={item.attribute} className="glass-panel" style={{ padding: '24px', background: 'rgba(255,255,255,0.02)' }}>
            <h3 className="text-lg font-bold mb-6 capitalize">{formatKey(item.attribute)} Attribute</h3>

            <div className="grid grid-cols-2 gap-8">
              {/* Before Mitigation */}
              <div>
                <div style={{
                  padding: '12px',
                  background: 'rgba(100, 116, 139, 0.2)',
                  borderRadius: '6px',
                  marginBottom: '12px',
                  textAlign: 'center',
                }}>
                  <p style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-secondary)' }}>BEFORE MITIGATION</p>
                </div>
                <ConfusionMatrix matrix={item.confusion_matrix_before} label="Confusion Matrix" />
                {item.accuracy_before !== null && (
                  <div style={{
                    padding: '12px',
                    background: 'rgba(59, 130, 246, 0.1)',
                    borderRadius: '6px',
                    textAlign: 'center',
                  }}>
                    <p style={{ fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '4px' }}>Overall Accuracy</p>
                    <p style={{ fontSize: '18px', fontWeight: 'bold', color: 'var(--accent-blue)' }}>
                      {(item.accuracy_before * 100).toFixed(2)}%
                    </p>
                  </div>
                )}
              </div>

              {/* After Mitigation */}
              <div>
                <div style={{
                  padding: '12px',
                  background: 'rgba(59, 130, 246, 0.2)',
                  borderRadius: '6px',
                  marginBottom: '12px',
                  textAlign: 'center',
                }}>
                  <p style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-secondary)' }}>AFTER MITIGATION</p>
                </div>
                <ConfusionMatrix matrix={item.confusion_matrix_after} label="Confusion Matrix" />
                {item.accuracy_after !== null && (
                  <div style={{
                    padding: '12px',
                    background: 'rgba(59, 130, 246, 0.1)',
                    borderRadius: '6px',
                    textAlign: 'center',
                  }}>
                    <p style={{ fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '4px' }}>Overall Accuracy</p>
                    <p style={{ fontSize: '18px', fontWeight: 'bold', color: 'var(--accent-blue)' }}>
                      {(item.accuracy_after * 100).toFixed(2)}%
                    </p>
                  </div>
                )}
              </div>
            </div>

            {/* Accuracy Delta */}
            {item.accuracy_delta !== null && (
              <div style={{
                marginTop: '16px',
                padding: '12px',
                background: 'rgba(139, 92, 246, 0.1)',
                borderRadius: '6px',
                textAlign: 'center',
                borderLeft: `3px solid ${item.accuracy_delta >= 0 ? 'var(--accent-green)' : 'var(--accent-red)'}`,
              }}>
                <p style={{ fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '4px' }}>Accuracy Change</p>
                <p style={{
                  fontSize: '16px',
                  fontWeight: 'bold',
                  color: item.accuracy_delta >= 0 ? 'var(--accent-green)' : 'var(--accent-red)',
                }}>
                  {item.accuracy_delta >= 0 ? '+' : ''}{(item.accuracy_delta * 100).toFixed(2)}%
                </p>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
