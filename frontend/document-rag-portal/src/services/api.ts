import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8080';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

// Add response interceptor for better error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 422) {
      const detail = error.response?.data?.detail;
      if (typeof detail === 'string') {
        error.message = `Validation Error: ${detail}`;
      } else if (Array.isArray(detail)) {
        // Handle FastAPI validation errors
        const messages = detail.map((err: any) => `${err.loc?.join('.') || 'field'}: ${err.msg}`);
        error.message = `Validation Errors: ${messages.join(', ')}`;
      } else {
        error.message = 'Request validation failed. Please check your input and try again.';
      }
    }
    return Promise.reject(error);
  }
);

export interface UploadResponse {
  status: string;
  session_id: string;
  message: string;
  details?: any;
}

export interface ChatResponse {
  answer: string;
  sources?: string[];
  metadata?: any;
}

export interface AnalysisResponse {
  status: string;
  filename: string;
  file_type: string;
  documents_processed: number;
  total_content_length: number;
  metadata?: any;
  preview?: string;
  summary?: string;
  error?: string;
  // Legacy fields for backward compatibility
  file_info?: {
    size_mb: number;
    extension: string;
    processing_time: number;
  };
  content_preview?: string;
}

export interface ComparisonResponse {
  similarity_score: number;
  common_words: number;
  unique_words: number;
  summary: string;
  error?: string;
}

export interface HealthResponse {
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

export interface EvaluationResultsSummary {
  total_test_cases: number;
  average_overall_score: number;
  metrics_evaluated: number;
}

export interface EvaluationMetricScores {
  average_score: number;
  success_rate: number;
}

export interface EvaluationLatestResponse {
  status: string;
  results_file?: string;
  results?: {
    summary_statistics: EvaluationResultsSummary;
    overall_scores: Record<string, EvaluationMetricScores>;
  };
  message?: string;
}

export const apiService = {
  // Health check
  async checkHealth(): Promise<HealthResponse> {
    const response = await api.get('/health');
    return response.data;
  },

  // Upload and index file
  async uploadAndIndex(file: File, sessionId?: string): Promise<UploadResponse> {
    // Validate input
    if (!file) {
      throw new Error('File is required for upload and indexing');
    }
    
    if (file.size === 0) {
      throw new Error('Cannot upload empty file');
    }
    
    if (file.size > 50 * 1024 * 1024) { // 50MB limit
      throw new Error('File size exceeds 50MB limit');
    }

    const formData = new FormData();
    formData.append('files', file);
    formData.append('session_id', sessionId || `session_${Date.now()}`);
    formData.append('use_session_dirs', 'true');
    formData.append('chunk_size', '1000');
    formData.append('chunk_overlap', '200');
    formData.append('k', '5');

    try {
      const response = await api.post('/chat/index', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 60000, // 60 second timeout for file uploads
      });
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 422) {
        throw new Error(`Validation error: ${error.response?.data?.detail || 'Invalid request format'}`);
      }
      throw error;
    }
  },

  // Chat with document
  async chatWithDocument(question: string, sessionId: string): Promise<ChatResponse> {
    // Validate input
    if (!question?.trim()) {
      throw new Error('Question is required for chat');
    }
    
    if (!sessionId?.trim()) {
      throw new Error('Session ID is required for chat');
    }

    const formData = new FormData();
    formData.append('question', question);
    formData.append('session_id', sessionId);
    formData.append('use_session_dirs', 'true');
    formData.append('k', '5');

    try {
      const response = await api.post('/chat/query', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 30000, // 30 second timeout for chat
      });
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 422) {
        throw new Error(`Chat validation error: ${error.response?.data?.detail || 'Invalid chat request'}`);
      }
      throw error;
    }
  },

  // Analyze document
  async analyzeDocument(file: File): Promise<AnalysisResponse> {
    // Validate input
    if (!file) {
      throw new Error('File is required for analysis');
    }
    
    if (file.size === 0) {
      throw new Error('Cannot analyze empty file');
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await api.post('/analyze-document', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 45000, // 45 second timeout for analysis
      });
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 422) {
        throw new Error(`Analysis validation error: ${error.response?.data?.detail || 'Invalid file format for analysis'}`);
      }
      throw error;
    }
  },

  // Compare documents
  async compareDocuments(file1: File, file2: File): Promise<ComparisonResponse> {
    // Validate input
    if (!file1 || !file2) {
      throw new Error('Both files are required for comparison');
    }
    
    if (file1.size === 0 || file2.size === 0) {
      throw new Error('Cannot compare empty files');
    }

    const formData = new FormData();
    formData.append('reference', file1);
    formData.append('actual', file2);

    try {
      const response = await api.post('/compare', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 120000, // 2 minute timeout for comparison
      });
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 422) {
        throw new Error(`Comparison validation error: ${error.response?.data?.detail || 'Invalid files for comparison'}`);
      }
      throw error;
    }
  },

  // Evaluation
  async getLatestEvaluation(): Promise<EvaluationLatestResponse> {
    const response = await api.get('/evaluation/latest');
    return response.data;
  },

  async runEvaluation(): Promise<any> {
    const response = await api.get('/evaluation/run');
    return response.data;
  },

  // Cache Management
  async getCacheStatus(): Promise<any> {
    const response = await api.get('/cache/status');
    return response.data;
  },

  async clearCache(): Promise<any> {
    const response = await api.post('/cache/clear');
    return response.data;
  },
};

export default apiService;
