# Post Pilot

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