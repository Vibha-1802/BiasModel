import React, { useCallback, useState } from 'react';
import { UploadCloud, File, AlertCircle, CheckCircle, Brain, Zap, BarChart3, Shield } from 'lucide-react';

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
    <div style={{ minHeight: '100vh', paddingTop: '20px', paddingBottom: '40px' }}>
      {/* Header Section */}
      <div style={{ maxWidth: '900px', margin: '0 auto', paddingBottom: '60px', textAlign: 'center' }}>
        <h1 className="text-2xl font-bold mb-4">AI Bias Detection & Mitigation</h1>
        <p style={{ fontSize: '1.05rem', color: 'var(--text-secondary)', maxWidth: '700px', margin: '0 auto' }}>
          Detect, analyze, and mitigate bias in your machine learning models with advanced fairness metrics and AI-powered insights.
        </p>
      </div>

      {/* Main Upload Section */}
      <div className="glass-panel" style={{ padding: '48px', maxWidth: '700px', margin: '0 auto 60px', textAlign: 'center' }}>
        <div style={{ marginBottom: '32px' }}>
          <h2 className="text-xl font-bold mb-2">Upload Your Dataset</h2>
          <p style={{ color: 'var(--text-secondary)' }}>CSV format with labeled predictions and demographic attributes</p>
        </div>

        <div 
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          style={{
            border: `2px dashed ${dragActive ? 'var(--accent-blue)' : 'var(--border-glass)'}`,
            borderRadius: '12px',
            padding: '48px 24px',
            backgroundColor: dragActive ? 'rgba(79, 122, 255, 0.03)' : 'rgba(255, 255, 255, 0.01)',
            transition: 'all 0.2s',
            cursor: 'pointer',
            position: 'relative'
          }}
          onClick={() => document.getElementById('file-upload').click()}
        >
          <input 
            id="file-upload" 
            type="file" 
            accept=".csv" 
            onChange={handleChange} 
            style={{ display: 'none' }} 
          />
          
          {file ? (
            <div className="flex flex-col items-center gap-4">
              <File size={48} className="text-blue" />
              <div>
                <p className="font-medium text-lg">{file.name}</p>
                <p className="text-sm">{(file.size / 1024).toFixed(1)} KB</p>
              </div>
              <button 
                className="btn-primary mt-4" 
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
              <UploadCloud size={48} style={{ color: 'var(--text-secondary)' }} />
              <div>
                <p className="text-lg font-medium">Drag and drop your CSV here</p>
                <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>or click to browse files</p>
              </div>
            </div>
          )}
        </div>

        {error && (
          <div className="mt-8 flex items-center gap-2 bg-red-soft p-4" style={{ borderRadius: '8px' }}>
            <AlertCircle size={20} style={{ color: 'var(--accent-red)', flexShrink: 0 }} />
            <p style={{ color: 'var(--accent-red)', margin: 0, fontSize: '0.95rem' }}>{error}</p>
          </div>
        )}

        {isLoading && (
          <div className="mt-8 animate-fade-in">
            <p className="mb-4" style={{ color: 'var(--accent-blue)', fontWeight: 500 }}>Processing dataset and analyzing fairness metrics...</p>
            <div style={{ width: '100%', height: '3px', background: 'var(--bg-secondary)', borderRadius: '2px', overflow: 'hidden' }}>
              <div style={{ 
                width: '50%', 
                height: '100%', 
                background: 'var(--accent-blue)', 
                animation: 'loading 1.5s infinite ease-in-out',
                borderRadius: '2px'
              }}></div>
            </div>
          </div>
        )}
      </div>

      {/* Features Section */}
      <div style={{ maxWidth: '1000px', margin: '0 auto', paddingBottom: '60px' }}>
        <h2 className="text-xl font-bold text-center mb-12">How It Works</h2>
        <div className="grid grid-cols-1 gap-6" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))' }}>
          {features.map((feature, idx) => {
            const Icon = feature.icon;
            return (
              <div key={idx} className="glass-panel" style={{ padding: '32px' }}>
                <div style={{ marginBottom: '16px' }}>
                  <Icon size={32} style={{ color: 'var(--accent-blue)' }} />
                </div>
                <h3 className="text-sm font-bold mb-2">{feature.title}</h3>
                <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: '1.5', margin: 0 }}>
                  {feature.description}
                </p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Key Metrics Section */}
      <div className="glass-panel" style={{ maxWidth: '900px', margin: '0 auto', padding: '40px' }}>
        <h2 className="text-xl font-bold mb-6">What We Measure</h2>
        <div className="grid grid-cols-1 gap-6" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))' }}>
          <div style={{ paddingBottom: '24px', borderBottom: '1px solid var(--border-glass)' }}>
            <h4 className="font-bold mb-2" style={{ color: 'var(--accent-blue)' }}>Statistical Parity Difference</h4>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', margin: 0 }}>
              Measures if positive outcomes occur at equal rates across protected groups. Ideally close to 0.
            </p>
          </div>
          <div style={{ paddingBottom: '24px', borderBottom: '1px solid var(--border-glass)' }}>
            <h4 className="font-bold mb-2" style={{ color: 'var(--accent-green)' }}>Disparate Impact Ratio</h4>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', margin: 0 }}>
              Compares hiring/acceptance rates across groups. The 80% rule suggests ratio ≥ 0.8.
            </p>
          </div>
          <div style={{ paddingBottom: '24px', borderBottom: '1px solid var(--border-glass)' }}>
            <h4 className="font-bold mb-2" style={{ color: 'var(--accent-purple)' }}>Equalized Odds Difference</h4>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', margin: 0 }}>
              Ensures false positive and false negative rates are equal across groups. Ideally close to 0.
            </p>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes loading {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(200%); }
        }
        .spinner {
          width: 14px;
          height: 14px;
          border: 2px solid rgba(255,255,255,0.2);
          border-top-color: #fff;
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }
        @keyframes spin { 100% { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
}
