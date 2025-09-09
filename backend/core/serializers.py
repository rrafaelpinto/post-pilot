from rest_framework import serializers
from .models import Theme, Post


class ThemeSerializer(serializers.ModelSerializer):
    posts_count = serializers.ReadOnlyField()
    articles_count = serializers.ReadOnlyField()
    simple_posts_count = serializers.ReadOnlyField()

    class Meta:
        model = Theme
        fields = [
            "id",
            "title",
            "created_at",
            "updated_at",
            "is_active",
            "processing_status",
            "is_processing",
            "suggested_topics",
            "topics_generated_at",
            "posts_count",
            "articles_count",
            "simple_posts_count",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "processing_status",
            "is_processing",
            "suggested_topics",
            "topics_generated_at",
        ]


class ThemeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theme
        fields = ["title"]


class PostSerializer(serializers.ModelSerializer):
    theme_title = serializers.CharField(source="theme.title", read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "theme",
            "theme_title",
            "post_type",
            "title",
            "content",
            "promotional_post",
            "cover_image_prompt",
            "topic",
            "seo_title",
            "seo_description",
            "link",
            "post_date",
            "scheduled_date",
            "status",
            "processing_status",
            "is_processing",
            "created_at",
            "updated_at",
            "generated_at",
            "generation_prompt",
            "ai_model_used",
            "ai_provider_used",
            "content_preview",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "generated_at",
            "processing_status",
            "is_processing",
            "generation_prompt",
            "ai_model_used",
            "ai_provider_used",
            "content_preview",
        ]


class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["theme", "topic", "post_type"]


class PostUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = [
            "title",
            "content",
            "promotional_post",
            "seo_title",
            "seo_description",
            "link",
            "scheduled_date",
            "status",
        ]


class TaskStatusSerializer(serializers.Serializer):
    task_id = serializers.CharField()
    state = serializers.CharField()
    result = serializers.JSONField(required=False)
    info = serializers.JSONField(required=False)


class GenerateTopicsSerializer(serializers.Serializer):
    theme_id = serializers.IntegerField()


class GeneratePostSerializer(serializers.Serializer):
    topic = serializers.CharField()
    post_type = serializers.ChoiceField(choices=["simple", "article"], default="simple")
    topic_data = serializers.JSONField(required=False)


class ImprovePostSerializer(serializers.Serializer):
    post_id = serializers.IntegerField()


class RegenerateImagePromptSerializer(serializers.Serializer):
    post_id = serializers.IntegerField()
