import os
import pandas as pd
import sys
from pypdf import PdfReader
import re

def extrair_texto_estruturado_pdf(pdf_path):
    """
    Extrai texto estruturado dos PDFs dos artigos do SalesForce
    com foco em máxima precisão para orientações de franqueados
    """
    try:
        reader = PdfReader(pdf_path)
        texto_completo = ""
        
        for page_num, page in enumerate(reader.pages):
            texto_pagina = page.extract_text()
            if texto_pagina.strip():
                texto_completo += f"\n--- PÁGINA {page_num + 1} ---\n"
                texto_completo += texto_pagina
        
        return texto_completo
    except Exception as e:
        print(f"Erro ao processar {pdf_path}: {e}")
        return None

def estruturar_artigos_salesforce(texto, pdf_path):
    """
    Estrutura o texto extraído identificando artigos específicos do SalesForce
    """
    artigos = []
    
    # Padrões para identificar códigos de artigo
    padroes_codigo = [
        r'(?:Código|CÓDIGO).*?(\d{3,5})',
        r'(?:Artigo|ARTIGO).*?(\d{3,5})',
        r'(?:CSF|Tech).*?(\d{3,5})'
    ]
    
    # Padrões para identificar títulos
    padroes_titulo = [
        r'(?:Título|TÍTULO)[:\-\s]+([^\n\r]{10,100})',
        r'(?:Como|COMO)\s+([^\n\r]{10,100})',
        r'(?:Procedimento|PROCEDIMENTO)[:\-\s]+([^\n\r]{10,100})'
    ]
    
    # Dividir texto em seções
    secoes = re.split(r'(?=\n--- PÁGINA|\n\d+\.|\nArtigo|\nCódigo)', texto)
    
    for secao in secoes:
        if len(secao.strip()) < 50:  # Ignorar seções muito pequenas
            continue
            
        # Extrair código do artigo
        codigo_artigo = "Não Encontrado"
        for padrao in padroes_codigo:
            match = re.search(padrao, secao, re.IGNORECASE)
            if match:
                codigo_artigo = match.group(1)
                break
        
        # Extrair título
        titulo_artigo = "Não Encontrado"
        for padrao in padroes_titulo:
            match = re.search(padrao, secao, re.IGNORECASE)
            if match:
                titulo_artigo = match.group(1).strip()
                break
        
        # Se não encontrou título por padrão, pegar primeira linha significativa
        if titulo_artigo == "Não Encontrado":
            linhas = [l.strip() for l in secao.split('\n') if l.strip() and len(l.strip()) > 10]
            if linhas:
                titulo_artigo = linhas[0][:100]
        
        # Texto para busca (limpeza básica)
        texto_busca = re.sub(r'\s+', ' ', secao).strip()
        texto_busca = re.sub(r'[^\w\s\-\.\,\:\;\!\?\(\)]', '', texto_busca)
        
        if len(texto_busca) > 100:  # Só incluir se tiver conteúdo suficiente
            artigos.append({
                'codigo_artigo': codigo_artigo,
                'titulo_artigo': titulo_artigo,
                'texto_para_busca': texto_busca,
                'fonte_arquivo': os.path.basename(pdf_path)
            })
    
    return artigos

def processar_pdfs_precisao_maxima():
    """
    Processa PDFs dos artigos SalesForce com foco em precisão máxima
    para orientações críticas de franqueados
    """
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    pasta_documentos = os.path.join(project_root, 'chatbot', 'documentos')
    caminho_saida = os.path.join(project_root, 'web_app', 'base_conhecimento_precisao.csv')
    
    if not os.path.isdir(pasta_documentos):
        print(f"ERRO CRÍTICO: Pasta de documentos não encontrada: {pasta_documentos}")
        return False
    
    arquivos_pdf = [os.path.join(pasta_documentos, f) 
                   for f in os.listdir(pasta_documentos) 
                   if f.lower().endswith('.pdf')]
    
    if not arquivos_pdf:
        print("ERRO CRÍTICO: Nenhum PDF encontrado!")
        return False
    
    print(f"🔥 PROCESSAMENTO CRÍTICO: {len(arquivos_pdf)} PDFs dos artigos SalesForce")
    print("⚠️  MÁXIMA PRECISÃO EXIGIDA para orientações de franqueados")
    
    todos_artigos = []
    
    for i, pdf_path in enumerate(arquivos_pdf, 1):
        print(f"\n📄 Processando [{i}/{len(arquivos_pdf)}]: {os.path.basename(pdf_path)}")
        
        texto_extraido = extrair_texto_estruturado_pdf(pdf_path)
        if not texto_extraido:
            print(f"❌ FALHA ao extrair texto de {os.path.basename(pdf_path)}")
            continue
        
        artigos_encontrados = estruturar_artigos_salesforce(texto_extraido, pdf_path)
        todos_artigos.extend(artigos_encontrados)
        
        print(f"✅ Extraídos {len(artigos_encontrados)} artigos")
    
    if not todos_artigos:
        print("❌ ERRO CRÍTICO: Nenhum artigo foi extraído dos PDFs!")
        return False
    
    # Criar DataFrame e salvar
    df = pd.DataFrame(todos_artigos)
    
    # Limpeza adicional para máxima qualidade
    df['codigo_artigo'] = df['codigo_artigo'].astype(str)
    df['titulo_artigo'] = df['titulo_artigo'].str.strip()
    df['texto_para_busca'] = df['texto_para_busca'].str.strip()
    
    # Remover duplicatas baseado no código e título
    df_limpo = df.drop_duplicates(subset=['codigo_artigo', 'titulo_artigo'])
    
    # Filtrar apenas artigos com conteúdo substancial
    df_final = df_limpo[df_limpo['texto_para_busca'].str.len() > 200].copy()
    
    try:
        df_final.to_csv(caminho_saida, index=False, encoding='utf-8-sig')
        print(f"\n🎯 SUCESSO CRÍTICO!")
        print(f"📊 Base de conhecimento salva: {caminho_saida}")
        print(f"📈 Total de artigos processados: {len(df_final)}")
        print(f"🎯 Precisão otimizada para orientações oficiais")
        return True
    except Exception as e:
        print(f"❌ ERRO ao salvar: {e}")
        return False

if __name__ == '__main__':
    print("🚨 PROCESSAMENTO CRÍTICO - ARTIGOS SALESFORCE GRUPO BOTICÁRIO")
    print("⚠️  Este sistema orienta franqueados sobre infrações oficiais")
    print("🎯 Exigência: Precisão máxima (100%)")
    print("-" * 60)
    
    sucesso = processar_pdfs_precisao_maxima()
    
    if sucesso:
        print("\n✅ PROCESSAMENTO CONCLUÍDO COM SUCESSO!")
        print("🔥 Pronto para orientações críticas de franqueados")
    else:
        print("\n❌ FALHA CRÍTICA NO PROCESSAMENTO!")
        print("🚨 Sistema não está apto para produção") 