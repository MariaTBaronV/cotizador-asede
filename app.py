from fastapi import FastAPI
from pydantic import BaseModel
import os
import requests
from datetime import datetime

app = FastAPI(title="Crear alerta de seguro ASEDE")

# 🔹 Modelo de datos
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

@app.post("/crear-alerta-cotizacion/")
def crear_alerta(datos: CotizacionRequest):
    HUBSPOT_API_KEY = os.getenv("HUBSPOT_API_KEY")
    HUBSPOT_OWNER_ID = os.getenv("HUBSPOT_OWNER_ID")

    nombre_completo = f"{datos.nombres} {datos.apellidos}"
    timestamp = datetime.utcnow().isoformat() + "Z"

    mensaje = (
        f"🚗 Nueva solicitud de cotización recibida:\n\n"
        f"👤 Cliente: {nombre_completo}\n"
        f"📄 Documento: {datos.documento}\n"
        f"📧 Email: {datos.correo}\n"
        f"📞 Teléfono: {datos.telefono}\n"
        f"📅 Nacimiento: {datos.fecha_nacimiento}\n"
        f"🧑 Género: {datos.genero} | Ocupación
