import React from 'react';
import { CheckCircle, XCircle, AlertCircle, Activity } from 'lucide-react';
import { formatKey } from '../utils/formatters';

export default function MitigationStatus({ fairlearnMitigation, reportingPack }) {
  if (!fairlearnMitigation) return null;

  const statusIcons = {
    '✅': <CheckCircle size={20} style={{ color: 'var(--accent-green)' }} />,
    '⚠️': <AlertCircle size={20} style={{ color: '#f59e0b' }} />,
    '❌': <XCircle size={20} style={{ color: 'var(--accent-red)' }} />,
  };

  const getStatusColor = (status) => {
    if (status?.includes('✅') || status?.includes('PASSED')) return 'var(--accent-green)';
    if (status?.includes('⚠️') || status?.includes('PARTIAL')) return '#f59e0b';
    if (status?.includes('❌') || status?.includes('FAILED')) return 'var(--accent-red)';
    return 'var(--text-secondary)';
  };

  const extractStatusText = (status) => {
    if (!status) return 'N/A';
    return status.replace(/^[✅❌⚠️]\s*/, '').trim();
  };

  return (
    <div className="glass-card mb-8">
      <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
        <Activity size={24} style={{ color: 'var(--accent-blue)' }} />
        Fairness Mitigation Pipeline
      </h2>

      {/* Phase 1: Baseline Evaluation */}
      <div className="glass-panel" style={{ padding: '20px', background: 'rgba(255,255,255,0.02)', marginBottom: '16px' }}>
        <div className="flex items-start justify-between mb-3">
          <h3 className="font-bold flex items-center gap-2">
            <span style={{ fontSize: '18px' }}>📊</span>
            Phase 1: Baseline Bias Evaluation
          </h3>
          {fairlearnMitigation.phase_1_status && (
            <span
              style={{
                color: getStatusColor(fairlearnMitigation.phase_1_status),
                fontSize: '13px',
                fontWeight: 600,
              }}
            >
              {extractStatusText(fairlearnMitigation.phase_1_status)}
            </span>
          )}
        </div>
        <p className="text-sm text-secondary">
          Evaluates bias metrics (statistical parity, disparate impact, equalized odds) across protected attributes.
        </p>
      </div>

      {/* Phase 2: Mitigation */}
      <div className="glass-panel" style={{ padding: '20px', background: 'rgba(255,255,255,0.02)', marginBottom: '16px' }}>
        <div className="flex items-start justify-between mb-3">
          <h3 className="font-bold flex items-center gap-2">
            <span style={{ fontSize: '18px' }}>🔧</span>
            Phase 2: Mitigation Intervention
          </h3>
          {fairlearnMitigation.phase_2_method && (
            <span
              style={{
                background: 'rgba(59, 130, 246, 0.1)',
                color: 'var(--accent-blue)',
                padding: '4px 10px',
                borderRadius: '6px',
                fontSize: '11px',
                fontWeight: 600,
              }}
            >
              {formatKey(fairlearnMitigation.phase_2_method)}
            </span>
          )}
        </div>
        <p className="text-sm text-secondary mb-4">
          Applies mitigation techniques to reduce bias in protected attributes.
        </p>

        {/* Success/Failure Summary */}
        <div className="grid grid-cols-2 gap-4 pt-3 border-t border-glass">
          <div>
            <p className="text-xs font-bold text-secondary uppercase mb-2">Successful Attributes</p>
            {fairlearnMitigation.phase_2_successful_attributes?.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {fairlearnMitigation.phase_2_successful_attributes.map((attr, i) => (
                  <span
                    key={i}
                    style={{
                      background: 'rgba(16, 185, 129, 0.1)',
                      color: 'var(--accent-green)',
                      padding: '6px 10px',
                      borderRadius: '6px',
                      fontSize: '12px',
                      fontWeight: 500,
                    }}
                  >
                    ✓ {formatKey(attr)}
                  </span>
                ))}
              </div>
            ) : (
              <p className="text-sm text-secondary">None</p>
            )}
          </div>
          <div>
            <p className="text-xs font-bold text-secondary uppercase mb-2">Failed Attributes</p>
            {fairlearnMitigation.phase_2_failed_attributes?.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {fairlearnMitigation.phase_2_failed_attributes.map((attr, i) => (
                  <span
                    key={i}
                    style={{
                      background: 'rgba(239, 68, 68, 0.1)',
                      color: 'var(--accent-red)',
                      padding: '6px 10px',
                      borderRadius: '6px',
                      fontSize: '12px',
                      fontWeight: 500,
                    }}
                  >
                    ✗ {formatKey(attr)}
                  </span>
                ))}
              </div>
            ) : (
              <p className="text-sm text-secondary">None</p>
            )}
          </div>
        </div>
      </div>

      {/* Phase 3: Post-Mitigation Evaluation */}
      <div className="glass-panel" style={{ padding: '20px', background: 'rgba(255,255,255,0.02)', marginBottom: '16px' }}>
        <div className="flex items-start justify-between mb-3">
          <h3 className="font-bold flex items-center gap-2">
            <span style={{ fontSize: '18px' }}>📈</span>
            Phase 3: Post-Mitigation Evaluation
          </h3>
          {fairlearnMitigation.phase_3_status && (
            <span
              style={{
                color: getStatusColor(fairlearnMitigation.phase_3_status),
                fontSize: '13px',
                fontWeight: 600,
              }}
            >
              {extractStatusText(fairlearnMitigation.phase_3_status)}
            </span>
          )}
        </div>
        <p className="text-sm text-secondary">
          Re-evaluates bias metrics after mitigation to measure improvement.
        </p>
      </div>

      {/* Phase 4: Summary Report */}
      {fairlearnMitigation.phase_4_summary && Object.keys(fairlearnMitigation.phase_4_summary).length > 0 && (
        <div className="glass-panel" style={{ padding: '20px', background: 'rgba(255,255,255,0.02)' }}>
          <h3 className="font-bold mb-4 flex items-center gap-2">
            <span style={{ fontSize: '18px' }}>📋</span>
            Phase 4: Mitigation Summary
          </h3>
          <div className="grid grid-cols-3 gap-4">
            {fairlearnMitigation.phase_4_summary.total_protected_attributes !== undefined && (
              <div style={{ padding: '12px', background: 'rgba(59, 130, 246, 0.05)', borderRadius: '8px' }}>
                <p className="text-xs text-secondary font-bold uppercase mb-1">Protected Attributes</p>
                <p className="text-2xl font-bold">{fairlearnMitigation.phase_4_summary.total_protected_attributes}</p>
              </div>
            )}
            {fairlearnMitigation.phase_4_summary.total_metrics_passed !== undefined && (
              <div style={{ padding: '12px', background: 'rgba(16, 185, 129, 0.05)', borderRadius: '8px' }}>
                <p className="text-xs text-secondary font-bold uppercase mb-1">Metrics Passed</p>
                <p className="text-2xl font-bold text-green">{fairlearnMitigation.phase_4_summary.total_metrics_passed}</p>
              </div>
            )}
            {fairlearnMitigation.phase_4_summary.total_metrics_improved !== undefined && (
              <div style={{ padding: '12px', background: 'rgba(139, 92, 246, 0.05)', borderRadius: '8px' }}>
                <p className="text-xs text-secondary font-bold uppercase mb-1">Metrics Improved</p>
                <p className="text-2xl font-bold" style={{ color: 'var(--accent-purple)' }}>{fairlearnMitigation.phase_4_summary.total_metrics_improved}</p>
              </div>
            )}
          </div>
          {fairlearnMitigation.phase_4_summary.mitigation_effectiveness && (
            <div
              style={{
                marginTop: '16px',
                padding: '12px 16px',
                background: 'rgba(255,255,255,0.02)',
                borderRadius: '8px',
                borderLeft: `3px solid ${getStatusColor(fairlearnMitigation.phase_4_summary.mitigation_effectiveness)}`,
              }}
            >
              <p className="text-sm font-medium">{fairlearnMitigation.phase_4_summary.mitigation_effectiveness}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
