import sys

print("Archivo ejecutado:", __file__)

def main():
    if len(sys.argv) < 2:
        sys.exit("Falta el nombre")

    nombre = sys.argv[1]

    hello(nombre)
    goodbye(nombre)

def hello(name):
    print(f"hello, {name}")

def goodbye(name):
    print(f"goodbye, {name}")

if __name__ == "__main__":
    main()


