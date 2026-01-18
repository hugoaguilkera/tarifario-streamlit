# =====================================================
# APP STREAMLIT - TARIFARIO REAL (SQLite)
# Autor: Ingeniero Hugo + IA
# =====================================================


# =====================================================
# BLOQUE 1 - IMPORTS Y CONFIGURACIÓN
# =====================================================
import io
import sqlite3

import pandas as pd
import streamlit as st

DB_NAME = "tarifario.db"

st.set_page_config(
    page_title="Tarifario Pactra",
    layout="wide",
)


# =====================================================
# BLOQUE 2 - ESTILOS
# =====================================================
st.markdown(
    """
<style>
.card {
    background: #0b1220;
    padding: 24px;
    border-radius: 14px;
    box-shadow: 0 0 20px rgba(0,255,120,0.2);
}
.metric {
    background: #111827;
    padding: 10px;
    border-radius: 8px;
    color: white;
}
.highlight {
    color: #22c55e;
    font-weight: bold;
}
</style>
""",
    unsafe_allow_html=True,
)


# =====================================================
# BLOQUE 3 - FUNCIONES BD
# =====================================================
@st.cache_data
def cargar_bd_completa() -> pd.DataFrame:
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql("SELECT * FROM tarifario_estandar", conn)
    conn.close()
    return df


@st.cache_data
def cargar_rutas() -> pd.DataFrame:
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql(
        """
        SELECT DISTINCT
            CIUDAD_ORIGEN AS origen,
            CIUDAD_DESTINO AS destino
        FROM tarifario_estandar
        WHERE CIUDAD_ORIGEN IS NOT NULL
          AND CIUDAD_DESTINO IS NOT NULL
        ORDER BY origen, destino
    """,
        conn,
    )
    conn.close()
    return df

def refrescar_bd():
    cargar_bd_completa.clear()


# =====================================================
# BLOQUE 4 - LÓGICA DE NEGOCIO
# =====================================================
def obtener_columna_precio(tipo_operacion: str, tipo_viaje: str) -> str:
    if tipo_operacion in ["Exportación", "Importación"]:
        return "PRECIO_VIAJE_SENCILLO"
    if tipo_viaje == "REDONDO":
        return "PRECIO_VIAJE_REDONDO"
    return "PRECIO_VIAJE_SENCILLO"


def calcular_mejor_opcion(df: pd.DataFrame, col_precio: str) -> pd.Series | None:
    df_valida = df[
        df[col_precio].notna()
        & (df[col_precio] > 0)
        & df["ALL_IN"].notna()
        & (df["ALL_IN"] > 0)
    ].copy()

    if df_valida.empty:
        return None

    df_valida["PRECIO_USADO"] = df_valida[col_precio]
    df_valida["PROFIT"] = df_valida["PRECIO_USADO"] - df_valida["ALL_IN"]
    df_valida["MARGEN"] = df_valida["PROFIT"] / df_valida["PRECIO_USADO"]
    return df_valida.sort_values("ALL_IN").iloc[0]

# =====================================================
# BLOQUE 5 - FILTROS + CÁLCULO + RESULTADO (BUSCADOR REAL)
# =====================================================

if "df_filtrado" not in st.session_state:
    st.session_state["df_filtrado"] = pd.DataFrame()

if "configuracion" not in st.session_state:
    st.session_state["configuracion"] = {}

# ===============================
# CATÁLOGOS (NO tarifario)
# ===============================
with sqlite3.connect(DB_NAME) as conn:

    tipos_operacion = pd.read_sql(
        "SELECT TIPO_OPERACION FROM CAT_TIPO_OPERACION ORDER BY TIPO_OPERACION",
        conn
    )["TIPO_OPERACION"].tolist()

    tipos_viaje = ["SENCILLO", "REDONDO"]

    tipos_unidad = pd.read_sql(
        "SELECT TIPO_UNIDAD FROM CAT_TIPO_UNIDAD ORDER BY TIPO_UNIDAD",
        conn
    )["TIPO_UNIDAD"].tolist()

    paises = pd.read_sql(
        "SELECT PAIS FROM CAT_PAISES ORDER BY PAIS",
        conn
    )["PAIS"].tolist()

