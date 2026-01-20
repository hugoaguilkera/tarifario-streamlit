# =====================================================
# TARIFARIO - CARGA MAESTRA DESDE EXCEL A SQLITE
# Autor: Ingeniero Hugo
# Objetivo:
# - Leer Excel REAL
# - Limpiar columnas
# - Crear tabla dinámica
# - Cargar todo sin errores
# =====================================================

import sqlite3
import pandas as pd
import os

# =====================================================
# BLOQUE 1 - CONFIGURACIÓN
# =====================================================
DB_NAME = "tarifario.db"

EXCEL_PATH = r"C:\python\TARIFARIO\COTIZACIONES_PRUEBA.xlsx"
SHEET_NAME = "Tarifario estandar"

TABLE_NAME = "tarifario_estandar"


# =====================================================
# BLOQUE 2 - UTILIDADES
# =====================================================
def limpiar_columnas(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = (
        df.columns
        .str.strip()
        .str.upper()
        .str.replace(" ", "_")
        .str.replace(".", "_")
        .str.replace("/", "_")
    )
    return df


def mapear_tipo_sqlite(dtype) -> str:
    if "int" in str(dtype):
        return "INTEGER"
    if "float" in str(dtype):
        return "REAL"
    return "TEXT"


# =====================================================
# BLOQUE 3 - BASE DE DATOS
# =====================================================
def recrear_tabla(conn, df: pd.DataFrame):
    cur = conn.cursor()

    cur.execute(f"DROP TABLE IF EXISTS {TABLE_NAME}")

    columnas_sql = []
    for col, dtype in df.dtypes.items():
        tipo = mapear_tipo_sqlite(dtype)
        columnas_sql.append(f'"{col}" {tipo}')

    sql_create = f"""
    CREATE TABLE {TABLE_NAME} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        {", ".join(columnas_sql)}
    )
    """

    cur.execute(sql_create)
    conn.commit()
    print("✔ Tabla recreada dinámicamente")


# =====================================================
# BLOQUE 4 - CARGA DE DATOS
# =====================================================
def cargar_datos():
    if not os.path.exists(EXCEL_PATH):
        raise FileNotFoundError(f"No existe el archivo: {EXCEL_PATH}")

    print("📄 Leyendo Excel...")
    df = pd.read_excel(EXCEL_PATH, sheet_name=SHEET_NAME)
    df = df.dropna(how="all")
    df = limpiar_columnas(df)

    conn = sqlite3.connect(DB_NAME)

    recrear_tabla(conn, df)

    print("⬆ Cargando datos a SQLite...")
    df.to_sql(TABLE_NAME, conn, if_exists="append", index=False)

    conn.close()
    print(f"✔ {len(df)} registros cargados correctamente")


# =====================================================
# BLOQUE 5 - MAIN
# =====================================================
def main():
    cargar_datos()
    print("✅ PROCESO TERMINADO SIN ERRORES")


if __name__ == "__main__":
    main()

# =====================================================
# BLOQUE 6 - FILTROS PROFESIONALES ORIGEN / DESTINO
# Autor: Ingeniero Hugo + IA
# Objetivo:
# Construir filtros en cascada (País → Estado → Ciudad)
# leyendo 100% desde SQLite (tabla CAT_ESTADOS)
# =====================================================

# =========================
# FUNCIONES DE CATÁLOGOS
# =========================

@st.cache_data(show_spinner=False)
def obtener_paises():
    """
    Devuelve la lista de países únicos desde CAT_ESTADOS.
    """
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql(
        """
        SELECT DISTINCT PAIS
        FROM CAT_ESTADOS
        WHERE PAIS IS NOT NULL
        ORDER BY PAIS
        """,
        conn
    )
    conn.close()
    return df["PAIS"].tolist()


@st.cache_data(show_spinner=False)
def obtener_estados(pais: str):
    """
    Devuelve los estados filtrados por país.
    """
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql(
        """
        SELECT DISTINCT ESTADO
        FROM CAT_ESTADOS
        WHERE PAIS = ?
          AND ESTADO IS NOT NULL
        ORDER BY ESTADO
        """,
        conn,
        params=(pais,)
    )
    conn.close()
    return df["ESTADO"].tolist()


@st.cache_data(show_spinner=False)
def obtener_ciudades(pais: str, estado: str):
    """
    Devuelve las ciudades filtradas por país y estado.
    """
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql(
        """
        SELECT DISTINCT CIUDAD
        FROM CAT_ESTADOS
        WHERE PAIS = ?
          AND ESTADO = ?
          AND CIUDAD IS NOT NULL
        ORDER BY CIUDAD
        """,
        conn,
        params=(pais, estado)
    )
    conn.close()
    return df["CIUDAD"].tolist()


# =========================
# UI - SECCIÓN ORIGEN
# =========================

st.markdown("## 📍 Origen")

pais_origen = st.selectbox(
    "País de origen",
    obtener_paises(),
    key="filtro_pais_origen"
)

estado_origen = st.selectbox(
    "Estado de origen",
    obtener_estados(pais_origen),
    key="filtro_estado_origen"
)

ciudad_origen = st.selectbox(
    "Ciudad de origen",
    obtener_ciudades(pais_origen, estado_origen),
    key="filtro_ciudad_origen"
)


# =========================
# UI - SECCIÓN DESTINO
# =========================

st.markdown("## 🏁 Destino")

pais_destino = st.selectbox(
    "País de destino",
    obtener_paises(),
    key="filtro_pais_destino"
)

estado_destino = st.selectbox(
    "Estado de destino",
    obtener_estados(pais_destino),
    key="filtro_estado_destino"
)

ciudad_destino = st.selectbox(
    "Ciudad de destino",
    obtener_ciudades(pais_destino, estado_destino),
    key="filtro_ciudad_destino"
)


# =========================
# DEBUG CONTROLADO (OPCIONAL)
# =========================
with st.expander("🔎 Ver selección actual"):
    st.write({
        "origen": {
            "pais": pais_origen,
            "estado": estado_origen,
            "ciudad": ciudad_origen
        },
        "destino": {
            "pais": pais_destino,
            "estado": estado_destino,
            "ciudad": ciudad_destino
        }
    })