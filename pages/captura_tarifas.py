# =====================================================
# PANTALLA 2 - CAPTURA DE TARIFAS Y COSTOS (LIBRE)
# =====================================================

import streamlit as st
import sqlite3
import pandas as pd
import os

DB_NAME = "tarifario.db"

st.title("🟩 Captura de tarifas y costos")

# 🔴 RESET DE SESSION (usar solo para debug)
if st.button("RESET ESTADO"):
    st.session_state.clear()
    st.rerun()

# =====================================================
# BLOQUE 0.1 - CARGA SEGURA DE TARIFA EN SESSION_STATE
# =====================================================

# 🔒 Campos que vive en session_state (UI)
CAMPOS_SESSION = [
    "pais_origen","estado_origen","ciudad_origen",
    "pais_destino","estado_destino","ciudad_destino",
    "tipo_unidad",
    "precio_viaje_sencillo","precio_viaje_redondo",
    "tarifa_viaje_sencillo","tarifa_viaje_redondo","tarifa_viaje_full",
    "usa_freight","mexican_freight","crossing","border_crossing",
    "aduanas_aranceles","insurance","peajes","maniobras"
]

# 🔒 Inicialización defensiva (CRÍTICA)
for c in CAMPOS_SESSION:
    if c not in st.session_state:
        st.session_state[c] = None

# Flag de control
if "tarifa_cargada" not in st.session_state:
    st.session_state["tarifa_cargada"] = False


# 🎯 MAPEO EXPLÍCITO UI -> BD (NUNCA usar .upper())
MAPEO_SESSION_BD = {
    "pais_origen": "PAIS_ORIGEN",
    "estado_origen": "ESTADO_ORIGEN",
    "ciudad_origen": "CIUDAD_ORIGEN",
    "pais_destino": "PAIS_DESTINO",
    "estado_destino": "ESTADO_DESTINO",
    "ciudad_destino": "CIUDAD_DESTINO",
    "tipo_unidad": "TIPO_UNIDAD",
    "precio_viaje_sencillo": "PRECIO_VIAJE_SENCILLO",
    "precio_viaje_redondo": "PRECIO_VIAJE_REDONDO",
    "tarifa_viaje_sencillo": "TARIFA_VIAJE_SENCILLO",
    "tarifa_viaje_redondo": "TARIFA_VIAJE_REDONDO",
    "tarifa_viaje_full": "TARIFA_VIAJE_FULL",
    "usa_freight": "USA_FREIGHT",
    "mexican_freight": "MEXICAN_FREIGHT",
    "crossing": "CROSSING",
    "border_crossing": "BORDER_CROSSING",
    "aduanas_aranceles": "ADUANAS_ARANCELES",
    "insurance": "INSURANCE",
    "peajes": "PEAJES",
    "maniobras": "MANIOBRAS"
}

# =====================================================
# 🔄 CARGA CONTROLADA DE TARIFA (SOLO UNA VEZ)
# =====================================================
if (
    "tarifa_base_tmp" in st.session_state
    and st.session_state["tarifa_base_tmp"] is not None
    and not st.session_state["tarifa_cargada"]
):

    tarifa_base = st.session_state["tarifa_base_tmp"]

    for campo_ui, campo_bd in MAPEO_SESSION_BD.items():
        if campo_bd in tarifa_base:
            st.session_state[campo_ui] = tarifa_base[campo_bd]

    st.session_state["tarifa_cargada"] = True

else:
    tarifa_base = None

# =====================================================
# BLOQUE 0 - BUSCADOR RÁPIDO DE TARIFAS (EDICIÓN / NUEVA)
# =====================================================
st.subheader("🔍 Buscar tarifa existente para modificar")

