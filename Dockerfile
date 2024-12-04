# Usar a imagem base Python
FROM python:3.10-slim

# Configurar o diretório de trabalho dentro do container
WORKDIR /app

# Copiar apenas o arquivo requirements.txt para o container
COPY requirements.txt .

# Atualizar pip e instalar dependências
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Baixar o modelo ONNX do Google Drive
RUN apt-get update && apt-get install -y wget
RUN wget -O modelo_vit.onnx "https://drive.google.com/uc?id=1wHMYfley5JAqcSfSgEwE3mKUrk97_pP8&export=download"

# Copiar o restante do projeto para o container
COPY . .

# Expor a porta para o FastAPI
EXPOSE 8000

# Comando para iniciar o servidor FastAPI
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
