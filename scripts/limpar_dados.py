import pandas as pd
import os
from bs4 import BeautifulSoup
import re

def limpar_e_estruturar_csv():
    """
    Lê o CSV bruto, extrai e limpa os dados da coluna de HTML, 
    e salva um novo CSV estruturado.
    """
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    caminho_csv_bruto = os.path.join(project_root, 'web_app', 'base_conhecimento.csv')
    caminho_csv_limpo = os.path.join(project_root, 'web_app', 'base_conhecimento_limpa.csv')

    print(f"Lendo o arquivo de dados brutos: {caminho_csv_bruto}")
    try:
        # Lê as colunas como string para evitar erros de tipo
        df = pd.read_csv(caminho_csv_bruto, dtype={ '0': str, '3': str })
    except FileNotFoundError:
        print(f"Erro: Arquivo não encontrado. Verifique o caminho: {caminho_csv_bruto}")
        return

    print("Iniciando processo de limpeza e estruturação dos dados...")

    resultados = []

    for index, row in df.iterrows():
        # Lógica para encontrar o conteúdo HTML na coluna '3' ou '0'
        html_content = None
        if isinstance(row.get('3'), str) and '<p>' in row.get('3', ''):
            html_content = row['3']
        elif isinstance(row.get('0'), str) and '<p>' in row.get('0', ''):
            html_content = row['0']
        
        # Pula a linha se nenhum conteúdo HTML for encontrado
        if not html_content:
            continue

        soup = BeautifulSoup(html_content, 'html.parser')

        # Extrai todo o texto visível do HTML para a busca da IA
        texto_para_busca = soup.get_text(separator=' ', strip=True)

        # Tenta extrair um título (procura por tags de cabeçalho ou a primeira tag strong)
        titulo_artigo = soup.find(['h1', 'h2', 'h3', 'strong'])
        titulo_artigo = titulo_artigo.get_text(strip=True) if titulo_artigo else "Título não encontrado"
        
        # Tenta extrair um código de artigo (procura por um número de 4+ dígitos seguido por '-')
        codigo_match = re.search(r'(\d{4,})\s*-', texto_para_busca)
        codigo_artigo = codigo_match.group(1) if codigo_match else "Código não encontrado"

        resultados.append({
            'codigo_artigo': codigo_artigo,
            'titulo_artigo': titulo_artigo,
            'texto_para_busca': texto_para_busca,
            'html_original': html_content # Mantemos o original para referência, se necessário
        })

    if not resultados:
        print("Nenhum dado válido foi extraído. O arquivo CSV limpo não será criado.")
        return

    df_limpo = pd.DataFrame(resultados)

    print(f"Processo concluído. {len(df_limpo)} linhas de dados limpos foram geradas.")

    try:
        df_limpo.to_csv(caminho_csv_limpo, index=False, encoding='utf-8-sig')
        print("-" * 50)
        print(f"SUCESSO! Arquivo limpo e estruturado salvo em: {caminho_csv_limpo}")
        print("-" * 50)
    except Exception as e:
        print(f"Erro ao salvar o arquivo CSV limpo: {e}")

if __name__ == '__main__':
    limpar_e_estruturar_csv()
