'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { Calendar, Filter, RefreshCw, TrendingUp } from 'lucide-react';
import { Badge } from '@/components/ui/badge';

export interface DLDFilterState {
  // Timeline filters
  timeline: '1m' | '3m' | '6m' | '1y' | '3y' | '5y' | 'custom' | 'all';
  startDate: string;
  endDate: string;
  
  // Property filters
  propertyType: string;
  propertyUsage: string;
  propertySubtype: string;
  registrationType: string;
  
  // Location filters
  location: string;
  area: string;
  
  // Price filters
  minPrice: string;
  maxPrice: string;
  
  // Developer filters
  developerName: string;
  projectName: string;
  
  // Additional filters
  buyerNationality: string;
  sellerNationality: string;
  hasParking: boolean;
  hasMetro: boolean;
}

interface DLDFiltersProps {
  filters: DLDFilterState;
  onFiltersChange: (filters: DLDFilterState) => void;
  onReset: () => void;
  onApply: () => void;
  isLoading?: boolean;
}

const TIMELINE_OPTIONS = [
  { value: '1m', label: 'Last Month', icon: '📅' },
  { value: '3m', label: 'Last 3 Months', icon: '📊' },
  { value: '6m', label: 'Last 6 Months', icon: '📈' },
  { value: '1y', label: 'Last Year', icon: '📊' },
  { value: '3y', label: 'Last 3 Years', icon: '📈' },
  { value: '5y', label: 'Last 5 Years', icon: '📊' },
  { value: 'custom', label: 'Custom Range', icon: '🎯' },
  { value: 'all', label: 'All Time', icon: '🌍' },
];

const PROPERTY_TYPES = [
  'Building', 'Land', 'Unit', 'Villa'
];

const PROPERTY_USAGE = [
  'Residential', 'Commercial', 'Land', 'Mixed Use'
];

const PROPERTY_SUBTYPES = [
  'Building', 'Clinic', 'Flat', 'Gymnasium', 'Hotel', 'Hotel Apartment', 'Hotel Rooms', 'Office', 'Parking'
];

const REGISTRATION_TYPES = [
  'Existing Properties', 'Off-Plan Properties'
];

