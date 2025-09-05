import json
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

import openai
from django.conf import settings


class AIServiceBase(ABC):
    """Base class for AI service providers"""

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        print(f"Using AI service provider: {type(self).__name__}")

    @abstractmethod
    def _make_request(self, messages: List[Dict], **kwargs) -> str:
        """Make API request to the AI provider"""
        pass

    def generate_topics(
        self, theme_title: str, existing_topics: Optional[List] = None
    ) -> Dict:
        """Generate topics using the AI provider"""
        # Build context about existing topics
        existing_context = ""
        if existing_topics:
            existing_titles = []
            for topic in existing_topics:
                if isinstance(topic, dict) and "title" in topic:
                    existing_titles.append(topic["title"])
                elif isinstance(topic, str):
                    existing_titles.append(topic)

            if existing_titles:
                existing_context = f"""
                
**IMPORTANT - Existing Topics to Avoid Duplication:**
The following topics have already been suggested for this theme:
{chr(10).join([f"- {title}" for title in existing_titles])}

Please generate NEW topics that complement these existing ones, avoiding repetition and exploring different angles of the theme.
"""

        prompt = f"""
        You are an expert in technical content creation for LinkedIn, focused on developers.

        **Theme/Stack:** "{theme_title}"
        {existing_context}

        **Target Audience:**
        - Junior developers
        - Senior engineers  
        - General tech professionals

        **Task:**
        Generate 3 to 5 {"additional" if existing_topics else ""} specific topics for weekly LinkedIn posts. Each topic should include:
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
        """

        messages = [{"role": "user", "content": prompt}]

        try:
            response_text = self._make_request(messages)
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            if start != -1 and end != 0:
                try:
                    return json.loads(response_text[start:end])
                except json.JSONDecodeError:
                    pass
            return {"topics": []}
        except Exception as e:
            print(f"Error generating topics: {e}")
            return {"topics": []}

    def generate_post_content(self, topic, post_type, theme_title, topic_data=None):
        """
        Second agent: Generates post content based on the topic and template
        """
        if post_type == "simple":
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
            2. Introduction presenting the problem/opportunity (200-250 words)
            3. 3-4 well-developed main points with examples (800-1000 words total)
            4. Conclusion with practical insights and actionable takeaways (200-250 words)
            5. Call to action for engagement
            
            **ALSO CREATE A PROMOTIONAL POST:**
            Additionally, create a short promotional LinkedIn post (max 1300 characters) to promote this article.
            The promotional post should:
            - Hook readers with an intriguing question or statement
            - Briefly tease the main value/insights of the article
            - Include a clear call-to-action to read the full article
            - End with relevant hashtags (6-8)
            
            **COVER IMAGE PROMPT:**
            Create a detailed description for an AI image generator to create a professional cover image for this article.
            
            CRITICAL RULE - NO TEXT IN IMAGE:
            ❌ NEVER include text, titles, letters, or words in the image
            ❌ DO NOT show the article title or any written content
            ✅ Focus purely on visual elements, symbols, and abstract representations
            
            The description should be:
            - Visual-only elements that represent the technical topic
            - Abstract or realistic approach (but never textual)
            - Professional modern aesthetic suitable for LinkedIn
            - Specific colors, style, and composition details
            - Clean, minimalist design without any text
            - 120-200 words describing only visual elements
            
            The article should be between 1500-2000 words, informative and professional.
            Tone: conversational, accessible, and direct.
            """

        # Build the prompt with structured topic data if available
        topic_context = ""
        if topic_data and isinstance(topic_data, dict):
            topic_context = f"""
            **Structured topic data:**
            - Suggested hook: "{topic_data.get("hook", "")}"
            - Suggested post type: {topic_data.get("post_type", "tip")}
            - Summary: {topic_data.get("summary", "")}
            - Suggested CTA: "{topic_data.get("cta", "")}"
            
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
            "cover_image_prompt": "Detailed description for AI image generation (only for articles, omit for simple posts)",
            "seo_title": "SEO title",
            "seo_description": "SEO description"
        }}

        All prompts and generated content must be in English.
        """

        messages = [
            {
                "role": "system",
                "content": f"You are an expert in technical content creation for LinkedIn. Always respond only with valid JSON. You are creating a {post_type} for developers. All prompts and generated content must be in English.",
            },
            {"role": "user", "content": prompt},
        ]

        try:
            content = self._make_request(messages)
            if content:
                content = content.strip()
                # Remove possible markdown code blocks
                if content.startswith("```json"):
                    content = content[7:]
                if content.endswith("```"):
                    content = content[:-3]

                return json.loads(content)
            else:
                return {
                    "title": f"Post about {topic}",
                    "content": f"Content about {topic} will be generated soon.",
                    "seo_title": topic[:60],
                    "seo_description": f"Learn more about {topic}"[:160],
                }

        except Exception as e:
            print(f"Error generating content: {e}")
            return {
                "title": f"Post about {topic}",
                "content": f"Content about {topic} will be generated soon.",
                "seo_title": topic[:60],
                "seo_description": f"Learn more about {topic}"[:160],
            }

    def improve_post_content(self, current_content, post_title, post_type, topic):
        """
        Third agent: Improves existing post content with enhanced details, practical examples, and secure code
        """
        improvement_prompt = f"""
        You are an expert technical content creator and code reviewer, specialized in creating secure, production-ready content for developers.

        **TASK:** Enhance and improve the following {post_type} content with:

        **ENHANCEMENT REQUIREMENTS:**
        1. **Extend with More Details**: Add deeper explanations for each key point
        2. **Practical Examples**: Include real-world scenarios with working code examples
        3. **Security-First Code**: All code must be rigorously secure and follow best practices
        4. **Error-Free Implementation**: Code should be production-ready, tested, and robust
        5. **Technical Depth**: Explain the "why" and "how" behind each concept
        6. **Markdown Formatting**: Use proper Markdown syntax for better readability

        **CURRENT CONTENT TO IMPROVE:**
        Title: "{post_title}"
        Topic: "{topic}"
        Content: "{current_content}"

        **CODE QUALITY STANDARDS:**
        - Include proper error handling
        - Use secure coding practices (input validation, sanitization, etc.)
        - Add comments explaining critical sections
        - Follow language-specific best practices
        - Include edge case handling
        - Use meaningful variable names
        - Implement proper logging where applicable

        **FORMATTING GUIDELINES:**
        - Use # ## ### for headers
        - Use ```language for code blocks with proper language specification
        - Use **bold** for emphasis
        - Use `inline code` for technical terms
        - Use > for important notes/warnings
        - Use - or * for bullet points
        - Add horizontal rules (---) between major sections

        **OUTPUT STRUCTURE:**
        {"article" if post_type == "article" else "simple post"} should be significantly enhanced with:
        - More comprehensive explanations
        - Additional practical examples
        - Security considerations
        - Performance tips
        - Common pitfalls to avoid
        - Related concepts and connections
        - Relevant hashtags (8-8 relevant hashtags)

        Return the improved content in JSON format:
        {{
            "improved_content": "Enhanced content in Markdown format with detailed explanations and secure code examples",
            "improvement_summary": "Brief summary of key improvements made"
        }}

        **TARGET AUDIENCE:**
        - Junior to Senior developers
        - DevOps engineers
        - Technical leads
        - Security-conscious developers

        All content must be in English and technically accurate.
        """

        messages = [
            {
                "role": "system",
                "content": "You are an expert technical content creator and security-focused code reviewer. Always respond with valid JSON. Create production-ready, secure code examples with comprehensive explanations.",
            },
            {"role": "user", "content": improvement_prompt},
        ]

        try:
            content = self._make_request(messages)
            if content:
                content = content.strip()
                # Remove possible markdown code blocks
                if content.startswith("```json"):
                    content = content[7:]
                if content.endswith("```"):
                    content = content[:-3]

                return json.loads(content)
            else:
                return {
                    "improved_content": current_content,
                    "improvement_summary": "Content could not be improved at this time.",
                }

        except Exception as e:
            print(f"Error improving content: {e}")
            return {
                "improved_content": current_content,
                "improvement_summary": "Content could not be improved due to an error.",
            }

    def regenerate_cover_image_prompt(
        self, post_title, topic, theme_title, current_prompt=None
    ):
        """
        Fourth agent: Regenerates cover image prompt for articles - NO TEXT VERSION
        """
        regeneration_prompt = f"""
        You are an expert in visual design and AI image generation prompts, specialized in creating professional cover images WITHOUT TEXT.

        **TASK:** Create a detailed, professional prompt for AI image generation to create a cover image for a LinkedIn article.

        **ARTICLE DETAILS:**
        - Title: "{post_title}"
        - Topic: "{topic}"
        - Theme: "{theme_title}"

        **CURRENT PROMPT (if regenerating):**
        {f'Current prompt: "{current_prompt}"' if current_prompt else "This is the first generation."}

        **CRITICAL RULE - NO TEXT IN IMAGE:**
        ❌ NEVER include text, titles, letters, or words in the image
        ❌ DO NOT show the article title or any written content
        ❌ AVOID any textual elements or typography
        ✅ Focus purely on visual elements, symbols, and abstract representations
        ✅ Maximum 1-2 single keywords if absolutely essential (but prefer none)

        **VISUAL APPROACH:**
        1. **Abstract/Conceptual**: Use shapes, symbols, metaphors to represent the topic
        2. **Realistic Elements**: Objects, tools, or environments related to the concept
        3. **Symbolic Representation**: Icons and symbols that convey the meaning
        4. **Color Psychology**: Use colors that evoke the right emotions for the topic
        5. **Minimalist Design**: Clean, uncluttered composition

        **STYLE GUIDELINES:**
        - Professional, modern aesthetic suitable for LinkedIn
        - High-quality digital art or professional photography style
        - Balanced composition with focal point
        - Corporate color palette (blues, grays, whites, accent colors)
        - Clean backgrounds (gradients, textures, or solid colors)
        - Subtle lighting and shadows for depth
        - 16:9 aspect ratio (landscape orientation)

        **VISUAL ELEMENTS TO CONSIDER:**
        - For Technology: Geometric shapes, circuits, glowing elements, abstract networks
        - For Business: Professional objects, charts (visual only), ascending elements
        - For Development: Code-inspired patterns, building blocks, construction metaphors
        - For Leadership: Mountain peaks, pathways, guiding lights, upward arrows
        - For Innovation: Light bulbs, gears, flowing energy, dynamic compositions

        **OUTPUT:** Create a detailed description (120-200 words) focusing purely on visual elements.

        Return in JSON format:
        {{
            "cover_image_prompt": "Detailed visual-only description for AI image generation",
            "style_notes": "Brief explanation of the visual approach chosen",
            "visual_elements": "Key visual elements that represent the concept"
        }}

        Remember: NO TEXT, NO TITLES, NO WORDS in the image description!
        """

        messages = [
            {
                "role": "system",
                "content": "You are an expert visual designer and AI prompt engineer. NEVER include text in image descriptions. Always respond with valid JSON. Create detailed, text-free professional image generation prompts.",
            },
            {"role": "user", "content": regeneration_prompt},
        ]

        try:
            content = self._make_request(messages)
            if content:
                content = content.strip()
                # Remove possible markdown code blocks
                if content.startswith("```json"):
                    content = content[7:]
                if content.endswith("```"):
                    content = content[:-3]

                return json.loads(content)
            else:
                return {
                    "cover_image_prompt": f"Abstract professional illustration representing {topic} concept through visual elements only, modern minimalist style, corporate color palette, no text, clean composition, high quality digital art",
                    "style_notes": "Could not generate new prompt at this time - using fallback visual-only prompt.",
                    "visual_elements": "Abstract shapes and symbols related to the topic",
                }

        except Exception as e:
            print(f"Error regenerating image prompt: {e}")
            return {
                "cover_image_prompt": f"Abstract professional illustration representing {topic} concept through visual elements only, modern minimalist style, corporate color palette, no text, clean composition, high quality digital art",
                "style_notes": "Error occurred during generation - using fallback visual-only prompt.",
                "visual_elements": "Abstract shapes and symbols related to the topic",
            }


