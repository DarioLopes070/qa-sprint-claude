# QA Sprint

Sistema web local completo para gestão de QA, incluindo projetos, casos de teste, execuções e bugs.  
Stack: Python + Flask, SQLite + SQLAlchemy, Jinja2 + Bootstrap 5.

**Funcionalidades implementadas:**
- Gestão completa de Projetos (CRUD)
- Casos de teste com passos, resultado esperado e associação a projetos
- Registro de execuções de testes com histórico (aprovado, reprovado, bloqueado)
- Gestão completa de Bugs com severidade e status
- Dashboard com indicadores reais calculados a partir do banco de dados
- Filtro por projeto em todas as listagens
- Tema escuro com acessibilidade WCAG AA

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

### Cobertura Atual

A suíte de testes inclui:
- **31 testes** originais (projetos, dashboard)
- **16 testes** de TestCase e TestExecution (modelos, validações, relacionamentos, cascade delete)
- **19 testes** de Bug e relacionamentos Project (modelos, validações, contagens, cascade delete)
- **28 testes** de integração para rotas de Test Cases e Bugs (CRUD, execuções, validação, CSRF, redirects, flash, 404, cascade)

**Total: 94 testes passando**

Áreas cobertas:
- Modelos e validações
- CRUD de Projetos
- CRUD de Casos de Teste
- Registro de Execuções
- CRUD de Bugs
- Relacionamentos e exclusões em cascata
- Indicadores do dashboard

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
│   ├── models.py             (Project, TestCase, TestExecution, Bug)
│   ├── commands.py           (comando flask init-db)
│   ├── main/
│   │   ├── __init__.py
│   │   ├── routes.py         (dashboard com indicadores)
│   │   ├── forms.py
│   │   └── templates/
│   │       ├── base.html
│   │       ├── dashboard.html
│   │       ├── 404.html
│   │       └── 500.html
│   ├── projects/
│   │   ├── __init__.py
│   │   ├── routes.py         (CRUD de projetos)
│   │   ├── forms.py
│   │   └── templates/
│   │       └── projects/
│   │           ├── list.html
│   │           ├── create.html
│   │           ├── detail.html
│   │           ├── edit.html
│   │           └── delete.html
│   ├── testcases/
│   │   ├── __init__.py
│   │   ├── routes.py         (CRUD de casos de teste + execuções)
│   │   ├── forms.py
│   │   └── templates/
│   │       └── testcases/
│   │           ├── list.html
│   │           ├── create.html
│   │           ├── detail.html
│   │           ├── edit.html
│   │           └── delete.html
│   └── bugs/
│       ├── __init__.py
│       ├── routes.py         (CRUD de bugs)
│       ├── forms.py
│       └── templates/
│           └── bugs/
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
    ├── test_dashboard.py
    ├── test_testcase_model.py
    └── test_bug_model.py
```

---

## Funcionalidades Implementadas

### Dashboard
- Filtro por projeto
- Total de projetos, ativos e arquivados
- Total de casos de teste
- Testes aprovados, reprovados, bloqueados e não executados
- Total de bugs, abertos, em andamento e resolvidos
- Bugs por severidade (baixa, média, alta, crítica)
- Ações rápidas para criar projetos, casos de teste e bugs

### CRUD de Projetos
| Operação | Rota | Método |
|----------|------|--------|
| Listar | `/projetos/` | GET |
| Criar | `/projetos/novo` | GET, POST |
| Detalhes | `/projetos/<id>` | GET |
| Editar | `/projetos/<id>/editar` | GET, POST |
| Excluir | `/projetos/<id>/excluir` | GET (confirma), POST (executa) |

### Casos de Teste
| Operação | Rota | Método |
|----------|------|--------|
| Listar | `/testcases/` | GET |
| Criar | `/testcases/novo` | GET, POST |
| Detalhes | `/testcases/<id>` | GET |
| Editar | `/testcases/<id>/editar` | GET, POST |
| Excluir | `/testcases/<id>/excluir` | GET (confirma), POST (executa) |
| Executar | `/testcases/<id>/executar` | POST |

**Campos:** Título, Projeto (obrigatório), Passos de Execução, Resultado Esperado
**Execuções:** Status (aprovado/reprovado/bloqueado), Observações, Histórico ordenado por data

### Bugs
| Operação | Rota | Método |
|----------|------|--------|
| Listar | `/bugs/` | GET |
| Criar | `/bugs/novo` | GET, POST |
| Detalhes | `/bugs/<id>` | GET |
| Editar | `/bugs/<id>/editar` | GET, POST |
| Excluir | `/bugs/<id>/excluir` | GET (confirma), POST (executa) |

**Campos:** Título, Descrição, Projeto (obrigatório), Severidade (baixa/média/alta/crítica), Status (aberto/em andamento/resolvido) |

### Validações
- **Projetos**: Nome obrigatório, máx. 120 chars, único, espaços removidos. Status: Ativo/Arquivado
- **Casos de Teste**: Título obrigatório, máx 200 chars. Passos e resultado esperado obrigatórios. Projeto obrigatório
- **Execuções**: Status obrigatório (aprovado/reprovado/bloqueado). Caso de teste obrigatório
- **Bugs**: Título obrigatório, máx 200 chars. Descrição obrigatória. Projeto obrigatório. Severidade e status obrigatórios
- **CSRF**: proteção em todos os formulários
- **404**: retornado para recursos inexistentes

### Interface
- Tema escuro (dark mode) consistente
- Layout responsivo com Bootstrap 5
- Navegação: Dashboard, Projetos, Casos de Teste, Bugs
- Mensagens de sucesso/erro em português
- Estados vazios informativos
- Paginação na listagem (10 por página)
- Filtro por projeto em todas as listagens
- Badges coloridos por status/severidade

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