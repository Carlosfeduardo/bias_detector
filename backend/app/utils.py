import re
from typing import List, Dict, Any
import unicodedata

def normalize_text(text: str) -> str:
    """Normaliza texto removendo caracteres especiais e espaços extras"""
    # Remove caracteres de controle
    text = ''.join(char for char in text if unicodedata.category(char) != 'Cc')
    
    # Normaliza espaços
    text = re.sub(r'\s+', ' ', text)
    
    # Remove espaços no início e fim
    text = text.strip()
    
    return text

def split_text_into_chunks(text: str, max_length: int = 1000) -> List[str]:
    """Divide texto em chunks menores para processamento"""
    if len(text) <= max_length:
        return [text]
    
    chunks = []
    sentences = re.split(r'[.!?]+', text)
    current_chunk = ""
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        
        if len(current_chunk + sentence) <= max_length:
            current_chunk += sentence + ". "
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def calculate_text_statistics(text: str) -> Dict[str, Any]:
    """Calcula estatísticas básicas do texto"""
    words = text.split()
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    return {
        'total_characters': len(text),
        'total_words': len(words),
        'total_sentences': len(sentences),
        'avg_words_per_sentence': len(words) / len(sentences) if sentences else 0,
        'avg_chars_per_word': len(text) / len(words) if words else 0
    }

def extract_key_terms(text: str, min_length: int = 3) -> List[str]:
    """Extrai termos-chave do texto"""
    # Remove pontuação e converte para minúsculas
    text_clean = re.sub(r'[^\w\s]', ' ', text.lower())
    words = text_clean.split()
    
    # Filtra palavras muito curtas e stopwords básicas
    stopwords = {
        'o', 'a', 'os', 'as', 'um', 'uma', 'uns', 'umas',
        'de', 'do', 'da', 'dos', 'das', 'em', 'no', 'na', 'nos', 'nas',
        'para', 'por', 'com', 'sem', 'sob', 'sobre', 'entre',
        'e', 'ou', 'mas', 'porque', 'que', 'se', 'quando', 'onde',
        'como', 'por que', 'qual', 'quais', 'quem', 'quanto', 'quantos',
        'é', 'são', 'foi', 'foram', 'será', 'serão', 'está', 'estão',
        'tem', 'têm', 'teve', 'tiveram', 'ter', 'tendo', 'tido',
        'seu', 'sua', 'seus', 'suas', 'meu', 'minha', 'meus', 'minhas',
        'este', 'esta', 'estes', 'estas', 'esse', 'essa', 'esses', 'essas',
        'aquele', 'aquela', 'aqueles', 'aquelas', 'isso', 'isto', 'aquilo'
    }
    
    key_terms = []
    for word in words:
        if (len(word) >= min_length and 
            word not in stopwords and 
            not word.isdigit()):
            key_terms.append(word)
    
    # Remove duplicatas mantendo ordem
    seen = set()
    unique_terms = []
    for term in key_terms:
        if term not in seen:
            seen.add(term)
            unique_terms.append(term)
    
    return unique_terms[:20]  # Retorna apenas os 20 primeiros

def format_confidence_score(confidence: float) -> str:
    """Formata score de confiança para exibição"""
    if confidence >= 0.8:
        return f"Alta ({confidence:.1%})"
    elif confidence >= 0.5:
        return f"Média ({confidence:.1%})"
    else:
        return f"Baixa ({confidence:.1%})"

def validate_article_title(title: str) -> bool:
    """Valida se o título do artigo é aceitável"""
    if not title or len(title.strip()) < 2:
        return False
    
    # Remove títulos com caracteres suspeitos
    if re.search(r'[<>{}[\]|\\]', title):
        return False
    
    return True

def sanitize_html(text: str) -> str:
    """Remove tags HTML básicas do texto"""
    # Remove tags HTML
    text = re.sub(r'<[^>]+>', '', text)
    
    # Decodifica entidades HTML básicas
    html_entities = {
        '&amp;': '&',
        '&lt;': '<',
        '&gt;': '>',
        '&quot;': '"',
        '&#39;': "'",
        '&nbsp;': ' '
    }
    
    for entity, char in html_entities.items():
        text = text.replace(entity, char)
    
    return text

def truncate_text(text: str, max_length: int = 200) -> str:
    """Trunca texto mantendo palavras completas"""
    if len(text) <= max_length:
        return text
    
    truncated = text[:max_length]
    
    # Encontra o último espaço para não cortar palavras
    last_space = truncated.rfind(' ')
    if last_space > max_length * 0.8:  # Se o último espaço não está muito atrás
        truncated = truncated[:last_space]
    
    return truncated + "..."

def calculate_readability_score(text: str) -> float:
    """Calcula um score básico de legibilidade (simplificado)"""
    stats = calculate_text_statistics(text)
    
    if stats['total_sentences'] == 0:
        return 0.0
    
    # Fórmula simplificada baseada em palavras por sentença e caracteres por palavra
    words_per_sentence = stats['avg_words_per_sentence']
    chars_per_word = stats['avg_chars_per_word']
    
    # Score inversamente proporcional à complexidade
    # Valores típicos: sentenças curtas (< 15 palavras) e palavras curtas (< 6 chars) = score alto
    sentence_complexity = min(words_per_sentence / 15, 2.0)  # Normaliza até 2.0
    word_complexity = min(chars_per_word / 6, 2.0)  # Normaliza até 2.0
    
    readability = max(0.0, 1.0 - (sentence_complexity + word_complexity) / 4.0)
    
    return round(readability, 2) 