class OpenAIService(AIServiceBase):
    """Service for integration with the OpenAI API"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        super().__init__(api_key=api_key or settings.OPENAI_API_KEY, model=model)
        openai.api_key = self.api_key
        self.client = openai.OpenAI(api_key=self.api_key)

    def _make_request(self, messages: List[Dict], **kwargs) -> str:
        """Make request to OpenAI API"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=4000,
            **kwargs,
        )
        return response.choices[0].message.content


class GrokService(AIServiceBase):
    """Service for integration with Grok (X.AI) API"""

    def __init__(self, api_key: Optional[str] = None, model: str = "grok-beta"):
        super().__init__(
            api_key=api_key or getattr(settings, "GROK_API_KEY", ""), model=model
        )
        self.base_url = "https://api.x.ai/v1"

    def _make_request(self, messages: List[Dict], **kwargs) -> str:
        """Make request to Grok API"""
        import requests

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        data = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 4000,
            **kwargs,
        }

        response = requests.post(
            f"{self.base_url}/chat/completions", headers=headers, json=data, timeout=120
        )
        response.raise_for_status()

        result = response.json()
        return result["choices"][0]["message"]["content"]


class GeminiService(AIServiceBase):
    """Service for integration with Google Gemini API"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-1.5-pro"):
        super().__init__(
            api_key=api_key or getattr(settings, "GEMINI_API_KEY", ""), model=model
        )
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"

    def _make_request(self, messages: List[Dict], **kwargs) -> str:
        """Make request to Gemini API"""
        import requests

        # Convert OpenAI-style messages to Gemini format
        gemini_messages = []
        for msg in messages:
            if msg["role"] == "user":
                gemini_messages.append(
                    {"role": "user", "parts": [{"text": msg["content"]}]}
                )
            elif msg["role"] == "assistant":
                gemini_messages.append(
                    {"role": "model", "parts": [{"text": msg["content"]}]}
                )

        data = {
            "contents": gemini_messages,
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 4000, **kwargs},
        }

        url = f"{self.base_url}/models/{self.model}:generateContent"
        params = {"key": self.api_key}

        response = requests.post(url, params=params, json=data, timeout=120)
        response.raise_for_status()

        result = response.json()
        return result["candidates"][0]["content"]["parts"][0]["text"]


class AIServiceFactory:
    """Factory class to create AI service instances"""

    PROVIDERS = {
        "openai": OpenAIService,
        "grok": GrokService,
        "gemini": GeminiService,
    }

    @classmethod
    def create_service(cls, provider: str = "openai", **kwargs) -> AIServiceBase:
        """Create an AI service instance"""
        if provider not in cls.PROVIDERS:
            raise ValueError(
                f"Unsupported provider: {provider}. Available: {list(cls.PROVIDERS.keys())}"
            )

        service_class = cls.PROVIDERS[provider]
        return service_class(**kwargs)

    @classmethod
    def get_available_providers(cls) -> List[str]:
        """Get list of available providers"""
        return list(cls.PROVIDERS.keys())


# Manter compatibilidade com código existente
def get_default_ai_service() -> AIServiceBase:
    """Get the default AI service (can be configured via settings)"""
    default_provider = getattr(settings, "DEFAULT_AI_PROVIDER", "openai")
    return AIServiceFactory.create_service(default_provider)
