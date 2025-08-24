from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from .models import Theme, Post
from .services import OpenAIService


def dashboard(request):
    """Dashboard principal com estatísticas"""
    total_themes = Theme.objects.filter(is_active=True).count()
    total_posts = Post.objects.count()
    published_posts = Post.objects.filter(status='published').count()
    draft_posts = Post.objects.filter(status='draft').count()
    generated_posts = Post.objects.filter(status='generated').count()
    
    recent_posts = Post.objects.order_by('-created_at')[:5]
    recent_themes = Theme.objects.filter(is_active=True).order_by('-created_at')[:5]
    
    context = {
        'total_themes': total_themes,
        'total_posts': total_posts,
        'published_posts': published_posts,
        'draft_posts': draft_posts,
        'generated_posts': generated_posts,
        'recent_posts': recent_posts,
        'recent_themes': recent_themes,
    }
    
    return render(request, 'core/dashboard.html', context)


# VIEWS PARA TEMAS
def theme_list(request):
    """Lista todos os temas"""
    themes = Theme.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'core/theme_list.html', {'themes': themes})


def theme_detail(request, theme_id):
    """Detalhe de um tema específico"""
    theme = get_object_or_404(Theme, id=theme_id)
    posts = theme.posts.all().order_by('-created_at')
    return render(request, 'core/theme_detail.html', {
        'theme': theme,
        'posts': posts
    })


def theme_create(request):
    """Cria um novo tema"""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        
        if title and description:
            theme = Theme.objects.create(
                title=title,
                description=description
            )
            messages.success(request, f'Tema "{theme.title}" criado com sucesso!')
            return redirect('theme_detail', theme_id=theme.id)
        else:
            messages.error(request, 'Título e descrição são obrigatórios.')
    
    return render(request, 'core/theme_create.html')


@require_http_methods(["POST"])
def generate_topics(request, theme_id):
    """Gera tópicos para um tema usando OpenAI"""
    theme = get_object_or_404(Theme, id=theme_id)
    
    try:
        openai_service = OpenAIService()
        topics_data = openai_service.generate_topics(theme.title, theme.description)
        
        if topics_data.get('topics'):
            theme.suggested_topics = topics_data
            theme.topics_generated_at = timezone.now()
            theme.save()
            
            messages.success(request, f'{len(topics_data["topics"])} tópicos gerados com sucesso!')
        else:
            messages.error(request, 'Não foi possível gerar tópicos. Tente novamente.')
            
    except Exception as e:
        messages.error(request, f'Erro ao gerar tópicos: {str(e)}')
    
    return redirect('theme_detail', theme_id=theme.id)


@require_http_methods(["POST"])
def generate_post_from_topic(request, theme_id):
    """Gera um post baseado em um tópico específico"""
    theme = get_object_or_404(Theme, id=theme_id)
    
    topic = request.POST.get('topic')
    post_type = request.POST.get('post_type', 'simple')
    
    if not topic:
        messages.error(request, 'Tópico é obrigatório.')
        return redirect('theme_detail', theme_id=theme.id)
    
    # Verifica se já existe um post deste tipo para este tema
    existing_post = Post.objects.filter(theme=theme, post_type=post_type).first()
    if existing_post:
        messages.warning(request, f'Já existe um {existing_post.get_post_type_display().lower()} para este tema.')
        return redirect('theme_detail', theme_id=theme.id)
    
    try:
        openai_service = OpenAIService()
        content_data = openai_service.generate_post_content(topic, post_type, theme.title)
        
        # Cria o post
        post = Post.objects.create(
            theme=theme,
            post_type=post_type,
            title=content_data.get('title', f'Post sobre {topic}'),
            content=content_data.get('content', ''),
            topic=topic,
            seo_title=content_data.get('seo_title', topic[:60]),
            seo_description=content_data.get('seo_description', ''),
            status='generated',
            generated_at=timezone.now(),
            generation_prompt=f"Tópico: {topic}, Tipo: {post_type}",
            ai_model_used="gpt-4" if post_type == 'article' else "gpt-3.5-turbo"
        )
        
        messages.success(request, f'{post.get_post_type_display()} gerado com sucesso!')
        
    except Exception as e:
        messages.error(request, f'Erro ao gerar post: {str(e)}')
    
    return redirect('theme_detail', theme_id=theme.id)


# VIEWS PARA POSTS
def post_list(request):
    """Lista todos os posts"""
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'core/post_list.html', {'posts': posts})


def post_detail(request, post_id):
    """Detalhe de um post específico"""
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'core/post_detail.html', {'post': post})


def post_edit(request, post_id):
    """Edita um post"""
    post = get_object_or_404(Post, id=post_id)
    
    if request.method == 'POST':
        post.title = request.POST.get('title', post.title)
        post.content = request.POST.get('content', post.content)
        post.seo_title = request.POST.get('seo_title', post.seo_title)
        post.seo_description = request.POST.get('seo_description', post.seo_description)
        post.link = request.POST.get('link', post.link)
        post.status = request.POST.get('status', post.status)
        
        # Se agendado, captura a data
        if post.status == 'scheduled':
            scheduled_date = request.POST.get('scheduled_date')
            if scheduled_date:
                post.scheduled_date = scheduled_date
        
        post.save()
        messages.success(request, 'Post atualizado com sucesso!')
        return redirect('post_detail', post_id=post.id)
    
    return render(request, 'core/post_edit.html', {'post': post})


def post_publish(request, post_id):
    """Publica um post"""
    post = get_object_or_404(Post, id=post_id)
    
    if request.method == 'POST':
        post.status = 'published'
        post.post_date = timezone.now()
        post.save()
        
        messages.success(request, f'Post "{post.title}" publicado com sucesso!')
    
    return redirect('post_detail', post_id=post.id)
