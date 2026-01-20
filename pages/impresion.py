import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime


# ===============================
# CONFIG
# ===============================
DB = "tarifario.db"
TABLA = "tarifario_estandar"

st.set_page_config(page_title="Impresión de Tarifas", layout="wide")
st.title("🖨️ Impresión de Tarifas")
st.success("Pantalla de impresión cargada")

# ===============================
# CONEXIÓN BD
# ===============================
conn = sqlite3.connect(DB)

# ===============================
# COLUMNAS BASE
# ===============================
COL_CLIENTE   = "CLIENTE"
COL_CLAVE     = "ID_TARIFA"
COL_UNIDAD    = "TIPO_UNIDAD"
COL_VIAJE     = "TIPO_DE_VIAJE"
COL_OPERACION = "TIPO_DE_OPERACION"
COL_TRP       = "TRANSPORTISTA"

COL_PAIS_O    = "PAIS_ORIGEN"
COL_ESTADO_O  = "ESTADO_ORIGEN"
COL_CIUDAD_O  = "CIUDAD_ORIGEN"

COL_PAIS_D    = "PAIS_DESTINO"
COL_ESTADO_D  = "ESTADO_DESTINO"
COL_CIUDAD_D  = "CIUDAD_DESTINO"

COL_ALLIN     = "ALL_IN"

# ===============================
# FUNCIONES
# ===============================
def distinct(col):
    return (
        pd.read_sql(f"SELECT DISTINCT {col} FROM {TABLA}", conn)[col]
        .dropna()
        .tolist()
    )

def get_val(row, *cols):
    for c in cols:
        if c in row.index:
            return row[c]
    return ""

# ===============================
# BUSCADOR
# ===============================
st.subheader("🔎 Buscador de tarifas")

clientes    = distinct(COL_CLIENTE)
claves      = distinct(COL_CLAVE)
unidades    = distinct(COL_UNIDAD)
viajes      = distinct(COL_VIAJE)
operaciones = distinct(COL_OPERACION)
trps        = distinct(COL_TRP)

c1, c2, c3, c4, c5, c6 = st.columns(6)
cliente   = c1.selectbox("Cliente", ["Todos"] + clientes)
clave     = c2.selectbox("Clave", ["Todas"] + claves)
unidad    = c3.selectbox("Unidad", ["Todas"] + unidades)
viaje     = c4.selectbox("Viaje", ["Todos"] + viajes)
operacion = c5.selectbox("Operación", ["Todas"] + operaciones)
trp       = c6.selectbox("Transportista", ["Todos"] + trps)

st.markdown("**Ruta**")

paises_o   = distinct(COL_PAIS_O)
estados_o  = distinct(COL_ESTADO_O)
ciudades_o = distinct(COL_CIUDAD_O)

paises_d   = distinct(COL_PAIS_D)
estados_d  = distinct(COL_ESTADO_D)
ciudades_d = distinct(COL_CIUDAD_D)

o1, o2, o3, d1, d2, d3 = st.columns(6)
pais_o   = o1.selectbox("País O", ["Todos"] + paises_o)
estado_o = o2.selectbox("Estado O", ["Todos"] + estados_o)
ciudad_o = o3.selectbox("Ciudad O", ["Todos"] + ciudades_o)

pais_d   = d1.selectbox("País D", ["Todos"] + paises_d)
estado_d = d2.selectbox("Estado D", ["Todos"] + estados_d)
ciudad_d = d3.selectbox("Ciudad D", ["Todos"] + ciudades_d)

# ===============================
# QUERY
# ===============================
query = f"SELECT * FROM {TABLA} WHERE 1=1"
params = []

def add(col, val, todos="Todos"):
    global query, params
    if val != todos:
        query += f" AND {col}=?"
        params.append(val)

add(COL_CLIENTE, cliente)
add(COL_CLAVE, clave, "Todas")
add(COL_UNIDAD, unidad, "Todas")
add(COL_VIAJE, viaje)
add(COL_OPERACION, operacion, "Todas")
add(COL_TRP, trp)

add(COL_PAIS_O, pais_o)
add(COL_ESTADO_O, estado_o)
add(COL_CIUDAD_O, ciudad_o)

add(COL_PAIS_D, pais_d)
add(COL_ESTADO_D, estado_d)
add(COL_CIUDAD_D, ciudad_d)

df = pd.read_sql(query, conn, params=params)

# ===============================
# RESULTADOS
# ===============================
st.subheader("📊 Resultados")

if df.empty:
    st.warning("No se encontraron tarifas.")
    st.stop()

st.dataframe(df, use_container_width=True)

# ===============================
# SELECCIÓN
# ===============================
idx = st.number_input("Fila a imprimir", 0, len(df) - 1, 0)
r = df.iloc[idx]

# ===============================
# CONTROL DE RETORNO
# ===============================
if "mostrar_retorno" not in st.session_state:
    st.session_state["mostrar_retorno"] = True

c_r1, c_r2 = st.columns(2)
if c_r1.button("🔁 Quitar retorno"):
    st.session_state["mostrar_retorno"] = False
