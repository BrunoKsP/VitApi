# Usar a imagem base Python
FROM python:3.10-slim

# Configurar o diretório de trabalho dentro do container
WORKDIR /app

# Copiar apenas o requirements.txt para o cache de build
COPY requirements.txt .

# Instalar as dependências no ambiente do container
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código da aplicação para o container
COPY . .

# Expor a porta para o FastAPI (por padrão, 8000)
EXPOSE 8000

# Comando para iniciar o servidor FastAPI
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
