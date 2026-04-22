import React from 'react';
import { formatKey, formatValue } from '../utils/formatters';

export default function FeatureStatsTable({ numericalSummary, featureStats }) {
  if (!numericalSummary || !featureStats) return null;

  const features = Object.keys(numericalSummary);
  if (features.length === 0) return null;

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-8 mb-8">
      <h2 className="font-headline-md text-headline-md mb-6 text-on-background">Numerical Features Summary</h2>
      <div className="overflow-x-auto rounded-lg border border-slate-200">
        <table className="w-full border-collapse text-left bg-white">
          <thead className="bg-slate-50 border-b border-slate-200">
            <tr>
              <th className="px-4 py-3 font-label-md text-xs uppercase tracking-widest text-slate-500">Feature</th>
              <th className="px-4 py-3 font-label-md text-xs uppercase tracking-widest text-slate-500">Min</th>
              <th className="px-4 py-3 font-label-md text-xs uppercase tracking-widest text-slate-500">Max</th>
              <th className="px-4 py-3 font-label-md text-xs uppercase tracking-widest text-slate-500">Mean</th>
              <th className="px-4 py-3 font-label-md text-xs uppercase tracking-widest text-slate-500">Median</th>
              <th className="px-4 py-3 font-label-md text-xs uppercase tracking-widest text-slate-500">Std Dev</th>
              <th className="px-4 py-3 font-label-md text-xs uppercase tracking-widest text-slate-500">Outliers</th>
            </tr>
          </thead>
          <tbody>
            {features.map((key) => {
              const stat = numericalSummary[key];
              const fStat = featureStats[key];
              return (
                <tr key={key} className="border-b border-slate-100 hover:bg-slate-50 transition-colors">
                  <td className="px-4 py-3 font-headline-sm text-sm text-on-background">{formatKey(key)}</td>
                  <td className="px-4 py-3 font-code-sm text-slate-600">{formatValue(stat.min)}</td>
                  <td className="px-4 py-3 font-code-sm text-slate-600">{formatValue(stat.max)}</td>
                  <td className="px-4 py-3 font-code-sm text-slate-600">{formatValue(stat.mean)}</td>
                  <td className="px-4 py-3 font-code-sm text-slate-600">{formatValue(stat.median)}</td>
                  <td className="px-4 py-3 font-code-sm text-slate-600">{formatValue(stat.std)}</td>
                  <td className="px-4 py-3 font-code-sm">
                    {fStat?.outlier_count > 0 ? (
                      <span className="text-error font-bold">{fStat.outlier_count}</span>
                    ) : (
                      <span className="text-slate-400">0</span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
