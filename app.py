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
