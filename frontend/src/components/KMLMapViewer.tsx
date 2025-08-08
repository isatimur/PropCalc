'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Alert, AlertDescription } from './ui/alert';
import { Search, MapPin, Navigation, Globe } from 'lucide-react';

interface Area {
  id: number;
  name: string;
  name_arabic?: string;
  name_english?: string;
  sector_number?: string;
  community_number?: string;
  center_latitude?: number;
  center_longitude?: number;
  area_sqm?: number;
  perimeter_m?: number;
  source_file?: string;
}

interface Point {
  id: number;
  name: string;
  latitude: number;
  longitude: number;
  altitude?: number;
  source_file?: string;
}

interface SearchResults {
  areas: Area[];
  points: Point[];
  total_areas: number;
  total_points: number;
  search_coordinates?: {
    latitude: number;
    longitude: number;
  };
  radius_km?: number;
}

const KMLMapViewer: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResults | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedArea, setSelectedArea] = useState<Area | null>(null);
  const [coordinateSearch, setCoordinateSearch] = useState({
    latitude: 25.2048,
    longitude: 55.2708,
    radius: 5.0
  });

  const searchAreas = async () => {
    if (!searchTerm.trim()) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`/api/kml/areas/search?search_term=${encodeURIComponent(searchTerm)}&limit=20`);
      if (!response.ok) throw new Error('Failed to search areas');
      
      const data = await response.json();
      setSearchResults(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const searchByCoordinates = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/kml/search/coordinates', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          latitude: coordinateSearch.latitude,
          longitude: coordinateSearch.longitude,
          radius_km: coordinateSearch.radius
        })
      });
      
      if (!response.ok) throw new Error('Failed to search by coordinates');
      
      const data = await response.json();
      setSearchResults(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const getAreaDetails = async (areaId: number) => {
    try {
      const response = await fetch(`/api/kml/areas/${areaId}`);
      if (!response.ok) throw new Error('Failed to get area details');
      
      const area = await response.json();
      setSelectedArea(area);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    }
  };

  const formatAreaSize = (areaSqm: number) => {
    if (areaSqm >= 1000000) {
      return `${(areaSqm / 1000000).toFixed(2)} km²`;
    } else if (areaSqm >= 10000) {
      return `${(areaSqm / 10000).toFixed(2)} ha`;
    } else {
      return `${areaSqm.toFixed(0)} m²`;
    }
  };

  const formatDistance = (distanceKm: number) => {
    if (distanceKm < 1) {
      return `${(distanceKm * 1000).toFixed(0)} m`;
    } else {
      return `${distanceKm.toFixed(2)} km`;
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">KML Geographic Data Viewer</h1>
        <Badge variant="secondary">
          <Globe className="w-4 h-4 mr-2" />
          Dubai Geographic Areas
        </Badge>
      </div>

      <Tabs defaultValue="search" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="search">Area Search</TabsTrigger>
          <TabsTrigger value="coordinates">Coordinate Search</TabsTrigger>
        </TabsList>

        <TabsContent value="search" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Search className="w-5 h-5" />
                Search Areas by Name
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex gap-2">
                <Input
                  placeholder="Enter area name (English or Arabic)..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && searchAreas()}
                />
                <Button onClick={searchAreas} disabled={loading}>
                  {loading ? 'Searching...' : 'Search'}
                </Button>
              </div>
              
              {error && (
                <Alert>
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="coordinates" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MapPin className="w-5 h-5" />
                Search by Coordinates
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="text-sm font-medium">Latitude</label>
                  <Input
                    type="number"
                    step="0.000001"
                    value={coordinateSearch.latitude}
                    onChange={(e) => setCoordinateSearch(prev => ({
                      ...prev,
                      latitude: parseFloat(e.target.value) || 0
                    }))}
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">Longitude</label>
                  <Input
                    type="number"
                    step="0.000001"
                    value={coordinateSearch.longitude}
                    onChange={(e) => setCoordinateSearch(prev => ({
                      ...prev,
                      longitude: parseFloat(e.target.value) || 0
                    }))}
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">Radius (km)</label>
                  <Input
                    type="number"
                    step="0.1"
                    value={coordinateSearch.radius}
                    onChange={(e) => setCoordinateSearch(prev => ({
                      ...prev,
                      radius: parseFloat(e.target.value) || 5.0
                    }))}
                  />
                </div>
              </div>
              
              <Button onClick={searchByCoordinates} disabled={loading}>
                {loading ? 'Searching...' : 'Search by Coordinates'}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {searchResults && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Navigation className="w-5 h-5" />
              Search Results
              <Badge variant="outline">
                {searchResults.total_areas} areas, {searchResults.total_points} points
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Areas */}
              <div>
                <h3 className="font-semibold mb-3">Areas ({searchResults.areas.length})</h3>
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {searchResults.areas.map((area) => (
                    <div
                      key={area.id}
                      className="p-3 border rounded-lg hover:bg-gray-50 cursor-pointer"
                      onClick={() => getAreaDetails(area.id)}
                    >
                      <div className="font-medium">{area.name_english || area.name}</div>
                      {area.name_arabic && (
                        <div className="text-sm text-gray-600">{area.name_arabic}</div>
                      )}
                      <div className="flex gap-2 mt-2">
                        {area.sector_number && (
                          <Badge variant="secondary">Sector {area.sector_number}</Badge>
                        )}
                        {area.community_number && (
                          <Badge variant="secondary">Community {area.community_number}</Badge>
                        )}
                      </div>
                      {area.area_sqm && (
                        <div className="text-xs text-gray-500 mt-1">
                          Area: {formatAreaSize(area.area_sqm)}
                        </div>
                      )}
                      {area.center_latitude && area.center_longitude && (
                        <div className="text-xs text-gray-500">
                          Center: {area.center_latitude.toFixed(6)}, {area.center_longitude.toFixed(6)}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Points */}
              <div>
                <h3 className="font-semibold mb-3">Points ({searchResults.points.length})</h3>
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {searchResults.points.slice(0, 20).map((point) => (
                    <div key={point.id} className="p-3 border rounded-lg">
                      <div className="font-medium">{point.name}</div>
                      <div className="text-xs text-gray-500">
                        {point.latitude.toFixed(6)}, {point.longitude.toFixed(6)}
                      </div>
                      {point.altitude && (
                        <div className="text-xs text-gray-500">
                          Altitude: {point.altitude.toFixed(1)}m
                        </div>
                      )}
                    </div>
                  ))}
                  {searchResults.points.length > 20 && (
                    <div className="text-sm text-gray-500 text-center py-2">
                      Showing first 20 of {searchResults.points.length} points
                    </div>
                  )}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {selectedArea && (
        <Card>
          <CardHeader>
            <CardTitle>Area Details</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <h4 className="font-semibold">Basic Information</h4>
                <div className="space-y-2 mt-2">
                  <div><strong>ID:</strong> {selectedArea.id}</div>
                  <div><strong>Name:</strong> {selectedArea.name_english || selectedArea.name}</div>
                  {selectedArea.name_arabic && (
                    <div><strong>Arabic Name:</strong> {selectedArea.name_arabic}</div>
                  )}
                  {selectedArea.sector_number && (
                    <div><strong>Sector:</strong> {selectedArea.sector_number}</div>
                  )}
                  {selectedArea.community_number && (
                    <div><strong>Community:</strong> {selectedArea.community_number}</div>
                  )}
                </div>
              </div>
              <div>
                <h4 className="font-semibold">Geographic Data</h4>
                <div className="space-y-2 mt-2">
                  {selectedArea.center_latitude && selectedArea.center_longitude && (
                    <div><strong>Center:</strong> {selectedArea.center_latitude.toFixed(6)}, {selectedArea.center_longitude.toFixed(6)}</div>
                  )}
                  {selectedArea.area_sqm && (
                    <div><strong>Area:</strong> {formatAreaSize(selectedArea.area_sqm)}</div>
                  )}
                  {selectedArea.perimeter_m && (
                    <div><strong>Perimeter:</strong> {formatDistance(selectedArea.perimeter_m / 1000)}</div>
                  )}
                  {selectedArea.source_file && (
                    <div><strong>Source:</strong> {selectedArea.source_file}</div>
                  )}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default KMLMapViewer; 