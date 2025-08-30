import React, { useState } from 'react';
import { ScaleIcon } from '@heroicons/react/24/outline';
import FileUpload from '../components/FileUpload';
import { apiService, ComparisonResponse } from '../services/api';

const DocumentComparison: React.FC = () => {
  const [file1, setFile1] = useState<File | null>(null);
  const [file2, setFile2] = useState<File | null>(null);
  const [comparing, setComparing] = useState(false);
  const [result, setResult] = useState<ComparisonResponse | null>(null);

  const handleCompare = async () => {
    if (!file1 || !file2) return;

    setComparing(true);
    try {
      const response = await apiService.compareDocuments(file1, file2);
      setResult(response);
    } catch (error) {
      setResult({
        similarity_score: 0,
        common_words: 0,
        unique_words: 0,
        summary: '',
        error: error instanceof Error ? error.message : 'Comparison failed',
      });
    } finally {
      setComparing(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Document Comparison</h1>
        <p className="text-gray-600">Compare two documents to find similarities and differences</p>
      </div>

      {/* Upload Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Document 1</h2>
          <FileUpload onFileSelect={setFile1} disabled={comparing} />
          {file1 && (
            <div className="mt-4 p-3 bg-gray-50 rounded border">
              <p className="font-medium">{file1.name}</p>
              <p className="text-sm text-gray-500">{(file1.size / 1024 / 1024).toFixed(2)} MB</p>
            </div>
          )}
        </div>

        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Document 2</h2>
          <FileUpload onFileSelect={setFile2} disabled={comparing} />
          {file2 && (
            <div className="mt-4 p-3 bg-gray-50 rounded border">
              <p className="font-medium">{file2.name}</p>
              <p className="text-sm text-gray-500">{(file2.size / 1024 / 1024).toFixed(2)} MB</p>
            </div>
          )}
        </div>
      </div>

      {/* Compare Button */}
      <div className="text-center">
        <button
          onClick={handleCompare}
          disabled={!file1 || !file2 || comparing}
          className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed inline-flex items-center"
        >
          <ScaleIcon className="h-5 w-5 mr-2" />
          {comparing ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
              Comparing...
            </>
          ) : (
            'Compare Documents'
          )}
        </button>
      </div>

      {/* Results Section */}
      {result && (
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Comparison Results</h2>
          
          {result.error ? (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-800">❌ {result.error}</p>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center p-4 bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg border border-blue-200">
                  <p className="text-3xl font-bold text-blue-600">
                    {(result.similarity_score * 100).toFixed(1)}%
                  </p>
                  <p className="text-blue-800 font-medium">Similarity Score</p>
                </div>
                <div className="text-center p-4 bg-gradient-to-r from-green-50 to-green-100 rounded-lg border border-green-200">
                  <p className="text-3xl font-bold text-green-600">{result.common_words}</p>
                  <p className="text-green-800 font-medium">Common Words</p>
                </div>
                <div className="text-center p-4 bg-gradient-to-r from-purple-50 to-purple-100 rounded-lg border border-purple-200">
                  <p className="text-3xl font-bold text-purple-600">{result.unique_words}</p>
                  <p className="text-purple-800 font-medium">Unique Words</p>
                </div>
              </div>

              {/* Summary */}
              {result.summary && (
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-3">Comparison Summary</h3>
                  <div className="p-4 bg-gray-50 border border-gray-200 rounded-lg">
                    <p className="text-gray-700 leading-relaxed">{result.summary}</p>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default DocumentComparison;
