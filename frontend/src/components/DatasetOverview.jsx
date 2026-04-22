import React from 'react';
import { Database, Columns, Target } from 'lucide-react';
import { formatKey } from '../utils/formatters';

export default function DatasetOverview({ data }) {
  if (!data) return null;

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-8 mb-8">
      <h2 className="font-headline-md text-headline-md mb-6 text-on-background">Dataset Fundamentals</h2>
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
        <div className="flex items-center gap-4 bg-slate-50 p-4 rounded-lg border border-slate-100">
          <div className="p-3 bg-primary/10 rounded-lg text-primary">
            <Database size={24} />
          </div>
          <div>
            <p className="font-label-md text-sm text-slate-500 uppercase tracking-widest">Total Rows</p>
            <p className="font-headline-lg text-2xl text-on-background">{data.rows?.toLocaleString()}</p>
          </div>
        </div>
        
        <div className="flex items-center gap-4 bg-slate-50 p-4 rounded-lg border border-slate-100">
          <div className="p-3 bg-secondary/10 rounded-lg text-secondary">
            <Columns size={24} />
          </div>
          <div>
            <p className="font-label-md text-sm text-slate-500 uppercase tracking-widest">Total Columns</p>
            <p className="font-headline-lg text-2xl text-on-background">{data.columns?.toLocaleString()}</p>
          </div>
        </div>
        
        <div className="flex items-center gap-4 bg-slate-50 p-4 rounded-lg border border-slate-100">
          <div className="p-3 bg-[#9d6ef5]/10 rounded-lg text-[#9d6ef5]">
            <Target size={24} />
          </div>
          <div>
            <p className="font-label-md text-sm text-slate-500 uppercase tracking-widest">Target Column</p>
            <p className="font-headline-sm text-xl text-on-background">{formatKey(data.target_column)}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
