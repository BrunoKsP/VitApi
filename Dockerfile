# Usar a imagem base Python
FROM python:3.10-slim

# Configurar o diretório de trabalho dentro do container
# Configurar o diretório de trabalho
WORKDIR /app

# Instalar dependências
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Criar o diretório para o modelo
RUN mkdir -p ./modelo

# Baixar o modelo do Google Drive para o diretório correto
RUN wget -O ./modelo/modelo_vit.onnx "https://drive.google.com/uc?id=1wHMYfley5JAqcSfSgEwE3mKUrk97_pP8&export=download"

# Copiar o restante do código
COPY . .

# Expor a porta para o FastAPI
EXPOSE 8000

# Comando para iniciar o servidor FastAPI
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
