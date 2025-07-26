import os
import sys
import pickle
import re
import google.generativeai as genai
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

# Adiciona o diretório do projeto ao PATH para encontrar a pasta 'chatbot'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def criar_e_salvar_indice():
    """
    Processa os PDFs e salva o índice FAISS e os documentos em disco.
    """
    try:
        # 1. Configurar a API Key
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            print("Erro: A variável de ambiente GOOGLE_API_KEY não foi definida.")
            return
        genai.configure(api_key=api_key)

        # 2. Definir caminhos
        script_dir = os.path.dirname(__file__)
        caminho_documentos = os.path.join(script_dir, "..", "chatbot", "documentos")
        caminho_indice = os.path.join(script_dir, "faiss_index")

        if not os.path.isdir(caminho_documentos):
            print(f"Erro: Diretório de documentos não encontrado em '{caminho_documentos}'")
            return

        # 3. Carregar e Processar os PDFs
        print(f"Carregando documentos de '{caminho_documentos}'...")
        loader = PyPDFDirectoryLoader(caminho_documentos)
        documentos = loader.load()

        if not documentos:
            print("Nenhum documento PDF encontrado para indexar.")
            return

        print("Dividindo documentos em pedaços e adicionando metadados...")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        textos = text_splitter.split_documents(documentos)

        # Adicionar metadados personalizados aos documentos
        for doc in textos:
            source_name = os.path.basename(doc.metadata.get('source', ''))
            
            # Extrair o código do artigo
            article_code_match = re.search(r'Artigo (\d+)', source_name)
            doc.metadata['article_code'] = article_code_match.group(1) if article_code_match else 'Não Informado'
            
            # Extrair o título do artigo (removendo a parte do artigo e a extensão .pdf)
            title_match = re.match(r'(.*?)\s*Artigo\s*\d+\.pdf', source_name)
            doc.metadata['article_title'] = title_match.group(1).strip() if title_match else source_name.replace('.pdf', '').strip()

        # 4. Gerar Embeddings e Criar o Índice FAISS
        print("Gerando embeddings e criando o índice FAISS...")
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        vectorstore = FAISS.from_documents(textos, embeddings)

        # 5. Salvar o Índice e os Documentos
        os.makedirs(caminho_indice, exist_ok=True)
        vectorstore.save_local(caminho_indice)
        
        print("-" * 80)
        print(f"Índice FAISS e documentos foram salvos com sucesso em: '{caminho_indice}'")
        print("Execute 'python web_app/app.py' agora para iniciar o servidor rápido.")
        print("-" * 80)

    except Exception as e:
        print(f"Ocorreu um erro ao criar o índice: {e}")

if __name__ == "__main__":
    criar_e_salvar_indice()