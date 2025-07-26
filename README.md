# Projeto JavisGB - Assistente de IA para Atendimento

Este projeto é uma aplicação web que utiliza Inteligência Artificial para responder a perguntas de analistas de atendimento com base em uma base de conhecimento de documentos PDF.

---

## Resumo Detalhado do Projeto

Construímos uma aplicação web completa que funciona como um assistente de IA para analistas de atendimento. O sistema, apelidado de "JavisGB", permite que um usuário faça perguntas em uma interface de chat e receba respostas geradas por uma inteligência artificial (Google Gemini) com base em um conjunto específico de documentos PDF.

O projeto foi estruturado de forma robusta, separando a lógica do chatbot, o servidor que o disponibiliza (backend) e a interface do usuário (frontend). Além disso, implementamos uma otimização crucial para garantir que a aplicação inicie rapidamente, tornando-a mais prática para o uso diário.

### Componentes Construídos e Suas Funcionalidades

1.  **O Chatbot (A Inteligência do Sistema)**
    *   **Localização:** `chatbot/chatbot.py`
    *   **Tecnologia:** Python, usando as bibliotecas LangChain e Google Generative AI.
    *   **O que faz:**
        *   **Carregamento Otimizado:** Não processa mais os PDFs toda vez que inicia. Em vez disso, ele carrega um **índice vetorial pré-processado** (armazenado na pasta `web_app/faiss_index`), o que torna a inicialização quase instantânea.
        *   **Geração de Respostas:** Utiliza o modelo `gemini-1.5-flash-latest` para entender a pergunta do usuário.
        *   **Busca de Conhecimento (RAG):** Procura as informações mais relevantes dentro do índice vetorial dos documentos para formular uma resposta precisa e baseada exclusivamente no conteúdo fornecido.
        *   **Interface de Função:** Expõe duas funções principais: `inicializar_chatbot()` e `get_chatbot_answer()`, que são usadas pelo backend.

2.  **O Script de Indexação (A Otimização de Performance)**
    *   **Localização:** `web_app/criar_indice.py`
    *   **O que faz:** Este é um script de "passo único". Ele é responsável por:
        *   Ler todos os documentos da pasta `chatbot/documentos/`.
        *   Dividir o texto dos PDFs em pedaços menores (chunks).
        *   Converter esses pedaços em vetores numéricos (embeddings) usando o modelo do Google.
        *   Salvar o resultado final como um índice **FAISS** na pasta `web_app/faiss_index`.
    *   **Benefício:** Este processo pesado é executado apenas uma vez (ou quando os PDFs mudam), garantindo que o servidor principal inicie rapidamente.

3.  **O Backend (A API com Flask)**
    *   **Localização:** `web_app/app.py`
    *   **Tecnologia:** Python, usando o microframework Flask.
    *   **O que faz:**
        *   Serve como a ponte entre o frontend e o chatbot.
        *   Ao ser iniciado, ele chama a função `inicializar_chatbot()` para carregar o índice em memória.
        *   Expõe um endpoint `POST /chat` na porta `5001`.
        *   Recebe as perguntas do usuário, passa para a função `get_chatbot_answer()` e retorna a resposta do chatbot em formato JSON.

4.  **O Frontend (A Interface do Usuário)**
    *   **Localização:** `web_app/frontend/`
    *   **Tecnologia:** JavaScript, usando a biblioteca React.
    *   **O que faz:**
        *   **Login:** Apresenta uma tela de login simples (usuário `admin`, senha `admin`) para controlar o acesso.
        *   **Chat:** Oferece uma interface de chat clássica onde o usuário pode digitar suas perguntas.
        *   **Comunicação:** Envia as perguntas para a API do backend (`http://127.0.0.1:5001/chat`) e exibe a resposta recebida.
        *   **Feedback Visual:** Mostra uma mensagem de "Buscando informações..." enquanto aguarda a resposta do chatbot.

5.  **Versionamento (Segurança e Histórico)**
    *   **Tecnologia:** Git e GitHub.
    *   **O que foi feito:**
        *   Inicializamos um repositório Git na raiz do projeto.
        *   Adicionamos todos os arquivos relevantes.
        *   Enviamos com sucesso o estado atual do projeto para o seu repositório no GitHub: `https://github.com/daniloMenesesEsme/javisgb`. Isso garante que você tenha um ponto de restauração seguro e um histórico de todo o trabalho feito.

---

## Mapa Mental da Estrutura do Projeto

```
/ (Raiz do Projeto)
│
├── .gitignore             # Ignora arquivos e pastas desnecessários (venv, node_modules, etc.)
│
├── chatbot/               # Contém toda a lógica da IA
│   ├── documentos/        # Pasta para armazenar os PDFs que formam a base de conhecimento
│   └── chatbot.py         # Módulo principal que carrega o índice e gera as respostas
│
├── web_app/               # Contém a aplicação web (backend e frontend)
│   │
│   ├── frontend/          # Interface do usuário em React
│   │   ├── public/        # Arquivos estáticos (HTML, ícones)
│   │   └── src/           # Código-fonte do React
│   │       ├── App.js     # Componente principal que gerencia o login e o chat
│   │       ├── Login.js   # Componente da tela de login
│   │       └── Chat.js    # Componente da interface de chat
│   │
│   ├── venv/              # Ambiente virtual do Python (ignorado pelo .gitignore)
│   │
│   ├── faiss_index/       # Onde o índice vetorial é salvo (ignorado pelo .gitignore)
│   │
│   ├── app.py             # Servidor web (backend) em Flask que serve a API
│   │
│   └── criar_indice.py    # Script para processar os PDFs e criar o índice FAISS
│
└── README.md              # Este arquivo de documentação
```

---

## Fluxograma de Dados

Este fluxograma descreve o ciclo de vida de uma pergunta feita pelo usuário.

```mermaid
graph TD
    subgraph "Passo 1: Indexação (Executado uma vez)"
        A[PDFs em /chatbot/documentos] --> B(Executa criar_indice.py);
        B --> C{Processa PDFs, gera Embeddings};
        C --> D[/web_app/faiss_index];
    end

    subgraph "Passo 2: Execução da Aplicação"
        E[Usuário acessa a aplicação no navegador] --> F(Frontend - Login.js);
        F --> G(Frontend - Chat.js);
        G -- Pergunta do usuário --> H{API POST /chat};
        H --> I[Backend - app.py];
        I -- Carrega na inicialização --> D;
        I -- Envia pergunta para --> J(Chatbot - chatbot.py);
        J -- Usa o índice carregado --> K{Busca documentos relevantes no FAISS};
        K -- Envia contexto e pergunta para --> L(Modelo Gemini);
        L -- Gera resposta --> J;
        J -- Retorna resposta para --> I;
        I -- Resposta JSON --> H;
        H -- Exibe resposta para --> G;
    end

    style D fill:#f9f,stroke:#333,stroke-width:2px
```