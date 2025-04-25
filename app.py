from flask import Flask, request, jsonify
from agentemotor_cotizador import cotizar_seguro

app = Flask(__name__)

@app.route("/cotizar", methods=["POST"])
def cotizar():
    data = request.json
    resultado = cotizar_seguro(data)
    return jsonify({"resultado": resultado})

if __name__ == "__main__":
    app.run(port=5000)
