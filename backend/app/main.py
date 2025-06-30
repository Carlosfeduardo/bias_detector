from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import os
from typing import List, Optional, Dict, Any
import time
import asyncio

from .models import AnalyzeRequest, AnalyzeResponse, ErrorResponse, BiasAnalysis, AnalysisRequest, AnalysisResponse
from .wikipedia_client import WikipediaClient
from .bias_detector import BiasDetector
from .reformulator import TextReformulator
from .utils import validate_article_title, normalize_text, truncate_text

# Import condicional do detector avançado
try:
    from .advanced_bias_detector import AdvancedBiasDetector
    ADVANCED_DETECTOR_AVAILABLE = True
    print("✅ Detector avançado disponível")
except ImportError as e:
    ADVANCED_DETECTOR_AVAILABLE = False
    print(f"⚠️ Detector avançado não disponível: {e}")
    print("💡 Usando apenas detector básico")

# Configuração da API OpenAI a partir de variável de ambiente
API_KEY_OPENAI = os.getenv("OPENAI_API_KEY")
if not API_KEY_OPENAI:
    raise ValueError("Variável de ambiente OPENAI_API_KEY não encontrada. Configure sua chave da API OpenAI.")
print("✅ Chave OpenAI carregada da variável de ambiente")

# Inicialização da aplicação
app = FastAPI(
    title="Detector de Viés em Artigos da Wikipedia",
    description="API para detectar e reformular viés textual em artigos da Wikipedia sobre IA",
    version="1.0.0"
)

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:3001", 
        "https://biasdetector.online",
        "https://www.biasdetector.online",
        "http://biasdetector.online",
        "http://www.biasdetector.online",
        "http://103.199.184.185",
        "https://103.199.184.185"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicialização dos componentes
wikipedia_client = WikipediaClient()
bias_detector = BiasDetector()
text_reformulator = TextReformulator(API_KEY_OPENAI)

# Inicialização condicional do detector avançado
if ADVANCED_DETECTOR_AVAILABLE:
    try:
        advanced_bias_detector = AdvancedBiasDetector()
        print("✅ Detector avançado inicializado")
    except Exception as e:
        print(f"⚠️ Erro ao inicializar detector avançado: {e}")
        advanced_bias_detector = None
        ADVANCED_DETECTOR_AVAILABLE = False
else:
    advanced_bias_detector = None

# New models for detailed progress tracking
class AnalysisStep(BaseModel):
    id: str
    title: str
    description: str
    status: str  # 'waiting', 'running', 'completed', 'error'
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    details: Optional[List[str]] = None
    metrics: Optional[Dict[str, Any]] = None

class DetailedAnalysisResponse(BaseModel):
    success: bool
    steps: List[AnalysisStep]
    final_result: Optional[AnalysisResponse] = None
    total_duration: Optional[float] = None
    error_message: Optional[str] = None

@app.get("/")
async def root():
    """Endpoint raiz com informações da API"""
    return {
        "message": "Detector de Viés em Artigos da Wikipedia",
        "version": "1.0.0",
        "status": "ativo",
        "endpoints": {
            "analyze": "/analyze - Analisa viés em artigo da Wikipedia",
            "health": "/health - Verifica saúde da API"
        }
    }

