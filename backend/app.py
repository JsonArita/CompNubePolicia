import os
import json
import math
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes to allow frontend integration

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points
    on the Earth's surface in kilometers using the Haversine formula.
    """
    R = 6371.0  # Earth's radius in kilometers

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# Load station data from stations.json
def load_stations():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    stations_path = os.path.join(base_dir, 'stations.json')
    try:
        with open(stations_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return [
            {"nombre": "Estación Policial Centro (Tegucigalpa)", "lat": 14.1131, "lon": -87.1852},
            {"nombre": "Estación Policial Norte - Belén (Tegucigalpa)", "lat": 14.1290, "lon": -87.1960},
            {"nombre": "Estación Policial Sur - Loarque (Tegucigalpa)", "lat": 14.0720, "lon": -87.2200},
            {"nombre": "Estación Policial Kennedy (Tegucigalpa)", "lat": 14.0880, "lon": -87.1750},
            {"nombre": "Estación Policial El Manchén (Tegucigalpa)", "lat": 14.1120, "lon": -87.1890},
            {"nombre": "Estación Policial Suncery (San Pedro Sula)", "lat": 15.4990, "lon": -88.0128},
            {"nombre": "Posta Policial Estadio Olímpico (San Pedro Sula)", "lat": 15.4766, "lon": -88.0211},
            {"nombre": "Primera Estación Policial S.O. (San Pedro Sula)", "lat": 15.4995, "lon": -88.0298},
            {"nombre": "Estación Policial Barrio Guamilito (San Pedro Sula)", "lat": 15.5098, "lon": -88.0264},
            {"nombre": "Jefatura de Policía - UDEP-3 (Comayagua)", "lat": 14.4612, "lon": -87.6375},
            {"nombre": "Posta Policial La Zarcita (Comayagua)", "lat": 14.4485, "lon": -87.6292}
        ]

@app.route('/estaciones', methods=['GET'])
def get_nearest_stations():
    # Retrieve query parameters
    try:
        user_lat = float(request.args.get('lat'))
        user_lon = float(request.args.get('lon'))
    except (TypeError, ValueError):
        return jsonify({"error": "Parámetros 'lat' y 'lon' son requeridos y deben ser numéricos."}), 400

    limite = request.args.get('limite', default=3)
    try:
        limite = int(limite)
    except ValueError:
        limite = 3

    stations = load_stations()
    results = []

    for station in stations:
        dist = haversine(user_lat, user_lon, station['lat'], station['lon'])
        results.append({
            "nombre": station['nombre'],
            "lat": station['lat'],
            "lon": station['lon'],
            "distancia_km": round(dist, 2)
        })

    # Sort stations by distance ascending
    results.sort(key=lambda x: x['distancia_km'])

    # Return only the requested number of stations
    return jsonify(results[:limite])

if __name__ == '__main__':
    # Bind to 0.0.0.0 and use environment port to support cloud deployment (e.g. Render)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
