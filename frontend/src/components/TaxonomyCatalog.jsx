import React, { useState } from 'react';
import { ChevronDown, ChevronUp, BookOpen } from 'lucide-react';
import { formatKey } from '../utils/formatters';

export default function TaxonomyCatalog({ taxonomy }) {
  const [expandedSection, setExpandedSection] = useState(null);

  if (!taxonomy) return null;

  const {
    detection_metrics_catalog,
    mitigation_algorithms_catalog,
  } = taxonomy;

  const sections = [
    {
      id: 'detection',
      title: 'Detection Metrics Catalog',
      icon: '📊',
      description: 'All available fairness metrics for bias detection',
      items: detection_metrics_catalog || {},
    },
    {
      id: 'mitigation',
      title: 'Mitigation Algorithms Catalog',
      icon: '🔧',
      description: 'All available algorithms organized by stage',
      items: mitigation_algorithms_catalog || {},
      isNested: true,
    },
  ];

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-8 mb-8">
      <div className="flex items-center gap-3 mb-6">
        <BookOpen size={24} className="text-primary" />
        <div>
          <h2 className="font-headline-md text-headline-md text-on-background">Fairness & Mitigation Catalog</h2>
          <p className="font-body-md text-sm text-on-surface-variant">Complete reference of detection metrics and mitigation strategies</p>
        </div>
      </div>

      <div className="flex flex-col gap-4">
        {sections.map((section) => (
          <div key={section.id}>
            {/* Section Header */}
            <div
              onClick={() => setExpandedSection(expandedSection === section.id ? null : section.id)}
              className="px-5 py-4 bg-slate-50 border border-slate-200 rounded-lg cursor-pointer flex justify-between items-center transition-colors hover:bg-slate-100"
            >
              <div className="flex items-center gap-4 flex-1">
                <span className="text-2xl">{section.icon}</span>
                <div>
                  <h3 className="font-headline-sm text-lg text-on-background">{section.title}</h3>
                  <p className="font-body-md text-sm text-on-surface-variant">{section.description}</p>
                </div>
              </div>
              {expandedSection === section.id ? (
                <ChevronUp size={20} className="text-slate-400" />
              ) : (
                <ChevronDown size={20} className="text-slate-400" />
              )}
            </div>

            {/* Expanded Content */}
            {expandedSection === section.id && (
              <div className="mt-4 px-2">
                {section.isNested ? (
                  // Mitigation Algorithms (nested by stage)
                  <div className="flex flex-col gap-6">
                    {Object.entries(section.items).map(([stage, algorithms]) => (
                      <div key={stage}>
                        <h4 className="font-label-md text-[11px] font-bold text-slate-500 uppercase tracking-widest mb-3 pb-2 border-b border-slate-200">
                          {formatKey(stage)}
                        </h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          {Object.entries(algorithms).map(([algoKey, algoData]) => (
                            <div
                              key={algoKey}
                              className={`p-4 bg-white border rounded-lg ${algoData.supported_now ? 'border-secondary/30 border-l-4 border-l-secondary shadow-sm' : 'border-slate-200 border-l-4 border-l-slate-200'}`}
                            >
                              <div className="flex justify-between items-start mb-2">
                                <h5 className="font-headline-sm text-sm text-on-background">{formatKey(algoKey)}</h5>
                                {algoData.supported_now && (
                                  <span className="bg-secondary/10 text-secondary px-2 py-0.5 rounded text-[10px] font-label-md tracking-wider uppercase">
                                    ✓ Active
                                  </span>
                                )}
                              </div>
                              <p className="font-body-md text-xs text-on-surface-variant">{algoData.description}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  // Detection Metrics (flat list)
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {Object.entries(section.items).map(([metricKey, metricData]) => (
                      <div
                        key={metricKey}
                        className={`p-4 bg-white border rounded-lg ${metricData.supported_now ? 'border-secondary/30 border-l-4 border-l-secondary shadow-sm' : 'border-slate-200 border-l-4 border-l-slate-200'}`}
                      >
                        <div className="flex justify-between items-start mb-2">
                          <h5 className="font-headline-sm text-sm text-on-background">{formatKey(metricKey)}</h5>
                          {metricData.supported_now && (
                            <span className="bg-secondary/10 text-secondary px-2 py-0.5 rounded text-[10px] font-label-md tracking-wider uppercase">
                              ✓ Active
                            </span>
                          )}
                        </div>
                        <p className="font-body-md text-xs text-on-surface-variant">{metricData.description}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Legend */}
      <div className="mt-6 p-4 bg-slate-50 border border-slate-200 border-l-4 border-l-slate-400 rounded-lg">
        <p className="font-body-md text-xs text-on-surface-variant m-0 leading-relaxed">
          <span className="font-bold text-on-background">✓ Active:</span> Currently supported and can be used in bias detection/mitigation.
          <br />
          <span className="font-bold text-on-background">Inactive:</span> Not yet implemented but planned for future versions.
        </p>
      </div>
    </div>
  );
}
