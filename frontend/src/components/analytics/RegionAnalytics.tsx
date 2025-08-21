'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  TrendingUp, 
  TrendingDown, 
  Minus, 
  MapPin, 
  Building2, 
  DollarSign,
  BarChart3,
  Search,
  Filter
} from 'lucide-react';

interface RegionAnalytics {
  region_info: {
    id: number;
    internet_name: string;
    region_category: string;
    municipality: string;
    popularity_score: number;
    avg_price_aed: string;
    min_price_aed: string;
    max_price_aed: string;
    transaction_volume: number;
  };
  analytics: {
    period_days: number;
    total_transactions: number;
    total_volume_aed: number;
    avg_price_aed: number;
    median_price_aed: number;
    min_price_aed: number;
    max_price_aed: number;
    avg_price_per_sqft: number;
    property_types_count: number;
    developers_count: number;
    price_trend: string;
    property_types: Array<{
      type: string;
      count: number;
      avg_price: number;
    }>;
    top_developers: Array<{
      name: string;
      count: number;
      avg_price: number;
    }>;
  };
}

interface PopularArea {
  id: number;
  internet_name: string;
  region_category: string;
  popularity_score: number;
  avg_price_aed: string;
  transaction_volume: number;
  total_transactions: number;
}

const RegionAnalytics: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedRegion, setSelectedRegion] = useState<string>('');
  const [regionAnalytics, setRegionAnalytics] = useState<RegionAnalytics | null>(null);
  const [popularAreas, setPopularAreas] = useState<PopularArea[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchPopularAreas();
  }, []);

  const fetchPopularAreas = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/areas/popular?limit=20');
      const data = await response.json();
      if (data.success) {
        setPopularAreas(data.data);
      }
    } catch (err) {
      console.error('Error fetching popular areas:', err);
    }
  };

  const searchRegions = async () => {
    if (!searchQuery.trim()) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`http://localhost:8000/api/v1/areas/search?q=${encodeURIComponent(searchQuery)}&limit=10`);
      const data = await response.json();
      
      if (data.success && data.data.length > 0) {
        // Auto-select first result
        setSelectedRegion(data.data[0].internet_name);
        await fetchRegionAnalytics(data.data[0].internet_name);
      } else {
        setError('No regions found for your search');
      }
    } catch (err) {
      setError('Failed to search regions');
      console.error('Error searching regions:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchRegionAnalytics = async (regionName: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`http://localhost:8000/api/v1/areas/analytics/${encodeURIComponent(regionName)}`);
      const data = await response.json();
      
      if (data.success) {
        setRegionAnalytics(data.data);
      } else {
        setError(data.error || 'Failed to fetch region analytics');
      }
    } catch (err) {
      setError('Failed to fetch region analytics');
      console.error('Error fetching region analytics:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRegionSelect = (regionName: string) => {
    setSelectedRegion(regionName);
    fetchRegionAnalytics(regionName);
  };

  const formatPrice = (price: number | string) => {
    const numPrice = typeof price === 'string' ? parseFloat(price) : price;
    if (numPrice >= 1000000) {
      return `AED ${(numPrice / 1000000).toFixed(1)}M`;
    } else if (numPrice >= 1000) {
      return `AED ${(numPrice / 1000).toFixed(1)}K`;
    }
    return `AED ${numPrice.toFixed(0)}`;
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'rising':
        return <TrendingUp className="h-4 w-4 text-green-500" />;
      case 'declining':
        return <TrendingDown className="h-4 w-4 text-red-500" />;
      default:
        return <Minus className="h-4 w-4 text-gray-500" />;
    }
  };

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      'Downtown': 'bg-blue-100 text-blue-800',
      'Marina': 'bg-cyan-100 text-cyan-800',
      'Island': 'bg-purple-100 text-purple-800',
      'Suburban': 'bg-green-100 text-green-800',
      'Business': 'bg-orange-100 text-orange-800',
      'Luxury': 'bg-pink-100 text-pink-800',
      'Beach': 'bg-teal-100 text-teal-800',
      'Sports': 'bg-indigo-100 text-indigo-800'
    };
    return colors[category] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Region Analytics Dashboard</h1>
        <p className="text-gray-600">Comprehensive analysis of Dubai real estate regions</p>
      </div>

      {/* Search Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="h-5 w-5" />
            Search Regions
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2">
            <Input
              placeholder="Search for a region (e.g., Dubai Marina, Burj Khalifa)"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && searchRegions()}
            />
            <Button onClick={searchRegions} disabled={loading}>
              {loading ? 'Searching...' : 'Search'}
            </Button>
          </div>
          {error && (
            <p className="text-red-500 text-sm mt-2">{error}</p>
          )}
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Popular Areas */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5" />
                Popular Regions
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {popularAreas.map((area) => (
                  <div
                    key={area.id}
                    className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                      selectedRegion === area.internet_name
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => handleRegionSelect(area.internet_name)}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-semibold text-sm">{area.internet_name}</h4>
                      <Badge className={getCategoryColor(area.region_category)}>
                        {area.region_category}
                      </Badge>
                    </div>
                    <div className="flex items-center justify-between text-sm text-gray-600">
                      <span>Score: {area.popularity_score}</span>
                      <span>{formatPrice(area.avg_price_aed)}</span>
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      {area.total_transactions.toLocaleString()} transactions
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Region Analytics */}
        <div className="lg:col-span-2">
          {regionAnalytics ? (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MapPin className="h-5 w-5" />
                  {regionAnalytics.region_info.internet_name} Analytics
                </CardTitle>
                <div className="flex items-center gap-2">
                  <Badge className={getCategoryColor(regionAnalytics.region_info.region_category)}>
                    {regionAnalytics.region_info.region_category}
                  </Badge>
                  <Badge variant="outline">
                    Popularity: {regionAnalytics.region_info.popularity_score}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <Tabs defaultValue="overview" className="w-full">
                  <TabsList className="grid w-full grid-cols-4">
                    <TabsTrigger value="overview">Overview</TabsTrigger>
                    <TabsTrigger value="pricing">Pricing</TabsTrigger>
                    <TabsTrigger value="transactions">Transactions</TabsTrigger>
                    <TabsTrigger value="developers">Developers</TabsTrigger>
                  </TabsList>

                  <TabsContent value="overview" className="space-y-4">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="text-center p-4 bg-blue-50 rounded-lg">
                        <div className="text-2xl font-bold text-blue-600">
                          {formatPrice(regionAnalytics.analytics.total_volume_aed)}
                        </div>
                        <div className="text-sm text-gray-600">Total Volume</div>
                      </div>
                      <div className="text-center p-4 bg-green-50 rounded-lg">
                        <div className="text-2xl font-bold text-green-600">
                          {regionAnalytics.analytics.total_transactions.toLocaleString()}
                        </div>
                        <div className="text-sm text-gray-600">Transactions</div>
                      </div>
                      <div className="text-center p-4 bg-purple-50 rounded-lg">
                        <div className="text-2xl font-bold text-purple-600">
                          {formatPrice(regionAnalytics.analytics.avg_price_aed)}
                        </div>
                        <div className="text-sm text-gray-600">Avg Price</div>
                      </div>
                      <div className="text-center p-4 bg-orange-50 rounded-lg">
                        <div className="text-2xl font-bold text-orange-600">
                          AED {regionAnalytics.analytics.avg_price_per_sqft.toFixed(0)}
                        </div>
                        <div className="text-sm text-gray-600">Price/sqft</div>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 p-3 bg-gray-50 rounded-lg">
                      <span className="font-medium">Price Trend:</span>
                      {getTrendIcon(regionAnalytics.analytics.price_trend)}
                      <span className="capitalize">{regionAnalytics.analytics.price_trend}</span>
                    </div>
                  </TabsContent>

                  <TabsContent value="pricing" className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="text-center p-4 bg-red-50 rounded-lg">
                        <div className="text-xl font-bold text-red-600">
                          {formatPrice(regionAnalytics.analytics.min_price_aed)}
                        </div>
                        <div className="text-sm text-gray-600">Minimum Price</div>
                      </div>
                      <div className="text-center p-4 bg-blue-50 rounded-lg">
                        <div className="text-xl font-bold text-blue-600">
                          {formatPrice(regionAnalytics.analytics.median_price_aed)}
                        </div>
                        <div className="text-sm text-gray-600">Median Price</div>
                      </div>
                      <div className="text-center p-4 bg-green-50 rounded-lg">
                        <div className="text-xl font-bold text-green-600">
                          {formatPrice(regionAnalytics.analytics.max_price_aed)}
                        </div>
                        <div className="text-sm text-gray-600">Maximum Price</div>
                      </div>
                    </div>
                  </TabsContent>

                  <TabsContent value="transactions" className="space-y-4">
                    <div className="space-y-4">
                      <h4 className="font-semibold">Property Types</h4>
                      {regionAnalytics.analytics.property_types.map((type, index) => (
                        <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <span className="font-medium">{type.type}</span>
                          <div className="text-right">
                            <div className="font-semibold">{type.count} units</div>
                            <div className="text-sm text-gray-600">
                              {formatPrice(type.avg_price)} avg
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </TabsContent>

                  <TabsContent value="developers" className="space-y-4">
                    <div className="space-y-4">
                      <h4 className="font-semibold">Top Developers</h4>
                      {regionAnalytics.analytics.top_developers.map((dev, index) => (
                        <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <div className="flex items-center gap-2">
                            <Building2 className="h-4 w-4 text-gray-500" />
                            <span className="font-medium">{dev.name || 'Unknown'}</span>
                          </div>
                          <div className="text-right">
                            <div className="font-semibold">{dev.count} properties</div>
                            <div className="text-sm text-gray-600">
                              {formatPrice(dev.avg_price)} avg
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </TabsContent>
                </Tabs>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="text-center py-12">
                <MapPin className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">Select a Region</h3>
                <p className="text-gray-600">
                  Choose a region from the popular areas list or search for a specific region to view detailed analytics.
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

export default RegionAnalytics;