with sqlite3.connect(DB_NAME) as conn:
    df_existentes = pd.read_sql(
        """
        SELECT
            ID_TARIFA,
            TRANSPORTISTA,
            CLIENTE,
            TIPO_UNIDAD,

            PRECIO_VIAJE_SENCILLO,
            PRECIO_VIAJE_REDONDO,
            TARIFA_VIAJE_SENCILLO,
            TARIFA_VIAJE_REDONDO,
            TARIFA_VIAJE_FULL,

            USA_FREIGHT,
            MEXICAN_FREIGHT,
            CROSSING,
            BORDER_CROSSING,
            ADUANAS_ARANCELES,
            INSURANCE,
            PEAJES,
            MANIOBRAS,

            PAIS_ORIGEN,
            ESTADO_ORIGEN,
            CIUDAD_ORIGEN,
            PAIS_DESTINO,
            ESTADO_DESTINO,
            CIUDAD_DESTINO,

            ALL_IN
        FROM tarifario_estandar
        WHERE ACTIVA = 1
          AND ID_TARIFA IS NOT NULL
        """,
        conn
    )

# ---------------- FILTROS DE BÚSQUEDA ----------------

# Filtros seguros (si no existen, se crean)
filtro_transportista = st.selectbox(
    "Filtrar por transportista",
    ["Todos"] + sorted(df_existentes["TRANSPORTISTA"].dropna().unique().tolist()),
    key="filtro_transportista"
)

filtro_cliente = st.selectbox(
    "Filtrar por cliente",
    ["Todos"] + sorted(df_existentes["CLIENTE"].dropna().unique().tolist()),
    key="filtro_cliente"
)

# Aplicar filtros
if filtro_transportista != "Todos":
    df_existentes = df_existentes[
        df_existentes["TRANSPORTISTA"] == filtro_transportista
    ]

if filtro_cliente != "Todos":
    df_existentes = df_existentes[
        df_existentes["CLIENTE"] == filtro_cliente
    ]

# Orden final
df_existentes = df_existentes.sort_values(
    ["TRANSPORTISTA", "PAIS_ORIGEN", "CIUDAD_ORIGEN"]
).reset_index(drop=True)


# ---------------- OPCIONES SELECT ----------------
opciones_tarifa = ["NUEVA"] + df_existentes["ID_TARIFA"].tolist()

tarifa_id_sel = st.selectbox(
    "Selecciona tarifa",
    opciones_tarifa,
    format_func=lambda x: (
        "➕ NUEVA TARIFA"
        if x == "NUEVA"
        else df_existentes.loc[
            df_existentes["ID_TARIFA"] == x
        ].iloc[0][
            ["TRANSPORTISTA", "CIUDAD_ORIGEN", "CIUDAD_DESTINO"]
        ].astype(str).str.cat(sep=" | ")
    ),
    key="tarifa_id_captura"
)

# ---------------- MODO NUEVA ----------------
if tarifa_id_sel == "NUEVA":
    tarifa_base = None

    # 🔒 LIMPIEZA TOTAL DE CAPTURA
    st.session_state["tarifa_base_tmp"] = None
    st.session_state["tarifa_cargada"] = False

    st.info("🆕 Modo captura de tarifa nueva")

# ---------------- MODO EDICIÓN ----------------
else:
    tarifa_base = df_existentes[
        df_existentes["ID_TARIFA"] == tarifa_id_sel
    ].iloc[0]

    # 🔐 disparador limpio para BLOQUE 0.1
    st.session_state["tarifa_base_tmp"] = tarifa_base
    st.session_state["tarifa_cargada"] = False

    st.caption(
        f"Tarifa seleccionada | Transportista: {tarifa_base['TRANSPORTISTA']} | "
        f"ALL IN: {tarifa_base['ALL_IN']}"
    )


# =====================================================
# BOTÓN - ADMINISTRAR CATÁLOGOS
# =====================================================
if st.button("🛠️ Administrar catálogos"):
    st.switch_page("pages/administrar_catalogos.py")

# =====================================================
# BLOQUE A - DATOS DEL SERVICIO
# =====================================================
conn = sqlite3.connect(DB_NAME)
st.subheader("📌 Datos del servicio")

c1, c2, c3 = st.columns(3)

tipo_operacion = c1.selectbox(
    "Tipo operación",
    pd.read_sql(
        "SELECT TIPO_OPERACION FROM CAT_TIPO_OPERACION ORDER BY TIPO_OPERACION",
        conn
    )["TIPO_OPERACION"],
    key="tipo_operacion"
)

tipo_viaje = c2.selectbox(
    "Tipo viaje",
    ["SENCILLO", "REDONDO"],
    key="tipo_viaje"
)

