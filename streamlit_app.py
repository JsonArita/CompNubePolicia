import streamlit as st
import pandas as pd
import math
import os
import json

# Set Page Config
st.set_page_config(
    page_title="Estaciones Policiales Cercanas",
    page_icon="👮",
    layout="centered"
)

# Custom Premium Styling (Dark Theme & Glassmorphism Vibes)
st.markdown("""
    <style>
        /* General background adjustments */
        .stApp {
            background-color: #0f172a;
            color: #f8fafc;
        }
        /* Custom Header Badge */
        .badge {
            display: inline-block;
            background: rgba(59, 130, 246, 0.15);
            border: 1px solid rgba(59, 130, 246, 0.3);
            color: #60a5fa;
            padding: 4px 12px;
            border-radius: 50px;
            font-size: 0.85rem;
            font-weight: 600;
            text-transform: uppercase;
            margin-bottom: 15px;
        }
        /* Custom Cards */
        .station-card {
            background: rgba(30, 41, 59, 0.7);
            border: 1px solid rgba(255, 255, 255, 0.08);
            padding: 15px;
            border-radius: 12px;
            margin-bottom: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.3s ease;
        }
        .station-card:hover {
            border-color: rgba(59, 130, 246, 0.3);
            transform: translateX(5px);
            background: rgba(30, 41, 59, 0.9);
        }
        .station-name {
            font-weight: bold;
            font-size: 1.1rem;
            color: #f8fafc;
        }
        .station-coords {
            font-size: 0.85rem;
            color: #94a3b8;
            margin-top: 4px;
        }
        .station-dist {
            text-align: right;
        }
        .dist-val {
            font-size: 1.4rem;
            font-weight: 800;
            color: #10b981;
        }
        .dist-unit {
            font-size: 0.75rem;
            color: #94a3b8;
            font-weight: 600;
            text-transform: uppercase;
        }
    </style>
""", unsafe_allow_html=True)

# Haversine Distance Calculator
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# Load Stations
def load_stations():
    # Try loading from backend/stations.json
    stations_path = os.path.join("backend", "stations.json")
    if os.path.exists(stations_path):
        try:
            with open(stations_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
            
    # Default fallback list (Tegucigalpa, San Pedro Sula, Comayagua)
    return [
        { "nombre": "Estación Policial Centro (Tegucigalpa)", "lat": 14.1131, "lon": -87.1852 },
        { "nombre": "Estación Policial Norte - Belén (Tegucigalpa)", "lat": 14.1290, "lon": -87.1960 },
        { "nombre": "Estación Policial Sur - Loarque (Tegucigalpa)", "lat": 14.0720, "lon": -87.2200 },
        { "nombre": "Estación Policial Kennedy (Tegucigalpa)", "lat": 14.0880, "lon": -87.1750 },
        { "nombre": "Estación Policial El Manchén (Tegucigalpa)", "lat": 14.1120, "lon": -87.1890 },
        { "nombre": "Estación Policial Suncery (San Pedro Sula)", "lat": 15.4990, "lon": -88.0128 },
        { "nombre": "Posta Policial Estadio Olímpico (San Pedro Sula)", "lat": 15.4766, "lon": -88.0211 },
        { "nombre": "Primera Estación Policial S.O. (San Pedro Sula)", "lat": 15.4995, "lon": -88.0298 },
        { "nombre": "Estación Policial Barrio Guamilito (San Pedro Sula)", "lat": 15.5098, "lon": -88.0264 },
        { "nombre": "Jefatura de Policía - UDEP-3 (Comayagua)", "lat": 14.4612, "lon": -87.6375 },
        { "nombre": "Posta Policial La Zarcita (Comayagua)", "lat": 14.4485, "lon": -87.6292 }
    ]

# UI Header
st.markdown('<div class="badge">👮 Seguridad Ciudadana</div>', unsafe_allow_html=True)
st.title("Estaciones Policiales Más Cercanas")
st.write("Encuentra rápidamente los 3 centros de policía más cercanos ingresando tus coordenadas.")

# Sidebar / User input section
st.subheader("📍 Ingresa tu Ubicación")
col1, col2 = st.columns(2)

with col1:
    user_lat = st.number_input("Latitud", value=14.0818, format="%.6f", help="Ejemplo de Tegucigalpa: 14.0818")
with col2:
    user_lon = st.number_input("Longitud", value=-87.1921, format="%.6f", help="Ejemplo de Tegucigalpa: -87.1921")

# Quick Coordinate presets (useful for testing different cities)
st.markdown("**Presets de prueba:**")
col_tg, col_sps, col_com = st.columns(3)
if col_tg.button("Tegucigalpa (Centro)"):
    st.session_state.lat = 14.1131
    st.session_state.lon = -87.1852
if col_sps.button("San Pedro Sula"):
    st.session_state.lat = 15.4990
    st.session_state.lon = -88.0128
if col_com.button("Comayagua"):
    st.session_state.lat = 14.4612
    st.session_state.lon = -87.6375

# Sync presets with fields if clicked
if "lat" in st.session_state:
    user_lat = st.session_state.lat
    user_lon = st.session_state.lon
    # Clear state so user can manually edit afterwards
    del st.session_state.lat
    del st.session_state.lon

# Compute distances
stations = load_stations()
results = []
for s in stations:
    dist = haversine(user_lat, user_lon, s["lat"], s["lon"])
    results.append({
        "nombre": s["nombre"],
        "latitude": s["lat"],
        "longitude": s["lon"],
        "distancia_km": round(dist, 2)
    })

# Sort and get nearest 3
results_df = pd.DataFrame(results)
nearest_3 = results_df.sort_values(by="distancia_km").head(3)

# Display Results
st.markdown("---")
st.subheader("📋 Las 3 Estaciones Más Cercanas")

for idx, row in nearest_3.iterrows():
    st.markdown(f"""
        <div class="station-card">
            <div>
                <div class="station-name">{row['nombre']}</div>
                <div class="station-coords">📍 Lat: {row['latitude']} | Lon: {row['longitude']}</div>
            </div>
            <div class="station-dist">
                <span class="dist-val">{row['distancia_km']}</span> <span class="dist-unit">km</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

# Show Map
st.markdown("---")
st.subheader("🗺️ Mapa de Ubicaciones")

# Create dataframe for map showing both the user and the nearest stations
map_data = pd.DataFrame([
    {"latitude": user_lat, "longitude": user_lon, "name": "Tu Ubicación", "type": "user"}
])

# Append nearest stations
for _, row in nearest_3.iterrows():
    map_data = pd.concat([map_data, pd.DataFrame([{
        "latitude": row["latitude"],
        "longitude": row["longitude"],
        "name": row["nombre"],
        "type": "station"
    }])], ignore_index=True)

# Display Map
st.map(map_data, latitude="latitude", longitude="longitude", size=20)
st.caption("El punto central representa tu ubicación actual y los otros representan las estaciones más cercanas.")
