from flask import Flask, request, jsonify, render_template
import sqlite3

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/mejor_proveedor", methods=["POST"])
def mejor_proveedor():
    data = request.json
    origen = data["origen"]
    destino = data["destino"]

    # DEMO (luego se conecta a BD real)
    return jsonify({
        "ruta": f"{origen} → {destino}",
        "proveedor": "UNIMEX",
        "precio": 15000,
        "costo": 10500,
        "margen": 0.30
    })

if __name__ == "__main__":
    app.run(debug=True)



