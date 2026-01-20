import requests
import sys

# Verifica que hayas escrito el nombre de la canción
if len(sys.argv) != 2:
    sys.exit("Debes escribir el nombre de la canción")

# Construye la URL para buscar en iTunes
url = "https://itunes.apple.com/search"

# Parámetros para la búsqueda
params = {
    "entity": "song",
    "limit": 1,
    "term": sys.argv[1]
}

# Hace la petición a iTunes
respuesta = requests.get(url, params=params)

# Convierte la respuesta a JSON
datos = respuesta.json()

# Verifica que haya resultados
if datos["resultCount"] == 0:
    sys.exit("No se encontró ninguna canción")

# Obtiene la información de la canción
cancion = datos["results"][0]
nombre = cancion["trackName"]
artista = cancion["artistName"]
preview_url = cancion["previewUrl"]

print(f"Descargando: {nombre} - {artista}")
print(f"Desde: {preview_url}")

# Descarga el archivo de preview (30 segundos en MP3)
audio = requests.get(preview_url)

# Guarda el archivo
archivo = nombre.replace(" ", "_") + ".mp3"

with open(archivo, "wb") as f:
    f.write(audio.content)

print(f"Archivo guardado como: {archivo}")