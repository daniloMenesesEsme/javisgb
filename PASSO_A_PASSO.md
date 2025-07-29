# Passo a Passo do Desenvolvimento do Chatbot de Conhecimento

Este documento resume as principais etapas de desenvolvimento e refatoração do projeto, transformando um chatbot básico em um sistema de busca de conhecimento robusto e preciso.

---

## Fase 1: Configuração Inicial e Melhoria da Interface

O objetivo inicial era fazer o bot funcionar e melhorar a experiência de usuário.

1.  **Configuração da API Key:**
    - O sistema foi modificado para carregar a `GOOGLE_API_KEY` a partir de um arquivo `.env`, utilizando a biblioteca `python-dotenv`. Isso evita expor a chave no código.
    - O arquivo `.env` foi adicionado ao `.gitignore` para garantir a segurança.

2.  **Melhoria da Experiência do Usuário (UX):
    - **Feedback de Carregamento:** O arquivo `web_app/frontend/src/Chat.js` foi modificado para incluir um estado `isLoading`. Agora, uma mensagem "*Analisando os documentos...*" é exibida enquanto o usuário aguarda a resposta da IA.
    - **Estilização do Markdown:** O arquivo `web_app/frontend/src/Chat.css` foi atualizado com estilos completos para renderizar corretamente as respostas em Markdown, incluindo tabelas, listas, títulos e blocos de código.

3.  **Ajuste do Prompt da IA:**
    - O prompt em `chatbot/chatbot.py` foi reescrito para forçar a IA a sempre responder em um formato estruturado, com seções numeradas (Código do Artigo, Título, Causas, Soluções).

---

## Fase 2: Refatoração do Backend para Busca de Precisão

O maior desafio era a baixa precisão das buscas, pois o sistema lia os PDFs como texto corrido. A solução foi refatorar todo o processo de ingestão de dados.

1.  **Extração Estruturada dos PDFs:**
    - Foram instaladas as bibliotecas `pandas` e `tabula-py`.
    - Foi criado o script `scripts/processar_documentos.py`, que lê todos os PDFs da pasta `chatbot/documentos`, extrai as tabelas e salva os dados brutos em `web_app/base_conhecimento.csv`.

2.  **Limpeza e Estruturação dos Dados:**
    - Foi instalada a biblioteca `BeautifulSoup4` para analisar o conteúdo HTML encontrado no CSV.
    - Foi criado o script `scripts/limpar_dados.py`. Sua função é:
        - Ler o `base_conhecimento.csv`.
        - Lidar com inconsistências na extração (procurando dados nas colunas '0' e '3').
        - Usar `BeautifulSoup` para extrair o texto limpo do HTML, criando as colunas:
            - `codigo_artigo`
            - `titulo_artigo`
            - `texto_para_busca` (o conteúdo principal para a busca da IA)
        - Salvar o resultado final em `web_app/base_conhecimento_limpa.csv`.

3.  **Criação do Novo Índice Inteligente:**
    - Foi criado o script `web_app/criar_indice_estruturado.py`.
    - Ele lê o arquivo `base_conhecimento_limpa.csv`.
    - Ele cria um novo índice vetorial FAISS na pasta `web_app/faiss_index_estruturado`, usando **apenas** a coluna `texto_para_busca` para a busca e armazenando `codigo_artigo` e `titulo_artigo` como metadados.

4.  **Integração Final com o Chatbot:**
    - O arquivo principal `chatbot/chatbot.py` foi atualizado para:
        - Carregar o novo e mais preciso índice (`faiss_index_estruturado`).
        - Utilizar um prompt que aproveita os metadados recuperados para construir a resposta final, garantindo máxima precisão e eliminando a necessidade de "adivinhar" o código ou o título do artigo.

---

## Fase 3: Versionamento e Boas Práticas

1.  **`.gitignore`:** O arquivo foi atualizado para ignorar todos os arquivos gerados automaticamente (CSVs, índices FAISS, arquivos de ambiente), mantendo o repositório limpo.
2.  **Commit:** Todas as alterações foram salvas no repositório Git com uma mensagem de commit detalhada, criando um ponto de restauração seguro para o projeto.
