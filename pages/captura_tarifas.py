# =====================================================
# PANTALLA 2 - CAPTURA DE TARIFAS Y COSTOS (LIBRE)
# RUTAS EXISTENTES + NUEVA RUTA MANUAL
# =====================================================

import streamlit as st
import sqlite3
import pandas as pd
import os

# 🔴 RESET DE SESSION (usar UNA sola vez)
if st.button("RESET ESTADO"):
    st.session_state.clear()
    st.rerun()

DB_NAME = "tarifario.db"

st.title("🟩 Captura de tarifas y costos")

# =====================================================
# BOTÓN - ADMINISTRAR CATÁLOGOS
# =====================================================
if st.button("🛠️ Administrar catálogos"):
    st.switch_page("pages/administrar_catalogos.py")


# =====================================================
# FUNCIÓN UTILITARIA
# =====================================================
def cargar_opciones(query, params=()):
    df = pd.read_sql(query, conn, params=params)
    opciones = sorted(df.iloc[:, 0].dropna().unique())
    return opciones

# =====================================================
# BLOQUE A - DATOS DEL SERVICIO
# =====================================================

conn = sqlite3.connect(DB_NAME)
st.subheader("📌 Datos del servicio")

c1, c2, c3 = st.columns(3)

# --- Tipo de operación desde SQL ---
tipo_operacion = c1.selectbox(
    "Tipo operación",
    pd.read_sql(
        """
        SELECT TIPO_OPERACION
        FROM CAT_TIPO_OPERACION
        ORDER BY TIPO_OPERACION
        """,
        conn
    )["TIPO_OPERACION"],
    key="tipo_operacion"
)

# --- Tipo de viaje (se queda fijo por ahora) ---
tipo_viaje = c2.selectbox(
    "Tipo viaje",
    ["SENCILLO", "REDONDO"],
    key="tipo_viaje"
)

# --- Columna reservada (no tocar) ---
c3.empty()

# Debug opcional
import os
st.caption(f"DB PATH: {os.path.abspath(DB_NAME)}")


# =====================================================
# BLOQUE B - RUTA + TIPO DE UNIDAD (CATÁLOGOS)
# =====================================================

st.subheader("📍 Ruta")

conn = sqlite3.connect(DB_NAME)

# ---------- ORIGEN ----------
opciones_pais = pd.read_sql(
    """
    SELECT DISTINCT PAIS
    FROM CAT_ESTADOS
    WHERE PAIS IN ('MX', 'USA', 'CAN')
    ORDER BY PAIS
    """,
    conn
)["PAIS"].tolist()

pais_origen = st.selectbox(
    "País origen",
    opciones_pais,
    key="pais_origen"
)

# autocorrección segura
if st.session_state.get("pais_origen") not in opciones_pais:
    st.session_state["pais_origen"] = opciones_pais[0]

estado_origen = st.selectbox(
    "Estado origen",
    pd.read_sql(
        """
        SELECT DISTINCT ESTADO
        FROM CAT_ESTADOS
        WHERE PAIS = ? AND ESTADO IS NOT NULL
        ORDER BY ESTADO
        """,
        conn,
        params=(st.session_state["pais_origen"],)
    )["ESTADO"].tolist(),
    key="estado_origen"
)

ciudad_origen = st.selectbox(
    "Ciudad origen",
    pd.read_sql(
        """
        SELECT DISTINCT CIUDAD
        FROM CAT_ESTADOS
        WHERE PAIS = ? AND ESTADO = ? AND CIUDAD IS NOT NULL
        ORDER BY CIUDAD
        """,
        conn,
        params=(st.session_state["pais_origen"], st.session_state["estado_origen"])
    )["CIUDAD"].tolist(),
    key="ciudad_origen"
)

st.divider()

# ---------- DESTINO ----------
pais_destino = st.selectbox(
    "País destino",
    opciones_pais,
    key="pais_destino"
)

if st.session_state.get("pais_destino") not in opciones_pais:
    st.session_state["pais_destino"] = opciones_pais[0]

estado_destino = st.selectbox(
    "Estado destino",
    pd.read_sql(
        """
        SELECT DISTINCT ESTADO
        FROM CAT_ESTADOS
        WHERE PAIS = ? AND ESTADO IS NOT NULL
        ORDER BY ESTADO
        """,
        conn,
        params=(st.session_state["pais_destino"],)
    )["ESTADO"].tolist(),
    key="estado_destino"
)

ciudad_destino = st.selectbox(
    "Ciudad destino",
    pd.read_sql(
        """
        SELECT DISTINCT CIUDAD
        FROM CAT_ESTADOS
        WHERE PAIS = ? AND ESTADO = ? AND CIUDAD IS NOT NULL
        ORDER BY CIUDAD
        """,
        conn,
        params=(st.session_state["pais_destino"], st.session_state["estado_destino"])
    )["CIUDAD"].tolist(),
    key="ciudad_destino"
)

st.divider()

