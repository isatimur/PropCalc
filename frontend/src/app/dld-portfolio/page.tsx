"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { 
  Plus, 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  MapPin, 
  Building2,
  Calendar,
  BarChart3,
  PieChart,
  RefreshCw,
  Eye,
  Edit,
  Trash2,
  Download,
  Filter,
  Search,
  Target,
  AlertTriangle,
  CheckCircle,
  Clock
} from "lucide-react";

interface PortfolioProperty {
  id: string;
  name: string;
  location: string;
  property_type: string;
  purchase_date: string;
  purchase_price_aed: number;
  current_value_aed: number;
  area_sqft: number;
  rental_income_monthly: number;
  occupancy_rate: number;
  appreciation_percent: number;
  roi_percent: number;
  status: 'active' | 'pending' | 'sold';
  last_valuation_date: string;
  notes: string;
}

interface PortfolioMetrics {
  total_investment: number;
  current_value: number;
  total_appreciation: number;
  total_roi: number;
  monthly_rental_income: number;
  annual_rental_yield: number;
  portfolio_diversification_score: number;
  risk_score: number;
  liquidity_score: number;
}

interface MarketOpportunity {
  id: string;
  property_type: string;
  location: string;
  estimated_price: number;
  potential_appreciation: number;
  rental_yield_potential: number;
  risk_level: 'low' | 'medium' | 'high';
  market_trend: 'bullish' | 'bearish' | 'neutral';
  recommendation: 'buy' | 'hold' | 'sell';
  reasoning: string[];
}

