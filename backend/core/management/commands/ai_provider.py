from django.core.management.base import BaseCommand
from django.conf import settings
from core.services import AIServiceFactory
import os


class Command(BaseCommand):
    help = 'Manage AI provider configuration'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--list',
            action='store_true',
            help='List all available AI providers'
        )
        parser.add_argument(
            '--current',
            action='store_true',
            help='Show current AI provider'
        )
        parser.add_argument(
            '--set',
            type=str,
            help='Set the default AI provider (openai, grok, gemini)'
        )
        parser.add_argument(
            '--test',
            type=str,
            help='Test connection to specific AI provider'
        )
    
    def handle(self, *args, **options):
        if options['list']:
            self.list_providers()
        elif options['current']:
            self.show_current_provider()
        elif options['set']:
            self.set_provider(options['set'])
        elif options['test']:
            self.test_provider(options['test'])
        else:
            self.stdout.write(self.style.ERROR('Please provide an action. Use --help for available options.'))
    
    def list_providers(self):
        """List all available AI providers"""
        providers = AIServiceFactory.get_available_providers()
        self.stdout.write(self.style.SUCCESS('Available AI providers:'))
        
        for provider in providers:
            current_mark = ' (CURRENT)' if provider == getattr(settings, 'DEFAULT_AI_PROVIDER', 'openai') else ''
            self.stdout.write(f'  • {provider}{current_mark}')
        
        self.stdout.write('')
        self.stdout.write('To set a provider as default: python manage.py ai_provider --set <provider>')
    
    def show_current_provider(self):
        """Show current default AI provider"""
        current_provider = getattr(settings, 'DEFAULT_AI_PROVIDER', 'openai')
        self.stdout.write(self.style.SUCCESS(f'Current default AI provider: {current_provider}'))
        
        # Check if API key is configured
        api_key_settings = {
            'openai': 'OPENAI_API_KEY',
            'grok': 'GROK_API_KEY',
            'gemini': 'GEMINI_API_KEY'
        }
        
        setting_name = api_key_settings.get(current_provider)
        if setting_name:
            api_key = getattr(settings, setting_name, '')
            if api_key:
                self.stdout.write(self.style.SUCCESS(f'✓ API key is configured for {current_provider}'))
            else:
                self.stdout.write(self.style.WARNING(f'⚠ API key is NOT configured for {current_provider}'))
                self.stdout.write(f'  Set {setting_name} in your environment variables')
    
    def set_provider(self, provider):
        """Set default AI provider"""
        available_providers = AIServiceFactory.get_available_providers()
        
        if provider not in available_providers:
            self.stdout.write(
                self.style.ERROR(f'Invalid provider: {provider}')
            )
            self.stdout.write(f'Available providers: {", ".join(available_providers)}')
            return
        
        # Update environment variable (for current session only)
        os.environ['DEFAULT_AI_PROVIDER'] = provider
        
        self.stdout.write(
            self.style.SUCCESS(f'Default AI provider set to: {provider}')
        )
        self.stdout.write('')
        self.stdout.write('Note: This change is temporary for the current session.')
        self.stdout.write(f'To make it permanent, set DEFAULT_AI_PROVIDER={provider} in your .env file')
        
        # Check API key configuration
        api_key_settings = {
            'openai': 'OPENAI_API_KEY',
            'grok': 'GROK_API_KEY', 
            'gemini': 'GEMINI_API_KEY'
        }
        
        setting_name = api_key_settings.get(provider)
        if setting_name:
            api_key = getattr(settings, setting_name, '')
            if not api_key:
                self.stdout.write('')
                self.stdout.write(self.style.WARNING(f'⚠ Warning: {setting_name} is not configured'))
                self.stdout.write(f'  Please set {setting_name} in your .env file to use {provider}')
    
    def test_provider(self, provider):
        """Test connection to AI provider"""
        available_providers = AIServiceFactory.get_available_providers()
        
        if provider not in available_providers:
            self.stdout.write(
                self.style.ERROR(f'Invalid provider: {provider}')
            )
            self.stdout.write(f'Available providers: {", ".join(available_providers)}')
            return
        
        try:
            # Create service instance
            service = AIServiceFactory.create_service(provider)
            
            # Test with a simple topic generation
            self.stdout.write(f'Testing connection to {provider}...')
            result = service.generate_topics('Python Testing', existing_topics=[])
            
            if result and result.get('topics'):
                self.stdout.write(self.style.SUCCESS(f'✓ {provider} connection successful!'))
                self.stdout.write(f'  Generated {len(result["topics"])} test topics')
            else:
                self.stdout.write(self.style.WARNING(f'⚠ {provider} connection failed or returned empty result'))
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ {provider} connection failed: {str(e)}'))
            
            # Provide specific error help
            if 'API key' in str(e) or 'authentication' in str(e).lower():
                api_key_settings = {
                    'openai': 'OPENAI_API_KEY',
                    'grok': 'GROK_API_KEY',
                    'gemini': 'GEMINI_API_KEY'
                }
                setting_name = api_key_settings.get(provider)
                if setting_name:
                    self.stdout.write(f'  Check that {setting_name} is correctly set in your .env file')