c3.empty()

st.caption(f"DB PATH: {os.path.abspath(DB_NAME)}")


# =====================================================
# BLOQUE B - RUTA (NORMALIZADA Y SEGURA)
# =====================================================

st.subheader("📍 Ruta")

with sqlite3.connect(DB_NAME) as conn:

    # ---------- PAÍSES ----------
    df_paises = pd.read_sql(
        "SELECT ID_PAIS, PAIS FROM CAT_PAISES WHERE ACTIVO = 1 ORDER BY PAIS",
        conn
    )

    # Normalizar
    df_paises["PAIS"] = df_paises["PAIS"].str.strip().str.upper()
    paises = df_paises["PAIS"].tolist()

    # ---------- PAÍS ORIGEN ----------
    pais_origen_prev = st.session_state.get("pais_origen")

    pais_origen = st.selectbox(
        "País origen",
        paises,
        index=paises.index(pais_origen_prev)
        if pais_origen_prev in paises
        else 0,
        key="pais_origen"
    )

    if pais_origen_prev != pais_origen and not st.session_state.get("tarifa_cargada"):
        st.session_state["estado_origen"] = None
        st.session_state["ciudad_origen"] = None

    st.session_state["pais_origen_prev"] = pais_origen

    filtro_pais_origen = df_paises.loc[
        df_paises["PAIS"] == pais_origen, "ID_PAIS"
    ]

    if filtro_pais_origen.empty:
        st.error(f"País origen no existe en catálogo: {pais_origen}")
        st.stop()

    id_pais_origen = int(filtro_pais_origen.iloc[0])

    # ---------- ESTADO ORIGEN ----------
    df_estados_origen = pd.read_sql(
        """
        SELECT ID_ESTADO, ESTADO
        FROM CAT_ESTADOS_NEW
        WHERE ID_PAIS = ? AND ACTIVO = 1
        ORDER BY ESTADO
        """,
        conn,
        params=(id_pais_origen,)
    )

    estados_origen = df_estados_origen["ESTADO"].tolist()
    estado_origen_prev = st.session_state.get("estado_origen")

    estado_origen = st.selectbox(
        "Estado origen",
        estados_origen,
        index=estados_origen.index(estado_origen_prev)
        if estado_origen_prev in estados_origen
        else 0,
        key="estado_origen"
    )

    if estado_origen_prev != estado_origen and not st.session_state.get("tarifa_cargada"):
        st.session_state["ciudad_origen"] = None

    if estado_origen in estados_origen:
        id_estado_origen = int(
            df_estados_origen.loc[
                df_estados_origen["ESTADO"] == estado_origen, "ID_ESTADO"
            ].iloc[0]
        )
    else:
        id_estado_origen = None
        st.session_state["ciudad_origen"] = None

    # ---------- CIUDAD ORIGEN ----------
    ciudad_origen = None
    if id_estado_origen is not None:
        df_ciudades_origen = pd.read_sql(
            """
            SELECT ID_CIUDAD, CIUDAD
            FROM CAT_CIUDADES
            WHERE ID_ESTADO = ? AND ACTIVO = 1
            ORDER BY CIUDAD
            """,
            conn,
            params=(id_estado_origen,)
        )

        ciudades_origen = df_ciudades_origen["CIUDAD"].tolist()
        ciudad_origen_prev = st.session_state.get("ciudad_origen")

        ciudad_origen = st.selectbox(
            "Ciudad origen",
            ciudades_origen,
            index=ciudades_origen.index(ciudad_origen_prev)
            if ciudad_origen_prev in ciudades_origen
            else 0,
            key="ciudad_origen"
        )

    st.divider()

    # ---------- PAÍS DESTINO ----------
    pais_destino_prev = st.session_state.get("pais_destino")

    pais_destino = st.selectbox(
        "País destino",
        paises,
        index=paises.index(pais_destino_prev)
        if pais_destino_prev in paises
        else 0,
        key="pais_destino"
    )

    if pais_destino_prev != pais_destino and not st.session_state.get("tarifa_cargada"):
        st.session_state["estado_destino"] = None
        st.session_state["ciudad_destino"] = None

    st.session_state["pais_destino_prev"] = pais_destino

    filtro_pais_destino = df_paises.loc[
        df_paises["PAIS"] == pais_destino, "ID_PAIS"
    ]

    if filtro_pais_destino.empty:
        st.error(f"País destino no existe en catálogo: {pais_destino}")
        st.stop()

    id_pais_destino = int(filtro_pais_destino.iloc[0])

    # ---------- ESTADO DESTINO ----------
    df_estados_destino = pd.read_sql(
        """
        SELECT ID_ESTADO, ESTADO
        FROM CAT_ESTADOS_NEW
        WHERE ID_PAIS = ? AND ACTIVO = 1
        ORDER BY ESTADO
        """,
        conn,
        params=(id_pais_destino,)
    )

    estados_destino = df_estados_destino["ESTADO"].tolist()
    estado_destino_prev = st.session_state.get("estado_destino")

    estado_destino = st.selectbox(
        "Estado destino",
        estados_destino,
        index=estados_destino.index(estado_destino_prev)
        if estado_destino_prev in estados_destino
        else 0,
        key="estado_destino"
    )

    if estado_destino in estados_destino:
        id_estado_destino = int(
            df_estados_destino.loc[
                df_estados_destino["ESTADO"] == estado_destino, "ID_ESTADO"
            ].iloc[0]
        )
    else:
        id_estado_destino = None
        st.session_state["ciudad_destino"] = None

    # ---------- CIUDAD DESTINO ----------
    ciudad_destino = None
    if id_estado_destino is not None:
        df_ciudades_destino = pd.read_sql(
            """
            SELECT ID_CIUDAD, CIUDAD
            FROM CAT_CIUDADES
            WHERE ID_ESTADO = ? AND ACTIVO = 1
            ORDER BY CIUDAD
            """,
            conn,
            params=(id_estado_destino,)
        )

        ciudades_destino = df_ciudades_destino["CIUDAD"].tolist()
        ciudad_destino_prev = st.session_state.get("ciudad_destino")

        ciudad_destino = st.selectbox(
            "Ciudad destino",
            ciudades_destino,
            index=ciudades_destino.index(ciudad_destino_prev)
            if ciudad_destino_prev in ciudades_destino
            else 0,
            key="ciudad_destino"
        )

    st.divider()

    # ---------- TIPO DE UNIDAD ----------
    df_unidades = pd.read_sql(
        "SELECT TIPO_UNIDAD FROM CAT_TIPO_UNIDAD ORDER BY TIPO_UNIDAD",
        conn
    )

    unidades = df_unidades["TIPO_UNIDAD"].tolist()
    tipo_unidad_prev = st.session_state.get("tipo_unidad")

    tipo_unidad = st.selectbox(
        "Tipo de unidad",
        unidades,
        index=unidades.index(tipo_unidad_prev)
        if tipo_unidad_prev in unidades
        else 0,
        key="tipo_unidad"
    )