# ---------- TIPO DE UNIDAD (CATÁLOGO PLANO) ----------
df_unidades = pd.read_sql(
    "SELECT TIPO_UNIDAD FROM CAT_TIPO_UNIDAD ORDER BY TIPO_UNIDAD",
    conn
)

tipo_unidad = st.selectbox(
    "Tipo de unidad",
    df_unidades["TIPO_UNIDAD"].tolist(),
    key="tipo_unidad"
)

conn.close()

# =====================================================
# BLOQUE C - DATOS COMERCIALES (SQL)  ✅ ESTABLE
# =====================================================
st.subheader("👤 Datos comerciales")

with sqlite3.connect(DB_NAME) as conn:

    col_cli, col_trp = st.columns(2)

    cliente = col_cli.selectbox(
        "Cliente",
        pd.read_sql(
            "SELECT CLIENTE FROM CAT_CLIENTES ORDER BY CLIENTE",
            conn
        )["CLIENTE"].tolist(),
        key="cliente"
    )

    transportista = col_trp.selectbox(
        "Transportista",
        pd.read_sql(
            "SELECT TRANSPORTISTA FROM CAT_TRANSPORTISTAS ORDER BY TRANSPORTISTA",
            conn
        )["TRANSPORTISTA"].tolist(),
        key="transportista"
    )


# =====================================================
# BLOQUE D - TARIFAS
# =====================================================
st.subheader("💰 Tarifas")

c1, c2, c3 = st.columns(3)
precio_sencillo = c1.number_input("Precio viaje sencillo", min_value=0.0, step=50.0)
precio_redondo = c2.number_input("Precio viaje redondo", min_value=0.0, step=50.0)
moneda = c3.selectbox("Moneda", ["MXN", "USD"])

# =====================================================
# BLOQUE D1 - TARIFAS COMERCIALES (OBLIGATORIO)
# =====================================================
st.subheader("📑 Tarifas negociadas")

c1, c2, c3 = st.columns(3)

tarifa_sencillo = c1.number_input(
    "Tarifa viaje sencillo",
    min_value=0.0,
    step=50.0
)

tarifa_redondo = c2.number_input(
    "Tarifa viaje redondo",
    min_value=0.0,
    step=50.0
)

tarifa_full = c3.number_input(
    "Tarifa full (opcional)",
    min_value=0.0,
    step=50.0
)

# =====================================================
# BLOQUE D2 - ALL IN (MANUAL)
# =====================================================
st.subheader("🧮 ALL IN")

all_in = st.number_input(
    "ALL IN (costo total MANUAL)",
    min_value=0.0,
    step=100.0
)

# =====================================================
# BLOQUE E - COSTOS
# =====================================================
st.subheader("📦 Costos")

c1, c2, c3, c4 = st.columns(4)
usa_freight = c1.number_input("USA Freight", min_value=0.0)
mex_freight = c2.number_input("Mexican Freight", min_value=0.0)
crossing = c3.number_input("Crossing", min_value=0.0)
border_crossing = c4.number_input("Border Crossing", min_value=0.0)

c5, c6, c7, c8 = st.columns(4)
aduanas = c5.number_input("Aduanas / Aranceles", min_value=0.0)
insurance = c6.number_input("Seguro", min_value=0.0)
peajes = c7.number_input("Peajes", min_value=0.0)
maniobras = c8.number_input("Maniobras", min_value=0.0)

# =====================================================
# BLOQUE E.2 - INFORMACIÓN OPERATIVA ADICIONAL
# =====================================================

st.subheader("📝 Información operativa adicional")

c1, c2 = st.columns(2)

with c1:
    remark = st.text_area("Remark / Observaciones")
    requerimiento = st.text_area("Requerimiento especial")
    direccion_recoleccion = st.text_input("Dirección de recolección")
    destino_empresa = st.text_input("Empresa destino")

with c2:
    destino_direccion = st.text_input("Dirección destino")
    team_driver = st.checkbox("Team driver")
    waiting = st.checkbox("Waiting")
    free_time = st.number_input("Free time (horas)", min_value=0, step=1)
    costo_waiting = st.number_input("Costo waiting charge", min_value=0.0, step=100.0)
    trucking_cancel_fee = st.number_input("Trucking cancel fee", min_value=0.0, step=100.0)

st.subheader("💾 Guardar tarifa")

errores = []



if precio_sencillo == 0 and precio_redondo == 0:
    errores.append("Debes capturar al menos un PRECIO")

if all_in == 0:
    errores.append("Debes capturar el ALL IN")

if errores:
    st.error(" | ".join(errores))
    st.stop()
    # =====================================================
# SELECCIÓN DE TARIFA / PRECIO ACTIVO
# =====================================================

if tipo_viaje == "SENCILLO":
    mejor_precio = precio_sencillo
    mejor_tarifa = tarifa_sencillo
else:
    mejor_precio = precio_redondo
    mejor_tarifa = tarifa_redondo


    # Flag para mostrar mejor tarifa solo después de acción
