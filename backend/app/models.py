from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum

class BiasType(str, Enum):
    # Tipos básicos (existentes)
    LOADED_LANGUAGE = "linguagem_carregada"
    OPINION_AS_FACT = "opiniao_como_fato"
    MISSING_COUNTERPOINT = "ausencia_contraponto"
    SUBJECTIVE_TERMS = "termos_subjetivos"
    EMOTIONAL_LANGUAGE = "linguagem_emocional"
    
    # Novos tipos específicos para IA
    TECHNOLOGICAL_DETERMINISM = "determinismo_tecnologico"
    ANTHROPOMORPHISM = "antropomorfismo"
    OVERSIMPLIFICATION = "supersimplificacao"
    HYPE_LANGUAGE = "linguagem_sensacionalista"
    FEAR_MONGERING = "alarmismo"
    FALSE_CERTAINTY = "falsa_certeza"
    SELECTION_BIAS = "vies_selecao"
    CONFIRMATION_BIAS = "vies_confirmacao"
    TEMPORAL_BIAS = "vies_temporal"
    AUTHORITY_BIAS = "vies_autoridade"

class BiasAnalysis(BaseModel):
    trecho_original: str
    tipo_vies: BiasType
    explicacao: str
    reformulacao_sugerida: str
    posicao_inicio: int
    posicao_fim: int
    confianca: float
    # Novas métricas quantitativas
    intensidade_emocional: Optional[float] = 0.0
    polaridade_sentimento: Optional[float] = 0.0
    complexidade_sintatica: Optional[float] = 0.0
    nivel_certeza: Optional[float] = 0.0
    score_formalidade: Optional[float] = 0.0

class AnalyzeRequest(BaseModel):
    titulo_artigo: str
    usar_detector_avancado: Optional[bool] = True

class AnalysisRequest(BaseModel):
    title: str
    use_advanced: Optional[bool] = True

class AnalysisResponse(BaseModel):
    article_title: str
    article_url: str
    article_content: str
    ai_related: bool
    bias_detected: bool
    overall_bias_score: float
    bias_categories: List[str]
    detailed_analysis: str
    reformulated_text: Optional[str] = None
    analysis_summary: Optional[str] = None
    total_trechos_analisados: Optional[int] = None
    trecho_original: Optional[str] = None
    # Novas métricas agregadas  
    metricas_quantitativas: Optional[Dict[str, float]] = {}

class AnalyzeResponse(BaseModel):
    titulo: str
    conteudo_original: str
    url_wikipedia: str
    analises_vies: List[BiasAnalysis]
    resumo_geral: str
    total_trechos_analisados: int  # Total de segmentos analisados no artigo
    total_trechos_com_vies: int    # Segmentos onde viés foi detectado
    # Novas métricas gerais
    score_polaridade_geral: Optional[float] = 0.0
    score_emocional_geral: Optional[float] = 0.0
    score_complexidade_geral: Optional[float] = 0.0
    distribuicao_tipos_vies: Optional[Dict[str, int]] = None
    
class ErrorResponse(BaseModel):
    erro: str
    detalhes: Optional[str] = None 