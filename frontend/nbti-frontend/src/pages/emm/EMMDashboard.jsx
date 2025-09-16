import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import {
  BookOpen,
  TrendingUp,
  Clock,
  Award,
  Target,
  Calendar,
  BarChart3,
  Play,
  Eye,
  Plus,
  Users,
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { useAuth } from '../../contexts/AuthContext';
import { emmAPI } from '../../services/api';

const EMMDashboard = () => {
  const { user, hasRole } = useAuth();
  const navigate = useNavigate();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const response = await emmAPI.getDashboard();
      setDashboardData(response.data);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

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

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  const stats = dashboardData?.stats || {};

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="p-6 space-y-6"
    >
      {/* Header */}
      <motion.div variants={itemVariants}>
        <h1 className="text-3xl font-bold text-gray-900">Exam Management</h1>
        <p className="text-gray-600 mt-2">
          Track your exam performance and available assessments
        </p>
      </motion.div>

      {/* Quick Stats */}
      <motion.div
        variants={itemVariants}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
      >
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Available Exams
            </CardTitle>
            <BookOpen className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats.available_exams || 0}
            </div>
            <p className="text-xs text-muted-foreground">
              Ready to take
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Completed Exams
            </CardTitle>
            <Award className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats.completed_exams || 0}
            </div>
            <p className="text-xs text-muted-foreground">
              {stats.passed_exams || 0} passed
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Average Score
            </CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats.average_score?.toFixed(1) || '0.0'}%
            </div>
            <p className="text-xs text-muted-foreground">
              Across all exams
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Study Time
            </CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats.total_study_time || '0h'}
            </div>
            <p className="text-xs text-muted-foreground">
              This month
            </p>
          </CardContent>
        </Card>
      </motion.div>

      {/* Recent Exam Results */}
      <motion.div variants={itemVariants}>
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="flex items-center">
                  <BarChart3 className="mr-2 h-5 w-5" />
                  Recent Exam Results
                </CardTitle>
                <CardDescription>
                  Your latest exam submissions and scores
                </CardDescription>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => navigate('/emm/results')}
              >
                <Eye className="mr-2 h-4 w-4" />
                View All
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {stats.recent_submissions?.length > 0 ? (
              <div className="space-y-4">
                {stats.recent_submissions.slice(0, 5).map((submission) => (
                  <div
                    key={submission.id}
                    className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer"
                    onClick={() => navigate(`/emm/results/${submission.id}`)}
                  >
                    <div className="flex items-center space-x-4">
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                        submission.percentage >= submission.passing_score
                          ? 'bg-green-100'
                          : 'bg-red-100'
                      }`}>
                        {submission.percentage >= submission.passing_score ? (
                          <Award className="h-5 w-5 text-green-600" />
                        ) : (
                          <Target className="h-5 w-5 text-red-600" />
                        )}
                      </div>
                      <div>
                        <p className="font-medium">{submission.exam_title}</p>
                        <p className="text-sm text-gray-600">
                          Completed {new Date(submission.submitted_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-3">
                      <div className="text-right">
                        <p className={`font-semibold ${
                          submission.percentage >= submission.passing_score
                            ? 'text-green-600'
                            : 'text-red-600'
                        }`}>
                          {submission.percentage.toFixed(1)}%
                        </p>
                        <Progress 
                          value={submission.percentage} 
                          className="w-16 h-2"
                        />
                      </div>
                      <Badge variant={
                        submission.percentage >= submission.passing_score
                          ? 'default'
                          : 'destructive'
                      }>
                        {submission.percentage >= submission.passing_score ? 'Passed' : 'Failed'}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <BookOpen className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  No exam results yet
                </h3>
                <p className="text-gray-600 mb-4">
                  Take your first exam to see results here.
                </p>
                <Button onClick={() => navigate('/emm/exams')}>
                  <Play className="mr-2 h-4 w-4" />
                  Browse Exams
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>

      {/* Performance Trends */}
      {stats.performance_trends && (
        <motion.div variants={itemVariants}>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <TrendingUp className="mr-2 h-5 w-5" />
                Performance Trends
              </CardTitle>
              <CardDescription>
                Your exam performance over time
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {stats.performance_trends.map((trend, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">{trend.period}</p>
                      <p className="text-sm text-gray-600">
                        {trend.exams_taken} exams taken
                      </p>
                    </div>
                    <div className="flex items-center space-x-3">
                      <div className="text-right">
                        <p className="font-semibold">
                          {trend.average_score.toFixed(1)}%
                        </p>
                        <Progress 
                          value={trend.average_score} 
                          className="w-20 h-2"
                        />
                      </div>
                      <div className={`flex items-center ${
                        trend.trend === 'up' ? 'text-green-600' :
                        trend.trend === 'down' ? 'text-red-600' : 'text-gray-600'
                      }`}>
                        <TrendingUp className={`h-4 w-4 ${
                          trend.trend === 'down' ? 'rotate-180' : ''
                        }`} />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Quick Actions */}
      <motion.div variants={itemVariants}>
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>
              Common tasks you might want to perform
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Button
                variant="outline"
                className="h-20 flex flex-col items-center justify-center space-y-2"
                onClick={() => navigate('/emm/exams')}
              >
                <Play className="h-6 w-6" />
                <span>Take Exam</span>
              </Button>
              
              <Button
                variant="outline"
                className="h-20 flex flex-col items-center justify-center space-y-2"
                onClick={() => navigate('/emm/results')}
              >
                <BarChart3 className="h-6 w-6" />
                <span>View Results</span>
              </Button>
              
              {hasRole('Exam Administrator') && (
                <Button
                  variant="outline"
                  className="h-20 flex flex-col items-center justify-center space-y-2"
                  onClick={() => navigate('/emm/manage')}
                >
                  <Users className="h-6 w-6" />
                  <span>Manage Exams</span>
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Upcoming Exams */}
      {stats.upcoming_exams?.length > 0 && (
        <motion.div variants={itemVariants}>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Calendar className="mr-2 h-5 w-5" />
                Upcoming Exams
              </CardTitle>
              <CardDescription>
                Scheduled exams you can prepare for
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {stats.upcoming_exams.map((exam, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-3 bg-blue-50 rounded-lg border border-blue-200"
                  >
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                        <Calendar className="h-4 w-4 text-blue-600" />
                      </div>
                      <div>
                        <p className="font-medium">{exam.title}</p>
                        <p className="text-sm text-gray-600">
                          {exam.duration} minutes • {exam.total_questions} questions
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <Badge variant="outline" className="border-blue-300 text-blue-700">
                        {exam.start_date}
                      </Badge>
                      <p className="text-xs text-gray-500 mt-1">
                        {exam.start_time}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Study Recommendations */}
      {stats.study_recommendations?.length > 0 && (
        <motion.div variants={itemVariants}>
          <Card>
            <CardHeader>
              <CardTitle>Study Recommendations</CardTitle>
              <CardDescription>
                Areas where you can improve your performance
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {stats.study_recommendations.map((recommendation, index) => (
                  <div
                    key={index}
                    className="flex items-start space-x-3 p-3 bg-yellow-50 rounded-lg border border-yellow-200"
                  >
                    <div className="w-8 h-8 bg-yellow-100 rounded-full flex items-center justify-center">
                      <Target className="h-4 w-4 text-yellow-600" />
                    </div>
                    <div className="flex-1">
                      <p className="font-medium text-yellow-800">
                        {recommendation.topic}
                      </p>
                      <p className="text-sm text-yellow-700">
                        {recommendation.description}
                      </p>
                      <p className="text-xs text-yellow-600 mt-1">
                        Current score: {recommendation.current_score}% • Target: {recommendation.target_score}%
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}
    </motion.div>
  );
};

export default EMMDashboard;

