import os
import re
import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser
import json # Adicionado: Importa o módulo json

# Cache para armazenar a cadeia de QA
qa_chain_cache = None

def format_docs(docs):
    """Função auxiliar para formatar os documentos recuperados em uma única string."""
    return "\n\n".join(doc.page_content for doc in docs)

def inicializar_chatbot():
    """
    Carrega o índice FAISS e inicializa a cadeia de QA usando LCEL,
    configurada para retornar a resposta e os documentos de origem.
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
        retriever = vectorstore.as_retriever(search_kwargs={"k": 8})

        print("Criando a cadeia de QA com LCEL para retornar fontes...")
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.02, streaming=True)
        
        prompt_template = """Você é um assistente especializado em artigos técnicos do Grupo Boticário para orientação de franqueados.
        Analise TODA a pergunta do usuário e CONSOLIDE informações similares para otimizar TMA/TME.
        
        **REGRAS CRÍTICAS PARA CONSOLIDAÇÃO:**
        1. ELIMINE repetições - agrupe informações similares em uma única entrada
        2. PRIORIZE informações mais relevantes - máximo 5 causas principais
        3. CONSOLIDE procedimentos similares - evite duplicações
        4. USE hierarquia: Principais → Secundárias → Técnicas
        5. AGRUPE por categoria: Hardware, Software, Configuração, Rede
        6. SEJA CONCISO - foque no essencial para reduzir tempo de leitura
        7. UNIFIQUE terminologia - use termos consistentes
        
        **FORMATO OBRIGATÓRIO - Layout Azul Profissional:**
        
        ## 1. Código do Artigo: 
        [Extraia qualquer código numérico encontrado no contexto relacionado à pergunta]
        
        ## 2. Título do Artigo: 
        [Extraia o título mais relevante do contexto, mesmo que parcial]
        
        ## 3. Descrição das Principais Causas:
        
        **🔧 HARDWARE (Físicas)**
        **• Causa 1: [Nome Consolidado]**
           - Descrição: [Agrupe problemas físicos similares]
           - Referência: [Artigos principais]
        
        **💻 SOFTWARE (Sistema)**  
        **• Causa 2: [Nome Consolidado]**
           - Descrição: [Agrupe problemas de software similares]
           - Referência: [Artigos principais]
        
        **⚙️ CONFIGURAÇÃO (Setup)**
        **• Causa 3: [Nome Consolidado]**
           - Descrição: [Agrupe problemas de configuração similares]  
           - Referência: [Artigos principais]
        
        **🌐 CONECTIVIDADE (Rede)**
        **• Causa 4: [Nome Consolidado]**
           - Descrição: [Agrupe problemas de rede similares]
           - Referência: [Artigos principais]
        
        *(MÁXIMO 5 CAUSAS CONSOLIDADAS - Elimine duplicações e agrupe similares)*
        
        ## 4. Soluções Consolidadas por Prioridade:
        
        ### **🚀 SOLUÇÃO RÁPIDA (1º Tentar)**
        1. **Verificação Inicial:** [Consolidar verificações básicas similares]
        2. **Ação Imediata:** [Consolidar soluções rápidas similares]
        
        ### **🔧 SOLUÇÃO TÉCNICA (2º Nível)**  
        1. **Diagnóstico:** [Consolidar procedimentos de diagnóstico]
        2. **Configuração:** [Consolidar ajustes técnicos]
        3. **Teste:** [Consolidar validações]
        
        ### **📞 ESCALAÇÃO (3º Nível)**
        **Para AERO:** [Consolidar procedimentos específicos AERO]
        **Para Franquias:** [Consolidar orientações gerais]
        
        **⚡ Tempo Estimado:** [Indicar tempo para otimizar TMA]
        **📋 Categorização:** [Macro/Submotivo para classificação]
        
        ### **Informações Adicionais:**
        [Qualquer informação técnica relevante encontrada no contexto]
        
        **OTIMIZAÇÃO TMA/TME - REGRAS OBRIGATÓRIAS:**
        - MÁXIMO 5 causas consolidadas (elimine repetições)
        - MÁXIMO 6 soluções priorizadas (do mais rápido ao mais complexo)
        - AGRUPE informações similares em categorias
        - USE terminologia consistente (evite variações)
        - INDIQUE tempo estimado para cada solução
        - PRIORIZE soluções por eficácia comprovada
        - ELIMINE informações redundantes entre artigos
        
        **CONSOLIDAÇÃO INTELIGENTE:** Se encontrar 10 causas similares, agrupe em 3 categorias principais.
        **FOCO NO RESULTADO:** Analista deve ter resposta clara em máximo 2 minutos de leitura.

        **Contexto Disponível:**
        {context}

        **Pergunta do Analista:**
        {question}

        **Resposta Estruturada:**
        """
        prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

        # Define a cadeia que formata o input para o LLM
        rag_chain_from_docs = (
            RunnablePassthrough.assign(context=(lambda x: format_docs(x["source_documents"])))
            | prompt
            | llm
            | StrOutputParser()
        )

        # Define a cadeia final que recupera os documentos e depois chama a cadeia acima
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
        yield "data: " + json.dumps({"error": "O chatbot não foi inicializado corretamente." }) + "\n\n"
        return

    try:
        stream = qa_chain_cache.stream(question)
        
        # O primeiro chunk pode conter as fontes e/ou o início da resposta
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
        
        # Envia as fontes primeiro
        yield "data: " + json.dumps({"sources": unique_sources}) + "\n\n"

        # Envia o primeiro pedaço da resposta, se houver
        if 'answer' in first_chunk:
            yield "data: " + json.dumps({"token": first_chunk['answer']}) + "\n\n"

        # Continua enviando o resto da resposta em streaming
        for chunk in stream:
            if 'answer' in chunk:
                yield "data: " + json.dumps({"token": chunk['answer']}) + "\n\n"

    except Exception as e:
        error_message = f"Ocorreu um erro ao processar a pergunta: {e}"
        print(error_message)
        yield "data: " + json.dumps({"error": error_message}) + "\n\n"

# Bloco de teste atualizado
if __name__ == '__main__':
    if inicializar_chatbot():
        print("\n--- Chatbot de Conhecimento (Teste Local com Fontes) ---")
        print("Digite 'sair' para terminar.")
        while True:
            pergunta = input("\nSua pergunta: ")
            if pergunta.lower() == 'sair':
                break
            
            # A função de teste agora usa o stream
            full_response = ""
            sources_received = []
            for chunk_data in get_chatbot_answer_stream(pergunta):
                try:
                    data = json.loads(chunk_data.replace("data: ", "").strip())
                    if "token" in data:
                        full_response += data["token"]
                    if "sources" in data:
                        sources_received = data["sources"]
                except json.JSONDecodeError:
                    print(f"Erro ao decodificar JSON: {chunk_data}")
                    continue
            
            if full_response or sources_received:
                print("\n--- Resposta Gerada ---")
                print(full_response)
                print("\n--- Fontes ---")
                if sources_received:
                    for source in sources_received:
                        print(f"- Título: {source['title']}, Arquivo: {source['source_file']}")
                else:
                    print("Nenhuma fonte encontrada.")
                print("---------------------")
            else:
                print("Erro: Nenhuma resposta ou fonte recebida.")