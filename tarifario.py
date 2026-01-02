import sqlite3
import pandas as pd

DB_NAME = "tarifario.db"
EXCEL_PATH = r"C:\python\TARIFARIO\COTIZACIONES.xlsx"
SHEET_NAME = "Tarifario estandar"

def crear_bd():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS tarifario_estandar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_tarifa TEXT,
        fecha_vigencia_ini TEXT,
        fecha_vigencia_fin TEXT,
        fecha_actualizacion TEXT,
        responsable TEXT,
        tipo_de_operacion TEXT,
        tipo_de_viaje TEXT,
        tipo_unidad TEXT,
        transportista TEXT,
        cliente TEXT,
        pais_origen TEXT,
        estado_origen TEXT,
        ciudad_origen TEXT,
        direccion_recoleccion TEXT,
        destino TEXT,
        pais_destino TEXT,
        estado_destino TEXT,
        ciudad_destino TEXT,
        destino_empresa TEXT,
        destino_direccion TEXT,
        usa_freight REAL,
        mexican_freight REAL,
        crossing REAL,
        team_driver REAL,
        peajes REAL,
        maniobras REAL,
        insurance REAL,
        aduanas_aranceles REAL,
        tarifa_viaje_sencillo REAL,
        tarifa_viaje_full REAL,
        moneda TEXT,
        all_in REAL,
        precio_viaje_sencillo REAL,
        moneda_base_sencillo TEXT,
        precio_viaje_redondo REAL,
        moneda_base_redondo TEXT,
        tarifa_viaje_redondo REAL,
        remark TEXT,
        requerimiento TEXT,
        border_crossing TEXT,
        trucking_cancel_fee REAL,
        waiting REAL,
        costo_waiting_charge REAL,
        free_time TEXT
    )
    """)

    conn.commit()
    conn.close()

def limpiar_columnas(df):
    df.columns = (
        df.columns
        .str.strip()
        .str.upper()
        .str.replace(" ", "_")
        .str.replace(".", "_")
    )
    return df

def cargar_datos():
    df = pd.read_excel(EXCEL_PATH, sheet_name=SHEET_NAME)
    df = df.dropna(how="all")
    df = limpiar_columnas(df)

    conn = sqlite3.connect(DB_NAME)
    df.to_sql("tarifario_estandar", conn, if_exists="append", index=False)
    conn.close()

    print(f"✔ {len(df)} filas cargadas")

def main():
    crear_bd()
    cargar_datos()
    print("Proceso terminado correctamente")

if __name__ == "__main__":
    main()




