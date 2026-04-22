import React, { useState } from 'react';
import axios from 'axios';
import UploadSection from './components/UploadSection';
import Dashboard from './components/Dashboard';
import './index.css';

function App() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);

  const handleUpload = async (file) => {
    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      // The API endpoint configured in main.py is /bias/analyze-dataset
      const response = await axios.post('http://localhost:8000/bias/analyze-dataset?response_mode=full', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const responseData = response.data;
      let downloadUrl = null;
      if (responseData?.optimal_mitigation?.mitigated_dataset_csv) {
          const csvString = responseData.optimal_mitigation.mitigated_dataset_csv;
          const blob = new Blob([csvString], { type: 'text/csv;charset=utf-8;' });
          downloadUrl = URL.createObjectURL(blob);
          delete responseData.optimal_mitigation.mitigated_dataset_csv;
      }

      setData({ ...responseData, downloadUrl });
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'Failed to analyze the dataset. Please ensure the backend is running on port 8000.');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setData(null);
    setError(null);
  };

  return (
    <div className="container">
      {!data ? (
        <UploadSection 
          onUpload={handleUpload} 
          isLoading={loading} 
          error={error} 
        />
      ) : (
        <Dashboard data={data} onReset={handleReset} />
      )}
    </div>
  );
}

export default App;
