from flask import Flask, render_template, request
import requests
import pandas as pd
from datetime import datetime, timedelta
import locale

app = Flask(__name__)

# Configurações da API
BASE_URL = "https://pncp.gov.br/api/consulta/v1/contratacoes/proposta"  # Endpoint correto

# Lista de modalidades disponíveis (extraída da resposta da API)
MODALIDADES = [
    "Pregão - Eletrônico",
    "Pregão - Presencial",
    "Concorrência - Presencial",
    "Dispensa"
]

# Configurar o locale para formatação de moeda brasileira
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except locale.Error:
    # Caso o locale 'pt_BR.UTF-8' não esteja disponível, usar um fallback
    locale.setlocale(locale.LC_ALL, '')

# Função para buscar licitações
def buscar_licitacoes(uf="SP", data_final=None, cnpj=None, codigo_municipio_ibge=None, modalidade_nome=None, municipio_nome=None, pagina=1):
    # Definir valor padrão para dataFinal se não fornecido
    if not data_final:
        data_final = datetime.now().strftime("%Y%m%d")  # Formato: YYYYMMDD
    else:
        # Converter data_final do formato YYYY-MM-DD para YYYYMMDD
        data_final = data_final.replace("-", "")
    
    # Parâmetros ajustados
    parametros = {
        "uf": uf,
        "dataFinal": data_final,
        "pagina": pagina,
        "tamanhoPagina": 50
    }
    
    # Adicionar parâmetros opcionais se fornecidos
    if cnpj:
        # Remover pontuação do CNPJ
        cnpj = ''.join(filter(str.isdigit, cnpj))
        parametros["cnpj"] = cnpj
    if codigo_municipio_ibge:
        parametros["codigoMunicipioIbge"] = codigo_municipio_ibge
    
    print(f"Parâmetros enviados: {parametros}")
    print(f"URL completa: {BASE_URL}?{requests.compat.urlencode(parametros)}")
    try:
        resposta = requests.get(BASE_URL, params=parametros, timeout=10)
        resposta.raise_for_status()
        # Adicionar logs para inspecionar a resposta
        print(f"Código de status: {resposta.status_code}")
        print(f"Conteúdo bruto da resposta: {resposta.text}")
        # Verificar se a resposta está vazia
        if not resposta.text.strip():
            print("Resposta vazia recebida da API.")
            return [], 1, 1  # Retorna lista vazia, página atual e total de páginas
        dados = resposta.json()
        print(f"Resposta da API (JSON): {dados}")
        
        # Filtrar os resultados com base em modalidadeNome e municipioNome
        licitacoes = dados.get("data", [])
        if modalidade_nome:
            licitacoes = [licitacao for licitacao in licitacoes if licitacao.get("modalidadeNome") == modalidade_nome]
        if municipio_nome:
            licitacoes = [licitacao for licitacao in licitacoes if licitacao.get("unidadeOrgao", {}).get("municipioNome", "").lower() == municipio_nome.lower()]
        
        return licitacoes, dados.get("numeroPagina", 1), dados.get("totalPaginas", 1)
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar dados: {e}")
        return [], 1, 1
    except ValueError as e:
        print(f"Erro ao decodificar JSON: {e}")
        print(f"Conteúdo bruto da resposta: {resposta.text}")
        return [], 1, 1

# Rota principal
@app.route("/", methods=["GET", "POST"])
def painel():
    # Valores padrão
    uf = "SP"
    data_final = datetime.now().strftime("%Y-%m-%d")
    cnpj = ""
    codigo_municipio_ibge = ""
    modalidade_nome = ""
    municipio_nome = ""
    pagina = 10
    
    # Se o formulário for enviado, atualizar os valores
    if request.method == "POST":
        uf = request.form.get("uf", "SP").upper()
        data_final = request.form.get("data_final", data_final)
        cnpj = request.form.get("cnpj", "")
        codigo_municipio_ibge = request.form.get("codigo_municipio_ibge", "")
        modalidade_nome = request.form.get("modalidade_nome", "")
        municipio_nome = request.form.get("municipio_nome", "")
        pagina = int(request.form.get("pagina", 1))
    
    # Buscar licitações
    licitacoes, numero_pagina, total_paginas = buscar_licitacoes(
        uf=uf,
        data_final=data_final,
        cnpj=cnpj if cnpj else None,
        codigo_municipio_ibge=codigo_municipio_ibge if codigo_municipio_ibge else None,
        modalidade_nome=modalidade_nome if modalidade_nome else None,
        municipio_nome=municipio_nome if municipio_nome else None,
        pagina=pagina
    )
    
    # Processar os dados
    if licitacoes:
        df = pd.DataFrame(licitacoes)
        # Mapear os campos retornados pela API para os esperados no frontend
        colunas = ["numeroCompra", "objetoCompra", "valorTotalEstimado", "dataPublicacaoPncp", "orgaoEntidade"]
        colunas_disponiveis = [col for col in colunas if col in df.columns]
        if colunas_disponiveis:
            # Renomear colunas e extrair informações aninhadas
            df = df[colunas_disponiveis].copy()
            if "orgaoEntidade" in df.columns:
                df["orgao"] = df["orgaoEntidade"].apply(lambda x: x.get("razaoSocial", "N/A") if isinstance(x, dict) else "N/A")
                df = df.drop(columns=["orgaoEntidade"])
            df = df.rename(columns={
                "numeroCompra": "Número",
                "objetoCompra": "Objeto",
                "valorTotalEstimado": "Valor Estimado",
                "dataPublicacaoPncp": "Data"
            })
            # Formatar a coluna "Valor Estimado" como moeda brasileira
            if "Valor Estimado" in df.columns:
                df["Valor Estimado"] = df["Valor Estimado"].apply(
                    lambda x: locale.currency(x, grouping=True) if pd.notnull(x) else "R$ 0,00"
                )
            # Formatar a coluna "Data" para DD/MM/YYYY
            if "Data" in df.columns:
                df["Data"] = df["Data"].apply(
                    lambda x: datetime.strptime(x, "%Y-%m-%dT%H:%M:%S").strftime("%d/%m/%Y %H:%M:%S") if pd.notnull(x) else "N/A"
                )
            # Reordenar colunas para exibição
            colunas_finais = ["Número", "Objeto", "Valor Estimado", "Data", "orgao"]
            colunas_finais = [col for col in colunas_finais if col in df.columns]
            df = df[colunas_finais]
            df = df.rename(columns={"orgao": "Órgão"})
            tabela_html = df.to_html(index=False, classes="table table-striped custom-table", escape=False)
        else:
            tabela_html = "<p>Colunas esperadas não encontradas nos dados.</p>"
    else:
        tabela_html = "<p>Nenhuma licitação encontrada.</p>"
    
    # Renderizar a página com os dados
    return render_template(
        "index.html",
        tabela=tabela_html,
        uf=uf,
        data_final=data_final,
        cnpj=cnpj,
        codigo_municipio_ibge=codigo_municipio_ibge,
        modalidade_nome=modalidade_nome,
        municipio_nome=municipio_nome,
        pagina=numero_pagina,
        total_paginas=total_paginas,
        modalidades=MODALIDADES
    )

if __name__ == "__main__":
    app.run(debug=True)