# ===============================
# CONFIGURACIÓN DEL SERVICIO
# ===============================
st.subheader("⚙️ Configuración del servicio")

c1, c2, c3 = st.columns(3)

with c1:
    tipo_operacion = st.selectbox("Tipo de operación", tipos_operacion)

with c2:
    tipo_viaje = st.selectbox("Tipo de viaje", tipos_viaje)

with c3:
    tipo_unidad = st.selectbox("Tipo de unidad", tipos_unidad)

# ===============================
# ORIGEN
# ===============================
st.subheader("📍 Origen")

with sqlite3.connect(DB_NAME) as conn:
    pais_origen = st.selectbox("País origen", paises)

    estados_origen = pd.read_sql(
        """
        SELECT e.ESTADO
        FROM CAT_ESTADOS_NEW e
        JOIN CAT_PAISES p ON p.ID_PAIS = e.ID_PAIS
        WHERE p.PAIS = ?
        ORDER BY e.ESTADO
        """,
        conn, params=(pais_origen,)
    )["ESTADO"].tolist()

    estado_origen = st.selectbox("Estado origen", estados_origen)

    ciudades_origen = pd.read_sql(
        """
        SELECT c.CIUDAD
        FROM CAT_CIUDADES c
        JOIN CAT_ESTADOS_NEW e ON e.ID_ESTADO = c.ID_ESTADO
        WHERE e.ESTADO = ?
        ORDER BY c.CIUDAD
        """,
        conn, params=(estado_origen,)
    )["CIUDAD"].tolist()

    ciudad_origen = st.selectbox("Ciudad origen", ciudades_origen)

# ===============================
# DESTINO
# ===============================
st.subheader("🏁 Destino")

with sqlite3.connect(DB_NAME) as conn:
    pais_destino = st.selectbox("País destino", paises)

    estados_destino = pd.read_sql(
        """
        SELECT e.ESTADO
        FROM CAT_ESTADOS_NEW e
        JOIN CAT_PAISES p ON p.ID_PAIS = e.ID_PAIS
        WHERE p.PAIS = ?
        ORDER BY e.ESTADO
        """,
        conn, params=(pais_destino,)
    )["ESTADO"].tolist()

    estado_destino = st.selectbox("Estado destino", estados_destino)

    ciudades_destino = pd.read_sql(
        """
        SELECT c.CIUDAD
        FROM CAT_CIUDADES c
        JOIN CAT_ESTADOS_NEW e ON e.ID_ESTADO = c.ID_ESTADO
        WHERE e.ESTADO = ?
        ORDER BY c.CIUDAD
        """,
        conn, params=(estado_destino,)
    )["CIUDAD"].tolist()

    ciudad_destino = st.selectbox("Ciudad destino", ciudades_destino)

# ===============================
# ACCIÓN BUSCAR
# ===============================
if st.button("🔍 Buscar tarifas"):

    df_base = cargar_bd_completa()

    with sqlite3.connect(DB_NAME) as conn:

        id_pais_origen = pd.read_sql(
            "SELECT ID_PAIS FROM CAT_PAISES WHERE PAIS = ?",
            conn, params=(pais_origen,)
        ).iloc[0, 0]

        id_estado_origen = pd.read_sql(
            """
            SELECT e.ID_ESTADO
            FROM CAT_ESTADOS_NEW e
            JOIN CAT_PAISES p ON p.ID_PAIS = e.ID_PAIS
            WHERE p.PAIS = ? AND e.ESTADO = ?
            """,
            conn, params=(pais_origen, estado_origen)
        ).iloc[0, 0]

        id_ciudad_origen = pd.read_sql(
            """
            SELECT c.ID_CIUDAD
            FROM CAT_CIUDADES c
            JOIN CAT_ESTADOS_NEW e ON e.ID_ESTADO = c.ID_ESTADO
            WHERE e.ESTADO = ? AND c.CIUDAD = ?
            """,
            conn, params=(estado_origen, ciudad_origen)
        ).iloc[0, 0]

    # ===============================
    # FILTRO REAL (ORIGEN + DESTINO)
    # ===============================
    df_filtrado = df_base[
        (df_base["TIPO_DE_OPERACION"] == tipo_operacion)
        & (df_base["TIPO_DE_VIAJE"] == tipo_viaje)
        & (df_base["TIPO_UNIDAD"] == tipo_unidad)
        & (df_base["ID_PAIS"] == id_pais_origen)
        & (df_base["ID_ESTADO"] == id_estado_origen)
        & (df_base["ID_CIUDAD"] == id_ciudad_origen)
        & (df_base["PAIS_DESTINO"] == pais_destino)
        & (df_base["ESTADO_DESTINO"] == estado_destino)
        & (df_base["CIUDAD_DESTINO"] == ciudad_destino)
    ].copy()

    st.session_state["df_filtrado"] = df_filtrado
    st.session_state["configuracion"] = {
        "tipo_operacion": tipo_operacion,
        "tipo_viaje": tipo_viaje,
        "tipo_unidad": tipo_unidad,
    }

