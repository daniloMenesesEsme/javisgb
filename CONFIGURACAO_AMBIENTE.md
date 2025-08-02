# Configuração de Ambiente - Projeto Conhecimento IA

## Variáveis de Ambiente Necessárias

### Backend (Python/Flask)
Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```bash
# Chave de API do Google (OBRIGATÓRIO)
GOOGLE_API_KEY=sua_chave_api_aqui

# Credenciais de Login (RECOMENDADO)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=boticario2024_seguro

# Configurações do Flask (OPCIONAL)
FLASK_ENV=development
FLASK_DEBUG=True
```

### Frontend (React)
Crie um arquivo `.env` na pasta `web_app/frontend/` com:

```bash
# URL do Backend
REACT_APP_API_URL=http://localhost:5001

# Em produção, altere para:
# REACT_APP_API_URL=https://seu-dominio.com
```

## Como Obter a Chave de API do Google

1. Acesse [Google AI Studio](https://aistudio.google.com)
2. Faça login com sua conta Google
3. Clique em "Get API Key"
4. Copie a chave gerada
5. Cole no arquivo `.env` como mostrado acima

## Instalação de Dependências

### Backend:
```bash
pip install -r requirements.txt
```

### Frontend:
```bash
cd web_app/frontend
npm install
```

## Execução do Projeto

### 1. Executar Backend:
```bash
cd web_app
python app.py
```

### 2. Executar Frontend (novo terminal):
```bash
cd web_app/frontend
npm start
```

## Solução de Problemas Comuns

### Erro: "Module not found: react-markdown"
**Solução:** Execute `npm install react-markdown` no diretório do frontend

### Erro: "GOOGLE_API_KEY not found"
**Solução:** Verifique se o arquivo `.env` existe e contém a chave correta

### Erro: "Chatbot não inicializado"
**Solução:** Certifique-se que o índice FAISS foi criado executando os scripts de processamento 