from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import os
import sys
import json
import csv
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Importa a função correta para streaming
from chatbot.chatbot import inicializar_chatbot, get_chatbot_answer_stream

app = Flask(__name__)
CORS(app)

chatbot_pronto = False
FEEDBACK_FILE = os.path.join(os.path.dirname(__file__), 'feedback.csv')

@app.route('/')
def home():
    return "Backend do Chatbot está funcionando!"

@app.route('/chat', methods=['GET'])
def chat():
    if not chatbot_pronto:
        def error_stream():
            error_data = {"error": "O Chatbot ainda não está pronto."}
            yield "data: " + json.dumps(error_data) + "\n\n"
        return Response(error_stream(), mimetype='text/event-stream')

    pergunta = request.args.get('message')

    if not pergunta:
        def error_stream():
            error_data = {"error": "Nenhuma mensagem foi fornecida."}
            yield "data: " + json.dumps(error_data) + "\n\n"
        return Response(error_stream(), mimetype='text/event-stream')

    return Response(get_chatbot_answer_stream(pergunta), mimetype='text/event-stream')

@app.route('/api/auth', methods=['POST'])
def authenticate():
    """Endpoint para autenticação de usuários"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        # Buscar credenciais das variáveis de ambiente
        valid_username = os.environ.get('ADMIN_USERNAME', 'admin')
        valid_password = os.environ.get('ADMIN_PASSWORD', 'boticario2024')
        
        if username == valid_username and password == valid_password:
            return jsonify({"status": "success", "message": "Autenticação bem-sucedida"})
        else:
            return jsonify({"status": "error", "message": "Credenciais inválidas"}), 401
    except Exception as e:
        print(f"Erro na autenticação: {e}")
        return jsonify({"status": "error", "message": "Erro interno de autenticação"}), 500

@app.route('/feedback', methods=['POST'])
def feedback():
    try:
        data = request.get_json()
        question = data.get('question')
        answer = data.get('answer')
        feedback_type = data.get('feedback')

        if not all([question, answer, feedback_type]):
            return jsonify({"status": "error", "message": "Dados de feedback incompletos."}), 400

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row = [timestamp, question, answer, feedback_type]

        file_exists = os.path.isfile(FEEDBACK_FILE)
        with open(FEEDBACK_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Timestamp", "Question", "Answer", "Feedback"])
            writer.writerow(row)

        return jsonify({"status": "success", "message": "Feedback recebido com sucesso!"})
    except Exception as e:
        print(f"Erro ao salvar feedback: {e}")
        return jsonify({"status": "error", "message": "Erro interno ao salvar feedback."}), 500

if __name__ == '__main__':
    print("--- Iniciando Servidor Flask e Chatbot ---")
    chatbot_pronto = inicializar_chatbot()
    if chatbot_pronto:
        print("--- Servidor pronto para receber requisições --- ")
        app.run(host='0.0.0.0', port=5001, debug=True)
    else:
        print("!!! Falha ao inicializar o chatbot. O servidor não será iniciado. !!!")