# ===============================
# RESULTADO + MEJOR TARIFA
# ===============================
if not st.session_state["df_filtrado"].empty:
    st.divider()
    st.subheader("🏆 Mejor tarifa automática")

    config = st.session_state["configuracion"]

    col_precio = obtener_columna_precio(
        config["tipo_operacion"],
        config["tipo_viaje"]
    )

    mejor = calcular_mejor_opcion(
        st.session_state["df_filtrado"],
        col_precio
    )

    if mejor is None:
        st.warning("Hay tarifas, pero no tienen precio o ALL IN.")
    else:
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Transportista", mejor["TRANSPORTISTA"])
        c2.metric("Tipo operación", config["tipo_operacion"])
        c3.metric("Tipo viaje", config["tipo_viaje"])
        c4.metric("Precio", f"${mejor['PRECIO_USADO']:,.0f}")
        c5.metric("ALL IN", f"${mejor['ALL_IN']:,.0f}")
        st.caption(f"Margen estimado: {mejor['MARGEN']*100:.1f}%")

        with st.expander("📋 Ver todas las opciones"):
            st.dataframe(
                st.session_state["df_filtrado"],
                use_container_width=True,
                height=300
            )
else:
    st.info("Aún no hay resultados. Configura filtros y busca.")


# =====================================================
# BLOQUE 6 - VER BASE DE DATOS (GENÉRICO)
# =====================================================
st.divider()
st.subheader("📋 Base de datos completa (SQLite)")

ver_bd = st.checkbox("👁️ Ver base de datos completa", key="ver_bd_checkbox")

if ver_bd:
    df_bd = cargar_bd_completa()
    st.caption(f"Registros totales: {len(df_bd):,}")
    st.dataframe(df_bd, width="stretch", height=450)

    buffer = io.BytesIO()
    df_bd.to_excel(buffer, index=False)
    buffer.seek(0)

    st.download_button(
        "⬇ Descargar Excel",
        data=buffer,
        file_name="tarifario_completo.sqlite.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="download_bd_btn",
    )


# =====================================================
# BLOQUE 7 - TARIFARIO ESTÁNDAR (BD REAL)
# =====================================================
st.divider()
st.subheader("🗄️ Tarifario estándar (Base oficial)")

df_tarifario = cargar_bd_completa()

st.caption(f"Total de registros: {len(df_tarifario):,}")

st.dataframe(
    df_tarifario,
    width="stretch",
    height=450,
)

buffer_tarifario = io.BytesIO()
df_tarifario.to_excel(buffer_tarifario, index=False)
buffer_tarifario.seek(0)

st.download_button(
    "⬇ Descargar tarifario estándar",
    data=buffer_tarifario,
    file_name="tarifario_estandar.sqlite.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    key="download_tarifario_btn",
)


# =====================================================
# BLOQUE 8 - EXPORTAR TARIFARIO FILTRADO A EXCEL
# =====================================================
st.divider()
st.subheader("📤 Exportar tarifario filtrado")

df_export = st.session_state.get("df_filtrado", pd.DataFrame())

if not df_export.empty:
    buffer_export = io.BytesIO()
    df_export.to_excel(buffer_export, index=False)
    buffer_export.seek(0)

    st.download_button(
        label="📥 Descargar tarifario filtrado (Excel)",
        data=buffer_export,
        file_name="tarifario_filtrado.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="download_filtrado_btn",
    )
else:
    st.info("No hay datos filtrados para exportar.")
