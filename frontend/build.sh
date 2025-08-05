#!/bin/bash

# Script de build para Flutter Web
echo "🚀 Iniciando build do Flutter Web..."

# Verificar se o Flutter está instalado
if ! command -v flutter &> /dev/null; then
    echo "❌ Flutter não encontrado. Instale o Flutter primeiro."
    exit 1
fi

# Verificar se estamos na pasta correta
if [ ! -f "pubspec.yaml" ]; then
    echo "❌ pubspec.yaml não encontrado. Execute este script na pasta frontend."
    exit 1
fi

# Limpar builds anteriores
echo "🧹 Limpando builds anteriores..."
flutter clean

# Obter dependências
echo "📦 Obtendo dependências..."
flutter pub get

# Verificar se o web está habilitado
echo "🌐 Verificando configuração web..."
flutter config --enable-web

# Build para web
echo "🔨 Fazendo build para web..."

# Variáveis de ambiente com valores padrão
API_BASE_URL=${API_BASE_URL:-/api/v1/database}
APP_TITLE=${APP_TITLE:-Database Sync}
IS_DEVELOPMENT=${IS_DEVELOPMENT:-false}
ENABLE_DEBUG=${ENABLE_DEBUG:-false}

flutter build web --release \
  --dart-define=API_BASE_URL=$API_BASE_URL \
  --dart-define=APP_TITLE="$APP_TITLE" \
  --dart-define=IS_DEVELOPMENT=$IS_DEVELOPMENT \
  --dart-define=ENABLE_DEBUG=$ENABLE_DEBUG

# Verificar se o build foi bem-sucedido
if [ -d "build/web" ]; then
    echo "✅ Build concluído com sucesso!"
    echo "📁 Arquivos gerados em: build/web/"
    echo "🌐 Para testar localmente: flutter run -d web-server --web-port 3000"
else
    echo "❌ Erro no build. Verifique os logs acima."
    exit 1
fi 