export default function DLDPortfolioPage() {
  const [portfolioProperties, setPortfolioProperties] = useState<PortfolioProperty[]>([]);
  const [portfolioMetrics, setPortfolioMetrics] = useState<PortfolioMetrics | null>(null);
  const [marketOpportunities, setMarketOpportunities] = useState<MarketOpportunity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState<string>('all');
  const [showAddProperty, setShowAddProperty] = useState(false);

  useEffect(() => {
    fetchPortfolioData();
  }, []);

  const fetchPortfolioData = async () => {
    try {
      setLoading(true);
      // Mock data for now - replace with actual API call
      const mockPortfolioProperties: PortfolioProperty[] = [
        {
          id: '1',
          name: 'Marina Heights Apartment',
          location: 'Dubai Marina',
          property_type: 'Apartment',
          purchase_date: '2022-03-15',
          purchase_price_aed: 2800000,
          current_value_aed: 3200000,
          area_sqft: 1200,
          rental_income_monthly: 18000,
          occupancy_rate: 95,
          appreciation_percent: 14.3,
          roi_percent: 8.2,
          status: 'active',
          last_valuation_date: '2024-01-15',
          notes: 'Excellent location, high rental demand'
        },
        {
          id: '2',
          name: 'Palm Villa',
          location: 'Palm Jumeirah',
          property_type: 'Villa',
          purchase_date: '2021-08-20',
          purchase_price_aed: 7500000,
          current_value_aed: 8500000,
          area_sqft: 3500,
          rental_income_monthly: 45000,
          occupancy_rate: 88,
          appreciation_percent: 13.3,
          roi_percent: 7.2,
          status: 'active',
          last_valuation_date: '2024-01-20',
          notes: 'Luxury property, premium rental market'
        },
        {
          id: '3',
          name: 'Downtown Office Space',
          location: 'Downtown Dubai',
          property_type: 'Office',
          purchase_date: '2023-01-10',
          purchase_price_aed: 4200000,
          current_value_aed: 4500000,
          area_sqft: 2000,
          rental_income_monthly: 25000,
          occupancy_rate: 92,
          appreciation_percent: 7.1,
          roi_percent: 7.1,
          status: 'active',
          last_valuation_date: '2024-01-10',
          notes: 'Commercial property, stable returns'
        }
      ];

      const mockPortfolioMetrics: PortfolioMetrics = {
        total_investment: 14500000,
        current_value: 16200000,
        total_appreciation: 1700000,
        total_roi: 11.7,
        monthly_rental_income: 88000,
        annual_rental_yield: 7.3,
        portfolio_diversification_score: 78,
        risk_score: 42,
        liquidity_score: 65
      };

      const mockMarketOpportunities: MarketOpportunity[] = [
        {
          id: '1',
          property_type: 'Apartment',
          location: 'Jumeirah Beach Residence',
          estimated_price: 3500000,
          potential_appreciation: 12.5,
          rental_yield_potential: 8.5,
          risk_level: 'medium',
          market_trend: 'bullish',
          recommendation: 'buy',
          reasoning: [
            'Growing tourist demand',
            'Infrastructure development',
            'Strong rental market'
          ]
        },
        {
          id: '2',
          property_type: 'Villa',
          location: 'Emirates Hills',
          estimated_price: 12000000,
          potential_appreciation: 15.2,
          rental_yield_potential: 6.8,
          risk_level: 'low',
          market_trend: 'bullish',
          recommendation: 'buy',
          reasoning: [
            'Premium location',
            'Limited supply',
            'High-end market stability'
          ]
        }
      ];

      setPortfolioProperties(mockPortfolioProperties);
      setPortfolioMetrics(mockPortfolioMetrics);
      setMarketOpportunities(mockMarketOpportunities);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch portfolio data');
    } finally {
      setLoading(false);
    }
  };

  const filteredProperties = portfolioProperties.filter(property => {
    const matchesSearch = property.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         property.location.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = filterType === 'all' || property.property_type === filterType;
    return matchesSearch && matchesType;
  });

  const formatCurrency = (amount: number) => {
    if (amount >= 1e6) {
      return `${(amount / 1e6).toFixed(1)}M AED`;
    } else if (amount >= 1e3) {
      return `${(amount / 1e3).toFixed(1)}K AED`;
    }
    return `${amount.toFixed(0)} AED`;
  };

  const formatPercentage = (value: number) => {
    const sign = value >= 0 ? '+' : '';
    return `${sign}${value.toFixed(1)}%`;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'sold':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
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

  const getRecommendationColor = (recommendation: string) => {
    switch (recommendation) {
      case 'buy':
        return 'bg-green-100 text-green-800';
      case 'hold':
        return 'bg-yellow-100 text-yellow-800';
      case 'sell':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="flex items-center space-x-2">
          <RefreshCw className="animate-spin h-6 w-6" />
          <span>Loading Portfolio...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Card className="w-96">
          <CardHeader>
            <CardTitle className="text-red-600">Error</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-600">{error}</p>
            <Button onClick={fetchPortfolioData} className="mt-4">
              <RefreshCw className="h-4 w-4 mr-2" />
              Retry
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">DLD Investment Portfolio</h1>
          <p className="text-gray-600 mt-2">
            Manage and analyze your real estate investment portfolio
          </p>
        </div>
        <div className="flex space-x-2">
          <Button onClick={() => setShowAddProperty(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Add Property
          </Button>
          <Button onClick={fetchPortfolioData} variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Portfolio Overview Cards */}
      {portfolioMetrics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Investment</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatCurrency(portfolioMetrics.total_investment)}</div>
              <p className="text-xs text-muted-foreground">
                Initial capital invested
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Current Value</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatCurrency(portfolioMetrics.current_value)}</div>
              <p className="text-xs text-muted-foreground">
                {formatPercentage(portfolioMetrics.total_roi)} total ROI
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Monthly Rental</CardTitle>
              <Calendar className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatCurrency(portfolioMetrics.monthly_rental_income)}</div>
              <p className="text-xs text-muted-foreground">
                {portfolioMetrics.annual_rental_yield.toFixed(1)}% annual yield
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Risk Score</CardTitle>
              <AlertTriangle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{portfolioMetrics.risk_score}/100</div>
              <p className="text-xs text-muted-foreground">
                Lower is better
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Main Content Tabs */}
      <Tabs defaultValue="portfolio" className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="portfolio">Portfolio</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
          <TabsTrigger value="opportunities">Market Opportunities</TabsTrigger>
        </TabsList>

        {/* Portfolio Tab */}
        <TabsContent value="portfolio" className="space-y-6">
          {/* Search and Filter */}
          <Card>
            <CardHeader>
              <CardTitle>Portfolio Properties</CardTitle>
              <CardDescription>
                Manage and monitor your real estate investments
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col sm:flex-row gap-4 mb-6">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    placeholder="Search properties..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
                <select
                  value={filterType}
                  onChange={(e) => setFilterType(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="all">All Types</option>
                  <option value="Apartment">Apartment</option>
                  <option value="Villa">Villa</option>
                  <option value="Office">Office</option>
                  <option value="Retail">Retail</option>
                </select>
              </div>

              <div className="space-y-4">
                {filteredProperties.map((property) => (
                  <div key={property.id} className="border rounded-lg p-4">
                    <div className="flex justify-between items-start mb-4">
                      <div className="flex items-center space-x-3">
                        <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                          <Building2 className="h-6 w-6 text-blue-600" />
                        </div>
                        <div>
                          <div className="font-medium text-lg">{property.name}</div>
                          <div className="text-sm text-muted-foreground flex items-center space-x-2">
                            <MapPin className="h-4 w-4" />
                            <span>{property.location}</span>
                            <span>•</span>
                            <span>{property.property_type}</span>
                          </div>
                        </div>
                      </div>
                      <div className="flex space-x-2">
                        <Badge className={getStatusColor(property.status)}>
                          {property.status}
                        </Badge>
                        <Button variant="outline" size="sm">
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button variant="outline" size="sm">
                          <Edit className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <span className="text-muted-foreground">Purchase Price:</span>
                        <div className="font-medium">{formatCurrency(property.purchase_price_aed)}</div>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Current Value:</span>
                        <div className="font-medium">{formatCurrency(property.current_value_aed)}</div>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Appreciation:</span>
                        <div className={`font-medium ${property.appreciation_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {formatPercentage(property.appreciation_percent)}
                        </div>
                      </div>
                      <div>
                        <span className="text-muted-foreground">ROI:</span>
                        <div className="font-medium text-blue-600">{property.roi_percent.toFixed(1)}%</div>
                      </div>
                    </div>

                    <div className="mt-4 pt-4 border-t grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                      <div>
                        <span className="text-muted-foreground">Monthly Rental:</span>
                        <div className="font-medium">{formatCurrency(property.rental_income_monthly)}</div>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Occupancy Rate:</span>
                        <div className="font-medium">{property.occupancy_rate}%</div>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Area:</span>
                        <div className="font-medium">{property.area_sqft.toLocaleString()} sq ft</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Analytics Tab */}
        <TabsContent value="analytics" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Portfolio Performance */}
            <Card>
              <CardHeader>
                <CardTitle>Portfolio Performance</CardTitle>
                <CardDescription>
                  Key performance indicators and metrics
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between items-center">
                  <span>Diversification Score</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-24 bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full" 
                        style={{ width: `${portfolioMetrics?.portfolio_diversification_score || 0}%` }}
                      ></div>
                    </div>
                    <span className="text-sm font-medium">{portfolioMetrics?.portfolio_diversification_score || 0}%</span>
                  </div>
                </div>
                
                <div className="flex justify-between items-center">
                  <span>Risk Score</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-24 bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-red-600 h-2 rounded-full" 
                        style={{ width: `${portfolioMetrics?.risk_score || 0}%` }}
                      ></div>
                    </div>
                    <span className="text-sm font-medium">{portfolioMetrics?.risk_score || 0}/100</span>
                  </div>
                </div>
                
                <div className="flex justify-between items-center">
                  <span>Liquidity Score</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-24 bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-green-600 h-2 rounded-full" 
                        style={{ width: `${portfolioMetrics?.liquidity_score || 0}%` }}
                      ></div>
                    </div>
                    <span className="text-sm font-medium">{portfolioMetrics?.liquidity_score || 0}%</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Property Distribution */}
            <Card>
              <CardHeader>
                <CardTitle>Property Distribution</CardTitle>
                <CardDescription>
                  Portfolio allocation by property type
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {['Apartment', 'Villa', 'Office'].map((type) => {
                    const properties = portfolioProperties.filter(p => p.property_type === type);
                    const totalValue = properties.reduce((sum, p) => sum + p.current_value_aed, 0);
                    const percentage = portfolioMetrics ? (totalValue / portfolioMetrics.current_value) * 100 : 0;
                    
                    return (
                      <div key={type} className="flex justify-between items-center">
                        <span className="text-sm">{type}</span>
                        <div className="flex items-center space-x-2">
                          <div className="w-24 bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-blue-600 h-2 rounded-full" 
                              style={{ width: `${percentage}%` }}
                            ></div>
                          </div>
                          <span className="text-sm font-medium">{percentage.toFixed(1)}%</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Market Opportunities Tab */}
        <TabsContent value="opportunities" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Market Opportunities</CardTitle>
              <CardDescription>
                Recommended investment opportunities based on market analysis
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {marketOpportunities.map((opportunity) => (
                  <div key={opportunity.id} className="border rounded-lg p-4">
                    <div className="flex justify-between items-start mb-4">
                      <div className="flex items-center space-x-3">
                        <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                          <Target className="h-6 w-6 text-green-600" />
                        </div>
                        <div>
                          <div className="font-medium text-lg">{opportunity.property_type} - {opportunity.location}</div>
                          <div className="text-sm text-muted-foreground">
                            Estimated Price: {formatCurrency(opportunity.estimated_price)}
                          </div>
                        </div>
                      </div>
                      <div className="flex space-x-2">
                        <Badge className={getRiskColor(opportunity.risk_level)}>
                          {opportunity.risk_level} risk
                        </Badge>
                        <Badge className={getRecommendationColor(opportunity.recommendation)}>
                          {opportunity.recommendation.toUpperCase()}
                        </Badge>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm mb-4">
                      <div>
                        <span className="text-muted-foreground">Potential Appreciation:</span>
                        <div className="font-medium text-green-600">
                          {formatPercentage(opportunity.potential_appreciation)}
                        </div>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Rental Yield Potential:</span>
                        <div className="font-medium text-blue-600">
                          {opportunity.rental_yield_potential.toFixed(1)}%
                        </div>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Market Trend:</span>
                        <div className="font-medium capitalize">{opportunity.market_trend}</div>
                      </div>
                    </div>

                    <div>
                      <h4 className="font-medium mb-2">Investment Reasoning</h4>
                      <ul className="space-y-1 text-sm">
                        {opportunity.reasoning.map((reason, index) => (
                          <li key={index} className="flex items-center space-x-2">
                            <CheckCircle className="h-4 w-4 text-green-600" />
                            <span>{reason}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    <div className="mt-4 pt-4 border-t flex justify-end space-x-2">
                      <Button variant="outline" size="sm">
                        <Eye className="h-4 w-4 mr-2" />
                        View Details
                      </Button>
                      <Button size="sm">
                        <Plus className="h-4 w-4 mr-2" />
                        Add to Watchlist
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
