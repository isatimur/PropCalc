"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import {
  Brain, TrendingUp, TrendingDown, DollarSign, MapPin, Building2, Calendar,
  BarChart3, PieChart, RefreshCw, Eye, Download, Filter, Search, Target,
  AlertTriangle, CheckCircle, Clock, Zap, Lightbulb, TrendingUpIcon, Activity
} from "lucide-react";

interface MarketIntelligence {
  id: string;
  title: string;
  description: string;
  category: 'trend' | 'opportunity' | 'risk' | 'insight';
  confidence: number;
  impact: 'high' | 'medium' | 'low';
  timeframe: 'immediate' | 'short_term' | 'long_term';
  data_sources: string[];
  created_at: string;
  last_updated: string;
}

interface PredictiveModel {
  id: string;
  name: string;
  description: string;
  accuracy: number;
  last_trained: string;
  next_update: string;
  features: string[];
  predictions: Prediction[];
}

interface Prediction {
  id: string;
  metric: string;
  current_value: number;
  predicted_value: number;
  confidence_interval: [number, number];
  timeframe: string;
  trend: 'up' | 'down' | 'stable';
}

interface MarketSegment {
  id: string;
  name: string;
  current_performance: number;
  predicted_performance: number;
  risk_score: number;
  opportunity_score: number;
  key_drivers: string[];
  recommendations: string[];
}

interface StrategicRecommendation {
  id: string;
  title: string;
  description: string;
  category: 'investment' | 'timing' | 'location' | 'property_type';
  priority: 'high' | 'medium' | 'low';
  expected_roi: number;
  risk_level: 'low' | 'medium' | 'high';
  implementation_steps: string[];
}

