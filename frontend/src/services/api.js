// Centralized API Base Configuration
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Reusable HTTP fetch wrapper for FastAPI backend requests.
 */
async function request(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  // Headers handling — do not force application/json if body is FormData
  const isFormData = options.body instanceof FormData;
  const headers = isFormData
    ? { ...options.headers }
    : { 'Content-Type': 'application/json', ...options.headers };

  const config = {
    ...options,
    headers,
  };

  try {
    const response = await fetch(url, config);
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const error = new Error(errorData.detail || errorData.message || `HTTP error ${response.status}`);
      error.status = response.status;
      error.data = errorData;
      throw error;
    }
    return await response.json();
  } catch (err) {
    if (err.isNetworkError || (err.name === 'TypeError' && err.message === 'Failed to fetch')) {
      const netError = new Error('Backend server unreachable');
      netError.isNetworkError = true;
      throw netError;
    }
    throw err;
  }
}

/**
 * Health check endpoint service.
 * @returns {Promise<{ status: string }>}
 */
export async function getHealth() {
  return await request('/health');
}

/**
 * Interactive Chat endpoint service.
 */
export async function chat(query, mitigationEnabled = true, topK = null) {
  return await request('/api/chat', {
    method: 'POST',
    body: JSON.stringify({
      query,
      mitigation_enabled: Boolean(mitigationEnabled),
      ...(topK ? { top_k: Number(topK) } : {}),
    }),
  });
}

/**
 * Fetch corpus document and chunk statistics.
 */
export async function getDocumentStats() {
  return await request('/api/documents/stats');
}

/**
 * Upload a document (PDF, TXT, CSV, JSON) with source URL provenance.
 */
export async function uploadDocument(file, sourceUrl = '') {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('source_url', sourceUrl || '');

  return await request('/api/documents/upload', {
    method: 'POST',
    body: formData,
  });
}

/**
 * Trigger document ingestion and FAISS vector index rebuilding.
 */
export async function ingestDocuments() {
  return await request('/api/documents/ingest', {
    method: 'POST',
  });
}

/**
 * Fetch high-level Phase 10 benchmark summary metrics.
 * @returns {Promise<Object>} Summary metrics response
 */
export async function getDashboardSummary() {
  return await request('/api/dashboard/summary');
}

/**
 * Fetch individual experiment run results with optional query parameters.
 * @param {Object} filters - Optional filters { language, mitigation, hallucination }
 * @returns {Promise<Object>} Results array response
 */
export async function getDashboardResults(filters = {}) {
  const queryParams = new URLSearchParams();
  if (filters.language) {
    queryParams.append('language', filters.language);
  }
  if (filters.mitigation !== undefined && filters.mitigation !== null && filters.mitigation !== '') {
    queryParams.append('mitigation', String(filters.mitigation));
  }
  if (filters.hallucination !== undefined && filters.hallucination !== null && filters.hallucination !== '') {
    queryParams.append('hallucination', String(filters.hallucination));
  }

  const queryString = queryParams.toString();
  const endpoint = `/api/dashboard/results${queryString ? `?${queryString}` : ''}`;
  return await request(endpoint);
}

export const api = {
  baseUrl: API_BASE_URL,
  request,
  getHealth,
  chat,
  getDocumentStats,
  uploadDocument,
  ingestDocuments,
  getDashboardSummary,
  getDashboardResults,
};

export default api;
