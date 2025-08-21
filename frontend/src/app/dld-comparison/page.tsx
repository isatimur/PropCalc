"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { 
  Search, 
  Filter, 
  BarChart3, 
  TrendingUp, 
  TrendingDown, 
  Minus,
  MapPin,
  Building2,
  DollarSign,
  Calendar,
  Target,
  RefreshCw,
  Download,
  Eye,
  Plus,
  CheckCircle,
  AlertTriangle,
  Clock
} from "lucide-react";

interface PropertyComparison {
  id: string;
  name: string;
  location: string;
  property_type: string;
  price_aed: number;
  price_per_sqft: number;
  area_sqft: number;
  bedrooms?: number;
  bathrooms?: number;
  age_years: number;
  rental_yield: number;
  appreciation_1y: number;
  appreciation_3y: number;
  market_demand: 'high' | 'medium' | 'low';
  investment_score: number;
  risk_level: 'low' | 'medium' | 'high';
  amenities: string[];
  transportation_score: number;
  school_score: number;
  shopping_score: number;
}

interface LocationComparison {
  location: string;
  avg_price_aed: number;
  avg_price_per_sqft: number;
  transaction_volume: number;
  price_trend_6m: number;
  price_trend_12m: number;
  rental_yield_avg: number;
  market_volatility: number;
  infrastructure_score: number;
  future_growth_potential: number;
  investment_grade: 'A' | 'B' | 'C' | 'D';
}

interface MarketSegmentComparison {
  segment: string;
  avg_price: number;
  price_growth: number;
  demand_trend: 'increasing' | 'decreasing' | 'stable';
  supply_level: 'high' | 'medium' | 'low';
  rental_market: 'strong' | 'moderate' | 'weak';
  investment_opportunity: 'excellent' | 'good' | 'fair' | 'poor';
  key_advantages: string[];
  key_risks: string[];
}

