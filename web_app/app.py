from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import os
import sys
import json
import csv
import subprocess
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

def verificar_e_processar_dados():
    """Verifica se os dados foram processados, se não, executa os scripts"""
    base_conhecimento_path = os.path.join(os.path.dirname(__file__), 'base_conhecimento_precisao.csv')
    faiss_index_path = os.path.join(os.path.dirname(__file__), 'faiss_index_estruturado')
    
    if not os.path.exists(base_conhecimento_path) or not os.path.exists(faiss_index_path):
        print("🔧 Primeira execução: Processando dados...")
        
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        
        try:
            # Processar PDFs
            print("📄 Processando PDFs...")
            subprocess.run([sys.executable, 'scripts/processar_documentos_pypdf.py'], 
                         cwd=root_dir, check=True)
            
            # Limpar dados
            print("🧹 Limpando dados...")
            subprocess.run([sys.executable, 'scripts/limpar_dados.py'], 
                         cwd=root_dir, check=True)
            
            # Criar índice FAISS
            print("🔍 Criando índice FAISS...")
            subprocess.run([sys.executable, 'web_app/criar_indice_estruturado.py'], 
                         cwd=root_dir, check=True)
            
            print("✅ Processamento concluído!")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro no processamento: {e}")
            raise e

# Inicialização automática para deploy
print("--- Iniciando Servidor Flask e Chatbot ---")
verificar_e_processar_dados()
chatbot_pronto = inicializar_chatbot()
if chatbot_pronto:
    print("--- Chatbot inicializado com sucesso ---")
else:
    print("!!! Aviso: Falha ao inicializar o chatbot !!!")

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
    print("--- Iniciando Servidor Flask em Produção ---")
    
    # A inicialização já foi feita no topo do arquivo
    port = int(os.environ.get('PORT', 5001))
    
    if chatbot_pronto:
        print(f"--- Servidor rodando na porta {port} --- ")
        app.run(host='0.0.0.0', port=port, debug=False)
    else:
        print("!!! Falha ao inicializar o chatbot. O servidor não será iniciado. !!!")
        app.run(host='0.0.0.0', port=port, debug=False)  # Roda mesmo assim para debug