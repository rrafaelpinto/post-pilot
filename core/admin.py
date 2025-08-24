from django.contrib import admin
from .models import Theme, Post


@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ['title', 'posts_count', 'articles_count', 'simple_posts_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at', 'topics_generated_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at', 'topics_generated_at']
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('title', 'description', 'is_active')
        }),
        ('Tópicos Gerados pela IA', {
            'fields': ('suggested_topics', 'topics_generated_at'),
            'classes': ('collapse',)
        }),
        ('Controle de Datas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def posts_count(self, obj):
        return obj.posts_count
    posts_count.short_description = 'Total de Posts'
    
    def articles_count(self, obj):
        return obj.articles_count
    articles_count.short_description = 'Artigos'
    
    def simple_posts_count(self, obj):
        return obj.simple_posts_count
    simple_posts_count.short_description = 'Posts Simples'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'theme', 'post_type', 'status', 'post_date', 
        'is_published', 'created_at'
    ]
    list_filter = [
        'post_type', 'status', 'post_date', 'created_at', 
        'theme', 'generated_at'
    ]
    search_fields = ['title', 'content', 'topic', 'seo_title', 'seo_description']
    readonly_fields = ['created_at', 'updated_at', 'generated_at']
    date_hierarchy = 'post_date'
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('theme', 'post_type', 'title', 'topic', 'content')
        }),
        ('SEO', {
            'fields': ('seo_title', 'seo_description'),
            'classes': ('collapse',)
        }),
        ('Publicação', {
            'fields': ('status', 'post_date', 'scheduled_date', 'link')
        }),
        ('Geração por IA', {
            'fields': ('generation_prompt', 'ai_model_used', 'generated_at'),
            'classes': ('collapse',)
        }),
        ('Controle de Datas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def is_published(self, obj):
        return obj.is_published
    is_published.boolean = True
    is_published.short_description = 'Publicado'
    
    actions = ['mark_as_published', 'mark_as_draft']
    
    def mark_as_published(self, request, queryset):
        queryset.update(status='published')
        self.message_user(request, f'{queryset.count()} posts marcados como publicados.')
    mark_as_published.short_description = 'Marcar como publicado'
    
    def mark_as_draft(self, request, queryset):
        queryset.update(status='draft')
        self.message_user(request, f'{queryset.count()} posts marcados como rascunho.')
    mark_as_draft.short_description = 'Marcar como rascunho'
