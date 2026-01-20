#!/usr/bin/env python3
"""Programa simple de ejemplo: pide el nombre al usuario y muestra un saludo con la fecha.
"""

import datetime


def obtener_nombre():
    """Pide al usuario su nombre. Si no se escribe nada, devuelve 'Amigo'."""
    try:
        nombre = input("¿Cómo te llamas? ").strip()
    except EOFError:
        # En algunos entornos de test puede no haber stdin
        nombre = ""
    return nombre or "Amigo"


def crear_saludo(nombre: str) -> str:
    """Genera un saludo incluyendo la fecha de hoy."""
    hoy = datetime.date.today().strftime("%d/%m/%Y")
    return f"¡Hola, {nombre}! Hoy es {hoy}."


def main() -> None:
    nombre = obtener_nombre()
    saludo = crear_saludo(nombre)
    print(saludo)


if __name__ == "__main__":
    main()
