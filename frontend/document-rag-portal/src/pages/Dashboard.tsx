import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  DocumentTextIcon,
  ChatBubbleLeftRightIcon,
  ChartBarIcon,
  ScaleIcon,
  Cog6ToothIcon,
  CloudArrowUpIcon,
} from '@heroicons/react/24/outline';
import { apiService, HealthResponse } from '../services/api';

const features = [
  {
    name: 'Single Document Chat',
    description: 'Upload a document and have an intelligent conversation about its content.',
    href: '/single-chat',
    icon: DocumentTextIcon,
    color: 'from-blue-500 to-blue-600',
  },
  {
    name: 'Multi-Document Chat',
    description: 'Chat with multiple documents simultaneously for comprehensive insights.',
    href: '/multi-chat',
    icon: ChatBubbleLeftRightIcon,
    color: 'from-green-500 to-green-600',
  },
  {
    name: 'Document Analysis',
    description: 'Analyze document content with AI-powered insights and summaries.',
    href: '/analysis',
    icon: ChartBarIcon,
    color: 'from-purple-500 to-purple-600',
  },
  {
    name: 'Document Comparison',
    description: 'Compare two documents to find similarities and differences.',
    href: '/comparison',
    icon: ScaleIcon,
    color: 'from-orange-500 to-orange-600',
  },
  {
    name: 'System Status',
    description: 'Monitor system health, API status, and service performance.',
    href: '/system-status',
    icon: Cog6ToothIcon,
    color: 'from-red-500 to-red-600',
  },
];

const Dashboard: React.FC = () => {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const healthData = await apiService.checkHealth();
        setHealth(healthData);
      } catch (error) {
        console.error('Failed to fetch health status:', error);
      } finally {
        setLoading(false);
      }
    };

    checkHealth();
  }, []);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gradient mb-4">
          Document RAG Portal
        </h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          Advanced Document Analysis & Conversational AI Platform
        </p>
      </div>

      {/* Status Card */}
      <div className="card max-w-md mx-auto">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">System Status</h3>
            <p className="text-sm text-gray-600">API Service Health</p>
          </div>
          <div className="flex items-center">
            {loading ? (
              <div className="animate-pulse flex space-x-2">
                <div className="w-3 h-3 bg-gray-300 rounded-full"></div>
                <span className="text-gray-500">Checking...</span>
              </div>
            ) : health ? (
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse-slow"></div>
                <span className="text-green-600 font-semibold">Online</span>
              </div>
            ) : (
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                <span className="text-red-600 font-semibold">Offline</span>
              </div>
            )}
          </div>
        </div>
        {health && (
          <div className="mt-3 text-sm text-gray-600">
            <p>Service: {health.service}</p>
            <p>Version: {health.version}</p>
          </div>
        )}
      </div>

      {/* Features Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {features.map((feature) => (
          <Link
            key={feature.name}
            to={feature.href}
            className="card hover:shadow-xl transform hover:-translate-y-1 transition-all duration-300 group"
          >
            <div className="flex items-center space-x-4 mb-4">
              <div className={`flex-shrink-0 w-12 h-12 bg-gradient-to-r ${feature.color} rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform duration-200`}>
                <feature.icon className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900 group-hover:text-primary-600 transition-colors duration-200">
                  {feature.name}
                </h3>
              </div>
            </div>
            <p className="text-gray-600 text-sm leading-relaxed">
              {feature.description}
            </p>
            <div className="mt-4 flex items-center text-primary-600 text-sm font-medium">
              <span>Get started</span>
              <svg className="ml-2 w-4 h-4 group-hover:translate-x-1 transition-transform duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </div>
          </Link>
        ))}
      </div>

      {/* Quick Start */}
      <div className="card">
        <div className="text-center">
          <CloudArrowUpIcon className="mx-auto h-16 w-16 text-primary-500 mb-4" />
          <h3 className="text-2xl font-semibold text-gray-900 mb-2">Quick Start</h3>
          <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
            Get started by uploading your first document. Our AI will analyze it and enable intelligent conversations about its content.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/single-chat"
              className="btn-primary inline-flex items-center justify-center"
            >
              <DocumentTextIcon className="w-5 h-5 mr-2" />
              Upload Document
            </Link>
            <Link
              to="/system-status"
              className="btn-secondary inline-flex items-center justify-center"
            >
              <Cog6ToothIcon className="w-5 h-5 mr-2" />
              Check System Status
            </Link>
          </div>
        </div>
      </div>

      {/* Features Overview */}
      {health?.features && (
        <div className="card">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Available Features</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
            {health.features.map((feature, index) => (
              <div
                key={index}
                className="bg-gray-50 rounded-lg px-3 py-2 text-sm font-medium text-gray-700 text-center"
              >
                ✅ {feature.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
