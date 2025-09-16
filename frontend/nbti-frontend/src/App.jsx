import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Layout from './components/layout/Layout';
import AuthPage from './pages/AuthPage';
import Dashboard from './pages/Dashboard';
import PMSRoutes from './components/routes/PMSRoutes';
import EMMRoutes from './components/routes/EMMRoutes';
import './App.css';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Routes>
            {/* Public routes */}
            <Route path="/auth" element={<AuthPage />} />
            
            {/* Protected routes */}
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <Layout />
                </ProtectedRoute>
              }
            >
              {/* Dashboard */}
              <Route index element={<Navigate to="/dashboard" replace />} />
              <Route path="dashboard" element={<Dashboard />} />
              
              {/* PMS Routes */}
              <Route path="pms/*" element={<PMSRoutes />} />
              
              {/* EMM Routes */}
              <Route path="emm/*" element={<EMMRoutes />} />
              
              {/* User Management Routes */}
              <Route 
                path="users/*" 
                element={
                  <ProtectedRoute requiredRoles={['HR Admin', 'Director']}>
                    <div className="p-6"><h1>User Management - Coming Soon</h1></div>
                  </ProtectedRoute>
                } 
              />
              
              {/* Settings Routes */}
              <Route path="settings/*" element={<div className="p-6"><h1>Settings - Coming Soon</h1></div>} />
            </Route>
            
            {/* Catch all route */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;

