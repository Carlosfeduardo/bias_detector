import spacy
import torch
from transformers import AutoTokenizer, AutoModel, pipeline
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from textstat import flesch_reading_ease, flesch_kincaid_grade
import networkx as nx
from collections import Counter, defaultdict
from typing import List, Dict, Tuple, Any, Optional
import re
from dataclasses import dataclass
from scipy import stats
import pandas as pd

from .models import BiasType, BiasAnalysis

@dataclass
class SemanticFeatures:
    """Características semânticas de um texto"""
    sentiment_polarity: float
    sentiment_confidence: float
    subjectivity_score: float
    emotional_intensity: float
    certainty_level: float
    formality_score: float

@dataclass
class SyntacticFeatures:
    """Características sintáticas de um texto"""
    dependency_complexity: float
    pos_diversity: float
    modal_verb_ratio: float
    passive_voice_ratio: float
    hedge_word_ratio: float
    intensifier_ratio: float

@dataclass
class AdvancedBiasAnalysis:
    """Análise avançada de viés com múltiplas dimensões"""
    text_segment: str
    start_pos: int
    end_pos: int
    bias_types: List[BiasType]
    confidence_scores: Dict[BiasType, float]
    semantic_features: SemanticFeatures
    syntactic_features: SyntacticFeatures
    explanation: str
    evidence: Dict[str, Any]
    reformulation_suggestions: List[str]
    overall_bias_score: float

