import { NextRequest, NextResponse } from 'next/server';
import axios from 'axios';

// Force dynamic rendering
export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  try {
    const backendUrl = 'http://backend:8000';
    console.log('Testing backend connection to:', backendUrl);
    
    // Test health endpoint
    console.log('Testing health endpoint...');
    const healthResponse = await axios.get(`${backendUrl}/health`);
    console.log('Health response status:', healthResponse.status);
    
    const healthData = healthResponse.data;
    console.log('Health data:', healthData);
    
    // Test market overview
    console.log('Testing market overview...');
    const marketResponse = await axios.get(`${backendUrl}/api/v1/demo/market/overview`);
    console.log('Market response status:', marketResponse.status);
    
    const marketData = marketResponse.data;
    console.log('Market data keys:', Object.keys(marketData));
    
    // Test projects
    console.log('Testing projects...');
    const projectsResponse = await axios.get(`${backendUrl}/api/v1/demo/projects?limit=3`);
    console.log('Projects response status:', projectsResponse.status);
    
    const projectsData = projectsResponse.data;
    console.log('Projects data keys:', Object.keys(projectsData));
    
    // Test Vantage Score stats
    console.log('Testing Vantage Score stats...');
    const vantageResponse = await axios.get(`${backendUrl}/api/v1/demo/vantage-score/stats`);
    console.log('Vantage response status:', vantageResponse.status);
    
    const vantageData = vantageResponse.data;
    console.log('Vantage data keys:', Object.keys(vantageData));

    return NextResponse.json({
      status: 'success',
      timestamp: new Date().toISOString(),
      backend: {
        health: healthData,
        market: {
          total_transactions: marketData.total_transactions,
          average_price: marketData.average_price,
          market_sentiment: marketData.market_sentiment
        },
        projects: {
          count: projectsData.projects?.length || 0,
          total: projectsData.total,
          sample: projectsData.projects?.slice(0, 2).map((p: any) => p.name) || []
        },
        vantage_score: {
          total_transactions: vantageData.data?.total_transactions,
          average_price: vantageData.data?.average_price,
          data_source: vantageData.data?.data_source
        }
      }
    });
  } catch (error) {
    console.error('Backend test error:', error);
    return NextResponse.json({
      status: 'error',
      message: error instanceof Error ? error.message : 'Unknown error',
      timestamp: new Date().toISOString()
    });
  }
} 