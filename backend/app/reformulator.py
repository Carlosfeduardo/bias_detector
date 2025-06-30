import openai
from typing import List
from .models import BiasAnalysis, BiasType
import json
import re

class TextReformulator:
    def __init__(self, api_key: str):
        openai.api_key = api_key
        self.client = openai.OpenAI(api_key=api_key)
        
        self.bias_type_descriptions = {
            BiasType.LOADED_LANGUAGE: "linguagem carregada ou tendenciosa",
            BiasType.OPINION_AS_FACT: "opinião apresentada como fato",
            BiasType.MISSING_COUNTERPOINT: "falta de contrapontos ou nuances",
            BiasType.SUBJECTIVE_TERMS: "termos subjetivos ou incertos",
            BiasType.EMOTIONAL_LANGUAGE: "linguagem emocionalmente carregada"
        }
    
    def reformulate_analyses(self, analyses: List[BiasAnalysis]) -> List[BiasAnalysis]:
        """Reformula todos os trechos com viés detectado"""
        reformulated_analyses = []
        
        for analysis in analyses:
            try:
                reformulated_text = self._reformulate_single_text(
                    analysis.trecho_original,
                    analysis.tipo_vies,
                    analysis.explicacao
                )
                
                # Atualiza a análise com a reformulação
                analysis.reformulacao_sugerida = reformulated_text
                reformulated_analyses.append(analysis)
                
            except Exception as e:
                print(f"Erro ao reformular texto: {e}")
                # Mantém o texto original se houver erro
                analysis.reformulacao_sugerida = analysis.trecho_original
                reformulated_analyses.append(analysis)
        
        return reformulated_analyses
    
    def _reformulate_single_text(self, original_text: str, bias_type: BiasType, explanation: str) -> str:
        """Reformula um único trecho de texto"""
        
        bias_description = self.bias_type_descriptions.get(bias_type, "texto tendencioso")
        
        # Cria prompt específico baseado no tipo de viés
        specific_instructions = self._get_specific_instructions(bias_type)
        
        prompt = f"""Você é um especialista em escrita neutra e objetiva. Sua tarefa é reformular textos para remover viés e torná-los mais neutros e factuais.

TEXTO ORIGINAL:
"{original_text}"

TIPO DE VIÉS DETECTADO:
{bias_description}

EXPLICAÇÃO DO PROBLEMA:
{explanation}

INSTRUÇÕES GERAIS PARA REFORMULAÇÃO:
1. Mantenha todas as informações factuais do texto original
2. Remova ou substitua termos tendenciosos por alternativas neutras
3. Adicione qualificadores quando necessário (ex: "segundo estudos", "de acordo com")
4. Evite afirmações categóricas sem evidência
5. Use linguagem mais objetiva e científica
6. Mantenha o texto em português brasileiro
7. Preserve o comprimento aproximado do texto original

INSTRUÇÕES ESPECÍFICAS PARA ESTE TIPO DE VIÉS:
{specific_instructions}

IMPORTANTE: Você DEVE modificar o texto. NÃO retorne o texto original inalterado. Faça as mudanças necessárias para torná-lo mais neutro.

TEXTO REFORMULADO:"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um especialista em escrita neutra e objetiva para textos acadêmicos e científicos. Sempre responda em português brasileiro."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            reformulated = response.choices[0].message.content.strip()
            
            # Remove possíveis prefixos da resposta
            prefixes_to_remove = [
                "TEXTO REFORMULADO:",
                "Reformulação:",
                "Versão neutra:",
                "Texto reformulado:"
            ]
            
            for prefix in prefixes_to_remove:
                if reformulated.startswith(prefix):
                    reformulated = reformulated[len(prefix):].strip()
            
            # Remove aspas se presentes
            if reformulated.startswith('"') and reformulated.endswith('"'):
                reformulated = reformulated[1:-1]
            
            return reformulated
            
        except Exception as e:
            print(f"Erro na API da OpenAI: {e}")
            return self._fallback_reformulation(original_text, bias_type)
    
    def _fallback_reformulation(self, original_text: str, bias_type: BiasType) -> str:
        """Reformulação básica caso a API falhe"""
        
        fallback_replacements = {
            # Linguagem carregada - apenas substituições seguras
            "obviamente": "de acordo com os dados",
            "claramente": "conforme observado",
            "certamente": "segundo evidências",
            "definitivamente": "com base em",
            "absolutamente": "segundo análises",
            
            # Termos exagerados
            "revolucionário": "inovador",
            "extraordinário": "notável",
            "fantástico": "significativo",
            "incrível": "relevante",
            "terrível": "problemático",
            "horrível": "inadequado",
            
            # Intensificadores e advérbios problemáticos
            "significativamente": "de forma considerável",
            "drasticamente": "de maneira acentuada",
            "extremamente": "muito",
            "tremendamente": "consideravelmente",
            "incrivelmente": "notavelmente",
            
            # Termos que implicam julgamento
            "controverso": "objeto de debate",
            "polêmico": "que gera discussão",
            "questionável": "passível de análise",
            "duvidoso": "incerto",
            "suspeito": "que requer verificação",
            
            # Absolutos problemáticos - apenas quando no início de afirmação
            " sempre ": " frequentemente ",
            " nunca ": " raramente ",
            " todos ": " a maioria dos ",
            " ninguém ": " poucos ",
            " completamente ": " amplamente ",
            " totalmente ": " substancialmente ",
            
            # Marcadores de opinião
            "deve ser": "pode ser considerado",
            "precisa ser": "seria recomendável que seja",
            "é essencial": "é considerado importante",
            "é fundamental": "é relevante",
            
            # Expressões de certeza excessiva
            "sem dúvida": "segundo análises",
            "com certeza": "provavelmente",
            "é óbvio que": "indica que",
            "é claro que": "sugere que"
        }
        
        reformulated = original_text
        
        # Aplicação mais cuidadosa das substituições
        for old_term, new_term in fallback_replacements.items():
            # Verifica se a substituição não vai gerar texto nonsense
            if old_term in reformulated.lower():
                # Para substituições de palavras isoladas, usa word boundaries
                if old_term.strip() == old_term:  # Se não tem espaços nas bordas
                    pattern = r'\b' + re.escape(old_term) + r'\b'
                    reformulated = re.sub(pattern, new_term, reformulated, flags=re.IGNORECASE)
                else:
                    # Para frases, substitui diretamente
                    reformulated = reformulated.replace(old_term, new_term)
        
        # Reformulações específicas por tipo de viés
        if bias_type == BiasType.EMOTIONAL_LANGUAGE:
            reformulated = self._apply_emotional_neutralization(reformulated)
        elif bias_type == BiasType.LOADED_LANGUAGE:
            reformulated = self._apply_loaded_language_neutralization(reformulated)
        
        return reformulated
    
    def _apply_emotional_neutralization(self, text: str) -> str:
        """Aplica neutralização específica para linguagem emocional"""
        
        # Padrões específicos para linguagem emocional
        emotional_neutralizations = {
            # Transformações contextuais para textos políticos/estatísticos
            r'\bcaíram significativamente\b': 'apresentaram redução',
            r'\btiveram ganhos reais\b': 'registraram crescimento',
            r'\bse expandiram\b': 'aumentaram',
            r'\bmelhorias significativas\b': 'melhorias observadas',
            r'\bavanços consideráveis\b': 'progressos registrados',
            r'\bprogressos extraordinários\b': 'progressos notáveis',
        }
        
        result = text
        for pattern, replacement in emotional_neutralizations.items():
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        
        return result
    
    def _apply_loaded_language_neutralization(self, text: str) -> str:
        """Aplica neutralização específica para linguagem carregada"""
        
        # Padrões específicos para linguagem carregada
        loaded_neutralizations = {
            # Julgamentos legais e políticos
            r'\bem um julgamento controverso\b': 'em um julgamento que gerou debate',
            r'\boperação controversa\b': 'operação que foi objeto de discussão',
            r'\bdecisão polêmica\b': 'decisão que dividiu opiniões',
            r'\bmedida questionável\b': 'medida que gerou questionamentos',
            r'\batitude suspeita\b': 'atitude que levantou questões',
            
            # Qualificações excessivas
            r'\bcompletamente inadequado\b': 'inadequado',
            r'\btotalmente inaceitável\b': 'inaceitável',
            r'\babsolutamente necessário\b': 'necessário',
        }
        
        result = text
        for pattern, replacement in loaded_neutralizations.items():
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        
        return result
    
    def _get_specific_instructions(self, bias_type: BiasType) -> str:
        """Retorna instruções específicas baseadas no tipo de viés"""
        
        instructions_map = {
            BiasType.EMOTIONAL_LANGUAGE: """
