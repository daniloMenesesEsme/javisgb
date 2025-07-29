from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys

load_dotenv()
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from chatbot.chatbot import inicializar_chatbot, get_chatbot_answer

app = Flask(__name__)
CORS(app)  # Habilita CORS para permitir requisições do frontend

# Flag para verificar se o chatbot foi inicializado com sucesso
chatbot_pronto = False

@app.route('/')
def home():
    """Rota básica para verificar se o backend está no ar."""
    return "Backend do Chatbot está funcionando!"

@app.route('/chat', methods=['POST'])
def chat():
    """Recebe perguntas do frontend e retorna a resposta do chatbot."""
    if not chatbot_pronto:
        return jsonify({"error": "O Chatbot ainda não está pronto. Por favor, aguarde um momento."}), 503

    data = request.get_json()
    pergunta = data.get('message')

    if not pergunta:
        return jsonify({"error": "Nenhuma mensagem foi fornecida."}), 400

    # Usa a função centralizada para obter a resposta
    success, result = get_chatbot_answer(pergunta)

    if success:
        return jsonify({"response": result})
    else:
        # Retorna o erro que ocorreu dentro do chatbot
        return jsonify({"error": result}), 500

if __name__ == '__main__':
    # Inicializa o chatbot ao iniciar o servidor Flask
    print("--- Iniciando Servidor Flask e Chatbot ---")
    chatbot_pronto = inicializar_chatbot()
    if chatbot_pronto:
        print("--- Servidor pronto para receber requisições --- ")
        # O modo debug=False é mais seguro para produção, mas para desenvolvimento, True é útil.
        # Use a porta 5001 para evitar conflitos com a porta 5000 padrão.
        app.run(host='0.0.0.0', port=5001, debug=True)
    else:
        print("!!! Falha ao inicializar o chatbot. O servidor não será iniciado. !!!")
        print("Por favor, verifique as configurações, especialmente a variável de ambiente GOOGLE_API_KEY.")
