import sys
from sayings import hello

# Si escribiste exactamente 1 argumento (nombre)
if len(sys.argv) == 2:
    hello(sys.argv[1])
