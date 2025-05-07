import httpx
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

def obtener_info_vehiculo(placa):
    url = f"https://proaseguros.co.agentemotor.com/vehiculos?plate={placa}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    }
    session = httpx.Client(headers=headers, timeout=300.0)

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
        try:
            page = browser.new_page()

            print("⚡ Código actualizado — versión seccionada 7 de mayo")
            print("[1] Cargando página y buscando vehículo...")

            # 👉 PASO 1: Ir a la página con la placa ya cargada
            page.goto(f"https://proaseguros.co.agentemotor.com/vehiculos?plate={data['placa']}")

            # 👉 PASO 2: Confirmar vehículo
            page.wait_for_selector('.card-vehicle', timeout=60000)
            page.click('text=Es mi vehículo')

            # Capturar datos del vehículo
            datos_vehiculo = {}
            datos_vehiculo['tipo'] = page.locator('.card-vehicle h3').inner_text()
            datos_vehiculo['modelo'] = page.locator('.card-vehicle p >> nth=0').inner_text()
            datos_vehiculo['fasecolda'] = page.locator('.card-vehicle p >> nth=1').inner_text()
            datos_vehiculo['cilindraje'] = page.locator('.card-vehicle p >> nth=2').inner_text()
            datos_vehiculo['precio'] = page.locator('.card-vehicle p >> nth=3').inner_text()

            print("[2] Vehículo confirmado:", datos_vehiculo)

            # 👉 PASO 3: Datos adicionales del vehículo
            page.click('#plate_type')
            page.get_by_role("option", name="Particular").click()

            page.click('#use_type')
            page.get_by_text(data['tipo_uso']).click()

            page.fill('#accesories_price', str(data['accesorios']))
            page.fill('#ubication', data['municipio'])
            print("[3] Datos adicionales del vehículo completados")

            page.click('text=Siguiente')

            # 👉 PASO 4: Datos del propietario
            page.click('#identification_type')
            page.get_by_text('Cédula de ciudadania').click()

            page.fill('#identification_number', data['documento'])
            page.fill('#first_name', data['nombres'])
            page.fill('#last_name', data['apellidos'])
            page.fill('#birth_date', data['fecha_nacimiento'])

            page.check(f'input[value="{data["genero"]}"]')

            page.click('#occupation')
            page.get_by_text(data['ocupacion']).click()

            page.click('#marital_status')
            page.get_by_text(data['estado_civil']).click()

            page.fill('#phone', data['telefono'])
            page.fill('#email', data['correo'])

            page.check('#agree_terms')
            print("[4] Datos del propietario completados")

            page.click('text=Cotizar')

            # 👉 PASO 5: Capturar cotizaciones
            page.wait_for_selector('.policy-card', timeout=120000)

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

            print("[5] Cotizaciones capturadas correctamente")
            print("Cotizaciones encontradas:", resultados)

            return {
                "cotizaciones": resultados,
                "datos_vehiculo": datos_vehiculo
            }

        except Exception as e:
            print("❌ ERROR EN EL SCRAPING:", str(e))
            return {
                "cotizaciones": [],
                "error": str(e),
                "datos_vehiculo": {}
            }

        finally:
            browser.close()

