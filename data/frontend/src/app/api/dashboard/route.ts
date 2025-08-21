import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const timeframe = searchParams.get('timeframe') || '30d';

    console.log('Dashboard API called with timeframe:', timeframe);

    // Create a simple mock response for now to test the frontend
    const dashboardData = {
      market_overview: {
        total_projects: 8,
        active_projects: 8,
        average_score: 50,
        market_confidence: 'Medium',
        total_investment_value: '$15.2B',
        high_confidence_projects: 6,
        confidence_percentage: 65
      },
      top_performers: [
        {
          project_name: 'Burj Vista 2',
          vantage_score: 85,
          developer_name: 'Emaar Properties',
          location: 'Downtown Dubai',
          price_range: 'Luxury'
        },
        {
          project_name: 'Palm Jumeirah Vista',
          vantage_score: 78,
          developer_name: 'Nakheel',
          location: 'Palm Jumeirah',
          price_range: 'Ultra Luxury'
        },
        {
          project_name: 'Sobha Hartland 2',
          vantage_score: 88,
          developer_name: 'Sobha Realty',
          location: 'Mohammed Bin Rashid City',
          price_range: 'Premium'
        },
        {
          project_name: 'Bluewaters Residences',
          vantage_score: 75,
          developer_name: 'Meraas',
          location: 'Bluewaters Island',
          price_range: 'Luxury'
        },
        {
          project_name: 'Dubai Hills Estate',
          vantage_score: 82,
          developer_name: 'Emaar Properties',
          location: 'Dubai Hills',
          price_range: 'Premium'
        }
      ],
      risk_zones: [
        {
          area: 'Dubai South',
          risk_level: 'Medium',
          affected_projects: 3,
          average_score: 45,
          reasons: ['Infrastructure delays', 'Market saturation']
        },
        {
          area: 'Dubai Creek Harbour',
          risk_level: 'Low',
          affected_projects: 2,
          average_score: 75,
          reasons: ['Strong developer track record']
        },
        {
          area: 'Dubai Hills Estate',
          risk_level: 'Low',
          affected_projects: 1,
          average_score: 82,
          reasons: ['High demand area']
        }
      ],
      recent_updates: [
        {
          id: 1,
          project_name: 'Burj Vista 2',
          score_change: 5,
          change_percentage: 10,
          timestamp: new Date().toISOString()
        },
        {
          id: 2,
          project_name: 'Palm Jumeirah Vista',
          score_change: -2,
          change_percentage: -4,
          timestamp: new Date(Date.now() - 86400000).toISOString()
        },
        {
          id: 3,
          project_name: 'Damac Hills 2',
          score_change: 3,
          change_percentage: 6,
          timestamp: new Date(Date.now() - 172800000).toISOString()
        }
      ],
      market_trends: {
        score_trend: 'up',
        trend_percentage: 5.2,
        data_points: [
          { date: '2024-01', average_score: 48, project_count: 6 },
          { date: '2024-02', average_score: 52, project_count: 7 },
          { date: '2024-03', average_score: 50, project_count: 8 }
        ]
      }
    };

    console.log('Dashboard data prepared successfully');
    return NextResponse.json(dashboardData);
  } catch (error) {
    console.error('Dashboard API error:', error);
    return NextResponse.json(
      { error: `Failed to fetch dashboard data: ${error instanceof Error ? error.message : 'Unknown error'}` },
      { status: 500 }
    );
  }
} 