mostrar_mejor_tarifa = st.session_state.get("mostrar_mejor_tarifa", False)

# =====================================================
# MEJOR TARIFA AUTOMÁTICA (LÓGICA REAL)
# =====================================================

if tipo_viaje == "SENCILLO":
    mejor_tarifa = tarifa_sencillo
    mejor_precio = precio_sencillo
elif tipo_viaje == "REDONDO":
    mejor_tarifa = tarifa_redondo
    mejor_precio = precio_redondo
else:
    mejor_tarifa = 0
    mejor_precio = 0

st.subheader("🏆 Mejor tarifa automática")

if tipo_viaje == "SENCILLO":
    valido = (tarifa_sencillo > 0) and (precio_sencillo > 0) and (all_in > 0)
    mejor_precio = precio_sencillo
elif tipo_viaje == "REDONDO":
    valido = (tarifa_redondo > 0) and (precio_redondo > 0) and (all_in > 0)
    mejor_precio = precio_redondo
else:
    valido = False
    mejor_precio = 0

if not valido:
    st.warning("Hay tarifas, pero no tienen precio o ALL IN.")
else:
    margen = mejor_precio - all_in
    st.success(
        f"Precio: {mejor_precio} {moneda} | "
        f"ALL IN: {all_in} | "
        f"Margen: {margen}"
    )

# ---------------- VALIDAR DUPLICADO ----------------
with sqlite3.connect(DB_NAME) as conn:
    cur = conn.cursor()

    duplicado = cur.execute("""
        SELECT COUNT(*)
        FROM tarifario_estandar
        WHERE
            TRANSPORTISTA = ?
            AND TIPO_UNIDAD = ?
            AND PAIS_ORIGEN = ?
            AND ESTADO_ORIGEN = ?
            AND CIUDAD_ORIGEN = ?
            AND PAIS_DESTINO = ?
            AND ESTADO_DESTINO = ?
            AND CIUDAD_DESTINO = ?
    """, (
        transportista,
        tipo_unidad,
        pais_origen,
        estado_origen,
        ciudad_origen,
        pais_destino,
        estado_destino,
        ciudad_destino
    )).fetchone()[0]

# ---------------- CONFIRMACIÓN ----------------
if duplicado > 0:
    st.warning(
        "⚠️ Ya existe una tarifa con el mismo proveedor y la misma ruta."
    )
    confirmar = st.checkbox("Confirmo que deseo guardar una nueva versión")
else:
    confirmar = True

# ---------------- INSERT FINAL ----------------
if st.button("💾 Guardar tarifa") and confirmar:

    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO tarifario_estandar (
                RESPONSABLE,
                TIPO_DE_OPERACION,
                TIPO_DE_VIAJE,
                TIPO_UNIDAD,
                TRANSPORTISTA,
                CLIENTE,

                PAIS_ORIGEN,
                ESTADO_ORIGEN,
                CIUDAD_ORIGEN,
                PAIS_DESTINO,
                ESTADO_DESTINO,
                CIUDAD_DESTINO,

                TARIFA_VIAJE_SENCILLO,
                TARIFA_VIAJE_REDONDO,
                TARIFA_VIAJE_FULL,

                PRECIO_VIAJE_SENCILLO,
                PRECIO_VIAJE_REDONDO,
                MONEDA,

                USA_FREIGHT,
                MEXICAN_FREIGHT,
                CROSSING,
                BORDER_CROSSING,
                ADUANAS_ARANCELES,
                INSURANCE,
                PEAJES,
                MANIOBRAS,
                ALL_IN,

                REMARK,
                REQUERIMIENTO,
                DIRECCION_DE_RECOLECCION,
                DESTINO_EMPRESA,
                DESTINO_DIRECCION,
                TEAM_DRIVER,
                WAITING,
                COSTO_DE_WAITING_CHARGE,
                FREE_TIME,
                TRUCKING_CANCEL_FEE
            )
            VALUES (?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?,
                    ?, ?, ?,
                    ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            1,  # RESPONSABLE (temporal, luego FK a CAT_USUARIOS)
            tipo_operacion,
            tipo_viaje,
            tipo_unidad,
            transportista,
            cliente,

            pais_origen,
            estado_origen,
            ciudad_origen,
            pais_destino,
            estado_destino,
            ciudad_destino,

            tarifa_sencillo,
            tarifa_redondo,
            tarifa_full,

            precio_sencillo,
            precio_redondo,
            moneda,

            usa_freight,
            mex_freight,
            crossing,
            border_crossing,
            aduanas,
            insurance,
            peajes,
            maniobras,
            all_in,

            remark,
            requerimiento,
            direccion_recoleccion,
            destino_empresa,
            destino_direccion,
            int(team_driver),
            int(waiting),
            costo_waiting,
            free_time,
            trucking_cancel_fee
        ))

        conn.commit()

    st.success("✅ Tarifa guardada correctamente")
