# Multi-AI Provider Support

O Post Pilot agora suporta múltiplos provedores de AI para geração de conteúdo. Você pode escolher entre OpenAI, Grok (X.AI) ou Google Gemini.

## Provedores Disponíveis

### 1. OpenAI (GPT-4)
- **Modelo padrão**: gpt-4o / gpt-4o-mini
- **Ponto forte**: Excelente qualidade geral, ampla compatibilidade
- **Configuração**: Requer `OPENAI_API_KEY`

### 2. Grok (X.AI)
- **Modelo padrão**: grok-beta
- **Ponto forte**: Criado pela X (Twitter), conhecimento atualizado
- **Configuração**: Requer `GROK_API_KEY`

### 3. Google Gemini
- **Modelo padrão**: gemini-1.5-pro
- **Ponto forte**: Boa integração com ecossistema Google
- **Configuração**: Requer `GEMINI_API_KEY`

## Configuração

### 1. Variáveis de Ambiente

Adicione as chaves de API necessárias no seu arquivo `.env`:

```bash
# Provedor padrão (openai, grok, gemini)
DEFAULT_AI_PROVIDER=openai

# Chaves de API (configure apenas as que pretende usar)
OPENAI_API_KEY=sk-your-openai-api-key-here
GROK_API_KEY=xai-your-grok-api-key-here
GEMINI_API_KEY=your-gemini-api-key-here
```

### 2. Obter Chaves de API

#### OpenAI
1. Acesse [platform.openai.com](https://platform.openai.com/)
2. Crie uma conta ou faça login
3. Vá para API Keys e crie uma nova chave
4. Adicione créditos à sua conta

#### Grok (X.AI)
1. Acesse [x.ai](https://x.ai/)
2. Solicite acesso à API (ainda em beta)
3. Obtenha sua chave quando aprovado

#### Google Gemini
1. Acesse [ai.google.dev](https://ai.google.dev/)
2. Crie um projeto no Google Cloud Console
3. Ative a API do Gemini
4. Crie uma chave de API

## Gerenciamento de Provedores

Use o comando de gerenciamento para administrar os provedores:

### Listar provedores disponíveis
```bash
python manage.py ai_provider --list
```

### Ver provedor atual
```bash
python manage.py ai_provider --current
```

### Trocar provedor padrão
```bash
python manage.py ai_provider --set openai
python manage.py ai_provider --set grok
python manage.py ai_provider --set gemini
```

### Testar conexão com um provedor
```bash
python manage.py ai_provider --test openai
python manage.py ai_provider --test grok
python manage.py ai_provider --test gemini
```

## Arquitetura

O sistema utiliza um padrão Factory para criar instâncias dos serviços:

```python
from core.services import AIServiceFactory, get_default_ai_service

# Usar o provedor padrão
ai_service = get_default_ai_service()

# Criar um provedor específico
openai_service = AIServiceFactory.create_service('openai')
grok_service = AIServiceFactory.create_service('grok')
gemini_service = AIServiceFactory.create_service('gemini')
```

## Interface Comum

Todos os provedores implementam a mesma interface:

```python
# Gerar tópicos
topics = ai_service.generate_topics('Python', existing_topics=[])

# Gerar conteúdo de post
content = ai_service.generate_post_content('Python Tips', 'simple', 'Python', topic_data)

# Melhorar conteúdo existente
improved = ai_service.improve_post_content(content, title, 'simple', 'Python Tips')

# Gerar prompt de imagem
image_prompt = ai_service.regenerate_cover_image_prompt(title, topic, theme)
```

## Migração de Provedor

Para migrar de um provedor para outro:

1. **Configure a nova chave de API** no `.env`
2. **Teste a conexão**: `python manage.py ai_provider --test novo_provedor`
3. **Troque o provedor**: `python manage.py ai_provider --set novo_provedor`
4. **Atualize o .env** para tornar permanente: `DEFAULT_AI_PROVIDER=novo_provedor`
5. **Reinicie o Celery** para aplicar as mudanças nas tasks

## Custos e Limites

### OpenAI
- **GPT-4o**: ~$5-15 por 1M tokens
- **GPT-4o-mini**: ~$0.15-0.60 por 1M tokens
- Limites de rate: Dependem do tier da conta

### Grok
- Preços em definição (ainda em beta)
- Acesso limitado por convite

### Gemini
- **Gemini 1.5 Pro**: Tier gratuito disponível
- Limites de rate: 15 RPM no tier gratuito

## Troubleshooting

### Erro de autenticação
```bash
# Verificar se a chave está configurada
python manage.py ai_provider --current

# Testar conexão
python manage.py ai_provider --test provedor
```

### Tasks falhando após mudança de provedor
```bash
# Reiniciar workers do Celery
celery -A post_pilot worker --loglevel=info --reload
```

### Verificar configuração
```python
from django.conf import settings
print(f"Provedor padrão: {settings.DEFAULT_AI_PROVIDER}")
print(f"OpenAI configurado: {'✓' if settings.OPENAI_API_KEY else '✗'}")
print(f"Grok configurado: {'✓' if getattr(settings, 'GROK_API_KEY', '') else '✗'}")
print(f"Gemini configurado: {'✓' if getattr(settings, 'GEMINI_API_KEY', '') else '✗'}")
```

## Recomendações

### Para produção
- **OpenAI GPT-4o**: Melhor qualidade geral, mais estável
- Configure limites de rate e monitoring

### Para desenvolvimento
- **OpenAI GPT-4o-mini**: Mais econômico, boa qualidade
- **Gemini**: Tier gratuito disponível

### Para experimentação
- **Grok**: Conhecimento mais atualizado (quando disponível)
- Compare resultados entre diferentes provedores
