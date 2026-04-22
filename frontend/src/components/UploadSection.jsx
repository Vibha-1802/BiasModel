import React, { useCallback, useState } from 'react';
import { UploadCloud, File, AlertCircle, Brain, Zap, BarChart3, Shield } from 'lucide-react';

export default function UploadSection({ onUpload, isLoading, error }) {
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState(null);

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile.name.endsWith('.csv')) {
        setFile(droppedFile);
      }
    }
  }, []);

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleAnalyze = () => {
    if (file) {
      onUpload(file);
    }
  };

  const features = [
    { icon: Brain, title: 'AI-Powered Analysis', description: 'LLM-driven reasoning to identify bias patterns and fairness issues' },
    { icon: BarChart3, title: 'Comprehensive Metrics', description: 'Statistical parity, disparate impact, and equalized odds analysis' },
    { icon: Zap, title: 'Automated Mitigation', description: 'Apply targeted bias reduction while preserving model accuracy' },
    { icon: Shield, title: 'Fairness Reporting', description: 'Detailed before/after metrics and actionable recommendations' }
  ];

  return (
    <div className="min-h-screen pt-16 pb-16 bg-background text-on-background px-6 max-w-[1440px] mx-auto">
      {/* Header Section */}
      <div className="max-w-[900px] mx-auto pb-16 text-center mt-12">
        <h1 className="font-headline-lg text-headline-lg mb-4 text-on-background">AI Bias Detection & Mitigation</h1>
        <p className="font-body-lg text-body-lg text-on-surface-variant max-w-[700px] mx-auto">
          Detect, analyze, and mitigate bias in your machine learning models with advanced fairness metrics and AI-powered insights.
        </p>
      </div>

      {/* Main Upload Section */}
      <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-8 max-w-[700px] mx-auto mb-16 text-center">
        <div className="mb-8">
          <h2 className="font-headline-md text-headline-md mb-2 text-on-background">Upload Your Dataset</h2>
          <p className="font-body-md text-on-surface-variant">CSV format with labeled predictions and demographic attributes</p>
        </div>

        <div 
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-xl p-12 transition-all cursor-pointer relative ${dragActive ? 'border-primary bg-primary/5' : 'border-slate-300 hover:border-primary/50 hover:bg-slate-50'}`}
          onClick={() => document.getElementById('file-upload').click()}
        >
          <input 
            id="file-upload" 
            type="file" 
            accept=".csv" 
            onChange={handleChange} 
            className="hidden" 
          />
          
          {file ? (
            <div className="flex flex-col items-center gap-4">
              <File size={48} className="text-primary" />
              <div>
                <p className="font-headline-sm text-sm font-bold text-on-background">{file.name}</p>
                <p className="font-body-md text-sm text-on-surface-variant">{(file.size / 1024).toFixed(1)} KB</p>
              </div>
              <button 
                className="bg-primary text-on-primary px-6 py-3 font-label-md uppercase tracking-wider hover:bg-on-primary-fixed-variant transition-all rounded shadow-sm mt-4 flex items-center justify-center gap-2" 
                onClick={(e) => { e.stopPropagation(); handleAnalyze(); }}
                disabled={isLoading}
              >
                {isLoading ? (
                  <>
                    <div className="spinner"></div> Analyzing...
                  </>
                ) : 'Analyze Dataset'}
              </button>
            </div>
          ) : (
            <div className="flex flex-col items-center gap-4">
              <UploadCloud size={48} className="text-slate-400" />
              <div>
                <p className="font-headline-sm text-lg font-bold text-on-background">Drag and drop your CSV here</p>
                <p className="font-body-md text-sm text-on-surface-variant">or click to browse files</p>
              </div>
            </div>
          )}
        </div>

        {error && (
          <div className="mt-8 flex items-center gap-2 bg-error-container p-4 rounded-lg">
            <AlertCircle size={20} className="text-error flex-shrink-0" />
            <p className="text-error m-0 font-body-md">{error}</p>
          </div>
        )}

        {isLoading && (
          <div className="mt-8 animate-fade-in text-left">
            <p className="mb-4 text-primary font-medium font-body-md">Processing dataset and analyzing fairness metrics...</p>
            <div className="w-full h-1 bg-surface-container-high rounded-full overflow-hidden">
              <div className="w-1/2 h-full bg-primary rounded-full animate-[loading_1.5s_infinite_ease-in-out]"></div>
            </div>
          </div>
        )}
      </div>

      {/* Features Section */}
      <div className="max-w-[1000px] mx-auto pb-16">
        <h2 className="font-headline-md text-headline-md text-center mb-12 text-on-background">How It Works</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, idx) => {
            const Icon = feature.icon;
            return (
              <div key={idx} className="bg-white p-6 border border-slate-200 flex flex-col gap-sm hover:border-primary/50 transition-all rounded-lg">
                <div className="mb-4 w-12 h-12 bg-surface-container-low flex items-center justify-center rounded">
                  <Icon size={24} className="text-primary" />
                </div>
                <h3 className="font-headline-sm text-[16px] leading-snug">{feature.title}</h3>
                <p className="font-body-md text-[14px] text-on-surface-variant m-0 mt-2">
                  {feature.description}
                </p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Key Metrics Section */}
      <div className="bg-white border border-slate-200 rounded-xl p-10 max-w-[900px] mx-auto">
        <h2 className="font-headline-md text-headline-md mb-6 text-on-background">What We Measure</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="pb-6 border-b md:border-b-0 md:border-r border-slate-200 md:pr-6">
            <h4 className="font-headline-sm text-sm uppercase tracking-tight text-primary mb-2">Statistical Parity Difference</h4>
            <p className="font-body-md text-sm text-on-surface-variant m-0">
              Measures if positive outcomes occur at equal rates across protected groups. Ideally close to 0.
            </p>
          </div>
          <div className="pb-6 border-b md:border-b-0 md:border-r border-slate-200 md:px-6">
            <h4 className="font-headline-sm text-sm uppercase tracking-tight text-secondary mb-2">Disparate Impact Ratio</h4>
            <p className="font-body-md text-sm text-on-surface-variant m-0">
              Compares hiring/acceptance rates across groups. The 80% rule suggests ratio ≥ 0.8.
            </p>
          </div>
          <div className="md:pl-6">
            <h4 className="font-headline-sm text-sm uppercase tracking-tight text-[#9d6ef5] mb-2">Equalized Odds Difference</h4>
            <p className="font-body-md text-sm text-on-surface-variant m-0">
              Ensures false positive and false negative rates are equal across groups. Ideally close to 0.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
