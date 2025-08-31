import React, { useState, useEffect } from 'react';
import { Cog6ToothIcon, CheckCircleIcon, XCircleIcon, ClockIcon } from '@heroicons/react/24/outline';
import { apiService, HealthResponse } from '../services/api';

const SystemStatus: React.FC = () => {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastChecked, setLastChecked] = useState<Date | null>(null);

  const checkHealth = async () => {
    setLoading(true);
    try {
      const healthData = await apiService.checkHealth();
      setHealth(healthData);
      setLastChecked(new Date());
    } catch (error) {
      setHealth(null);
      setLastChecked(new Date());
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkHealth();
  }, []);

  const formatUptime = (timestamp: string) => {
    const now = new Date();
    const then = new Date(timestamp);
    const diffMs = now.getTime() - then.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    
    if (diffHours > 0) {
      return `${diffHours}h ${diffMins % 60}m`;
    }
    return `${diffMins}m`;
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">System Status</h1>
        <p className="text-gray-600">Monitor system health, API status, and service performance</p>
      </div>

      {/* Health Status Card */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-900 flex items-center">
            <Cog6ToothIcon className="h-6 w-6 mr-2" />
            API Service Status
          </h2>
          <button
            onClick={checkHealth}
            disabled={loading}
            className="btn-secondary disabled:opacity-50"
          >
            {loading ? 'Checking...' : 'Refresh Status'}
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="text-center p-4 rounded-lg border-2 border-dashed">
            <div className="flex items-center justify-center mb-2">
              {loading ? (
                <ClockIcon className="h-8 w-8 text-yellow-500 animate-spin" />
              ) : health ? (
                <CheckCircleIcon className="h-8 w-8 text-green-500" />
              ) : (
                <XCircleIcon className="h-8 w-8 text-red-500" />
              )}
            </div>
            <p className="font-semibold text-lg">
              {loading ? 'Checking...' : health ? 'Online' : 'Offline'}
            </p>
            <p className="text-sm text-gray-500">API Status</p>
          </div>

          <div className="text-center p-4 rounded-lg border-2 border-dashed">
            <p className="font-semibold text-lg text-gray-900">
              {health?.service || 'Unknown'}
            </p>
            <p className="text-sm text-gray-500">Service Name</p>
          </div>

          <div className="text-center p-4 rounded-lg border-2 border-dashed">
            <p className="font-semibold text-lg text-gray-900">
              {health?.version || 'Unknown'}
            </p>
            <p className="text-sm text-gray-500">Version</p>
          </div>
        </div>

        {health?.timestamp && (
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <p className="text-sm text-gray-600">
              Last health check: {new Date(health.timestamp).toLocaleString()}
            </p>
            <p className="text-xs text-gray-500">
              Uptime: {formatUptime(health.timestamp)}
            </p>
          </div>
        )}

        {lastChecked && (
          <div className="text-center mt-3">
            <p className="text-xs text-gray-500">
              Status checked at: {lastChecked.toLocaleTimeString()}
            </p>
          </div>
        )}
      </div>

      {/* Features */}
      {health?.features && (
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Available Features</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {health.features.map((feature, index) => (
              <div
                key={index}
                className="flex items-center p-3 bg-green-50 border border-green-200 rounded-lg"
              >
                <CheckCircleIcon className="h-5 w-5 text-green-500 mr-3 flex-shrink-0" />
                <span className="text-sm font-medium text-green-800">
                  {feature.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* System Information */}
      <div className="card">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Frontend Information</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="text-center p-3 bg-blue-50 rounded-lg">
            <p className="font-semibold text-blue-900">React</p>
            <p className="text-sm text-blue-700">Frontend Framework</p>
          </div>
          <div className="text-center p-3 bg-purple-50 rounded-lg">
            <p className="font-semibold text-purple-900">TypeScript</p>
            <p className="text-sm text-purple-700">Language</p>
          </div>
          <div className="text-center p-3 bg-green-50 rounded-lg">
            <p className="font-semibold text-green-900">Tailwind CSS</p>
            <p className="text-sm text-green-700">Styling</p>
          </div>
          <div className="text-center p-3 bg-yellow-50 rounded-lg">
            <p className="font-semibold text-yellow-900">Axios</p>
            <p className="text-sm text-yellow-700">HTTP Client</p>
          </div>
        </div>
      </div>

      {/* Connection Details */}
      <div className="card">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Connection Details</h2>
        <div className="space-y-3">
          <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
            <span className="font-medium text-gray-700">API Base URL:</span>
            <span className="text-gray-900 font-mono text-sm">
              {process.env.REACT_APP_API_URL || 'http://localhost:8080'}
            </span>
          </div>
          <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
            <span className="font-medium text-gray-700">Request Timeout:</span>
            <span className="text-gray-900">30 seconds</span>
          </div>
          <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
            <span className="font-medium text-gray-700">Max File Size:</span>
            <span className="text-gray-900">200 MB</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SystemStatus;
