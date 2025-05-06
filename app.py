from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

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

@app.post("/cotizar")
def cotizar(datos: CotizacionRequest):
    try:
        resultado = cotizar_seguro(datos.dict())
        return resultado

    except Exception as e:
        print("ERROR EN EL SERVIDOR:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

# 🚀 Bloque para que Render detecte el puerto y levante el servidor
if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("app:app", host="0.0.0.0", port=port)
