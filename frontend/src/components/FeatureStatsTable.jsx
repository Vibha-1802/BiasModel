import React from 'react';
import { formatKey, formatValue } from '../utils/formatters';

export default function FeatureStatsTable({ numericalSummary, featureStats }) {
  if (!numericalSummary || !featureStats) return null;

  const features = Object.keys(numericalSummary);
  if (features.length === 0) return null;

  return (
    <div className="glass-card mb-8">
      <h2 className="text-xl font-bold mb-6">Numerical Features Summary</h2>
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border-glass)' }}>
              <th style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontWeight: 500 }}>Feature</th>
              <th style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontWeight: 500 }}>Min</th>
              <th style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontWeight: 500 }}>Max</th>
              <th style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontWeight: 500 }}>Mean</th>
              <th style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontWeight: 500 }}>Median</th>
              <th style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontWeight: 500 }}>Std Dev</th>
              <th style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontWeight: 500 }}>Outliers</th>
            </tr>
          </thead>
          <tbody>
            {features.map((key) => {
              const stat = numericalSummary[key];
              const fStat = featureStats[key];
              return (
                <tr key={key} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                  <td style={{ padding: '12px 16px', fontWeight: 500, color: 'var(--text-primary)' }}>{formatKey(key)}</td>
                  <td style={{ padding: '12px 16px' }}>{formatValue(stat.min)}</td>
                  <td style={{ padding: '12px 16px' }}>{formatValue(stat.max)}</td>
                  <td style={{ padding: '12px 16px' }}>{formatValue(stat.mean)}</td>
                  <td style={{ padding: '12px 16px' }}>{formatValue(stat.median)}</td>
                  <td style={{ padding: '12px 16px' }}>{formatValue(stat.std)}</td>
                  <td style={{ padding: '12px 16px' }}>
                    {fStat?.outlier_count > 0 ? (
                      <span className="text-red font-medium">{fStat.outlier_count}</span>
                    ) : (
                      <span className="text-secondary">0</span>
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
