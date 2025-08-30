import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import apiService from '../services/api';
import {
  CircleStackIcon,
  ArrowPathIcon,
  TrashIcon,
  ChartBarIcon,
  ClockIcon,
  ServerIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline';

interface CacheStats {
  cache_enabled: boolean;
  statistics: {
    cache_type: string;
    cache_enabled: boolean;
    cache_size?: number;
  };
  info: string;
  timestamp: string;
}

interface HealthResponse {
  status: string;
  service: string;
  version: string;
  timestamp: string;
  features: string[];
  cache?: {
    cache_type: string;
    cache_enabled: boolean;
    cache_size?: number;
  };
}

const CacheManagement: React.FC = () => {
  const { isAdmin } = useAuth();
  const [cacheStats, setCacheStats] = useState<CacheStats | null>(null);
  const [healthData, setHealthData] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null);
  const [clearingCache, setClearingCache] = useState(false);

  const fetchCacheStats = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Fetch cache status
      const cacheResponse = await apiService.getCacheStatus();
      setCacheStats(cacheResponse);
      
      // Fetch health data for additional cache info
      const healthResponse = await apiService.checkHealth();
      setHealthData(healthResponse);
      
      setLastRefresh(new Date());
    } catch (err: any) {
      setError(err.response?.data?.error || err.message || 'Failed to fetch cache status');
    } finally {
      setLoading(false);
    }
  };

  const clearCache = async () => {
    try {
      setClearingCache(true);
      const response = await apiService.clearCache();
      
      if (response.success) {
        // Refresh stats after clearing
        await fetchCacheStats();
      } else {
        setError(response.error || 'Failed to clear cache');
      }
    } catch (err: any) {
      setError(err.response?.data?.error || err.message || 'Failed to clear cache');
    } finally {
      setClearingCache(false);
    }
  };

  useEffect(() => {
    if (isAdmin) {
      fetchCacheStats();
      
      // Auto-refresh every 30 seconds
      const interval = setInterval(fetchCacheStats, 30000);
      return () => clearInterval(interval);
    }
  }, [isAdmin]);

  // Redirect if not admin
  if (!isAdmin) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <ExclamationTriangleIcon className="mx-auto h-12 w-12 text-red-500" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">Access Denied</h3>
          <p className="mt-1 text-sm text-gray-500">
            Cache management is only available to admin users.
          </p>
        </div>
      </div>
    );
  }

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="md:flex md:items-center md:justify-between">
        <div className="min-w-0 flex-1">
          <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:truncate sm:text-3xl sm:tracking-tight">
            <CircleStackIcon className="inline h-8 w-8 mr-3 text-blue-600" />
            Cache Management
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            Monitor and manage LangChain cache performance
          </p>
        </div>
        <div className="mt-4 flex md:ml-4 md:mt-0 space-x-3">
          <button
            onClick={fetchCacheStats}
            disabled={loading}
            className="inline-flex items-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 disabled:opacity-50"
          >
            <ArrowPathIcon className={`-ml-0.5 mr-1.5 h-5 w-5 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
          <button
            onClick={clearCache}
            disabled={clearingCache || !cacheStats?.cache_enabled}
            className="inline-flex items-center rounded-md bg-red-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-red-500 disabled:opacity-50"
          >
            <TrashIcon className="-ml-0.5 mr-1.5 h-5 w-5" />
            {clearingCache ? 'Clearing...' : 'Clear Cache'}
          </button>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="rounded-md bg-red-50 p-4">
          <div className="flex">
            <ExclamationTriangleIcon className="h-5 w-5 text-red-400" />
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Error</h3>
              <p className="mt-1 text-sm text-red-700">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Cache Status Cards */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {/* Cache Status */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                {cacheStats?.cache_enabled ? (
                  <CheckCircleIcon className="h-6 w-6 text-green-400" />
                ) : (
                  <ExclamationTriangleIcon className="h-6 w-6 text-red-400" />
                )}
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Cache Status</dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {cacheStats?.cache_enabled ? 'Enabled' : 'Disabled'}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        {/* Cache Type */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ServerIcon className="h-6 w-6 text-blue-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Cache Type</dt>
                  <dd className="text-lg font-medium text-gray-900 capitalize">
                    {cacheStats?.statistics?.cache_type || 'Unknown'}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        {/* Cache Size */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ChartBarIcon className="h-6 w-6 text-purple-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Cached Entries</dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {cacheStats?.statistics?.cache_size ?? 'N/A'}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        {/* Last Refresh */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ClockIcon className="h-6 w-6 text-yellow-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Last Refresh</dt>
                  <dd className="text-sm font-medium text-gray-900">
                    {lastRefresh ? lastRefresh.toLocaleTimeString() : 'Never'}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Detailed Information */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Cache Information */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
              Cache Information
            </h3>
            
            {cacheStats && (
              <div className="space-y-3">
                <div className="bg-gray-50 rounded-lg p-4">
                  <pre className="text-sm text-gray-700 whitespace-pre-wrap">
                    {cacheStats.info}
                  </pre>
                </div>
                
                <div className="text-xs text-gray-500">
                  Last updated: {formatTimestamp(cacheStats.timestamp)}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* System Health */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
              System Health
            </h3>
            
            {healthData && (
              <div className="space-y-4">
                <div className="flex justify-between">
                  <span className="text-sm font-medium text-gray-500">Service:</span>
                  <span className="text-sm text-gray-900">{healthData.service}</span>
                </div>
                
                <div className="flex justify-between">
                  <span className="text-sm font-medium text-gray-500">Version:</span>
                  <span className="text-sm text-gray-900">{healthData.version}</span>
                </div>
                
                <div className="flex justify-between">
                  <span className="text-sm font-medium text-gray-500">Status:</span>
                  <span className={`text-sm font-medium ${
                    healthData.status === 'ok' ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {healthData.status.toUpperCase()}
                  </span>
                </div>

                <div>
                  <span className="text-sm font-medium text-gray-500">Features:</span>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {healthData.features.map((feature) => (
                      <span
                        key={feature}
                        className="inline-flex items-center rounded-full bg-blue-100 px-2.5 py-0.5 text-xs font-medium text-blue-800"
                      >
                        {feature}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="text-xs text-gray-500">
                  Last checked: {formatTimestamp(healthData.timestamp)}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Performance Tips */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
            Cache Performance Tips
          </h3>
          
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
            <div>
              <h4 className="text-sm font-medium text-gray-900 mb-2">Benefits of Caching</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• 60-80% faster response times for similar queries</li>
                <li>• 70-80% reduction in API costs</li>
                <li>• Improved user experience with instant responses</li>
                <li>• Better system scalability</li>
              </ul>
            </div>
            
            <div>
              <h4 className="text-sm font-medium text-gray-900 mb-2">Optimization Recommendations</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Monitor cache hit rates regularly</li>
                <li>• Clear cache if responses become stale</li>
                <li>• Consider SQLite cache for persistence</li>
                <li>• Use auto-refresh for real-time monitoring</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CacheManagement;
