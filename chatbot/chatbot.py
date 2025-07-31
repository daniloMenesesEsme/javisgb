import os
import re
import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate

# Cache para armazenar a cadeia de QA
qa_chain_cache = None

def inicializar_chatbot():
    """
    Carrega o índice FAISS pré-construído e inicializa a cadeia de QA.
    Retorna True em caso de sucesso, False em caso de falha.
    """
    global qa_chain_cache
    try:
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            print("Erro: A chave de API do Google (GOOGLE_API_KEY) não foi definida.")
            return False
        genai.configure(api_key=api_key)

        # Caminho para o novo índice estruturado
        caminho_indice = os.path.join(os.path.dirname(__file__), "..", "web_app", "faiss_index_estruturado")

        if not os.path.isdir(caminho_indice):
            print("-" * 80)
            print(f"Erro: O diretório do índice estruturado '{caminho_indice}' não foi encontrado.")
            print("Por favor, execute o script 'python web_app/criar_indice_estruturado.py' primeiro.")
            print("-" * 80)
            return False

        print("Carregando índice FAISS estruturado local...")
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        vectorstore = FAISS.load_local(caminho_indice, embeddings, allow_dangerous_deserialization=True)

        print("Criando a cadeia de QA com o Gemini e o novo prompt...")
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.3)
        
        # NOVO PROMPT_TEMPLATE: Instruindo o modelo a extrair e formatar a resposta com base na "coluna" e tópicos
        prompt_template_final = """Você é um assistente de atendimento especializado em artigos do Grupo Boticário.
        Sua tarefa é fornecer respostas precisas e detalhadas com base EXCLUSIVAMENTE no contexto fornecido.
        
        **INSTRUÇÕES DE FORMATAÇÃO DA RESPOSTA:**
        1.  **Código do Artigo:** Procure no contexto pela frase "Código e descrição do artigo". Se encontrar, extraia o código numérico associado a ela. Se não encontrar, use "Não Encontrado".
        2.  **Título do Artigo:** Se encontrou o "Código e descrição do artigo", extraia a descrição (título) associada a ele. Caso contrário, use "Não Encontrado".
        3.  **Tópico/Procedimento:** Tente identificar um tópico ou subtópico relevante no contexto que se relacione diretamente com a pergunta. Se não for possível identificar um tópico claro, use "Informações Gerais" ou "Página: [Número da Página]" (o número da página pode ser obtido do metadata do documento, se disponível).
        4.  **Formato da Resposta:** Sua resposta DEVE seguir o formato EXATO abaixo, utilizando Markdown para organização:

            ```markdown
            ## Informações do Artigo
            **Código do Artigo:** [Código extraído ou "Não Encontrado"]
            **Título do Artigo:** [Título extraído ou "Não Encontrado"]
            **Tópico:** [Tópico inferido ou "Informações Gerais" ou "Página: X"]

            ## Descrição do Procedimento
            [Sua resposta detalhada e passo a passo, baseada no contexto, explicando o procedimento que o analista deve realizar para resolver o problema. Utilize listas numeradas ou com marcadores (bullet points) para procedimentos, se aplicável.]
            ```

        Se a informação exata para a pergunta não estiver no contexto fornecido, diga claramente "Não encontrei a informação específica para esta pergunta nos documentos disponíveis."
        Responda sempre de forma clara, objetiva e EXCLUSIVAMENTE em português do Brasil.

        Contexto: {context}
        Pergunta: {question}
        
        Resposta detalhada em português do Brasil:"""

        prompt = PromptTemplate(template=prompt_template_final, input_variables=["context", "question"])

        qa_chain_cache = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt}
        )
        print("Chatbot inicializado com sucesso a partir do índice local!")
        return True

    except Exception as e:
        print(f"Ocorreu um erro durante a inicialização do chatbot: {e}")
        return False

def get_chatbot_answer(question):
    """
    Recebe uma pergunta e retorna a resposta do chatbot.
    A formatação da fonte é feita diretamente pelo modelo via prompt.
    Retorna uma tupla (success, result).
    """
    if qa_chain_cache is None:
        return False, "O chatbot não foi inicializado corretamente."
    
    try:
        print(f"Recebendo pergunta: {question}")
        resposta = qa_chain_cache.invoke({"query": question})
        
        final_response_text = resposta["result"]

        print(f"Resposta gerada: {final_response_text}")
        return True, final_response_text
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