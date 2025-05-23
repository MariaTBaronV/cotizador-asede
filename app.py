from fastapi import FastAPI, Request, Query
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from datetime import datetime
import os
import requests

app = FastAPI(title="Crear alerta de seguro ASEDE")

# 🔹 Modelo de datos de cotización
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

# 🔹 Crear alerta en HubSpot
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
        f"🧑 Género: {datos.genero} | Ocupación: {datos.ocupacion} | Estado civil: {datos.estado_civil}\n\n"
        f"🚘 Vehículo: Placa {datos.placa}, Uso: {datos.tipo_uso}, Municipio: {datos.municipio}\n"
        f"🔧 Valor accesorios: ${datos.accesorios:,}"
    )

    payload = {
        "properties": {
            "hs_timestamp": timestamp,
            "hs_task_subject": f"Cotización Vehículo - {nombre_completo}",
            "hs_task_body": mensaje,
            "hs_task_status": "NOT_STARTED",
            "hs_task_priority": "HIGH"
        }
    }

    if HUBSPOT_OWNER_ID:
        payload["properties"]["hubspot_owner_id"] = HUBSPOT_OWNER_ID

    headers = {
        "Authorization": f"Bearer {HUBSPOT_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        "https://api.hubapi.com/crm/v3/objects/tasks",
        headers=headers,
        json=payload
    )

    print("Status:", response.status_code)
    print("HubSpot response:", response.text)

    if response.status_code == 201:
        return {"message": "✅ Alerta creada en HubSpot", "hubspot_id": response.json().get("id")}
    else:
        return {
            "error": "❌ No se pudo crear la alerta",
            "detalle": response.json()
        }, response.status_code

# 🔹 Token para verificar el webhook
VERIFY_TOKEN = "Marco_2020"

# 🔹 Verificación GET desde Meta
@app.get("/webhook", response_class=PlainTextResponse)
async def verificar_webhook(
    hub_mode: str = Query(default=None, alias="hub.mode"),
    hub_challenge: str = Query(default=None, alias="hub.challenge"),
    hub_verify_token: str = Query(default=None, alias="hub.verify_token")
):
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return hub_challenge
    return PlainTextResponse("Token inválido", status_code=403)

# 🔹 Función para responder por WhatsApp
def enviar_mensaje_whatsapp(texto: str, numero: str):
    url = "https://graph.facebook.com/v22.0/682672741587063/messages"
    token = os.getenv("WHATSAPP_TOKEN")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    data = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "text",
        "text": {
            "body": texto
        }
    }

    response = requests.post(url, headers=headers, json=data)
    print("📤 Respuesta enviada:", response.status_code, response.text)

# 🔹 POST para recibir mensajes desde WhatsApp
@app.post("/webhook")
async def recibir_mensaje(request: Request):
    body = await request.json()
    try:
        mensaje = body["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"]
        numero = body["entry"][0]["changes"][0]["value"]["messages"][0]["from"]

        print(f"📩 Mensaje recibido de {numero}: {mensaje}")

        respuesta = f"Hola 👋 soy Axel, tu asesor de ASEDE. ¿En qué puedo ayudarte hoy?"
        enviar_mensaje_whatsapp(respuesta, numero)

        return {"status": "mensaje recibido"}
    except Exception as e:
        print("⚠️ Error al procesar mensaje:", e)
        return {"error": str(e)}, 400

# 🔹 Ejecutar localmente
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("app:app", host="0.0.0.0", port=port)
