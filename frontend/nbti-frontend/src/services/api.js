import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://13.222.172.48:5000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(
            `${process.env.REACT_APP_API_URL || 'http://localhost:5000/api'}/auth/refresh`,
            {},
            {
              headers: {
                Authorization: `Bearer ${refreshToken}`,
              },
            }
          );

          const { access_token } = response.data;
          localStorage.setItem('access_token', access_token);

          // Retry the original request with new token
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (userData) => api.post('/auth/register', userData),
  logout: () => api.post('/auth/logout'),
  getMe: () => api.get('/auth/me'),
  changePassword: (passwordData) => api.post('/auth/change-password', passwordData),
  refresh: () => api.post('/auth/refresh'),
};

// User API
export const userAPI = {
  getUsers: (params) => api.get('/users', { params }),
  getUser: (id) => api.get(`/users/${id}`),
  updateUser: (id, userData) => api.put(`/users/${id}`, userData),
  deleteUser: (id) => api.delete(`/users/${id}`),
  getRoles: () => api.get('/roles'),
  createRole: (roleData) => api.post('/roles', roleData),
  assignRole: (userId, roleData) => api.post(`/users/${userId}/roles`, roleData),
  removeRole: (userId, roleId) => api.delete(`/users/${userId}/roles/${roleId}`),
  initRoles: () => api.post('/init-roles'),
};

// PMS API
export const pmsAPI = {
  // Evaluations
  getEvaluations: (params) => api.get('/pms/evaluations', { params }),
  createEvaluation: (evaluationData) => api.post('/pms/evaluations', evaluationData),
  getEvaluation: (id) => api.get(`/pms/evaluations/${id}`),
  assignSupervisor: (id, supervisorData) => api.post(`/pms/evaluations/${id}/assign-supervisor`, supervisorData),
  finalizeEvaluation: (id) => api.post(`/pms/evaluations/${id}/finalize`),
  
  // Goals
  getGoals: (evaluationId) => api.get(`/pms/evaluations/${evaluationId}/goals`),
  createGoal: (evaluationId, goalData) => api.post(`/pms/evaluations/${evaluationId}/goals`, goalData),
  agreeGoal: (goalId) => api.post(`/pms/goals/${goalId}/agree`),
  rateGoal: (goalId, ratingData) => api.post(`/pms/goals/${goalId}/rate`, ratingData),
  commentGoal: (goalId, commentData) => api.post(`/pms/goals/${goalId}/comment`, commentData),
  
  // Dashboard
  getDashboard: () => api.get('/pms/dashboard'),
};

// EMM API
export const emmAPI = {
  // Questions
  getQuestions: (params) => api.get('/emm/questions', { params }),
  createQuestion: (questionData) => api.post('/emm/questions', questionData),
  getQuestion: (id) => api.get(`/emm/questions/${id}`),
  updateQuestion: (id, questionData) => api.put(`/emm/questions/${id}`, questionData),
  
  // Exams
  getExams: (params) => api.get('/emm/exams', { params }),
  createExam: (examData) => api.post('/emm/exams', examData),
  getExam: (id) => api.get(`/emm/exams/${id}`),
  startExam: (id) => api.post(`/emm/exams/${id}/start`),
  
  // Submissions
  getSubmissions: (params) => api.get('/emm/submissions', { params }),
  getSubmission: (id) => api.get(`/emm/submissions/${id}`),
  submitAnswer: (submissionId, answerData) => api.post(`/emm/submissions/${submissionId}/answer`, answerData),
  submitExam: (submissionId) => api.post(`/emm/submissions/${submissionId}/submit`),
  
  // Dashboard
  getDashboard: () => api.get('/emm/dashboard'),
  getPromotionScores: () => api.get('/emm/integration/promotion-scores'),
};

// General API
export const generalAPI = {
  health: () => api.get('/health'),
  docs: () => api.get('/docs'),
};

export default api;

