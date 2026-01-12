from flask import Flask, render_template_string, request
from geopy.geocoders import Nominatim

app = Flask(__name__)
geolocator = Nominatim(user_agent="my_app")

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Optymalizacja tras</title>
</head>
<body>
    <h2>Wprowadź adresy</h2>
    <form method="POST">
        Adresy (po jednym w linii):<br>
        <textarea name="addresses" rows="10" cols="40">{{ addresses }}</textarea><br><br>
        Liczba kierowców: <input type="number" name="drivers" min="1" value="{{ drivers }}"><br><br>
        <input type="submit" value="Generuj trasy">
    </form>

    {% if routes %}
        <h2>Trasy</h2>
        {% for i, route in enumerate(routes) %}
            <h3>Kierowca {{ i+1 }}</h3>
            <ul>
            {% for addr, coords in route %}
                <li>{{ addr }} {% if coords %} - ({{ coords[0] }}, {{ coords[1] }}){% else %} - brak współrzędnych{% endif %}</li>
            {% endfor %}
            </ul>
        {% endfor %}
    {% endif %}
</body>
</html>
"""

def get_coords(address):
    try:
        location = geolocator.geocode(address)
        if location:
            return location.latitude, location.longitude
        else:
            return None
    except Exception as e:
        print(f"Błąd geokodowania: {e}")
        return None

@app.route("/", methods=["GET", "POST"])
def index():
    routes = []
    addresses_text = ""
    drivers = 1

    if request.method == "POST":
        addresses_text = request.form.get("addresses", "")
        drivers = int(request.form.get("drivers", 1))
        addresses = [addr.strip() for addr in addresses_text.split("\n") if addr.strip()]

        # geokodowanie adresów
        coords_list = [(addr, get_coords(addr)) for addr in addresses]

        # prosty podział na trasy dla kierowców (kolejność po prostu równomiernie)
        routes = [[] for _ in range(drivers)]
        for i, item in enumerate(coords_list):
            routes[i % drivers].append(item)

    return render_template_string(HTML_PAGE, routes=routes, addresses=addresses_text, drivers=drivers)

if __name__ == "__main__":
    app.run(debug=True)
