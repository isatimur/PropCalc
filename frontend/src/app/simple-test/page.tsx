'use client';

import { useState, useEffect } from 'react';

export default function SimpleTest() {
  const [backendStatus, setBackendStatus] = useState<string>('Testing...');
  const [marketData, setMarketData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const testBackend = async () => {
      try {
        // Test basic backend health
        const healthResponse = await fetch('http://localhost:8001/');
        const healthData = await healthResponse.json();
        setBackendStatus(`Backend Health: ${healthData.status}`);

        // Test market overview
        const marketResponse = await fetch('http://localhost:8001/api/v1/demo/market/overview');
        const marketData = await marketResponse.json();
        setMarketData(marketData);
        setError(null);

      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
        setBackendStatus('Backend connection failed');
      }
    };

    testBackend();
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Simple Backend Test</h1>
        
        <div className="space-y-6">
          {/* Backend Status */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">Backend Status</h2>
            <p className="text-lg">{backendStatus}</p>
          </div>

          {/* Error Display */}
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
              <h2 className="text-xl font-bold mb-2">Error</h2>
              <p className="text-sm">{error}</p>
            </div>
          )}

          {/* Market Data */}
          {marketData && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold mb-4">Market Overview Data</h2>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Total Properties</p>
                  <p className="text-2xl font-bold">{marketData.total_properties?.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Total Transactions</p>
                  <p className="text-2xl font-bold">{marketData.total_transactions?.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Average Price</p>
                  <p className="text-2xl font-bold">AED {marketData.average_price?.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Market Sentiment</p>
                  <p className="text-2xl font-bold capitalize">{marketData.market_sentiment}</p>
                </div>
              </div>
            </div>
          )}

          {/* Success Message */}
          {marketData && !error && (
            <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
              <h2 className="text-xl font-bold mb-2">✅ Frontend-Backend Integration Successful!</h2>
              <p className="text-sm">
                The frontend is successfully communicating with the backend API.
                Market overview data is being fetched and displayed correctly.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
} 