export default function DLDComparisonPage() {
  const [properties, setProperties] = useState<PropertyComparison[]>([]);
  const [locations, setLocations] = useState<LocationComparison[]>([]);
  const [marketSegments, setMarketSegments] = useState<MarketSegmentComparison[]>([]);
  const [selectedProperties, setSelectedProperties] = useState<string[]>([]);
  const [selectedLocations, setSelectedLocations] = useState<string[]>([]);
  const [selectedSegments, setSelectedSegments] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState<string>('all');

  useEffect(() => {
    fetchComparisonData();
  }, []);

  const fetchComparisonData = async () => {
    try {
      setLoading(true);
      // Mock data for now - replace with actual API call
      const mockProperties: PropertyComparison[] = [
        {
          id: '1',
          name: 'Marina Heights Tower',
          location: 'Dubai Marina',
          property_type: 'Apartment',
          price_aed: 3200000,
          price_per_sqft: 2667,
          area_sqft: 1200,
          bedrooms: 2,
          bathrooms: 2,
          age_years: 3,
          rental_yield: 7.2,
          appreciation_1y: 12.5,
          appreciation_3y: 28.3,
          market_demand: 'high',
          investment_score: 85,
          risk_level: 'low',
          amenities: ['Pool', 'Gym', 'Security', 'Parking'],
          transportation_score: 9,
          school_score: 7,
          shopping_score: 9
        },
        {
          id: '2',
          name: 'Palm Vista Villa',
          location: 'Palm Jumeirah',
          property_type: 'Villa',
          price_aed: 8500000,
          price_per_sqft: 2429,
          area_sqft: 3500,
          bedrooms: 4,
          bathrooms: 5,
          age_years: 2,
          rental_yield: 6.8,
          appreciation_1y: 15.2,
          appreciation_3y: 32.1,
          market_demand: 'high',
          investment_score: 88,
          risk_level: 'medium',
          amenities: ['Private Pool', 'Garden', 'Security', 'Beach Access'],
          transportation_score: 6,
          school_score: 8,
          shopping_score: 7
        },
        {
          id: '3',
          name: 'Downtown Business Center',
          location: 'Downtown Dubai',
          property_type: 'Office',
          price_aed: 4500000,
          price_per_sqft: 2250,
          area_sqft: 2000,
          age_years: 5,
          rental_yield: 8.1,
          appreciation_1y: 8.7,
          appreciation_3y: 18.9,
          market_demand: 'medium',
          investment_score: 72,
          risk_level: 'medium',
          amenities: ['Reception', 'Security', 'Parking', 'Meeting Rooms'],
          transportation_score: 10,
          school_score: 6,
          shopping_score: 10
        }
      ];

      const mockLocations: LocationComparison[] = [
        {
          location: 'Dubai Marina',
          avg_price_aed: 3200000,
          avg_price_per_sqft: 2667,
          transaction_volume: 450,
          price_trend_6m: 8.5,
          price_trend_12m: 15.2,
          rental_yield_avg: 7.2,
          market_volatility: 12.3,
          infrastructure_score: 85,
          future_growth_potential: 78,
          investment_grade: 'A'
        },
        {
          location: 'Palm Jumeirah',
          avg_price_aed: 8500000,
          avg_price_per_sqft: 2429,
          transaction_volume: 280,
          price_trend_6m: 6.2,
          price_trend_12m: 12.8,
          rental_yield_avg: 6.8,
          market_volatility: 15.7,
          infrastructure_score: 78,
          future_growth_potential: 72,
          investment_grade: 'A'
        },
        {
          location: 'Downtown Dubai',
          avg_price_aed: 4200000,
          avg_price_per_sqft: 2100,
          transaction_volume: 320,
          price_trend_6m: 4.8,
          price_trend_12m: 9.6,
          rental_yield_avg: 8.1,
          market_volatility: 18.2,
          infrastructure_score: 92,
          future_growth_potential: 65,
          investment_grade: 'B'
        }
      ];

      const mockMarketSegments: MarketSegmentComparison[] = [
        {
          segment: 'Luxury Apartments',
          avg_price: 4500000,
          price_growth: 12.5,
          demand_trend: 'increasing',
          supply_level: 'low',
          rental_market: 'strong',
          investment_opportunity: 'excellent',
          key_advantages: ['High rental yields', 'Strong appreciation', 'Limited supply'],
          key_risks: ['Market volatility', 'High entry cost', 'Economic sensitivity']
        },
        {
          segment: 'Premium Villas',
          avg_price: 12000000,
          price_growth: 15.2,
          demand_trend: 'increasing',
          supply_level: 'low',
          rental_market: 'strong',
          investment_opportunity: 'excellent',
          key_advantages: ['Exclusive locations', 'High capital appreciation', 'Premium rental market'],
          key_risks: ['Illiquidity', 'High maintenance costs', 'Market concentration risk']
        },
        {
          segment: 'Commercial Offices',
          avg_price: 3800000,
          price_growth: 6.8,
          demand_trend: 'stable',
          supply_level: 'medium',
          rental_market: 'moderate',
          investment_opportunity: 'good',
          key_advantages: ['Stable returns', 'Long-term leases', 'Corporate tenants'],
          key_risks: ['Economic sensitivity', 'Vacancy risk', 'Regulatory changes']
        }
      ];

      setProperties(mockProperties);
      setLocations(mockLocations);
      setMarketSegments(mockMarketSegments);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch comparison data');
    } finally {
      setLoading(false);
    }
  };

  const togglePropertySelection = (propertyId: string) => {
    setSelectedProperties(prev => 
      prev.includes(propertyId) 
        ? prev.filter(id => id !== propertyId)
        : [...prev, propertyId]
    );
  };

  const toggleLocationSelection = (location: string) => {
    setSelectedLocations(prev => 
      prev.includes(location) 
        ? prev.filter(loc => loc !== location)
        : [...prev, location]
    );
  };

  const toggleSegmentSelection = (segment: string) => {
    setSelectedSegments(prev => 
      prev.includes(segment) 
        ? prev.filter(seg => seg !== segment)
        : [...prev, segment]
    );
  };

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

  const getDemandColor = (demand: string) => {
    switch (demand) {
      case 'high':
        return 'bg-green-100 text-green-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'low':
        return 'bg-red-100 text-red-800';
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

  const getInvestmentGradeColor = (grade: string) => {
    switch (grade) {
      case 'A':
        return 'bg-green-100 text-green-800';
      case 'B':
        return 'bg-blue-100 text-blue-800';
      case 'C':
        return 'bg-yellow-100 text-yellow-800';
      case 'D':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getOpportunityColor = (opportunity: string) => {
    switch (opportunity) {
      case 'excellent':
        return 'bg-green-100 text-green-800';
      case 'good':
        return 'bg-blue-100 text-blue-800';
      case 'fair':
        return 'bg-yellow-100 text-yellow-800';
      case 'poor':
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
          <span>Loading Comparison Data...</span>
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
            <Button onClick={fetchComparisonData} className="mt-4">
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
          <h1 className="text-3xl font-bold text-gray-900">DLD Comparative Analysis</h1>
          <p className="text-gray-600 mt-2">
            Compare properties, locations, and market segments for informed investment decisions
          </p>
        </div>
        <div className="flex space-x-2">
          <Button onClick={fetchComparisonData} variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh Data
          </Button>
          <Button>
            <Download className="h-4 w-4 mr-2" />
            Export Report
          </Button>
        </div>
      </div>

      {/* Main Content Tabs */}
      <Tabs defaultValue="properties" className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="properties">Property Comparison</TabsTrigger>
          <TabsTrigger value="locations">Location Analysis</TabsTrigger>
          <TabsTrigger value="segments">Market Segments</TabsTrigger>
        </TabsList>

        {/* Property Comparison Tab */}
        <TabsContent value="properties" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Property Comparison</CardTitle>
              <CardDescription>
                Select up to 3 properties to compare side by side
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
                </select>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {properties.map((property) => (
                  <Card 
                    key={property.id} 
                    className={`cursor-pointer transition-all ${
                      selectedProperties.includes(property.id) 
                        ? 'ring-2 ring-blue-500 bg-blue-50' 
                        : 'hover:shadow-md'
                    }`}
                    onClick={() => togglePropertySelection(property.id)}
                  >
                    <CardHeader className="pb-3">
                      <div className="flex justify-between items-start">
                        <div>
                          <CardTitle className="text-lg">{property.name}</CardTitle>
                          <CardDescription className="flex items-center space-x-2 mt-2">
                            <MapPin className="h-4 w-4" />
                            <span>{property.location}</span>
                          </CardDescription>
                        </div>
                        <div className="flex space-x-2">
                          <Badge variant="outline">{property.property_type}</Badge>
                          {selectedProperties.includes(property.id) && (
                            <CheckCircle className="h-5 w-5 text-blue-600" />
                          )}
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <div className="grid grid-cols-2 gap-3 text-sm">
                        <div>
                          <span className="text-muted-foreground">Price:</span>
                          <div className="font-medium">{formatCurrency(property.price_aed)}</div>
                        </div>
                        <div>
                          <span className="text-muted-foreground">Price/sq ft:</span>
                          <div className="font-medium">{property.price_per_sqft.toLocaleString()} AED</div>
                        </div>
                        <div>
                          <span className="text-muted-foreground">Area:</span>
                          <div className="font-medium">{property.area_sqft.toLocaleString()} sq ft</div>
                        </div>
                        <div>
                          <span className="text-muted-foreground">Rental Yield:</span>
                          <div className="font-medium text-blue-600">{property.rental_yield.toFixed(1)}%</div>
                        </div>
                      </div>
                      
                      <div className="pt-2 border-t">
                        <div className="flex justify-between items-center text-sm">
                          <span>Investment Score:</span>
                          <div className="flex items-center space-x-2">
                            <div className="w-16 bg-gray-200 rounded-full h-2">
                              <div 
                                className="bg-blue-600 h-2 rounded-full" 
                                style={{ width: `${property.investment_score}%` }}
                              ></div>
                            </div>
                            <span className="font-medium">{property.investment_score}/100</span>
                          </div>
                        </div>
                      </div>

                      <div className="flex space-x-2">
                        <Badge className={getDemandColor(property.market_demand)}>
                          {property.market_demand} demand
                        </Badge>
                        <Badge className={getRiskColor(property.risk_level)}>
                          {property.risk_level} risk
                        </Badge>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>

              {/* Comparison Table */}
              {selectedProperties.length > 0 && (
                <div className="mt-8">
                  <h3 className="text-lg font-semibold mb-4">Comparison Table</h3>
                  <div className="overflow-x-auto">
                    <table className="w-full border-collapse border border-gray-200">
                      <thead>
                        <tr className="bg-gray-50">
                          <th className="border border-gray-200 p-3 text-left">Metric</th>
                          {selectedProperties.map(propId => {
                            const prop = properties.find(p => p.id === propId);
                            return (
                              <th key={propId} className="border border-gray-200 p-3 text-left">
                                {prop?.name}
                              </th>
                            );
                          })}
                        </tr>
                      </thead>
                      <tbody>
                        <tr>
                          <td className="border border-gray-200 p-3 font-medium">Location</td>
                          {selectedProperties.map(propId => {
                            const prop = properties.find(p => p.id === propId);
                            return (
                              <td key={propId} className="border border-gray-200 p-3">
                                {prop?.location}
                              </td>
                            );
                          })}
                        </tr>
                        <tr className="bg-gray-50">
                          <td className="border border-gray-200 p-3 font-medium">Price</td>
                          {selectedProperties.map(propId => {
                            const prop = properties.find(p => p.id === propId);
                            return (
                              <td key={propId} className="border border-gray-200 p-3">
                                {formatCurrency(prop?.price_aed || 0)}
                              </td>
                            );
                          })}
                        </tr>
                        <tr>
                          <td className="border border-gray-200 p-3 font-medium">Price per sq ft</td>
                          {selectedProperties.map(propId => {
                            const prop = properties.find(p => p.id === propId);
                            return (
                              <td key={propId} className="border border-gray-200 p-3">
                                {prop?.price_per_sqft.toLocaleString()} AED
                              </td>
                            );
                          })}
                        </tr>
                        <tr className="bg-gray-50">
                          <td className="border border-gray-200 p-3 font-medium">Rental Yield</td>
                          {selectedProperties.map(propId => {
                            const prop = properties.find(p => p.id === propId);
                            return (
                              <td key={propId} className="border border-gray-200 p-3">
                                {prop?.rental_yield.toFixed(1)}%
                              </td>
                            );
                          })}
                        </tr>
                        <tr>
                          <td className="border border-gray-200 p-3 font-medium">1Y Appreciation</td>
                          {selectedProperties.map(propId => {
                            const prop = properties.find(p => p.id === propId);
                            return (
                              <td key={propId} className="border border-gray-200 p-3">
                                {formatPercentage(prop?.appreciation_1y || 0)}
                              </td>
                            );
                          })}
                        </tr>
                        <tr className="bg-gray-50">
                          <td className="border border-gray-200 p-3 font-medium">Investment Score</td>
                          {selectedProperties.map(propId => {
                            const prop = properties.find(p => p.id === propId);
                            return (
                              <td key={propId} className="border border-gray-200 p-3">
                                {prop?.investment_score}/100
                              </td>
                            );
                          })}
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Location Analysis Tab */}
        <TabsContent value="locations" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Location Comparison</CardTitle>
              <CardDescription>
                Compare different locations for investment potential
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {locations.map((location) => (
                  <Card 
                    key={location.location} 
                    className={`cursor-pointer transition-all ${
                      selectedLocations.includes(location.location) 
                        ? 'ring-2 ring-blue-500 bg-blue-50' 
                        : 'hover:shadow-md'
                    }`}
                    onClick={() => toggleLocationSelection(location.location)}
                  >
                    <CardHeader className="pb-3">
                      <div className="flex justify-between items-start">
                        <div>
                          <CardTitle className="text-lg">{location.location}</CardTitle>
                          <CardDescription className="mt-2">
                            Investment Grade: {location.investment_grade}
                          </CardDescription>
                        </div>
                        <div className="flex space-x-2">
                          <Badge className={getInvestmentGradeColor(location.investment_grade)}>
                            Grade {location.investment_grade}
                          </Badge>
                          {selectedLocations.includes(location.location) && (
                            <CheckCircle className="h-5 w-5 text-blue-600" />
                          )}
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <div className="grid grid-cols-2 gap-3 text-sm">
                        <div>
                          <span className="text-muted-foreground">Avg Price:</span>
                          <div className="font-medium">{formatCurrency(location.avg_price_aed)}</div>
                        </div>
                        <div>
                          <span className="text-muted-foreground">Price/sq ft:</span>
                          <div className="font-medium">{location.avg_price_per_sqft.toLocaleString()} AED</div>
                        </div>
                        <div>
                          <span className="text-muted-foreground">6M Trend:</span>
                          <div className={`font-medium ${location.price_trend_6m >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {formatPercentage(location.price_trend_6m)}
                          </div>
                        </div>
                        <div>
                          <span className="text-muted-foreground">Rental Yield:</span>
                          <div className="font-medium text-blue-600">{location.rental_yield_avg.toFixed(1)}%</div>
                        </div>
                      </div>
                      
                      <div className="pt-2 border-t space-y-2">
                        <div className="flex justify-between items-center text-sm">
                          <span>Infrastructure:</span>
                          <div className="flex items-center space-x-2">
                            <div className="w-16 bg-gray-200 rounded-full h-2">
                              <div 
                                className="bg-blue-600 h-2 rounded-full" 
                                style={{ width: `${location.infrastructure_score}%` }}
                              ></div>
                            </div>
                            <span className="font-medium">{location.infrastructure_score}/100</span>
                          </div>
                        </div>
                        <div className="flex justify-between items-center text-sm">
                          <span>Growth Potential:</span>
                          <div className="flex items-center space-x-2">
                            <div className="w-16 bg-gray-200 rounded-full h-2">
                              <div 
                                className="bg-green-600 h-2 rounded-full" 
                                style={{ width: `${location.future_growth_potential}%` }}
                              ></div>
                            </div>
                            <span className="font-medium">{location.future_growth_potential}/100</span>
                          </div>
                        </div>
                      </div>

                      <div className="flex space-x-2">
                        <Badge variant="outline">
                          {location.transaction_volume} transactions
                        </Badge>
                        <Badge variant="outline">
                          {location.market_volatility.toFixed(1)}% volatility
                        </Badge>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Market Segments Tab */}
        <TabsContent value="segments" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Market Segment Analysis</CardTitle>
              <CardDescription>
                Compare different market segments for investment opportunities
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {marketSegments.map((segment) => (
                  <Card 
                    key={segment.segment} 
                    className={`cursor-pointer transition-all ${
                      selectedSegments.includes(segment.segment) 
                        ? 'ring-2 ring-blue-500 bg-blue-50' 
                        : 'hover:shadow-md'
                    }`}
                    onClick={() => toggleSegmentSelection(segment.segment)}
                  >
                    <CardHeader className="pb-3">
                      <div className="flex justify-between items-start">
                        <div>
                          <CardTitle className="text-lg">{segment.segment}</CardTitle>
                          <CardDescription className="mt-2">
                            Avg Price: {formatCurrency(segment.avg_price)}
                          </CardDescription>
                        </div>
                        <div className="flex space-x-2">
                          <Badge className={getOpportunityColor(segment.investment_opportunity)}>
                            {segment.investment_opportunity}
                          </Badge>
                          {selectedSegments.includes(segment.segment) && (
                            <CheckCircle className="h-5 w-5 text-blue-600" />
                          )}
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <div className="grid grid-cols-2 gap-3 text-sm">
                        <div>
                          <span className="text-muted-foreground">Price Growth:</span>
                          <div className="font-medium text-green-600">{formatPercentage(segment.price_growth)}</div>
                        </div>
                        <div>
                          <span className="text-muted-foreground">Demand Trend:</span>
                          <div className="font-medium capitalize">{segment.demand_trend}</div>
                        </div>
                        <div>
                          <span className="text-muted-foreground">Supply Level:</span>
                          <div className="font-medium capitalize">{segment.supply_level}</div>
                        </div>
                        <div>
                          <span className="text-muted-foreground">Rental Market:</span>
                          <div className="font-medium capitalize">{segment.rental_market}</div>
                        </div>
                      </div>
                      
                      <div className="pt-2 border-t">
                        <h4 className="font-medium mb-2 text-sm">Key Advantages</h4>
                        <ul className="space-y-1 text-xs">
                          {segment.key_advantages.map((advantage, index) => (
                            <li key={index} className="flex items-center space-x-2">
                              <CheckCircle className="h-3 w-3 text-green-600" />
                              <span>{advantage}</span>
                            </li>
                          ))}
                        </ul>
                      </div>

                      <div className="pt-2 border-t">
                        <h4 className="font-medium mb-2 text-sm">Key Risks</h4>
                        <ul className="space-y-1 text-xs">
                          {segment.key_risks.map((risk, index) => (
                            <li key={index} className="flex items-center space-x-2">
                              <AlertTriangle className="h-3 w-3 text-yellow-600" />
                              <span>{risk}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
