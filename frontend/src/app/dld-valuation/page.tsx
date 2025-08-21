"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import {
  Calculator, TrendingUp, TrendingDown, DollarSign, MapPin, Building2, Calendar, 
  BarChart3, PieChart, RefreshCw, Eye, Download, Filter, Search, Target, 
  AlertTriangle, CheckCircle, Clock, Home, Ruler, Percent, AlertCircle, Upload
} from "lucide-react";

interface ValuationRequest {
  id: string;
  property_type: string;
  location: string;
  area_sqft: number;
  bedrooms?: number;
  bathrooms?: number;
  age_years: number;
  floor_level?: number;
  view_type?: string;
  amenities: string[];
  parking_spaces?: number;
  balcony_area?: number;
  garden_area?: number;
  pool?: boolean;
  gym?: boolean;
  security?: boolean;
  created_at: string;
  status: 'pending' | 'completed' | 'failed';
}

interface ValuationResult {
  id: string;
  request_id: string;
  estimated_value_aed: number;
  confidence_score: number;
  valuation_method: string;
  comparable_sales: ComparableSale[];
  market_factors: MarketFactor[];
  risk_factors: RiskFactor[];
  recommendations: string[];
  created_at: string;
  valid_until: string;
}

interface ComparableSale {
  id: string;
  property_name: string;
  location: string;
  property_type: string;
  area_sqft: number;
  bedrooms?: number;
  bathrooms?: number;
  sale_price_aed: number;
  sale_date: string;
  price_per_sqft: number;
  similarity_score: number;
  distance_km: number;
}

interface MarketFactor {
  factor: string;
  impact: 'positive' | 'negative' | 'neutral';
  description: string;
  weight: number;
}

interface RiskFactor {
  factor: string;
  risk_level: 'low' | 'medium' | 'high';
  description: string;
  mitigation: string;
}

interface ValuationHistory {
  id: string;
  property_address: string;
  property_type: string;
  valuation_date: string;
  estimated_value_aed: number;
  actual_sale_price_aed?: number;
  accuracy_percent?: number;
  status: 'active' | 'sold' | 'expired';
}

