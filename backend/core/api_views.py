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
        summary="Dashboard Statistics",
        description="Returns general system statistics including theme and post counters, and listing of most recent items.",
        responses={200: "Statistics retrieved successfully"},
        tags=["Dashboard"],
    )
)
class DashboardViewSet(viewsets.ViewSet):
    """
    ViewSet for dashboard statistics.

    Provides endpoints to retrieve statistical information
    about the system, including:
    - Theme and post counters
    - Post status by category
    - Active AI service
    - Listing of most recent items
    """

    permission_classes = [AllowAny]

    @action(detail=False, methods=["get"])
    def stats(self, request):
        """Returns dashboard statistics"""
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
        summary="List Themes",
        description="Returns paginated list of all active themes ordered by creation date.",
        tags=["Themes"],
    ),
    create=extend_schema(
        summary="Create Theme",
        description="Creates a new theme for content generation.",
        tags=["Themes"],
    ),
    retrieve=extend_schema(
        summary="Theme Details",
        description="Returns complete details of a specific theme.",
        tags=["Themes"],
    ),
    update=extend_schema(
        summary="Update Theme",
        description="Updates all information of a theme.",
        tags=["Themes"],
    ),
    partial_update=extend_schema(
        summary="Partially Update Theme",
        description="Partially updates theme information.",
        tags=["Themes"],
    ),
    destroy=extend_schema(
        summary="Delete Theme",
        description="Removes a theme from the system (soft delete).",
        tags=["Themes"],
    ),
    generate_topics=extend_schema(
        summary="Generate Topics",
        description="Starts AI topic generation process for the specified theme.",
        responses={200: "Topic generation started successfully"},
        tags=["Themes", "AI"],
    ),
    generate_post=extend_schema(
        summary="Generate Post",
        description="Starts AI post generation process based on a specific topic.",
        request=GeneratePostSerializer,
        responses={200: "Post generation started successfully"},
        tags=["Themes", "AI"],
    ),
    posts=extend_schema(
        summary="Theme Posts",
        description="Lists all posts belonging to a specific theme.",
        responses={200: PostSerializer(many=True)},
        tags=["Themes"],
    ),
    status=extend_schema(
        summary="Theme Status",
        description="Checks the current processing status of the theme.",
        responses={200: "Status retrieved successfully"},
        tags=["Themes"],
    ),
)
class ThemeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for complete theme management.

    Themes are the core of the system, representing categories
    or subjects for which content will be generated.

    Main functionalities:
    - Complete CRUD for themes
    - Automatic topic generation with AI
    - Post generation based on topics
    - Processing status monitoring
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
        """Generates topics for a theme using AI"""
        theme = get_object_or_404(Theme, pk=pk)

        # Mark as processing
        theme.is_processing = True
        theme.processing_status = "processing"
        theme.save()

        # Start asynchronous task
        task = generate_topics_task.delay(theme.id)

        # Message based on whether topics already exist
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
        """Generates a post based on a specific topic"""
        theme = get_object_or_404(Theme, pk=pk)

        serializer = GeneratePostSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        topic = data["topic"]
        post_type = data.get("post_type", "simple")
        topic_data = data.get("topic_data")

        # Start asynchronous task
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
        """Lists posts from a specific theme"""
        theme = get_object_or_404(Theme, pk=pk)
        posts = theme.posts.all().order_by("-created_at")
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def status(self, request, pk=None):
        """Checks theme processing status"""
        theme = get_object_or_404(Theme, pk=pk)

        # If marked as processing but no task for a long time, clear it
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
        summary="List Posts",
        description="Returns paginated list of all posts ordered by creation date.",
        tags=["Posts"],
    ),
    create=extend_schema(
        summary="Create Post",
        description="Creates a new post manually.",
        tags=["Posts"],
    ),
    retrieve=extend_schema(
        summary="Post Details",
        description="Returns complete details of a specific post.",
        tags=["Posts"],
    ),
    update=extend_schema(
        summary="Update Post",
        description="Updates all information of a post.",
        tags=["Posts"],
    ),
    partial_update=extend_schema(
        summary="Partially Update Post",
        description="Partially updates post information.",
        tags=["Posts"],
    ),
    destroy=extend_schema(
        summary="Delete Post",
        description="Removes a post from the system.",
        tags=["Posts"],
    ),
    improve=extend_schema(
        summary="Improve Post",
        description="Starts post content improvement process using AI.",
        responses={200: "Improvement process started successfully"},
        tags=["Posts", "AI"],
    ),
    regenerate_image_prompt=extend_schema(
        summary="Regenerate Image Prompt",
        description="Generates or regenerates the prompt for article cover image.",
        responses={200: "Prompt generation started successfully"},
        tags=["Posts", "AI"],
    ),
    publish=extend_schema(
        summary="Publish Post",
        description="Marks the post as published and sets the publication date.",
        responses={200: "Post published successfully"},
        tags=["Posts"],
    ),
    status=extend_schema(
        summary="Post Status",
        description="Checks the current processing status of the post.",
        responses={200: "Status retrieved successfully"},
        tags=["Posts"],
    ),
)
class PostViewSet(viewsets.ModelViewSet):
    """
    ViewSet for complete post management.

    Posts are the content generated by the system, which can be:
    - Simple posts: short content for social media
    - Articles: long and detailed content

    Main functionalities:
    - Complete CRUD for posts
    - Content improvement with AI
    - Image prompt generation
    - Publication control
    - Processing status monitoring
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
        """Improves post content using AI"""
        post = get_object_or_404(Post, pk=pk)

        # Mark as processing
        post.is_processing = True
        post.processing_status = "processing"
        post.save()

        # Start asynchronous task
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
        """Generates or regenerates cover image prompt for article"""
        post = get_object_or_404(Post, pk=pk)

        # Check if it's an article
        if post.post_type != "article":
            return Response(
                {"error": "Only articles can have cover image prompt."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Mark as processing
        post.is_processing = True
        post.processing_status = "processing"
        post.save()

        # Start asynchronous task
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
        """Publishes a post"""
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
        """Checks post processing status"""
        post = get_object_or_404(Post, pk=pk)

        # If marked as processing but no task for a long time, clear it
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
        summary="Check Task Status",
        description="Checks the processing status of a Celery asynchronous task.",
        parameters=[
            OpenApiParameter(
                name="task_id",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Celery task ID to check",
            )
        ],
        responses={200: "Task status retrieved successfully"},
        tags=["Tasks"],
    )
)
class TaskStatusViewSet(viewsets.ViewSet):
    """
    ViewSet for checking Celery task status.

    Allows monitoring the progress of asynchronous operations
    like topic generation, post creation and content improvements
    that are executed in the background.

    Possible task states:
    - PENDING: waiting for execution
    - STARTED: in execution
    - SUCCESS: completed successfully
    - FAILURE: failed execution
    - RETRY: retrying
    """

    permission_classes = [AllowAny]

    @action(detail=False, methods=["get"])
    def check(self, request):
        """Checks Celery task status"""
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
