export interface BiasAnalysis {
  trecho_original: string;
  tipo_vies: string;
  explicacao: string;
  reformulacao_sugerida: string;
  posicao_inicio: number;
  posicao_fim: number;
  confianca: number;
  // Novas métricas quantitativas
  intensidade_emocional?: number;
  polaridade_sentimento?: number;
  complexidade_sintatica?: number;
  nivel_certeza?: number;
  score_formalidade?: number;
}

export interface AnalyzeRequest {
  titulo_artigo: string;
  usar_detector_avancado?: boolean;
}

export interface AnalyzeResponse {
  titulo: string;
  conteudo_original: string;
  url_wikipedia: string;
  analises_vies: BiasAnalysis[];
  resumo_geral: string;
  total_trechos_analisados: number;
  total_trechos_com_vies: number;
  // Novas métricas gerais
  score_polaridade_geral?: number;
  score_emocional_geral?: number;
  score_complexidade_geral?: number;
  distribuicao_tipos_vies?: Record<string, number>;
}

// New types for detailed analysis
export interface AnalysisRequest {
  title: string;
  use_advanced?: boolean;
}

export interface AnalysisResult {
  article_title: string;
  article_url: string;
  article_content: string;
  ai_related: boolean;
  bias_detected: boolean;
  overall_bias_score: number;
  bias_categories: string[];
  detailed_analysis: string;
  reformulated_text?: string;
  analysis_summary?: string;
  total_trechos_analisados?: number;
  metricas_quantitativas?: Record<string, number>;
}

export interface AnalysisStep {
  id: string;
  title: string;
  description: string;
  status: 'waiting' | 'running' | 'completed' | 'error';
  start_time?: number;
  end_time?: number;
  details?: string[];
  metrics?: Record<string, any>;
}

export interface DetailedAnalysisResponse {
  success: boolean;
  steps: AnalysisStep[];
  final_result?: AnalysisResult;
  total_duration?: number;
  error_message?: string;
}

export interface ErrorResponse {
  erro: string;
  detalhes?: string;
}

export interface ApiError {
  detail: string;
}

// Novos tipos de viés
export const BiasTypes = {
  // Tipos básicos
  LOADED_LANGUAGE: "linguagem_carregada",
  OPINION_AS_FACT: "opiniao_como_fato", 
  MISSING_COUNTERPOINT: "ausencia_contraponto",
  SUBJECTIVE_TERMS: "termos_subjetivos",
  EMOTIONAL_LANGUAGE: "linguagem_emocional",
  
  // Novos tipos específicos para IA
  TECHNOLOGICAL_DETERMINISM: "determinismo_tecnologico",
  ANTHROPOMORPHISM: "antropomorfismo", 
  OVERSIMPLIFICATION: "supersimplificacao",
  HYPE_LANGUAGE: "linguagem_sensacionalista",
  FEAR_MONGERING: "alarmismo",
  FALSE_CERTAINTY: "falsa_certeza",
  SELECTION_BIAS: "vies_selecao",
  CONFIRMATION_BIAS: "vies_confirmacao", 
  TEMPORAL_BIAS: "vies_temporal",
  AUTHORITY_BIAS: "vies_autoridade"
} as const;

export const BiasTypeLabels: Record<string, string> = {
  "linguagem_carregada": "Linguagem Carregada",
  "opiniao_como_fato": "Opinião como Fato",
  "ausencia_contraponto": "Ausência de Contraponto", 
  "termos_subjetivos": "Termos Subjetivos",
  "linguagem_emocional": "Linguagem Emocional",
  "determinismo_tecnologico": "Determinismo Tecnológico",
  "antropomorfismo": "Antropomorfismo",
  "supersimplificacao": "Supersimplificação", 
  "linguagem_sensacionalista": "Linguagem Sensacionalista",
  "alarmismo": "Alarmismo",
  "falsa_certeza": "Falsa Certeza",
  "vies_selecao": "Viés de Seleção",
  "vies_confirmacao": "Viés de Confirmação",
  "vies_temporal": "Viés Temporal", 
  "vies_autoridade": "Viés de Autoridade"
};

export const BiasTypeColors: Record<string, string> = {
  "linguagem_carregada": "bg-red-100 text-red-800 border-red-200",
  "opiniao_como_fato": "bg-orange-100 text-orange-800 border-orange-200",
  "ausencia_contraponto": "bg-yellow-100 text-yellow-800 border-yellow-200",
  "termos_subjetivos": "bg-blue-100 text-blue-800 border-blue-200",
  "linguagem_emocional": "bg-purple-100 text-purple-800 border-purple-200",
  "determinismo_tecnologico": "bg-green-100 text-green-800 border-green-200",
  "antropomorfismo": "bg-teal-100 text-teal-800 border-teal-200",
  "supersimplificacao": "bg-pink-100 text-pink-800 border-pink-200",
  "linguagem_sensacionalista": "bg-indigo-100 text-indigo-800 border-indigo-200",
  "alarmismo": "bg-red-100 text-red-800 border-red-200",
  "falsa_certeza": "bg-orange-100 text-orange-800 border-orange-200",
  "vies_selecao": "bg-yellow-100 text-yellow-800 border-yellow-200",
  "vies_confirmacao": "bg-green-100 text-green-800 border-green-200",
  "vies_temporal": "bg-blue-100 text-blue-800 border-blue-200",
  "vies_autoridade": "bg-purple-100 text-purple-800 border-purple-200"
};

export function getConfidenceColor(confidence: number): string {
  if (confidence >= 0.8) return "text-bias-high";
  if (confidence >= 0.5) return "text-bias-medium";
  return "text-bias-low";
}

export function getConfidenceLabel(confidence: number): string {
  if (confidence >= 0.8) return "Alta";
  if (confidence >= 0.5) return "Média";
  return "Baixa";
} 