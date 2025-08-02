import os
import pandas as pd
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from dotenv import load_dotenv
import google.generativeai as genai

def criar_e_salvar_indice_estruturado():
    """
    Lê o arquivo CSV limpo, cria documentos com metadados, gera embeddings 
    e salva um novo índice FAISS estruturado.
    """
    load_dotenv()
    print("--- Iniciando a criação do novo índice FAISS estruturado ---")

    # 1. Configurar a API Key do Google
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("Erro: A chave de API do Google (GOOGLE_API_KEY) não foi definida.")
        return
    genai.configure(api_key=api_key)

    # 2. Definir os caminhos
    project_root = os.path.abspath(os.path.dirname(__file__))
    caminho_csv = os.path.join(project_root, 'base_conhecimento_precisao.csv')
    caminho_indice_novo = os.path.join(project_root, 'faiss_index_estruturado')

    if not os.path.exists(caminho_csv):
        print(f"Erro: Arquivo de conhecimento limpo não encontrado em '{caminho_csv}'.")
        print("Por favor, execute o script 'scripts/limpar_dados.py' primeiro.")
        return

    # 3. Carregar os dados do CSV
    print(f"Carregando dados do arquivo: {caminho_csv}")
    df = pd.read_csv(caminho_csv)
    df.dropna(subset=['texto_para_busca'], inplace=True) # Garante que a coluna de busca não seja vazia

    # 4. Criar documentos LangChain com metadados
    print("Criando documentos estruturados para o LangChain...")
    documentos = []
    for _, row in df.iterrows():
        # O conteúdo da página é o texto que será usado para a busca
        page_content = str(row['texto_para_busca'])
        
        # Os metadados são as informações que queremos recuperar junto com o resultado
        metadata = {
            'codigo_artigo': str(row.get('codigo_artigo', 'N/A')),
            'titulo_artigo': str(row.get('titulo_artigo', 'N/A')),
            'article_title': str(row.get('titulo_artigo', 'N/A')),  # Compatibilidade com chatbot.py
            'source_file': f"Artigo_{row.get('codigo_artigo', 'desconhecido')}.pdf"  # Arquivo fonte simulado
            # Adicione aqui outros campos do CSV que queira manter como metadados
        }
        documento = Document(page_content=page_content, metadata=metadata)
        documentos.append(documento)

    if not documentos:
        print("Nenhum documento válido foi criado a partir do arquivo CSV. Abortando.")
        return

    print(f"{len(documentos)} documentos foram criados com sucesso.")

    # 5. Gerar Embeddings e criar o índice FAISS
    try:
        print("Inicializando o modelo de embeddings do Google...")
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        
        print("Gerando embeddings e construindo o índice FAISS... (Isso pode levar alguns minutos)")
        vectorstore = FAISS.from_documents(documentos, embeddings)
        
        print(f"Salvando o novo índice em: {caminho_indice_novo}")
        vectorstore.save_local(caminho_indice_novo)
        
        print("-" * 50)
        print("SUCESSO! O novo índice FAISS estruturado foi criado e salvo.")
        print("-" * 50)

    except Exception as e:
        print(f"Ocorreu um erro crítico durante a criação do índice: {e}")

if __name__ == '__main__':
    criar_e_salvar_indice_estruturado()
