import axios from 'axios';
import { AnalysisResult, AnalysisRequest, DetailedAnalysisResponse, AnalyzeRequest, AnalyzeResponse } from '../types';

// Configuração base do axios
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  timeout: 120000, // 2 minutos - análise pode demorar
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for debugging
api.interceptors.request.use(request => {
  console.log('Starting Request:', request);
  return request;
});

// Add response interceptor for debugging
api.interceptors.response.use(
  response => {
    console.log('Response:', response);
    return response;
  },
  error => {
    console.error('API Error:', error);
    
    if (error.response?.data?.detail) {
      throw new Error(error.response.data.detail);
    }
    
    if (error.code === 'ECONNABORTED') {
      throw new Error('Tempo limite excedido. Tente novamente.');
    }
    
    if (error.response?.status === 404) {
      throw new Error('Artigo não encontrado na Wikipedia.');
    }
    
    if (error.response?.status === 400) {
      throw new Error(error.response.data?.detail || 'Dados inválidos.');
    }
    
    if (error.response?.status >= 500) {
      throw new Error('Erro interno do servidor. Tente novamente mais tarde.');
    }
    
    throw new Error(error.message || 'Erro desconhecido na comunicação com a API.');
  }
);

// Main analysis functions
export const analyzeArticleBasic = async (title: string, useAdvanced: boolean = true): Promise<AnalyzeResponse> => {
  const request: AnalyzeRequest = { 
    titulo_artigo: title,
    usar_detector_avancado: useAdvanced 
  };
  const response = await api.post<AnalyzeResponse>('/analyze', request);
  return response.data;
};

export const analyzeArticleAdvanced = async (title: string): Promise<any> => {
  const request: AnalyzeRequest = { 
    titulo_artigo: title,
    usar_detector_avancado: true 
  };
  const response = await api.post<any>('/analyze-advanced', request);
  return response.data;
};

export const analyzeArticle = async (title: string, useAdvanced: boolean = true): Promise<AnalysisResult> => {
  const request: AnalysisRequest = { title, use_advanced: useAdvanced };
  const response = await api.post<AnalysisResult>('/analyze', request);
  return response.data;
};

export const analyzeArticleDetailed = async (title: string, useAdvanced: boolean = true): Promise<DetailedAnalysisResponse> => {
  const request: AnalysisRequest = { title, use_advanced: useAdvanced };
  const response = await api.post<DetailedAnalysisResponse>('/analyze-detailed', request);
  return response.data;
};

// Test endpoints
export const testWikipedia = async (title: string) => {
  const response = await api.get(`/test-wikipedia/${encodeURIComponent(title)}`);
  return response.data;
};

export const testBiasDetection = async () => {
  const response = await api.get('/test-bias-detection');
  return response.data;
};

export const checkModelsStatus = async () => {
  const response = await api.get('/models-status');
  return response.data;
};

// Health check
export const healthCheck = async (): Promise<{ status: string }> => {
  const response = await api.get('/health');
  return response.data;
};

export default api; 