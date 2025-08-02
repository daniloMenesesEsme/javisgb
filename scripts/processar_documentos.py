import os
import tabula
import pandas as pd
import sys

def processar_pdfs_para_csv():
    """
    Lê todos os arquivos PDF de uma pasta, extrai as tabelas e os consolida em um único arquivo CSV.
    """
    # Adiciona o diretório raiz ao path para garantir que o script encontre as pastas corretas
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # Caminhos relativos ao diretório raiz do projeto
    pasta_documentos = os.path.join(project_root, 'chatbot', 'documentos')
    caminho_saida_csv = os.path.join(project_root, 'web_app', 'base_conhecimento.csv')

    if not os.path.isdir(pasta_documentos):
        print(f"Erro: A pasta de documentos '{pasta_documentos}' não foi encontrada.")
        sys.exit(1)

    # Lista todos os arquivos PDF na pasta de documentos
    arquivos_pdf = [os.path.join(pasta_documentos, f) for f in os.listdir(pasta_documentos) if f.lower().endswith('.pdf')]

    if not arquivos_pdf:
        print(f"Nenhum arquivo PDF encontrado em '{pasta_documentos}'.")
        return

    print(f"Encontrados {len(arquivos_pdf)} arquivos PDF para processar...")

    lista_de_dataframes = []

    for i, pdf in enumerate(arquivos_pdf):
        print(f"Processando arquivo {i+1}/{len(arquivos_pdf)}: {os.path.basename(pdf)}")
        try:
            # Extrai todas as tabelas do PDF. 'lattice=True' é bom para tabelas com linhas visíveis.
            tabelas = tabula.read_pdf(pdf, pages='all', multiple_tables=True, lattice=True, pandas_options={'header': None})
            
            if tabelas and len(tabelas) > 0:
                # Filtra tabelas vazias ou com dados insuficientes
                tabelas_validas = [t for t in tabelas if not t.empty and len(t.columns) > 0]
                if tabelas_validas:
                    # Concatena todas as tabelas encontradas em um único DataFrame
                    df_pdf = pd.concat(tabelas_validas, ignore_index=True)
                    lista_de_dataframes.append(df_pdf)
                    print(f"  -> Sucesso: {len(tabelas_validas)} tabela(s) extraída(s)")
                else:
                    print(f"  -> Aviso: Tabelas encontradas mas estão vazias em {os.path.basename(pdf)}")
            else:
                print(f"  -> Aviso: Nenhuma tabela encontrada em {os.path.basename(pdf)}")
        except FileNotFoundError:
            print(f"  -> Erro: Arquivo não encontrado: {os.path.basename(pdf)}")
        except PermissionError:
            print(f"  -> Erro: Sem permissão para acessar: {os.path.basename(pdf)}")
        except Exception as e:
            print(f"  -> Erro ao processar o arquivo {os.path.basename(pdf)}: {type(e).__name__}: {e}")

    if not lista_de_dataframes:
        print("Nenhuma tabela foi extraída de nenhum dos arquivos PDF. O arquivo CSV não será criado.")
        return

    print("Consolidando todos os dados...")
    df_final = pd.concat(lista_de_dataframes, ignore_index=True)

    # --- Limpeza e Estruturação dos Dados ---
    # Baseado na sua descrição, vamos assumir uma estrutura de colunas.
    # Você pode precisar ajustar os nomes e a ordem se a extração não for perfeita.
    
    # Renomeia as colunas (ajuste os números se a extração gerar colunas diferentes)
    # Exemplo: df_final.columns = ['ColunaA', 'ColunaB', 'ColunaC', ...]
    # Por enquanto, vamos manter os nomes genéricos e você pode nos dizer como renomeá-las depois de ver o resultado.

    # Remove linhas que são completamente vazias
    df_final.dropna(how='all', inplace=True)

    # Salva o DataFrame consolidado em um arquivo CSV
    try:
        df_final.to_csv(caminho_saida_csv, index=False, encoding='utf-8-sig')
        print("-" * 50)
        print(f"SUCESSO! Arquivo consolidado salvo em: {caminho_saida_csv}")
        print(f"Total de {len(df_final)} linhas processadas.")
        print("-" * 50)
    except Exception as e:
        print(f"Erro ao salvar o arquivo CSV: {e}")

if __name__ == '__main__':
    processar_pdfs_para_csv()
