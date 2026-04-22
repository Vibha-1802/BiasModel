import React from 'react';
import { CheckCircle, XCircle, AlertCircle, Activity } from 'lucide-react';
import { formatKey } from '../utils/formatters';

export default function MitigationStatus({ fairlearnMitigation, reportingPack }) {
  if (!fairlearnMitigation) return null;

  const statusIcons = {
    '✅': <CheckCircle size={20} className="text-secondary" />,
    '⚠️': <AlertCircle size={20} className="text-[#f59e0b]" />,
    '❌': <XCircle size={20} className="text-error" />,
  };

  const getStatusColorClass = (status) => {
    if (status?.includes('✅') || status?.includes('PASSED')) return 'text-secondary';
    if (status?.includes('⚠️') || status?.includes('PARTIAL')) return 'text-[#f59e0b]';
    if (status?.includes('❌') || status?.includes('FAILED')) return 'text-error';
    return 'text-slate-500';
  };

  const extractStatusText = (status) => {
    if (!status) return 'N/A';
    return status.replace(/^[✅❌⚠️]\s*/, '').trim();
  };

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-8 mb-8">
      <h2 className="font-headline-md text-headline-md mb-6 flex items-center gap-2 text-on-background">
        <Activity size={24} className="text-primary" />
        Fairness Mitigation Pipeline
      </h2>

      {/* Phase 1: Baseline Evaluation */}
      <div className="bg-slate-50 border border-slate-100 rounded-lg p-5 mb-4">
        <div className="flex items-start justify-between mb-2">
          <h3 className="font-headline-sm text-base text-on-background flex items-center gap-2">
            Phase 1: Baseline Bias Evaluation
          </h3>
          {fairlearnMitigation.phase_1_status && (
            <span className={`font-label-md text-sm ${getStatusColorClass(fairlearnMitigation.phase_1_status)}`}>
              {extractStatusText(fairlearnMitigation.phase_1_status)}
            </span>
          )}
        </div>
        <p className="font-body-md text-sm text-on-surface-variant m-0">
          Evaluates bias metrics (statistical parity, disparate impact, equalized odds) across protected attributes.
        </p>
      </div>

      {/* Phase 2: Mitigation */}
      <div className="bg-slate-50 border border-slate-100 rounded-lg p-5 mb-4">
        <div className="flex items-start justify-between mb-2">
          <h3 className="font-headline-sm text-base text-on-background flex items-center gap-2">
            Phase 2: Mitigation Intervention
          </h3>
          {fairlearnMitigation.phase_2_method && (
            <span className="bg-primary/10 text-primary px-3 py-1 rounded-md font-label-md text-[11px] uppercase tracking-widest">
              {formatKey(fairlearnMitigation.phase_2_method)}
            </span>
          )}
        </div>
        <p className="font-body-md text-sm text-on-surface-variant mb-4">
          Applies mitigation techniques to reduce bias in protected attributes.
        </p>

        {/* Success/Failure Summary */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-4 border-t border-slate-200">
          <div>
            <p className="font-label-md text-[11px] text-slate-500 uppercase tracking-widest mb-2">Successful Attributes</p>
            {fairlearnMitigation.phase_2_successful_attributes?.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {fairlearnMitigation.phase_2_successful_attributes.map((attr, i) => (
                  <span
                    key={i}
                    className="bg-secondary/10 text-secondary px-3 py-1.5 rounded-md font-label-md text-[12px]"
                  >
                    ✓ {formatKey(attr)}
                  </span>
                ))}
              </div>
            ) : (
              <p className="font-body-md text-sm text-slate-400">None</p>
            )}
          </div>
          <div>
            <p className="font-label-md text-[11px] text-slate-500 uppercase tracking-widest mb-2">Failed Attributes</p>
            {fairlearnMitigation.phase_2_failed_attributes?.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {fairlearnMitigation.phase_2_failed_attributes.map((attr, i) => (
                  <span
                    key={i}
                    className="bg-error/10 text-error px-3 py-1.5 rounded-md font-label-md text-[12px]"
                  >
                    ✗ {formatKey(attr)}
                  </span>
                ))}
              </div>
            ) : (
              <p className="font-body-md text-sm text-slate-400">None</p>
            )}
          </div>
        </div>
      </div>

      {/* Phase 3: Post-Mitigation Evaluation */}
      <div className="bg-slate-50 border border-slate-100 rounded-lg p-5 mb-4">
        <div className="flex items-start justify-between mb-2">
          <h3 className="font-headline-sm text-base text-on-background flex items-center gap-2">
            Phase 3: Post-Mitigation Evaluation
          </h3>
          {fairlearnMitigation.phase_3_status && (
            <span className={`font-label-md text-sm ${getStatusColorClass(fairlearnMitigation.phase_3_status)}`}>
              {extractStatusText(fairlearnMitigation.phase_3_status)}
            </span>
          )}
        </div>
        <p className="font-body-md text-sm text-on-surface-variant m-0">
          Re-evaluates bias metrics after mitigation to measure improvement.
        </p>
      </div>

      {/* Phase 4: Summary Report */}
      {fairlearnMitigation.phase_4_summary && Object.keys(fairlearnMitigation.phase_4_summary).length > 0 && (
        <div className="bg-slate-50 border border-slate-100 rounded-lg p-5">
          <h3 className="font-headline-sm text-base text-on-background mb-4 flex items-center gap-2">
            <span>📋</span>
            Phase 4: Mitigation Summary
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {fairlearnMitigation.phase_4_summary.total_protected_attributes !== undefined && (
              <div className="bg-primary/5 p-4 rounded-lg border border-primary/10">
                <p className="font-label-md text-[11px] text-slate-500 uppercase tracking-widest mb-1">Protected Attributes</p>
                <p className="font-headline-lg text-2xl text-on-background">{fairlearnMitigation.phase_4_summary.total_protected_attributes}</p>
              </div>
            )}
            {fairlearnMitigation.phase_4_summary.total_metrics_passed !== undefined && (
              <div className="bg-secondary/5 p-4 rounded-lg border border-secondary/10">
                <p className="font-label-md text-[11px] text-slate-500 uppercase tracking-widest mb-1">Metrics Passed</p>
                <p className="font-headline-lg text-2xl text-secondary">{fairlearnMitigation.phase_4_summary.total_metrics_passed}</p>
              </div>
            )}
            {fairlearnMitigation.phase_4_summary.total_metrics_improved !== undefined && (
              <div className="bg-[#9d6ef5]/5 p-4 rounded-lg border border-[#9d6ef5]/10">
                <p className="font-label-md text-[11px] text-slate-500 uppercase tracking-widest mb-1">Metrics Improved</p>
                <p className="font-headline-lg text-2xl text-[#9d6ef5]">{fairlearnMitigation.phase_4_summary.total_metrics_improved}</p>
              </div>
            )}
          </div>
          {fairlearnMitigation.phase_4_summary.mitigation_effectiveness && (
            <div className="mt-4 p-4 bg-white border border-slate-200 rounded-lg shadow-sm">
              <p className={`font-body-md text-sm font-medium m-0 ${getStatusColorClass(fairlearnMitigation.phase_4_summary.mitigation_effectiveness)}`}>
                {fairlearnMitigation.phase_4_summary.mitigation_effectiveness}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
