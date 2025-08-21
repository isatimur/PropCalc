'use client';

import { useState, useEffect } from 'react';

export default function TestPage() {
  const [healthStatus, setHealthStatus] = useState<string>('Loading...');
  const [projectsStatus, setProjectsStatus] = useState<string>('Loading...');
  const [error, setError] = useState<string>('');

  useEffect(() => {
    // Test health endpoint
    fetch('http://localhost:8001/')
      .then(response => response.json())
      .then(data => {
        setHealthStatus(JSON.stringify(data, null, 2));
      })
      .catch(err => {
        setHealthStatus(`Error: ${err.message}`);
        setError(err.message);
      });

    // Test projects endpoint
    fetch('http://localhost:8001/api/v1/projects')
      .then(response => response.json())
      .then(data => {
        setProjectsStatus(JSON.stringify(data, null, 2));
      })
      .catch(err => {
        setProjectsStatus(`Error: ${err.message}`);
        setError(err.message);
      });
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">API Test Page</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">Health Endpoint</h2>
            <pre className="bg-gray-100 p-4 rounded text-sm overflow-auto">
              {healthStatus}
            </pre>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">Projects Endpoint</h2>
            <pre className="bg-gray-100 p-4 rounded text-sm overflow-auto">
              {projectsStatus}
            </pre>
          </div>
        </div>

        {error && (
          <div className="mt-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-red-800 mb-2">Error Details</h3>
            <p className="text-red-700">{error}</p>
          </div>
        )}
      </div>
    </div>
  );
} 