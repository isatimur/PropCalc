'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';

import { Button } from '@/components/ui/button';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import realDataApi from '@/lib/api';
import VantageScoreDashboard from '@/components/VantageScoreDashboard';
import { Loader2 } from 'lucide-react';

const formSchema = z.object({
  price: z.coerce.number().min(10000, { message: 'Price must be at least 10,000' }),
  area: z.coerce.number().min(100, { message: 'Area must be at least 100 sqft' }),
  location_score: z.coerce.number().min(0).max(100),
  developer_score: z.coerce.number().min(0).max(100),
  market_trend: z.coerce.number().min(-10).max(10),
});

export default function VantageScoreCalculator() {
  const [scoreData, setScoreData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      price: 500000,
      area: 1200,
      location_score: 75,
      developer_score: 80,
      market_trend: 2,
    },
  });

  async function onSubmit(values: z.infer<typeof formSchema>) {
    setIsLoading(true);
    setError(null);
    setScoreData(null);
    try {
      const data = await realDataApi.calculateRealVantageScore(values);
      setScoreData(data);
    } catch (err) {
      setError('Failed to calculate Vantage Score. Please try again.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="container mx-auto p-4 md:p-8">
      <Card className="max-w-4xl mx-auto">
        <CardHeader>
          <CardTitle>Vantage Score™ Calculator</CardTitle>
          <CardDescription>
            Enter property details to get an AI-powered investment score and detailed analysis.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <FormField
                  control={form.control}
                  name="price"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Price (AED)</FormLabel>
                      <FormControl>
                        <Input type="number" placeholder="e.g., 1,200,000" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="area"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Area (sqft)</FormLabel>
                      <FormControl>
                        <Input type="number" placeholder="e.g., 1,500" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="location_score"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Location Score (0-100)</FormLabel>
                      <FormControl>
                        <Input type="number" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="developer_score"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Developer Score (0-100)</FormLabel>
                      <FormControl>
                        <Input type="number" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="market_trend"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Market Trend (-10 to 10)</FormLabel>
                      <FormControl>
                        <Input type="number" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
              <Button type="submit" disabled={isLoading} className="w-full">
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Calculating...
                  </>
                ) : (
                  'Calculate Vantage Score'
                )}
              </Button>
            </form>
          </Form>
        </CardContent>
      </Card>

      {error && (
        <div className="mt-8 text-center text-red-500">{error}</div>
      )}

      {scoreData && (
        <div className="mt-8">
          <VantageScoreDashboard scoreData={scoreData} />
        </div>
      )}
    </div>
  );
}