• Substitua advérbios intensificadores por versões mais neutras (ex: "significativamente" → "de forma considerável")
• Transforme verbos carregados emocionalmente (ex: "tiveram ganhos reais" → "registraram crescimento")
• Use termos mais técnicos e menos emocionais para descrever mudanças e resultados
• Evite palavras que implicam julgamento de valor implícito""",
            
            BiasType.LOADED_LANGUAGE: """
• Substitua termos que implicam julgamento por descrições neutras (ex: "controverso" → "que gerou debate")
• Remova qualificadores absolutos desnecessários (ex: "completamente" → remover se possível)
• Use linguagem descritiva em vez de avaliativa
• Substitua opiniões implícitas por fatos observáveis""",
            
            BiasType.OPINION_AS_FACT: """
• Adicione qualificadores que indiquem fonte ou perspectiva (ex: "é claro que" → "segundo análises")
• Transforme afirmações categóricas em declarações condicionais
• Use verbos que indiquem probabilidade ou evidência em vez de certeza absoluta""",
            
            BiasType.SUBJECTIVE_TERMS: """
• Substitua termos vagos por descrições mais específicas quando possível
• Remova ou qualifique expressões de incerteza excessiva
• Use linguagem mais precisa e técnica""",
            
            BiasType.MISSING_COUNTERPOINT: """
