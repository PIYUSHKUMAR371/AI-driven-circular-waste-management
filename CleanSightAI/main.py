from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import tensorflow as tf
import numpy as np
from PIL import Image
import io
from datetime import datetime
import math
import random
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request



# =====================================================
# LOAD AI MODEL
# =====================================================
model = tf.keras.models.load_model("waste_classifier_model_v3.keras")

class_names = [
    'Bouteille_plastique',
    'Brique_en_carton',
    'Emballage_metallique',
    'Ordure_menagere',
    'Papier_Carton',
    'Verre'
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
# FASTAPI APP
# =====================================================
app = FastAPI(
    title="Smart Waste Logistics Optimization Platform",
    version="5.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# SYSTEM CONSTANTS
# =====================================================
DEPOT = (28.6130, 77.2080)
LANDFILL = (28.6500, 77.2300)

# =====================================================
# DYNAMIC BIN STORAGE
# =====================================================
bins = {}

# =====================================================
# GEO DISTANCE (HAVERSINE)
# =====================================================
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * \
        math.cos(math.radians(lat2)) * math.sin(dlon/2)**2

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# =====================================================
# CARBON CALCULATION
# =====================================================
def calculate_carbon(distance_km):
    emission_factor = 1.3
    return round(distance_km * emission_factor, 2)

# =====================================================
# AI SUSTAINABILITY LOGIC
# =====================================================
def sustainability_logic(category, confidence):

    if category == "Recyclable":
        disposal = "Place in Blue Recycling Bin"
        carbon_impact = "Recycling reduces landfill waste and lowers CO2 emissions."
        reward_points = 10

    elif category == "Biodegradable":
        disposal = "Place in Green Compost Bin"
        carbon_impact = "Composting reduces methane emissions."
        reward_points = 8

    else:
        disposal = "Dispose at Authorized Hazardous Waste Center"
        carbon_impact = "Proper disposal prevents contamination."
        reward_points = 15

    if confidence > 0.95:
        reward_points += 5

    return disposal, carbon_impact, reward_points

# =====================================================
# AI PREDICTION ENDPOINT
# =====================================================
@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        image = image.resize((224, 224))

        img_array = np.array(image).astype("float32")
        img_array = np.expand_dims(img_array, axis=0)

        predictions = model.predict(img_array)
        probabilities = predictions[0]

        predicted_index = np.argmax(probabilities)
        confidence = float(probabilities[predicted_index])

        if confidence < CONFIDENCE_THRESHOLD:
            return {
                "waste_type": "Uncertain",
                "category": "Manual Verification Required",
                "confidence": round(confidence, 4),
                "reward_points": 0
            }

        waste_type = class_names[predicted_index]
        category = category_mapping[waste_type]

        disposal, carbon_impact, reward_points = sustainability_logic(category, confidence)

        return {
            "waste_type": waste_type,
            "category": category,
            "confidence": round(confidence, 4),
            "disposal_instruction": disposal,
            "environmental_impact": carbon_impact,
            "reward_points": reward_points
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# =====================================================
# ADD BIN
# =====================================================
@app.post("/add-bin")
def add_bin(bin_id: str, latitude: float, longitude: float):

    if bin_id in bins:
        raise HTTPException(status_code=400, detail="Bin already exists")

    bins[bin_id] = {
        "fill_level": 0,
        "gas_level": 0,
        "latitude": latitude,
        "longitude": longitude,
        "last_updated": str(datetime.now())
    }

    return {
        "message": "Bin added successfully",
        "bin_data": bins[bin_id]
    }

# =====================================================
# UPDATE BIN
# =====================================================
@app.post("/update-bin")
def update_bin(bin_id: str, fill_level: int, gas_level: int):

    if bin_id not in bins:
        raise HTTPException(status_code=404, detail="Bin not found")

    bins[bin_id]["fill_level"] = fill_level
    bins[bin_id]["gas_level"] = gas_level
    bins[bin_id]["last_updated"] = str(datetime.now())

    return {
        "message": "Bin updated successfully",
        "bin_data": bins[bin_id]
    }

# =====================================================
# FASTAPI APP & MIDDLEWARE
# =====================================================
templates = Jinja2Templates(directory="templates")

@app.get("/map", response_class=HTMLResponse)
async def show_map(request: Request):
    return templates.TemplateResponse("map.html", {"request": request})

# =====================================================
# GET ALL BINS
# =====================================================
@app.get("/bins")
def get_bins():
    return {"bins": bins}

# =====================================================
# ROUTE OPTIMIZATION (UPGRADED)
# =====================================================
@app.get("/optimize-route")
def optimize_route():

    if not bins:
        return {"message": "No bins registered in the system"}

    active_bins = {
        bin_id: data
        for bin_id, data in bins.items()
        if data["fill_level"] > 80 or data["gas_level"] > 70
    }

    if not active_bins:
        return {"message": "No bins require collection"}

    # -------- OPTIMIZED ROUTE (Nearest Neighbor) --------
    remaining = active_bins.copy()
    optimized_route = []
    optimized_distance = 0

    current_lat, current_lon = DEPOT

    while remaining:
        nearest_bin = None
        shortest_distance = float("inf")

        for bin_id, data in remaining.items():
            dist = haversine(
                current_lat, current_lon,
                data["latitude"], data["longitude"]
            )

            if dist < shortest_distance:
                shortest_distance = dist
                nearest_bin = bin_id

        optimized_route.append(nearest_bin)
        optimized_distance += shortest_distance

        current_lat = remaining[nearest_bin]["latitude"]
        current_lon = remaining[nearest_bin]["longitude"]

        del remaining[nearest_bin]

    optimized_distance += haversine(
        current_lat, current_lon,
        LANDFILL[0], LANDFILL[1]
    )

    # -------- NAIVE ROUTE (Random Order) --------
    naive_route = list(active_bins.keys())
    random.shuffle(naive_route)

    naive_distance = 0
    current_lat, current_lon = DEPOT

    for bin_id in naive_route:
        bin_data = active_bins[bin_id]
        dist = haversine(
            current_lat, current_lon,
            bin_data["latitude"], bin_data["longitude"]
        )
        naive_distance += dist
        current_lat = bin_data["latitude"]
        current_lon = bin_data["longitude"]

    naive_distance += haversine(
        current_lat, current_lon,
        LANDFILL[0], LANDFILL[1]
    )

    # -------- CARBON CALCULATIONS --------
    optimized_carbon = calculate_carbon(optimized_distance)
    naive_carbon = calculate_carbon(naive_distance)

    carbon_saved = round(naive_carbon - optimized_carbon, 2)
    percent_reduction = round((carbon_saved / naive_carbon) * 100, 2) if naive_carbon > 0 else 0

    return {
        "optimized_route": optimized_route,
        "naive_route": naive_route,
        "optimized_distance_km": round(optimized_distance, 2),
        "naive_distance_km": round(naive_distance, 2),
        "optimized_carbon_kg": optimized_carbon,
        "naive_carbon_kg": naive_carbon,
        "carbon_saved_kg": carbon_saved,
        "percent_reduction": percent_reduction,
        "total_bins_collected": len(optimized_route)
    }