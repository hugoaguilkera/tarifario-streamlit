def obtener_precio(row):
    if row["operacion"] in ["Local", "Foraneo"]:
        if row["tipo_viaje"] == "Sencillo":
            return row["PRECIO VIAJE SENCILLO"]
        else:
            return row["PRECIO VIAJE REDONDO"]
    else:
        return row["ALL IN"]

