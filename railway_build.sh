#!/bin/bash

# Para a execução se qualquer comando falhar
set -e

echo "BUILD_START: Instalando dependências..."
pip install -r requirements.txt

echo "BUILD_STEP: Processando PDFs para criar base_conhecimento.csv..."
python scripts/processar_documentos_pypdf.py

echo "BUILD_STEP: Limpando base_conhecimento.csv..."
python scripts/limpar_dados.py

echo "BUILD_STEP: Criando o índice FAISS estruturado..."
python web_app/criar_indice_estruturado.py

echo "BUILD_COMPLETE: Todos os artefatos foram construídos com sucesso."
