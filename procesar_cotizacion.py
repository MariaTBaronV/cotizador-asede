from playwright.async_api import async_playwright
from captcha_solver import resolver_captcha

async def procesar_cotizacion(datos):

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        url_formulario = "https://proaseguros.co.agentemotor.com/"
        await page.goto(url_formulario)

        # 📝 1. Llenar placa y tipo de uso (simulando)
        await page.fill('input[name="plate"]', datos.placa)
        await page.click('button:has-text("Buscar")')

        # 👁 Esperar que cargue la siguiente sección
        await page.wait_for_selector('input[name="identification_number"]', timeout=30000)

        # 📝 2. Llenar datos personales
        await page.fill('input[name="identification_number"]', datos.documento)
        await page.fill('input[name="first_name"]', datos.nombres)
        await page.fill('input[name="last_name"]', datos.apellidos)
        await page.fill('input[name="birth_date"]', datos.fecha_nacimiento)
        await page.fill('input[name="phone"]', datos.telefono)
        await page.fill('input[name="email"]', datos.correo)

        # 📝 Seleccionar género
        if datos.genero == "M":
            await page.click('input[value="M"]')
        else:
            await page.click('input[value="F"]')

        # 📝 Otros campos (ocupacion, estado civil, etc.) pueden ser con select o input
        # NOTA: aquí debes adaptar dependiendo de cómo sean esos campos en el DOM real

        # ✅ 3. Resolver reCAPTCHA
        frame = page.frame_locator('iframe[title="reCAPTCHA"]')
        sitekey = await frame.get_attribute('//*[@title="reCAPTCHA"]', 'src')
        sitekey = sitekey.split("k=")[1].split("&")[0]

        token = await resolver_captcha(sitekey, url_formulario)

        # 📝 4. Insertar token en el campo g-recaptcha-response
        await page.evaluate(f'''document.getElementById("g-recaptcha-response").innerHTML = "{token}";''')

        # 📝 5. Hacer clic en Cotizar
        await page.click('button:has-text("Cotizar")')

        # 👁 6. Esperar resultados
        await page.wait_for_selector('.policy-card', timeout=60000)

        cards = await page.locator('.policy-card').all()

        resultados = []
for card in cards:
    titulo = await card.locator('.card-head-title-style').inner_text()
    precio = await card.locator('.card-price-span').inner_text()
    aseguradora = await card.locator('.company-name').inner_text()

    # Limpiar precio
    valor_prima = int(precio.replace("$", "").replace(".", "").replace(",", "").strip())

    # Obtener coberturas
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


        return {"cotizaciones": resultados}
