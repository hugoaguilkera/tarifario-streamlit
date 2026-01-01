# import requests
# import sys
# import json

# # Validar que escribiste un término de búsqueda
# if len(sys.argv) != 2:
#     sys.exit("Debes escribir el nombre del artista o canción")

# # URL base de la API de iTunes
# url = "https://itunes.apple.com/search"

# # Parámetros de búsqueda
# params = {
#     "term": sys.argv[1],
#     "entity": "song",
#     "limit": 1
# }

# # Petición HTTP
# respuesta = requests.get(url, params=params)

# # Validar respuesta HTTP
# if respuesta.status_code != 200:
#     sys.exit(f"Error al conectar con iTunes: {respuesta.status_code}")

# # Convertir la respuesta a JSON
# datos = respuesta.json()

# # Imprimir JSON formateado como en el video
# print(json.dumps(datos, indent=4))


import requests
import sys
import json
import os

# -------------------------------------------------
# Validar que se haya escrito un término de búsqueda
# -------------------------------------------------
if len(sys.argv) != 2:
    sys.exit("Uso correcto: python itunes_pro.py 'nombre artista o canción'")

termino = sys.argv[1]

# -----------------------------
# Construir URL y parámetros API
# -----------------------------
url = "https://itunes.apple.com/search"

params = {
    "term": termino,
    "entity": "song",
    "limit": 50,   # Traemos 10 resultados
    "country": "US"
}

print(f"\nBuscando en iTunes: {termino} ...\n")

# -------------------------
# Petición HTTP con manejo
# -------------------------
try:
    respuesta = requests.get(url, params=params, timeout=5)
    respuesta.raise_for_status()
except requests.exceptions.Timeout:
    sys.exit("La petición tardó demasiado. Intente de nuevo.")
except requests.exceptions.RequestException as e:
    sys.exit(f"Error conectando con iTunes: {e}")

# -------------------------
# Procesar JSON
# -------------------------
datos = respuesta.json()

if datos.get("resultCount", 0) == 0:
    sys.exit("No se encontraron resultados.")

# Mostrar JSON completo, formateado
print("=== JSON COMPLETO ===")
print(json.dumps(datos, indent=4))
print("\n=======================\n")

# -------------------------
# Mostrar datos resumidos
# -------------------------
print("=== RESULTADOS ENCONTRADOS ===\n")

for i, result in enumerate(datos["results"], start=1):
    print(f"Canción {i}:")
    print(f"  🎵 trackName:     {result.get('trackName', 'N/A')}")
    print(f"  👤 artistName:    {result.get('artistName', 'N/A')}")
    print(f"  💿 albumName:     {result.get('collectionName', 'N/A')}")
    print(f"  🔗 previewUrl:    {result.get('previewUrl', 'N/A')}")
    print(f"  🖼️ coverArt:      {result.get('artworkUrl100', 'N/A')}")
    print("-" * 40)

# ------------------------------------
# Opción: descargar preview (30 segundos)
# ------------------------------------
primer_resultado = datos["results"][0]
preview_url = primer_resultado.get("previewUrl")

if preview_url:
    try:
        print("\nDescargando preview de 30s...")
        preview_data = requests.get(preview_url).content
        
        nombre_archivo = f"preview_{termino}.m4a"
        with open(nombre_archivo, "wb") as f:
            f.write(preview_data)
        
        print(f"Preview descargado correctamente como '{nombre_archivo}'")
    except Exception as e:
        print(f"No se pudo descargar el preview: {e}")

print("\nProceso terminado con éxito.\n")
