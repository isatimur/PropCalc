"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Search, Filter, Download, MapPin, Building2, Calendar, DollarSign, TrendingUp, RefreshCw, Eye, BarChart3
} from "lucide-react";

interface DLDTransaction {
  transaction_id: string;
  property_id: string;
  transaction_date: string;
  transaction_type: string;
  property_type: string;
  area_sqft: number | null;
  price_aed: number;
  price_per_sqft: number | null;
  location: string;
  developer: string | null;
  project_name: string | null;
  latitude: number | null;
  longitude: number | null;
  created_at: string;
  updated_at: string;
}

export default function DLDTransactionsPage() {
  const [transactions, setTransactions] = useState<DLDTransaction[]>([]);
  const [filteredTransactions, setFilteredTransactions] = useState<DLDTransaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'list' | 'grid'>('list');
  const [selectedTransaction, setSelectedTransaction] = useState<DLDTransaction | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  
  // Filters
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedPropertyType, setSelectedPropertyType] = useState('all');
  const [selectedLocation, setSelectedLocation] = useState('all');
  const [priceRange, setPriceRange] = useState({ min: '', max: '' });
  const [sortBy, setSortBy] = useState('date');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize] = useState(50);
  const [totalTransactions, setTotalTransactions] = useState(0);

  useEffect(() => {
    fetchTransactions();
  }, [currentPage]);

  const fetchTransactions = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const offset = (currentPage - 1) * pageSize;
      const response = await fetch(`/api/v1/dld/transactions?skip=${offset}&limit=${pageSize}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setTransactions(data.data || data);
      setFilteredTransactions(data.data || data);
      setTotalTransactions(data.total || data.length);
    } catch (err) {
      console.error('Error fetching transactions:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch transactions');
    } finally {
      setLoading(false);
    }
  };

  // Apply filters
  useEffect(() => {
    let filtered = [...transactions];

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(t => 
        t.location.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (t.developer && t.developer.toLowerCase().includes(searchTerm.toLowerCase())) ||
        (t.project_name && t.project_name.toLowerCase().includes(searchTerm.toLowerCase())) ||
        t.transaction_id.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Property type filter
    if (selectedPropertyType !== 'all') {
      filtered = filtered.filter(t => t.property_type === selectedPropertyType);
    }

    // Location filter
    if (selectedLocation !== 'all') {
      filtered = filtered.filter(t => t.location === selectedLocation);
    }

    // Price range filter
    if (priceRange.min) {
      filtered = filtered.filter(t => t.price_aed >= parseFloat(priceRange.min));
    }
    if (priceRange.max) {
      filtered = filtered.filter(t => t.price_aed <= parseFloat(priceRange.max));
    }

    // Sorting
    filtered.sort((a, b) => {
      let aValue: any, bValue: any;
      
      switch (sortBy) {
        case 'date':
          aValue = new Date(a.transaction_date);
          bValue = new Date(b.transaction_date);
          break;
        case 'price':
          aValue = a.price_aed;
          bValue = b.price_aed;
          break;
        case 'area':
          aValue = a.area_sqft || 0;
          bValue = b.area_sqft || 0;
          break;
        case 'location':
          aValue = a.location;
          bValue = b.location;
          break;
        default:
          aValue = a.transaction_date;
          bValue = b.transaction_date;
      }

      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

    setFilteredTransactions(filtered);
  }, [transactions, searchTerm, selectedPropertyType, selectedLocation, priceRange, sortBy, sortOrder]);

  const handleTransactionClick = (transaction: DLDTransaction) => {
    setSelectedTransaction(transaction);
    setShowDetailModal(true);
  };

  const closeDetailModal = () => {
    setShowDetailModal(false);
    setSelectedTransaction(null);
  };

  const exportData = () => {
    const csvContent = [
      ['Transaction ID', 'Date', 'Property Type', 'Location', 'Developer', 'Project', 'Area (sqft)', 'Price (AED)', 'Price/sqft'],
      ...filteredTransactions.map(t => [
        t.transaction_id,
        t.transaction_date,
        t.property_type,
        t.location,
        t.developer || '',
        t.project_name || '',
        t.area_sqft || '',
        t.price_aed,
        t.price_per_sqft || ''
      ])
    ].map(row => row.join(',')).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'dld-transactions.csv';
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const getPropertyTypeColor = (type: string) => {
    const colors: { [key: string]: string } = {
      'apartment': 'bg-blue-100 text-blue-800',
      'villa': 'bg-green-100 text-green-800',
      'townhouse': 'bg-purple-100 text-purple-800',
      'office': 'bg-orange-100 text-orange-800',
      'retail': 'bg-pink-100 text-pink-800',
      'land': 'bg-gray-100 text-gray-800'
    };
    return colors[type.toLowerCase()] || 'bg-gray-100 text-gray-800';
  };

  const getTransactionTypeColor = (type: string) => {
    const colors: { [key: string]: string } = {
      'sale': 'bg-green-100 text-green-800',
      'rent': 'bg-blue-100 text-blue-800',
      'lease': 'bg-purple-100 text-purple-800'
    };
    return colors[type.toLowerCase()] || 'bg-gray-100 text-gray-800';
  };

  if (loading && transactions.length === 0) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading DLD transactions...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-red-800 mb-2">Error Loading Data</h2>
          <p className="text-red-600 mb-4">{error}</p>
          <Button onClick={fetchTransactions} variant="outline">
            <RefreshCw className="w-4 h-4 mr-2" />
            Retry
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">DLD Transaction Explorer</h1>
          <p className="text-gray-600 mt-2">
            Browse, filter, and analyze individual DLD transactions with comprehensive data
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={exportData}>
            <Download className="w-4 h-4 mr-2" />
            Export CSV
          </Button>
          <Button variant="outline" onClick={fetchTransactions}>
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <label className="text-sm font-medium text-gray-700 mb-2 block">Search</label>
              <Input
                placeholder="Search transactions..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full"
              />
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700 mb-2 block">Property Type</label>
              <select
                value={selectedPropertyType}
                onChange={(e) => setSelectedPropertyType(e.target.value)}
                className="w-full border border-gray-300 rounded-md px-3 py-2"
              >
                <option value="all">All Types</option>
                <option value="apartment">Apartment</option>
                <option value="villa">Villa</option>
                <option value="townhouse">Townhouse</option>
                <option value="office">Office</option>
                <option value="retail">Retail</option>
                <option value="land">Land</option>
              </select>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700 mb-2 block">Location</label>
              <select
                value={selectedLocation}
                onChange={(e) => setSelectedLocation(e.target.value)}
                className="w-full border border-gray-300 rounded-md px-3 py-2"
              >
                <option value="all">All Locations</option>
                {Array.from(new Set(transactions.map(t => t.location))).map(location => (
                  <option key={location} value={location}>{location}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700 mb-2 block">Price Range (AED)</label>
              <div className="flex gap-2">
                <Input
                  placeholder="Min"
                  value={priceRange.min}
                  onChange={(e) => setPriceRange(prev => ({ ...prev, min: e.target.value }))}
                  className="w-full"
                />
                <Input
                  placeholder="Max"
                  value={priceRange.max}
                  onChange={(e) => setPriceRange(prev => ({ ...prev, max: e.target.value }))}
                  className="w-full"
                />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* View Toggle and Sorting */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button
            variant={viewMode === 'list' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setViewMode('list')}
          >
            <BarChart3 className="w-4 h-4 mr-2" />
            List View
          </Button>
          <Button
            variant={viewMode === 'grid' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setViewMode('grid')}
          >
            <BarChart3 className="w-4 h-4 mr-2" />
            Grid View
          </Button>
        </div>
        
        <div className="flex items-center gap-2">
          <label className="text-sm font-medium text-gray-700">Sort by:</label>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="border border-gray-300 rounded-md px-2 py-1 text-sm"
          >
            <option value="date">Date</option>
            <option value="price">Price</option>
            <option value="area">Area</option>
            <option value="location">Location</option>
          </select>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc')}
          >
            {sortOrder === 'asc' ? '↑' : '↓'}
          </Button>
        </div>
      </div>

      {/* Results Summary */}
      <div className="text-sm text-gray-600">
        Showing {filteredTransactions.length} of {totalTransactions} transactions
      </div>

      {/* Transactions Display */}
      <Tabs value={viewMode} onValueChange={(value) => setViewMode(value as 'list' | 'grid')}>
        <TabsContent value="list" className="space-y-4">
          {filteredTransactions.map((transaction) => (
            <Card key={transaction.transaction_id} className="cursor-pointer hover:shadow-md transition-shadow" onClick={() => handleTransactionClick(transaction)}>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <Badge className={getPropertyTypeColor(transaction.property_type)}>
                        {transaction.property_type}
                      </Badge>
                      <Badge className={getTransactionTypeColor(transaction.transaction_type)}>
                        {transaction.transaction_type}
                      </Badge>
                      <Badge variant="outline">
                        {transaction.transaction_id.slice(-8)}
                      </Badge>
                    </div>
                    <h3 className="font-semibold text-lg mb-2">
                      {transaction.location}
                    </h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-600">
                      <div>
                        <span className="font-medium">Price:</span>
                        <div className="text-lg font-bold text-green-600">
                          AED {transaction.price_aed.toLocaleString()}
                        </div>
                      </div>
                      <div>
                        <span className="font-medium">Area:</span>
                        <div>{transaction.area_sqft ? `${transaction.area_sqft.toLocaleString()} sqft` : 'N/A'}</div>
                      </div>
                      <div>
                        <span className="font-medium">Price/sqft:</span>
                        <div>{transaction.price_per_sqft ? `AED ${transaction.price_per_sqft.toLocaleString()}` : 'N/A'}</div>
                      </div>
                      <div>
                        <span className="font-medium">Date:</span>
                        <div>{new Date(transaction.transaction_date).toLocaleDateString()}</div>
                      </div>
                    </div>
                    {transaction.developer && (
                      <div className="mt-2 text-sm text-gray-600">
                        <span className="font-medium">Developer:</span> {transaction.developer}
                      </div>
                    )}
                    {transaction.project_name && (
                      <div className="mt-1 text-sm text-gray-600">
                        <span className="font-medium">Project:</span> {transaction.project_name}
                      </div>
                    )}
                  </div>
                  <Button variant="outline" size="sm">
                    <Eye className="w-4 h-4 mr-2" />
                    View Details
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </TabsContent>

        <TabsContent value="grid" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredTransactions.map((transaction) => (
              <Card key={transaction.transaction_id} className="cursor-pointer hover:shadow-md transition-shadow" onClick={() => handleTransactionClick(transaction)}>
                <CardContent className="pt-6">
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <Badge className={getPropertyTypeColor(transaction.property_type)}>
                        {transaction.property_type}
                      </Badge>
                      <Badge variant="outline">
                        {transaction.transaction_id.slice(-8)}
                      </Badge>
                    </div>
                    
                    <div>
                      <h3 className="font-semibold text-lg mb-2">{transaction.location}</h3>
                      <div className="text-2xl font-bold text-green-600 mb-2">
                        AED {transaction.price_aed.toLocaleString()}
                      </div>
                      <div className="text-sm text-gray-600">
                        {transaction.area_sqft ? `${transaction.area_sqft.toLocaleString()} sqft` : 'Area N/A'}
                      </div>
                    </div>

                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Type:</span>
                        <span className="font-medium">{transaction.transaction_type}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Date:</span>
                        <span>{new Date(transaction.transaction_date).toLocaleDateString()}</span>
                      </div>
                      {transaction.price_per_sqft && (
                        <div className="flex justify-between">
                          <span className="text-gray-600">Price/sqft:</span>
                          <span>AED {transaction.price_per_sqft.toLocaleString()}</span>
                        </div>
                      )}
                    </div>

                    {transaction.developer && (
                      <div className="pt-2 border-t">
                        <div className="text-sm text-gray-600">
                          <span className="font-medium">Developer:</span> {transaction.developer}
                        </div>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>

      {/* Pagination */}
      {totalTransactions > pageSize && (
        <div className="flex items-center justify-center gap-2">
          <Button
            variant="outline"
            onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
            disabled={currentPage === 1}
          >
            Previous
          </Button>
          <span className="text-sm text-gray-600">
            Page {currentPage} of {Math.ceil(totalTransactions / pageSize)}
          </span>
          <Button
            variant="outline"
            onClick={() => setCurrentPage(prev => Math.min(Math.ceil(totalTransactions / pageSize), prev + 1))}
            disabled={currentPage >= Math.ceil(totalTransactions / pageSize)}
          >
            Next
          </Button>
        </div>
      )}

      {/* Detail Modal */}
      {showDetailModal && selectedTransaction && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold">Transaction Details</h2>
                <Button variant="outline" size="sm" onClick={closeDetailModal}>
                  ✕
                </Button>
              </div>
              
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-gray-600">Transaction ID</label>
                    <p className="font-mono text-sm">{selectedTransaction.transaction_id}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-600">Property ID</label>
                    <p className="font-mono text-sm">{selectedTransaction.property_id}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-600">Transaction Date</label>
                    <p>{new Date(selectedTransaction.transaction_date).toLocaleDateString()}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-600">Transaction Type</label>
                    <Badge className={getTransactionTypeColor(selectedTransaction.transaction_type)}>
                      {selectedTransaction.transaction_type}
                    </Badge>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-600">Property Type</label>
                    <Badge className={getPropertyTypeColor(selectedTransaction.property_type)}>
                      {selectedTransaction.property_type}
                    </Badge>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-600">Location</label>
                    <p>{selectedTransaction.location}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-600">Price (AED)</label>
                    <p className="text-lg font-bold text-green-600">
                      {selectedTransaction.price_aed.toLocaleString()}
                    </p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-600">Area (sqft)</label>
                    <p>{selectedTransaction.area_sqft ? selectedTransaction.area_sqft.toLocaleString() : 'N/A'}</p>
                  </div>
                  {selectedTransaction.price_per_sqft && (
                    <div>
                      <label className="text-sm font-medium text-gray-600">Price per sqft</label>
                      <p>AED {selectedTransaction.price_per_sqft.toLocaleString()}</p>
                    </div>
                  )}
                  {selectedTransaction.developer && (
                    <div>
                      <label className="text-sm font-medium text-gray-600">Developer</label>
                      <p>{selectedTransaction.developer}</p>
                    </div>
                  )}
                  {selectedTransaction.project_name && (
                    <div>
                      <label className="text-sm font-medium text-gray-600">Project Name</label>
                      <p>{selectedTransaction.project_name}</p>
                    </div>
                  )}
                </div>
                
                {(selectedTransaction.latitude && selectedTransaction.longitude) && (
                  <div>
                    <label className="text-sm font-medium text-gray-600">Coordinates</label>
                    <p className="font-mono text-sm">
                      {selectedTransaction.latitude}, {selectedTransaction.longitude}
                    </p>
                  </div>
                )}
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-gray-600">Created</label>
                    <p className="text-sm">{new Date(selectedTransaction.created_at).toLocaleString()}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-600">Updated</label>
                    <p className="text-sm">{new Date(selectedTransaction.updated_at).toLocaleString()}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
