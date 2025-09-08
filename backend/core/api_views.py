from datetime import timedelta

from celery.result import AsyncResult
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

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


@extend_schema_view(
    stats=extend_schema(
        summary="Estatísticas do Dashboard",
        description="Retorna estatísticas gerais do sistema incluindo contadores de temas, posts, e listagem dos itens mais recentes.",
        responses={200: "Estatísticas recuperadas com sucesso"},
        tags=["Dashboard"],
    )
)
class DashboardViewSet(viewsets.ViewSet):
    """
    ViewSet para estatísticas do dashboard.

    Fornece endpoints para recuperar informações estatísticas
    sobre o sistema, incluindo:
    - Contadores de temas e posts
    - Status dos posts por categoria
    - Serviço de IA ativo
    - Listagem dos itens mais recentes
    """

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


@extend_schema_view(
    list=extend_schema(
        summary="Listar Temas",
        description="Retorna lista paginada de todos os temas ativos ordenados por data de criação.",
        tags=["Temas"],
    ),
    create=extend_schema(
        summary="Criar Tema",
        description="Cria um novo tema para geração de conteúdo.",
        tags=["Temas"],
    ),
    retrieve=extend_schema(
        summary="Detalhar Tema",
        description="Retorna detalhes completos de um tema específico.",
        tags=["Temas"],
    ),
    update=extend_schema(
        summary="Atualizar Tema",
        description="Atualiza todas as informações de um tema.",
        tags=["Temas"],
    ),
    partial_update=extend_schema(
        summary="Atualizar Tema Parcialmente",
        description="Atualiza parcialmente as informações de um tema.",
        tags=["Temas"],
    ),
    destroy=extend_schema(
        summary="Deletar Tema",
        description="Remove um tema do sistema (soft delete).",
        tags=["Temas"],
    ),
    generate_topics=extend_schema(
        summary="Gerar Tópicos",
        description="Inicia processo de geração de tópicos usando IA para o tema especificado.",
        responses={200: "Geração de tópicos iniciada com sucesso"},
        tags=["Temas", "IA"],
    ),
    generate_post=extend_schema(
        summary="Gerar Post",
        description="Inicia processo de geração de post usando IA baseado em um tópico específico.",
        request=GeneratePostSerializer,
        responses={200: "Geração de post iniciada com sucesso"},
        tags=["Temas", "IA"],
    ),
    posts=extend_schema(
        summary="Posts do Tema",
        description="Lista todos os posts pertencentes a um tema específico.",
        responses={200: PostSerializer(many=True)},
        tags=["Temas"],
    ),
    status=extend_schema(
        summary="Status do Tema",
        description="Verifica o status de processamento atual do tema.",
        responses={200: "Status recuperado com sucesso"},
        tags=["Temas"],
    ),
)
class ThemeViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento completo de temas.

    Os temas são o núcleo do sistema, representando categorias
    ou assuntos para os quais o conteúdo será gerado.

    Funcionalidades principais:
    - CRUD completo de temas
    - Geração automática de tópicos com IA
    - Geração de posts baseados em tópicos
    - Monitoramento de status de processamento
    """

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


@extend_schema_view(
    list=extend_schema(
        summary="Listar Posts",
        description="Retorna lista paginada de todos os posts ordenados por data de criação.",
        tags=["Posts"],
    ),
    create=extend_schema(
        summary="Criar Post",
        description="Cria um novo post manualmente.",
        tags=["Posts"],
    ),
    retrieve=extend_schema(
        summary="Detalhar Post",
        description="Retorna detalhes completos de um post específico.",
        tags=["Posts"],
    ),
    update=extend_schema(
        summary="Atualizar Post",
        description="Atualiza todas as informações de um post.",
        tags=["Posts"],
    ),
    partial_update=extend_schema(
        summary="Atualizar Post Parcialmente",
        description="Atualiza parcialmente as informações de um post.",
        tags=["Posts"],
    ),
    destroy=extend_schema(
        summary="Deletar Post", description="Remove um post do sistema.", tags=["Posts"]
    ),
    improve=extend_schema(
        summary="Melhorar Post",
        description="Inicia processo de melhoria do conteúdo do post usando IA.",
        responses={200: "Processo de melhoria iniciado com sucesso"},
        tags=["Posts", "IA"],
    ),
    regenerate_image_prompt=extend_schema(
        summary="Regenerar Prompt de Imagem",
        description="Gera ou regenera o prompt para imagem de capa do artigo.",
        responses={200: "Geração de prompt iniciada com sucesso"},
        tags=["Posts", "IA"],
    ),
    publish=extend_schema(
        summary="Publicar Post",
        description="Marca o post como publicado e define a data de publicação.",
        responses={200: "Post publicado com sucesso"},
        tags=["Posts"],
    ),
    status=extend_schema(
        summary="Status do Post",
        description="Verifica o status de processamento atual do post.",
        responses={200: "Status recuperado com sucesso"},
        tags=["Posts"],
    ),
)
class PostViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento completo de posts.

    Os posts são o conteúdo gerado pelo sistema, podendo ser:
    - Posts simples: conteúdo curto para redes sociais
    - Artigos: conteúdo longo e detalhado

    Funcionalidades principais:
    - CRUD completo de posts
    - Melhoria de conteúdo com IA
    - Geração de prompts para imagens
    - Controle de publicação
    - Monitoramento de status de processamento
    """

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


@extend_schema_view(
    check=extend_schema(
        summary="Verificar Status de Task",
        description="Verifica o status de processamento de uma task assíncrona do Celery.",
        parameters=[
            OpenApiParameter(
                name="task_id",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description="ID da task do Celery para verificar",
            )
        ],
        responses={200: "Status da task recuperado com sucesso"},
        tags=["Tasks"],
    )
)
class TaskStatusViewSet(viewsets.ViewSet):
    """
    ViewSet para verificação de status de tasks do Celery.

    Permite monitorar o progresso de operações assíncronas
    como geração de tópicos, criação de posts e melhorias
    de conteúdo que são executadas em background.

    Estados possíveis das tasks:
    - PENDING: aguardando execução
    - STARTED: em execução
    - SUCCESS: concluída com sucesso
    - FAILURE: falhou na execução
    - RETRY: tentando novamente
    """

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
