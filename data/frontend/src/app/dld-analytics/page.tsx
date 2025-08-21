"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { 
  BarChart3, 
  TrendingUp, 
  MapPin, 
  Building2, 
  DollarSign, 
  PieChart,
  Download,
  RefreshCw
} from "lucide-react";
import DLDAnalyticsCharts from "@/components/DLDAnalyticsCharts";

interface DLDAnalytics {
  summary: {
    total_transactions: number;
    total_value_aed: number;
    avg_price_aed: number;
    unique_locations: number;
    unique_developers: number;
    unique_property_types: number;
  };
  property_types: Array<{
    type: string;
    transaction_count: number;
    avg_price_aed: number;
    total_value_aed: number;
    avg_area_sqft: number;
  }>;
  locations: Array<{
    location: string;
    transaction_count: number;
    avg_price_aed: number;
    total_value_aed: number;
    avg_price_per_sqft: number;
  }>;
  developers: Array<{
    developer_name: string;
    transaction_count: number;
    avg_price_aed: number;
    total_value_aed: number;
    locations_count: number;
  }>;
  price_ranges: Array<{
    range: string;
    transaction_count: number;
    avg_price_aed: number;
  }>;
}

export default function DLDAnalyticsPage() {
  const [analytics, setAnalytics] = useState<DLDAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/v1/analytics/dld/full-report');
      if (!response.ok) {
        throw new Error('Failed to fetch analytics data');
      }
      const data = await response.json();
      setAnalytics(data.report);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    if (amount >= 1e9) {
      return `${(amount / 1e9).toFixed(1)}B AED`;
    } else if (amount >= 1e6) {
      return `${(amount / 1e6).toFixed(1)}M AED`;
    } else if (amount >= 1e3) {
      return `${(amount / 1e3).toFixed(1)}K AED`;
    }
    return `${amount.toFixed(0)} AED`;
  };

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat().format(num);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="flex items-center space-x-2">
          <RefreshCw className="animate-spin h-6 w-6" />
          <span>Loading DLD Analytics...</span>
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
            <Button onClick={fetchAnalytics} className="mt-4">
              <RefreshCw className="h-4 w-4 mr-2" />
              Retry
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Card className="w-96">
          <CardHeader>
            <CardTitle>No Data Available</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-600">DLD analytics data is not available.</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const { summary, property_types, locations, developers, price_ranges } = analytics;

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">DLD Analytics Dashboard</h1>
          <p className="text-gray-600 mt-2">
            Comprehensive analysis of Dubai Land Department transactions
          </p>
        </div>
        <Button onClick={fetchAnalytics} variant="outline">
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh Data
        </Button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Transactions</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatNumber(summary.total_transactions)}</div>
            <p className="text-xs text-muted-foreground">
              All DLD transactions
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Value</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(summary.total_value_aed)}</div>
            <p className="text-xs text-muted-foreground">
              Combined transaction value
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Average Price</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(summary.avg_price_aed)}</div>
            <p className="text-xs text-muted-foreground">
              Per transaction
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Unique Locations</CardTitle>
            <MapPin className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatNumber(summary.unique_locations)}</div>
            <p className="text-xs text-muted-foreground">
              Across Dubai
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Analytics */}
      <Tabs defaultValue="property-types" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="property-types">Property Types</TabsTrigger>
          <TabsTrigger value="locations">Locations</TabsTrigger>
          <TabsTrigger value="developers">Developers</TabsTrigger>
          <TabsTrigger value="prices">Price Analysis</TabsTrigger>
        </TabsList>

        <TabsContent value="property-types" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Property Type Distribution</CardTitle>
              <CardDescription>
                Analysis of transactions by property type
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {property_types.map((type, index) => {
                  const percentage = (type.transaction_count / summary.total_transactions) * 100;
                  return (
                    <div key={type.type} className="space-y-2">
                      <div className="flex justify-between items-center">
                        <div className="flex items-center space-x-2">
                          <Badge variant="outline">{type.type}</Badge>
                          <span className="font-medium">{formatNumber(type.transaction_count)}</span>
                        </div>
                        <span className="text-sm text-muted-foreground">
                          {percentage.toFixed(1)}%
                        </span>
                      </div>
                      <Progress value={percentage} className="h-2" />
                      <div className="grid grid-cols-3 gap-4 text-sm">
                        <div>
                          <span className="text-muted-foreground">Avg Price:</span>
                          <div className="font-medium">{formatCurrency(type.avg_price_aed)}</div>
                        </div>
                        <div>
                          <span className="text-muted-foreground">Total Value:</span>
                          <div className="font-medium">{formatCurrency(type.total_value_aed)}</div>
                        </div>
                        <div>
                          <span className="text-muted-foreground">Avg Area:</span>
                          <div className="font-medium">{type.avg_area_sqft.toFixed(0)} sqft</div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="locations" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Top Locations by Transaction Volume</CardTitle>
              <CardDescription>
                Most active locations in Dubai real estate market
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {locations.slice(0, 10).map((location, index) => (
                  <div key={location.location} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-4">
                      <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                        <span className="text-sm font-bold text-blue-600">{index + 1}</span>
                      </div>
                      <div>
                        <div className="font-medium">{location.location}</div>
                        <div className="text-sm text-muted-foreground">
                          {formatNumber(location.transaction_count)} transactions
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-medium">{formatCurrency(location.avg_price_aed)}</div>
                      <div className="text-sm text-muted-foreground">
                        {formatCurrency(location.total_value_aed)}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="developers" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Top Developers by Volume</CardTitle>
              <CardDescription>
                Leading developers in Dubai real estate market
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {developers.slice(0, 10).map((developer, index) => (
                  <div key={developer.developer_name} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-4">
                      <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                        <span className="text-sm font-bold text-green-600">{index + 1}</span>
                      </div>
                      <div>
                        <div className="font-medium">{developer.developer_name}</div>
                        <div className="text-sm text-muted-foreground">
                          {formatNumber(developer.transaction_count)} transactions
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-medium">{formatCurrency(developer.total_value_aed)}</div>
                      <div className="text-sm text-muted-foreground">
                        Avg: {formatCurrency(developer.avg_price_aed)}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="prices" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Price Range Distribution</CardTitle>
              <CardDescription>
                Distribution of transactions across price ranges
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {price_ranges.map((range, index) => {
                  const percentage = (range.transaction_count / summary.total_transactions) * 100;
                  return (
                    <div key={range.range} className="space-y-2">
                      <div className="flex justify-between items-center">
                        <div className="flex items-center space-x-2">
                          <Badge variant="secondary">{range.range}</Badge>
                          <span className="font-medium">{formatNumber(range.transaction_count)}</span>
                        </div>
                        <span className="text-sm text-muted-foreground">
                          {percentage.toFixed(1)}%
                        </span>
                      </div>
                      <Progress value={percentage} className="h-2" />
                      <div className="text-sm text-muted-foreground">
                        Avg Price: {formatCurrency(range.avg_price_aed)}
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Charts Section */}
      <Card>
        <CardHeader>
          <CardTitle>Analytics Charts</CardTitle>
          <CardDescription>
            Interactive visualizations of DLD analytics data
          </CardDescription>
        </CardHeader>
        <CardContent>
          <DLDAnalyticsCharts data={analytics} />
        </CardContent>
      </Card>
    </div>
  );
} 