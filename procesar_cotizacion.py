from playwright.async_api import async_playwright
from captcha_solver import resolver_captcha
async def procesar_cotizacion(datos):

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Tu código para llenar datos...

        await page.click('button:has-text("Cotizar")')
        await page.wait_for_selector('.policy-card', timeout=60000)

        cards = await page.locator('.policy-card').all()

        resultados = []
        for card in cards:
            titulo = await card.locator('.card-head-title-style').inner_text()
            precio = await card.locator('.card-price-span').inner_text()
            aseguradora = await card.locator('.company-name').inner_text()

            valor_prima = int(precio.replace("$", "").replace(".", "").replace(",", "").strip())

            coberturas = []
            coberturas_elementos = await card.locator('.coverage-list li').all()
            for cobertura in coberturas_elementos:
                texto = await cobertura.inner_text()
                coberturas.append(texto)

            resultados.append({
                "aseguradora": aseguradora,
                "plan": titulo,
                "valor_prima": valor_prima,
                "coberturas_principales": coberturas
            })

        await browser.close()

        return {"cotizaciones": resultados}
