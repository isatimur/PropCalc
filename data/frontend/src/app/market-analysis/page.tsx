'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

interface MarketInsights {
  market_overview: {
    total_projects: number;
    average_score: number;
    market_confidence: string;
    total_investment_value: string;
    projects_under_construction: number;
  };
  top_performers: Array<{
    project_name: string;
    vantage_score: number;
    developer_name: string;
    location: string;
    price_range: string;
  }>;
  risk_zones: Array<{
    area: string;
    risk_level: string;
    reason: string;
    affected_projects: number;
  }>;
  developer_rankings: Array<{
    name: string;
    average_score: number;
    projects_count: number;
    track_record: number;
  }>;
  market_trends: {
    score_trend: 'up' | 'down' | 'stable';
    price_trend: 'up' | 'down' | 'stable';
    sales_velocity_trend: 'up' | 'down' | 'stable';
  };
}

export default function MarketAnalysis() {
  const [insights, setInsights] = useState<MarketInsights | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      setInsights({
        market_overview: {
          total_projects: 156,
          average_score: 78.5,
          market_confidence: 'High',
          total_investment_value: '$45.2B',
          projects_under_construction: 89
        },
        top_performers: [
          {
            project_name: 'Bluewaters Residences',
            vantage_score: 91.0,
            developer_name: 'Meraas',
            location: 'Bluewaters Island',
            price_range: '$1.5M - $2.2M'
          },
          {
            project_name: 'Burj Vista 2',
            vantage_score: 87.5,
            developer_name: 'Emaar Properties',
            location: 'Downtown Dubai',
            price_range: '$1.2M - $1.8M'
          },
          {
            project_name: 'Sobha Hartland 2',
            vantage_score: 84.0,
            developer_name: 'Sobha Realty',
            location: 'Mohammed Bin Rashid City',
            price_range: '$1.1M - $1.6M'
          }
        ],
        risk_zones: [
          {
            area: 'Dubai South',
            risk_level: 'Medium',
            reason: 'Infrastructure development delays',
            affected_projects: 12
          },
          {
            area: 'Dubai Creek Harbour',
            risk_level: 'Low',
            reason: 'Market saturation concerns',
            affected_projects: 8
          }
        ],
        developer_rankings: [
          {
            name: 'Emaar Properties',
            average_score: 87.2,
            projects_count: 15,
            track_record: 92.5
          },
          {
            name: 'Meraas',
            average_score: 85.8,
            projects_count: 8,
            track_record: 85.0
          },
          {
            name: 'Sobha Realty',
            average_score: 84.3,
            projects_count: 12,
            track_record: 88.0
          },
          {
            name: 'Nakheel',
            average_score: 72.1,
            projects_count: 22,
            track_record: 78.0
          },
          {
            name: 'Damac Properties',
            average_score: 58.5,
            projects_count: 18,
            track_record: 65.0
          }
        ],
        market_trends: {
          score_trend: 'up',
          price_trend: 'up',
          sales_velocity_trend: 'stable'
        }
      });
      setLoading(false);
    }, 1000);
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Analyzing market data...</p>
        </div>
      </div>
    );
  }

  if (!insights) return null;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Market Analysis</h1>
              <p className="text-gray-600 mt-1">From Speculation to Science</p>
            </div>
            <Link href="/" className="text-blue-600 hover:text-blue-800">
              ← Back to Dashboard
            </Link>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Market Overview */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Market Overview</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600">{insights.market_overview.total_projects}</div>
              <div className="text-sm text-gray-600">Total Projects</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600">{insights.market_overview.average_score}</div>
              <div className="text-sm text-gray-600">Average Vantage Score</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-600">{insights.market_overview.market_confidence}</div>
              <div className="text-sm text-gray-600">Market Confidence</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-orange-600">{insights.market_overview.total_investment_value}</div>
              <div className="text-sm text-gray-600">Total Investment Value</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-red-600">{insights.market_overview.projects_under_construction}</div>
              <div className="text-sm text-gray-600">Under Construction</div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Top Performers */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-xl font-bold text-gray-900 mb-4">Top Performing Projects</h3>
            <div className="space-y-4">
              {insights.top_performers.map((project, index) => (
                <div key={index} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex justify-between items-start">
                    <div>
                      <h4 className="font-semibold text-gray-900">{project.project_name}</h4>
                      <p className="text-sm text-gray-600">{project.developer_name}</p>
                      <p className="text-sm text-gray-500">{project.location}</p>
                      <p className="text-sm text-gray-500">{project.price_range}</p>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-green-600">{project.vantage_score}</div>
                      <div className="text-xs text-gray-500">Vantage Score</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Risk Zones */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-xl font-bold text-gray-900 mb-4">Risk Zones</h3>
            <div className="space-y-4">
              {insights.risk_zones.map((zone, index) => (
                <div key={index} className="border rounded-lg p-4">
                  <div className="flex justify-between items-start">
                    <div>
                      <h4 className="font-semibold text-gray-900">{zone.area}</h4>
                      <p className="text-sm text-gray-600">{zone.reason}</p>
                      <p className="text-sm text-gray-500">{zone.affected_projects} projects affected</p>
                    </div>
                    <div className="text-right">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                        zone.risk_level === 'High' ? 'bg-red-100 text-red-800' :
                        zone.risk_level === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-green-100 text-green-800'
                      }`}>
                        {zone.risk_level} Risk
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Developer Rankings */}
        <div className="bg-white rounded-lg shadow-lg p-6 mt-8">
          <h3 className="text-xl font-bold text-gray-900 mb-6">Developer Rankings</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-4 font-semibold text-gray-900">Developer</th>
                  <th className="text-center py-3 px-4 font-semibold text-gray-900">Avg Score</th>
                  <th className="text-center py-3 px-4 font-semibold text-gray-900">Projects</th>
                  <th className="text-center py-3 px-4 font-semibold text-gray-900">Track Record</th>
                </tr>
              </thead>
              <tbody>
                {insights.developer_rankings.map((developer, index) => (
                  <tr key={index} className="border-b hover:bg-gray-50">
                    <td className="py-4 px-4 font-medium text-gray-900">{developer.name}</td>
                    <td className="py-4 px-4 text-center">
                      <span className="font-semibold text-blue-600">{developer.average_score}</span>
                    </td>
                    <td className="py-4 px-4 text-center text-gray-600">{developer.projects_count}</td>
                    <td className="py-4 px-4 text-center">
                      <span className="font-semibold text-green-600">{developer.track_record}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Market Trends */}
        <div className="bg-white rounded-lg shadow-lg p-6 mt-8">
          <h3 className="text-xl font-bold text-gray-900 mb-6">Market Trends</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600 mb-2">Vantage Scores</div>
              <div className={`text-4xl ${insights.market_trends.score_trend === 'up' ? 'text-green-600' : insights.market_trends.score_trend === 'down' ? 'text-red-600' : 'text-gray-600'}`}>
                {insights.market_trends.score_trend === 'up' ? '↗' : insights.market_trends.score_trend === 'down' ? '↘' : '→'}
              </div>
              <div className="text-sm text-gray-600 mt-2">Trending {insights.market_trends.score_trend}</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600 mb-2">Property Prices</div>
              <div className={`text-4xl ${insights.market_trends.price_trend === 'up' ? 'text-green-600' : insights.market_trends.price_trend === 'down' ? 'text-red-600' : 'text-gray-600'}`}>
                {insights.market_trends.price_trend === 'up' ? '↗' : insights.market_trends.price_trend === 'down' ? '↘' : '→'}
              </div>
              <div className="text-sm text-gray-600 mt-2">Trending {insights.market_trends.price_trend}</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600 mb-2">Sales Velocity</div>
              <div className={`text-4xl ${insights.market_trends.sales_velocity_trend === 'up' ? 'text-green-600' : insights.market_trends.sales_velocity_trend === 'down' ? 'text-red-600' : 'text-gray-600'}`}>
                {insights.market_trends.sales_velocity_trend === 'up' ? '↗' : insights.market_trends.sales_velocity_trend === 'down' ? '↘' : '→'}
              </div>
              <div className="text-sm text-gray-600 mt-2">Trending {insights.market_trends.sales_velocity_trend}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 