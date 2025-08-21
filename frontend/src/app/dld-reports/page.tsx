"use client";

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Progress } from "@/components/ui/progress";
import { 
  FileText, 
  BarChart3, 
  LineChart, 
  PieChart, 
  Download,
  RefreshCw,
  Filter,
  Search,
  Calendar,
  TrendingUp,
  TrendingDown,
  MapPin,
  Building2,
  DollarSign,
  Users,
  Eye,
  Share2,
  Printer,
  Mail,
  AlertTriangle,
  CheckCircle,
  Clock,
  Target,
  ArrowUpRight,
  ArrowDownRight,
  Minus
} from "lucide-react";

interface Report {
  id: string;
  title: string;
  type: 'market' | 'transaction' | 'valuation' | 'trend' | 'comparison';
  location: string;
  dateRange: string;
  status: 'completed' | 'processing' | 'failed';
  createdAt: string;
  lastUpdated: string;
  dataPoints: number;
  fileSize: string;
  downloadUrl?: string;
  summary: ReportSummary;
  tags: string[];
}

interface ReportSummary {
  totalProperties: number;
  avgPrice: number;
  priceChange: number;
  transactionVolume: number;
  volumeChange: number;
  marketTrend: 'up' | 'down' | 'stable';
  keyInsights: string[];
}

interface MarketData {
  location: string;
  propertyType: string;
  avgPrice: number;
  priceChange: number;
  volume: number;
  volumeChange: number;
  demand: 'high' | 'medium' | 'low';
  supply: 'high' | 'medium' | 'low';
  forecast: number;
}

interface TransactionData {
  id: string;
  propertyType: string;
  location: string;
  transactionType: 'sale' | 'rent' | 'lease';
  price: number;
  area: number;
  date: string;
  buyer: string;
  seller: string;
  status: 'completed' | 'pending' | 'cancelled';
}

