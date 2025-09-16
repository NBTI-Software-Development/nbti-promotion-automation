import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  ArrowLeft,
  CheckCircle,
  XCircle,
  Clock,
  Target,
  Award,
  TrendingUp,
  Download,
  Eye,
  BarChart3,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useAuth } from '../../contexts/AuthContext';
import { emmAPI } from '../../services/api';

const ExamResultsPage = () => {
  const { submissionId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  
  const [submission, setSubmission] = useState(null);
  const [exam, setExam] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchResults();
  }, [submissionId]);

  const fetchResults = async () => {
    try {
      setLoading(true);
      const response = await emmAPI.getSubmission(submissionId);
      const submissionData = response.data.submission;
      
      setSubmission(submissionData);
      
      // Fetch exam details
      const examResponse = await emmAPI.getExam(submissionData.exam_id);
      setExam(examResponse.data.exam);
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to load results');
    } finally {
      setLoading(false);
    }
  };

  const formatDuration = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
      return `${hours}h ${minutes}m ${secs}s`;
    }
    return `${minutes}m ${secs}s`;
  };

  const getScoreColor = (percentage, passingScore) => {
    if (percentage >= passingScore) return 'text-green-600';
    if (percentage >= passingScore * 0.8) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getGrade = (percentage) => {
    if (percentage >= 90) return 'A';
    if (percentage >= 80) return 'B';
    if (percentage >= 70) return 'C';
    if (percentage >= 60) return 'D';
    return 'F';
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          <div className="h-32 bg-gray-200 rounded"></div>
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-24 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <Alert variant="destructive">
          <XCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    );
  }

  const passed = submission?.percentage >= exam?.passing_score;
  const timeTaken = submission?.time_taken || 0;
  const totalQuestions = exam?.total_questions || 0;
  const correctAnswers = submission?.correct_answers || 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="p-6 space-y-6"
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate('/emm/exams')}
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Exams
          </Button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Exam Results</h1>
            <p className="text-gray-600 mt-1">{exam?.title}</p>
          </div>
        </div>
        
        <div className="flex space-x-2">
          <Button variant="outline" size="sm">
            <Download className="mr-2 h-4 w-4" />
            Download Certificate
          </Button>
          <Button variant="outline" size="sm">
            <Eye className="mr-2 h-4 w-4" />
            Review Answers
          </Button>
        </div>
      </div>

      {/* Result Summary */}
      <Card className={`border-2 ${passed ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'}`}>
        <CardContent className="pt-6">
          <div className="text-center space-y-4">
            <div className={`inline-flex items-center justify-center w-16 h-16 rounded-full ${
              passed ? 'bg-green-100' : 'bg-red-100'
            }`}>
              {passed ? (
                <CheckCircle className="h-8 w-8 text-green-600" />
              ) : (
                <XCircle className="h-8 w-8 text-red-600" />
              )}
            </div>
            
            <div>
              <h2 className={`text-2xl font-bold ${passed ? 'text-green-800' : 'text-red-800'}`}>
                {passed ? 'Congratulations!' : 'Not Passed'}
              </h2>
              <p className={`text-lg ${passed ? 'text-green-700' : 'text-red-700'}`}>
                {passed 
                  ? 'You have successfully passed this exam.'
                  : 'You did not meet the passing requirements.'
                }
              </p>
            </div>

            <div className="flex items-center justify-center space-x-8">
              <div className="text-center">
                <div className={`text-4xl font-bold ${getScoreColor(submission?.percentage, exam?.passing_score)}`}>
                  {submission?.percentage?.toFixed(1)}%
                </div>
                <div className="text-sm text-gray-600">Your Score</div>
              </div>
              
              <div className="text-center">
                <div className="text-4xl font-bold text-gray-700">
                  {getGrade(submission?.percentage)}
                </div>
                <div className="text-sm text-gray-600">Grade</div>
              </div>
              
              <div className="text-center">
                <div className="text-4xl font-bold text-blue-600">
                  {exam?.passing_score}%
                </div>
                <div className="text-sm text-gray-600">Required</div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Detailed Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Correct Answers
            </CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {correctAnswers}/{totalQuestions}
            </div>
            <Progress 
              value={(correctAnswers / totalQuestions) * 100} 
              className="mt-2"
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Time Taken
            </CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatDuration(timeTaken)}
            </div>
            <p className="text-xs text-muted-foreground">
              of {exam?.duration} minutes allowed
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Attempt Number
            </CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              #{submission?.attempt_number || 1}
            </div>
            <p className="text-xs text-muted-foreground">
              This attempt
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Completion Date
            </CardTitle>
            <Award className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-lg font-bold">
              {new Date(submission?.submitted_at).toLocaleDateString()}
            </div>
            <p className="text-xs text-muted-foreground">
              {new Date(submission?.submitted_at).toLocaleTimeString()}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Performance Breakdown */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <BarChart3 className="mr-2 h-5 w-5" />
            Performance Breakdown
          </CardTitle>
          <CardDescription>
            Detailed analysis of your exam performance
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium mb-3">Question Types</h4>
              <div className="space-y-3">
                {submission?.question_type_breakdown?.map((breakdown, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">{breakdown.type}</span>
                    <div className="flex items-center space-x-2">
                      <span className="text-sm font-medium">
                        {breakdown.correct}/{breakdown.total}
                      </span>
                      <div className="w-20">
                        <Progress 
                          value={(breakdown.correct / breakdown.total) * 100} 
                          className="h-2"
                        />
                      </div>
                      <span className="text-sm text-gray-500 w-12">
                        {((breakdown.correct / breakdown.total) * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h4 className="font-medium mb-3">Difficulty Levels</h4>
              <div className="space-y-3">
                {submission?.difficulty_breakdown?.map((breakdown, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">{breakdown.difficulty}</span>
                    <div className="flex items-center space-x-2">
                      <span className="text-sm font-medium">
                        {breakdown.correct}/{breakdown.total}
                      </span>
                      <div className="w-20">
                        <Progress 
                          value={(breakdown.correct / breakdown.total) * 100} 
                          className="h-2"
                        />
                      </div>
                      <span className="text-sm text-gray-500 w-12">
                        {((breakdown.correct / breakdown.total) * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <Separator />

          <div>
            <h4 className="font-medium mb-3">Recommendations</h4>
            <div className="space-y-2">
              {passed ? (
                <div className="flex items-start space-x-2">
                  <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-green-800">
                      Excellent performance!
                    </p>
                    <p className="text-sm text-green-700">
                      You have demonstrated strong knowledge in this subject area.
                    </p>
                  </div>
                </div>
              ) : (
                <div className="space-y-2">
                  <div className="flex items-start space-x-2">
                    <XCircle className="h-5 w-5 text-red-600 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium text-red-800">
                        Areas for improvement identified
                      </p>
                      <p className="text-sm text-red-700">
                        Consider reviewing the topics where you scored lower and retake the exam when ready.
                      </p>
                    </div>
                  </div>
                  
                  {exam?.retake_allowed && (
                    <Button 
                      className="mt-3"
                      onClick={() => navigate(`/emm/exams/${exam.id}`)}
                    >
                      Retake Exam
                    </Button>
                  )}
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Next Steps */}
      <Card>
        <CardHeader>
          <CardTitle>Next Steps</CardTitle>
          <CardDescription>
            What you can do next
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Button
              variant="outline"
              className="h-20 flex flex-col items-center justify-center space-y-2"
              onClick={() => navigate('/emm/exams')}
            >
              <Target className="h-6 w-6" />
              <span>Take More Exams</span>
            </Button>
            
            <Button
              variant="outline"
              className="h-20 flex flex-col items-center justify-center space-y-2"
              onClick={() => navigate('/emm/results')}
            >
              <BarChart3 className="h-6 w-6" />
              <span>View All Results</span>
            </Button>
            
            <Button
              variant="outline"
              className="h-20 flex flex-col items-center justify-center space-y-2"
              onClick={() => navigate('/dashboard')}
            >
              <Award className="h-6 w-6" />
              <span>Dashboard</span>
            </Button>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
};

export default ExamResultsPage;