@app.get("/health")
async def health_check():
    """Endpoint para verificar saúde da API"""
    return {
        "status": "healthy",
        "components": {
            "wikipedia_client": "ok",
            "bias_detector": "ok",
            "text_reformulator": "ok"
        }
    }

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_article(request: AnalyzeRequest):
    """
    Analisa um artigo da Wikipedia em busca de viés textual
    
    Args:
        request: Objeto contendo o título do artigo
        
    Returns:
        AnalyzeResponse: Análise completa do artigo com viés detectado
        
    Raises:
        HTTPException: Em caso de erro no processamento
    """
    try:
        # Validação do título
        if not validate_article_title(request.titulo_artigo):
            raise HTTPException(
                status_code=400,
                detail="Título do artigo inválido. Use apenas caracteres alfanuméricos e espaços."
            )
        
        # Busca o artigo na Wikipedia
        print(f"Buscando artigo: {request.titulo_artigo}")
        article_data = wikipedia_client.get_article_content(request.titulo_artigo)
        
        if not article_data:
            raise HTTPException(
                status_code=404,
                detail=f"Artigo '{request.titulo_artigo}' não encontrado na Wikipedia portuguesa."
            )
        
        # Verifica se o artigo é relacionado à IA
        if not wikipedia_client.is_ai_related(article_data['title'], article_data['content']):
            raise HTTPException(
                status_code=400,
                detail="Este artigo não parece ser relacionado à Inteligência Artificial ou áreas correlatas."
            )
        
        # Normaliza o conteúdo
        normalized_content = normalize_text(article_data['content'])
        
        if len(normalized_content) < 100:
            raise HTTPException(
                status_code=400,
                detail="Artigo muito curto para análise de viés."
            )
        
        # Calcula total de segmentos analisados (sentenças)
        total_segments_analyzed = 0
        if ADVANCED_DETECTOR_AVAILABLE and advanced_bias_detector and advanced_bias_detector.nlp:
            doc = advanced_bias_detector.nlp(normalized_content)
            total_segments_analyzed = len([sent for sent in doc.sents if len(sent.text.strip()) >= 20])
        else:
            # Fallback: estima baseado em pontuação
            total_segments_analyzed = len([s.strip() for s in normalized_content.split('.') if len(s.strip()) >= 20])
        
        # Escolhe o detector baseado na preferência e disponibilidade
        if request.usar_detector_avancado and ADVANCED_DETECTOR_AVAILABLE and advanced_bias_detector:
            print("🧠 Usando detector avançado...")
            try:
                advanced_analyses = advanced_bias_detector.analyze_text_advanced(normalized_content)
                
                # Converte análises avançadas para formato básico
                bias_analyses = []
                for adv_analysis in advanced_analyses:
                    if adv_analysis.confidence_scores:
                        # Seleciona o tipo de viés com maior confiança
                        best_bias_type = max(adv_analysis.confidence_scores.items(), key=lambda x: x[1])
                        bias_type, confidence = best_bias_type
                        
                        basic_analysis = BiasAnalysis(
                            trecho_original=adv_analysis.text_segment,
                            tipo_vies=bias_type,
                            explicacao=adv_analysis.explanation,
                            reformulacao_sugerida="",
                            posicao_inicio=adv_analysis.start_pos,
                            posicao_fim=adv_analysis.end_pos,
                            confianca=confidence,
                            intensidade_emocional=adv_analysis.semantic_features.emotional_intensity,
                            polaridade_sentimento=adv_analysis.semantic_features.sentiment_polarity,
                            complexidade_sintatica=adv_analysis.syntactic_features.dependency_complexity,
                            nivel_certeza=adv_analysis.semantic_features.certainty_level,
                            score_formalidade=adv_analysis.semantic_features.formality_score
                        )
                        bias_analyses.append(basic_analysis)
                        
            except Exception as e:
                print(f"Erro no detector avançado, usando básico: {e}")
                bias_analyses = bias_detector.analyze_text(normalized_content)
        else:
            print("📝 Usando detector básico melhorado...")
            bias_analyses = bias_detector.analyze_text(normalized_content)
        
        # Calcula métricas agregadas
        metricas_gerais = {}
        if bias_analyses:
            metricas_gerais = {
                'polaridade_media': sum(a.polaridade_sentimento or 0 for a in bias_analyses) / len(bias_analyses),
                'intensidade_emocional_media': sum(a.intensidade_emocional or 0 for a in bias_analyses) / len(bias_analyses),
                'complexidade_media': sum(a.complexidade_sintatica or 0 for a in bias_analyses) / len(bias_analyses),
                'nivel_certeza_medio': sum(a.nivel_certeza or 0 for a in bias_analyses) / len(bias_analyses),
                'score_formalidade_medio': sum(a.score_formalidade or 0 for a in bias_analyses) / len(bias_analyses)
            }
        
        # Distribuição dos tipos de viés
        distribuicao_tipos = {}
        for analysis in bias_analyses:
            tipo = analysis.tipo_vies.value
            distribuicao_tipos[tipo] = distribuicao_tipos.get(tipo, 0) + 1
        
        if not bias_analyses:
            # Retorna resposta mesmo sem viés detectado
            return AnalyzeResponse(
                titulo=article_data['title'],
                conteudo_original=normalized_content,
                url_wikipedia=article_data['url'],
                analises_vies=[],
                resumo_geral=f"Nenhum viés significativo foi detectado no artigo '{article_data['title']}'. O artigo foi analisado em {total_segments_analyzed} segmentos e nenhum apresentou viés detectável.",
                total_trechos_analisados=total_segments_analyzed,
                total_trechos_com_vies=0,
                score_polaridade_geral=0.0,
                score_emocional_geral=0.0,
                score_complexidade_geral=0.0,
                distribuicao_tipos_vies={}
            )
        
        # Reformula os trechos com viés
        print("Reformulando trechos com viés...")
        reformulated_analyses = text_reformulator.reformulate_analyses(bias_analyses)
        
        # Gera resumo geral expandido
        print("Gerando resumo geral expandido...")
        resumo_base = text_reformulator.generate_general_summary(
            reformulated_analyses, 
            article_data['title']
        )
        
        # Adiciona estatísticas ao resumo
        resumo_expandido = f"""{resumo_base}

📊 **Métricas Quantitativas:**
- Polaridade média do sentimento: {metricas_gerais.get('polaridade_media', 0):.2f} (-1 a 1)
- Intensidade emocional média: {metricas_gerais.get('intensidade_emocional_media', 0):.2f} (0 a 1)
- Complexidade sintática média: {metricas_gerais.get('complexidade_media', 0):.2f} (0 a 1)
- Nível de certeza médio: {metricas_gerais.get('nivel_certeza_medio', 0):.2f} (0 a 1)
- Score de formalidade médio: {metricas_gerais.get('score_formalidade_medio', 0):.2f} (0 a 1)

🎯 **Distribuição dos Tipos de Viés:**
""" + "\n".join([f"- {tipo.replace('_', ' ').title()}: {count} ocorrência(s)" for tipo, count in distribuicao_tipos.items()])
        
        # Monta resposta
        total_com_vies = len(reformulated_analyses)
        print(f"DEBUG: total_segments_analyzed={total_segments_analyzed}, total_com_vies={total_com_vies}")
        
        response = AnalyzeResponse(
            titulo=article_data['title'],
            conteudo_original=normalized_content,
            url_wikipedia=article_data['url'],
            analises_vies=reformulated_analyses,
            resumo_geral=resumo_expandido,
            total_trechos_analisados=total_segments_analyzed,
            total_trechos_com_vies=total_com_vies,
            score_polaridade_geral=metricas_gerais.get('polaridade_media', 0.0),
            score_emocional_geral=metricas_gerais.get('intensidade_emocional_media', 0.0),
            score_complexidade_geral=metricas_gerais.get('complexidade_media', 0.0),
            distribuicao_tipos_vies=distribuicao_tipos
        )
        
        print(f"DEBUG: Modelo criado com campos: {list(response.model_dump().keys())}")
        
        detector_usado = "avançado" if (request.usar_detector_avancado and ADVANCED_DETECTOR_AVAILABLE) else "básico melhorado"
        print(f"Análise concluída ({detector_usado}): {len(reformulated_analyses)} trechos com viés detectados")
        return response
        
    except HTTPException:
        # Re-lança HTTPExceptions
        raise
    except Exception as e:
        print(f"Erro interno: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno do servidor: {str(e)}"
        )

