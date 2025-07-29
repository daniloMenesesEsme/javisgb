import pandas as pd
import os

# Caminhos
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
caminho_csv = os.path.join(project_root, 'web_app', 'base_conhecimento.csv')
caminho_saida_txt = os.path.join(project_root, 'scripts', 'analise.txt')

try:
    # Tenta ler o CSV com uma codificação diferente, se necessário
    try:
        df = pd.read_csv(caminho_csv, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(caminho_csv, encoding='latin1')

    # Abre o arquivo de saída com codificação UTF-8
    with open(caminho_saida_txt, 'w', encoding='utf-8') as f:
        f.write("--- Nomes das Colunas ---\n")
        f.write(str(list(df.columns)) + '\n\n')

        f.write("--- Primeiras 5 Linhas ---\n")
        f.write(df.head().to_string())
    
    print(f"Análise salva com sucesso em: {caminho_saida_txt}")

except FileNotFoundError:
    print(f"Erro: O arquivo {caminho_csv} não foi encontrado.")
except Exception as e:
    print(f"Ocorreu um erro: {e}")