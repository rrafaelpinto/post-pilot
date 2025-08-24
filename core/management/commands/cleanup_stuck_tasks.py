from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from core.models import Theme, Post


class Command(BaseCommand):
    help = 'Limpa registros presos em estado de processamento'

    def add_arguments(self, parser):
        parser.add_argument(
            '--older-than',
            type=int,
            default=30,
            help='Limpar registros em processamento há mais de X minutos (padrão: 30)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Apenas mostrar o que seria limpo, sem fazer alterações'
        )

    def handle(self, *args, **options):
        older_than_minutes = options['older_than']
        dry_run = options['dry_run']
        
        # Calcular tempo limite
        time_limit = timezone.now() - timedelta(minutes=older_than_minutes)
        
        # Encontrar temas presos
        themes_stuck = Theme.objects.filter(
            is_processing=True,
            updated_at__lt=time_limit
        )
        
        # Encontrar posts presos
        posts_stuck = Post.objects.filter(
            is_processing=True,
            updated_at__lt=time_limit
        )
        
        self.stdout.write(
            self.style.WARNING(
                f'Encontrados {themes_stuck.count()} temas e {posts_stuck.count()} posts '
                f'em processamento há mais de {older_than_minutes} minutos'
            )
        )
        
        if themes_stuck.exists():
            self.stdout.write('\nTemas presos:')
            for theme in themes_stuck:
                self.stdout.write(f'  - Tema {theme.id}: {theme.title} (desde {theme.updated_at})')
        
        if posts_stuck.exists():
            self.stdout.write('\nPosts presos:')
            for post in posts_stuck:
                self.stdout.write(f'  - Post {post.id}: {post.title} (desde {post.updated_at})')
        
        if not dry_run:
            if themes_stuck.exists() or posts_stuck.exists():
                # Limpar temas
                themes_count = themes_stuck.update(
                    is_processing=False,
                    processing_status='timeout'
                )
                
                # Limpar posts
                posts_count = posts_stuck.update(
                    is_processing=False,
                    processing_status='timeout'
                )
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'\n✅ Corrigidos {themes_count} temas e {posts_count} posts!'
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS('✅ Nenhum registro preso encontrado!')
                )
        else:
            self.stdout.write(
                self.style.WARNING('\n🔍 Modo dry-run: nenhuma alteração foi feita.')
            )
            self.stdout.write('Execute sem --dry-run para aplicar as correções.')
