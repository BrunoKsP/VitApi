from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import onnxruntime as ort
from PIL import Image
import io
import base64
import numpy as np

# Inicializar o aplicativo FastAPI
app = FastAPI()

# Caminho para o modelo ONNX
model_path = "./modelo/modelo_vit.onnx"
session = ort.InferenceSession(model_path)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas as origens
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos HTTP
    allow_headers=["*"],  # Permite todos os cabeçalhos
)

# Função para pré-processar a imagem
def preprocess_image(image):
    try:
        img = Image.open(image).convert("RGB")
        img = img.resize((224, 224))  # Redimensionar para 224x224
        img_data = np.asarray(img, dtype=np.float32) / 255.0  # Normalizar para [0, 1]
        img_data = np.transpose(img_data, (2, 0, 1))  # [H, W, C] -> [C, H, W]
        img_data = np.expand_dims(img_data, axis=0)  # [C, H, W] -> [1, C, H, W]
        return img_data
    except Exception as e:
        print(e)
        raise ValueError("Erro ao processar a imagem. Certifique-se de que o arquivo seja uma imagem válida.") from e

# Modelo de entrada da API
class PredictRequest(BaseModel):
    image_base64: str  # Imagem codificada em Base64

# Endpoint para previsão
@app.post("/predict")
async def predict(request: PredictRequest):
    try:
        # Decodificar a imagem Base64
        image_data = base64.b64decode(request.image_base64)
        
        # Verificar se a imagem foi corretamente decodificada
        if not image_data:
            raise HTTPException(status_code=400, detail="Imagem inválida. Base64 não decodificada corretamente.")
        
        # Criar um objeto BytesIO a partir dos dados decodificados
        image = io.BytesIO(image_data)
        
        # Pré-processar a imagem        
        input_data = preprocess_image(image)

        # Obter o nome da entrada
        input_name = session.get_inputs()[0].name

        # Fazer a inferência
        outputs = session.run(None, {input_name: input_data})
        predictions = outputs[0][0]  # Pegue a primeira saída (batch único)

        infected_probability = predictions[0]
        healthy_probability = predictions[1]

        # Calcular porcentagens
        infected_percentage = (np.exp(infected_probability) / (np.exp(infected_probability) + np.exp(healthy_probability))) * 100
        healthy_percentage = 100 - infected_percentage
        print("infected_percentage",infected_percentage)

        infected_percentage = float(infected_percentage)
        healthy_percentage = float(healthy_percentage)

        # Determinar a classe com maior probabilidade
        class_index = np.argmax(predictions)
        classes = ["Infectada", "Saudável"]  # Ajuste conforme necessário
        classification = classes[class_index]

        # Retornar resultado
        return JSONResponse(content={
            "classification": classification,
            "probabilities": [infected_percentage, healthy_percentage]
        })
    
    except ValueError as ve:
        print(ve)
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"Erro: {e}")
        raise HTTPException(status_code=500, detail="Erro ao processar a imagem.")
