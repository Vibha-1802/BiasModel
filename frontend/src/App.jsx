import React, { useState } from 'react';
import axios from 'axios';
import LandingPage from './components/LandingPage';
import UploadSection from './components/UploadSection';
import Dashboard from './components/Dashboard';
import './index.css';

function App() {
  const [currentView, setCurrentView] = useState('landing'); // 'landing', 'upload', 'dashboard'
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

      setData(response.data);
      setCurrentView('dashboard');
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
    setCurrentView('upload');
  };

  return (
    <>
      {currentView === 'landing' && (
        <LandingPage onTryItNow={() => setCurrentView('upload')} />
      )}
      {currentView === 'upload' && (
        <UploadSection 
          onUpload={handleUpload} 
          isLoading={loading} 
          error={error} 
        />
      )}
      {currentView === 'dashboard' && data && (
        <Dashboard data={data} onReset={handleReset} />
      )}
    </>
  );
}

export default App;
