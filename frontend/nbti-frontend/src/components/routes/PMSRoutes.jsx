import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import ProtectedRoute from '../ProtectedRoute';
import PMSDashboard from '../../pages/pms/PMSDashboard';
import EvaluationsPage from '../../pages/pms/EvaluationsPage';
import EvaluationDetailsPage from '../../pages/pms/EvaluationDetailsPage';

const PMSRoutes = () => {
  return (
    <ProtectedRoute requiredRoles={['Staff Member', 'Supervisor', 'HR Admin', 'Director']}>
      <Routes>
        {/* Default redirect to dashboard */}
        <Route index element={<Navigate to="dashboard" replace />} />
        
        {/* PMS Dashboard */}
        <Route path="dashboard" element={<PMSDashboard />} />
        
        {/* Evaluations */}
        <Route path="evaluations" element={<EvaluationsPage />} />
        <Route path="evaluations/:id" element={<EvaluationDetailsPage />} />
        
        {/* Goals - redirect to evaluations for now */}
        <Route path="goals" element={<Navigate to="../evaluations" replace />} />
        
        {/* Team management for supervisors */}
        <Route 
          path="team" 
          element={
            <ProtectedRoute requiredRoles={['Supervisor', 'HR Admin', 'Director']}>
              <div className="p-6">
                <h1 className="text-3xl font-bold text-gray-900 mb-4">Team Management</h1>
                <p className="text-gray-600">Team evaluation management features coming soon.</p>
              </div>
            </ProtectedRoute>
          } 
        />
        
        {/* Catch all - redirect to dashboard */}
        <Route path="*" element={<Navigate to="dashboard" replace />} />
      </Routes>
    </ProtectedRoute>
  );
};

export default PMSRoutes;

