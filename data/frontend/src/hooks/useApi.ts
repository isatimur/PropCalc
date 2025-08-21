import { useState, useEffect } from 'react';
import realDataApi, { MarketOverview, Project, DLDTransaction, PaginatedResponse } from '@/lib/api';

// Real data hooks
export const useRealMarketData = () => {
  const [marketData, setMarketData] = useState<MarketOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchRealMarketData = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await realDataApi.getRealMarketOverview();
        setMarketData(data);
      } catch (err) {
        console.error('Failed to fetch real market data:', err);
        setError('Failed to load real market data');
      } finally {
        setLoading(false);
      }
    };

    fetchRealMarketData();
  }, []);

  return { marketData, loading, error };
};

// Legacy hook for backward compatibility
export const useMarketOverview = () => {
  const { marketData, loading, error } = useRealMarketData();
  return { data: marketData, loading, error };
};

export const useRealProjects = (limit = 10, offset = 0) => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);
  const [hasMore, setHasMore] = useState(false);

  useEffect(() => {
    const fetchRealProjects = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await realDataApi.getRealProjects(limit, offset);
        setProjects(data.projects || []);
        setTotal(data.total);
        setHasMore(data.has_more || false);
      } catch (err) {
        console.error('Failed to fetch real projects:', err);
        setError('Failed to load real projects');
      } finally {
        setLoading(false);
      }
    };

    fetchRealProjects();
  }, [limit, offset]);

  return { projects, loading, error, total, hasMore };
};

export const useRealVantageScoreStats = () => {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchRealVantageScoreStats = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await realDataApi.getRealVantageScoreStats();
        setStats(data);
      } catch (err) {
        console.error('Failed to fetch real Vantage Score stats:', err);
        setError('Failed to load real Vantage Score statistics');
      } finally {
        setLoading(false);
      }
    };

    fetchRealVantageScoreStats();
  }, []);

  return { stats, loading, error };
};

export const useRealDataQuality = () => {
  const [quality, setQuality] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchRealDataQuality = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await realDataApi.getRealDataQuality();
        setQuality(data);
      } catch (err) {
        console.error('Failed to fetch real data quality:', err);
        setError('Failed to load real data quality metrics');
      } finally {
        setLoading(false);
      }
    };

    fetchRealDataQuality();
  }, []);

  return { quality, loading, error };
};

export const useRealProject = (projectId: string) => {
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!projectId) {
      setLoading(false);
      return;
    }

    const fetchRealProject = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await realDataApi.getRealProject(projectId);
        setProject(data);
      } catch (err) {
        console.error('Failed to fetch real project:', err);
        setError('Failed to load real project data');
      } finally {
        setLoading(false);
      }
    };

    fetchRealProject();
  }, [projectId]);

  return { project, loading, error };
};

export const useRealMarketTrends = () => {
  const [trends, setTrends] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchRealMarketTrends = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await realDataApi.getRealMarketTrends();
        setTrends(data);
      } catch (err) {
        console.error('Failed to fetch real market trends:', err);
        setError('Failed to load real market trends');
      } finally {
        setLoading(false);
      }
    };

    fetchRealMarketTrends();
  }, []);

  return { trends, loading, error };
};

// Legacy hooks for backward compatibility
export const useProjects = (limit = 10, offset = 0) => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await realDataApi.getProjects(limit, offset);
        setProjects(data.projects || []);
        setTotal(data.total);
      } catch (err) {
        console.error('Failed to fetch projects:', err);
        setError('Failed to load projects');
      } finally {
        setLoading(false);
      }
    };

    fetchProjects();
  }, [limit, offset]);

  return { projects, loading, error, total };
};

export const useDLDProjects = (limit = 10, offset = 0) => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    const fetchDLDProjects = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await realDataApi.getDLDProjects(limit, offset);
        setProjects(data.projects || []);
        setTotal(data.total);
      } catch (err) {
        console.error('Failed to fetch DLD projects:', err);
        setError('Failed to load DLD projects');
      } finally {
        setLoading(false);
      }
    };

    fetchDLDProjects();
  }, [limit, offset]);

  return { projects, loading, error, total };
};

export const useDLDTransactions = (limit = 10, offset = 0) => {
  const [transactions, setTransactions] = useState<DLDTransaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    const fetchDLDTransactions = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await realDataApi.getDLDTransactions(limit, offset);
        setTransactions(data.transactions || []);
        setTotal(data.total);
      } catch (err) {
        console.error('Failed to fetch DLD transactions:', err);
        setError('Failed to load DLD transactions');
      } finally {
        setLoading(false);
      }
    };

    fetchDLDTransactions();
  }, [limit, offset]);

  return { transactions, loading, error, total };
};

export const useDLDMarketStats = () => {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDLDMarketStats = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await realDataApi.getDLDMarketStats();
        setStats(data);
      } catch (err) {
        console.error('Failed to fetch DLD market stats:', err);
        setError('Failed to load DLD market statistics');
      } finally {
        setLoading(false);
      }
    };

    fetchDLDMarketStats();
  }, []);

  return { stats, loading, error };
};

export const useRealDLDHealth = () => {
  const [health, setHealth] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchRealDLDHealth = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await realDataApi.getRealDLDHealth();
        setHealth(data);
      } catch (err) {
        console.error('Failed to fetch real DLD health:', err);
        setError('Failed to load real DLD health status');
      } finally {
        setLoading(false);
      }
    };

    fetchRealDLDHealth();
  }, []);

  return { health, loading, error };
};

export const useComprehensiveAnalytics = () => {
  const [analytics, setAnalytics] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchComprehensiveAnalytics = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await realDataApi.getComprehensiveAnalytics();
        setAnalytics(data);
      } catch (err) {
        console.error('Failed to fetch comprehensive analytics:', err);
        setError('Failed to load comprehensive analytics');
      } finally {
        setLoading(false);
      }
    };

    fetchComprehensiveAnalytics();
  }, []);

  return { analytics, loading, error };
};

export const usePipelineStatus = () => {
  const [status, setStatus] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPipelineStatus = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await realDataApi.getPipelineStatus();
        setStatus(data);
      } catch (err) {
        console.error('Failed to fetch pipeline status:', err);
        setError('Failed to load pipeline status');
      } finally {
        setLoading(false);
      }
    };

    fetchPipelineStatus();
  }, []);

  return { status, loading, error };
};

export const useRealtimeStatus = () => {
  const [status, setStatus] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchRealtimeStatus = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await realDataApi.getRealtimeStatus();
        setStatus(data);
      } catch (err) {
        console.error('Failed to fetch realtime status:', err);
        setError('Failed to load realtime status');
      } finally {
        setLoading(false);
      }
    };

    fetchRealtimeStatus();
  }, []);

  return { status, loading, error };
}; 