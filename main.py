from flask import Flask, render_template_string, request
from geopy.geocoders import Nominatim
import folium

app = Flask(__name__)
geolocator = Nominatim(user_agent="route_app")

# Strona główna z formularzem
HTML_TEMPLATE = """
<!doctype html>
<html>
<head>
    <title>Optymalizacja tras</title>
</head>
<body>
    <h1>Generowanie tras dla kierowców</h1>
    <form method="POST">
        Adresy (po jednym w linii):<br>
        <textarea name="addresses" rows="10" cols="40" placeholder="Wpisz adresy tutaj, po jednym w linii"></textarea><br><br>

        Liczba kierowców: 
        <input type="number" name="num_drivers" min="1" max="10" value="1"><br><br>

        Adres startowy: 
        <input type="text" name="start_address" placeholder="ul. Ekologiczna 12, 05-080 Klaudyn"><br><br>

        <input type="submit" value="Generuj trasy">
    </form>

    {% if routes %}
        <h2>Trasy wygenerowane:</h2>
        {% for i, route in enumerate(routes, 1) %}
            <h3>Kierowca {{ i }}:</h3>
            <ul>
                {% for addr in route %}
                    <li>{{ addr }}</li>
                {% endfor %}
            </ul>
        {% endfor %}
        <h2>Mapa tras:</h2>
        <iframe src="{{ map_file }}" width="100%" height="500"></iframe>
    {% endif %}
</body>
</html>
"""

def geocode_address(address):
    location = geolocator.geocode(address)
    if location:
        return (location.latitude, location.longitude)
    return None

def split_routes(addresses, num_drivers):
    # Proste dzielenie adresów na kierowców równomiernie
    routes = [[] for _ in range(num_drivers)]
    for i, addr in enumerate(addresses):
        routes[i % num_drivers].append(addr)
    return routes

@app.route("/", methods=["GET", "POST"])
def index():
    routes = None
    map_file = None
    if request.method == "POST":
        addresses = request.form.get("addresses", "").split("\n")
        addresses = [a.strip() for a in addresses if a.strip()]

        num_drivers = int(request.form.get("num_drivers", 1))
        start_address = request.form.get("start_address", "").strip()
        if start_address:
            addresses = [start_address] + addresses

        # Podziel na trasy
        routes = split_routes(addresses, num_drivers)

        # Generuj mapę
        m = folium.Map(location=geocode_address(addresses[0]) or (52.2297, 21.0122), zoom_start=12)
        colors = ["red", "blue", "green", "purple", "orange", "darkred", "lightblue", "pink", "cadetblue", "darkgreen"]

        for idx, route in enumerate(routes):
            route_coords = []
            for addr in route:
                loc = geocode_address(addr)
                if loc:
                    route_coords.append(loc)
                    folium.Marker(loc, popup=addr, icon=folium.Icon(color=colors[idx % len(colors)])).add_to(m)
            if route_coords:
                folium.PolyLine(route_coords, color=colors[idx % len(colors)], weight=3, opacity=0.8).add_to(m)

        # Zapisz mapę do pliku
        map_file = "map.html"
        m.save(map_file)

    return render_template_string(HTML_TEMPLATE, routes=routes, map_file=map_file)

if __name__ == "__main__":
    app.run(debug=True)
