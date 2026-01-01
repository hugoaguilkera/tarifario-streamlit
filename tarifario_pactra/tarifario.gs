function filtrarTarifario() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const tarifario = ss.getSheetByName("Tarifario");
  const reporte = ss.getSheetByName("Reporte");

  // Filtros
  const origen = reporte.getRange("B2").getValue();
  const destino = reporte.getRange("C2").getValue();
  const transportista = reporte.getRange("D2").getValue();
  const tipoUnidad = reporte.getRange("E2").getValue();

  const lastRow = tarifario.getLastRow();
  if (lastRow < 2) return;

  const headers = tarifario.getRange("A1:L1").getValues()[0];
  headers.push("Profit"); // nueva columna

  const data = tarifario.getRange(2, 1, lastRow - 1, 12).getValues();

  // Filtrado + cálculo de profit
  const resultados = data
    .filter(row => {
      return (
        (!origen || row[4] == origen) &&
        (!destino || row[6] == destino) &&
        (!transportista || row[7] == transportista) &&
        (!tipoUnidad || row[8] == tipoUnidad)
      );
    })
    .map(row => {
      const tarifa = Number(row[9]) || 0; // J
      const precio = Number(row[10]) || 0; // K
      const profit = precio - tarifa;
      return [...row, profit];
    });

  // Limpiar área
  reporte.getRange("A7:M").clearContent().clearFormat();

  // Encabezado
  reporte.getRange("A7:M7").setValues([headers]);

  // Resultados
  if (resultados.length > 0) {
    reporte
      .getRange(8, 1, resultados.length, 13)
      .setValues(resultados);
  }

  const totalRows = resultados.length + 1;
  const tableRange = reporte.getRange(7, 1, totalRows, 13);

  // Bordes
  tableRange.setBorder(
    true, true, true, true, true, true,
    "#000000",
    SpreadsheetApp.BorderStyle.SOLID_MEDIUM
  );

  // Encabezado azul ejecutivo
  reporte.getRange("A7:M7")
    .setBackground("#1F4E79")
    .setFontColor("#FFFFFF")
    .setFontWeight("bold")
    .setHorizontalAlignment("center");

  // Cuerpo
  if (resultados.length > 0) {
    reporte.getRange(8, 1, resultados.length, 13)
      .setHorizontalAlignment("center")
      .setVerticalAlignment("middle");
  }

  // Ajuste columnas
  reporte.autoResizeColumns(1, 13);
}

function generarReporteG() {

  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const shLocal = ss.getSheetByName("LOCAL-NACIONAL");
  const shImpExp = ss.getSheetByName("IMPORTACIÓN - EXPORTACIÓN");
  const shRep = ss.getSheetByName("REPORTE_G");

  shRep.clearContents();
  shRep.appendRow([
    "ORIGEN",
    "DESTINO",
    "TIPO DE UNIDAD",
    "TRANSPORTISTA",
    "TIPO DE OPERACIÓN",
    "PRECIO USD"
  ]);

  // 👉 DESDE FILA 3
  const dataLocal = shLocal.getRange(3, 1, shLocal.getLastRow() - 2, shLocal.getLastColumn()).getValues();
  const dataImp = shImpExp.getRange(3, 1, shImpExp.getLastRow() - 2, shImpExp.getLastColumn()).getValues();

  const mejores = {};

  // ---------- LOCAL / FORÁNEO ----------
  dataLocal.forEach(r => {

    const tipoOperacion = r[1]; // LOCAL o FORÁNEO
    const tipoUnidad = r[2];
    const transportista = r[3];
    const origen = r[6];
    const destino = r[8];

    const moneda = r[10];
    const tipoCambio = r[13];

    let precioSencillo = r[9];
    let precioRedondo = r[11];

    let precioFinal = Math.min(precioSencillo || Infinity, precioRedondo || Infinity);

    if (moneda === "MXN") {
      precioFinal = precioFinal / tipoCambio;
    }

    const key = origen + "|" + destino + "|" + tipoUnidad + "|" + tipoOperacion;

    if (!mejores[key] || precioFinal < mejores[key].precio) {
      mejores[key] = {
        origen,
        destino,
        tipoUnidad,
        transportista,
        tipoOperacion,
        precio: precioFinal
      };
    }
  });

  // ---------- IMPORTACIÓN / EXPORTACIÓN ----------
  dataImp.forEach(r => {

    const tipoOperacion = r[1]; // IMPORTACIÓN / EXPORTACIÓN
    const tipoUnidad = r[2];
    const transportista = r[3];
    const origen = r[6];
    const destino = r[8];

    let precio = r[12];
    const moneda = r[13];

    if (moneda === "MXN") {
      precio = precio / 18.40;
    }

    const key = origen + "|" + destino + "|" + tipoUnidad + "|" + tipoOperacion;

    if (!mejores[key] || precio < mejores[key].precio) {
      mejores[key] = {
        origen,
        destino,
        tipoUnidad,
        transportista,
        tipoOperacion,
        precio
      };
    }
  });

  // ---------- ESCRIBIR REPORTE ----------
  Object.values(mejores).forEach(r => {
    shRep.appendRow([
      r.origen,
      r.destino,
      r.tipoUnidad,
      r.transportista,
      r.tipoOperacion,
      r.precio
    ]);
  });