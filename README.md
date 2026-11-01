# QA Sprint

Sistema web local para gestão de projetos, casos de teste e bugs.  
Stack: Python + Flask, SQLite + SQLAlchemy, Jinja2 + Bootstrap 5.

---

## Requisitos

- Python 3.10+
- Windows CMD (PowerShell também funciona)

---

## Instalação e Execução

### 1. Criar e ativar o ambiente virtual

```cmd
cd D:\projeto\qa-sprint-claude
python -m venv .venv
.venv\Scripts\activate
```

### 2. Instalar dependências

```cmd
pip install -r requirements.txt
```

### 3. Inicializar o banco de dados

```cmd
flask init-db
```

> O banco SQLite é criado em `instance/qa_sprint.db`. O comando **não apaga dados existentes** — apenas cria as tabelas que não existirem.

### 4. Iniciar a aplicação

```cmd
python run.py
```

A aplicação estará disponível em: **http://127.0.0.1:5000**

---

## Executar os Testes

```cmd
.venv\Scripts\activate
pytest -v
```

Ou com cobertura:

```cmd
pytest --cov=qa_sprint --cov-report=term-missing
```

Os testes usam um banco de dados **temporário em memória** (SQLite `:memory:`), não tocando no banco de desenvolvimento.

---

## Estrutura do Projeto

```
qa-sprint-claude/
├── .gitignore
├── requirements.txt
├── config.py
├── run.py
├── README.md
├── instance/
│   └── qa_sprint.db          (criado automaticamente)
├── qa_sprint/
│   ├── __init__.py           (application factory)
│   ├── extensions.py         (db, csrf)
│   ├── models.py             (modelo Project)
│   ├── commands.py           (comando flask init-db)
│   ├── main/
│   │   ├── __init__.py
│   │   ├── routes.py         (dashboard, 404, 500)
│   │   ├── forms.py
│   │   └── templates/
│   │       ├── base.html
│   │       ├── dashboard.html
│   │       ├── 404.html
│   │       └── 500.html
│   └── projects/
│       ├── __init__.py
│       ├── routes.py         (CRUD de projetos)
│       ├── forms.py
│       └── templates/
│           └── projects/
│               ├── list.html
│               ├── create.html
│               ├── detail.html
│               ├── edit.html
│               └── delete.html
└── tests/
    ├── __init__.py
    ├── conftest.py           (fixtures pytest)
    ├── test_models.py
    ├── test_projects_routes.py
    └── test_dashboard.py
```

---

## Funcionalidades Implementadas

### Dashboard
- Contagem total de projetos
- Contagem de projetos ativos
- Contagem de projetos arquivados
- Botão para criar novo projeto

### CRUD de Projetos
| Operação | Rota | Método |
|----------|------|--------|
| Listar | `/projetos/` | GET |
| Criar | `/projetos/novo` | GET, POST |
| Detalhes | `/projetos/<id>` | GET |
| Editar | `/projetos/<id>/editar` | GET, POST |
| Excluir | `/projetos/<id>/excluir` | GET (confirma), POST (executa) |

### Validações
- **Nome**: obrigatório, máx. 120 caracteres, espaços nas extremidades removidos, único
- **Descrição**: opcional, máx. 2000 caracteres
- **Status**: apenas "Ativo" ou "Arquivado" (padrão: "Ativo")
- **CSRF**: proteção em todos os formulários
- **404**: retornado para projetos inexistentes

### Interface
- Tema escuro (dark mode) consistente
- Layout responsivo com Bootstrap 5
- Navegação: Dashboard ↔ Projetos
- Mensagens de sucesso/erro em português
- Estados vazios informativos
- Paginação na listagem (10 por página)

---

## Variáveis de Ambiente

Crie um arquivo `.env` na raiz se quiser sobrescrever configurações:

```env
SECRET_KEY=sua-chave-secreta-aqui
DATABASE_URL=sqlite:///instance/qa_sprint.db
FLASK_ENV=development
```

---

## Licença

Projeto educacional / interno.