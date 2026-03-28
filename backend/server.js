const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const axios = require('axios');

const app = express();
app.use(express.json());
app.use(cors());

const PORT = 5000;

// =====================================================
// 2. DATABASE CONNECTION
// =====================================================
mongoose.connect('mongodb://localhost:27017/wasteDB')
    .then(() => console.log("✅ Node Manager: Connected to MongoDB"))
    .catch(err => console.log("❌ DB Connection Error: ", err));

// =====================================================
// 3. SCHEMAS & MODELS (Smart City Data Architecture)
// =====================================================

// IoT Bin Registry
const binSchema = new mongoose.Schema({
    bin_id: String,
    latitude: Number,
    longitude: Number,
    fill_level: { type: Number, default: 0 },
    gas_level: { type: Number, default: 0 },
    last_updated: { type: Date, default: Date.now }
});
const Bin = mongoose.model('Bin', binSchema);

// Fleet Logistics Registry
const truckSchema = new mongoose.Schema({
    truck_id: String,
    driver_name: String,
    status: { type: String, enum: ['idle', 'en-route', 'collecting'], default: 'idle' },
    current_lat: { type: Number, default: 28.6130 },
    current_lon: { type: Number, default: 77.2080 },
    capacity: { type: Number, default: 1000 },
    carbon_emitted: { type: Number, default: 0 }
});
const Truck = mongoose.model('Truck', truckSchema);

// ✅ NEW: Circular Economy Ledger (Sustainability History)
const collectionLogSchema = new mongoose.Schema({
    bin_id: String,
    truck_id: String,
    weight_kg: Number,      // Simulated waste mass
    waste_type: String,     // Categorized via simulation
    co2_saved_kg: Number,   // Environmental impact calculation
    timestamp: { type: Date, default: Date.now }
});
const CollectionLog = mongoose.model('CollectionLog', collectionLogSchema);

// AI Vision Analytics
const analyticsSchema = new mongoose.Schema({
    type: String,
    timestamp: { type: Date, default: Date.now }
});
const Analytics = mongoose.model('Analytics', analyticsSchema);

// =====================================================
// 4. API ROUTES (Logistics & Governance)
// =====================================================

// --- SUSTAINABILITY & AUDIT ROUTES ---

// Fetch the last 50 collection events for the Admin Dashboard
app.get('/api/collection-history', async (req, res) => {
    try {
        const logs = await CollectionLog.find().sort({ timestamp: -1 }).limit(50);
        res.json(logs);
    } catch (err) { res.status(500).json({ error: err.message }); }
});

// --- TRUCK ROUTES ---
app.get('/api/trucks', async (req, res) => {
    try {
        const trucks = await Truck.find();
        res.json(trucks);
    } catch (err) { res.status(500).json({ message: err.message }); }
});

app.post('/api/add-truck', async (req, res) => {
    try {
        const { truck_id, driver_name, capacity } = req.body;
        const newTruck = new Truck({ truck_id, driver_name, capacity });
        await newTruck.save();
        res.status(201).json({ message: "Truck successfully added to fleet." });
    } catch (err) { res.status(500).json({ error: "Failed to onboard truck." }); }
});

// --- BIN & COLLECTION ROUTES ---
app.get('/api/bins', async (req, res) => {
    try {
        const bins = await Bin.find();
        res.json(bins);
    } catch (err) { res.status(500).json({ message: err.message }); }
});

// ✅ UPDATED: Now records data to the Sustainability Ledger automatically
app.post('/api/empty-bin', async (req, res) => {
    try {
        const { bin_id, truck_id } = req.body;
        
        // Industrial Simulation: Calculate weight and CO2 impact
        const weight = Math.floor(Math.random() * 45) + 5; // 5kg to 50kg
        const co2Impact = (weight * 0.45).toFixed(2);      // Impact coefficient
        const categories = ['Recyclable', 'Organic', 'Plastic', 'Glass'];
        
        // 1. Log the event in the Sustainability History
        const newLog = new CollectionLog({
            bin_id,
            truck_id: truck_id || "FLEET-AUTO",
            weight_kg: weight,
            waste_type: categories[Math.floor(Math.random() * categories.length)],
            co2_saved_kg: parseFloat(co2Impact)
        });
        await newLog.save();

        // 2. Reset the IoT sensor status
        await Bin.updateOne({ bin_id }, { $set: { fill_level: 0, gas_level: 0, last_updated: new Date() }});
        
        res.json({ message: `Success: Audit recorded for ${bin_id}.`, impact: newLog });
    } catch (err) { res.status(500).json({ error: err.message }); }
});

// --- AI & IOT SIMULATION ---
app.post('/api/classify', async (req, res) => {
    try {
        const pythonResponse = await axios.post('http://localhost:8000/predict', req.body);
        const { category } = pythonResponse.data;
        if (category && category !== "Uncertain") {
            await new Analytics({ type: category }).save();
        }
        res.json(pythonResponse.data);
    } catch (err) { res.status(500).json({ error: "AI Engine Offline." }); }
});

app.post('/api/simulate-iot', async (req, res) => {
    try {
        const bins = await Bin.find();
        for (let bin of bins) {
            await Bin.updateOne({ bin_id: bin.bin_id },
                { $set: { fill_level: Math.floor(Math.random() * 100), gas_level: Math.floor(Math.random() * 50), last_updated: new Date() }}
            );
        }
        res.json({ message: "IoT Simulation triggered." });
    } catch (err) { res.status(500).json({ error: err.message }); }
});

app.get('/api/analytics', async (req, res) => {
    const counts = await Analytics.aggregate([{ $group: { _id: "$type", count: { $sum: 1 } } }]);
    res.json(counts);
});

// =====================================================
// 5. SERVER STARTUP
// =====================================================
app.listen(PORT, () => {
    console.log(`🚀 CleanSight Engine running on http://localhost:${PORT}`);
});
