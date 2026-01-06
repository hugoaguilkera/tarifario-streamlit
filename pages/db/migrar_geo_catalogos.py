import sqlite3
import os

DB_NAME = r"C:\MiPython\tarifario.db"

if not os.path.exists(DB_NAME):
    raise Exception(f"❌ No se encontró la base de datos en {DB_NAME}")

conn = sqlite3.connect(DB_NAME)
cur = conn.cursor()

# -----------------------------
# Validar tabla legacy
# -----------------------------
cur.execute("""
SELECT name 
FROM sqlite_master 
WHERE type='table' AND name='CAT_ESTADOS'
""")

if not cur.fetchone():
    raise Exception("❌ La tabla CAT_ESTADOS no existe en esta base de datos.")

print("✅ Tabla legacy CAT_ESTADOS encontrada.")

# -----------------------------
# 1) Migrar PAISES
# -----------------------------
cur.execute("""
INSERT OR IGNORE INTO CAT_PAISES (PAIS)
SELECT DISTINCT PAIS
FROM CAT_ESTADOS
WHERE PAIS IS NOT NULL AND TRIM(PAIS) <> ''
""")

# -----------------------------
# 2) Migrar ESTADOS
# -----------------------------
cur.execute("""
INSERT OR IGNORE INTO CAT_ESTADOS_NEW (ID_PAIS, ESTADO)
SELECT p.ID_PAIS, e.ESTADO
FROM (
    SELECT DISTINCT PAIS, ESTADO
    FROM CAT_ESTADOS
    WHERE ESTADO IS NOT NULL AND TRIM(ESTADO) <> ''
) e
JOIN CAT_PAISES p 
  ON p.PAIS = e.PAIS
""")

# -----------------------------
# 3) Migrar CIUDADES
# -----------------------------
cur.execute("""
INSERT OR IGNORE INTO CAT_CIUDADES (ID_ESTADO, CIUDAD)
SELECT en.ID_ESTADO, e.CIUDAD
FROM (
    SELECT DISTINCT PAIS, ESTADO, CIUDAD
    FROM CAT_ESTADOS
    WHERE CIUDAD IS NOT NULL AND TRIM(CIUDAD) <> ''
) e
JOIN CAT_PAISES p 
  ON p.PAIS = e.PAIS
JOIN CAT_ESTADOS_NEW en
  ON en.ESTADO = e.ESTADO
 AND en.ID_PAIS = p.ID_PAIS
""")

conn.commit()

# -----------------------------
# Validaciones finales
# -----------------------------
print("\n📊 RESULTADOS MIGRACIÓN:")
for tabla in ["CAT_PAISES", "CAT_ESTADOS_NEW", "CAT_CIUDADES"]:
    cur.execute(f"SELECT COUNT(*) FROM {tabla}")
    total = cur.fetchone()[0]
    print(f"✔ {tabla}: {total} registros")

conn.close()

print("\n✅ PASO 2 completado: migración geográfica OK.")
