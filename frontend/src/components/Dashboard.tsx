'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { 
  TrendingUp, 
  TrendingDown, 
  Building2, 
  MapPin, 
  DollarSign, 
  Users, 
  Activity,
  Database,
  BarChart3,
  Target,
  Clock,
  CheckCircle,
  AlertCircle,
  Info
} from 'lucide-react';
import { formatNumber, formatPercentage, formatCurrency } from '@/lib/utils';
import { 
  useRealMarketData, 
  useRealProjects, 
  useRealVantageScoreStats,
  useRealDataQuality,
  useRealMarketTrends
} from '@/hooks/useApi';

export default function Dashboard() {
  const { marketData, loading: marketLoading, error: marketError } = useRealMarketData();
  const { projects, loading: projectsLoading, error: projectsError } = useRealProjects(8);
  const { stats, loading: statsLoading, error: statsError } = useRealVantageScoreStats();
  const { quality, loading: qualityLoading, error: qualityError } = useRealDataQuality();
  const { trends, loading: trendsLoading, error: trendsError } = useRealMarketTrends();

  if (marketLoading || projectsLoading || statsLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="flex items-center space-x-2">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="text-sm text-muted-foreground">Loading real data...</span>
        </div>
      </div>
    );
  }

  if (marketError || projectsError || statsError) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold mb-2">Error Loading Data</h2>
          <p className="text-muted-foreground mb-4">
            {marketError || projectsError || statsError}
          </p>
          <Button onClick={() => window.location.reload()}>
            Retry
          </Button>
        </div>
      </div>
    );
  }

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment?.toLowerCase()) {
      case 'positive':
        return 'bg-green-100 text-green-800';
      case 'negative':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-yellow-100 text-yellow-800';
    }
  };

  const getSentimentIcon = (sentiment: string) => {
    switch (sentiment?.toLowerCase()) {
      case 'positive':
        return <TrendingUp className="h-4 w-4" />;
      case 'negative':
        return <TrendingDown className="h-4 w-4" />;
      default:
        return <Activity className="h-4 w-4" />;
    }
  };

  return (
    <div className="space-y-6 p-6">
      {/* Header with Real Data Indicator */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">PropCalc Dashboard</h1>
          <p className="text-muted-foreground">Real-time Dubai real estate analytics</p>
        </div>
        <div className="flex items-center space-x-2">
          <Badge variant="outline" className="flex items-center space-x-1">
            <Database className="h-3 w-3" />
            <span>Real DLD Data</span>
          </Badge>
          {quality && (
            <Badge variant="outline" className="flex items-center space-x-1">
              <CheckCircle className="h-3 w-3" />
              <span>{formatNumber(quality.total_transactions)} Transactions</span>
            </Badge>
          )}
        </div>
      </div>

      {/* Market Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Transactions</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatNumber(marketData?.total_transactions || 0)}
            </div>
            <p className="text-xs text-muted-foreground">
              Real DLD transactions
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Average Price</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(marketData?.average_price || 0)}
            </div>
            <p className="text-xs text-muted-foreground">
              AED per transaction
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Market Sentiment</CardTitle>
            {getSentimentIcon(marketData?.market_sentiment || 'neutral')}
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold capitalize">
              {marketData?.market_sentiment || 'neutral'}
            </div>
            <p className="text-xs text-muted-foreground">
              Based on 30-day trends
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Vantage Score</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatNumber(marketData?.average_vantage_score || 0)}
            </div>
            <p className="text-xs text-muted-foreground">
              AI-powered scoring
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Market Trends & Real Data Quality */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <BarChart3 className="h-5 w-5" />
              <span>Market Trends (30 Days)</span>
            </CardTitle>
            <CardDescription>Real-time market performance indicators</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {trends && (
              <>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Price Change</span>
                  <div className="flex items-center space-x-2">
                    {trends.price_change_30d > 0 ? (
                      <TrendingUp className="h-4 w-4 text-green-500" />
                    ) : (
                      <TrendingDown className="h-4 w-4 text-red-500" />
                    )}
                    <span className={`text-sm font-medium ${
                      trends.price_change_30d > 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {formatPercentage(Math.abs(trends.price_change_30d || 0))}
                    </span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Volume Change</span>
                  <div className="flex items-center space-x-2">
                    {trends.volume_change_30d > 0 ? (
                      <TrendingUp className="h-4 w-4 text-green-500" />
                    ) : (
                      <TrendingDown className="h-4 w-4 text-red-500" />
                    )}
                    <span className={`text-sm font-medium ${
                      trends.volume_change_30d > 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {formatPercentage(Math.abs(trends.volume_change_30d || 0))}
                    </span>
                  </div>
                </div>
              </>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Info className="h-5 w-5" />
              <span>Data Quality & Freshness</span>
            </CardTitle>
            <CardDescription>Real DLD data insights</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {quality && (
              <>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Data Source</span>
                  <Badge variant="outline">Dubai Land Department</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Total Records</span>
                  <span className="text-sm font-medium">
                    {formatNumber(quality.total_transactions)}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Average Price</span>
                  <span className="text-sm font-medium">
                    {formatCurrency(quality.average_price)}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Last Updated</span>
                  <div className="flex items-center space-x-1">
                    <Clock className="h-3 w-3 text-muted-foreground" />
                    <span className="text-sm text-muted-foreground">Real-time</span>
                  </div>
                </div>
              </>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Top Locations Section */}
      {marketData?.top_locations && marketData.top_locations.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <MapPin className="h-5 w-5" />
              <span>Top Performing Locations</span>
            </CardTitle>
            <CardDescription>Areas with highest transaction volume</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {marketData.top_locations.slice(0, 6).map((location, index) => (
                <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                    <span className="text-sm font-medium">{location.name}</span>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-medium">
                      {formatNumber(location.transactions)} transactions
                    </div>
                    <div className="text-xs text-muted-foreground">
                      {formatCurrency(location.avg_price)} avg
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Property Types Analysis */}
      {marketData?.property_types && marketData.property_types.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Building2 className="h-5 w-5" />
              <span>Property Type Distribution</span>
            </CardTitle>
            <CardDescription>Market breakdown by property type</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {marketData.property_types.slice(0, 6).map((type, index) => (
                <div key={index} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">{type.type}</span>
                    <span className="text-sm text-muted-foreground">
                      {formatNumber(type.count)} units
                    </span>
                  </div>
                  <Progress value={(type.count / (marketData.total_properties || 1)) * 100} />
                  <div className="text-xs text-muted-foreground">
                    Avg: {formatCurrency(type.avg_price)}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Recent Projects */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Building2 className="h-5 w-5" />
            <span>Recent Projects</span>
          </CardTitle>
          <CardDescription>Latest real estate developments with real data</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects.slice(0, 6).map((project) => (
              <div key={project.id} className="space-y-3">
                <div className="flex items-start justify-between">
                  <div className="space-y-1">
                    <h3 className="font-medium text-sm">{project.name}</h3>
                    <p className="text-xs text-muted-foreground">{project.location}</p>
                  </div>
                  <Badge variant="outline" className="text-xs">
                    {project.property_type || 'Residential'}
                  </Badge>
                </div>
                
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Price</span>
                    <span className="font-medium">
                      {project.price ? formatCurrency(project.price) : 'N/A'}
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Area</span>
                    <span className="font-medium">
                      {project.area ? `${formatNumber(project.area)} sqft` : 'N/A'}
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Vantage Score</span>
                    <div className="flex items-center space-x-1">
                      <Target className="h-3 w-3 text-blue-500" />
                      <span className="font-medium">
                        {project.vantage_score ? formatNumber(project.vantage_score) : 'N/A'}
                      </span>
                    </div>
                  </div>
                </div>
                
                {project.developer && (
                  <div className="text-xs text-muted-foreground">
                    Developer: {project.developer}
                  </div>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Vantage Score Statistics */}
      {stats && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Target className="h-5 w-5" />
              <span>Vantage Score™ Analytics</span>
            </CardTitle>
            <CardDescription>AI-powered property scoring insights</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {stats.data && (
                <>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600">
                      {formatNumber(stats.data.total_transactions)}
                    </div>
                    <div className="text-sm text-muted-foreground">Properties Analyzed</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600">
                      {formatCurrency(stats.data.average_price)}
                    </div>
                    <div className="text-sm text-muted-foreground">Average Price</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-purple-600">
                      {stats.data.data_freshness || 'Real-time'}
                    </div>
                    <div className="text-sm text-muted-foreground">Data Freshness</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-orange-600">
                      {stats.data.data_source || 'DLD'}
                    </div>
                    <div className="text-sm text-muted-foreground">Data Source</div>
                  </div>
                </>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
} 