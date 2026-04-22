import React from 'react';
import { formatKey } from '../utils/formatters';

export default function ConfusionMatrixVisualization({ performanceMatrix }) {
  if (!performanceMatrix || performanceMatrix.length === 0) return null;

  const ConfusionMatrix = ({ matrix, label }) => {
    if (!matrix || matrix.length !== 2) return null;

    const [[tn, fp], [fn, tp]] = matrix;
    const total = tn + fp + fn + tp;
    const accuracy = total > 0 ? ((tn + tp) / total * 100).toFixed(2) : 0;
    const precision = tp + fp > 0 ? (tp / (tp + fp) * 100).toFixed(2) : 0;
    const recall = tp + fn > 0 ? (tp / (tp + fn) * 100).toFixed(2) : 0;
    const f1 = precision > 0 && recall > 0 ? (2 * (precision * recall) / (precision + recall)).toFixed(2) : 0;

    return (
      <div className="mb-6">
        <h4 className="font-headline-sm text-sm mb-4 text-on-background">{label}</h4>
        
        {/* Confusion Matrix Grid */}
        <div className="grid grid-cols-[60px_100px_100px] gap-2 mb-4 items-center justify-center sm:justify-start">
          {/* Headers */}
          <div />
          <div className="text-center font-label-md text-xs text-slate-500">Pred: 0</div>
          <div className="text-center font-label-md text-xs text-slate-500">Pred: 1</div>

          {/* True Negatives and False Positives */}
          <div className="font-label-md text-xs text-slate-500 text-right pr-2">Actual: 0</div>
          <div className="bg-secondary/10 border border-secondary/20 rounded-md p-3 text-center min-h-[50px] flex flex-col justify-center">
            <div className="text-lg font-headline-sm text-secondary">{tn}</div>
            <div className="text-[10px] font-label-md text-secondary/70">TN</div>
          </div>
          <div className="bg-error/10 border border-error/20 rounded-md p-3 text-center min-h-[50px] flex flex-col justify-center">
            <div className="text-lg font-headline-sm text-error">{fp}</div>
            <div className="text-[10px] font-label-md text-error/70">FP</div>
          </div>

          {/* False Negatives and True Positives */}
          <div className="font-label-md text-xs text-slate-500 text-right pr-2">Actual: 1</div>
          <div className="bg-error/10 border border-error/20 rounded-md p-3 text-center min-h-[50px] flex flex-col justify-center">
            <div className="text-lg font-headline-sm text-error">{fn}</div>
            <div className="text-[10px] font-label-md text-error/70">FN</div>
          </div>
          <div className="bg-secondary/10 border border-secondary/20 rounded-md p-3 text-center min-h-[50px] flex flex-col justify-center">
            <div className="text-lg font-headline-sm text-secondary">{tp}</div>
            <div className="text-[10px] font-label-md text-secondary/70">TP</div>
          </div>
        </div>

        {/* Metrics */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
          <div className="bg-primary/5 p-2 rounded-md text-center border border-primary/10">
            <p className="font-label-md text-[10px] text-slate-500 mb-1">Accuracy</p>
            <p className="font-headline-sm text-sm text-primary">{accuracy}%</p>
          </div>
          <div className="bg-[#9d6ef5]/5 p-2 rounded-md text-center border border-[#9d6ef5]/10">
            <p className="font-label-md text-[10px] text-slate-500 mb-1">Precision</p>
            <p className="font-headline-sm text-sm text-[#9d6ef5]">{precision}%</p>
          </div>
          <div className="bg-secondary/5 p-2 rounded-md text-center border border-secondary/10">
            <p className="font-label-md text-[10px] text-slate-500 mb-1">Recall</p>
            <p className="font-headline-sm text-sm text-secondary">{recall}%</p>
          </div>
          <div className="bg-pink-500/5 p-2 rounded-md text-center border border-pink-500/10">
            <p className="font-label-md text-[10px] text-slate-500 mb-1">F1-Score</p>
            <p className="font-headline-sm text-sm text-pink-600">{f1}</p>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-8 mb-8">
      <h2 className="font-headline-md text-headline-md mb-6 text-on-background">Confusion Matrices & Performance Details</h2>
      <p className="font-body-md text-on-surface-variant mb-8">Before and after mitigation performance comparison</p>

      <div className="grid grid-cols-1 gap-8">
        {performanceMatrix.map((item) => (
          <div key={item.attribute} className="bg-slate-50 border border-slate-100 rounded-lg p-6">
            <h3 className="font-headline-sm text-lg mb-6 capitalize text-on-background">{formatKey(item.attribute)} Attribute</h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {/* Before Mitigation */}
              <div>
                <div className="p-3 bg-slate-200/50 rounded-md mb-4 text-center border border-slate-200">
                  <p className="font-label-md text-[11px] text-slate-600">BEFORE MITIGATION</p>
                </div>
                <ConfusionMatrix matrix={item.confusion_matrix_before} label="Confusion Matrix" />
                {item.accuracy_before !== null && (
                  <div className="p-3 bg-primary/5 rounded-md text-center border border-primary/10">
                    <p className="font-label-md text-[11px] text-slate-500 mb-1">Overall Accuracy</p>
                    <p className="font-headline-sm text-lg text-primary">
                      {(item.accuracy_before * 100).toFixed(2)}%
                    </p>
                  </div>
                )}
              </div>

              {/* After Mitigation */}
              <div>
                <div className="p-3 bg-primary/10 rounded-md mb-4 text-center border border-primary/20">
                  <p className="font-label-md text-[11px] text-primary">AFTER MITIGATION</p>
                </div>
                <ConfusionMatrix matrix={item.confusion_matrix_after} label="Confusion Matrix" />
                {item.accuracy_after !== null && (
                  <div className="p-3 bg-primary/5 rounded-md text-center border border-primary/10">
                    <p className="font-label-md text-[11px] text-slate-500 mb-1">Overall Accuracy</p>
                    <p className="font-headline-sm text-lg text-primary">
                      {(item.accuracy_after * 100).toFixed(2)}%
                    </p>
                  </div>
                )}
              </div>
            </div>

            {/* Accuracy Delta */}
            {item.accuracy_delta !== null && (
              <div className={`mt-6 p-4 rounded-md text-center border-l-4 ${item.accuracy_delta >= 0 ? 'bg-secondary/10 border-l-secondary' : 'bg-error/10 border-l-error'}`}>
                <p className="font-label-md text-[11px] text-slate-500 mb-1">Accuracy Change</p>
                <p className={`font-headline-sm text-base ${item.accuracy_delta >= 0 ? 'text-secondary' : 'text-error'}`}>
                  {item.accuracy_delta >= 0 ? '+' : ''}{(item.accuracy_delta * 100).toFixed(2)}%
                </p>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
