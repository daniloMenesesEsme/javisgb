import os
import re
import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser

# Cache para armazenar a cadeia de QA
qa_chain_cache = None

def format_docs(docs):
    """Função auxiliar para formatar os documentos recuperados em uma única string."""
    return "\n\n".join(doc.page_content for doc in docs)

def inicializar_chatbot():
    """
    Carrega o índice FAISS e inicializa a cadeia de QA usando LCEL.
    """
    global qa_chain_cache
    try:
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            print("Erro: A chave de API do Google (GOOGLE_API_KEY) não foi definida.")
            return False
        genai.configure(api_key=api_key)

        caminho_indice = os.path.join(os.path.dirname(__file__), "..", "web_app", "faiss_index_estruturado")

        if not os.path.isdir(caminho_indice):
            print(f"Erro: O diretório do índice '{caminho_indice}' não foi encontrado.")
            return False

        print("Carregando índice FAISS...")
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        vectorstore = FAISS.load_local(caminho_indice, embeddings, allow_dangerous_deserialization=True)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

        print("Criando a cadeia de QA com LCEL para streaming...")
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.3, streaming=True)
        
        prompt_template = "Você é um assistente de atendimento especializado em artigos do Grupo Boticário. Sua tarefa é fornecer respostas precisas e detalhadas com base EXCLUSIVAMENTE no contexto fornecido. Se a informação exata para a pergunta não estiver no contexto, diga claramente \"Não encontrei a informação específica para esta pergunta nos documentos disponíveis.\" Responda sempre de forma clara, objetiva e EXCLUSIVAMENTE em português do Brasil. **Contexto:** {context} **Pergunta do Usuário:** {question} **Sua Resposta Estruturada:**"
        prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

        rag_chain_from_docs = (
            RunnablePassthrough.assign(context=(lambda x: format_docs(x["source_documents"])))
            | prompt
            | llm
            | StrOutputParser()
        )

        qa_chain_cache = RunnableParallel(
            {
                "source_documents": retriever,
                "question": RunnablePassthrough()
            }
        ).assign(answer=rag_chain_from_docs)
        
        print("Chatbot inicializado com sucesso para streaming!")
        return True

    except Exception as e:
        print(f"Ocorreu um erro durante a inicialização do chatbot: {e}")
        return False

def get_chatbot_answer_stream(question):
    """
    Recebe uma pergunta e retorna um gerador para a resposta e as fontes.
    """
    if qa_chain_cache is None:
        yield "data: {\"error\": \"O chatbot não foi inicializado corretamente.\"}\n\n"
        return

    try:
        stream = qa_chain_cache.stream(question)
        # Primeiro, processa as fontes
        first_chunk = next(stream)
        source_docs = first_chunk.get("source_documents", [])
        
        unique_sources = []
        seen_sources = set()
        for doc in source_docs:
            source_file = doc.metadata.get('source_file', 'Origem desconhecida')
            if source_file not in seen_sources:
                unique_sources.append({
                    "title": doc.metadata.get('article_title', 'N/A'),
                    "source_file": source_file
                })
                seen_sources.add(source_file)
        
        import json
        yield f"data: {json.dumps({'sources': unique_sources})}\n\n"

        # Envia o primeiro pedaço da resposta
        if 'answer' in first_chunk:
            yield f"data: {json.dumps({'token': first_chunk['answer']})}\n\n"

        # Envia o resto da resposta em streaming
        for chunk in stream:
            if 'answer' in chunk:
                yield f"data: {json.dumps({'token': chunk['answer']})}\n\n"

    except Exception as e:
        error_message = f"Ocorreu um erro ao processar a pergunta: {e}"
        print(error_message)
        yield f"data: {json.dumps({'error': error_message})}\n\n"