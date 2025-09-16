import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import {
  Target,
  TrendingUp,
  Clock,
  CheckCircle,
  Users,
  Calendar,
  Award,
  BarChart3,
  Plus,
  Eye,
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { useAuth } from '../../contexts/AuthContext';
import { pmsAPI } from '../../services/api';

const PMSDashboard = () => {
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
      const response = await pmsAPI.getDashboard();
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
        <h1 className="text-3xl font-bold text-gray-900">Performance Management</h1>
        <p className="text-gray-600 mt-2">
          Track your performance evaluations and goals
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
              Total Evaluations
            </CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats.total_evaluations || 0}
            </div>
            <p className="text-xs text-muted-foreground">
              {stats.completed_evaluations || 0} completed
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Active Goals
            </CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats.active_goals || 0}
            </div>
            <p className="text-xs text-muted-foreground">
              {stats.agreed_goals || 0} agreed upon
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Average Score
            </CardTitle>
            <Award className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats.average_score?.toFixed(1) || '0.0'}
            </div>
            <p className="text-xs text-muted-foreground">
              Out of 5.0
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Pending Reviews
            </CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats.pending_evaluations || 0}
            </div>
            <p className="text-xs text-muted-foreground">
              Require attention
            </p>
          </CardContent>
        </Card>
      </motion.div>

      {/* Recent Evaluations */}
      <motion.div variants={itemVariants}>
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="flex items-center">
                  <Target className="mr-2 h-5 w-5" />
                  Recent Evaluations
                </CardTitle>
                <CardDescription>
                  Your latest performance evaluations
                </CardDescription>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => navigate('/pms/evaluations')}
              >
                <Eye className="mr-2 h-4 w-4" />
                View All
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {stats.recent_evaluations?.length > 0 ? (
              <div className="space-y-4">
                {stats.recent_evaluations.slice(0, 3).map((evaluation) => (
                  <div
                    key={evaluation.id}
                    className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer"
                    onClick={() => navigate(`/pms/evaluations/${evaluation.id}`)}
                  >
                    <div className="flex items-center space-x-4">
                      <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                        <Target className="h-5 w-5 text-blue-600" />
                      </div>
                      <div>
                        <p className="font-medium">
                          {evaluation.quarter} {evaluation.year}
                        </p>
                        <p className="text-sm text-gray-600">
                          {evaluation.goals?.length || 0} goals
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-3">
                      {evaluation.final_score && (
                        <div className="text-right">
                          <p className="font-semibold">
                            {evaluation.final_score.toFixed(1)}/5.0
                          </p>
                          <Progress 
                            value={(evaluation.final_score / 5) * 100} 
                            className="w-16 h-2"
                          />
                        </div>
                      )}
                      <Badge variant={
                        evaluation.status === 'Completed' ? 'default' :
                        evaluation.status === 'In Progress' ? 'secondary' : 'outline'
                      }>
                        {evaluation.status}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <Target className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  No evaluations yet
                </h3>
                <p className="text-gray-600 mb-4">
                  Start by creating your first performance evaluation.
                </p>
                <Button onClick={() => navigate('/pms/evaluations')}>
                  <Plus className="mr-2 h-4 w-4" />
                  Create Evaluation
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
                Your performance over time
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {stats.performance_trends.map((trend, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">{trend.period}</p>
                      <p className="text-sm text-gray-600">
                        {trend.goals_count} goals
                      </p>
                    </div>
                    <div className="flex items-center space-x-3">
                      <div className="text-right">
                        <p className="font-semibold">
                          {trend.average_score.toFixed(1)}/5.0
                        </p>
                        <Progress 
                          value={(trend.average_score / 5) * 100} 
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
                onClick={() => navigate('/pms/evaluations')}
              >
                <Target className="h-6 w-6" />
                <span>View Evaluations</span>
              </Button>
              
              <Button
                variant="outline"
                className="h-20 flex flex-col items-center justify-center space-y-2"
                onClick={() => navigate('/pms/goals')}
              >
                <CheckCircle className="h-6 w-6" />
                <span>Manage Goals</span>
              </Button>
              
              {hasRole('Supervisor') && (
                <Button
                  variant="outline"
                  className="h-20 flex flex-col items-center justify-center space-y-2"
                  onClick={() => navigate('/pms/team')}
                >
                  <Users className="h-6 w-6" />
                  <span>Team Reviews</span>
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Upcoming Deadlines */}
      {stats.upcoming_deadlines?.length > 0 && (
        <motion.div variants={itemVariants}>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Calendar className="mr-2 h-5 w-5" />
                Upcoming Deadlines
              </CardTitle>
              <CardDescription>
                Important dates to remember
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {stats.upcoming_deadlines.map((deadline, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg border border-yellow-200"
                  >
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-yellow-100 rounded-full flex items-center justify-center">
                        <Clock className="h-4 w-4 text-yellow-600" />
                      </div>
                      <div>
                        <p className="font-medium">{deadline.title}</p>
                        <p className="text-sm text-gray-600">{deadline.description}</p>
                      </div>
                    </div>
                    <Badge variant="outline" className="border-yellow-300 text-yellow-700">
                      {deadline.due_date}
                    </Badge>
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

export default PMSDashboard;

