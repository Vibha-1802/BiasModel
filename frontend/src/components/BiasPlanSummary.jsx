import React from 'react';
import { AlertTriangle, Tag, Zap } from 'lucide-react';
import { formatKey } from '../utils/formatters';

export default function BiasPlanSummary({ biasPlan, biasTypes }) {
  if (!biasPlan) return null;

  const biasTypeColors = {
    representation_bias: '#3b82f6',
    historical_bias: '#ef4444',
    measurement_bias: '#f59e0b',
    aggregation_bias: '#8b5cf6',
    label_bias: '#ec4899',
    proxy_discrimination: '#06b6d4',
    temporal_bias: '#10b981',
  };

  return (
    <div className="glass-card mb-8">
      <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
        <AlertTriangle size={24} style={{ color: 'var(--accent-purple)' }} />
        Bias Analysis Plan
      </h2>
      
      <div className="grid grid-cols-2 gap-8 mb-8">
        {/* Dataset Domain */}
        <div className="glass-panel" style={{ padding: '24px', background: 'rgba(255,255,255,0.02)' }}>
          <div className="flex items-center gap-2 mb-3">
            <Tag size={18} style={{ color: 'var(--accent-blue)' }} />
            <h3 className="font-bold text-lg">Dataset Domain</h3>
          </div>
          <p className="text-2xl font-bold text-blue">{formatKey(biasPlan.dataset_domain || 'unknown')}</p>
          <p className="text-sm text-secondary mt-2">Automatically detected domain for the dataset</p>
        </div>

        {/* Protected Attributes */}
        <div className="glass-panel" style={{ padding: '24px', background: 'rgba(255,255,255,0.02)' }}>
          <div className="flex items-center gap-2 mb-3">
            <AlertTriangle size={18} style={{ color: 'var(--accent-red)' }} />
            <h3 className="font-bold text-lg">Protected Attributes</h3>
          </div>
          <div className="flex flex-wrap gap-2">
            {biasPlan.protected_attributes?.map((attr, i) => (
              <span
                key={i}
                className="badge"
                style={{
                  background: 'rgba(239, 68, 68, 0.1)',
                  color: 'var(--accent-red)',
                  padding: '8px 14px',
                  fontSize: '13px',
                }}
              >
                {formatKey(attr)}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Bias Types Detected */}
      {biasPlan.bias_types_detected && biasPlan.bias_types_detected.length > 0 && (
        <div className="glass-panel" style={{ padding: '24px', background: 'rgba(255,255,255,0.02)', marginBottom: '24px' }}>
          <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
            <Zap size={18} style={{ color: 'var(--accent-green)' }} />
            Detected Bias Types
          </h3>
          <div className="flex flex-wrap gap-3">
            {biasPlan.bias_types_detected.map((biasType, i) => (
              <div
                key={i}
                style={{
                  padding: '12px 16px',
                  borderRadius: '8px',
                  background: `${biasTypeColors[biasType] || '#64748b'}15`,
                  border: `1px solid ${biasTypeColors[biasType] || '#64748b'}40`,
                  color: biasTypeColors[biasType] || '#94a3b8',
                  fontSize: '13px',
                  fontWeight: 500,
                }}
              >
                {formatKey(biasType)}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Reasoning */}
      {biasPlan.reasoning && (
        <div style={{
          padding: '16px',
          borderLeft: '3px solid var(--accent-blue)',
          background: 'rgba(59, 130, 246, 0.05)',
          borderRadius: '4px',
        }}>
          <p className="text-sm text-secondary leading-relaxed italic">{biasPlan.reasoning}</p>
        </div>
      )}
    </div>
  );
}
