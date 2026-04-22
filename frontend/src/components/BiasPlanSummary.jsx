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
    <div className="bg-white border border-slate-200 rounded-xl p-8 mb-8">
      <h2 className="font-headline-md text-headline-md mb-6 flex items-center gap-2 text-on-background">
        <AlertTriangle size={24} className="text-[#9d6ef5]" />
        Bias Analysis Plan
      </h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
        {/* Dataset Domain */}
        <div className="bg-slate-50 border border-slate-100 rounded-lg p-6">
          <div className="flex items-center gap-2 mb-3">
            <Tag size={18} className="text-primary" />
            <h3 className="font-headline-sm text-lg text-on-background">Dataset Domain</h3>
          </div>
          <p className="font-headline-lg text-2xl text-primary capitalize">{formatKey(biasPlan.dataset_domain || 'unknown')}</p>
          <p className="font-body-md text-sm text-on-surface-variant mt-2">Automatically detected domain for the dataset</p>
        </div>

        {/* Protected Attributes */}
        <div className="bg-slate-50 border border-slate-100 rounded-lg p-6">
          <div className="flex items-center gap-2 mb-3">
            <AlertTriangle size={18} className="text-error" />
            <h3 className="font-headline-sm text-lg text-on-background">Protected Attributes</h3>
          </div>
          <div className="flex flex-wrap gap-2">
            {biasPlan.protected_attributes?.map((attr, i) => (
              <span
                key={i}
                className="font-label-md px-3 py-1.5 rounded-md bg-error/10 text-error text-[13px] tracking-wide"
              >
                {formatKey(attr)}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Bias Types Detected */}
      {biasPlan.bias_types_detected && biasPlan.bias_types_detected.length > 0 && (
        <div className="bg-slate-50 border border-slate-100 rounded-lg p-6 mb-6">
          <h3 className="font-headline-sm text-lg mb-4 flex items-center gap-2 text-on-background">
            <Zap size={18} className="text-secondary" />
            Detected Bias Types
          </h3>
          <div className="flex flex-wrap gap-3">
            {biasPlan.bias_types_detected.map((biasType, i) => (
              <div
                key={i}
                style={{
                  padding: '10px 14px',
                  borderRadius: '6px',
                  background: `${biasTypeColors[biasType] || '#64748b'}15`,
                  border: `1px solid ${biasTypeColors[biasType] || '#64748b'}40`,
                  color: biasTypeColors[biasType] || '#64748b',
                }}
                className="font-label-md text-[13px] tracking-wide"
              >
                {formatKey(biasType)}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Reasoning */}
      {biasPlan.reasoning && (
        <div className="p-4 border-l-4 border-primary bg-primary/5 rounded-r-md">
          <p className="font-body-md text-sm text-slate-700 italic leading-relaxed m-0">{biasPlan.reasoning}</p>
        </div>
      )}
    </div>
  );
}
