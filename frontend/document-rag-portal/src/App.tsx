import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import PrivateRoute from './components/PrivateRoute';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import SingleDocumentChat from './pages/SingleDocumentChat';
import MultiDocumentChat from './pages/MultiDocumentChat';
import DocumentAnalysis from './pages/DocumentAnalysis';
import DocumentComparison from './pages/DocumentComparison';
import SystemStatus from './pages/SystemStatus';
import CacheManagement from './components/CacheManagement';
import Evaluation from './pages/Evaluation';
import './App.css';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <PrivateRoute>
            <Layout>
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/single-chat" element={<SingleDocumentChat />} />
                <Route path="/multi-chat" element={<MultiDocumentChat />} />
                <Route path="/analysis" element={<DocumentAnalysis />} />
                <Route path="/comparison" element={<DocumentComparison />} />
                <Route path="/system-status" element={<SystemStatus />} />
                <Route 
                  path="/cache-management" 
                  element={
                    <PrivateRoute requireAdmin={true}>
                      <CacheManagement />
                    </PrivateRoute>
                  } 
                />
                <Route 
                  path="/evaluation" 
                  element={
                    <PrivateRoute requireAdmin={true}>
                      <Evaluation />
                    </PrivateRoute>
                  } 
                />
              </Routes>
            </Layout>
          </PrivateRoute>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