export default function DLDReportsPage() {
  const [reports, setReports] = useState<Report[]>([]);
  const [marketData, setMarketData] = useState<MarketData[]>([]);
  const [transactionData, setTransactionData] = useState<TransactionData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedReportType, setSelectedReportType] = useState<string>('all');
  const [selectedLocation, setSelectedLocation] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [showReportBuilder, setShowReportBuilder] = useState(false);
  const [newReport, setNewReport] = useState({
    title: '',
    type: '',
    location: '',
    dateRange: '',
    tags: []
  });

  // Mock data - replace with actual API calls
  const mockReports: Report[] = [
    {
      id: '1',
      title: 'Dubai Marina Market Analysis Q4 2024',
      type: 'market',
      location: 'Dubai Marina',
      dateRange: 'Oct 2024 - Dec 2024',
      status: 'completed',
      createdAt: '2024-01-15',
      lastUpdated: '2024-01-15',
      dataPoints: 1250,
      fileSize: '2.4 MB',
      downloadUrl: '/reports/dubai-marina-q4-2024.pdf',
      summary: {
        totalProperties: 1250,
        avgPrice: 4200000,
        priceChange: 8.5,
        transactionVolume: 156,
        volumeChange: 12.3,
        marketTrend: 'up',
        keyInsights: [
          'Strong demand for waterfront properties',
          'Luxury segment showing 15% growth',
          'New developments driving prices up'
        ]
      },
      tags: ['Market Analysis', 'Dubai Marina', 'Q4 2024', 'Luxury']
    },
    {
      id: '2',
      title: 'Commercial Property Transaction Report',
      type: 'transaction',
      location: 'Business Bay',
      dateRange: 'Jan 2024 - Dec 2024',
      status: 'completed',
      createdAt: '2024-01-10',
      lastUpdated: '2024-01-10',
      dataPoints: 890,
      fileSize: '1.8 MB',
      downloadUrl: '/reports/commercial-transactions-2024.pdf',
      summary: {
        totalProperties: 890,
        avgPrice: 7800000,
        priceChange: -2.1,
        transactionVolume: 45,
        volumeChange: -8.7,
        marketTrend: 'down',
        keyInsights: [
          'Office market experiencing decline',
          'Remote work impact on demand',
          'Retail space showing resilience'
        ]
      },
      tags: ['Transactions', 'Commercial', 'Business Bay', '2024']
    },
    {
      id: '3',
      title: 'Property Valuation Trends Analysis',
      type: 'valuation',
      location: 'All Dubai',
      dateRange: 'Jan 2024 - Dec 2024',
      status: 'processing',
      createdAt: '2024-01-12',
      lastUpdated: '2024-01-14',
      dataPoints: 3200,
      fileSize: 'Processing...',
      summary: {
        totalProperties: 3200,
        avgPrice: 5500000,
        priceChange: 6.8,
        transactionVolume: 450,
        volumeChange: 15.2,
        marketTrend: 'up',
        keyInsights: [
          'Overall market showing positive growth',
          'Residential outperforming commercial',
          'Premium locations leading recovery'
        ]
      },
      tags: ['Valuation', 'Trends', 'Dubai', '2024']
    }
  ];

  const mockMarketData: MarketData[] = [
    {
      location: 'Dubai Marina',
      propertyType: 'Residential',
      avgPrice: 4200000,
      priceChange: 8.5,
      volume: 156,
      volumeChange: 12.3,
      demand: 'high',
      supply: 'medium',
      forecast: 12.3
    },
    {
      location: 'Business Bay',
      propertyType: 'Commercial',
      avgPrice: 7800000,
      priceChange: -2.1,
      volume: 45,
      volumeChange: -8.7,
      demand: 'medium',
      supply: 'high',
      forecast: -1.8
    },
    {
      location: 'Palm Jumeirah',
      propertyType: 'Luxury',
      avgPrice: 12000000,
      priceChange: 15.2,
      volume: 89,
      volumeChange: 25.6,
      demand: 'high',
      supply: 'low',
      forecast: 18.7
    }
  ];

  const mockTransactionData: TransactionData[] = [
    {
      id: 't1',
      propertyType: 'Residential Villa',
      location: 'Dubai Marina',
      transactionType: 'sale',
      price: 4500000,
      area: 2500,
      date: '2024-01-15',
      buyer: 'Private Investor',
      seller: 'Developer',
      status: 'completed'
    },
    {
      id: 't2',
      propertyType: 'Commercial Office',
      location: 'Business Bay',
      transactionType: 'lease',
      price: 180000,
      area: 5000,
      date: '2024-01-14',
      buyer: 'Tech Company',
      seller: 'Property Owner',
      status: 'completed'
    }
  ];

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        setReports(mockReports);
        setMarketData(mockMarketData);
        setTransactionData(mockTransactionData);
        setError(null);
      } catch (err) {
        setError('Failed to fetch report data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const filteredReports = reports.filter(report => {
    const matchesType = selectedReportType === 'all' || report.type === selectedReportType;
    const matchesLocation = selectedLocation === 'all' || report.location === selectedLocation;
    const matchesSearch = searchQuery === '' || 
      report.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      report.location.toLowerCase().includes(searchQuery.toLowerCase());
    
    return matchesType && matchesLocation && matchesSearch;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'processing':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'failed':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4" />;
      case 'processing':
        return <Clock className="h-4 w-4" />;
      case 'failed':
        return <AlertTriangle className="h-4 w-4" />;
      default:
        return <Clock className="h-4 w-4" />;
    }
  };

  const getTrendIcon = (trend: 'up' | 'down' | 'stable') => {
    switch (trend) {
      case 'up':
        return <ArrowUpRight className="h-4 w-4 text-green-600" />;
      case 'down':
        return <ArrowDownRight className="h-4 w-4 text-red-600" />;
      default:
        return <Minus className="h-4 w-4 text-gray-600" />;
    }
  };

  const getDemandColor = (demand: 'high' | 'medium' | 'low') => {
    switch (demand) {
      case 'high':
        return 'bg-green-100 text-green-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'low':
        return 'bg-red-100 text-red-800';
    }
  };

  const getSupplyColor = (supply: 'high' | 'medium' | 'low') => {
    switch (supply) {
      case 'high':
        return 'bg-red-100 text-red-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'low':
        return 'bg-green-100 text-green-800';
    }
  };

  const handleReportSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Here you would typically send the data to your API
    console.log('New report request:', newReport);
    setShowReportBuilder(false);
    setNewReport({
      title: '',
      type: '',
      location: '',
      dateRange: '',
      tags: []
    });
  };

  const downloadReport = (report: Report) => {
    if (report.downloadUrl) {
      const link = document.createElement('a');
      link.href = report.downloadUrl;
      link.download = `${report.title.replace(/\s+/g, '-')}.pdf`;
      link.click();
    }
  };

  const shareReport = (report: Report) => {
    // Here you would implement sharing functionality
    console.log('Sharing report:', report.title);
  };

  const printReport = (report: Report) => {
    // Here you would implement printing functionality
    console.log('Printing report:', report.title);
  };

  const exportAllData = () => {
    const data = {
      reports: filteredReports,
      marketData,
      transactionData,
      exportDate: new Date().toISOString(),
      filters: {
        reportType: selectedReportType,
        location: selectedLocation,
        searchQuery
      }
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `dld-reports-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const refreshData = useCallback(async () => {
    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 800));
      setError(null);
    } catch (err) {
      setError('Failed to refresh data');
    } finally {
      setLoading(false);
    }
  }, []);

  if (loading && reports.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4 text-blue-600" />
          <p className="text-gray-600">Loading reports...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <AlertTriangle className="h-8 w-8 mx-auto mb-4 text-red-600" />
          <p className="text-red-600 mb-4">{error}</p>
          <Button onClick={refreshData}>Retry</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">DLD Reports & Analytics</h1>
        <p className="text-gray-600">Comprehensive property market reports, analytics, and insights powered by DLD data</p>
      </div>

      {/* Quick Actions */}
      <div className="flex flex-wrap gap-4 mb-6">
        <Button onClick={() => setShowReportBuilder(true)} className="flex items-center gap-2">
          <FileText className="h-4 w-4" />
          Generate Report
        </Button>
        <Button variant="outline" onClick={refreshData} disabled={loading}>
          <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
        <Button variant="outline" onClick={exportAllData}>
          <Download className="h-4 w-4 mr-2" />
          Export All Data
        </Button>
      </div>

      {/* Filters */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Report Filters
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <Label htmlFor="search">Search Reports</Label>
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  id="search"
                  placeholder="Search reports..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <div>
              <Label htmlFor="reportType">Report Type</Label>
              <Select value={selectedReportType} onValueChange={setSelectedReportType}>
                <SelectTrigger>
                  <SelectValue placeholder="All Types" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Types</SelectItem>
                  <SelectItem value="market">Market Analysis</SelectItem>
                  <SelectItem value="transaction">Transaction Reports</SelectItem>
                  <SelectItem value="valuation">Valuation Reports</SelectItem>
                  <SelectItem value="trend">Trend Analysis</SelectItem>
                  <SelectItem value="comparison">Comparison Reports</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="location">Location</Label>
              <Select value={selectedLocation} onValueChange={setSelectedLocation}>
                <SelectTrigger>
                  <SelectValue placeholder="All Locations" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Locations</SelectItem>
                  <SelectItem value="Dubai Marina">Dubai Marina</SelectItem>
                  <SelectItem value="Business Bay">Business Bay</SelectItem>
                  <SelectItem value="Palm Jumeirah">Palm Jumeirah</SelectItem>
                  <SelectItem value="All Dubai">All Dubai</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Report Builder */}
      {showReportBuilder && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Generate New Report</CardTitle>
            <CardDescription>Configure and generate custom reports based on your requirements</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleReportSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="title">Report Title</Label>
                  <Input
                    id="title"
                    placeholder="Enter report title"
                    value={newReport.title}
                    onChange={(e) => setNewReport({...newReport, title: e.target.value})}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="type">Report Type</Label>
                  <Select value={newReport.type} onValueChange={(value) => setNewReport({...newReport, type: value})}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select report type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="market">Market Analysis</SelectItem>
                      <SelectItem value="transaction">Transaction Report</SelectItem>
                      <SelectItem value="valuation">Valuation Report</SelectItem>
                      <SelectItem value="trend">Trend Analysis</SelectItem>
                      <SelectItem value="comparison">Comparison Report</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="location">Location</Label>
                  <Input
                    id="location"
                    placeholder="Enter location"
                    value={newReport.location}
                    onChange={(e) => setNewReport({...newReport, location: e.target.value})}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="dateRange">Date Range</Label>
                  <Input
                    id="dateRange"
                    placeholder="e.g., Q4 2024, Jan-Dec 2024"
                    value={newReport.dateRange}
                    onChange={(e) => setNewReport({...newReport, dateRange: e.target.value})}
                    required
                  />
                </div>
              </div>
              <div className="flex gap-2">
                <Button type="submit">Generate Report</Button>
                <Button type="button" variant="outline" onClick={() => setShowReportBuilder(false)}>
                  Cancel
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      <Tabs defaultValue="reports" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="reports" className="flex items-center gap-2">
            <FileText className="h-4 w-4" />
            Reports
          </TabsTrigger>
          <TabsTrigger value="market" className="flex items-center gap-2">
            <BarChart3 className="h-4 w-4" />
            Market Data
          </TabsTrigger>
          <TabsTrigger value="transactions" className="flex items-center gap-2">
            <LineChart className="h-4 w-4" />
            Transactions
          </TabsTrigger>
          <TabsTrigger value="analytics" className="flex items-center gap-2">
            <PieChart className="h-4 w-4" />
            Analytics
          </TabsTrigger>
        </TabsList>

        <TabsContent value="reports" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {filteredReports.map((report) => (
              <Card key={report.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <CardTitle className="text-lg mb-2">{report.title}</CardTitle>
                      <div className="flex items-center gap-2 mb-2">
                        <MapPin className="h-4 w-4 text-gray-500" />
                        <span className="text-sm text-gray-600">{report.location}</span>
                        <Badge variant="outline" className="text-xs">
                          {report.type}
                        </Badge>
                      </div>
                      <div className="flex items-center gap-2">
                        <Calendar className="h-4 w-4 text-gray-500" />
                        <span className="text-sm text-gray-600">{report.dateRange}</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge className={getStatusColor(report.status)}>
                        {getStatusIcon(report.status)}
                        <span className="ml-1">{report.status}</span>
                      </Badge>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-600">Data Points</p>
                      <p className="text-lg font-semibold">{report.dataPoints.toLocaleString()}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">File Size</p>
                      <p className="text-sm font-medium">{report.fileSize}</p>
                    </div>
                  </div>

                  <div>
                    <p className="text-sm text-gray-600 mb-2">Key Insights</p>
                    <div className="space-y-1">
                      {report.summary.keyInsights.slice(0, 2).map((insight, index) => (
                        <div key={index} className="flex items-start gap-2">
                          <div className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2 flex-shrink-0" />
                          <p className="text-sm text-gray-700">{insight}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      {report.tags.slice(0, 2).map((tag, index) => (
                        <Badge key={index} variant="outline" className="text-xs">
                          {tag}
                        </Badge>
                      ))}
                      {report.tags.length > 2 && (
                        <Badge variant="outline" className="text-xs">
                          +{report.tags.length - 2}
                        </Badge>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      {report.status === 'completed' && (
                        <>
                          <Button size="sm" variant="outline" onClick={() => downloadReport(report)}>
                            <Download className="h-3 w-3" />
                          </Button>
                          <Button size="sm" variant="outline" onClick={() => shareReport(report)}>
                            <Share2 className="h-3 w-3" />
                          </Button>
                          <Button size="sm" variant="outline" onClick={() => printReport(report)}>
                            <Printer className="h-3 w-3" />
                          </Button>
                        </>
                      )}
                    </div>
                  </div>

                  <div className="text-xs text-gray-500">
                    Created: {new Date(report.createdAt).toLocaleDateString()}
                    {report.lastUpdated !== report.createdAt && 
                      ` • Updated: ${new Date(report.lastUpdated).toLocaleDateString()}`
                    }
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {filteredReports.length === 0 && (
            <Card>
              <CardContent className="text-center py-8">
                <FileText className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                <p className="text-gray-600">No reports found matching your criteria</p>
                <Button 
                  variant="outline" 
                  onClick={() => {
                    setSelectedReportType('all');
                    setSelectedLocation('all');
                    setSearchQuery('');
                  }}
                  className="mt-2"
                >
                  Clear Filters
                </Button>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="market" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {marketData.map((market, index) => (
              <Card key={index} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <MapPin className="h-4 w-4" />
                    {market.location}
                  </CardTitle>
                  <CardDescription>{market.propertyType} Properties</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-600">Average Price</p>
                      <p className="text-lg font-semibold">
                        ${market.avgPrice.toLocaleString()}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Price Change</p>
                      <div className="flex items-center gap-1">
                        {getTrendIcon(market.priceChange >= 0 ? 'up' : 'down')}
                        <p className={`text-lg font-semibold ${
                          market.priceChange >= 0 ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {Math.abs(market.priceChange)}%
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-600">Volume</p>
                      <p className="text-lg font-semibold">{market.volume}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Volume Change</p>
                      <div className="flex items-center gap-1">
                        {getTrendIcon(market.volumeChange >= 0 ? 'up' : 'down')}
                        <p className={`text-sm font-semibold ${
                          market.volumeChange >= 0 ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {Math.abs(market.volumeChange)}%
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-600">Demand</p>
                      <Badge className={getDemandColor(market.demand)}>
                        {market.demand}
                      </Badge>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Supply</p>
                      <Badge className={getSupplyColor(market.supply)}>
                        {market.supply}
                      </Badge>
                    </div>
                  </div>

                  <div>
                    <p className="text-sm text-gray-600">Forecast</p>
                    <div className="flex items-center gap-1">
                      {getTrendIcon(market.forecast >= 0 ? 'up' : 'down')}
                      <p className={`text-lg font-semibold ${
                        market.forecast >= 0 ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {market.forecast >= 0 ? '+' : ''}{market.forecast}%
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="transactions" className="space-y-6">
          <div className="space-y-4">
            {transactionData.map((transaction) => (
              <Card key={transaction.id} className="hover:shadow-lg transition-shadow">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="font-semibold">{transaction.propertyType}</h3>
                        <Badge variant="outline">{transaction.transactionType}</Badge>
                        <Badge className={transaction.status === 'completed' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}>
                          {transaction.status}
                        </Badge>
                      </div>
                      <div className="flex items-center gap-4 text-sm text-gray-600">
                        <span className="flex items-center gap-1">
                          <MapPin className="h-4 w-4" />
                          {transaction.location}
                        </span>
                        <span>{transaction.area} sq ft</span>
                        <span>{new Date(transaction.date).toLocaleDateString()}</span>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-semibold">${transaction.price.toLocaleString()}</p>
                      <p className="text-sm text-gray-600">
                        ${Math.round(transaction.price / transaction.area)}/sq ft
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="analytics" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Report Generation Stats</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Total Reports</span>
                    <span className="font-semibold">{reports.length}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Completed</span>
                    <span className="font-semibold text-green-600">
                      {reports.filter(r => r.status === 'completed').length}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Processing</span>
                    <span className="font-semibold text-yellow-600">
                      {reports.filter(r => r.status === 'processing').length}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Failed</span>
                    <span className="font-semibold text-red-600">
                      {reports.filter(r => r.status === 'failed').length}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Data Coverage</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-gray-600">Total Data Points</span>
                      <span className="font-semibold">
                        {reports.reduce((sum, r) => sum + r.dataPoints, 0).toLocaleString()}
                      </span>
                    </div>
                    <Progress value={75} className="h-2" />
                  </div>
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-gray-600">Coverage</span>
                      <span className="font-semibold">75%</span>
                    </div>
                    <Progress value={75} className="h-2" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>

      {/* Summary Statistics */}
      <Card className="mt-8">
        <CardHeader>
          <CardTitle>Reports Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {reports.length}
              </div>
              <p className="text-sm text-gray-600">Total Reports</p>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {reports.filter(r => r.status === 'completed').length}
              </div>
              <p className="text-sm text-gray-600">Completed</p>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {reports.reduce((sum, r) => sum + r.dataPoints, 0).toLocaleString()}
              </div>
              <p className="text-sm text-gray-600">Data Points</p>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">
                {reports.filter(r => r.status === 'processing').length}
              </div>
              <p className="text-sm text-gray-600">In Progress</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
