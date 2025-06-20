
from flask import Flask, jsonify, render_template
import requests
from math import radians, sin, cos, sqrt, atan2

app = Flask(__name__)

STOP_LAT = 59.750917
STOP_LON = 30.628973

NTS_API_URL = "https://nts-admin.orgp.spb.ru/api/visary/geometry/vehicle"
BBOX = "30.6285095,59.8496436,30.5371857,59.7169451"

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/bus328")
def get_bus_328():
    try:
        params = {"transport": "bus", "bbox": BBOX}
        resp = requests.get(NTS_API_URL, params=params, timeout=5)
        vehicles = resp.json()

        buses_328 = []
        for v in vehicles:
            if v.get("route") == "328":
                buses_328.append({
                    "vehicle_id": v.get("id"),
                    "latitude": v.get("lat"),
                    "longitude": v.get("lon"),
                    "bearing": v.get("direction"),
                    "speed": v.get("speed", 20)
                })

        return jsonify(buses_328)

    except Exception as e:
        return jsonify({"error": "Ошибка получения автобусов", "details": str(e)}), 500

@app.route("/eta")
def get_eta():
    try:
        params = {"transport": "bus", "bbox": BBOX}
        resp = requests.get(NTS_API_URL, params=params, timeout=5)
        vehicles = resp.json()

        buses_328 = [v for v in vehicles if v.get("route") == "328"]

        if not buses_328:
            return jsonify({"error": "Автобус 328 не найден"})

        bus = buses_328[0]
        dist_km = haversine(bus["lat"], bus["lon"], STOP_LAT, STOP_LON)
        speed_kmh = bus.get("speed", 20) or 20
        eta_min = (dist_km / speed_kmh) * 60

        return jsonify({
            "eta_minutes": round(eta_min, 1),
            "distance_km": round(dist_km, 2),
            "speed_kmh": round(speed_kmh, 1),
            "bus_lat": bus["lat"],
            "bus_lon": bus["lon"]
        })

    except Exception as e:
        return jsonify({"error": "Ошибка обработки ETA", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10000)

