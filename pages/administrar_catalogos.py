import streamlit as st
import sqlite3
import pandas as pd

DB_NAME = r"C:\MiPython\tarifario.db"

st.title("🛠️ Administración de catálogos")
st.info("Aquí se administran clientes, transportistas y futuros catálogos.")

# =====================================================
# CONEXIÓN
# =====================================================
conn = sqlite3.connect(DB_NAME)

# =====================================================
# 👤 CLIENTES
# =====================================================
st.subheader("👤 Clientes")

# --- Alta de cliente ---
nuevo_cliente = st.text_input(
    "Nuevo cliente",
    placeholder="Ej. SUNGWOO / DONGHEE / NIFCO"
)

if st.button("➕ Agregar cliente"):
    nuevo = nuevo_cliente.strip().upper()

    if nuevo == "":
        st.warning("Escribe un nombre de cliente.")
    else:
        existe = pd.read_sql(
            "SELECT 1 FROM CAT_CLIENTES WHERE CLIENTE = ?",
            conn,
            params=(nuevo,)
        )

        if not existe.empty:
            st.warning("⚠️ El cliente ya existe.")
        else:
            conn.execute(
                "INSERT INTO CAT_CLIENTES (CLIENTE, ACTIVO) VALUES (?, 1)",
                (nuevo,)
            )
            conn.commit()
            st.success("Cliente agregado correctamente.")
            st.rerun()

# --- Tabla de clientes ---
df_clientes = pd.read_sql(
    """
    SELECT CLIENTE, ACTIVO
    FROM CAT_CLIENTES
    ORDER BY CLIENTE
    """,
    conn
)
# =====================================================
# 👤 desactivar cliente
# ====================================================
st.subheader("🗑️ Desactivar cliente (confirmación)")

cliente_desactivar = st.selectbox(
    "Selecciona cliente a desactivar",
    pd.read_sql(
        "SELECT CLIENTE FROM CAT_CLIENTES WHERE ACTIVO = 1 ORDER BY CLIENTE",
        conn
    )["CLIENTE"],
    key="cliente_desactivar"
)

# --- Validar si tiene tarifas ---
tarifas = pd.read_sql(
    """
    SELECT COUNT(*) AS TOTAL
    FROM tarifario_estandar
    WHERE CLIENTE = ?
    """,
    conn,
    params=(cliente_desactivar,)
)["TOTAL"][0]

st.warning(
    f"⚠️ Este cliente tiene {tarifas} tarifa(s) registrada(s). "
    "No se borrarán, pero el cliente quedará inactivo."
)

confirmacion = st.checkbox(
    "Entiendo el impacto y deseo continuar",
    key="confirmar_desactivar_cliente"
)

if st.button("🚫 Desactivar cliente", key="btn_desactivar_cliente"):
    if not confirmacion:
        st.error("Debes confirmar antes de continuar.")
    else:
        conn.execute(
            """
            UPDATE CAT_CLIENTES
            SET ACTIVO = 0
            WHERE CLIENTE = ?
            """,
            (cliente_desactivar,)
        )
        conn.commit()
        st.success("Cliente desactivado correctamente.")
        st.rerun()

# =====================================================
# ♻️ Reactivar cliente
# =====================================================
st.subheader("♻️ Reactivar cliente")

df_clientes_inactivos = pd.read_sql(
    "SELECT CLIENTE FROM CAT_CLIENTES WHERE ACTIVO = 0 ORDER BY CLIENTE",
    conn
)

if df_clientes_inactivos.empty:
    st.info("No hay clientes inactivos.")
else:
    cliente_reactivar = st.selectbox(
        "Selecciona cliente a reactivar",
        df_clientes_inactivos["CLIENTE"],
        key="cliente_reactivar"
    )

    if st.button("✅ Reactivar cliente", key="btn_reactivar_cliente"):
        conn.execute(
            """
            UPDATE CAT_CLIENTES
            SET ACTIVO = 1
            WHERE CLIENTE = ?
            """,
            (cliente_reactivar,)
        )
        conn.commit()
        st.success("Cliente reactivado correctamente.")
        st.rerun()

st.dataframe(df_clientes, use_container_width=True)


# # =====================================================
# 🚛 TRANSPORTISTAS
# =====================================================
st.subheader("🚛 Transportistas")

nuevo_transportista = st.text_input(
    "Nuevo transportista",
    placeholder="Ej. 100 LOGISTICS / UNIMEX / ARLEX",
    key="nuevo_transportista"
)