• Adicione qualificadores que reconheçam possíveis limitações ou perspectivas alternativas
• Use linguagem que não exclua outras possibilidades
• Adicione contexto quando apropriado"""
        }
        
        return instructions_map.get(bias_type, "• Torne o texto mais neutro e objetivo, removendo linguagem tendenciosa.")
    
    def generate_general_summary(self, analyses: List[BiasAnalysis], article_title: str) -> str:
        """Gera um resumo geral da análise de viés"""
        
        if not analyses:
            return f"Nenhum viés significativo foi detectado no artigo '{article_title}'."
        
        bias_counts = {}
        for analysis in analyses:
            bias_type = analysis.tipo_vies
            bias_counts[bias_type] = bias_counts.get(bias_type, 0) + 1
        
        summary_prompt = f"""Analise os seguintes dados sobre viés detectado no artigo da Wikipedia "{article_title}" e crie um resumo executivo em português brasileiro:

ESTATÍSTICAS DE VIÉS DETECTADO:
"""
        
        for bias_type, count in bias_counts.items():
            description = self.bias_type_descriptions[bias_type]
            summary_prompt += f"- {description}: {count} ocorrências\n"
        
        summary_prompt += f"""
TOTAL DE TRECHOS ANALISADOS: {len(analyses)}

Crie um resumo de 2-3 parágrafos que:
1. Descreva os principais tipos de viés encontrados
2. Explique o impacto potencial na neutralidade do artigo
3. Forneça recomendações gerais para melhorar a objetividade

RESUMO:"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um especialista em análise de texto e neutralidade editorial. Sempre responda em português brasileiro de forma clara e objetiva."
                    },
                    {
                        "role": "user",
                        "content": summary_prompt
                    }
                ],
                max_tokens=400,
                temperature=0.4
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Erro ao gerar resumo: {e}")
            return self._fallback_summary(bias_counts, len(analyses), article_title)
    
    def _fallback_summary(self, bias_counts: dict, total_analyses: int, article_title: str) -> str:
        """Resumo básico caso a API falhe"""
        
        summary = f"Análise do artigo '{article_title}' detectou {total_analyses} trechos com possível viés:\n\n"
        
        for bias_type, count in bias_counts.items():
            description = self.bias_type_descriptions[bias_type]
            summary += f"• {count} casos de {description}\n"
        
        summary += f"\nRecomenda-se revisar estes trechos para melhorar a neutralidade e objetividade do conteúdo."
        
        return summary 