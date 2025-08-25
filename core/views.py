from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .models import Post, Theme
from .tasks import (
    generate_post_content_task,
    generate_topics_task,
    improve_post_content_task,
    regenerate_image_prompt_task,
)
from .services import get_default_ai_service

def dashboard(request):
    """Dashboard principal com estatísticas"""
    total_themes = Theme.objects.filter(is_active=True).count()
    total_posts = Post.objects.count()
    published_posts = Post.objects.filter(status='published').count()
    draft_posts = Post.objects.filter(status='draft').count()
    generated_posts = Post.objects.filter(status='generated').count()
    ai_service = get_default_ai_service()
    ai_service = f'{type(ai_service).__name__}'
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
        'ai_service': ai_service,
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
        
        if title:
            theme = Theme.objects.create(
                title=title,
            )
            messages.success(request, f'Tema "{theme.title}" criado com sucesso!')
            return redirect('theme_detail', theme_id=theme.id)
        else:
            messages.error(request, 'Título é obrigatório.')
    
    return render(request, 'core/theme_create.html')


@require_http_methods(["POST"])
def generate_topics(request, theme_id):
    """Gera tópicos para um tema usando OpenAI de forma assíncrona"""
    theme = get_object_or_404(Theme, id=theme_id)
    
    # Marca que está processando
    theme.is_processing = True
    theme.processing_status = 'processing'
    theme.save()
    
    # Inicia a task assíncrona
    task = generate_topics_task.delay(theme_id)
    
    # Mensagem diferente baseada se já existem tópicos
    if theme.suggested_topics and theme.suggested_topics.get('topics'):
        existing_count = len(theme.suggested_topics['topics'])
        messages.info(request, f'Adicionando mais tópicos ao tema! Você já tem {existing_count} tópicos. A página será atualizada automaticamente quando novos tópicos forem gerados. (Task ID: {task.id})')
    else:
        messages.info(request, f'Geração de tópicos iniciada! A página será atualizada automaticamente quando concluída. (Task ID: {task.id})')
    
    return redirect('theme_detail', theme_id=theme.id)


@require_http_methods(["POST"])
def generate_post_from_topic(request, theme_id):
    """Gera um post baseado em um tópico específico"""
    theme = get_object_or_404(Theme, id=theme_id)
    
    topic = request.POST.get('topic')
    post_type = request.POST.get('post_type', 'simple')
    
    # Coleta dados estruturados do tópico se disponíveis
    topic_data = None
    topic_hook = request.POST.get('topic_hook')
    topic_type = request.POST.get('topic_type')
    topic_summary = request.POST.get('topic_summary')
    topic_cta = request.POST.get('topic_cta')
    
    if any([topic_hook, topic_type, topic_summary, topic_cta]):
        topic_data = {
            'hook': topic_hook,
            'post_type': topic_type,
            'summary': topic_summary,
            'cta': topic_cta
        }
    
    if not topic:
        messages.error(request, 'Tópico é obrigatório.')
        return redirect('theme_detail', theme_id=theme.id)
    
    # Inicia a task assíncrona
    task = generate_post_content_task.delay(theme_id, topic, post_type, topic_data)
    
    messages.info(request, f'Geração de post iniciada! A página será atualizada automaticamente quando concluída. (Task ID: {task.id})')
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


def post_delete(request, post_id):
    """Exclui um post"""
    post = get_object_or_404(Post, id=post_id)
    
    if request.method == 'POST':
        post_title = post.title
        theme_id = post.theme.id
        post.delete()
        
        messages.success(request, f'Post "{post_title}" excluído com sucesso!')
        return redirect('theme_detail', theme_id=theme_id)
    
    return render(request, 'core/post_delete.html', {'post': post})


@require_http_methods(["POST"])
def post_improve(request, post_id):
    """Melhora o conteúdo de um post usando IA de forma assíncrona"""
    post = get_object_or_404(Post, id=post_id)
    
    # Marca que está processando
    post.is_processing = True
    post.processing_status = 'processing'
    post.save()
    
    # Inicia a task assíncrona
    task = improve_post_content_task.delay(post_id)
    
    messages.info(request, f'Melhoria do post iniciada! A página será atualizada automaticamente quando concluída. (Task ID: {task.id})')
    return redirect('post_detail', post_id=post.id)
@require_http_methods(["POST"])
def regenerate_image_prompt(request, post_id):
    """Gera ou regenera o prompt da imagem de capa para um artigo de forma assíncrona"""
    post = get_object_or_404(Post, id=post_id)
    
    # Verificar se é um artigo
    if post.post_type != 'article':
        messages.error(request, 'Apenas artigos podem ter prompt de imagem de capa.')
        return redirect('post_detail', post_id=post.id)
    
    # Marca que está processando
    post.is_processing = True
    post.processing_status = 'processing'
    post.save()
    
    # Inicia a task assíncrona
    task = regenerate_image_prompt_task.delay(post_id)
    
    is_first_generation = not post.cover_image_prompt
    action_type = "geração" if is_first_generation else "regeneração"
    
    messages.info(request, f'{action_type.title()} do prompt da imagem iniciada! A página será atualizada automaticamente quando concluída. (Task ID: {task.id})')
    return redirect('post_detail', post_id=post.id)


# Nova view para verificar status das tasks
def check_task_status(request, task_id):
    """Verifica o status de uma task do Celery"""
    from celery.result import AsyncResult
    
    task_result = AsyncResult(task_id)
    
    response_data = {
        'state': task_result.state,
        'result': task_result.result if task_result.ready() else None,
        'info': task_result.info if not task_result.ready() else None
    }
    
    return JsonResponse(response_data)


def check_theme_status(request):
    """Verifica o status de processamento de um tema ou post"""
    theme_id = request.GET.get('theme_id')
    post_id = request.GET.get('post_id')
    
    if not theme_id and not post_id:
        return JsonResponse({'error': 'theme_id ou post_id é obrigatório'}, status=400)
    
    try:
        if theme_id:
            # Verificar status do tema
            theme = Theme.objects.get(id=theme_id)
            
            # Se está marcado como processando mas sem task há muito tempo, limpar
            from datetime import timedelta

            from django.utils import timezone
            if theme.is_processing and theme.updated_at < timezone.now() - timedelta(minutes=5):
                theme.is_processing = False
                theme.processing_status = 'timeout'
                theme.save()
            
            response_data = {
                'theme_id': theme.id,
                'is_processing': theme.is_processing,
                'processing_status': getattr(theme, 'processing_status', None),
                'status': 'processing' if theme.is_processing else 'completed',
                'has_topics': bool(theme.suggested_topics),
                'topics_count': len(theme.suggested_topics.get('topics', [])) if theme.suggested_topics else 0
            }
            
        elif post_id:
            # Verificar status do post
            post = Post.objects.get(id=post_id)
            
            # Se está marcado como processando mas sem task há muito tempo, limpar
            from datetime import timedelta

            from django.utils import timezone
            if post.is_processing and post.updated_at < timezone.now() - timedelta(minutes=5):
                post.is_processing = False
                post.processing_status = 'timeout'
                post.save()
            
            response_data = {
                'post_id': post.id,
                'is_processing': post.is_processing,
                'processing_status': getattr(post, 'processing_status', None),
                'status': 'processing' if post.is_processing else 'completed',
                'title': post.title,
                'content_length': len(post.content) if post.content else 0
            }
        
        return JsonResponse(response_data)
        
    except (Theme.DoesNotExist, Post.DoesNotExist):
        return JsonResponse({'error': 'Item não encontrado'}, status=404)