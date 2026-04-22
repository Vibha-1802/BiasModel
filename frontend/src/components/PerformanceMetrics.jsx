import React from 'react';
import { formatKey } from '../utils/formatters';
import { TrendingUp, TrendingDown, Scale } from 'lucide-react';

export default function PerformanceMetrics({ performanceMatrix }) {
  if (!performanceMatrix || performanceMatrix.length === 0) return null;

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-8 mb-8">
      <h2 className="font-headline-md text-headline-md mb-6 text-on-background">Fairness vs. Accuracy Tradeoff</h2>
      <p className="mb-6 font-body-md text-on-surface-variant">
        Removing bias often restricts the model, which can lead to a slight drop in accuracy. This shows the impact of mitigation on predictive performance.
      </p>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {performanceMatrix.map((item) => {
          const accBefore = (item.accuracy_before * 100).toFixed(2);
          const accAfter = (item.accuracy_after * 100).toFixed(2);
          const delta = (item.accuracy_delta * 100).toFixed(2);
          const isPositive = item.accuracy_delta >= 0;

          return (
            <div key={item.attribute} className="bg-slate-50 border border-slate-100 rounded-lg p-6">
              <div className="flex justify-between items-center mb-6">
                <h3 className="font-headline-sm text-lg capitalize text-on-background">{formatKey(item.attribute)} Mitigation</h3>
                {item.success ? (
                  <span className="font-label-md px-3 py-1 rounded-full bg-secondary/10 text-secondary uppercase tracking-widest text-[10px]">Successful</span>
                ) : (
                  <span className="font-label-md px-3 py-1 rounded-full bg-error/10 text-error uppercase tracking-widest text-[10px]">Failed</span>
                )}
              </div>
              
              <div className="flex justify-between w-full mb-6 pr-8">
                <div>
                  <p className="font-label-md text-sm text-on-surface-variant mb-1">Accuracy Before</p>
                  <p className="font-headline-lg text-2xl text-on-background">{accBefore}%</p>
                </div>
                <div>
                  <p className="font-label-md text-sm text-on-surface-variant mb-1">Accuracy After</p>
                  <div className="flex items-center gap-2">
                    <p className="font-headline-lg text-2xl text-on-background">{accAfter}%</p>
                    <span className={`text-sm flex items-center font-bold ${isPositive ? 'text-secondary' : 'text-error'}`}>
                      {isPositive ? <TrendingUp size={16} className="mr-1" /> : <TrendingDown size={16} className="mr-1" />}
                      {Math.abs(delta)}%
                    </span>
                  </div>
                </div>
              </div>

              {item.weights_summary && (
                <div className="border-t border-slate-200 pt-4 mt-2">
                  <div className="flex items-center gap-2 mb-2">
                    <Scale size={16} className="text-[#9d6ef5]" />
                    <p className="font-label-md text-sm uppercase tracking-tight text-[#9d6ef5]">Reweighing Intervention</p>
                  </div>
                  <p className="font-body-md text-sm text-on-surface-variant">
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
