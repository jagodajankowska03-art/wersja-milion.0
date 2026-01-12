from flask import Flask, request, render_template_string
from geopy.geocoders import Nominatim
import folium
import math

app = Flask(__name__)

def split_addresses(coords, num_drivers):
    """
    Prosty algorytm dzielenia punktów na kierowców.
    Zwraca listę list współrzędnych dla każdego kierowcy.
    """
    driver_routes = [[] for _ in range(num_drivers)]
    for i, coord in enumerate(coords):
        driver_routes[i % num_drivers].append(coord)
    return driver_routes

@app.route('/', methods=['GET', 'POST'])
def index():
    mapa_html = ""
    if request.method == 'POST':
        start_address = request.form.get('start', '')
        addresses = request.form.get('addresses', '').split('\n')
        num_drivers = int(request.form.get('drivers', 1))

        geolocator = Nominatim(user_agent="multi_driver_app")

        try:
            # Współrzędne startu
            start_loc = geolocator.geocode(start_address)
            start_coords = (start_loc.latitude, start_loc.longitude)

            # Współrzędne punktów
            coords = []
            for addr in addresses:
                loc = geolocator.geocode(addr.strip())
                if loc:
                    coords.append((loc.latitude, loc.longitude))

            # Dzielimy punkty na kierowców
            routes = split_addresses(coords, num_drivers)

            # Tworzymy mapę Folium
            m = folium.Map(location=start_coords, zoom_start=12)
            folium.Marker(start_coords, tooltip="Start", icon=folium.Icon(color='green')).add_to(m)

            colors = ["blue", "red", "orange", "purple", "darkgreen", "darkred", "cadetblue"]
            for i, route in enumerate(routes):
                # Dodajemy punkty i linię trasy
                if route:
                    folium.Marker(route[0], tooltip=f"Kierowca {i+1} start", icon=folium.Icon(color=colors[i % len(colors)])).add_to(m)
                    folium.PolyLine([start_coords]+route, color=colors[i % len(colors)], weight=2.5).add_to(m)
                    for j, c in enumerate(route):
                        folium.Marker(c, tooltip=f"K{i+1}-P{j+1}").add_to(m)

            mapa_html = m._repr_html_()
        except Exception as e:
            mapa_html = f"<p>Błąd: {e}</p>"

    return render_template_string('''
        <h2>Optymalizacja tras dla wielu kierowców</h2>
        <form method="post">
            Adres startowy: <input type="text" name="start" value="ul.Ekologiczna 12, 05-080 Klaudyn"><br><br>
            Adresy (po jednym w linii):<br>
            <textarea name="addresses" rows="10" cols="40">ul. Marszałkowska 1, Warszawa
ul. Puławska 15, Warszawa
ul. Grzybowska 2, Warszawa
ul. Polna 7, Warszawa
ul. Nowowiejska 8, Warszawa</textarea><br><br>
            Liczba kierowców: <input type="number" name="drivers" value="2" min="1" max="5"><br><br>
            <input type="submit" value="Generuj trasy">
        </form>
        <hr>
        {{ mapa_html|safe }}
    ''', mapa_html=mapa_html)

if __name__ == "__main__":
    app.run(debug=True)
