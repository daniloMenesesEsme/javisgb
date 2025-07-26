# Projeto JavisGB - Assistente de IA para Atendimento

Este projeto é uma aplicação web que utiliza Inteligência Artificial para responder a perguntas de analistas de atendimento com base em uma base de conhecimento de documentos PDF.

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
