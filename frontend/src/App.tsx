import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from './components/ui/toaster';
import Layout from './components/common/Layout';
import Dashboard from './pages/Dashboard';
import PatientsPage from './pages/PatientsPage';
import PredictionsPage from './pages/PredictionsPage';
import ApiTestPage from './ApiTestPage';
import SimpleApiTest from './SimpleApiTest';

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="min-h-screen">
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route
              path="/dashboard"
              element={
                <Layout>
                  <Dashboard />
                </Layout>
              }
            />
            <Route
              path="/patients"
              element={
                <Layout>
                  <PatientsPage />
                </Layout>
              }
            />
            <Route
              path="/predictions"
              element={
                <Layout>
                  <PredictionsPage />
                </Layout>
              }
            />
            <Route
              path="/test-api"
              element={<ApiTestPage />}
            />
            <Route
              path="/simple-test"
              element={<SimpleApiTest />}
            />
          </Routes>
        </div>
        <Toaster />
      </Router>
    </QueryClientProvider>
  );
}

export default App;
