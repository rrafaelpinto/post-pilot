# Post Pilot - Gerador de Posts LinkedIn com IA

Sistema Django para geração de posts e artigos no LinkedIn utilizando OpenAI API com processamento assíncrono via Celery.

## 🚀 Funcionalidades

- **Geração de Tópicos**: IA gera 3-5 tópicos estruturados para cada tema
- **Criação de Posts**: Gera posts simples (até 1300 caracteres) ou artigos longos
- **Melhoria de Conteúdo**: Aprimora posts existentes com exemplos práticos e código seguro
- **Processamento Assíncrono**: Utiliza Celery + Redis para chamadas de API não bloqueantes
- **Interface Web Completa**: Dashboard para gerenciar temas, posts e visualizar estatísticas
- **Renderização Markdown**: Suporte completo a Markdown nos posts gerados
- **Monitoramento**: Interface Flower para acompanhar tarefas em tempo real

## 🛠 Stack Tecnológica

- **Backend**: Django 5.2.5
- **IA**: OpenAI API (GPT-4o, GPT-4o-mini)
- **Queue System**: Celery + Redis
- **Database**: SQLite (desenvolvimento) / PostgreSQL (produção)
- **Frontend**: Bootstrap 5.1.3
- **Monitoramento**: Flower
- **Markdown**: Python-Markdown

## 📋 Pré-requisitos

- Python 3.11+
- Redis Server
- Conta na OpenAI com API Key

## 🔧 Instalação e Configuração

### 1. Clone o Repositório
```bash
git clone <repository-url>
cd post-pilot
```

### 2. Configuração do Ambiente Virtual
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate     # Windows
```

### 3. Instalação das Dependências
```bash
pip install django python-dotenv openai markdown
pip install celery redis django-celery-beat flower
```

### 4. Configuração das Variáveis de Ambiente
```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas configurações:
```env
# OpenAI Configuration
OPENAI_API_KEY=sua_chave_da_openai_aqui

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Django Configuration
DEBUG=True
SECRET_KEY=sua_chave_secreta_aqui
```

### 5. Instalação e Configuração do Redis

#### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

#### macOS (Homebrew):
```bash
brew install redis
brew services start redis
```

