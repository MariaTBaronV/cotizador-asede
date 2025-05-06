import httpx
from bs4 import BeautifulSoup

def obtener_info_vehiculo(placa):
    url = f"https://proaseguros.co.agentemotor.com/vehiculos?plate={placa}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    }
    session = httpx.Client(headers=headers, timeout=30.0)

    respuesta = session.get(url)
    if respuesta.status_code != 200:
        return f"Error al cargar la página. Código: {respuesta.status_code}"

    soup = BeautifulSoup(respuesta.text, 'html.parser')

    # Buscar datos del vehículo
    tarjeta = soup.find('div', class_='card-vehicle')
    if not tarjeta:
        return "No se encontró la información del vehículo."

    resultado = {}

    # Placa
    resultado['placa'] = placa

    # Modelo
    modelo = tarjeta.find(string=lambda text: "Modelo" in text)
    if modelo:
        resultado['modelo'] = modelo.parent.find_next_sibling().text.strip()

    # Cilindraje
    cilindraje = tarjeta.find(string=lambda text: "Cilindraje" in text)
    if cilindraje:
        resultado['cilindraje'] = cilindraje.parent.find_next_sibling().text.strip()

    # Precio
    precio = tarjeta.find(string=lambda text: "Precio de referencia" in text)
    if precio:
        resultado['precio_referencia'] = precio.parent.find_next_sibling().text.strip()

    return resultado

def cotizar_seguro(data):
    placa = data.get("placa")
    if not placa:
        return {"error": "No se proporcionó placa."}

    datos = obtener_info_vehiculo(placa)
    if isinstance(datos, str):  # si hubo un error
        return {"error": datos}

    return {"cotizacion": datos}
