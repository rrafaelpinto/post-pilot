from django import template
import markdown

register = template.Library()

@register.filter
def markdown_to_html(value):
    """
    Converte texto Markdown para HTML com sintaxe destacada
    """
    if not value:
        return ""
    
    # Configurar extensões do markdown
    extensions = [
        'markdown.extensions.fenced_code',
        'markdown.extensions.codehilite',
        'markdown.extensions.tables',
        'markdown.extensions.toc',
        'markdown.extensions.nl2br',
        'markdown.extensions.sane_lists'
    ]
    
    # Configurações para destacar código
    extension_configs = {
        'markdown.extensions.codehilite': {
            'css_class': 'highlight',
            'use_pygments': False,  # Use CSS highlighting
        }
    }
    
    # Converter markdown para HTML
    md = markdown.Markdown(
        extensions=extensions,
        extension_configs=extension_configs
    )
    
    return md.convert(value)
