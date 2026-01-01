

import sys
#print("ARCHIVO CORRECTO")
#print(__file__)

 # Si no pasaste al menos un argumento (además del archivo)
if len(sys.argv) < 2:
     sys.exit("Muy pocos argumentos")
 # Recorre TODOS los argumentos, incluyendo el archivo
for argumento in sys.argv:
     print("hola, mi nombre es", argumento)

#import sys

# Si no pasaste al menos un argumento (además del archivo)
#if len(sys.argv) < 2:
#    sys.exit("Muy pocos argumentos")

# Recorre SOLO los argumentos, ignorando el archivo
#for argumento in sys.argv[1:]:
 #   print("hola, mi nombre es", argumento)

