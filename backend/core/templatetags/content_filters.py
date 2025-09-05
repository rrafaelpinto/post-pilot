from django import template
import re

register = template.Library()

@register.filter
def sentence_count(value):
    """Conta o número de sentenças no texto"""
    if not value:
        return 0
    
    # Remove espaços extras e quebras de linha
    text = re.sub(r'\s+', ' ', value.strip())
    
    # Conta sentenças terminadas com ., !, ?
    sentences = re.split(r'[.!?]+', text)
    
    # Remove strings vazias
    sentences = [s.strip() for s in sentences if s.strip()]
    
    return len(sentences)

@register.filter
def paragraph_count(value):
    """Conta o número de parágrafos no texto"""
    if not value:
        return 0
    
    # Divide por quebras de linha duplas (parágrafos)
    paragraphs = re.split(r'\n\s*\n', value.strip())
    
    # Remove strings vazias
    paragraphs = [p.strip() for p in paragraphs if p.strip()]
    
    return len(paragraphs)

@register.filter
def words_per_sentence(value):
    """Calcula a média de palavras por sentença"""
    if not value:
        return 0
    
    word_count = len(value.split())
    sentence_count_val = sentence_count(value)
    
    if sentence_count_val == 0:
        return 0
    
    return round(word_count / sentence_count_val, 1)

@register.filter
def reading_difficulty(value):
    """Avalia a dificuldade de leitura baseada em métricas simples"""
    if not value:
        return "Indefinido"
    
    words = len(value.split())
    sentences = sentence_count(value)
    
    if sentences == 0:
        return "Indefinido"
    
    avg_words_per_sentence = words / sentences
    
    if avg_words_per_sentence <= 15:
        return "Fácil"
    elif avg_words_per_sentence <= 20:
        return "Média"
    else:
        return "Difícil"

@register.filter
def content_density(value):
    """Calcula a densidade do conteúdo (palavras por 1000 caracteres)"""
    if not value:
        return 0
    
    words = len(value.split())
    chars = len(value)
    
    if chars == 0:
        return 0
    
    return round((words / chars) * 1000, 1)
