import sqlite3
import pandas as pd

DB_NAME = "tarifario.db"

# =========================
# 1) CREAR BD Y TABLAS
# =========================
def crear_bd():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.executescript("""
    CREATE TABLE IF NOT EXISTS ruta (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        origen TEXT,
        destino TEXT,
        pais TEXT,
        tipo_unidad TEXT,
        tipo_servicio TEXT,
        clave_ruta TEXT UNIQUE
    );

    CREATE TABLE IF NOT EXISTS proveedor (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT UNIQUE
    );

    CREATE TABLE IF NOT EXISTS tarifa (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ruta_id INTEGER,
        proveedor_id INTEGER,
        operacion TEXT,
        tipo_viaje TEXT,
        moneda TEXT,
        costo_total REAL,
        precio REAL
    );

    CREATE TABLE IF NOT EXISTS resultado (
        tarifa_id INTEGER PRIMARY KEY,
        profit REAL,
        margen REAL
    );
    """)

    conn.commit()
    conn.close()


# =========================
# 2) CARGA PILOTO
# =========================
def carga_piloto():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # Ruta
    cur.execute("""
    INSERT OR IGNORE INTO ruta
    (origen, destino, pais, tipo_unidad, tipo_servicio, clave_ruta)
    VALUES (?, ?, ?, ?, ?, ?)
    """, ("MTY", "GDL", "MX", "53'", "Sencillo", "MTY-GDL-MX-53-S"))

    cur.execute("SELECT id FROM ruta WHERE clave_ruta=?", ("MTY-GDL-MX-53-S",))
    ruta_id = cur.fetchone()[0]

    # Proveedores
    for p in ("A", "B"):
        cur.execute("INSERT OR IGNORE INTO proveedor (nombre) VALUES (?)", (p,))

    cur.execute("SELECT id FROM proveedor WHERE nombre='A'")
    prov_a = cur.fetchone()[0]
    cur.execute("SELECT id FROM proveedor WHERE nombre='B'")
    prov_b = cur.fetchone()[0]

    # Tarifas
    tarifas = [
        (ruta_id, prov_a, "Local", "Sencillo", "MXN", 11000, 15000),
        (ruta_id, prov_b, "Local", "Sencillo", "MXN", 10500, 15000),
    ]

    for t in tarifas:
        cur.execute("""
        INSERT INTO tarifa
        (ruta_id, proveedor_id, operacion, tipo_viaje, moneda, costo_total, precio)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, t)

    # Resultados
    cur.execute("SELECT id, costo_total, precio FROM tarifa")
    for tid, costo, precio in cur.fetchall():
        profit = precio - costo
        margen = profit / precio
        cur.execute("""
        INSERT OR REPLACE INTO resultado
        (tarifa_id, profit, margen)
        VALUES (?, ?, ?)
        """, (tid, profit, margen))

    conn.commit()
    conn.close()


# =========================
# 3) REPORTE FINAL
# =========================
def generar_reporte():
    conn = sqlite3.connect(DB_NAME)

    df = pd.read_sql_query("""
    SELECT
        r.clave_ruta AS Ruta,
        p.nombre AS Proveedor,
        t.operacion AS Operacion,
        t.tipo_viaje AS TipoViaje,
        t.moneda AS Moneda,
        t.costo_total AS Costo,
        t.precio AS Precio,
        res.profit AS Profit,
        res.margen AS Margen,
        CASE
            WHEN t.costo_total = (
                SELECT MIN(costo_total)
                FROM tarifa
                WHERE ruta_id = t.ruta_id
            ) THEN 'SI'
            ELSE 'NO'
        END AS Recomendado
    FROM tarifa t
    JOIN proveedor p ON p.id = t.proveedor_id
    JOIN ruta r ON r.id = t.ruta_id
    JOIN resultado res ON res.tarifa_id = t.id
    ORDER BY t.costo_total
    """, conn)

    conn.close()
    df.to_excel("reporte_tarifario.xlsx", index=False)
    return df


# =========================
# 4) CORREO
# =========================
def generar_correo(df):
    mejor = df[df["Recomendado"] == "SI"].iloc[0]

    correo = f"""
Buen día,

Con base en el análisis de tarifas para la ruta {mejor['Ruta']},
la opción recomendada es el proveedor {mejor['Proveedor']}
al presentar el menor costo operativo.

Resumen:
- Precio al cliente: {mejor['Precio']}
- Costo total: {mejor['Costo']}
- Margen: {round(mejor['Margen'] * 100, 2)} %

Quedamos atentos para proceder.

Saludos,
"""
    print(correo)


# =========================
# MAIN
# =========================
if __name__ == "__main__":
    crear_bd()
    carga_piloto()
    df = generar_reporte()
    generar_correo(df)
    print("Proceso terminado correctamente")