# =====================================================
# BLOQUE C - DATOS COMERCIALES (SQL) ✅ ROBUSTO
# =====================================================
st.subheader("👤 Datos comerciales")

with sqlite3.connect(DB_NAME) as conn:

    col_cli, col_trp = st.columns(2)

    # ---------- CLIENTES ----------
    lista_clientes = ["SIN CLIENTE"] + pd.read_sql(
        "SELECT CLIENTE FROM CAT_CLIENTES ORDER BY CLIENTE",
        conn
    )["CLIENTE"].tolist()

    cliente_default = (
        tarifa_base["CLIENTE"]
        if tarifa_base is not None and tarifa_base["CLIENTE"] in lista_clientes
        else "SIN CLIENTE"
    )

    cliente = col_cli.selectbox(
        "Cliente",
        lista_clientes,
        index=lista_clientes.index(cliente_default),
        key="cliente"
    )

    # ---------- TRANSPORTISTAS ----------
    lista_transportistas = pd.read_sql(
        "SELECT TRANSPORTISTA FROM CAT_TRANSPORTISTAS ORDER BY TRANSPORTISTA",
        conn
    )["TRANSPORTISTA"].tolist()

    transportista_default = (
        tarifa_base["TRANSPORTISTA"]
        if tarifa_base is not None and tarifa_base["TRANSPORTISTA"] in lista_transportistas
        else lista_transportistas[0]
    )

    transportista = col_trp.selectbox(
        "Transportista",
        lista_transportistas,
        index=lista_transportistas.index(transportista_default),
        key="transportista"
    )


