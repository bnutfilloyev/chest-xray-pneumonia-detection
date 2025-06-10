import React, { useState, useEffect } from 'react';
import { simpleApiService } from './services/simpleApi';

const ApiTestPage: React.FC = () => {
  const [status, setStatus] = useState<string>('Loading...');
  const [patients, setPatients] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [logs, setLogs] = useState<string[]>([]);

  const addLog = (message: string) => {
    setLogs(prev => [...prev, `${new Date().toLocaleTimeString()}: ${message}`]);
    console.log(message);
  };

  useEffect(() => {
    const testApi = async () => {
      try {
        addLog('🔄 Starting API test...');
        setStatus('Testing API connection...');
        
        addLog(`🔧 API base URL: ${process.env.REACT_APP_API_URL || 'http://localhost:8000'}`);
        
        // Test health endpoint first
        addLog('🔄 Testing health endpoint...');
        try {
          const healthResult = await simpleApiService.healthCheck();
          addLog('✅ Health check successful');
        } catch (healthError: any) {
          addLog(`❌ Health check failed: ${healthError.message}`);
        }
        
        // Test patients endpoint
        addLog('🔄 Testing patients endpoint...');
        const result = await simpleApiService.getPatients();
        addLog(`✅ API test successful: ${result.length} patients loaded`);
        
        setPatients(result);
        setStatus(`✅ Success! Loaded ${result.length} patients`);
        setError(null);
      } catch (err: any) {
        const errorMessage = err.message || 'Unknown error';
        addLog(`❌ API test failed: ${errorMessage}`);
        addLog(`❌ Error details: ${JSON.stringify({
          status: err.response?.status,
          statusText: err.response?.statusText,
          data: err.response?.data,
          url: err.config?.url
        })}`);
        setError(errorMessage);
        setStatus('❌ API test failed');
      }
    };

    testApi();
  }, []);

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>API Connection Test</h1>
      <div style={{ marginBottom: '20px' }}>
        <h3>Status: {status}</h3>
        {error && (
          <div style={{ color: 'red', backgroundColor: '#ffe6e6', padding: '10px', borderRadius: '4px' }}>
            <strong>Error:</strong> {error}
          </div>
        )}
      </div>
      
      <div style={{ marginBottom: '20px' }}>
        <h3>Logs</h3>
        <div style={{ backgroundColor: '#f5f5f5', padding: '10px', borderRadius: '4px', maxHeight: '200px', overflowY: 'scroll' }}>
          {logs.map((log, index) => (
            <div key={index}>{log}</div>
          ))}
        </div>
      </div>
      
      <div>
        <h3>Patients ({patients.length})</h3>
        {patients.length > 0 && (
          <div>
            <p>First patient:</p>
            <pre style={{ backgroundColor: '#f5f5f5', padding: '10px', borderRadius: '4px' }}>
              {JSON.stringify(patients[0], null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
};

export default ApiTestPage;
