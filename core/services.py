import openai
from django.conf import settings
import json


class OpenAIService:
    """Service for integration with the OpenAI API"""
    
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def generate_topics(self, theme_title):
        """
        First agent: Generates 3-5 structured post topics based on the theme
        """
        prompt = f"""
        You are an expert in technical content creation for LinkedIn, focused on developers.

        **Theme/Stack:** "{theme_title}"

        **Target Audience:**
        - Junior developers
        - Senior engineers  
        - General tech professionals

        **Task:**
        Generate 3 to 5 specific topics for weekly LinkedIn posts. Each topic should include:
        1. **Title/Topic** - Clear and specific title
        2. **Suggested Hook** - Catchy question or statement to start the post
        3. **Post Type** - Type of post (tip, lesson, comparison, concept explanation, best practice, etc.)
        4. **One-sentence Summary** - One sentence summary of the main idea
        5. **Suggested CTA** - Engaging call to action for the end of the post

        **Desired Tone:**
        - Conversational, accessible, and direct
        - Focused on real problems developers face
        - Practical and applicable

        Return in JSON format:
        {{
            "topics": [
                {{
                    "title": "Specific topic title",
                    "hook": "Catchy question or statement",
                    "post_type": "tip/lesson/comparison/concept/best_practice",
                    "summary": "One sentence summary of the topic",
                    "cta": "Engaging call to action"
                }}
            ]
        }}

        All prompts and generated content must be in English.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Modelo mais econômico e rápido para geração de tópicos
                messages=[
                    {"role": "system", "content": "You are an expert in technical content creation for LinkedIn. Always respond only with valid JSON. Focus on practical and relevant topics for developers. All prompts and generated content must be in English."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            content = response.choices[0].message.content
            if content:
                content = content.strip()
                # Remove possible markdown code blocks
                if content.startswith('```json'):
                    content = content[7:]
                if content.endswith('```'):
                    content = content[:-3]
                
                return json.loads(content)
            else:
                return {"topics": []}
            
        except Exception as e:
            print(f"Error generating topics: {e}")
            return {"topics": []}
    
    def generate_post_content(self, topic, post_type, theme_title, topic_data=None):
        """
        Second agent: Generates post content based on the topic and template
        """
        if post_type == 'simple':
            template_prompt = """
            Create a simple LinkedIn post following this template:
            
            1. Catchy opening hook (1-2 lines)
            2. Topic development (2-3 short paragraphs)
            3. Call to action or question for engagement
            4. Relevant hashtags (3-5 hashtags)
            
            The post must have a maximum of 1300 characters and be engaging.
            Tone: conversational, accessible, and direct.
            """
        else:  # article
            template_prompt = """
            Create a comprehensive LinkedIn article following this template:
            
            **ARTICLE STRUCTURE:**
            1. Catchy and professional title
            2. Introduction presenting the problem/opportunity (150-200 words)
            3. 3-4 well-developed main points with examples (600-800 words total)
            4. Conclusion with practical insights and actionable takeaways (150-200 words)
            5. Call to action for engagement
            
            **ALSO CREATE A PROMOTIONAL POST:**
            Additionally, create a short promotional LinkedIn post (max 1300 characters) to promote this article.
            The promotional post should:
            - Hook readers with an intriguing question or statement
            - Briefly tease the main value/insights of the article
            - Include a clear call-to-action to read the full article
            - End with relevant hashtags (3-5)
            
            The article should be between 1000-1500 words, informative and professional.
            Tone: conversational, accessible, and direct.
            """
        
        # Build the prompt with structured topic data if available
        topic_context = ""
        if topic_data and isinstance(topic_data, dict):
            topic_context = f"""
            **Structured topic data:**
            - Suggested hook: "{topic_data.get('hook', '')}"
            - Suggested post type: {topic_data.get('post_type', 'tip')}
            - Summary: {topic_data.get('summary', '')}
            - Suggested CTA: "{topic_data.get('cta', '')}"
            
            Use this information as a basis, but adapt as needed for the requested content type.
            """
        
        prompt = f"""
        You are an expert in technical content creation for LinkedIn, focused on developers.

        **General theme:** "{theme_title}"
        **Specific topic:** "{topic}"
        **Content type:** {post_type}
        
        {topic_context}
        
        {template_prompt}
        
        **Target Audience:**
        - Junior developers
        - Senior engineers  
        - General tech professionals
        
        Also create:
        - SEO optimized title (max. 60 characters)
        - SEO description (max. 160 characters)
        
        **Focus on:**
        - Real problems developers face
        - Practical and applicable solutions
        - Concrete examples when possible
        
        Return in JSON format:
        {{
            "title": "Post/article title",
            "content": "Full content (article text for articles, post text for simple posts)",
            "promotional_post": "Short promotional post text (only for articles, omit for simple posts)",
            "seo_title": "SEO title",
            "seo_description": "SEO description"
        }}

        All prompts and generated content must be in English.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o" if post_type == 'article' else "gpt-4o-mini",  # GPT-4o para artigos, GPT-4o-mini para posts simples
                messages=[
                    {"role": "system", "content": f"You are an expert in technical content creation for LinkedIn. Always respond only with valid JSON. You are creating a {post_type} for developers. All prompts and generated content must be in English."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=3000 if post_type == 'article' else 1200  # Mais tokens para artigos
            )
            
            content = response.choices[0].message.content
            if content:
                content = content.strip()
                # Remove possible markdown code blocks
                if content.startswith('```json'):
                    content = content[7:]
                if content.endswith('```'):
                    content = content[:-3]
                
                return json.loads(content)
            else:
                return {
                    "title": f"Post about {topic}",
                    "content": f"Content about {topic} will be generated soon.",
                    "seo_title": topic[:60],
                    "seo_description": f"Learn more about {topic}"[:160]
                }
            
        except Exception as e:
            print(f"Error generating content: {e}")
            return {
                "title": f"Post about {topic}",
                "content": f"Content about {topic} will be generated soon.",
                "seo_title": topic[:60],
                "seo_description": f"Learn more about {topic}"[:160]
            }
