import requests

API_KEY = "TU_API_KEY_AQUI"

def buscar_pelicula(nombre):
    url = "http://www.omdbapi.com/"
    params = {
        "t": nombre,
        "apikey": API_KEY
    }
    
    response = requests.get(url, params=params)
    datos = response.json()

    if datos["Response"] == "False":
        print("No se encontró la película.")
    else:
        print("Título:", datos["Title"])
        print("Año:", datos["Year"])
        print("Género:", datos["Genre"])
        print("Actores:", datos["Actors"])
        print("Trama:", datos["Plot"])

buscar_pelicula("Prey")