export default function DLDFilters({ filters, onFiltersChange, onReset, onApply, isLoading }: DLDFiltersProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const handleFilterChange = (key: keyof DLDFilterState, value: any) => {
    onFiltersChange({ ...filters, [key]: value });
  };

  const handleTimelineChange = (timeline: string) => {
    const newFilters = { ...filters, timeline: timeline as any };
    
    // Auto-set dates for predefined timelines
    if (timeline !== 'custom' && timeline !== 'all') {
      const endDate = new Date();
      let startDate = new Date();
      
      switch (timeline) {
        case '1m':
          startDate.setMonth(endDate.getMonth() - 1);
          break;
        case '3m':
          startDate.setMonth(endDate.getMonth() - 3);
          break;
        case '6m':
          startDate.setMonth(endDate.getMonth() - 6);
          break;
        case '1y':
          startDate.setFullYear(endDate.getFullYear() - 1);
          break;
        case '3y':
          startDate.setFullYear(endDate.getFullYear() - 3);
          break;
        case '5y':
          startDate.setFullYear(endDate.getFullYear() - 5);
          break;
      }
      
      newFilters.startDate = startDate.toISOString().split('T')[0];
      newFilters.endDate = endDate.toISOString().split('T')[0];
    }
    
    onFiltersChange(newFilters);
  };

  const getActiveFiltersCount = () => {
    let count = 0;
    if (filters.propertyType) count++;
    if (filters.propertyUsage) count++;
    if (filters.propertySubtype) count++;
    if (filters.registrationType) count++;
    if (filters.location) count++;
    if (filters.area) count++;
    if (filters.minPrice) count++;
    if (filters.maxPrice) count++;
    if (filters.developerName) count++;
    if (filters.projectName) count++;
    if (filters.buyerNationality) count++;
    if (filters.sellerNationality) count++;
    return count;
  };

  const activeFiltersCount = getActiveFiltersCount();

  return (
    <Card className="mb-6">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Filter className="h-5 w-5 text-blue-600" />
            <CardTitle className="text-lg">DLD Analytics Filters</CardTitle>
            {activeFiltersCount > 0 && (
              <Badge variant="secondary" className="ml-2">
                {activeFiltersCount} active
              </Badge>
            )}
          </div>
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsExpanded(!isExpanded)}
            >
              {isExpanded ? 'Hide' : 'Show'} Advanced
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={onReset}
              disabled={isLoading}
            >
              <RefreshCw className="h-4 w-4 mr-1" />
              Reset
            </Button>
            <Button
              onClick={onApply}
              disabled={isLoading}
              className="bg-blue-600 hover:bg-blue-700"
            >
              <TrendingUp className="h-4 w-4 mr-1" />
              Apply Filters
            </Button>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Timeline Selection */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="timeline">Timeline</Label>
            <Select value={filters.timeline} onValueChange={handleTimelineChange}>
              <SelectTrigger>
                <SelectValue placeholder="Select timeline" />
              </SelectTrigger>
              <SelectContent>
                {TIMELINE_OPTIONS.map((option) => (
                  <SelectItem key={option.value} value={option.value}>
                    <span className="mr-2">{option.icon}</span>
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          
          {filters.timeline === 'custom' && (
            <>
              <div className="space-y-2">
                <Label htmlFor="startDate">Start Date</Label>
                <Input
                  type="date"
                  value={filters.startDate}
                  onChange={(e) => handleFilterChange('startDate', e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="endDate">End Date</Label>
                <Input
                  type="date"
                  value={filters.endDate}
                  onChange={(e) => handleFilterChange('endDate', e.target.value)}
                />
              </div>
            </>
          )}
        </div>

        {/* Basic Filters */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="space-y-2">
            <Label htmlFor="propertyType">Property Type</Label>
            <Select value={filters.propertyType} onValueChange={(value) => handleFilterChange('propertyType', value)}>
              <SelectTrigger>
                <SelectValue placeholder="All types" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All types</SelectItem>
                {PROPERTY_TYPES.map((type) => (
                  <SelectItem key={type} value={type}>{type}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="propertyUsage">Property Usage</Label>
            <Select value={filters.propertyUsage} onValueChange={(value) => handleFilterChange('propertyUsage', value)}>
              <SelectTrigger>
                <SelectValue placeholder="All usage types" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All usage types</SelectItem>
                {PROPERTY_USAGE.map((usage) => (
                  <SelectItem key={usage} value={usage}>{usage}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="registrationType">Registration Type</Label>
            <Select value={filters.registrationType} onValueChange={(value) => handleFilterChange('registrationType', value)}>
              <SelectTrigger>
                <SelectValue placeholder="All registration types" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All registration types</SelectItem>
                {REGISTRATION_TYPES.map((type) => (
                  <SelectItem key={type} value={type}>{type}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Advanced Filters */}
        {isExpanded && (
          <div className="space-y-4 pt-4 border-t">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="location">Location</Label>
                <Input
                  placeholder="e.g., Dubai Marina"
                  value={filters.location}
                  onChange={(e) => handleFilterChange('location', e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="area">Area</Label>
                <Input
                  placeholder="e.g., Downtown"
                  value={filters.area}
                  onChange={(e) => handleFilterChange('area', e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="developerName">Developer</Label>
                <Input
                  placeholder="Developer name"
                  value={filters.developerName}
                  onChange={(e) => handleFilterChange('developerName', e.target.value)}
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="minPrice">Min Price (AED)</Label>
                <Input
                  type="number"
                  placeholder="0"
                  value={filters.minPrice}
                  onChange={(e) => handleFilterChange('minPrice', e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="maxPrice">Max Price (AED)</Label>
                <Input
                  type="number"
                  placeholder="10000000"
                  value={filters.maxPrice}
                  onChange={(e) => handleFilterChange('maxPrice', e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="projectName">Project Name</Label>
                <Input
                  placeholder="Project name"
                  value={filters.projectName}
                  onChange={(e) => handleFilterChange('projectName', e.target.value)}
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="buyerNationality">Buyer Nationality</Label>
                <Input
                  placeholder="e.g., UAE, India, UK"
                  value={filters.buyerNationality}
                  onChange={(e) => handleFilterChange('buyerNationality', e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="sellerNationality">Seller Nationality</Label>
                <Input
                  placeholder="e.g., UAE, India, UK"
                  value={filters.sellerNationality}
                  onChange={(e) => handleFilterChange('sellerNationality', e.target.value)}
                />
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
