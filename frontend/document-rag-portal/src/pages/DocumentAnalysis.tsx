import React, { useState } from 'react';
import { ChartBarIcon } from '@heroicons/react/24/outline';
import FileUpload from '../components/FileUpload';
import { apiService, AnalysisResponse } from '../services/api';

const DocumentAnalysis: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState<AnalysisResponse | null>(null);

  const handleFileSelect = (selectedFile: File) => {
    setFile(selectedFile);
    setResult(null);
  };

  const handleAnalyze = async () => {
    if (!file) return;

    setAnalyzing(true);
    try {
      const response = await apiService.analyzeDocument(file);
      setResult(response);
    } catch (error) {
      setResult({
        status: 'error',
        filename: file?.name || 'unknown',
        file_type: 'unknown',
        documents_processed: 0,
        total_content_length: 0,
        error: error instanceof Error ? error.message : 'Analysis failed',
      });
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Document Analysis</h1>
        <p className="text-gray-600">Analyze document content with AI-powered insights and summaries</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upload Section */}
        <div className="card space-y-4">
          <h2 className="text-xl font-semibold text-gray-900 flex items-center">
            <ChartBarIcon className="h-6 w-6 mr-2" />
            Document Upload & Analysis
          </h2>
          
          <FileUpload onFileSelect={handleFileSelect} disabled={analyzing} />

          {file && (
            <div className="p-4 bg-gray-50 rounded-lg border">
              <p className="font-medium text-gray-900">{file.name}</p>
              <p className="text-sm text-gray-500">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
            </div>
          )}

          <button
            onClick={handleAnalyze}
            disabled={!file || analyzing}
            className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {analyzing ? (
              <div className="flex items-center justify-center">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                Analyzing...
              </div>
            ) : (
              'Analyze Document'
            )}
          </button>
        </div>

        {/* Results Section */}
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Analysis Results</h2>
          
          {!result ? (
            <div className="text-center py-12 text-gray-500">
              Upload and analyze a document to see results here
            </div>
          ) : result.error ? (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-800">❌ {result.error}</p>
            </div>
          ) : (
            <div className="space-y-4">
              {result.file_info && (
                <div className="grid grid-cols-3 gap-4">
                  <div className="text-center p-3 bg-blue-50 rounded-lg">
                    <p className="text-2xl font-bold text-blue-600">{result.file_info.size_mb.toFixed(1)}</p>
                    <p className="text-sm text-blue-800">MB</p>
                  </div>
                  <div className="text-center p-3 bg-green-50 rounded-lg">
                    <p className="text-2xl font-bold text-green-600">{result.file_info.extension.toUpperCase()}</p>
                    <p className="text-sm text-green-800">Format</p>
                  </div>
                  <div className="text-center p-3 bg-purple-50 rounded-lg">
                    <p className="text-2xl font-bold text-purple-600">{result.file_info.processing_time.toFixed(1)}s</p>
                    <p className="text-sm text-purple-800">Processing</p>
                  </div>
                </div>
              )}

              {result.documents_processed && (
                <div className="p-4 bg-gray-50 rounded-lg">
                  <h4 className="font-medium text-gray-900 mb-2">Processing Summary</h4>
                  <p className="text-gray-700">Records processed: {result.documents_processed}</p>
                </div>
              )}

              {result.content_preview && (
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Content Preview</h4>
                  <div className="p-3 bg-gray-50 rounded border text-sm font-mono max-h-40 overflow-y-auto">
                    {result.content_preview.substring(0, 1000)}
                    {result.content_preview.length > 1000 && '...'}
                  </div>
                </div>
              )}

              {result.summary && (
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">AI Analysis Insights</h4>
                  <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                    <p className="text-blue-900">{result.summary}</p>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DocumentAnalysis;
