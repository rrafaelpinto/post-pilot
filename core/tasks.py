from celery import shared_task
from django.utils import timezone
from django.contrib.auth.models import User
from .models import Theme, Post
from .services import OpenAIService
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def generate_topics_async(self, theme_id, user_id=None):
    """
    Tarefa assíncrona para gerar tópicos usando OpenAI
    """
    try:
        theme = Theme.objects.get(id=theme_id)
        
        # Atualizar status para processando
        theme.processing_status = 'processing'
        theme.save()
        
        openai_service = OpenAIService()
        topics_data = openai_service.generate_topics(theme.title)
        
        if topics_data.get('topics'):
            theme.suggested_topics = topics_data
            theme.topics_generated_at = timezone.now()
            theme.processing_status = 'completed'
            theme.save()
            
            logger.info(f'Tópicos gerados com sucesso para tema {theme.title}')
            return {
                'status': 'success',
                'message': f'{len(topics_data["topics"])} tópicos gerados com sucesso!',
                'topics_count': len(topics_data["topics"])
            }
        else:
            theme.processing_status = 'failed'
            theme.save()
            
            logger.error(f'Falha ao gerar tópicos para tema {theme.title}')
            return {
                'status': 'error',
                'message': 'Não foi possível gerar tópicos. Tente novamente.'
            }
            
    except Theme.DoesNotExist:
        logger.error(f'Tema com ID {theme_id} não encontrado')
        return {
            'status': 'error',
            'message': 'Tema não encontrado'
        }
    except Exception as e:
        logger.error(f'Erro ao gerar tópicos: {str(e)}')
        
        # Tentar novamente em caso de erro
        if self.request.retries < self.max_retries:
            logger.info(f'Tentativa {self.request.retries + 1} de {self.max_retries}')
            raise self.retry(countdown=60 * (self.request.retries + 1))
        
        # Atualizar status de falha após esgotar tentativas
        try:
            theme = Theme.objects.get(id=theme_id)
            theme.processing_status = 'failed'
            theme.save()
        except:
            pass
            
        return {
            'status': 'error',
            'message': f'Erro ao gerar tópicos: {str(e)}'
        }


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def generate_post_content_async(self, theme_id, topic, post_type, topic_data=None, user_id=None):
    """
    Tarefa assíncrona para gerar conteúdo de post usando OpenAI
    """
    try:
        theme = Theme.objects.get(id=theme_id)
        
        # Verificar se já existe um post deste tipo para este tema
        existing_post = Post.objects.filter(theme=theme, post_type=post_type, topic=topic).first()
        if existing_post:
            return {
                'status': 'warning',
                'message': f'Já existe um {existing_post.get_post_type_display().lower()} para este tópico.',
                'post_id': existing_post.id
            }
        
        openai_service = OpenAIService()
        content_data = openai_service.generate_post_content(topic, post_type, theme.title, topic_data)
        
        # Criar o post
        post_data = {
            'theme': theme,
            'post_type': post_type,
            'title': content_data.get('title', f'Post sobre {topic}'),
            'content': content_data.get('content', ''),
            'topic': topic,
            'seo_title': content_data.get('seo_title', topic[:60]),
            'seo_description': content_data.get('seo_description', ''),
            'status': 'generated',
            'generated_at': timezone.now(),
            'generation_prompt': f"Tópico: {topic}, Tipo: {post_type}",
            'ai_model_used': "gpt-4o" if post_type == 'article' else "gpt-4o-mini"
        }
        
        # Para artigos, adicionar o post promocional se disponível
        if post_type == 'article' and content_data.get('promotional_post'):
            post_data['promotional_post'] = content_data.get('promotional_post')
        
        post = Post.objects.create(**post_data)
        
        logger.info(f'Post gerado com sucesso: {post.title}')
        return {
            'status': 'success',
            'message': f'{post.get_post_type_display()} gerado com sucesso!',
            'post_id': post.id,
            'post_title': post.title
        }
        
    except Theme.DoesNotExist:
        logger.error(f'Tema com ID {theme_id} não encontrado')
        return {
            'status': 'error',
            'message': 'Tema não encontrado'
        }
    except Exception as e:
        logger.error(f'Erro ao gerar post: {str(e)}')
        
        # Tentar novamente em caso de erro
        if self.request.retries < self.max_retries:
            logger.info(f'Tentativa {self.request.retries + 1} de {self.max_retries}')
            raise self.retry(countdown=60 * (self.request.retries + 1))
            
        return {
            'status': 'error',
            'message': f'Erro ao gerar post: {str(e)}'
        }


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def improve_post_content_async(self, post_id, user_id=None):
    """
    Tarefa assíncrona para melhorar conteúdo de post usando OpenAI
    """
    try:
        post = Post.objects.get(id=post_id)
        
        # Atualizar status para processando
        post.processing_status = 'processing'
        post.save()
        
        openai_service = OpenAIService()
        improvement_data = openai_service.improve_post_content(
            current_content=post.content,
            post_title=post.title,
            post_type=post.post_type,
            topic=post.topic
        )
        
        if improvement_data.get('improved_content'):
            # Atualizar o conteúdo do post
            post.content = improvement_data['improved_content']
            post.updated_at = timezone.now()
            post.processing_status = 'completed'
            
            # Atualizar informações de geração
            if post.generation_prompt:
                post.generation_prompt += f" | Melhorado em: {timezone.now().strftime('%d/%m/%Y %H:%M')}"
            else:
                post.generation_prompt = f"Melhorado em: {timezone.now().strftime('%d/%m/%Y %H:%M')}"
            
            post.save()
            
            improvement_summary = improvement_data.get('improvement_summary', 'Conteúdo melhorado com sucesso!')
            logger.info(f'Post melhorado com sucesso: {post.title}')
            
            return {
                'status': 'success',
                'message': f'Post melhorado! {improvement_summary}',
                'post_id': post.id,
                'improvement_summary': improvement_summary
            }
        else:
            post.processing_status = 'failed'
            post.save()
            
            return {
                'status': 'error',
                'message': 'Não foi possível melhorar o post. Tente novamente.'
            }
            
    except Post.DoesNotExist:
        logger.error(f'Post com ID {post_id} não encontrado')
        return {
            'status': 'error',
            'message': 'Post não encontrado'
        }
    except Exception as e:
        logger.error(f'Erro ao melhorar post: {str(e)}')
        
        # Tentar novamente em caso de erro
        if self.request.retries < self.max_retries:
            logger.info(f'Tentativa {self.request.retries + 1} de {self.max_retries}')
            raise self.retry(countdown=60 * (self.request.retries + 1))
        
        # Atualizar status de falha após esgotar tentativas
        try:
            post = Post.objects.get(id=post_id)
            post.processing_status = 'failed'
            post.save()
        except:
            pass
            
        return {
            'status': 'error',
            'message': f'Erro ao melhorar post: {str(e)}'
        }