class AdvancedBiasDetector:
    def __init__(self):
        self._initialize_models()
        self._load_bias_lexicons()
        self._setup_semantic_analyzers()
        
    def _initialize_models(self):
        """Inicializa todos os modelos necessários"""
        try:
            # spaCy para análise sintática e NER
            self.nlp = spacy.load("pt_core_news_lg")
            print("✓ spaCy modelo português carregado")
        except OSError:
            print("⚠️ Modelo spaCy pt_core_news_lg não encontrado. Tentando modelo básico...")
            try:
                self.nlp = spacy.load("pt_core_news_sm")
                print("✓ spaCy modelo básico carregado")
            except OSError:
                print("❌ Nenhum modelo spaCy português encontrado")
                self.nlp = None
        
        # BERT multilingual para embeddings contextuais
        self.bert_model_name = "neuralmind/bert-base-portuguese-cased"
        try:
            self.bert_tokenizer = AutoTokenizer.from_pretrained(self.bert_model_name)
            self.bert_model = AutoModel.from_pretrained(self.bert_model_name)
            print("✓ BERT português carregado")
        except Exception as e:
            print(f"⚠️ Erro ao carregar BERT português: {e}. Usando modelo multilingual...")
            self.bert_model_name = "bert-base-multilingual-cased"
            try:
                self.bert_tokenizer = AutoTokenizer.from_pretrained(self.bert_model_name)
                self.bert_model = AutoModel.from_pretrained(self.bert_model_name)
                print("✓ BERT multilingual carregado")
            except Exception as e2:
                print(f"❌ Erro ao carregar BERT: {e2}")
                self.bert_tokenizer = None
                self.bert_model = None
        
        # Pipeline de análise de sentimento
        try:
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-xlm-roberta-base-sentiment",
                tokenizer="cardiffnlp/twitter-xlm-roberta-base-sentiment",
                device=-1  # CPU
            )
            print("✓ Analisador de sentimento carregado")
        except Exception as e:
            print(f"⚠️ Erro ao carregar sentiment analyzer: {e}")
            self.sentiment_analyzer = None
    
    def _load_bias_lexicons(self):
        """Carrega léxicos especializados para detecção de viés"""
        
        # Palavras de certeza vs incerteza
        self.certainty_words = {
            'high': ['certamente', 'definitivamente', 'obviamente', 'claramente', 'inquestionavelmente',
                    'indiscutivelmente', 'sem dúvida', 'indubitavelmente', 'absolutamente'],
            'medium': ['provavelmente', 'possivelmente', 'aparentemente', 'presumivelmente'],
            'low': ['talvez', 'quiçá', 'eventualmente', 'possivelmente']
        }
        
        # Intensificadores
        self.intensifiers = [
            'muito', 'extremamente', 'bastante', 'demasiadamente', 'incrivelmente',
            'extraordinariamente', 'excepcionalmente', 'particularmente', 'especialmente'
        ]
        
        # Hedge words (palavras que suavizam afirmações)
        self.hedge_words = [
            'aparentemente', 'supostamente', 'alegadamente', 'presumivelmente',
            'parcialmente', 'relativamente', 'de certa forma', 'até certo ponto'
        ]
        
        # Verbos modais
        self.modal_verbs = [
            'deve', 'deveria', 'pode', 'poderia', 'precisa', 'precisaria',
            'tem que', 'tinha que', 'seria necessário', 'é preciso'
        ]
        
        # Palavras emocionalmente carregadas por categoria (expandido para textos políticos)
        self.emotional_lexicon = {
            'positive_extreme': ['revolucionário', 'extraordinário', 'fantástico', 'incrível', 
                               'espetacular', 'sensacional', 'maravilhoso', 'heroico', 'glorioso',
                               'excepcional', 'magnífico', 'brilhante', 'genial', 'histórico'],
            'positive_moderate': ['bom', 'interessante', 'útil', 'eficaz', 'promissor', 'competente',
                                'experiente', 'dedicado', 'comprometido', 'responsável'],
            'negative_extreme': ['terrível', 'horrível', 'desastroso', 'catastrófico', 
                               'lamentável', 'vergonhoso', 'escandaloso', 'corrupto', 'criminoso',
                               'traidor', 'mentiroso', 'incompetente', 'irresponsável'],
            'negative_moderate': ['problemático', 'inadequado', 'limitado', 'questionável',
                                'controverso', 'duvidoso', 'suspeito', 'preocupante']
        }
        
        # Frames semânticos tendenciosos (expandido para textos políticos e gerais)
        self.biased_frames = {
            'technological_determinism': [
                'mudará tudo', 'revolucionará', 'transformará completamente',
                'nunca mais será o mesmo', 'mudança radical'
            ],
            'anthropomorphism': [
                'a ia decide', 'a máquina pensa', 'o algoritmo escolhe',
                'o sistema acredita', 'a tecnologia quer'
            ],
            'fear_mongering': [
                'ameaça existencial', 'perigo iminente', 'risco catastrófico',
                'fim da humanidade', 'apocalipse tecnológico', 'crise sem precedentes',
                'desastre total', 'colapso inevitável'
            ],
            'hype_language': [
                'próxima grande revolução', 'santo graal', 'solução definitiva',
                'mudança de paradigma', 'avanço sem precedentes'
            ],
            'political_bias': [
                'sempre foi', 'nunca fez', 'todos sabem', 'é óbvio que',
                'claramente demonstra', 'sem dúvida alguma', 'qualquer pessoa sabe'
            ],
            'absolute_language': [
                'sempre', 'nunca', 'todos', 'ninguém', 'completamente',
                'totalmente', 'absolutamente', 'definitivamente', 'impossível'
            ],
            'emotional_appeals': [
                'é um escândalo', 'é uma vergonha', 'é inadmissível',
                'não se pode aceitar', 'é inaceitável', 'é revoltante'
            ]
        }
    
    def _setup_semantic_analyzers(self):
        """Configura analisadores semânticos especializados"""
        
        # Dicionário de polaridade para palavras técnicas de IA
        self.ai_polarity_lexicon = {
            # Termos neutros técnicos
            'algoritmo': 0.0, 'modelo': 0.0, 'dados': 0.0, 'treinamento': 0.0,
            'aprendizado': 0.1, 'processamento': 0.0, 'análise': 0.0,
            
            # Termos positivos
            'inovação': 0.3, 'avanço': 0.3, 'melhoria': 0.4, 'otimização': 0.2,
            'eficiência': 0.3, 'precisão': 0.2, 'acurácia': 0.2,
            
            # Termos problemáticos
            'viés': -0.4, 'erro': -0.3, 'falha': -0.4, 'limitação': -0.2,
            'problema': -0.3, 'desafio': -0.1, 'dificuldade': -0.2
        }
    
    def get_bert_embeddings(self, texts: List[str]) -> np.ndarray:
        """Obtém embeddings BERT para lista de textos"""
        if not self.bert_tokenizer or not self.bert_model:
            return np.array([])
            
        embeddings = []
        
        for text in texts:
            try:
                # Tokeniza o texto
                inputs = self.bert_tokenizer(
                    text, 
                    return_tensors="pt", 
                    truncation=True, 
                    padding=True, 
                    max_length=512
                )
                
                # Obtém embeddings
                with torch.no_grad():
                    outputs = self.bert_model(**inputs)
                    # Usa a média dos tokens como embedding da sentença
                    embedding = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
                    embeddings.append(embedding)
            except Exception as e:
                print(f"Erro ao obter embedding: {e}")
                # Fallback: embedding zero
                embeddings.append(np.zeros(768))
        
        return np.array(embeddings) if embeddings else np.array([])
    
    def analyze_semantic_features(self, text: str) -> SemanticFeatures:
        """Analisa características semânticas do texto"""
        
        # Análise de sentimento
        sentiment_score = 0.0
        sentiment_conf = 0.0
        if self.sentiment_analyzer:
            try:
                result = self.sentiment_analyzer(text)[0]
                sentiment_score = result['score'] if result['label'] == 'POSITIVE' else -result['score']
                sentiment_conf = result['score']
            except Exception as e:
                print(f"Erro na análise de sentimento: {e}")
        
        # Subjetividade baseada em marcadores linguísticos
        if self.nlp:
            doc = self.nlp(text)
            
            # Contagem de marcadores subjetivos (expandida)
            subjective_markers = 0
            total_tokens = len([token for token in doc if not token.is_space])
            
            subjective_verbs = ['acreditar', 'pensar', 'sentir', 'parecer', 'sugerir', 'imaginar', 'suspeitar', 'duvidar']
            subjective_adjs = ['incrível', 'extraordinário', 'fantástico', 'terrível', 'magnífico', 'horrível']
            
            for token in doc:
                if token.lemma_.lower() in subjective_verbs:
                    subjective_markers += 2
                if token.lemma_.lower() in subjective_adjs:
                    subjective_markers += 1.5
                if token.pos_ == 'ADV' and token.lemma_.lower() in self.hedge_words:
                    subjective_markers += 1
                # Detecta adjetivos superlativos
                if token.pos_ == 'ADJ' and ('íssimo' in token.text.lower() or 'érrimo' in token.text.lower()):
                    subjective_markers += 1
            
            subjectivity = min(subjective_markers / max(total_tokens, 1) * 15, 1.0)
            
            # Formalidade (baseada em complexidade lexical e sintática)
            formality = self._calculate_formality(doc)
        else:
            subjectivity = 0.5
            formality = 0.5
        
        # Intensidade emocional (normalizada melhor)
        emotional_words = 0
        text_words = text.lower().split()
        for category, words in self.emotional_lexicon.items():
            for word in words:
                if word in text.lower():
                    weight = 3 if 'extreme' in category else 1.5
                    emotional_words += weight
        
        # Normaliza por número de palavras, com um fator de escala melhor
        emotional_intensity = min(emotional_words / max(len(text_words), 1) * 10, 1.0)
        
        # Nível de certeza (melhorado)
        certainty_score = 0
        for level, words in self.certainty_words.items():
            for word in words:
                if word in text.lower():
                    if level == 'high':
                        certainty_score += 5
                    elif level == 'medium':
                        certainty_score += 3
                    else:
                        certainty_score += 1
        
        # Normaliza melhor e adiciona fator de escala
        certainty_level = min(certainty_score / max(len(text_words), 1) * 8, 1.0)
        
        return SemanticFeatures(
            sentiment_polarity=sentiment_score,
            sentiment_confidence=sentiment_conf,
            subjectivity_score=subjectivity,
            emotional_intensity=emotional_intensity,
            certainty_level=certainty_level,
            formality_score=formality
        )
    
    def analyze_syntactic_features(self, text: str) -> SyntacticFeatures:
        """Analisa características sintáticas do texto"""
        if not self.nlp:
            return SyntacticFeatures(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
            
        doc = self.nlp(text)
        
        # Complexidade das dependências
        dep_depths = []
        for token in doc:
            depth = self._get_dependency_depth(token)
            dep_depths.append(depth)
        
        dependency_complexity = np.mean(dep_depths) if dep_depths else 0
        
        # Diversidade de POS tags
        pos_counts = Counter([token.pos_ for token in doc if not token.is_space])
        pos_diversity = len(pos_counts) / max(len([t for t in doc if not t.is_space]), 1)
        
        # Ratio de verbos modais
        modal_count = sum(1 for token in doc if token.lemma_.lower() in self.modal_verbs)
        modal_ratio = modal_count / max(len([t for t in doc if t.pos_ == 'VERB']), 1)
        
        # Ratio de voz passiva
        passive_count = sum(1 for token in doc if 'Pass' in token.morph.get('Voice', []))
        passive_ratio = passive_count / max(len([t for t in doc if t.pos_ == 'VERB']), 1)
        
        # Ratio de hedge words
        hedge_count = sum(1 for token in doc if token.lemma_.lower() in self.hedge_words)
        hedge_ratio = hedge_count / max(len(doc), 1)
        
        # Ratio de intensificadores
        intensifier_count = sum(1 for token in doc if token.lemma_.lower() in self.intensifiers)
        intensifier_ratio = intensifier_count / max(len(doc), 1)
        
        return SyntacticFeatures(
            dependency_complexity=dependency_complexity,
            pos_diversity=pos_diversity,
            modal_verb_ratio=modal_ratio,
            passive_voice_ratio=passive_ratio,
            hedge_word_ratio=hedge_ratio,
            intensifier_ratio=intensifier_ratio
        )
    
    def _get_dependency_depth(self, token) -> int:
        """Calcula profundidade da árvore de dependências"""
        depth = 0
        current = token
        while current.head != current:
            depth += 1
            current = current.head
            if depth > 20:  # Evita loops infinitos
                break
        return depth
    
    def _calculate_formality(self, doc) -> float:
        """Calcula score de formalidade do texto"""
        formal_markers = 0
        informal_markers = 0
        
        for token in doc:
            # Marcadores formais
            if token.pos_ in ['NOUN', 'ADJ'] and len(token.text) > 6:
                formal_markers += 1
            if token.lemma_.lower() in ['todavia', 'contudo', 'portanto', 'outrossim']:
                formal_markers += 2
            
            # Marcadores informais
            if token.lemma_.lower() in ['né', 'tipo', 'meio', 'bem']:
                informal_markers += 1
        
        total_markers = formal_markers + informal_markers
        if total_markers == 0:
            return 0.5  # Neutro
        
        return formal_markers / total_markers
    
    def detect_semantic_bias(self, text: str) -> Dict[BiasType, float]:
        """Detecta viés usando análise semântica avançada"""
        bias_scores = defaultdict(float)
        
        # Análise com BERT embeddings (se disponível)
        if self.nlp:
            sentences = [sent.text for sent in self.nlp(text).sents]
            if len(sentences) > 1:
                embeddings = self.get_bert_embeddings(sentences)
                if embeddings.size > 0:
                    # Calcula diversidade semântica
                    similarities = cosine_similarity(embeddings)
                    avg_similarity = np.mean(similarities[np.triu_indices_from(similarities, k=1)])
                    
                    # Alta similaridade pode indicar falta de diversidade de perspectivas
                    if avg_similarity > 0.8:
                        bias_scores[BiasType.MISSING_COUNTERPOINT] += 0.3
        
        # Detecção de frames semânticos tendenciosos (expandido)
        text_lower = text.lower()
        for frame_type, phrases in self.biased_frames.items():
            for phrase in phrases:
                if phrase in text_lower:
                    if frame_type == 'technological_determinism':
                        bias_scores[BiasType.LOADED_LANGUAGE] += 0.4
                    elif frame_type == 'anthropomorphism':
                        bias_scores[BiasType.OPINION_AS_FACT] += 0.5
                    elif frame_type == 'fear_mongering':
                        bias_scores[BiasType.EMOTIONAL_LANGUAGE] += 0.6
                    elif frame_type == 'hype_language':
                        bias_scores[BiasType.LOADED_LANGUAGE] += 0.5
                    elif frame_type == 'political_bias':
                        bias_scores[BiasType.OPINION_AS_FACT] += 0.4
                    elif frame_type == 'absolute_language':
                        bias_scores[BiasType.LOADED_LANGUAGE] += 0.25
                    elif frame_type == 'emotional_appeals':
                        bias_scores[BiasType.EMOTIONAL_LANGUAGE] += 0.35
        
        # Análise de polaridade específica para IA
        ai_polarity_sum = 0
        ai_terms_count = 0
        for term, polarity in self.ai_polarity_lexicon.items():
            if term in text_lower:
                ai_polarity_sum += abs(polarity)
                ai_terms_count += 1
        
        if ai_terms_count > 0:
            avg_ai_polarity = ai_polarity_sum / ai_terms_count
            if avg_ai_polarity > 0.3:
                bias_scores[BiasType.LOADED_LANGUAGE] += avg_ai_polarity
        
        return dict(bias_scores)
    
    def analyze_text_advanced(self, content: str) -> List[AdvancedBiasAnalysis]:
        """Análise avançada completa do texto"""
        if not self.nlp:
            print("❌ spaCy não disponível, usando análise básica")
            return []
            
        doc = self.nlp(content)
        analyses = []
        
        # Analisa por sentenças
        segments = list(doc.sents)
        
        for segment in segments:
            segment_text = segment.text.strip()
            if len(segment_text) < 20:  # Pula segmentos muito curtos
                continue
            
            start_pos = segment.start_char
            end_pos = segment.end_char
            
            # Análises semânticas
            semantic_features = self.analyze_semantic_features(segment_text)
            
            # Análises sintáticas
            syntactic_features = self.analyze_syntactic_features(segment_text)
            
            # Detecção de viés multi-dimensional
            bias_scores = self.detect_semantic_bias(segment_text)
            
            # Detecção baseada em features
            feature_bias = self._detect_feature_based_bias(semantic_features, syntactic_features)
            
            # Combina scores
            for bias_type, score in feature_bias.items():
                bias_scores[bias_type] = max(bias_scores.get(bias_type, 0), score)
            
            # Filtra vieses significativos (threshold reduzido para detectar mais viéses sutis)
            significant_biases = {k: v for k, v in bias_scores.items() if v > 0.15}
            
            if significant_biases:
                # Calcula score geral
                overall_score = np.mean(list(significant_biases.values()))
                
                # Gera explicação detalhada
                explanation = self._generate_detailed_explanation(
                    segment_text, significant_biases, semantic_features, syntactic_features
                )
                
                # Coleta evidências
                evidence = self._collect_evidence(segment_text, significant_biases)
                
                # Gera sugestões de reformulação
                suggestions = self._generate_reformulation_suggestions(
                    segment_text, significant_biases, semantic_features
                )
                
                analysis = AdvancedBiasAnalysis(
                    text_segment=segment_text,
                    start_pos=start_pos,
                    end_pos=end_pos,
                    bias_types=list(significant_biases.keys()),
                    confidence_scores=significant_biases,
                    semantic_features=semantic_features,
                    syntactic_features=syntactic_features,
                    explanation=explanation,
                    evidence=evidence,
                    reformulation_suggestions=suggestions,
                    overall_bias_score=overall_score
                )
                
                analyses.append(analysis)
        
        return analyses
    
    def _detect_feature_based_bias(self, semantic: SemanticFeatures, syntactic: SyntacticFeatures) -> Dict[BiasType, float]:
        """Detecta viés baseado em features semânticas e sintáticas"""
        bias_scores = {}
        
        # Alta certeza + linguagem emocional = linguagem carregada (threshold reduzido)
        if semantic.certainty_level > 0.4 and semantic.emotional_intensity > 0.2:
            bias_scores[BiasType.LOADED_LANGUAGE] = semantic.certainty_level * semantic.emotional_intensity
        
        # Alta subjetividade = termos subjetivos (threshold reduzido)
        if semantic.subjectivity_score > 0.3:
            bias_scores[BiasType.SUBJECTIVE_TERMS] = semantic.subjectivity_score
        
        # Baixa formalidade + alta certeza = opinião como fato (threshold reduzido)
        if semantic.formality_score < 0.4 and semantic.certainty_level > 0.5:
            bias_scores[BiasType.OPINION_AS_FACT] = 1 - semantic.formality_score
        
        # Alta intensidade emocional = linguagem emocional (threshold reduzido)
        if semantic.emotional_intensity > 0.3:
            bias_scores[BiasType.EMOTIONAL_LANGUAGE] = semantic.emotional_intensity
        
        # Baixa diversidade sintática + alta certeza = falta de contrapontos (threshold reduzido)
        if syntactic.pos_diversity < 0.4 and semantic.certainty_level > 0.4:
            bias_scores[BiasType.MISSING_COUNTERPOINT] = semantic.certainty_level
        
        return bias_scores
    
    def _generate_detailed_explanation(self, text: str, biases: Dict[BiasType, float], 
                                     semantic: SemanticFeatures, syntactic: SyntacticFeatures) -> str:
        """Gera explicação detalhada da análise"""
        explanations = []
        
        for bias_type, score in biases.items():
            if bias_type == BiasType.LOADED_LANGUAGE:
                explanations.append(
                    f"Linguagem carregada detectada (confiança: {score:.2f}). "
                    f"O texto apresenta certeza elevada ({semantic.certainty_level:.2f}) "
                    f"combinada com intensidade emocional ({semantic.emotional_intensity:.2f})."
                )
            elif bias_type == BiasType.SUBJECTIVE_TERMS:
                explanations.append(
                    f"Termos subjetivos identificados (confiança: {score:.2f}). "
                    f"Score de subjetividade: {semantic.subjectivity_score:.2f}. "
                    f"Uso de hedge words: {syntactic.hedge_word_ratio:.2f}."
                )
            elif bias_type == BiasType.EMOTIONAL_LANGUAGE:
                explanations.append(
                    f"Linguagem emocional detectada (confiança: {score:.2f}). "
                    f"Intensidade emocional: {semantic.emotional_intensity:.2f}. "
                    f"Polaridade do sentimento: {semantic.sentiment_polarity:.2f}."
                )
            elif bias_type == BiasType.OPINION_AS_FACT:
                explanations.append(
                    f"Opinião apresentada como fato (confiança: {score:.2f}). "
                    f"Baixa formalidade ({semantic.formality_score:.2f}) com alta certeza ({semantic.certainty_level:.2f})."
                )
            elif bias_type == BiasType.MISSING_COUNTERPOINT:
                explanations.append(
                    f"Ausência de contrapontos detectada (confiança: {score:.2f}). "
                    f"Baixa diversidade sintática ({syntactic.pos_diversity:.2f}) e alta certeza."
                )
        
        return " ".join(explanations)
    
    def _collect_evidence(self, text: str, biases: Dict[BiasType, float]) -> Dict[str, Any]:
        """Coleta evidências específicas do viés detectado"""
        evidence = {}
        
        # Palavras específicas encontradas
        found_words = {
            'certainty': [w for w in sum(self.certainty_words.values(), []) if w in text.lower()],
            'emotional': [w for w in sum(self.emotional_lexicon.values(), []) if w in text.lower()],
            'hedge': [w for w in self.hedge_words if w in text.lower()],
            'intensifiers': [w for w in self.intensifiers if w in text.lower()]
        }
        
        evidence['linguistic_markers'] = {k: v for k, v in found_words.items() if v}
        
        # Frames semânticos encontrados
        found_frames = {}
        for frame_type, phrases in self.biased_frames.items():
            found = [p for p in phrases if p in text.lower()]
            if found:
                found_frames[frame_type] = found
        
        evidence['semantic_frames'] = found_frames
        
        return evidence
    
    def _generate_reformulation_suggestions(self, text: str, biases: Dict[BiasType, float], 
                                          semantic: SemanticFeatures) -> List[str]:
        """Gera múltiplas sugestões de reformulação"""
        suggestions = []
        
        # Sugestão baseada na redução de certeza
        if semantic.certainty_level > 0.6:
            suggestions.append(
                "Considere adicionar qualificadores como 'segundo estudos', 'evidências sugerem' ou 'de acordo com pesquisas'"
            )
        
        # Sugestão baseada na redução emocional
        if semantic.emotional_intensity > 0.5:
            suggestions.append(
                "Substitua termos emocionalmente carregados por alternativas mais neutras e descritivas"
            )
        
        # Sugestão baseada na objetividade
        if semantic.subjectivity_score > 0.4:
            suggestions.append(
                "Reformule afirmações subjetivas para incluir fontes ou evidências específicas"
            )
        
        # Sugestões específicas por tipo de viés
        for bias_type in biases.keys():
            if bias_type == BiasType.MISSING_COUNTERPOINT:
                suggestions.append(
                    "Considere incluir perspectivas alternativas ou limitações das tecnologias mencionadas"
                )
            elif bias_type == BiasType.OPINION_AS_FACT:
                suggestions.append(
                    "Distinga claramente entre fatos verificáveis e interpretações ou opiniões"
                )
        
        return suggestions

    def generate_comprehensive_report(self, analyses: List[AdvancedBiasAnalysis]) -> Dict[str, Any]:
        """Gera relatório abrangente da análise"""
        if not analyses:
            return {"status": "no_bias_detected", "summary": "Nenhum viés significativo detectado"}
        
        # Estatísticas gerais
        total_segments = len(analyses)
        bias_type_counts = Counter()
        confidence_scores = []
        
        for analysis in analyses:
            for bias_type in analysis.bias_types:
                bias_type_counts[bias_type] += 1
            confidence_scores.extend(analysis.confidence_scores.values())
        
        # Métricas agregadas
        avg_confidence = np.mean(confidence_scores)
        semantic_features_avg = self._aggregate_semantic_features(analyses)
        syntactic_features_avg = self._aggregate_syntactic_features(analyses)
        
        report = {
            "summary": {
                "total_biased_segments": total_segments,
                "average_confidence": avg_confidence,
                "most_common_bias": bias_type_counts.most_common(1)[0] if bias_type_counts else None
            },
            "bias_distribution": dict(bias_type_counts),
            "semantic_profile": semantic_features_avg,
            "syntactic_profile": syntactic_features_avg,
            "detailed_analyses": [
                {
                    "text": analysis.text_segment[:100] + "...",
                    "bias_types": [bt.value for bt in analysis.bias_types],
                    "overall_score": analysis.overall_bias_score,
                    "explanation": analysis.explanation
                }
                for analysis in analyses[:5]  # Top 5 para o resumo
            ],
            "recommendations": self._generate_comprehensive_recommendations(analyses)
        }
        
        return report
    
    def _aggregate_semantic_features(self, analyses: List[AdvancedBiasAnalysis]) -> Dict[str, float]:
        """Agrega features semânticas"""
        features = [a.semantic_features for a in analyses]
        return {
            "avg_sentiment_polarity": np.mean([f.sentiment_polarity for f in features]),
            "avg_subjectivity": np.mean([f.subjectivity_score for f in features]),
            "avg_emotional_intensity": np.mean([f.emotional_intensity for f in features]),
            "avg_certainty_level": np.mean([f.certainty_level for f in features]),
            "avg_formality": np.mean([f.formality_score for f in features])
        }
    
    def _aggregate_syntactic_features(self, analyses: List[AdvancedBiasAnalysis]) -> Dict[str, float]:
        """Agrega features sintáticas"""
        features = [a.syntactic_features for a in analyses]
        return {
            "avg_dependency_complexity": np.mean([f.dependency_complexity for f in features]),
            "avg_pos_diversity": np.mean([f.pos_diversity for f in features]),
            "avg_modal_ratio": np.mean([f.modal_verb_ratio for f in features]),
            "avg_passive_ratio": np.mean([f.passive_voice_ratio for f in features]),
            "avg_hedge_ratio": np.mean([f.hedge_word_ratio for f in features])
        }
    
    def _generate_comprehensive_recommendations(self, analyses: List[AdvancedBiasAnalysis]) -> List[str]:
        """Gera recomendações abrangentes"""
        recommendations = []
        
        # Analisa padrões gerais
        high_certainty_count = sum(1 for a in analyses if a.semantic_features.certainty_level > 0.7)
        high_emotion_count = sum(1 for a in analyses if a.semantic_features.emotional_intensity > 0.6)
        low_formality_count = sum(1 for a in analyses if a.semantic_features.formality_score < 0.3)
        
        if high_certainty_count > len(analyses) * 0.3:
            recommendations.append(
                "Reduza afirmações categóricas excessivas adicionando qualificadores e referências a fontes"
            )
        
        if high_emotion_count > len(analyses) * 0.2:
            recommendations.append(
                "Substitua linguagem emocionalmente carregada por termos mais técnicos e neutros"
            )
        
        if low_formality_count > len(analyses) * 0.4:
            recommendations.append(
                "Aumente o registro formal do texto para melhorar a credibilidade acadêmica"
            )
        
        recommendations.append(
            "Considere incluir perspectivas alternativas e limitações das tecnologias discutidas"
        )
        
        return recommendations 