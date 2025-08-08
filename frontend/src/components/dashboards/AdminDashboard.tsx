'use client';

import { useState, useEffect } from 'react';
import { 
  Users, 
  Building, 
  BarChart3, 
  Settings, 
  Shield, 
  Database,
  Activity,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  Eye,
  Edit,
  Trash2,
  Plus,
  Download,
  RefreshCw,
  MoreHorizontal
} from 'lucide-react';

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Progress } from "@/components/ui/progress";
import { 
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Loading } from "@/components/ui/loading";
import { ErrorCard } from "@/components/ui/error";
import { useMarketOverview, useProjects } from "@/hooks/useApi";
import { formatCurrency, formatPercentage, formatNumber } from "@/lib/utils";
import Navigation from "@/components/navigation/Navigation";

interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  last_login: string;
}

interface SystemMetrics {
  total_users: number;
  active_users: number;
  total_projects: number;
  total_transactions: number;
  system_uptime: number;
  api_response_time: number;
  error_rate: number;
}

export default function AdminDashboard() {
  const { data: marketOverview, loading: marketLoading, error: marketError } = useMarketOverview();
  const { projects, loading: projectsLoading, error: projectsError } = useProjects(10);
  
  const [users, setUsers] = useState<User[]>([]);
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics | null>(null);
  const [loading, setLoading] = useState(false);

  // Mock data for demonstration
  useEffect(() => {
    setUsers([
      { id: '1', email: 'admin@propcalc.ae', full_name: 'System Admin', role: 'admin', is_active: true, last_login: '2024-01-15T10:30:00Z' },
      { id: '2', email: 'developer@propcalc.ae', full_name: 'Ahmed Al-Mansouri', role: 'developer', is_active: true, last_login: '2024-01-15T09:15:00Z' },
      { id: '3', email: 'investor@propcalc.ae', full_name: 'Sarah Thompson', role: 'investor', is_active: true, last_login: '2024-01-15T08:45:00Z' },
      { id: '4', email: 'consultant@propcalc.ae', full_name: 'Mohammad Hassan', role: 'consultant', is_active: true, last_login: '2024-01-15T07:30:00Z' },
    ]);

    setSystemMetrics({
      total_users: 156,
      active_users: 89,
      total_projects: 234,
      total_transactions: 15420,
      system_uptime: 99.9,
      api_response_time: 45,
      error_rate: 0.1
    });
  }, []);

  if (marketLoading || projectsLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 p-8">
        <Loading size="lg" text="Loading admin dashboard..." className="min-h-screen" />
      </div>
    );
  }

  if (marketError || projectsError) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 p-8">
        <ErrorCard 
          message={marketError || projectsError || "Failed to load admin dashboard"} 
          onRetry={() => window.location.reload()}
        />
      </div>
    );
  }

  // projects is already available from the hook

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      <Navigation />
      {/* Header */}
      <div className="bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div>
              <h1 className="text-2xl font-bold text-slate-900">Admin Dashboard</h1>
              <p className="text-sm text-slate-600">System Administration & Analytics</p>
            </div>
            <div className="flex items-center space-x-4">
              <Badge variant="secondary" className="bg-green-100 text-green-700">
                <CheckCircle className="h-3 w-3 mr-1" />
                System Healthy
              </Badge>
              <Button variant="outline" size="sm">
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh
              </Button>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" size="sm">
                    <MoreHorizontal className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuLabel>Admin Actions</DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem>
                    <Users className="h-4 w-4 mr-2" />
                    Manage Users
                  </DropdownMenuItem>
                  <DropdownMenuItem>
                    <Settings className="h-4 w-4 mr-2" />
                    System Settings
                  </DropdownMenuItem>
                  <DropdownMenuItem>
                    <Database className="h-4 w-4 mr-2" />
                    Database Admin
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* System Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-200">
            <CardContent>
              <div className="text-3xl font-bold text-slate-900 mb-2">
                {systemMetrics?.total_users || 0}
              </div>
              <div className="flex items-center text-sm">
                <Users className="h-4 w-4 text-blue-500 mr-2" />
                <span className="text-slate-600">Total Users</span>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-green-50 to-emerald-50 border-green-200">
            <CardContent>
              <div className="text-3xl font-bold text-slate-900 mb-2">
                {formatPercentage(systemMetrics?.system_uptime || 0)}%
              </div>
              <div className="flex items-center text-sm">
                <Activity className="h-4 w-4 text-green-500 mr-2" />
                <span className="text-slate-600">System Uptime</span>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-purple-50 to-violet-50 border-purple-200">
            <CardContent>
              <div className="text-3xl font-bold text-slate-900 mb-2">
                {systemMetrics?.api_response_time || 0}ms
              </div>
              <div className="flex items-center text-sm">
                <TrendingUp className="h-4 w-4 text-purple-500 mr-2" />
                <span className="text-slate-600">Avg Response Time</span>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-orange-50 to-amber-50 border-orange-200">
            <CardContent>
              <div className="text-3xl font-bold text-slate-900 mb-2">
                {systemMetrics?.error_rate || 0}%
              </div>
              <div className="flex items-center text-sm">
                <AlertTriangle className="h-4 w-4 text-orange-500 mr-2" />
                <span className="text-slate-600">Error Rate</span>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* User Management */}
          <Card className="shadow-lg border-slate-200">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-lg font-semibold text-slate-900">User Management</CardTitle>
                  <CardDescription>Active users and their roles</CardDescription>
                </div>
                <Button size="sm">
                  <Plus className="h-4 w-4 mr-2" />
                  Add User
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {users.map((user) => (
                  <div key={user.id} className="flex items-center justify-between p-4 border-b border-slate-100 last:border-b-0">
                    <div className="flex items-center space-x-3">
                      <Avatar className="h-10 w-10">
                        <AvatarFallback className="bg-blue-100 text-blue-600">
                          {user.full_name.charAt(0)}
                        </AvatarFallback>
                      </Avatar>
                      <div>
                        <h4 className="font-semibold text-slate-900">{user.full_name}</h4>
                        <p className="text-sm text-slate-500">{user.email}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge variant="secondary" className="text-xs">
                        {user.role}
                      </Badge>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem>
                            <Eye className="h-4 w-4 mr-2" />
                            View Details
                          </DropdownMenuItem>
                          <DropdownMenuItem>
                            <Edit className="h-4 w-4 mr-2" />
                            Edit User
                          </DropdownMenuItem>
                          <DropdownMenuItem className="text-red-600">
                            <Trash2 className="h-4 w-4 mr-2" />
                            Delete User
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* System Analytics */}
          <Card className="shadow-lg border-slate-200">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-lg font-semibold text-slate-900">System Analytics</CardTitle>
                  <CardDescription>Performance and usage metrics</CardDescription>
                </div>
                <Button variant="outline" size="sm">
                  <Download className="h-4 w-4 mr-2" />
                  Export
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-600">Active Users</span>
                  <span className="text-sm font-medium">{systemMetrics?.active_users || 0}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-600">Total Projects</span>
                  <span className="text-sm font-medium">{systemMetrics?.total_projects || 0}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-600">Total Transactions</span>
                  <span className="text-sm font-medium">{formatNumber(systemMetrics?.total_transactions || 0)}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-600">System Health</span>
                  <Badge variant="secondary" className="bg-green-100 text-green-700">
                    Excellent
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Recent Activity */}
        <Card className="mt-8 shadow-lg border-slate-200">
          <CardHeader>
            <CardTitle className="text-lg font-semibold text-slate-900">Recent Activity</CardTitle>
            <CardDescription>Latest system events and user actions</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center space-x-3 p-3 bg-green-50 rounded-lg">
                <CheckCircle className="h-4 w-4 text-green-500" />
                <div>
                  <p className="text-sm font-medium text-slate-900">New user registered</p>
                  <p className="text-xs text-slate-500">Sarah Thompson joined as Investor</p>
                </div>
                <span className="text-xs text-slate-400 ml-auto">2 min ago</span>
              </div>
              <div className="flex items-center space-x-3 p-3 bg-blue-50 rounded-lg">
                <BarChart3 className="h-4 w-4 text-blue-500" />
                <div>
                  <p className="text-sm font-medium text-slate-900">Data sync completed</p>
                  <p className="text-xs text-slate-500">DLD transactions updated successfully</p>
                </div>
                <span className="text-xs text-slate-400 ml-auto">5 min ago</span>
              </div>
              <div className="flex items-center space-x-3 p-3 bg-purple-50 rounded-lg">
                <Settings className="h-4 w-4 text-purple-500" />
                <div>
                  <p className="text-sm font-medium text-slate-900">System configuration updated</p>
                  <p className="text-xs text-slate-500">Rate limiting rules modified</p>
                </div>
                <span className="text-xs text-slate-400 ml-auto">10 min ago</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
} 