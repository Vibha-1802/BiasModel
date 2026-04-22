import React from 'react';
import { formatKey } from '../utils/formatters';
import { TrendingUp, TrendingDown, Scale } from 'lucide-react';

export default function PerformanceMetrics({ performanceMatrix }) {
  if (!performanceMatrix || performanceMatrix.length === 0) return null;

  return (
    <div className="glass-card mb-8">
      <h2 className="text-xl font-bold mb-6">Fairness vs. Accuracy Tradeoff</h2>
      <p className="mb-6 text-secondary">
        Removing bias often restricts the model, which can lead to a slight drop in accuracy. This shows the impact of mitigation on predictive performance.
      </p>
      
      <div className="grid grid-cols-2 gap-6">
        {performanceMatrix.map((item) => {
          const accBefore = (item.accuracy_before * 100).toFixed(2);
          const accAfter = (item.accuracy_after * 100).toFixed(2);
          const delta = (item.accuracy_delta * 100).toFixed(2);
          const isPositive = item.accuracy_delta >= 0;

          return (
            <div key={item.attribute} className="glass-panel" style={{ padding: '24px', backgroundColor: 'rgba(255,255,255,0.02)' }}>
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-lg font-bold capitalize">{formatKey(item.attribute)} Mitigation</h3>
                {item.success ? (
                  <span className="badge bg-green-soft">Successful</span>
                ) : (
                  <span className="badge bg-red-soft">Failed</span>
                )}
              </div>
              
              <div className="flex justify-between w-full mb-6 pr-8">
                <div>
                  <p className="text-sm text-secondary mb-1">Accuracy Before</p>
                  <p className="text-2xl font-bold">{accBefore}%</p>
                </div>
                <div>
                  <p className="text-sm text-secondary mb-1">Accuracy After</p>
                  <div className="flex items-center gap-2">
                    <p className="text-2xl font-bold">{accAfter}%</p>
                    <span className={`text-sm flex items-center ${isPositive ? 'text-green' : 'text-red'}`}>
                      {isPositive ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
                      {Math.abs(delta)}%
                    </span>
                  </div>
                </div>
              </div>

              {item.weights_summary && (
                <div style={{ borderTop: '1px solid var(--border-glass)', paddingTop: '16px' }}>
                  <div className="flex items-center gap-2 mb-2">
                    <Scale size={16} className="text-purple" style={{ color: 'var(--accent-purple)' }} />
                    <p className="text-sm font-medium">Reweighing Intervention</p>
                  </div>
                  <p className="text-sm text-secondary">
                    Row weights were adjusted between <span className="font-bold text-primary">{item.weights_summary.min.toFixed(2)}</span> and <span className="font-bold text-primary">{item.weights_summary.max.toFixed(2)}</span> to achieve fairness.
                  </p>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
