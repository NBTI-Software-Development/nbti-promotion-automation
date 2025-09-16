import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Loader2, Calendar } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useAuth } from '../../contexts/AuthContext';
import { pmsAPI } from '../../services/api';

// Validation schema
const evaluationSchema = z.object({
  quarter: z.string().min(1, 'Quarter is required'),
  year: z.number().min(2020, 'Year must be 2020 or later').max(2030, 'Year must be 2030 or earlier'),
});

const CreateEvaluationForm = ({ onSuccess }) => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
    watch,
  } = useForm({
    resolver: zodResolver(evaluationSchema),
    defaultValues: {
      quarter: '',
      year: new Date().getFullYear(),
    },
  });

  const watchedQuarter = watch('quarter');
  const watchedYear = watch('year');

  const onSubmit = async (data) => {
    try {
      setLoading(true);
      setError('');

      const evaluationData = {
        staff_id: user.id,
        quarter: data.quarter,
        year: data.year,
      };

      await pmsAPI.createEvaluation(evaluationData);
      onSuccess();
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to create evaluation');
    } finally {
      setLoading(false);
    }
  };

  const currentYear = new Date().getFullYear();
  const years = Array.from({ length: 5 }, (_, i) => currentYear - 2 + i);

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="space-y-2">
        <Label htmlFor="quarter">Quarter</Label>
        <Select
          value={watchedQuarter}
          onValueChange={(value) => setValue('quarter', value)}
        >
          <SelectTrigger>
            <SelectValue placeholder="Select quarter" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="Q1">Q1 (January - March)</SelectItem>
            <SelectItem value="Q2">Q2 (April - June)</SelectItem>
            <SelectItem value="Q3">Q3 (July - September)</SelectItem>
            <SelectItem value="Q4">Q4 (October - December)</SelectItem>
          </SelectContent>
        </Select>
        {errors.quarter && (
          <p className="text-sm text-red-500">{errors.quarter.message}</p>
        )}
      </div>

      <div className="space-y-2">
        <Label htmlFor="year">Year</Label>
        <Select
          value={watchedYear?.toString()}
          onValueChange={(value) => setValue('year', parseInt(value))}
        >
          <SelectTrigger>
            <SelectValue placeholder="Select year" />
          </SelectTrigger>
          <SelectContent>
            {years.map((year) => (
              <SelectItem key={year} value={year.toString()}>
                {year}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        {errors.year && (
          <p className="text-sm text-red-500">{errors.year.message}</p>
        )}
      </div>

      <div className="bg-blue-50 p-4 rounded-lg">
        <div className="flex items-start">
          <Calendar className="h-5 w-5 text-blue-600 mt-0.5 mr-3" />
          <div>
            <h4 className="text-sm font-medium text-blue-900">
              Evaluation Period
            </h4>
            <p className="text-sm text-blue-700 mt-1">
              This evaluation will cover your performance for {watchedQuarter} {watchedYear}.
              You'll be able to set goals and track progress throughout this period.
            </p>
          </div>
        </div>
      </div>

      <div className="flex justify-end space-x-3 pt-4">
        <Button
          type="submit"
          disabled={loading}
          className="w-full"
        >
          {loading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Creating...
            </>
          ) : (
            'Create Evaluation'
          )}
        </Button>
      </div>
    </form>
  );
};

export default CreateEvaluationForm;

