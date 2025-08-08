'use client';

import { useState, useEffect } from 'react';
import apiClient from '@/lib/api';

export default function TestIntegration() {
  const [marketData, setMarketData] = useState<any>(null);
  const [projectsData, setProjectsData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const testIntegration = async () => {
      try {
        setLoading(true);
        setError(null);

        // Test market overview
        const marketOverview = await apiClient.getMarketOverview();
        setMarketData(marketOverview);

        // Test projects
        const projects = await apiClient.getProjects(5, 0);
        setProjectsData(projects);

      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    testIntegration();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Testing frontend-backend integration...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            <h2 className="text-xl font-bold mb-2">Integration Test Failed</h2>
            <p className="text-sm">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Frontend-Backend Integration Test</h1>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Market Overview */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">Market Overview</h2>
            <pre className="bg-gray-100 p-4 rounded text-sm overflow-auto">
              {JSON.stringify(marketData, null, 2)}
            </pre>
          </div>

          {/* Projects */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">Projects (First 5)</h2>
            <pre className="bg-gray-100 p-4 rounded text-sm overflow-auto">
              {JSON.stringify(projectsData, null, 2)}
            </pre>
          </div>
        </div>

        <div className="mt-8 bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
          <h2 className="text-xl font-bold mb-2">✅ Integration Test Successful!</h2>
          <p className="text-sm">
            The frontend is successfully communicating with the backend API.
            Both market overview and projects endpoints are working correctly.
          </p>
        </div>
      </div>
    </div>
  );
} 