import os
import sys
import re
import google.generativeai as genai
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Adiciona o diretório do projeto ao PATH para importações corretas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def extrair_metadados_do_texto(texto):
    """
    Extrai código e título do artigo do texto completo do documento usando regex.
    """
    codigo_artigo = "Não Informado"
    titulo_artigo = "Não Informado"

    # Tenta encontrar o padrão "Código e descrição do artigo 12345 - Título do Artigo"
    # Esta regex é flexível com "Código" e "descrição" e espaços.
    padrao_principal = re.search(
        r"c[oó]digo e descriç[ãa]o do artigo\s*(\d+)\s*-\s*(.+)",
        texto,
        re.IGNORECASE
    )
    if padrao_principal:
        codigo_artigo = padrao_principal.group(1).strip()
        titulo_artigo = padrao_principal.group(2).strip()
        return codigo_artigo, titulo_artigo

    # Fallback: Se o padrão principal não for encontrado, tenta padrões mais simples
    padrao_codigo = re.search(r"artigo\s*nº\s*(\d+)", texto, re.IGNORECASE)
    if padrao_codigo:
        codigo_artigo = padrao_codigo.group(1).strip()

    # Tenta encontrar um título após a palavra "Título:"
    padrao_titulo = re.search(r"t[íi]tulo:\s*(.+)", texto, re.IGNORECASE)
    if padrao_titulo:
        titulo_artigo = padrao_titulo.group(1).strip()

    return codigo_artigo, titulo_artigo

def criar_e_salvar_indice():
    """
    Processa os PDFs, extrai metadados do conteúdo e salva o índice FAISS.
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
        # Corrigido: Salvar no diretório que o chatbot espera
        caminho_indice = os.path.join(script_dir, "faiss_index_estruturado")

        if not os.path.isdir(caminho_documentos):
            print(f"Erro: Diretório de documentos não encontrado em '{caminho_documentos}'")
            return

        # 3. Carregar os PDFs
        print(f"Carregando documentos de '{caminho_documentos}'...")
        loader = PyPDFDirectoryLoader(caminho_documentos)
        documentos = loader.load()

        if not documentos:
            print("Nenhum documento PDF encontrado para indexar.")
            return

        print("Processando documentos, extraindo metadados e dividindo em pedaços...")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        todos_os_chunks = []

        for doc in documentos:
            # Extrai metadados do CONTEÚDO do documento inteiro
            codigo_artigo, titulo_artigo = extrair_metadados_do_texto(doc.page_content)
            source_name = os.path.basename(doc.metadata.get('source', ''))

            # Se o título não for encontrado no texto, usa o nome do arquivo como fallback
            if titulo_artigo == "Não Informado":
                # Remove a extensão e possíveis padrões como "Artigo 123" do nome do arquivo
                titulo_artigo = re.sub(r'artigo\s*\d+', '', source_name, flags=re.IGNORECASE).replace('.pdf', '').strip()

            print(f"  - Processando: {source_name} | Código: {codigo_artigo} | Título: {titulo_artigo}")

            # Divide o documento em chunks
            chunks = text_splitter.split_documents([doc])

            # Adiciona os metadados extraídos a cada chunk
            for chunk in chunks:
                chunk.metadata['article_code'] = codigo_artigo
                chunk.metadata['article_title'] = titulo_artigo
                # Mantém o nome do arquivo original para referência
                chunk.metadata['source_file'] = source_name

            todos_os_chunks.extend(chunks)

        # 4. Gerar Embeddings e Criar o Índice FAISS
        print("\nGerando embeddings e criando o índice FAISS...")
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        vectorstore = FAISS.from_documents(todos_os_chunks, embeddings)

        # 5. Salvar o Índice
        os.makedirs(caminho_indice, exist_ok=True)
        vectorstore.save_local(caminho_indice)

        print("-" * 80)
        print(f"Índice FAISS estruturado foi salvo com sucesso em: '{caminho_indice}'")
        print("Execute 'python web_app/app.py' agora para iniciar o servidor.")
        print("-" * 80)

    except Exception as e:
        print(f"Ocorreu um erro ao criar o índice: {e}")

if __name__ == "__main__":
    criar_e_salvar_indice()
