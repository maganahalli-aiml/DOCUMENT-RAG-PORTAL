import React, { useEffect, useState } from 'react';
import { apiService, EvaluationLatestResponse } from '../services/api';

const Badge: React.FC<{ value: number; invert?: boolean }> = ({ value, invert }) => {
  // value is 0..1, higher is better unless invert=true
  const score = Math.max(0, Math.min(1, value));
  const good = invert ? score < 0.1 : score >= 0.8;
  const warn = invert ? score < 0.2 : score >= 0.6 && score < 0.8;
  const color = good ? 'bg-green-100 text-green-700' : warn ? 'bg-yellow-100 text-yellow-700' : 'bg-red-100 text-red-700';
  return <span className={`px-2 py-1 rounded text-xs font-semibold ${color}`}>{(score * 100).toFixed(0)}%</span>;
};

const Evaluation: React.FC = () => {
  const [data, setData] = useState<EvaluationLatestResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiService.getLatestEvaluation();
      setData(res);
    } catch (e: any) {
      setError(e?.message || 'Failed to load evaluation');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const runNow = async () => {
    try {
      setRunning(true);
      await apiService.runEvaluation();
      await load();
    } catch (e: any) {
      setError(e?.message || 'Run failed');
    } finally {
      setRunning(false);
    }
  };

  const summary = data?.results?.summary_statistics;
  const metrics = data?.results?.overall_scores || {};

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Evaluation Metrics</h1>
          <p className="text-gray-600">DeepEval (mock/dev) results for the RAG system</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={load}
            className="btn-secondary"
            disabled={loading}
          >
            Refresh
          </button>
          <button
            onClick={runNow}
            className="btn-primary"
            disabled={running}
          >
            {running ? 'Running…' : 'Run Evaluation'}
          </button>
        </div>
      </div>

      {loading && <div className="card">Loading latest results…</div>}
      {error && <div className="card text-red-600">{error}</div>}

      {!loading && data?.status === 'empty' && (
        <div className="card">No evaluation results found. Click "Run Evaluation" to generate.</div>
      )}

      {!loading && data?.results && (
        <div className="space-y-6">
          <div className="card">
            <h3 className="text-lg font-semibold mb-2">Summary</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <div className="text-sm text-gray-600">Overall Score</div>
                <div className="text-xl font-bold">{summary?.average_overall_score.toFixed(3)}</div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Total Test Cases</div>
                <div className="text-xl font-bold">{summary?.total_test_cases}</div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Metrics Evaluated</div>
                <div className="text-xl font-bold">{summary?.metrics_evaluated}</div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Source</div>
                <div className="text-xs text-gray-700 break-all">{data?.results_file}</div>
              </div>
            </div>
          </div>

          <div className="card">
            <h3 className="text-lg font-semibold mb-3">Metric Breakdown</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.entries(metrics).map(([name, scores]) => {
                const invert = ['hallucination', 'toxicity', 'bias'].includes(name.toLowerCase());
                return (
                  <div key={name} className="p-3 rounded border border-gray-200">
                    <div className="flex items-center justify-between mb-2">
                      <div className="font-medium">{name.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())}</div>
                      <Badge value={scores.average_score} invert={invert} />
                    </div>
                    <div className="w-full bg-gray-100 h-2 rounded">
                      <div
                        className={`h-2 rounded ${invert ? 'bg-red-400' : 'bg-green-500'}`}
                        style={{ width: `${Math.max(0, Math.min(1, scores.average_score)) * 100}%` }}
                      />
                    </div>
                    <div className="text-xs text-gray-600 mt-2">Success rate: {(scores.success_rate * 100).toFixed(1)}%</div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Evaluation;
