from django.db import models
from django.utils import timezone


class Theme(models.Model):
    """Modelo para temas de postagens"""
    title = models.CharField(max_length=200, verbose_name="Título do Tema")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    
    # Campos para armazenar os tópicos sugeridos pela OpenAI
    suggested_topics = models.JSONField(
        null=True, 
        blank=True, 
        verbose_name="Tópicos Sugeridos",
        help_text="Tópicos sugeridos pelo primeiro agente da OpenAI"
    )
    topics_generated_at = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name="Tópicos gerados em"
    )
    
    class Meta:
        verbose_name = "Tema"
        verbose_name_plural = "Temas"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def posts_count(self):
        """Retorna o número total de posts relacionados a este tema"""
        return self.posts.count()
    
    @property
    def articles_count(self):
        """Retorna o número de artigos relacionados a este tema"""
        return self.posts.filter(post_type='article').count()
    
    @property
    def simple_posts_count(self):
        """Retorna o número de posts simples relacionados a este tema"""
        return self.posts.filter(post_type='simple').count()


class Post(models.Model):
    """Modelo para postagens do LinkedIn"""
    
    POST_TYPES = [
        ('simple', 'Post Simples'),
        ('article', 'Artigo'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Rascunho'),
        ('generated', 'Gerado'),
        ('published', 'Publicado'),
        ('scheduled', 'Agendado'),
    ]
    
    # Informações básicas
    theme = models.ForeignKey(
        Theme, 
        on_delete=models.CASCADE, 
        related_name='posts',
        verbose_name="Tema"
    )
    post_type = models.CharField(
        max_length=10, 
        choices=POST_TYPES, 
        verbose_name="Tipo de Post"
    )
    title = models.CharField(max_length=200, verbose_name="Título")
    content = models.TextField(verbose_name="Conteúdo")
    promotional_post = models.TextField(
        blank=True,
        verbose_name="Post Promocional",
        help_text="Post resumido para promover artigos no LinkedIn"
    )
    topic = models.CharField(
        max_length=200, 
        verbose_name="Tópico",
        help_text="Tópico específico usado para gerar este post"
    )
    
    # SEO
    seo_title = models.CharField(
        max_length=60, 
        verbose_name="Título SEO",
        help_text="Título otimizado para SEO (máx. 60 caracteres)"
    )
    seo_description = models.CharField(
        max_length=160, 
        verbose_name="Descrição SEO",
        help_text="Descrição otimizada para SEO (máx. 160 caracteres)"
    )
    
    # Link e datas
    link = models.URLField(
        blank=True, 
        null=True, 
        verbose_name="Link",
        help_text="Link relacionado ao post (opcional)"
    )
    post_date = models.DateTimeField(
        default=timezone.now, 
        verbose_name="Data da Postagem"
    )
    scheduled_date = models.DateTimeField(
        blank=True, 
        null=True, 
        verbose_name="Data Agendada"
    )
    
    # Controle
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='draft',
        verbose_name="Status"
    )
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    generated_at = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name="Gerado em",
        help_text="Data e hora em que o conteúdo foi gerado pela IA"
    )
    
    # Metadados da geração
    generation_prompt = models.TextField(
        blank=True, 
        verbose_name="Prompt de Geração",
        help_text="Prompt usado para gerar o conteúdo"
    )
    ai_model_used = models.CharField(
        max_length=50, 
        blank=True, 
        verbose_name="Modelo de IA Usado"
    )
    
    class Meta:
        verbose_name = "Post"
        verbose_name_plural = "Posts"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.get_post_type_display()})"
    
    def save(self, *args, **kwargs):
        # Se está sendo gerado pela primeira vez, define a data de geração
        if self.status == 'generated' and not self.generated_at:
            self.generated_at = timezone.now()
        super().save(*args, **kwargs)
    
    @property
    def is_published(self):
        """Verifica se o post foi publicado"""
        return self.status == 'published'
    
    @property
    def is_scheduled(self):
        """Verifica se o post está agendado"""
        return self.status == 'scheduled' and self.scheduled_date and self.scheduled_date > timezone.now()
    
    @property
    def content_preview(self):
        """Retorna uma prévia do conteúdo (primeiros 100 caracteres)"""
        if len(self.content) > 100:
            return self.content[:100] + "..."
        return self.content
