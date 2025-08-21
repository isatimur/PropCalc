import { NextRequest, NextResponse } from 'next/server';

// Force dynamic rendering
export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  try {
    // Get the backend URL - use the internal Docker network name when running in containers
    const backendUrl = 'http://backend:8000';
    
    // Extract query parameters from the request
    const { searchParams } = new URL(request.url);
    const area_id = searchParams.get('area_id');
    const limit = searchParams.get('limit');
    
    // Build the backend URL with query parameters
    const backendEndpoint = `${backendUrl}/api/v1/analytics/dld/full-report`;
    const url = new URL(backendEndpoint);
    
    if (area_id) {
      url.searchParams.append('area_id', area_id);
    }
    if (limit) {
      url.searchParams.append('limit', limit);
    }
    
    console.log('Proxying request to:', url.toString());
    
    // Make the request to the backend
    const response = await fetch(url.toString(), {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        // Forward any authorization headers if present
        ...(request.headers.get('authorization') && {
          'authorization': request.headers.get('authorization')!
        })
      },
      // Add timeout
      signal: AbortSignal.timeout(30000) // 30 second timeout
    });
    
    if (!response.ok) {
      console.error('Backend response error:', response.status, response.statusText);
      return NextResponse.json(
        { 
          error: 'Backend request failed', 
          status: response.status,
          message: response.statusText 
        },
        { status: response.status }
      );
    }
    
    const data = await response.json();
    
    console.log('Successfully proxied DLD full report request');
    
    // Return the data with proper headers
    return NextResponse.json(data, {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
      }
    });
    
  } catch (error) {
    console.error('Error proxying DLD full report request:', error);
    
    // Handle different types of errors
    if (error instanceof TypeError && error.message.includes('fetch')) {
      return NextResponse.json(
        { 
          error: 'Backend connection failed',
          message: 'Unable to connect to the backend service',
          details: error.message
        },
        { status: 503 }
      );
    }
    
    if (error instanceof Error && error.name === 'AbortError') {
      return NextResponse.json(
        { 
          error: 'Request timeout',
          message: 'Backend request timed out'
        },
        { status: 504 }
      );
    }
    
    return NextResponse.json(
      { 
        error: 'Internal server error',
        message: 'An unexpected error occurred while processing the request',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}

// Optional: Add other HTTP methods if needed
export async function OPTIONS(request: NextRequest) {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  });
}
