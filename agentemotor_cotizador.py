import httpx
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

def cotizar_seguro(data):
    with sync_playwright() as p:
        print("🔵 Iniciando Playwright")
        browser = p.chromium.connect_over_cdp(
            "wss://chrome.browserless.io?token=SGBIhxdnzd9X5221dc6414af0d58022b6795405ab0"
        )
        page = browser.new_page()

        print("🔵 Abriendo Agentemotor")
        page.goto("https://proaseguros.co.agentemotor.com/")

        print("🔵 Llenando placa")
        page.fill('#plate', data['placa'])

        print("🔵 Esperando botón habilitado")
        page.wait_for_function(
            "document.querySelector('#btn-plate') && !document.querySelector('#btn-plate').disabled",
            timeout=30000
        )
        page.click('#btn-plate')

        print("🔵 Esperando tarjeta de vehículo")
        page.wait_for_selector('.card-vehicle', timeout=60000)
        page.click('text=Es mi vehículo')

        print("🔵 Llenando tipo de placa y uso")
        page.click('#plate_type')
        page.get_by_text('Particular').click()

        page.click('#use_type')
        page.get_by_text(data['tipo_uso']).click()

        print("🔵 Llenando accesorios y municipio")
        page.fill('#accesories_price', str(data['accesorios']))
        page.fill('#ubication', data['municipio'])
        page.click('text=Siguiente')

        print("🔵 Llenando datos personales")
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

        print("🔵 Haciendo clic en Cotizar")
        page.click('text=Cotizar')

        print("🔵 Esperando tarjetas de pólizas")
        page.wait_for_selector('.policy-card', timeout=120000)

        print("🔵 Leyendo tarjetas encontradas")
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

        print("✅ Cotizaciones encontradas:", resultados)
        browser.close()

        return {"cotizaciones": resultados}
