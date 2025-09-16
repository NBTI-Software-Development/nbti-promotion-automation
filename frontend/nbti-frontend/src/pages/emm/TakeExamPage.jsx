import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Clock,
  ChevronLeft,
  ChevronRight,
  Flag,
  AlertTriangle,
  CheckCircle,
  Save,
  Send,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Progress } from '@/components/ui/progress';
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
import { emmAPI } from '../../services/api';

const TakeExamPage = () => {
  const { examId, submissionId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  
  const [exam, setExam] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [flaggedQuestions, setFlaggedQuestions] = useState(new Set());
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [showSubmitDialog, setShowSubmitDialog] = useState(false);

  useEffect(() => {
    fetchExamData();
  }, [examId, submissionId]);

  // Timer effect
  useEffect(() => {
    if (timeRemaining > 0) {
      const timer = setInterval(() => {
        setTimeRemaining(prev => {
          if (prev <= 1) {
            handleSubmitExam();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);

      return () => clearInterval(timer);
    }
  }, [timeRemaining]);

  const fetchExamData = async () => {
    try {
      setLoading(true);
      const [examResponse, submissionResponse] = await Promise.all([
        emmAPI.getExam(examId),
        emmAPI.getSubmission(submissionId),
      ]);
      
      const examData = examResponse.data.exam;
      const submissionData = submissionResponse.data.submission;
      
      setExam(examData);
      setQuestions(examData.questions || []);
      
      // Calculate time remaining
      const startTime = new Date(submissionData.started_at);
      const duration = examData.duration * 60; // Convert to seconds
      const elapsed = Math.floor((Date.now() - startTime.getTime()) / 1000);
      const remaining = Math.max(0, duration - elapsed);
      setTimeRemaining(remaining);
      
      // Load existing answers
      if (submissionData.answers) {
        const answersMap = {};
        submissionData.answers.forEach(answer => {
          answersMap[answer.question_id] = answer.answer_text;
        });
        setAnswers(answersMap);
      }
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to load exam');
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerChange = useCallback(async (questionId, answer) => {
    setAnswers(prev => ({ ...prev, [questionId]: answer }));
    
    // Auto-save answer
    try {
      setSaving(true);
      await emmAPI.submitAnswer(submissionId, {
        question_id: questionId,
        answer_text: answer,
      });
    } catch (error) {
      console.error('Failed to save answer:', error);
    } finally {
      setSaving(false);
    }
  }, [submissionId]);

  const handleFlagQuestion = (questionIndex) => {
    setFlaggedQuestions(prev => {
      const newSet = new Set(prev);
      if (newSet.has(questionIndex)) {
        newSet.delete(questionIndex);
      } else {
        newSet.add(questionIndex);
      }
      return newSet;
    });
  };

  const handleSubmitExam = async () => {
    try {
      setSubmitting(true);
      await emmAPI.submitExam(submissionId);
      navigate(`/emm/results/${submissionId}`);
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to submit exam');
    } finally {
      setSubmitting(false);
    }
  };

  const formatTime = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  };

  const getTimeColor = () => {
    if (timeRemaining <= 300) return 'text-red-600'; // 5 minutes
    if (timeRemaining <= 900) return 'text-yellow-600'; // 15 minutes
    return 'text-green-600';
  };

  const currentQuestion = questions[currentQuestionIndex];
  const progress = questions.length > 0 ? ((currentQuestionIndex + 1) / questions.length) * 100 : 0;
  const answeredCount = Object.keys(answers).length;

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error && !exam) {
    return (
      <div className="p-6">
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <h1 className="text-xl font-semibold text-gray-900">
                {exam?.title}
              </h1>
              <Badge variant="outline">
                Question {currentQuestionIndex + 1} of {questions.length}
              </Badge>
            </div>
            
            <div className="flex items-center space-x-4">
              {saving && (
                <div className="flex items-center text-sm text-gray-600">
                  <Save className="mr-1 h-4 w-4 animate-pulse" />
                  Saving...
                </div>
              )}
              
              <div className={`flex items-center text-lg font-mono ${getTimeColor()}`}>
                <Clock className="mr-2 h-5 w-5" />
                {formatTime(timeRemaining)}
              </div>
              
              <Dialog open={showSubmitDialog} onOpenChange={setShowSubmitDialog}>
                <DialogTrigger asChild>
                  <Button variant="outline">
                    <Send className="mr-2 h-4 w-4" />
                    Submit Exam
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Submit Exam</DialogTitle>
                    <DialogDescription>
                      Are you sure you want to submit your exam? This action cannot be undone.
                    </DialogDescription>
                  </DialogHeader>
                  <div className="space-y-4">
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="text-gray-600">Total Questions:</span>
                          <span className="ml-2 font-semibold">{questions.length}</span>
                        </div>
                        <div>
                          <span className="text-gray-600">Answered:</span>
                          <span className="ml-2 font-semibold">{answeredCount}</span>
                        </div>
                        <div>
                          <span className="text-gray-600">Unanswered:</span>
                          <span className="ml-2 font-semibold">{questions.length - answeredCount}</span>
                        </div>
                        <div>
                          <span className="text-gray-600">Flagged:</span>
                          <span className="ml-2 font-semibold">{flaggedQuestions.size}</span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex justify-end space-x-3">
                      <Button
                        variant="outline"
                        onClick={() => setShowSubmitDialog(false)}
                      >
                        Continue Exam
                      </Button>
                      <Button
                        onClick={handleSubmitExam}
                        disabled={submitting}
                      >
                        {submitting ? 'Submitting...' : 'Submit Exam'}
                      </Button>
                    </div>
                  </div>
                </DialogContent>
              </Dialog>
            </div>
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-2">
          <Progress value={progress} className="h-2" />
        </div>
      </div>

      {error && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-4">
          <Alert variant="destructive">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        </div>
      )}

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Question Content */}
          <div className="lg:col-span-3">
            <AnimatePresence mode="wait">
              {currentQuestion && (
                <motion.div
                  key={currentQuestionIndex}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  transition={{ duration: 0.3 }}
                >
                  <Card>
                    <CardHeader>
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <CardTitle className="text-lg">
                            Question {currentQuestionIndex + 1}
                          </CardTitle>
                          <CardDescription className="mt-2">
                            {currentQuestion.question_type === 'MCQ' ? 'Multiple Choice' : 'Essay'}
                          </CardDescription>
                        </div>
                        <Button
                          variant={flaggedQuestions.has(currentQuestionIndex) ? "default" : "outline"}
                          size="sm"
                          onClick={() => handleFlagQuestion(currentQuestionIndex)}
                        >
                          <Flag className="h-4 w-4" />
                        </Button>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-6">
                      <div className="prose max-w-none">
                        <p className="text-lg text-gray-900 leading-relaxed">
                          {currentQuestion.question_text}
                        </p>
                      </div>

                      {currentQuestion.question_type === 'MCQ' ? (
                        <RadioGroup
                          value={answers[currentQuestion.id] || ''}
                          onValueChange={(value) => handleAnswerChange(currentQuestion.id, value)}
                        >
                          <div className="space-y-3">
                            {currentQuestion.options?.map((option, index) => (
                              <div key={index} className="flex items-center space-x-2">
                                <RadioGroupItem
                                  value={option}
                                  id={`option-${index}`}
                                />
                                <Label
                                  htmlFor={`option-${index}`}
                                  className="flex-1 cursor-pointer p-3 rounded-lg border hover:bg-gray-50 transition-colors"
                                >
                                  {option}
                                </Label>
                              </div>
                            ))}
                          </div>
                        </RadioGroup>
                      ) : (
                        <div>
                          <Label htmlFor="essay-answer" className="text-sm font-medium">
                            Your Answer
                          </Label>
                          <Textarea
                            id="essay-answer"
                            value={answers[currentQuestion.id] || ''}
                            onChange={(e) => handleAnswerChange(currentQuestion.id, e.target.value)}
                            placeholder="Type your answer here..."
                            className="mt-2 min-h-[200px]"
                          />
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Navigation */}
            <div className="flex items-center justify-between mt-6">
              <Button
                variant="outline"
                onClick={() => setCurrentQuestionIndex(prev => Math.max(0, prev - 1))}
                disabled={currentQuestionIndex === 0}
              >
                <ChevronLeft className="mr-2 h-4 w-4" />
                Previous
              </Button>
              
              <div className="text-sm text-gray-600">
                {answers[currentQuestion?.id] ? (
                  <div className="flex items-center text-green-600">
                    <CheckCircle className="mr-1 h-4 w-4" />
                    Answered
                  </div>
                ) : (
                  'Not answered'
                )}
              </div>
              
              <Button
                variant="outline"
                onClick={() => setCurrentQuestionIndex(prev => Math.min(questions.length - 1, prev + 1))}
                disabled={currentQuestionIndex === questions.length - 1}
              >
                Next
                <ChevronRight className="ml-2 h-4 w-4" />
              </Button>
            </div>
          </div>

          {/* Question Navigator */}
          <div className="lg:col-span-1">
            <Card className="sticky top-24">
              <CardHeader>
                <CardTitle className="text-sm">Question Navigator</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-5 gap-2">
                  {questions.map((_, index) => (
                    <button
                      key={index}
                      onClick={() => setCurrentQuestionIndex(index)}
                      className={`
                        w-10 h-10 rounded text-sm font-medium transition-colors
                        ${index === currentQuestionIndex
                          ? 'bg-blue-600 text-white'
                          : answers[questions[index]?.id]
                          ? 'bg-green-100 text-green-800 hover:bg-green-200'
                          : flaggedQuestions.has(index)
                          ? 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200'
                          : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                        }
                      `}
                    >
                      {index + 1}
                      {flaggedQuestions.has(index) && (
                        <Flag className="h-2 w-2 absolute -top-1 -right-1" />
                      )}
                    </button>
                  ))}
                </div>
                
                <div className="mt-4 space-y-2 text-xs">
                  <div className="flex items-center">
                    <div className="w-3 h-3 bg-blue-600 rounded mr-2"></div>
                    Current
                  </div>
                  <div className="flex items-center">
                    <div className="w-3 h-3 bg-green-100 border border-green-300 rounded mr-2"></div>
                    Answered
                  </div>
                  <div className="flex items-center">
                    <div className="w-3 h-3 bg-yellow-100 border border-yellow-300 rounded mr-2"></div>
                    Flagged
                  </div>
                  <div className="flex items-center">
                    <div className="w-3 h-3 bg-gray-100 border border-gray-300 rounded mr-2"></div>
                    Not answered
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TakeExamPage;

