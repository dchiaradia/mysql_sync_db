# Database Sync

Um sistema completo para sincronização de dados entre bancos de dados MySQL, desenvolvido com FastAPI (backend) e Flutter Web (frontend).

## 📋 Descrição

O Database Sync é uma aplicação que permite sincronizar tabelas entre dois bancos de dados MySQL diferentes. 
O sistema oferece uma interface web intuitiva para visualizar, comparar e sincronizar dados entre bancos de origem e destino.

### 🎯 Funcionalidades

- **Comparação de Tabelas**: Visualiza diferenças entre bancos de origem e destino
- **Sincronização de Dados**: Sincroniza dados entre tabelas correspondentes
- **Interface Web Responsiva**: Interface moderna desenvolvida com Flutter Web
- **API RESTful**: Backend robusto com FastAPI
- **Suporte a Múltiplos Bancos**: Arquitetura preparada para diferentes tipos de banco de dados
- **Docker Compose**: Deploy simplificado com containers

## 🏗️ Arquitetura

```
database_sync/
├── backend/                 # API FastAPI
│   ├── app/
│   │   ├── core/           # Configurações e adaptadores de banco
│   │   ├── models/         # Modelos de dados
│   │   ├── routes/         # Endpoints da API
│   │   └── services/       # Lógica de negócio
│   ├── main.py             # Ponto de entrada da aplicação
│   └── requirements.txt    # Dependências Python
├── frontend/               # Interface Flutter Web
│   ├── lib/
│   │   ├── screens/        # Telas da aplicação
│   │   ├── services/       # Serviços de API
│   │   ├── models/         # Modelos de dados
│   │   └── config/         # Configurações
│   └── pubspec.yaml        # Dependências Flutter
├── docker-compose.yml      # Orquestração de containers
├── init_source.sql         # Script de inicialização do banco origem
├── init_destination.sql    # Script de inicialização do banco destino
└── env.example             # Exemplo de variáveis de ambiente
```

## 🚀 Como Executar

### Pré-requisitos

- Docker e Docker Compose instalados
- Git

### 1. Clone o repositório

```bash
git clone <url-do-repositorio>
cd database_sync
```

### 2. Configure as variáveis de ambiente

```bash
cp env.example .env
```

Edite o arquivo `.env` conforme suas necessidades:

```env
# Configurações dos bancos de dados
DATABASE_TYPE=mysql
SOURCE_USER=root
SOURCE_PASSWORD=password
SOURCE_DB=source_db
SOURCE_HOST=mysql_source
SOURCE_PORT=3306

DESTINATION_USER=root
DESTINATION_PASSWORD=password
DESTINATION_DB=destination_db
DESTINATION_HOST=mysql_destination
DESTINATION_PORT=3306

# Configurações do frontend
FRONTEND_PORT=3000
API_BASE_URL=/api/v1/database
APP_TITLE=Database Sync
```

### 3. Execute com Docker Compose

```bash
docker-compose up -d
```

### 4. Acesse a aplicação

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Documentação da API**: http://localhost:8000/docs

## 📊 Bancos de Dados

O projeto inclui dois bancos MySQL com dados de exemplo:

### Banco de Origem (source_db)
- Tabelas: `users`, `products`, `orders`
- Dados de exemplo incluídos

### Banco de Destino (destination_db)
- Tabelas: `users`, `products`, `categories`
- Dados de exemplo (parcial)

## 🔧 Desenvolvimento

### Backend (FastAPI)

```bash
cd backend
pip install -r requirements.txt
python main.py
```

### Frontend (Flutter)

```bash
cd frontend
flutter pub get
flutter run -d chrome
```

## 📚 Documentação da API

A API oferece os seguintes endpoints:

- `GET /api/v1/database/health` - Health check
- `GET /api/v1/database/tables` - Lista tabelas disponíveis
- `GET /api/v1/database/compare/{table_name}` - Compara dados de uma tabela
- `POST /api/v1/database/sync/{table_name}` - Sincroniza dados de uma tabela

Acesse http://localhost:8000/docs para documentação interativa.

## 🐳 Containers

O projeto utiliza os seguintes containers:

- **mysql_source**: Banco de dados de origem (porta 3306)
- **mysql_destination**: Banco de dados de destino (porta 3307)
- **backend**: API FastAPI (porta 8000)
- **frontend**: Interface Flutter Web (porta 3000)

## 🔍 Monitoramento

Para verificar o status dos containers:

```bash
docker-compose ps
```

Para ver logs:

```bash
docker-compose logs -f [service_name]
```

## 🛠️ Tecnologias Utilizadas

- **Backend**: FastAPI, SQLAlchemy, PyMySQL
- **Frontend**: Flutter Web, HTTP, JSON
- **Banco de Dados**: MySQL 8.0
- **Containerização**: Docker, Docker Compose
- **Proxy**: Nginx (configurado no frontend)

## 📝 Licença

Este projeto é de uso educacional e de demonstração.

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📞 Suporte

Para dúvidas ou problemas, abra uma issue no repositório. 