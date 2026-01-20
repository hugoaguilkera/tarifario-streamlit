import requests
import json

def main():
    response = requests.get("https://api.artic.edu/api/v1/artworks/search")
    content = response.json()

    # Imprimir bonito
    print(json.dumps(content, indent=4, ensure_ascii=False))

main()

