# Usar uma imagem base oficial do Python
FROM python:3.9-slim

# Definir o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copiar o requirements.txt e instalar as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante do projeto para o contêiner
COPY . .

# Expor a porta que a aplicação usará
EXPOSE 5001

# Comando para rodar a aplicação
CMD ["python", "app.py"]