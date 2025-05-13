import os
import requests
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Datos del cliente y vehículo recibidos desde el chatbot
class CotizacionVehiculo(BaseModel):
    nombre_completo: str
    tipo_documento: str
    numero_documento: str
    fecha_nacimiento: str  # idealmente formato YYYY-MM-DD
    celular: str
    email: str
    genero: str
    ocupacion: str
    estado_civil: str
    placa: str
    tipo_uso: str
    municipio_circulacion: str
    valor_accesorios: int

HUBSPOT_API_KEY = os.getenv("HUBSPOT_API_KEY")
HUBSPOT_OWNER_ID = "tu_owner_id_en_hubspot"  # Reemplaza por el ID real

@app.post("/crear-alerta-cotizacion/")
def crear_alerta_cotizacion(datos: CotizacionVehiculo):
    
    mensaje_alerta = (
        f"🚗 **Nueva cotización de seguro recibida** 🚗\n\n"
        f"👤 **Información del Cliente:**\n"
        f"- **Nombre Completo:** {datos.nombre_completo}\n"
        f"- **Tipo Documento:** {datos.tipo_documento}\n"
        f"- **Número Documento:** {datos.numero_documento}\n"
        f"- **Fecha Nacimiento:** {datos.fecha_nacimiento}\n"
        f"- **Celular:** {datos.celular}\n"
        f"- **Correo Electrónico:** {datos.email}\n"
        f"- **Género:** {datos.genero}\n"
        f"- **Ocupación:** {datos.ocupacion}\n"
        f"- **Estado Civil:** {datos.estado_civil}\n\n"
        f"🚘 **Información del Vehículo:**\n"
        f"- **Placa:** {datos.placa}\n"
        f"- **Tipo Uso:** {datos.tipo_uso}\n"
        f"- **Municipio de Circulación:** {datos.municipio_circulacion}\n"
        f"- **Valor Accesorios:** ${datos.valor_accesorios:,}\n"
    )

    url = f"https://api.hubapi.com/crm/v3/objects/tasks?hapikey={HUBSPOT_API_KEY}"

    data = {
        "properties": {
            "hs_timestamp": "2025-05-12T10:00:00Z",
            "hs_task_body": mensaje_alerta,
            "hs_task_subject": f"Cotización Vehículo - {datos.nombre_completo}",
            "hs_task_status": "NOT_STARTED",
            "hs_task_priority": "HIGH",
            "hubspot_owner_id": HUBSPOT_OWNER_ID
        }
    }

    response = requests.post(url, json=data)

    if response.status_code == 201:
        return {
            "message": "✅ Alerta creada exitosamente en HubSpot.",
            "hubspot_task_id": response.json().get('id')
        }
    else:
        return {
            "error": "❌ Hubo un problema al crear la alerta en HubSpot.",
            "detalle": response.json()
        }, response.status_code
