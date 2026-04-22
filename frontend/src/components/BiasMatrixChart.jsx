import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine } from 'recharts';
import { formatKey } from '../utils/formatters';

export default function BiasMatrixChart({ biasMatrix }) {
  if (!biasMatrix || biasMatrix.length === 0) return null;

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white border border-slate-200 rounded-lg shadow-sm p-4">
          <p className="font-headline-sm text-sm font-bold text-on-background mb-2">{formatKey(label)}</p>
          {payload.map((p, i) => (
            <p key={i} style={{ color: p.color, margin: '4px 0' }} className="font-body-md text-sm">
              {p.name}: <span className="font-bold">{Number(p.value).toFixed(4)}</span>
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  const renderChart = (title, dataKeyBefore, dataKeyAfter, goal, goalLabel) => {
    return (
      <div className="flex-1 min-w-[300px] h-[350px]">
        <h3 className="font-headline-sm text-base text-center mb-4 text-on-background">{title}</h3>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={biasMatrix} margin={{ top: 30, right: 50, left: 20, bottom: 40 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
            <XAxis dataKey="attribute" stroke="#64748b" tick={{fontSize: 12}} tickFormatter={formatKey} angle={-45} textAnchor="end" height={80} />
            <YAxis stroke="#64748b" tick={{fontSize: 12}} />
            <Tooltip content={<CustomTooltip />} />
            <Legend wrapperStyle={{ paddingTop: '15px', fontSize: '12px' }} />
            <ReferenceLine y={goal} stroke="#824500" strokeDasharray="3 3" label={{ value: goalLabel, fill: '#824500', position: 'right', dy: 0, offset: 10, fontSize: 12 }} />
            <Bar dataKey={dataKeyBefore} name="Before Mitigation" fill="#cbd5e1" radius={[4, 4, 0, 0]} />
            <Bar dataKey={dataKeyAfter} name="After Mitigation" fill="#004ac6" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    );
  };

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-8 mb-8">
      <h2 className="font-headline-md text-headline-md mb-6 text-on-background">Bias Mitigation Results</h2>
      <div className="flex flex-col lg:flex-row gap-8">
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