if st.button("➕ Agregar transportista", key="btn_add_transportista"):
    nuevo = nuevo_transportista.strip().upper()

    if nuevo == "":
        st.warning("Escribe un nombre de transportista.")
    else:
        existe = pd.read_sql(
            "SELECT 1 FROM CAT_TRANSPORTISTAS WHERE TRANSPORTISTA = ?",
            conn,
            params=(nuevo,)
        )

        if not existe.empty:
            st.warning("⚠️ El transportista ya existe.")
        else:
            conn.execute(
                "INSERT INTO CAT_TRANSPORTISTAS (TRANSPORTISTA, ACTIVO) VALUES (?, 1)",
                (nuevo,)
            )
            conn.commit()
            st.success("Transportista agregado correctamente.")
            st.rerun()

# ---- Tabla de transportistas activos ----
df_transportistas = pd.read_sql(
    "SELECT TRANSPORTISTA FROM CAT_TRANSPORTISTAS WHERE ACTIVO = 1 ORDER BY TRANSPORTISTA",
    conn
)

st.dataframe(df_transportistas, use_container_width=True)

st.divider()

# =====================================================
# 🚫 Desactivar transportista
# =====================================================
st.subheader("🚫 Desactivar transportista")

transportista_off = st.selectbox(
    "Selecciona transportista a desactivar",
    df_transportistas["TRANSPORTISTA"],
    key="transportista_off"
)

if st.button("❌ Desactivar", key="btn_off_transportista"):
    conn.execute(
        "UPDATE CAT_TRANSPORTISTAS SET ACTIVO = 0 WHERE TRANSPORTISTA = ?",
        (transportista_off,)
    )
    conn.commit()
    st.success("Transportista desactivado.")
    st.rerun()
# =====================================================
# ♻️ Reactivar transportista
# =====================================================
st.subheader("♻️ Reactivar transportista")

df_transportistas_inactivos = pd.read_sql(
    "SELECT TRANSPORTISTA FROM CAT_TRANSPORTISTAS WHERE ACTIVO = 0 ORDER BY TRANSPORTISTA",
    conn
)

if df_transportistas_inactivos.empty:
    st.info("No hay transportistas inactivos.")
else:
    transportista_on = st.selectbox(
        "Selecciona transportista a reactivar",
        df_transportistas_inactivos["TRANSPORTISTA"],
        key="transportista_on"
    )

    if st.button("✅ Reactivar", key="btn_on_transportista"):
        conn.execute(
            "UPDATE CAT_TRANSPORTISTAS SET ACTIVO = 1 WHERE TRANSPORTISTA = ?",
            (transportista_on,)
        )
        conn.commit()
        st.success("Transportista reactivado.")
        st.rerun()

# =====================================================
# 📌 NOTA PROFESIONAL
# =====================================================
st.caption(
    "Este módulo es el punto único para dar de alta nuevos valores. "
    "Las pantallas de captura SOLO seleccionan."
)

# =====================================================
# ⚙️ TIPO DE OPERACIÓN
# =====================================================
st.subheader("⚙️ Tipo de operación")

nuevo_tipo_operacion = st.text_input(
    "Nuevo tipo de operación",
    placeholder="Ej. EXPORTACIÓN / IMPORTACIÓN / CROSS DOCK"
)

if st.button("➕ Agregar tipo de operación"):
    nuevo = nuevo_tipo_operacion.strip().upper()

    if nuevo == "":
        st.warning("Escribe un tipo de operación.")
    else:
        existe = pd.read_sql(
            "SELECT 1 FROM CAT_TIPO_OPERACION WHERE TIPO_OPERACION = ?",
            conn,
            params=(nuevo,)
        )

        if not existe.empty:
            st.warning("⚠️ El tipo de operación ya existe.")
        else:
            conn.execute(
                "INSERT INTO CAT_TIPO_OPERACION (TIPO_OPERACION) VALUES (?)",
                (nuevo,)
            )
            conn.commit()
            st.success("Tipo de operación agregado correctamente.")
            st.rerun()

df_tipo_operacion = pd.read_sql(
    "SELECT TIPO_OPERACION FROM CAT_TIPO_OPERACION ORDER BY TIPO_OPERACION",
    conn
)

st.dataframe(df_tipo_operacion, use_container_width=True)

st.divider()

# =====================================================
# 🚚 TIPO DE VIAJE
# =====================================================
st.subheader("🚚 Tipo de viaje")

nuevo_tipo_viaje = st.text_input(
    "Nuevo tipo de viaje",
    placeholder="Ej. SENCILLO / REDONDO / MULTI"
)

