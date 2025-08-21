import React from 'react'
import { render, screen } from '@testing-library/react'
import Dashboard from '../Dashboard'

// Mock the API hooks
jest.mock('@/hooks/useApi', () => ({
  useRealMarketData: () => ({
    marketData: {
      total_projects: 100,
      total_units: 5000,
      active_developers: 25,
      avg_price_per_sqft: 1200,
      sales_percentage: 75
    },
    loading: false,
    error: null
  }),
  useRealProjects: () => ({
    projects: [
      {
        id: '1',
        name: 'Test Project',
        developer_name: 'Test Developer',
        location: 'Test Location',
        price_aed: 1500000,
        area_sqft: 1200
      }
    ],
    loading: false,
    error: null,
    total: 1,
    hasMore: false
  }),
  useRealVantageScoreStats: () => ({
    stats: {
      total_scores: 100,
      avg_score: 85,
      score_distribution: { high: 30, medium: 50, low: 20 }
    },
    loading: false,
    error: null
  }),
  useRealDataQuality: () => ({
    quality: {
      completeness: 95,
      accuracy: 92,
      timeliness: 88
    },
    loading: false,
    error: null
  }),
  useRealMarketTrends: () => ({
    trends: {
      price_trend: 'up',
      volume_trend: 'stable',
      sentiment: 'positive'
    },
    loading: false,
    error: null
  })
}))

describe('Dashboard Component', () => {
  it('renders dashboard title', () => {
    render(<Dashboard />)
    expect(screen.getByText('PropCalc Dashboard')).toBeInTheDocument()
  })

  it('renders market data section', () => {
    render(<Dashboard />)
    expect(screen.getByText('Real-time Dubai real estate analytics')).toBeInTheDocument()
  })

  it('renders projects section', () => {
    render(<Dashboard />)
    expect(screen.getByText('Test Project')).toBeInTheDocument()
    expect(screen.getByText('Test Developer')).toBeInTheDocument()
  })

  it('renders analytics cards', () => {
    render(<Dashboard />)
    expect(screen.getByText('100')).toBeInTheDocument() // Total projects
    expect(screen.getByText('5000')).toBeInTheDocument() // Total units
    expect(screen.getByText('25')).toBeInTheDocument() // Active developers
  })

  it('handles loading state', () => {
    // Mock loading state
    jest.doMock('@/hooks/useApi', () => ({
      useRealMarketData: () => ({ marketData: null, loading: true, error: null }),
      useRealProjects: () => ({ projects: [], loading: true, error: null, total: 0, hasMore: false }),
      useRealVantageScoreStats: () => ({ stats: null, loading: true, error: null }),
      useRealDataQuality: () => ({ quality: null, loading: true, error: null }),
      useRealMarketTrends: () => ({ trends: null, loading: true, error: null })
    }))

    render(<Dashboard />)
    expect(screen.getByText('Loading real data...')).toBeInTheDocument()
  })

  it('handles error state', () => {
    // Mock error state
    jest.doMock('@/hooks/useApi', () => ({
      useRealMarketData: () => ({ marketData: null, loading: false, error: 'Failed to load data' }),
      useRealProjects: () => ({ projects: [], loading: false, error: null, total: 0, hasMore: false }),
      useRealVantageScoreStats: () => ({ stats: null, loading: false, error: null }),
      useRealDataQuality: () => ({ quality: null, loading: false, error: null }),
      useRealMarketTrends: () => ({ trends: null, loading: false, error: null })
    }))

    render(<Dashboard />)
    expect(screen.getByText('Error Loading Data')).toBeInTheDocument()
    expect(screen.getByText('Failed to load data')).toBeInTheDocument()
  })
})
