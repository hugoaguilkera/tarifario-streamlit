import sys
import cowsay

# Verificar que el usuario escribió su nombre
if len(sys.argv) < 2:
    print("Debes escribir tu nombre después del archivo.")
    sys.exit()

# Capturar el nombre desde la terminal
nombre = sys.argv[1]

# Crear el mensaje
mensaje = f"Hola {nombre}, soy una vaca en Python"

# Mostrar la vaca hablando
cowsay.cow(mensaje)