if st.button("➕ Agregar tipo de viaje"):
    nuevo = nuevo_tipo_viaje.strip().upper()

    if nuevo == "":
        st.warning("Escribe un tipo de viaje.")
    else:
        existe = pd.read_sql(
            "SELECT 1 FROM CAT_TIPO_VIAJE WHERE TIPO_VIAJE = ?",
            conn,
            params=(nuevo,)
        )

        if not existe.empty:
            st.warning("⚠️ El tipo de viaje ya existe.")
        else:
            conn.execute(
                "INSERT INTO CAT_TIPO_VIAJE (TIPO_VIAJE) VALUES (?)",
                (nuevo,)
            )
            conn.commit()
            st.success("Tipo de viaje agregado correctamente.")
            st.rerun()

df_tipo_viaje = pd.read_sql(
    "SELECT TIPO_VIAJE FROM CAT_TIPO_VIAJE ORDER BY TIPO_VIAJE",
    conn
)

st.dataframe(df_tipo_viaje, use_container_width=True)

st.divider()

# =====================================================
# 🆕 ALTA DE PAÍS / ESTADO / CIUDAD
# =====================================================
st.subheader("🆕 Alta de País / Estado / Ciudad")

# -----------------
# 🌍 Alta País
# -----------------
st.markdown("### 🌍 Nuevo país")

nuevo_pais = st.text_input("Nombre del país", placeholder="Ej. CAN / USA / MEX")

if st.button("➕ Agregar país"):
    pais = nuevo_pais.strip().upper()
    if pais == "":
        st.warning("Escribe un país.")
    else:
        existe = pd.read_sql(
            "SELECT 1 FROM CAT_PAISES WHERE PAIS = ?",
            conn,
            params=(pais,)
        )
        if not existe.empty:
            st.warning("⚠️ El país ya existe.")
        else:
            conn.execute(
                "INSERT INTO CAT_PAISES (PAIS, ACTIVO) VALUES (?, 1)",
                (pais,)
            )
            conn.commit()
            st.success("✅ País agregado.")
            st.rerun()

# -----------------
# 🗺️ Alta Estado
# -----------------
st.markdown("### 🗺️ Nuevo estado")

df_paises_all = pd.read_sql(
    "SELECT ID_PAIS, PAIS FROM CAT_PAISES WHERE ACTIVO = 1 ORDER BY PAIS",
    conn
)

pais_estado = st.selectbox(
    "País del estado",
    df_paises_all["PAIS"],
    key="pais_estado"
)

nuevo_estado = st.text_input(
    "Nombre del estado",
    placeholder="Ej. ALBERTA / TEXAS / NUEVO LEÓN"
)

if st.button("➕ Agregar estado"):
    estado = nuevo_estado.strip().upper()
    id_pais = int(
        df_paises_all.loc[df_paises_all["PAIS"] == pais_estado, "ID_PAIS"].iloc[0]
    )

    if estado == "":
        st.warning("Escribe un estado.")
    else:
        existe = pd.read_sql(
            """
            SELECT 1 FROM CAT_ESTADOS_NEW
            WHERE ESTADO = ? AND ID_PAIS = ?
            """,
            conn,
            params=(estado, id_pais)
        )

        if not existe.empty:
            st.warning("⚠️ El estado ya existe para ese país.")
        else:
            conn.execute(
                """
                INSERT INTO CAT_ESTADOS_NEW (ESTADO, ID_PAIS, ACTIVO)
                VALUES (?, ?, 1)
                """,
                (estado, id_pais)
            )
            conn.commit()
            st.success("✅ Estado agregado.")
            st.rerun()

# -----------------
# 🏙️ Alta Ciudad
# -----------------
st.markdown("### 🏙️ Nueva ciudad")

df_estados_all = pd.read_sql(
    """
    SELECT E.ID_ESTADO, E.ESTADO, P.PAIS
    FROM CAT_ESTADOS_NEW E
    JOIN CAT_PAISES P ON P.ID_PAIS = E.ID_PAIS
    WHERE E.ACTIVO = 1
    ORDER BY P.PAIS, E.ESTADO
    """,
    conn
)

estado_ciudad = st.selectbox(
    "Estado de la ciudad",
    df_estados_all["ESTADO"],
    key="estado_ciudad"
)

nueva_ciudad = st.text_input(
    "Nombre de la ciudad",
    placeholder="Ej. CALGARY / ATLANTA / MONTERREY"
)

