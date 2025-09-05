from datetime import timedelta

from celery.result import AsyncResult
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Post, Theme
from .serializers import (
    GeneratePostSerializer,
    PostCreateSerializer,
    PostSerializer,
    PostUpdateSerializer,
    ThemeCreateSerializer,
    ThemeSerializer,
)
from .services import get_default_ai_service
from .tasks import (
    generate_post_content_task,
    generate_topics_task,
    improve_post_content_task,
    regenerate_image_prompt_task,
)


class DashboardViewSet(viewsets.ViewSet):
    """ViewSet para estatísticas do dashboard"""

    permission_classes = [AllowAny]

    @action(detail=False, methods=["get"])
    def stats(self, request):
        """Retorna estatísticas do dashboard"""
        total_themes = Theme.objects.filter(is_active=True).count()
        total_posts = Post.objects.count()
        published_posts = Post.objects.filter(status="published").count()
        draft_posts = Post.objects.filter(status="draft").count()
        generated_posts = Post.objects.filter(status="generated").count()

        ai_service = get_default_ai_service()
        ai_service_name = f"{type(ai_service).__name__}"

        recent_posts = Post.objects.order_by("-created_at")[:5]
        recent_themes = Theme.objects.filter(is_active=True).order_by("-created_at")[:5]

        return Response(
            {
                "total_themes": total_themes,
                "total_posts": total_posts,
                "published_posts": published_posts,
                "draft_posts": draft_posts,
                "generated_posts": generated_posts,
                "ai_service": ai_service_name,
                "recent_posts": PostSerializer(recent_posts, many=True).data,
                "recent_themes": ThemeSerializer(recent_themes, many=True).data,
            }
        )


class ThemeViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciamento de temas"""

    permission_classes = [AllowAny]

    def get_queryset(self):
        return Theme.objects.filter(is_active=True).order_by("-created_at")

    def get_serializer_class(self):
        if self.action == "create":
            return ThemeCreateSerializer
        return ThemeSerializer

    @action(detail=True, methods=["post"])
    def generate_topics(self, request, pk=None):
        """Gera tópicos para um tema usando AI"""
        theme = get_object_or_404(Theme, pk=pk)

        # Marca como processando
        theme.is_processing = True
        theme.processing_status = "processing"
        theme.save()

        # Inicia task assíncrona
        task = generate_topics_task.delay(theme.id)

        # Mensagem baseada se já existem tópicos
        existing_count = 0
        if theme.suggested_topics and theme.suggested_topics.get("topics"):
            existing_count = len(theme.suggested_topics["topics"])

        return Response(
            {
                "task_id": task.id,
                "message": f"Topic generation started. Task ID: {task.id}",
                "existing_topics_count": existing_count,
                "theme_id": theme.id,
            }
        )

    @action(detail=True, methods=["post"])
    def generate_post(self, request, pk=None):
        """Gera um post baseado em um tópico específico"""
        theme = get_object_or_404(Theme, pk=pk)

        serializer = GeneratePostSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        topic = data["topic"]
        post_type = data.get("post_type", "simple")
        topic_data = data.get("topic_data")

        # Inicia task assíncrona
        task = generate_post_content_task.delay(theme.id, topic, post_type, topic_data)

        return Response(
            {
                "task_id": task.id,
                "message": f"Post generation started. Task ID: {task.id}",
                "theme_id": theme.id,
                "topic": topic,
                "post_type": post_type,
            }
        )

    @action(detail=True, methods=["get"])
    def posts(self, request, pk=None):
        """Lista posts de um tema específico"""
        theme = get_object_or_404(Theme, pk=pk)
        posts = theme.posts.all().order_by("-created_at")
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def status(self, request, pk=None):
        """Verifica status de processamento do tema"""
        theme = get_object_or_404(Theme, pk=pk)

        # Se está marcado como processando mas sem task há muito tempo, limpar
        if theme.is_processing and theme.updated_at < timezone.now() - timedelta(
            minutes=5
        ):
            theme.is_processing = False
            theme.processing_status = "timeout"
            theme.save()

        return Response(
            {
                "theme_id": theme.id,
                "is_processing": theme.is_processing,
                "processing_status": theme.processing_status,
                "status": "processing" if theme.is_processing else "completed",
                "has_topics": bool(theme.suggested_topics),
                "topics_count": len(theme.suggested_topics.get("topics", []))
                if theme.suggested_topics
                else 0,
            }
        )


class PostViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciamento de posts"""

    permission_classes = [AllowAny]
    queryset = Post.objects.all().order_by("-created_at")

    def get_serializer_class(self):
        if self.action == "create":
            return PostCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return PostUpdateSerializer
        return PostSerializer

    @action(detail=True, methods=["post"])
    def improve(self, request, pk=None):
        """Melhora o conteúdo do post usando AI"""
        post = get_object_or_404(Post, pk=pk)

        # Marca como processando
        post.is_processing = True
        post.processing_status = "processing"
        post.save()

        # Inicia task assíncrona
        task = improve_post_content_task.delay(post.id)

        return Response(
            {
                "task_id": task.id,
                "message": f"Post improvement started. Task ID: {task.id}",
                "post_id": post.id,
            }
        )

    @action(detail=True, methods=["post"])
    def regenerate_image_prompt(self, request, pk=None):
        """Gera ou regenera prompt de imagem de capa para artigo"""
        post = get_object_or_404(Post, pk=pk)

        # Verifica se é um artigo
        if post.post_type != "article":
            return Response(
                {"error": "Only articles can have cover image prompt."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Marca como processando
        post.is_processing = True
        post.processing_status = "processing"
        post.save()

        # Inicia task assíncrona
        task = regenerate_image_prompt_task.delay(post.id)

        is_first_generation = not post.cover_image_prompt
        action_type = "generation" if is_first_generation else "regeneration"

        return Response(
            {
                "task_id": task.id,
                "message": f"Image prompt {action_type} started. Task ID: {task.id}",
                "post_id": post.id,
                "action_type": action_type,
            }
        )

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        """Publica um post"""
        post = get_object_or_404(Post, pk=pk)

        post.status = "published"
        post.post_date = timezone.now()
        post.save()

        return Response(
            {
                "message": f'Post "{post.title}" published successfully!',
                "post_id": post.id,
                "published_at": post.post_date,
            }
        )

    @action(detail=True, methods=["get"])
    def status(self, request, pk=None):
        """Verifica status de processamento do post"""
        post = get_object_or_404(Post, pk=pk)

        # Se está marcado como processando mas sem task há muito tempo, limpar
        if post.is_processing and post.updated_at < timezone.now() - timedelta(
            minutes=5
        ):
            post.is_processing = False
            post.processing_status = "timeout"
            post.save()

        return Response(
            {
                "post_id": post.id,
                "is_processing": post.is_processing,
                "processing_status": post.processing_status,
                "status": "processing" if post.is_processing else "completed",
                "title": post.title,
                "content_length": len(post.content) if post.content else 0,
            }
        )


class TaskStatusViewSet(viewsets.ViewSet):
    """ViewSet para verificar status de tasks do Celery"""

    permission_classes = [AllowAny]

    @action(detail=False, methods=["get"])
    def check(self, request):
        """Verifica status de uma task do Celery"""
        task_id = request.query_params.get("task_id")

        if not task_id:
            return Response(
                {"error": "task_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        task_result = AsyncResult(task_id)

        response_data = {
            "task_id": task_id,
            "state": task_result.state,
            "result": task_result.result if task_result.ready() else None,
            "info": task_result.info if not task_result.ready() else None,
        }

        return Response(response_data)
