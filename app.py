from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from playwright.async_api import async_playwright
import httpx
import asyncio
import os
import uvicorn

from procesar_cotizacion import procesar_cotizacion

# 👉 Tu API KEY de 2Captcha
API_KEY_2CAPTCHA = "1ce42240deeab8e84bb50b73fb2c77c9"

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
async def cotizar_seguro(datos: CotizacionRequest):
    try:
        resultado = await procesar_cotizacion(datos)
        return resultado
    except Exception as e:
        print("ERROR EN EL SERVIDOR:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
