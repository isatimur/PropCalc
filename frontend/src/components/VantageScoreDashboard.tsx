'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Target, HelpCircle } from 'lucide-react';
import ShapWaterfallChart from './ShapWaterfallChart';
import { Bar } from 'react-chartjs-2';

interface VantageScoreDashboardProps {
  scoreData: {
    vantage_score: number;
    confidence: number;
    explainability: {
      feature_importance: { [key: string]: number };
      shap_explanation: {
        base_value: number;
        shap_values: { [key: string]: number };
      };
    };
  };
}

const VantageScoreDashboard: React.FC<VantageScoreDashboardProps> = ({ scoreData }) => {
  const { vantage_score, confidence, explainability } = scoreData;
  const { feature_importance, shap_explanation } = explainability;

  const featureImportanceData = {
    labels: Object.keys(feature_importance),
    datasets: [
      {
        label: 'Feature Importance',
        data: Object.values(feature_importance),
        backgroundColor: 'rgba(75, 192, 192, 0.6)',
        borderColor: 'rgba(75, 192, 192, 1)',
        borderWidth: 1,
      },
    ],
  };

  return (
    <div className="space-y-6 p-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Vantage Score™ Analysis</span>
            <Target className="h-6 w-6 text-blue-500" />
          </CardTitle>
          <CardDescription>AI-powered prediction and explanation.</CardDescription>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="flex flex-col items-center justify-center space-y-4">
            <div className="text-6xl font-bold text-blue-600">{vantage_score.toFixed(1)}</div>
            <div className="w-full">
              <div className="flex justify-between items-center mb-1">
                <span className="text-sm font-medium text-muted-foreground">Confidence</span>
                <span className="text-sm font-bold">{(confidence * 100).toFixed(0)}%</span>
              </div>
              <Progress value={confidence * 100} />
            </div>
          </div>
          <div>
            <ShapWaterfallChart shapExplanation={shap_explanation} />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <HelpCircle className="h-5 w-5 mr-2" />
            Overall Feature Importance
          </CardTitle>
          <CardDescription>Which factors matter most across all predictions.</CardDescription>
        </CardHeader>
        <CardContent>
          <Bar data={featureImportanceData} options={{ indexAxis: 'y', responsive: true, plugins: { legend: { display: false } } }} />
        </CardContent>
      </Card>
    </div>
  );
};

export default VantageScoreDashboard;
