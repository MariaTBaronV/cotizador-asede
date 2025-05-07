from fastapi import FastAPI
from pydantic import BaseModel
from agentemotor_cotizador import cotizar_seguro
from twilio.rest import Client

app = FastAPI(title="Cotizar Seguro ASEDE")

# -------------------------------
# 🔹 Modelo de datos que recibe la API
# -------------------------------
class CotizacionRequest(BaseModel):
    placa: str
    tipo_uso: str
    municipio: str
    accesorios: int
    documento: str
    nombres: str
    apellidos: str
    fecha_nacimiento: str
    genero: str
    ocupacion: str
    estado_civil: str
    telefono: str
    correo: str

# -------------------------------
# 🔹 Endpoint de cotización (sin segundo plano)
# -------------------------------
@app.post("/cotizar")
def cotizar(datos: CotizacionRequest):
    datos_dict = datos.dict()

    # Ejecutar el scraping y obtener las cotizaciones
    resultado = cotizar_seguro(datos_dict)

    # 🔥 Aquí ya devuelves las cotizaciones directamente al GPT
    return {
        "mensaje": "Cotización completada.",
        "cotizaciones": resultado["cotizaciones"]
    }

# -------------------------------
# 🔹 Ejecución en Render
# -------------------------------
if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("app:app", host="0.0.0.0", port=port)
