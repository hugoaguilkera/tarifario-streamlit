import cowsay
import sys

# Si escribiste exactamente un nombre después del archivo
if len(sys.argv) == 2:
    cowsay.trex("hola, " + sys.argv[1])
