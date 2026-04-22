import React from 'react';
import { ShieldAlert, Settings, Wrench } from 'lucide-react';
import { formatKey } from '../utils/formatters';

export default function TaxonomyView({ taxonomy, biasPlan }) {
  if (!taxonomy || !biasPlan) return null;

  return (
    <div className="glass-card mb-8">
      <h2 className="text-xl font-bold mb-6">LLM Fairness Strategy Recommendations</h2>
      
      <div className="grid grid-cols-2 gap-8">
        <div>
          <div className="flex items-center gap-2 mb-4">
            <ShieldAlert className="text-blue" size={20} />
            <h3 className="text-lg font-medium">Recommended Metrics</h3>
          </div>
          <div className="flex flex-col gap-3">
            {taxonomy.recommended_detection_metrics?.map((metric, i) => (
              <div key={i} className="glass-panel" style={{ padding: '16px', background: 'rgba(255,255,255,0.02)' }}>
                <div className="flex justify-between items-start mb-2">
                  <p className="font-bold text-primary">{formatKey(metric.name)}</p>
                  {metric.supported_now && <span className="badge bg-green-soft" style={{ fontSize: '10px' }}>Active</span>}
                </div>
                <p className="text-sm text-secondary">{metric.description}</p>
              </div>
            ))}
          </div>
        </div>

        <div>
          <div className="flex items-center gap-2 mb-4">
            <Wrench className="text-purple" style={{ color: 'var(--accent-purple)' }} size={20} />
            <h3 className="text-lg font-medium">Recommended Mitigation</h3>
          </div>
          <div className="flex flex-col gap-4">
            {Object.entries(taxonomy.recommended_mitigation || {}).map(([phase, methods]) => (
              <div key={phase}>
                <h4 className="text-sm font-bold text-secondary uppercase tracking-wider mb-2">{formatKey(phase)}</h4>
                <div className="flex flex-col gap-2">
                  {methods.map((method, i) => (
                    <div key={i} className="glass-panel flex items-center justify-between" style={{ padding: '12px 16px', background: 'rgba(255,255,255,0.02)' }}>
                      <div>
                        <p className="font-medium text-primary text-sm">{formatKey(method.name)}</p>
                        <p className="text-xs text-secondary mt-1">{method.description}</p>
                      </div>
                      {method.supported_now && <span className="badge bg-green-soft" style={{ fontSize: '10px' }}>Active</span>}
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
