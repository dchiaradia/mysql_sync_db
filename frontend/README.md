# Database Sync - Frontend

Interface web da aplicação Database Sync desenvolvida com Flutter Web, oferecendo uma experiência moderna e responsiva para sincronização de dados entre bancos MySQL.

## 📋 Descrição

O frontend é uma aplicação Flutter Web que fornece uma interface intuitiva para visualizar, comparar e sincronizar dados entre bancos de dados. A aplicação se comunica com o backend através de uma API RESTful.

## 🏗️ Arquitetura

```
frontend/
├── lib/
│   ├── config/             # Configurações da aplicação
│   │   └── env_config.dart # Configurações de ambiente
│   ├── models/             # Modelos de dados
│   ├── screens/            # Telas da aplicação
│   │   └── database_sync_screen.dart # Tela principal
│   ├── services/           # Serviços de API
│   ├── UILib/              # Componentes de UI reutilizáveis
│   └── main.dart           # Ponto de entrada da aplicação
├── web/                    # Configurações web
├── pubspec.yaml            # Dependências Flutter
├── Dockerfile              # Configuração do container
├── nginx.conf              # Configuração do proxy Nginx
└── build.sh               # Script de build
```

## 🚀 Como Executar

### Pré-requisitos

- Flutter SDK 3.8.1+
- Dart SDK
- Chrome ou navegador compatível

### 1. Instale as dependências

```bash
flutter pub get
```

### 2. Configure as variáveis de ambiente

As configurações são definidas através de variáveis de ambiente no Docker ou podem ser configuradas diretamente no código:

```dart
// lib/config/env_config.dart
class EnvConfig {
  static const String apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: '/api/v1/database'
  );
  static const String appTitle = String.fromEnvironment(
    'APP_TITLE',
    defaultValue: 'Database Sync'
  );
}
```

### 3. Execute em modo desenvolvimento

```bash
flutter run -d chrome
```

### 4. Build para produção

```bash
flutter build web
```

## 🎨 Interface do Usuário

### Funcionalidades Principais

- **Visualização de Tabelas**: Lista todas as tabelas disponíveis nos bancos
- **Comparação de Dados**: Mostra diferenças entre bancos de origem e destino
- **Sincronização**: Executa operações de sincronização de dados
- **Interface Responsiva**: Adapta-se a diferentes tamanhos de tela
- **Feedback Visual**: Indicadores de loading e status das operações

### Componentes de UI

- **Loading Indicators**: Usando `flutter_spinkit`
- **Data Tables**: Exibição tabular de dados
- **Buttons**: Ações de sincronização e navegação
- **Cards**: Organização de informações
- **Alerts**: Feedback de sucesso e erro

## 🛠️ Tecnologias Utilizadas

- **Flutter Web**: Framework para desenvolvimento web
- **HTTP**: Cliente HTTP para comunicação com API
- **JSON**: Serialização/deserialização de dados
- **Material Design**: Design system do Flutter
- **Nginx**: Proxy reverso para produção

## 📦 Dependências

### Principais
- `flutter`: SDK Flutter
- `http: ^1.1.0`: Cliente HTTP
- `json_annotation: ^4.8.1`: Anotações JSON
- `flutter_spinkit: ^5.2.0`: Indicadores de loading

### Desenvolvimento
- `flutter_lints: ^5.0.0`: Linting
- `json_serializable: ^6.7.1`: Geração de código JSON
- `build_runner: ^2.4.7`: Geração de código

## 🔧 Desenvolvimento

### Estrutura de Código

#### Configurações (`lib/config/`)
- `env_config.dart`: Configurações de ambiente e constantes

#### Modelos (`lib/models/`)
- Classes de dados para representar entidades da API
- Anotações JSON para serialização

#### Telas (`lib/screens/`)
- `database_sync_screen.dart`: Tela principal da aplicação
- Widgets responsáveis pela interface do usuário

#### Serviços (`lib/services/`)
- Comunicação com a API backend
- Tratamento de requisições HTTP

#### UI Library (`lib/UILib/`)
- Componentes reutilizáveis
- Widgets customizados

### Padrões de Código

- **State Management**: Gerenciamento de estado local
- **Async/Await**: Operações assíncronas
- **Error Handling**: Tratamento de erros de API
- **Responsive Design**: Interface adaptativa

## 🐳 Docker

### Build da imagem

```bash
docker build -t database-sync-frontend .
```

### Executar container

```bash
docker run -p 3000:80 database-sync-frontend
```

### Build com variáveis de ambiente

```bash
docker build \
  --build-arg API_BASE_URL=/api/v1/database \
  --build-arg APP_TITLE="Database Sync" \
  --build-arg IS_DEVELOPMENT=false \
  -t database-sync-frontend .
```

## 🌐 Configuração Web

### Nginx

O projeto inclui uma configuração Nginx para produção:

```nginx
server {
    listen 80;
    server_name localhost;
    
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }
    
    location /api/ {
        proxy_pass http://backend:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Build Script

O script `build.sh` automatiza o processo de build:

```bash
#!/bin/bash
flutter build web --release
```

## 📱 Responsividade

A aplicação é responsiva e funciona em:

- **Desktop**: Interface completa com todas as funcionalidades
- **Tablet**: Layout adaptado para telas médias
- **Mobile**: Interface otimizada para dispositivos móveis

## 🎯 Funcionalidades da Interface

### 1. Listagem de Tabelas
- Exibe todas as tabelas disponíveis nos bancos
- Indica quais tabelas existem em ambos os bancos
- Mostra contagem de registros por tabela

### 2. Comparação de Dados
- Compara dados entre bancos de origem e destino
- Destaca diferenças encontradas
- Exibe estatísticas de comparação

### 3. Sincronização
- Executa operações de sincronização
- Mostra progresso em tempo real
- Exibe resultados da operação

### 4. Feedback Visual
- Loading indicators durante operações
- Mensagens de sucesso e erro
- Status das operações

## 🔍 Debugging

### Modo Debug

```bash
flutter run -d chrome --debug
```

### Logs do Container

```bash
docker-compose logs -f frontend
```

### DevTools

Acesse as DevTools do Flutter para debugging:
- Chrome DevTools
- Flutter Inspector

## 🧪 Testes

### Testes de Widget

```bash
flutter test
```

### Testes de Integração

```bash
flutter drive --target=test_driver/app.dart
```

## 📝 Configurações Avançadas

### Variáveis de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `API_BASE_URL` | URL base da API | `/api/v1/database` |
| `APP_TITLE` | Título da aplicação | `Database Sync` |
| `IS_DEVELOPMENT` | Modo desenvolvimento | `false` |
| `ENABLE_DEBUG` | Habilitar debug | `false` |

### Build Arguments

```bash
flutter build web \
  --dart-define=API_BASE_URL=/api/v1/database \
  --dart-define=APP_TITLE="Database Sync" \
  --dart-define=IS_DEVELOPMENT=false
```

## 🔒 Segurança

- Comunicação segura com backend via HTTPS (em produção)
- Validação de entrada de dados
- Sanitização de dados exibidos
- CORS configurado adequadamente

## 📞 Suporte

Para dúvidas sobre o frontend, consulte:
- Documentação do Flutter: https://flutter.dev/docs
- Issues do projeto
- Flutter Web: https://flutter.dev/web

## 🚀 Deploy

### Produção

```bash
# Build da aplicação
flutter build web --release

# Deploy com Docker
docker-compose up -d frontend
```

### Desenvolvimento

```bash
# Executar em modo hot reload
flutter run -d chrome --hot
``` 