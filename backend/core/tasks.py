import logging

from celery import shared_task
from django.utils import timezone

from .models import Post, Theme
from .services import get_default_ai_service

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def generate_topics_task(self, theme_id, user_id=None):
    """
    Asynchronous task to generate topics using AI
    """
    theme = None
    try:
        theme = Theme.objects.get(id=theme_id)

        # Update status to processing
        theme.is_processing = True
        theme.processing_status = "processing"
        theme.save()

        ai_service = get_default_ai_service()

        # Check if topics already exist to build appropriate prompt
        existing_topics = []
        if theme.suggested_topics and theme.suggested_topics.get("topics"):
            existing_topics = theme.suggested_topics["topics"]
            logger.info(
                f"Theme already has {len(existing_topics)} topics. Generating additional topics."
            )

        # Generate new topics (considering existing ones)
        topics_data = ai_service.generate_topics(
            theme.title, existing_topics=existing_topics
        )

        if topics_data.get("topics"):
            # Combine existing topics with new ones
            if existing_topics:
                combined_topics = existing_topics + topics_data["topics"]
                combined_data = {
                    "topics": combined_topics,
                    "total_count": len(combined_topics),
                    "last_generated": timezone.now().isoformat(),
                }
                new_topics_count = len(topics_data["topics"])
            else:
                combined_data = topics_data
                new_topics_count = len(topics_data["topics"])

            theme.suggested_topics = combined_data
            theme.topics_generated_at = timezone.now()
            theme.processing_status = "completed"
            theme.is_processing = False  # Important: mark as not processing
            theme.save()

            logger.info(
                f"Topics successfully added to theme {theme.title}. Total: {len(combined_data['topics'])}"
            )
            return {
                "status": "success",
                "message": f"{new_topics_count} new topics added! Total: {len(combined_data['topics'])} topics.",
                "topics_count": len(combined_data["topics"]),
                "new_topics_count": new_topics_count,
            }
        else:
            theme.processing_status = "failed"
            theme.is_processing = False  # Important: mark as not processing
            theme.save()

            logger.error(f"Failed to generate topics for theme {theme.title}")
            return {
                "status": "error",
                "message": "Could not generate topics. Please try again.",
            }

    except Theme.DoesNotExist:
        logger.error(f"Tema com ID {theme_id} não encontrado")
        return {"status": "error", "message": "Tema não encontrado"}
    except Exception as e:
        logger.error(f"Erro ao gerar tópicos: {str(e)}")

        # Ensure is_processing is unmarked even on error
        if theme:
            try:
                theme.is_processing = False
                theme.processing_status = "failed"
                theme.save()
            except:
                pass

        # Tentar novamente em caso de erro
        if self.request.retries < self.max_retries:
            logger.info(f"Tentativa {self.request.retries + 1} de {self.max_retries}")
            raise self.retry(countdown=60 * (self.request.retries + 1))

        # Atualizar status de falha após esgotar tentativas
        try:
            theme = Theme.objects.get(id=theme_id)
            theme.processing_status = "failed"
            theme.is_processing = False  # Importante: marcar como não processando
            theme.save()
        except:
            pass

        return {"status": "error", "message": f"Erro ao gerar tópicos: {str(e)}"}


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def generate_post_content_task(
    self, theme_id, topic, post_type, topic_data=None, user_id=None
):
    """
    Tarefa assíncrona para gerar conteúdo de post usando OpenAI
    """
    try:
        theme = Theme.objects.get(id=theme_id)

        # Verificar se já existe um post deste tipo para este tema
        existing_post = Post.objects.filter(
            theme=theme, post_type=post_type, topic=topic
        ).first()
        if existing_post:
            return {
                "status": "warning",
                "message": f"Já existe um {existing_post.get_post_type_display().lower()} para este tópico.",
                "post_id": existing_post.id,
            }

        ai_service = get_default_ai_service()
        logger.info(
            f"Gerando conteúdo para tema '{theme.title}', tópico '{topic}', tipo '{post_type}', através do provedor '{type(ai_service).__name__}'"
        )
        content_data = ai_service.generate_post_content(
            topic, post_type, theme.title, topic_data
        )

        # Criar o post
        post_data = {
            "theme": theme,
            "post_type": post_type,
            "title": content_data.get("title", f"Post sobre {topic}"),
            "content": content_data.get("content", ""),
            "topic": topic,
            "seo_title": content_data.get("seo_title", topic[:60]),
            "seo_description": content_data.get("seo_description", ""),
            "status": "generated",
            "generated_at": timezone.now(),
            "generation_prompt": f"Tópico: {topic}, Tipo: {post_type}",
            "ai_model_used": "gpt-4o" if post_type == "article" else "gpt-4o-mini",
        }

        # Para artigos, adicionar o post promocional se disponível
        if post_type == "article" and content_data.get("promotional_post"):
            post_data["promotional_post"] = content_data.get("promotional_post")

        post = Post.objects.create(**post_data)

        logger.info(f"Post gerado com sucesso: {post.title}")
        return {
            "status": "success",
            "message": f"{post.get_post_type_display()} gerado com sucesso!",
            "post_id": post.id,
            "post_title": post.title,
        }

    except Theme.DoesNotExist:
        logger.error(f"Tema com ID {theme_id} não encontrado")
        return {"status": "error", "message": "Tema não encontrado"}
    except Exception as e:
        logger.error(f"Erro ao gerar post: {str(e)}")

        # Tentar novamente em caso de erro
        if self.request.retries < self.max_retries:
            logger.info(f"Tentativa {self.request.retries + 1} de {self.max_retries}")
            raise self.retry(countdown=60 * (self.request.retries + 1))

        return {"status": "error", "message": f"Erro ao gerar post: {str(e)}"}


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def improve_post_content_task(self, post_id, user_id=None):
    """
    Tarefa assíncrona para melhorar conteúdo de post usando OpenAI
    """
    try:
        post = Post.objects.get(id=post_id)

        # Atualizar status para processando
        post.processing_status = "processing"
        post.save()

        ai_service = get_default_ai_service()
        improvement_data = ai_service.improve_post_content(
            current_content=post.content,
            post_title=post.title,
            post_type=post.post_type,
            topic=post.topic,
        )

        if improvement_data.get("improved_content"):
            # Verificar se o conteúdo foi realmente melhorado (não é igual ao original)
            if improvement_data["improved_content"] != post.content:
                # Atualizar o conteúdo do post
                post.content = improvement_data["improved_content"]
                post.updated_at = timezone.now()
                post.processing_status = "completed"

                # Atualizar informações de geração
                if post.generation_prompt:
                    post.generation_prompt += (
                        f" | Melhorado em: {timezone.now().strftime('%d/%m/%Y %H:%M')}"
                    )
                else:
                    post.generation_prompt = (
                        f"Melhorado em: {timezone.now().strftime('%d/%m/%Y %H:%M')}"
                    )

                post.save()

                improvement_summary = improvement_data.get(
                    "improvement_summary", "Conteúdo melhorado com sucesso!"
                )
                logger.info(f"Post melhorado com sucesso: {post.title}")

                return {
                    "status": "success",
                    "message": f"Post melhorado! {improvement_summary}",
                    "post_id": post.id,
                    "improvement_summary": improvement_summary,
                }
            else:
                # Conteúdo não foi alterado, mas há um resumo de melhoria (provavelmente um erro)
                post.processing_status = "failed"
                post.save()

                error_message = improvement_data.get(
                    "improvement_summary", "O conteúdo não pôde ser melhorado."
                )

                logger.warning(f"Falha ao melhorar post {post.title}: {error_message}")

                return {
                    "status": "error",
                    "message": error_message,
                    "post_id": post.id,
                }
        else:
            post.processing_status = "failed"
            post.save()

            return {
                "status": "error",
                "message": "Não foi possível melhorar o post. Tente novamente.",
            }

    except Post.DoesNotExist:
        logger.error(f"Post com ID {post_id} não encontrado")
        return {"status": "error", "message": "Post não encontrado"}
    except Exception as e:
        logger.error(f"Erro ao melhorar post: {str(e)}")

        # Tentar novamente em caso de erro
        if self.request.retries < self.max_retries:
            logger.info(f"Tentativa {self.request.retries + 1} de {self.max_retries}")
            raise self.retry(countdown=60 * (self.request.retries + 1))

        # Atualizar status de falha após esgotar tentativas
        try:
            post = Post.objects.get(id=post_id)
            post.processing_status = "failed"
            post.save()
        except:
            pass

        return {"status": "error", "message": f"Erro ao melhorar post: {str(e)}"}


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def regenerate_image_prompt_task(self, post_id, user_id=None):
    """
    Tarefa assíncrona para regenerar prompt de imagem de capa usando OpenAI
    """
    try:
        post = Post.objects.get(id=post_id)

        # Verificar se é um artigo
        if post.post_type != "article":
            return {
                "status": "error",
                "message": "Apenas artigos podem ter prompt de imagem de capa.",
            }

        # Atualizar status para processando
        post.is_processing = True
        post.processing_status = "processing"
        post.save()

        # Determinar se é geração inicial ou regeneração
        is_first_generation = not post.cover_image_prompt
        action_type = "gerado" if is_first_generation else "regenerado"

        ai_service = get_default_ai_service()
        image_data = ai_service.regenerate_cover_image_prompt(
            post_title=post.title,
            topic=post.topic,
            theme_title=post.theme.title,
            current_prompt=post.cover_image_prompt,
        )

        if image_data.get("cover_image_prompt"):
            # Atualizar o prompt da imagem
            post.cover_image_prompt = image_data["cover_image_prompt"]
            post.updated_at = timezone.now()
            post.is_processing = False
            post.processing_status = "completed"

            # Atualizar informações de geração
            timestamp = timezone.now().strftime("%d/%m/%Y %H:%M")
            if is_first_generation:
                generation_info = f"Imagem gerada em: {timestamp}"
            else:
                generation_info = f"Imagem regenerada em: {timestamp}"

            if post.generation_prompt:
                post.generation_prompt += f" | {generation_info}"
            else:
                post.generation_prompt = generation_info

            post.save()

            style_notes = image_data.get(
                "style_notes", f"Prompt da imagem {action_type} com sucesso!"
            )
            logger.info(f"Prompt da imagem {action_type} com sucesso: {post.title}")

            return {
                "status": "success",
                "message": f"Prompt da imagem {action_type}! {style_notes}",
                "post_id": post.id,
                "action_type": action_type,
                "style_notes": style_notes,
            }
        else:
            post.is_processing = False
            post.processing_status = "failed"
            post.save()

            return {
                "status": "error",
                "message": f"Não foi possível {action_type.replace('do', 'r')} o prompt da imagem. Tente novamente.",
            }

    except Post.DoesNotExist:
        logger.error(f"Post com ID {post_id} não encontrado")
        return {"status": "error", "message": "Post não encontrado"}
    except Exception as e:
        logger.error(f"Erro ao regenerar prompt da imagem: {str(e)}")

        # Tentar novamente em caso de erro
        if self.request.retries < self.max_retries:
            logger.info(f"Tentativa {self.request.retries + 1} de {self.max_retries}")
            raise self.retry(countdown=60 * (self.request.retries + 1))

        # Atualizar status de falha após esgotar tentativas
        try:
            post = Post.objects.get(id=post_id)
            post.is_processing = False
            post.processing_status = "failed"
            post.save()
        except Exception:
            pass

        return {
            "status": "error",
            "message": f"Erro ao regenerar prompt da imagem: {str(e)}",
        }
