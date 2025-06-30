import requests
from typing import Optional, Dict, Any
import re

class WikipediaClient:
    def __init__(self):
        self.base_url = "https://pt.wikipedia.org/api/rest_v1"
        self.api_url = "https://pt.wikipedia.org/w/api.php"
        
    def search_article(self, title: str) -> Optional[str]:
        """Busca o título exato do artigo na Wikipedia"""
        params = {
            'action': 'query',
            'format': 'json',
            'list': 'search',
            'srsearch': title,
            'srlimit': 1,
            'srnamespace': 0
        }
        
        try:
            response = requests.get(self.api_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            if data.get('query', {}).get('search'):
                return data['query']['search'][0]['title']
            return None
            
        except Exception as e:
            print(f"Erro ao buscar artigo: {e}")
            return None

    def get_article_content(self, title: str) -> Optional[Dict[str, Any]]:
        """Obtém o conteúdo completo do artigo"""
        try:
            # Primeiro, busca o título correto
            correct_title = self.search_article(title)
            if not correct_title:
                return None
            
            # Busca o conteúdo do artigo
            params = {
                'action': 'query',
                'format': 'json',
                'titles': correct_title,
                'prop': 'extracts',
                'exintro': False,
                'explaintext': True,
                'exsectionformat': 'plain'
            }
            
            response = requests.get(self.api_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            pages = data.get('query', {}).get('pages', {})
            
            if not pages:
                return None
                
            page = next(iter(pages.values()))
            
            if 'extract' not in page:
                return None
                
            content = page['extract']
            # Remove referências e limpa o texto
            content = self._clean_content(content)
            
            return {
                'title': correct_title,
                'content': content,
                'url': f"https://pt.wikipedia.org/wiki/{correct_title.replace(' ', '_')}"
            }
            
        except Exception as e:
            print(f"Erro ao obter conteúdo: {e}")
            return None
    
    def _clean_content(self, content: str) -> str:
        """Limpa o conteúdo removendo referências e formatação"""
        # Remove referências [1], [2], etc.
        content = re.sub(r'\[\d+\]', '', content)
        
        # Remove linhas vazias múltiplas
        content = re.sub(r'\n\s*\n', '\n\n', content)
        
        # Remove espaços extras
        content = re.sub(r' +', ' ', content)
        
        return content.strip()
    
    def is_ai_related(self, title: str, content: str) -> bool:
        """Verifica se o artigo é relacionado à Inteligência Artificial"""
        # Palavras que devem ser encontradas como palavras completas
        ai_keywords_exact = [
            'inteligência artificial', 'machine learning', 'aprendizado de máquina',
            'deep learning', 'aprendizado profundo', 'redes neurais', 
            'processamento de linguagem natural', 'visão computacional', 
            'data science', 'ciência de dados', 'big data',
            'mineração de dados', 'reconhecimento de padrões', 'chatbot',
            'neural network', 'algoritmo genético', 'sistema especialista'
        ]
        
        # Palavras que precisam de word boundary (palavras completas)
        ai_keywords_word_boundary = [
            r'\bia\b',  # "ia" como palavra completa, não como parte de "brasileiro"
            r'\bbot\b', # "bot" como palavra completa
            r'\bpln\b', # PLN como palavra completa
            r'\bml\b',  # ML como palavra completa
            r'\bal\b'   # AI em inglês
        ]
        
        # Termos específicos que indicam IA
        ai_technical_terms = [
            'algoritmo de aprendizado', 'rede neural', 'inteligencia artificial',
            'automacao inteligente', 'sistema cognitivo', 'computacao cognitiva',
            'aprendizagem automatica', 'reconhecimento automatico',
            'classificacao automatica', 'predicao automatica'
        ]
        
        text_to_check = (title + ' ' + content[:2000]).lower()
        
        # Verifica termos exatos
        for keyword in ai_keywords_exact:
            if keyword.lower() in text_to_check:
                return True
                
        # Verifica termos técnicos
        for term in ai_technical_terms:
            if term.lower() in text_to_check:
                return True
        
        # Verifica palavras com word boundary
        for pattern in ai_keywords_word_boundary:
            if re.search(pattern, text_to_check, re.IGNORECASE):
                return True
        
        return False 