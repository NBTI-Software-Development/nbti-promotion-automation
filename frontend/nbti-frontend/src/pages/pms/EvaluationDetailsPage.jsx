import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  ArrowLeft,
  Plus,
  Target,
  CheckCircle,
  Clock,
  User,
  MessageSquare,
  Star,
  Edit,
  Save,
  X,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useAuth } from '../../contexts/AuthContext';
import { pmsAPI } from '../../services/api';

const EvaluationDetailsPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user, hasRole } = useAuth();
  
  const [evaluation, setEvaluation] = useState(null);
  const [goals, setGoals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [editingGoal, setEditingGoal] = useState(null);
  const [newGoalDialog, setNewGoalDialog] = useState(false);

  useEffect(() => {
    fetchEvaluationDetails();
  }, [id]);

  const fetchEvaluationDetails = async () => {
    try {
      setLoading(true);
      const [evalResponse, goalsResponse] = await Promise.all([
        pmsAPI.getEvaluation(id),
        pmsAPI.getGoals(id),
      ]);
      
      setEvaluation(evalResponse.data.evaluation);
      setGoals(goalsResponse.data.goals);
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to load evaluation details');
    } finally {
      setLoading(false);
    }
  };

  const handleAddGoal = async (goalData) => {
    try {
      await pmsAPI.createGoal(id, goalData);
      setNewGoalDialog(false);
      fetchEvaluationDetails();
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to create goal');
    }
  };

  const handleAgreeGoal = async (goalId) => {
    try {
      await pmsAPI.agreeGoal(goalId);
      fetchEvaluationDetails();
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to agree on goal');
    }
  };

  const handleRateGoal = async (goalId, rating, comments) => {
    try {
      await pmsAPI.rateGoal(goalId, { rating, supervisor_comments: comments });
      fetchEvaluationDetails();
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to rate goal');
    }
  };

  const handleCommentGoal = async (goalId, comment) => {
    try {
      await pmsAPI.commentGoal(goalId, { comment });
      fetchEvaluationDetails();
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to add comment');
    }
  };

  const handleFinalizeEvaluation = async () => {
    try {
      await pmsAPI.finalizeEvaluation(id);
      fetchEvaluationDetails();
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to finalize evaluation');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'Completed':
        return 'default';
      case 'In Progress':
        return 'secondary';
      case 'Pending':
        return 'outline';
      default:
        return 'outline';
    }
  };

  const getRatingStars = (rating) => {
    return Array.from({ length: 5 }, (_, i) => (
      <Star
        key={i}
        className={`h-4 w-4 ${
          i < rating ? 'text-yellow-400 fill-current' : 'text-gray-300'
        }`}
      />
    ));
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

  if (error && !evaluation) {
    return (
      <div className="p-6">
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    );
  }

  const canEditGoals = evaluation?.status !== 'Completed' && 
    (evaluation?.staff_id === user?.id || hasRole('Supervisor') || hasRole('HR Admin'));
  
  const canRateGoals = evaluation?.supervisor_id === user?.id && evaluation?.status !== 'Completed';
  
  const canFinalize = evaluation?.supervisor_id === user?.id && 
    evaluation?.status === 'In Progress' && 
    goals.every(goal => goal.rating !== null);

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
            onClick={() => navigate('/pms/evaluations')}
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Evaluations
          </Button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              {evaluation?.quarter} {evaluation?.year} Evaluation
            </h1>
            <p className="text-gray-600 mt-1">
              Performance evaluation details and goals
            </p>
          </div>
        </div>
        
        {canFinalize && (
          <Button onClick={handleFinalizeEvaluation}>
            <CheckCircle className="mr-2 h-4 w-4" />
            Finalize Evaluation
          </Button>
        )}
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Evaluation Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Evaluation Overview</span>
            <Badge variant={getStatusColor(evaluation?.status)}>
              {evaluation?.status}
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="space-y-2">
              <Label className="text-sm font-medium text-gray-600">Period</Label>
              <p className="text-lg font-semibold">
                {evaluation?.quarter} {evaluation?.year}
              </p>
            </div>
            
            <div className="space-y-2">
              <Label className="text-sm font-medium text-gray-600">Goals</Label>
              <p className="text-lg font-semibold">
                {goals.length} goals
                {goals.length > 0 && (
                  <span className="text-sm text-gray-500 ml-2">
                    ({goals.filter(g => g.agreed).length} agreed)
                  </span>
                )}
              </p>
            </div>
            
            {evaluation?.final_score !== null && (
              <div className="space-y-2">
                <Label className="text-sm font-medium text-gray-600">Final Score</Label>
                <div className="flex items-center space-x-2">
                  <span className="text-lg font-semibold">
                    {evaluation.final_score.toFixed(1)}/5.0
                  </span>
                  <div className="flex">
                    {getRatingStars(Math.round(evaluation.final_score))}
                  </div>
                </div>
              </div>
            )}
          </div>
          
          {evaluation?.final_score !== null && (
            <div className="mt-4">
              <Label className="text-sm font-medium text-gray-600">Progress</Label>
              <Progress 
                value={(evaluation.final_score / 5) * 100} 
                className="mt-2"
              />
            </div>
          )}
        </CardContent>
      </Card>

      {/* Goals Section */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center">
              <Target className="mr-2 h-5 w-5" />
              Goals
            </CardTitle>
            {canEditGoals && (
              <Dialog open={newGoalDialog} onOpenChange={setNewGoalDialog}>
                <DialogTrigger asChild>
                  <Button size="sm">
                    <Plus className="mr-2 h-4 w-4" />
                    Add Goal
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Add New Goal</DialogTitle>
                    <DialogDescription>
                      Create a new performance goal for this evaluation period.
                    </DialogDescription>
                  </DialogHeader>
                  <NewGoalForm onSubmit={handleAddGoal} />
                </DialogContent>
              </Dialog>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {goals.length > 0 ? (
            <div className="space-y-4">
              {goals.map((goal) => (
                <GoalCard
                  key={goal.id}
                  goal={goal}
                  canEdit={canEditGoals}
                  canRate={canRateGoals}
                  canComment={evaluation?.staff_id === user?.id}
                  onAgree={() => handleAgreeGoal(goal.id)}
                  onRate={(rating, comments) => handleRateGoal(goal.id, rating, comments)}
                  onComment={(comment) => handleCommentGoal(goal.id, comment)}
                />
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Target className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                No goals yet
              </h3>
              <p className="text-gray-600 mb-4">
                Start by adding your first performance goal.
              </p>
              {canEditGoals && (
                <Button onClick={() => setNewGoalDialog(true)}>
                  <Plus className="mr-2 h-4 w-4" />
                  Add Goal
                </Button>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
};

// Goal Card Component
const GoalCard = ({ goal, canEdit, canRate, canComment, onAgree, onRate, onComment }) => {
  const [isRating, setIsRating] = useState(false);
  const [isCommenting, setIsCommenting] = useState(false);
  const [rating, setRating] = useState(goal.rating || 0);
  const [comments, setComments] = useState(goal.supervisor_comments || '');
  const [comment, setComment] = useState(goal.staff_comments || '');

  const handleSubmitRating = () => {
    onRate(rating, comments);
    setIsRating(false);
  };

  const handleSubmitComment = () => {
    onComment(comment);
    setIsCommenting(false);
  };

  return (
    <Card className={`${goal.agreed ? 'border-green-200 bg-green-50' : ''}`}>
      <CardContent className="pt-6">
        <div className="space-y-4">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h4 className="font-medium text-gray-900">{goal.description}</h4>
              {goal.target && (
                <p className="text-sm text-gray-600 mt-1">
                  <strong>Target:</strong> {goal.target}
                </p>
              )}
            </div>
            
            <div className="flex items-center space-x-2">
              {goal.agreed ? (
                <Badge variant="default" className="bg-green-100 text-green-800">
                  <CheckCircle className="mr-1 h-3 w-3" />
                  Agreed
                </Badge>
              ) : (
                canEdit && (
                  <Button size="sm" variant="outline" onClick={onAgree}>
                    <CheckCircle className="mr-1 h-3 w-3" />
                    Agree
                  </Button>
                )
              )}
              
              {goal.rating && (
                <div className="flex items-center space-x-1">
                  {Array.from({ length: 5 }, (_, i) => (
                    <Star
                      key={i}
                      className={`h-4 w-4 ${
                        i < goal.rating ? 'text-yellow-400 fill-current' : 'text-gray-300'
                      }`}
                    />
                  ))}
                  <span className="text-sm text-gray-600 ml-1">
                    ({goal.rating}/5)
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* Rating Section */}
          {canRate && !goal.rating && (
            <div className="border-t pt-4">
              {!isRating ? (
                <Button size="sm" variant="outline" onClick={() => setIsRating(true)}>
                  <Star className="mr-1 h-3 w-3" />
                  Rate Goal
                </Button>
              ) : (
                <div className="space-y-3">
                  <div>
                    <Label className="text-sm font-medium">Rating</Label>
                    <div className="flex items-center space-x-1 mt-1">
                      {Array.from({ length: 5 }, (_, i) => (
                        <button
                          key={i}
                          onClick={() => setRating(i + 1)}
                          className="focus:outline-none"
                        >
                          <Star
                            className={`h-5 w-5 ${
                              i < rating ? 'text-yellow-400 fill-current' : 'text-gray-300'
                            } hover:text-yellow-400 transition-colors`}
                          />
                        </button>
                      ))}
                    </div>
                  </div>
                  
                  <div>
                    <Label className="text-sm font-medium">Comments</Label>
                    <Textarea
                      value={comments}
                      onChange={(e) => setComments(e.target.value)}
                      placeholder="Add your feedback..."
                      className="mt-1"
                    />
                  </div>
                  
                  <div className="flex space-x-2">
                    <Button size="sm" onClick={handleSubmitRating}>
                      <Save className="mr-1 h-3 w-3" />
                      Submit Rating
                    </Button>
                    <Button size="sm" variant="outline" onClick={() => setIsRating(false)}>
                      <X className="mr-1 h-3 w-3" />
                      Cancel
                    </Button>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Comments Section */}
          {goal.supervisor_comments && (
            <div className="border-t pt-4">
              <Label className="text-sm font-medium text-gray-600">Supervisor Feedback</Label>
              <p className="text-sm text-gray-700 mt-1">{goal.supervisor_comments}</p>
            </div>
          )}

          {canComment && (
            <div className="border-t pt-4">
              {!isCommenting && !goal.staff_comments ? (
                <Button size="sm" variant="outline" onClick={() => setIsCommenting(true)}>
                  <MessageSquare className="mr-1 h-3 w-3" />
                  Add Comment
                </Button>
              ) : goal.staff_comments && !isCommenting ? (
                <div>
                  <Label className="text-sm font-medium text-gray-600">Your Comments</Label>
                  <p className="text-sm text-gray-700 mt-1">{goal.staff_comments}</p>
                  <Button 
                    size="sm" 
                    variant="outline" 
                    className="mt-2"
                    onClick={() => setIsCommenting(true)}
                  >
                    <Edit className="mr-1 h-3 w-3" />
                    Edit Comment
                  </Button>
                </div>
              ) : (
                <div className="space-y-3">
                  <div>
                    <Label className="text-sm font-medium">Your Comments</Label>
                    <Textarea
                      value={comment}
                      onChange={(e) => setComment(e.target.value)}
                      placeholder="Add your thoughts on this goal..."
                      className="mt-1"
                    />
                  </div>
                  
                  <div className="flex space-x-2">
                    <Button size="sm" onClick={handleSubmitComment}>
                      <Save className="mr-1 h-3 w-3" />
                      Save Comment
                    </Button>
                    <Button size="sm" variant="outline" onClick={() => setIsCommenting(false)}>
                      <X className="mr-1 h-3 w-3" />
                      Cancel
                    </Button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

// New Goal Form Component
const NewGoalForm = ({ onSubmit }) => {
  const [description, setDescription] = useState('');
  const [target, setTarget] = useState('');
  const [weight, setWeight] = useState(1);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({
      description,
      target: target || undefined,
      weight: parseFloat(weight),
    });
    setDescription('');
    setTarget('');
    setWeight(1);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <Label htmlFor="description">Goal Description</Label>
        <Textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Describe the performance goal..."
          required
        />
      </div>
      
      <div>
        <Label htmlFor="target">Target (Optional)</Label>
        <Textarea
          id="target"
          value={target}
          onChange={(e) => setTarget(e.target.value)}
          placeholder="Specific target or outcome..."
        />
      </div>
      
      <div>
        <Label htmlFor="weight">Weight</Label>
        <Input
          id="weight"
          type="number"
          min="0.1"
          max="5"
          step="0.1"
          value={weight}
          onChange={(e) => setWeight(e.target.value)}
        />
      </div>
      
      <Button type="submit" className="w-full">
        Add Goal
      </Button>
    </form>
  );
};

export default EvaluationDetailsPage;