# =====================================================
# BLOQUE D - TARIFAS (PRECARGA CONTROLADA)
# =====================================================
st.subheader("💰 Tarifas")

c1, c2, c3 = st.columns(3)

precio_sencillo = c1.number_input(
    "Precio viaje sencillo",
    min_value=0.0,
    step=50.0,
    value=float(tarifa_base["PRECIO_VIAJE_SENCILLO"]) if tarifa_base is not None else 0.0,
    key="precio_viaje_sencillo"
)

precio_redondo = c2.number_input(
    "Precio viaje redondo",
    min_value=0.0,
    step=50.0,
    value=float(tarifa_base["PRECIO_VIAJE_REDONDO"]) if tarifa_base is not None else 0.0,
    key="precio_viaje_redondo"
)

moneda = c3.selectbox(
    "Moneda",
    ["MXN", "USD"],
    index=0 if tarifa_base is None or tarifa_base.get("MONEDA", "MXN") == "MXN" else 1,
    key="moneda"
)

# -----------------------------------------------------
# TARIFAS NEGOCIADAS
# -----------------------------------------------------
st.subheader("📑 Tarifas negociadas")

c1, c2, c3, c4 = st.columns(4)

tarifa_sencillo = c1.number_input(
    "Tarifa viaje sencillo",
    min_value=0.0,
    step=50.0,
    value=float(tarifa_base["TARIFA_VIAJE_SENCILLO"]) if tarifa_base is not None else 0.0,
    key="tarifa_viaje_sencillo"
)

tarifa_redondo = c2.number_input(
    "Tarifa viaje redondo",
    min_value=0.0,
    step=50.0,
    value=float(tarifa_base["TARIFA_VIAJE_REDONDO"]) if tarifa_base is not None else 0.0,
    key="tarifa_viaje_redondo"
)

tarifa_full = c3.number_input(
    "Tarifa full (opcional)",
    min_value=0.0,
    step=50.0,
    value=float(tarifa_base["TARIFA_VIAJE_FULL"]) if tarifa_base is not None else 0.0,
    key="tarifa_viaje_full"
)

moneda_tarifa = c4.selectbox(
    "Moneda tarifa",
    ["USD", "MXN"],
    index=0 if tarifa_base is None or tarifa_base.get("MONEDA", "USD") == "USD" else 1,
    key="moneda_tarifa"
)

# =====================================================
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
# BLOQUE E.1 - ALL IN (AUTOMÁTICO) ✅ SEGURO
# =====================================================

# 🔒 Normalización defensiva de costos
usa_freight       = float(usa_freight or 0)
mex_freight       = float(mex_freight or 0)
crossing          = float(crossing or 0)
border_crossing   = float(border_crossing or 0)
aduanas           = float(aduanas or 0)
insurance         = float(insurance or 0)
peajes            = float(peajes or 0)
maniobras         = float(maniobras or 0)

all_in = (
    usa_freight
    + mex_freight
    + crossing
    + border_crossing
    + aduanas
    + insurance
    + peajes
    + maniobras
)

st.subheader("🧮 ALL IN (Costo total automático)")
st.number_input(
    "ALL IN",
    value=all_in,
    format="%.2f",
    disabled=True
)

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

# =====================================================
# BLOQUE E.3 - VALIDACIONES DE GUARDADO ✅
# =====================================================

# 🔒 Normalizar precios y tarifas
precio_sencillo = float(precio_sencillo or 0)
precio_redondo  = float(precio_redondo or 0)
tarifa_sencillo = float(tarifa_sencillo or 0)
tarifa_redondo  = float(tarifa_redondo or 0)
all_in          = float(all_in or 0)

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
# BLOQUE E.4 - MEJOR TARIFA AUTOMÁTICA (LÓGICA REAL) ✅
# =====================================================

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
        #cargar_bd_completa.clear()
        st.session_state["df_filtrado"] = pd.DataFrame()
        st.success("✅ Tarifa guardada correctamente")

        

    


