'use client';

import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { 
  BarChart3, 
  MapPin, 
  Building2, 
  TrendingUp,
  Database,
  FileText
} from "lucide-react";

export default function Home() {
  return (
    <div className="container mx-auto p-6">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          PropCalc - Real Estate Analytics Platform
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Advanced analytics and insights for Dubai real estate market
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* DLD Analytics */}
        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <div className="flex items-center space-x-2">
              <BarChart3 className="h-6 w-6 text-blue-600" />
              <CardTitle>DLD Analytics</CardTitle>
            </div>
            <CardDescription>
              Comprehensive analysis of Dubai Land Department transactions
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="text-sm text-gray-600">
                • 1.5M+ transactions analyzed<br/>
                • 257 unique locations<br/>
                • 205 developers<br/>
                • Real-time insights
              </div>
              <Link href="/dld-analytics">
                <Button className="w-full">
                  View Analytics
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>

        {/* Market Analysis */}
        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <div className="flex items-center space-x-2">
              <TrendingUp className="h-6 w-6 text-green-600" />
              <CardTitle>Market Analysis</CardTitle>
            </div>
            <CardDescription>
              Market trends and performance indicators
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="text-sm text-gray-600">
                • Price trends<br/>
                • Market performance<br/>
                • Investment opportunities<br/>
                • Risk assessment
              </div>
              <Link href="/market-analysis">
                <Button className="w-full" variant="outline">
                  View Analysis
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>

        {/* KML Viewer */}
        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <div className="flex items-center space-x-2">
              <MapPin className="h-6 w-6 text-red-600" />
              <CardTitle>KML Viewer</CardTitle>
            </div>
            <CardDescription>
              Geographic data visualization and mapping
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="text-sm text-gray-600">
                • Geographic boundaries<br/>
                • Area analysis<br/>
                • Location intelligence<br/>
                • Interactive maps
              </div>
              <Link href="/kml-viewer">
                <Button className="w-full" variant="outline">
                  View Maps
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>

        {/* Developers Database */}
        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <div className="flex items-center space-x-2">
              <Building2 className="h-6 w-6 text-purple-600" />
              <CardTitle>Developers</CardTitle>
            </div>
            <CardDescription>
              Comprehensive developer database and insights
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="text-sm text-gray-600">
                • 40+ Dubai developers<br/>
                • Performance metrics<br/>
                • Project portfolios<br/>
                • Contact information
              </div>
              <Link href="/developers">
                <Button className="w-full" variant="outline">
                  View Developers
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>

        {/* Data Sources */}
        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <div className="flex items-center space-x-2">
              <Database className="h-6 w-6 text-orange-600" />
              <CardTitle>Data Sources</CardTitle>
            </div>
            <CardDescription>
              Real-time data integration and management
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="text-sm text-gray-600">
                • DLD integration<br/>
                • KML processing<br/>
                • Real-time updates<br/>
                • Data validation
              </div>
              <Link href="/data-sources">
                <Button className="w-full" variant="outline">
                  View Sources
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>

        {/* Reports */}
        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <div className="flex items-center space-x-2">
              <FileText className="h-6 w-6 text-indigo-600" />
              <CardTitle>Reports</CardTitle>
            </div>
            <CardDescription>
              Detailed reports and documentation
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="text-sm text-gray-600">
                • Analytics reports<br/>
                • Market insights<br/>
                • Technical documentation<br/>
                • API documentation
              </div>
              <Link href="/reports">
                <Button className="w-full" variant="outline">
                  View Reports
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Stats */}
      <div className="mt-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Platform Overview</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-blue-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">1.5M+</div>
            <div className="text-sm text-gray-600">Transactions Analyzed</div>
          </div>
          <div className="bg-green-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-green-600">257</div>
            <div className="text-sm text-gray-600">Unique Locations</div>
          </div>
          <div className="bg-purple-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-purple-600">205</div>
            <div className="text-sm text-gray-600">Developers</div>
          </div>
          <div className="bg-orange-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-orange-600">5.9B</div>
            <div className="text-sm text-gray-600">AED Total Value</div>
          </div>
        </div>
      </div>
    </div>
  );
}
