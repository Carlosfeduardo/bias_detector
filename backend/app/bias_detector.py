import re
import spacy
import nltk
from typing import List, Tuple, Dict
from .models import BiasType, BiasAnalysis
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import statistics

class BiasDetector:
    def __init__(self):
        # Padrões mais específicos e contextualmente apropriados
        self.loaded_language_patterns = [
            # Mantém padrões realmente problemáticos
            r'\b(obviamente|claramente|certamente|inquestionavelmente|indiscutivelmente)\s+(?:será|vai|irá|deve)',
            r'\b(revolucionário|extraordinário|fantástico|incrível|impressionante|sensacional)\s+(?:avanço|descoberta|tecnologia)',
            r'\b(terrível|horrível|desastroso|catastrófico|lamentável|vergonhoso)\s+(?:para|na|da)',
            r'\b(sempre|nunca|todos|ninguém|completamente|totalmente|absolutamente)\s+(?:será|vai|pode|deve|irá)',
            r'\b(definitivamente|absolutamente|indubitavelmente|inquestionavelmente)\s+(?:mudará|transformará|revolucionará)',
            # Remove padrões que são comuns em textos técnicos
            # r'\b(principal|primário|mais importante|fundamental|essencial)\b',  # REMOVIDO - comum em textos técnicos
            # r'\b(amplamente|vastamente|enormemente)\s+(?:usado|aceito|reconhecido)',  # REMOVIDO - estatísticas válidas
        ]
        
        # Padrões científicos ACEITOS (whitelist) - não devem ser flagrados como viés
        self.scientific_acceptable_patterns = [
            r'\b(?:forte(?:s)?|significante(?:s)?|importante(?:s)?)\s+(?:correlação|relação|ligação|associação|laços?)',
            r'\b(?:amplamente|vastamente|largamente)\s+(?:usado|utilizado|aceito|reconhecido|estudado)',
            r'\b(?:principal|primário|fundamental|essencial|básico)\s+(?:método|abordagem|técnica|algoritmo|modelo)',
            r'\b(?:diretamente|intimamente|estreitamente)\s+(?:ligado|relacionado|conectado|associado)',
            r'\bproduz\s+(?:métodos?|resultados?|dados?|evidências?)',
            r'\b(?:método|abordagem|técnica)\s+(?:eficaz|eficiente|robusta?|confiável)',
        ]
        
        # Novos padrões para IA - mais específicos para viés real
        self.technological_determinism_patterns = [
            r'\b(mudará tudo|revolucionará|transformará completamente)\b',
            r'\b(nunca mais será o mesmo|mudança radical|paradigma totalmente novo)\b',
            r'\b(substituirá|eliminará|tornará obsoleto)\s+(?:todos|todas)',
            r'\b(inevitavelmente|inexoravelmente)\s+(?:mudará|transformará)',
            r'\b(fim da|morte da|extinção da)\s+(?:era|época)',
            r'\bIA\s+(?:vai|irá)\s+(?:dominar|controlar|substituir)\s+(?:tudo|todos)',
        ]
        
        self.anthropomorphism_patterns = [
            r'\b(?:a|o)\s+(?:ia|algoritmo|sistema|máquina|computador|robô)\s+(?:decide|pensa|escolhe|quer|deseja|acredita|sente|entende|compreende)\b',
            r'\b(?:inteligência|capacidade|habilidade)\s+(?:artificial|da máquina)\s+(?:compreende|entende|aprende|raciocina|pensa)\b',
            r'\b(?:sistemas?|algoritmos?)\s+(?:inteligentes?|conscientes?|pensantes?|sábios?)\b',
            r'\b(?:máquinas?|robôs?)\s+(?:sentem|pensam|querem|desejam)\b',
            r'\b(?:os|as)\s+(?:algoritmos?|máquinas?)\s+(?:pensam|decidem)\b',
            r'\b(?:algoritmos?|máquinas?)\s+(?:são\s+)?(?:melhores?|superiores?)\s+(?:que|do\s+que)\s+(?:humanos?|pessoas?)\b'
        ]
        
        self.hype_language_patterns = [
            r'\b(próxima grande revolução|santo graal|solução definitiva)\b',
            r'\b(mudança de paradigma|avanço sem precedentes|breakthrough)\b',
            r'\b(game changer|disruptivo|inovação radical)\b',
            r'\b(vai mudar o mundo|transformação histórica)\b',
            r'\bIA\s+(?:é|será)\s+(?:a solução|o futuro|revolucionária)\b'
        ]
        
        self.fear_mongering_patterns = [
            r'\b(ameaça existencial|perigo iminente|risco catastrófico)\b',
            r'\b(fim da humanidade|apocalipse tecnológico|cenário distópico)\b',
            r'\b(controlará|dominará|escravizará)\s+(?:a humanidade|os humanos)\b',
            r'\b(skynet|matrix|terminator)\b',
            r'\bIA\s+(?:vai|irá)\s+(?:destruir|eliminar|acabar com)\b'
        ]
        
        self.subjective_indicators = [
            r'\b(acredita-se|pensa-se|considera-se|imagina-se)\b',
            r'\b(parece|aparenta|sugere|indica|implica)\b',
            r'\b(provavelmente|possivelmente|talvez|certamente)\b',
            r'\b(deveria|poderia|seria melhor|é necessário)\b',
            r'\b(frequentemente|geralmente|normalmente|tipicamente)\b',
            r'\b(tende a|tem tendência|costuma)\b',
            r'\b(muitas vezes|várias vezes|na maioria das vezes)\b',
            r'\b(pode ser|pode estar|poderia ser)\b'
        ]
        
        self.opinion_markers = [
            r'\b(na minha opinião|em minha opinião|acredito que|penso que)\b',
            r'\b(é importante|é essencial|é fundamental|é crucial)\b',
            r'\b(deve-se|devemos|precisamos|é preciso)\b'
        ]
        
        self.emotional_language = [
            r'\b(emocionante|empolgante|assustador|preocupante|alarmante)\b',
            r'\b(surpreendente|chocante|inacreditável|impressionante)\b',
            r'\b(maravilhoso|terrível|fantástico|horrível)\b'
        ]
        
        self.false_certainty_patterns = [
            r'\b(com certeza|sem dúvida|comprovadamente)\s+(?:irá|será|vai)\b',
            r'\b(está provado|é comprovado|cientificamente comprovado)\b',
            r'\b(todos os especialistas|a ciência|estudos)\s+(?:concordam|mostram|provam)\b',
            r'\b(?:esta|isso)\s+(?:é|será)\s+(?:definitivamente|certamente)\s+(?:a|o)\s+(?:solução|resposta)\b',
            r'\b(?:definitivamente|certamente)\s+(?:a|o)\s+(?:melhor|única|principal)\s+(?:solução|forma|maneira)\b'
        ]
        
        # Inicializa spacy se disponível
        try:
            self.nlp = spacy.load("pt_core_news_sm")
        except OSError:
            print("Modelo spacy português não encontrado. Usando análise básica.")
            self.nlp = None
    
    def analyze_text(self, content: str) -> List[BiasAnalysis]:
        """Analisa o texto completo e retorna lista de viés detectados com métricas"""
        analyses = []
        
        # Divide o texto em sentenças
        sentences = self._split_into_sentences(content)
        
        for sentence in sentences:
            sentence_analyses = self._analyze_sentence(sentence, content)
            analyses.extend(sentence_analyses)
        
        # Remove duplicatas e ordena por posição
        analyses = self._remove_duplicates(analyses)
        analyses.sort(key=lambda x: x.posicao_inicio)
        
        # Adiciona métricas quantitativas
        analyses = self._add_quantitative_metrics(analyses, content)
        
        return analyses
    
    def _add_quantitative_metrics(self, analyses: List[BiasAnalysis], full_text: str) -> List[BiasAnalysis]:
        """Adiciona métricas quantitativas a cada análise"""
        for analysis in analyses:
            sentence = analysis.trecho_original
            
            # Intensidade emocional (baseada em palavras emocionalmente carregadas)
            analysis.intensidade_emocional = self._calculate_emotional_intensity(sentence)
            
            # Polaridade do sentimento (simplificada)
            analysis.polaridade_sentimento = self._calculate_sentiment_polarity(sentence)
            
            # Complexidade sintática
            analysis.complexidade_sintatica = self._calculate_syntactic_complexity(sentence)
            
            # Nível de certeza
            analysis.nivel_certeza = self._calculate_certainty_level(sentence)
            
            # Score de formalidade
            analysis.score_formalidade = self._calculate_formality_score(sentence)
            
            # Ajusta confiança baseada nas métricas
            analysis.confianca = self._adjust_confidence_with_metrics(analysis)
        
        return analyses
    
    def _calculate_emotional_intensity(self, text: str) -> float:
        """Calcula intensidade emocional do texto"""
        emotional_words = [
            'revolucionário', 'extraordinário', 'fantástico', 'incrível', 'terrível', 
            'horrível', 'maravilhoso', 'assustador', 'emocionante', 'chocante'
        ]
        
        intensifiers = ['muito', 'extremamente', 'bastante', 'tremendamente', 'incrivelmente']
        
        text_lower = text.lower()
        emotional_count = sum(1 for word in emotional_words if word in text_lower)
        intensifier_count = sum(1 for word in intensifiers if word in text_lower)
        
        base_intensity = emotional_count / max(len(text.split()), 1)
        intensifier_boost = intensifier_count * 0.2
        
        return min(base_intensity + intensifier_boost, 1.0)
    
    def _calculate_sentiment_polarity(self, text: str) -> float:
        """Calcula polaridade do sentimento (-1 a 1)"""
        positive_words = [
            'bom', 'excelente', 'ótimo', 'maravilhoso', 'fantástico', 'incrível',
            'eficaz', 'útil', 'valioso', 'importante', 'inovador', 'revolucionário'
        ]
        
        negative_words = [
            'ruim', 'péssimo', 'terrível', 'horrível', 'problemático', 'limitado',
            'inadequado', 'ineficaz', 'perigoso', 'preocupante', 'alarmante'
        ]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        total_count = positive_count + negative_count
        if total_count == 0:
            return 0.0
        
        return (positive_count - negative_count) / total_count
    
    def _calculate_syntactic_complexity(self, text: str) -> float:
        """Calcula complexidade sintática"""
        if self.nlp:
            doc = self.nlp(text)
            
            # Conta subordinadas e dependências complexas
            complex_deps = ['acl', 'advcl', 'ccomp', 'xcomp']
            complex_count = sum(1 for token in doc if token.dep_ in complex_deps)
            
            # Tamanho médio das frases
            avg_sentence_length = len(doc) / max(len(list(doc.sents)), 1)
            
            return min((complex_count * 0.1) + (avg_sentence_length * 0.02), 1.0)
        else:
            # Análise simples sem spaCy
            subordinating_words = ['que', 'quando', 'onde', 'como', 'porque', 'embora', 'apesar']
            subordinating_count = sum(1 for word in subordinating_words if word in text.lower())
            word_count = len(text.split())
            
            return min((subordinating_count * 0.1) + (word_count * 0.01), 1.0)
    
    def _calculate_certainty_level(self, text: str) -> float:
        """Calcula nível de certeza das afirmações"""
        certainty_words = [
            'certamente', 'definitivamente', 'obviamente', 'claramente',
            'sem dúvida', 'comprovadamente', 'inquestionavelmente'
        ]
        
        uncertainty_words = [
            'talvez', 'possivelmente', 'provavelmente', 'aparentemente',
            'supostamente', 'pode ser', 'poderia ser'
        ]
        
        text_lower = text.lower()
        certainty_count = sum(1 for word in certainty_words if word in text_lower)
        uncertainty_count = sum(1 for word in uncertainty_words if word in text_lower)
        
        total_words = len(text.split())
        certainty_ratio = certainty_count / max(total_words, 1)
        uncertainty_ratio = uncertainty_count / max(total_words, 1)
        
        return min(max(certainty_ratio - uncertainty_ratio + 0.5, 0.0), 1.0)
    
    def _calculate_formality_score(self, text: str) -> float:
        """Calcula score de formalidade"""
        informal_words = [
            'tipo', 'né', 'cara', 'mano', 'galera', 'pessoal',
            'super', 'mega', 'hiper', 'muito louco', 'demais'
        ]
        
        formal_indicators = [
            'portanto', 'todavia', 'contudo', 'outrossim', 'destarte',
            'mediante', 'conforme', 'consoante'
        ]
        
        text_lower = text.lower()
        informal_count = sum(1 for word in informal_words if word in text_lower)
        formal_count = sum(1 for word in formal_indicators if word in text_lower)
        
        total_words = len(text.split())
        informal_ratio = informal_count / max(total_words, 1)
        formal_ratio = formal_count / max(total_words, 1)
        
        return min(max(formal_ratio - informal_ratio + 0.5, 0.0), 1.0)
    
    def _adjust_confidence_with_metrics(self, analysis: BiasAnalysis) -> float:
        """Ajusta confiança baseada nas métricas calculadas"""
        base_confidence = analysis.confianca
        
        # Fatores de ajuste baseados nas métricas
        intensity_factor = 1.0 + (analysis.intensidade_emocional * 0.2)
        polarity_factor = 1.0 + (abs(analysis.polaridade_sentimento) * 0.15)
        certainty_factor = 1.0 + (analysis.nivel_certeza * 0.1)
        
        adjusted_confidence = base_confidence * intensity_factor * polarity_factor * certainty_factor
        
        return min(adjusted_confidence, 1.0)

    def _split_into_sentences(self, text: str) -> List[str]:
        """Divide o texto em sentenças"""
        if self.nlp:
            doc = self.nlp(text)
            return [sent.text.strip() for sent in doc.sents if len(sent.text.strip()) > 10]
        else:
            # Fallback simples
            sentences = re.split(r'[.!?]+', text)
            return [s.strip() for s in sentences if len(s.strip()) > 10]
    
    def _analyze_sentence(self, sentence: str, full_text: str) -> List[BiasAnalysis]:
        """Analisa uma sentença individual com contexto melhorado"""
        analyses = []
        
        # Lista de métodos de detecção com prioridade
        detection_methods = [
            self._detect_technological_determinism,
            self._detect_anthropomorphism,
            self._detect_hype_language,
            self._detect_fear_mongering,
            self._detect_false_certainty,
            self._detect_loaded_language,
            self._detect_subjective_terms,
            self._detect_opinion_as_fact,
            self._detect_emotional_language,
            self._detect_missing_counterpoint
        ]
        
        # Skip sentenças muito curtas ou que são claramente técnicas
        if len(sentence.strip()) < 20:
            return analyses
            
        # Skip definições técnicas básicas
        technical_definition_patterns = [
            r'^\s*[A-Z][a-z\s]+é\s+(?:um|uma|o|a)\s+(?:método|técnica|algoritmo|modelo|processo)',
            r'^\s*(?:Algoritmos?|Modelos?|Sistemas?|Redes?)\s+(?:de|para|que)',
        ]
        
        for pattern in technical_definition_patterns:
            if re.match(pattern, sentence, re.IGNORECASE):
                return analyses  # Skip definições técnicas básicas
        
        # Aplicar métodos de detecção
        for detection_method in detection_methods:
            try:
                result = detection_method(sentence)
                if result and result[0] is not None:
                    bias_type, confidence, explanation = result
                    
                    # Verifica se já existe análise similar para esta sentença
                    existing_similar = any(
                        a.tipo_vies == bias_type and abs(a.confianca - confidence) < 0.2 
                        for a in analyses
                    )
                    
                    if not existing_similar and confidence > 0.3:  # Threshold mínimo
                        # Calcula posição no texto completo
                        start_pos = full_text.find(sentence)
                        end_pos = start_pos + len(sentence) if start_pos != -1 else 0
                        
                        analysis = BiasAnalysis(
                            trecho_original=sentence.strip(),
                            tipo_vies=bias_type,
                            explicacao=explanation,
                            reformulacao_sugerida="",
                            posicao_inicio=start_pos,
                            posicao_fim=end_pos,
                            confianca=confidence,
                            # Métricas serão adicionadas posteriormente
                            intensidade_emocional=0.0,
                            polaridade_sentimento=0.0,
                            complexidade_sintatica=0.0,
                            nivel_certeza=0.0,
                            score_formalidade=0.0
                        )
                        analyses.append(analysis)
                        
            except Exception as e:
                print(f"Erro na detecção {detection_method.__name__}: {e}")
                continue
        
        return analyses
    
    def _detect_technological_determinism(self, sentence: str) -> Tuple[BiasType, float, str]:
        """Detecta determinismo tecnológico"""
        matches = []
        sentence_lower = sentence.lower()
        
        for pattern in self.technological_determinism_patterns:
            pattern_matches = re.finditer(pattern, sentence_lower, re.IGNORECASE)
            matches.extend([match.group() for match in pattern_matches])
        
        if matches:
            confidence = min(len(matches) * 0.4 + 0.3, 1.0)
            explanation = f"Detectado determinismo tecnológico: {', '.join(set(matches))}. A tecnologia é apresentada como force inevitável que determinará mudanças."
            return BiasType.TECHNOLOGICAL_DETERMINISM, confidence, explanation
        
        return None, 0.0, ""
    
    def _detect_anthropomorphism(self, sentence: str) -> Tuple[BiasType, float, str]:
        """Detecta antropomorfismo"""
        matches = []
        sentence_lower = sentence.lower()
        
        for pattern in self.anthropomorphism_patterns:
            pattern_matches = re.finditer(pattern, sentence_lower, re.IGNORECASE)
            matches.extend([match.group() for match in pattern_matches])
        
        if matches:
            confidence = min(len(matches) * 0.35 + 0.4, 1.0)
            explanation = f"Detectado antropomorfismo: {', '.join(set(matches))}. Máquinas descritas com características humanas."
            return BiasType.ANTHROPOMORPHISM, confidence, explanation
        
        return None, 0.0, ""
    
    def _detect_hype_language(self, sentence: str) -> Tuple[BiasType, float, str]:
        """Detecta linguagem sensacionalista/hype"""
        matches = []
        sentence_lower = sentence.lower()
        
        for pattern in self.hype_language_patterns:
            pattern_matches = re.finditer(pattern, sentence_lower, re.IGNORECASE)
            matches.extend([match.group() for match in pattern_matches])
        
        if matches:
            confidence = min(len(matches) * 0.3 + 0.35, 1.0)
            explanation = f"Detectada linguagem sensacionalista: {', '.join(set(matches))}. Uso de termos exagerados para promover tecnologia."
            return BiasType.HYPE_LANGUAGE, confidence, explanation
        
        return None, 0.0, ""
    
    def _detect_fear_mongering(self, sentence: str) -> Tuple[BiasType, float, str]:
        """Detecta alarmismo"""
        matches = []
        sentence_lower = sentence.lower()
        
        for pattern in self.fear_mongering_patterns:
            pattern_matches = re.finditer(pattern, sentence_lower, re.IGNORECASE)
            matches.extend([match.group() for match in pattern_matches])
        
        if matches:
            confidence = min(len(matches) * 0.45 + 0.4, 1.0)
            explanation = f"Detectado alarmismo: {', '.join(set(matches))}. Uso de linguagem que gera medo desnecessário sobre IA."
            return BiasType.FEAR_MONGERING, confidence, explanation
        
        return None, 0.0, ""
    
    def _detect_false_certainty(self, sentence: str) -> Tuple[BiasType, float, str]:
        """Detecta falsa certeza"""
        matches = []
        sentence_lower = sentence.lower()
        
        for pattern in self.false_certainty_patterns:
            pattern_matches = re.finditer(pattern, sentence_lower, re.IGNORECASE)
            matches.extend([match.group() for match in pattern_matches])
        
        if matches:
            confidence = min(len(matches) * 0.35 + 0.3, 1.0)
            explanation = f"Detectada falsa certeza: {', '.join(set(matches))}. Afirmações categóricas sem evidências adequadas."
            return BiasType.FALSE_CERTAINTY, confidence, explanation
        
        return None, 0.0, ""

    def _detect_loaded_language(self, sentence: str) -> Tuple[BiasType, float, str]:
        """Detecta linguagem carregada com contexto científico"""
        
        # Primeiro verifica se o texto contém terminologia científica aceitável
        sentence_lower = sentence.lower()
        for acceptable_pattern in self.scientific_acceptable_patterns:
            if re.search(acceptable_pattern, sentence_lower, re.IGNORECASE):
                return None, 0.0, ""  # Não flagra textos científicos legítimos
        
        matches = []
        for pattern in self.loaded_language_patterns:
            pattern_matches = re.finditer(pattern, sentence_lower, re.IGNORECASE)
            matches.extend([match.group() for match in pattern_matches])
        
        if matches:
            # Reduz confiança para contextos científicos
            base_confidence = len(matches) * 0.25 + 0.3
            
            # Verifica contexto científico (reduz confiança)
            scientific_terms = ['algoritmo', 'modelo', 'dados', 'análise', 'estudo', 'pesquisa', 'evidência', 'resultado']
            has_scientific_context = any(term in sentence_lower for term in scientific_terms)
            
            if has_scientific_context:
                base_confidence *= 0.6  # Reduz confiança em 40% para contextos científicos
            
            sentence_length_factor = len(sentence.split()) / 20.0
            confidence = min(base_confidence + sentence_length_factor * 0.1, 1.0)
            
            # Só reporta se confiança for maior que threshold
            if confidence > 0.4:
                explanation = f"Detectada linguagem carregada com termos como: {', '.join(set(matches))}. Estes termos podem influenciar a percepção do leitor de forma tendenciosa."
                return BiasType.LOADED_LANGUAGE, confidence, explanation
        
        return None, 0.0, ""
    
    def _detect_subjective_terms(self, sentence: str) -> Tuple[BiasType, float, str]:
        """Detecta termos subjetivos com contexto melhorado"""
        matches = []
        sentence_lower = sentence.lower()
        
        # Padrões subjetivos mais específicos
        subjective_patterns = [
            r'\b(acredita-se|pensa-se|considera-se|imagina-se)\s+(?:que)',
            r'\b(parece|aparenta)\s+(?:que|ser|estar)',
            r'\b(provavelmente|possivelmente|talvez)\s+(?:vai|será|pode)',
            r'\b(deveria|poderia|seria melhor)\s+(?:que|se|para)',
            r'\b(na minha opinião|acredito que|penso que)\b'
        ]
        
        for pattern in subjective_patterns:
            pattern_matches = re.finditer(pattern, sentence_lower, re.IGNORECASE)
            matches.extend([match.group() for match in pattern_matches])
        
        if matches:
            # Verifica se há contexto científico que justifica a subjetividade
            scientific_subjectivity_ok = [
                'estudo sugere', 'pesquisa indica', 'evidência aponta',
                'dados sugerem', 'análise mostra', 'resultados indicam'
            ]
            
            has_scientific_justification = any(term in sentence_lower for term in scientific_subjectivity_ok)
            
            if has_scientific_justification:
                return None, 0.0, ""  # Subjetividade científica é aceitável
            
            base_confidence = len(matches) * 0.2 + 0.3
            confidence = min(base_confidence, 0.85)
            
            if confidence > 0.4:
                explanation = f"Encontrados indicadores subjetivos: {', '.join(set(matches))}. Estes termos introduzem incerteza ou opinião pessoal sem base científica clara."
                return BiasType.SUBJECTIVE_TERMS, confidence, explanation
        
        return None, 0.0, ""
    
    def _detect_opinion_as_fact(self, sentence: str) -> Tuple[BiasType, float, str]:
        """Detecta opiniões apresentadas como fatos - específico para textos de IA"""
        matches = []
        sentence_lower = sentence.lower()
        
        # Padrões específicos para afirmações categóricas sem evidência em IA
        opinion_patterns = [
            r'\bIA\s+(?:é|será|vai ser)\s+(?:melhor|superior|mais eficiente)\s+(?:que|do que)',
            r'\b(?:é|são)\s+(?:o|a|os|as)\s+(?:melhor|única|principal)\s+(?:forma|maneira|solução)',
            r'\b(?:deve|devem|precisa|precisam)\s+(?:usar|adotar|implementar)\s+IA',
            r'\b(?:é óbvio|é claro|todos sabem)\s+que',
            r'\bIA\s+(?:sempre|nunca|definitivamente)\s+(?:vai|irá|pode)',
            r'\b(?:sem dúvida|certamente|obviamente)\s+(?:a IA|os algoritmos)'
        ]
        
        for pattern in opinion_patterns:
            pattern_matches = re.finditer(pattern, sentence_lower, re.IGNORECASE)
            matches.extend([match.group() for match in pattern_matches])
        
        if matches:
            # Verifica se há citação de evidências
            has_evidence = any(term in sentence_lower for term in [
                'estudo', 'pesquisa', 'dados', 'evidência', 'resultado',
                'análise', 'experimento', 'segundo', 'de acordo com'
            ])
            
            if has_evidence:
                return None, 0.0, ""  # OK se há evidências citadas
            
            confidence = min(len(matches) * 0.3 + 0.4, 0.9)
            
            if confidence > 0.5:
                explanation = f"Detectadas afirmações categóricas sobre IA sem evidências: {', '.join(set(matches))}. Podem ser opiniões apresentadas como fatos."
                return BiasType.OPINION_AS_FACT, confidence, explanation
        
        return None, 0.0, ""
    
    def _detect_emotional_language(self, sentence: str) -> Tuple[BiasType, float, str]:
        """Detecta linguagem emocional"""
        matches = []
        sentence_lower = sentence.lower()
        
        for pattern in self.emotional_language:
            pattern_matches = re.finditer(pattern, sentence_lower, re.IGNORECASE)
            matches.extend([match.group() for match in pattern_matches])
        
        if matches:
            confidence = min(len(matches) * 0.25 + 0.3, 1.0)
            explanation = f"Detectada linguagem emocional: {', '.join(set(matches))}. Termos emocionalmente carregados podem influenciar a objetividade."
            return BiasType.EMOTIONAL_LANGUAGE, confidence, explanation
        
        return None, 0.0, ""
    
    def _detect_missing_counterpoint(self, sentence: str) -> Tuple[BiasType, float, str]:
        """Detecta ausência de contrapontos com foco em afirmações absolutas sobre IA"""
        # Identifica afirmações muito categóricas sem nuances específicas para IA
        categorical_indicators = [
            r'\b(?:máquinas?|algoritmos?|IA|inteligência artificial)\s+(?:sempre|nunca|completamente|totalmente)\b',
            r'\b(?:sempre|nunca|todos|ninguém|completamente|totalmente)\s+(?:será|vai|pode|deve|irá)',
            r'\b(?:impossível|inviável|inevitável|inquestionável)\s+(?:que|para|de)',
            r'\b(?:único|exclusivo|somente|apenas)\s+(?:forma|maneira|modo|jeito|solução)',
            r'\b(?:certamente|definitivamente)\s+(?:vão|irão|vai|irá)\s+(?:dominar|controlar|substituir)\b'
        ]
        
        matches = []
        sentence_lower = sentence.lower()
        
        for pattern in categorical_indicators:
            pattern_matches = re.finditer(pattern, sentence_lower, re.IGNORECASE)
            matches.extend([match.group() for match in pattern_matches])
        
        if matches and len(sentence) > 60:  # Apenas para sentenças mais longas
            # Verifica se há qualificadores que reduzem a certeza
            qualifiers = ['pode ser', 'talvez', 'possivelmente', 'em alguns casos', 'frequentemente', 'geralmente']
            has_qualifiers = any(q in sentence_lower for q in qualifiers)
            
            if has_qualifiers:
                return None, 0.0, ""  # OK se há qualificadores
                
            confidence = min(len(matches) * 0.2 + 0.35, 0.85)
            explanation = f"Detectadas afirmações categóricas: {', '.join(set(matches))}. Podem beneficiar-se de contrapontos ou nuances adicionais."
            return BiasType.MISSING_COUNTERPOINT, confidence, explanation
        
        return None, 0.0, ""
    
    def _remove_duplicates(self, analyses: List[BiasAnalysis]) -> List[BiasAnalysis]:
        """Remove análises duplicadas baseadas na posição"""
        seen_positions = set()
        unique_analyses = []
        
        for analysis in analyses:
            pos_key = (analysis.posicao_inicio, analysis.posicao_fim, analysis.tipo_vies)
            if pos_key not in seen_positions:
                seen_positions.add(pos_key)
                unique_analyses.append(analysis)
        
        return unique_analyses

    def _is_scientific_context_acceptable(self, sentence: str, detected_terms: List[str]) -> bool:
        """Verifica se os termos detectados são aceitáveis no contexto científico"""
        sentence_lower = sentence.lower()
        
        # Contextos onde linguagem "forte" é aceitável
        scientific_contexts = [
            'correlação', 'relação', 'ligação', 'associação', 'laços',
            'método', 'abordagem', 'técnica', 'algoritmo', 'modelo',
            'evidência', 'resultado', 'dado', 'análise', 'estudo'
        ]
        
        # Verifica se algum termo científico está próximo aos termos detectados
        for term in detected_terms:
            term_pos = sentence_lower.find(term.lower())
            if term_pos != -1:
                # Verifica contexto de 50 caracteres antes e depois
                context_start = max(0, term_pos - 50)
                context_end = min(len(sentence_lower), term_pos + len(term) + 50)
                context = sentence_lower[context_start:context_end]
                
                for sci_term in scientific_contexts:
                    if sci_term in context:
                        return True
        
        return False 