♻️ AI-Driven Circular Waste Intelligence System

🚧 Prototype Project built for AI-powered Smart Waste Management and Circular Economy research.

An AI + IoT powered smart waste management prototype designed to improve waste classification, collection efficiency, and environmental sustainability.

This project demonstrates how computer vision, route optimization, and smart bin monitoring can be combined to build an intelligent waste logistics platform.

🌍 Problem Statement

Modern cities generate millions of tons of waste every year, but most waste systems suffer from:

Manual waste segregation

Inefficient garbage collection routes

Overflowing waste bins

Poor recycling rates

High carbon emissions from collection vehicles

This project proposes a Smart Waste Intelligence Platform that:

Automatically classifies waste using AI

Monitors smart bins using IoT data

Optimizes collection routes

Estimates carbon emission savings

Visualizes bin locations using interactive maps

🧠 Core Features
1️⃣ AI Waste Classification

Upload an image of waste and the AI model predicts:

Waste type

Waste category

Disposal instructions

Environmental impact

Reward points for correct disposal

Supported waste classes:

Plastic Bottle

Carton Packaging

Metal Packaging

Household Waste

Paper/Cardboard

Glass

The system categorizes waste into:

♻️ Recyclable

🌱 Biodegradable

☣️ Hazardous

2️⃣ Smart Bin Monitoring (IoT Simulation)

Each waste bin stores:

Fill Level

Gas Level

Location

Last Updated Time

Collection is triggered when:

Fill Level > 80%

Gas Level > 70%

This simulates IoT-enabled smart garbage bins.

3️⃣ Route Optimization Engine

The system calculates the most efficient collection route.

Two routes are compared:

Optimized Route

Uses a Nearest Neighbor algorithm

Naive Route

Random bin order

The system calculates:

Distance traveled

Carbon emissions

Carbon saved

This demonstrates green logistics optimization.

4️⃣ Carbon Emission Analysis

Carbon emissions are calculated using:

CO₂ = Distance × Emission Factor

The system outputs:

Optimized carbon emission

Naive carbon emission

Total carbon saved

Percentage reduction

5️⃣ Smart Waste Map

The project includes an interactive waste map built with Leaflet.js.

Features:

Waste bin location visualization

OpenStreetMap integration

Future-ready for real IoT bin data

🏗️ System Architecture
User Uploads Waste Image
          │
          ▼
FastAPI Backend
          │
          ▼
TensorFlow AI Model
(MobileNetV2)
          │
          ▼
Waste Classification
          │
          ▼
Smart Disposal Recommendation
          │
          ▼
Bin Monitoring + Route Optimization
          │
          ▼
Collection Planning + Carbon Analysis
⚙️ Technologies Used
Component	Technology
Backend API	FastAPI
AI Model	TensorFlow / Keras
Computer Vision	MobileNetV2
Data Processing	NumPy
Image Processing	PIL
Mapping	Leaflet.js
Dataset Training	TensorFlow Dataset API
📂 Project Structure
AI-Waste-Intelligence-System
│
├── main.py
│   FastAPI backend with AI prediction and routing
│
├── train.py
│   Script used to train the waste classification model
│
├── waste_classifier_model_v3.keras
│   Trained AI model
│
├── templates/
│   └── map.html
│
├── settings.json
│   Development environment settings
│
└── README.md
⚠️ Dataset Notice

The full training dataset is not included in this repository because it contains tens of thousands of images and exceeds GitHub file size limits.

However, the model was trained using a large waste classification dataset containing images of recyclable and non-recyclable materials.

If you want to retrain the model:

Download a public waste dataset such as:

TrashNet

WasteNet

TACO Dataset

Update the dataset path in:

train.py
data_dir = "path_to_dataset"
🚀 How to Run the Prototype
1️⃣ Clone the Repository
git clone https://github.com/yourusername/AI-Waste-Intelligence-System.git

cd AI-Waste-Intelligence-System
2️⃣ Install Dependencies
pip install fastapi uvicorn tensorflow pillow numpy scikit-learn
3️⃣ Run the API Server
uvicorn main:app --reload

The API will run at:

http://127.0.0.1:8000
4️⃣ Open API Documentation

FastAPI automatically generates documentation:

http://127.0.0.1:8000/docs

From here you can test:

/predict

/add-bin

/update-bin

/optimize-route

🧪 Testing the AI Model

Use the /predict endpoint.

Upload an image of waste and the API will return:

{
  "waste_type": "Bouteille_plastique",
  "category": "Recyclable",
  "confidence": 0.94,
  "disposal_instruction": "Place in Blue Recycling Bin",
  "environmental_impact": "Recycling reduces landfill waste and lowers CO2 emissions.",
  "reward_points": 10
}
🗺️ View the Smart Waste Map

Open the map endpoint:

http://127.0.0.1:8000/map

This will show the waste bin visualization map.
sorry , it seems that the map function still needs a little bit of work, and i can't do it now due to my exams, but i will do it before the final submittion 
But I can say for sure that my other functions work perfectly, they could use a good fronend tho 

🌱 Future Improvements

Possible upgrades:

Real IoT sensors for smart bins

Mobile app for citizens

Reinforcement learning route optimization

Real-time truck tracking

City-scale waste analytics dashboard

🎯 Project Vision

The goal is to create a circular waste intelligence platform that helps cities:

Reduce landfill waste

Improve recycling rates

Lower carbon emissions

Optimize garbage collection logistics

👨‍💻 Author

Piyush Kumar
Computer Science & Engineering (Data Science)

Interested in:

Artificial Intelligence

Sustainability Tech

Smart Cities

Data Science

⭐ If you like this project
