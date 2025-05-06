import httpx
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

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

    tarjeta = soup.find('div', class_='card-vehicle')
    if not tarjeta:
        return "No se encontró la información del vehículo."

    resultado = {
        'placa': placa
    }

    modelo = tarjeta.find(string=lambda text: "Modelo" in text)
    if modelo:
        resultado['modelo'] = modelo.parent.find_next_sibling().text.strip()

    cilindraje = tarjeta.find(string=lambda text: "Cilindraje" in text)
    if cilindraje:
        resultado['cilindraje'] = cilindraje.parent.find_next_sibling().text.strip()

    precio = tarjeta.find(string=lambda text: "Precio de referencia" in text)
    if precio:
        resultado['precio_referencia'] = precio.parent.find_next_sibling().text.strip()

    return resultado

def cotizar_seguro(data):
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(
            "wss://chrome.browserless.io?token=SGBIhxdnzd9X5221dc6414af0d58022b6795405ab0"
        )
        page = browser.new_page()

        page.goto("https://proaseguros.co.agentemotor.com/")

        # Llenar placa
        page.fill('#plate', data['placa'])

        # Esperar que el botón esté habilitado antes de hacer clic
        page.wait_for_function(
            "document.querySelector('#btn-plate') && !document.querySelector('#btn-plate').disabled",
            timeout=30000
        )
        page.click('#btn-plate')

        # Seleccionar el vehículo
        page.wait_for_selector('.card-vehicle', timeout=30000)
        page.click('text=Es mi vehículo')

        # Datos del vehículo
        page.click('#plate_type')
        page.get_by_text('Particular').click()

        page.click('#use_type')
        page.get_by_text(data['tipo_uso']).click()

        page.fill('#accesories_price', str(data['accesorios']))
        page.fill('#ubication', data['municipio'])
        page.click('text=Siguiente')

        # Datos del propietario
        page.click('#identification_type')
        page.get_by_text('Cédula de ciudadania').click()

        page.fill('#identification_number', data['documento'])
        page.fill('#first_name', data['nombres'])
        page.fill('#last_name', data['apellidos'])
        page.fill('#birth_date', data['fecha_nacimiento'])

        # Género
        page.check(f'input[value="{data["genero"]}"]')

        page.click('#occupation')
        page.get_by_text(data['ocupacion']).click()

        page.click('#marital_status')
        page.get_by_text(data['estado_civil']).click()

        page.fill('#phone', data['telefono'])
        page.fill('#email', data['correo'])

        # Aceptar términos
        page.check('#agree_terms')

        # Hacer clic en "Cotizar"
        page.click('text=Cotizar')

        page.wait_for_selector('.policy-card', timeout=60000)

        cards = page.locator('.policy-card').all()

        resultados = []
        for card in cards:
            titulo = card.locator('.card-head-title-style').inner_text()
            precio = card.locator('.card-price-span').inner_text()
            aseguradora = card.locator('.company-name').inner_text()

            valor_prima = int(precio.replace("$", "").replace(".", "").replace(",", "").strip())

            coberturas = []
            coberturas_elementos = card.locator('.coverage-list li').all()
            for cobertura in coberturas_elementos:
                texto = cobertura.inner_text()
                coberturas.append(texto)

            resultados.append({
                "aseguradora": aseguradora,
                "plan": titulo,
                "valor_prima": valor_prima,
                "coberturas_principales": coberturas
            })

        browser.close()

        return {"cotizaciones": resultados}
