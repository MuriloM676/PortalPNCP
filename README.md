# Painel de Monitoramento de Licitações

Este projeto é um painel web para monitoramento de licitações públicas no Brasil, utilizando a API do [Portal Nacional de Contratações Públicas (PNCP)](https://pncp.gov.br/). O painel permite consultar licitações com base em filtros como estado (UF), data final, modalidade, município, CNPJ e código IBGE do município, exibindo os resultados em uma tabela formatada.

## Funcionalidades

- **Consulta de Licitações**: Busca licitações públicas usando a API do PNCP.
- **Filtros Personalizados**:
  - Estado (UF)
  - Data final
  - Modalidade (ex.: Pregão Eletrônico, Dispensa)
  - Município
  - CNPJ (opcional)
  - Código IBGE do município (opcional)
- **Tabela Formatada**:
  - Exibe número da compra, objeto, valor estimado (em R$), data (formato DD/MM/YYYY) e órgão.
  - Estilização personalizada com Bootstrap e CSS.
- **Paginação**: Navegação entre páginas de resultados (oculta quando há apenas uma página).
- **Validação de Entrada**: Validação do CNPJ no frontend.

## Tecnologias Utilizadas

- **Backend**: Python, Flask, Pandas, Requests
- **Frontend**: HTML, Bootstrap 5, CSS personalizado, JavaScript
- **API**: PNCP (Portal Nacional de Contratações Públicas)

## Pré-requisitos

Antes de executar o projeto, certifique-se de ter o seguinte instalado:

- Python 3.8 ou superior
- pip (gerenciador de pacotes do Python)
- Um navegador web (ex.: Chrome, Firefox)

## Instalação

Siga os passos abaixo para configurar e executar o projeto localmente:

1. **Clone o repositório**:
   ```bash
   git clone https://github.com/<seu-usuario>/<nome-do-repositorio>.git
   cd <nome-do-repositorio>