export default function DLDMarketIntelligencePage() {
  const [activeTab, setActiveTab] = useState("overview");
  const [selectedLocation, setSelectedLocation] = useState("all");
  const [selectedTimeframe, setSelectedTimeframe] = useState("12m");
  const [marketIntelligence, setMarketIntelligence] = useState<MarketIntelligence[]>([]);
  const [predictiveModels, setPredictiveModels] = useState<PredictiveModel[]>([]);
  const [marketSegments, setMarketSegments] = useState<MarketSegment[]>([]);
  const [strategicRecommendations, setStrategicRecommendations] = useState<StrategicRecommendation[]>([]);

  // Mock data
  useEffect(() => {
    // Mock market intelligence data
    setMarketIntelligence([
      {
        id: "mi1",
        title: "Dubai Marina Supply Constraint",
        description: "Limited new supply in Dubai Marina is driving up prices by 8-12% annually",
        category: "trend",
        confidence: 92,
        impact: "high",
        timeframe: "short_term",
        data_sources: ["DLD Transactions", "Construction Permits", "Market Surveys"],
        created_at: "2024-01-15",
        last_updated: "2024-01-20"
      },
      {
        id: "mi2",
        title: "Emerging Investment Opportunity in Dubai Hills",
        description: "New infrastructure projects are creating value appreciation potential of 15-20%",
        category: "opportunity",
        confidence: 78,
        impact: "medium",
        timeframe: "long_term",
        data_sources: ["DLD Transactions", "Infrastructure Plans", "Demographic Data"],
        created_at: "2024-01-18",
        last_updated: "2024-01-20"
      },
      {
        id: "mi3",
        title: "Interest Rate Sensitivity Analysis",
        description: "Properties above 5M AED showing increased sensitivity to rate changes",
        category: "risk",
        confidence: 85,
        impact: "medium",
        timeframe: "immediate",
        data_sources: ["DLD Transactions", "Mortgage Data", "Economic Indicators"],
        created_at: "2024-01-16",
        last_updated: "2024-01-20"
      }
    ]);

    // Mock predictive models
    setPredictiveModels([
      {
        id: "pm1",
        name: "Price Prediction Model v2.1",
        description: "ML model for predicting property prices based on DLD data and market factors",
        accuracy: 87.3,
        last_trained: "2024-01-15",
        next_update: "2024-02-15",
        features: ["Location", "Property Type", "Area", "Amenities", "Market Trends"],
        predictions: [
          {
            id: "pred1",
            metric: "Dubai Marina Apartment Prices",
            current_value: 2800,
            predicted_value: 3050,
            confidence_interval: [2950, 3150],
            timeframe: "6 months",
            trend: "up"
          },
          {
            id: "pred2",
            metric: "Palm Jumeirah Villa Prices",
            current_value: 4200,
            predicted_value: 4450,
            confidence_interval: [4350, 4550],
            timeframe: "12 months",
            trend: "up"
          }
        ]
      }
    ]);

    // Mock market segments
    setMarketSegments([
      {
        id: "ms1",
        name: "Luxury Apartments (5M+ AED)",
        current_performance: 8.5,
        predicted_performance: 12.2,
        risk_score: 0.3,
        opportunity_score: 0.8,
        key_drivers: ["Limited Supply", "High Net Worth Demand", "Premium Amenities"],
        recommendations: ["Focus on prime locations", "Invest in high-end finishes", "Target international buyers"]
      },
      {
        id: "ms2",
        name: "Mid-Market Villas (2M-5M AED)",
        current_performance: 6.2,
        predicted_performance: 8.8,
        risk_score: 0.4,
        opportunity_score: 0.7,
        key_drivers: ["Family Demand", "School Proximity", "Community Amenities"],
        recommendations: ["Target family buyers", "Emphasize community features", "Highlight school districts"]
      }
    ]);

    // Mock strategic recommendations
    setStrategicRecommendations([
      {
        id: "sr1",
        title: "Invest in Dubai Marina Premium Units",
        description: "High-end apartments in Dubai Marina show strong appreciation potential with limited supply",
        category: "investment",
        priority: "high",
        expected_roi: 15.2,
        risk_level: "low",
        implementation_steps: [
          "Identify available premium units",
          "Analyze comparable sales",
          "Secure financing options",
          "Monitor market conditions"
        ]
      },
      {
        id: "sr2",
        title: "Timing: Q2 2024 Entry Point",
        description: "Market analysis suggests optimal entry point in Q2 2024 before seasonal price increases",
        category: "timing",
        priority: "medium",
        expected_roi: 8.5,
        risk_level: "medium",
        implementation_steps: [
          "Prepare investment capital",
          "Research target properties",
          "Set up property viewings",
          "Negotiate favorable terms"
        ]
      }
    ]);
  }, []);

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'trend': return "bg-blue-100 text-blue-800";
      case 'opportunity': return "bg-green-100 text-green-800";
      case 'risk': return "bg-red-100 text-red-800";
      case 'insight': return "bg-purple-100 text-purple-800";
      default: return "bg-gray-100 text-gray-800";
    }
  };

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'high': return "bg-red-100 text-red-800";
      case 'medium': return "bg-yellow-100 text-yellow-800";
      case 'low': return "bg-green-100 text-green-800";
      default: return "bg-gray-100 text-gray-800";
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return "bg-red-100 text-red-800";
      case 'medium': return "bg-yellow-100 text-yellow-800";
      case 'low': return "bg-green-100 text-green-800";
      default: return "bg-gray-100 text-gray-800";
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'high': return "bg-red-100 text-red-800";
      case 'medium': return "bg-yellow-100 text-yellow-800";
      case 'low': return "bg-green-100 text-green-800";
      default: return "bg-gray-100 text-gray-800";
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up': return <TrendingUp className="w-4 h-4 text-green-600" />;
      case 'down': return <TrendingDown className="w-4 h-4 text-red-600" />;
      default: return <Activity className="w-4 h-4 text-gray-600" />;
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">DLD Market Intelligence Dashboard</h1>
          <p className="text-gray-600 mt-2">
            AI-powered market insights, predictive analytics, and strategic recommendations
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <Download className="w-4 h-4 mr-2" />
            Export Report
          </Button>
          <Button variant="outline" size="sm">
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh Data
          </Button>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex gap-4">
            <div className="flex-1">
              <Label htmlFor="location">Location</Label>
              <Select value={selectedLocation} onValueChange={setSelectedLocation}>
                <SelectTrigger>
                  <SelectValue placeholder="Select location" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Locations</SelectItem>
                  <SelectItem value="dubai_marina">Dubai Marina</SelectItem>
                  <SelectItem value="palm_jumeirah">Palm Jumeirah</SelectItem>
                  <SelectItem value="downtown_dubai">Downtown Dubai</SelectItem>
                  <SelectItem value="business_bay">Business Bay</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex-1">
              <Label htmlFor="timeframe">Timeframe</Label>
              <Select value={selectedTimeframe} onValueChange={setSelectedTimeframe}>
                <SelectTrigger>
                  <SelectValue placeholder="Select timeframe" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="3m">3 Months</SelectItem>
                  <SelectItem value="6m">6 Months</SelectItem>
                  <SelectItem value="12m">12 Months</SelectItem>
                  <SelectItem value="24m">24 Months</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="intelligence">Market Intelligence</TabsTrigger>
          <TabsTrigger value="predictions">Predictions</TabsTrigger>
          <TabsTrigger value="segments">Market Segments</TabsTrigger>
          <TabsTrigger value="recommendations">Strategic Recommendations</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center gap-2">
                  <Brain className="w-8 h-8 text-blue-600" />
                  <div>
                    <p className="text-sm text-gray-600">AI Insights</p>
                    <p className="text-2xl font-bold">24</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center gap-2">
                  <TrendingUpIcon className="w-8 h-8 text-green-600" />
                  <div>
                    <p className="text-sm text-gray-600">Prediction Accuracy</p>
                    <p className="text-2xl font-bold">87.3%</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center gap-2">
                  <Target className="w-8 h-8 text-purple-600" />
                  <div>
                    <p className="text-sm text-gray-600">Opportunities</p>
                    <p className="text-2xl font-bold">12</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center gap-2">
                  <AlertTriangle className="w-8 h-8 text-red-600" />
                  <div>
                    <p className="text-sm text-gray-600">Risk Alerts</p>
                    <p className="text-2xl font-bold">3</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Recent Intelligence */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Lightbulb className="w-5 h-5" />
                Recent Market Intelligence
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {marketIntelligence.slice(0, 3).map((intel) => (
                  <div key={intel.id} className="border rounded-lg p-4">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <Badge className={getCategoryColor(intel.category)}>
                            {intel.category}
                          </Badge>
                          <Badge className={getImpactColor(intel.impact)}>
                            {intel.impact} impact
                          </Badge>
                          <Badge variant="outline">
                            {intel.confidence}% confidence
                          </Badge>
                        </div>
                        <h4 className="font-semibold mb-1">{intel.title}</h4>
                        <p className="text-sm text-gray-600 mb-2">{intel.description}</p>
                        <div className="flex items-center gap-4 text-xs text-gray-500">
                          <span>Updated: {new Date(intel.last_updated).toLocaleDateString()}</span>
                          <span>Timeframe: {intel.timeframe.replace('_', ' ')}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="intelligence" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="w-5 h-5" />
                Market Intelligence Feed
              </CardTitle>
              <CardDescription>
                AI-generated insights based on DLD data analysis
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {marketIntelligence.map((intel) => (
                  <div key={intel.id} className="border rounded-lg p-4">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <Badge className={getCategoryColor(intel.category)}>
                            {intel.category}
                          </Badge>
                          <Badge className={getImpactColor(intel.impact)}>
                            {intel.impact} impact
                          </Badge>
                          <Badge variant="outline">
                            {intel.confidence}% confidence
                          </Badge>
                        </div>
                        <h4 className="font-semibold mb-1">{intel.title}</h4>
                        <p className="text-sm text-gray-600 mb-2">{intel.description}</p>
                        <div className="text-xs text-gray-500 mb-2">
                          <strong>Data Sources:</strong> {intel.data_sources.join(', ')}
                        </div>
                        <div className="flex items-center gap-4 text-xs text-gray-500">
                          <span>Created: {new Date(intel.created_at).toLocaleDateString()}</span>
                          <span>Updated: {new Date(intel.last_updated).toLocaleDateString()}</span>
                          <span>Timeframe: {intel.timeframe.replace('_', ' ')}</span>
                        </div>
                      </div>
                      <Button variant="outline" size="sm">
                        <Eye className="w-4 h-4 mr-2" />
                        View Details
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="predictions" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="w-5 h-5" />
                Predictive Models & Forecasts
              </CardTitle>
              <CardDescription>
                Machine learning predictions based on DLD data and market analysis
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {predictiveModels.map((model) => (
                  <div key={model.id} className="border rounded-lg p-4">
                    <div className="mb-4">
                      <h4 className="font-semibold text-lg mb-2">{model.name}</h4>
                      <p className="text-sm text-gray-600 mb-2">{model.description}</p>
                      <div className="flex items-center gap-4 text-sm">
                        <span><strong>Accuracy:</strong> {model.accuracy}%</span>
                        <span><strong>Last Trained:</strong> {new Date(model.last_trained).toLocaleDateString()}</span>
                        <span><strong>Next Update:</strong> {new Date(model.next_update).toLocaleDateString()}</span>
                      </div>
                      <div className="mt-2">
                        <strong>Features:</strong> {model.features.join(', ')}
                      </div>
                    </div>

                    <div className="space-y-4">
                      <h5 className="font-medium">Predictions</h5>
                      {model.predictions.map((pred) => (
                        <div key={pred.id} className="bg-gray-50 rounded-lg p-3">
                          <div className="flex justify-between items-center mb-2">
                            <span className="font-medium">{pred.metric}</span>
                            {getTrendIcon(pred.trend)}
                          </div>
                          <div className="grid grid-cols-3 gap-4 text-sm">
                            <div>
                              <span className="text-gray-600">Current:</span>
                              <div className="font-semibold">AED {pred.current_value.toLocaleString()}</div>
                            </div>
                            <div>
                              <span className="text-gray-600">Predicted:</span>
                              <div className="font-semibold">AED {pred.predicted_value.toLocaleString()}</div>
                            </div>
                            <div>
                              <span className="text-gray-600">Confidence:</span>
                              <div className="font-semibold">
                                {pred.confidence_interval[0].toLocaleString()} - {pred.confidence_interval[1].toLocaleString()}
                              </div>
                            </div>
                          </div>
                          <div className="text-xs text-gray-500 mt-2">
                            Timeframe: {pred.timeframe}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="segments" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="w-5 h-5" />
                Market Segment Analysis
              </CardTitle>
              <CardDescription>
                Performance analysis and predictions for different market segments
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {marketSegments.map((segment) => (
                  <div key={segment.id} className="border rounded-lg p-4">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h4 className="font-semibold text-lg mb-2">{segment.name}</h4>
                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div>
                            <span className="text-gray-600">Current Performance:</span>
                            <div className="font-semibold text-green-600">+{segment.current_performance}%</div>
                          </div>
                          <div>
                            <span className="text-gray-600">Predicted Performance:</span>
                            <div className="font-semibold text-blue-600">+{segment.predicted_performance}%</div>
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="mb-2">
                          <Badge className="bg-red-100 text-red-800 mb-1">
                            Risk: {(segment.risk_score * 100).toFixed(0)}%
                          </Badge>
                          <Badge className="bg-green-100 text-green-800">
                            Opportunity: {(segment.opportunity_score * 100).toFixed(0)}%
                          </Badge>
                        </div>
                      </div>
                    </div>

                    <div className="space-y-3">
                      <div>
                        <strong className="text-sm">Key Drivers:</strong>
                        <div className="flex flex-wrap gap-2 mt-1">
                          {segment.key_drivers.map((driver, index) => (
                            <Badge key={index} variant="outline" className="text-xs">
                              {driver}
                            </Badge>
                          ))}
                        </div>
                      </div>
                      <div>
                        <strong className="text-sm">Recommendations:</strong>
                        <ul className="list-disc list-inside text-sm text-gray-600 mt-1 space-y-1">
                          {segment.recommendations.map((rec, index) => (
                            <li key={index}>{rec}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="recommendations" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="w-5 h-5" />
                Strategic Investment Recommendations
              </CardTitle>
              <CardDescription>
                AI-generated investment strategies based on market intelligence
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {strategicRecommendations.map((rec) => (
                  <div key={rec.id} className="border rounded-lg p-4">
                    <div className="flex justify-between items-start mb-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <Badge className={getPriorityColor(rec.priority)}>
                            {rec.priority} priority
                          </Badge>
                          <Badge className="bg-blue-100 text-blue-800">
                            {rec.expected_roi}% ROI
                          </Badge>
                          <Badge className={getRiskColor(rec.risk_level)}>
                            {rec.risk_level} risk
                          </Badge>
                        </div>
                        <h4 className="font-semibold text-lg mb-2">{rec.title}</h4>
                        <p className="text-sm text-gray-600 mb-3">{rec.description}</p>
                      </div>
                    </div>

                    <div className="space-y-3">
                      <div>
                        <strong className="text-sm">Implementation Steps:</strong>
                        <ol className="list-decimal list-inside text-sm text-gray-600 mt-1 space-y-1">
                          {rec.implementation_steps.map((step, index) => (
                            <li key={index}>{step}</li>
                          ))}
                        </ol>
                      </div>
                    </div>

                    <div className="flex gap-2 mt-4">
                      <Button size="sm">
                        <Eye className="w-4 h-4 mr-2" />
                        View Details
                      </Button>
                      <Button variant="outline" size="sm">
                        <Download className="w-4 h-4 mr-2" />
                        Export Strategy
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
