import os
import google.generativeai as genai
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate

# Cache para armazenar a cadeia de QA e evitar reprocessamento
qa_chain_cache = None

def inicializar_chatbot():
    """
    Carrega os documentos, cria os embeddings, o vectorstore e a cadeia de QA.
    Retorna True em caso de sucesso, False em caso de falha.
    """
    global qa_chain_cache
    try:
        if not os.environ.get("GOOGLE_API_KEY"):
            print("Erro: A chave de API do Google (GOOGLE_API_KEY) não foi definida.")
            return False

        genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

        script_dir = os.path.dirname(__file__)
        caminho_documentos = os.path.join(script_dir, "documentos")

        if not os.path.isdir(caminho_documentos):
            print(f"Erro: A pasta de documentos '{caminho_documentos}' não foi encontrada.")
            return False

        print("Carregando documentos PDF...")
        loader = PyPDFDirectoryLoader(caminho_documentos)
        documentos = loader.load()

        if not documentos:
            print("Nenhum documento PDF encontrado.")
            return False

        print("Dividindo documentos em pedaços...")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        textos = text_splitter.split_documents(documentos)

        print("Criando embeddings e vectorstore com o Gemini...")
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        vectorstore = FAISS.from_documents(textos, embeddings)

        print("Criando a cadeia de QA com o Gemini...")
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.3)
        
        prompt_template = """Você é um assistente de atendimento especializado.
        Sua tarefa é fornecer respostas precisas com base EXCLUSIVAMENTE no contexto fornecido.
        Se a informação não estiver no contexto, diga: 'Não encontrei a informação nos documentos.'
        Responda sempre em português do Brasil.

        Contexto: {context}

        Pergunta: {question}
        Resposta:"""

        prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

        qa_chain_cache = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt}
        )
        print("Chatbot inicializado com sucesso!")
        return True

    except Exception as e:
        print(f"Ocorreu um erro durante a inicialização do chatbot: {e}")
        return False

def get_chatbot_answer(question):
    """
    Recebe uma pergunta e retorna a resposta do chatbot.
    Retorna uma tupla (success, result).
    """
    if qa_chain_cache is None:
        return False, "O chatbot não foi inicializado corretamente."
    
    try:
        print(f"Recebendo pergunta: {question}")
        resposta = qa_chain_cache.invoke({"query": question})
        print(f"Resposta gerada: {resposta['result']}")
        return True, resposta["result"]
    except Exception as e:
        error_message = f"Ocorreu um erro ao processar a pergunta: {e}"
        print(error_message)
        return False, error_message

# O bloco abaixo serve para testar o chatbot de forma independente
if __name__ == '__main__':
    if inicializar_chatbot():
        print("\n--- Chatbot de Conhecimento (Teste Local) ---")
        print("Digite 'sair' para terminar.")
        while True:
            pergunta = input("\nSua pergunta: ")
            if pergunta.lower() == 'sair':
                break
            
            success, resposta = get_chatbot_answer(pergunta)
            if success:
                print("\nResposta:")
                print(resposta)
            else:
                print(f"Erro: {resposta}")