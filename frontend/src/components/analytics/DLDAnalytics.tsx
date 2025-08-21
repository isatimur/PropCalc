'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, TrendingUp, TrendingDown, Minus, AlertCircle, Download, FileText, FileSpreadsheet } from 'lucide-react';
import DLDFilters, { DLDFilterState } from './DLDFilters';

interface DLDAnalyticsData {
  summary: {
    total_transactions: number;
    total_volume_aed: number;
    average_price_aed: number;
    market_health_score: number;
    growth_rate_yoy: number;
    market_sentiment: string;
    analysis_period: {
      start_date: string;
      end_date: string;
    };
  };
  trends: {
    price_trends: {
      overall_trend: string;
      luxury_segment: string;
      mid_market: string;
      affordable: string;
    };
    volume_trends: {
      transaction_volume: string;
      market_liquidity: string;
      seasonal_patterns: string;
    };
    market_momentum: string;
  };
  insights: string[];
  recommendations: string[];
  metadata: {
    data_source: string;
    analysis_timestamp: string;
    data_quality_score: number;
    coverage_percentage: number;
  };
}

interface MarketTrendsData {
  timeframe: string;
  property_type: string | null;
  region: string | null;
  price_trends: {
    overall_trend: string;
    luxury_segment: string;
    mid_market: string;
    affordable: string;
    price_per_sqft_trend: string;
    volatility_index: string;
  };
  volume_trends: {
    transaction_volume: string;
    market_liquidity: string;
    seasonal_patterns: string;
    volume_momentum: string;
  };
  market_sentiment: string;
  key_indicators: {
    total_transactions: number;
    total_volume_aed: number;
    average_price_aed: number;
    market_health_score: number;
    growth_rate_yoy: number;
  };
  forecast: {
    next_period_prediction: string;
    confidence_level: number;
    risk_factors: string[];
  } | null;
}

interface PortfolioData {
  portfolio_id: string;
  performance_metrics: {
    total_properties: number;
    total_value_aed: number;
    total_investment_aed: number;
    total_appreciation_aed: number;
    appreciation_percentage: number;
    monthly_rental_income: number;
    annual_rental_yield: number;
    portfolio_diversification_score: number;
    risk_score: number;
    liquidity_score: number;
  };
  risk_assessment: {
    overall_risk: string;
    market_risk: string;
    liquidity_risk: string;
    concentration_risk: string;
    currency_risk: string;
  };
  diversification: {
    property_type_diversification: string;
    location_diversification: string;
    price_range_diversification: string;
    tenant_diversification: string;
  };
  geospatial_analysis: any;
  recommendations: string[];
}

const defaultFilters: DLDFilterState = {
  timeline: '1y',
  startDate: '',
  endDate: '',
  propertyType: '',
  propertyUsage: '',
  propertySubtype: '',
  registrationType: '',
  location: '',
  area: '',
  minPrice: '',
  maxPrice: '',
  developerName: '',
  projectName: '',
  buyerNationality: '',
  sellerNationality: '',
  hasParking: false,
  hasMetro: false,
};

