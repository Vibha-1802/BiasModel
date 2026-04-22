import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine } from 'recharts';
import { formatKey } from '../utils/formatters';

export default function BiasMatrixChart({ biasMatrix }) {
  if (!biasMatrix || biasMatrix.length === 0) return null;

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="glass-panel" style={{ padding: '12px 16px', border: '1px solid var(--border-glass)' }}>
          <p className="font-bold mb-2">{formatKey(label)}</p>
          {payload.map((p, i) => (
            <p key={i} style={{ color: p.color, margin: '4px 0' }}>
              {p.name}: <span className="font-medium">{Number(p.value).toFixed(4)}</span>
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  const renderChart = (title, dataKeyBefore, dataKeyAfter, goal, goalLabel) => {
    return (
      <div style={{ flex: 1, minWidth: '300px', height: '350px' }}>
        <h3 className="text-lg font-medium text-center mb-4">{title}</h3>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={biasMatrix} margin={{ top: 30, right: 30, left: 20, bottom: 25 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" vertical={false} />
            <XAxis dataKey="attribute" stroke="var(--text-secondary)" tickFormatter={formatKey} />
            <YAxis stroke="var(--text-secondary)" />
            <Tooltip content={<CustomTooltip />} />
            <Legend wrapperStyle={{ paddingTop: '15px' }} />
            <ReferenceLine y={goal} stroke="var(--accent-purple)" strokeDasharray="3 3" label={{ value: goalLabel, fill: 'var(--accent-purple)', position: 'insideTopLeft', dy: -15 }} />
            <Bar dataKey={dataKeyBefore} name="Before Mitigation" fill="#64748b" radius={[4, 4, 0, 0]} />
            <Bar dataKey={dataKeyAfter} name="After Mitigation" fill="var(--accent-blue)" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    );
  };

  return (
    <div className="glass-card mb-8">
      <h2 className="text-xl font-bold mb-6">Bias Mitigation Results</h2>
      <div className="flex flex-wrap gap-8">
        {renderChart(
          "Statistical Parity Difference", 
          "statistical_parity_difference_before", 
          "statistical_parity_difference_after", 
          0, 
          "Ideal: 0"
        )}
        {renderChart(
          "Disparate Impact Ratio", 
          "disparate_impact_ratio_before", 
          "disparate_impact_ratio_after", 
          1, 
          "Ideal: 1"
        )}
        {biasMatrix[0].equalized_odds_difference_before !== undefined && renderChart(
          "Equalized Odds Difference", 
          "equalized_odds_difference_before", 
          "equalized_odds_difference_after", 
          0, 
          "Ideal: 0"
        )}
      </div>
    </div>
  );
}
