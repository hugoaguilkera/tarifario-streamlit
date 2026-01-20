import requests

grupo = "Shakira"   # Puedes cambiar el nombre del grupo
url = f"https://itunes.apple.com/search?term={grupo}&entity=song&limit=20"

respuesta = requests.get(url).json()

print(f"Lista de canciones de {grupo}:\n")

for item in respuesta["results"]:
    print("-", item["trackName"])
