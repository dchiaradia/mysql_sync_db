#!/bin/bash

echo "Iniciando aplicação..."
exec uvicorn main:app --host 0.0.0.0 --port 8000 