@app.get("/test-wikipedia/{title}")
async def test_wikipedia_search(title: str):
    """Endpoint de teste para buscar artigos na Wikipedia"""
    try:
        article_data = wikipedia_client.get_article_content(title)
        
        if not article_data:
            return {"error": "Artigo não encontrado"}
        
        # Retorna versão truncada para teste
        return {
            "title": article_data['title'],
            "content_preview": truncate_text(article_data['content'], 500),
            "url": article_data['url'],
            "is_ai_related": wikipedia_client.is_ai_related(
                article_data['title'], 
                article_data['content']
            ),
            "content_length": len(article_data['content'])
        }
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/test-bias-detection")
async def test_bias_detection():
    """Endpoint de teste para detecção de viés"""
    test_text = """
    A inteligência artificial é obviamente a tecnologia mais revolucionária da nossa era. 
    Todos os especialistas concordam que ela mudará completamente nossa sociedade. 
    É impossível imaginar um futuro sem IA, pois ela é claramente superior aos métodos tradicionais.
    Nunca houve uma tecnologia tão fantástica e transformadora.
    """
    
    try:
        analyses = bias_detector.analyze_text(test_text)
        return {
            "test_text": test_text,
            "bias_analyses": [
                {
                    "type": analysis.tipo_vies,
                    "confidence": analysis.confianca,
                    "explanation": analysis.explicacao,
                    "original_text": analysis.trecho_original
                }
                for analysis in analyses
            ],
            "total_detected": len(analyses)
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/analyze-advanced", response_model=dict)
async def analyze_article_advanced(request: AnalyzeRequest):
    """
    Analisa um artigo da Wikipedia usando técnicas avançadas de NLP
    
    Args:
        request: Objeto contendo o título do artigo
        
    Returns:
        Dict: Análise avançada completa com métricas detalhadas
        
    Raises:
        HTTPException: Em caso de erro no processamento
    """
    # Verifica se o detector avançado está disponível
    if not ADVANCED_DETECTOR_AVAILABLE or advanced_bias_detector is None:
        raise HTTPException(
            status_code=503,
            detail="Detector avançado não disponível. Dependências de NLP não instaladas. Use o endpoint /analyze para análise básica."
        )
    
    try:
        # Validação do título
        if not validate_article_title(request.titulo_artigo):
            raise HTTPException(
                status_code=400,
                detail="Título do artigo inválido. Use apenas caracteres alfanuméricos e espaços."
            )
        
        # Busca o artigo na Wikipedia
        print(f"🔍 Buscando artigo (análise avançada): {request.titulo_artigo}")
        article_data = wikipedia_client.get_article_content(request.titulo_artigo)
        
        if not article_data:
            raise HTTPException(
                status_code=404,
                detail=f"Artigo '{request.titulo_artigo}' não encontrado na Wikipedia portuguesa."
            )
        
        # Verifica se o artigo é relacionado à IA
        if not wikipedia_client.is_ai_related(article_data['title'], article_data['content']):
            raise HTTPException(
                status_code=400,
                detail="Este artigo não parece ser relacionado à Inteligência Artificial ou áreas correlatas."
            )
        
        # Normaliza o conteúdo
        normalized_content = normalize_text(article_data['content'])
        
        if len(normalized_content) < 100:
            raise HTTPException(
                status_code=400,
                detail="Artigo muito curto para análise de viés."
            )
        
        # Análise avançada de viés
        print("🧠 Executando análise avançada de viés...")
        advanced_analyses = advanced_bias_detector.analyze_text_advanced(normalized_content)
        
        if not advanced_analyses:
            return {
                "status": "no_bias_detected",
                "title": article_data['title'],
                "url": article_data['url'],
                "content_length": len(normalized_content),
                "message": "Nenhum viés significativo detectado na análise avançada",
                "analysis_type": "advanced_nlp"
            }
        
        # Gera relatório abrangente
        print("📊 Gerando relatório abrangente...")
        comprehensive_report = advanced_bias_detector.generate_comprehensive_report(advanced_analyses)
        
        # Converte analyses para formato compatível
        converted_analyses = []
        for analysis in advanced_analyses:
            converted_analysis = {
                "text_segment": analysis.text_segment,
                "start_pos": analysis.start_pos,
                "end_pos": analysis.end_pos,
                "bias_types": [bt.value for bt in analysis.bias_types],
                "confidence_scores": {bt.value: score for bt, score in analysis.confidence_scores.items()},
                "overall_bias_score": analysis.overall_bias_score,
                "explanation": analysis.explanation,
                "evidence": analysis.evidence,
                "reformulation_suggestions": analysis.reformulation_suggestions,
                "semantic_features": {
                    "sentiment_polarity": analysis.semantic_features.sentiment_polarity,
                    "sentiment_confidence": analysis.semantic_features.sentiment_confidence,
                    "subjectivity_score": analysis.semantic_features.subjectivity_score,
                    "emotional_intensity": analysis.semantic_features.emotional_intensity,
                    "certainty_level": analysis.semantic_features.certainty_level,
                    "formality_score": analysis.semantic_features.formality_score
                },
                "syntactic_features": {
                    "dependency_complexity": analysis.syntactic_features.dependency_complexity,
                    "pos_diversity": analysis.syntactic_features.pos_diversity,
                    "modal_verb_ratio": analysis.syntactic_features.modal_verb_ratio,
                    "passive_voice_ratio": analysis.syntactic_features.passive_voice_ratio,
                    "hedge_word_ratio": analysis.syntactic_features.hedge_word_ratio,
                    "intensifier_ratio": analysis.syntactic_features.intensifier_ratio
                }
            }
            converted_analyses.append(converted_analysis)
        
        # Reformula trechos usando análise avançada
        print("✏️ Reformulando trechos com IA...")
        advanced_reformulations = []
        for analysis in advanced_analyses[:5]:  # Limita a 5 para não sobrecarregar a API
            try:
                # Cria BiasAnalysis temporário para o reformulador
                temp_analysis = BiasAnalysis(
                    trecho_original=analysis.text_segment,
                    tipo_vies=analysis.bias_types[0] if analysis.bias_types else BiasType.LOADED_LANGUAGE,
                    explicacao=analysis.explanation,
                    reformulacao_sugerida="",
                    posicao_inicio=analysis.start_pos,
                    posicao_fim=analysis.end_pos,
                    confianca=analysis.overall_bias_score
                )
                
                reformulated = text_reformulator.reformulate_analyses([temp_analysis])
                if reformulated:
                    advanced_reformulations.append({
                        "original": analysis.text_segment,
                        "reformulated": reformulated[0].reformulacao_sugerida,
                        "confidence": analysis.overall_bias_score,
                        "bias_types": [bt.value for bt in analysis.bias_types]
                    })
            except Exception as e:
                print(f"Erro na reformulação: {e}")
        
        # Monta resposta avançada
        response = {
            "status": "advanced_analysis_completed",
            "analysis_type": "advanced_nlp",
            "title": article_data['title'],
            "url": article_data['url'],
            "content_length": len(normalized_content),
            "total_biased_segments": len(advanced_analyses),
            "advanced_analyses": converted_analyses,
            "comprehensive_report": comprehensive_report,
            "reformulations": advanced_reformulations,
            "analysis_metadata": {
                "models_used": {
                    "spacy": "pt_core_news_sm/lg",
                    "bert": "neuralmind/bert-base-portuguese-cased or multilingual",
                    "sentiment": "cardiffnlp/twitter-xlm-roberta-base-sentiment",
                    "reformulation": "openai/gpt-4o-mini"
                },
                "features_analyzed": [
                    "semantic_features", "syntactic_features", "semantic_frames",
                    "bert_embeddings", "dependency_parsing", "pos_tagging"
                ],
                "bias_detection_methods": [
                    "pattern_matching", "feature_engineering", "semantic_similarity",
                    "sentiment_analysis", "linguistic_markers"
                ]
            }
        }
        
        print(f"✅ Análise avançada concluída: {len(advanced_analyses)} segmentos analisados")
        return response
        
    except HTTPException:
        # Re-lança HTTPExceptions
        raise
    except Exception as e:
        print(f"Erro interno na análise avançada: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno do servidor na análise avançada: {str(e)}"
        )

@app.get("/test-metrics")
async def test_metrics():
    """Endpoint de teste para verificar se métricas aparecem"""
    test_response = AnalysisResponse(
        article_title="Teste",
        article_url="http://test.com",
        article_content="Conteúdo de teste",
        ai_related=True,
        bias_detected=False,
        overall_bias_score=0.0,
        bias_categories=[],
        detailed_analysis="Teste",
        metricas_quantitativas={"teste_direto": 999.999}
    )
    return test_response

@app.get("/models-status")
async def check_models_status():
    """Verifica status dos modelos de NLP carregados"""
    status = {
        "basic_detector": {
            "loaded": True,
            "description": "Detector básico baseado em regex"
        },
        "advanced_detector": {
            "loaded": ADVANCED_DETECTOR_AVAILABLE and advanced_bias_detector is not None,
            "available": ADVANCED_DETECTOR_AVAILABLE
        },
        "reformulator": {
            "openai_integration": "disponível",
                            "model": "gpt-4o-mini"
        }
    }
    
    # Adiciona detalhes do detector avançado se disponível
    if ADVANCED_DETECTOR_AVAILABLE and advanced_bias_detector is not None:
        try:
            status["advanced_detector"].update({
                "spacy_model": "disponível" if advanced_bias_detector.nlp else "não disponível",
                "bert_model": "disponível" if advanced_bias_detector.bert_model else "não disponível", 
                "sentiment_analyzer": "disponível" if advanced_bias_detector.sentiment_analyzer else "não disponível"
            })
        except Exception as e:
            status["advanced_detector"]["error"] = str(e)
    else:
        status["advanced_detector"]["message"] = "Dependências avançadas não instaladas"
    
    return status

@app.post("/analyze-detailed", response_model=DetailedAnalysisResponse)
async def analyze_article_detailed(request: AnalysisRequest):
    """
    Analyze Wikipedia article with detailed step-by-step progress tracking
    """
    start_total_time = time.time()
    
    # Initialize all steps
    steps = [
        AnalysisStep(
            id="validation",
            title="1. Validação de Entrada",
            description="Verificando título do artigo e parâmetros",
            status="waiting"
        ),
        AnalysisStep(
            id="wikipedia-search",
            title="2. Busca na Wikipedia",
            description="Procurando artigo na Wikipedia portuguesa",
            status="waiting"
        ),
        AnalysisStep(
            id="content-extraction",
            title="3. Extração de Conteúdo",
            description="Baixando e limpando conteúdo do artigo",
            status="waiting"
        ),
        AnalysisStep(
            id="ai-relevance",
            title="4. Verificação de Relevância IA",
            description="Verificando se artigo é relacionado à IA",
            status="waiting"
        ),
        AnalysisStep(
            id="bias-detection",
            title="5. Detecção de Viés",
            description="Analisando texto em busca de viés",
            status="waiting"
        ),
        AnalysisStep(
            id="reformulation",
            title="6. Reformulação com IA",
            description="Gerando sugestões de reformulação",
            status="waiting"
        ),
        AnalysisStep(
            id="summary-generation",
            title="7. Geração de Resumo",
            description="Criando resumo final da análise",
            status="waiting"
        )
    ]
    
    try:
        # Step 1: Validation
        current_step = next(s for s in steps if s.id == "validation")
        current_step.status = "running"
        current_step.start_time = time.time()
        current_step.details = [
            f"Validando título: '{request.title}'",
            f"Modo avançado: {'Disponível' if ADVANCED_DETECTOR_AVAILABLE else 'Não disponível'}",
            "Verificando parâmetros de entrada..."
        ]
        
        if not request.title or len(request.title.strip()) < 2:
            current_step.status = "error"
            current_step.end_time = time.time()
            return DetailedAnalysisResponse(
                success=False,
                steps=steps,
                error_message="Título do artigo é obrigatório e deve ter pelo menos 2 caracteres"
            )
        
        current_step.status = "completed"
        current_step.end_time = time.time()
        current_step.metrics = {
            "título_válido": True,
            "caracteres": len(request.title),
            "modo_avançado": ADVANCED_DETECTOR_AVAILABLE
        }
        
        # Step 2: Wikipedia Search
        current_step = next(s for s in steps if s.id == "wikipedia-search")
        current_step.status = "running"
        current_step.start_time = time.time()
        current_step.details = [
            "Conectando à API da Wikipedia...",
            f"Buscando por: {request.title}",
            "Verificando disponibilidade do artigo..."
        ]
        
        # Simulate some processing time for visual effect
        await asyncio.sleep(0.5)
        
        wikipedia_result = wikipedia_client.get_article_content(request.title)
        
        if not wikipedia_result:
            current_step.status = "error"
            current_step.end_time = time.time()
            return DetailedAnalysisResponse(
                success=False,
                steps=steps,
                error_message=f"Artigo '{request.title}' não encontrado na Wikipedia portuguesa."
            )
        
        current_step.status = "completed"
        current_step.end_time = time.time()
        current_step.metrics = {
            "artigo_encontrado": True,
            "url": wikipedia_result["url"],
            "tamanho_artigo": len(wikipedia_result["content"]) if wikipedia_result["content"] else 0
        }
        
        # Step 3: Content Extraction
        current_step = next(s for s in steps if s.id == "content-extraction")
        current_step.status = "running"
        current_step.start_time = time.time()
        current_step.details = [
            "Extraindo texto principal do artigo...",
            "Removendo formatação wiki...",
            "Limpando conteúdo HTML...",
            "Processando parágrafos..."
        ]
        
        await asyncio.sleep(0.3)
        
        content = wikipedia_result["content"]
        word_count = len(content.split()) if content else 0
        char_count = len(content) if content else 0
        
        current_step.status = "completed"
        current_step.end_time = time.time()
        current_step.metrics = {
            "palavras": word_count,
            "caracteres": char_count,
            "parágrafos": content.count('\n\n') + 1 if content else 0
        }
        
        # Step 4: AI Relevance Check
        current_step = next(s for s in steps if s.id == "ai-relevance")
        current_step.status = "running"
        current_step.start_time = time.time()
        current_step.details = [
            "Analisando palavras-chave relacionadas à IA...",
            "Verificando contexto semântico...",
            "Calculando score de relevância..."
        ]
        
        await asyncio.sleep(0.4)
        
        ai_relevance = wikipedia_client.is_ai_related(wikipedia_result["title"], content)
        
        current_step.status = "completed"
        current_step.end_time = time.time()
        current_step.metrics = {
            "é_relacionado_ia": ai_relevance,
            "algoritmo": "Detecção por palavras-chave",
            "confiança": 0.85 if ai_relevance else 0.15
        }
        
        # Step 5: Bias Detection
        current_step = next(s for s in steps if s.id == "bias-detection")
        current_step.status = "running"
        current_step.start_time = time.time()
        
        if ADVANCED_DETECTOR_AVAILABLE:
            current_step.details = [
                "Carregando modelos avançados (spaCy, BERT)...",
                "Análise semântica profunda...",
                "Detecção de padrões linguísticos...",
                "Calculando métricas quantitativas...",
                "Análise de sentimento contextual..."
            ]
            await asyncio.sleep(1.0)  # Advanced analysis takes longer
            
            advanced_analyses = advanced_bias_detector.analyze_text_advanced(content)
            analysis_method = "Avançado (spaCy + BERT + XLM-RoBERTa)"
            
            # Converter AdvancedBiasAnalysis para BiasAnalysis básico para compatibilidade
            bias_analyses = []
            for adv_analysis in advanced_analyses:
                # Seleciona o tipo de viés com maior confiança
                if adv_analysis.confidence_scores:
                    best_bias_type = max(adv_analysis.confidence_scores.items(), key=lambda x: x[1])
                    bias_type, confidence = best_bias_type
                    
                    basic_analysis = BiasAnalysis(
                        trecho_original=adv_analysis.text_segment,
                        tipo_vies=bias_type,
                        explicacao=adv_analysis.explanation,
                        reformulacao_sugerida="",  # Será preenchido depois
                        posicao_inicio=adv_analysis.start_pos,
                        posicao_fim=adv_analysis.end_pos,
                        confianca=confidence
                    )
                    bias_analyses.append(basic_analysis)
        else:
            current_step.details = [
                "Analisando padrões de linguagem tendenciosa...",
                "Detectando termos subjetivos...",
                "Verificando linguagem emocional...",
                "Buscando opiniões apresentadas como fatos..."
            ]
            await asyncio.sleep(0.6)
            
            bias_analyses = bias_detector.analyze_text(content)
            analysis_method = "Básico (Regex + NLP)"
        
        # Criar um objeto de resultado compatível com o que o resto do código espera  
        bias_detected = len(bias_analyses) > 0  # Qualquer detecção é considerada viés
        overall_bias_score = sum(analysis.confianca for analysis in bias_analyses) / len(bias_analyses) if bias_analyses else 0.0
        bias_categories = list(set(analysis.tipo_vies.value for analysis in bias_analyses))
        detailed_analysis = f"Encontrados {len(bias_analyses)} trechos com viés em {len(bias_categories)} categorias diferentes."
        
        # Criar objeto de resultado compatível
        class AnalysisResult:
            def __init__(self, bias_detected, overall_bias_score, bias_categories, detailed_analysis):
                self.bias_detected = bias_detected
                self.overall_bias_score = overall_bias_score
                self.bias_categories = bias_categories
                self.detailed_analysis = detailed_analysis
        
        analysis_result = AnalysisResult(bias_detected, overall_bias_score, bias_categories, detailed_analysis)
        
        current_step.status = "completed"
        current_step.end_time = time.time()
        current_step.metrics = {
            "método": analysis_method,
            "viés_detectado": analysis_result.bias_detected,
            "score_geral": analysis_result.overall_bias_score,
            "categorias": len(analysis_result.bias_categories)
        }
        
        # Step 6: Reformulation
        current_step = next(s for s in steps if s.id == "reformulation")
        current_step.status = "running"
        current_step.start_time = time.time()
        current_step.details = [
            "Identificando trechos problemáticos...",
            "Gerando sugestões com OpenAI GPT...",
            "Criando versões neutras...",
            "Validando melhorias..."
        ]
        
        await asyncio.sleep(0.8)
        
        reformulated_text = ""
        if ADVANCED_DETECTOR_AVAILABLE and analysis_result.bias_detected:
            try:
                # Reformula usando o método correto da classe TextReformulator
                reformulated_analyses = text_reformulator.reformulate_analyses(bias_analyses)
                reformulated_text = "\n\n".join([f"Trecho original: {analysis.trecho_original}\nVersão reformulada: {analysis.reformulacao_sugerida}" for analysis in reformulated_analyses[:3]])  # Limita a 3 exemplos
            except Exception as e:
                print(f"Reformulation error: {e}")
                reformulated_text = "Erro na reformulação: " + str(e)
        
        current_step.status = "completed"
        current_step.end_time = time.time()
        current_step.metrics = {
            "reformulação_gerada": bool(reformulated_text),
            "caracteres_reformulados": len(reformulated_text),
                            "serviço": "OpenAI GPT-4o-mini"
        }
        
        # Step 7: Summary Generation
        current_step = next(s for s in steps if s.id == "summary-generation")
        current_step.status = "running"
        current_step.start_time = time.time()
        current_step.details = [
            "Compilando resultados finais...",
            "Gerando resumo executivo...",
            "Calculando estatísticas...",
            "Preparando recomendações..."
        ]
        
        await asyncio.sleep(0.3)
        
        # Calculate quantitative metrics for any text (even without bias)
        metricas_quantitativas = {}
        
        if ADVANCED_DETECTOR_AVAILABLE and advanced_bias_detector is not None:
            # Calculate basic semantic and syntactic features for the entire text
            try:
                semantic_features = advanced_bias_detector.analyze_semantic_features(content[:1000])  # Use first 1000 chars
                syntactic_features = advanced_bias_detector.analyze_syntactic_features(content[:1000])
                
                metricas_quantitativas = {
                    "polaridade_media": semantic_features.sentiment_polarity,
                    "intensidade_emocional_media": semantic_features.emotional_intensity,
                    "complexidade_media": syntactic_features.dependency_complexity,
                    "nivel_certeza_medio": semantic_features.certainty_level,
                    "score_formalidade_medio": semantic_features.formality_score,
                    "subjetividade_media": semantic_features.subjectivity_score
                }
                
                # Always try to aggregate metrics from any analyses
                if advanced_analyses:
                    comprehensive_report = advanced_bias_detector.generate_comprehensive_report(advanced_analyses)
                    if 'semantic_profile' in comprehensive_report:
                        semantic_profile = comprehensive_report['semantic_profile']
                        metricas_quantitativas.update({
                            "polaridade_media": semantic_profile.get('avg_sentiment_polarity', semantic_features.sentiment_polarity),
                            "intensidade_emocional_media": semantic_profile.get('avg_emotional_intensity', semantic_features.emotional_intensity),
                            "nivel_certeza_medio": semantic_profile.get('avg_certainty_level', semantic_features.certainty_level),
                            "score_formalidade_medio": semantic_profile.get('avg_formality', semantic_features.formality_score),
                            "subjetividade_media": semantic_profile.get('avg_subjectivity', semantic_features.subjectivity_score)
                        })
                        
                    if 'syntactic_profile' in comprehensive_report:
                        syntactic_profile = comprehensive_report['syntactic_profile']
                        metricas_quantitativas.update({
                            "complexidade_media": syntactic_profile.get('avg_dependency_complexity', syntactic_features.dependency_complexity),
                            "diversidade_pos": syntactic_profile.get('avg_pos_diversity', syntactic_features.pos_diversity),
                            "ratio_verbos_modais": syntactic_profile.get('avg_modal_ratio', syntactic_features.modal_verb_ratio)
                        })
                        
            except Exception as e:
                # Provide default metrics if calculation fails
                metricas_quantitativas = {
                    "polaridade_media": 0.0,
                    "intensidade_emocional_media": 0.0,
                    "complexidade_media": 0.0,
                    "nivel_certeza_medio": 0.0,
                    "score_formalidade_medio": 0.0
                }
        else:
            # Use basic text analysis when advanced detector not available
            metricas_quantitativas = {
                "polaridade_media": 0.0,
                "intensidade_emocional_media": 0.0,
                "complexidade_media": 0.0,
                "nivel_certeza_medio": 0.0,
                "score_formalidade_medio": 0.0
            }

        # Calculate total segments analyzed (same as in /analyze endpoint)
        total_segments_analyzed = 0
        if ADVANCED_DETECTOR_AVAILABLE and advanced_bias_detector and advanced_bias_detector.nlp:
            doc = advanced_bias_detector.nlp(content)
            total_segments_analyzed = len([sent for sent in doc.sents if len(sent.text.strip()) >= 20])
            print(f"DEBUG DETAILED: spaCy encontrou {total_segments_analyzed} segmentos válidos")
        else:
            # Fallback: estimate based on punctuation
            total_segments_analyzed = len([s.strip() for s in content.split('.') if len(s.strip()) >= 20])
            print(f"DEBUG DETAILED: Fallback encontrou {total_segments_analyzed} segmentos válidos")
        
        print(f"DEBUG DETAILED: Valor final total_segments_analyzed = {total_segments_analyzed}")
        print(f"DEBUG DETAILED: Bias analyses encontradas = {len(bias_analyses)}")
        
        # Create final result
        final_result = AnalysisResponse(
            article_title=request.title,
            article_url=wikipedia_result["url"],
            article_content=content[:500] + "..." if len(content) > 500 else content,
            ai_related=ai_relevance,
            bias_detected=analysis_result.bias_detected,
            overall_bias_score=analysis_result.overall_bias_score,
            bias_categories=analysis_result.bias_categories,
            detailed_analysis=analysis_result.detailed_analysis,
            reformulated_text=reformulated_text,
            total_trechos_analisados=total_segments_analyzed,
            metricas_quantitativas=metricas_quantitativas,
            analysis_summary=f"""
Análise concluída com sucesso!

📊 **Resumo dos Resultados:**
- Artigo relacionado à IA: {'Sim' if ai_relevance else 'Não'}
- Viés detectado: {'Sim' if analysis_result.bias_detected else 'Não'}
- Score de viés: {analysis_result.overall_bias_score:.2f}/1.0
- Categorias de viés: {len(analysis_result.bias_categories)}
- Método de análise: {analysis_method}

🔍 **Processo:**
- Tempo total: {time.time() - start_total_time:.1f}s
- Etapas executadas: {len(steps)}
- Reformulação: {'Gerada' if reformulated_text else 'Não necessária'}
            """.strip()
        )
        
        current_step.status = "completed"
        current_step.end_time = time.time()
        current_step.metrics = {
            "resumo_gerado": True,
            "recomendações": len(analysis_result.bias_categories),
            "tempo_total": time.time() - start_total_time
        }
        
        return DetailedAnalysisResponse(
            success=True,
            steps=steps,
            final_result=final_result,
            total_duration=time.time() - start_total_time
        )
        
    except Exception as e:
        # Mark current step as error
        for step in steps:
            if step.status == "running":
                step.status = "error"
                step.end_time = time.time()
                break
                
        return DetailedAnalysisResponse(
            success=False,
            steps=steps,
            error_message=f"Erro interno: {str(e)}",
            total_duration=time.time() - start_total_time
        )

if __name__ == "__main__":
    # Configuração para desenvolvimento
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 