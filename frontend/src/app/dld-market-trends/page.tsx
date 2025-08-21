"use client";

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { 
  TrendingUp, 
  TrendingDown, 
  MapPin, 
  Building2, 
  DollarSign, 
  BarChart3,
  LineChart,
  PieChart,
  Download,
  RefreshCw,
  Filter,
  Search,
  Calendar,
  Target,
  AlertTriangle,
  CheckCircle,
  Info
} from "lucide-react";

interface MarketTrend {
  id: string;
  propertyType: string;
  location: string;
  trend: 'up' | 'down' | 'stable';
  changePercent: number;
  avgPrice: number;
  volume: number;
  confidence: number;
  lastUpdated: string;
  factors: string[];
}

interface MarketInsight {
  id: string;
  type: 'opportunity' | 'risk' | 'trend' | 'forecast';
  title: string;
  description: string;
  impact: 'high' | 'medium' | 'low';
  confidence: number;
  timeframe: string;
  recommendations: string[];
}

export default function DLDMarketTrendsPage() {
  const [trends, setTrends] = useState<MarketTrend[]>([]);
  const [insights, setInsights] = useState<MarketInsight[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedPropertyType, setSelectedPropertyType] = useState<string>('all');
  const [selectedLocation, setSelectedLocation] = useState<string>('all');
  const [timeRange, setTimeRange] = useState<string>('30d');
  const [searchQuery, setSearchQuery] = useState('');

  // Mock data - replace with actual API calls
  const mockTrends: MarketTrend[] = [
    {
      id: '1',
      propertyType: 'Residential',
      location: 'Downtown',
      trend: 'up',
      changePercent: 12.5,
      avgPrice: 450000,
      volume: 156,
      confidence: 85,
      lastUpdated: '2024-01-15',
      factors: ['Low inventory', 'High demand', 'Interest rate stability']
    },
    {
      id: '2',
      propertyType: 'Commercial',
      location: 'Business District',
      trend: 'down',
      changePercent: -3.2,
      avgPrice: 1200000,
      volume: 23,
      confidence: 72,
      lastUpdated: '2024-01-15',
      factors: ['Remote work impact', 'Economic uncertainty', 'High vacancy rates']
    },
    {
      id: '3',
      propertyType: 'Industrial',
      location: 'Outskirts',
      trend: 'up',
      changePercent: 8.7,
      avgPrice: 850000,
      volume: 45,
      confidence: 91,
      lastUpdated: '2024-01-15',
      factors: ['E-commerce growth', 'Supply chain optimization', 'Infrastructure development']
    }
  ];

  const mockInsights: MarketInsight[] = [
    {
      id: '1',
      type: 'opportunity',
      title: 'Residential Market Recovery',
      description: 'Strong indicators suggest residential properties in downtown areas will continue appreciating due to limited supply and high demand.',
      impact: 'high',
      confidence: 87,
      timeframe: '6-12 months',
      recommendations: [
        'Focus on residential acquisitions in downtown areas',
        'Consider pre-construction investments',
        'Monitor zoning changes for development opportunities'
      ]
    },
    {
      id: '2',
      type: 'risk',
      title: 'Commercial Office Space Decline',
      description: 'Continued remote work adoption and economic uncertainty may further depress commercial office values.',
      impact: 'medium',
      confidence: 73,
      timeframe: '3-6 months',
      recommendations: [
        'Diversify commercial portfolio away from traditional office space',
        'Consider adaptive reuse opportunities',
        'Monitor lease renewal patterns'
      ]
    },
    {
      id: '3',
      type: 'trend',
      title: 'Industrial Sector Growth',
      description: 'Industrial properties continue to show strong growth potential due to e-commerce expansion and supply chain needs.',
      impact: 'high',
      confidence: 91,
      timeframe: '12-18 months',
      recommendations: [
        'Increase industrial property allocations',
        'Focus on logistics-friendly locations',
        'Consider build-to-suit opportunities'
      ]
    }
  ];

  useEffect(() => {
    // Simulate API call
    const fetchData = async () => {
      try {
        setLoading(true);
        // Simulate network delay
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        setTrends(mockTrends);
        setInsights(mockInsights);
        setError(null);
      } catch (err) {
        setError('Failed to fetch market trends data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const filteredTrends = trends.filter(trend => {
    const matchesPropertyType = selectedPropertyType === 'all' || trend.propertyType === selectedPropertyType;
    const matchesLocation = selectedLocation === 'all' || trend.location === selectedLocation;
    const matchesSearch = searchQuery === '' || 
      trend.propertyType.toLowerCase().includes(searchQuery.toLowerCase()) ||
      trend.location.toLowerCase().includes(searchQuery.toLowerCase());
    
    return matchesPropertyType && matchesLocation && matchesSearch;
  });

  const filteredInsights = insights.filter(insight => {
    const matchesType = selectedPropertyType === 'all' || 
      insight.recommendations.some(rec => rec.toLowerCase().includes(selectedPropertyType.toLowerCase()));
    const matchesSearch = searchQuery === '' || 
      insight.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      insight.description.toLowerCase().includes(searchQuery.toLowerCase());
    
    return matchesType && matchesSearch;
  });

  const getTrendIcon = (trend: 'up' | 'down' | 'stable') => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="h-5 w-5 text-green-600" />;
      case 'down':
        return <TrendingDown className="h-5 w-5 text-red-600" />;
      default:
        return <TrendingUp className="h-5 w-5 text-gray-600" />;
    }
  };

  const getImpactColor = (impact: 'high' | 'medium' | 'low') => {
    switch (impact) {
      case 'high':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low':
        return 'bg-green-100 text-green-800 border-green-200';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'opportunity':
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      case 'risk':
        return <AlertTriangle className="h-5 w-5 text-red-600" />;
      case 'trend':
        return <TrendingUp className="h-5 w-5 text-blue-600" />;
      case 'forecast':
        return <Target className="h-5 w-5 text-purple-600" />;
      default:
        return <Info className="h-5 w-5 text-gray-600" />;
    }
  };

  const exportData = () => {
    const data = {
      trends: filteredTrends,
      insights: filteredInsights,
      exportDate: new Date().toISOString(),
      filters: {
        propertyType: selectedPropertyType,
        location: selectedLocation,
        timeRange,
        searchQuery
      }
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `dld-market-trends-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const refreshData = useCallback(async () => {
    setLoading(true);
    try {
      // Simulate refresh
      await new Promise(resolve => setTimeout(resolve, 800));
      setError(null);
    } catch (err) {
      setError('Failed to refresh data');
    } finally {
      setLoading(false);
    }
  }, []);

  if (loading && trends.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4 text-blue-600" />
          <p className="text-gray-600">Loading market trends...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <AlertTriangle className="h-8 w-8 mx-auto mb-4 text-red-600" />
          <p className="text-red-600 mb-4">{error}</p>
          <Button onClick={refreshData}>Retry</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">DLD Market Trends & Intelligence</h1>
        <p className="text-gray-600">Comprehensive market analysis and trend forecasting for informed investment decisions</p>
      </div>

      {/* Filters and Controls */}
      <Card className="mb-6">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Filter className="h-5 w-5" />
              Market Analysis Filters
            </CardTitle>
            <div className="flex gap-2">
              <Button variant="outline" onClick={refreshData} disabled={loading}>
                <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
              <Button onClick={exportData}>
                <Download className="h-4 w-4 mr-2" />
                Export Data
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <Label htmlFor="search">Search</Label>
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  id="search"
                  placeholder="Search trends and insights..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <div>
              <Label htmlFor="propertyType">Property Type</Label>
              <Select value={selectedPropertyType} onValueChange={setSelectedPropertyType}>
                <SelectTrigger>
                  <SelectValue placeholder="All Types" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Types</SelectItem>
                  <SelectItem value="Residential">Residential</SelectItem>
                  <SelectItem value="Commercial">Commercial</SelectItem>
                  <SelectItem value="Industrial">Industrial</SelectItem>
                  <SelectItem value="Land">Land</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="location">Location</Label>
              <Select value={selectedLocation} onValueChange={setSelectedLocation}>
                <SelectTrigger>
                  <SelectValue placeholder="All Locations" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Locations</SelectItem>
                  <SelectItem value="Downtown">Downtown</SelectItem>
                  <SelectItem value="Business District">Business District</SelectItem>
                  <SelectItem value="Outskirts">Outskirts</SelectItem>
                  <SelectItem value="Suburban">Suburban</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="timeRange">Time Range</Label>
              <Select value={timeRange} onValueChange={setTimeRange}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="7d">Last 7 days</SelectItem>
                  <SelectItem value="30d">Last 30 days</SelectItem>
                  <SelectItem value="90d">Last 90 days</SelectItem>
                  <SelectItem value="1y">Last year</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      <Tabs defaultValue="trends" className="space-y-6">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="trends" className="flex items-center gap-2">
            <BarChart3 className="h-4 w-4" />
            Market Trends
          </TabsTrigger>
          <TabsTrigger value="insights" className="flex items-center gap-2">
            <TrendingUp className="h-4 w-4" />
            Market Insights
          </TabsTrigger>
        </TabsList>

        <TabsContent value="trends" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {filteredTrends.map((trend) => (
              <Card key={trend.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{trend.propertyType}</CardTitle>
                    {getTrendIcon(trend.trend)}
                  </div>
                  <CardDescription className="flex items-center gap-2">
                    <MapPin className="h-4 w-4" />
                    {trend.location}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-600">Price Change</p>
                      <p className={`text-lg font-semibold ${
                        trend.trend === 'up' ? 'text-green-600' : 
                        trend.trend === 'down' ? 'text-red-600' : 'text-gray-600'
                      }`}>
                        {trend.trend === 'up' ? '+' : ''}{trend.changePercent}%
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Avg Price</p>
                      <p className="text-lg font-semibold">
                        ${trend.avgPrice.toLocaleString()}
                      </p>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-600">Volume</p>
                      <p className="text-lg font-semibold">{trend.volume}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Confidence</p>
                      <p className="text-lg font-semibold">{trend.confidence}%</p>
                    </div>
                  </div>

                  <div>
                    <p className="text-sm text-gray-600 mb-2">Key Factors</p>
                    <div className="flex flex-wrap gap-1">
                      {trend.factors.map((factor, index) => (
                        <Badge key={index} variant="secondary" className="text-xs">
                          {factor}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  <div className="text-xs text-gray-500">
                    Last updated: {new Date(trend.lastUpdated).toLocaleDateString()}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {filteredTrends.length === 0 && (
            <Card>
              <CardContent className="text-center py-8">
                <BarChart3 className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                <p className="text-gray-600">No trends found matching your criteria</p>
                <Button 
                  variant="outline" 
                  onClick={() => {
                    setSelectedPropertyType('all');
                    setSelectedLocation('all');
                    setSearchQuery('');
                  }}
                  className="mt-2"
                >
                  Clear Filters
                </Button>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="insights" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {filteredInsights.map((insight) => (
              <Card key={insight.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2">
                      {getTypeIcon(insight.type)}
                      <CardTitle className="text-lg capitalize">{insight.type}</CardTitle>
                    </div>
                    <Badge className={getImpactColor(insight.impact)}>
                      {insight.impact} Impact
                    </Badge>
                  </div>
                  <CardDescription className="text-base font-medium">
                    {insight.title}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <p className="text-gray-700">{insight.description}</p>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-600">Confidence</p>
                      <p className="text-lg font-semibold">{insight.confidence}%</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Timeframe</p>
                      <p className="text-lg font-semibold">{insight.timeframe}</p>
                    </div>
                  </div>

                  <div>
                    <p className="text-sm text-gray-600 mb-2">Recommendations</p>
                    <ul className="space-y-2">
                      {insight.recommendations.map((rec, index) => (
                        <li key={index} className="flex items-start gap-2">
                          <div className="w-2 h-2 bg-blue-600 rounded-full mt-2 flex-shrink-0"></div>
                          <span className="text-sm text-gray-700">{rec}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {filteredInsights.length === 0 && (
            <Card>
              <CardContent className="text-center py-8">
                <TrendingUp className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                <p className="text-gray-600">No insights found matching your criteria</p>
                <Button 
                  variant="outline" 
                  onClick={() => {
                    setSelectedPropertyType('all');
                    setSearchQuery('');
                  }}
                  className="mt-2"
                >
                  Clear Filters
                </Button>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>

      {/* Summary Statistics */}
      <Card className="mt-8">
        <CardHeader>
          <CardTitle>Market Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {trends.filter(t => t.trend === 'up').length}
              </div>
              <p className="text-sm text-gray-600">Upward Trends</p>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">
                {trends.filter(t => t.trend === 'down').length}
              </div>
              <p className="text-sm text-gray-600">Downward Trends</p>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {insights.filter(i => i.type === 'opportunity').length}
              </div>
              <p className="text-sm text-gray-600">Opportunities</p>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">
                {insights.filter(i => i.type === 'risk').length}
              </div>
              <p className="text-sm text-gray-600">Risks Identified</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
