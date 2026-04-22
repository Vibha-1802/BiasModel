import React from 'react';
import { Database, Columns, Target } from 'lucide-react';
import { formatKey } from '../utils/formatters';

export default function DatasetOverview({ data }) {
  if (!data) return null;

  return (
    <div className="glass-card mb-8">
      <h2 className="text-xl font-bold mb-6">Dataset Fundamentals</h2>
      <div className="grid grid-cols-3 gap-6">
        <div className="flex items-center gap-4">
          <div style={{ padding: '12px', background: 'rgba(59, 130, 246, 0.1)', borderRadius: '12px', color: 'var(--accent-blue)' }}>
            <Database size={24} />
          </div>
          <div>
            <p className="text-sm">Total Rows</p>
            <p className="text-2xl font-bold">{data.rows?.toLocaleString()}</p>
          </div>
        </div>
        
        <div className="flex items-center gap-4">
          <div style={{ padding: '12px', background: 'rgba(16, 185, 129, 0.1)', borderRadius: '12px', color: 'var(--accent-green)' }}>
            <Columns size={24} />
          </div>
          <div>
            <p className="text-sm">Total Columns</p>
            <p className="text-2xl font-bold">{data.columns?.toLocaleString()}</p>
          </div>
        </div>
        
        <div className="flex items-center gap-4">
          <div style={{ padding: '12px', background: 'rgba(139, 92, 246, 0.1)', borderRadius: '12px', color: 'var(--accent-purple)' }}>
            <Target size={24} />
          </div>
          <div>
            <p className="text-sm">Target Column</p>
            <p className="text-xl font-bold">{formatKey(data.target_column)}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
