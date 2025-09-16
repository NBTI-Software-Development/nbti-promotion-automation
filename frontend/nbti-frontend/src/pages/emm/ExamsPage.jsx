import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import {
  BookOpen,
  Clock,
  Users,
  Calendar,
  Play,
  Eye,
  Search,
  Filter,
  CheckCircle,
  AlertCircle,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useAuth } from '../../contexts/AuthContext';
import { emmAPI } from '../../services/api';

const ExamsPage = () => {
  const { user, hasRole } = useAuth();
  const navigate = useNavigate();
  const [exams, setExams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [error, setError] = useState('');

  useEffect(() => {
    fetchExams();
  }, [statusFilter]);

  const fetchExams = async () => {
    try {
      setLoading(true);
      const params = {};
      if (statusFilter !== 'all') params.status = statusFilter;

      const response = await emmAPI.getExams(params);
      setExams(response.data.exams);
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to load exams');
    } finally {
      setLoading(false);
    }
  };

  const handleStartExam = async (examId) => {
    try {
      const response = await emmAPI.startExam(examId);
      const submissionId = response.data.submission_id;
      navigate(`/emm/exams/${examId}/take/${submissionId}`);
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to start exam');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'Active':
        return 'default';
      case 'Scheduled':
        return 'secondary';
      case 'Completed':
        return 'outline';
      case 'Draft':
        return 'outline';
      default:
        return 'outline';
    }
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'Easy':
        return 'bg-green-100 text-green-800';
      case 'Medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'Hard':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const filteredExams = exams.filter(exam =>
    exam.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    exam.description?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        duration: 0.5,
      },
    },
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="p-6 space-y-6"
    >
      {/* Header */}
      <motion.div variants={itemVariants} className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Available Exams</h1>
          <p className="text-gray-600 mt-2">
            Take exams to demonstrate your knowledge and skills
          </p>
        </div>
        
        {hasRole('Exam Administrator') && (
          <Button onClick={() => navigate('/emm/manage')}>
            <BookOpen className="mr-2 h-4 w-4" />
            Manage Exams
          </Button>
        )}
      </motion.div>

      {error && (
        <motion.div variants={itemVariants}>
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        </motion.div>
      )}

      {/* Filters */}
      <motion.div variants={itemVariants}>
        <Card>
          <CardContent className="pt-6">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                  <Input
                    placeholder="Search exams..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>
              
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="w-full sm:w-[180px]">
                  <SelectValue placeholder="Filter by status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Statuses</SelectItem>
                  <SelectItem value="Active">Active</SelectItem>
                  <SelectItem value="Scheduled">Scheduled</SelectItem>
                  <SelectItem value="Completed">Completed</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Exams List */}
      <motion.div variants={itemVariants}>
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, i) => (
              <Card key={i} className="animate-pulse">
                <CardHeader>
                  <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                  <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="h-3 bg-gray-200 rounded"></div>
                    <div className="h-3 bg-gray-200 rounded w-2/3"></div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : filteredExams.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredExams.map((exam) => (
              <motion.div
                key={exam.id}
                whileHover={{ y: -2 }}
                transition={{ duration: 0.2 }}
              >
                <Card className="cursor-pointer hover:shadow-lg transition-shadow h-full">
                  <CardHeader className="pb-3">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <CardTitle className="text-lg line-clamp-2">
                          {exam.title}
                        </CardTitle>
                        <CardDescription className="mt-2 line-clamp-2">
                          {exam.description}
                        </CardDescription>
                      </div>
                      <Badge variant={getStatusColor(exam.status)}>
                        {exam.status}
                      </Badge>
                    </div>
                  </CardHeader>
                  
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div className="flex items-center text-gray-600">
                        <Clock className="mr-1 h-3 w-3" />
                        {exam.duration} min
                      </div>
                      <div className="flex items-center text-gray-600">
                        <BookOpen className="mr-1 h-3 w-3" />
                        {exam.total_questions} questions
                      </div>
                      <div className="flex items-center text-gray-600">
                        <Users className="mr-1 h-3 w-3" />
                        {exam.attempts_count || 0} attempts
                      </div>
                      <div className="flex items-center text-gray-600">
                        <Calendar className="mr-1 h-3 w-3" />
                        {exam.passing_score}% to pass
                      </div>
                    </div>

                    {exam.difficulty && (
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">Difficulty:</span>
                        <Badge className={getDifficultyColor(exam.difficulty)}>
                          {exam.difficulty}
                        </Badge>
                      </div>
                    )}

                    {exam.start_time && exam.end_time && (
                      <div className="text-xs text-gray-500 bg-gray-50 p-2 rounded">
                        <div>Start: {new Date(exam.start_time).toLocaleString()}</div>
                        <div>End: {new Date(exam.end_time).toLocaleString()}</div>
                      </div>
                    )}

                    {/* User's best score if available */}
                    {exam.user_best_score !== undefined && (
                      <div className="flex items-center justify-between p-2 bg-blue-50 rounded">
                        <span className="text-sm text-blue-700">Your best score:</span>
                        <div className="flex items-center">
                          <span className="font-semibold text-blue-800">
                            {exam.user_best_score.toFixed(1)}%
                          </span>
                          {exam.user_best_score >= exam.passing_score && (
                            <CheckCircle className="ml-1 h-4 w-4 text-green-600" />
                          )}
                        </div>
                      </div>
                    )}

                    <div className="flex space-x-2 pt-2">
                      {exam.status === 'Active' && (
                        <Button
                          className="flex-1"
                          onClick={() => handleStartExam(exam.id)}
                        >
                          <Play className="mr-2 h-4 w-4" />
                          Start Exam
                        </Button>
                      )}
                      
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => navigate(`/emm/exams/${exam.id}`)}
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        ) : (
          <Card>
            <CardContent className="text-center py-12">
              <BookOpen className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                No exams found
              </h3>
              <p className="text-gray-600">
                {searchTerm || statusFilter !== 'all'
                  ? 'Try adjusting your search or filters.'
                  : 'No exams are currently available.'}
              </p>
            </CardContent>
          </Card>
        )}
      </motion.div>
    </motion.div>
  );
};

export default ExamsPage;

