import React, { useState } from 'react';
import { ChevronDown, ChevronUp, CheckCircle, XCircle, TrendingDown, TrendingUp } from 'lucide-react';
import { formatKey } from '../utils/formatters';

export default function DetailedBiasMatrix({ biasMatrix }) {
  const [expandedAttribute, setExpandedAttribute] = useState(null);

  if (!biasMatrix || biasMatrix.length === 0) return null;

  const metricKeys = [
    'statistical_parity_difference',
    'disparate_impact_ratio',
    'equalized_odds_difference',
  ];

  const getMetricThreshold = (metricKey) => {
    switch (metricKey) {
      case 'statistical_parity_difference':
        return 0.1; // Typically, |difference| <= 0.1 is good
      case 'disparate_impact_ratio':
        return 0.8; // 80% rule: ratio >= 0.8
      case 'equalized_odds_difference':
        return 0.1;
      default:
        return 0.1;
    }
  };

  const formatMetricValue = (value) => {
    if (value === null || value === undefined) return 'N/A';
    return Number(value).toFixed(4);
  };

  const getImprovementIcon = (before, after) => {
    if (before === null || after === null) return null;
    const improved = Math.abs(after) < Math.abs(before);
    return improved ? (
      <TrendingDown size={14} className="text-secondary" />
    ) : (
      <TrendingUp size={14} className="text-error" />
    );
  };

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-8 mb-8">
      <h2 className="font-headline-md text-headline-md mb-6 text-on-background">Detailed Bias Metrics by Attribute</h2>
      <p className="font-body-md text-on-surface-variant mb-6">Expand each attribute to see detailed metric values, pass/fail status, and improvement trends.</p>

      <div className="flex flex-col gap-3">
        {biasMatrix.map((item, idx) => (
          <div key={idx} className="bg-white border border-slate-200 rounded-lg overflow-hidden">
            {/* Header - Click to Expand */}
            <div
              onClick={() => setExpandedAttribute(expandedAttribute === idx ? null : idx)}
              className="px-5 py-4 flex justify-between items-center cursor-pointer hover:bg-slate-50 transition-colors"
            >
              <div className="flex items-center gap-4 flex-1">
                <h3 className="font-headline-sm text-lg text-on-background">{formatKey(item.attribute)}</h3>
                
                {/* Quick Status Summary */}
                <div className="flex gap-3">
                  {metricKeys.map((metricKey) => {
                    const passedBefore = item[`${metricKey}_passed_before`];
                    const passedAfter = item[`${metricKey}_passed_after`];
                    
                    if (passedBefore === null || passedBefore === undefined) return null;
                    
                    return (
                      <div key={metricKey} className="flex items-center gap-1">
                        {passedBefore ? (
                          <CheckCircle size={16} className="text-secondary" />
                        ) : (
                          <XCircle size={16} className="text-error" />
                        )}
                        {passedAfter !== null && passedAfter !== undefined && (
                          <span className="text-slate-400 text-xs">→</span>
                        )}
                        {passedAfter !== null && passedAfter !== undefined && (
                          passedAfter ? (
                            <CheckCircle size={16} className="text-secondary" />
                          ) : (
                            <XCircle size={16} className="text-error" />
                          )
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>

              <div className="flex items-center gap-3">
                <span className="font-label-md text-slate-500 uppercase tracking-widest text-[11px]">
                  {expandedAttribute === idx ? 'Hide' : 'Show'} Details
                </span>
                {expandedAttribute === idx ? (
                  <ChevronUp size={20} className="text-slate-400" />
                ) : (
                  <ChevronDown size={20} className="text-slate-400" />
                )}
              </div>
            </div>

            {/* Expanded Content */}
            {expandedAttribute === idx && (
              <div className="p-5 border-t border-slate-200 bg-slate-50">
                <div className="grid grid-cols-1 gap-6">
                  {metricKeys.map((metricKey) => {
                    const valueBefore = item[`${metricKey}_before`];
                    const valueAfter = item[`${metricKey}_after`];
                    const passedBefore = item[`${metricKey}_passed_before`];
                    const passedAfter = item[`${metricKey}_passed_after`];
                    const delta = item[`${metricKey}_delta`];

                    if (valueBefore === null && valueBefore === undefined) return null;

                    const threshold = getMetricThreshold(metricKey);
                    const goalValue = metricKey === 'disparate_impact_ratio' ? 1 : 0;

                    return (
                      <div
                        key={metricKey}
                        className={`p-4 bg-white border border-slate-200 rounded-lg border-l-4 ${passedAfter ? 'border-l-secondary' : 'border-l-error'}`}
                      >
                        <div className="flex justify-between items-start mb-4">
                          <div>
                            <h4 className="font-headline-sm text-base mb-1 text-on-background">{formatKey(metricKey)}</h4>
                            <p className="font-label-md text-xs text-on-surface-variant">
                              Goal: {goalValue === 0 ? 'Close to 0' : 'Close to 1'} (threshold: ±{threshold.toFixed(2)})
                            </p>
                          </div>
                          <div className="flex gap-2">
                            {passedBefore ? (
                              <div className="flex items-center gap-1 bg-secondary/10 px-2 py-1 rounded">
                                <CheckCircle size={14} className="text-secondary" />
                                <span className="font-label-md text-[11px] text-secondary">PASS</span>
                              </div>
                            ) : (
                              <div className="flex items-center gap-1 bg-error/10 px-2 py-1 rounded">
                                <XCircle size={14} className="text-error" />
                                <span className="font-label-md text-[11px] text-error">FAIL</span>
                              </div>
                            )}
                          </div>
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                          <div className="bg-slate-50 p-3 rounded-md border border-slate-100">
                            <p className="font-label-md text-[11px] text-slate-500 mb-1">BEFORE MITIGATION</p>
                            <p className="font-headline-sm text-lg text-on-background">{formatMetricValue(valueBefore)}</p>
                          </div>

                          <div className="bg-primary/5 p-3 rounded-md border border-primary/10">
                            <p className="font-label-md text-[11px] text-primary mb-1">AFTER MITIGATION</p>
                            <div className="flex items-end justify-between">
                              <p className="font-headline-sm text-lg text-primary">{formatMetricValue(valueAfter)}</p>
                              {valueAfter !== null && (
                                getImprovementIcon(valueBefore, valueAfter)
                              )}
                            </div>
                          </div>

                          <div className="bg-[#9d6ef5]/5 p-3 rounded-md border border-[#9d6ef5]/10">
                            <p className="font-label-md text-[11px] text-[#9d6ef5] mb-1">CHANGE (Δ)</p>
                            <p className="font-headline-sm text-lg text-[#9d6ef5]">{formatMetricValue(delta)}</p>
                          </div>
                        </div>

                        {valueAfter !== null && valueAfter !== undefined && passedAfter !== null && passedAfter !== undefined && (
                          <div className={`mt-3 px-3 py-2 rounded-md ${passedAfter ? 'bg-secondary/10 text-secondary' : 'bg-error/10 text-error'}`}>
                            <p className="font-label-md text-xs">
                              {passedAfter ? '✓ This metric now passes fairness threshold' : '✗ This metric still fails fairness threshold'}
                            </p>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