#### Windows:
Baixe e instale o Redis do [repositório oficial](https://github.com/microsoftarchive/redis/releases)

### 6. Configuração do Banco de Dados
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

## 🚀 Executando o Sistema

### Método Recomendado: Múltiplos Terminais

#### Terminal 1 - Django Server:
```bash
python manage.py runserver
```

#### Terminal 2 - Celery Worker:
```bash
./scripts/start_worker.sh
# ou manualmente:
celery -A post_pilot worker --loglevel=info --concurrency=2 --queues=default,ai_tasks
```

#### Terminal 3 - Celery Beat (Scheduler):
```bash
./scripts/start_beat.sh
# ou manualmente:
celery -A post_pilot beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

#### Terminal 4 - Flower (Monitoramento):
```bash
./scripts/start_flower.sh
# ou manualmente:
celery -A post_pilot flower --port=5555
```

### Acessos:
- **Aplicação Web**: http://localhost:8000
- **Admin Django**: http://localhost:8000/admin
- **Flower (Monitoramento)**: http://localhost:5555

## 📖 Como Usar

### 1. Criar um Tema
1. Acesse o dashboard
2. Clique em "Criar Novo Tema"
3. Digite o título do tema (ex: "React Hooks", "Python FastAPI", "Docker")

### 2. Gerar Tópicos
1. Na página do tema, clique em "Gerar Tópicos"
2. A IA criará 3-5 tópicos estruturados com hooks, resumos e CTAs
3. O processamento é assíncrono - você pode acompanhar via Flower

### 3. Criar Posts
1. Para cada tópico, escolha:
   - **Post Simples**: Até 1300 caracteres, otimizado para LinkedIn
   - **Artigo**: 1000-1500 palavras + post promocional
2. O conteúdo é gerado em formato Markdown

### 4. Melhorar Posts
1. Na página do post, clique em "Melhorar Post"
2. A IA expandirá o conteúdo com:
   - Exemplos práticos de código
   - Explicações detalhadas
   - Considerações de segurança
   - Boas práticas

## 🔄 Arquitetura Assíncrona

### Fluxo de Processamento:
1. **Interface Web** → Dispara tarefa Celery
2. **Redis** → Armazena a tarefa na fila
3. **Celery Worker** → Processa chamada à OpenAI API
4. **Resultado** → Atualiza o banco de dados
5. **Interface** → Exibe resultado ou status

### Filas Configuradas:
- `default`: Tarefas gerais
- `ai_tasks`: Chamadas específicas para OpenAI (isoladas)

### Retry Strategy:
- **Máximo**: 3 tentativas
- **Delay**: Progressivo (60s, 120s, 180s)
- **Timeout**: 10 minutos por tarefa

## 📊 Monitoramento com Flower

Acesse http://localhost:5555 para:
- Visualizar tarefas em execução
- Acompanhar filas e workers
- Ver histórico de execuções
- Monitorar performance

## 🔧 Configurações Avançadas

### Modelos OpenAI Utilizados:
- **Tópicos**: GPT-4o-mini (econômico e rápido)
- **Posts Simples**: GPT-4o-mini
- **Artigos**: GPT-4o (maior qualidade)
- **Melhorias**: GPT-4o (melhor análise)

### Configurações de Performance:
```python
# settings.py
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_TASK_SOFT_TIME_LIMIT = 300  # 5 minutos
CELERY_TASK_TIME_LIMIT = 600       # 10 minutos
```

## 🐛 Troubleshooting

### Redis não conecta:
```bash
# Verificar se Redis está rodando
redis-cli ping  # Deve retornar "PONG"

# Verificar porta
sudo netstat -tlnp | grep :6379
```

### Celery Worker não inicia:
```bash
# Verificar logs
celery -A post_pilot worker --loglevel=debug

# Verificar configurações
python manage.py shell
>>> from django.conf import settings
>>> print(settings.CELERY_BROKER_URL)
```

### OpenAI API Timeout:
```bash
# Verificar API Key
python manage.py shell
>>> import os
>>> print(os.getenv('OPENAI_API_KEY'))
```

## 📝 Estrutura de Dados

### Theme Model:
- `title`: Título do tema
- `suggested_topics`: Tópicos gerados pela IA (JSON)
- `processing_status`: Status do processamento assíncrono

### Post Model:
- `post_type`: 'simple' ou 'article'
- `content`: Conteúdo em Markdown
- `promotional_post`: Post promocional (apenas artigos)
- `processing_status`: Status do processamento assíncrono

## 🚀 Produção

### Configurações Recomendadas:
```bash
# PostgreSQL
pip install psycopg2-binary

# Gunicorn
pip install gunicorn

# Supervisor para gerenciar processos
sudo apt install supervisor
```

### Docker Compose (Opcional):
```yaml
version: '3.8'
services:
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
  
  worker:
    build: .
    command: celery -A post_pilot worker
    depends_on:
      - redis
```

## 📄 Licença

Este projeto está sob licença MIT. Veja o arquivo LICENSE para mais detalhes.

## 🤝 Contribuições

Contribuições são bem-vindas! Por favor:
1. Faça um fork do projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 🆘 Suporte

Para dúvidas e suporte:
- Abra uma issue no GitHub
- Consulte a documentação do Django
- Verifique a documentação do Celery

---

**Desenvolvido com ❤️ para otimizar a criação de conteúdo técnico no LinkedIn**

Sistema Django para geração automática de postagens para LinkedIn usando OpenAI.

## Funcionalidades

- **Gestão de Temas**: Crie temas para suas postagens
- **Geração de Tópicos**: Use IA para gerar 3-5 tópicos relevantes baseados no tema
- **Geração de Conteúdo**: Crie posts simples ou artigos baseados nos tópicos
- **Tipos de Conteúdo**: 
  - Posts simples (até 1300 caracteres)
  - Artigos (800-1200 palavras)
- **SEO**: Título e descrição otimizados para cada post
- **Status de Publicação**: Rascunho, Gerado, Publicado, Agendado

## Instalação

1. Clone o repositório
2. Instale as dependências:
```bash
pip install django openai python-dotenv
```

3. Configure a chave da OpenAI no arquivo `.env`:
```
OPENAI_API_KEY=sua_chave_aqui
```

4. Execute as migrações:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Crie um superusuário:
```bash
python manage.py createsuperuser
```

6. Execute o servidor:
```bash
python manage.py runserver
```

## Uso

### 1. Criar um Tema
- Acesse `/themes/create/`
- Defina título e descrição detalhada do tema
- O tema servirá como base para geração de tópicos

### 2. Gerar Tópicos
- Na página do tema, clique em "Gerar Tópicos"
- A IA irá sugerir 3-5 tópicos relevantes
- Os tópicos ficam salvos no tema

### 3. Gerar Posts
- Selecione um tópico gerado
- Escolha o tipo (Post Simples ou Artigo)
- A IA irá criar o conteúdo completo
- Cada tema pode ter 1 artigo + 1 post simples

### 4. Gerenciar Posts
- Edite o conteúdo gerado se necessário
- Defina status (rascunho, publicado, agendado)
- Adicione links relacionados

## Estrutura do Projeto

```
post_pilot/
├── core/                   # App principal
│   ├── models.py          # Theme e Post models
│   ├── admin.py           # Interface admin
│   ├── views.py           # Views principais
│   ├── services.py        # Integração OpenAI
│   └── urls.py            # URLs do app
├── templates/core/        # Templates HTML
├── post_pilot/           # Configurações Django
└── db.sqlite3           # Banco SQLite
```

## Modelos

### Theme
- Título e descrição
- Tópicos sugeridos (JSON)
- Data de geração dos tópicos
- Status ativo/inativo

### Post
- Relacionado a um tema
- Tipo: simples ou artigo
- Título, conteúdo, tópico
- SEO: título e descrição
- Link opcional
- Status e datas de controle
- Metadados de geração (prompt, modelo usado)

## Admin Interface

Acesse `/admin/` para:
- Gerenciar temas e posts
- Ver estatísticas
- Ações em lote (marcar como publicado/rascunho)
- Filtros por tipo, status, data

## Agentes OpenAI

### Agente 1 - Geração de Tópicos
- Modelo: GPT-3.5-turbo
- Recebe tema e descrição
- Retorna 3-5 tópicos específicos em JSON

### Agente 2 - Geração de Conteúdo
- Modelo: GPT-3.5-turbo (posts) / GPT-4 (artigos)
- Recebe tópico e tipo de conteúdo
- Segue templates pré-definidos
- Retorna título, conteúdo e SEO em JSON

## URLs Principais

- `/` - Dashboard
- `/themes/` - Lista de temas
- `/themes/create/` - Criar tema
- `/themes/{id}/` - Detalhe do tema
- `/posts/` - Lista de posts
- `/posts/{id}/` - Detalhe do post
- `/admin/` - Interface administrativa

## Configurações

Variáveis de ambiente no `.env`:
- `OPENAI_API_KEY` - Chave da API OpenAI (obrigatória)
- `SECRET_KEY` - Chave secreta Django (opcional para dev)

## Próximos Passos

- Implementar agendamento de publicação
- Integração com LinkedIn API
- Analytics de performance
- Templates personalizáveis
- Aprovação em workflow