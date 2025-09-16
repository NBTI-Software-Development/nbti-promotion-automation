import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import ProtectedRoute from '../ProtectedRoute';
import EMMDashboard from '../../pages/emm/EMMDashboard';
import ExamsPage from '../../pages/emm/ExamsPage';
import TakeExamPage from '../../pages/emm/TakeExamPage';
import ExamResultsPage from '../../pages/emm/ExamResultsPage';

const EMMRoutes = () => {
  return (
    <ProtectedRoute requiredRoles={['Staff Member', 'Exam Administrator', 'Question Author', 'HR Admin']}>
      <Routes>
        {/* Default redirect to dashboard */}
        <Route index element={<Navigate to="dashboard" replace />} />
        
        {/* EMM Dashboard */}
        <Route path="dashboard" element={<EMMDashboard />} />
        
        {/* Exams */}
        <Route path="exams" element={<ExamsPage />} />
        <Route path="exams/:examId" element={<ExamsPage />} />
        <Route path="exams/:examId/take/:submissionId" element={<TakeExamPage />} />
        
        {/* Results */}
        <Route path="results" element={<div className="p-6"><h1>All Results - Coming Soon</h1></div>} />
        <Route path="results/:submissionId" element={<ExamResultsPage />} />
        
        {/* Question Management for authorized users */}
        <Route 
          path="questions" 
          element={
            <ProtectedRoute requiredRoles={['Question Author', 'Exam Administrator', 'HR Admin']}>
              <div className="p-6">
                <h1 className="text-3xl font-bold text-gray-900 mb-4">Question Bank</h1>
                <p className="text-gray-600">Question management features coming soon.</p>
              </div>
            </ProtectedRoute>
          } 
        />
        
        {/* Exam Management for administrators */}
        <Route 
          path="manage" 
          element={
            <ProtectedRoute requiredRoles={['Exam Administrator', 'HR Admin']}>
              <div className="p-6">
                <h1 className="text-3xl font-bold text-gray-900 mb-4">Exam Management</h1>
                <p className="text-gray-600">Exam administration features coming soon.</p>
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

export default EMMRoutes;

