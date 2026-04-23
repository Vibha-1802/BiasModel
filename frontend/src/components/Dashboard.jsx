import React, { useState } from 'react';
import { RefreshCw, BarChart3, Zap, BookOpen, Database, AlertTriangle } from 'lucide-react';
import DatasetOverview from './DatasetOverview';
import FeatureStatsTable from './FeatureStatsTable';
import BiasMatrixChart from './BiasMatrixChart';
import PerformanceMetrics from './PerformanceMetrics';
import BiasPlanSummary from './BiasPlanSummary';
import MitigationStatus from './MitigationStatus';
import DetailedBiasMatrix from './DetailedBiasMatrix';
import ConfusionMatrixVisualization from './ConfusionMatrixVisualization';
import TaxonomyCatalog from './TaxonomyCatalog';
import TaxonomyView from './TaxonomyView';

export default function Dashboard({ data, onReset }) {
  const [activeTab, setActiveTab] = useState('overview');

  if (!data) return null;

  const tabs = [
    { id: 'overview', label: 'Overview', icon: Database },
    { id: 'bias-plan', label: 'Bias Analysis Plan', icon: AlertTriangle },
    { id: 'mitigation', label: 'Mitigation Pipeline', icon: Zap },
    { id: 'detailed-metrics', label: 'Detailed Metrics', icon: BarChart3 },
    { id: 'catalog', label: 'Metric Catalog', icon: BookOpen },
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview':
        return (
          <>
            <DatasetOverview data={data.dataset_summary} />
            <div className="grid grid-cols-1 gap-8 mt-8">
              <BiasMatrixChart biasMatrix={data.reporting_pack?.bias_matrix} />
              <PerformanceMetrics performanceMatrix={data.reporting_pack?.performance_matrix} />
            </div>
            <div className="mt-8">
              <FeatureStatsTable 
                numericalSummary={data.numerical_summary} 
                featureStats={data.feature_stats} 
              />
            </div>
          </>
        );
      case 'bias-plan':
        return (
          <>
            <BiasPlanSummary 
              biasPlan={data.bias_plan} 
              biasTypes={data.bias_plan?.bias_types_detected}
            />
            <div className="mt-8">
              <TaxonomyView taxonomy={data.fairness_taxonomy} biasPlan={data.bias_plan} />
            </div>
          </>
        );
      case 'mitigation':
        return (
          <>
            <MitigationStatus 
              fairlearnMitigation={data.fairlearn_mitigation} 
              reportingPack={data.reporting_pack}
            />
          </>
        );
      case 'detailed-metrics':
        return (
          <>
            <DetailedBiasMatrix biasMatrix={data.reporting_pack?.bias_matrix} />
            <div className="mt-8">
              <ConfusionMatrixVisualization performanceMatrix={data.reporting_pack?.performance_matrix} />
            </div>
          </>
        );
      case 'catalog':
        return (
          <>
            <TaxonomyCatalog taxonomy={data.fairness_taxonomy} />
          </>
        );
      default:
        return null;
    }
  };

  return (
    <div className="animate-fade-in pb-16 pt-12 px-6 max-w-[1440px] mx-auto bg-background text-on-background min-h-screen">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between md:items-center mb-8 gap-4">
        <div>
          <h1 className="font-headline-lg text-headline-lg m-0">Fairness Analysis Report</h1>
          <p className="font-body-md text-on-surface-variant mt-2">Comprehensive bias detection and mitigation analysis</p>
        </div>
<<<<<<< HEAD
        <button 
          className="bg-white border border-slate-300 text-on-surface px-6 py-2 rounded shadow-sm flex items-center justify-center gap-2 hover:bg-slate-50 transition-all font-label-md uppercase tracking-wider" 
          onClick={onReset}
        >
          <RefreshCw size={16} /> 
          <span>Analyze New Dataset</span>
        </button>
=======
        <div style={{ display: 'flex', gap: '12px' }}>
          {data.downloadUrl && (
            <a 
              href={data.downloadUrl} 
              download="mitigated_dataset.csv" 
              className="btn-primary" 
              style={{ backgroundColor: 'var(--accent-blue)', display: 'flex', alignItems: 'center', gap: '8px', textDecoration: 'none' }}
            >
              <Database size={16} /> 
              <span>Download Mitigated Data</span>
            </a>
          )}
          <button className="btn-primary" onClick={onReset} style={{ backgroundColor: 'var(--bg-secondary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <RefreshCw size={16} /> 
            <span>Analyze New Dataset</span>
          </button>
        </div>
>>>>>>> 3c7504e93760a26a1835264707e32672f04008a0
      </div>

      {/* Tab Navigation */}
      <div className="bg-white border border-slate-200 rounded-lg shadow-sm mb-8 flex flex-wrap sm:flex-nowrap overflow-hidden">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex-1 py-4 px-4 flex items-center justify-center gap-2 transition-all border-b-2 font-label-md uppercase tracking-wider text-[12px] sm:text-[14px] ${
                isActive 
                  ? 'border-primary text-primary bg-primary/5' 
                  : 'border-transparent text-slate-500 hover:bg-slate-50 hover:text-slate-700'
              }`}
            >
              <Icon size={16} />
              <span className="hidden sm:inline">{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Tab Content */}
      <div className="animate-fade-in">
        {renderTabContent()}
      </div>
    </div>
  );
}
