from fastapi import FastAPI
from pydantic import BaseModel
import threading
from agentemotor_cotizador import cotizar_seguro
from twilio.rest import Client

app = FastAPI(title="Cotizar Seguro ASEDE")

# -------------------------------
# 🔹 Función para enviar WhatsApp
# -------------------------------
def enviar_whatsapp(telefono_cliente, mensaje):
    account_sid = "AC6103b4c903359f66974224092970526f"   
    auth_token = "ffe1662b836502fdb0db2751e7d6fafd"                    

    client = Client(account_sid, auth_token)

    telefono_formato = "+57" + telefono_cliente  # Asumimos números de Colombia

    client.messages.create(
        from_="whatsapp:+14155238886",  # Número sandbox de Twilio
        body=mensaje,
        to="whatsapp:" + telefono_formato
    )

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
# 🔹 Proceso en segundo plano
# -------------------------------
def procesar_en_segundo_plano(datos):
    try:
        resultado = cotizar_seguro(datos)

        precios = ""
        for cot in resultado["cotizaciones"]:
            precios += (
                f"\n🔹 Aseguradora: {cot['aseguradora']}"
                f"\nPlan: {cot['plan']}"
                f"\nPrecio: ${cot['valor_prima']:,}\n"
            )

        mensaje = (
            f"Hola {datos['nombres']} 👋. "
            "Tu cotización está lista 🚗:" + precios +
            "\nSi deseas, un asesor puede contactarte para avanzar con la contratación."
        )

        enviar_whatsapp(datos["telefono"], mensaje)

    except Exception as e:
        print("ERROR EN COTIZACIÓN:", str(e))

# -------------------------------
# 🔹 Endpoint de cotización
# -------------------------------
@app.post("/cotizar")
def cotizar(datos: CotizacionRequest):
    datos_dict = datos.dict()

    # Lanzar el scraping en segundo plano
    hilo = threading.Thread(target=procesar_en_segundo_plano, args=(datos_dict,))
    hilo.start()

    return {
        "mensaje": "Recibí tu solicitud. Estoy procesando tu cotización. Te contactaré en breve con los precios."
    }

# -------------------------------
# 🔹 Ejecución en Render
# -------------------------------
if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("app:app", host="0.0.0.0", port=port)
