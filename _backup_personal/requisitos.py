import requests
respuesta = requests.get('https://google.com')
print(respuesta.status_code)
