# Variáveis de Ambiente - Frontend Flutter

Este documento descreve as variáveis de ambiente disponíveis para configurar o frontend Flutter.

## 📋 Variáveis Disponíveis

### API Configuration

#### `API_BASE_URL`
- **Descrição**: URL base para as chamadas da API
- **Padrão**: `/api/v1/database`
- **Exemplos**:
  - `/api/v1/database` (proxy nginx)
  - `http://localhost:8000/api/v1/database` (desenvolvimento local)

### App Configuration

#### `APP_TITLE`
- **Descrição**: Título da aplicação exibido no navegador
- **Padrão**: `Database Sync`
- **Exemplo**: `Meu Sistema de Sincronização`

#### `IS_DEVELOPMENT`
- **Descrição**: Habilita modo de desenvolvimento
- **Padrão**: `false`
- **Valores**: `true` ou `false`

#### `ENABLE_DEBUG`
- **Descrição**: Habilita logs de debug
- **Padrão**: `false`
- **Valores**: `true` ou `false`

### Server Configuration

#### `FRONTEND_PORT`
- **Descrição**: Porta onde o frontend será acessível
- **Padrão**: `3000`
- **Exemplo**: `8080`

## 🚀 Como Usar

### 1. Docker Compose

Configure as variáveis no arquivo `.env` na raiz do projeto:

```bash
# .env
API_BASE_URL=/api/v1/database
APP_TITLE=Database Sync
IS_DEVELOPMENT=false
ENABLE_DEBUG=false
FRONTEND_PORT=3000
```

### 2. Build Local

Para desenvolvimento local, você pode definir as variáveis antes do build:

```bash
# Desenvolvimento local
export API_BASE_URL=http://localhost:8000/api/v1/database
export APP_TITLE="Database Sync - Dev"
export IS_DEVELOPMENT=true
export ENABLE_DEBUG=true

# Executar build
./build.sh
```

### 3. Docker Build Direto

```bash
docker build \
  --build-arg API_BASE_URL=/api/v1/database \
  --build-arg APP_TITLE="Database Sync" \
  --build-arg IS_DEVELOPMENT=false \
  --build-arg ENABLE_DEBUG=false \
  -t database-sync-frontend .
```

## 🔧 Configurações Recomendadas

### Desenvolvimento Local
```bash
API_BASE_URL=http://localhost:8000/api/v1/database
APP_TITLE=Database Sync - Dev
IS_DEVELOPMENT=true
ENABLE_DEBUG=true
FRONTEND_PORT=3000
```

### Produção com Docker
```bash
API_BASE_URL=/api/v1/database
APP_TITLE=Database Sync
IS_DEVELOPMENT=false
ENABLE_DEBUG=false
FRONTEND_PORT=3000
```

### Produção com Backend Externo
```bash
API_BASE_URL=https://api.meusite.com/api/v1/database
APP_TITLE=Database Sync
IS_DEVELOPMENT=false
ENABLE_DEBUG=false
FRONTEND_PORT=3000
```

## 📝 Notas Importantes

1. **API_BASE_URL**: 
   - Use `/api/v1/database` quando usar o proxy nginx do Docker
   - Use URL completa quando acessar backend externo

2. **Build Time**: As variáveis são incorporadas no build, não em runtime
   - Para mudar configurações, é necessário rebuild

3. **Segurança**: 
   - `IS_DEVELOPMENT=true` pode expor informações sensíveis
   - `ENABLE_DEBUG=true` pode gerar logs verbosos

4. **Cache**: O navegador pode cachear a aplicação
   - Use Ctrl+F5 para forçar reload após mudanças 