export default function DLDValuationPage() {
  const [activeTab, setActiveTab] = useState("calculator");
  const [valuationRequest, setValuationRequest] = useState<Partial<ValuationRequest>>({
    property_type: '',
    location: '',
    area_sqft: 0,
    bedrooms: 0,
    bathrooms: 0,
    age_years: 0,
    amenities: []
  });
  const [valuationResult, setValuationResult] = useState<ValuationResult | null>(null);
  const [isCalculating, setIsCalculating] = useState(false);
  const [valuationHistory, setValuationHistory] = useState<ValuationHistory[]>([]);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [calculationProgress, setCalculationProgress] = useState(0);

  // Mock data
  useEffect(() => {
    // Mock valuation history
    setValuationHistory([
      {
        id: "vh1",
        property_address: "Marina Heights Tower, Dubai Marina",
        property_type: "Apartment",
        valuation_date: "2024-01-15",
        estimated_value_aed: 2500000,
        actual_sale_price_aed: 2450000,
        accuracy_percent: 98.0,
        status: "sold"
      },
      {
        id: "vh2",
        property_address: "Palm Jumeirah Villa, Palm Jumeirah",
        property_type: "Villa",
        valuation_date: "2024-01-10",
        estimated_value_aed: 8500000,
        status: "active"
      },
      {
        id: "vh3",
        property_address: "Downtown Views, Downtown Dubai",
        property_type: "Apartment",
        valuation_date: "2024-01-05",
        estimated_value_aed: 3200000,
        actual_sale_price_aed: 3150000,
        accuracy_percent: 98.4,
        status: "sold"
      }
    ]);
  }, []);

  const handleInputChange = (field: keyof ValuationRequest, value: any) => {
    setValuationRequest((prev: Partial<ValuationRequest>) => ({
      ...prev,
      [field]: value
    }));
  };

  const handleAmenityToggle = (amenity: string) => {
    setValuationRequest((prev: Partial<ValuationRequest>) => ({
      ...prev,
      amenities: prev.amenities?.includes(amenity)
        ? prev.amenities?.filter((a: string) => a !== amenity) || []
        : [...(prev.amenities || []), amenity]
    }));
  };

  const validateForm = () => {
    const newErrors: Record<string, string> = {};
    
    if (!valuationRequest.property_type) {
      newErrors.property_type = 'Property type is required';
    }
    
    if (!valuationRequest.location) {
      newErrors.location = 'Location is required';
    }
    
    if (!valuationRequest.area_sqft || valuationRequest.area_sqft <= 0) {
      newErrors.area_sqft = 'Valid area is required';
    }
    
    if (valuationRequest.bedrooms && valuationRequest.bedrooms < 0) {
      newErrors.bedrooms = 'Bedrooms cannot be negative';
    }
    
    if (valuationRequest.bathrooms && valuationRequest.bathrooms < 0) {
      newErrors.bathrooms = 'Bathrooms cannot be negative';
    }
    
    if (valuationRequest.age_years && valuationRequest.age_years < 0) {
      newErrors.age_years = 'Age cannot be negative';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const calculateValuation = async () => {
    if (!validateForm()) {
      return;
    }
    
    setIsCalculating(true);
    setCalculationProgress(0);
    
    // Simulate progress updates
    const progressInterval = setInterval(() => {
      setCalculationProgress((prev: number) => {
        if (prev >= 90) {
          clearInterval(progressInterval);
          return 90;
        }
        return prev + 10;
      });
    }, 200);
    
    // Simulate API call
    setTimeout(() => {
      const mockResult: ValuationResult = {
        id: "val1",
        request_id: "req1",
        estimated_value_aed: 2800000,
        confidence_score: 87,
        valuation_method: "Comparable Sales + Market Analysis",
        comparable_sales: [
          {
            id: "cs1",
            property_name: "Marina Heights Tower",
            location: "Dubai Marina",
            property_type: "Apartment",
            area_sqft: 1200,
            bedrooms: 2,
            bathrooms: 2,
            sale_price_aed: 2750000,
            sale_date: "2024-01-10",
            price_per_sqft: 2292,
            similarity_score: 92,
            distance_km: 0.5
          },
          {
            id: "cs2",
            property_name: "Marina Gate 1",
            location: "Dubai Marina",
            property_type: "Apartment",
            area_sqft: 1250,
            bedrooms: 2,
            bathrooms: 2,
            sale_price_aed: 2850000,
            sale_date: "2024-01-05",
            price_per_sqft: 2280,
            similarity_score: 88,
            distance_km: 0.8
          }
        ],
        market_factors: [
          {
            factor: "Market Appreciation",
            impact: "positive",
            description: "Dubai Marina showing 8% annual growth",
            weight: 0.25
          },
          {
            factor: "Supply & Demand",
            impact: "positive",
            description: "High demand for 2-bedroom apartments",
            weight: 0.20
          },
          {
            factor: "Interest Rates",
            impact: "negative",
            description: "Rising mortgage rates affecting affordability",
            weight: 0.15
          }
        ],
        risk_factors: [
          {
            factor: "Market Volatility",
            risk_level: "medium",
            description: "Potential market correction in next 12 months",
            mitigation: "Consider long-term investment horizon"
          },
          {
            factor: "Liquidity Risk",
            risk_level: "low",
            description: "High demand area ensures good liquidity",
            mitigation: "Market timing is favorable"
          }
        ],
        recommendations: [
          "Property shows strong investment potential with 8% annual appreciation",
          "Consider holding period of 3-5 years for optimal returns",
          "Monitor market conditions for optimal exit timing",
          "Property is well-positioned in high-demand area"
        ],
        created_at: new Date().toISOString(),
        valid_until: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString()
      };
      
      setCalculationProgress(100);
      setTimeout(() => {
        setValuationResult(mockResult);
        setIsCalculating(false);
        setCalculationProgress(0);
        setActiveTab("results");
      }, 500);
    }, 2000);
  };

  const exportReport = () => {
    if (!valuationResult) return;
    
    // Create a comprehensive report
    const report = {
      title: "DLD Property Valuation Report",
      generatedAt: new Date().toISOString(),
      propertyDetails: valuationRequest,
      valuation: valuationResult,
      marketInsights: {
        trends: valuationResult.market_factors.map((f: MarketFactor) => f.description),
        risks: valuationResult.risk_factors.map((r: RiskFactor) => r.description),
        recommendations: valuationResult.recommendations
      }
    };
    
    // Convert to JSON and download
    const dataStr = JSON.stringify(report, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `valuation-report-${Date.now()}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  const getConfidenceColor = (score: number) => {
    if (score >= 80) return "bg-green-100 text-green-800";
    if (score >= 60) return "bg-yellow-100 text-yellow-800";
    return "bg-red-100 text-red-800";
  };

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'positive': return "bg-green-100 text-green-800";
      case 'negative': return "bg-red-100 text-red-800";
      default: return "bg-gray-100 text-gray-800";
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'low': return "bg-green-100 text-green-800";
      case 'medium': return "bg-yellow-100 text-yellow-800";
      case 'high': return "bg-red-100 text-red-800";
      default: return "bg-gray-100 text-gray-800";
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">DLD Property Valuation Tool</h1>
          <p className="text-gray-600 mt-2">
            Get accurate property valuations using DLD data, market trends, and AI-powered analysis
          </p>
        </div>
        <Button 
          variant="outline" 
          size="sm" 
          onClick={exportReport}
          disabled={!valuationResult}
        >
          <Download className="w-4 h-4 mr-2" />
          Export Report
        </Button>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="calculator">Valuation Calculator</TabsTrigger>
          <TabsTrigger value="results">Valuation Results</TabsTrigger>
          <TabsTrigger value="history">Valuation History</TabsTrigger>
          <TabsTrigger value="insights">Market Insights</TabsTrigger>
        </TabsList>

        <TabsContent value="calculator" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calculator className="w-5 h-5" />
                Property Valuation Calculator
              </CardTitle>
              <CardDescription>
                Enter property details to get an accurate valuation based on DLD data and market analysis
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="property_type">Property Type *</Label>
                    <Select value={valuationRequest.property_type} onValueChange={(value) => handleInputChange('property_type', value)}>
                      <SelectTrigger className={errors.property_type ? "border-red-500" : ""}>
                        <SelectValue placeholder="Select property type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="apartment">Apartment</SelectItem>
                        <SelectItem value="villa">Villa</SelectItem>
                        <SelectItem value="townhouse">Townhouse</SelectItem>
                        <SelectItem value="penthouse">Penthouse</SelectItem>
                        <SelectItem value="office">Office</SelectItem>
                        <SelectItem value="retail">Retail</SelectItem>
                      </SelectContent>
                    </Select>
                    {errors.property_type && (
                      <div className="flex items-center gap-2 mt-1 text-red-600 text-sm">
                        <AlertCircle className="w-4 h-4" />
                        {errors.property_type}
                      </div>
                    )}
                  </div>

                  <div>
                    <Label htmlFor="location">Location *</Label>
                    <Select value={valuationRequest.location} onValueChange={(value) => handleInputChange('location', value)}>
                      <SelectTrigger className={errors.location ? "border-red-500" : ""}>
                        <SelectValue placeholder="Select location" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="dubai_marina">Dubai Marina</SelectItem>
                        <SelectItem value="palm_jumeirah">Palm Jumeirah</SelectItem>
                        <SelectItem value="downtown_dubai">Downtown Dubai</SelectItem>
                        <SelectItem value="business_bay">Business Bay</SelectItem>
                        <SelectItem value="jbr">JBR</SelectItem>
                        <SelectItem value="emirates_hills">Emirates Hills</SelectItem>
                      </SelectContent>
                    </Select>
                    {errors.location && (
                      <div className="flex items-center gap-2 mt-1 text-red-600 text-sm">
                        <AlertCircle className="w-4 h-4" />
                        {errors.location}
                      </div>
                    )}
                  </div>

                  <div>
                    <Label htmlFor="area_sqft">Area (sq ft) *</Label>
                    <Input
                      id="area_sqft"
                      type="number"
                      placeholder="Enter area in square feet"
                      value={valuationRequest.area_sqft || ''}
                      onChange={(e) => handleInputChange('area_sqft', parseInt(e.target.value))}
                      className={errors.area_sqft ? "border-red-500" : ""}
                    />
                    {errors.area_sqft && (
                      <div className="flex items-center gap-2 mt-1 text-red-600 text-sm">
                        <AlertCircle className="w-4 h-4" />
                        {errors.area_sqft}
                      </div>
                    )}
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="bedrooms">Bedrooms</Label>
                      <Input
                        id="bedrooms"
                        type="number"
                        placeholder="0"
                        value={valuationRequest.bedrooms || ''}
                        onChange={(e) => handleInputChange('bedrooms', parseInt(e.target.value))}
                        className={errors.bedrooms ? "border-red-500" : ""}
                      />
                      {errors.bedrooms && (
                        <div className="flex items-center gap-2 mt-1 text-red-600 text-sm">
                          <AlertCircle className="w-4 h-4" />
                          {errors.bedrooms}
                        </div>
                      )}
                    </div>
                    <div>
                      <Label htmlFor="bathrooms">Bathrooms</Label>
                      <Input
                        id="bathrooms"
                        type="number"
                        placeholder="0"
                        value={valuationRequest.bathrooms || ''}
                        onChange={(e) => handleInputChange('bathrooms', parseInt(e.target.value))}
                        className={errors.bathrooms ? "border-red-500" : ""}
                      />
                      {errors.bathrooms && (
                        <div className="flex items-center gap-2 mt-1 text-red-600 text-sm">
                          <AlertCircle className="w-4 h-4" />
                          {errors.bathrooms}
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <div>
                    <Label htmlFor="age_years">Age (Years)</Label>
                    <Input
                      id="age_years"
                      type="number"
                      placeholder="Property age in years"
                      value={valuationRequest.age_years || ''}
                      onChange={(e) => handleInputChange('age_years', parseInt(e.target.value))}
                      className={errors.age_years ? "border-red-500" : ""}
                    />
                    {errors.age_years && (
                      <div className="flex items-center gap-2 mt-1 text-red-600 text-sm">
                        <AlertCircle className="w-4 h-4" />
                        {errors.age_years}
                      </div>
                    )}
                  </div>

                  <div>
                    <Label htmlFor="floor_level">Floor Level</Label>
                    <Input
                      id="floor_level"
                      type="number"
                      placeholder="Floor number"
                      value={valuationRequest.floor_level || ''}
                      onChange={(e) => handleInputChange('floor_level', parseInt(e.target.value))}
                    />
                  </div>

                  <div>
                    <Label>Amenities</Label>
                    <div className="grid grid-cols-2 gap-2 mt-2">
                      {['Pool', 'Gym', 'Security', 'Parking', 'Balcony', 'Garden'].map((amenity) => (
                        <Button
                          key={amenity}
                          variant={valuationRequest.amenities?.includes(amenity.toLowerCase()) ? "default" : "outline"}
                          size="sm"
                          onClick={() => handleAmenityToggle(amenity.toLowerCase())}
                          className="justify-start"
                        >
                          {amenity}
                        </Button>
                      ))}
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="notes">Additional Notes</Label>
                    <Textarea
                      id="notes"
                      placeholder="Any additional property details..."
                      rows={3}
                    />
                  </div>

                  {/* New: Property Images Section */}
                  <div>
                    <Label>Property Images</Label>
                    <div className="mt-2 p-4 border-2 border-dashed border-gray-300 rounded-lg text-center">
                      <div className="space-y-2">
                        <div className="text-gray-600">
                          <Upload className="w-8 h-8 mx-auto mb-2" />
                          <p className="text-sm">Upload property images for better valuation accuracy</p>
                          <p className="text-xs text-gray-500">Supports JPG, PNG up to 5MB each</p>
                        </div>
                        <Button variant="outline" size="sm">
                          <Upload className="w-4 h-4 mr-2" />
                          Choose Images
                        </Button>
                      </div>
                    </div>
                    <div className="mt-2 text-xs text-gray-500">
                      Adding images can improve valuation accuracy by up to 15%
                    </div>
                  </div>
                </div>
              </div>

              {isCalculating && (
                <div className="space-y-4">
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${calculationProgress}%` }}
                    ></div>
                  </div>
                  <p className="text-sm text-gray-600 text-center">
                    Analyzing property data and market conditions... {calculationProgress}%
                  </p>
                </div>
              )}

              <div className="flex justify-end">
                <Button 
                  onClick={calculateValuation} 
                  disabled={isCalculating || !valuationRequest.property_type || !valuationRequest.location || !valuationRequest.area_sqft}
                  className="min-w-[200px]"
                >
                  {isCalculating ? (
                    <>
                      <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                      Calculating...
                    </>
                  ) : (
                    <>
                      <Calculator className="w-4 h-4 mr-2" />
                      Calculate Valuation
                    </>
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="results" className="space-y-6">
          {valuationResult ? (
            <div className="space-y-6">
              {/* Valuation Summary */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Target className="w-5 h-5" />
                    Valuation Summary
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="text-center">
                      <div className="text-3xl font-bold text-green-600">
                        AED {valuationResult.estimated_value_aed.toLocaleString()}
                      </div>
                      <div className="text-sm text-gray-600">Estimated Value</div>
                    </div>
                    <div className="text-center">
                      <div className="text-3xl font-bold text-blue-600">
                        {valuationResult.confidence_score}%
                      </div>
                      <div className="text-sm text-gray-600">Confidence Score</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-semibold text-gray-700">
                        {valuationResult.valuation_method}
                      </div>
                      <div className="text-sm text-gray-600">Valuation Method</div>
                    </div>
                  </div>
                  
                  <div className="mt-6">
                    <Badge className={getConfidenceColor(valuationResult.confidence_score)}>
                      {valuationResult.confidence_score >= 80 ? 'High Confidence' : 
                       valuationResult.confidence_score >= 60 ? 'Medium Confidence' : 'Low Confidence'}
                    </Badge>
                    <span className="text-sm text-gray-600 ml-2">
                      Valid until {new Date(valuationResult.valid_until).toLocaleDateString()}
                    </span>
                  </div>
                </CardContent>
              </Card>

              {/* Comparable Sales */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <BarChart3 className="w-5 h-5" />
                    Comparable Sales
                  </CardTitle>
                  <CardDescription>
                    Recent sales of similar properties used in valuation
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {valuationResult.comparable_sales.map((sale) => (
                      <div key={sale.id} className="border rounded-lg p-4">
                        <div className="flex justify-between items-start">
                          <div>
                            <h4 className="font-semibold">{sale.property_name}</h4>
                            <p className="text-sm text-gray-600">{sale.location}</p>
                            <div className="flex gap-4 mt-2 text-sm">
                              <span>{sale.area_sqft} sq ft</span>
                              {sale.bedrooms && <span>{sale.bedrooms} beds</span>}
                              {sale.bathrooms && <span>{sale.bathrooms} baths</span>}
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="text-lg font-semibold">
                              AED {sale.sale_price_aed.toLocaleString()}
                            </div>
                            <div className="text-sm text-gray-600">
                              {sale.price_per_sqft} AED/sq ft
                            </div>
                            <Badge className="mt-1">
                              {sale.similarity_score}% similar
                            </Badge>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Market Factors */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <TrendingUp className="w-5 h-5" />
                      Market Factors
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {valuationResult.market_factors.map((factor) => (
                        <div key={factor.factor} className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <Badge className={getImpactColor(factor.impact)}>
                              {factor.impact}
                            </Badge>
                            <span className="text-sm font-medium">{factor.factor}</span>
                          </div>
                          <span className="text-xs text-gray-500">{(factor.weight * 100).toFixed(0)}%</span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <AlertTriangle className="w-5 h-5" />
                      Risk Factors
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {valuationResult.risk_factors.map((risk) => (
                        <div key={risk.factor} className="space-y-2">
                          <div className="flex items-center gap-2">
                            <Badge className={getRiskColor(risk.risk_level)}>
                              {risk.risk_level}
                            </Badge>
                            <span className="text-sm font-medium">{risk.factor}</span>
                          </div>
                          <p className="text-xs text-gray-600">{risk.description}</p>
                          <p className="text-xs text-blue-600">{risk.mitigation}</p>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Recommendations */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <CheckCircle className="w-5 h-5" />
                    Investment Recommendations
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {valuationResult.recommendations.map((rec, index) => (
                      <div key={index} className="flex items-start gap-3">
                        <CheckCircle className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" />
                        <p className="text-sm">{rec}</p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          ) : (
            <Card>
              <CardContent className="text-center py-12">
                <Calculator className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No Valuation Results</h3>
                <p className="text-gray-600 mb-4">
                  Use the calculator to get a property valuation based on DLD data and market analysis.
                </p>
                <Button onClick={() => setActiveTab("calculator")}>
                  Go to Calculator
                </Button>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="history" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="w-5 h-5" />
                Valuation History
              </CardTitle>
              <CardDescription>
                Track your previous valuations and their accuracy
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {valuationHistory.map((history) => (
                  <div key={history.id} className="border rounded-lg p-4">
                    <div className="flex justify-between items-start">
                      <div>
                        <h4 className="font-semibold">{history.property_address}</h4>
                        <p className="text-sm text-gray-600">{history.property_type}</p>
                        <p className="text-xs text-gray-500">
                          Valued on {new Date(history.valuation_date).toLocaleDateString()}
                        </p>
                      </div>
                      <div className="text-right">
                        <div className="text-lg font-semibold">
                          AED {history.estimated_value_aed.toLocaleString()}
                        </div>
                        {history.actual_sale_price_aed && (
                          <div className="text-sm text-gray-600">
                            Actual: AED {history.actual_sale_price_aed.toLocaleString()}
                          </div>
                        )}
                        <div className="flex items-center gap-2 mt-2">
                          <Badge variant={history.status === 'sold' ? 'default' : 'secondary'}>
                            {history.status}
                          </Badge>
                          {history.accuracy_percent && (
                            <Badge variant="outline" className="text-xs">
                              {history.accuracy_percent}% accurate
                            </Badge>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="insights" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="w-5 h-5" />
                  Market Trends
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Dubai Marina</span>
                    <Badge className="bg-green-100 text-green-800">+8.2%</Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Palm Jumeirah</span>
                    <Badge className="bg-green-100 text-green-800">+6.8%</Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Downtown Dubai</span>
                    <Badge className="bg-green-100 text-green-800">+7.5%</Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Business Bay</span>
                    <Badge className="bg-yellow-100 text-yellow-800">+3.2%</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="w-5 h-5" />
                  Price Ranges
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Under 2M AED</span>
                    <Badge variant="outline">High Demand</Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm">2M - 5M AED</span>
                    <Badge variant="outline">Stable</Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm">5M - 10M AED</span>
                    <Badge variant="outline">Growing</Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm">10M+ AED</span>
                    <Badge variant="outline">Luxury</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="w-5 h-5" />
                Investment Opportunities
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="border rounded-lg p-4">
                  <div className="flex justify-between items-start">
                    <div>
                      <h4 className="font-semibold">Emerging Areas</h4>
                      <p className="text-sm text-gray-600">Areas showing early signs of growth</p>
                    </div>
                    <Badge className="bg-blue-100 text-blue-800">Watch</Badge>
                  </div>
                  <div className="mt-3 space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Dubai Hills Estate</span>
                      <span className="text-green-600">+12%</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Meydan</span>
                      <span className="text-green-600">+9%</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Dubai South</span>
                      <span className="text-green-600">+15%</span>
                    </div>
                  </div>
                </div>

                <div className="border rounded-lg p-4">
                  <div className="flex justify-between items-start">
                    <div>
                      <h4 className="font-semibold">Market Indicators</h4>
                      <p className="text-sm text-gray-600">Key factors affecting valuations</p>
                    </div>
                    <Badge className="bg-green-100 text-green-800">Positive</Badge>
                  </div>
                  <div className="mt-3 space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Supply vs Demand</span>
                      <span className="text-green-600">Favorable</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Interest Rates</span>
                      <span className="text-yellow-600">Stable</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Economic Growth</span>
                      <span className="text-green-600">Strong</span>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* New: Property Comparison Section */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="w-5 h-5" />
                Similar Properties Analysis
              </CardTitle>
              <CardDescription>
                Compare your property with similar ones in the market
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center p-4 border rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">2,800</div>
                    <div className="text-sm text-gray-600">AED/sq ft</div>
                    <div className="text-xs text-gray-500 mt-1">Your Property</div>
                  </div>
                  <div className="text-center p-4 border rounded-lg">
                    <div className="text-2xl font-bold text-green-600">2,650</div>
                    <div className="text-sm text-gray-600">AED/sq ft</div>
                    <div className="text-xs text-gray-500 mt-1">Market Average</div>
                  </div>
                  <div className="text-center p-4 border rounded-lg">
                    <div className="text-2xl font-bold text-purple-600">+5.7%</div>
                    <div className="text-sm text-gray-600">Premium</div>
                    <div className="text-xs text-gray-500 mt-1">vs Market</div>
                  </div>
                </div>
                
                <div className="mt-6">
                  <h4 className="font-semibold mb-3">Key Differentiators</h4>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-sm">
                      <CheckCircle className="w-4 h-4 text-green-600" />
                      <span>Premium location in Dubai Marina</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <CheckCircle className="w-4 h-4 text-green-600" />
                      <span>Modern building with high-end amenities</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <CheckCircle className="w-4 h-4 text-green-600" />
                      <span>Excellent sea view and balcony</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <CheckCircle className="w-4 h-4 text-green-600" />
                      <span>High rental yield potential</span>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* New: Market Forecast Section */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5" />
                Market Forecast (Next 12 Months)
              </CardTitle>
              <CardDescription>
                AI-powered market predictions based on current trends
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 border rounded-lg">
                    <h5 className="font-semibold text-sm mb-2">Dubai Marina</h5>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Q1 2024</span>
                        <span className="text-green-600">+2.1%</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span>Q2 2024</span>
                        <span className="text-green-600">+1.8%</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span>Q3 2024</span>
                        <span className="text-green-600">+2.3%</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span>Q4 2024</span>
                        <span className="text-green-600">+2.0%</span>
                      </div>
                    </div>
                    <div className="mt-3 pt-2 border-t">
                      <div className="text-sm font-medium">Annual Growth: +8.2%</div>
                    </div>
                  </div>
                  
                  <div className="p-4 border rounded-lg">
                    <h5 className="font-semibold text-sm mb-2">Overall Dubai</h5>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Q1 2024</span>
                        <span className="text-green-600">+1.5%</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span>Q2 2024</span>
                        <span className="text-green-600">+1.2%</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span>Q3 2024</span>
                        <span className="text-green-600">+1.8%</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span>Q4 2024</span>
                        <span className="text-green-600">+1.6%</span>
                      </div>
                    </div>
                    <div className="mt-3 pt-2 border-t">
                      <div className="text-sm font-medium">Annual Growth: +6.1%</div>
                    </div>
                  </div>
                </div>
                
                <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                  <h5 className="font-semibold text-sm mb-2 text-blue-800">Investment Recommendation</h5>
                  <p className="text-sm text-blue-700">
                    Based on current market analysis, Dubai Marina properties are expected to outperform 
                    the overall Dubai market by approximately 2.1% annually. This makes it an attractive 
                    investment opportunity with strong growth potential.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
