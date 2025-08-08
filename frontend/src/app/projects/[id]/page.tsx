'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';

interface ProjectDetail {
  id: number;
  name: string;
  developer: {
    name: string;
    track_record_score: number;
    completed_projects: number;
    average_delay_days: number;
  };
  vantage_score: number;
  score_breakdown: {
    developer_track_record: number;
    sales_velocity: number;
    location_potential: number;
    project_quality_proxy: number;
    social_sentiment: number;
  };
  transparency_data: {
    sales_progress: Array<{
      date: string;
      units_sold: number;
      total_units: number;
      percentage: number;
    }>;
    construction_updates: Array<{
      date: string;
      progress_percentage: number;
      description: string;
      status: string;
    }>;
    satellite_images: Array<{
      date: string;
      image_url: string;
      description: string;
    }>;
  };
  risk_factors: Array<{
    category: string;
    description: string;
    severity: 'low' | 'medium' | 'high';
  }>;
  recommendations: Array<{
    type: 'buy' | 'hold' | 'sell' | 'monitor';
    description: string;
    reasoning: string;
  }>;
  market_comparison: {
    similar_projects: Array<{
      name: string;
      vantage_score: number;
      price_per_sqft: number;
      location: string;
    }>;
    market_position: string;
  };
}

export default function ProjectDetail() {
  const params = useParams();
  const [project, setProject] = useState<ProjectDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    // Simulate API call for demo
    setTimeout(() => {
      setProject({
        id: parseInt(params.id as string),
        name: "Marina Heights",
        developer: {
          name: "Emaar Properties",
          track_record_score: 92,
          completed_projects: 45,
          average_delay_days: 15
        },
        vantage_score: 87,
        score_breakdown: {
          developer_track_record: 92,
          sales_velocity: 85,
          location_potential: 90,
          project_quality_proxy: 88,
          social_sentiment: 82
        },
        transparency_data: {
          sales_progress: [
            { date: "2024-01", units_sold: 150, total_units: 300, percentage: 50 },
            { date: "2024-02", units_sold: 180, total_units: 300, percentage: 60 },
            { date: "2024-03", units_sold: 210, total_units: 300, percentage: 70 },
            { date: "2024-04", units_sold: 240, total_units: 300, percentage: 80 }
          ],
          construction_updates: [
            { date: "2024-01-15", progress_percentage: 25, description: "Foundation completed", status: "on_track" },
            { date: "2024-02-15", progress_percentage: 45, description: "Structure 50% complete", status: "on_track" },
            { date: "2024-03-15", progress_percentage: 65, description: "MEP installation started", status: "on_track" },
            { date: "2024-04-15", progress_percentage: 80, description: "Interior finishing", status: "on_track" }
          ],
          satellite_images: [
            { date: "2024-01-01", image_url: "/api/satellite/1", description: "Site preparation" },
            { date: "2024-02-01", image_url: "/api/satellite/2", description: "Foundation work" },
            { date: "2024-03-01", image_url: "/api/satellite/3", description: "Structure rising" },
            { date: "2024-04-01", image_url: "/api/satellite/4", description: "Near completion" }
          ]
        },
        risk_factors: [
          { category: "Construction", description: "Potential delays due to material shortages", severity: "medium" },
          { category: "Market", description: "Interest rate fluctuations affecting demand", severity: "low" },
          { category: "Developer", description: "Strong track record reduces risk", severity: "low" }
        ],
        recommendations: [
          { type: "buy", description: "Strong buy recommendation", reasoning: "Excellent developer track record and strong sales velocity" },
          { type: "monitor", description: "Monitor construction progress", reasoning: "Regular updates show consistent progress" }
        ],
        market_comparison: {
          similar_projects: [
            { name: "Downtown Elite", vantage_score: 84, price_per_sqft: 1200, location: "Downtown Dubai" },
            { name: "Palm Vista", vantage_score: 73, price_per_sqft: 950, location: "Palm Jumeirah" },
            { name: "Marina Heights", vantage_score: 87, price_per_sqft: 1100, location: "Dubai Marina" }
          ],
          market_position: "Premium segment with strong competitive advantage"
        }
      });
      setLoading(false);
    }, 1000);
  }, [params.id]);

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high': return 'text-red-600 bg-red-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'low': return 'text-green-600 bg-green-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getRecommendationColor = (type: string) => {
    switch (type) {
      case 'buy': return 'text-green-600 bg-green-100';
      case 'hold': return 'text-yellow-600 bg-yellow-100';
      case 'sell': return 'text-red-600 bg-red-100';
      case 'monitor': return 'text-blue-600 bg-blue-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-xl text-gray-600">Loading project analysis...</p>
        </div>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Project Not Found</h2>
          <Link href="/" className="text-blue-600 hover:text-blue-700">Return to Home</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <Link href="/" className="text-blue-600 hover:text-blue-700 mr-4">
                ← Back to Home
              </Link>
              <h1 className="text-3xl font-bold text-gray-900">{project.name}</h1>
            </div>
            <div className="text-right">
              <div className={`text-3xl font-bold ${getScoreColor(project.vantage_score)}`}>
                Vantage Score: {project.vantage_score}
              </div>
              <div className="text-sm text-gray-600">Trust Protocol Analysis</div>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8">
            {[
              { id: 'overview', label: 'Overview' },
              { id: 'transparency', label: 'Transparency' },
              { id: 'analysis', label: 'Risk Analysis' },
              { id: 'comparison', label: 'Market Comparison' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'overview' && (
          <div className="space-y-8">
            {/* Developer Information */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Developer Analysis</h2>
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">{project.developer.name}</h3>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Track Record Score:</span>
                      <span className="font-semibold">{project.developer.track_record_score}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Completed Projects:</span>
                      <span className="font-semibold">{project.developer.completed_projects}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Average Delay:</span>
                      <span className="font-semibold">{project.developer.average_delay_days} days</span>
                    </div>
                  </div>
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Vantage Score Breakdown</h3>
                  <div className="space-y-2">
                    {Object.entries(project.score_breakdown).map(([key, value]) => (
                      <div key={key} className="flex justify-between">
                        <span className="text-gray-600 capitalize">{key.replace(/_/g, ' ')}:</span>
                        <span className="font-semibold">{value}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Recommendations */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Investment Recommendations</h2>
              <div className="space-y-4">
                {project.recommendations.map((rec, index) => (
                  <div key={index} className="flex items-start space-x-3">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${getRecommendationColor(rec.type)}`}>
                      {rec.type.toUpperCase()}
                    </span>
                    <div>
                      <p className="font-semibold text-gray-900">{rec.description}</p>
                      <p className="text-sm text-gray-600">{rec.reasoning}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'transparency' && (
          <div className="space-y-8">
            {/* Sales Progress */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Sales Progress</h2>
              <div className="space-y-4">
                {project.transparency_data.sales_progress.map((progress, index) => (
                  <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded">
                    <div>
                      <div className="font-semibold">{progress.date}</div>
                      <div className="text-sm text-gray-600">
                        {progress.units_sold} / {progress.total_units} units sold
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-blue-600">{progress.percentage}%</div>
                      <div className="w-32 bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-blue-600 h-2 rounded-full" 
                          style={{ width: `${progress.percentage}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Construction Updates */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Construction Progress</h2>
              <div className="space-y-4">
                {project.transparency_data.construction_updates.map((update, index) => (
                  <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded">
                    <div>
                      <div className="font-semibold">{update.date}</div>
                      <div className="text-sm text-gray-600">{update.description}</div>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-green-600">{update.progress_percentage}%</div>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        update.status === 'on_track' ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'
                      }`}>
                        {update.status.replace('_', ' ')}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'analysis' && (
          <div className="space-y-8">
            {/* Risk Factors */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Risk Analysis</h2>
              <div className="space-y-4">
                {project.risk_factors.map((risk, index) => (
                  <div key={index} className="flex items-start space-x-3 p-4 bg-gray-50 rounded">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${getSeverityColor(risk.severity)}`}>
                      {risk.severity.toUpperCase()}
                    </span>
                    <div>
                      <p className="font-semibold text-gray-900">{risk.category}</p>
                      <p className="text-sm text-gray-600">{risk.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'comparison' && (
          <div className="space-y-8">
            {/* Market Comparison */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Market Comparison</h2>
              <div className="mb-4">
                <p className="text-gray-600">{project.market_comparison.market_position}</p>
              </div>
              <div className="space-y-4">
                {project.market_comparison.similar_projects.map((similar, index) => (
                  <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded">
                    <div>
                      <div className="font-semibold">{similar.name}</div>
                      <div className="text-sm text-gray-600">{similar.location}</div>
                    </div>
                    <div className="text-right">
                      <div className={`text-xl font-bold ${getScoreColor(similar.vantage_score)}`}>
                        {similar.vantage_score}
                      </div>
                      <div className="text-sm text-gray-600">${similar.price_per_sqft}/sqft</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
