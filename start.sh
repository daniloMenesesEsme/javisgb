#!/bin/bash

echo "🔧 Instalando dependências..."
pip install -r requirements.txt

echo "🚀 Iniciando aplicação..."
gunicorn web_app.app:app --bind 0.0.0.0:$PORT