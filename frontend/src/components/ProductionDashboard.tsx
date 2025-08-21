'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Activity, 
  Database, 
  TrendingUp, 
  AlertTriangle, 
  Play, 
  Square, 
  Settings,
  BarChart3,
  MapPin,
  Building,
  DollarSign,
  Clock,
  Users,
  Zap
} from 'lucide-react';

interface StreamingStatus {
  status: string;
  mode: string;
  metrics: {
    total_processed: number;
    total_failed: number;
    records_per_second: number;
    quality_score: number;
    uptime_seconds: number;
  };
  queue_sizes: {
    processing_queue: number;
    analytics_queue: number;
  };
}

interface MarketInsight {
  insight_type: string;
  title: string;
  description: string;
  confidence_score: number;
  impact_level: string;
  timestamp: string;
}

interface SystemHealth {
  overall_status: string;
  cpu_usage_percent: number;
  memory_usage_mb: number;
  total_processed: number;
  records_per_second: number;
  uptime_seconds: number;
}

const ProductionDashboard: React.FC = () => {
  const [streamingStatus, setStreamingStatus] = useState<StreamingStatus | null>(null);
  const [marketInsights, setMarketInsights] = useState<MarketInsight[]>([]);
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch streaming status
  const fetchStreamingStatus = async () => {
    try {
      const response = await fetch('/api/v1/production/streaming/status');
      if (response.ok) {
        const data = await response.json();
        setStreamingStatus(data.data);
      }
    } catch (err) {
      console.error('Error fetching streaming status:', err);
    }
  };

  // Fetch market insights
  const fetchMarketInsights = async () => {
    try {
      const response = await fetch('/api/v1/production/insights/market');
      if (response.ok) {
        const data = await response.json();
        setMarketInsights(data.insights || []);
      }
    } catch (err) {
      console.error('Error fetching market insights:', err);
    }
  };

  // Fetch system health
  const fetchSystemHealth = async () => {
    try {
      const response = await fetch('/api/v1/production/system/health');
      if (response.ok) {
        const data = await response.json();
        setSystemHealth(data.health);
      }
    } catch (err) {
      console.error('Error fetching system health:', err);
    }
  };

  // Start streaming
  const startStreaming = async (mode: string = 'real_time') => {
    try {
      setIsLoading(true);
      const response = await fetch('/api/v1/production/streaming/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          mode,
          batch_size: 1000,
          processing_interval: 5,
          analytics_interval: 60
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log('Streaming started:', data);
        // Refresh status after starting
        setTimeout(fetchStreamingStatus, 2000);
      } else {
        const errorData = await response.json();
        setError(`Failed to start streaming: ${errorData.detail}`);
      }
    } catch (err) {
      setError(`Error starting streaming: ${err}`);
    } finally {
      setIsLoading(false);
    }
  };

  // Stop streaming
  const stopStreaming = async () => {
    try {
      setIsLoading(true);
      const response = await fetch('/api/v1/production/streaming/stop', {
        method: 'POST'
      });
      
      if (response.ok) {
        console.log('Streaming stopped');
        fetchStreamingStatus();
      }
    } catch (err) {
      setError(`Error stopping streaming: ${err}`);
    } finally {
      setIsLoading(false);
    }
  };

  // Initial data fetch
  useEffect(() => {
    const fetchInitialData = async () => {
      setIsLoading(true);
      try {
        await Promise.all([
          fetchStreamingStatus(),
          fetchMarketInsights(),
          fetchSystemHealth()
        ]);
      } catch (err) {
        setError('Failed to load dashboard data');
      } finally {
        setIsLoading(false);
      }
    };

    fetchInitialData();
  }, []);

  // Auto-refresh data
  useEffect(() => {
    const interval = setInterval(() => {
      fetchStreamingStatus();
      fetchSystemHealth();
      if (Math.random() > 0.7) { // Refresh insights less frequently
        fetchMarketInsights();
      }
    }, 5000); // Refresh every 5 seconds

    return () => clearInterval(interval);
  }, []);

  const formatUptime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'streaming': return 'bg-green-500';
      case 'processing': return 'bg-blue-500';
      case 'analyzing': return 'bg-purple-500';
      case 'error': return 'bg-red-500';
      case 'idle': return 'bg-gray-500';
      default: return 'bg-yellow-500';
    }
  };

  const getHealthStatus = (health: SystemHealth) => {
    if (health.overall_status === 'healthy') return { color: 'text-green-600', icon: '🟢' };
    if (health.overall_status === 'warning') return { color: 'text-yellow-600', icon: '🟡' };
    return { color: 'text-red-600', icon: '🔴' };
  };

  if (isLoading && !streamingStatus) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Production DLD Streaming</h1>
          <p className="text-muted-foreground">
            Real-time Dubai Land Department data streaming and analytics
          </p>
        </div>
        
        <div className="flex space-x-2">
          <Button 
            onClick={() => startStreaming('real_time')} 
            disabled={streamingStatus?.status === 'streaming' || isLoading}
            className="bg-green-600 hover:bg-green-700"
          >
            <Play className="w-4 h-4 mr-2" />
            Start Streaming
          </Button>
          <Button 
            onClick={stopStreaming} 
            disabled={streamingStatus?.status === 'idle' || isLoading}
            variant="destructive"
          >
            <Square className="w-4 h-4 mr-2" />
            Stop
          </Button>
        </div>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Status Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Streaming Status</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${getStatusColor(streamingStatus?.status || 'idle')}`}></div>
              <div className="text-2xl font-bold capitalize">
                {streamingStatus?.status || 'Unknown'}
              </div>
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Mode: {streamingStatus?.mode || 'N/A'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Records Processed</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {streamingStatus?.metrics.total_processed?.toLocaleString() || '0'}
            </div>
            <p className="text-xs text-muted-foreground">
              {streamingStatus?.metrics.records_per_second?.toFixed(2) || '0'} records/sec
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Data Quality</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {streamingStatus?.metrics.quality_score?.toFixed(1) || '0'}%
            </div>
            <Progress 
              value={streamingStatus?.metrics.quality_score || 0} 
              className="mt-2"
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">System Health</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-2">
              <span className="text-2xl">
                {systemHealth ? getHealthStatus(systemHealth).icon : '⚪'}
              </span>
              <div className={`text-2xl font-bold ${systemHealth ? getHealthStatus(systemHealth).color : ''}`}>
                {systemHealth?.overall_status || 'Unknown'}
              </div>
            </div>
            <p className="text-xs text-muted-foreground">
              Uptime: {systemHealth ? formatUptime(systemHealth.uptime_seconds) : 'N/A'}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="insights">Market Insights</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
          <TabsTrigger value="system">System</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Queue Status */}
            <Card>
              <CardHeader>
                <CardTitle>Processing Queues</CardTitle>
                <CardDescription>Real-time queue status and throughput</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Processing Queue</span>
                  <Badge variant="secondary">
                    {streamingStatus?.queue_sizes.processing_queue || 0} items
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Analytics Queue</span>
                  <Badge variant="secondary">
                    {streamingStatus?.queue_sizes.analytics_queue || 0} items
                  </Badge>
                </div>
                <div className="pt-2 border-t">
                  <div className="text-sm text-muted-foreground">
                    Failed: {streamingStatus?.metrics.total_failed || 0}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* System Metrics */}
            <Card>
              <CardHeader>
                <CardTitle>System Performance</CardTitle>
                <CardDescription>Resource usage and performance metrics</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>CPU Usage</span>
                    <span>{systemHealth?.cpu_usage_percent?.toFixed(1) || 0}%</span>
                  </div>
                  <Progress value={systemHealth?.cpu_usage_percent || 0} />
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Memory Usage</span>
                    <span>{((systemHealth?.memory_usage_mb || 0) / 1024).toFixed(1)} GB</span>
                  </div>
                  <Progress value={((systemHealth?.memory_usage_mb || 0) / 8192) * 100} />
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="insights" className="space-y-4">
          <div className="grid grid-cols-1 gap-4">
            {marketInsights.length > 0 ? (
              marketInsights.map((insight, index) => (
                <Card key={index}>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-lg">{insight.title}</CardTitle>
                      <div className="flex space-x-2">
                        <Badge variant={insight.impact_level === 'HIGH' ? 'destructive' : 
                                      insight.impact_level === 'MEDIUM' ? 'default' : 'secondary'}>
                          {insight.impact_level}
                        </Badge>
                        <Badge variant="outline">
                          {(insight.confidence_score * 100).toFixed(0)}% confidence
                        </Badge>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <p className="text-muted-foreground">{insight.description}</p>
                    <div className="mt-2 text-xs text-muted-foreground">
                      Generated: {new Date(insight.timestamp).toLocaleString()}
                    </div>
                  </CardContent>
                </Card>
              ))
            ) : (
              <Card>
                <CardContent className="pt-6">
                  <div className="text-center text-muted-foreground">
                    No market insights available yet. Start streaming to generate insights.
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>

        <TabsContent value="analytics" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <TrendingUp className="w-5 h-5 mr-2" />
                  Market Trends
                </CardTitle>
              </CardHeader>
              <CardContent>
                <Button variant="outline" className="w-full">
                  View Trends
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <MapPin className="w-5 h-5 mr-2" />
                  Location Heatmap
                </CardTitle>
              </CardHeader>
              <CardContent>
                <Button variant="outline" className="w-full">
                  View Heatmap
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Building className="w-5 h-5 mr-2" />
                  Developer Rankings
                </CardTitle>
              </CardHeader>
              <CardContent>
                <Button variant="outline" className="w-full">
                  View Rankings
                </Button>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="system" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Configuration</CardTitle>
                <CardDescription>Current streaming configuration</CardDescription>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm font-medium">Batch Size</span>
                  <span className="text-sm">1000</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm font-medium">Processing Interval</span>
                  <span className="text-sm">5s</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm font-medium">Analytics Interval</span>
                  <span className="text-sm">60s</span>
                </div>
                <div className="pt-2 border-t">
                  <Button variant="outline" size="sm">
                    <Settings className="w-4 h-4 mr-2" />
                    Configure
                  </Button>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Database Status</CardTitle>
                <CardDescription>Database connection and statistics</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <span className="text-sm">PostgreSQL Connected</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <span className="text-sm">Redis Connected</span>
                  </div>
                  <div className="pt-2 border-t">
                    <Button variant="outline" size="sm">
                      <Database className="w-4 h-4 mr-2" />
                      View Stats
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default ProductionDashboard;
