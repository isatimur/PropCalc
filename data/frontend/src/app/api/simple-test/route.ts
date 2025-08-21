import { NextRequest, NextResponse } from 'next/server';
import axios from 'axios';

// Force dynamic rendering
export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  try {
    console.log('Simple test starting...');
    
    // Test with IP address instead of hostname
    const response = await axios.get('http://172.20.0.6:8000/health');
    console.log('Response status:', response.status);
    
    const data = response.data;
    console.log('Response data:', data);
    
    return NextResponse.json({
      status: 'success',
      message: 'Backend connection successful',
      data: data,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('Simple test error:', error);
    return NextResponse.json({
      status: 'error',
      message: error instanceof Error ? error.message : 'Unknown error',
      timestamp: new Date().toISOString()
    });
  }
} 