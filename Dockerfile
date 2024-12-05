FROM python:3.10-slim

WORKDIR /app

# Instalar dependências do sistema e gdown
RUN apt-get update && apt-get install -y wget python3-pip && pip install gdown

# Instalar dependências do Python
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Criar o diretório para o modelo
RUN mkdir -p ./modelo

# Baixar o modelo usando gdown
RUN gdown --id 1wHMYfley5JAqcSfSgEwE3mKUrk97_pP8 -O ./modelo/modelo_vit.onnx

# Copiar o restante do código
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
