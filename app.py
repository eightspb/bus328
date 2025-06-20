from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

NTS_API_URL = "https://nts-admin.orgp.spb.ru/api/visary/geometry/vehicle"
PROXY = {
    "http": "http://149.154.67.34:3128",
    "https": "http://149.154.67.34:3128"
}

@app.route('/bus328')
def get_bus_328():
    bbox = "30.6285095,59.8496436,30.5371857,59.7169451"
    params = {
        "transport": "bus",
        "bbox": bbox
    }

    try:
        resp = requests.get(NTS_API_URL, params=params, proxies=PROXY, timeout=10)
        vehicles = resp.json()

        buses_328 = [
            v for v in vehicles
            if "328" in str(v.get("route", "")).lower()
        ]

        return jsonify(buses_328)

    except Exception as e:
        return jsonify({"error": "Ошибка получения автобусов", "details": str(e)}), 500

@app.route('/eta')
def eta():
    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)
    if not lat or not lon:
        return jsonify({"error": "Неверные координаты"}), 400

    # Тут можно позже добавить ETA по формуле расстояния
    return jsonify({"eta": "Загрузка времён прибытия..."})

@app.route('/')
def index():
    return open("templates/index.html").read()

if __name__ == '__main__':
    app.run(debug=True)
