import openai
from django.conf import settings
import json


class OpenAIService:
    """Serviço para integração com a API da OpenAI"""
    
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def generate_topics(self, theme_title):
        """
        Primeiro agente: Gera 3-5 tópicos para postagem baseado no tema
        """
        prompt = f"""
        Você é um especialista em marketing de conteúdo para LinkedIn. 
        
        Baseado no tema: "{theme_title}"
        
        Gere entre 3 a 5 tópicos específicos e relevantes para criação de postagens no LinkedIn.
        Cada tópico deve ser focado, específico e ter potencial para engajamento.
        
        Retorne apenas um JSON com a lista de tópicos no seguinte formato:
        {{
            "topics": [
                "Tópico 1 específico e relevante",
                "Tópico 2 específico e relevante",
                "Tópico 3 específico e relevante"
            ]
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Você é um especialista em marketing de conteúdo para LinkedIn. Sempre responda apenas com JSON válido."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            content = response.choices[0].message.content.strip()
            # Remove possíveis markdown code blocks
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            
            return json.loads(content)
            
        except Exception as e:
            print(f"Erro ao gerar tópicos: {e}")
            return {"topics": []}
    
    def generate_post_content(self, topic, post_type, theme_title):
        """
        Segundo agente: Gera conteúdo da postagem baseado no tópico e template
        """
        if post_type == 'simple':
            template_prompt = """
            Crie um post simples para LinkedIn seguindo este template:
            
            1. Hook inicial chamativo (1-2 linhas)
            2. Desenvolvimento do tópico (2-3 parágrafos curtos)
            3. Call to action ou pergunta para engajamento
            4. Hashtags relevantes (3-5 hashtags)
            
            O post deve ter no máximo 1300 caracteres e ser envolvente.
            """
        else:  # article
            template_prompt = """
            Crie um artigo para LinkedIn seguindo este template:
            
            1. Título chamativo e profissional
            2. Introdução que apresenta o problema/oportunidade
            3. 3-4 pontos principais bem desenvolvidos
            4. Conclusão com insights práticos
            5. Call to action
            
            O artigo deve ter entre 800-1200 palavras e ser informativo e profissional.
            """
        
        prompt = f"""
        Tema geral: "{theme_title}"
        Tópico específico: "{topic}"
        Tipo de conteúdo: {post_type}
        
        {template_prompt}
        
        Crie também:
        - Título SEO otimizado (máx. 60 caracteres)
        - Descrição SEO (máx. 160 caracteres)
        
        Retorne no formato JSON:
        {{
            "title": "Título do post/artigo",
            "content": "Conteúdo completo",
            "seo_title": "Título SEO",
            "seo_description": "Descrição SEO"
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4" if post_type == 'article' else "gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"Você é um especialista em criação de conteúdo para LinkedIn. Sempre responda apenas com JSON válido. Você está criando um {post_type}."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000 if post_type == 'article' else 1000
            )
            
            content = response.choices[0].message.content.strip()
            # Remove possíveis markdown code blocks
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            
            return json.loads(content)
            
        except Exception as e:
            print(f"Erro ao gerar conteúdo: {e}")
            return {
                "title": f"Post sobre {topic}",
                "content": f"Conteúdo sobre {topic} será gerado em breve.",
                "seo_title": topic[:60],
                "seo_description": f"Saiba mais sobre {topic}"[:160]
            }
