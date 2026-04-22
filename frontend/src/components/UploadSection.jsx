import React, { useCallback, useState } from 'react';
import { UploadCloud, File, AlertCircle } from 'lucide-react';

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

  return (
    <div className="glass-panel" style={{ padding: '48px', maxWidth: '600px', margin: '64px auto', textAlign: 'center' }}>
      <div style={{ marginBottom: '32px' }}>
        <h1 className="text-2xl font-bold mb-2">Bias Detection Engine</h1>
        <p>Upload a dataset to evaluate fairness and apply bias mitigation.</p>
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
          backgroundColor: dragActive ? 'rgba(59, 130, 246, 0.05)' : 'rgba(255, 255, 255, 0.02)',
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
                  <div className="spinner"></div> Analyzing Dataset...
                </>
              ) : 'Analyze Dataset'}
            </button>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-4">
            <UploadCloud size={48} className="text-secondary" />
            <p className="text-lg">Drag and drop your CSV file here</p>
            <p className="text-sm">or click to browse files</p>
          </div>
        )}
      </div>

      {error && (
        <div className="mt-8 flex items-center gap-2 bg-red-soft p-4 rounded text-left" style={{ borderRadius: '8px' }}>
          <AlertCircle size={20} className="text-red" />
          <p className="text-red m-0" style={{ margin: 0 }}>{error}</p>
        </div>
      )}

      {isLoading && (
        <div className="mt-8 animate-fade-in">
          <p className="mb-4 text-blue font-medium">This may take a minute while the LLM reasons about fairness...</p>
          <div style={{ width: '100%', height: '4px', background: 'var(--bg-secondary)', borderRadius: '2px', overflow: 'hidden' }}>
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
      
      <style>{`
        @keyframes loading {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(200%); }
        }
        .spinner {
          width: 16px;
          height: 16px;
          border: 2px solid rgba(255,255,255,0.3);
          border-top-color: #fff;
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }
        @keyframes spin { 100% { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
}
