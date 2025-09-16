import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Target,
  BookOpen,
  Users,
  TrendingUp,
  Calendar,
  Award,
  Clock,
  CheckCircle,
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { useAuth } from '../contexts/AuthContext';
import { pmsAPI, emmAPI } from '../services/api';

const Dashboard = () => {
  const { user, hasRole } = useAuth();
  const [pmsData, setPmsData] = useState(null);
  const [emmData, setEmmData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const promises = [];
        
        // Fetch PMS data if user has access
        if (hasRole('Staff Member') || hasRole('Supervisor') || hasRole('HR Admin')) {
          promises.push(pmsAPI.getDashboard());
        }
        
        // Fetch EMM data if user has access
        if (hasRole('Staff Member') || hasRole('Exam Administrator') || hasRole('HR Admin')) {
          promises.push(emmAPI.getDashboard());
        }

        const results = await Promise.allSettled(promises);
        
        if (results[0]?.status === 'fulfilled') {
          setPmsData(results[0].value.data);
        }
        
        if (results[1]?.status === 'fulfilled') {
          setEmmData(results[1].value.data);
        }
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, [hasRole]);

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
          <div className="h-8 bg-gray-200 rounded w-1/4"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="p-6 space-y-6"
    >
      {/* Header */}
      <motion.div variants={itemVariants}>
        <h1 className="text-3xl font-bold text-gray-900">
          Welcome back, {user?.first_name}!
        </h1>
        <p className="text-gray-600 mt-2">
          Here's an overview of your performance and exam activities.
        </p>
      </motion.div>

      {/* Quick Stats */}
      <motion.div
        variants={itemVariants}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
      >
        {/* PMS Stats */}
        {pmsData && (
          <>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  Total Evaluations
                </CardTitle>
                <Target className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {pmsData.stats?.total_evaluations || 0}
                </div>
                <p className="text-xs text-muted-foreground">
                  {pmsData.stats?.completed_evaluations || 0} completed
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
                  {pmsData.stats?.pending_evaluations || 0}
                </div>
                <p className="text-xs text-muted-foreground">
                  Require your attention
                </p>
              </CardContent>
            </Card>
          </>
        )}

        {/* EMM Stats */}
        {emmData && (
          <>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  Available Exams
                </CardTitle>
                <BookOpen className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {emmData.stats?.available_exams || 0}
                </div>
                <p className="text-xs text-muted-foreground">
                  Ready to take
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
                  {emmData.stats?.average_score?.toFixed(1) || '0.0'}%
                </div>
                <p className="text-xs text-muted-foreground">
                  Across all exams
                </p>
              </CardContent>
            </Card>
          </>
        )}
      </motion.div>

      {/* Recent Activities */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent PMS Activities */}
        {pmsData && (
          <motion.div variants={itemVariants}>
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Target className="mr-2 h-5 w-5" />
                  Recent Evaluations
                </CardTitle>
                <CardDescription>
                  Your latest performance evaluations
                </CardDescription>
              </CardHeader>
              <CardContent>
                {pmsData.stats?.recent_evaluations?.length > 0 ? (
                  <div className="space-y-4">
                    {pmsData.stats.recent_evaluations.slice(0, 3).map((evaluation) => (
                      <div
                        key={evaluation.id}
                        className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                      >
                        <div>
                          <p className="font-medium">
                            {evaluation.quarter} {evaluation.year}
                          </p>
                          <p className="text-sm text-gray-600">
                            Status: {evaluation.status}
                          </p>
                        </div>
                        <Badge
                          variant={
                            evaluation.status === 'Completed'
                              ? 'default'
                              : evaluation.status === 'In Progress'
                              ? 'secondary'
                              : 'outline'
                          }
                        >
                          {evaluation.status}
                        </Badge>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-center py-4">
                    No recent evaluations
                  </p>
                )}
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Recent EMM Activities */}
        {emmData && (
          <motion.div variants={itemVariants}>
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <BookOpen className="mr-2 h-5 w-5" />
                  Recent Exam Results
                </CardTitle>
                <CardDescription>
                  Your latest exam submissions
                </CardDescription>
              </CardHeader>
              <CardContent>
                {emmData.stats?.recent_submissions?.length > 0 ? (
                  <div className="space-y-4">
                    {emmData.stats.recent_submissions.slice(0, 3).map((submission) => (
                      <div
                        key={submission.id}
                        className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                      >
                        <div>
                          <p className="font-medium">
                            Exam #{submission.exam_id}
                          </p>
                          <p className="text-sm text-gray-600">
                            Score: {submission.percentage?.toFixed(1) || 'N/A'}%
                          </p>
                        </div>
                        <Badge
                          variant={
                            submission.status === 'Completed'
                              ? 'default'
                              : 'secondary'
                          }
                        >
                          {submission.status}
                        </Badge>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-center py-4">
                    No recent exam submissions
                  </p>
                )}
              </CardContent>
            </Card>
          </motion.div>
        )}
      </div>

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
              {hasRole('Staff Member') && (
                <>
                  <Button
                    variant="outline"
                    className="h-20 flex flex-col items-center justify-center space-y-2"
                    onClick={() => window.location.href = '/pms/evaluations'}
                  >
                    <Target className="h-6 w-6" />
                    <span>View Evaluations</span>
                  </Button>
                  
                  <Button
                    variant="outline"
                    className="h-20 flex flex-col items-center justify-center space-y-2"
                    onClick={() => window.location.href = '/emm/exams'}
                  >
                    <BookOpen className="h-6 w-6" />
                    <span>Take Exam</span>
                  </Button>
                </>
              )}
              
              {hasRole('HR Admin') && (
                <Button
                  variant="outline"
                  className="h-20 flex flex-col items-center justify-center space-y-2"
                  onClick={() => window.location.href = '/users'}
                >
                  <Users className="h-6 w-6" />
                  <span>Manage Users</span>
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  );
};

export default Dashboard;

