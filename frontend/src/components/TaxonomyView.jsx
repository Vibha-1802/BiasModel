import React from 'react';
import { ShieldAlert, Wrench, BrainCircuit } from 'lucide-react';
import { formatKey } from '../utils/formatters';

export default function TaxonomyView({ taxonomy, biasPlan }) {
  if (!taxonomy || !biasPlan) return null;

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-8 mb-8">
      <h2 className="font-headline-md text-headline-md mb-6 text-on-background">LLM Fairness Strategy Recommendations</h2>
      
      {biasPlan.reasoning && (
        <div className="bg-primary/5 border border-primary/10 rounded-lg p-6 mb-8">
          <div className="flex items-center gap-2 mb-4">
            <BrainCircuit className="text-primary" size={24} />
            <h3 className="font-headline-sm text-lg text-on-background">LLM Reasoning</h3>
          </div>
          <p className="font-body-md text-on-surface-variant mb-6 leading-relaxed">{biasPlan.reasoning}</p>
          
          {biasPlan.bias_types_detected && biasPlan.bias_types_detected.length > 0 && (
            <div>
              <p className="font-label-md text-xs text-slate-500 uppercase tracking-widest mb-3">Detected Bias Types</p>
              <div className="flex flex-wrap gap-2">
                {biasPlan.bias_types_detected.map((type, i) => (
                  <span key={i} className="bg-primary/10 text-primary px-3 py-1.5 rounded-md font-label-md text-[12px]">
                    {formatKey(type)}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div>
          <div className="flex items-center gap-2 mb-4">
            <ShieldAlert className="text-primary" size={20} />
            <h3 className="font-headline-sm text-lg text-on-background">Recommended Metrics</h3>
          </div>
          <div className="flex flex-col gap-3">
            {taxonomy.recommended_detection_metrics?.map((metric, i) => (
              <div key={i} className="bg-slate-50 border border-slate-100 rounded-lg p-4">
                <div className="flex justify-between items-start mb-2">
                  <p className="font-headline-sm text-base text-primary">{formatKey(metric.name)}</p>
                  {metric.supported_now && <span className="bg-secondary/10 text-secondary px-2 py-0.5 rounded text-[10px] font-label-md tracking-wider uppercase">Active</span>}
                </div>
                <p className="font-body-md text-sm text-on-surface-variant">{metric.description}</p>
              </div>
            ))}
          </div>
        </div>

        <div>
          <div className="flex items-center gap-2 mb-4">
            <Wrench className="text-[#9d6ef5]" size={20} />
            <h3 className="font-headline-sm text-lg text-on-background">Recommended Mitigation</h3>
          </div>
          <div className="flex flex-col gap-5">
            {Object.entries(taxonomy.recommended_mitigation || {}).map(([phase, methods]) => (
              <div key={phase}>
                <h4 className="font-label-md text-[11px] text-slate-500 uppercase tracking-widest mb-3">{formatKey(phase)}</h4>
                <div className="flex flex-col gap-2">
                  {methods.map((method, i) => (
                    <div key={i} className="bg-slate-50 border border-slate-100 rounded-lg p-3 flex items-start justify-between">
                      <div className="pr-4">
                        <p className="font-headline-sm text-[15px] text-primary">{formatKey(method.name)}</p>
                        <p className="font-body-md text-xs text-on-surface-variant mt-1">{method.description}</p>
                      </div>
                      {method.supported_now && <span className="bg-secondary/10 text-secondary px-2 py-0.5 rounded text-[10px] font-label-md tracking-wider uppercase whitespace-nowrap mt-0.5">Active</span>}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