if st.button("➕ Agregar ciudad"):
    ciudad = nueva_ciudad.strip().upper()
    id_estado = int(
        df_estados_all.loc[df_estados_all["ESTADO"] == estado_ciudad, "ID_ESTADO"].iloc[0]
    )

    if ciudad == "":
        st.warning("Escribe una ciudad.")
    else:
        existe = pd.read_sql(
            """
            SELECT 1 FROM CAT_CIUDADES
            WHERE CIUDAD = ? AND ID_ESTADO = ?
            """,
            conn,
            params=(ciudad, id_estado)
        )

        if not existe.empty:
            st.warning("⚠️ La ciudad ya existe para ese estado.")
        else:
            conn.execute(
                """
                INSERT INTO CAT_CIUDADES (CIUDAD, ID_ESTADO, ACTIVO)
                VALUES (?, ?, 1)
                """,
                (ciudad, id_estado)
            )
            conn.commit()
            st.success("✅ Ciudad agregada.")
            st.rerun()


# ============================
# 🌍 PAÍS / ESTADO / CIUDAD (NORMALIZADO)
# ============================

st.subheader("🌍 País / Estado / Ciudad")

# -------------------------------------------------
# 🌍 PAÍS
# -------------------------------------------------
df_paises = pd.read_sql(
    """
    SELECT ID_PAIS, PAIS
    FROM CAT_PAISES
    WHERE ACTIVO = 1
    ORDER BY PAIS
    """,
    conn
)

if df_paises.empty:
    st.error("❌ No hay países activos en el catálogo.")
    st.stop()

pais_sel = st.selectbox(
    "🌍 País",
    df_paises["PAIS"],
    key="pais_sel"
)

id_pais = int(
    df_paises.loc[df_paises["PAIS"] == pais_sel, "ID_PAIS"].iloc[0]
)

# -------------------------------------------------
# 🗺️ ESTADO
# -------------------------------------------------
df_estados = pd.read_sql(
    """
    SELECT ID_ESTADO, ESTADO
    FROM CAT_ESTADOS_NEW
    WHERE ID_PAIS = ?
      AND ACTIVO = 1
    ORDER BY ESTADO
    """,
    conn,
    params=(id_pais,)
)

if df_estados.empty:
    st.warning("⚠️ No hay estados registrados para este país.")
    estado_sel = None
    id_estado = None
else:
    estado_sel = st.selectbox(
        "🗺️ Estado",
        df_estados["ESTADO"],
        key="estado_sel"
    )

    id_estado = int(
        df_estados.loc[df_estados["ESTADO"] == estado_sel, "ID_ESTADO"].iloc[0]
    )

# -------------------------------------------------
# 🏙️ CIUDAD
# -------------------------------------------------
if id_estado is None:
    ciudad_sel = None
    id_ciudad = None
else:
    df_ciudades = pd.read_sql(
        """
        SELECT ID_CIUDAD, CIUDAD
        FROM CAT_CIUDADES
        WHERE ID_ESTADO = ?
          AND ACTIVO = 1
        ORDER BY CIUDAD
        """,
        conn,
        params=(id_estado,)
    )

    if df_ciudades.empty:
        st.warning("⚠️ No hay ciudades registradas para este estado.")
        ciudad_sel = None
        id_ciudad = None
    else:
        ciudad_sel = st.selectbox(
            "🏙️ Ciudad",
            df_ciudades["CIUDAD"],
            key="ciudad_sel"
        )

        id_ciudad = int(
            df_ciudades.loc[df_ciudades["CIUDAD"] == ciudad_sel, "ID_CIUDAD"].iloc[0]
        )

# =====================================================
# 🚚 TIPO DE UNIDAD
# =====================================================
st.subheader("🚚 Tipo de unidad")

nueva_unidad = st.text_input(
    "Nuevo tipo de unidad",
    placeholder="Ej. TORTON / RABON / PLATAFORMA 53 / CAJA REFRIGERADA 48"
)

if st.button("➕ Agregar tipo de unidad"):
    unidad = nueva_unidad.strip().upper()

    if unidad == "":
        st.warning("Escribe un tipo de unidad.")
    else:
        existe = pd.read_sql(
            "SELECT 1 FROM CAT_TIPO_UNIDAD WHERE TIPO_UNIDAD = ?",
            conn,
            params=(unidad,)
        )

        if not existe.empty:
            st.warning("⚠️ El tipo de unidad ya existe.")
        else:
            conn.execute(
                "INSERT INTO CAT_TIPO_UNIDAD (TIPO_UNIDAD) VALUES (?)",
                (unidad,)
            )
            conn.commit()
            st.success("Tipo de unidad agregado.")
            st.rerun()

# Mostrar catálogo
df_unidades = pd.read_sql(
    "SELECT TIPO_UNIDAD FROM CAT_TIPO_UNIDAD ORDER BY TIPO_UNIDAD",
    conn
)

st.dataframe(df_unidades, use_container_width=True)

conn.close()