if c_r2.button("🔁 Incluir retorno"):
    st.session_state["mostrar_retorno"] = True

# ===============================
# FREIGHTS SEGUROS
# ===============================
mx_freight = get_val(r, "MEXICAN_FREIGHT", "MEX_FREIGHT", "MX_FREIGHT")
us_freight = get_val(r, "US_FREIGHT", "US_FRT", "US_COST")
crossing   = get_val(r, "CROSSING", "CRUCE")

# ===============================
# BLOQUE RETORNO (CONDICIONAL)
# ===============================
retorno_html = ""
if st.session_state["mostrar_retorno"]:
    retorno_html = """
    <br>
    <b>RETORNO</b>
    <table style="width:100%; border-collapse:collapse; margin-top:5px">
    <tr style="background:#f0f0f0">
      <th>ORIGEN</th>
      <th>DESTINO</th>
      <th>REQUERIMIENTO</th>
      <th>MEXICAN FREIGHT</th>
      <th>CROSSING</th>
      <th>US FREIGHT</th>
      <th>ALL IN</th>
    </tr>
    <tr contenteditable="true">
      <td>[Origen Retorno]</td>
      <td>[Destino Retorno]</td>
      <td>[Requerimiento]</td>
      <td align="right">[Mex Freight]</td>
      <td align="right">[Crossing]</td>
      <td align="right">[US Freight]</td>
      <td align="right"><b>[All In]</b></td>
    </tr>
    </table>
    """

# ===============================
# COTIZACIÓN EDITABLE
# ===============================
cotizacion_html = f"""
<div id="print-area" style="font-family:Arial; font-size:14px; line-height:1.6">

<p><b>Pactra México</b></p>

<p><b>Estimado(a) {r[COL_CLIENTE]},</b><br>
Esperando se encuentre muy bien.</p>

<p>
En seguimiento a su solicitud, compartimos la cotización correspondiente
al servicio de transporte solicitado:
</p>

<p><b>
Cotización de Servicio de Transporte – Pactra México ({r[COL_OPERACION]})
</b></p>

<table style="width:100%; border-collapse:collapse; margin-top:10px">
<tr style="background:#003A8F; color:white">
  <th>ORIGEN</th>
  <th>DESTINO</th>
  <th>REQUERIMIENTO</th>
  <th>MEXICAN FREIGHT</th>
  <th>CROSSING</th>
  <th>US FREIGHT</th>
  <th>ALL IN</th>
</tr>
<tr>
  <td>{r[COL_CIUDAD_O]}, {r[COL_ESTADO_O]}</td>
  <td>{r[COL_CIUDAD_D]}, {r[COL_ESTADO_D]}</td>
  <td>{r[COL_UNIDAD]} / {r[COL_VIAJE]}</td>
  <td align="right">{mx_freight}</td>
  <td align="right">{crossing}</td>
  <td align="right">{us_freight}</td>
  <td align="right"><b>{r[COL_ALLIN]}</b></td>
</tr>
</table>

{retorno_html}

<br>
<b>Condiciones Comerciales:</b>
<ul>
  <li>Las tarifas están expresadas en <b>USD/MXN</b> y no incluyen IVA.</li>
  <li>La tarifa incluye el costo del transporte en unidad tipo <b>53 FT</b>.</li>
  <li>Tiempo libre de maniobras: 3 horas en carga y 3 horas en descarga. Posterior a este tiempo aplicará cargo por demora según tarifa vigente.</li>
  <li>El seguro de mercancía no está incluido. Puede cotizarse adicionalmente bajo solicitud expresa del cliente.</li>
  <li>Las tarifas están sujetas a disponibilidad de unidad y condiciones de ruta al momento de confirmar el servicio.</li>
  <li>Vigencia de la cotización: <b>[X días]</b> a partir de la fecha de emisión.</li>
  <li>No incluye maniobras especiales, custodia, almacenaje ni costos de cruce fronterizo salvo se indique expresamente lo contrario.</li>
  <li>Los tiempos de tránsito son estimados y pueden variar por factores externos como clima, tráfico, inspecciones u otras causas ajenas al control del transportista.</li>
</ul>

<p>
Atentamente,<br>
<b>Pactra México – División Logística Internacional</b>
</p>

</div>
"""

st.components.v1.html(
    f"""
    <style>
    @media print {{
      body * {{
        visibility: hidden;
      }}
      #print-area, #print-area * {{
        visibility: visible;
      }}
      #print-area {{
        position: absolute;
        left: 0;
        top: 0;
        width: 100%;
      }}
      .print-btn {{
        display: none;
      }}
    }}

    .print-btn {{
      background:#003A8F;
      color:white;
      padding:10px 18px;
      border:none;
      border-radius:4px;
      font-size:14px;
      cursor:pointer;
      margin-bottom:15px;
    }}
    </style>

    <button class="print-btn" onclick="window.print()">
      🖨️ Imprimir / Guardar PDF
    </button>

    {cotizacion_html}
    """,
    height=820
)
