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
            <div className="grid grid-cols-1 gap-8">
              <BiasMatrixChart biasMatrix={data.reporting_pack?.bias_matrix} />
              <PerformanceMetrics performanceMatrix={data.reporting_pack?.performance_matrix} />
            </div>
            <FeatureStatsTable 
              numericalSummary={data.numerical_summary} 
              featureStats={data.feature_stats} 
            />
          </>
        );
      case 'bias-plan':
        return (
          <>
            <BiasPlanSummary 
              biasPlan={data.bias_plan} 
              biasTypes={data.bias_plan?.bias_types_detected}
            />
            <TaxonomyView taxonomy={data.fairness_taxonomy} biasPlan={data.bias_plan} />
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
            <ConfusionMatrixVisualization performanceMatrix={data.reporting_pack?.performance_matrix} />
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
    <div className="animate-fade-in" style={{ paddingBottom: '64px' }}>
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-2xl font-bold">Fairness Analysis Report</h1>
          <p className="text-secondary">Comprehensive bias detection and mitigation analysis</p>
        </div>
        <button className="btn-primary" onClick={onReset} style={{ backgroundColor: 'var(--bg-secondary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <RefreshCw size={16} /> 
          <span>Analyze New Dataset</span>
        </button>
      </div>

      {/* Tab Navigation */}
      <div className="glass-card mb-8" style={{ padding: '0', display: 'flex', borderRadius: '16px', overflow: 'hidden', background: 'rgba(255,255,255,0.02)' }}>
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                flex: 1,
                padding: '16px 20px',
                border: 'none',
                background: isActive ? 'rgba(59, 130, 246, 0.1)' : 'transparent',
                borderBottom: isActive ? '2px solid var(--accent-blue)' : '2px solid transparent',
                color: isActive ? 'var(--text-primary)' : 'var(--text-secondary)',
                cursor: 'pointer',
                transition: 'all 0.2s',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                fontWeight: isActive ? 600 : 500,
                fontSize: '14px',
              }}
              onMouseEnter={(e) => {
                if (!isActive) {
                  e.target.style.background = 'rgba(255,255,255,0.03)';
                }
              }}
              onMouseLeave={(e) => {
                if (!isActive) {
                  e.target.style.background = 'transparent';
                }
              }}
            >
              <Icon size={16} />
              <span>{tab.label}</span>
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
