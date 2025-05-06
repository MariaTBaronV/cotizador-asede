from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import threading
from agentemotor_cotizador import cotizar_seguro

app = FastAPI(title="Cotizar Seguro ASEDE")

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

def procesar_en_segundo_plano(datos):
    try:
        resultado = cotizar_seguro(datos)
        # Aquí puedes enviar correo o guardar en base de datos
        print("Cotización completada:", resultado)
    except Exception as e:
        print("ERROR EN COTIZACIÓN:", str(e))

@app.post("/cotizar")
def cotizar(datos: CotizacionRequest):
    datos_dict = datos.dict()
    # Lanzar el procesamiento en segundo plano
    hilo = threading.Thread(target=procesar_en_segundo_plano, args=(datos_dict,))
    hilo.start()
    return {"mensaje": "Recibí tu solicitud. Estoy procesando tu cotización. Te contactaré en breve con los precios."}

# Bloque para ejecutar en Render
if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("app:app", host="0.0.0.0", port=port)
