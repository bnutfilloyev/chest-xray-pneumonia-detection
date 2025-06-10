import React, { useState, useEffect } from 'react';
import axios from 'axios';

const SimpleApiTest: React.FC = () => {
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const testApi = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      console.log('Testing API...');
      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
      console.log('API URL:', apiUrl);
      
      const response = await axios.get(`${apiUrl}/api/v1/patients/`);
      console.log('API Response:', response);
      
      setResult({
        status: response.status,
        statusText: response.statusText,
        data: response.data,
        headers: response.headers
      });
    } catch (error: any) {
      console.error('API Error:', error);
      setError({
        message: error.message,
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        isAxiosError: error.isAxiosError,
        code: error.code
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    testApi();
  }, []);

  return (
    <div style={{ padding: '20px' }}>
      <h1>Simple API Test (No React Query)</h1>
      
      <div style={{ marginBottom: '20px' }}>
        <button 
          onClick={testApi}
          disabled={loading}
          style={{ 
            backgroundColor: loading ? '#ccc' : '#007bff', 
            color: 'white', 
            padding: '10px 20px', 
            border: 'none', 
            borderRadius: '5px' 
          }}
        >
          {loading ? 'Testing...' : 'Test API'}
        </button>
      </div>

      <div>
        <h3>Environment:</h3>
        <pre style={{ backgroundColor: '#f0f0f0', padding: '10px' }}>
          REACT_APP_API_URL: {process.env.REACT_APP_API_URL || 'undefined'}
          NODE_ENV: {process.env.NODE_ENV}
        </pre>
      </div>

      {loading && (
        <div style={{ backgroundColor: '#fff3cd', padding: '20px', borderRadius: '8px' }}>
          <h3>Loading...</h3>
        </div>
      )}

      {result && (
        <div style={{ backgroundColor: '#d4edda', padding: '20px', borderRadius: '8px', marginTop: '20px' }}>
          <h3>Success Result:</h3>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}

      {error && (
        <div style={{ backgroundColor: '#f8d7da', padding: '20px', borderRadius: '8px', marginTop: '20px' }}>
          <h3>Error Result:</h3>
          <pre>{JSON.stringify(error, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};

export default SimpleApiTest;