export default function DLDAnalytics() {
  const [analyticsData, setAnalyticsData] = useState<DLDAnalyticsData | null>(null);
  const [marketTrends, setMarketTrends] = useState<MarketTrendsData | null>(null);
  const [portfolioData, setPortfolioData] = useState<PortfolioData | null>(null);
  const [filters, setFilters] = useState<DLDFilterState>(defaultFilters);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const buildQueryParams = (filters: DLDFilterState) => {
    const params = new URLSearchParams();
    
    if (filters.startDate) params.append('start_date', filters.startDate);
    if (filters.endDate) params.append('end_date', filters.endDate);
    if (filters.propertyType) params.append('property_type', filters.propertyType);
    if (filters.propertyUsage) params.append('property_usage', filters.propertyUsage);
    if (filters.propertySubtype) params.append('property_subtype', filters.propertySubtype);
    if (filters.registrationType) params.append('registration_type', filters.registrationType);
    if (filters.location) params.append('location', filters.location);
    if (filters.area) params.append('area', filters.area);
    if (filters.minPrice) params.append('min_price', filters.minPrice);
    if (filters.maxPrice) params.append('max_price', filters.maxPrice);
    if (filters.developerName) params.append('developer_name', filters.developerName);
    if (filters.projectName) params.append('project_name', filters.projectName);
    if (filters.buyerNationality) params.append('buyer_nationality', filters.buyerNationality);
    if (filters.sellerNationality) params.append('seller_nationality', filters.sellerNationality);
    
    return params.toString();
  };

  const fetchAnalytics = async () => {
    setLoading(true);
    setError(null);
    try {
      const queryParams = buildQueryParams(filters);
      const url = `http://localhost:8000/api/v1/dld/analytics${queryParams ? `?${queryParams}` : ''}`;
      
      const response = await fetch(url);
      if (response.ok) {
        const data = await response.json();
        setAnalyticsData(data);
      } else {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
    } catch (error) {
      console.error('Error fetching DLD analytics:', error);
      setError(error instanceof Error ? error.message : 'Failed to fetch analytics');
    }
    setLoading(false);
  };

  const fetchMarketTrends = async () => {
    setLoading(true);
    setError(null);
    try {
      const queryParams = buildQueryParams(filters);
      const url = `http://localhost:8000/api/v1/dld/market-trends?timeframe=${filters.timeline}${queryParams ? `&${queryParams}` : ''}`;
      
      const response = await fetch(url);
      if (response.ok) {
        const data = await response.json();
        setMarketTrends(data);
      } else {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
    } catch (error) {
      console.error('Error fetching market trends:', error);
      setError(error instanceof Error ? error.message : 'Failed to fetch market trends');
    }
    setLoading(false);
  };

  const fetchPortfolio = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:8000/api/v1/dld/portfolio?portfolio_id=test123');
      if (response.ok) {
        const data = await response.json();
        setPortfolioData(data);
      } else {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
    } catch (error) {
      console.error('Error fetching portfolio:', error);
      setError(error instanceof Error ? error.message : 'Failed to fetch portfolio');
    }
    setLoading(false);
  };

  const handleFiltersChange = (newFilters: DLDFilterState) => {
    setFilters(newFilters);
  };

  const handleReset = () => {
    setFilters(defaultFilters);
  };

  const handleApply = () => {
    fetchAnalytics();
    fetchMarketTrends();
  };

  const handleExportCSV = async () => {
    try {
      const queryParams = buildQueryParams(filters);
      const url = `http://localhost:8000/api/v1/dld/export/csv?${queryParams}`;
      
      // Create a temporary link element to trigger download
      const link = document.createElement('a');
      link.href = url;
      link.download = `dld_export_${filters.startDate}_${filters.endDate}.csv`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error('Error exporting CSV:', error);
    }
  };

  const handleExportExcel = async () => {
    try {
      const queryParams = buildQueryParams(filters);
      const url = `http://localhost:8000/api/v1/dld/export/excel?${queryParams}`;
      
      // Create a temporary link element to trigger download
      const link = document.createElement('a');
      link.href = url;
      link.download = `dld_export_${filters.startDate}_${filters.endDate}.xlsx`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error('Error exporting Excel:', error);
    }
  };

  useEffect(() => {
    // Set default dates for 1y timeline
    const endDate = new Date();
    const startDate = new Date();
    startDate.setFullYear(endDate.getFullYear() - 1);
    
    setFilters(prev => ({
      ...prev,
      startDate: startDate.toISOString().split('T')[0],
      endDate: endDate.toISOString().split('T')[0],
    }));
  }, []);

  useEffect(() => {
    if (filters.startDate && filters.endDate) {
      fetchAnalytics();
      fetchMarketTrends();
    }
  }, [filters.startDate, filters.endDate]);

  const formatCurrency = (amount: number) => {
    if (amount >= 1000000000) {
      return `AED ${(amount / 1000000000).toFixed(2)}B`;
    } else if (amount >= 1000000) {
      return `AED ${(amount / 1000000).toFixed(2)}M`;
    } else if (amount >= 1000) {
      return `AED ${(amount / 1000).toFixed(2)}K`;
    }
    return `AED ${amount.toFixed(2)}`;
  };

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment.toLowerCase()) {
      case 'bullish':
        return 'bg-green-100 text-green-800';
      case 'bearish':
        return 'bg-red-100 text-red-800';
      case 'neutral':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk.toLowerCase()) {
      case 'low':
        return 'bg-green-100 text-green-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'high':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend.toLowerCase()) {
      case 'rising':
      case 'increasing':
      case 'strong_growth':
        return <TrendingUp className="h-4 w-4 text-green-600" />;
      case 'falling':
      case 'decreasing':
        return <TrendingDown className="h-4 w-4 text-red-600" />;
      default:
        return <Minus className="h-4 w-4 text-gray-600" />;
    }
  };

  if (error) {
    return (
      <div className="container mx-auto p-6">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            {error}. Please check your connection and try again.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">DLD Analytics Dashboard</h1>
        <div className="flex gap-2">
          <Button onClick={handleApply} disabled={loading}>
            {loading ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : null}
            Refresh Data
          </Button>
          <Button onClick={handleExportCSV} variant="outline" className="flex items-center gap-2">
            <Download className="h-4 w-4" />
            <FileText className="h-4 w-4" />
            Export CSV
          </Button>
          <Button onClick={handleExportExcel} variant="outline" className="flex items-center gap-2">
            <Download className="h-4 w-4" />
            <FileSpreadsheet className="h-4 w-4" />
            Export Excel
          </Button>
        </div>
      </div>

      <DLDFilters
        filters={filters}
        onFiltersChange={handleFiltersChange}
        onReset={handleReset}
        onApply={handleApply}
        isLoading={loading}
      />

      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Market Overview</TabsTrigger>
          <TabsTrigger value="trends">Market Trends</TabsTrigger>
          <TabsTrigger value="portfolio">Portfolio Analysis</TabsTrigger>
          <TabsTrigger value="insights">Insights & Recommendations</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {analyticsData ? (
            <>
              {/* Summary Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Total Transactions</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{analyticsData.summary.total_transactions.toLocaleString()}</div>
                    <p className="text-xs text-muted-foreground">
                      {analyticsData.summary.analysis_period.start_date} - {analyticsData.summary.analysis_period.end_date}
                    </p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Total Volume</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{formatCurrency(analyticsData.summary.total_volume_aed)}</div>
                    <p className="text-xs text-muted-foreground">Transaction volume</p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Market Health</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{analyticsData.summary.market_health_score}/100</div>
                    <Progress value={analyticsData.summary.market_health_score} className="mt-2" />
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Market Sentiment</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <Badge className={getSentimentColor(analyticsData.summary.market_sentiment)}>
                      {analyticsData.summary.market_sentiment}
                    </Badge>
                    <p className="text-xs text-muted-foreground mt-1">
                      YoY Growth: {analyticsData.summary.growth_rate_yoy}%
                    </p>
                  </CardContent>
                </Card>
              </div>

              {/* Trends Overview */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Price Trends</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span>Overall Trend</span>
                      <div className="flex items-center space-x-2">
                        {getTrendIcon(analyticsData.trends.price_trends.overall_trend)}
                        <Badge variant="outline">{analyticsData.trends.price_trends.overall_trend}</Badge>
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <span>Luxury Segment</span>
                      <div className="flex items-center space-x-2">
                        {getTrendIcon(analyticsData.trends.price_trends.luxury_segment)}
                        <Badge variant="outline">{analyticsData.trends.price_trends.luxury_segment}</Badge>
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <span>Mid Market</span>
                      <div className="flex items-center space-x-2">
                        {getTrendIcon(analyticsData.trends.price_trends.mid_market)}
                        <Badge variant="outline">{analyticsData.trends.price_trends.mid_market}</Badge>
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <span>Affordable</span>
                      <div className="flex items-center space-x-2">
                        {getTrendIcon(analyticsData.trends.price_trends.affordable)}
                        <Badge variant="outline">{analyticsData.trends.price_trends.affordable}</Badge>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Volume Trends</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span>Transaction Volume</span>
                      <div className="flex items-center space-x-2">
                        {getTrendIcon(analyticsData.trends.volume_trends.transaction_volume)}
                        <Badge variant="outline">{analyticsData.trends.volume_trends.transaction_volume}</Badge>
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <span>Market Liquidity</span>
                      <div className="flex items-center space-x-2">
                        {getTrendIcon(analyticsData.trends.volume_trends.market_liquidity)}
                        <Badge variant="outline">{analyticsData.trends.volume_trends.market_liquidity}</Badge>
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <span>Seasonal Patterns</span>
                      <div className="flex items-center space-x-2">
                        {getTrendIcon(analyticsData.trends.volume_trends.seasonal_patterns)}
                        <Badge variant="outline">{analyticsData.trends.volume_trends.seasonal_patterns}</Badge>
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <span>Market Momentum</span>
                      <Badge className={getSentimentColor(analyticsData.trends.market_momentum)}>
                        {analyticsData.trends.market_momentum}
                      </Badge>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </>
          ) : (
            <div className="text-center py-12">
              <Loader2 className="h-8 w-8 animate-spin mx-auto text-gray-400" />
              <p className="text-gray-500 mt-2">Loading market overview...</p>
            </div>
          )}
        </TabsContent>

        <TabsContent value="trends" className="space-y-6">
          {marketTrends ? (
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Market Trends Analysis</CardTitle>
                  <CardDescription>
                    Timeframe: {marketTrends.timeframe} | Property Type: {marketTrends.property_type || 'All'} | Region: {marketTrends.region || 'All'}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h4 className="font-semibold mb-3">Price Trends</h4>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span>Overall Trend:</span>
                          <Badge variant="outline">{marketTrends.price_trends.overall_trend}</Badge>
                        </div>
                        <div className="flex justify-between">
                          <span>Luxury Segment:</span>
                          <Badge variant="outline">{marketTrends.price_trends.luxury_segment}</Badge>
                        </div>
                        <div className="flex justify-between">
                          <span>Mid Market:</span>
                          <Badge variant="outline">{marketTrends.price_trends.mid_market}</Badge>
                        </div>
                        <div className="flex justify-between">
                          <span>Affordable:</span>
                          <Badge variant="outline">{marketTrends.price_trends.affordable}</Badge>
                        </div>
                        <div className="flex justify-between">
                          <span>Price per Sqft:</span>
                          <Badge variant="outline">{marketTrends.price_trends.price_per_sqft_trend}</Badge>
                        </div>
                        <div className="flex justify-between">
                          <span>Volatility:</span>
                          <Badge variant="outline">{marketTrends.price_trends.volatility_index}</Badge>
                        </div>
                      </div>
                    </div>
                    <div>
                      <h4 className="font-semibold mb-3">Volume Trends</h4>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span>Transaction Volume:</span>
                          <Badge variant="outline">{marketTrends.volume_trends.transaction_volume}</Badge>
                        </div>
                        <div className="flex justify-between">
                          <span>Market Liquidity:</span>
                          <Badge variant="outline">{marketTrends.volume_trends.market_liquidity}</Badge>
                        </div>
                        <div className="flex justify-between">
                          <span>Seasonal Patterns:</span>
                          <Badge variant="outline">{marketTrends.volume_trends.seasonal_patterns}</Badge>
                        </div>
                        <div className="flex justify-between">
                          <span>Volume Momentum:</span>
                          <Badge variant="outline">{marketTrends.volume_trends.volume_momentum}</Badge>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <Card>
                      <CardHeader className="pb-2">
                        <CardTitle className="text-sm">Total Transactions</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">{marketTrends.key_indicators.total_transactions.toLocaleString()}</div>
                      </CardContent>
                    </Card>
                    <Card>
                      <CardHeader className="pb-2">
                        <CardTitle className="text-sm">Total Volume</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">{formatCurrency(marketTrends.key_indicators.total_volume_aed)}</div>
                      </CardContent>
                    </Card>
                    <Card>
                      <CardHeader className="pb-2">
                        <CardTitle className="text-sm">Market Health</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">{marketTrends.key_indicators.market_health_score}/100</div>
                        <Progress value={marketTrends.key_indicators.market_health_score} className="mt-2" />
                      </CardContent>
                    </Card>
                  </div>

                  {marketTrends.forecast && (
                    <Card>
                      <CardHeader>
                        <CardTitle>Market Forecast</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-3">
                          <div className="flex justify-between">
                            <span>Next Period Prediction:</span>
                            <Badge variant="outline">{marketTrends.forecast.next_period_prediction}</Badge>
                          </div>
                          <div className="flex justify-between">
                            <span>Confidence Level:</span>
                            <Badge variant="outline">{Math.round(marketTrends.forecast.confidence_level * 100)}%</Badge>
                          </div>
                          <div>
                            <span className="font-medium">Risk Factors:</span>
                            <div className="mt-2 space-y-1">
                              {marketTrends.forecast.risk_factors.map((factor, index) => (
                                <div key={index} className="text-sm text-gray-600">• {factor}</div>
                              ))}
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  )}
                </CardContent>
              </Card>
            </div>
          ) : (
            <div className="text-center py-12">
              <Loader2 className="h-8 w-8 animate-spin mx-auto text-gray-400" />
              <p className="text-gray-500 mt-2">Loading market trends...</p>
            </div>
          )}
        </TabsContent>

        <TabsContent value="portfolio" className="space-y-6">
          {portfolioData ? (
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Portfolio Performance</CardTitle>
                  <CardDescription>Portfolio ID: {portfolioData.portfolio_id}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold">{portfolioData.performance_metrics.total_properties}</div>
                      <p className="text-sm text-gray-600">Total Properties</p>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold">{formatCurrency(portfolioData.performance_metrics.total_value_aed)}</div>
                      <p className="text-sm text-gray-600">Total Value</p>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold">{portfolioData.performance_metrics.appreciation_percentage}%</div>
                      <p className="text-sm text-gray-600">Appreciation</p>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold">{portfolioData.performance_metrics.annual_rental_yield}%</div>
                      <p className="text-sm text-gray-600">Rental Yield</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Risk Assessment</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {Object.entries(portfolioData.risk_assessment).map(([key, value]) => (
                      <div key={key} className="flex justify-between items-center">
                        <span className="capitalize">{key.replace('_', ' ')}:</span>
                        <Badge className={getRiskColor(value)}>{value}</Badge>
                      </div>
                    ))}
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Diversification</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {Object.entries(portfolioData.diversification).map(([key, value]) => (
                      <div key={key} className="flex justify-between items-center">
                        <span className="capitalize">{key.replace('_', ' ')}:</span>
                        <Badge variant="outline">{value}</Badge>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              </div>

              <Card>
                <CardHeader>
                  <CardTitle>Recommendations</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {portfolioData.recommendations.map((recommendation, index) => (
                      <div key={index} className="flex items-start space-x-2">
                        <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                        <span className="text-sm">{recommendation}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          ) : (
            <div className="text-center py-12">
              <Loader2 className="h-8 w-8 animate-spin mx-auto text-gray-400" />
              <p className="text-gray-500 mt-2">Loading portfolio analysis...</p>
            </div>
          )}
        </TabsContent>

        <TabsContent value="insights" className="space-y-6">
          {analyticsData ? (
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Market Insights</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {analyticsData.insights.map((insight, index) => (
                      <div key={index} className="flex items-start space-x-2">
                        <div className="w-2 h-2 bg-green-500 rounded-full mt-2 flex-shrink-0"></div>
                        <span className="text-sm">{insight}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Investment Recommendations</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {analyticsData.recommendations.map((recommendation, index) => (
                      <div key={index} className="flex items-start space-x-2">
                        <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                        <span className="text-sm">{recommendation}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Data Quality & Coverage</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold">{Math.round(analyticsData.metadata.data_quality_score * 100)}%</div>
                      <p className="text-sm text-gray-600">Data Quality Score</p>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold">{analyticsData.metadata.coverage_percentage}%</div>
                      <p className="text-sm text-gray-600">Market Coverage</p>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold">{analyticsData.metadata.data_source}</div>
                      <p className="text-sm text-gray-600">Data Source</p>
                    </div>
                  </div>
                  <div className="mt-4 text-sm text-gray-600">
                    Last updated: {new Date(analyticsData.metadata.analysis_timestamp).toLocaleString()}
                  </div>
                </CardContent>
              </Card>
            </div>
          ) : (
            <div className="text-center py-12">
              <Loader2 className="h-8 w-8 animate-spin mx-auto text-gray-400" />
              <p className="text-gray-500 mt-2">Loading insights...</p>
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
