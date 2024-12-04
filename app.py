from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
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

# Carregar o modelo ONNX
session = ort.InferenceSession(model_path)

# Função para pré-processar a imagem
def preprocess_image(image):
    img = Image.open(image).convert("RGB")
    img = img.resize((224, 224))  # Redimensionar para 224x224
    img_data = np.asarray(img, dtype=np.float32) / 255.0  # Normalizar para [0, 1]
    img_data = np.transpose(img_data, (2, 0, 1))  # [H, W, C] -> [C, H, W]
    img_data = np.expand_dims(img_data, axis=0)  # [C, H, W] -> [1, C, H, W]
    return img_data

# Modelo de entrada da API
class PredictRequest(BaseModel):
    image_base64: str  # Imagem codificada em Base64

# Endpoint para previsão
@app.post("/predict")
async def predict(request: PredictRequest):
    try:
        # Decodificar a imagem Base64
        image_data = base64.b64decode(request.image_base64)
        image = io.BytesIO(image_data)

        # Pré-processar a imagem
        input_data = preprocess_image(image)

        # Obter o nome da entrada
        input_name = session.get_inputs()[0].name

        # Fazer a inferência
        outputs = session.run(None, {input_name: input_data})
        predictions = outputs[0][0]  # Pegue a primeira saída (batch único)

        # Determinar a classe com maior probabilidade
        class_index = np.argmax(predictions)
        classes = ["Infectada", "Saudável"]  # Ajuste conforme necessário
        classification = classes[class_index]

        # Retornar resultado
        return JSONResponse(content={
            "classification": classification,
            "probabilities": predictions.tolist()
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
