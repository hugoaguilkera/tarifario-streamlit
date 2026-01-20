import sqlite3
import pandas as pd

DB_NAME = "tarifario.db"
EXCEL_PATH = r"C:\python\TARIFARIO\COTIZACIONES_PRUEBA.xlsx"
SHEET_NAME = "CAT_ESTADOS"

def main():
    print("📄 Leyendo CAT_ESTADOS...")
    df = pd.read_excel(EXCEL_PATH, sheet_name=SHEET_NAME)

    df.columns = (
        df.columns
        .str.strip()
        .str.upper()
        .str.replace(" ", "_")
    )

    conn = sqlite3.connect(DB_NAME)

    df.to_sql(
        "CAT_ESTADOS",
        conn,
        if_exists="replace",
        index=False
    )

    conn.close()
    print(f"✅ CAT_ESTADOS cargado ({len(df)} registros)")

if __name__ == "__main__":
    main()
