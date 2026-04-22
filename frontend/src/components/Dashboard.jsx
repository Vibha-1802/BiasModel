import React from 'react';
import DatasetOverview from './DatasetOverview';
import FeatureStatsTable from './FeatureStatsTable';
import BiasMatrixChart from './BiasMatrixChart';
import PerformanceMetrics from './PerformanceMetrics';
import TaxonomyView from './TaxonomyView';
import { RefreshCw } from 'lucide-react';

export default function Dashboard({ data, onReset }) {
  if (!data) return null;

  return (
    <div className="animate-fade-in" style={{ paddingBottom: '64px' }}>
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-2xl font-bold">Analysis Report</h1>
          <p className="text-secondary">Bias detection and mitigation results for your dataset.</p>
        </div>
        <button className="btn-primary" onClick={onReset} style={{ backgroundColor: 'var(--bg-secondary)' }}>
          <RefreshCw size={16} /> Analyze New Dataset
        </button>
      </div>

      <DatasetOverview data={data.dataset_summary} />
      
      <div className="grid grid-cols-1 gap-8">
        <BiasMatrixChart biasMatrix={data.reporting_pack?.bias_matrix} />
        <PerformanceMetrics performanceMatrix={data.reporting_pack?.performance_matrix} />
      </div>

      <TaxonomyView taxonomy={data.fairness_taxonomy} biasPlan={data.bias_plan} />
      
      <FeatureStatsTable 
        numericalSummary={data.numerical_summary} 
        featureStats={data.feature_stats} 
      />

    </div>
  );
}
