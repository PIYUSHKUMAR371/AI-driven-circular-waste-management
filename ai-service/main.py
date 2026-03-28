from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import tensorflow as tf
import numpy as np
from PIL import Image
import io

# =====================================================
# 1. APP & AI MODEL INITIALIZATION
# =====================================================
app = FastAPI(title="CleanSight AI Specialist Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load your trained model
model = tf.keras.models.load_model("waste_classifier_model_v3.keras")

class_names = [
    'Bouteille_plastique', 'Brique_en_carton', 'Emballage_metallique',
    'Ordure_menagere', 'Papier_Carton', 'Verre'
]

category_mapping = {
    "Bouteille_plastique": "Recyclable",
    "Brique_en_carton": "Recyclable",
    "Emballage_metallique": "Recyclable",
    "Papier_Carton": "Biodegradable",
    "Ordure_menagere": "Hazardous",
    "Verre": "Recyclable"
}

CONFIDENCE_THRESHOLD = 0.5

# =====================================================
# 2. AI PREDICTION ENDPOINT (The only one needed)
# =====================================================
@app.post("/predict")
async def predict_waste(file: UploadFile = File(...)):
    """Classifies waste type from an uploaded image."""
    try:
        content = await file.read()
        
        # Pre-process image for the model
        img = Image.open(io.BytesIO(content)).convert("RGB").resize((224, 224))
        img_array = np.array(img).astype("float32")
        img_array = np.expand_dims(img_array, axis=0)

        # Run Prediction
        preds = model.predict(img_array)
        idx = np.argmax(preds[0])
        conf = float(preds[0][idx])

        if conf < CONFIDENCE_THRESHOLD:
            return {
                "waste_type": "Unknown",
                "category": "Uncertain",
                "confidence": round(conf, 4),
                "reward_points": 0
            }

        label = class_names[idx]
        category = category_mapping.get(label, "Other")
        
        # Simple reward logic
        points = 15 if category == "Hazardous" else (10 if category == "Recyclable" else 8)

        return {
            "waste_type": label,
            "category": category,
            "confidence": round(conf, 4),
            "reward_points": points
        }
        
    except Exception as e:
        print(f"Prediction Error: {e}")
        raise HTTPException(status_code=400, detail=f"AI Error: {str(e)}")

# Note: We removed /bins, /add-bin, and /optimize-route because 
# they are now handled by Node.js and React.
