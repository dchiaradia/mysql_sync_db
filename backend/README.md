# Database Sync - Backend

Backend da aplicação Database Sync desenvolvido com FastAPI para fornecer uma API RESTful para sincronização de dados entre bancos MySQL.

## 📋 Descrição

O backend é responsável por gerenciar a comunicação com os bancos de dados, comparar estruturas e dados, e executar operações de sincronização. Utiliza FastAPI para fornecer uma API moderna e performática.

## 🏗️ Arquitetura

```
backend/
├── app/
│   ├── core/               # Configurações e adaptadores
│   │   ├── config.py       # Configurações da aplicação
│   │   ├── database.py     # Adaptadores de banco de dados
│   │   └── adapters/       # Adaptadores específicos por banco
│   ├── models/             # Modelos de dados Pydantic
│   ├── routes/             # Endpoints da API
│   ├── services/           # Lógica de negócio
│   └── __init__.py
├── main.py                 # Ponto de entrada da aplicação
├── requirements.txt        # Dependências Python
├── Dockerfile              # Configuração do container
└── start.sh               # Script de inicialização
```

## 🚀 Como Executar

### Pré-requisitos

- Python 3.8+
- pip

### 1. Instale as dependências

```bash
pip install -r requirements.txt
```

### 2. Configure as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
# Configurações do banco de dados
DATABASE_TYPE=mysql
SOURCE_USER=root
SOURCE_PASSWORD=password
SOURCE_DB=source_db
SOURCE_HOST=localhost
SOURCE_PORT=3306

DESTINATION_USER=root
DESTINATION_PASSWORD=password
DESTINATION_DB=destination_db
DESTINATION_HOST=localhost
DESTINATION_PORT=3307

# Configurações da aplicação
DEBUG=true
```

### 3. Execute a aplicação

```bash
python main.py
```

Ou usando uvicorn diretamente:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Acesse a API

- **API**: http://localhost:8000
- **Documentação**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📚 Endpoints da API

### Health Check
- `GET /health` - Verifica o status da aplicação
- `GET /` - Informações básicas da API

### Database Operations
- `GET /api/v1/database/health` - Health check específico do banco
- `GET /api/v1/database/source/tables` - Lista tabelas do banco de origem
- `GET /api/v1/database/destination/tables` - Lista tabelas do banco de destino
- `GET /api/v1/database/compare` - Compara os bancos de origem e destino
- `GET /api/v1/database/summary` - Resumo completo dos bancos
- `POST /api/v1/database/migrate/{table_name}` - Migra uma tabela específica
- `POST /api/v1/database/migrate-batch` - Migra múltiplas tabelas em lote

### Cron Jobs (Sincronização Automática)
- `POST /api/v1/cron/jobs` - Cadastra um novo cron job para sincronização automática
- `GET /api/v1/cron/jobs` - Lista todos os cron jobs cadastrados
- `DELETE /api/v1/cron/jobs/{job_id}` - Remove um cron job específico
- `GET /api/v1/cron/jobs/count` - Retorna o número total de cron jobs


## 🛠️ Tecnologias Utilizadas

- **FastAPI**: Framework web moderno e rápido
- **SQLAlchemy**: ORM para Python
- **PyMySQL**: Driver MySQL para Python
- **Pydantic**: Validação de dados e serialização
- **Uvicorn**: Servidor ASGI
- **APScheduler**: Agendamento de tarefas (cron jobs)
- **Python-dotenv**: Gerenciamento de variáveis de ambiente

## 📦 Dependências

### Principais
- `fastapi==0.104.1` - Framework web
- `uvicorn[standard]==0.24.0` - Servidor ASGI
- `sqlalchemy==2.0.23` - ORM
- `pymysql==1.1.0` - Driver MySQL
- `pydantic==2.5.0` - Validação de dados

### Desenvolvimento
- `python-dotenv==1.0.0` - Variáveis de ambiente
- `python-multipart==0.0.6` - Upload de arquivos

## 🔧 Desenvolvimento

### Estrutura de Código

#### Configurações (`app/core/`)
- `config.py`: Configurações da aplicação usando Pydantic Settings
- `database.py`: Adaptadores e conexões com bancos de dados

#### Rotas (`app/routes/`)
- Endpoints da API organizados por funcionalidade
- Validação de entrada usando Pydantic models

#### Serviços (`app/services/`)
- Lógica de negócio
- Operações de comparação e sincronização

#### Modelos (`app/models/`)
- Schemas Pydantic para validação de dados
- Modelos de resposta da API

### Padrões de Código

- **Type Hints**: Uso extensivo de type hints
- **Async/Await**: Operações assíncronas para melhor performance
- **Error Handling**: Tratamento robusto de erros
- **Logging**: Logs estruturados para debugging

## 🐳 Docker

### Build da imagem

```bash
docker build -t database-sync-backend .
```

### Executar container

```bash
docker run -p 8000:8000 --env-file .env database-sync-backend
```

## 🔍 Logs e Debugging

### Logs da aplicação

```bash
docker-compose logs -f backend
```

### Health check

```bash
curl http://localhost:8000/health
```

### Documentação interativa

Acesse http://localhost:8000/docs para testar os endpoints diretamente no navegador.

## 🧪 Testes

Para executar testes (quando implementados):

```bash
pytest
```

## 📝 Configurações Avançadas

### Variáveis de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `DATABASE_TYPE` | Tipo de banco de dados | `mysql` |
| `SOURCE_HOST` | Host do banco origem | `localhost` |
| `SOURCE_PORT` | Porta do banco origem | `3306` |
| `SOURCE_DB` | Nome do banco origem | `source_db` |
| `SOURCE_USER` | Usuário do banco origem | `root` |
| `SOURCE_PASSWORD` | Senha do banco origem | - |
| `DESTINATION_HOST` | Host do banco destino | `localhost` |
| `DESTINATION_PORT` | Porta do banco destino | `3307` |
| `DESTINATION_DB` | Nome do banco destino | `destination_db` |
| `DESTINATION_USER` | Usuário do banco destino | `root` |
| `DESTINATION_PASSWORD` | Senha do banco destino | - |
| `DEBUG` | Modo debug | `false` |

## 🔒 Segurança

- CORS configurado para permitir requisições do frontend
- Validação de entrada com Pydantic
- Tratamento seguro de conexões com banco de dados
- Logs sem informações sensíveis

## 📞 Suporte

Para dúvidas sobre o backend, consulte:
- Documentação da API: http://localhost:8000/docs
- Issues do projeto
- Documentação do FastAPI: https://fastapi.tiangolo.com/ 